"""
Custom exception classes for standardized error handling
"""
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class APIException(HTTPException):
    """Base API exception with enhanced error tracking"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        request_id: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self._generate_error_code()
        self.request_id = request_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()

    def _generate_error_code(self) -> str:
        """Generate error code based on status"""
        return f"ERR_{self.status_code}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dict for JSON response"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.detail,
                "status_code": self.status_code,
                "request_id": self.request_id,
                "timestamp": self.timestamp
            }
        }


class AuthenticationError(APIException):
    """Authentication failed"""
    def __init__(self, detail: str = "Authentication failed", **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_FAILED",
            headers={"WWW-Authenticate": "Bearer"},
            **kwargs
        )


class AuthorizationError(APIException):
    """Authorization failed - insufficient permissions"""
    def __init__(self, detail: str = "Insufficient permissions", **kwargs):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTH_FORBIDDEN",
            **kwargs
        )


class ResourceNotFoundError(APIException):
    """Resource not found"""
    def __init__(self, resource: str = "Resource", **kwargs):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
            error_code="NOT_FOUND",
            **kwargs
        )


class ValidationError(APIException):
    """Validation error"""
    def __init__(self, detail: str, **kwargs):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            **kwargs
        )


class RateLimitError(APIException):
    """Rate limit exceeded"""
    def __init__(
        self,
        detail: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        headers = {"Retry-After": str(retry_after)} if retry_after else None
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            headers=headers,
            **kwargs
        )


class PlanLimitError(APIException):
    """Plan limit exceeded"""
    def __init__(self, detail: str = "Plan limit exceeded. Please upgrade.", **kwargs):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
            error_code="PLAN_LIMIT_EXCEEDED",
            **kwargs
        )


class ConflictError(APIException):
    """Resource conflict (e.g., duplicate)"""
    def __init__(self, detail: str, **kwargs):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT",
            **kwargs
        )


class ServiceUnavailableError(APIException):
    """Service temporarily unavailable"""
    def __init__(
        self,
        detail: str = "Service temporarily unavailable",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        headers = {"Retry-After": str(retry_after)} if retry_after else None
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="SERVICE_UNAVAILABLE",
            headers=headers,
            **kwargs
        )


class ExternalAPIError(APIException):
    """External API call failed"""
    def __init__(self, service: str, detail: Optional[str] = None, **kwargs):
        message = detail or f"Failed to communicate with {service}"
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=message,
            error_code="EXTERNAL_API_ERROR",
            **kwargs
        )


class DatabaseError(APIException):
    """Database operation failed"""
    def __init__(self, detail: str = "Database operation failed", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
            **kwargs
        )


class InvalidTokenError(AuthenticationError):
    """Invalid or expired token"""
    def __init__(self, detail: str = "Invalid or expired token", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "INVALID_TOKEN"


class EmailAlreadyExistsError(ConflictError):
    """Email already registered"""
    def __init__(self, **kwargs):
        super().__init__(
            detail="An account with this email already exists",
            **kwargs
        )
        self.error_code = "EMAIL_EXISTS"


class WeakPasswordError(ValidationError):
    """Password doesn't meet security requirements"""
    def __init__(self, detail: str = "Password doesn't meet security requirements", **kwargs):
        super().__init__(detail=detail, **kwargs)
        self.error_code = "WEAK_PASSWORD"


class InvalidCredentialsError(AuthenticationError):
    """Invalid email or password"""
    def __init__(self, **kwargs):
        super().__init__(
            detail="Invalid email or password",
            **kwargs
        )
        self.error_code = "INVALID_CREDENTIALS"


class EmailNotVerifiedError(AuthenticationError):
    """Email not verified"""
    def __init__(self, **kwargs):
        super().__init__(
            detail="Please verify your email address before logging in",
            **kwargs
        )
        self.error_code = "EMAIL_NOT_VERIFIED"


class SubscriptionRequiredError(PlanLimitError):
    """Active subscription required"""
    def __init__(self, **kwargs):
        super().__init__(
            detail="An active subscription is required to access this feature",
            **kwargs
        )
        self.error_code = "SUBSCRIPTION_REQUIRED"


class WebsiteLimitError(PlanLimitError):
    """Website limit reached"""
    def __init__(self, limit: int, **kwargs):
        super().__init__(
            detail=f"Website limit reached ({limit}). Please upgrade your plan.",
            **kwargs
        )
        self.error_code = "WEBSITE_LIMIT_REACHED"
