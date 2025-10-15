"""Middleware package for AIIndex API"""

from .policy import (
    PolicyEnforcer,
    PolicyConfig,
    policy_enforcement_middleware,
    clear_policy_cache,
    invalidate_policy
)

from .denial_receipt import (
    DenialReceiptGenerator,
    DenialReceipt,
    DenialReason,
    create_denial_response
)

from .rate_limiter import (
    RateLimitMiddleware,
    RateLimitConfig,
    RedisRateLimiter,
    create_rate_limiter
)

from .bot_reputation import (
    BotReputationSystem,
    BotReputation,
    ReputationStatus,
    ViolationType,
    get_reputation_system
)

from .fraud_detection import (
    FraudDetector,
    FraudAlert,
    FraudType,
    get_fraud_detector
)

from .version_negotiation import (
    VersionNegotiator,
    ProtocolVersion,
    VersionFeatures,
    version_negotiation_middleware,
    get_request_version,
    requires_version
)

__all__ = [
    # Policy enforcement
    "PolicyEnforcer",
    "PolicyConfig",
    "policy_enforcement_middleware",
    "clear_policy_cache",
    "invalidate_policy",

    # Denial receipts
    "DenialReceiptGenerator",
    "DenialReceipt",
    "DenialReason",
    "create_denial_response",

    # Rate limiting
    "RateLimitMiddleware",
    "RateLimitConfig",
    "RedisRateLimiter",
    "create_rate_limiter",

    # Bot reputation
    "BotReputationSystem",
    "BotReputation",
    "ReputationStatus",
    "ViolationType",
    "get_reputation_system",

    # Fraud detection
    "FraudDetector",
    "FraudAlert",
    "FraudType",
    "get_fraud_detector",

    # Version negotiation
    "VersionNegotiator",
    "ProtocolVersion",
    "VersionFeatures",
    "version_negotiation_middleware",
    "get_request_version",
    "requires_version",
]
