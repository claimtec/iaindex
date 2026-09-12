"""
Schema generation and validation routes
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
    SchemaGenerateRequest,
    SchemaGenerateResponse,
    SchemaValidateRequest,
    SchemaValidateResponse,
    WebsiteCreate,
    WebsiteResponse,
    WebsiteListResponse,
    WebsiteUpdateRequest,
    Recommendation
)
from ..services.schema_generator import SchemaGeneratorService
from ..middleware.auth import get_api_key, optional_auth
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/schema", tags=["schema"])
limiter = Limiter(key_func=get_remote_address)


# Dependency for Supabase client
async def get_supabase_client() -> Client:
    """Get Supabase client"""
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_key)


@router.post("/generate", response_model=SchemaGenerateResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def generate_schema(
    request: Request,
    schema_request: SchemaGenerateRequest,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
) -> SchemaGenerateResponse:
    """
    Generate AI-optimized schema markup for a website

    Uses Claude AI to scrape the website and generate comprehensive
    schema.org JSON-LD markup optimized for AI search engines.

    Returns the generated schema along with optimization recommendations.
    """
    try:
        # Initialize schema generator service
        generator = SchemaGeneratorService()

        # Generate schema
        logger.info(f"Generating schema for URL: {schema_request.url}")

        result = await generator.generate_schema(
            url=str(schema_request.url),
            business_type=schema_request.business_type,
            business_name=schema_request.business_name,
            location=schema_request.location
        )

        # Extract domain from URL
        parsed_url = urlparse(str(schema_request.url))
        domain = parsed_url.netloc.replace('www.', '')

        # Check if website exists in database
        existing_website = supabase.table("websites").select("*").eq(
            "domain", domain
        ).execute()

        website_data = {
            "domain": domain,
            "url": str(schema_request.url),
            "schema_markup": result['schema_markup'],
            "schema_generated_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        # Add optional fields if provided
        if schema_request.business_name:
            website_data["business_name"] = schema_request.business_name
        if schema_request.business_type:
            website_data["business_type"] = schema_request.business_type
        if schema_request.location:
            website_data["location"] = schema_request.location

        if existing_website.data:
            # Update existing website
            supabase.table("websites").update(website_data).eq(
                "domain", domain
            ).execute()
            logger.info(f"Updated schema for existing website: {domain}")
        else:
            # Create new website record
            website_data["created_at"] = datetime.utcnow().isoformat()
            supabase.table("websites").insert(website_data).execute()
            logger.info(f"Created new website record: {domain}")

        # Convert recommendations to Pydantic models
        recommendations = [
            Recommendation(**rec) for rec in result['recommendations']
        ]

        return SchemaGenerateResponse(
            schema_markup=result['schema_markup'],
            recommendations=recommendations,
            generated_at=datetime.fromisoformat(result['generated_at']),
            scraped_data=result.get('scraped_data')
        )

    except Exception as e:
        logger.error(f"Schema generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate schema: {str(e)}"
        )


@router.post("/validate", response_model=SchemaValidateResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def validate_schema(
    request: Request,
    validate_request: SchemaValidateRequest,
    api_key: str = Depends(get_api_key)
) -> SchemaValidateResponse:
    """
    Validate schema markup against schema.org standards

    Checks for required fields, proper structure, and provides
    validation score with detailed errors and warnings.
    """
    try:
        # Initialize schema generator service
        generator = SchemaGeneratorService()

        # Validate schema
        validation_result = await generator.validate_schema(
            validate_request.schema_markup
        )

        logger.info(
            f"Schema validation completed: "
            f"valid={validation_result['valid']}, score={validation_result['score']}"
        )

        return SchemaValidateResponse(
            valid=validation_result['valid'],
            errors=validation_result['errors'],
            warnings=validation_result['warnings'],
            score=validation_result['score']
        )

    except Exception as e:
        logger.error(f"Schema validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate schema: {str(e)}"
        )


@router.get("/{website_id}", response_model=WebsiteResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def get_website_schema(
    request: Request,
    website_id: str,
    user: Optional[str] = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> WebsiteResponse:
    """
    Get saved schema markup for a website

    Returns the website's stored schema markup along with
    business information and visibility data.
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
        logger.error(f"Error fetching website schema: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch website schema: {str(e)}"
        )


@router.post("/websites", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_per_minute)
async def create_website(
    request: Request,
    website: WebsiteCreate,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
) -> WebsiteResponse:
    """
    Register a new website for schema generation and visibility tracking

    Creates a website record in the database. Can optionally include
    initial schema markup if already available.
    """
    try:
        # Check if website already exists
        existing = supabase.table("websites").select("*").eq(
            "domain", website.domain
        ).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Website with domain {website.domain} already exists"
            )

        # Create website record
        now = datetime.utcnow().isoformat()
        website_data = {
            "domain": website.domain,
            "url": str(website.url),
            "business_name": website.business_name,
            "business_type": website.business_type,
            "keywords": website.keywords,
            "location": website.location,
            "schema_markup": website.schema_markup,
            "created_at": now,
            "updated_at": now
        }

        if website.schema_markup:
            website_data["schema_generated_at"] = now

        result = supabase.table("websites").insert(website_data).execute()

        if not result.data:
            raise Exception("Failed to create website record")

        created_website = result.data[0]

        logger.info(f"Created new website: {website.domain}")

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


@router.get("/websites", response_model=WebsiteListResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def list_websites(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
) -> WebsiteListResponse:
    """
    List all registered websites

    Returns a paginated list of websites with their schema and
    visibility information.
    """
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        # Calculate offset
        offset = (page - 1) * page_size

        # Get total count
        count_result = supabase.table("websites").select(
            "*", count="exact"
        ).execute()
        total = count_result.count or 0

        # Get paginated websites
        websites_result = supabase.table("websites").select("*").order(
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


@router.patch("/{website_id}", response_model=WebsiteResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def update_website(
    request: Request,
    website_id: str,
    update_data: WebsiteUpdateRequest,
    api_key: str = Depends(get_api_key),
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
