"""
Receipt data models
"""
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ReceiptStatus(str, Enum):
    """Receipt verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    REJECTED = "rejected"


class ReceiptIngestRequest(BaseModel):
    """Request model for receipt ingestion"""
    receipt_id: str = Field(..., description="Unique receipt identifier")
    publisher_domain: str = Field(..., description="Publisher's domain")
    article_url: HttpUrl = Field(..., description="Article URL")
    timestamp: datetime = Field(..., description="Receipt timestamp")
    signature: str = Field(..., description="Cryptographic signature")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    @validator('publisher_domain')
    def validate_domain(cls, v):
        """Validate domain format"""
        if not v or '.' not in v:
            raise ValueError("Invalid domain format")
        return v.lower().strip()

    @validator('signature')
    def validate_signature(cls, v):
        """Validate signature is not empty"""
        if not v or len(v) < 10:
            raise ValueError("Invalid signature")
        return v


class ReceiptIngestResponse(BaseModel):
    """Response model for receipt ingestion"""
    receipt_id: str
    status: ReceiptStatus
    verified: bool
    message: str
    merkle_root: Optional[str] = None
    timestamp: datetime


class ReceiptQueryParams(BaseModel):
    """Query parameters for receipt listing"""
    publisher_domain: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ReceiptStatus] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ReceiptResponse(BaseModel):
    """Individual receipt response"""
    receipt_id: str
    publisher_domain: str
    article_url: str
    timestamp: datetime
    status: ReceiptStatus
    verified: bool
    signature: str
    merkle_root: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ReceiptListResponse(BaseModel):
    """Paginated receipt list response"""
    receipts: list[ReceiptResponse]
    total: int
    limit: int
    offset: int
