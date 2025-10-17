"""
Attestation and Merkle tree routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from supabase import Client
from datetime import datetime
import datetime as dt
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..services.merkle import MerkleTreeService
from ..middleware.auth import optional_auth
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/attestations", tags=["attestations"])
limiter = Limiter(key_func=get_remote_address)


# Dependency for Supabase client
async def get_supabase_client() -> Client:
    """Get Supabase client"""
    from supabase import create_client
    return create_client(settings.supabase_url, settings.supabase_key)


class AttestationResponse(BaseModel):
    """Response model for attestation"""
    date: str
    merkle_root: str
    receipt_count: int
    verified_count: int
    created_at: datetime
    tree_height: int


@router.get("/{date_str}", response_model=Dict[str, Any])
@limiter.limit(settings.rate_limit_per_hour)
async def get_attestation(
    request: Request,
    date_str: str,
    user: str = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get Merkle root attestation for a specific date

    Returns the Merkle root hash for all receipts on the specified date,
    along with statistics and verification information. This provides
    cryptographic proof of all receipts processed on that day.
    """
    try:
        # Parse and validate date
        try:
            date_obj = datetime.fromisoformat(date_str).date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

        date_key = date_obj.isoformat()

        # Check if attestation already exists
        existing = supabase.table("merkle_roots").select("*").eq(
            "date", date_key
        ).execute()

        if existing.data:
            attestation = existing.data[0]
            return {
                "date": attestation["date"],
                "merkle_root": attestation["merkle_root"],
                "receipt_count": attestation["receipt_count"],
                "verified_count": attestation["verified_count"],
                "created_at": attestation["created_at"],
                "tree_height": attestation.get("tree_height", 0),
                "cached": True
            }

        # Get all receipts for this date
        start_datetime = datetime.combine(date_obj, datetime.min.time())
        end_datetime = datetime.combine(date_obj, datetime.max.time())

        receipts_query = supabase.table("receipts").select("*").gte(
            "timestamp", start_datetime.isoformat()
        ).lte(
            "timestamp", end_datetime.isoformat()
        ).execute()

        receipts = receipts_query.data

        if not receipts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No receipts found for date {date_key}"
            )

        # Extract receipt hashes
        receipt_hashes = [r["receipt_hash"] for r in receipts if r.get("receipt_hash")]

        if not receipt_hashes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No receipt hashes available"
            )

        # Build Merkle tree
        merkle_root, tree_levels = MerkleTreeService.build_merkle_tree(receipt_hashes)
        tree_height = len(tree_levels)

        # Calculate statistics
        receipt_count = len(receipts)
        verified_count = sum(1 for r in receipts if r.get("verified", False))

        # Store attestation
        attestation_data = {
            "date": date_key,
            "merkle_root": merkle_root,
            "receipt_count": receipt_count,
            "verified_count": verified_count,
            "tree_height": tree_height,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        supabase.table("merkle_roots").insert(attestation_data).execute()

        # Update receipts with merkle root
        for receipt in receipts:
            supabase.table("receipts").update({
                "merkle_root": merkle_root,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("receipt_id", receipt["receipt_id"]).execute()

        logger.info(f"Attestation created for {date_key}: {merkle_root}")

        return {
            "date": date_key,
            "merkle_root": merkle_root,
            "receipt_count": receipt_count,
            "verified_count": verified_count,
            "created_at": datetime.utcnow().isoformat(),
            "tree_height": tree_height,
            "cached": False
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Attestation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve attestation: {str(e)}"
        )


@router.get("/{date_str}/receipts/{receipt_id}/proof")
@limiter.limit(settings.rate_limit_per_minute)
async def get_merkle_proof(
    request: Request,
    date_str: str,
    receipt_id: str,
    user: str = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get Merkle proof for a specific receipt

    Returns the Merkle proof path that can be used to verify a receipt's
    inclusion in the daily attestation without revealing other receipts.
    """
    try:
        # Parse date
        try:
            date_obj = datetime.fromisoformat(date_str).date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

        date_key = date_obj.isoformat()

        # Get receipt
        receipt_query = supabase.table("receipts").select("*").eq(
            "receipt_id", receipt_id
        ).execute()

        if not receipt_query.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )

        receipt = receipt_query.data[0]
        receipt_hash = receipt.get("receipt_hash")

        if not receipt_hash:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Receipt hash not available"
            )

        # Get all receipts for the date to rebuild tree
        start_datetime = datetime.combine(date_obj, datetime.min.time())
        end_datetime = datetime.combine(date_obj, datetime.max.time())

        receipts_query = supabase.table("receipts").select("*").gte(
            "timestamp", start_datetime.isoformat()
        ).lte(
            "timestamp", end_datetime.isoformat()
        ).order("timestamp", desc=False).execute()

        receipts = receipts_query.data
        receipt_hashes = [r["receipt_hash"] for r in receipts if r.get("receipt_hash")]

        # Rebuild Merkle tree
        merkle_root, tree_levels = MerkleTreeService.build_merkle_tree(receipt_hashes)

        # Generate proof
        proof = MerkleTreeService.get_merkle_proof(receipt_hash, tree_levels)

        if proof is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found in Merkle tree for this date"
            )

        # Verify proof
        is_valid = MerkleTreeService.verify_merkle_proof(
            receipt_hash, merkle_root, proof
        )

        return {
            "receipt_id": receipt_id,
            "date": date_key,
            "receipt_hash": receipt_hash,
            "merkle_root": merkle_root,
            "proof": [{"hash": h, "position": p} for h, p in proof],
            "verified": is_valid
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Merkle proof error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Merkle proof: {str(e)}"
        )


@router.get("")
@limiter.limit(settings.rate_limit_per_minute)
async def list_attestations(
    request: Request,
    limit: int = 30,
    offset: int = 0,
    user: str = Depends(optional_auth),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    List all attestations

    Returns a paginated list of all daily attestations with their Merkle roots
    and statistics.
    """
    try:
        query = supabase.table("merkle_roots").select(
            "*", count="exact"
        ).order("date", desc=True).range(offset, offset + limit - 1)

        result = query.execute()

        return {
            "attestations": result.data,
            "total": result.count or 0,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Attestation listing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list attestations: {str(e)}"
        )
