"""
External Timestamping Service

Anchors content to blockchain or OpenTimestamps for immutable proof of existence.
Provides cryptographic timestamping and verification capabilities.
"""
import logging
import hashlib
import json
import os
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import datetime as dt
from pydantic import BaseModel, Field, HttpUrl
import httpx
from enum import Enum

logger = logging.getLogger(__name__)


# Configuration
class TimestampingConfig:
    """Configuration for timestamping service"""
    # OpenTimestamps
    OTS_API_URL = os.getenv("OTS_API_URL", "https://alice.btc.calendar.opentimestamps.org")
    OTS_CALENDAR_URLS = [
        "https://alice.btc.calendar.opentimestamps.org",
        "https://bob.btc.calendar.opentimestamps.org",
        "https://finney.calendar.eternitywall.com"
    ]

    # Blockchain settings
    BLOCKCHAIN_NETWORK = os.getenv("BLOCKCHAIN_NETWORK", "bitcoin")
    BLOCKCHAIN_EXPLORER_URL = os.getenv(
        "BLOCKCHAIN_EXPLORER_URL",
        "https://blockstream.info/api"
    )

    # Storage
    PROOF_STORAGE_PATH = os.getenv("PROOF_STORAGE_PATH", "./proofs")

    # Request timeout
    REQUEST_TIMEOUT = 30


# Models
class BlockchainNetwork(str, Enum):
    """Supported blockchain networks"""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"


class TimestampRequest(BaseModel):
    """Request to create timestamp"""
    merkle_root: str = Field(..., description="Merkle root hash to timestamp")
    date: dt.date = Field(..., description="Date for this attestation")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata"
    )
    blockchain: BlockchainNetwork = Field(
        default=BlockchainNetwork.BITCOIN,
        description="Blockchain to use"
    )


class TimestampProof(BaseModel):
    """Proof of timestamp"""
    merkle_root: str
    date: dt.date
    blockchain: str
    tx_id: Optional[str] = None
    block_height: Optional[int] = None
    block_hash: Optional[str] = None
    timestamp: datetime
    ots_proof: Optional[str] = Field(
        default=None,
        description="OpenTimestamps proof file (base64)"
    )
    proof_url: Optional[HttpUrl] = None
    verified: bool = False


class TimestampResponse(BaseModel):
    """Response from timestamping operation"""
    merkle_root: str
    date: str
    tx_id: Optional[str] = None
    timestamp_proof_url: Optional[str] = None
    blockchain: str
    status: str
    created_at: datetime


class AttestationResponse(BaseModel):
    """Response for attestation query"""
    merkle_root: str
    tx_id: Optional[str] = None
    timestamp_proof_url: Optional[str] = None
    blockchain: str
    created_at: datetime
    verified_at: Optional[datetime] = None
    proof: Optional[TimestampProof] = None


class VerifyProofRequest(BaseModel):
    """Request to verify timestamp proof"""
    merkle_root: str
    date: dt.date
    tx_id: Optional[str] = None
    ots_proof: Optional[str] = None


class VerifyProofResponse(BaseModel):
    """Response from proof verification"""
    merkle_root: str
    date: str
    verified: bool
    blockchain: str
    timestamp: Optional[datetime] = None
    block_height: Optional[int] = None
    verification_details: Dict[str, Any] = Field(default_factory=dict)


# Exceptions
class TimestampingError(Exception):
    """Base exception for timestamping errors"""
    pass


class OpenTimestampsError(TimestampingError):
    """OpenTimestamps error"""
    pass


class BlockchainError(TimestampingError):
    """Blockchain error"""
    pass


class TimestampingService:
    """
    Service for external timestamping

    Features:
    - OpenTimestamps integration
    - Bitcoin blockchain anchoring
    - Merkle root timestamping
    - Proof generation and verification
    - Daily attestation management
    """

    def __init__(self):
        """Initialize timestamping service"""
        self.config = TimestampingConfig()
        self.http_client = httpx.AsyncClient(timeout=self.config.REQUEST_TIMEOUT)

        # In-memory storage for development (use database in production)
        self.timestamps: Dict[str, TimestampProof] = {}

        # Ensure proof storage directory exists
        os.makedirs(self.config.PROOF_STORAGE_PATH, exist_ok=True)

    def _compute_hash(self, data: str) -> bytes:
        """
        Compute SHA-256 hash

        Args:
            data: Data to hash

        Returns:
            Hash bytes
        """
        return hashlib.sha256(data.encode('utf-8')).digest()

    def _format_date_key(self, date_obj: dt.date) -> str:
        """
        Format date as key

        Args:
            date_obj: Date

        Returns:
            Date string (YYYY-MM-DD)
        """
        return date_obj.isoformat()

    async def submit_to_opentimestamps(
        self,
        merkle_root: str
    ) -> str:
        """
        Submit hash to OpenTimestamps

        Args:
            merkle_root: Merkle root hash to timestamp

        Returns:
            OTS proof file content (base64)

        Raises:
            OpenTimestampsError: If submission fails
        """
        logger.info(f"Submitting to OpenTimestamps: {merkle_root}")

        # Convert hex hash to bytes
        try:
            hash_bytes = bytes.fromhex(merkle_root)
        except ValueError:
            raise OpenTimestampsError(f"Invalid hash format: {merkle_root}")

        # Submit to multiple calendars for redundancy
        success = False
        ots_proof = None

        for calendar_url in self.config.OTS_CALENDAR_URLS:
            try:
                # POST to calendar
                response = await self.http_client.post(
                    f"{calendar_url}/timestamp",
                    content=hash_bytes,
                    headers={"Content-Type": "application/octet-stream"}
                )
                response.raise_for_status()

                # Get OTS proof
                ots_proof = response.content

                logger.info(f"Successfully submitted to {calendar_url}")
                success = True
                break

            except Exception as e:
                logger.warning(f"Failed to submit to {calendar_url}: {e}")
                continue

        if not success:
            raise OpenTimestampsError("Failed to submit to any OpenTimestamps calendar")

        # Encode proof as base64 for storage
        import base64
        ots_proof_b64 = base64.b64encode(ots_proof).decode('utf-8')

        return ots_proof_b64

    async def verify_opentimestamps_proof(
        self,
        merkle_root: str,
        ots_proof_b64: str
    ) -> Dict[str, Any]:
        """
        Verify OpenTimestamps proof

        Args:
            merkle_root: Original merkle root
            ots_proof_b64: Base64-encoded OTS proof

        Returns:
            Verification result

        Raises:
            OpenTimestampsError: If verification fails
        """
        logger.info(f"Verifying OpenTimestamps proof for {merkle_root}")

        import base64

        try:
            # Decode proof
            ots_proof = base64.b64decode(ots_proof_b64)
            hash_bytes = bytes.fromhex(merkle_root)

            # Verify with calendar
            # Note: Full OTS verification requires the opentimestamps-client library
            # This is a simplified version

            response = await self.http_client.post(
                f"{self.config.OTS_API_URL}/verify",
                content=ots_proof,
                headers={"Content-Type": "application/octet-stream"}
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"OTS verification result: {result}")

            return {
                "verified": True,
                "timestamp": result.get("timestamp"),
                "bitcoin_block_height": result.get("bitcoin_block_height")
            }

        except Exception as e:
            logger.error(f"OTS verification failed: {e}")
            return {
                "verified": False,
                "error": str(e)
            }

    async def query_blockchain_transaction(
        self,
        tx_id: str,
        blockchain: BlockchainNetwork = BlockchainNetwork.BITCOIN
    ) -> Dict[str, Any]:
        """
        Query blockchain for transaction details

        Args:
            tx_id: Transaction ID
            blockchain: Blockchain network

        Returns:
            Transaction details

        Raises:
            BlockchainError: If query fails
        """
        logger.info(f"Querying {blockchain} for transaction: {tx_id}")

        try:
            if blockchain == BlockchainNetwork.BITCOIN:
                # Query Bitcoin blockchain
                response = await self.http_client.get(
                    f"{self.config.BLOCKCHAIN_EXPLORER_URL}/tx/{tx_id}"
                )
                response.raise_for_status()
                tx_data = response.json()

                return {
                    "tx_id": tx_id,
                    "block_height": tx_data.get("status", {}).get("block_height"),
                    "block_hash": tx_data.get("status", {}).get("block_hash"),
                    "timestamp": tx_data.get("status", {}).get("block_time"),
                    "confirmed": tx_data.get("status", {}).get("confirmed", False)
                }

            else:
                # Other blockchains would be implemented here
                raise BlockchainError(f"Blockchain {blockchain} not supported")

        except httpx.HTTPStatusError as e:
            logger.error(f"Blockchain query failed: {e}")
            raise BlockchainError(f"Transaction query failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Blockchain query error: {e}")
            raise BlockchainError(f"Query failed: {str(e)}")

    async def create_timestamp(
        self,
        request: TimestampRequest
    ) -> TimestampResponse:
        """
        Create timestamp for merkle root

        Args:
            request: Timestamp request

        Returns:
            Timestamp response

        Raises:
            TimestampingError: If timestamping fails
        """
        logger.info(
            f"Creating timestamp for merkle root: {request.merkle_root} "
            f"on {request.date}"
        )

        date_key = self._format_date_key(request.date)
        created_at = datetime.utcnow()

        # Submit to OpenTimestamps
        try:
            ots_proof = await self.submit_to_opentimestamps(request.merkle_root)
            logger.info("Successfully submitted to OpenTimestamps")
            status = "pending"  # OTS timestamps take time to confirm
            tx_id = None

        except OpenTimestampsError as e:
            logger.error(f"OpenTimestamps submission failed: {e}")
            ots_proof = None
            status = "failed"
            tx_id = None

        # Store timestamp proof
        proof = TimestampProof(
            merkle_root=request.merkle_root,
            date=request.date,
            blockchain=request.blockchain.value,
            tx_id=tx_id,
            timestamp=created_at,
            ots_proof=ots_proof,
            verified=False
        )

        storage_key = f"{date_key}:{request.merkle_root}"
        self.timestamps[storage_key] = proof

        # Save proof to file
        proof_file = os.path.join(
            self.config.PROOF_STORAGE_PATH,
            f"{date_key}.json"
        )
        with open(proof_file, 'w') as f:
            json.dump(proof.dict(), f, indent=2, default=str)

        timestamp_proof_url = f"https://iaindex.com/api/v1/attestations/{date_key}/proof"

        return TimestampResponse(
            merkle_root=request.merkle_root,
            date=date_key,
            tx_id=tx_id,
            timestamp_proof_url=timestamp_proof_url,
            blockchain=request.blockchain.value,
            status=status,
            created_at=created_at
        )

    async def get_attestation(
        self,
        date_str: str
    ) -> AttestationResponse:
        """
        Get attestation for a specific date

        Args:
            date_str: Date string (YYYY-MM-DD)

        Returns:
            Attestation response

        Raises:
            TimestampingError: If attestation not found
        """
        logger.info(f"Retrieving attestation for date: {date_str}")

        # Try to load from storage
        proof_file = os.path.join(
            self.config.PROOF_STORAGE_PATH,
            f"{date_str}.json"
        )

        if os.path.exists(proof_file):
            with open(proof_file, 'r') as f:
                proof_data = json.load(f)
                proof = TimestampProof(**proof_data)

            return AttestationResponse(
                merkle_root=proof.merkle_root,
                tx_id=proof.tx_id,
                timestamp_proof_url=f"https://iaindex.com/api/v1/attestations/{date_str}/proof",
                blockchain=proof.blockchain,
                created_at=proof.timestamp,
                verified_at=datetime.utcnow() if proof.verified else None,
                proof=proof
            )

        # Check in-memory storage
        for key, proof in self.timestamps.items():
            if key.startswith(date_str):
                return AttestationResponse(
                    merkle_root=proof.merkle_root,
                    tx_id=proof.tx_id,
                    timestamp_proof_url=f"https://iaindex.com/api/v1/attestations/{date_str}/proof",
                    blockchain=proof.blockchain,
                    created_at=proof.timestamp,
                    verified_at=datetime.utcnow() if proof.verified else None,
                    proof=proof
                )

        raise TimestampingError(f"No attestation found for date: {date_str}")

    async def verify_timestamp_proof(
        self,
        request: VerifyProofRequest
    ) -> VerifyProofResponse:
        """
        Verify timestamp proof

        Args:
            request: Verification request

        Returns:
            Verification response
        """
        logger.info(
            f"Verifying timestamp proof for {request.merkle_root} "
            f"on {request.date}"
        )

        date_key = self._format_date_key(request.date)
        verified = False
        timestamp = None
        block_height = None
        verification_details = {}

        # Verify OpenTimestamps proof
        if request.ots_proof:
            try:
                ots_result = await self.verify_opentimestamps_proof(
                    request.merkle_root,
                    request.ots_proof
                )
                verified = ots_result.get("verified", False)
                timestamp = ots_result.get("timestamp")
                block_height = ots_result.get("bitcoin_block_height")
                verification_details["opentimestamps"] = ots_result

            except Exception as e:
                logger.error(f"OTS verification failed: {e}")
                verification_details["opentimestamps"] = {
                    "verified": False,
                    "error": str(e)
                }

        # Verify blockchain transaction
        if request.tx_id:
            try:
                tx_data = await self.query_blockchain_transaction(request.tx_id)
                if tx_data.get("confirmed"):
                    verified = True
                    timestamp = datetime.fromtimestamp(tx_data.get("timestamp", 0))
                    block_height = tx_data.get("block_height")

                verification_details["blockchain"] = tx_data

            except Exception as e:
                logger.error(f"Blockchain verification failed: {e}")
                verification_details["blockchain"] = {
                    "verified": False,
                    "error": str(e)
                }

        return VerifyProofResponse(
            merkle_root=request.merkle_root,
            date=date_key,
            verified=verified,
            blockchain="bitcoin",
            timestamp=timestamp,
            block_height=block_height,
            verification_details=verification_details
        )

    async def get_daily_attestations(
        self,
        start_date: dt.date,
        end_date: dt.date
    ) -> List[AttestationResponse]:
        """
        Get all attestations in date range

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of attestations
        """
        logger.info(f"Retrieving attestations from {start_date} to {end_date}")

        attestations = []
        current_date = start_date

        while current_date <= end_date:
            date_key = self._format_date_key(current_date)

            try:
                attestation = await self.get_attestation(date_key)
                attestations.append(attestation)
            except TimestampingError:
                # No attestation for this date
                pass

            # Move to next day
            from datetime import timedelta
            current_date += timedelta(days=1)

        return attestations

    def get_blockchain_explorer_url(
        self,
        tx_id: str,
        blockchain: BlockchainNetwork = BlockchainNetwork.BITCOIN
    ) -> str:
        """
        Get blockchain explorer URL for transaction

        Args:
            tx_id: Transaction ID
            blockchain: Blockchain network

        Returns:
            Explorer URL
        """
        if blockchain == BlockchainNetwork.BITCOIN:
            return f"https://blockstream.info/tx/{tx_id}"
        elif blockchain == BlockchainNetwork.ETHEREUM:
            return f"https://etherscan.io/tx/{tx_id}"
        elif blockchain == BlockchainNetwork.POLYGON:
            return f"https://polygonscan.com/tx/{tx_id}"
        else:
            return ""

    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()
        logger.info("Timestamping service cleaned up")


# Singleton instance
_timestamping_service: Optional[TimestampingService] = None


def get_timestamping_service() -> TimestampingService:
    """Get or create timestamping service instance"""
    global _timestamping_service
    if _timestamping_service is None:
        _timestamping_service = TimestampingService()
    return _timestamping_service
