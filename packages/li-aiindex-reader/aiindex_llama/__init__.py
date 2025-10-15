"""
AIIndex LlamaIndex Connector

Data loader for AI-readable website metadata (ai-index.json)
Includes receipt generation and cryptographic verification for LlamaIndex.
"""

from .reader import AIIndexReader
from .signer import AIIndexReceiptSigner
from .loader import AIIndexLoader
from .policy import PolicyEnforcer, parse_domain
from .renderer import RenderFallbackAdapter
from .types import (
    AIIndexDocument,
    Publisher,
    Entity,
    Page,
    FAQ,
    AccessPolicy,
    Signature,
    Verification,
    Receipt,
    Access,
    Purpose,
    Attribution,
    ReceiptMetadata,
    EntityType,
    ContentType,
    SignatureAlgorithm,
    HTTPMethod,
    PurposeType,
    AttributionMethod,
    # v1.1 Policy Types
    PolicyAction,
    RateLimit,
    PolicyRule,
    ReceiptPolicyConfig,
    RenderFallbackMode,
    RenderFallback,
    AIIndexPolicy,
    DenialReceipt,
    RenderResponse,
    PolicyViolationError,
    RateLimitError,
)

__version__ = "1.1.0"

__all__ = [
    "AIIndexReader",
    "AIIndexReceiptSigner",
    "AIIndexLoader",
    "PolicyEnforcer",
    "parse_domain",
    "RenderFallbackAdapter",
    "AIIndexDocument",
    "Publisher",
    "Entity",
    "Page",
    "FAQ",
    "AccessPolicy",
    "Signature",
    "Verification",
    "Receipt",
    "Access",
    "Purpose",
    "Attribution",
    "ReceiptMetadata",
    "EntityType",
    "ContentType",
    "SignatureAlgorithm",
    "HTTPMethod",
    "PurposeType",
    "AttributionMethod",
    # v1.1 Policy Types
    "PolicyAction",
    "RateLimit",
    "PolicyRule",
    "ReceiptPolicyConfig",
    "RenderFallbackMode",
    "RenderFallback",
    "AIIndexPolicy",
    "DenialReceipt",
    "RenderResponse",
    "PolicyViolationError",
    "RateLimitError",
]
