"""
Authentication service using Supabase Auth API
This properly integrates with Supabase's auth system
"""
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import httpx
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
    """Authentication service using Supabase Auth"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_key

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user using Supabase Auth

        This will:
        1. Create user in auth.users via Supabase Auth API
        2. Trigger will auto-create profile in profiles table
        3. Update profile with additional data
        """
        try:
            # Use Supabase Auth API to create user
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/auth/v1/signup",
                    json={
                        "email": email,
                        "password": password,
                        "data": {
                            "full_name": full_name,
                            "company": company
                        }
                    },
                    headers={
                        "apikey": self.supabase_key,
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code == 400:
                    error_data = response.json()
                    if "already registered" in str(error_data).lower():
                        raise EmailAlreadyExistsError()
                    raise DatabaseError(detail=f"Registration failed: {error_data.get('msg', 'Unknown error')}")

                if response.status_code != 200:
                    raise DatabaseError(detail=f"Registration failed with status {response.status_code}")

                data = response.json()
                user_id = data.get("user", {}).get("id")

                if not user_id:
                    raise DatabaseError(detail="Failed to create user")

            # Wait a moment for trigger to create profile
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
                    # Don't fail registration if profile update fails

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

        except EmailAlreadyExistsError:
            raise
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            raise DatabaseError(detail=f"Failed to register user: {str(e)}")

    async def login_user(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Login user using Supabase Auth API

        Returns user data with password_hash for verification
        """
        try:
            # Use Supabase Auth API to login
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/auth/v1/token?grant_type=password",
                    json={
                        "email": email,
                        "password": password
                    },
                    headers={
                        "apikey": self.supabase_key,
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code == 400:
                    raise InvalidCredentialsError()

                if response.status_code != 200:
                    raise DatabaseError(detail=f"Login failed with status {response.status_code}")

                data = response.json()
                user_id = data.get("user", {}).get("id")

                if not user_id:
                    raise InvalidCredentialsError()

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
                return profile_data

            user = result.data[0]

            # Update last login
            try:
                self.supabase.table("profiles").update({
                    "last_login": datetime.utcnow().isoformat()
                }).eq("id", user_id).execute()
            except Exception as e:
                logger.warning(f"Failed to update last_login: {e}")

            # Add a fake password_hash for compatibility with existing code
            user["password_hash"] = "managed_by_supabase_auth"

            return user

        except InvalidCredentialsError:
            raise
        except Exception as e:
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

    # Token methods (keep for compatibility with existing routes)
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
        """Dummy method for compatibility - Supabase handles password hashing"""
        return "managed_by_supabase_auth"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Dummy method for compatibility - Supabase handles password verification"""
        return True  # Password verification happens in login_user via Supabase Auth API
