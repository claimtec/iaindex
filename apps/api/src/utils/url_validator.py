"""
URL Validation Utilities
Prevents SSRF (Server-Side Request Forgery) attacks by validating URLs
"""
from urllib.parse import urlparse
import ipaddress
import socket
from typing import Optional, List
import logging
import re

logger = logging.getLogger(__name__)


class SSRFProtectionError(Exception):
    """Exception raised when URL fails SSRF protection checks"""
    pass


class URLValidator:
    """
    URL Validator with SSRF protection

    Validates URLs to prevent Server-Side Request Forgery attacks by blocking:
    - Private IP addresses (localhost, 127.0.0.1, 192.168.x.x, 10.x.x.x, etc.)
    - Internal network addresses
    - Cloud metadata endpoints (AWS, GCP, Azure)
    - Non-HTTP/HTTPS protocols
    - Invalid URL formats
    """

    # Private IP ranges (IPv4)
    PRIVATE_IP_RANGES = [
        ipaddress.ip_network("0.0.0.0/8"),          # Current network
        ipaddress.ip_network("10.0.0.0/8"),         # Private network
        ipaddress.ip_network("127.0.0.0/8"),        # Loopback
        ipaddress.ip_network("169.254.0.0/16"),     # Link-local
        ipaddress.ip_network("172.16.0.0/12"),      # Private network
        ipaddress.ip_network("192.168.0.0/16"),     # Private network
        ipaddress.ip_network("224.0.0.0/4"),        # Multicast
        ipaddress.ip_network("240.0.0.0/4"),        # Reserved
    ]

    # Private IP ranges (IPv6)
    PRIVATE_IPV6_RANGES = [
        ipaddress.ip_network("::1/128"),            # Loopback
        ipaddress.ip_network("fc00::/7"),           # Unique local
        ipaddress.ip_network("fe80::/10"),          # Link-local
    ]

    # Blocked domains (cloud metadata endpoints)
    BLOCKED_DOMAINS = [
        "169.254.169.254",      # AWS/Azure metadata
        "metadata.google.internal",  # GCP metadata
        "metadata",
        "localhost",
        "0.0.0.0",
    ]

    # Allowed schemes
    ALLOWED_SCHEMES = ["http", "https"]

    @classmethod
    def validate_url(
        cls,
        url: str,
        allow_private: bool = False,
        allowed_schemes: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None
    ) -> str:
        """
        Validate URL and check for SSRF vulnerabilities

        Args:
            url: URL to validate
            allow_private: Allow private IP addresses (default: False)
            allowed_schemes: List of allowed URL schemes (default: http, https)
            blocked_domains: Additional domains to block

        Returns:
            Validated URL string

        Raises:
            SSRFProtectionError: If URL fails validation
        """
        if not url or not isinstance(url, str):
            raise SSRFProtectionError("Invalid URL: URL must be a non-empty string")

        # Parse URL
        try:
            parsed = urlparse(url.strip())
        except Exception as e:
            raise SSRFProtectionError(f"Invalid URL format: {e}")

        # Check scheme
        schemes = allowed_schemes or cls.ALLOWED_SCHEMES
        if parsed.scheme not in schemes:
            raise SSRFProtectionError(
                f"Invalid URL scheme: {parsed.scheme}. Allowed schemes: {', '.join(schemes)}"
            )

        # Check hostname exists
        if not parsed.hostname:
            raise SSRFProtectionError("Invalid URL: No hostname found")

        # Combine default and custom blocked domains
        all_blocked_domains = cls.BLOCKED_DOMAINS.copy()
        if blocked_domains:
            all_blocked_domains.extend(blocked_domains)

        # Check against blocked domains
        hostname_lower = parsed.hostname.lower()
        for blocked in all_blocked_domains:
            if hostname_lower == blocked.lower() or hostname_lower.endswith(f".{blocked.lower()}"):
                raise SSRFProtectionError(f"Blocked domain: {parsed.hostname}")

        # Check for IP address in hostname
        if cls._is_ip_address(parsed.hostname):
            ip_addr = ipaddress.ip_address(parsed.hostname)

            # Check if private IP
            if not allow_private and cls._is_private_ip(ip_addr):
                raise SSRFProtectionError(
                    f"Private IP addresses are not allowed: {parsed.hostname}"
                )

        # Resolve hostname to IP and check for private IPs
        elif not allow_private:
            try:
                # Resolve hostname to IP address
                ip_addresses = cls._resolve_hostname(parsed.hostname)

                # Check if any resolved IP is private
                for ip_str in ip_addresses:
                    try:
                        ip_addr = ipaddress.ip_address(ip_str)
                        if cls._is_private_ip(ip_addr):
                            raise SSRFProtectionError(
                                f"Hostname resolves to private IP: {parsed.hostname} -> {ip_str}"
                            )
                    except ValueError:
                        continue

            except socket.gaierror:
                # DNS resolution failed - allow it but log warning
                logger.warning(f"Could not resolve hostname for SSRF check: {parsed.hostname}")
            except Exception as e:
                logger.error(f"Error resolving hostname for SSRF check: {e}")

        # Check URL length (prevent DOS)
        if len(url) > 2048:
            raise SSRFProtectionError("URL too long (max 2048 characters)")

        # Check for suspicious patterns
        if cls._has_suspicious_patterns(url):
            raise SSRFProtectionError("URL contains suspicious patterns")

        return url

    @classmethod
    def _is_ip_address(cls, hostname: str) -> bool:
        """Check if hostname is an IP address"""
        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            return False

    @classmethod
    def _is_private_ip(cls, ip_addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
        """Check if IP address is private"""
        if isinstance(ip_addr, ipaddress.IPv4Address):
            return any(ip_addr in network for network in cls.PRIVATE_IP_RANGES)
        elif isinstance(ip_addr, ipaddress.IPv6Address):
            return any(ip_addr in network for network in cls.PRIVATE_IPV6_RANGES)
        return False

    @classmethod
    def _resolve_hostname(cls, hostname: str) -> List[str]:
        """Resolve hostname to IP addresses"""
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            # Extract unique IP addresses
            ips = set()
            for info in addr_info:
                ip = info[4][0]
                ips.add(ip)
            return list(ips)
        except Exception as e:
            logger.error(f"Failed to resolve hostname {hostname}: {e}")
            return []

    @classmethod
    def _has_suspicious_patterns(cls, url: str) -> bool:
        """Check for suspicious patterns in URL"""
        suspicious_patterns = [
            r"@",  # User info in URL (e.g., http://user@internal.com)
            r"localhost",
            r"127\.0\.0\.1",
            r"0\.0\.0\.0",
            r"\[::\]",  # IPv6 localhost
            r"0x[0-9a-fA-F]+",  # Hex encoded IPs
        ]

        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, url_lower):
                logger.warning(f"Suspicious pattern detected in URL: {pattern}")
                return True

        return False

    @classmethod
    def validate_and_normalize_url(cls, url: str, **kwargs) -> str:
        """
        Validate URL and normalize it

        Args:
            url: URL to validate and normalize
            **kwargs: Additional arguments for validate_url

        Returns:
            Normalized URL string
        """
        validated_url = cls.validate_url(url, **kwargs)

        # Parse and normalize
        parsed = urlparse(validated_url)

        # Normalize scheme to lowercase
        scheme = parsed.scheme.lower()

        # Normalize hostname to lowercase
        hostname = parsed.hostname.lower() if parsed.hostname else ""

        # Normalize port
        port = f":{parsed.port}" if parsed.port else ""

        # Reconstruct URL
        normalized = f"{scheme}://{hostname}{port}{parsed.path}"

        if parsed.query:
            normalized += f"?{parsed.query}"

        if parsed.fragment:
            normalized += f"#{parsed.fragment}"

        return normalized


# Convenience function
def validate_url(url: str, allow_private: bool = False) -> str:
    """
    Validate URL for SSRF protection

    Args:
        url: URL to validate
        allow_private: Allow private IP addresses (default: False)

    Returns:
        Validated URL string

    Raises:
        SSRFProtectionError: If URL fails validation

    Example:
        try:
            safe_url = validate_url("https://example.com")
            # Use safe_url for HTTP request
        except SSRFProtectionError as e:
            # Handle invalid URL
            logger.error(f"Invalid URL: {e}")
    """
    return URLValidator.validate_url(url, allow_private=allow_private)
