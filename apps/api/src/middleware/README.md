# AIIndex API Policy Enforcement Middleware

Comprehensive middleware system for enforcing AIIndex policies, rate limiting, bot reputation management, fraud detection, and protocol version negotiation.

## Components

### 1. Policy Enforcement (`policy.py`)

Fetches and evaluates AIIndex policies from publisher domains.

**Features:**
- Fetches policies from `/.well-known/aiindex-policy.json` or `/ai-index.json`
- Evaluates training vs retrieval intent from `X-AIIndex-Intent` header
- Validates client_id against allowlists/blocklists
- 5-minute policy caching per domain
- Returns 403 Forbidden with signed denial receipt on violation

**Usage:**
```python
from fastapi import FastAPI
from middleware import policy_enforcement_middleware

app = FastAPI()

# Add middleware
app.middleware("http")(policy_enforcement_middleware)

# Manual policy check
async with PolicyEnforcer(request) as enforcer:
    violation = await enforcer.enforce("example.com")
    if violation:
        # Handle policy violation
        pass
```

**Headers:**
- `X-AIIndex-Intent: training|retrieval` - Request intent
- `X-AIIndex-Client-ID: <client_id>` - Client identifier
- `X-AIIndex-Version: 1.1` - Protocol version

### 2. Denial Receipt Generator (`denial_receipt.py`)

Creates cryptographically signed denial receipts for policy violations.

**Features:**
- Generates unique receipt IDs
- Signs with publisher's RSA private key
- Includes violation reason and policy URL
- Verifiable by clients using public key

**Usage:**
```python
from middleware import DenialReceiptGenerator

generator = DenialReceiptGenerator()

# Generate denial receipt
receipt = await generator.generate(
    domain="publisher.com",
    client_id="openai-gpt",
    violation_reason="blocked_training",
    intent="training",
    policy_url="https://publisher.com/.well-known/aiindex-policy.json"
)

# Returns 403 with receipt
return JSONResponse(status_code=403, content=receipt)
```

**Receipt Structure:**
```json
{
  "receipt_id": "uuid",
  "receipt_type": "denial",
  "denied_at": "2025-10-13T10:30:00Z",
  "domain": "publisher.com",
  "client_id": "openai-gpt",
  "intent": "training",
  "violation_reason": "blocked_training",
  "policy_url": "https://publisher.com/.well-known/aiindex-policy.json",
  "signature": "base64_signature",
  "signature_algorithm": "RSA-SHA256"
}
```

### 3. Advanced Rate Limiter (`rate_limiter.py`)

Redis-based rate limiting with sliding window algorithm.

**Features:**
- Per-client rate limiting (minute/hour/day windows)
- Sliding window algorithm for accuracy
- Burst allowance support
- Client whitelisting
- Returns 429 with Retry-After header

**Usage:**
```python
from middleware import create_rate_limiter, RateLimitConfig

# Create rate limiter
config = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    requests_per_day=10000,
    burst=10,
    whitelist=["openai-gpt", "anthropic-claude"]
)

rate_limiter = create_rate_limiter(
    redis_url="redis://localhost:6379",
    config=config
)

# Add middleware
app.middleware("http")(rate_limiter)

# Manual check
allowed, info = await rate_limiter.limiter.check_all_windows(
    client_id="some-client",
    config=config
)
```

**Response Headers:**
- `X-RateLimit-Limit: 60` - Limit per window
- `X-RateLimit-Remaining: 45` - Remaining requests
- `X-RateLimit-Reset: 2025-10-13T10:31:00Z` - Reset time
- `Retry-After: 60` - Seconds to wait (on 429)

### 4. Bot Reputation System (`bot_reputation.py`)

Maintains reputation scores and tracks client behavior.

**Features:**
- Verified client allowlist (OpenAI, Anthropic, Google, etc.)
- Reputation scoring (0-100)
- Automatic blocking below threshold
- Violation tracking and penalties
- PostgreSQL-backed persistence

**Usage:**
```python
from middleware import get_reputation_system, ViolationType

reputation = get_reputation_system(db_client)

# Check if client is allowed
allowed, reason = await reputation.is_allowed("some-client")

# Record violation
should_block = await reputation.record_violation(
    client_id="bad-actor",
    violation_type=ViolationType.FRAUD_ATTEMPT,
    description="Content hash mismatch detected",
    severity=9
)

# Improve reputation (for good behavior)
await reputation.improve_reputation(
    client_id="good-client",
    amount=5.0,
    reason="successful_verifications"
)

# Manually verify client
await reputation.verify_client(
    client_id="new-ai-service",
    metadata={"name": "New AI Service", "verified_by": "admin"}
)
```

**Reputation Statuses:**
- `verified` - Manually verified legitimate client (score 100)
- `trusted` - Trusted based on behavior (score 80+)
- `neutral` - New/unknown client (score 50)
- `suspicious` - Suspicious behavior (score 20-40)
- `blocked` - Blocked due to violations (score < 20)

### 5. Fraud Detection (`fraud_detection.py`)

Detects fraudulent receipt submissions.

**Features:**
- Content hash mismatch detection
- Clock skew detection (5-minute threshold)
- Signature reuse detection
- Batch fraud detection (10+ receipts in 10 seconds)
- Rate anomaly detection
- Audit logging

**Usage:**
```python
from middleware import get_fraud_detector

detector = get_fraud_detector(db_client)

# Check receipt for fraud
alerts = await detector.check_receipt(
    receipt_id="receipt-123",
    signature="signature_string",
    timestamp=datetime.now(timezone.utc),
    content="article content",
    content_hash="provided_hash",
    client_id="some-client"
)

# Check for specific fraud types
alert = await detector.check_content_hash(
    receipt_id="receipt-123",
    provided_hash="abc123",
    actual_content="content",
    client_id="client"
)

# Get fraud alerts
alerts = await detector.get_alerts(
    client_id="suspicious-client",
    min_severity=7,
    limit=50
)
```

**Fraud Types:**
- `content_hash_mismatch` - Content hash doesn't match (severity 9)
- `clock_skew` - Timestamp drift > 5 minutes (severity 6)
- `signature_reuse` - Signature used before (severity 8)
- `batch_fraud` - Too many submissions (severity 8)
- `duplicate_receipt` - Receipt ID reused (severity 7)
- `rate_anomaly` - Sudden spike in activity (severity 6)

### 6. Version Negotiation (`version_negotiation.py`)

Handles AIIndex protocol version negotiation.

**Features:**
- Parses `X-AIIndex-Version` header
- Validates against supported versions (1.0, 1.1, 1.2)
- Returns appropriate schema and features
- 406 Not Acceptable for unsupported versions
- Deprecation warnings for old versions

**Usage:**
```python
from middleware import (
    version_negotiation_middleware,
    get_request_version,
    requires_version,
    ProtocolVersion
)

# Add middleware
app.middleware("http")(version_negotiation_middleware)

# Get version in endpoint
@app.get("/v1/receipts")
async def get_receipts(request: Request):
    version = get_request_version(request)
    # Use version-specific logic
    pass

# Require minimum version
@app.get("/v1/advanced")
@requires_version(ProtocolVersion.V1_1)
async def advanced_endpoint(request: Request):
    # Only accessible with v1.1+
    pass
```

**Supported Versions:**

| Version | Features | Status |
|---------|----------|--------|
| 1.0 | Basic receipts, RSA signatures | Deprecated (sunset 2025-12-31) |
| 1.1 | + Policy enforcement, denial receipts, Ed25519 | Stable |
| 1.2 | + Fraud detection, bot reputation, webhooks | Latest |

## Complete Integration Example

```python
from fastapi import FastAPI, Request
from middleware import (
    policy_enforcement_middleware,
    version_negotiation_middleware,
    create_rate_limiter,
    RateLimitConfig,
    get_reputation_system,
    get_fraud_detector
)

app = FastAPI()

# 1. Add version negotiation (first)
app.middleware("http")(version_negotiation_middleware)

# 2. Add rate limiting
rate_limiter = create_rate_limiter(
    redis_url="redis://localhost:6379",
    config=RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000
    )
)
app.middleware("http")(rate_limiter)

# 3. Add policy enforcement (last)
app.middleware("http")(policy_enforcement_middleware)

# Initialize systems
reputation = get_reputation_system()
fraud_detector = get_fraud_detector()

@app.post("/v1/receipts")
async def ingest_receipt(request: Request, receipt_data: dict):
    # Check reputation
    client_id = request.headers.get("X-AIIndex-Client-ID")
    allowed, reason = await reputation.is_allowed(client_id)

    if not allowed:
        raise HTTPException(status_code=403, detail=f"Client blocked: {reason}")

    # Check for fraud
    alerts = await fraud_detector.check_receipt(
        receipt_id=receipt_data["receipt_id"],
        signature=receipt_data["signature"],
        timestamp=receipt_data["timestamp"],
        content=receipt_data.get("content"),
        content_hash=receipt_data.get("content_hash"),
        client_id=client_id
    )

    if alerts:
        # Record violation in reputation system
        for alert in alerts:
            await reputation.record_violation(
                client_id=client_id,
                violation_type=alert.fraud_type,
                description=alert.description,
                severity=alert.severity
            )

        raise HTTPException(
            status_code=400,
            detail=f"Fraud detected: {alerts[0].description}"
        )

    # Process receipt...
    return {"status": "success"}
```

## Configuration

### Environment Variables

```bash
# Private key for signing denial receipts
PUBLISHER_PRIVATE_KEY_PATH=/etc/iaindex/publisher_private_key.pem

# Redis for rate limiting
REDIS_URL=redis://localhost:6379

# Database for reputation/fraud tracking
DATABASE_URL=postgresql://user:pass@localhost/iaindex
```

### Database Schema

```sql
-- Bot reputation table
CREATE TABLE bot_reputation (
    client_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    reputation_score FLOAT NOT NULL,
    violation_count INT NOT NULL DEFAULT 0,
    last_violation TIMESTAMP,
    verified_at TIMESTAMP,
    blocked_at TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Violation records
CREATE TABLE violation_records (
    violation_id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL,
    violation_type VARCHAR(50) NOT NULL,
    description TEXT,
    severity INT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Fraud alerts
CREATE TABLE fraud_alerts (
    alert_id VARCHAR(255) PRIMARY KEY,
    fraud_type VARCHAR(50) NOT NULL,
    severity INT NOT NULL,
    description TEXT,
    client_id VARCHAR(255),
    receipt_id VARCHAR(255),
    detected_at TIMESTAMP DEFAULT NOW(),
    evidence JSONB,
    action_taken VARCHAR(255)
);
```

## Testing

```python
import pytest
from middleware import PolicyEnforcer, FraudDetector

@pytest.mark.asyncio
async def test_policy_enforcement():
    from fastapi import Request

    # Mock request with training intent
    request = Request(...)
    request.headers = {
        "X-AIIndex-Intent": "training",
        "X-AIIndex-Client-ID": "test-client"
    }

    async with PolicyEnforcer(request) as enforcer:
        violation = await enforcer.enforce("publisher.com")
        assert violation is not None

@pytest.mark.asyncio
async def test_fraud_detection():
    detector = FraudDetector()

    # Test clock skew
    old_timestamp = datetime.now(timezone.utc) - timedelta(minutes=10)
    alert = await detector.check_clock_skew(
        receipt_id="test",
        timestamp=old_timestamp,
        client_id="test"
    )

    assert alert is not None
    assert alert.fraud_type == FraudType.CLOCK_SKEW
```

## Performance Considerations

- **Policy Cache**: 5-minute TTL reduces external HTTP calls
- **Redis Rate Limiting**: Use Redis cluster for high availability
- **In-Memory Fallback**: All systems fallback to in-memory when Redis/DB unavailable
- **Batch Operations**: Use batch verification for multiple receipts
- **Async Operations**: All I/O operations are async for better performance

## Security Best practices

1. **Private Key Protection**: Store private keys securely, use HSM in production
2. **Redis Security**: Use TLS for Redis connections, enable authentication
3. **Rate Limiting**: Implement multiple tiers (IP, client, domain)
4. **Signature Verification**: Always verify signatures before processing
5. **Audit Logging**: Log all policy violations and fraud attempts
6. **Regular Updates**: Keep client allowlists updated

## License

Part of the IAIndex project - see main LICENSE file.
