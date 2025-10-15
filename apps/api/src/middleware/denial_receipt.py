"""
Denial Receipt Generator

Creates cryptographically signed denial receipts for policy violations.
Returns structured denial information with publisher signature.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, timezone
import uuid
import json
import hashlib
import logging
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
import os

logger = logging.getLogger(__name__)


class DenialReason:
    """Standard denial reason codes"""
    BLOCKED_TRAINING = "blocked_training"
    BLOCKED_RETRIEVAL = "blocked_retrieval"
    RATE_LIMIT_EXCEEDED = "rate_limit"
    UNKNOWN_CLIENT = "unknown_client"
    NOT_IN_ALLOWLIST = "not_in_allowlist"
    NO_POLICY_TRAINING_BLOCKED = "no_policy_training_blocked"
    INVALID_SIGNATURE = "invalid_signature"
    FRAUD_DETECTED = "fraud_detected"


class DenialReceipt(BaseModel):
    """Denial receipt structure"""
    receipt_id: str = Field(..., description="Unique receipt ID")
    receipt_type: str = Field(default="denial", description="Receipt type")
    denied_at: datetime = Field(..., description="Denial timestamp")
    domain: str = Field(..., description="Publisher domain")
    client_id: Optional[str] = Field(None, description="Client identifier")
    intent: Optional[str] = Field(None, description="Request intent (training/retrieval)")
    violation_reason: str = Field(..., description="Reason for denial")
    policy_url: Optional[str] = Field(None, description="URL to publisher policy")
    policy_effective_date: Optional[datetime] = Field(None, description="Policy effective date")
    signature: Optional[str] = Field(None, description="Cryptographic signature")
    signature_algorithm: str = Field(default="RSA-SHA256", description="Signature algorithm")
    public_key_url: Optional[str] = Field(None, description="URL to publisher's public key")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DenialReceiptGenerator:
    """Generates and signs denial receipts"""

    def __init__(self, private_key_path: Optional[str] = None):
        """
        Initialize denial receipt generator

        Args:
            private_key_path: Path to private key file (PEM format)
        """
        self.private_key_path = private_key_path or os.getenv(
            "PUBLISHER_PRIVATE_KEY_PATH",
            "/etc/iaindex/publisher_private_key.pem"
        )
        self._private_key = None

    def _load_private_key(self) -> Optional[rsa.RSAPrivateKey]:
        """Load private key from file"""
        if self._private_key:
            return self._private_key

        try:
            if os.path.exists(self.private_key_path):
                with open(self.private_key_path, "rb") as key_file:
                    self._private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )
                logger.info("Private key loaded successfully")
                return self._private_key
        except Exception as e:
            logger.warning(f"Failed to load private key: {e}")

        return None

    def _generate_test_key(self) -> rsa.RSAPrivateKey:
        """Generate ephemeral key for testing/development"""
        logger.warning("Using ephemeral key - NOT for production use!")
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

    def _create_signature_payload(self, receipt: DenialReceipt) -> str:
        """Create canonical payload for signing"""
        payload_dict = {
            "receipt_id": receipt.receipt_id,
            "receipt_type": receipt.receipt_type,
            "denied_at": receipt.denied_at.isoformat(),
            "domain": receipt.domain,
            "client_id": receipt.client_id,
            "intent": receipt.intent,
            "violation_reason": receipt.violation_reason,
            "policy_url": receipt.policy_url
        }

        # Remove None values
        payload_dict = {k: v for k, v in payload_dict.items() if v is not None}

        # Create canonical JSON (sorted keys, no whitespace)
        canonical_json = json.dumps(payload_dict, sort_keys=True, separators=(",", ":"))
        return canonical_json

    def _sign_receipt(self, receipt: DenialReceipt) -> str:
        """Sign the denial receipt"""
        # Try to load private key
        private_key = self._load_private_key()

        # Fall back to ephemeral key if no key found
        if not private_key:
            private_key = self._generate_test_key()

        # Create signature payload
        payload = self._create_signature_payload(receipt)

        # Sign payload
        signature_bytes = private_key.sign(
            payload.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Encode signature as base64
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        return signature_b64

    async def generate(
        self,
        domain: str,
        client_id: Optional[str],
        violation_reason: str,
        intent: Optional[str] = None,
        policy_url: Optional[str] = None,
        policy_effective_date: Optional[datetime] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Generate signed denial receipt

        Args:
            domain: Publisher domain
            client_id: Client identifier
            violation_reason: Reason for denial
            intent: Request intent (training/retrieval)
            policy_url: URL to publisher policy
            policy_effective_date: Policy effective date
            metadata: Additional metadata

        Returns:
            Denial receipt as dictionary
        """
        receipt_id = str(uuid.uuid4())
        denied_at = datetime.now(timezone.utc)

        # Create receipt
        receipt = DenialReceipt(
            receipt_id=receipt_id,
            denied_at=denied_at,
            domain=domain,
            client_id=client_id,
            intent=intent,
            violation_reason=violation_reason,
            policy_url=policy_url,
            policy_effective_date=policy_effective_date,
            metadata=metadata or {}
        )

        # Add public key URL
        receipt.public_key_url = f"https://{domain}/.well-known/aiindex-public-key.pem"

        # Sign receipt
        try:
            signature = self._sign_receipt(receipt)
            receipt.signature = signature
            logger.info(f"Generated signed denial receipt: {receipt_id}")
        except Exception as e:
            logger.error(f"Failed to sign denial receipt: {e}")
            # Still return receipt without signature
            receipt.signature = None

        return receipt.model_dump(mode='json')

    def verify_receipt(self, receipt_data: dict, public_key: rsa.RSAPublicKey) -> bool:
        """
        Verify denial receipt signature

        Args:
            receipt_data: Receipt data dictionary
            public_key: Publisher's public key

        Returns:
            True if signature is valid
        """
        try:
            # Extract signature
            signature_b64 = receipt_data.get("signature")
            if not signature_b64:
                logger.warning("No signature in receipt")
                return False

            signature_bytes = base64.b64decode(signature_b64)

            # Recreate receipt without signature
            receipt_copy = receipt_data.copy()
            receipt_copy.pop("signature", None)

            # Parse dates
            if "denied_at" in receipt_copy:
                if isinstance(receipt_copy["denied_at"], str):
                    receipt_copy["denied_at"] = datetime.fromisoformat(
                        receipt_copy["denied_at"].replace("Z", "+00:00")
                    )

            if "policy_effective_date" in receipt_copy:
                if isinstance(receipt_copy["policy_effective_date"], str):
                    receipt_copy["policy_effective_date"] = datetime.fromisoformat(
                        receipt_copy["policy_effective_date"].replace("Z", "+00:00")
                    )

            receipt = DenialReceipt(**receipt_copy)

            # Create signature payload
            payload = self._create_signature_payload(receipt)

            # Verify signature
            public_key.verify(
                signature_bytes,
                payload.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            logger.info(f"Receipt signature verified: {receipt.receipt_id}")
            return True

        except Exception as e:
            logger.error(f"Receipt signature verification failed: {e}")
            return False


def create_denial_response(
    domain: str,
    client_id: Optional[str],
    violation_reason: str,
    intent: Optional[str] = None,
    policy_url: Optional[str] = None,
    policy_effective_date: Optional[datetime] = None,
    additional_info: Optional[str] = None
) -> dict:
    """
    Helper function to create denial response

    Args:
        domain: Publisher domain
        client_id: Client identifier
        violation_reason: Reason for denial
        intent: Request intent
        policy_url: URL to publisher policy
        policy_effective_date: Policy effective date
        additional_info: Additional information for client

    Returns:
        Formatted denial response
    """
    metadata = {}
    if additional_info:
        metadata["additional_info"] = additional_info

    # Map violation reasons to user-friendly messages
    messages = {
        DenialReason.BLOCKED_TRAINING: "Training access is blocked by publisher policy",
        DenialReason.BLOCKED_RETRIEVAL: "Retrieval access is blocked by publisher policy",
        DenialReason.RATE_LIMIT_EXCEEDED: "Rate limit exceeded for this client",
        DenialReason.UNKNOWN_CLIENT: "Client ID is required but not provided",
        DenialReason.NOT_IN_ALLOWLIST: "Client is not in the publisher's allowlist",
        DenialReason.NO_POLICY_TRAINING_BLOCKED: "No policy found, training blocked by default",
        DenialReason.INVALID_SIGNATURE: "Invalid or missing signature",
        DenialReason.FRAUD_DETECTED: "Fraudulent activity detected"
    }

    message = messages.get(violation_reason, "Access denied by publisher policy")
    metadata["message"] = message

    return {
        "error": "Forbidden",
        "message": message,
        "denial_receipt": {
            "receipt_id": str(uuid.uuid4()),
            "denied_at": datetime.now(timezone.utc).isoformat(),
            "domain": domain,
            "client_id": client_id,
            "intent": intent,
            "violation_reason": violation_reason,
            "policy_url": policy_url,
            "policy_effective_date": policy_effective_date.isoformat() if policy_effective_date else None,
            "metadata": metadata
        }
    }
