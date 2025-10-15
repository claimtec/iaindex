"""
AIIndexReceiptSigner - Create and sign access receipts, post to publisher webhooks
"""

import base64
import hashlib
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.exceptions import InvalidSignature

from .types import (
    AIIndexDocument,
    Receipt,
    Signature,
    SignatureAlgorithm,
    Access,
    Purpose,
    Attribution,
    ReceiptMetadata,
    HTTPMethod,
)


class AIIndexReceiptSigner:
    """
    Create and sign cryptographic receipts for AI access tracking.

    Supports ES256 (ECDSA) and RS256 (RSA) signature algorithms.

    Example:
        >>> signer = AIIndexReceiptSigner(
        ...     client_id="my-app",
        ...     private_key_pem=private_key,
        ...     key_id="key-001"
        ... )
        >>> receipt = signer.create_receipt(document, url="https://example.com/ai-index.json")
        >>> posted = signer.post_receipt(receipt, webhook_url)
    """

    def __init__(
        self,
        client_id: str,
        private_key_pem: bytes,
        key_id: str,
        client_name: Optional[str] = None,
        client_version: Optional[str] = None,
        algorithm: str = "ES256",
        webhook_retries: int = 3,
        webhook_timeout: int = 10,
        intent: str = "retrieval",
    ):
        """
        Initialize AIIndexReceiptSigner.

        Args:
            client_id: Unique client identifier
            private_key_pem: Private key in PEM format (bytes)
            key_id: Key identifier
            client_name: Client display name
            client_version: Client version
            algorithm: Signature algorithm ("ES256" or "RS256")
            webhook_retries: Number of retry attempts for webhooks
            webhook_timeout: Webhook request timeout in seconds
            intent: Default intent ('training' or 'retrieval')
        """
        self.client_id = client_id
        self.private_key_pem = private_key_pem
        self.key_id = key_id
        self.client_name = client_name or "LlamaIndex AIIndex Client"
        self.client_version = client_version or "1.0.0"
        self.algorithm = SignatureAlgorithm(algorithm)
        self.webhook_retries = webhook_retries
        self.webhook_timeout = webhook_timeout
        self.intent = intent

        self.backend = default_backend()
        self.private_key = self._load_private_key()

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": f"{self.client_name}/{self.client_version}",
            "X-AIIndex-Version": "v1.1",
            "X-AIIndex-Client-ID": self.client_id,
            "X-AIIndex-Intent": self.intent,
        })

    def _load_private_key(self) -> Any:
        """Load private key from PEM format."""
        return serialization.load_pem_private_key(
            self.private_key_pem,
            password=None,
            backend=self.backend
        )

    def create_receipt(
        self,
        document: AIIndexDocument,
        url: str,
        status_code: int = 200,
        pages_accessed: Optional[List[str]] = None,
        purpose: Optional[Purpose] = None,
        attribution: Optional[Attribution] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Receipt:
        """
        Create and sign a receipt for accessing an ai-index.json file.

        Args:
            document: AIIndex document that was accessed
            url: URL of the ai-index.json file
            status_code: HTTP status code received
            pages_accessed: List of page URLs accessed
            purpose: Purpose of access
            attribution: Attribution details
            metadata: Additional metadata

        Returns:
            Signed receipt
        """
        receipt_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Compute content hash
        content_hash = self._compute_hash(document.model_dump_json(exclude_none=True))

        # Build access details
        access = Access(
            url=url,
            method=HTTPMethod.GET,
            status_code=status_code,
            content_hash=content_hash,
            pages_accessed=pages_accessed,
        )

        # Build receipt metadata
        receipt_metadata = ReceiptMetadata(
            user_agent=f"{self.client_name}/{self.client_version}",
            sdk_version="1.0.0",
            **(metadata or {}),
        )

        # Build payload (without signature)
        payload_dict = {
            "version": "1.0",
            "receipt_id": receipt_id,
            "publisher_id": document.publisher_id,
            "publisher_domain": document.domain,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "client_version": self.client_version,
            "timestamp": timestamp.isoformat(),
            "access": access.model_dump(mode='json', exclude_none=True),
            "purpose": purpose.model_dump(mode='json', exclude_none=True) if purpose else None,
            "attribution": attribution.model_dump(mode='json', exclude_none=True) if attribution else None,
            "metadata": receipt_metadata.model_dump(mode='json', exclude_none=True),
        }

        # Sign the payload
        signature = self._sign_payload(payload_dict)

        # Create complete receipt
        receipt = Receipt(
            version="1.0",
            receipt_id=receipt_id,
            publisher_id=document.publisher_id,
            publisher_domain=document.domain,
            client_id=self.client_id,
            client_name=self.client_name,
            client_version=self.client_version,
            timestamp=timestamp,
            access=access,
            purpose=purpose,
            attribution=attribution,
            signature=signature,
            metadata=receipt_metadata,
        )

        return receipt

    def _sign_payload(self, payload: Dict[str, Any]) -> Signature:
        """
        Sign a receipt payload.

        Args:
            payload: Payload dictionary to sign

        Returns:
            Signature object
        """
        # Serialize payload
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        payload_bytes = payload_json.encode('utf-8')

        # Compute hash
        payload_hash = self._compute_hash(payload_json)

        # Sign based on algorithm
        if self.algorithm == SignatureAlgorithm.ES256:
            signature_bytes = self.private_key.sign(
                payload_bytes,
                ec.ECDSA(hashes.SHA256())
            )
        elif self.algorithm == SignatureAlgorithm.RS256:
            signature_bytes = self.private_key.sign(
                payload_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

        # Encode signature
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

        return Signature(
            algorithm=self.algorithm,
            kid=self.key_id,
            signature=signature_b64,
            document_hash=payload_hash,
            signed_at=datetime.utcnow(),
        )

    def post_receipt(
        self,
        receipt: Receipt,
        webhook_url: str,
        intent: Optional[str] = None
    ) -> bool:
        """
        Post receipt to publisher's webhook.

        Args:
            receipt: Signed receipt
            webhook_url: Publisher's webhook URL
            intent: Optional intent override

        Returns:
            True if successfully posted
        """
        last_error = None

        for attempt in range(self.webhook_retries):
            try:
                headers = {
                    "X-AIIndex-Version": "v1.1",
                    "X-AIIndex-Client-ID": self.client_id,
                    "X-AIIndex-Intent": intent or self.intent,
                }

                response = self.session.post(
                    webhook_url,
                    json=receipt.model_dump(mode='json'),
                    timeout=self.webhook_timeout,
                    headers=headers,
                )

                if 200 <= response.status_code < 300:
                    return True

                raise Exception(f"Webhook returned status {response.status_code}")

            except Exception as e:
                last_error = e
                print(f"Failed to post receipt (attempt {attempt + 1}/{self.webhook_retries}): {e}")

                if attempt < self.webhook_retries - 1:
                    # Exponential backoff
                    time.sleep(2 ** attempt)

        print(f"All webhook retry attempts failed: {last_error}")
        return False

    def create_and_post_receipt(
        self,
        document: AIIndexDocument,
        url: str,
        status_code: int = 200,
        pages_accessed: Optional[List[str]] = None,
        purpose: Optional[Purpose] = None,
        attribution: Optional[Attribution] = None,
        metadata: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> Tuple[Receipt, bool]:
        """
        Create receipt and automatically post to webhook if specified.

        Args:
            document: AIIndex document
            url: URL of ai-index.json
            status_code: HTTP status code
            pages_accessed: List of accessed pages
            purpose: Access purpose
            attribution: Attribution details
            metadata: Additional metadata
            webhook_url: Optional webhook URL override
            intent: Optional intent override

        Returns:
            Tuple of (receipt, posted_successfully)
        """
        receipt = self.create_receipt(
            document=document,
            url=url,
            status_code=status_code,
            pages_accessed=pages_accessed,
            purpose=purpose,
            attribution=attribution,
            metadata=metadata,
        )

        posted = False
        final_webhook_url = webhook_url
        if not final_webhook_url and document.access_policy:
            final_webhook_url = str(document.access_policy.webhook_url) if document.access_policy.webhook_url else None

        if final_webhook_url:
            posted = self.post_receipt(receipt, final_webhook_url, intent)

        return receipt, posted

    def create_and_post_receipts_batch(
        self,
        items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Batch create and post receipts.

        Args:
            items: List of dictionaries with 'document' and other receipt parameters

        Returns:
            List of results with 'receipt', 'posted', and optional 'error'
        """
        results = []

        for item in items:
            try:
                document = item['document']
                receipt, posted = self.create_and_post_receipt(
                    document=document,
                    url=item.get('url', ''),
                    status_code=item.get('status_code', 200),
                    pages_accessed=item.get('pages_accessed'),
                    purpose=item.get('purpose'),
                    attribution=item.get('attribution'),
                    metadata=item.get('metadata'),
                )
                results.append({
                    "receipt": receipt,
                    "posted": posted,
                })
            except Exception as e:
                results.append({
                    "receipt": None,
                    "posted": False,
                    "error": str(e),
                })

        return results

    @staticmethod
    def generate_keypair(algorithm: str = "ES256") -> Tuple[bytes, bytes]:
        """
        Generate a new keypair for signing.

        Args:
            algorithm: Signature algorithm ("ES256" or "RS256")

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        backend = default_backend()

        if algorithm == "ES256":
            private_key = ec.generate_private_key(ec.SECP256R1(), backend)
        elif algorithm == "RS256":
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=backend
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem

    @staticmethod
    def verify_receipt(receipt: Receipt, public_key_pem: bytes) -> bool:
        """
        Verify a receipt signature.

        Args:
            receipt: Receipt to verify
            public_key_pem: Public key in PEM format

        Returns:
            True if signature is valid
        """
        try:
            backend = default_backend()

            # Load public key
            public_key = serialization.load_pem_public_key(public_key_pem, backend)

            # Reconstruct payload (without signature)
            receipt_dict = receipt.model_dump(mode='json')
            receipt_dict.pop('signature')

            payload_json = json.dumps(receipt_dict, sort_keys=True, separators=(',', ':'))
            payload_bytes = payload_json.encode('utf-8')

            # Verify hash
            computed_hash = hashlib.sha256(payload_bytes).hexdigest()
            if computed_hash != receipt.signature.document_hash:
                return False

            # Decode signature
            signature_bytes = base64.b64decode(receipt.signature.signature)

            # Verify based on algorithm
            if receipt.signature.algorithm == SignatureAlgorithm.ES256:
                public_key.verify(
                    signature_bytes,
                    payload_bytes,
                    ec.ECDSA(hashes.SHA256())
                )
            elif receipt.signature.algorithm == SignatureAlgorithm.RS256:
                public_key.verify(
                    signature_bytes,
                    payload_bytes,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
            else:
                return False

            return True

        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Verification error: {e}")
            return False

    def _compute_hash(self, data: str) -> str:
        """Compute SHA-256 hash of data."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "AIIndexReceiptSigner":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
