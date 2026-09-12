"""
Authentication service with Supabase integration and bcrypt password hashing
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets
import logging
from supabase import Client

from ..config import settings
from ..utils.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    InvalidTokenError,
    EmailNotVerifiedError,
    DatabaseError
)

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Refresh token settings
REFRESH_TOKEN_EXPIRE_DAYS = 30


class AuthenticationService:
    """Authentication service for user management"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create refresh token"""
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )

            # Verify token type
            if payload.get("type") != token_type:
                raise InvalidTokenError(detail=f"Invalid token type. Expected {token_type}")

            # Verify expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise InvalidTokenError(detail="Token has expired")

            return payload

        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise InvalidTokenError(detail="Could not validate token")

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user

        Args:
            email: User email
            password: User password (will be hashed)
            full_name: User's full name
            company: Company name

        Returns:
            Created user data

        Raises:
            EmailAlreadyExistsError: If email is already registered
            DatabaseError: If database operation fails
        """
        try:
            # Check if user exists
            existing_user = self.supabase.table("profiles").select("id").eq("email", email.lower()).execute()

            if existing_user.data:
                raise EmailAlreadyExistsError()

            # Hash password
            hashed_password = self.hash_password(password)

            # Create user record
            user_data = {
                "email": email.lower(),
                "password_hash": hashed_password,
                "full_name": full_name,
                "company": company,
                "email_verified": False,
                "plan": "free",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            result = self.supabase.table("profiles").insert(user_data).execute()

            if not result.data:
                raise DatabaseError(detail="Failed to create user")

            user = result.data[0]
            logger.info(f"User registered successfully: {email}")

            # Remove password hash from response
            user.pop("password_hash", None)

            return user

        except EmailAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            raise DatabaseError(detail="Failed to register user")

    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password

        Args:
            email: User email
            password: User password

        Returns:
            User data if authentication successful

        Raises:
            InvalidCredentialsError: If email or password is incorrect
            EmailNotVerifiedError: If email is not verified (optional)
        """
        try:
            # Get user by email
            result = self.supabase.table("profiles").select("*").eq("email", email.lower()).execute()

            if not result.data:
                raise InvalidCredentialsError()

            user = result.data[0]

            # Verify password
            if not self.verify_password(password, user.get("password_hash", "")):
                raise InvalidCredentialsError()

            # Optional: Check email verification
            # if not user.get("email_verified", False):
            #     raise EmailNotVerifiedError()

            # Update last login
            self.supabase.table("profiles").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user["id"]).execute()

            logger.info(f"User authenticated successfully: {email}")

            # Remove password hash from response
            user.pop("password_hash", None)

            return user

        except (InvalidCredentialsError, EmailNotVerifiedError):
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise InvalidCredentialsError()

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = self.supabase.table("profiles").select("*").eq("id", user_id).execute()

            if not result.data:
                return None

            user = result.data[0]
            # Remove password hash
            user.pop("password_hash", None)

            return user

        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None

    async def update_user(
        self,
        user_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update user profile"""
        try:
            # Remove sensitive fields
            updates.pop("password_hash", None)
            updates.pop("email", None)  # Email changes require verification
            updates.pop("id", None)
            updates.pop("created_at", None)

            updates["updated_at"] = datetime.utcnow().isoformat()

            result = self.supabase.table("profiles").update(updates).eq("id", user_id).execute()

            if not result.data:
                raise DatabaseError(detail="Failed to update user")

            user = result.data[0]
            user.pop("password_hash", None)

            logger.info(f"User updated successfully: {user_id}")

            return user

        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise DatabaseError(detail="Failed to update user")

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user account (GDPR compliance)

        This performs a soft delete by anonymizing data
        """
        try:
            # Anonymize user data instead of hard delete
            anonymized_data = {
                "email": f"deleted_{user_id}@deleted.local",
                "full_name": "Deleted User",
                "company": None,
                "password_hash": "",
                "deleted_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            result = self.supabase.table("profiles").update(anonymized_data).eq("id", user_id).execute()

            if result.data:
                logger.info(f"User deleted (anonymized): {user_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            raise DatabaseError(detail="Failed to delete user")

    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        try:
            # Get user
            result = self.supabase.table("profiles").select("password_hash").eq("id", user_id).execute()

            if not result.data:
                raise InvalidCredentialsError()

            user = result.data[0]

            # Verify old password
            if not self.verify_password(old_password, user.get("password_hash", "")):
                raise InvalidCredentialsError(detail="Current password is incorrect")

            # Hash new password
            new_hash = self.hash_password(new_password)

            # Update password
            self.supabase.table("profiles").update({
                "password_hash": new_hash,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()

            logger.info(f"Password changed for user: {user_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to change password: {e}")
            raise DatabaseError(detail="Failed to change password")

    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return f"sk_{secrets.token_urlsafe(32)}"

    async def create_api_key(
        self,
        user_id: str,
        name: str,
        scopes: Optional[list] = None
    ) -> Dict[str, Any]:
        """Create API key for user"""
        try:
            api_key = self.generate_api_key()
            key_prefix = api_key[:12]  # Store prefix for identification

            # Hash the API key for storage
            key_hash = self.hash_password(api_key)

            key_data = {
                "user_id": user_id,
                "name": name,
                "key_hash": key_hash,
                "key_prefix": key_prefix,
                "scopes": scopes,
                "active": True,
                "created_at": datetime.utcnow().isoformat()
            }

            result = self.supabase.table("api_keys").insert(key_data).execute()

            if not result.data:
                raise DatabaseError(detail="Failed to create API key")

            key_record = result.data[0]

            # Return the full key only once (it won't be retrievable again)
            key_record["key"] = api_key
            key_record.pop("key_hash", None)

            logger.info(f"API key created for user: {user_id}")

            return key_record

        except Exception as e:
            logger.error(f"Failed to create API key: {e}")
            raise DatabaseError(detail="Failed to create API key")
