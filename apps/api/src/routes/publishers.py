"""
Publisher verification routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from supabase import Client
from datetime import datetime, timedelta
import logging
from typing import List

from ..models.publisher import (
    PublisherVerifyRequest,
    PublisherVerifyResponse,
    VerificationCheckResponse,
    VerificationStatus,
    VerificationMethod,
    VerifiedPublisher,
    VerifiedDomainListResponse
)
from ..services.verification import DomainVerificationService
from ..middleware.auth import get_api_key, optional_auth
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/publishers", tags=["publishers"])
limiter = Limiter(key_func=get_remote_address)


# Dependency for Supabase client
async def get_supabase_client() -> Client:
    """Get Supabase client"""
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_key)


@router.post("/verify", response_model=PublisherVerifyResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def initiate_verification(
    request: Request,
    verify_request: PublisherVerifyRequest,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
) -> PublisherVerifyResponse:
    """
    Initiate domain verification process

    Creates a verification token and provides instructions for the publisher
    to verify ownership of their domain via DNS TXT record, HTML meta tag,
    or file upload.
    """
    try:
        domain = verify_request.domain

        # Check if domain is already verified
        existing = supabase.table("publishers").select("*").eq(
            "domain", domain
        ).execute()

        if existing.data and existing.data[0].get("domain_verified"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Domain is already verified"
            )

        # Generate verification token
        token = DomainVerificationService.generate_verification_token()
        expires_at = DomainVerificationService.get_verification_expiry()

        # Get instructions
        instructions = DomainVerificationService.get_verification_instructions(
            verify_request.method.value,
            token,
            domain
        )

        # Store or update verification record
        verification_data = {
            "domain": domain,
            "verification_token": token,
            "verification_method": verify_request.method.value,
            "domain_verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        if existing.data:
            # Update existing record
            supabase.table("publishers").update(verification_data).eq(
                "domain", domain
            ).execute()
        else:
            # Create new record
            supabase.table("publishers").insert(verification_data).execute()

        logger.info(f"Verification initiated for domain: {domain}")

        return PublisherVerifyResponse(
            domain=domain,
            verification_token=token,
            verification_method=verify_request.method,
            instructions=instructions,
            expires_at=expires_at,
            status=VerificationStatus.PENDING
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification initiation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate verification: {str(e)}"
        )


@router.get("/verify/{token}", response_model=VerificationCheckResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def check_verification(
    request: Request,
    token: str,
    supabase: Client = Depends(get_supabase_client)
) -> VerificationCheckResponse:
    """
    Check verification status for a token

    Attempts to verify the domain by checking for the verification token
    in DNS records, HTML meta tags, or uploaded files based on the chosen
    verification method.
    """
    try:
        # Find verification record
        publisher = supabase.table("publishers").select("*").eq(
            "verification_token", token
        ).execute()

        if not publisher.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verification token not found"
            )

        publisher_data = publisher.data[0]
        domain = publisher_data["domain"]

        # Check if already verified
        if publisher_data.get("domain_verified"):
            return VerificationCheckResponse(
                domain=domain,
                status=VerificationStatus.VERIFIED,
                verified=True,
                verified_at=datetime.fromisoformat(publisher_data["updated_at"]),
                message="Domain is already verified"
            )

        # Check if expired (calculate from created_at + expiry hours)
        created_at = datetime.fromisoformat(publisher_data["created_at"])
        expiry_hours = settings.verification_token_expiry_hours
        expires_at = created_at.replace(tzinfo=None) + timedelta(hours=expiry_hours)

        if datetime.utcnow() > expires_at:
            supabase.table("publishers").update({
                "updated_at": datetime.utcnow().isoformat()
            }).eq("domain", domain).execute()

            return VerificationCheckResponse(
                domain=domain,
                status=VerificationStatus.EXPIRED,
                verified=False,
                message="Verification token has expired"
            )

        # Perform verification based on method
        method = publisher_data["verification_method"]

        if method == VerificationMethod.DNS_TXT.value:
            verified, message = DomainVerificationService.verify_dns_txt_record(
                domain, token
            )
        else:
            # TODO: Implement HTML meta and file upload verification
            verified = False
            message = f"Verification method {method} not yet implemented"

        # Update status
        if verified:
            supabase.table("publishers").update({
                "domain_verified": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("domain", domain).execute()

            logger.info(f"Domain verified successfully: {domain}")

            return VerificationCheckResponse(
                domain=domain,
                status=VerificationStatus.VERIFIED,
                verified=True,
                verified_at=datetime.utcnow(),
                message=message
            )
        else:
            supabase.table("publishers").update({
                "updated_at": datetime.utcnow().isoformat()
            }).eq("domain", domain).execute()

            return VerificationCheckResponse(
                domain=domain,
                status=VerificationStatus.PENDING,
                verified=False,
                message=message
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check verification: {str(e)}"
        )


@router.get("/verified-domains", response_model=VerifiedDomainListResponse)
@limiter.limit(settings.rate_limit_per_hour)
async def get_verified_domains(
    request: Request,
    user: str = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> VerifiedDomainListResponse:
    """
    Get list of verified publisher domains (public endpoint)

    Returns a list of all verified publishers with their verification date
    and receipt statistics. This endpoint is publicly accessible.
    """
    try:
        # Get all verified publishers
        publishers_query = supabase.table("publishers").select("*").eq(
            "domain_verified", True
        ).order("updated_at", desc=True).execute()

        verified_publishers = []

        for publisher in publishers_query.data:
            domain = publisher["domain"]

            # Get receipt count for this publisher
            receipts_query = supabase.table("receipts").select(
                "*", count="exact"
            ).eq("publisher_domain", domain).execute()

            receipt_count = receipts_query.count or 0

            # Get last receipt timestamp
            last_receipt = None
            if receipts_query.data:
                timestamps = [datetime.fromisoformat(r["timestamp"]) for r in receipts_query.data]
                last_receipt = max(timestamps)

            verified_publishers.append(
                VerifiedPublisher(
                    domain=domain,
                    verified_at=datetime.fromisoformat(publisher["updated_at"]),
                    receipt_count=receipt_count,
                    last_receipt_at=last_receipt
                )
            )

        return VerifiedDomainListResponse(
            domains=verified_publishers,
            total=len(verified_publishers),
            updated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Verified domains listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve verified domains: {str(e)}"
        )
