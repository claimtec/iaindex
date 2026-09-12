"""
AI Visibility tracking routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from supabase import Client
from datetime import datetime
import logging
from typing import Optional, List
import uuid

from ..models.visibility import (
    VisibilityCheckRequest,
    VisibilityCheckResponse,
    VisibilityHistory,
    VisibilityHistoryItem,
    VisibilityTrend,
    VisibilityDetailedResponse,
    AIMention,
    AIPlatform
)
from ..services.ai_visibility import AIVisibilityService
from ..middleware.auth import get_api_key, optional_auth
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/visibility", tags=["visibility"])
limiter = Limiter(key_func=get_remote_address)


# Dependency for Supabase client
async def get_supabase_client() -> Client:
    """Get Supabase client"""
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_key)


@router.post("/check", response_model=VisibilityCheckResponse)
@limiter.limit("10/hour")  # More restrictive rate limit for visibility checks
async def check_visibility(
    request: Request,
    visibility_request: VisibilityCheckRequest,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
) -> VisibilityCheckResponse:
    """
    Check website visibility in AI search engines

    Queries ChatGPT Search, Perplexity, and other AI platforms to check
    if the website appears in search results for given queries.

    Returns visibility score (0-100) and detailed mention information.

    Rate limited to 10 checks per hour to manage API costs.
    """
    try:
        # Fetch website from database
        website = supabase.table("websites").select("*").eq(
            "id", visibility_request.website_id
        ).execute()

        if not website.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website with ID {visibility_request.website_id} not found"
            )

        website_data = website.data[0]
        url = website_data['url']
        domain = website_data['domain']

        # Determine queries to use
        queries = visibility_request.queries
        if not queries:
            # Use keywords if available, otherwise generate basic queries
            keywords = website_data.get('keywords', [])
            if keywords:
                queries = keywords[:10]  # Limit to 10 queries
            else:
                # Generate basic queries from business info
                queries = []
                business_name = website_data.get('business_name')
                business_type = website_data.get('business_type')

                if business_name:
                    queries.append(business_name)
                if business_type and business_name:
                    queries.append(f"{business_name} {business_type}")
                if domain:
                    queries.append(domain.replace('.', ' '))

                if not queries:
                    queries = [domain]

        # Determine platforms to check
        platforms = visibility_request.platforms
        if platforms:
            # Convert string enum values to enum objects
            platform_enums = [AIPlatform(p) for p in platforms]
        else:
            platform_enums = None  # Will default to all in service

        # Initialize visibility service
        visibility_service = AIVisibilityService()

        logger.info(
            f"Checking visibility for {domain} with {len(queries)} queries"
        )

        # Perform visibility check
        check_result = await visibility_service.check_visibility(
            url=url,
            queries=queries,
            platforms=platform_enums
        )

        # Convert mentions to Pydantic models
        mentions = [
            AIMention(
                platform=m['platform'],
                query=m['query'],
                mentioned=m['mentioned'],
                position=m.get('position'),
                context_snippet=m.get('context_snippet'),
                citation_url=m.get('citation_url'),
                checked_at=datetime.fromisoformat(m['checked_at'])
            )
            for m in check_result['mentions']
        ]

        # Save results to database
        mention_records = []
        for mention in check_result['mentions']:
            mention_record = {
                "id": str(uuid.uuid4()),
                "website_id": visibility_request.website_id,
                "platform": mention['platform'],
                "query": mention['query'],
                "mentioned": mention['mentioned'],
                "position": mention.get('position'),
                "context_snippet": mention.get('context_snippet'),
                "citation_url": mention.get('citation_url'),
                "visibility_score": check_result['visibility_score'],
                "checked_at": mention['checked_at'],
                "created_at": datetime.utcnow().isoformat()
            }
            mention_records.append(mention_record)

        # Batch insert mentions
        if mention_records:
            supabase.table("ai_mentions").insert(mention_records).execute()

        # Update website with latest visibility score
        supabase.table("websites").update({
            "visibility_score": check_result['visibility_score'],
            "last_visibility_check": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", visibility_request.website_id).execute()

        logger.info(
            f"Visibility check completed for {domain}: "
            f"score={check_result['visibility_score']}, "
            f"mentions={check_result['total_mentions']}"
        )

        return VisibilityCheckResponse(
            visibility_score=check_result['visibility_score'],
            mentions=mentions,
            platform_scores=check_result['platform_scores'],
            total_mentions=check_result['total_mentions'],
            checked_at=datetime.fromisoformat(check_result['checked_at']),
            queries_tested=check_result['queries_tested'],
            platforms_checked=check_result['platforms_checked']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Visibility check error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check visibility: {str(e)}"
        )


@router.get("/{website_id}", response_model=VisibilityDetailedResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def get_visibility(
    request: Request,
    website_id: str,
    user: Optional[str] = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> VisibilityDetailedResponse:
    """
    Get latest visibility check results with historical data

    Returns the most recent visibility check along with historical
    trends and analysis.
    """
    try:
        # Fetch website
        website = supabase.table("websites").select("*").eq(
            "id", website_id
        ).execute()

        if not website.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website with ID {website_id} not found"
            )

        website_data = website.data[0]

        # Get latest visibility check
        latest_check = supabase.table("ai_mentions").select("*").eq(
            "website_id", website_id
        ).order("checked_at", desc=True).limit(1).execute()

        if not latest_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No visibility checks found for website {website_id}"
            )

        latest_mention = latest_check.data[0]

        # Get all mentions from the same check (same checked_at timestamp)
        checked_at = latest_mention['checked_at']
        all_mentions = supabase.table("ai_mentions").select("*").eq(
            "website_id", website_id
        ).eq("checked_at", checked_at).execute()

        # Convert mentions to response format
        mentions = [
            AIMention(
                platform=m['platform'],
                query=m['query'],
                mentioned=m['mentioned'],
                position=m.get('position'),
                context_snippet=m.get('context_snippet'),
                citation_url=m.get('citation_url'),
                checked_at=datetime.fromisoformat(m['checked_at'])
            )
            for m in all_mentions.data
        ]

        # Calculate platform scores from mentions
        platform_scores = {}
        platform_mentions_dict = {}
        for mention in all_mentions.data:
            platform = mention['platform']
            if platform not in platform_mentions_dict:
                platform_mentions_dict[platform] = []
            platform_mentions_dict[platform].append(mention)

        visibility_service = AIVisibilityService()
        for platform, p_mentions in platform_mentions_dict.items():
            platform_scores[platform] = visibility_service._calculate_platform_score(
                p_mentions
            )

        # Get queries tested
        queries_tested = list(set([m['query'] for m in all_mentions.data]))
        platforms_checked = list(set([m['platform'] for m in all_mentions.data]))

        current_check = VisibilityCheckResponse(
            visibility_score=latest_mention['visibility_score'],
            mentions=mentions,
            platform_scores=platform_scores,
            total_mentions=len(all_mentions.data),
            checked_at=datetime.fromisoformat(checked_at),
            queries_tested=queries_tested,
            platforms_checked=platforms_checked
        )

        # Get historical data
        history_data = await visibility_service.get_historical_visibility(
            website_id=website_id,
            supabase_client=supabase
        )

        # Convert checks to VisibilityHistoryItem
        history_items = []
        seen_timestamps = set()

        for check in history_data['checks']:
            timestamp = check['checked_at']
            if timestamp not in seen_timestamps:
                seen_timestamps.add(timestamp)

                # Get all mentions for this timestamp
                check_mentions = supabase.table("ai_mentions").select("*").eq(
                    "website_id", website_id
                ).eq("checked_at", timestamp).execute()

                platforms = list(set([m['platform'] for m in check_mentions.data]))

                history_items.append(
                    VisibilityHistoryItem(
                        id=check['id'],
                        visibility_score=check['visibility_score'],
                        total_mentions=len(check_mentions.data),
                        platforms_checked=platforms,
                        checked_at=datetime.fromisoformat(timestamp)
                    )
                )

        history = VisibilityHistory(
            checks=history_items,
            average_score=history_data['average_score'],
            trend=VisibilityTrend(history_data['trend']),
            total_checks=history_data['total_checks'],
            highest_score=history_data['highest_score'],
            lowest_score=history_data['lowest_score'],
            last_checked=datetime.fromisoformat(
                history_data['last_checked']
            ) if history_data['last_checked'] else None
        )

        website_info = {
            'id': website_data['id'],
            'domain': website_data['domain'],
            'url': website_data['url'],
            'business_name': website_data.get('business_name'),
            'business_type': website_data.get('business_type')
        }

        return VisibilityDetailedResponse(
            current=current_check,
            history=history,
            website_info=website_info
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching visibility data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch visibility data: {str(e)}"
        )


@router.get("/{website_id}/history", response_model=VisibilityHistory)
@limiter.limit(settings.rate_limit_per_minute)
async def get_visibility_history(
    request: Request,
    website_id: str,
    limit: int = 20,
    user: Optional[str] = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> VisibilityHistory:
    """
    Get historical visibility data for a website

    Returns historical visibility checks with trend analysis.
    Can limit the number of historical records returned.
    """
    try:
        # Check if website exists
        website = supabase.table("websites").select("id").eq(
            "id", website_id
        ).execute()

        if not website.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website with ID {website_id} not found"
            )

        # Get historical data
        visibility_service = AIVisibilityService()
        history_data = await visibility_service.get_historical_visibility(
            website_id=website_id,
            supabase_client=supabase
        )

        # Convert checks to VisibilityHistoryItem
        history_items = []
        seen_timestamps = set()

        for check in history_data['checks'][:limit]:
            timestamp = check['checked_at']
            if timestamp not in seen_timestamps:
                seen_timestamps.add(timestamp)

                # Get all mentions for this timestamp
                check_mentions = supabase.table("ai_mentions").select("*").eq(
                    "website_id", website_id
                ).eq("checked_at", timestamp).execute()

                platforms = list(set([m['platform'] for m in check_mentions.data]))

                history_items.append(
                    VisibilityHistoryItem(
                        id=check['id'],
                        visibility_score=check['visibility_score'],
                        total_mentions=len(check_mentions.data),
                        platforms_checked=platforms,
                        checked_at=datetime.fromisoformat(timestamp)
                    )
                )

        return VisibilityHistory(
            checks=history_items,
            average_score=history_data['average_score'],
            trend=VisibilityTrend(history_data['trend']),
            total_checks=history_data['total_checks'],
            highest_score=history_data['highest_score'],
            lowest_score=history_data['lowest_score'],
            last_checked=datetime.fromisoformat(
                history_data['last_checked']
            ) if history_data['last_checked'] else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching visibility history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch visibility history: {str(e)}"
        )


@router.delete("/{website_id}/checks/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(settings.rate_limit_per_minute)
async def delete_visibility_check(
    request: Request,
    website_id: str,
    check_id: str,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete a specific visibility check

    Removes a visibility check record from the database.
    Requires authentication.
    """
    try:
        # Verify the check belongs to the website
        check = supabase.table("ai_mentions").select("*").eq(
            "id", check_id
        ).eq("website_id", website_id).execute()

        if not check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Visibility check {check_id} not found for website {website_id}"
            )

        # Delete the check
        supabase.table("ai_mentions").delete().eq("id", check_id).execute()

        logger.info(f"Deleted visibility check {check_id} for website {website_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting visibility check: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete visibility check: {str(e)}"
        )


@router.get("/platforms", response_model=List[str])
@limiter.limit(settings.rate_limit_per_minute)
async def get_supported_platforms(
    request: Request,
    user: Optional[str] = Depends(optional_auth)
) -> List[str]:
    """
    Get list of supported AI platforms

    Returns a list of AI search platforms that can be checked
    for visibility.
    """
    return [platform.value for platform in AIPlatform]


@router.get("/{website_id}/platforms/{platform}", response_model=dict)
@limiter.limit(settings.rate_limit_per_minute)
async def get_platform_visibility(
    request: Request,
    website_id: str,
    platform: str,
    user: Optional[str] = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> dict:
    """
    Get visibility data for a specific platform

    Returns detailed visibility information for a single AI platform,
    including all historical checks and mentions.
    """
    try:
        # Validate platform
        try:
            platform_enum = AIPlatform(platform)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform: {platform}. Supported platforms: "
                       f"{[p.value for p in AIPlatform]}"
            )

        # Check if website exists
        website = supabase.table("websites").select("*").eq(
            "id", website_id
        ).execute()

        if not website.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website with ID {website_id} not found"
            )

        # Get all mentions for this platform
        mentions = supabase.table("ai_mentions").select("*").eq(
            "website_id", website_id
        ).eq("platform", platform).order(
            "checked_at", desc=True
        ).limit(50).execute()

        if not mentions.data:
            return {
                'platform': platform,
                'website_id': website_id,
                'total_mentions': 0,
                'average_score': 0,
                'mentions': []
            }

        # Calculate average score
        scores = [m.get('visibility_score', 0) for m in mentions.data]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Format mentions
        formatted_mentions = [
            {
                'id': m['id'],
                'query': m['query'],
                'mentioned': m['mentioned'],
                'position': m.get('position'),
                'context_snippet': m.get('context_snippet'),
                'citation_url': m.get('citation_url'),
                'checked_at': m['checked_at']
            }
            for m in mentions.data
        ]

        return {
            'platform': platform,
            'website_id': website_id,
            'domain': website.data[0]['domain'],
            'total_mentions': len(mentions.data),
            'average_score': round(avg_score, 1),
            'mentions': formatted_mentions[:20]  # Return last 20 mentions
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching platform visibility: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch platform visibility: {str(e)}"
        )
