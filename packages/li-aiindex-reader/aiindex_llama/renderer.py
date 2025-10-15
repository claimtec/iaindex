"""
AIIndex v1.1 Render Fallback Support
"""

import re
from typing import Dict, Any, Optional

import requests

from .types import RenderResponse, RenderFallback


class RenderFallbackAdapter:
    """
    Adapter for render fallback support in AIIndex v1.1.

    Handles fetching rendered content when ai-index.json is not available.
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize RenderFallbackAdapter.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "X-AIIndex-Version": "v1.1",
        })

    def fetch_rendered_content(
        self,
        domain: str,
        url: Optional[str] = None,
        client_id: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> Optional[RenderResponse]:
        """
        Fetch rendered content when ai-index.json is not available.

        Calls /render/snapshot endpoint.

        Args:
            domain: Domain to fetch from
            url: Optional custom render URL
            client_id: Optional client ID
            intent: Optional intent ('training' or 'retrieval')

        Returns:
            RenderResponse if successful, None otherwise
        """
        try:
            render_url = url or f"https://{domain}/render/snapshot"

            headers: Dict[str, str] = {
                "X-AIIndex-Version": "v1.1",
            }

            if client_id:
                headers["X-AIIndex-Client-ID"] = client_id

            if intent:
                headers["X-AIIndex-Intent"] = intent

            response = self.session.get(
                render_url,
                timeout=self.timeout,
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                return RenderResponse(**data)

            return None

        except Exception as e:
            print(f"Failed to fetch rendered content: {e}")
            return None

    def try_render_fallback(
        self,
        domain: str,
        render_fallback: Optional[RenderFallback],
        client_id: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> Optional[RenderResponse]:
        """
        Try to fetch rendered content based on render_fallback settings.

        Args:
            domain: Domain to fetch from
            render_fallback: Render fallback configuration
            client_id: Optional client ID
            intent: Optional intent

        Returns:
            RenderResponse if successful, None otherwise
        """
        if not render_fallback or not render_fallback.enabled:
            return None

        # Skip if mode is 'none'
        if render_fallback.mode and render_fallback.mode.value == 'none':
            return None

        # Use custom endpoint if provided
        endpoint = None
        if render_fallback.endpoint:
            endpoint = str(render_fallback.endpoint)
        else:
            endpoint = f"https://{domain}/render/snapshot"

        return self.fetch_rendered_content(domain, endpoint, client_id, intent)

    def extract_text(self, render_response: RenderResponse) -> str:
        """
        Convert rendered content to simple text format.

        Args:
            render_response: Response from render endpoint

        Returns:
            Extracted text content
        """
        if render_response.rendered_text:
            return render_response.rendered_text

        if render_response.rendered_html:
            # Basic HTML to text conversion (strip tags)
            text = render_response.rendered_html

            # Remove script and style tags
            text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
            text = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', text, flags=re.IGNORECASE)

            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', text)

            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text).strip()

            return text

        return ''

    def probe_render_endpoint(self, domain: str) -> bool:
        """
        Check if render fallback is available for a domain.

        Args:
            domain: Domain to probe

        Returns:
            True if render endpoint is available
        """
        try:
            render_url = f"https://{domain}/render/snapshot"
            response = self.session.head(render_url, timeout=self.timeout)
            return response.status_code == 200
        except Exception:
            return False

    def get_metadata(self, render_response: RenderResponse) -> Dict[str, Any]:
        """
        Get metadata from render response.

        Args:
            render_response: Response from render endpoint

        Returns:
            Metadata dictionary
        """
        metadata = {
            'url': str(render_response.url),
            'source': 'render-fallback',
        }

        if render_response.metadata:
            metadata.update(render_response.metadata)
            if 'rendered_at' in render_response.metadata:
                metadata['rendered_at'] = render_response.metadata['rendered_at']
            if 'cache_ttl' in render_response.metadata:
                metadata['cache_ttl'] = render_response.metadata['cache_ttl']

        return metadata

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "RenderFallbackAdapter":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
