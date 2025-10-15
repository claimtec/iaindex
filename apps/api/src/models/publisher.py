"""
Publisher data models
"""
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class VerificationStatus(str, Enum):
    """Publisher verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class VerificationMethod(str, Enum):
    """Verification method type"""
    DNS_TXT = "dns_txt"
    HTML_META = "html_meta"
    FILE_UPLOAD = "file_upload"


class PublisherVerifyRequest(BaseModel):
    """Request model for publisher verification"""
    domain: str = Field(..., description="Domain to verify")
    method: VerificationMethod = Field(default=VerificationMethod.DNS_TXT)
    contact_email: Optional[str] = None

    @validator('domain')
    def validate_domain(cls, v):
        """Validate domain format"""
        if not v or '.' not in v:
            raise ValueError("Invalid domain format")
        # Remove protocol and path if present
        domain = v.lower().strip()
        domain = domain.replace('http://', '').replace('https://', '')
        domain = domain.split('/')[0]
        return domain


class PublisherVerifyResponse(BaseModel):
    """Response model for verification initiation"""
    domain: str
    verification_token: str
    verification_method: VerificationMethod
    instructions: str
    expires_at: datetime
    status: VerificationStatus


class VerificationCheckResponse(BaseModel):
    """Response model for verification check"""
    domain: str
    status: VerificationStatus
    verified: bool
    verified_at: Optional[datetime] = None
    message: str


class VerifiedPublisher(BaseModel):
    """Verified publisher public information"""
    domain: str
    verified_at: datetime
    receipt_count: int = 0
    last_receipt_at: Optional[datetime] = None


class PublisherAnalytics(BaseModel):
    """Publisher analytics data"""
    domain: str
    total_receipts: int
    verified_receipts: int
    failed_receipts: int
    first_receipt_at: Optional[datetime] = None
    last_receipt_at: Optional[datetime] = None
    daily_breakdown: Optional[Dict[str, int]] = None


class VerifiedDomainListResponse(BaseModel):
    """Response for verified domains list"""
    domains: list[VerifiedPublisher]
    total: int
    updated_at: datetime
