"""
Receipt management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from supabase import Client
from datetime import datetime
import logging
from typing import Dict, Any

from ..models.receipt import (
    ReceiptIngestRequest,
    ReceiptIngestResponse,
    ReceiptStatus,
    ReceiptListResponse,
    ReceiptResponse,
    ReceiptQueryParams
)
from ..services.signature import SignatureVerificationService
from ..services.merkle import MerkleTreeService
from ..middleware.auth import get_api_key
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/receipts", tags=["receipts"])
limiter = Limiter(key_func=get_remote_address)


# Dependency for Supabase client
async def get_supabase_client() -> Client:
    """Get Supabase client"""
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_key)


@router.post(
    "/ingest",
    response_model=ReceiptIngestResponse,
    status_code=status.HTTP_201_CREATED
)
@limiter.limit(settings.rate_limit_per_minute)
async def ingest_receipt(
    request: Request,
    receipt: ReceiptIngestRequest,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
) -> ReceiptIngestResponse:
    """
    Verify and store a receipt

    This endpoint accepts a receipt from a publisher, verifies its signature,
    and stores it in the database. The receipt is then included in the daily
    Merkle tree attestation.
    """
    try:
        # Check if receipt already exists
        existing = supabase.table("receipts").select("receipt_id").eq(
            "receipt_id", receipt.receipt_id
        ).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Receipt already exists"
            )

        # Verify publisher is verified
        publisher = supabase.table("publishers").select("*").eq(
            "domain", receipt.publisher_domain
        ).eq("domain_verified", True).execute()

        if not publisher.data:
            logger.warning(f"Unverified publisher: {receipt.publisher_domain}")
            return ReceiptIngestResponse(
                receipt_id=receipt.receipt_id,
                status=ReceiptStatus.REJECTED,
                verified=False,
                message="Publisher not verified",
                timestamp=datetime.utcnow()
            )

        publisher_data = publisher.data[0]

        # Verify signature
        is_valid = SignatureVerificationService.verify_receipt_signature(
            receipt.receipt_id,
            receipt.publisher_domain,
            str(receipt.article_url),
            receipt.timestamp.isoformat(),
            receipt.signature,
            publisher_data.get("verification_key", settings.secret_key),
            method=publisher_data.get("signature_method", "hmac")
        )

        receipt_status = ReceiptStatus.VERIFIED if is_valid else ReceiptStatus.FAILED

        # Generate receipt hash for Merkle tree
        receipt_hash = SignatureVerificationService.generate_receipt_hash(
            receipt.receipt_id,
            receipt.publisher_domain,
            str(receipt.article_url),
            receipt.timestamp.isoformat()
        )

        # Store receipt
        receipt_data = {
            "receipt_id": receipt.receipt_id,
            "publisher_domain": receipt.publisher_domain,
            "article_url": str(receipt.article_url),
            "timestamp": receipt.timestamp.isoformat(),
            "signature": receipt.signature,
            "status": receipt_status.value,
            "verified": is_valid,
            "receipt_hash": receipt_hash,
            "metadata": receipt.metadata,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        result = supabase.table("receipts").insert(receipt_data).execute()

        # Get or create daily Merkle root
        date_key = MerkleTreeService.format_date_key(receipt.timestamp)
        merkle_root = None

        # Note: Merkle root is typically computed in a batch job
        # For now, we'll return None and compute it later

        logger.info(f"Receipt ingested: {receipt.receipt_id} - Status: {receipt_status}")

        return ReceiptIngestResponse(
            receipt_id=receipt.receipt_id,
            status=receipt_status,
            verified=is_valid,
            message="Receipt verified and stored" if is_valid else "Signature verification failed",
            merkle_root=merkle_root,
            timestamp=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Receipt ingestion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process receipt: {str(e)}"
        )


@router.get("", response_model=ReceiptListResponse)
@limiter.limit(settings.rate_limit_per_minute)
async def list_receipts(
    request: Request,
    publisher_domain: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    status_filter: ReceiptStatus = None,
    limit: int = 100,
    offset: int = 0,
    api_key: str = Depends(get_api_key),
    supabase: Client = Depends(get_supabase_client)
) -> ReceiptListResponse:
    """
    List receipts with optional filters

    Retrieve receipts with pagination and filtering by publisher domain,
    date range, and verification status.
    """
    try:
        # Build query
        query = supabase.table("receipts").select("*", count="exact")

        if publisher_domain:
            query = query.eq("publisher_domain", publisher_domain)

        if start_date:
            query = query.gte("timestamp", start_date.isoformat())

        if end_date:
            query = query.lte("timestamp", end_date.isoformat())

        if status_filter:
            query = query.eq("status", status_filter.value)

        # Apply pagination
        query = query.range(offset, offset + limit - 1).order("timestamp", desc=True)

        result = query.execute()

        # Convert to response models
        receipts = [
            ReceiptResponse(
                receipt_id=r["receipt_id"],
                publisher_domain=r["publisher_domain"],
                article_url=r["article_url"],
                timestamp=datetime.fromisoformat(r["timestamp"]),
                status=ReceiptStatus(r["status"]),
                verified=r["verified"],
                signature=r["signature"],
                merkle_root=r.get("merkle_root"),
                metadata=r.get("metadata"),
                created_at=datetime.fromisoformat(r["created_at"]),
                updated_at=datetime.fromisoformat(r["updated_at"])
            )
            for r in result.data
        ]

        return ReceiptListResponse(
            receipts=receipts,
            total=result.count or 0,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Receipt listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve receipts: {str(e)}"
        )
