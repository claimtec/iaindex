"""
Policy Enforcement Middleware

Fetches and evaluates AIIndex policies from publisher domains.
Checks training vs retrieval intent, validates client allowlists/blocklists,
and enforces rate limits with signed denial receipts.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, Literal
from datetime import datetime, timedelta
from pydantic import BaseModel, HttpUrl, Field
import httpx
import logging
import json
import hashlib
from functools import lru_cache
import time

logger = logging.getLogger(__name__)


class PolicyConfig(BaseModel):
    """AIIndex policy configuration"""
    version: str = Field(default="1.0")
    publisher_domain: str
    training_allowed: bool = Field(default=False)
    retrieval_allowed: bool = Field(default=True)
    training_allowlist: list[str] = Field(default_factory=list)
    training_blocklist: list[str] = Field(default_factory=list)
    retrieval_allowlist: list[str] = Field(default_factory=list)
    retrieval_blocklist: list[str] = Field(default_factory=list)
    rate_limits: Dict[str, int] = Field(default_factory=dict)
    policy_effective_date: Optional[datetime] = None
    policy_url: Optional[str] = None


class PolicyCache:
    """In-memory policy cache with TTL"""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, tuple[PolicyConfig, float]] = {}
        self._ttl = ttl_seconds

    def get(self, domain: str) -> Optional[PolicyConfig]:
        """Get cached policy if not expired"""
        if domain in self._cache:
            policy, timestamp = self._cache[domain]
            if time.time() - timestamp < self._ttl:
                logger.debug(f"Cache hit for domain: {domain}")
                return policy
            else:
                logger.debug(f"Cache expired for domain: {domain}")
                del self._cache[domain]
        return None

    def set(self, domain: str, policy: PolicyConfig):
        """Store policy in cache"""
        self._cache[domain] = (policy, time.time())
        logger.debug(f"Cached policy for domain: {domain}")

    def clear(self):
        """Clear all cached policies"""
        self._cache.clear()
        logger.info("Policy cache cleared")

    def invalidate(self, domain: str):
        """Invalidate specific domain cache"""
        if domain in self._cache:
            del self._cache[domain]
            logger.debug(f"Invalidated cache for domain: {domain}")


# Global policy cache instance (5 minute TTL)
policy_cache = PolicyCache(ttl_seconds=300)


class PolicyEnforcer:
    """Policy evaluation and enforcement"""

    def __init__(self, request: Request, http_client: Optional[httpx.AsyncClient] = None):
        self.request = request
        self.http_client = http_client or httpx.AsyncClient(timeout=10.0)
        self._owned_client = http_client is None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._owned_client:
            await self.http_client.aclose()

    async def fetch_policy(self, domain: str) -> Optional[PolicyConfig]:
        """
        Fetch AIIndex policy from domain

        Tries in order:
        1. /.well-known/aiindex-policy.json
        2. /ai-index.json (policy block)
        """
        # Check cache first
        cached_policy = policy_cache.get(domain)
        if cached_policy:
            return cached_policy

        # Try .well-known endpoint
        well_known_url = f"https://{domain}/.well-known/aiindex-policy.json"
        policy = await self._fetch_from_url(well_known_url, domain)

        if not policy:
            # Try ai-index.json with policy block
            ai_index_url = f"https://{domain}/ai-index.json"
            policy = await self._fetch_from_ai_index(ai_index_url, domain)

        if policy:
            policy_cache.set(domain, policy)
            logger.info(f"Successfully fetched policy for domain: {domain}")
        else:
            logger.warning(f"No policy found for domain: {domain}")

        return policy

    async def _fetch_from_url(self, url: str, domain: str) -> Optional[PolicyConfig]:
        """Fetch policy from specific URL"""
        try:
            response = await self.http_client.get(url)
            if response.status_code == 200:
                data = response.json()
                return self._parse_policy(data, domain, url)
        except httpx.HTTPError as e:
            logger.debug(f"Failed to fetch from {url}: {e}")
        except Exception as e:
            logger.error(f"Error fetching policy from {url}: {e}")
        return None

    async def _fetch_from_ai_index(self, url: str, domain: str) -> Optional[PolicyConfig]:
        """Fetch policy from ai-index.json file"""
        try:
            response = await self.http_client.get(url)
            if response.status_code == 200:
                data = response.json()
                # Extract policy block if it exists
                policy_data = data.get("policy", data)
                return self._parse_policy(policy_data, domain, url)
        except httpx.HTTPError as e:
            logger.debug(f"Failed to fetch ai-index.json from {url}: {e}")
        except Exception as e:
            logger.error(f"Error fetching ai-index.json from {url}: {e}")
        return None

    def _parse_policy(self, data: Dict[str, Any], domain: str, url: str) -> Optional[PolicyConfig]:
        """Parse policy data into PolicyConfig"""
        try:
            # Add domain and policy URL if not present
            if "publisher_domain" not in data:
                data["publisher_domain"] = domain
            if "policy_url" not in data:
                data["policy_url"] = url

            # Parse effective date if string
            if "policy_effective_date" in data and isinstance(data["policy_effective_date"], str):
                data["policy_effective_date"] = datetime.fromisoformat(
                    data["policy_effective_date"].replace("Z", "+00:00")
                )

            return PolicyConfig(**data)
        except Exception as e:
            logger.error(f"Error parsing policy data: {e}")
            return None

    def extract_headers(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract AIIndex-specific headers from request"""
        intent = self.request.headers.get("X-AIIndex-Intent", "").lower()
        client_id = self.request.headers.get("X-AIIndex-Client-ID", "").strip()
        version = self.request.headers.get("X-AIIndex-Version", "1.0")

        # Validate intent
        if intent and intent not in ["training", "retrieval"]:
            logger.warning(f"Invalid intent header: {intent}")
            intent = None

        return intent, client_id, version

    async def evaluate_policy(
        self,
        domain: str,
        intent: Literal["training", "retrieval"],
        client_id: str
    ) -> tuple[bool, Optional[str]]:
        """
        Evaluate if request is allowed by policy

        Returns:
            (allowed, violation_reason) tuple
        """
        policy = await self.fetch_policy(domain)

        if not policy:
            # No policy found - default to allow retrieval, block training
            if intent == "training":
                return False, "no_policy_training_blocked"
            return True, None

        # Check if intent is allowed
        if intent == "training":
            if not policy.training_allowed:
                return False, "blocked_training"

            # Check allowlist
            if policy.training_allowlist:
                if client_id not in policy.training_allowlist:
                    return False, "not_in_training_allowlist"

            # Check blocklist
            if client_id in policy.training_blocklist:
                return False, "blocked_training"

        elif intent == "retrieval":
            if not policy.retrieval_allowed:
                return False, "blocked_retrieval"

            # Check allowlist
            if policy.retrieval_allowlist:
                if client_id not in policy.retrieval_allowlist:
                    return False, "not_in_retrieval_allowlist"

            # Check blocklist
            if client_id in policy.retrieval_blocklist:
                return False, "blocked_retrieval"

        return True, None

    async def enforce(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Enforce policy for request

        Returns:
            None if allowed, violation info dict if denied
        """
        intent, client_id, version = self.extract_headers()

        # Require client_id
        if not client_id:
            return {
                "domain": domain,
                "client_id": None,
                "violation_reason": "unknown_client",
                "policy_url": None,
                "policy_effective_date": None
            }

        # Default to retrieval if not specified
        if not intent:
            intent = "retrieval"
            logger.debug(f"No intent specified, defaulting to retrieval for client: {client_id}")

        # Evaluate policy
        allowed, violation_reason = await self.evaluate_policy(domain, intent, client_id)

        if not allowed:
            policy = await self.fetch_policy(domain)
            return {
                "domain": domain,
                "client_id": client_id,
                "intent": intent,
                "violation_reason": violation_reason,
                "policy_url": policy.policy_url if policy else None,
                "policy_effective_date": policy.policy_effective_date if policy else None
            }

        logger.info(f"Policy check passed - Domain: {domain}, Client: {client_id}, Intent: {intent}")
        return None


async def policy_enforcement_middleware(request: Request, call_next):
    """
    FastAPI middleware for policy enforcement

    Checks AIIndex policies and blocks unauthorized requests
    """
    # Skip policy check for certain endpoints
    skip_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/v1/auth/"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        return await call_next(request)

    # Extract domain from request (could be from body, query, or path)
    domain = None

    # Try to get domain from query params
    if "domain" in request.query_params:
        domain = request.query_params["domain"]

    # If no domain found, proceed without policy check
    if not domain:
        return await call_next(request)

    # Enforce policy
    async with PolicyEnforcer(request) as enforcer:
        violation = await enforcer.enforce(domain)

        if violation:
            # Import denial receipt generator
            from .denial_receipt import DenialReceiptGenerator

            # Generate signed denial receipt
            generator = DenialReceiptGenerator()
            denial_receipt = await generator.generate(
                domain=violation["domain"],
                client_id=violation["client_id"],
                violation_reason=violation["violation_reason"],
                intent=violation.get("intent"),
                policy_url=violation["policy_url"],
                policy_effective_date=violation["policy_effective_date"]
            )

            logger.warning(
                f"Policy violation - Domain: {domain}, "
                f"Client: {violation['client_id']}, "
                f"Reason: {violation['violation_reason']}"
            )

            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=denial_receipt
            )

    # Policy check passed
    return await call_next(request)


def clear_policy_cache():
    """Clear the policy cache (useful for testing)"""
    policy_cache.clear()


def invalidate_policy(domain: str):
    """Invalidate cached policy for specific domain"""
    policy_cache.invalidate(domain)
