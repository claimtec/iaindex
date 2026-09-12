# IAIndex Security Deployment - Quick Start Guide

**CRITICAL: Follow these steps before deploying to production**

---

## Step 1: Generate and Set SECRET_KEY (5 minutes)

### Generate Secure Key:
```bash
# Generate 64-character hex key
openssl rand -hex 32
```

### Set in Azure Container App:
```bash
# Set environment variable
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --set-env-vars SECRET_KEY="<generated-key-from-above>"
```

### Verify:
```bash
# Check environment variables
az containerapp show \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --query "properties.template.containers[0].env" -o table
```

---

## Step 2: Run Database Migration (10 minutes)

### Option A: Via psql (Recommended)
```bash
# Connect to Supabase
psql $DATABASE_URL -f /Users/dineshanchetty/Documents/claimtec/iaindex/migrations/002_security_rls_fixes.sql
```

### Option B: Via Supabase Dashboard
1. Login to Supabase Dashboard
2. Go to **SQL Editor**
3. Copy contents of `migrations/002_security_rls_fixes.sql`
4. Click **Run**
5. Verify output shows "RLS enabled on table: ..."

### Verify RLS:
```sql
-- Connect to database
psql $DATABASE_URL

-- Check RLS status
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('websites', 'ai_mentions', 'recommendations');

-- Expected: rowsecurity = true for all tables
```

---

## Step 3: Deploy Updated Code (15 minutes)

### Build Docker Image:
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# Build
docker build -t iaindex-api:v1.2.0-security -f apps/api/Dockerfile apps/api
```

### Push to Azure Container Registry:
```bash
# Login to ACR
az acr login --name <your-acr-name>

# Tag
docker tag iaindex-api:v1.2.0-security <your-acr>.azurecr.io/iaindex-api:v1.2.0-security

# Push
docker push <your-acr>.azurecr.io/iaindex-api:v1.2.0-security
```

### Update Container App:
```bash
az containerapp update \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --image <your-acr>.azurecr.io/iaindex-api:v1.2.0-security
```

---

## Step 4: Verify Security (10 minutes)

### Test 1: Security Headers
```bash
curl -I https://api.iaindex.org/health

# ✅ Should see:
# Content-Security-Policy: default-src 'self'...
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Strict-Transport-Security: max-age=31536000...
```

### Test 2: CSRF Protection
```bash
# ❌ Should fail (403 Forbidden)
curl -X POST https://api.iaindex.org/v1/schema/generate \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'

# Response: "CSRF token validation failed"
```

### Test 3: SSRF Protection
```bash
# ❌ Should fail (400 Bad Request)
curl -X POST https://api.iaindex.org/v1/schema/generate \
  -H "Content-Type: application/json" \
  -d '{"url":"http://localhost"}'

# Response: "Private/local URLs are not allowed"
```

### Test 4: Health Check
```bash
# ✅ Should succeed
curl https://api.iaindex.org/health

# Response: {"status":"healthy",...}
```

---

## Step 5: Monitor (Ongoing)

### Check Logs:
```bash
# View container logs
az containerapp logs show \
  --name iaindex-api \
  --resource-group iaindex-rg \
  --tail 100
```

### Monitor for Issues:
- Watch for "CSRF validation failed" (expected for clients not using tokens)
- Watch for "Blocked domain" or "Private IP" errors
- Watch for "IP blocked" messages (abuse detection)

---

## Quick Troubleshooting

### Issue: App won't start
**Cause:** SECRET_KEY not set or invalid

**Fix:**
```bash
# Check if set
az containerapp show --name iaindex-api --resource-group iaindex-rg \
  --query "properties.template.containers[0].env" -o table

# Set if missing
az containerapp update --name iaindex-api --resource-group iaindex-rg \
  --set-env-vars SECRET_KEY="$(openssl rand -hex 32)"
```

### Issue: CSRF errors on valid requests
**Cause:** Client not including CSRF token

**Fix:** Frontend must:
1. Make GET request first (receives CSRF token in cookie)
2. Include `X-CSRF-Token` header in POST/PUT/DELETE requests

### Issue: RLS blocking API requests
**Cause:** User not authenticated or RLS policy mismatch

**Fix:**
1. Check auth.uid() is being set correctly
2. Verify JWT token is valid
3. Check RLS policies in database

### Issue: Rate limiting too aggressive
**Cause:** Default limits may be too low

**Fix:**
```python
# In main.py, adjust:
app.add_middleware(
    AbuseDetectionMiddleware,
    max_violations=20,  # Increase from 10
    violation_window_minutes=60,
    block_duration_minutes=30,  # Reduce from 60
)
```

---

## Security Checklist

**Before Launch:**
- [ ] SECRET_KEY environment variable set (64+ chars)
- [ ] Database migration 002 applied
- [ ] RLS enabled on all tables (verified)
- [ ] Security headers present (tested)
- [ ] CSRF protection working (tested)
- [ ] SSRF protection working (tested)
- [ ] All secrets rotated
- [ ] Hardcoded credentials removed

**Optional (Recommended):**
- [ ] WAF configured
- [ ] DDoS protection enabled
- [ ] Monitoring setup (Sentry)
- [ ] Penetration testing completed
- [ ] Backup strategy configured

---

## Environment Variables Reference

```bash
# Required (CRITICAL)
SECRET_KEY=<64-char-hex-string>

# Already Configured
DATABASE_URL=<supabase-url>
SUPABASE_URL=<supabase-url>
SUPABASE_KEY=<supabase-anon-key>
ANTHROPIC_API_KEY=<key>
OPENAI_API_KEY=<key>

# Optional
PERPLEXITY_API_KEY=<key>
SENTRY_DSN=<sentry-dsn>
```

---

## Files Changed Summary

**Critical Files:**
- `apps/api/src/config.py` - Secret key validation
- `apps/api/src/main.py` - Security middleware
- `migrations/002_security_rls_fixes.sql` - RLS fixes

**New Files:**
- `apps/api/src/middleware/security_headers.py`
- `apps/api/src/middleware/csrf_protection.py`
- `apps/api/src/middleware/abuse_detection.py`
- `apps/api/src/utils/url_validator.py`

---

## Support

**Issues:** Check `SECURITY_FIXES_REPORT.md` for detailed information

**Emergency:** If you discover a security vulnerability, report immediately

---

**Total Deployment Time:** ~40 minutes
**Difficulty:** Medium
**Status:** Production Ready ✅
