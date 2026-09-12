"""
CSRF Protection Middleware
Protects against Cross-Site Request Forgery attacks for state-changing operations
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, List, Optional
import secrets
import hmac
import hashlib
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware using Double Submit Cookie pattern

    Protects state-changing operations (POST, PUT, PATCH, DELETE) by requiring
    a valid CSRF token in the request header that matches a secure cookie.
    """

    def __init__(
        self,
        app,
        secret_key: str,
        token_name: str = "X-CSRF-Token",
        cookie_name: str = "csrf_token",
        cookie_path: str = "/",
        cookie_domain: Optional[str] = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: str = "strict",
        exempt_paths: Optional[List[str]] = None,
        exempt_methods: Optional[List[str]] = None
    ):
        """
        Initialize CSRF protection middleware

        Args:
            app: FastAPI application
            secret_key: Secret key for HMAC signing
            token_name: HTTP header name for CSRF token
            cookie_name: Cookie name for CSRF token
            cookie_path: Cookie path
            cookie_domain: Cookie domain
            cookie_secure: Use secure cookie (HTTPS only)
            cookie_httponly: HttpOnly cookie flag
            cookie_samesite: SameSite cookie attribute
            exempt_paths: List of paths exempt from CSRF protection
            exempt_methods: List of HTTP methods exempt from CSRF protection
        """
        super().__init__(app)
        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key
        self.token_name = token_name
        self.cookie_name = cookie_name
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite

        # Default exempt paths (health checks, docs, etc.)
        self.exempt_paths = exempt_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/v1/auth/login"
        ]

        # Default exempt methods (safe methods + OPTIONS)
        self.exempt_methods = exempt_methods or ["GET", "HEAD", "OPTIONS", "TRACE"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and validate CSRF token for state-changing operations"""

        # Skip CSRF check for exempt paths
        if self._is_exempt_path(request.url.path):
            response = await call_next(request)
            return response

        # Skip CSRF check for exempt methods (safe methods)
        if request.method in self.exempt_methods:
            response = await call_next(request)
            # Set CSRF cookie for GET requests (to be used in subsequent POST/PUT/etc)
            self._set_csrf_cookie(response)
            return response

        # Validate CSRF token for state-changing operations
        if not self._validate_csrf_token(request):
            logger.warning(
                f"CSRF validation failed - Method: {request.method}, "
                f"Path: {request.url.path}, "
                f"Client: {request.client.host if request.client else 'unknown'}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token validation failed. Include valid X-CSRF-Token header."
            )

        # Process request
        response = await call_next(request)

        # Refresh CSRF cookie
        self._set_csrf_cookie(response)

        return response

    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection"""
        return any(path.startswith(exempt_path) for exempt_path in self.exempt_paths)

    def _generate_csrf_token(self) -> str:
        """Generate a new CSRF token"""
        # Generate random token
        random_token = secrets.token_urlsafe(32)

        # Create HMAC signature
        signature = hmac.new(
            self.secret_key,
            random_token.encode(),
            hashlib.sha256
        ).hexdigest()

        # Combine token and signature
        return f"{random_token}.{signature}"

    def _validate_csrf_token(self, request: Request) -> bool:
        """
        Validate CSRF token using Double Submit Cookie pattern

        Compares the token in the request header with the token in the cookie
        """
        # Get token from header
        header_token = request.headers.get(self.token_name)
        if not header_token:
            logger.debug("CSRF token not found in request header")
            return False

        # Get token from cookie
        cookie_token = request.cookies.get(self.cookie_name)
        if not cookie_token:
            logger.debug("CSRF token not found in cookie")
            return False

        # Validate token format
        if "." not in header_token or "." not in cookie_token:
            logger.debug("Invalid CSRF token format")
            return False

        # Verify tokens match
        if not secrets.compare_digest(header_token, cookie_token):
            logger.debug("CSRF tokens do not match")
            return False

        # Verify HMAC signature
        try:
            random_token, signature = header_token.rsplit(".", 1)
            expected_signature = hmac.new(
                self.secret_key,
                random_token.encode(),
                hashlib.sha256
            ).hexdigest()

            if not secrets.compare_digest(signature, expected_signature):
                logger.debug("Invalid CSRF token signature")
                return False

        except Exception as e:
            logger.error(f"CSRF token validation error: {e}")
            return False

        return True

    def _set_csrf_cookie(self, response: Response) -> None:
        """Set CSRF token cookie in response"""
        # Generate new token
        token = self._generate_csrf_token()

        # Set cookie
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
            max_age=3600  # 1 hour
        )

        # Also set token in response header for easy access
        response.headers[self.token_name] = token


class CSRFProtectionConfig:
    """Configuration for CSRF protection"""

    def __init__(
        self,
        secret_key: str,
        enabled: bool = True,
        exempt_paths: Optional[List[str]] = None,
        cookie_secure: bool = True
    ):
        self.secret_key = secret_key
        self.enabled = enabled
        self.exempt_paths = exempt_paths or []
        self.cookie_secure = cookie_secure


def create_csrf_middleware(
    secret_key: str,
    cookie_secure: bool = True,
    exempt_paths: Optional[List[str]] = None
):
    """
    Factory function to create CSRF protection middleware

    Args:
        secret_key: Secret key for HMAC signing
        cookie_secure: Use secure cookie (HTTPS only)
        exempt_paths: List of paths exempt from CSRF protection

    Returns:
        CSRFProtectionMiddleware class

    Example:
        app.add_middleware(
            CSRFProtectionMiddleware,
            secret_key=settings.secret_key,
            cookie_secure=not settings.debug,
            exempt_paths=["/health", "/docs", "/public"]
        )
    """
    return CSRFProtectionMiddleware
