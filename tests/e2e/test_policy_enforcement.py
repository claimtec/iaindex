"""
End-to-End Tests: Policy Enforcement

Tests the complete policy enforcement flow including:
- Allow/block training and retrieval
- Denial receipt generation
- Required receipt validation
- Rate limiting
- Allowlist/blocklist enforcement
"""

import pytest
import httpx
import json
from datetime import datetime, timezone
from typing import Dict, Any


# Test configuration
API_BASE_URL = "http://localhost:3000"
TEST_PUBLISHER = "example-blog.com"


class TestPolicyEnforcement:
    """Policy enforcement E2E tests"""

    @pytest.mark.asyncio
    async def test_allowed_retrieval_returns_200(self):
        """Test 1: Allowed retrieval returns 200"""
        async with httpx.AsyncClient() as client:
            # Setup: Publisher allows retrieval
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "TestBot/1.0",
                    "X-AI-Intent": "retrieval"
                }
            )

            # Assert: Request succeeds
            assert response.status_code == 200
            data = response.json()
            assert data['policy']['retrieval'] == 'allow'

            # Verify headers
            assert 'X-AIIndex-Policy' in response.headers
            assert 'X-RateLimit-Limit' in response.headers

    @pytest.mark.asyncio
    async def test_blocked_training_returns_403_with_denial(self):
        """Test 2: Blocked training returns 403 with denial receipt"""
        async with httpx.AsyncClient() as client:
            # Setup: Publisher blocks training
            await self._set_publisher_policy(
                client,
                training='block',
                retrieval='allow'
            )

            # Request with training intent
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "TestBot/1.0",
                    "X-AI-Intent": "training",
                    "X-AI-Client-ID": "test-client-123"
                }
            )

            # Assert: Request blocked
            assert response.status_code == 403

            # Assert: Denial receipt provided
            data = response.json()
            assert 'denial_receipt' in data
            denial = data['denial_receipt']

            assert denial['denied'] is True
            assert denial['reason'] == 'policy_violation'
            assert denial['denied_action'] == 'training'
            assert denial['publisher_id'] == TEST_PUBLISHER
            assert 'timestamp' in denial
            assert 'receipt_id' in denial

            # Verify denial receipt signature
            assert 'signature' in denial
            assert denial['signature']['algorithm'] in ['ES256', 'RS256']

    @pytest.mark.asyncio
    async def test_missing_required_receipt_returns_403(self):
        """Test 3: Missing required receipt returns 403"""
        async with httpx.AsyncClient() as client:
            # Setup: Publisher requires signed receipts
            await self._set_publisher_policy(
                client,
                require_signed_receipt=True
            )

            # Request without receipt
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "TestBot/1.0",
                    "X-AI-Intent": "retrieval"
                }
            )

            # Assert: Request rejected
            assert response.status_code == 403
            data = response.json()
            assert 'denial_receipt' in data
            assert data['denial_receipt']['reason'] == 'receipt_required'

    @pytest.mark.asyncio
    async def test_rate_limit_returns_429(self):
        """Test 4: Rate limit returns 429"""
        async with httpx.AsyncClient() as client:
            # Setup: Low rate limit
            await self._set_publisher_policy(
                client,
                rate_limit=5  # 5 requests per minute
            )

            # Make requests until rate limited
            client_id = "rate-limit-test-client"
            success_count = 0
            rate_limited = False

            for i in range(10):
                response = await client.get(
                    f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                    headers={
                        "User-Agent": "TestBot/1.0",
                        "X-AI-Client-ID": client_id
                    }
                )

                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited = True
                    break

            # Assert: Rate limited
            assert rate_limited, "Expected to be rate limited"
            assert success_count <= 5, "Too many requests succeeded"

            # Verify rate limit headers
            assert 'X-RateLimit-Limit' in response.headers
            assert 'X-RateLimit-Remaining' in response.headers
            assert 'Retry-After' in response.headers

    @pytest.mark.asyncio
    async def test_allowlist_bypass_works(self):
        """Test 5: Allowlist bypass works"""
        async with httpx.AsyncClient() as client:
            # Setup: Block training by default, but allowlist specific client
            await self._set_publisher_policy(
                client,
                training='block',
                allowlist=['openai-gpt']
            )

            # Request from allowlisted client
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "GPT-Bot/1.0",
                    "X-AI-Client-ID": "openai-gpt",
                    "X-AI-Intent": "training"
                }
            )

            # Assert: Request allowed despite block policy
            assert response.status_code == 200

            # Request from non-allowlisted client
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "UnknownBot/1.0",
                    "X-AI-Client-ID": "unknown-client",
                    "X-AI-Intent": "training"
                }
            )

            # Assert: Request blocked
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_blocklist_returns_403(self):
        """Test 6: Blocklist returns 403"""
        async with httpx.AsyncClient() as client:
            # Setup: Blocklist specific client
            await self._set_publisher_policy(
                client,
                blocklist=['bad-scraper']
            )

            # Request from blocklisted client
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "BadScraper/1.0",
                    "X-AI-Client-ID": "bad-scraper"
                }
            )

            # Assert: Request blocked
            assert response.status_code == 403
            data = response.json()
            assert data['denial_receipt']['reason'] == 'client_blocked'

            # Request from normal client
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "GoodBot/1.0",
                    "X-AI-Client-ID": "good-client"
                }
            )

            # Assert: Request allowed
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_policy_version_negotiation(self):
        """Test 7: Policy version negotiation"""
        async with httpx.AsyncClient() as client:
            # Request v1.1 policy
            response = await client.get(
                f"{API_BASE_URL}/.well-known/aiindex-policy.json",
                headers={
                    "Accept": "application/json",
                    "X-AIIndex-Version": "1.1"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data['version'] == '1.1'
            assert 'policy' in data
            assert 'receipts' in data

            # Request v1.0 policy (backward compatibility)
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "Accept": "application/json",
                    "X-AIIndex-Version": "1.0"
                }
            )

            assert response.status_code == 200
            data = response.json()
            # Should return v1.0 compatible format
            assert 'access_policy' in data or 'policy' in data

    @pytest.mark.asyncio
    async def test_conditional_access_with_offer(self):
        """Test 8: Conditional access with require_offer"""
        async with httpx.AsyncClient() as client:
            # Setup: Require offer for training
            await self._set_publisher_policy(
                client,
                training='require_offer'
            )

            # Request without offer
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "TestBot/1.0",
                    "X-AI-Intent": "training"
                }
            )

            # Assert: Request blocked with offer required
            assert response.status_code == 403
            data = response.json()
            assert data['denial_receipt']['reason'] == 'offer_required'
            assert 'offer_url' in data['denial_receipt']

    # Helper methods

    async def _set_publisher_policy(
        self,
        client: httpx.AsyncClient,
        training: str = None,
        retrieval: str = None,
        require_signed_receipt: bool = None,
        rate_limit: int = None,
        allowlist: list = None,
        blocklist: list = None
    ):
        """Update publisher policy"""
        policy = {}

        if training:
            policy['training'] = training
        if retrieval:
            policy['retrieval'] = retrieval

        receipts = {}
        if require_signed_receipt is not None:
            receipts['require_signed'] = require_signed_receipt

        rate_limits = {}
        if rate_limit:
            rate_limits['requests_per_minute'] = rate_limit

        payload = {
            'policy': policy,
            'receipts': receipts,
            'rate_limits': rate_limits
        }

        if allowlist:
            payload['allowlist'] = allowlist
        if blocklist:
            payload['blocklist'] = blocklist

        # Update via API
        response = await client.patch(
            f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/policy",
            json=payload,
            headers={
                "Authorization": f"Bearer {self._get_test_api_key()}"
            }
        )

        assert response.status_code == 200

    def _get_test_api_key(self) -> str:
        """Get test API key"""
        # In production, load from environment
        return "test_api_key_12345"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
