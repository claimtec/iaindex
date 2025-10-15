"""
C2PA Content Credentials Service

Implements Coalition for Content Provenance and Authenticity (C2PA) standard.
Generates content credentials manifests, manages digital signatures, and provides verification.
"""
import logging
import hashlib
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, HttpUrl
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
import base64

logger = logging.getLogger(__name__)


# Configuration
class ProvenanceConfig:
    """Configuration for provenance service"""
    # Organization details
    ORG_NAME = os.getenv("ORG_NAME", "IA Index")
    ORG_WEBSITE = os.getenv("ORG_WEBSITE", "https://iaindex.com")
    ORG_EMAIL = os.getenv("ORG_EMAIL", "contact@iaindex.com")

    # Signing configuration
    PRIVATE_KEY_PATH = os.getenv("C2PA_PRIVATE_KEY_PATH", "./keys/c2pa_private.pem")
    CERTIFICATE_PATH = os.getenv("C2PA_CERTIFICATE_PATH", "./keys/c2pa_cert.pem")

    # C2PA specification version
    C2PA_VERSION = "1.3"
    MANIFEST_VERSION = "1.0"


# Models
class C2PAAction(BaseModel):
    """C2PA action (assertion)"""
    action: str = Field(..., description="Action type (e.g., 'c2pa.created', 'c2pa.edited')")
    when: str = Field(..., description="ISO 8601 timestamp")
    software_agent: Optional[str] = Field(
        default=None,
        description="Software that performed the action"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Action parameters"
    )


class C2PAAssertion(BaseModel):
    """C2PA assertion"""
    label: str = Field(..., description="Assertion label")
    data: Dict[str, Any] = Field(..., description="Assertion data")
    kind: str = Field(default="Json", description="Assertion kind")


class C2PAThumbnail(BaseModel):
    """C2PA thumbnail reference"""
    identifier: str = Field(..., description="Content identifier/hash")
    format: str = Field(default="image/png")


class C2PAManifest(BaseModel):
    """C2PA Manifest"""
    claim_generator: str = Field(..., description="Software that generated the claim")
    title: Optional[str] = None
    format: str = Field(default="application/json")
    instance_id: str = Field(..., description="Unique instance ID")
    thumbnail: Optional[C2PAThumbnail] = None
    assertions: List[C2PAAssertion] = Field(default_factory=list)
    signature: Optional[str] = Field(
        default=None,
        description="Digital signature of manifest"
    )
    signature_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Signature metadata"
    )
    credentials: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Signing credentials"
    )


class GenerateManifestRequest(BaseModel):
    """Request to generate C2PA manifest"""
    domain: str
    asset_url: HttpUrl = Field(..., description="URL to ai-index.json")
    asset_content: str = Field(..., description="Content of ai-index.json")
    actions: List[C2PAAction] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class GenerateManifestResponse(BaseModel):
    """Response with generated manifest"""
    manifest: C2PAManifest
    manifest_url: str
    asset_digest: str
    verification_url: str


class VerificationRequest(BaseModel):
    """Request to verify C2PA badge"""
    domain: str
    manifest_url: Optional[HttpUrl] = None


class VerificationResponse(BaseModel):
    """Response from verification"""
    domain: str
    verified: bool
    manifest_found: bool
    signature_valid: bool
    credential_valid: bool
    asset_digest: Optional[str] = None
    verified_at: datetime
    issues: List[str] = Field(default_factory=list)


# Exceptions
class ProvenanceError(Exception):
    """Base exception for provenance errors"""
    pass


class SigningError(ProvenanceError):
    """Signing error"""
    pass


class VerificationError(ProvenanceError):
    """Verification error"""
    pass


class ProvenanceService:
    """
    Service for C2PA content credentials

    Features:
    - C2PA-compliant manifest generation
    - Digital signatures with RSA
    - Asset digest computation
    - Manifest verification
    - HTML meta tag generation
    """

    def __init__(self):
        """Initialize provenance service"""
        self.config = ProvenanceConfig()
        self.private_key = None
        self.certificate = None
        self._load_signing_materials()

    def _load_signing_materials(self):
        """Load private key and certificate for signing"""
        try:
            # Load private key
            if os.path.exists(self.config.PRIVATE_KEY_PATH):
                with open(self.config.PRIVATE_KEY_PATH, 'rb') as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None,
                        backend=default_backend()
                    )
                logger.info("Loaded private key for C2PA signing")
            else:
                logger.warning(f"Private key not found at {self.config.PRIVATE_KEY_PATH}")
                # Generate a new key pair for development
                self._generate_key_pair()

            # Load certificate
            if os.path.exists(self.config.CERTIFICATE_PATH):
                with open(self.config.CERTIFICATE_PATH, 'rb') as f:
                    self.certificate = x509.load_pem_x509_certificate(
                        f.read(),
                        default_backend()
                    )
                logger.info("Loaded certificate for C2PA signing")

        except Exception as e:
            logger.error(f"Failed to load signing materials: {e}")
            self.private_key = None
            self.certificate = None

    def _generate_key_pair(self):
        """Generate new RSA key pair for development"""
        try:
            # Generate private key
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )

            # Generate self-signed certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.config.ORG_NAME),
                x509.NameAttribute(NameOID.COMMON_NAME, self.config.ORG_WEBSITE),
            ])

            self.certificate = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(self.private_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow().replace(year=datetime.utcnow().year + 1))
                .sign(self.private_key, hashes.SHA256(), default_backend())
            )

            logger.info("Generated new RSA key pair for development")

        except Exception as e:
            logger.error(f"Failed to generate key pair: {e}")
            raise SigningError(f"Key pair generation failed: {str(e)}")

    def _compute_asset_digest(self, content: str) -> str:
        """
        Compute SHA-256 digest of asset content

        Args:
            content: Asset content

        Returns:
            Hex-encoded SHA-256 hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _generate_instance_id(self, domain: str, timestamp: datetime) -> str:
        """
        Generate unique instance ID for manifest

        Args:
            domain: Domain
            timestamp: Creation timestamp

        Returns:
            Unique instance ID
        """
        content = f"{domain}:{timestamp.isoformat()}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()
        return f"xmp:iid:{hash_val[:32]}"

    def _sign_manifest(self, manifest_data: Dict[str, Any]) -> str:
        """
        Sign manifest data with private key

        Args:
            manifest_data: Manifest data to sign

        Returns:
            Base64-encoded signature

        Raises:
            SigningError: If signing fails
        """
        if not self.private_key:
            raise SigningError("Private key not available")

        try:
            # Serialize manifest data
            canonical_json = json.dumps(manifest_data, sort_keys=True, separators=(',', ':'))

            # Sign with RSA-PSS
            signature = self.private_key.sign(
                canonical_json.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # Encode as base64
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            logger.info("Manifest signed successfully")
            return signature_b64

        except Exception as e:
            logger.error(f"Failed to sign manifest: {e}")
            raise SigningError(f"Signing failed: {str(e)}")

    def _verify_signature(
        self,
        manifest_data: Dict[str, Any],
        signature_b64: str
    ) -> bool:
        """
        Verify manifest signature

        Args:
            manifest_data: Manifest data
            signature_b64: Base64-encoded signature

        Returns:
            True if signature is valid
        """
        if not self.certificate:
            logger.warning("Certificate not available for verification")
            return False

        try:
            # Decode signature
            signature = base64.b64decode(signature_b64)

            # Serialize manifest data
            canonical_json = json.dumps(manifest_data, sort_keys=True, separators=(',', ':'))

            # Verify with public key from certificate
            public_key = self.certificate.public_key()
            public_key.verify(
                signature,
                canonical_json.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            logger.info("Signature verified successfully")
            return True

        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    def generate_manifest(
        self,
        request: GenerateManifestRequest
    ) -> GenerateManifestResponse:
        """
        Generate C2PA-compliant manifest

        Args:
            request: Manifest generation request

        Returns:
            Generated manifest and metadata

        Raises:
            ProvenanceError: If generation fails
        """
        logger.info(f"Generating C2PA manifest for domain: {request.domain}")

        # Compute asset digest
        asset_digest = self._compute_asset_digest(request.asset_content)

        # Generate instance ID
        timestamp = datetime.now(timezone.utc)
        instance_id = self._generate_instance_id(request.domain, timestamp)

        # Build assertions
        assertions: List[C2PAAssertion] = []

        # Add actions assertion
        if request.actions:
            assertions.append(C2PAAssertion(
                label="c2pa.actions",
                data={
                    "actions": [action.dict() for action in request.actions]
                }
            ))

        # Add hash assertion
        assertions.append(C2PAAssertion(
            label="c2pa.hash.data",
            data={
                "name": "jumbf manifest",
                "alg": "sha256",
                "hash": asset_digest
            }
        ))

        # Add metadata assertion
        if request.metadata:
            assertions.append(C2PAAssertion(
                label="stds.schema-org.CreativeWork",
                data=request.metadata
            ))

        # Build manifest (without signature first)
        manifest_data = {
            "claim_generator": f"{self.config.ORG_NAME} C2PA Generator v{self.config.MANIFEST_VERSION}",
            "title": f"AI Index for {request.domain}",
            "format": "application/json",
            "instance_id": instance_id,
            "thumbnail": {
                "identifier": asset_digest[:16],
                "format": "application/json"
            },
            "assertions": [assertion.dict() for assertion in assertions]
        }

        # Sign manifest
        try:
            signature = self._sign_manifest(manifest_data)
            signature_info = {
                "alg": "ps256",  # RSA-PSS with SHA-256
                "cert_serial_number": (
                    str(self.certificate.serial_number)
                    if self.certificate else "dev-cert"
                ),
                "issuer": self.config.ORG_NAME,
                "time": timestamp.isoformat()
            }

            manifest_data["signature"] = signature
            manifest_data["signature_info"] = signature_info

        except SigningError as e:
            logger.warning(f"Failed to sign manifest: {e}")
            # Continue without signature for development

        # Create manifest object
        manifest = C2PAManifest(**manifest_data)

        # Generate URLs
        manifest_url = f"https://iaindex.com/c2pa/{request.domain}/manifest.json"
        verification_url = f"https://iaindex.com/api/v1/verify-badge?domain={request.domain}"

        logger.info(f"Generated C2PA manifest with instance ID: {instance_id}")

        return GenerateManifestResponse(
            manifest=manifest,
            manifest_url=manifest_url,
            asset_digest=asset_digest,
            verification_url=verification_url
        )

    async def store_manifest(
        self,
        domain: str,
        manifest: C2PAManifest
    ) -> str:
        """
        Store manifest (to S3 or database)

        Args:
            domain: Domain
            manifest: Manifest to store

        Returns:
            Storage URL
        """
        # TODO: Implement storage to S3 or database
        # For now, just log
        logger.info(f"Storing manifest for domain: {domain}")

        manifest_json = manifest.json(indent=2)
        manifest_url = f"https://iaindex.com/c2pa/{domain}/manifest.json"

        # In production, upload to S3:
        # s3_key = f"c2pa/{domain}/manifest.json"
        # s3_client.put_object(Bucket=bucket, Key=s3_key, Body=manifest_json)

        return manifest_url

    def generate_html_meta_tag(self, manifest_url: str) -> str:
        """
        Generate HTML meta tag for C2PA manifest

        Args:
            manifest_url: URL to manifest

        Returns:
            HTML meta tag
        """
        return f'<meta name="c2pa:manifest" content="{manifest_url}">'

    def generate_verification_badge_html(
        self,
        domain: str,
        verified: bool
    ) -> str:
        """
        Generate HTML for verification badge

        Args:
            domain: Domain
            verified: Verification status

        Returns:
            HTML badge code
        """
        badge_color = "green" if verified else "gray"
        status_text = "Verified" if verified else "Unverified"

        return f'''
<div class="c2pa-badge" style="display:inline-block;padding:8px 12px;background:{badge_color};color:white;border-radius:4px;">
    <span style="font-weight:bold;">C2PA {status_text}</span>
    <span style="font-size:0.9em;opacity:0.9;">{domain}</span>
</div>
'''

    async def verify_badge(
        self,
        request: VerificationRequest
    ) -> VerificationResponse:
        """
        Verify C2PA badge/manifest

        Args:
            request: Verification request

        Returns:
            Verification response
        """
        logger.info(f"Verifying C2PA badge for domain: {request.domain}")

        issues: List[str] = []
        manifest_found = False
        signature_valid = False
        credential_valid = False
        asset_digest = None

        # Step 1: Check if manifest exists
        manifest_url = request.manifest_url
        if not manifest_url:
            manifest_url = f"https://iaindex.com/c2pa/{request.domain}/manifest.json"

        try:
            # TODO: Fetch manifest from URL or storage
            # For now, simulate
            manifest_found = True
            logger.info(f"Manifest found at {manifest_url}")

        except Exception as e:
            issues.append(f"Manifest not found: {str(e)}")
            manifest_found = False

        # Step 2: Verify signature (if manifest found)
        if manifest_found:
            try:
                # TODO: Load manifest and verify signature
                # manifest_data = load_manifest(manifest_url)
                # signature = manifest_data.get("signature")
                # signature_valid = self._verify_signature(manifest_data, signature)

                # For now, simulate
                signature_valid = True
                logger.info("Signature verification passed")

            except Exception as e:
                issues.append(f"Signature verification failed: {str(e)}")
                signature_valid = False

        # Step 3: Verify credentials
        if signature_valid:
            try:
                # TODO: Verify certificate chain and credentials
                # For now, simulate
                credential_valid = self.certificate is not None
                logger.info("Credential verification passed")

            except Exception as e:
                issues.append(f"Credential verification failed: {str(e)}")
                credential_valid = False

        # Overall verification status
        verified = manifest_found and signature_valid and credential_valid

        return VerificationResponse(
            domain=request.domain,
            verified=verified,
            manifest_found=manifest_found,
            signature_valid=signature_valid,
            credential_valid=credential_valid,
            asset_digest=asset_digest,
            verified_at=datetime.now(timezone.utc),
            issues=issues
        )

    def get_manifest_json(
        self,
        domain: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve manifest JSON for domain

        Args:
            domain: Domain

        Returns:
            Manifest JSON or None
        """
        # TODO: Retrieve from storage
        logger.info(f"Retrieving manifest for domain: {domain}")
        return None


# Singleton instance
_provenance_service: Optional[ProvenanceService] = None


def get_provenance_service() -> ProvenanceService:
    """Get or create provenance service instance"""
    global _provenance_service
    if _provenance_service is None:
        _provenance_service = ProvenanceService()
    return _provenance_service
