# Migration Guide: AIIndex v1.0 to v1.1

## Overview

This guide covers the upgrade path from AIIndex v1.0 to v1.1. The v1.1 release adds significant new features while maintaining backward compatibility with v1.0 clients.

## What's New in v1.1

### Core Features

1. **Enhanced Policy Control**
   - Granular training/retrieval policies
   - Conditional access with `require_offer`
   - Per-client allowlists and blocklists

2. **Bot Reputation System**
   - Automatic tracking of client behavior
   - Violation detection and auto-blocking
   - Verified client registry

3. **Fraud Detection**
   - Content hash validation
   - Clock skew detection
   - Signature reuse prevention
   - Batch fraud detection

4. **Render Fallback**
   - Edge and local rendering for dynamic content
   - Cached snapshots with ETag support
   - S3 storage integration

5. **Vector Embeddings** (Optional)
   - Pre-computed semantic search vectors
   - Multiple model support
   - Export in JSON, Parquet, NumPy formats

6. **C2PA Provenance** (Optional)
   - Content Credentials integration
   - Cryptographic proof of authenticity
   - Blockchain anchoring via Merkle trees

## Backward Compatibility

### v1.0 Compatibility Promise

- All v1.0 `ai-index.json` files remain valid
- v1.0 clients can continue accessing v1.1 publishers
- Existing `access_policy` field automatically migrated to `policy`
- No breaking changes to core schema

### Version Negotiation

Clients can request specific versions via headers:

```http
X-AIIndex-Version: 1.0
```

Publishers will serve appropriate format based on client version.

## Migration Steps

### Step 1: Database Migration

Run the SQL migration script to add new tables and columns:

```bash
# Backup your database first!
pg_dump iaindex_db > backup_$(date +%Y%m%d).sql

# Run migration
psql iaindex_db < migrations/v1.0-to-v1.1.sql
```

**What this does:**
- Adds columns to `publishers` table (c2pa_enabled, embeddings_enabled, render_mode, policy_config)
- Creates `bot_reputation` table
- Creates `violation_records` table
- Creates `fraud_detection_logs` table
- Creates `merkle_timestamps` table
- Backfills default policies (allow-all)
- Adds indexes for performance

**Estimated time:** 2-5 minutes depending on database size

### Step 2: Migrate AI Index Files

Migrate your `ai-index.json` files to v1.1 format:

```bash
# Single file
python3 migrations/migrate-ai-index.py /path/to/ai-index.json

# All files in directory (recursive)
python3 migrations/migrate-ai-index.py /path/to/publishers --recursive

# Dry run (preview changes)
python3 migrations/migrate-ai-index.py /path/to/publishers --dry-run --recursive
```

**What this does:**
- Updates `version` to "1.1"
- Migrates `access_policy` to new `policy` structure
- Adds `receipts` section
- Adds `render_fallback` section
- Creates backup files (.json.bak)
- Preserves all existing v1.0 fields

**Estimated time:** < 1 second per file

### Step 3: Generate Policy Files

Generate `.well-known/aiindex-policy.json` for fast policy access:

```bash
# Single publisher
python3 migrations/generate-well-known.py /path/to/ai-index.json

# All publishers
python3 migrations/generate-well-known.py /path/to/publishers --recursive
```

**What this does:**
- Extracts policy, receipts, rate limits
- Creates `.well-known/aiindex-policy.json`
- Validates against schema

**Estimated time:** < 1 second per file

### Step 4: Update Application Code

Update your application to use v1.1 features:

#### Python Example

```python
from iaindex.middleware import (
    policy_enforcement_middleware,
    get_reputation_system,
    get_fraud_detector
)

# Add middleware to FastAPI app
app.add_middleware(policy_enforcement_middleware)

# Get reputation system
reputation = get_reputation_system(db_client)

# Check if client is allowed
allowed, reason = await reputation.is_allowed(client_id)

# Get fraud detector
fraud = get_fraud_detector(db_client)

# Check receipt for fraud
alerts = await fraud.check_receipt(
    receipt_id=receipt_id,
    signature=signature,
    timestamp=timestamp,
    client_id=client_id
)
```

#### TypeScript/Node.js Example

```typescript
import { PolicyEnforcer, BotReputationSystem } from '@aiindex/middleware';

// Initialize systems
const enforcer = new PolicyEnforcer(db);
const reputation = new BotReputationSystem(db);

// Enforce policy
const result = await enforcer.enforce(request);
if (!result.allowed) {
  return result.denialReceipt;
}

// Check reputation
const clientReputation = await reputation.getReputation(clientId);
if (clientReputation.status === 'blocked') {
  return forbidden();
}
```

### Step 5: Deploy Changes

1. **Update environment variables:**

```bash
# .env
AIINDEX_VERSION=1.1
ENABLE_BOT_REPUTATION=true
ENABLE_FRAUD_DETECTION=true
ENABLE_RENDER_FALLBACK=false  # Optional
ENABLE_EMBEDDINGS=false       # Optional
ENABLE_C2PA=false             # Optional
```

2. **Deploy application updates:**

```bash
# Deploy API service
docker-compose up -d api

# Restart workers
docker-compose restart worker
```

3. **Verify deployment:**

```bash
# Check version
curl https://api.aiindex.org/version

# Check policy endpoint
curl https://yourdomain.com/.well-known/aiindex-policy.json

# Check health
curl https://api.aiindex.org/health
```

### Step 6: Run Tests

Run end-to-end tests to verify migration:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all E2E tests
pytest tests/e2e/ -v

# Run specific test suites
pytest tests/e2e/test_policy_enforcement.py -v
pytest tests/e2e/test_rendering.py -v
pytest tests/e2e/test_embeddings.py -v
pytest tests/e2e/test_provenance.py -v
pytest tests/e2e/test_full_flow.py -v
```

**Expected results:**
- All policy enforcement tests pass
- Bot reputation tracking works
- Fraud detection catches violations
- Receipts appear in dashboard

## Breaking Changes

**None!** v1.1 is fully backward compatible with v1.0.

However, note the following deprecations:

### Deprecated (Still Supported)

- `access_policy` - Use `policy` instead (auto-migrated)
- Old receipt webhook format - v1.1 format preferred

These will continue working but are discouraged for new implementations.

## New Features (Optional)

### Enable Render Fallback

For publishers with dynamic content (SPAs):

```bash
# Configure render mode
curl -X PATCH https://api.aiindex.org/publishers/yourdomain.com/config \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "render_fallback": {
      "mode": "edge",
      "ttl": 3600
    }
  }'

# Render pages
curl -X POST https://api.aiindex.org/publishers/yourdomain.com/render \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "url": "https://yourdomain.com/dynamic-page",
    "update_index": true
  }'
```

### Enable Embeddings

For verified publishers wanting semantic search:

```bash
# Build embeddings
curl -X POST https://api.aiindex.org/publishers/yourdomain.com/embeddings/build \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "text-embedding-ada-002"
  }'

# Query will be available at:
# GET https://yourdomain.com/.well-known/embeddings.json
```

### Enable C2PA Provenance

For publishers wanting content authenticity:

```bash
# Generate C2PA manifest
curl -X POST https://api.aiindex.org/publishers/yourdomain.com/c2pa/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "asset_url": "https://yourdomain.com/article",
    "asset_type": "article"
  }'
```

## Rollback Procedure

If you need to rollback to v1.0:

### Step 1: Restore Database

```bash
# Restore from backup
psql iaindex_db < backup_YYYYMMDD.sql
```

### Step 2: Restore AI Index Files

```bash
# Restore from .bak files
find /path/to/publishers -name "*.json.bak" -exec sh -c 'mv "$1" "${1%.bak}"' _ {} \;
```

### Step 3: Revert Application Code

```bash
# Checkout previous version
git checkout v1.0.x

# Redeploy
docker-compose up -d
```

### Step 4: Verify Rollback

```bash
# Check version
curl https://api.aiindex.org/version
# Should return 1.0
```

## Performance Considerations

### Database Indexes

v1.1 adds several indexes for performance. If your database is large (>1M receipts), consider:

```sql
-- Add indexes concurrently to avoid downtime
CREATE INDEX CONCURRENTLY idx_bot_reputation_client ON bot_reputation(client_id);
CREATE INDEX CONCURRENTLY idx_fraud_logs_detected ON fraud_detection_logs(detected_at DESC);
```

### Cache Warming

After migration, warm caches for better performance:

```bash
# Warm policy cache
curl https://yourdomain.com/.well-known/aiindex-policy.json

# Warm reputation cache (if using Redis)
redis-cli FLUSHDB
```

### Rate Limiting

v1.1 adds more sophisticated rate limiting. Update your Redis configuration:

```yaml
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

## Monitoring

Monitor these new metrics after migration:

- **Bot Reputation:**
  - `aiindex.reputation.status` (by status)
  - `aiindex.reputation.violations` (total)
  - `aiindex.reputation.blocked` (blocked clients)

- **Fraud Detection:**
  - `aiindex.fraud.alerts` (by type)
  - `aiindex.fraud.severity` (average)
  - `aiindex.fraud.blocked_requests`

- **Policy Enforcement:**
  - `aiindex.policy.denials` (by reason)
  - `aiindex.policy.allowed` (total)
  - `aiindex.policy.cache_hits`

## Support

### Troubleshooting

**Issue:** Migration fails with foreign key constraint error

**Solution:** Ensure database is backed up and no active transactions. Run migration in a transaction:

```sql
BEGIN;
-- migration SQL
COMMIT;
```

**Issue:** Policy files not generating

**Solution:** Ensure `.well-known` directory exists and is writable:

```bash
mkdir -p /path/to/publisher/.well-known
chmod 755 /path/to/publisher/.well-known
```

**Issue:** Tests fail with connection refused

**Solution:** Ensure API server is running on correct port:

```bash
# Check API server
curl http://localhost:3000/health

# Update test configuration
export API_BASE_URL=http://localhost:3000
```

### Getting Help

- **Documentation:** https://docs.aiindex.org/migration
- **GitHub Issues:** https://github.com/aiindex/aiindex/issues
- **Discord:** https://discord.gg/aiindex
- **Email:** support@aiindex.org

## Changelog

### v1.1.0 (2025-10-13)

**Added:**
- Enhanced policy control (training/retrieval separation)
- Bot reputation system
- Fraud detection system
- Render fallback for dynamic content
- Vector embeddings support (optional)
- C2PA provenance integration (optional)
- Merkle tree anchoring
- `.well-known/aiindex-policy.json` endpoint

**Changed:**
- `access_policy` deprecated in favor of `policy`
- Receipt format enhanced with additional metadata
- Dashboard includes fraud alerts and reputation stats

**Fixed:**
- Rate limiting edge cases
- Receipt validation performance
- Cache invalidation issues

**Deprecated:**
- `access_policy` field (use `policy`)
- Legacy receipt webhook format

**Security:**
- Enhanced signature verification
- Fraud detection for tampered receipts
- Clock skew detection
- Signature reuse prevention

## Migration Checklist

- [ ] Backup database
- [ ] Run database migration SQL
- [ ] Verify new tables created
- [ ] Migrate ai-index.json files
- [ ] Generate policy files
- [ ] Update application code
- [ ] Update environment variables
- [ ] Deploy application changes
- [ ] Run E2E tests
- [ ] Verify dashboard shows new data
- [ ] Monitor logs for errors
- [ ] Update documentation
- [ ] Notify users of new features

## Timeline

**Recommended migration timeline:**

- **Week 1:** Test migration in staging environment
- **Week 2:** Monitor staging, fix issues
- **Week 3:** Migrate production database
- **Week 4:** Deploy application changes
- **Week 5:** Monitor production, enable optional features

**Estimated total time:** 2-4 hours for typical deployment

## Conclusion

AIIndex v1.1 brings powerful new features for content control, fraud prevention, and provenance tracking. The migration is straightforward and fully backward compatible.

For questions or issues during migration, please reach out to the AIIndex team.

Happy migrating! 🚀
