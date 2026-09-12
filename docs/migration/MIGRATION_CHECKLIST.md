# IAIndex Fresh Supabase Setup - Migration Checklist

## New Project Details
- **Project URL**: https://uskaaxzhbijpvpgzubbp.supabase.co
- **Anon Key**: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVza2FheHpoYmlqcHZwZ3p1YmJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NDUyODMsImV4cCI6MjA3NjMyMTI4M30.56CpnkPNRG4BYreMswYvDlaTmOXcjns2qkiiEA__wKY

---

## ✅ Phase 1: Supabase Dashboard Setup

### Step 1.1: Enable Email Authentication
- [ ] Go to: https://uskaaxzhbijpvpgzubbp.supabase.co/project/default/auth/providers
- [ ] Find **Email** provider
- [ ] Toggle **Enable Email provider** to ON
- [ ] **Enable email confirmations**: OFF (for testing, enable later for production)
- [ ] **Secure email change**: ON
- [ ] Click **Save**

### Step 1.2: Get Service Role Key
- [ ] Go to: https://uskaaxzhbijpvpgzubbp.supabase.co/project/default/settings/api
- [ ] Copy **service_role** key (keep this secret!)
- [ ] Save it to: `SERVICE_ROLE_KEY=[paste here]`

---

## ✅ Phase 2: Run Database Migrations

### Step 2.1: Run Base Migration
- [ ] Go to: https://uskaaxzhbijpvpgzubbp.supabase.co/project/default/sql/new
- [ ] Copy contents of **`000_FRESH_PROJECT_MIGRATION.sql`**
- [ ] Paste into SQL Editor
- [ ] Click **Run**
- [ ] Verify: "Migration 000 completed successfully!"
- [ ] Check that these tables exist:
  - [ ] profiles
  - [ ] publishers
  - [ ] receipts
  - [ ] attestations
  - [ ] merkle_roots, merkle_nodes, merkle_timestamps
  - [ ] bot_reputation, violation_records, fraud_detection_logs
  - [ ] user_preferences

### Step 2.2: Run AI Visibility Migration
- [ ] Copy contents of **`001_schema_pivot_migration.sql`**
- [ ] Paste into SQL Editor
- [ ] Click **Run**
- [ ] Verify tables created:
  - [ ] websites
  - [ ] ai_mentions
  - [ ] recommendations

### Step 2.3: Run Email Automation Migration
- [ ] Copy contents of **`002_email_automation.sql`**
- [ ] Paste into SQL Editor
- [ ] Click **Run**
- [ ] Verify tables created:
  - [ ] email_preferences
  - [ ] drip_campaigns (should have 1 row: "Onboarding")
  - [ ] drip_campaign_emails (should have 4 rows)
  - [ ] email_analytics

### Step 2.4: Run Analytics Migration
- [ ] Copy contents of **`003_analytics_tables.sql`**
- [ ] Paste into SQL Editor
- [ ] Click **Run**
- [ ] Verify tables created:
  - [ ] visibility_scans
  - [ ] scan_results
  - [ ] analytics_events

---

## ✅ Phase 3: Test User Creation

### Step 3.1: Create Test User via Dashboard
- [ ] Go to: https://uskaaxzhbijpvpgzubbp.supabase.co/project/default/auth/users
- [ ] Click **Add user** → **Create new user**
- [ ] Enter:
  - Email: `test@iaindex.org`
  - Password: `TestPassword123!`
  - **Auto Confirm User**: ✅ Check this box
- [ ] Click **Create user**
- [ ] Verify user appears in list

### Step 3.2: Verify Profile Auto-Created
Run this in SQL Editor:
```sql
SELECT * FROM profiles WHERE email = 'test@iaindex.org';
```
- [ ] Should return 1 row with user's profile
- [ ] If empty, the trigger is not working!

### Step 3.3: Check Trigger Exists
Run this in SQL Editor:
```sql
SELECT
    tgname as trigger_name,
    tgrelid::regclass as table_name,
    proname as function_name
FROM pg_trigger t
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE tgname = 'on_auth_user_created';
```
- [ ] Should return: `on_auth_user_created | auth.users | handle_new_user`

---

## ✅ Phase 4: Update Backend Environment Variables

### Step 4.1: Update Azure Container Apps Secrets
Run these commands:

```bash
# Set new Supabase credentials
az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets \
    supabase-url="https://uskaaxzhbijpvpgzubbp.supabase.co" \
    supabase-key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVza2FheHpoYmlqcHZwZ3p1YmJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NDUyODMsImV4cCI6MjA3NjMyMTI4M30.56CpnkPNRG4BYreMswYvDlaTmOXcjns2qkiiEA__wKY"
```
- [ ] Run command
- [ ] Verify: `Successfully updated secrets`

### Step 4.2: Get Latest Revision Name
```bash
az containerapp revision list \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --query "[0].name" \
  -o tsv
```
- [ ] Save revision name: `_________________`

### Step 4.3: Restart Container
```bash
az containerapp revision restart \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --revision [PASTE-REVISION-NAME-HERE]
```
- [ ] Run command
- [ ] Wait 30 seconds for restart

### Step 4.4: Check Backend Health
```bash
curl https://api.iaindex.org/health
```
- [ ] Should return: `{"status":"healthy"}`

---

## ✅ Phase 5: Test Backend Registration

### Step 5.1: Register User via API
```bash
curl -X POST https://api.iaindex.org/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "backendtest@iaindex.org",
    "password": "SecurePass123!",
    "full_name": "Backend Test User",
    "company": "Test Corp"
  }'
```

Expected response:
```json
{
  "user": {
    "id": "...",
    "email": "backendtest@iaindex.org",
    "full_name": "Backend Test User"
  },
  "access_token": "...",
  "refresh_token": "..."
}
```

- [ ] Registration succeeded
- [ ] Received access_token
- [ ] Received refresh_token

### Step 5.2: Verify User in Dashboard
- [ ] Go to: https://uskaaxzhbijpvpgzubbp.supabase.co/project/default/auth/users
- [ ] Verify `backendtest@iaindex.org` appears in list

### Step 5.3: Verify Profile Created
Run in SQL Editor:
```sql
SELECT * FROM profiles WHERE email = 'backendtest@iaindex.org';
```
- [ ] Profile exists
- [ ] full_name = "Backend Test User"
- [ ] company = "Test Corp"

---

## ✅ Phase 6: Update Frontend Environment Variables

### Step 6.1: Update apps/scan/.env.local
```bash
NEXT_PUBLIC_SUPABASE_URL=https://uskaaxzhbijpvpgzubbp.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVza2FheHpoYmlqcHZwZ3p1YmJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NDUyODMsImV4cCI6MjA3NjMyMTI4M30.56CpnkPNRG4BYreMswYvDlaTmOXcjns2qkiiEA__wKY
```
- [ ] Updated .env.local file

### Step 6.2: Restart Dev Server
```bash
cd apps/scan
npm run dev
```
- [ ] Server started successfully
- [ ] No errors in console

### Step 6.3: Test Frontend Registration
- [ ] Open http://localhost:3000
- [ ] Click "Sign Up" or "Get Started"
- [ ] Fill in registration form:
  - Email: `frontendtest@iaindex.org`
  - Password: `SecurePass123!`
  - Name: `Frontend Test User`
- [ ] Submit form
- [ ] Registration succeeded
- [ ] Redirected to dashboard

---

## ✅ Phase 7: Verification & Cleanup

### Step 7.1: Verify All Users
Run in SQL Editor:
```sql
SELECT
    u.email,
    u.created_at as auth_created,
    p.full_name,
    p.company,
    p.plan,
    p.created_at as profile_created
FROM auth.users u
JOIN profiles p ON u.id = p.id
ORDER BY u.created_at DESC;
```
- [ ] All 3 test users exist
- [ ] All have matching profiles
- [ ] Trigger is working correctly

### Step 7.2: Test Login
```bash
curl -X POST https://api.iaindex.org/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "backendtest@iaindex.org",
    "password": "SecurePass123!"
  }'
```
- [ ] Login succeeded
- [ ] Received new access_token

### Step 7.3: Cleanup Test Users (Optional)
If you want to remove test users:
```sql
-- Delete test users (this cascades to profiles)
DELETE FROM auth.users WHERE email IN (
    'test@iaindex.org',
    'backendtest@iaindex.org',
    'frontendtest@iaindex.org'
);
```

---

## 🎉 Success Criteria

- [x] New Supabase project created
- [ ] Email provider enabled
- [ ] All 4 migrations applied successfully
- [ ] All expected tables exist (22+ tables)
- [ ] User creation via Dashboard works
- [ ] Profile auto-created via trigger
- [ ] Backend environment variables updated
- [ ] Backend registration API works
- [ ] Frontend can connect to new project
- [ ] Frontend registration works
- [ ] Login works

---

## 🐛 Troubleshooting

### Issue: "Registration failed with status 500"
1. Check Supabase logs: https://uskaaxzhbijpvpgzubbp.supabase.co/project/default/logs/postgres-logs
2. Look for errors related to triggers or constraints
3. Verify trigger exists (Step 3.3)
4. Check backend logs

### Issue: Profile not auto-created
1. Run Step 3.2 to verify profile exists
2. If missing, check trigger exists (Step 3.3)
3. Manually create profile:
```sql
INSERT INTO profiles (id, email, email_verified)
SELECT id, email, email_confirmed_at IS NOT NULL
FROM auth.users
WHERE email = 'test@iaindex.org';
```

### Issue: "relation does not exist"
- Verify all migrations ran successfully
- Check table list in SQL Editor:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

### Issue: RLS blocks operations
Temporarily disable RLS for testing:
```sql
ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
```
Remember to re-enable after testing:
```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
```

---

## 📝 Notes

- Keep service_role key secret - never commit to git
- Re-enable email confirmations for production
- Set up custom email templates before launch
- Configure backup schedule in Supabase settings
- Add additional team members in Dashboard → Settings → Team

## Next Steps After Setup

1. ✅ Authentication working
2. Deploy updated backend to production
3. Update production environment variables
4. Test end-to-end flow in production
5. Configure monitoring and alerts
6. Set up CI/CD pipelines
7. Launch! 🚀
