"""
Authentication service using Supabase Auth
This replaces the bcrypt-based auth with proper Supabase Auth integration
"""
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from supabase import Client
from gotrue.errors import AuthApiError

from ..config import settings
from ..utils.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    InvalidTokenError,
    EmailNotVerifiedError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """Authentication service using Supabase Auth"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def register(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user using Supabase Auth

        Args:
            email: User email
            password: User password (min 8 chars)
            full_name: Optional full name
            company: Optional company name

        Returns:
            Dict with user data and tokens

        Raises:
            EmailAlreadyExistsError: If email already registered
            DatabaseError: If registration fails
        """
        try:
            # Sign up user with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "company": company
                    }
                }
            })

            if not auth_response.user:
                raise DatabaseError("Failed to create user")

            user_id = auth_response.user.id

            # Update profile with additional data
            # (The trigger will have created the profile, now we update it)
            if full_name or company:
                profile_data = {}
                if full_name:
                    profile_data["full_name"] = full_name
                if company:
                    profile_data["company"] = company

                self.supabase.table("profiles").update(profile_data).eq("id", user_id).execute()

            # Return user data and tokens
            return {
                "user": {
                    "id": str(user_id),
                    "email": email,
                    "full_name": full_name,
                    "email_verified": auth_response.user.email_confirmed_at is not None
                },
                "access_token": auth_response.session.access_token if auth_response.session else None,
                "refresh_token": auth_response.session.refresh_token if auth_response.session else None,
                "token_type": "bearer"
            }

        except AuthApiError as e:
            if "already registered" in str(e).lower() or "already exists" in str(e).lower():
                raise EmailAlreadyExistsError(f"Email {email} is already registered")
            logger.error(f"Supabase auth error during registration: {e}")
            raise DatabaseError(f"Failed to register user: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            raise DatabaseError(f"Failed to register user: {str(e)}")

    async def login(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Login user using Supabase Auth

        Args:
            email: User email
            password: User password

        Returns:
            Dict with user data and tokens

        Raises:
            InvalidCredentialsError: If credentials are invalid
            DatabaseError: If login fails
        """
        try:
            # Sign in with Supabase Auth
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not auth_response.user or not auth_response.session:
                raise InvalidCredentialsError("Invalid email or password")

            user_id = auth_response.user.id

            # Get profile data
            profile_response = self.supabase.table("profiles").select("*").eq("id", user_id).execute()

            profile = profile_response.data[0] if profile_response.data else {}

            # Update last login
            self.supabase.table("profiles").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()

            # Return user data and tokens
            return {
                "user": {
                    "id": str(user_id),
                    "email": auth_response.user.email,
                    "full_name": profile.get("full_name"),
                    "company": profile.get("company"),
                    "plan": profile.get("plan", "free"),
                    "email_verified": auth_response.user.email_confirmed_at is not None
                },
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "token_type": "bearer",
                "expires_at": auth_response.session.expires_at if hasattr(auth_response.session, 'expires_at') else None
            }

        except AuthApiError as e:
            if "invalid" in str(e).lower() or "credentials" in str(e).lower():
                raise InvalidCredentialsError("Invalid email or password")
            logger.error(f"Supabase auth error during login: {e}")
            raise DatabaseError(f"Failed to login: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise DatabaseError(f"Failed to login: {str(e)}")

    async def get_current_user(self, access_token: str) -> Dict[str, Any]:
        """
        Get current user from access token

        Args:
            access_token: JWT access token

        Returns:
            Dict with user data

        Raises:
            InvalidTokenError: If token is invalid
        """
        try:
            # Get user from token
            user_response = self.supabase.auth.get_user(access_token)

            if not user_response.user:
                raise InvalidTokenError("Invalid or expired token")

            user_id = user_response.user.id

            # Get profile data
            profile_response = self.supabase.table("profiles").select("*").eq("id", user_id).execute()

            profile = profile_response.data[0] if profile_response.data else {}

            return {
                "id": str(user_id),
                "email": user_response.user.email,
                "full_name": profile.get("full_name"),
                "company": profile.get("company"),
                "plan": profile.get("plan", "free"),
                "stripe_customer_id": profile.get("stripe_customer_id"),
                "email_verified": user_response.user.email_confirmed_at is not None,
                "created_at": profile.get("created_at")
            }

        except AuthApiError as e:
            raise InvalidTokenError(f"Invalid or expired token: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise InvalidTokenError(f"Failed to get user: {str(e)}")

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            Dict with new tokens

        Raises:
            InvalidTokenError: If refresh token is invalid
        """
        try:
            # Refresh session
            auth_response = self.supabase.auth.refresh_session(refresh_token)

            if not auth_response.session:
                raise InvalidTokenError("Invalid or expired refresh token")

            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "token_type": "bearer",
                "expires_at": auth_response.session.expires_at if hasattr(auth_response.session, 'expires_at') else None
            }

        except AuthApiError as e:
            raise InvalidTokenError(f"Invalid or expired refresh token: {str(e)}")
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise InvalidTokenError(f"Failed to refresh token: {str(e)}")

    async def update_profile(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        company: Optional[str] = None,
        email_notifications: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update user profile

        Args:
            user_id: User ID
            full_name: Optional new full name
            company: Optional new company
            email_notifications: Optional email notification preference

        Returns:
            Updated user data
        """
        try:
            update_data = {}
            if full_name is not None:
                update_data["full_name"] = full_name
            if company is not None:
                update_data["company"] = company
            if email_notifications is not None:
                update_data["email_notifications"] = email_notifications

            if not update_data:
                # No updates, just return current profile
                return await self.get_profile(user_id)

            # Update profile
            response = self.supabase.table("profiles").update(update_data).eq("id", user_id).execute()

            if not response.data:
                raise DatabaseError("Failed to update profile")

            return response.data[0]

        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            raise DatabaseError(f"Failed to update profile: {str(e)}")

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile by ID"""
        try:
            response = self.supabase.table("profiles").select("*").eq("id", user_id).execute()

            if not response.data:
                raise DatabaseError("Profile not found")

            return response.data[0]

        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            raise DatabaseError(f"Failed to get profile: {str(e)}")

    async def logout(self, access_token: str) -> None:
        """
        Logout user (sign out from Supabase)

        Args:
            access_token: Access token to invalidate
        """
        try:
            self.supabase.auth.sign_out()
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            # Don't raise exception on logout failure
            pass
