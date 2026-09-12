"""
Website CRUD routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from supabase import Client
from datetime import datetime
import logging
from typing import Optional
from urllib.parse import urlparse

from ..models.schema import (
    WebsiteCreate,
    WebsiteResponse,
    WebsiteListResponse,
    WebsiteUpdateRequest
)
from ..middleware.auth import get_api_key, optional_auth
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/websites", tags=["websites"])
limiter = Limiter(key_func=get_remote_address)


# Dependency for Supabase client
async def get_supabase_client() -> Client:
    """Get Supabase client"""
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_key)


@router.post("", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_per_minute)
async def create_or_get_website(
    request: Request,
    website: WebsiteCreate,
    user: Optional[str] = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> WebsiteResponse:
    """
    Create a new website or return existing one

    Creates a website record in the database. If the domain already exists,
    returns the existing website instead of creating a duplicate.

    This endpoint supports both authenticated and anonymous access.
    """
    try:
        # Extract domain from URL if not provided correctly
        parsed_url = urlparse(str(website.url))
        domain = parsed_url.netloc.replace('www.', '')

        # Override the domain with the parsed one to ensure consistency
        website.domain = domain

        # Check if website already exists
        existing = supabase.table("websites").select("*").eq(
            "domain", domain
        ).execute()

        if existing.data:
            # Return existing website
            existing_website = existing.data[0]
            logger.info(f"Website already exists, returning existing: {domain}")

            # Get latest visibility
            visibility_check = supabase.table("ai_mentions").select(
                "visibility_score, checked_at"
            ).eq("website_id", existing_website['id']).order(
                "checked_at", desc=True
            ).limit(1).execute()

            visibility_score = None
            last_visibility_check = None

            if visibility_check.data:
                visibility_score = visibility_check.data[0].get('visibility_score')
                checked_at = visibility_check.data[0].get('checked_at')
                if checked_at:
                    last_visibility_check = datetime.fromisoformat(checked_at)

            schema_generated_at = None
            if existing_website.get('schema_generated_at'):
                schema_generated_at = datetime.fromisoformat(
                    existing_website['schema_generated_at']
                )

            return WebsiteResponse(
                id=existing_website['id'],
                domain=existing_website['domain'],
                url=existing_website['url'],
                business_name=existing_website.get('business_name'),
                business_type=existing_website.get('business_type'),
                keywords=existing_website.get('keywords'),
                location=existing_website.get('location'),
                schema_markup=existing_website.get('schema_markup'),
                visibility_score=visibility_score,
                last_visibility_check=last_visibility_check,
                schema_generated_at=schema_generated_at,
                created_at=datetime.fromisoformat(existing_website['created_at']),
                updated_at=datetime.fromisoformat(existing_website['updated_at'])
            )

        # Create website record
        now = datetime.utcnow().isoformat()
        website_data = {
            "domain": domain,
            "url": str(website.url),
            "business_name": website.business_name,
            "business_type": website.business_type,
            "keywords": website.keywords,
            "location": website.location,
            "schema_markup": website.schema_markup,
            "created_at": now,
            "updated_at": now
        }

        # Add user_id if authenticated
        if user:
            website_data["user_id"] = user

        if website.schema_markup:
            website_data["schema_generated_at"] = now

        result = supabase.table("websites").insert(website_data).execute()

        if not result.data:
            raise Exception("Failed to create website record")

        created_website = result.data[0]

        logger.info(f"Created new website: {domain}")

        return WebsiteResponse(
            id=created_website['id'],
            domain=created_website['domain'],
            url=created_website['url'],
            business_name=created_website.get('business_name'),
            business_type=created_website.get('business_type'),
            keywords=created_website.get('keywords'),
            location=created_website.get('location'),
            schema_markup=created_website.get('schema_markup'),
            visibility_score=None,
            last_visibility_check=None,
            schema_generated_at=datetime.fromisoformat(now) if website.schema_markup else None,
            created_at=datetime.fromisoformat(created_website['created_at']),
            updated_at=datetime.fromisoformat(created_website['updated_at'])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating website: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create website: {str(e)}"
        )


@router.get("/{website_id}", response_model=WebsiteResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def get_website(
    request: Request,
    website_id: str,
    user: Optional[str] = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> WebsiteResponse:
    """
    Get website by ID

    Returns the website's details including schema markup,
    business information, and latest visibility data.
    """
    try:
        # Fetch website from database
        website = supabase.table("websites").select("*").eq(
            "id", website_id
        ).execute()

        if not website.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website with ID {website_id} not found"
            )

        website_data = website.data[0]

        # Get latest visibility check if available
        visibility_check = supabase.table("ai_mentions").select(
            "visibility_score, checked_at"
        ).eq("website_id", website_id).order(
            "checked_at", desc=True
        ).limit(1).execute()

        visibility_score = None
        last_visibility_check = None

        if visibility_check.data:
            visibility_score = visibility_check.data[0].get('visibility_score')
            checked_at = visibility_check.data[0].get('checked_at')
            if checked_at:
                last_visibility_check = datetime.fromisoformat(checked_at)

        # Parse timestamps
        created_at = datetime.fromisoformat(website_data['created_at'])
        updated_at = datetime.fromisoformat(website_data['updated_at'])
        schema_generated_at = None
        if website_data.get('schema_generated_at'):
            schema_generated_at = datetime.fromisoformat(
                website_data['schema_generated_at']
            )

        return WebsiteResponse(
            id=website_data['id'],
            domain=website_data['domain'],
            url=website_data['url'],
            business_name=website_data.get('business_name'),
            business_type=website_data.get('business_type'),
            keywords=website_data.get('keywords'),
            location=website_data.get('location'),
            schema_markup=website_data.get('schema_markup'),
            visibility_score=visibility_score,
            last_visibility_check=last_visibility_check,
            schema_generated_at=schema_generated_at,
            created_at=created_at,
            updated_at=updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching website: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch website: {str(e)}"
        )


@router.get("", response_model=WebsiteListResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def list_websites(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    user: Optional[str] = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> WebsiteListResponse:
    """
    List websites

    Returns a paginated list of websites. If authenticated, filters by user.
    If anonymous, returns all public websites.
    """
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        # Calculate offset
        offset = (page - 1) * page_size

        # Build query - filter by user if authenticated
        query = supabase.table("websites").select("*", count="exact")

        if user:
            query = query.eq("user_id", user)

        # Get total count
        count_result = query.execute()
        total = count_result.count or 0

        # Get paginated websites
        websites_query = supabase.table("websites").select("*")

        if user:
            websites_query = websites_query.eq("user_id", user)

        websites_result = websites_query.order(
            "created_at", desc=True
        ).range(offset, offset + page_size - 1).execute()

        websites = []
        for website_data in websites_result.data:
            # Get latest visibility for each website
            visibility_check = supabase.table("ai_mentions").select(
                "visibility_score, checked_at"
            ).eq("website_id", website_data['id']).order(
                "checked_at", desc=True
            ).limit(1).execute()

            visibility_score = None
            last_visibility_check = None

            if visibility_check.data:
                visibility_score = visibility_check.data[0].get('visibility_score')
                checked_at = visibility_check.data[0].get('checked_at')
                if checked_at:
                    last_visibility_check = datetime.fromisoformat(checked_at)

            schema_generated_at = None
            if website_data.get('schema_generated_at'):
                schema_generated_at = datetime.fromisoformat(
                    website_data['schema_generated_at']
                )

            websites.append(
                WebsiteResponse(
                    id=website_data['id'],
                    domain=website_data['domain'],
                    url=website_data['url'],
                    business_name=website_data.get('business_name'),
                    business_type=website_data.get('business_type'),
                    keywords=website_data.get('keywords'),
                    location=website_data.get('location'),
                    schema_markup=website_data.get('schema_markup'),
                    visibility_score=visibility_score,
                    last_visibility_check=last_visibility_check,
                    schema_generated_at=schema_generated_at,
                    created_at=datetime.fromisoformat(website_data['created_at']),
                    updated_at=datetime.fromisoformat(website_data['updated_at'])
                )
            )

        logger.info(f"Listed {len(websites)} websites (total: {total})")

        return WebsiteListResponse(
            websites=websites,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error listing websites: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list websites: {str(e)}"
        )


@router.put("/{website_id}", response_model=WebsiteResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def update_website(
    request: Request,
    website_id: str,
    update_data: WebsiteUpdateRequest,
    user: Optional[str] = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> WebsiteResponse:
    """
    Update website information

    Updates business details, keywords, location, or schema markup
    for an existing website.
    """
    try:
        # Check if website exists
        existing = supabase.table("websites").select("*").eq(
            "id", website_id
        ).execute()

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website with ID {website_id} not found"
            )

        # Build update data
        update_fields = {"updated_at": datetime.utcnow().isoformat()}

        if update_data.business_name is not None:
            update_fields["business_name"] = update_data.business_name
        if update_data.business_type is not None:
            update_fields["business_type"] = update_data.business_type
        if update_data.keywords is not None:
            update_fields["keywords"] = update_data.keywords
        if update_data.location is not None:
            update_fields["location"] = update_data.location
        if update_data.schema_markup is not None:
            update_fields["schema_markup"] = update_data.schema_markup
            update_fields["schema_generated_at"] = datetime.utcnow().isoformat()

        # Update website
        result = supabase.table("websites").update(update_fields).eq(
            "id", website_id
        ).execute()

        if not result.data:
            raise Exception("Failed to update website")

        updated_website = result.data[0]

        logger.info(f"Updated website: {website_id}")

        # Get latest visibility
        visibility_check = supabase.table("ai_mentions").select(
            "visibility_score, checked_at"
        ).eq("website_id", website_id).order(
            "checked_at", desc=True
        ).limit(1).execute()

        visibility_score = None
        last_visibility_check = None

        if visibility_check.data:
            visibility_score = visibility_check.data[0].get('visibility_score')
            checked_at = visibility_check.data[0].get('checked_at')
            if checked_at:
                last_visibility_check = datetime.fromisoformat(checked_at)

        schema_generated_at = None
        if updated_website.get('schema_generated_at'):
            schema_generated_at = datetime.fromisoformat(
                updated_website['schema_generated_at']
            )

        return WebsiteResponse(
            id=updated_website['id'],
            domain=updated_website['domain'],
            url=updated_website['url'],
            business_name=updated_website.get('business_name'),
            business_type=updated_website.get('business_type'),
            keywords=updated_website.get('keywords'),
            location=updated_website.get('location'),
            schema_markup=updated_website.get('schema_markup'),
            visibility_score=visibility_score,
            last_visibility_check=last_visibility_check,
            schema_generated_at=schema_generated_at,
            created_at=datetime.fromisoformat(updated_website['created_at']),
            updated_at=datetime.fromisoformat(updated_website['updated_at'])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating website: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update website: {str(e)}"
        )


@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(settings.rate_limit_per_minute)
async def delete_website(
    request: Request,
    website_id: str,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete website

    Removes a website record from the database.
    Requires authentication.

    Note: This will also delete all associated visibility checks
    if CASCADE is configured in the database.
    """
    try:
        # Verify the website exists
        website = supabase.table("websites").select("*").eq(
            "id", website_id
        ).execute()

        if not website.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website with ID {website_id} not found"
            )

        # Delete the website
        supabase.table("websites").delete().eq("id", website_id).execute()

        logger.info(f"Deleted website {website_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting website: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete website: {str(e)}"
        )
