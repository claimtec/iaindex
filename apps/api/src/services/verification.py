"""
Domain verification service
"""
import dns.resolver
import secrets
import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta
from ..config import settings

logger = logging.getLogger(__name__)


class DomainVerificationService:
    """Service for verifying publisher domains"""

    @staticmethod
    def generate_verification_token() -> str:
        """
        Generate a secure verification token

        Returns:
            Random verification token
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_verification_expiry() -> datetime:
        """
        Get expiry datetime for verification token

        Returns:
            Datetime when token expires
        """
        return datetime.utcnow() + timedelta(
            hours=settings.verification_token_expiry_hours
        )

    @staticmethod
    def format_dns_txt_record(token: str) -> str:
        """
        Format DNS TXT record for verification

        Args:
            token: Verification token

        Returns:
            Formatted TXT record value
        """
        return f"{settings.dns_verification_prefix}={token}"

    @staticmethod
    def verify_dns_txt_record(domain: str, token: str) -> Tuple[bool, str]:
        """
        Verify DNS TXT record contains verification token

        Args:
            domain: Domain to verify
            token: Expected verification token

        Returns:
            Tuple of (verified, message)
        """
        try:
            # Query TXT records
            answers = dns.resolver.resolve(domain, 'TXT')

            expected_record = DomainVerificationService.format_dns_txt_record(token)

            for rdata in answers:
                # TXT records are quoted, so we need to join and clean
                txt_value = ''.join([s.decode() if isinstance(s, bytes) else s for s in rdata.strings])

                if txt_value == expected_record:
                    return True, "Domain verified successfully"

            return False, f"Verification record not found. Expected: {expected_record}"

        except dns.resolver.NXDOMAIN:
            return False, f"Domain {domain} does not exist"
        except dns.resolver.NoAnswer:
            return False, f"No TXT records found for {domain}"
        except dns.resolver.Timeout:
            return False, "DNS query timed out"
        except Exception as e:
            logger.error(f"DNS verification error for {domain}: {e}")
            return False, f"Verification error: {str(e)}"

    @staticmethod
    def get_verification_instructions(method: str, token: str, domain: str) -> str:
        """
        Get verification instructions for a given method

        Args:
            method: Verification method
            token: Verification token
            domain: Domain to verify

        Returns:
            Human-readable instructions
        """
        if method == "dns_txt":
            txt_record = DomainVerificationService.format_dns_txt_record(token)
            return (
                f"Add the following TXT record to your DNS settings for {domain}:\n\n"
                f"Type: TXT\n"
                f"Name: @ (or {domain})\n"
                f"Value: {txt_record}\n\n"
                f"Note: DNS propagation may take up to 48 hours. "
                f"You can check verification status using the provided token."
            )
        elif method == "html_meta":
            return (
                f"Add the following meta tag to your website's <head> section:\n\n"
                f'<meta name="iaindex-verification" content="{token}" />\n\n'
                f"This should be added to your homepage at https://{domain}/"
            )
        elif method == "file_upload":
            return (
                f"Create a file at the following URL:\n\n"
                f"https://{domain}/.well-known/iaindex-verification.txt\n\n"
                f"The file should contain only: {token}\n\n"
                f"Ensure the file is publicly accessible."
            )
        else:
            return "Unknown verification method"
