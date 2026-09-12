"""
Usage tracking and plan-based rate limiting service
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import Request
import logging
from supabase import Client

logger = logging.getLogger(__name__)


# Plan configurations
PLAN_LIMITS = {
    "free": {
        "api_calls_per_day": 100,
        "websites_limit": 1,
        "schema_generations_per_month": 10,
        "visibility_checks_per_month": 50,
        "pdf_reports_per_month": 5,
        "api_access": False
    },
    "starter": {
        "api_calls_per_day": 100,
        "websites_limit": 1,
        "schema_generations_per_month": 100,
        "visibility_checks_per_month": 500,
        "pdf_reports_per_month": 50,
        "api_access": True
    },
    "professional": {
        "api_calls_per_day": 1000,
        "websites_limit": 5,
        "schema_generations_per_month": 1000,
        "visibility_checks_per_month": 5000,
        "pdf_reports_per_month": 500,
        "api_access": True
    },
    "agency": {
        "api_calls_per_day": 10000,
        "websites_limit": 50,
        "schema_generations_per_month": 10000,
        "visibility_checks_per_month": 50000,
        "pdf_reports_per_month": 5000,
        "api_access": True
    }
}


class UsageTracker:
    """Track API usage and enforce plan limits"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    def get_plan_limits(self, plan: str) -> Dict[str, Any]:
        """Get limits for a specific plan"""
        return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

    async def track_request(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        request: Request
    ) -> bool:
        """
        Track API request usage

        Args:
            user_id: User ID making the request
            endpoint: API endpoint path
            method: HTTP method
            status_code: Response status code
            response_time_ms: Response time in milliseconds
            request: FastAPI request object

        Returns:
            True if tracked successfully
        """
        try:
            usage_data = {
                "user_id": user_id,
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", "unknown"),
                "created_at": datetime.utcnow().isoformat()
            }

            self.supabase.table("usage_tracking").insert(usage_data).execute()

            logger.debug(f"Tracked request for user {user_id}: {method} {endpoint}")
            return True

        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
            return False

    async def check_daily_limit(self, user_id: str, plan: str) -> tuple[bool, Dict[str, Any]]:
        """
        Check if user is within daily API call limit

        Returns:
            (allowed, info) tuple
        """
        try:
            limits = self.get_plan_limits(plan)
            daily_limit = limits["api_calls_per_day"]

            # Get today's usage
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

            result = self.supabase.table("usage_tracking").select(
                "id", count="exact"
            ).eq("user_id", user_id).gte(
                "created_at", today_start.isoformat()
            ).execute()

            current_count = result.count or 0

            remaining = max(0, daily_limit - current_count)
            allowed = current_count < daily_limit

            return allowed, {
                "allowed": allowed,
                "current": current_count,
                "limit": daily_limit,
                "remaining": remaining,
                "reset": (today_start + timedelta(days=1)).isoformat(),
                "plan": plan
            }

        except Exception as e:
            logger.error(f"Failed to check daily limit: {e}")
            # Allow request on error to prevent blocking users
            return True, {"allowed": True, "error": str(e)}

    async def check_monthly_limit(
        self,
        user_id: str,
        plan: str,
        feature: str
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if user is within monthly feature limit

        Args:
            user_id: User ID
            plan: User's subscription plan
            feature: Feature type (schema_generations, visibility_checks, pdf_reports)

        Returns:
            (allowed, info) tuple
        """
        try:
            limits = self.get_plan_limits(plan)
            limit_key = f"{feature}_per_month"
            monthly_limit = limits.get(limit_key, 0)

            # Get this month's usage
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Map feature to endpoint pattern
            endpoint_patterns = {
                "schema_generations": "/v1/schema/generate",
                "visibility_checks": "/v1/visibility/check",
                "pdf_reports": "/v1/reports/generate"
            }

            endpoint = endpoint_patterns.get(feature)
            if not endpoint:
                logger.error(f"Unknown feature: {feature}")
                return True, {"allowed": True, "error": "Unknown feature"}

            result = self.supabase.table("usage_tracking").select(
                "id", count="exact"
            ).eq("user_id", user_id).eq("endpoint", endpoint).gte(
                "created_at", month_start.isoformat()
            ).execute()

            current_count = result.count or 0

            remaining = max(0, monthly_limit - current_count)
            allowed = current_count < monthly_limit

            # Calculate next reset (first day of next month)
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)

            return allowed, {
                "allowed": allowed,
                "current": current_count,
                "limit": monthly_limit,
                "remaining": remaining,
                "reset": next_month.isoformat(),
                "plan": plan,
                "feature": feature
            }

        except Exception as e:
            logger.error(f"Failed to check monthly limit: {e}")
            return True, {"allowed": True, "error": str(e)}

    async def check_website_limit(self, user_id: str, plan: str) -> tuple[bool, Dict[str, Any]]:
        """
        Check if user can add more websites

        Returns:
            (allowed, info) tuple
        """
        try:
            limits = self.get_plan_limits(plan)
            website_limit = limits["websites_limit"]

            # Get current website count
            result = self.supabase.table("websites").select(
                "id", count="exact"
            ).eq("user_id", user_id).execute()

            current_count = result.count or 0

            remaining = max(0, website_limit - current_count)
            allowed = current_count < website_limit

            return allowed, {
                "allowed": allowed,
                "current": current_count,
                "limit": website_limit,
                "remaining": remaining,
                "plan": plan
            }

        except Exception as e:
            logger.error(f"Failed to check website limit: {e}")
            return True, {"allowed": True, "error": str(e)}

    async def get_usage_summary(self, user_id: str, plan: str) -> Dict[str, Any]:
        """
        Get comprehensive usage summary for user

        Returns:
            Dictionary with usage statistics
        """
        try:
            limits = self.get_plan_limits(plan)

            # Daily API calls
            daily_allowed, daily_info = await self.check_daily_limit(user_id, plan)

            # Schema generations
            schema_allowed, schema_info = await self.check_monthly_limit(
                user_id, plan, "schema_generations"
            )

            # Visibility checks
            visibility_allowed, visibility_info = await self.check_monthly_limit(
                user_id, plan, "visibility_checks"
            )

            # PDF reports
            pdf_allowed, pdf_info = await self.check_monthly_limit(
                user_id, plan, "pdf_reports"
            )

            # Websites
            website_allowed, website_info = await self.check_website_limit(user_id, plan)

            return {
                "plan": plan,
                "plan_limits": limits,
                "daily_api_calls": daily_info,
                "schema_generations": schema_info,
                "visibility_checks": visibility_info,
                "pdf_reports": pdf_info,
                "websites": website_info,
                "api_access_enabled": limits["api_access"]
            }

        except Exception as e:
            logger.error(f"Failed to get usage summary: {e}")
            return {
                "plan": plan,
                "error": str(e)
            }

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"


async def create_usage_tracker(supabase_client: Client) -> UsageTracker:
    """Create usage tracker instance"""
    return UsageTracker(supabase_client)
