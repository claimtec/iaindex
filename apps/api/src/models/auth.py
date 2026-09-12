"""
Authentication and user management data models
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


class UserRegister(BaseModel):
    """User registration request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    company: Optional[str] = Field(None, max_length=100, description="Company name")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password too long (max 128 characters)")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator('full_name', 'company')
    @classmethod
    def validate_text_fields(cls, v):
        """Validate text fields for XSS"""
        if v:
            # Check for suspicious characters
            if re.search(r'[<>{}|\\^`\[\]]', v):
                raise ValueError("Field contains invalid characters")
        return v


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User response model (public data)"""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="User's full name")
    company: Optional[str] = Field(None, description="Company name")
    plan: Optional[str] = Field(None, description="Current subscription plan")
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")
    email_verified: bool = Field(False, description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserUpdate(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    company: Optional[str] = Field(None, max_length=100, description="Company name")
    email_notifications: Optional[bool] = Field(None, description="Email notifications preference")

    @field_validator('full_name', 'company')
    @classmethod
    def validate_text_fields(cls, v):
        """Validate text fields for XSS"""
        if v:
            # Check for suspicious characters
            if re.search(r'[<>{}|\\^`\[\]]', v):
                raise ValueError("Field contains invalid characters")
        return v


class TokenResponse(BaseModel):
    """JWT token response model"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry time in seconds")
    user: UserResponse = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one digit")
        return v


class UsageStats(BaseModel):
    """User usage statistics"""
    api_calls: int = Field(0, description="Total API calls this period")
    schema_generations: int = Field(0, description="Schema generations this period")
    visibility_checks: int = Field(0, description="Visibility checks this period")
    websites_count: int = Field(0, description="Total websites registered")
    storage_used_mb: float = Field(0, description="Storage used in MB")
    api_calls_limit: int = Field(..., description="API calls limit for current plan")
    period_start: datetime = Field(..., description="Billing period start")
    period_end: datetime = Field(..., description="Billing period end")


class ApiKeyCreate(BaseModel):
    """API key creation request"""
    name: str = Field(..., max_length=100, description="API key name/description")
    scopes: Optional[List[str]] = Field(None, description="API key scopes")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate API key name"""
        if re.search(r'[<>{}|\\^`\[\]]', v):
            raise ValueError("Name contains invalid characters")
        return v


class ApiKeyResponse(BaseModel):
    """API key response"""
    id: str = Field(..., description="API key ID")
    name: str = Field(..., description="API key name")
    key: Optional[str] = Field(None, description="API key (only shown once)")
    key_prefix: str = Field(..., description="API key prefix for identification")
    scopes: Optional[List[str]] = Field(None, description="API key scopes")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    active: bool = Field(True, description="Whether key is active")


class UserWebsitesResponse(BaseModel):
    """User's websites list response"""
    websites: List[Dict[str, Any]] = Field(..., description="List of user's websites")
    total: int = Field(..., description="Total number of websites")
    plan_limit: int = Field(..., description="Website limit for current plan")
