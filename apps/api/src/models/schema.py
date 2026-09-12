"""
Schema-related data models with enhanced security validation
"""
from pydantic import BaseModel, Field, HttpUrl, validator, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re


class SchemaGenerateRequest(BaseModel):
    """Request model for schema generation"""
    url: HttpUrl = Field(..., description="Website URL to generate schema for")
    business_type: Optional[str] = Field(
        None,
        description="Type of business (e.g., 'Restaurant', 'LocalBusiness', 'Organization')"
    )
    business_name: Optional[str] = Field(
        None,
        description="Name of the business"
    )
    location: Optional[Dict[str, Any]] = Field(
        None,
        description="Location data (address, city, country, coordinates)"
    )

    @validator('url', pre=True)
    def validate_url(cls, v):
        """Ensure URL has protocol"""
        if isinstance(v, str) and not v.startswith(('http://', 'https://')):
            return f"https://{v}"
        return v


class Recommendation(BaseModel):
    """Schema optimization recommendation"""
    type: str = Field(..., description="Type of recommendation (e.g., 'metadata', 'schema')")
    priority: str = Field(..., description="Priority level (e.g., 'high', 'medium', 'low', 'critical')")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    action_items: List[str] = Field(..., description="List of actionable items")
    impact_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Expected impact score (0-100)"
    )


class SchemaGenerateResponse(BaseModel):
    """Response model for schema generation"""
    schema_markup: Dict[str, Any] = Field(
        ...,
        description="Generated JSON-LD schema markup"
    )
    recommendations: List[Recommendation] = Field(
        ...,
        description="List of optimization recommendations"
    )
    generated_at: datetime = Field(
        ...,
        description="Timestamp when schema was generated"
    )
    scraped_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Metadata about scraped website data"
    )


class SchemaValidateRequest(BaseModel):
    """Request model for schema validation"""
    schema_markup: Dict[str, Any] = Field(
        ...,
        description="JSON-LD schema markup to validate"
    )

    @validator('schema_markup')
    def validate_schema_structure(cls, v):
        """Basic validation of schema structure"""
        if not isinstance(v, dict):
            raise ValueError("Schema markup must be a JSON object")
        return v


class SchemaValidateResponse(BaseModel):
    """Response model for schema validation"""
    valid: bool = Field(..., description="Whether schema is valid")
    errors: List[str] = Field(..., description="List of validation errors")
    warnings: List[str] = Field(..., description="List of validation warnings")
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Validation score (0-100)"
    )


class WebsiteCreate(BaseModel):
    """Request model for creating/registering a website"""
    domain: str = Field(..., description="Website domain")
    url: HttpUrl = Field(..., description="Full website URL")
    business_name: Optional[str] = Field(None, description="Business name")
    business_type: Optional[str] = Field(None, description="Business type")
    keywords: Optional[List[str]] = Field(
        None,
        description="Relevant keywords for visibility tracking"
    )
    location: Optional[Dict[str, Any]] = Field(
        None,
        description="Business location information"
    )
    schema_markup: Optional[Dict[str, Any]] = Field(
        None,
        description="Pre-existing schema markup (if any)"
    )

    @validator('domain')
    def validate_domain(cls, v):
        """Validate and clean domain"""
        if not v or '.' not in v:
            raise ValueError("Invalid domain format")

        # Clean domain
        domain = v.lower().strip()
        domain = domain.replace('http://', '').replace('https://', '')
        domain = domain.split('/')[0]
        domain = domain.replace('www.', '')

        # Security: Check for private/local domains
        if any(pattern in domain for pattern in ['localhost', '127.0.0.1', '0.0.0.0', '169.254']):
            raise ValueError("Private/local domains are not allowed")

        # Validate domain format (basic check)
        if not re.match(r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9\-]*[a-z0-9])?)*$', domain):
            raise ValueError("Invalid domain format")

        # Max length check
        if len(domain) > 253:
            raise ValueError("Domain too long (max 253 characters)")

        return domain

    @validator('url', pre=True)
    def validate_url(cls, v):
        """Ensure URL has protocol and validate format"""
        if isinstance(v, str):
            # Add protocol if missing
            if not v.startswith(('http://', 'https://')):
                v = f"https://{v}"
            # Check for suspicious patterns
            if any(pattern in v.lower() for pattern in ['localhost', '127.0.0.1', '0.0.0.0', '169.254']):
                raise ValueError("Private/local URLs are not allowed")
        return v

    @validator('keywords')
    def validate_keywords(cls, v):
        """Validate keywords list"""
        if v is not None:
            if len(v) > 50:
                raise ValueError("Too many keywords (max 50)")
            for keyword in v:
                if len(keyword) > 100:
                    raise ValueError("Keyword too long (max 100 characters)")
                # Check for suspicious characters
                if re.search(r'[<>{}|\\^`\[\]]', keyword):
                    raise ValueError("Keyword contains invalid characters")
        return v


class WebsiteResponse(BaseModel):
    """Response model for website data"""
    id: str = Field(..., description="Website ID")
    domain: str = Field(..., description="Website domain")
    url: str = Field(..., description="Website URL")
    business_name: Optional[str] = Field(None, description="Business name")
    business_type: Optional[str] = Field(None, description="Business type")
    keywords: Optional[List[str]] = Field(None, description="Tracked keywords")
    location: Optional[Dict[str, Any]] = Field(None, description="Location data")
    schema_markup: Optional[Dict[str, Any]] = Field(
        None,
        description="Generated schema markup"
    )
    visibility_score: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Latest visibility score (0-100)"
    )
    last_visibility_check: Optional[datetime] = Field(
        None,
        description="Timestamp of last visibility check"
    )
    schema_generated_at: Optional[datetime] = Field(
        None,
        description="When schema was last generated"
    )
    created_at: datetime = Field(..., description="Website registration timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class WebsiteListResponse(BaseModel):
    """Response model for listing websites"""
    websites: List[WebsiteResponse] = Field(..., description="List of websites")
    total: int = Field(..., description="Total number of websites")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Items per page")


class WebsiteUpdateRequest(BaseModel):
    """Request model for updating website data"""
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    keywords: Optional[List[str]] = None
    location: Optional[Dict[str, Any]] = None
    schema_markup: Optional[Dict[str, Any]] = None
