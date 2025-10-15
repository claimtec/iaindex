"""
Cloudflare Browser Rendering Service

Provides server-side rendering for JavaScript-heavy sites using Cloudflare Browser Rendering API.
Extracts rendered HTML/text, computes content hashes, and manages S3 snapshot storage.
"""
import hashlib
import logging
import json
from typing import Optional, Dict, Any, Literal
from datetime import datetime, timedelta
from pydantic import BaseModel, HttpUrl, Field
import httpx
import boto3
from botocore.exceptions import ClientError
import asyncio
from urllib.parse import urlparse
import os

logger = logging.getLogger(__name__)


# Configuration
class RenderingConfig:
    """Configuration for rendering service"""
    CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
    CLOUDFLARE_BROWSER_RENDERING_URL = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{CLOUDFLARE_ACCOUNT_ID}/browser/render"
    )

    # S3 Configuration
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET = os.getenv("S3_BUCKET_SNAPSHOTS", "iaindex-snapshots")

    # Cache settings
    CACHE_TTL_SECONDS = 3600  # 1 hour
    REQUEST_TIMEOUT = 30  # seconds
    MAX_CONTENT_SIZE = 5 * 1024 * 1024  # 5MB


# Request/Response Models
RenderMode = Literal["text", "html", "json"]


class RenderSnapshotRequest(BaseModel):
    """Request model for rendering snapshot"""
    url: HttpUrl = Field(..., description="URL to render")
    mode: RenderMode = Field(
        default="text",
        description="Render mode: text (plain text), html (full HTML), json (structured data)"
    )
    force_refresh: bool = Field(
        default=False,
        description="Force refresh, bypass cache"
    )
    wait_for: Optional[str] = Field(
        default=None,
        description="CSS selector to wait for before capturing"
    )
    viewport_width: int = Field(default=1920, ge=800, le=3840)
    viewport_height: int = Field(default=1080, ge=600, le=2160)
    user_agent: Optional[str] = None


class RenderSnapshotResponse(BaseModel):
    """Response model for rendering snapshot"""
    url: str
    content_hash: str
    rendered_text: Optional[str] = None
    rendered_html: Optional[str] = None
    rendered_json: Optional[Dict[str, Any]] = None
    rendered_at: datetime
    cache_hit: bool
    snapshot_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SnapshotMetadata(BaseModel):
    """Metadata stored with snapshot"""
    url: str
    content_hash: str
    rendered_at: datetime
    mode: RenderMode
    viewport: Dict[str, int]
    title: Optional[str] = None
    meta_description: Optional[str] = None
    size_bytes: int
    etag: Optional[str] = None


# Exceptions
class RenderingError(Exception):
    """Base exception for rendering errors"""
    pass


class CloudflareAPIError(RenderingError):
    """Cloudflare API error"""
    pass


class S3StorageError(RenderingError):
    """S3 storage error"""
    pass


class RenderingService:
    """
    Service for browser rendering using Cloudflare Browser Rendering API

    Features:
    - Server-side rendering of JavaScript-heavy sites
    - Content hash computation (SHA-256)
    - S3 snapshot storage
    - Edge cache with ETag support
    - Multiple render modes (text, html, json)
    """

    def __init__(self):
        """Initialize rendering service"""
        self.config = RenderingConfig()
        self.http_client = httpx.AsyncClient(timeout=self.config.REQUEST_TIMEOUT)
        self.s3_client = None
        self._cache: Dict[str, Dict[str, Any]] = {}  # In-memory cache
        self._init_s3_client()

    def _init_s3_client(self):
        """Initialize S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.config.AWS_SECRET_ACCESS_KEY,
                region_name=self.config.AWS_REGION
            )
            logger.info("S3 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None

    def _compute_content_hash(self, content: str) -> str:
        """
        Compute SHA-256 hash of content

        Args:
            content: Content to hash

        Returns:
            Hex-encoded SHA-256 hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL

        Args:
            url: Full URL

        Returns:
            Domain name
        """
        parsed = urlparse(url)
        return parsed.netloc or "unknown"

    def _get_cache_key(self, url: str, mode: RenderMode) -> str:
        """
        Generate cache key for URL and mode

        Args:
            url: URL to render
            mode: Render mode

        Returns:
            Cache key
        """
        return f"{url}:{mode}"

    def _check_cache(
        self,
        url: str,
        mode: RenderMode,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Check if cached version exists and is valid

        Args:
            url: URL to check
            mode: Render mode
            force_refresh: Force bypass cache

        Returns:
            Cached data or None
        """
        if force_refresh:
            return None

        cache_key = self._get_cache_key(url, mode)
        cached = self._cache.get(cache_key)

        if cached:
            expires_at = cached.get("expires_at")
            if expires_at and datetime.utcnow() < expires_at:
                logger.info(f"Cache hit for {url} (mode: {mode})")
                return cached
            else:
                # Expired, remove from cache
                del self._cache[cache_key]

        return None

    def _set_cache(
        self,
        url: str,
        mode: RenderMode,
        data: Dict[str, Any]
    ):
        """
        Store data in cache

        Args:
            url: URL
            mode: Render mode
            data: Data to cache
        """
        cache_key = self._get_cache_key(url, mode)
        data["expires_at"] = datetime.utcnow() + timedelta(
            seconds=self.config.CACHE_TTL_SECONDS
        )
        self._cache[cache_key] = data
        logger.info(f"Cached {url} (mode: {mode})")

    async def _call_cloudflare_browser_rendering(
        self,
        url: str,
        mode: RenderMode,
        wait_for: Optional[str] = None,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call Cloudflare Browser Rendering API

        Args:
            url: URL to render
            mode: Render mode
            wait_for: CSS selector to wait for
            viewport_width: Viewport width
            viewport_height: Viewport height
            user_agent: Custom user agent

        Returns:
            Rendering result

        Raises:
            CloudflareAPIError: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.config.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "url": str(url),
            "viewport": {
                "width": viewport_width,
                "height": viewport_height
            }
        }

        if wait_for:
            payload["wait_for"] = wait_for

        if user_agent:
            payload["user_agent"] = user_agent

        # Determine what to capture based on mode
        if mode == "text":
            payload["capture"] = ["text"]
        elif mode == "html":
            payload["capture"] = ["html"]
        elif mode == "json":
            payload["capture"] = ["html", "text", "metadata"]

        try:
            logger.info(f"Calling Cloudflare Browser Rendering API for {url}")
            response = await self.http_client.post(
                self.config.CLOUDFLARE_BROWSER_RENDERING_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()

            if not result.get("success"):
                error_msg = result.get("errors", ["Unknown error"])[0]
                raise CloudflareAPIError(f"Cloudflare API error: {error_msg}")

            return result.get("result", {})

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Cloudflare API: {e}")
            raise CloudflareAPIError(f"HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error calling Cloudflare API: {e}")
            raise CloudflareAPIError(f"API call failed: {str(e)}")

    def _generate_s3_key(self, domain: str, content_hash: str) -> str:
        """
        Generate S3 key for snapshot

        Args:
            domain: Domain name
            content_hash: Content hash

        Returns:
            S3 key path
        """
        return f"snapshots/{domain}/{content_hash}.json"

    async def _store_snapshot_s3(
        self,
        domain: str,
        content_hash: str,
        snapshot_data: Dict[str, Any],
        metadata: SnapshotMetadata
    ) -> str:
        """
        Store snapshot in S3

        Args:
            domain: Domain name
            content_hash: Content hash
            snapshot_data: Snapshot data to store
            metadata: Snapshot metadata

        Returns:
            S3 URL

        Raises:
            S3StorageError: If storage fails
        """
        if not self.s3_client:
            raise S3StorageError("S3 client not initialized")

        s3_key = self._generate_s3_key(domain, content_hash)

        try:
            # Store snapshot with metadata
            self.s3_client.put_object(
                Bucket=self.config.S3_BUCKET,
                Key=s3_key,
                Body=json.dumps(snapshot_data, indent=2),
                ContentType='application/json',
                Metadata={
                    'url': metadata.url,
                    'content-hash': metadata.content_hash,
                    'rendered-at': metadata.rendered_at.isoformat(),
                    'mode': metadata.mode
                },
                CacheControl=f'max-age={self.config.CACHE_TTL_SECONDS}'
            )

            s3_url = f"https://{self.config.S3_BUCKET}.s3.{self.config.AWS_REGION}.amazonaws.com/{s3_key}"
            logger.info(f"Stored snapshot in S3: {s3_url}")
            return s3_url

        except ClientError as e:
            logger.error(f"S3 storage error: {e}")
            raise S3StorageError(f"Failed to store snapshot: {str(e)}")

    async def _retrieve_snapshot_s3(
        self,
        domain: str,
        content_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve snapshot from S3

        Args:
            domain: Domain name
            content_hash: Content hash

        Returns:
            Snapshot data or None if not found
        """
        if not self.s3_client:
            return None

        s3_key = self._generate_s3_key(domain, content_hash)

        try:
            response = self.s3_client.get_object(
                Bucket=self.config.S3_BUCKET,
                Key=s3_key
            )
            data = json.loads(response['Body'].read())
            logger.info(f"Retrieved snapshot from S3: {s3_key}")
            return data
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.debug(f"Snapshot not found in S3: {s3_key}")
            else:
                logger.error(f"Error retrieving from S3: {e}")
            return None

    async def render_snapshot(
        self,
        request: RenderSnapshotRequest
    ) -> RenderSnapshotResponse:
        """
        Render a snapshot of the given URL

        Args:
            request: Render request

        Returns:
            Render response with content and metadata

        Raises:
            RenderingError: If rendering fails
        """
        url = str(request.url)
        domain = self._extract_domain(url)

        # Check cache first
        cached = self._check_cache(url, request.mode, request.force_refresh)
        if cached:
            return RenderSnapshotResponse(
                url=url,
                content_hash=cached["content_hash"],
                rendered_text=cached.get("rendered_text"),
                rendered_html=cached.get("rendered_html"),
                rendered_json=cached.get("rendered_json"),
                rendered_at=cached["rendered_at"],
                cache_hit=True,
                snapshot_url=cached.get("snapshot_url"),
                metadata=cached.get("metadata", {})
            )

        # Call Cloudflare Browser Rendering
        render_result = await self._call_cloudflare_browser_rendering(
            url=url,
            mode=request.mode,
            wait_for=request.wait_for,
            viewport_width=request.viewport_width,
            viewport_height=request.viewport_height,
            user_agent=request.user_agent
        )

        # Extract content based on mode
        rendered_text = None
        rendered_html = None
        rendered_json = None
        content_for_hash = ""

        if request.mode == "text":
            rendered_text = render_result.get("text", "")
            content_for_hash = rendered_text
        elif request.mode == "html":
            rendered_html = render_result.get("html", "")
            content_for_hash = rendered_html
        elif request.mode == "json":
            rendered_json = {
                "text": render_result.get("text", ""),
                "html": render_result.get("html", ""),
                "metadata": render_result.get("metadata", {})
            }
            content_for_hash = json.dumps(rendered_json, sort_keys=True)

        # Compute content hash
        content_hash = self._compute_content_hash(content_for_hash)
        rendered_at = datetime.utcnow()

        # Prepare snapshot data
        snapshot_data = {
            "url": url,
            "domain": domain,
            "content_hash": content_hash,
            "rendered_at": rendered_at.isoformat(),
            "mode": request.mode,
            "rendered_text": rendered_text,
            "rendered_html": rendered_html,
            "rendered_json": rendered_json,
            "viewport": {
                "width": request.viewport_width,
                "height": request.viewport_height
            }
        }

        # Metadata
        metadata = SnapshotMetadata(
            url=url,
            content_hash=content_hash,
            rendered_at=rendered_at,
            mode=request.mode,
            viewport={
                "width": request.viewport_width,
                "height": request.viewport_height
            },
            title=render_result.get("metadata", {}).get("title"),
            meta_description=render_result.get("metadata", {}).get("description"),
            size_bytes=len(content_for_hash.encode('utf-8'))
        )

        # Store in S3
        snapshot_url = None
        try:
            snapshot_url = await self._store_snapshot_s3(
                domain, content_hash, snapshot_data, metadata
            )
        except S3StorageError as e:
            logger.warning(f"Failed to store snapshot in S3: {e}")

        # Cache the result
        cache_data = {
            "content_hash": content_hash,
            "rendered_text": rendered_text,
            "rendered_html": rendered_html,
            "rendered_json": rendered_json,
            "rendered_at": rendered_at,
            "snapshot_url": snapshot_url,
            "metadata": metadata.dict()
        }
        self._set_cache(url, request.mode, cache_data)

        return RenderSnapshotResponse(
            url=url,
            content_hash=content_hash,
            rendered_text=rendered_text,
            rendered_html=rendered_html,
            rendered_json=rendered_json,
            rendered_at=rendered_at,
            cache_hit=False,
            snapshot_url=snapshot_url,
            metadata=metadata.dict()
        )

    async def get_snapshot_by_hash(
        self,
        domain: str,
        content_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve snapshot by content hash

        Args:
            domain: Domain name
            content_hash: Content hash

        Returns:
            Snapshot data or None
        """
        return await self._retrieve_snapshot_s3(domain, content_hash)

    async def update_ai_index_with_snapshot(
        self,
        ai_index_url: str,
        page_url: str,
        rendered_text: str,
        content_hash: str
    ) -> bool:
        """
        Update ai-index.json with rendered content

        Args:
            ai_index_url: URL to ai-index.json
            page_url: Page URL to update
            rendered_text: Rendered text content
            content_hash: Content hash

        Returns:
            True if successful
        """
        # This would fetch, update, and upload ai-index.json
        # Implementation depends on your storage mechanism
        logger.info(
            f"Updating ai-index.json at {ai_index_url} "
            f"for page {page_url} with hash {content_hash}"
        )
        # TODO: Implement ai-index.json update logic
        return True

    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()
        logger.info("Rendering service cleaned up")


# Singleton instance
_rendering_service: Optional[RenderingService] = None


def get_rendering_service() -> RenderingService:
    """Get or create rendering service instance"""
    global _rendering_service
    if _rendering_service is None:
        _rendering_service = RenderingService()
    return _rendering_service
