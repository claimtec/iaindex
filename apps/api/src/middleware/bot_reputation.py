"""
Bot Reputation System

Maintains allowlists and denylists for AI clients.
Tracks client behavior, violations, and reputation scores.
Auto-blocks bad actors after threshold violations.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime, timedelta, timezone
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class ReputationStatus(str, Enum):
    """Client reputation status"""
    VERIFIED = "verified"  # Verified legitimate client
    TRUSTED = "trusted"    # Trusted based on behavior
    NEUTRAL = "neutral"    # New or unknown client
    SUSPICIOUS = "suspicious"  # Showing suspicious behavior
    BLOCKED = "blocked"    # Blocked due to violations


class ViolationType(str, Enum):
    """Types of policy violations"""
    FRAUD_ATTEMPT = "fraud_attempt"
    INVALID_SIGNATURE = "invalid_signature"
    POLICY_VIOLATION = "policy_violation"
    RATE_LIMIT_ABUSE = "rate_limit_abuse"
    CONTENT_SCRAPING = "content_scraping"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


class BotReputation(BaseModel):
    """Bot reputation record"""
    client_id: str = Field(..., description="Client identifier")
    status: ReputationStatus = Field(default=ReputationStatus.NEUTRAL)
    reputation_score: float = Field(default=50.0, ge=0.0, le=100.0)
    violation_count: int = Field(default=0, ge=0)
    last_violation: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    blocked_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ViolationRecord(BaseModel):
    """Record of a policy violation"""
    violation_id: str
    client_id: str
    violation_type: ViolationType
    description: str
    severity: int = Field(..., ge=1, le=10)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BotReputationSystem:
    """Manages bot reputation and behavior tracking"""

    # Known verified AI clients (allowlist)
    VERIFIED_CLIENTS = {
        "openai-gpt": {
            "name": "OpenAI GPT",
            "verified": True,
            "reputation": 100.0
        },
        "anthropic-claude": {
            "name": "Anthropic Claude",
            "verified": True,
            "reputation": 100.0
        },
        "google-gemini": {
            "name": "Google Gemini",
            "verified": True,
            "reputation": 100.0
        },
        "meta-llama": {
            "name": "Meta Llama",
            "verified": True,
            "reputation": 100.0
        },
        "cohere-ai": {
            "name": "Cohere AI",
            "verified": True,
            "reputation": 100.0
        },
        "perplexity-ai": {
            "name": "Perplexity AI",
            "verified": True,
            "reputation": 95.0
        },
        "you-com": {
            "name": "You.com Search",
            "verified": True,
            "reputation": 95.0
        }
    }

    # Reputation score thresholds
    BLOCK_THRESHOLD = 20.0  # Block below this score
    SUSPICIOUS_THRESHOLD = 40.0  # Flag as suspicious below this
    TRUSTED_THRESHOLD = 80.0  # Trusted above this

    # Violation penalties (score deduction)
    VIOLATION_PENALTIES = {
        ViolationType.FRAUD_ATTEMPT: 30.0,
        ViolationType.INVALID_SIGNATURE: 15.0,
        ViolationType.POLICY_VIOLATION: 10.0,
        ViolationType.RATE_LIMIT_ABUSE: 5.0,
        ViolationType.CONTENT_SCRAPING: 8.0,
        ViolationType.SUSPICIOUS_PATTERN: 5.0
    }

    # Auto-block after N violations
    AUTO_BLOCK_THRESHOLD = 5

    def __init__(self, db_client=None):
        """
        Initialize bot reputation system

        Args:
            db_client: Database client (Supabase or similar)
        """
        self.db = db_client
        self._cache: Dict[str, BotReputation] = {}
        self._violation_history: Dict[str, List[ViolationRecord]] = {}

        # Initialize verified clients in cache
        for client_id, info in self.VERIFIED_CLIENTS.items():
            self._cache[client_id] = BotReputation(
                client_id=client_id,
                status=ReputationStatus.VERIFIED,
                reputation_score=info["reputation"],
                verified_at=datetime.now(timezone.utc),
                metadata={"name": info["name"], "verified": True}
            )

    async def get_reputation(self, client_id: str) -> BotReputation:
        """
        Get reputation for client

        Args:
            client_id: Client identifier

        Returns:
            BotReputation object
        """
        # Check cache
        if client_id in self._cache:
            return self._cache[client_id]

        # Try database
        if self.db:
            try:
                result = await self._fetch_from_db(client_id)
                if result:
                    reputation = BotReputation(**result)
                    self._cache[client_id] = reputation
                    return reputation
            except Exception as e:
                logger.error(f"Failed to fetch reputation from database: {e}")

        # Create new neutral reputation
        reputation = BotReputation(client_id=client_id)
        self._cache[client_id] = reputation

        # Save to database
        if self.db:
            await self._save_to_db(reputation)

        logger.info(f"Created new reputation record for client: {client_id}")
        return reputation

    async def is_allowed(self, client_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if client is allowed to access

        Args:
            client_id: Client identifier

        Returns:
            (allowed, reason) tuple
        """
        reputation = await self.get_reputation(client_id)

        if reputation.status == ReputationStatus.BLOCKED:
            return False, "client_blocked"

        if reputation.reputation_score < self.BLOCK_THRESHOLD:
            return False, "low_reputation_score"

        return True, None

    async def is_verified(self, client_id: str) -> bool:
        """Check if client is verified"""
        reputation = await self.get_reputation(client_id)
        return reputation.status == ReputationStatus.VERIFIED

    async def record_violation(
        self,
        client_id: str,
        violation_type: ViolationType,
        description: str,
        severity: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a policy violation

        Args:
            client_id: Client identifier
            violation_type: Type of violation
            description: Description of violation
            severity: Severity (1-10)
            metadata: Additional metadata

        Returns:
            True if client should be blocked
        """
        reputation = await self.get_reputation(client_id)

        # Don't penalize verified clients as harshly
        if reputation.status == ReputationStatus.VERIFIED:
            penalty = self.VIOLATION_PENALTIES.get(violation_type, 5.0) * 0.5
        else:
            penalty = self.VIOLATION_PENALTIES.get(violation_type, 5.0)

        # Apply severity multiplier
        penalty *= (severity / 5.0)

        # Update reputation
        reputation.reputation_score = max(0.0, reputation.reputation_score - penalty)
        reputation.violation_count += 1
        reputation.last_violation = datetime.now(timezone.utc)
        reputation.updated_at = datetime.now(timezone.utc)

        # Update status based on score
        if reputation.reputation_score < self.BLOCK_THRESHOLD:
            reputation.status = ReputationStatus.BLOCKED
            reputation.blocked_at = datetime.now(timezone.utc)
        elif reputation.reputation_score < self.SUSPICIOUS_THRESHOLD:
            if reputation.status != ReputationStatus.VERIFIED:
                reputation.status = ReputationStatus.SUSPICIOUS

        # Auto-block if too many violations
        should_block = False
        if reputation.violation_count >= self.AUTO_BLOCK_THRESHOLD:
            if reputation.status != ReputationStatus.VERIFIED:
                reputation.status = ReputationStatus.BLOCKED
                reputation.blocked_at = datetime.now(timezone.utc)
                should_block = True

        # Record violation
        violation = ViolationRecord(
            violation_id=f"{client_id}:{datetime.now(timezone.utc).timestamp()}",
            client_id=client_id,
            violation_type=violation_type,
            description=description,
            severity=severity,
            metadata=metadata or {}
        )

        if client_id not in self._violation_history:
            self._violation_history[client_id] = []
        self._violation_history[client_id].append(violation)

        # Update cache
        self._cache[client_id] = reputation

        # Save to database
        if self.db:
            await self._save_to_db(reputation)
            await self._save_violation_to_db(violation)

        logger.warning(
            f"Recorded violation - Client: {client_id}, "
            f"Type: {violation_type}, Score: {reputation.reputation_score:.2f}, "
            f"Status: {reputation.status}"
        )

        return should_block

    async def improve_reputation(
        self,
        client_id: str,
        amount: float = 5.0,
        reason: str = "good_behavior"
    ):
        """
        Improve client reputation

        Args:
            client_id: Client identifier
            amount: Amount to increase score
            reason: Reason for improvement
        """
        reputation = await self.get_reputation(client_id)

        # Don't improve beyond 100
        reputation.reputation_score = min(100.0, reputation.reputation_score + amount)
        reputation.updated_at = datetime.now(timezone.utc)

        # Update status based on score
        if reputation.reputation_score >= self.TRUSTED_THRESHOLD:
            if reputation.status != ReputationStatus.VERIFIED:
                reputation.status = ReputationStatus.TRUSTED
        elif reputation.reputation_score >= self.SUSPICIOUS_THRESHOLD:
            if reputation.status == ReputationStatus.SUSPICIOUS:
                reputation.status = ReputationStatus.NEUTRAL

        # Update cache
        self._cache[client_id] = reputation

        # Save to database
        if self.db:
            await self._save_to_db(reputation)

        logger.info(
            f"Improved reputation - Client: {client_id}, "
            f"Score: {reputation.reputation_score:.2f}, Reason: {reason}"
        )

    async def get_violation_history(
        self,
        client_id: str,
        limit: int = 100
    ) -> List[ViolationRecord]:
        """
        Get violation history for client

        Args:
            client_id: Client identifier
            limit: Maximum number of records

        Returns:
            List of violation records
        """
        # Get from cache/memory
        history = self._violation_history.get(client_id, [])

        # Try database if needed
        if self.db and len(history) == 0:
            try:
                db_history = await self._fetch_violations_from_db(client_id, limit)
                history = [ViolationRecord(**v) for v in db_history]
                self._violation_history[client_id] = history
            except Exception as e:
                logger.error(f"Failed to fetch violations from database: {e}")

        # Return most recent violations
        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]

    async def verify_client(self, client_id: str, metadata: Optional[Dict] = None):
        """
        Manually verify a client

        Args:
            client_id: Client identifier
            metadata: Verification metadata
        """
        reputation = await self.get_reputation(client_id)
        reputation.status = ReputationStatus.VERIFIED
        reputation.reputation_score = 100.0
        reputation.verified_at = datetime.now(timezone.utc)
        reputation.updated_at = datetime.now(timezone.utc)

        if metadata:
            reputation.metadata.update(metadata)

        # Update cache
        self._cache[client_id] = reputation

        # Save to database
        if self.db:
            await self._save_to_db(reputation)

        logger.info(f"Verified client: {client_id}")

    async def block_client(self, client_id: str, reason: str):
        """
        Manually block a client

        Args:
            client_id: Client identifier
            reason: Reason for blocking
        """
        reputation = await self.get_reputation(client_id)
        reputation.status = ReputationStatus.BLOCKED
        reputation.reputation_score = 0.0
        reputation.blocked_at = datetime.now(timezone.utc)
        reputation.updated_at = datetime.now(timezone.utc)
        reputation.metadata["block_reason"] = reason

        # Update cache
        self._cache[client_id] = reputation

        # Save to database
        if self.db:
            await self._save_to_db(reputation)

        logger.warning(f"Blocked client: {client_id}, Reason: {reason}")

    async def unblock_client(self, client_id: str):
        """Unblock a client"""
        reputation = await self.get_reputation(client_id)
        reputation.status = ReputationStatus.NEUTRAL
        reputation.reputation_score = 50.0
        reputation.blocked_at = None
        reputation.updated_at = datetime.now(timezone.utc)

        # Update cache
        self._cache[client_id] = reputation

        # Save to database
        if self.db:
            await self._save_to_db(reputation)

        logger.info(f"Unblocked client: {client_id}")

    # Database operations (implement based on your DB)
    async def _fetch_from_db(self, client_id: str) -> Optional[Dict]:
        """Fetch reputation from database"""
        # Implement database fetch logic
        return None

    async def _save_to_db(self, reputation: BotReputation):
        """Save reputation to database"""
        # Implement database save logic
        pass

    async def _save_violation_to_db(self, violation: ViolationRecord):
        """Save violation to database"""
        # Implement database save logic
        pass

    async def _fetch_violations_from_db(self, client_id: str, limit: int) -> List[Dict]:
        """Fetch violations from database"""
        # Implement database fetch logic
        return []


# Global reputation system instance
reputation_system: Optional[BotReputationSystem] = None


def get_reputation_system(db_client=None) -> BotReputationSystem:
    """Get or create reputation system instance"""
    global reputation_system
    if reputation_system is None:
        reputation_system = BotReputationSystem(db_client)
    return reputation_system
