# AIIndex Middleware - Quick Start Guide

## Installation

1. Install additional dependencies:
```bash
pip install redis packaging
```

2. Update requirements.txt:
```txt
redis==5.0.0
packaging==23.2
```

## Basic Setup (5 minutes)

```python
from fastapi import FastAPI
from middleware import (
    version_negotiation_middleware,
    policy_enforcement_middleware,
    create_rate_limiter,
    RateLimitConfig
)

app = FastAPI()

# 1. Add version negotiation
app.middleware("http")(version_negotiation_middleware)

# 2. Add rate limiting
rate_limiter = create_rate_limiter(
    redis_url="redis://localhost:6379",  # Optional, falls back to in-memory
    config=RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000
    )
)
app.middleware("http")(rate_limiter)

# 3. Add policy enforcement
app.middleware("http")(policy_enforcement_middleware)
```

## Testing

### Test with curl

```bash
# Basic request
curl -X POST http://localhost:8000/v1/receipts/ingest \
  -H "Content-Type: application/json" \
  -H "X-AIIndex-Client-ID: test-client" \
  -H "X-AIIndex-Intent: retrieval" \
  -H "X-AIIndex-Version: 1.1" \
  -d '{
    "receipt_id": "test-123",
    "publisher_domain": "example.com",
    "article_url": "https://example.com/article",
    "timestamp": "2025-10-13T10:00:00Z",
    "signature": "test_signature"
  }'

# Test training intent (likely blocked)
curl -X POST http://localhost:8000/v1/receipts/ingest \
  -H "X-AIIndex-Client-ID: test-client" \
  -H "X-AIIndex-Intent: training" \
  ...

# Test with verified client
curl -X POST http://localhost:8000/v1/receipts/ingest \
  -H "X-AIIndex-Client-ID: openai-gpt" \
  ...

# Check version info
curl http://localhost:8000/v1/version \
  -H "X-AIIndex-Version: 1.2"

# Check client reputation
curl http://localhost:8000/v1/clients/test-client/reputation
```

### Test Rate Limiting

```bash
# Trigger rate limit (send 100 requests quickly)
for i in {1..100}; do
  curl http://localhost:8000/v1/receipts/ingest \
    -H "X-AIIndex-Client-ID: test-client" \
    ...
done

# Should get 429 Too Many Requests after limit
```

### Test Fraud Detection

```python
from middleware import get_fraud_detector
from datetime import datetime, timezone, timedelta

detector = get_fraud_detector()

# Test clock skew
old_time = datetime.now(timezone.utc) - timedelta(minutes=10)
alert = await detector.check_clock_skew("receipt-1", old_time, "client-1")
print(f"Alert: {alert}")

# Test signature reuse
await detector.check_signature_reuse("receipt-1", "sig123", "client-1")
await detector.check_signature_reuse("receipt-2", "sig123", "client-1")  # Should alert
```

## Common Scenarios

### Scenario 1: Block Training, Allow Retrieval

Publisher creates `/.well-known/aiindex-policy.json`:
```json
{
  "version": "1.1",
  "publisher_domain": "example.com",
  "training_allowed": false,
  "retrieval_allowed": true,
  "policy_effective_date": "2025-10-01T00:00:00Z"
}
```

Request with `X-AIIndex-Intent: training` will receive 403 with denial receipt.

### Scenario 2: Allowlist Only

```json
{
  "version": "1.1",
  "publisher_domain": "example.com",
  "training_allowed": true,
  "training_allowlist": ["openai-gpt", "anthropic-claude"],
  "retrieval_allowed": true
}
```

Only listed clients can use training intent.

### Scenario 3: Rate Limiting by Client

```python
config = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    whitelist=["openai-gpt", "anthropic-claude"]  # No limits
)
```

Whitelisted clients bypass rate limits.

### Scenario 4: Fraud Detection + Auto-Block

```python
# Fraud triggers violation
alerts = await fraud_detector.check_receipt(...)

if alerts:
    for alert in alerts:
        should_block = await reputation.record_violation(
            client_id=client_id,
            violation_type=ViolationType.FRAUD_ATTEMPT,
            severity=alert.severity
        )
        if should_block:
            # Client auto-blocked after 5 violations
            print(f"Client {client_id} blocked")
```

## Monitoring

### Key Metrics to Track

```python
# Reputation scores
reputation = await reputation_system.get_reputation(client_id)
print(f"Score: {reputation.reputation_score}")

# Fraud alerts
alerts = await fraud_detector.get_alerts(min_severity=7, limit=100)
print(f"High-severity alerts: {len(alerts)}")

# Rate limit usage
# Check Redis keys: ratelimit:minute:*, ratelimit:hour:*
```

### Logging

All components log to standard Python logger:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("middleware")

# Will log:
# - Policy violations
# - Fraud attempts
# - Rate limit exceeded
# - Reputation changes
```

## Production Checklist

- [ ] Use Redis for rate limiting (not in-memory)
- [ ] Configure database for reputation/fraud tracking
- [ ] Set up private key for denial receipt signing
- [ ] Configure HTTPS for policy fetching
- [ ] Set appropriate rate limits for your use case
- [ ] Whitelist known good clients
- [ ] Monitor fraud alerts and take action
- [ ] Set up log aggregation (CloudWatch, Datadog, etc.)
- [ ] Configure alerts for high-severity fraud
- [ ] Implement admin endpoints authentication
- [ ] Regular backup of reputation data
- [ ] Document your policy and publish to /.well-known/

## Troubleshooting

### Policy not being enforced
- Check middleware order (policy should be last)
- Verify domain parameter is being passed
- Check policy URL is accessible
- Clear policy cache: `clear_policy_cache()`

### Rate limits not working
- Verify Redis connection
- Check client_id is being set
- Ensure middleware is added: `app.middleware("http")(rate_limiter)`
- Check Redis keys: `redis-cli keys "ratelimit:*"`

### Fraud detection too sensitive
- Adjust thresholds in FraudDetector
- Lower severity scores
- Whitelist trusted clients

### Reputation system blocking good clients
- Manually verify client: `await reputation.verify_client(client_id)`
- Clear violations: `await reputation.improve_reputation(client_id, 50.0)`
- Check violation history: `await reputation.get_violation_history(client_id)`

## Support

For issues and questions:
- GitHub: https://github.com/iaindex/iaindex
- Documentation: https://docs.iaindex.com
- Email: support@iaindex.com

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check [example_integration.py](example_integration.py) for complete examples
3. Customize thresholds and policies for your needs
4. Set up monitoring and alerting
5. Test thoroughly before production deployment
