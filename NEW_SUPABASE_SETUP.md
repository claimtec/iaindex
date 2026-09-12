# New Supabase Project Setup Guide

## Step 1: Create New Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Choose organization: ClaimTec
4. Project name: `iaindex-v2-fresh`
5. Database password: [Generate strong password and save it]
6. Region: Choose closest to your users (e.g., East US)
7. Wait for project to be provisioned (~2 minutes)

## Step 2: Enable Email Authentication

1. In Supabase Dashboard, go to **Authentication** → **Providers**
2. Find **Email** provider
3. Toggle **Enable Email provider** to ON
4. Configure settings:
   - **Enable email confirmations**: OFF (for testing, enable later for production)
   - **Secure email change**: ON
   - **Enable email OTP**: Optional
5. Click **Save**

## Step 3: Configure Email Templates (Optional for now)

1. Go to **Authentication** → **Email Templates**
2. You can customize:
   - Confirmation email
   - Magic Link email
   - Password reset email
3. For now, leave defaults - we'll customize later

## Step 4: Get API Credentials

1. Go to **Settings** → **API**
2. Copy and save these values:
   - **Project URL**: `https://[your-project-ref].supabase.co`
   - **anon public** key
   - **service_role** key (keep secret!)

## Step 5: Run Database Migrations

Run the migrations in this exact order:

### Migration 1: Core Schema
```bash
# Run: 000_FRESH_PROJECT_MIGRATION.sql
```
This creates:
- profiles table (linked to auth.users)
- publishers table
- receipts table
- attestations table
- user_preferences table
- All necessary indexes and RLS policies

### Migration 2: AI Visibility Features
```bash
# Run: 001_schema_pivot_migration.sql
```
This creates:
- websites table
- ai_mentions table
- recommendations table

### Migration 3: Email Automation
```bash
# Run: 002_email_automation.sql
```
This creates:
- email_preferences table
- drip_campaigns table
- drip_campaign_emails table
- email_analytics table

### Migration 4: Analytics
```bash
# Run: 003_analytics_tables.sql
```
This creates:
- visibility_scans table
- scan_results table
- analytics_events table

## Step 6: Verify Schema

Run this query to verify all tables exist:

```sql
SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname IN ('public', 'auth')
ORDER BY schemaname, tablename;
```

Expected tables in **public** schema:
- analytics_events
- ai_mentions
- attestations
- drip_campaigns
- drip_campaign_emails
- email_analytics
- email_preferences
- profiles
- publishers
- receipts
- recommendations
- scan_results
- user_preferences
- visibility_scans
- websites

## Step 7: Test User Creation via Dashboard

1. Go to **Authentication** → **Users**
2. Click **Add user** → **Create new user**
3. Enter:
   - Email: test@iaindex.org
   - Password: TestPassword123!
   - **Auto Confirm User**: Check this box (for testing)
4. Click **Create user**
5. Verify user appears in list
6. Run this query to verify profile was auto-created:

```sql
SELECT * FROM profiles WHERE email = 'test@iaindex.org';
```

If you see the profile, the trigger is working correctly!

## Step 8: Update Backend Environment Variables

Update Azure Container Apps with new Supabase credentials:

```bash
# Set the new Supabase URL and keys
az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets \
    supabase-url="https://[YOUR-NEW-PROJECT-REF].supabase.co" \
    supabase-key="[YOUR-NEW-ANON-KEY]"

# Restart the container to pick up new secrets
az containerapp revision restart \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --revision [LATEST-REVISION-NAME]
```

## Step 9: Test Backend Registration

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

## Step 10: Update Frontend Environment Variables

Update the scan app's `.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://[YOUR-NEW-PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[YOUR-NEW-ANON-KEY]
```

Restart the dev server:
```bash
cd apps/scan
npm run dev
```

## Troubleshooting

### If user creation fails:

1. Check Supabase logs:
   - Dashboard → **Logs** → **Postgres Logs**
   - Look for errors related to triggers or constraints

2. Verify trigger exists:
```sql
SELECT * FROM pg_trigger WHERE tgname = 'on_auth_user_created';
```

3. Test trigger manually:
```sql
-- This should create a profile automatically
INSERT INTO auth.users (
    instance_id, id, aud, role, email,
    encrypted_password, email_confirmed_at,
    raw_app_meta_data, raw_user_meta_data,
    created_at, updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000000',
    gen_random_uuid(),
    'authenticated',
    'authenticated',
    'triggertest@iaindex.org',
    crypt('TestPass123!', gen_salt('bf')),
    now(),
    '{"provider":"email","providers":["email"]}',
    '{}',
    now(), now()
);

-- Verify profile was created
SELECT * FROM profiles WHERE email = 'triggertest@iaindex.org';
```

### If RLS blocks operations:

Temporarily disable RLS for testing:
```sql
ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
```

Remember to re-enable after testing:
```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
```

## Success Criteria

✅ New Supabase project created
✅ Email provider enabled
✅ All 4 migrations applied successfully
✅ All expected tables exist
✅ User creation via Dashboard works
✅ Profile auto-created via trigger
✅ Backend environment variables updated
✅ Backend registration API works
✅ Frontend can connect to new project

## Next Steps After Setup

1. Enable email confirmations in production
2. Configure custom email templates
3. Set up monitoring and alerts
4. Configure backup schedule
5. Add additional team members
6. Set up staging environment with separate Supabase project
