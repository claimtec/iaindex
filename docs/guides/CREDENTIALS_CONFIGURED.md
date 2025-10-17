# AIIndex v1.1 - Credentials Configured ✅

**Date**: 2025-10-14 16:15:00
**Status**: ✅ **CREDENTIALS CONFIGURED - READY TO TEST**

---

## ✅ Configuration Complete

Your Supabase credentials have been configured in all environment files:

### Supabase Project Details
- **Project ID**: `casuupkmbqytgqnksnwd`
- **Project URL**: `https://casuupkmbqytgqnksnwd.supabase.co`
- **Region**: US West (AWS)
- **Anon Key**: Configured ✅
- **Secret Key**: Generated and configured ✅

### Files Updated

1. **`apps/api/.env.staging`** ✅
   - Supabase URL configured
   - Anon key configured
   - SECRET_KEY generated (32-byte hex)
   - DATABASE_URL set (requires password)

2. **`apps/web/.env.staging`** ✅
   - Supabase URL configured
   - Anon key configured

3. **`apps/web/.env.local`** ✅
   - Supabase URL configured (for local testing)
   - Anon key configured

---

## ⚠️ Important: Database Password Required

The `DATABASE_URL` in `apps/api/.env.staging` needs your database password:

**Current**:
```
DATABASE_URL=postgresql://postgres.casuupkmbqytgqnksnwd:YOUR_DB_PASSWORD@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

**To Get Your Password**:
1. Go to https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd
2. Click Settings → Database
3. Look for "Connection string"
4. Copy the password from the connection string
5. Replace `YOUR_DB_PASSWORD` in the DATABASE_URL

**Or Get Connection String Directly**:
1. Go to Supabase Dashboard → Project Settings → Database
2. Copy "Connection string" (URI format)
3. Replace entire DATABASE_URL with this value

---

## 🚀 Next Steps

### Step 1: Update Database Password (2 minutes)

```bash
# Edit the file
nano apps/api/.env.staging

# Or use any text editor to replace YOUR_DB_PASSWORD with actual password
```

### Step 2: Run Database Migration (5 minutes)

**Option A: Using Supabase SQL Editor** (Recommended)
1. Go to https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/editor
2. Click "New query"
3. Copy entire contents of `migrations/v1.0-to-v1.1.sql`
4. Paste and click "Run"
5. Should see: "Success. No rows returned"

**Option B: Using psql**
```bash
# After updating DATABASE_URL with password
psql "$DATABASE_URL" < migrations/v1.0-to-v1.1.sql
```

**Verify Migration**:
```sql
-- Run in Supabase SQL Editor
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Should see these new v1.1 tables:
-- ✓ bot_reputation
-- ✓ fraud_detection_logs
-- ✓ merkle_timestamps
-- ✓ violation_records
```

### Step 3: Test Dashboard Locally (Optional - 5 minutes)

```bash
cd apps/web
npm run dev
```

Open http://localhost:3000 in browser:
- Should see AIIndex dashboard
- Can test Supabase auth
- Can see login page

Press Ctrl+C to stop.

### Step 4: Test API Locally (Optional - 5 minutes)

```bash
cd apps/api
source venv/bin/activate  # If using virtual environment
uvicorn main:app --reload
```

Test endpoints:
```bash
# In another terminal
curl http://localhost:8000/
curl http://localhost:8000/health
```

Press Ctrl+C to stop.

### Step 5: Deploy to Staging

```bash
./deploy.sh staging
```

---

## 📝 Quick Reference

### Your Supabase Dashboard
https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd

**Useful Pages**:
- **SQL Editor**: https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/editor
- **Database**: https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/database/tables
- **API Settings**: https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/settings/api
- **Auth**: https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/auth/users

### Environment Files
- Local Dev: `apps/web/.env.local` ✅
- Staging API: `apps/api/.env.staging` ⚠️ (needs password)
- Staging Dashboard: `apps/web/.env.staging` ✅

### Database Migration
- File: `migrations/v1.0-to-v1.1.sql`
- Status: Not run yet
- Method: Copy/paste into Supabase SQL Editor

---

## ✅ Checklist Before Deployment

- [x] Supabase project created
- [x] Supabase credentials configured in .env files
- [x] Secret key generated
- [ ] **Database password added to DATABASE_URL**
- [ ] **Database migration run**
- [ ] Dashboard tested locally (optional)
- [ ] API tested locally (optional)
- [ ] Ready to deploy

---

## 🎯 You're Almost Ready!

**Just 2 more steps**:
1. Update database password in `apps/api/.env.staging`
2. Run database migration in Supabase SQL Editor

**Then deploy**:
```bash
./deploy.sh staging
```

---

**Last Updated**: 2025-10-14 16:15:00
