"""
AI Visibility data models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AIPlatform(str, Enum):
    """AI search platform types"""
    CHATGPT = "chatgpt"
    PERPLEXITY = "perplexity"
    CLAUDE = "claude"


class VisibilityCheckRequest(BaseModel):
    """Request model for visibility check"""
    website_id: str = Field(..., description="Website ID to check visibility for")
    queries: Optional[List[str]] = Field(
        None,
        description="Optional list of search queries to test (uses keywords if not provided)"
    )
    platforms: Optional[List[AIPlatform]] = Field(
        None,
        description="Optional list of platforms to check (checks all if not provided)"
    )

    @validator('queries')
    def validate_queries(cls, v):
        """Validate query list with security checks"""
        if v is not None:
            if len(v) == 0:
                raise ValueError("Query list cannot be empty if provided")
            if len(v) > 20:
                raise ValueError("Maximum 20 queries allowed per check")

            # Validate each query
            for query in v:
                # Max length check
                if len(query) > 500:
                    raise ValueError("Query too long (max 500 characters)")
                # Check for null bytes (security)
                if '\x00' in query:
                    raise ValueError("Query contains invalid characters")
                # Strip whitespace
                query = query.strip()
                if not query:
                    raise ValueError("Query cannot be empty or whitespace only")

        return v

    @validator('website_id')
    def validate_website_id(cls, v):
        """Validate website ID format (prevent injection)"""
        import re
        # UUID v4 format validation
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, v.lower()):
            raise ValueError("Invalid website ID format")
        return v


class AIMention(BaseModel):
    """Individual mention in AI search results"""
    platform: str = Field(..., description="AI platform where mention was found")
    query: str = Field(..., description="Search query that returned the mention")
    mentioned: bool = Field(..., description="Whether website was mentioned")
    position: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Position in results (1-10, lower is better)"
    )
    context_snippet: Optional[str] = Field(
        None,
        description="Text snippet showing context of mention"
    )
    citation_url: Optional[str] = Field(
        None,
        description="Citation URL if available (for Perplexity)"
    )
    checked_at: datetime = Field(..., description="When this check was performed")


class PlatformScore(BaseModel):
    """Visibility score for a specific platform"""
    platform: str = Field(..., description="Platform name")
    score: int = Field(..., ge=0, le=100, description="Platform visibility score (0-100)")
    mentions_found: int = Field(..., description="Number of mentions found")
    avg_position: Optional[float] = Field(
        None,
        description="Average position in results"
    )


class VisibilityCheckResponse(BaseModel):
    """Response model for visibility check"""
    visibility_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall visibility score (0-100)"
    )
    mentions: List[AIMention] = Field(..., description="List of all mentions found")
    platform_scores: Dict[str, int] = Field(
        ...,
        description="Scores by platform"
    )
    total_mentions: int = Field(..., description="Total number of mentions found")
    checked_at: datetime = Field(..., description="When visibility check was performed")
    queries_tested: List[str] = Field(..., description="Queries that were tested")
    platforms_checked: List[str] = Field(..., description="Platforms that were checked")


class VisibilityHistoryItem(BaseModel):
    """Single visibility check in history"""
    id: str = Field(..., description="Check ID")
    visibility_score: int = Field(..., ge=0, le=100, description="Visibility score")
    total_mentions: int = Field(..., description="Total mentions found")
    platforms_checked: List[str] = Field(..., description="Platforms checked")
    checked_at: datetime = Field(..., description="Check timestamp")


class VisibilityTrend(str, Enum):
    """Visibility trend direction"""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    INSUFFICIENT_DATA = "insufficient_data"


class VisibilityHistory(BaseModel):
    """Historical visibility data for a website"""
    checks: List[VisibilityHistoryItem] = Field(
        ...,
        description="List of historical checks"
    )
    average_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Average visibility score across all checks"
    )
    trend: VisibilityTrend = Field(..., description="Trend direction")
    total_checks: int = Field(..., description="Total number of checks performed")
    highest_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Highest score achieved"
    )
    lowest_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Lowest score recorded"
    )
    last_checked: Optional[datetime] = Field(
        None,
        description="Most recent check timestamp"
    )


class VisibilityDetailedResponse(BaseModel):
    """Detailed visibility response with historical data"""
    current: VisibilityCheckResponse = Field(
        ...,
        description="Current visibility check results"
    )
    history: VisibilityHistory = Field(
        ...,
        description="Historical visibility data"
    )
    website_info: Dict[str, Any] = Field(
        ...,
        description="Website information"
    )


class VisibilityComparisonRequest(BaseModel):
    """Request model for comparing visibility across websites"""
    website_ids: List[str] = Field(
        ...,
        min_items=2,
        max_items=10,
        description="List of website IDs to compare (2-10)"
    )
    platform: Optional[AIPlatform] = Field(
        None,
        description="Optional platform to filter comparison"
    )

    @validator('website_ids')
    def validate_website_ids(cls, v):
        """Validate all website IDs"""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        for website_id in v:
            if not re.match(uuid_pattern, website_id.lower()):
                raise ValueError(f"Invalid website ID format: {website_id}")
        return v


class VisibilityComparisonItem(BaseModel):
    """Single website in comparison"""
    website_id: str = Field(..., description="Website ID")
    domain: str = Field(..., description="Website domain")
    visibility_score: int = Field(..., ge=0, le=100, description="Current visibility score")
    average_score: float = Field(..., ge=0, le=100, description="Average historical score")
    trend: VisibilityTrend = Field(..., description="Visibility trend")
    total_mentions: int = Field(..., description="Total mentions in latest check")
    last_checked: Optional[datetime] = Field(None, description="Last check timestamp")


class VisibilityComparisonResponse(BaseModel):
    """Response model for visibility comparison"""
    websites: List[VisibilityComparisonItem] = Field(
        ...,
        description="List of websites with visibility data"
    )
    highest_score: VisibilityComparisonItem = Field(
        ...,
        description="Website with highest visibility score"
    )
    compared_at: datetime = Field(..., description="Comparison timestamp")


class VisibilityReportRequest(BaseModel):
    """Request model for generating visibility report"""
    website_id: str = Field(..., description="Website ID to generate report for")
    start_date: Optional[datetime] = Field(
        None,
        description="Start date for report period"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="End date for report period"
    )
    include_queries: bool = Field(
        True,
        description="Include detailed query breakdown"
    )
    include_platforms: bool = Field(
        True,
        description="Include platform-specific analysis"
    )


class VisibilityReportResponse(BaseModel):
    """Response model for visibility report"""
    website_id: str = Field(..., description="Website ID")
    domain: str = Field(..., description="Website domain")
    report_period: Dict[str, datetime] = Field(
        ...,
        description="Report period (start and end dates)"
    )
    summary: Dict[str, Any] = Field(..., description="Summary statistics")
    platform_breakdown: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Platform-specific data"
    )
    query_breakdown: Optional[Dict[str, Any]] = Field(
        None,
        description="Query-specific performance data"
    )
    recommendations: List[str] = Field(
        ...,
        description="Recommendations for improving visibility"
    )
    generated_at: datetime = Field(..., description="Report generation timestamp")
