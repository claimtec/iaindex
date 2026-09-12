"""
Authentication service using Supabase Python Client
Uses the official Supabase client library instead of raw HTTP calls
"""
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from supabase import Client

from ..config import settings
from ..utils.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    InvalidTokenError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Authentication service using Supabase Client"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user using Supabase Auth Client

        This will:
        1. Create user in auth.users via Supabase Auth
        2. Trigger will auto-create profile in profiles table
        3. Update profile with additional data
        """
        try:
            # Use Supabase client's sign_up method
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "company": company
                    }
                }
            })

            if not response.user:
                raise DatabaseError(detail="Failed to create user")

            user_id = str(response.user.id)

            # Wait for trigger to create profile
            import asyncio
            await asyncio.sleep(0.5)

            # Update profile with additional data
            if full_name or company:
                update_data = {}
                if full_name:
                    update_data["full_name"] = full_name
                if company:
                    update_data["company"] = company

                try:
                    self.supabase.table("profiles").update(update_data).eq("id", user_id).execute()
                except Exception as e:
                    logger.warning(f"Failed to update profile: {e}")

            # Get profile
            try:
                result = self.supabase.table("profiles").select("*").eq("id", user_id).execute()
                if result.data:
                    return result.data[0]
            except Exception as e:
                logger.warning(f"Failed to get profile: {e}")

            # Return basic user data if profile fetch fails
            return {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "company": company,
                "plan": "free",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            error_msg = str(e).lower()

            if "already registered" in error_msg or "already exists" in error_msg:
                raise EmailAlreadyExistsError()

            logger.error(f"Unexpected error during registration: {e}")
            raise DatabaseError(detail=f"Failed to register user: {str(e)}")

    async def login_user(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Login user using Supabase Auth Client
        """
        try:
            # Use Supabase client's sign_in_with_password method
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not response.user or not response.session:
                raise InvalidCredentialsError()

            user_id = str(response.user.id)

            # Get profile
            result = self.supabase.table("profiles").select("*").eq("id", user_id).execute()

            if not result.data:
                # Create profile if it doesn't exist (shouldn't happen with trigger)
                profile_data = {
                    "id": user_id,
                    "email": email,
                    "plan": "free"
                }
                self.supabase.table("profiles").insert(profile_data).execute()
                user = profile_data
            else:
                user = result.data[0]

            # Update last login
            try:
                self.supabase.table("profiles").update({
                    "last_login": datetime.utcnow().isoformat()
                }).eq("id", user_id).execute()
            except Exception as e:
                logger.warning(f"Failed to update last_login: {e}")

            # Add password_hash for compatibility
            user["password_hash"] = "managed_by_supabase_auth"

            return user

        except Exception as e:
            error_msg = str(e).lower()

            if "invalid" in error_msg or "credentials" in error_msg:
                raise InvalidCredentialsError()

            logger.error(f"Unexpected error during login: {e}")
            raise InvalidCredentialsError()

    async def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """Get user profile by ID"""
        try:
            result = self.supabase.table("profiles").select("*").eq("id", user_id).execute()

            if not result.data:
                raise DatabaseError(detail="User not found")

            return result.data[0]

        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise DatabaseError(detail=f"Failed to get user: {str(e)}")

    async def update_user(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        company: Optional[str] = None,
        email_notifications: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update user profile"""
        try:
            updates = {}
            if full_name is not None:
                updates["full_name"] = full_name
            if company is not None:
                updates["company"] = company
            if email_notifications is not None:
                updates["email_notifications"] = email_notifications

            if not updates:
                return await self.get_user_by_id(user_id)

            updates["updated_at"] = datetime.utcnow().isoformat()

            result = self.supabase.table("profiles").update(updates).eq("id", user_id).execute()

            if not result.data:
                raise DatabaseError(detail="Failed to update user")

            return result.data[0]

        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise DatabaseError(detail=f"Failed to update user: {str(e)}")

    async def delete_user(self, user_id: str) -> Dict[str, str]:
        """Soft delete user (GDPR compliant)"""
        try:
            anonymized_data = {
                "email": f"deleted_{user_id}@deleted.local",
                "full_name": None,
                "company": None,
                "deleted_at": datetime.utcnow().isoformat(),
                "email_notifications": False
            }

            result = self.supabase.table("profiles").update(anonymized_data).eq("id", user_id).execute()

            if not result.data:
                raise DatabaseError(detail="User not found")

            return {"message": "User account deleted successfully"}

        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise DatabaseError(detail=f"Failed to delete user: {str(e)}")

    # Token methods (keep for compatibility)
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime] = None) -> str:
        """Create JWT access token"""
        from jose import jwt
        from datetime import timedelta

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode = data.copy()
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create refresh token"""
        from jose import jwt
        from datetime import timedelta
        import secrets

        expire = datetime.utcnow() + timedelta(days=30)

        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)
        }

        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def hash_password(password: str) -> str:
        """Dummy - Supabase handles hashing"""
        return "managed_by_supabase_auth"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Dummy - Supabase handles verification"""
        return True
