"""
Security Headers Middleware
Implements comprehensive security headers to protect against common web vulnerabilities
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses

    Implements:
    - Content Security Policy (CSP)
    - X-Frame-Options (Clickjacking protection)
    - X-Content-Type-Options (MIME sniffing protection)
    - Strict-Transport-Security (HSTS)
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """

    def __init__(self, app, enable_hsts: bool = True, hsts_max_age: int = 31536000):
        """
        Initialize security headers middleware

        Args:
            app: FastAPI application
            enable_hsts: Enable HSTS header (disable for local development)
            hsts_max_age: HSTS max-age in seconds (default: 1 year)
        """
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add security headers to response"""

        # Process the request
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response) -> None:
        """Add all security headers to response"""

        # Content Security Policy (CSP)
        # Restrictive policy - adjust based on your needs
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Adjust as needed
            "style-src 'self' 'unsafe-inline'",  # For inline styles
            "img-src 'self' data: https:",  # Allow images from HTTPS sources
            "font-src 'self' data:",
            "connect-src 'self' https://api.anthropic.com https://api.openai.com https://api.perplexity.ai",
            "frame-ancestors 'none'",  # Prevent embedding
            "base-uri 'self'",
            "form-action 'self'",
            "upgrade-insecure-requests"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # X-Frame-Options: Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options: Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Strict-Transport-Security (HSTS): Force HTTPS
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            )

        # X-XSS-Protection: Enable XSS filter (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: Control browser features
        permissions_policies = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()"
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_policies)

        # X-Permitted-Cross-Domain-Policies: Restrict cross-domain policies
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Cache-Control for sensitive endpoints
        if self._is_sensitive_endpoint(response):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"

        # Remove server information disclosure
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

    def _is_sensitive_endpoint(self, response: Response) -> bool:
        """Check if response is from a sensitive endpoint"""
        # Add logic to identify sensitive endpoints
        # For now, treat all authenticated endpoints as sensitive
        return True


def create_security_headers_middleware(enable_hsts: bool = True, hsts_max_age: int = 31536000):
    """
    Factory function to create security headers middleware

    Args:
        enable_hsts: Enable HSTS header (disable for local development)
        hsts_max_age: HSTS max-age in seconds (default: 1 year)

    Returns:
        SecurityHeadersMiddleware instance

    Example:
        app.add_middleware(
            SecurityHeadersMiddleware,
            enable_hsts=not settings.debug,  # Disable HSTS in development
            hsts_max_age=31536000  # 1 year
        )
    """
    return SecurityHeadersMiddleware
