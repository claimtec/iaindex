# AIIndex v1.1 - Next Steps for Deployment

**Status**: ✅ **All technical work complete**
**Next**: Manual infrastructure setup required

---

## 🎯 Where We Are

✅ **100% of code is ready**
- All fixes applied
- Dashboard builds successfully (13 routes)
- API dependencies install cleanly (56 packages)
- Database migration validated and safe
- Deployment scripts tested and ready
- Smoke tests ready

🔄 **Waiting on**: Database setup and credentials

---

## 🚀 What You Need to Do Next

### Step 1: Create Supabase Projects (15 minutes)

**Staging Project**:
1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Name: `aiindex-staging`
4. Database password: Generate strong password
5. Region: Choose closest to your users
6. Wait for project to provision (~2 minutes)

**Production Project**:
1. Repeat above steps
2. Name: `aiindex-production`
3. Use different password
4. Same region

**Get Credentials**:
1. Go to Project Settings → API
2. Copy `Project URL` (looks like: https://xxxxx.supabase.co)
3. Copy `anon` `public` key
4. Go to Project Settings → Database
5. Copy `Connection string` (URI format)

---

### Step 2: Update Environment Files (5 minutes)

**Staging API** (`apps/api/.env.staging`):
```bash
# Replace these lines:
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT].supabase.co
SUPABASE_KEY=[YOUR-ANON-KEY]

# Generate new secret (run in terminal):
SECRET_KEY=$(openssl rand -hex 32)
```

**Staging Dashboard** (`apps/web/.env.staging`):
```bash
NEXT_PUBLIC_SUPABASE_URL=https://[YOUR-PROJECT].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
```

**Repeat for Production** (using production project credentials):
- `apps/api/.env.production`
- `apps/web/.env.production`

---

### Step 3: Run Database Migration (5 minutes)

**Option A: Using Supabase SQL Editor** (Recommended)
1. Go to your Supabase staging project
2. Click "SQL Editor"
3. Open `migrations/v1.0-to-v1.1.sql` in a text editor
4. Copy entire contents
5. Paste into SQL Editor
6. Click "Run"
7. Verify output: "Migration v1.0 to v1.1 completed successfully!"

**Option B: Using psql** (If you have PostgreSQL installed)
```bash
psql "YOUR-DATABASE-URL-FROM-SUPABASE" < migrations/v1.0-to-v1.1.sql
```

**Verify Migration**:
```sql
-- Run this in SQL Editor
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('bot_reputation', 'violation_records', 'fraud_detection_logs', 'merkle_timestamps');

-- Should return 4 rows
```

---

### Step 4: Deploy to Staging (10 minutes)

```bash
# From project root
./deploy.sh staging

# Watch output for:
# ✓ Pre-deployment checks complete
# ✓ Environment validation complete
# ✓ Database migration complete (may warn if already run - that's OK)
# ✓ API deployment prepared
# ✓ Dashboard deployment prepared
# ✓ Documentation deployment prepared
```

**Expected Output**:
- Script will prepare all components
- May show warnings (non-blocking)
- Will create deployment log file
- Exit with success message

---

### Step 5: Run Smoke Tests (2 minutes)

```bash
./scripts/smoke-tests.sh staging

# Watch for:
# ✓ PASS - All 9 tests should pass
# ✗ FAIL - If any fail, check logs
```

**If Tests Fail**:
1. Check that environment variables are set correctly
2. Check that database migration completed
3. Check logs: `cat deployment_staging_*.log`
4. Check API is running: `curl https://aiindex-api-staging.fly.dev/health`

---

### Step 6: Manual Testing (30 minutes)

Open staging dashboard and test:

1. **Login** → Should redirect to Supabase auth
2. **Dashboard** → Should show overview
3. **Policy Page** (`/dashboard/policy`) →
   - Toggle switches work
   - Rate limit sliders work
   - JSON preview updates
4. **Compliance Page** (`/dashboard/compliance`) →
   - Charts render (may be empty initially)
   - Export buttons work
5. **Provenance Page** (`/dashboard/provenance`) →
   - Tabs switch correctly
   - Badge generator works
   - QR code displays

---

### Step 7: Deploy to Production (After Staging Validates)

```bash
# Only if staging tests pass
./deploy.sh production
./scripts/smoke-tests.sh production
```

---

## 📝 Quick Commands Reference

```bash
# Deploy to staging
./deploy.sh staging

# Test staging
./scripts/smoke-tests.sh staging

# Deploy to production
./deploy.sh production

# Test production
./scripts/smoke-tests.sh production

# View deployment logs
ls -lt deployment_*.log | head -1  # Find latest log
tail -f deployment_staging_*.log    # Watch in real-time

# Rollback (if needed)
fly deploy --app aiindex-api --image aiindex-api:v1.0
vercel rollback --app aiindex-web
```

---

## 🔧 Optional Services (Can Configure Later)

### Redis (Rate Limiting)
```bash
# Free tier: Upstash Redis
# 1. Go to https://upstash.com/
# 2. Create Redis database
# 3. Copy REST URL
# 4. Add to .env: REDIS_URL=redis://...
```

### Cloudflare Browser Rendering
```bash
# 1. Sign up at https://cloudflare.com/
# 2. Go to Workers & Pages → Browser Rendering
# 3. Get Account ID and API Token
# 4. Add to .env:
#    CLOUDFLARE_ACCOUNT_ID=...
#    CLOUDFLARE_API_TOKEN=...
```

### OpenAI Embeddings
```bash
# 1. Go to https://platform.openai.com/api-keys
# 2. Create new API key
# 3. Add to .env: OPENAI_API_KEY=sk-...
```

### C2PA Certificates
```bash
# Generate self-signed certificates for testing:
openssl genrsa -out keys/c2pa_private.pem 2048
openssl req -new -x509 -key keys/c2pa_private.pem -out keys/c2pa_cert.pem -days 365

# Add to .env:
# C2PA_PRIVATE_KEY_PATH=./keys/c2pa_private.pem
# C2PA_CERTIFICATE_PATH=./keys/c2pa_cert.pem
```

---

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| [`DEPLOYMENT_PLAN.md`](./DEPLOYMENT_PLAN.md) | Comprehensive deployment guide (18KB) |
| [`DEPLOYMENT_READINESS.md`](./DEPLOYMENT_READINESS.md) | Pre-deployment checklist |
| [`DEPLOYMENT_FIXES_APPLIED.md`](./DEPLOYMENT_FIXES_APPLIED.md) | Issues fixed today |
| [`DEPLOYMENT_STATUS_FINAL.md`](./DEPLOYMENT_STATUS_FINAL.md) | Current status summary |
| [`DEPLOYMENT_NEXT_STEPS.md`](./DEPLOYMENT_NEXT_STEPS.md) | This document |

---

## ❓ FAQ

**Q: Do I need to set up ALL optional services before deploying?**
A: No. Only Supabase is required. Redis, Cloudflare, OpenAI, and C2PA are optional and can be added later.

**Q: Can I test locally first?**
A: Yes! Use `.env.local` with your staging credentials and run:
```bash
cd apps/web && npm run dev  # Dashboard on localhost:3000
cd apps/api && uvicorn main:app --reload  # API on localhost:8000
```

**Q: What if the deployment fails?**
A: Check the deployment log file (`deployment_staging_*.log`). Most issues are related to missing credentials or network connectivity.

**Q: How long does deployment take?**
A:
- Initial setup: 15-30 minutes
- Deployment script: 5-10 minutes
- Testing: 30-60 minutes
- **Total**: ~1-2 hours

**Q: Can I deploy just the dashboard first?**
A: Yes, but you'll need the API for full functionality. The dashboard calls API endpoints for data.

**Q: Is the database migration reversible?**
A: Yes. The migration only adds tables/columns without modifying existing data. See rollback plan in [`DEPLOYMENT_STATUS_FINAL.md`](./DEPLOYMENT_STATUS_FINAL.md).

---

## ✅ Checklist

Before you start:
- [ ] Read this document fully
- [ ] Have Supabase account ready
- [ ] Have text editor open for .env files
- [ ] Have terminal ready for commands
- [ ] Allocate 1-2 hours uninterrupted time

---

## 🎉 You're Ready!

All the code is done. All the scripts are ready. All the documentation is complete.

**Next action**: Create Supabase projects and update credentials.

**Then**: Run `./deploy.sh staging`

Good luck! 🚀

---

**Questions?** Check:
1. [`DEPLOYMENT_PLAN.md`](./DEPLOYMENT_PLAN.md) - Detailed guide
2. [`DEPLOYMENT_STATUS_FINAL.md`](./DEPLOYMENT_STATUS_FINAL.md) - Current status
3. Deployment logs - `deployment_*.log` files

---

**Last Updated**: 2025-10-14 16:10:00
