# AIIndex v1.1 Deployment Plan

**Date**: 2025-10-13
**Version**: 1.1
**Environment**: Staging → Production

---

## 🎯 Deployment Overview

**Objective**: Deploy AIIndex v1.1 to production with zero downtime and full backward compatibility

**Strategy**: Staged rollout with comprehensive testing
1. Staging deployment + testing
2. Database migration (with rollback plan)
3. API deployment
4. Dashboard deployment
5. Documentation deployment
6. Smoke tests
7. Production cutover
8. Monitoring

**Estimated Duration**: 2-3 hours
**Rollback Time**: <15 minutes

---

## ✅ Pre-Deployment Checklist

### Environment Configuration
- [ ] **Supabase**: Database URL, API keys validated
- [ ] **Redis**: Connection string validated (for rate limiting)
- [ ] **AWS S3**: Bucket configured for snapshots
- [ ] **Cloudflare**: Account ID and API token (for rendering)
- [ ] **OpenAI**: API key (for embeddings - optional)
- [ ] **Pinecone/Weaviate**: Vector DB configured (optional)
- [ ] **Environment Variables**: All `.env` files validated

### Code Validation
- [ ] **Git Status**: All changes committed
- [ ] **Version Tags**: v1.1.0 tag created
- [ ] **Dependencies**: All packages installed and locked
- [ ] **Build Tests**: All builds successful locally
- [ ] **Linting**: No errors in ESLint/Pylint
- [ ] **Type Checking**: TypeScript compilation successful

### Database Preparation
- [ ] **Backup Created**: Full database backup taken
- [ ] **Migration Scripts**: SQL scripts validated
- [ ] **Rollback Plan**: Documented and tested
- [ ] **Test Database**: Migration tested on copy

### External Services
- [ ] **DNS**: Records ready for updates
- [ ] **SSL Certificates**: Valid and not expiring
- [ ] **CDN**: Cloudflare cache cleared
- [ ] **Monitoring**: Sentry/DataDog configured
- [ ] **Status Page**: Ready to update

---

## 📋 Deployment Steps

### Phase 1: Database Migration (15-20 minutes)

#### Step 1.1: Backup Database
```bash
# Create timestamped backup
export BACKUP_FILE="aiindex_backup_$(date +%Y%m%d_%H%M%S).sql"
pg_dump $DATABASE_URL > $BACKUP_FILE

# Verify backup
echo "Backup size: $(du -h $BACKUP_FILE)"
echo "Backup location: $(pwd)/$BACKUP_FILE"

# Upload to S3 for safety
aws s3 cp $BACKUP_FILE s3://aiindex-backups/$(date +%Y-%m-%d)/
```

**Expected Output**: Backup file ~100-500MB depending on data volume

#### Step 1.2: Test Migration on Staging
```bash
# Connect to staging database
export STAGING_DB_URL="postgresql://..."

# Run migration
psql $STAGING_DB_URL < migrations/v1.0-to-v1.1.sql

# Verify migration
psql $STAGING_DB_URL -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('bot_reputation', 'violation_records', 'fraud_detection_logs', 'merkle_timestamps');"

# Check new columns
psql $STAGING_DB_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name='publishers' AND column_name IN ('c2pa_enabled', 'embeddings_enabled', 'render_mode', 'policy_config');"
```

**Expected Output**: 4 new tables, 4 new columns in publishers table

#### Step 1.3: Run Migration on Production
```bash
# Enable maintenance mode (optional)
# curl -X POST https://api.aiindex.org/maintenance -H "Authorization: Bearer $ADMIN_TOKEN"

# Run migration with timing
echo "Starting migration at $(date)"
time psql $DATABASE_URL < migrations/v1.0-to-v1.1.sql
echo "Completed migration at $(date)"

# Verify migration
psql $DATABASE_URL -c "SELECT COUNT(*) FROM bot_reputation;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM publishers WHERE c2pa_enabled IS NOT NULL;"
```

**Expected Output**: Migration completes in <30 seconds, all tables and columns created

**Rollback Plan**:
```bash
# If migration fails, restore from backup
psql $DATABASE_URL < $BACKUP_FILE
```

---

### Phase 2: API Deployment (20-30 minutes)

#### Step 2.1: Build and Test API Locally
```bash
cd apps/api

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Build Docker image (if using Docker)
docker build -t aiindex-api:v1.1 .

# Test locally
docker run -p 8000:8000 --env-file .env aiindex-api:v1.1
curl http://localhost:8000/health
```

**Expected Output**: All tests pass, health check returns 200

#### Step 2.2: Deploy to Staging
```bash
# Using Fly.io
cd apps/api

# Copy production env (with staging database)
cp .env.production .env.staging
# Edit .env.staging to use staging database URL

# Deploy to staging
fly deploy --config fly.staging.toml --env-file .env.staging

# Verify deployment
fly status --app aiindex-api-staging
curl https://aiindex-api-staging.fly.dev/health
curl https://aiindex-api-staging.fly.dev/v1/verified-domains
```

**Expected Output**: Deployment successful, health check returns 200

#### Step 2.3: Smoke Test Staging API
```bash
# Test policy enforcement
curl -X POST https://aiindex-api-staging.fly.dev/v1/receipts/ingest \
  -H "Content-Type: application/json" \
  -H "X-AIIndex-Client-ID: test-client" \
  -H "X-AIIndex-Intent: training" \
  -d '{
    "receipt_id": "test_001",
    "publisher_domain": "example.com",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'

# Should return 200 or 403 depending on policy

# Test version negotiation
curl -I https://aiindex-api-staging.fly.dev/v1/verified-domains \
  -H "X-AIIndex-Version: v1.1"

# Should return X-AIIndex-Version: v1.1 header

# Test new endpoints
curl https://aiindex-api-staging.fly.dev/v1/verify-badge?domain=example.com
```

**Expected Output**: All endpoints respond correctly

#### Step 2.4: Deploy to Production
```bash
# Deploy to production
fly deploy --config fly.toml --env-file .env.production

# Verify deployment
fly status --app aiindex-api
curl https://api.aiindex.org/health

# Check logs
fly logs --app aiindex-api
```

**Expected Output**: Zero downtime deployment, health check passes

---

### Phase 3: Dashboard Deployment (15-20 minutes)

#### Step 3.1: Build and Test Dashboard Locally
```bash
cd apps/web

# Install dependencies
npm install

# Build
npm run build

# Test build
npm run start
# Open http://localhost:3000
```

**Expected Output**: Build successful, all pages load

#### Step 3.2: Deploy to Staging (Vercel)
```bash
cd apps/web

# Deploy to staging
vercel --env=staging

# Verify deployment
curl https://aiindex-staging.vercel.app/
curl https://aiindex-staging.vercel.app/dashboard/policy
```

**Expected Output**: Staging deployment successful

#### Step 3.3: Test Dashboard Features
```bash
# Manual testing checklist:
# 1. Login works
# 2. Dashboard overview loads
# 3. New policy page renders
# 4. New compliance page renders
# 5. New provenance page renders
# 6. Analytics page shows new sections
# 7. Settings page works
# 8. Badge generator works
# 9. Dark mode works
# 10. Mobile responsive
```

#### Step 3.4: Deploy to Production
```bash
# Deploy to production
vercel --prod

# Verify deployment
curl https://aiindex.org/
curl https://aiindex.org/dashboard/policy

# Check Vercel logs
vercel logs
```

**Expected Output**: Production deployment successful

---

### Phase 4: Documentation Deployment (10-15 minutes)

#### Step 4.1: Build Documentation
```bash
cd apps/docs

# Install dependencies
npm install

# Build
npm run build

# Test build locally
npm run serve
# Open http://localhost:3002
```

**Expected Output**: Build successful, all docs pages load

#### Step 4.2: Deploy to Netlify
```bash
cd apps/docs

# Deploy to production
netlify deploy --prod --dir=build

# Verify deployment
curl https://docs.aiindex.org/
curl https://docs.aiindex.org/intro
curl https://docs.aiindex.org/publishers/domain-verification
```

**Expected Output**: Documentation site live

---

### Phase 5: End-to-End Testing (30-45 minutes)

#### Step 5.1: Run Automated Test Suite
```bash
cd tests/e2e

# Install dependencies
pip install -r requirements.txt

# Set environment to staging
export API_BASE_URL="https://aiindex-api-staging.fly.dev"
export WEB_BASE_URL="https://aiindex-staging.vercel.app"

# Run all tests
pytest -v --tb=short

# Run specific test suites
pytest test_policy_enforcement.py -v
pytest test_rendering.py -v
pytest test_embeddings.py -v
pytest test_provenance.py -v
pytest test_full_flow.py -v
```

**Expected Output**: 32 tests pass, 0 failures

#### Step 5.2: Manual Integration Tests

**Test 1: Policy Enforcement**
```bash
# Test training blocked
curl -X POST https://api.aiindex.org/v1/receipts/ingest \
  -H "Content-Type: application/json" \
  -H "X-AIIndex-Client-ID: test-client" \
  -H "X-AIIndex-Intent: training" \
  -d '{
    "receipt_id": "test_training_001",
    "publisher_domain": "test-blocked.com",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'

# Expected: HTTP 403 with denial receipt
```

**Test 2: Retrieval Allowed**
```bash
# Test retrieval allowed
curl -X POST https://api.aiindex.org/v1/receipts/ingest \
  -H "Content-Type: application/json" \
  -H "X-AIIndex-Client-ID: test-client" \
  -H "X-AIIndex-Intent: retrieval" \
  -d '{
    "receipt_id": "test_retrieval_001",
    "publisher_domain": "test-allowed.com",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'

# Expected: HTTP 200 with success response
```

**Test 3: Version Negotiation**
```bash
# Test v1.1 features
curl -I https://api.aiindex.org/v1/verified-domains \
  -H "X-AIIndex-Version: v1.1"

# Expected: X-AIIndex-Version: v1.1 in response headers
```

**Test 4: Dashboard Policy Page**
```
# Manual browser test:
1. Navigate to https://aiindex.org/dashboard/policy
2. Toggle "Block Training" ON
3. Click "Save Policy Settings"
4. Verify policy JSON preview updates
5. Check that policy is saved (refresh page)
```

**Test 5: Bot Reputation**
```bash
# Make 6 invalid requests from same client (should trigger block)
for i in {1..6}; do
  curl -X POST https://api.aiindex.org/v1/receipts/ingest \
    -H "Content-Type: application/json" \
    -H "X-AIIndex-Client-ID: bad-actor" \
    -d '{
      "receipt_id": "bad_'$i'",
      "publisher_domain": "protected.com",
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    }'
done

# Expected: First 5 return 403, 6th should show client blocked
```

---

### Phase 6: Plugin Testing (1-2 hours)

#### Test 6.1: WordPress Plugin
```bash
# Install on test WordPress site
wp plugin install /path/to/wp-plugin --activate

# Verify admin page loads
# Navigate to WordPress Admin > AIIndex

# Test policy toggle
# 1. Go to Policy Controls tab
# 2. Toggle "Block Training" ON
# 3. Click Save
# 4. Check ai-index.json endpoint

curl https://test-wp-site.com/ai-index.json | jq '.policy.training'
# Expected: "block"

# Test verification badge shortcode
# Add [aiindex_badge show_verification="true"] to page
# Visit page and verify badge displays
```

#### Test 6.2: Shopify App (if applicable)
```bash
# Test in Shopify development store
# 1. Install app
# 2. Navigate to Apps > AI Index
# 3. Go to Policy Controls tab
# 4. Toggle policies
# 5. Save
# 6. Check store's ai-index.json

curl https://test-shopify-store.myshopify.com/ai-index.json | jq '.policy'
```

#### Test 6.3: Other Plugins (Quick Smoke Tests)
```bash
# For each plugin (Webflow, Bubble, Wix, Squarespace, Framer, Ghost):
# 1. Open policy-config-v1.1.html in browser
# 2. Toggle policies
# 3. Click "Save Policy Settings"
# 4. Verify localStorage saved
# 5. Copy embed code
# 6. Test on sample site
```

---

### Phase 7: AI Connector Testing (30-45 minutes)

#### Test 7.1: LangChain Connector
```bash
cd packages/lc-aiindex-reader
npm install
npm run build

# Create test script
cat > test-connector.ts << 'EOF'
import { AIIndexReader } from './src';

async function test() {
  const reader = new AIIndexReader({
    clientId: 'test-langchain',
    intent: 'retrieval',
    respectPolicyBlocks: true,
  });

  try {
    const doc = await reader.fetch('example.com');
    console.log('Success:', doc.domain);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

test();
EOF

npx tsx test-connector.ts
```

**Expected Output**: Fetches document or handles 403 gracefully

#### Test 7.2: LlamaIndex Connector
```bash
cd packages/li-aiindex-reader
pip install -e .

# Create test script
cat > test_connector.py << 'EOF'
from aiindex_llama import AIIndexReader

reader = AIIndexReader(
    client_id="test-llamaindex",
    intent="retrieval",
    respect_policy_blocks=True,
)

try:
    doc = reader.fetch("example.com")
    print(f"Success: {doc.domain}")
except Exception as e:
    print(f"Error: {str(e)}")
EOF

python test_connector.py
```

**Expected Output**: Fetches document or handles PolicyViolationError

---

### Phase 8: Monitoring & Alerting (15-20 minutes)

#### Step 8.1: Verify Monitoring Endpoints
```bash
# Health checks
curl https://api.aiindex.org/health
curl https://aiindex.org/
curl https://docs.aiindex.org/

# Check response times
time curl https://api.aiindex.org/v1/verified-domains

# Check error rates
curl https://api.aiindex.org/metrics
```

#### Step 8.2: Configure Alerts (if using Sentry/DataDog)
```bash
# Verify Sentry DSN configured
echo $SENTRY_DSN

# Test error tracking
curl -X POST https://api.aiindex.org/test-error

# Check Sentry dashboard for error
```

#### Step 8.3: Set Up Uptime Monitoring
```bash
# Add endpoints to UptimeRobot or similar:
# 1. https://api.aiindex.org/health (every 5 min)
# 2. https://aiindex.org/ (every 5 min)
# 3. https://docs.aiindex.org/ (every 15 min)

# Configure alerts:
# - Email on downtime
# - Slack notification on downtime
# - SMS for critical failures (optional)
```

---

### Phase 9: Production Cutover (15-20 minutes)

#### Step 9.1: DNS Updates (if needed)
```bash
# Verify DNS records
dig api.aiindex.org
dig aiindex.org
dig docs.aiindex.org

# If using Cloudflare, update DNS via API or dashboard
# Verify propagation
dig +trace api.aiindex.org
```

#### Step 9.2: Enable Production Traffic
```bash
# If using feature flags, enable v1.1 features
# If using canary deployment, increase traffic to 100%

# Verify production endpoints
curl https://api.aiindex.org/health
curl https://api.aiindex.org/v1/verified-domains \
  -H "X-AIIndex-Version: v1.1"
```

#### Step 9.3: Post-Deployment Verification
```bash
# Run smoke tests on production
./scripts/smoke-tests.sh production

# Check logs for errors
fly logs --app aiindex-api | grep ERROR
vercel logs --app aiindex-web | grep error

# Monitor metrics
# - Response times: <200ms p95
# - Error rate: <0.1%
# - CPU usage: <70%
# - Memory usage: <80%
```

---

### Phase 10: Final Validation (10-15 minutes)

#### Step 10.1: End-User Flow Test
```bash
# Publisher flow:
# 1. Sign up at aiindex.org
# 2. Install WordPress plugin
# 3. Configure policy (block training)
# 4. Verify domain
# 5. Check dashboard shows policy active

# AI Developer flow:
# 1. Install SDK: npm install @aiindex/sdk
# 2. Fetch policy for test domain
# 3. Respect policy (get 403 if training blocked)
# 4. Send receipt
# 5. Verify receipt appears in publisher dashboard
```

#### Step 10.2: Performance Baseline
```bash
# Run load test (Apache Bench)
ab -n 1000 -c 10 https://api.aiindex.org/v1/verified-domains

# Expected:
# - Requests per second: >500
# - Mean response time: <100ms
# - No failed requests

# Check database performance
psql $DATABASE_URL -c "
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"
```

---

## 🚨 Rollback Plan

If critical issues are discovered:

### Immediate Rollback (5-10 minutes)
```bash
# 1. Revert API deployment
fly deploy --app aiindex-api --image aiindex-api:v1.0

# 2. Revert dashboard deployment
vercel rollback --app aiindex-web

# 3. Revert database (if needed - use with caution)
psql $DATABASE_URL < $BACKUP_FILE

# 4. Update status page
curl -X POST https://status.aiindex.org/incidents \
  -d "Rolling back to v1.0 due to critical issue"

# 5. Notify team
# Send Slack message to #engineering
```

### Rollback Decision Criteria
- **Critical**: Roll back immediately
  - API error rate >5%
  - Database corruption
  - Security vulnerability discovered
  - Payment processing broken

- **Major**: Fix forward or roll back within 1 hour
  - Feature not working as expected
  - Performance degradation >2x
  - Dashboard UI broken

- **Minor**: Fix forward
  - UI cosmetic issues
  - Non-critical feature bugs
  - Documentation errors

---

## 📊 Success Criteria

**Deployment is considered successful when**:
- ✅ All automated tests pass (32/32)
- ✅ Health checks return 200 on all services
- ✅ Manual smoke tests pass
- ✅ Response times within SLA (<200ms p95)
- ✅ Error rate <0.1%
- ✅ No critical bugs reported
- ✅ Monitoring and alerts configured
- ✅ Documentation updated
- ✅ Team notified of completion

---

## 📝 Post-Deployment Tasks

**Within 24 hours**:
- [ ] Monitor error logs for anomalies
- [ ] Review performance metrics
- [ ] Check user feedback channels
- [ ] Update changelog
- [ ] Announce v1.1 launch (press release, social media)
- [ ] Send email to beta users

**Within 1 week**:
- [ ] Publish case studies
- [ ] Create video tutorials
- [ ] Host AMA or office hours
- [ ] Gather feedback from early adopters
- [ ] Plan v1.2 roadmap

---

## 📞 Emergency Contacts

**On-Call Engineer**: [Your contact]
**Database Admin**: [Contact]
**DevOps**: [Contact]
**Product Lead**: [Contact]

**Emergency Procedures**:
- Slack: #aiindex-incidents
- PagerDuty: aiindex.pagerduty.com
- Status Page: status.aiindex.org

---

## ✅ Deployment Sign-Off

**Pre-Deployment Checklist Completed**: ____________________

**Deployment Started**: ______________ (Date/Time)

**Deployment Completed**: ______________ (Date/Time)

**Sign-Off**: ____________________

**Notes**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Ready to deploy!** Let's start with Phase 1: Database Migration.
