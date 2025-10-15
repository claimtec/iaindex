"""
Type definitions for AIIndex LlamaIndex connector using Pydantic models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, EmailStr, field_validator


class EntityType(str, Enum):
    """Valid entity types."""
    PERSON = "Person"
    ORGANIZATION = "Organization"
    PRODUCT = "Product"
    SERVICE = "Service"
    EVENT = "Event"
    PLACE = "Place"


class ContentType(str, Enum):
    """Valid content types for pages."""
    ARTICLE = "article"
    PAGE = "page"
    PRODUCT = "product"
    DOCUMENTATION = "documentation"
    FAQ = "faq"
    ABOUT = "about"


class SignatureAlgorithm(str, Enum):
    """Supported signature algorithms."""
    ES256 = "ES256"  # ECDSA with P-256 and SHA-256
    RS256 = "RS256"  # RSA with SHA-256


class HTTPMethod(str, Enum):
    """HTTP methods for access."""
    GET = "GET"
    POST = "POST"


class PurposeType(str, Enum):
    """Types of AI access purposes."""
    TRAINING = "training"
    RETRIEVAL = "retrieval"
    INFERENCE = "inference"
    RESEARCH = "research"
    INDEXING = "indexing"
    OTHER = "other"


class AttributionMethod(str, Enum):
    """Methods of content attribution."""
    CITATION = "citation"
    LINK = "link"
    INLINE = "inline"
    NONE = "none"


class Contact(BaseModel):
    """Contact information."""
    email: Optional[EmailStr] = None
    url: Optional[HttpUrl] = None


class Publisher(BaseModel):
    """Publisher information."""
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    contact: Optional[Contact] = None
    logo: Optional[HttpUrl] = None


class Entity(BaseModel):
    """Structured entity (person, organization, product, etc.)."""
    type: EntityType
    name: str
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    image: Optional[HttpUrl] = None
    properties: Optional[Dict[str, Any]] = None


class Page(BaseModel):
    """Indexed page metadata."""
    url: HttpUrl
    title: str
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    published: Optional[datetime] = None
    modified: Optional[datetime] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = Field(None, max_length=2000)


class FAQ(BaseModel):
    """Frequently asked question."""
    question: str
    answer: str
    category: Optional[str] = None


class AccessPolicy(BaseModel):
    """AI access control policy."""
    allowed: bool = True
    attribution_required: bool = True
    commercial_use: bool = True
    receipt_required: bool = False
    webhook_url: Optional[HttpUrl] = None


class Signature(BaseModel):
    """Cryptographic signature for verification."""
    algorithm: SignatureAlgorithm
    kid: str  # Key ID
    signature: str  # Base64-encoded signature
    document_hash: str  # SHA-256 hash
    signed_at: Optional[datetime] = None


class Verification(BaseModel):
    """AIIndex network verification status."""
    verified: Optional[bool] = None
    verified_at: Optional[datetime] = None
    verification_url: Optional[HttpUrl] = None


class AIIndexDocument(BaseModel):
    """Complete AIIndex document structure."""
    version: str = "1.0"
    publisher_id: str = Field(..., min_length=3, max_length=255)
    domain: str
    last_updated: datetime
    publisher: Optional[Publisher] = None
    entities: Optional[List[Entity]] = None
    pages: Optional[List[Page]] = None
    faq: Optional[List[FAQ]] = None
    access_policy: Optional[AccessPolicy] = None
    signature: Optional[Signature] = None
    verification: Optional[Verification] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not v.startswith('1.'):
            raise ValueError('Version must be 1.x')
        return v


class Access(BaseModel):
    """Access details for receipts."""
    url: Optional[HttpUrl] = None
    method: HTTPMethod = HTTPMethod.GET
    status_code: Optional[int] = Field(None, ge=200, le=599)
    content_hash: Optional[str] = None
    pages_accessed: Optional[List[HttpUrl]] = None


class Purpose(BaseModel):
    """Purpose of AI access."""
    type: Optional[PurposeType] = None
    description: Optional[str] = None
    commercial: Optional[bool] = None


class Attribution(BaseModel):
    """Attribution details."""
    method: Optional[AttributionMethod] = None
    citation_text: Optional[str] = None
    url: Optional[HttpUrl] = None


class ReceiptMetadata(BaseModel):
    """Metadata for receipts."""
    user_agent: Optional[str] = None
    sdk_version: Optional[str] = None
    request_id: Optional[str] = None


class Receipt(BaseModel):
    """AIIndex access receipt."""
    version: str = "1.0"
    receipt_id: str  # UUID v4
    publisher_id: str = Field(..., min_length=3, max_length=255)
    publisher_domain: Optional[str] = None
    client_id: str = Field(..., min_length=3, max_length=255)
    client_name: Optional[str] = None
    client_version: Optional[str] = None
    timestamp: datetime
    access: Optional[Access] = None
    purpose: Optional[Purpose] = None
    attribution: Optional[Attribution] = None
    signature: Signature
    metadata: Optional[ReceiptMetadata] = None

    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not v.startswith('1.'):
            raise ValueError('Version must be 1.x')
        return v

    @field_validator('receipt_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        import re
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        if not re.match(pattern, v):
            raise ValueError('receipt_id must be a valid UUID v4')
        return v


# AIIndex v1.1 Policy Types
class PolicyAction(str, Enum):
    """Policy actions for v1.1."""
    ALLOW = "allow"
    BLOCK = "block"
    REQUIRE_ATTRIBUTION = "require-attribution"


class RateLimit(BaseModel):
    """Rate limiting configuration."""
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    delay_ms: Optional[int] = None


class PolicyRule(BaseModel):
    """Policy rules for training and retrieval."""
    training: Optional[PolicyAction] = None
    retrieval: Optional[PolicyAction] = None
    rate_limit: Optional[RateLimit] = None


class ReceiptPolicyConfig(BaseModel):
    """Receipt policy configuration."""
    require_signed: Optional[bool] = False
    webhook_url: Optional[HttpUrl] = None
    required_fields: Optional[List[str]] = None


class RenderFallbackMode(str, Enum):
    """Render fallback modes."""
    SNAPSHOT = "snapshot"
    LIVE = "live"
    NONE = "none"


class RenderFallback(BaseModel):
    """Render fallback configuration."""
    enabled: Optional[bool] = False
    mode: Optional[RenderFallbackMode] = None
    endpoint: Optional[HttpUrl] = None


class AIIndexPolicy(BaseModel):
    """AIIndex v1.1 policy document."""
    version: str = "1.1"
    domain: str
    policy: PolicyRule
    receipts: Optional[ReceiptPolicyConfig] = None
    render_fallback: Optional[RenderFallback] = None
    updated_at: Optional[datetime] = None


class DenialReceipt(BaseModel):
    """Denial receipt from 403 responses."""
    denied: bool = True
    reason: str
    policy_url: Optional[HttpUrl] = None
    retry_after: Optional[int] = None
    alternative_endpoint: Optional[HttpUrl] = None


class RenderResponse(BaseModel):
    """Response from render endpoint."""
    url: HttpUrl
    rendered_text: Optional[str] = None
    rendered_html: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Custom Exceptions
class PolicyViolationError(Exception):
    """Raised when policy blocks access."""
    def __init__(
        self,
        message: str,
        action: PolicyAction,
        intent: str,
        denial_receipt: Optional[DenialReceipt] = None
    ):
        super().__init__(message)
        self.action = action
        self.intent = intent
        self.denial_receipt = denial_receipt


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after
