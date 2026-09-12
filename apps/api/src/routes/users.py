"""
User management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from supabase import create_client, Client

from ..config import settings
from ..models.auth import (
    UserResponse,
    UsageStats,
    ApiKeyCreate,
    ApiKeyResponse,
    UserWebsitesResponse
)
from ..services.auth_service import AuthenticationService
from ..middleware.auth import get_current_user
from ..utils.exceptions import ResourceNotFoundError, DatabaseError, PlanLimitError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/users", tags=["users"])


async def get_supabase_client() -> Client:
    """Get Supabase client"""
    return create_client(settings.supabase_url, settings.supabase_key)


async def get_auth_service(
    supabase: Client = Depends(get_supabase_client)
) -> AuthenticationService:
    """Get authentication service"""
    return AuthenticationService(supabase)


@router.get("/me", response_model=UserResponse)
async def get_user_details(
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Get current user details

    Returns detailed user information including subscription plan.
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
        logger.error(f"Failed to get user details: {e}")
        raise


@router.get("/me/websites", response_model=UserWebsitesResponse)
async def get_user_websites(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List user's registered websites

    Returns paginated list of websites with their visibility scores.
    """
    try:
        user_id = current_user.get("sub")
        plan = current_user.get("plan", "free")

        # Plan limits
        plan_limits = {
            "free": 1,
            "starter": 1,
            "professional": 5,
            "agency": 50
        }

        limit = plan_limits.get(plan, 1)

        # Calculate pagination
        offset = (page - 1) * page_size

        # Get user's websites
        result = supabase.table("websites").select("*").eq("user_id", user_id).order(
            "created_at", desc=True
        ).range(offset, offset + page_size - 1).execute()

        websites = result.data or []

        # Get total count
        count_result = supabase.table("websites").select("id", count="exact").eq("user_id", user_id).execute()
        total = count_result.count or 0

        return UserWebsitesResponse(
            websites=websites,
            total=total,
            plan_limit=limit
        )

    except Exception as e:
        logger.error(f"Failed to get user websites: {e}")
        raise DatabaseError(detail="Failed to retrieve websites")


@router.get("/me/usage", response_model=UsageStats)
async def get_usage_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get current user's usage statistics

    Returns API usage, limits, and billing period information.
    """
    try:
        user_id = current_user.get("sub")
        plan = current_user.get("plan", "free")

        # Plan limits for API calls per day
        plan_limits = {
            "free": 100,
            "starter": 100,
            "professional": 1000,
            "agency": 10000
        }

        api_calls_limit = plan_limits.get(plan, 100)

        # Get current billing period
        # For free users, period is monthly
        # For paid users, get from subscription
        period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if plan != "free":
            # Get subscription billing period
            sub_result = supabase.table("subscriptions").select(
                "current_period_start, current_period_end"
            ).eq("user_id", user_id).eq("status", "active").execute()

            if sub_result.data:
                period_start = datetime.fromisoformat(sub_result.data[0]["current_period_start"])
                period_end = datetime.fromisoformat(sub_result.data[0]["current_period_end"])
            else:
                period_end = period_start + timedelta(days=30)
        else:
            period_end = period_start + timedelta(days=30)

        # Get usage stats from usage_tracking table
        usage_result = supabase.table("usage_tracking").select("*").eq(
            "user_id", user_id
        ).gte("created_at", period_start.isoformat()).execute()

        # Calculate totals
        api_calls = len(usage_result.data) if usage_result.data else 0
        schema_generations = sum(
            1 for item in (usage_result.data or [])
            if item.get("endpoint") == "/v1/schema/generate"
        )
        visibility_checks = sum(
            1 for item in (usage_result.data or [])
            if item.get("endpoint") == "/v1/visibility/check"
        )

        # Get website count
        websites_result = supabase.table("websites").select("id", count="exact").eq("user_id", user_id).execute()
        websites_count = websites_result.count or 0

        # TODO: Calculate storage used (PDFs, reports, etc.)
        storage_used_mb = 0.0

        return UsageStats(
            api_calls=api_calls,
            schema_generations=schema_generations,
            visibility_checks=visibility_checks,
            websites_count=websites_count,
            storage_used_mb=storage_used_mb,
            api_calls_limit=api_calls_limit,
            period_start=period_start,
            period_end=period_end
        )

    except Exception as e:
        logger.error(f"Failed to get usage statistics: {e}")
        raise DatabaseError(detail="Failed to retrieve usage statistics")


@router.delete("/me")
async def delete_account(
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Delete user account (GDPR compliance)

    Performs soft delete by anonymizing user data.
    All associated data (websites, API keys) will be removed.
    """
    try:
        user_id = current_user.get("sub")

        # Delete user
        success = await auth_service.delete_user(user_id)

        if not success:
            raise DatabaseError(detail="Failed to delete account")

        logger.info(f"User account deleted: {user_id}")

        return {
            "message": "Account deleted successfully. All data has been anonymized.",
            "user_id": user_id
        }

    except Exception as e:
        logger.error(f"Failed to delete account: {e}")
        raise


@router.post("/me/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create a new API key

    - **name**: Descriptive name for the API key
    - **scopes**: Optional list of allowed scopes

    Returns the API key (shown only once - save it securely!).
    """
    try:
        user_id = current_user.get("sub")

        # Check existing API keys count
        keys_result = supabase.table("api_keys").select("id", count="exact").eq(
            "user_id", user_id
        ).eq("active", True).execute()

        if keys_result.count and keys_result.count >= 10:
            raise PlanLimitError(detail="Maximum number of API keys reached (10)")

        # Create API key
        key = await auth_service.create_api_key(
            user_id=user_id,
            name=key_data.name,
            scopes=key_data.scopes
        )

        logger.info(f"API key created for user: {user_id}")

        return ApiKeyResponse(
            id=key["id"],
            name=key["name"],
            key=key.get("key"),  # Full key, shown only once
            key_prefix=key["key_prefix"],
            scopes=key.get("scopes"),
            last_used=None,
            created_at=key["created_at"],
            active=True
        )

    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise


@router.get("/me/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    List user's API keys

    Returns list of API keys (without the actual key values).
    """
    try:
        user_id = current_user.get("sub")

        # Get API keys
        result = supabase.table("api_keys").select("*").eq(
            "user_id", user_id
        ).eq("active", True).order("created_at", desc=True).execute()

        keys = result.data or []

        return [
            ApiKeyResponse(
                id=key["id"],
                name=key["name"],
                key=None,  # Never return the full key
                key_prefix=key["key_prefix"],
                scopes=key.get("scopes"),
                last_used=key.get("last_used"),
                created_at=key["created_at"],
                active=key.get("active", True)
            )
            for key in keys
        ]

    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise DatabaseError(detail="Failed to retrieve API keys")


@router.delete("/me/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Revoke/delete an API key

    The API key will be deactivated immediately.
    """
    try:
        user_id = current_user.get("sub")

        # Verify ownership and deactivate
        result = supabase.table("api_keys").update({
            "active": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", key_id).eq("user_id", user_id).execute()

        if not result.data:
            raise ResourceNotFoundError(resource="API key")

        logger.info(f"API key revoked: {key_id}")

        return {
            "message": "API key revoked successfully",
            "key_id": key_id
        }

    except Exception as e:
        logger.error(f"Failed to revoke API key: {e}")
        raise DatabaseError(detail="Failed to revoke API key")
