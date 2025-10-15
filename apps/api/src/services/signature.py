"""
Signature verification service
"""
import hashlib
import hmac
from typing import Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
import base64
import logging

logger = logging.getLogger(__name__)


class SignatureVerificationService:
    """Service for verifying receipt signatures"""

    @staticmethod
    def verify_hmac_signature(
        data: str,
        signature: str,
        secret_key: str
    ) -> bool:
        """
        Verify HMAC signature

        Args:
            data: Data that was signed
            signature: Signature to verify
            secret_key: Secret key for verification

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            expected_signature = hmac.new(
                secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"HMAC verification error: {e}")
            return False

    @staticmethod
    def verify_rsa_signature(
        data: str,
        signature: str,
        public_key_pem: str
    ) -> bool:
        """
        Verify RSA signature

        Args:
            data: Data that was signed
            signature: Base64-encoded signature
            public_key_pem: Public key in PEM format

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode()
            )

            # Decode signature
            signature_bytes = base64.b64decode(signature)

            # Verify signature
            public_key.verify(
                signature_bytes,
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            logger.warning("Invalid RSA signature")
            return False
        except Exception as e:
            logger.error(f"RSA verification error: {e}")
            return False

    @staticmethod
    def generate_receipt_hash(
        receipt_id: str,
        publisher_domain: str,
        article_url: str,
        timestamp: str
    ) -> str:
        """
        Generate hash of receipt data

        Args:
            receipt_id: Receipt ID
            publisher_domain: Publisher domain
            article_url: Article URL
            timestamp: ISO format timestamp

        Returns:
            Hex-encoded SHA256 hash
        """
        data = f"{receipt_id}|{publisher_domain}|{article_url}|{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def verify_receipt_signature(
        receipt_id: str,
        publisher_domain: str,
        article_url: str,
        timestamp: str,
        signature: str,
        verification_key: str,
        method: str = "hmac"
    ) -> bool:
        """
        Verify receipt signature with appropriate method

        Args:
            receipt_id: Receipt ID
            publisher_domain: Publisher domain
            article_url: Article URL
            timestamp: ISO format timestamp
            signature: Signature to verify
            verification_key: Key for verification (secret or public key)
            method: Verification method ('hmac' or 'rsa')

        Returns:
            True if signature is valid, False otherwise
        """
        receipt_hash = SignatureVerificationService.generate_receipt_hash(
            receipt_id, publisher_domain, article_url, timestamp
        )

        if method == "hmac":
            return SignatureVerificationService.verify_hmac_signature(
                receipt_hash, signature, verification_key
            )
        elif method == "rsa":
            return SignatureVerificationService.verify_rsa_signature(
                receipt_hash, signature, verification_key
            )
        else:
            logger.error(f"Unknown verification method: {method}")
            return False
