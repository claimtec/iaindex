# IAIndex v2.0 - Production Deployment Checklist

**Based on:** QA Comprehensive Test Report
**Created:** October 18, 2025
**Owner:** DevOps / Deployment Team
**Estimated Time:** 14-20 hours (3 days)

---

## Overview

This checklist provides step-by-step instructions to deploy all pending changes and make IAIndex v2.0 production-ready.

**Current Blocker:** Work Stream 4 (Backend Enhancements) not deployed

**Goal:** Deploy all components, fix critical issues, achieve production readiness

---

## Pre-Deployment Checklist

### Environment Preparation

- [ ] **Access to Azure Portal**
  - Resource Group: `iaindex-rg`
  - Container App: `iaindex-api`
  - Subscription verified

- [ ] **Access to Supabase**
  - Admin credentials
  - Database connection string
  - Service role key

- [ ] **API Keys Ready**
  - [ ] Generate new SECRET_KEY: `openssl rand -hex 32`
  - [ ] SendGrid or Resend API key
  - [ ] Verify Anthropic API key
  - [ ] Verify OpenAI API key
  - [ ] Stripe keys (test mode for now)

- [ ] **DNS Access**
  - Access to iaindex.org DNS settings
  - Ready to create CNAME records

- [ ] **Development Environment**
  - Docker installed
  - Azure CLI installed
  - Git repository cloned
  - Database client (psql) installed

---

## Phase 1: Database Migrations (Est. 30-45 min)

### Step 1.1: Backup Current Database

```bash
# Create backup before migrations
pg_dump $SUPABASE_CONNECTION_STRING > backup_$(date +%Y%m%d).sql
```

**Verification:**
- [ ] Backup file created
- [ ] File size > 0 bytes
- [ ] File readable

### Step 1.2: Apply Security Fixes Migration

```bash
# Navigate to project root
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# Connect to Supabase and run migration
psql $SUPABASE_CONNECTION_STRING -f migrations/002_security_rls_fixes.sql
```

**Verification:**
- [ ] No error messages
- [ ] Output shows "ALTER TABLE" and "CREATE POLICY" statements
- [ ] RLS policies created successfully

### Step 1.3: Apply Subscriptions Migration

```bash
psql $SUPABASE_CONNECTION_STRING -f migrations/002_add_subscriptions.sql
```

**Verification:**
- [ ] Tables created: `users`, `subscriptions`, `payment_history`
- [ ] Check tables exist:
  ```sql
  \dt
  SELECT tablename FROM pg_tables WHERE schemaname = 'public';
  ```
- [ ] Verify RLS policies:
  ```sql
  SELECT tablename, policyname FROM pg_policies;
  ```

### Step 1.4: Apply Work Stream 4 Migration

```bash
psql $SUPABASE_CONNECTION_STRING -f migrations/work_stream_4_tables.sql
```

**Verification:**
- [ ] Additional tables created: `api_keys`, `usage_tracking`, `reports`
- [ ] Helper functions created: `get_active_subscription()`, `has_active_subscription()`
- [ ] Triggers created for `updated_at` fields
- [ ] All RLS policies active

### Step 1.5: Verify Database State

```sql
-- Connect to database
psql $SUPABASE_CONNECTION_STRING

-- List all tables
\dt

-- Expected tables:
-- receipts, publishers, ai_mentions, recommendations, attestations (Phase 1)
-- users, subscriptions, payment_history (Work Stream 2)
-- api_keys, usage_tracking, reports (Work Stream 4)

-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
-- All should show 't' for rowsecurity

-- Test basic query
SELECT COUNT(*) FROM users;
-- Should return 0 (or existing count)
```

**Verification:**
- [ ] All expected tables exist
- [ ] RLS enabled on all tables
- [ ] No errors when querying tables
- [ ] Foreign key constraints working

**⚠️ ROLLBACK PLAN:**
If errors occur:
```bash
# Restore from backup
psql $SUPABASE_CONNECTION_STRING < backup_YYYYMMDD.sql
```

---

## Phase 2: Backend Deployment (Est. 3-4 hours)

### Step 2.1: Update Dependencies

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/api

# Review requirements.txt to ensure all dependencies are listed
cat requirements.txt

# Expected new dependencies from Work Stream 4:
# - reportlab>=4.0.0
# - weasyprint>=60.0
# - sendgrid>=6.11.0
# - resend>=2.0.0
# - jinja2>=3.1.2
# - matplotlib>=3.8.0
# - plotly>=5.18.0
# - argon2-cffi>=23.1.0
# - email-validator>=2.1.0
```

**Verification:**
- [ ] All dependencies listed in requirements.txt
- [ ] No conflicting versions

### Step 2.2: Build Docker Image

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/api

# Build new image with tag
docker build -t iaindex-api:v1.2.0-workstream4 -f Dockerfile .

# Verify build succeeded
docker images | grep iaindex-api
```

**Verification:**
- [ ] Build completed without errors
- [ ] Image appears in `docker images`
- [ ] Image size reasonable (<500MB)

### Step 2.3: Test Locally (Optional but Recommended)

```bash
# Generate test SECRET_KEY
export SECRET_KEY=$(openssl rand -hex 32)

# Run container locally
docker run -p 8000:8000 \
  -e SECRET_KEY=$SECRET_KEY \
  -e SUPABASE_URL=$SUPABASE_URL \
  -e SUPABASE_KEY=$SUPABASE_KEY \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e SENDGRID_API_KEY=$SENDGRID_API_KEY \
  -e FROM_EMAIL=noreply@iaindex.org \
  iaindex-api:v1.2.0-workstream4

# In another terminal, test endpoints:
curl http://localhost:8000/health
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Should return 200 with token, not 404
```

**Verification:**
- [ ] Container starts without errors
- [ ] Health check returns 200
- [ ] `/v1/auth/register` returns 200 (not 404)
- [ ] No import errors in logs

### Step 2.4: Push to Azure Container Registry

```bash
# Login to Azure
az login

# Tag image for ACR (replace with your ACR name)
ACR_NAME="iaindexacr"  # Replace with actual name
docker tag iaindex-api:v1.2.0-workstream4 $ACR_NAME.azurecr.io/iaindex-api:v1.2.0

# Login to ACR
az acr login --name $ACR_NAME

# Push image
docker push $ACR_NAME.azurecr.io/iaindex-api:v1.2.0
```

**Verification:**
- [ ] Image pushed successfully
- [ ] Verify in Azure Portal: Container Registry → Repositories → iaindex-api
- [ ] Tag `v1.2.0` visible

### Step 2.5: Set Environment Variables

```bash
# Generate production SECRET_KEY
PROD_SECRET_KEY=$(openssl rand -hex 32)
echo "Save this SECRET_KEY securely: $PROD_SECRET_KEY"

# Set environment variables in Container App
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --set-env-vars \
    SECRET_KEY=$PROD_SECRET_KEY \
    SENDGRID_API_KEY=your-sendgrid-key \
    FROM_EMAIL=noreply@iaindex.org \
    FROM_NAME=IAIndex \
    APP_URL=https://app.iaindex.org \
    SITE_URL=https://scan.iaindex.org
```

**Verification:**
- [ ] Command completes without errors
- [ ] Verify in Azure Portal: Container App → Configuration → Environment Variables
- [ ] SECRET_KEY is set (value hidden)
- [ ] All email variables set

### Step 2.6: Update Container App Image

```bash
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --image $ACR_NAME.azurecr.io/iaindex-api:v1.2.0
```

**Verification:**
- [ ] Update command completes
- [ ] Container restarts automatically
- [ ] Check logs for errors:
  ```bash
  az containerapp logs show --name iaindex-api --resource-group iaindex-rg --tail 50
  ```

### Step 2.7: Verify Deployment

```bash
# Wait 2-3 minutes for deployment to stabilize

# Test health endpoint
curl https://api.iaindex.org/health

# Test new endpoints (should NOT return 404)
curl -X POST https://api.iaindex.org/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"qatest@example.com","password":"Test123!","full_name":"QA Test"}'

# Should return:
# {"access_token":"...", "refresh_token":"...", "user":{...}}

# Test protected endpoint (should return 401)
curl https://api.iaindex.org/v1/users/me
# Expected: {"error":"Invalid or missing authentication credentials","status_code":401}
```

**Verification:**
- [ ] Health check returns 200
- [ ] `/v1/auth/register` returns 200 with token
- [ ] `/v1/users/me` returns 401 (not 404)
- [ ] No 500 errors
- [ ] Response time acceptable

**⚠️ ROLLBACK PLAN:**
If deployment fails:
```bash
# Rollback to previous version
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --image $ACR_NAME.azurecr.io/iaindex-api:v1.1.0  # Previous tag
```

---

## Phase 3: Security Hardening (Est. 1 hour)

### Step 3.1: Verify Security Headers

```bash
# Check for security headers
curl -I https://api.iaindex.org/health | grep -i "x-"

# Expected headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

curl -I https://api.iaindex.org/health | grep -i "strict-transport"
# Expected: Strict-Transport-Security: max-age=31536000
```

**If headers are missing:**

1. Verify middleware is loaded in code:
   ```bash
   # Check main.py includes security middleware
   grep -n "SecurityHeadersMiddleware" apps/api/src/main.py
   # Should show line where middleware is added
   ```

2. Check Docker image includes middleware:
   ```bash
   docker run --rm iaindex-api:v1.2.0 \
     python -c "from src.middleware.security_headers import SecurityHeadersMiddleware; print('OK')"
   ```

3. If still missing, rebuild and redeploy with middleware verified

**Verification:**
- [ ] X-Content-Type-Options header present
- [ ] X-Frame-Options header present
- [ ] Strict-Transport-Security header present
- [ ] Content-Security-Policy header present

### Step 3.2: Test Rate Limiting

```bash
# Make 35 rapid requests to health endpoint
for i in {1..35}; do
  curl -s -o /dev/null -w "%{http_code}\n" https://api.iaindex.org/health
  sleep 0.1
done

# Should see some 429 responses after ~30 requests
```

**Verification:**
- [ ] Rate limiting triggers (429 response)
- [ ] Response includes Retry-After header
- [ ] Rate limit resets after waiting

### Step 3.3: Test Security Protections

```bash
# Test SQL injection protection
curl -X POST https://api.iaindex.org/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"' OR '1'='1"}'
# Expected: 400/422 or 501 (not 200)

# Test SSRF protection
curl -X POST https://api.iaindex.org/v1/schema/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"url":"http://169.254.169.254/latest/meta-data/","business_type":"test"}'
# Expected: 400/422 (URL rejected)
```

**Verification:**
- [ ] SQL injection blocked
- [ ] SSRF attempts blocked
- [ ] XSS payloads sanitized

### Step 3.4: Rotate API Keys (If Needed)

If any API keys were accidentally exposed:

```bash
# Rotate Anthropic key
az containerapp update --name iaindex-api --resource-group iaindex-rg \
  --set-env-vars ANTHROPIC_API_KEY=new-key

# Rotate OpenAI key
az containerapp update --name iaindex-api --resource-group iaindex-rg \
  --set-env-vars OPENAI_API_KEY=new-key

# Rotate Stripe keys
az containerapp update --name iaindex-api --resource-group iaindex-rg \
  --set-env-vars STRIPE_SECRET_KEY=new-key STRIPE_WEBHOOK_SECRET=new-secret
```

**Verification:**
- [ ] All API keys rotated if needed
- [ ] Old keys revoked in provider dashboards
- [ ] New keys working

---

## Phase 4: Performance Optimization (Est. 2-3 hours)

### Step 4.1: Enable Minimum Replicas

```bash
# Prevent scale-to-zero (eliminates cold starts)
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --min-replicas 1 \
  --max-replicas 10
```

**Verification:**
- [ ] Setting updated
- [ ] Container always has at least 1 instance running
- [ ] Check in Azure Portal: Container App → Scale

### Step 4.2: Add Database Indexes

```sql
-- Connect to database
psql $SUPABASE_CONNECTION_STRING

-- Add indexes on frequently queried columns
CREATE INDEX IF NOT EXISTS idx_publishers_verified ON publishers(verified);
CREATE INDEX IF NOT EXISTS idx_publishers_domain ON publishers(domain);
CREATE INDEX IF NOT EXISTS idx_receipts_created_at ON receipts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_mentions_website_id ON ai_mentions(website_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer_id ON subscriptions(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_created ON usage_tracking(user_id, created_at DESC);

-- Verify indexes created
\di
```

**Verification:**
- [ ] All indexes created successfully
- [ ] No duplicate indexes
- [ ] Query plan shows indexes being used

### Step 4.3: Test Performance Improvement

```bash
# Test response times (5 requests each)
for i in {1..5}; do
  curl -s -o /dev/null -w "Health: %{time_total}s\n" https://api.iaindex.org/health
  sleep 1
done

for i in {1..5}; do
  curl -s -o /dev/null -w "Publishers: %{time_total}s\n" https://api.iaindex.org/v1/publishers/verified-domains
  sleep 1
done

# Target: <0.5s average
```

**Verification:**
- [ ] Health endpoint: <500ms
- [ ] Publishers endpoint: <1000ms (down from 1900ms)
- [ ] No cold start delays

### Step 4.4: Monitor Resource Usage

```bash
# Check container resource usage
az containerapp show \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --query "properties.template.containers[0].resources"

# Check logs for memory/CPU warnings
az containerapp logs show \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --tail 100 | grep -i "memory\|cpu\|timeout"
```

**Verification:**
- [ ] CPU usage < 80%
- [ ] Memory usage < 80%
- [ ] No timeout errors
- [ ] No OOM (out of memory) errors

---

## Phase 5: Integration Testing (Est. 4-6 hours)

### Step 5.1: Test Authentication Flow

```bash
# Register new user
REGISTER_RESPONSE=$(curl -s -X POST https://api.iaindex.org/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"integration-test@example.com","password":"TestPass123!","full_name":"Integration Test"}')

echo $REGISTER_RESPONSE | jq .

# Extract access token
ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r .access_token)
echo "Access Token: $ACCESS_TOKEN"

# Test protected endpoint with token
curl -s https://api.iaindex.org/v1/users/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .

# Should return user profile
```

**Verification:**
- [ ] User registered successfully
- [ ] JWT token received
- [ ] Token works for protected endpoints
- [ ] User stored in database:
  ```sql
  SELECT email, plan, created_at FROM users WHERE email='integration-test@example.com';
  ```

### Step 5.2: Test AI Integrations

```bash
# Test schema generation (Claude)
curl -s -X POST https://api.iaindex.org/v1/schema/generate \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "business_name": "Test Business",
    "business_type": "LocalBusiness",
    "location": {
      "address": "123 Main St",
      "city": "Cape Town",
      "country": "South Africa"
    }
  }' | jq .

# Should return schema markup (JSON-LD)
```

**Verification:**
- [ ] Schema generation completes (may take 5-10 seconds)
- [ ] Valid JSON-LD schema returned
- [ ] Recommendations included
- [ ] No errors in response
- [ ] Anthropic API call succeeded (check logs)

```bash
# Test visibility checking (OpenAI)
# First, register a website
WEBSITE_RESPONSE=$(curl -s -X POST https://api.iaindex.org/v1/schema/websites \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "url": "https://example.com",
    "business_name": "Test Business",
    "business_type": "LocalBusiness",
    "keywords": ["test", "example"]
  }')

WEBSITE_ID=$(echo $WEBSITE_RESPONSE | jq -r .id)

# Check visibility
curl -s -X POST https://api.iaindex.org/v1/visibility/check \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "website_id": "'$WEBSITE_ID'",
    "queries": ["test business"],
    "platforms": ["chatgpt"]
  }' | jq .

# Should return visibility score and mentions
```

**Verification:**
- [ ] Website registered
- [ ] Visibility check completes
- [ ] Score returned (0-100)
- [ ] AI mentions extracted
- [ ] OpenAI API call succeeded

### Step 5.3: Test Stripe Integration

See `/STRIPE_TESTING_REPORT.md` for comprehensive testing.

**Quick Test:**

1. Open pricing page: http://localhost:3001/pricing (if scan tool deployed)
2. Click "Get Started" on a plan
3. Use test card: `4242 4242 4242 4242`
4. Verify checkout completes
5. Check database for subscription:
   ```sql
   SELECT * FROM subscriptions ORDER BY created_at DESC LIMIT 1;
   ```

**Verification:**
- [ ] Checkout session created
- [ ] Payment successful
- [ ] Webhook received
- [ ] Subscription created in database
- [ ] User plan updated

### Step 5.4: Test Email Delivery

```bash
# Configure SendGrid/Resend API key first
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --set-env-vars SENDGRID_API_KEY=your-real-key

# Test welcome email by registering new user
curl -X POST https://api.iaindex.org/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"your-real-email@example.com","password":"Test123!","full_name":"Email Test"}'

# Check inbox for welcome email
```

**Verification:**
- [ ] Email delivered within 1 minute
- [ ] Email properly formatted
- [ ] All links work
- [ ] Unsubscribe link present

### Step 5.5: Test PDF Report Generation

```bash
# Generate PDF report
curl -s -X POST https://api.iaindex.org/v1/reports/generate \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "website_id": "'$WEBSITE_ID'",
    "include_charts": true,
    "send_email": false
  }' | jq .

# Should return report URL
# Download and verify PDF opens correctly
```

**Verification:**
- [ ] PDF generated successfully
- [ ] PDF downloadable
- [ ] PDF contains visibility score
- [ ] Charts render correctly
- [ ] Recommendations included

---

## Phase 6: Frontend Deployment (Est. 4-6 hours)

### Step 6.1: Deploy Scan Tool

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/scan

# Install dependencies
npm install

# Set environment variables
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=https://api.iaindex.org
NEXT_PUBLIC_SITE_URL=https://scan.iaindex.org
NEXT_PUBLIC_APP_URL=https://app.iaindex.org
STRIPE_SECRET_KEY=your-stripe-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your-publishable-key
NEXT_PUBLIC_STRIPE_PRICE_STARTER=price_xxxxx
NEXT_PUBLIC_STRIPE_PRICE_PRO=price_xxxxx
NEXT_PUBLIC_STRIPE_PRICE_AGENCY=price_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
API_SECRET_KEY=your-api-secret
EOF

# Build
npm run build

# Test locally
npm run start
# Open http://localhost:3001
```

**Verification:**
- [ ] Build completes without errors
- [ ] App runs locally
- [ ] All pages load
- [ ] Forms work

**Deploy to Azure Static Web Apps:**

```bash
# Create static web app
az staticwebapp create \
  --name iaindex-scan \
  --resource-group iaindex-rg \
  --location "East US 2"

# Deploy (follow Azure SWA deployment guide)
# Or use GitHub Actions workflow
```

**Verification:**
- [ ] App deployed
- [ ] Accessible via temporary URL
- [ ] All pages load
- [ ] API calls work

### Step 6.2: Deploy Dashboard

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/dashboard

# Similar process as scan tool
npm install
# Configure .env.local
npm run build
npm run start

# Deploy to Azure Static Web Apps
az staticwebapp create \
  --name iaindex-dashboard \
  --resource-group iaindex-rg \
  --location "East US 2"
```

**Verification:**
- [ ] Dashboard deployed
- [ ] Login works
- [ ] User can register
- [ ] Dashboard displays correctly

### Step 6.3: Configure Custom Domains

**For scan.iaindex.org:**

1. In Azure Portal: Static Web Apps → iaindex-scan → Custom domains → Add
2. Choose "Custom domain on other DNS"
3. Add CNAME record in DNS:
   ```
   scan.iaindex.org → [generated-url].azurestaticapps.net
   ```
4. Verify domain
5. SSL certificate auto-provisions

**For app.iaindex.org:**

1. Same process for dashboard
2. Add CNAME:
   ```
   app.iaindex.org → [dashboard-url].azurestaticapps.net
   ```

**Verification:**
- [ ] DNS records propagated (check with `dig scan.iaindex.org`)
- [ ] HTTPS working
- [ ] SSL certificate valid
- [ ] Both domains accessible

---

## Phase 7: End-to-End Testing (Est. 2-3 hours)

### Step 7.1: Complete User Flow Test

**Test as new user:**

1. [ ] Visit https://scan.iaindex.org
2. [ ] Enter URL and click "Scan"
3. [ ] View results page
4. [ ] Enter email to receive PDF report
5. [ ] Receive email with PDF
6. [ ] Click "Upgrade" button
7. [ ] Select plan on pricing page
8. [ ] Complete Stripe checkout
9. [ ] Receive welcome email
10. [ ] Redirected to https://app.iaindex.org
11. [ ] Login to dashboard
12. [ ] Add website
13. [ ] Generate schema
14. [ ] Copy schema to website (manual)
15. [ ] Check visibility
16. [ ] View visibility report
17. [ ] Download PDF report
18. [ ] Access billing portal
19. [ ] Update payment method
20. [ ] Cancel subscription

**Verification:**
- [ ] All steps complete without errors
- [ ] Data persists across sessions
- [ ] Emails delivered
- [ ] PDFs generated correctly
- [ ] Payment processing works

### Step 7.2: Run Automated Test Suite

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# Run comprehensive QA test suite
python3 QA_COMPREHENSIVE_TEST_SUITE.py

# Expected: All tests PASS (or minimal warnings)
```

**Verification:**
- [ ] System health: PASS
- [ ] Authentication: PASS
- [ ] API endpoints: PASS
- [ ] Security: PASS
- [ ] Performance: <500ms average
- [ ] Error handling: PASS

### Step 7.3: Performance Testing

```bash
# Install k6 (load testing tool)
# brew install k6  # macOS
# choco install k6  # Windows

# Create simple load test
cat > loadtest.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 10 },  // Ramp up to 10 users
    { duration: '3m', target: 10 },  // Stay at 10 users
    { duration: '1m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests <1s
  },
};

export default function () {
  let res = http.get('https://api.iaindex.org/health');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
EOF

# Run load test
k6 run loadtest.js
```

**Verification:**
- [ ] All requests successful (0% failure rate)
- [ ] p95 < 1000ms
- [ ] p50 < 500ms
- [ ] No 500 errors

---

## Phase 8: Monitoring & Alerting (Est. 1-2 hours)

### Step 8.1: Configure Application Insights

```bash
# Enable Application Insights for Container App
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --enable-app-insights true
```

**Configure Alerts:**

1. In Azure Portal: Container App → Monitoring → Alerts → New alert rule
2. Create alerts for:
   - CPU usage > 80%
   - Memory usage > 80%
   - HTTP 5xx errors > 5 in 5 minutes
   - Response time p95 > 2s

**Verification:**
- [ ] Application Insights enabled
- [ ] Metrics flowing
- [ ] Alerts configured
- [ ] Test alerts trigger correctly

### Step 8.2: Set Up Sentry (Optional)

```bash
# Add Sentry for error tracking
# Sign up at sentry.io and get DSN

# Add to Container App environment
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --set-env-vars SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

**Verification:**
- [ ] Sentry configured
- [ ] Test error reported to Sentry
- [ ] Alerts configured

---

## Phase 9: Documentation & Handoff (Est. 1-2 hours)

### Step 9.1: Update Documentation

- [ ] Update `README.md` with production URLs
- [ ] Document environment variables
- [ ] Create runbook for common operations
- [ ] Document rollback procedures

### Step 9.2: Create Monitoring Dashboard

- [ ] Create custom Azure Dashboard
- [ ] Add key metrics:
  - Request rate
  - Error rate
  - Response times
  - Active users
  - Database connections
  - CPU/Memory usage

### Step 9.3: Team Handoff

- [ ] Document deployment process
- [ ] Share credentials securely
- [ ] Train support team
- [ ] Create incident response plan

---

## Phase 10: Production Launch (Est. 1 hour)

### Step 10.1: Final Checks

- [ ] All tests passing
- [ ] All endpoints responding
- [ ] Frontends accessible
- [ ] SSL certificates valid
- [ ] DNS propagated
- [ ] Monitoring active
- [ ] Backups configured

### Step 10.2: Launch Communications

- [ ] Announce internally
- [ ] Update status page
- [ ] Social media posts
- [ ] Email list notification
- [ ] Product Hunt submission (if applicable)

### Step 10.3: Post-Launch Monitoring

**First Hour:**
- [ ] Monitor error rates every 15 minutes
- [ ] Check response times
- [ ] Verify user registrations working
- [ ] Test payment flow

**First Day:**
- [ ] Review all logs
- [ ] Check for any errors
- [ ] Monitor user feedback
- [ ] Verify all emails delivered

**First Week:**
- [ ] Daily metric review
- [ ] Fix any issues immediately
- [ ] Optimize based on usage patterns
- [ ] Gather user feedback

---

## Rollback Procedures

### If Critical Issues Occur:

**Database Rollback:**
```bash
# Restore from backup
psql $SUPABASE_CONNECTION_STRING < backup_YYYYMMDD.sql
```

**Backend Rollback:**
```bash
# Rollback to previous image version
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --image $ACR_NAME.azurecr.io/iaindex-api:v1.1.0
```

**Frontend Rollback:**
```bash
# Revert to previous deployment in Azure Static Web Apps
# Via Portal: Deployments → Select previous version → Promote
```

**DNS Rollback:**
```bash
# Remove CNAME records or point to previous servers
# In DNS provider admin panel
```

---

## Success Criteria

### Deployment is successful when:

- [ ] **All API endpoints** return 200/401 (not 404)
- [ ] **Average response time** <500ms
- [ ] **Security headers** present in all responses
- [ ] **User registration** works end-to-end
- [ ] **Payment flow** completes successfully
- [ ] **Email delivery** functioning
- [ ] **Frontends** accessible via custom domains
- [ ] **SSL** working on all domains
- [ ] **Monitoring** active and alerting
- [ ] **QA test suite** passes with 0 failures

### Production readiness verified when:

- [ ] All items in this checklist complete
- [ ] No CRITICAL or HIGH severity bugs
- [ ] Performance targets met
- [ ] Security audit passes
- [ ] End-to-end user flows work
- [ ] Monitoring and alerting configured
- [ ] Team trained and ready
- [ ] Rollback procedures tested

---

## Contact & Support

**Checklist Created By:** QA Agent
**Based On:** QA Comprehensive Test Report
**Date:** October 18, 2025

**For Issues:**
- Review `/QA_COMPREHENSIVE_TEST_REPORT.md` for detailed findings
- Check logs: `az containerapp logs show --name iaindex-api --resource-group iaindex-rg --tail 100`
- Contact DevOps team
- Escalate critical issues immediately

---

**DEPLOYMENT CHECKLIST VERSION: 1.0**
**STATUS: READY FOR EXECUTION**

---

## Appendix: Quick Reference Commands

### Database:
```bash
# Connect to database
psql $SUPABASE_CONNECTION_STRING

# List tables
\dt

# Check RLS policies
SELECT tablename, policyname FROM pg_policies;

# Backup database
pg_dump $SUPABASE_CONNECTION_STRING > backup.sql
```

### Docker:
```bash
# Build image
docker build -t iaindex-api:v1.2.0 .

# Test locally
docker run -p 8000:8000 -e SECRET_KEY=test iaindex-api:v1.2.0

# Push to ACR
docker push $ACR_NAME.azurecr.io/iaindex-api:v1.2.0
```

### Azure:
```bash
# Update container app
az containerapp update --name iaindex-api --resource-group iaindex-rg --image $IMAGE

# Set environment variable
az containerapp update --name iaindex-api --resource-group iaindex-rg --set-env-vars KEY=value

# View logs
az containerapp logs show --name iaindex-api --resource-group iaindex-rg --tail 50

# Scale
az containerapp update --name iaindex-api --resource-group iaindex-rg --min-replicas 1 --max-replicas 10
```

### Testing:
```bash
# Health check
curl https://api.iaindex.org/health

# Test endpoint
curl -X POST https://api.iaindex.org/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Run QA suite
python3 QA_COMPREHENSIVE_TEST_SUITE.py
```

---

**END OF DEPLOYMENT CHECKLIST**
