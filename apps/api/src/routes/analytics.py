"""
Analytics routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from supabase import Client
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List
from collections import defaultdict

from ..models.publisher import PublisherAnalytics
from ..middleware.auth import get_api_key
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/analytics", tags=["analytics"])
limiter = Limiter(key_func=get_remote_address)


# Dependency for Supabase client
async def get_supabase_client() -> Client:
    """Get Supabase client"""
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_key)


@router.get("", response_model=PublisherAnalytics)
@limiter.limit(settings.rate_limit_per_minute)
async def get_publisher_analytics(
    request: Request,
    domain: str = None,
    days: int = 30,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
) -> PublisherAnalytics:
    """
    Get analytics for a publisher

    Returns aggregate statistics including total receipts, verification rates,
    and daily breakdown over the specified time period.
    """
    try:
        if not domain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain parameter is required"
            )

        # Verify publisher exists
        publisher = supabase.table("publishers").select("*").eq(
            "domain", domain
        ).execute()

        if not publisher.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publisher not found"
            )

        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get all receipts for publisher in date range
        receipts_query = supabase.table("receipts").select("*").eq(
            "publisher_domain", domain
        ).gte(
            "timestamp", start_date.isoformat()
        ).lte(
            "timestamp", end_date.isoformat()
        ).execute()

        receipts = receipts_query.data

        # Calculate statistics
        total_receipts = len(receipts)
        verified_receipts = sum(1 for r in receipts if r.get("verified", False))
        failed_receipts = sum(1 for r in receipts if not r.get("verified", False))

        # Get first and last receipt times
        first_receipt_at = None
        last_receipt_at = None

        if receipts:
            timestamps = [datetime.fromisoformat(r["timestamp"]) for r in receipts]
            first_receipt_at = min(timestamps)
            last_receipt_at = max(timestamps)

        # Calculate daily breakdown
        daily_breakdown = defaultdict(int)
        for receipt in receipts:
            date_key = datetime.fromisoformat(receipt["timestamp"]).date().isoformat()
            daily_breakdown[date_key] += 1

        return PublisherAnalytics(
            domain=domain,
            total_receipts=total_receipts,
            verified_receipts=verified_receipts,
            failed_receipts=failed_receipts,
            first_receipt_at=first_receipt_at,
            last_receipt_at=last_receipt_at,
            daily_breakdown=dict(daily_breakdown)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )


@router.get("/summary")
@limiter.limit(settings.rate_limit_per_minute)
async def get_system_analytics(
    request: Request,
    days: int = 30,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get system-wide analytics

    Returns aggregate statistics across all publishers including total receipts,
    verified publishers count, and system-wide verification rates.
    """
    try:
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get verified publishers count
        publishers_query = supabase.table("publishers").select(
            "*", count="exact"
        ).eq("verified", True).execute()

        verified_publishers = publishers_query.count or 0

        # Get receipts in date range
        receipts_query = supabase.table("receipts").select(
            "*", count="exact"
        ).gte(
            "timestamp", start_date.isoformat()
        ).lte(
            "timestamp", end_date.isoformat()
        ).execute()

        total_receipts = receipts_query.count or 0
        receipts = receipts_query.data

        verified_receipts = sum(1 for r in receipts if r.get("verified", False))
        failed_receipts = sum(1 for r in receipts if not r.get("verified", False))

        # Calculate daily breakdown
        daily_breakdown = defaultdict(int)
        for receipt in receipts:
            date_key = datetime.fromisoformat(receipt["timestamp"]).date().isoformat()
            daily_breakdown[date_key] += 1

        # Get unique publishers
        unique_publishers = len(set(r["publisher_domain"] for r in receipts))

        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "verified_publishers": verified_publishers,
            "active_publishers": unique_publishers,
            "total_receipts": total_receipts,
            "verified_receipts": verified_receipts,
            "failed_receipts": failed_receipts,
            "verification_rate": verified_receipts / total_receipts if total_receipts > 0 else 0,
            "daily_breakdown": dict(daily_breakdown)
        }

    except Exception as e:
        logger.error(f"System analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system analytics: {str(e)}"
        )
