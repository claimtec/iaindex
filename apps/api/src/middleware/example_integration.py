"""
Example Integration: Complete Middleware Setup

This file demonstrates how to integrate all AIIndex middleware components
into a FastAPI application.
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from typing import Optional
import logging

# Import all middleware components
from middleware import (
    # Policy enforcement
    policy_enforcement_middleware,
    PolicyEnforcer,
    clear_policy_cache,

    # Rate limiting
    create_rate_limiter,
    RateLimitConfig,

    # Bot reputation
    get_reputation_system,
    ViolationType,
    ReputationStatus,

    # Fraud detection
    get_fraud_detector,
    FraudType,

    # Version negotiation
    version_negotiation_middleware,
    get_request_version,
    requires_version,
    ProtocolVersion,

    # Denial receipts
    DenialReceiptGenerator
)

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI, redis_url: Optional[str] = None, db_client=None):
    """
    Setup all AIIndex middleware on FastAPI app

    Args:
        app: FastAPI application
        redis_url: Redis connection URL for rate limiting
        db_client: Database client for reputation/fraud tracking
    """

    # 1. Version negotiation (should be first)
    # Parses X-AIIndex-Version header and validates
    app.middleware("http")(version_negotiation_middleware)

    # 2. Rate limiting
    # Configure rate limits
    rate_config = RateLimitConfig(
        requests_per_minute=60,      # 60 requests per minute
        requests_per_hour=1000,      # 1000 requests per hour
        requests_per_day=10000,      # 10k requests per day
        burst=10,                    # Allow 10 burst requests
        whitelist=[                  # Whitelist verified clients
            "openai-gpt",
            "anthropic-claude",
            "google-gemini"
        ]
    )

    rate_limiter = create_rate_limiter(redis_url=redis_url, config=rate_config)
    app.middleware("http")(rate_limiter)

    # 3. Policy enforcement (should be last)
    # Checks publisher policies and blocks unauthorized access
    app.middleware("http")(policy_enforcement_middleware)

    logger.info("AIIndex middleware configured successfully")


# Create FastAPI app
app = FastAPI(
    title="AIIndex API with Policy Enforcement",
    version="1.0.0",
    description="Complete example with all AIIndex middleware"
)

# Setup middleware
setup_middleware(
    app,
    redis_url="redis://localhost:6379",
    db_client=None  # Pass your Supabase/PostgreSQL client here
)

# Initialize reputation and fraud detection systems
reputation_system = get_reputation_system()
fraud_detector = get_fraud_detector()


@app.get("/health")
async def health_check():
    """Health check endpoint (bypasses middleware)"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/v1/receipts/ingest")
async def ingest_receipt(request: Request, receipt_data: dict):
    """
    Ingest a publisher receipt with complete validation

    Headers:
        X-AIIndex-Client-ID: Client identifier (required)
        X-AIIndex-Intent: training|retrieval (optional, defaults to retrieval)
        X-AIIndex-Version: 1.0|1.1|1.2 (optional, defaults to 1.1)

    Body:
        {
            "receipt_id": "uuid",
            "publisher_domain": "example.com",
            "article_url": "https://example.com/article",
            "timestamp": "2025-10-13T10:00:00Z",
            "signature": "base64_signature",
            "content_hash": "sha256_hash",
            "metadata": {}
        }
    """
    # Extract client ID
    client_id = request.headers.get("X-AIIndex-Client-ID")
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-AIIndex-Client-ID header is required"
        )

    # Get protocol version
    version = get_request_version(request)
    logger.info(f"Processing receipt with protocol version {version.value}")

    # 1. Check bot reputation
    allowed, reason = await reputation_system.is_allowed(client_id)
    if not allowed:
        logger.warning(f"Client {client_id} blocked: {reason}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Client blocked: {reason}"
        )

    # Check if verified
    is_verified = await reputation_system.is_verified(client_id)
    logger.info(f"Client {client_id} verified: {is_verified}")

    # 2. Validate receipt data
    required_fields = [
        "receipt_id", "publisher_domain", "article_url",
        "timestamp", "signature"
    ]
    for field in required_fields:
        if field not in receipt_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )

    # Parse timestamp
    try:
        timestamp = datetime.fromisoformat(
            receipt_data["timestamp"].replace("Z", "+00:00")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timestamp format: {e}"
        )

    # 3. Fraud detection
    alerts = await fraud_detector.check_receipt(
        receipt_id=receipt_data["receipt_id"],
        signature=receipt_data["signature"],
        timestamp=timestamp,
        content=receipt_data.get("content"),
        content_hash=receipt_data.get("content_hash"),
        client_id=client_id
    )

    if alerts:
        logger.error(f"Fraud detected for client {client_id}: {len(alerts)} alerts")

        # Record violations in reputation system
        for alert in alerts:
            # Map fraud type to violation type
            violation_type = {
                FraudType.CONTENT_HASH_MISMATCH: ViolationType.FRAUD_ATTEMPT,
                FraudType.SIGNATURE_REUSE: ViolationType.FRAUD_ATTEMPT,
                FraudType.BATCH_FRAUD: ViolationType.SUSPICIOUS_PATTERN,
                FraudType.CLOCK_SKEW: ViolationType.SUSPICIOUS_PATTERN,
            }.get(alert.fraud_type, ViolationType.POLICY_VIOLATION)

            should_block = await reputation_system.record_violation(
                client_id=client_id,
                violation_type=violation_type,
                description=alert.description,
                severity=alert.severity
            )

            if should_block:
                logger.warning(f"Client {client_id} auto-blocked due to violations")

        # Return first fraud alert
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Fraud detected",
                "fraud_type": alerts[0].fraud_type,
                "description": alerts[0].description,
                "alert_id": alerts[0].alert_id
            }
        )

    # 4. Policy check (already done by middleware, but can double-check)
    async with PolicyEnforcer(request) as enforcer:
        violation = await enforcer.enforce(receipt_data["publisher_domain"])
        if violation:
            # This shouldn't happen if middleware is working
            logger.error(f"Policy violation not caught by middleware: {violation}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Policy violation"
            )

    # 5. Process receipt (your business logic here)
    logger.info(
        f"Successfully validated receipt {receipt_data['receipt_id']} "
        f"from {client_id} for {receipt_data['publisher_domain']}"
    )

    # Improve reputation for successful validation
    await reputation_system.improve_reputation(
        client_id=client_id,
        amount=1.0,
        reason="successful_receipt_validation"
    )

    return {
        "status": "success",
        "receipt_id": receipt_data["receipt_id"],
        "verified": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client_reputation": (await reputation_system.get_reputation(client_id)).reputation_score
    }


@app.get("/v1/clients/{client_id}/reputation")
async def get_client_reputation(client_id: str):
    """Get reputation information for a client"""
    reputation = await reputation_system.get_reputation(client_id)

    return {
        "client_id": reputation.client_id,
        "status": reputation.status,
        "reputation_score": reputation.reputation_score,
        "violation_count": reputation.violation_count,
        "last_violation": reputation.last_violation.isoformat() if reputation.last_violation else None,
        "verified": reputation.status == ReputationStatus.VERIFIED
    }


@app.get("/v1/clients/{client_id}/violations")
async def get_client_violations(client_id: str, limit: int = 50):
    """Get violation history for a client"""
    violations = await reputation_system.get_violation_history(client_id, limit)

    return {
        "client_id": client_id,
        "violation_count": len(violations),
        "violations": [
            {
                "violation_id": v.violation_id,
                "violation_type": v.violation_type,
                "description": v.description,
                "severity": v.severity,
                "timestamp": v.timestamp.isoformat()
            }
            for v in violations
        ]
    }


@app.get("/v1/fraud/alerts")
async def get_fraud_alerts(
    client_id: Optional[str] = None,
    fraud_type: Optional[FraudType] = None,
    min_severity: int = 1,
    limit: int = 100
):
    """Get fraud detection alerts"""
    alerts = await fraud_detector.get_alerts(
        client_id=client_id,
        fraud_type=fraud_type,
        min_severity=min_severity,
        limit=limit
    )

    return {
        "alert_count": len(alerts),
        "alerts": [
            {
                "alert_id": a.alert_id,
                "fraud_type": a.fraud_type,
                "severity": a.severity,
                "description": a.description,
                "client_id": a.client_id,
                "receipt_id": a.receipt_id,
                "detected_at": a.detected_at.isoformat(),
                "evidence": a.evidence
            }
            for a in alerts
        ]
    }


@app.post("/v1/admin/clients/{client_id}/verify")
async def verify_client(client_id: str, metadata: Optional[dict] = None):
    """Manually verify a client (admin endpoint)"""
    await reputation_system.verify_client(client_id, metadata)

    return {
        "status": "success",
        "message": f"Client {client_id} has been verified",
        "reputation_score": 100.0
    }


@app.post("/v1/admin/clients/{client_id}/block")
async def block_client(client_id: str, reason: str):
    """Manually block a client (admin endpoint)"""
    await reputation_system.block_client(client_id, reason)

    return {
        "status": "success",
        "message": f"Client {client_id} has been blocked",
        "reason": reason
    }


@app.post("/v1/admin/clients/{client_id}/unblock")
async def unblock_client(client_id: str):
    """Unblock a client (admin endpoint)"""
    await reputation_system.unblock_client(client_id)

    return {
        "status": "success",
        "message": f"Client {client_id} has been unblocked"
    }


@app.post("/v1/admin/cache/clear")
async def clear_cache():
    """Clear policy cache (admin endpoint)"""
    clear_policy_cache()

    return {
        "status": "success",
        "message": "Policy cache cleared"
    }


@app.get("/v1/version")
async def get_version_info(request: Request):
    """Get protocol version information"""
    version = get_request_version(request)

    from middleware.version_negotiation import version_negotiator
    version_info = version_negotiator.create_version_response(version)

    return version_info


@app.get("/v1/advanced")
@requires_version(ProtocolVersion.V1_1)
async def advanced_endpoint(request: Request):
    """
    Advanced endpoint requiring protocol version 1.1+

    This demonstrates version-gated endpoints
    """
    version = get_request_version(request)

    return {
        "message": "This endpoint requires protocol version 1.1 or higher",
        "your_version": version.value,
        "features": ["policy_enforcement", "denial_receipts", "fraud_detection"]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
