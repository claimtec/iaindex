"""
AIIndexReader - Fetch and parse ai-index.json files with schema validation
"""

import hashlib
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

import requests
from jsonschema import validate, ValidationError as JsonSchemaValidationError
from pydantic import ValidationError

from .types import AIIndexDocument, Entity, FAQ, AIIndexPolicy
from .policy import PolicyEnforcer, parse_domain
from .renderer import RenderFallbackAdapter


class AIIndexReader:
    """
    Fetch and parse ai-index.json files with schema validation.

    Example:
        >>> reader = AIIndexReader(timeout=10, validate_schema=True)
        >>> document = await reader.fetch("example.com")
        >>> print(document.publisher.name)
    """

    def __init__(
        self,
        timeout: int = 10,
        validate_schema: bool = True,
        user_agent: Optional[str] = None,
        client_id: Optional[str] = None,
        intent: str = "retrieval",
        respect_policy_blocks: bool = True,
        enable_render_fallback: bool = True,
    ):
        """
        Initialize AIIndexReader.

        Args:
            timeout: Request timeout in seconds (default: 10)
            validate_schema: Enable schema validation (default: True)
            user_agent: Custom User-Agent header
            client_id: Client identifier for X-AIIndex-Client-ID header
            intent: Default intent ('training' or 'retrieval')
            respect_policy_blocks: Enforce policy blocks (default: True)
            enable_render_fallback: Enable render fallback (default: True)
        """
        self.timeout = timeout
        self.validate_schema = validate_schema
        self.user_agent = user_agent or "LlamaIndex AIIndex Reader/1.0.0"
        self.client_id = client_id or "llamaindex-client"
        self.intent = intent
        self.respect_policy_blocks = respect_policy_blocks
        self.enable_render_fallback = enable_render_fallback

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "X-AIIndex-Version": "v1.1",
            "X-AIIndex-Client-ID": self.client_id,
            "X-AIIndex-Intent": self.intent,
        })

        self.policy_enforcer = PolicyEnforcer(timeout)
        self.render_adapter = RenderFallbackAdapter(timeout)

    def fetch(
        self,
        url_or_domain: str,
        intent: Optional[str] = None
    ) -> AIIndexDocument:
        """
        Fetch and parse ai-index.json from a URL or domain with policy enforcement.

        Args:
            url_or_domain: Full URL or domain name
            intent: Optional intent override ('training' or 'retrieval')

        Returns:
            Parsed AIIndexDocument

        Raises:
            requests.RequestException: On network errors
            ValidationError: On schema validation errors
            PolicyViolationError: On policy blocks
            RateLimitError: On rate limit exceeded
        """
        resolved_intent = intent or self.intent
        domain = parse_domain(url_or_domain)
        url = self._normalize_url(url_or_domain)

        try:
            # Try to fetch the document
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Validate with Pydantic if enabled
            if self.validate_schema:
                document = AIIndexDocument(**data)
            else:
                document = AIIndexDocument.model_construct(**data)

            # Fetch and evaluate policy
            if self.respect_policy_blocks:
                policy = self.policy_enforcer.fetch_policy(domain, document)
                allowed, requires_attribution, _ = self.policy_enforcer.evaluate_policy(
                    domain, resolved_intent, document
                )

                # Apply rate limiting if policy exists
                if policy:
                    self.policy_enforcer.apply_rate_limit(domain, policy)

            return document

        except requests.HTTPError as e:
            # Handle 403 Forbidden - check for denial receipt
            if e.response.status_code == 403:
                denial_receipt = self.policy_enforcer.parse_denial_receipt(e.response)
                if denial_receipt:
                    error_msg = f"Access denied (403): {denial_receipt.reason}"
                    if denial_receipt.retry_after:
                        error_msg += f" - Retry after {denial_receipt.retry_after}s"
                    raise Exception(error_msg)

            # Handle 404 Not Found - try render fallback if enabled
            if e.response.status_code == 404 and self.enable_render_fallback:
                print("ai-index.json not found, trying render fallback...")
                render_response = self.render_adapter.fetch_rendered_content(
                    domain,
                    None,
                    self.client_id,
                    resolved_intent
                )

                if render_response and render_response.rendered_text:
                    # Create a synthetic AIIndexDocument from rendered content
                    from datetime import datetime
                    synthetic_doc = AIIndexDocument(
                        version="1.1",
                        publisher_id=domain,
                        domain=domain,
                        last_updated=datetime.utcnow(),
                        publisher={
                            "name": domain,
                            "description": "Content from render fallback",
                        },
                        pages=[
                            {
                                "url": str(render_response.url),
                                "title": domain,
                                "summary": render_response.rendered_text[:500],
                            }
                        ],
                        metadata={
                            "source": "render-fallback",
                            **self.render_adapter.get_metadata(render_response),
                        },
                    )
                    return synthetic_doc

            raise Exception(f"Failed to fetch ai-index.json: {e}")

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch ai-index.json: {e}")
        except (ValidationError, JsonSchemaValidationError) as e:
            raise Exception(f"Schema validation failed: {e}")

    def fetch_batch(
        self, urls: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple ai-index.json files in batch.

        Args:
            urls: List of URLs or domains

        Returns:
            List of results with 'url', 'document' (if success), or 'error'
        """
        results = []

        for url in urls:
            try:
                document = self.fetch(url)
                results.append({
                    "url": url,
                    "document": document,
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "error": str(e),
                })

        return results

    def probe(self, domain: str) -> bool:
        """
        Check if a domain has an ai-index.json file.

        Args:
            domain: Domain name to probe

        Returns:
            True if ai-index.json exists and is accessible
        """
        url = self._normalize_url(domain)

        try:
            response = self.session.head(url, timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_content_hash(self, document: AIIndexDocument) -> str:
        """
        Compute SHA-256 hash of the document content.

        Args:
            document: AIIndex document

        Returns:
            Hex-encoded SHA-256 hash
        """
        content = document.model_dump_json(exclude_none=True)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def extract_page_urls(self, document: AIIndexDocument) -> List[str]:
        """
        Extract all page URLs from the document.

        Args:
            document: AIIndex document

        Returns:
            List of page URLs
        """
        if not document.pages:
            return []
        return [str(page.url) for page in document.pages]

    def extract_entities_by_type(
        self, document: AIIndexDocument, entity_type: str
    ) -> List[Entity]:
        """
        Extract entities filtered by type.

        Args:
            document: AIIndex document
            entity_type: Entity type to filter (e.g., "Person", "Organization")

        Returns:
            List of entities matching the type
        """
        if not document.entities:
            return []
        return [entity for entity in document.entities if entity.type.value == entity_type]

    def get_faq_by_category(
        self, document: AIIndexDocument, category: Optional[str] = None
    ) -> List[FAQ]:
        """
        Get FAQ items, optionally filtered by category.

        Args:
            document: AIIndex document
            category: Optional category filter

        Returns:
            List of FAQ items
        """
        if not document.faq:
            return []

        if category:
            return [item for item in document.faq if item.category == category]

        return document.faq

    def _normalize_url(self, url_or_domain: str) -> str:
        """
        Normalize URL to ai-index.json endpoint.

        Args:
            url_or_domain: URL or domain

        Returns:
            Full URL to ai-index.json
        """
        # If it's already a full URL to ai-index.json, return as-is
        if 'ai-index.json' in url_or_domain:
            return url_or_domain

        # Remove protocol if present
        domain = url_or_domain.replace('https://', '').replace('http://', '')

        # Remove trailing slash
        domain = domain.rstrip('/')

        # Remove path if present
        domain = domain.split('/')[0]

        # Construct full URL
        return f"https://{domain}/ai-index.json"

    def validate_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a document against the schema.

        Args:
            data: Raw document data

        Returns:
            Dictionary with 'valid' (bool) and optional 'errors' (list)
        """
        try:
            AIIndexDocument(**data)
            return {"valid": True}
        except ValidationError as e:
            return {
                "valid": False,
                "errors": [
                    {
                        "field": ".".join(str(loc) for loc in error["loc"]),
                        "message": error["msg"],
                    }
                    for error in e.errors()
                ],
            }

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "AIIndexReader":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
