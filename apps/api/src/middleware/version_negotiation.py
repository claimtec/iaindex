"""
Protocol Version Negotiation

Handles AIIndex protocol version negotiation.
Parses version headers, validates supported versions,
and returns appropriate schema and features.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import logging
from packaging import version

logger = logging.getLogger(__name__)


class ProtocolVersion(str, Enum):
    """Supported AIIndex protocol versions"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V1_2 = "1.2"


class VersionFeatures(BaseModel):
    """Features available in a protocol version"""
    version: str
    features: List[str] = Field(default_factory=list)
    receipt_schema_version: str
    policy_schema_version: str
    signature_algorithms: List[str] = Field(default_factory=list)
    deprecated: bool = False
    sunset_date: Optional[str] = None
    upgrade_url: Optional[str] = None


class VersionNegotiator:
    """Protocol version negotiation handler"""

    # Supported versions and their features
    SUPPORTED_VERSIONS = {
        ProtocolVersion.V1_0: VersionFeatures(
            version="1.0",
            features=[
                "basic_receipts",
                "domain_verification",
                "rsa_signatures"
            ],
            receipt_schema_version="1.0",
            policy_schema_version="1.0",
            signature_algorithms=["RSA-SHA256"],
            deprecated=True,
            sunset_date="2025-12-31",
            upgrade_url="https://docs.iaindex.com/migration/v1.0-to-v1.1"
        ),
        ProtocolVersion.V1_1: VersionFeatures(
            version="1.1",
            features=[
                "basic_receipts",
                "domain_verification",
                "rsa_signatures",
                "ed25519_signatures",
                "policy_enforcement",
                "denial_receipts",
                "rate_limiting",
                "intent_headers"
            ],
            receipt_schema_version="1.1",
            policy_schema_version="1.1",
            signature_algorithms=["RSA-SHA256", "Ed25519"],
            deprecated=False
        ),
        ProtocolVersion.V1_2: VersionFeatures(
            version="1.2",
            features=[
                "basic_receipts",
                "domain_verification",
                "rsa_signatures",
                "ed25519_signatures",
                "policy_enforcement",
                "denial_receipts",
                "rate_limiting",
                "intent_headers",
                "fraud_detection",
                "bot_reputation",
                "batch_verification",
                "webhook_notifications"
            ],
            receipt_schema_version="1.2",
            policy_schema_version="1.2",
            signature_algorithms=["RSA-SHA256", "Ed25519", "ECDSA-P256"],
            deprecated=False
        )
    }

    # Default version if not specified
    DEFAULT_VERSION = ProtocolVersion.V1_1

    # Minimum supported version
    MINIMUM_VERSION = ProtocolVersion.V1_0

    def __init__(self):
        """Initialize version negotiator"""
        self._version_cache: Dict[str, ProtocolVersion] = {}

    def parse_version_header(self, request: Request) -> Optional[ProtocolVersion]:
        """
        Parse version from request header

        Args:
            request: FastAPI request

        Returns:
            ProtocolVersion enum or None
        """
        version_header = request.headers.get("X-AIIndex-Version", "").strip()

        if not version_header:
            logger.debug("No version header provided, using default")
            return self.DEFAULT_VERSION

        # Normalize version (e.g., "v1.1" -> "1.1")
        if version_header.lower().startswith("v"):
            version_header = version_header[1:]

        # Try to match to supported version
        for protocol_version in ProtocolVersion:
            if protocol_version.value == version_header:
                logger.debug(f"Parsed version: {version_header}")
                return protocol_version

        logger.warning(f"Unsupported version requested: {version_header}")
        return None

    def is_version_supported(self, protocol_version: ProtocolVersion) -> bool:
        """
        Check if version is supported

        Args:
            protocol_version: Protocol version to check

        Returns:
            True if supported
        """
        return protocol_version in self.SUPPORTED_VERSIONS

    def get_version_features(self, protocol_version: ProtocolVersion) -> VersionFeatures:
        """
        Get features for a protocol version

        Args:
            protocol_version: Protocol version

        Returns:
            VersionFeatures object
        """
        return self.SUPPORTED_VERSIONS.get(protocol_version)

    def compare_versions(self, version_a: str, version_b: str) -> int:
        """
        Compare two version strings

        Args:
            version_a: First version
            version_b: Second version

        Returns:
            -1 if a < b, 0 if a == b, 1 if a > b
        """
        try:
            v_a = version.parse(version_a)
            v_b = version.parse(version_b)

            if v_a < v_b:
                return -1
            elif v_a > v_b:
                return 1
            else:
                return 0
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            return 0

    def select_best_version(
        self,
        requested_version: Optional[ProtocolVersion],
        minimum_version: Optional[ProtocolVersion] = None
    ) -> ProtocolVersion:
        """
        Select best version based on request and constraints

        Args:
            requested_version: Version requested by client
            minimum_version: Minimum acceptable version

        Returns:
            Best matching protocol version
        """
        # Use default if no version requested
        if not requested_version:
            return self.DEFAULT_VERSION

        # Check if requested version is supported
        if not self.is_version_supported(requested_version):
            # Return highest supported version
            supported_versions = list(self.SUPPORTED_VERSIONS.keys())
            return sorted(
                supported_versions,
                key=lambda v: version.parse(v.value),
                reverse=True
            )[0]

        # Check minimum version constraint
        if minimum_version:
            if self.compare_versions(
                requested_version.value,
                minimum_version.value
            ) < 0:
                return minimum_version

        return requested_version

    def create_version_response(
        self,
        protocol_version: ProtocolVersion
    ) -> Dict[str, Any]:
        """
        Create version information response

        Args:
            protocol_version: Protocol version

        Returns:
            Dictionary with version information
        """
        features = self.get_version_features(protocol_version)

        response = {
            "version": features.version,
            "features": features.features,
            "schema": {
                "receipt": features.receipt_schema_version,
                "policy": features.policy_schema_version
            },
            "signature_algorithms": features.signature_algorithms,
            "deprecated": features.deprecated
        }

        if features.deprecated:
            response["sunset_date"] = features.sunset_date
            response["upgrade_url"] = features.upgrade_url
            response["warning"] = (
                f"Version {features.version} is deprecated and will be "
                f"sunset on {features.sunset_date}. Please upgrade."
            )

        return response

    def create_unsupported_response(
        self,
        requested_version: str
    ) -> Dict[str, Any]:
        """
        Create response for unsupported version

        Args:
            requested_version: Version that was requested

        Returns:
            Error response dictionary
        """
        supported_versions = [v.value for v in self.SUPPORTED_VERSIONS.keys()]

        return {
            "error": "Unsupported Protocol Version",
            "message": f"Protocol version '{requested_version}' is not supported",
            "requested_version": requested_version,
            "supported_versions": supported_versions,
            "default_version": self.DEFAULT_VERSION.value,
            "recommendation": (
                f"Please use version {self.DEFAULT_VERSION.value} or upgrade "
                "to the latest supported version"
            )
        }

    def add_version_headers(
        self,
        response,
        protocol_version: ProtocolVersion
    ):
        """
        Add version-related headers to response

        Args:
            response: FastAPI response
            protocol_version: Protocol version being used
        """
        features = self.get_version_features(protocol_version)

        response.headers["X-AIIndex-Version"] = features.version
        response.headers["X-AIIndex-Schema-Version"] = features.receipt_schema_version

        if features.deprecated:
            response.headers["Deprecation"] = "true"
            if features.sunset_date:
                response.headers["Sunset"] = features.sunset_date
            if features.upgrade_url:
                response.headers["Link"] = f'<{features.upgrade_url}>; rel="upgrade"'


# Global version negotiator instance
version_negotiator = VersionNegotiator()


async def version_negotiation_middleware(request: Request, call_next):
    """
    FastAPI middleware for version negotiation

    Parses version header, validates, and adds version info to response
    """
    # Skip version negotiation for certain endpoints
    skip_paths = ["/health", "/docs", "/redoc", "/openapi.json", "/"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        return await call_next(request)

    # Parse requested version
    requested_version = version_negotiator.parse_version_header(request)

    # Check if version is supported
    if requested_version and not version_negotiator.is_version_supported(requested_version):
        logger.warning(f"Unsupported version requested: {requested_version}")

        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=version_negotiator.create_unsupported_response(requested_version.value)
        )

    # Select best version
    selected_version = version_negotiator.select_best_version(requested_version)

    # Store version in request state for use by endpoints
    request.state.protocol_version = selected_version

    # Log version selection
    logger.debug(
        f"Version negotiation - Requested: {requested_version}, "
        f"Selected: {selected_version}"
    )

    # Process request
    response = await call_next(request)

    # Add version headers to response
    version_negotiator.add_version_headers(response, selected_version)

    return response


def get_request_version(request: Request) -> ProtocolVersion:
    """
    Get protocol version from request state

    Args:
        request: FastAPI request

    Returns:
        Protocol version for this request
    """
    return getattr(request.state, "protocol_version", version_negotiator.DEFAULT_VERSION)


def requires_version(min_version: ProtocolVersion):
    """
    Decorator to require minimum protocol version for endpoint

    Args:
        min_version: Minimum required version

    Example:
        @app.get("/v1/advanced")
        @requires_version(ProtocolVersion.V1_1)
        async def advanced_endpoint():
            ...
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            current_version = get_request_version(request)

            if version_negotiator.compare_versions(
                current_version.value,
                min_version.value
            ) < 0:
                return JSONResponse(
                    status_code=status.HTTP_426_UPGRADE_REQUIRED,
                    content={
                        "error": "Protocol Upgrade Required",
                        "message": f"This endpoint requires protocol version {min_version.value} or higher",
                        "current_version": current_version.value,
                        "required_version": min_version.value
                    }
                )

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator
