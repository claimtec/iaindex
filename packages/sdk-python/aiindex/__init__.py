"""
AIIndex SDK for Python

A Python SDK for the AIIndex Protocol - enabling AI-readable website metadata,
access control, and cryptographic verification.
"""

from .generator import AIIndexGenerator
from .signer import SignatureManager
from .receipts import ReceiptHandler
from .validator import Validator
from .types import (
    AIIndexDocument,
    Publisher,
    Entity,
    Page,
    FAQ,
    AccessPolicy,
    Signature,
    Receipt,
    Access,
    Purpose,
    Attribution,
)

__version__ = "1.0.0"
__all__ = [
    "AIIndexGenerator",
    "SignatureManager",
    "ReceiptHandler",
    "Validator",
    "AIIndexDocument",
    "Publisher",
    "Entity",
    "Page",
    "FAQ",
    "AccessPolicy",
    "Signature",
    "Receipt",
    "Access",
    "Purpose",
    "Attribution",
]
