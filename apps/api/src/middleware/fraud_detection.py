"""
Receipt Fraud Detection

Detects fraudulent receipt submissions including:
- Content hash mismatches
- Clock skew (timestamp drift)
- Signature reuse
- Batch fraud patterns
- Anomalous behavior
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)


class FraudType(str, Enum):
    """Types of fraud detected"""
    CONTENT_HASH_MISMATCH = "content_hash_mismatch"
    CLOCK_SKEW = "clock_skew"
    SIGNATURE_REUSE = "signature_reuse"
    BATCH_FRAUD = "batch_fraud"
    DUPLICATE_RECEIPT = "duplicate_receipt"
    INVALID_SIGNATURE = "invalid_signature"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    RATE_ANOMALY = "rate_anomaly"


class FraudAlert(BaseModel):
    """Fraud detection alert"""
    alert_id: str
    fraud_type: FraudType
    severity: int = Field(..., ge=1, le=10)
    description: str
    client_id: Optional[str] = None
    receipt_id: Optional[str] = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: Dict[str, Any] = Field(default_factory=dict)
    action_taken: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FraudDetector:
    """Fraud detection system"""

    # Clock skew threshold (5 minutes)
    CLOCK_SKEW_THRESHOLD_SECONDS = 300

    # Signature reuse detection window (1 hour)
    SIGNATURE_REUSE_WINDOW_SECONDS = 3600

    # Batch fraud detection (10+ receipts in 10 seconds)
    BATCH_THRESHOLD_COUNT = 10
    BATCH_THRESHOLD_SECONDS = 10

    # Rate anomaly detection
    RATE_ANOMALY_MULTIPLIER = 10.0  # 10x normal rate

    def __init__(self, db_client=None):
        """
        Initialize fraud detector

        Args:
            db_client: Database client for persistence
        """
        self.db = db_client
        self._signature_cache: Dict[str, Tuple[str, float]] = {}  # signature -> (client_id, timestamp)
        self._receipt_cache: Dict[str, float] = {}  # receipt_id -> timestamp
        self._submission_history: Dict[str, List[float]] = defaultdict(list)  # client_id -> timestamps
        self._alerts: List[FraudAlert] = []

    def compute_content_hash(self, content: str) -> str:
        """
        Compute content hash

        Args:
            content: Content to hash

        Returns:
            SHA-256 hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def check_content_hash(
        self,
        receipt_id: str,
        provided_hash: str,
        actual_content: str,
        client_id: Optional[str] = None
    ) -> Optional[FraudAlert]:
        """
        Check if content hash matches actual content

        Args:
            receipt_id: Receipt identifier
            provided_hash: Hash provided in receipt
            actual_content: Actual content
            client_id: Client identifier

        Returns:
            FraudAlert if mismatch detected
        """
        computed_hash = self.compute_content_hash(actual_content)

        if computed_hash != provided_hash:
            alert = FraudAlert(
                alert_id=f"fraud:{receipt_id}:{time.time()}",
                fraud_type=FraudType.CONTENT_HASH_MISMATCH,
                severity=9,
                description="Content hash does not match provided hash",
                client_id=client_id,
                receipt_id=receipt_id,
                evidence={
                    "provided_hash": provided_hash,
                    "computed_hash": computed_hash,
                    "content_length": len(actual_content)
                }
            )

            await self._record_alert(alert)

            logger.error(
                f"Content hash mismatch - Receipt: {receipt_id}, "
                f"Client: {client_id}, Provided: {provided_hash[:16]}..., "
                f"Computed: {computed_hash[:16]}..."
            )

            return alert

        return None

    async def check_clock_skew(
        self,
        receipt_id: str,
        timestamp: datetime,
        client_id: Optional[str] = None
    ) -> Optional[FraudAlert]:
        """
        Check for clock skew (timestamp too far from current time)

        Args:
            receipt_id: Receipt identifier
            timestamp: Receipt timestamp
            client_id: Client identifier

        Returns:
            FraudAlert if clock skew detected
        """
        now = datetime.now(timezone.utc)

        # Ensure timestamp is timezone-aware
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        time_diff = abs((now - timestamp).total_seconds())

        if time_diff > self.CLOCK_SKEW_THRESHOLD_SECONDS:
            alert = FraudAlert(
                alert_id=f"fraud:{receipt_id}:{time.time()}",
                fraud_type=FraudType.CLOCK_SKEW,
                severity=6,
                description=f"Timestamp drift of {time_diff:.0f} seconds detected",
                client_id=client_id,
                receipt_id=receipt_id,
                evidence={
                    "receipt_timestamp": timestamp.isoformat(),
                    "server_timestamp": now.isoformat(),
                    "drift_seconds": time_diff,
                    "threshold_seconds": self.CLOCK_SKEW_THRESHOLD_SECONDS
                }
            )

            await self._record_alert(alert)

            logger.warning(
                f"Clock skew detected - Receipt: {receipt_id}, "
                f"Client: {client_id}, Drift: {time_diff:.0f}s"
            )

            return alert

        return None

    async def check_signature_reuse(
        self,
        receipt_id: str,
        signature: str,
        client_id: Optional[str] = None
    ) -> Optional[FraudAlert]:
        """
        Check for signature reuse

        Args:
            receipt_id: Receipt identifier
            signature: Signature string
            client_id: Client identifier

        Returns:
            FraudAlert if signature reuse detected
        """
        now = time.time()

        # Clean up old signatures
        expired_signatures = [
            sig for sig, (_, ts) in self._signature_cache.items()
            if now - ts > self.SIGNATURE_REUSE_WINDOW_SECONDS
        ]
        for sig in expired_signatures:
            del self._signature_cache[sig]

        # Check if signature was used recently
        if signature in self._signature_cache:
            previous_client, previous_time = self._signature_cache[signature]

            alert = FraudAlert(
                alert_id=f"fraud:{receipt_id}:{time.time()}",
                fraud_type=FraudType.SIGNATURE_REUSE,
                severity=8,
                description="Signature has been used in another recent receipt",
                client_id=client_id,
                receipt_id=receipt_id,
                evidence={
                    "signature_prefix": signature[:32],
                    "previous_client": previous_client,
                    "previous_time": datetime.fromtimestamp(previous_time, tz=timezone.utc).isoformat(),
                    "time_diff_seconds": now - previous_time
                }
            )

            await self._record_alert(alert)

            logger.error(
                f"Signature reuse detected - Receipt: {receipt_id}, "
                f"Client: {client_id}, Previous client: {previous_client}"
            )

            return alert

        # Store signature
        self._signature_cache[signature] = (client_id or "unknown", now)

        return None

    async def check_duplicate_receipt(
        self,
        receipt_id: str,
        client_id: Optional[str] = None
    ) -> Optional[FraudAlert]:
        """
        Check for duplicate receipt submission

        Args:
            receipt_id: Receipt identifier
            client_id: Client identifier

        Returns:
            FraudAlert if duplicate detected
        """
        if receipt_id in self._receipt_cache:
            previous_time = self._receipt_cache[receipt_id]

            alert = FraudAlert(
                alert_id=f"fraud:{receipt_id}:{time.time()}",
                fraud_type=FraudType.DUPLICATE_RECEIPT,
                severity=7,
                description="Receipt ID has been submitted before",
                client_id=client_id,
                receipt_id=receipt_id,
                evidence={
                    "previous_submission": datetime.fromtimestamp(previous_time, tz=timezone.utc).isoformat(),
                    "time_since_previous": time.time() - previous_time
                }
            )

            await self._record_alert(alert)

            logger.warning(
                f"Duplicate receipt detected - Receipt: {receipt_id}, "
                f"Client: {client_id}"
            )

            return alert

        # Store receipt
        self._receipt_cache[receipt_id] = time.time()

        return None

    async def check_batch_fraud(
        self,
        client_id: str
    ) -> Optional[FraudAlert]:
        """
        Check for batch fraud (many receipts in short time)

        Args:
            client_id: Client identifier

        Returns:
            FraudAlert if batch fraud detected
        """
        now = time.time()

        # Add current submission
        self._submission_history[client_id].append(now)

        # Clean up old submissions
        cutoff = now - self.BATCH_THRESHOLD_SECONDS
        self._submission_history[client_id] = [
            ts for ts in self._submission_history[client_id]
            if ts > cutoff
        ]

        # Check if threshold exceeded
        recent_count = len(self._submission_history[client_id])

        if recent_count >= self.BATCH_THRESHOLD_COUNT:
            alert = FraudAlert(
                alert_id=f"fraud:batch:{client_id}:{time.time()}",
                fraud_type=FraudType.BATCH_FRAUD,
                severity=8,
                description=f"Suspicious batch submission: {recent_count} receipts in {self.BATCH_THRESHOLD_SECONDS}s",
                client_id=client_id,
                evidence={
                    "submission_count": recent_count,
                    "time_window_seconds": self.BATCH_THRESHOLD_SECONDS,
                    "threshold": self.BATCH_THRESHOLD_COUNT,
                    "submission_rate": recent_count / self.BATCH_THRESHOLD_SECONDS
                }
            )

            await self._record_alert(alert)

            logger.error(
                f"Batch fraud detected - Client: {client_id}, "
                f"Count: {recent_count} in {self.BATCH_THRESHOLD_SECONDS}s"
            )

            return alert

        return None

    async def check_rate_anomaly(
        self,
        client_id: str,
        normal_rate: float = 1.0  # requests per minute
    ) -> Optional[FraudAlert]:
        """
        Check for rate anomalies (sudden spikes)

        Args:
            client_id: Client identifier
            normal_rate: Normal request rate (per minute)

        Returns:
            FraudAlert if anomaly detected
        """
        now = time.time()

        # Look at last minute
        cutoff = now - 60
        recent_submissions = [
            ts for ts in self._submission_history[client_id]
            if ts > cutoff
        ]

        current_rate = len(recent_submissions)

        # Check if rate is anomalously high
        if current_rate > normal_rate * self.RATE_ANOMALY_MULTIPLIER:
            alert = FraudAlert(
                alert_id=f"fraud:rate:{client_id}:{time.time()}",
                fraud_type=FraudType.RATE_ANOMALY,
                severity=6,
                description=f"Rate anomaly: {current_rate} req/min vs normal {normal_rate} req/min",
                client_id=client_id,
                evidence={
                    "current_rate": current_rate,
                    "normal_rate": normal_rate,
                    "multiplier": current_rate / normal_rate if normal_rate > 0 else 0,
                    "threshold_multiplier": self.RATE_ANOMALY_MULTIPLIER
                }
            )

            await self._record_alert(alert)

            logger.warning(
                f"Rate anomaly detected - Client: {client_id}, "
                f"Rate: {current_rate} req/min (normal: {normal_rate} req/min)"
            )

            return alert

        return None

    async def check_receipt(
        self,
        receipt_id: str,
        signature: str,
        timestamp: datetime,
        content: Optional[str] = None,
        content_hash: Optional[str] = None,
        client_id: Optional[str] = None
    ) -> List[FraudAlert]:
        """
        Perform comprehensive fraud checks on receipt

        Args:
            receipt_id: Receipt identifier
            signature: Signature string
            timestamp: Receipt timestamp
            content: Actual content (optional)
            content_hash: Provided content hash (optional)
            client_id: Client identifier

        Returns:
            List of fraud alerts (empty if no fraud detected)
        """
        alerts = []

        # Check for duplicate receipt
        alert = await self.check_duplicate_receipt(receipt_id, client_id)
        if alert:
            alerts.append(alert)

        # Check clock skew
        alert = await self.check_clock_skew(receipt_id, timestamp, client_id)
        if alert:
            alerts.append(alert)

        # Check signature reuse
        alert = await self.check_signature_reuse(receipt_id, signature, client_id)
        if alert:
            alerts.append(alert)

        # Check content hash if provided
        if content and content_hash:
            alert = await self.check_content_hash(receipt_id, content_hash, content, client_id)
            if alert:
                alerts.append(alert)

        # Check batch fraud if client_id provided
        if client_id:
            alert = await self.check_batch_fraud(client_id)
            if alert:
                alerts.append(alert)

        return alerts

    async def get_alerts(
        self,
        client_id: Optional[str] = None,
        fraud_type: Optional[FraudType] = None,
        min_severity: int = 1,
        limit: int = 100
    ) -> List[FraudAlert]:
        """
        Get fraud alerts

        Args:
            client_id: Filter by client ID
            fraud_type: Filter by fraud type
            min_severity: Minimum severity
            limit: Maximum number of alerts

        Returns:
            List of fraud alerts
        """
        alerts = self._alerts

        # Apply filters
        if client_id:
            alerts = [a for a in alerts if a.client_id == client_id]

        if fraud_type:
            alerts = [a for a in alerts if a.fraud_type == fraud_type]

        if min_severity > 1:
            alerts = [a for a in alerts if a.severity >= min_severity]

        # Sort by timestamp (most recent first)
        alerts = sorted(alerts, key=lambda a: a.detected_at, reverse=True)

        return alerts[:limit]

    async def clear_alerts(self, client_id: Optional[str] = None):
        """
        Clear fraud alerts

        Args:
            client_id: Clear alerts for specific client (None = clear all)
        """
        if client_id:
            self._alerts = [a for a in self._alerts if a.client_id != client_id]
            logger.info(f"Cleared alerts for client: {client_id}")
        else:
            self._alerts.clear()
            logger.info("Cleared all fraud alerts")

    async def _record_alert(self, alert: FraudAlert):
        """
        Record fraud alert

        Args:
            alert: Fraud alert to record
        """
        self._alerts.append(alert)

        # Save to database if available
        if self.db:
            try:
                await self._save_alert_to_db(alert)
            except Exception as e:
                logger.error(f"Failed to save alert to database: {e}")

        # Keep only recent alerts in memory (last 1000)
        if len(self._alerts) > 1000:
            self._alerts = self._alerts[-1000:]

    async def _save_alert_to_db(self, alert: FraudAlert):
        """Save alert to database"""
        # Implement database save logic
        pass


# Global fraud detector instance
fraud_detector: Optional[FraudDetector] = None


def get_fraud_detector(db_client=None) -> FraudDetector:
    """Get or create fraud detector instance"""
    global fraud_detector
    if fraud_detector is None:
        fraud_detector = FraudDetector(db_client)
    return fraud_detector
