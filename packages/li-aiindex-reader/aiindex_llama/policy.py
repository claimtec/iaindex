"""
AIIndex v1.1 Policy Discovery and Enforcement
"""

import time
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

import requests

from .types import (
    AIIndexDocument,
    AIIndexPolicy,
    PolicyAction,
    PolicyViolationError,
    RateLimitError,
    DenialReceipt,
)


class PolicyEnforcer:
    """
    Policy enforcement for AIIndex v1.1.

    Handles:
    - Policy discovery (well-known endpoint + fallback)
    - Policy evaluation (training/retrieval blocks)
    - Rate limiting
    - Denial receipt parsing
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize PolicyEnforcer.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "X-AIIndex-Version": "v1.1",
        })

        # Caching
        self.policy_cache: Dict[str, Tuple[AIIndexPolicy, float]] = {}
        self.last_request_time: Dict[str, float] = {}
        self.request_counts: Dict[str, Dict] = {}

    def fetch_policy(
        self,
        domain: str,
        aiindex_doc: Optional[AIIndexDocument] = None
    ) -> Optional[AIIndexPolicy]:
        """
        Fetch policy with fallback mechanism.

        1. Try /.well-known/aiindex-policy.json first
        2. Fall back to ai-index.json policy block

        Args:
            domain: Domain to fetch policy for
            aiindex_doc: Optional AIIndex document with embedded policy

        Returns:
            AIIndexPolicy if found, None otherwise
        """
        # Check cache first
        if domain in self.policy_cache:
            policy, expires_at = self.policy_cache[domain]
            if time.time() < expires_at:
                return policy

        # Try well-known endpoint first
        try:
            well_known_url = f"https://{domain}/.well-known/aiindex-policy.json"
            response = self.session.get(well_known_url, timeout=self.timeout)

            if response.status_code == 200:
                policy_data = response.json()
                policy = AIIndexPolicy(**policy_data)
                self._cache_policy(domain, policy)
                return policy
        except Exception:
            # Well-known endpoint not found, fall back
            pass

        # Fall back to policy embedded in ai-index.json
        if aiindex_doc and hasattr(aiindex_doc, 'policy'):
            try:
                embedded_policy = AIIndexPolicy(
                    version="1.1",
                    domain=domain,
                    policy=aiindex_doc.policy,
                    receipts=getattr(aiindex_doc, 'receipts', None),
                    render_fallback=getattr(aiindex_doc, 'render_fallback', None),
                    updated_at=aiindex_doc.last_updated,
                )
                self._cache_policy(domain, embedded_policy)
                return embedded_policy
            except Exception:
                pass

        return None

    def evaluate_policy(
        self,
        domain: str,
        intent: str,
        aiindex_doc: Optional[AIIndexDocument] = None
    ) -> Tuple[bool, bool, Optional[AIIndexPolicy]]:
        """
        Evaluate policy for a specific intent.

        Args:
            domain: Domain to evaluate
            intent: Intent ('training' or 'retrieval')
            aiindex_doc: Optional AIIndex document

        Returns:
            Tuple of (allowed, requires_attribution, policy)

        Raises:
            PolicyViolationError: If access is blocked
        """
        policy = self.fetch_policy(domain, aiindex_doc)

        if not policy:
            # No policy found, default to allow
            return True, False, None

        # Get action for the intent
        action = None
        if intent == 'training':
            action = policy.policy.training
        elif intent == 'retrieval':
            action = policy.policy.retrieval

        if action == PolicyAction.BLOCK:
            denial_receipt = DenialReceipt(
                denied=True,
                reason=f"{intent} is blocked by publisher policy",
                policy_url=f"https://{domain}/.well-known/aiindex-policy.json",
            )
            raise PolicyViolationError(
                f"Access denied: {intent} is blocked for {domain}",
                PolicyAction.BLOCK,
                intent,
                denial_receipt
            )

        requires_attribution = action == PolicyAction.REQUIRE_ATTRIBUTION

        return True, requires_attribution, policy

    def apply_rate_limit(
        self,
        domain: str,
        policy: Optional[AIIndexPolicy]
    ) -> None:
        """
        Apply rate limiting based on policy.

        Args:
            domain: Domain being accessed
            policy: Policy with rate limit rules

        Raises:
            RateLimitError: If rate limit exceeded
        """
        if not policy or not policy.policy.rate_limit:
            return

        rate_limit = policy.policy.rate_limit
        now = time.time()

        # Check delay between requests
        if rate_limit.delay_ms:
            last_request = self.last_request_time.get(domain, 0)
            time_since_last = (now - last_request) * 1000  # Convert to ms

            if time_since_last < rate_limit.delay_ms:
                wait_time = (rate_limit.delay_ms - time_since_last) / 1000
                time.sleep(wait_time)

            self.last_request_time[domain] = time.time()

        # Initialize or get counters
        if domain not in self.request_counts:
            self.request_counts[domain] = {
                'minute': 0,
                'hour': 0,
                'minute_start': now,
                'hour_start': now,
            }

        counts = self.request_counts[domain]

        # Reset counters if time windows have passed
        if now - counts['minute_start'] >= 60:
            counts['minute'] = 0
            counts['minute_start'] = now

        if now - counts['hour_start'] >= 3600:
            counts['hour'] = 0
            counts['hour_start'] = now

        # Check limits
        if rate_limit.requests_per_minute:
            if counts['minute'] >= rate_limit.requests_per_minute:
                retry_after = int(60 - (now - counts['minute_start']))
                raise RateLimitError(
                    f"Rate limit exceeded: {rate_limit.requests_per_minute} requests per minute",
                    retry_after
                )

        if rate_limit.requests_per_hour:
            if counts['hour'] >= rate_limit.requests_per_hour:
                retry_after = int(3600 - (now - counts['hour_start']))
                raise RateLimitError(
                    f"Rate limit exceeded: {rate_limit.requests_per_hour} requests per hour",
                    retry_after
                )

        # Increment counters
        counts['minute'] += 1
        counts['hour'] += 1

    def parse_denial_receipt(self, response: requests.Response) -> Optional[DenialReceipt]:
        """
        Parse denial receipt from 403 response.

        Args:
            response: HTTP response object

        Returns:
            DenialReceipt if found, None otherwise
        """
        if response.status_code == 403:
            try:
                data = response.json()
                if isinstance(data, dict):
                    return DenialReceipt(
                        denied=data.get('denied', True),
                        reason=data.get('reason', 'Access denied'),
                        policy_url=data.get('policy_url'),
                        retry_after=data.get('retry_after'),
                        alternative_endpoint=data.get('alternative_endpoint'),
                    )
            except Exception:
                pass

        return None

    def requires_signed_receipt(self, policy: Optional[AIIndexPolicy]) -> bool:
        """
        Check if receipts are required.

        Args:
            policy: Policy to check

        Returns:
            True if signed receipts are required
        """
        return policy and policy.receipts and policy.receipts.require_signed is True

    def get_webhook_url(self, policy: Optional[AIIndexPolicy]) -> Optional[str]:
        """
        Get webhook URL from policy.

        Args:
            policy: Policy to check

        Returns:
            Webhook URL if available
        """
        if policy and policy.receipts:
            return str(policy.receipts.webhook_url) if policy.receipts.webhook_url else None
        return None

    def clear_cache(self, domain: Optional[str] = None) -> None:
        """
        Clear cache for a domain or all domains.

        Args:
            domain: Optional domain to clear (clears all if None)
        """
        if domain:
            self.policy_cache.pop(domain, None)
            self.last_request_time.pop(domain, None)
            self.request_counts.pop(domain, None)
        else:
            self.policy_cache.clear()
            self.last_request_time.clear()
            self.request_counts.clear()

    def _cache_policy(self, domain: str, policy: AIIndexPolicy) -> None:
        """
        Cache policy with 1 hour TTL.

        Args:
            domain: Domain to cache for
            policy: Policy to cache
        """
        expires_at = time.time() + 3600  # 1 hour
        self.policy_cache[domain] = (policy, expires_at)

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "PolicyEnforcer":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


def parse_domain(url: str) -> str:
    """
    Parse domain from URL.

    Args:
        url: URL or domain string

    Returns:
        Domain name
    """
    try:
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        parsed = urlparse(url)
        return parsed.hostname or url.replace('https://', '').replace('http://', '').split('/')[0]
    except Exception:
        return url.replace('https://', '').replace('http://', '').split('/')[0]
