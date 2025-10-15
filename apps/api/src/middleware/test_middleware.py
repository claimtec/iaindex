"""
Test Suite for AIIndex Middleware

Run tests with: pytest test_middleware.py -v
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, AsyncMock, patch
import json

# Import middleware components
from middleware import (
    PolicyEnforcer,
    PolicyConfig,
    DenialReceiptGenerator,
    DenialReason,
    RedisRateLimiter,
    RateLimitConfig,
    BotReputationSystem,
    ViolationType,
    ReputationStatus,
    FraudDetector,
    FraudType,
    VersionNegotiator,
    ProtocolVersion
)


class TestPolicyEnforcement:
    """Test policy enforcement middleware"""

    @pytest.mark.asyncio
    async def test_policy_fetch(self):
        """Test fetching policy from domain"""
        mock_request = Mock()
        mock_request.headers = {}

        enforcer = PolicyEnforcer(mock_request)

        # Test with mock HTTP response
        with patch.object(enforcer.http_client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "version": "1.1",
                "publisher_domain": "example.com",
                "training_allowed": False,
                "retrieval_allowed": True
            }
            mock_get.return_value = mock_response

            policy = await enforcer.fetch_policy("example.com")

            assert policy is not None
            assert policy.publisher_domain == "example.com"
            assert policy.training_allowed is False
            assert policy.retrieval_allowed is True

    @pytest.mark.asyncio
    async def test_training_blocked(self):
        """Test that training is blocked when policy disallows it"""
        mock_request = Mock()
        mock_request.headers = {
            "X-AIIndex-Intent": "training",
            "X-AIIndex-Client-ID": "test-client"
        }

        enforcer = PolicyEnforcer(mock_request)

        # Mock policy
        policy = PolicyConfig(
            publisher_domain="example.com",
            training_allowed=False,
            retrieval_allowed=True
        )

        with patch.object(enforcer, 'fetch_policy', return_value=policy):
            allowed, reason = await enforcer.evaluate_policy(
                "example.com", "training", "test-client"
            )

            assert allowed is False
            assert reason == "blocked_training"

    @pytest.mark.asyncio
    async def test_allowlist_enforcement(self):
        """Test allowlist enforcement"""
        mock_request = Mock()
        enforcer = PolicyEnforcer(mock_request)

        policy = PolicyConfig(
            publisher_domain="example.com",
            training_allowed=True,
            training_allowlist=["openai-gpt", "anthropic-claude"]
        )

        # Allowed client
        with patch.object(enforcer, 'fetch_policy', return_value=policy):
            allowed, _ = await enforcer.evaluate_policy(
                "example.com", "training", "openai-gpt"
            )
            assert allowed is True

        # Not in allowlist
        with patch.object(enforcer, 'fetch_policy', return_value=policy):
            allowed, reason = await enforcer.evaluate_policy(
                "example.com", "training", "unknown-client"
            )
            assert allowed is False
            assert reason == "not_in_training_allowlist"


class TestDenialReceipts:
    """Test denial receipt generation"""

    @pytest.mark.asyncio
    async def test_receipt_generation(self):
        """Test generating denial receipt"""
        generator = DenialReceiptGenerator()

        receipt = await generator.generate(
            domain="example.com",
            client_id="test-client",
            violation_reason=DenialReason.BLOCKED_TRAINING,
            intent="training"
        )

        assert receipt["receipt_type"] == "denial"
        assert receipt["domain"] == "example.com"
        assert receipt["client_id"] == "test-client"
        assert receipt["violation_reason"] == "blocked_training"
        assert "receipt_id" in receipt
        assert "denied_at" in receipt

    @pytest.mark.asyncio
    async def test_receipt_signature(self):
        """Test that receipt includes signature"""
        generator = DenialReceiptGenerator()

        receipt = await generator.generate(
            domain="example.com",
            client_id="test-client",
            violation_reason=DenialReason.BLOCKED_TRAINING
        )

        # Should have signature (even if ephemeral key)
        # In production, this would use actual private key
        assert "signature" in receipt


class TestRateLimiting:
    """Test rate limiting functionality"""

    @pytest.mark.asyncio
    async def test_rate_limit_basic(self):
        """Test basic rate limiting"""
        limiter = RedisRateLimiter()
        config = RateLimitConfig(
            requests_per_minute=10,
            requests_per_hour=100
        )

        # First requests should be allowed
        for i in range(10):
            allowed, info = await limiter.check_rate_limit(
                "test-client", config, "minute"
            )
            assert allowed is True

        # 11th request should be blocked
        allowed, info = await limiter.check_rate_limit(
            "test-client", config, "minute"
        )
        assert allowed is False
        assert info["allowed"] is False

    @pytest.mark.asyncio
    async def test_whitelist_bypass(self):
        """Test that whitelisted clients bypass rate limits"""
        limiter = RedisRateLimiter()
        config = RateLimitConfig(
            requests_per_minute=5,
            whitelist=["openai-gpt"]
        )

        # Whitelisted client should never be blocked
        for i in range(100):
            allowed, info = await limiter.check_rate_limit(
                "openai-gpt", config, "minute"
            )
            assert allowed is True
            assert info.get("whitelisted") is True

    @pytest.mark.asyncio
    async def test_burst_allowance(self):
        """Test burst allowance"""
        limiter = RedisRateLimiter()
        config = RateLimitConfig(
            requests_per_minute=10,
            burst=5
        )

        # Should allow up to limit + burst
        for i in range(15):
            allowed, info = await limiter.check_rate_limit(
                "test-client", config, "minute"
            )
            assert allowed is True

        # 16th should be blocked
        allowed, info = await limiter.check_rate_limit(
            "test-client", config, "minute"
        )
        assert allowed is False


class TestBotReputation:
    """Test bot reputation system"""

    @pytest.mark.asyncio
    async def test_initial_reputation(self):
        """Test initial reputation for new client"""
        system = BotReputationSystem()

        reputation = await system.get_reputation("new-client")

        assert reputation.client_id == "new-client"
        assert reputation.status == ReputationStatus.NEUTRAL
        assert reputation.reputation_score == 50.0
        assert reputation.violation_count == 0

    @pytest.mark.asyncio
    async def test_verified_clients(self):
        """Test that verified clients have high reputation"""
        system = BotReputationSystem()

        reputation = await system.get_reputation("openai-gpt")

        assert reputation.status == ReputationStatus.VERIFIED
        assert reputation.reputation_score == 100.0

    @pytest.mark.asyncio
    async def test_violation_recording(self):
        """Test recording violations"""
        system = BotReputationSystem()

        initial = await system.get_reputation("test-client")
        initial_score = initial.reputation_score

        # Record violation
        await system.record_violation(
            client_id="test-client",
            violation_type=ViolationType.FRAUD_ATTEMPT,
            description="Test fraud",
            severity=8
        )

        updated = await system.get_reputation("test-client")

        assert updated.violation_count == 1
        assert updated.reputation_score < initial_score
        assert updated.last_violation is not None

    @pytest.mark.asyncio
    async def test_auto_blocking(self):
        """Test automatic blocking after threshold violations"""
        system = BotReputationSystem()

        # Record multiple violations
        for i in range(6):
            await system.record_violation(
                client_id="bad-client",
                violation_type=ViolationType.FRAUD_ATTEMPT,
                description=f"Violation {i}",
                severity=7
            )

        reputation = await system.get_reputation("bad-client")

        # Should be blocked after 5 violations
        assert reputation.status == ReputationStatus.BLOCKED
        assert reputation.blocked_at is not None

    @pytest.mark.asyncio
    async def test_reputation_improvement(self):
        """Test improving reputation"""
        system = BotReputationSystem()

        # Get initial score
        initial = await system.get_reputation("test-client")
        initial_score = initial.reputation_score

        # Improve reputation
        await system.improve_reputation("test-client", amount=10.0)

        updated = await system.get_reputation("test-client")

        assert updated.reputation_score == initial_score + 10.0


class TestFraudDetection:
    """Test fraud detection system"""

    @pytest.mark.asyncio
    async def test_clock_skew_detection(self):
        """Test clock skew detection"""
        detector = FraudDetector()

        # Old timestamp (10 minutes ago)
        old_time = datetime.now(timezone.utc) - timedelta(minutes=10)

        alert = await detector.check_clock_skew(
            receipt_id="test-receipt",
            timestamp=old_time,
            client_id="test-client"
        )

        assert alert is not None
        assert alert.fraud_type == FraudType.CLOCK_SKEW
        assert alert.severity >= 5

    @pytest.mark.asyncio
    async def test_signature_reuse_detection(self):
        """Test signature reuse detection"""
        detector = FraudDetector()

        # First use should be OK
        alert1 = await detector.check_signature_reuse(
            receipt_id="receipt-1",
            signature="sig123",
            client_id="test-client"
        )
        assert alert1 is None

        # Second use should trigger alert
        alert2 = await detector.check_signature_reuse(
            receipt_id="receipt-2",
            signature="sig123",
            client_id="test-client"
        )
        assert alert2 is not None
        assert alert2.fraud_type == FraudType.SIGNATURE_REUSE

    @pytest.mark.asyncio
    async def test_batch_fraud_detection(self):
        """Test batch fraud detection"""
        detector = FraudDetector()

        # Submit many receipts quickly
        for i in range(12):
            alert = await detector.check_batch_fraud("test-client")

        # Should have triggered batch fraud alert
        assert alert is not None
        assert alert.fraud_type == FraudType.BATCH_FRAUD

    @pytest.mark.asyncio
    async def test_content_hash_mismatch(self):
        """Test content hash mismatch detection"""
        detector = FraudDetector()

        alert = await detector.check_content_hash(
            receipt_id="test-receipt",
            provided_hash="wrong_hash",
            actual_content="test content",
            client_id="test-client"
        )

        assert alert is not None
        assert alert.fraud_type == FraudType.CONTENT_HASH_MISMATCH
        assert alert.severity >= 8

    @pytest.mark.asyncio
    async def test_duplicate_receipt_detection(self):
        """Test duplicate receipt detection"""
        detector = FraudDetector()

        # First submission OK
        alert1 = await detector.check_duplicate_receipt(
            receipt_id="receipt-123",
            client_id="test-client"
        )
        assert alert1 is None

        # Second submission should alert
        alert2 = await detector.check_duplicate_receipt(
            receipt_id="receipt-123",
            client_id="test-client"
        )
        assert alert2 is not None
        assert alert2.fraud_type == FraudType.DUPLICATE_RECEIPT


class TestVersionNegotiation:
    """Test protocol version negotiation"""

    def test_parse_version_header(self):
        """Test parsing version header"""
        negotiator = VersionNegotiator()

        mock_request = Mock()

        # Test with v prefix
        mock_request.headers = {"X-AIIndex-Version": "v1.1"}
        version = negotiator.parse_version_header(mock_request)
        assert version == ProtocolVersion.V1_1

        # Test without v prefix
        mock_request.headers = {"X-AIIndex-Version": "1.2"}
        version = negotiator.parse_version_header(mock_request)
        assert version == ProtocolVersion.V1_2

        # Test default
        mock_request.headers = {}
        version = negotiator.parse_version_header(mock_request)
        assert version == negotiator.DEFAULT_VERSION

    def test_version_features(self):
        """Test getting version features"""
        negotiator = VersionNegotiator()

        features = negotiator.get_version_features(ProtocolVersion.V1_1)

        assert features.version == "1.1"
        assert "policy_enforcement" in features.features
        assert "denial_receipts" in features.features
        assert "RSA-SHA256" in features.signature_algorithms

    def test_version_comparison(self):
        """Test version comparison"""
        negotiator = VersionNegotiator()

        # 1.0 < 1.1
        assert negotiator.compare_versions("1.0", "1.1") == -1

        # 1.1 == 1.1
        assert negotiator.compare_versions("1.1", "1.1") == 0

        # 1.2 > 1.1
        assert negotiator.compare_versions("1.2", "1.1") == 1

    def test_unsupported_version_response(self):
        """Test unsupported version response"""
        negotiator = VersionNegotiator()

        response = negotiator.create_unsupported_response("2.0")

        assert "error" in response
        assert response["requested_version"] == "2.0"
        assert "supported_versions" in response


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
