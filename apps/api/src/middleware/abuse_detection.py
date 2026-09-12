"""
Abuse Detection Middleware
Detects and blocks malicious patterns and IP-based abuse
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from typing import Callable, Dict, Set, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class AbuseDetectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to detect and block abusive behavior

    Features:
    - IP-based blocking
    - Suspicious pattern detection
    - Automated blocking after threshold violations
    - Temporary and permanent bans
    """

    def __init__(
        self,
        app,
        max_violations: int = 10,
        violation_window_minutes: int = 60,
        block_duration_minutes: int = 60,
        permanent_block_threshold: int = 50,
        whitelist_ips: Optional[Set[str]] = None,
        blacklist_ips: Optional[Set[str]] = None
    ):
        """
        Initialize abuse detection middleware

        Args:
            app: FastAPI application
            max_violations: Maximum violations before temporary block
            violation_window_minutes: Time window for counting violations
            block_duration_minutes: Duration of temporary block
            permanent_block_threshold: Violations before permanent block
            whitelist_ips: Set of whitelisted IP addresses
            blacklist_ips: Set of blacklisted IP addresses
        """
        super().__init__(app)
        self.max_violations = max_violations
        self.violation_window = timedelta(minutes=violation_window_minutes)
        self.block_duration = timedelta(minutes=block_duration_minutes)
        self.permanent_block_threshold = permanent_block_threshold

        # IP tracking
        self.whitelist_ips = whitelist_ips or set()
        self.blacklist_ips = blacklist_ips or set()
        self.blocked_ips: Dict[str, datetime] = {}  # IP -> block_until
        self.permanently_blocked_ips: Set[str] = set()
        self.violation_counts: Dict[str, list] = defaultdict(list)  # IP -> [timestamps]

        # Suspicious patterns
        self.suspicious_patterns = [
            r"<script",  # XSS attempts
            r"javascript:",  # XSS attempts
            r"eval\(",  # Code injection
            r"union.*select",  # SQL injection
            r"drop.*table",  # SQL injection
            r"insert.*into",  # SQL injection
            r"exec\(",  # Command injection
            r"\.\.\/",  # Path traversal
            r"%00",  # Null byte injection
            r"0x[0-9a-f]+",  # Hex encoding (potential obfuscation)
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and check for abuse"""

        # Extract client IP
        client_ip = self._get_client_ip(request)

        # Check whitelist first
        if client_ip in self.whitelist_ips:
            return await call_next(request)

        # Check blacklist
        if client_ip in self.blacklist_ips or client_ip in self.permanently_blocked_ips:
            logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
            return self._create_block_response(
                client_ip,
                "IP address is permanently blocked",
                permanent=True
            )

        # Check temporary blocks
        if client_ip in self.blocked_ips:
            block_until = self.blocked_ips[client_ip]
            if datetime.utcnow() < block_until:
                logger.warning(f"Blocked request from temporarily blocked IP: {client_ip}")
                return self._create_block_response(
                    client_ip,
                    "IP address is temporarily blocked due to suspicious activity",
                    block_until=block_until
                )
            else:
                # Block expired, remove it
                del self.blocked_ips[client_ip]

        # Check for suspicious patterns in request
        if self._has_suspicious_patterns(request):
            self._record_violation(client_ip, "suspicious_pattern")
            logger.warning(
                f"Suspicious pattern detected - IP: {client_ip}, "
                f"Path: {request.url.path}, Method: {request.method}"
            )

            # Check if should block
            if self._should_block_ip(client_ip):
                return self._create_block_response(
                    client_ip,
                    "Too many suspicious requests detected"
                )

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Invalid request",
                    "message": "Request contains suspicious patterns"
                }
            )

        # Process request
        try:
            response = await call_next(request)

            # Check response status for potential abuse indicators
            if response.status_code == 401:
                self._record_violation(client_ip, "auth_failure", weight=0.5)
            elif response.status_code == 403:
                self._record_violation(client_ip, "forbidden", weight=0.3)
            elif response.status_code == 429:
                self._record_violation(client_ip, "rate_limit", weight=1.0)

            # Check if should block based on accumulated violations
            if self._should_block_ip(client_ip):
                self._block_ip(client_ip)

            return response

        except Exception as e:
            logger.error(f"Error processing request from {client_ip}: {e}")
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check X-Forwarded-For header (for proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (client IP)
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to client host
        if request.client:
            return request.client.host

        return "unknown"

    def _has_suspicious_patterns(self, request: Request) -> bool:
        """Check if request contains suspicious patterns"""
        # Check URL path
        path = request.url.path.lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                logger.debug(f"Suspicious pattern in path: {pattern}")
                return True

        # Check query parameters
        query_string = str(request.url.query).lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                logger.debug(f"Suspicious pattern in query: {pattern}")
                return True

        # Check headers for suspicious user agents
        user_agent = request.headers.get("User-Agent", "").lower()
        suspicious_agents = [
            "sqlmap",  # SQL injection tool
            "nikto",   # Vulnerability scanner
            "nmap",    # Network scanner
            "masscan", # Port scanner
            "nessus",  # Vulnerability scanner
            "curl",    # Often used in automated attacks (too broad for production)
            "wget",    # Often used in automated attacks (too broad for production)
        ]

        for agent in suspicious_agents:
            if agent in user_agent:
                logger.debug(f"Suspicious user agent: {user_agent}")
                return True

        return False

    def _record_violation(self, ip: str, violation_type: str, weight: float = 1.0) -> None:
        """Record a violation for an IP address"""
        now = datetime.utcnow()

        # Add violation with timestamp and weight
        self.violation_counts[ip].append({
            "timestamp": now,
            "type": violation_type,
            "weight": weight
        })

        # Clean old violations outside the window
        cutoff = now - self.violation_window
        self.violation_counts[ip] = [
            v for v in self.violation_counts[ip]
            if v["timestamp"] > cutoff
        ]

        logger.info(
            f"Violation recorded - IP: {ip}, Type: {violation_type}, "
            f"Total violations: {len(self.violation_counts[ip])}"
        )

    def _should_block_ip(self, ip: str) -> bool:
        """Check if IP should be blocked based on violations"""
        if ip not in self.violation_counts:
            return False

        # Calculate weighted violation score
        now = datetime.utcnow()
        cutoff = now - self.violation_window

        weighted_score = sum(
            v["weight"] for v in self.violation_counts[ip]
            if v["timestamp"] > cutoff
        )

        # Check for permanent block
        total_violations = sum(v["weight"] for v in self.violation_counts[ip])
        if total_violations >= self.permanent_block_threshold:
            logger.warning(
                f"IP exceeds permanent block threshold - IP: {ip}, "
                f"Violations: {total_violations}"
            )
            self.permanently_blocked_ips.add(ip)
            return True

        # Check for temporary block
        if weighted_score >= self.max_violations:
            logger.warning(
                f"IP exceeds temporary block threshold - IP: {ip}, "
                f"Score: {weighted_score}"
            )
            return True

        return False

    def _block_ip(self, ip: str) -> None:
        """Block an IP address temporarily"""
        block_until = datetime.utcnow() + self.block_duration
        self.blocked_ips[ip] = block_until

        logger.warning(
            f"IP blocked - IP: {ip}, Block until: {block_until.isoformat()}"
        )

    def _create_block_response(
        self,
        ip: str,
        message: str,
        permanent: bool = False,
        block_until: Optional[datetime] = None
    ) -> JSONResponse:
        """Create a block response"""
        content = {
            "error": "Access Denied",
            "message": message,
            "ip": ip,
            "permanent": permanent
        }

        if block_until:
            content["blocked_until"] = block_until.isoformat()
            content["retry_after"] = int((block_until - datetime.utcnow()).total_seconds())

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=content
        )

    def get_blocked_ips(self) -> Dict[str, any]:
        """Get list of currently blocked IPs"""
        now = datetime.utcnow()

        return {
            "temporary_blocks": {
                ip: block_until.isoformat()
                for ip, block_until in self.blocked_ips.items()
                if block_until > now
            },
            "permanent_blocks": list(self.permanently_blocked_ips),
            "blacklist": list(self.blacklist_ips)
        }

    def unblock_ip(self, ip: str) -> bool:
        """Manually unblock an IP address"""
        removed = False

        if ip in self.blocked_ips:
            del self.blocked_ips[ip]
            removed = True

        if ip in self.permanently_blocked_ips:
            self.permanently_blocked_ips.remove(ip)
            removed = True

        if ip in self.violation_counts:
            del self.violation_counts[ip]

        if removed:
            logger.info(f"IP manually unblocked: {ip}")

        return removed


def create_abuse_detection_middleware(
    max_violations: int = 10,
    whitelist_ips: Optional[Set[str]] = None,
    blacklist_ips: Optional[Set[str]] = None
):
    """
    Factory function to create abuse detection middleware

    Args:
        max_violations: Maximum violations before temporary block
        whitelist_ips: Set of whitelisted IP addresses
        blacklist_ips: Set of blacklisted IP addresses

    Returns:
        AbuseDetectionMiddleware class

    Example:
        app.add_middleware(
            AbuseDetectionMiddleware,
            max_violations=10,
            whitelist_ips={"192.168.1.1", "10.0.0.1"},
            blacklist_ips={"1.2.3.4"}
        )
    """
    return AbuseDetectionMiddleware
