"""
Authentication routes for user registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any
from datetime import timedelta
import logging

from supabase import create_client, Client

from ..config import settings
from ..models.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    UserUpdate,
    TokenResponse,
    RefreshTokenRequest,
    UsageStats,
    ApiKeyCreate,
    ApiKeyResponse,
    UserWebsitesResponse
)
from ..services.auth_service import AuthenticationService
from ..middleware.auth import get_current_user
from ..utils.exceptions import (
    AuthenticationError,
    ResourceNotFoundError,
    DatabaseError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/auth", tags=["authentication"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


async def get_supabase_client() -> Client:
    """Get Supabase client"""
    return create_client(settings.supabase_url, settings.supabase_key)


async def get_auth_service(
    supabase: Client = Depends(get_supabase_client)
) -> AuthenticationService:
    """Get authentication service"""
    return AuthenticationService(supabase)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserRegister,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Register a new user account

    - **email**: Valid email address
    - **password**: Minimum 8 characters, must contain uppercase, lowercase, and digit
    - **full_name**: Optional user's full name
    - **company**: Optional company name

    Returns JWT access token and user information.
    """
    try:
        # Register user
        user = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            company=user_data.company
        )

        # Create tokens
        access_token = auth_service.create_access_token(
            data={"sub": user["id"], "email": user["email"]}
        )
        refresh_token = auth_service.create_refresh_token(user["id"])

        # Prepare user response
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            company=user.get("company"),
            plan=user.get("plan", "free"),
            stripe_customer_id=user.get("stripe_customer_id"),
            email_verified=user.get("email_verified", False),
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )

        logger.info(f"User registered: {user_data.email}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=user_response
        )

    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    credentials: UserLogin,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Login with email and password

    - **email**: User's email address
    - **password**: User's password

    Returns JWT access token and refresh token.
    """
    try:
        # Authenticate user
        user = await auth_service.login_user(
            email=credentials.email,
            password=credentials.password
        )

        # Create tokens
        access_token = auth_service.create_access_token(
            data={"sub": user["id"], "email": user["email"], "plan": user.get("plan")}
        )
        refresh_token = auth_service.create_refresh_token(user["id"])

        # Prepare user response
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            company=user.get("company"),
            plan=user.get("plan", "free"),
            stripe_customer_id=user.get("stripe_customer_id"),
            email_verified=user.get("email_verified", False),
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )

        logger.info(f"User logged in: {credentials.email}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=user_response
        )

    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Get current authenticated user's profile

    Requires valid JWT token in Authorization header.
    """
    try:
        user_id = current_user.get("sub")

        user = await auth_service.get_user_by_id(user_id)

        if not user:
            raise ResourceNotFoundError(resource="User")

        return UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            company=user.get("company"),
            plan=user.get("plan", "free"),
            stripe_customer_id=user.get("stripe_customer_id"),
            email_verified=user.get("email_verified", False),
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )

    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise


@router.patch("/update", response_model=UserResponse)
async def update_user_profile(
    updates: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Update current user's profile

    - **full_name**: Update user's full name
    - **company**: Update company name
    - **email_notifications**: Update email preferences
    """
    try:
        user_id = current_user.get("sub")

        # Convert to dict and remove None values
        update_data = {k: v for k, v in updates.dict().items() if v is not None}

        user = await auth_service.update_user(user_id, **update_data)

        logger.info(f"User profile updated: {user_id}")

        return UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            company=user.get("company"),
            plan=user.get("plan", "free"),
            stripe_customer_id=user.get("stripe_customer_id"),
            email_verified=user.get("email_verified", False),
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )

    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh_access_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token

    - **refresh_token**: Valid refresh token

    Returns new access token.
    """
    try:
        # Verify refresh token
        payload = auth_service.verify_token(
            refresh_request.refresh_token,
            token_type="refresh"
        )

        user_id = payload.get("sub")

        # Get user data
        user = await auth_service.get_user_by_id(user_id)

        if not user:
            raise AuthenticationError(detail="User not found")

        # Create new access token
        access_token = auth_service.create_access_token(
            data={"sub": user["id"], "email": user["email"], "plan": user.get("plan")}
        )

        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user.get("full_name"),
            company=user.get("company"),
            plan=user.get("plan", "free"),
            stripe_customer_id=user.get("stripe_customer_id"),
            email_verified=user.get("email_verified", False),
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_request.refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=user_response
        )

    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise


@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Logout current user

    Note: Since we're using JWT tokens (stateless), logout is handled client-side
    by removing the token. This endpoint is here for completeness and could be
    extended to implement token blacklisting if needed.
    """
    user_id = current_user.get("sub")
    logger.info(f"User logged out: {user_id}")

    return {
        "message": "Logged out successfully",
        "user_id": user_id
    }


@router.delete("/delete-account")
async def delete_user_account(
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Delete user account (GDPR compliance)

    This performs a soft delete by anonymizing user data.
    """
    try:
        user_id = current_user.get("sub")

        success = await auth_service.delete_user(user_id)

        if not success:
            raise DatabaseError(detail="Failed to delete account")

        logger.info(f"User account deleted: {user_id}")

        return {
            "message": "Account deleted successfully",
            "user_id": user_id
        }

    except Exception as e:
        logger.error(f"Failed to delete account: {e}")
        raise
