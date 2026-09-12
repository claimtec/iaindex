# Authentication Setup - Final Summary

## Current Status

✅ **Backend Code:** Fully updated to use Supabase Auth API
✅ **Database:** `profiles` table created with trigger
✅ **Deployment:** Backend deployed (revision 0000019)

⚠️ **Blockers:**
1. Supabase Auth Email provider needs to be enabled
2. Supabase API key may need to be refreshed in Azure environment

---

## Steps to Fix Authentication

### Step 1: Get Fresh Supabase Keys (5 minutes)

1. Go to: https://supabase.com/dashboard
2. Select your project: `casuupkmbqytgqnksnwd`
3. Go to **Settings** → **API**
4. Copy these keys:
   - **Project URL:** `https://casuupkmbqytgqnksnwd.supabase.co`
   - **anon public key:** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
   - **service_role secret:** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

### Step 2: Enable Email Authentication (2 minutes)

1. In Supabase Dashboard: **Authentication** → **Providers**
2. Find **Email** provider
3. **Enable** it (toggle ON)
4. **Uncheck** "Confirm email" (for testing)
5. Click **Save**

### Step 3: Update Azure Environment Variables (5 minutes)

Update the Supabase keys in Azure Container Apps:

```bash
# Get the fresh keys from Step 1, then run:
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars \
    SUPABASE_URL="https://casuupkmbqytgqnksnwd.supabase.co" \
  --replace-env-vars \
    SUPABASE_KEY="secretref:supabase-key"

# Update the secret with fresh anon key
az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets supabase-key="YOUR_ANON_KEY_HERE"
```

**Replace `YOUR_ANON_KEY_HERE` with the anon public key from Step 1**

### Step 4: Restart the Container App (Optional)

The app should auto-restart after updating secrets, but if needed:

```bash
az containerapp revision restart \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --revision aiindex-api--0000019
```

### Step 5: Test Registration

```bash
curl -X POST https://api.iaindex.org/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dinesh@iaindex.org",
    "password": "SecurePass123",
    "full_name": "Dinesh Anchetty",
    "company": "ClaimTec"
  }' | jq '.'
```

**Expected Success Response:**
```json
{
  "user": {
    "id": "uuid-here",
    "email": "dinesh@iaindex.org",
    "full_name": "Dinesh Anchetty",
    "company": "ClaimTec",
    "plan": "free"
  },
  "access_token": "eyJ...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### Step 6: Test Login

```bash
curl -X POST https://api.iaindex.org/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dinesh@iaindex.org",
    "password": "SecurePass123"
  }' | jq '.'
```

---

## Alternative: Manual User Creation for Testing

If you want to test immediately without waiting for API keys:

1. Go to Supabase Dashboard → **Authentication** → **Users**
2. Click **"Add user"** (or "Invite user")
3. Enter:
   - Email: `dinesh@iaindex.org`
   - Password: `SecurePass123`
   - **Check:** "Auto Confirm User"
4. Click **"Create user"** or **"Send invitation"**

Then test login:
```bash
curl -X POST https://api.iaindex.org/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dinesh@iaindex.org",
    "password": "SecurePass123"
  }' | jq '.'
```

**Note:** This creates the user in `auth.users`, and the trigger will automatically create the profile in the `profiles` table.

---

## Verification Queries

After creating a user, verify everything is working:

```sql
-- Check auth.users (in Supabase SQL Editor)
SELECT id, email, created_at, email_confirmed_at, last_sign_in_at
FROM auth.users
WHERE email = 'dinesh@iaindex.org';

-- Check profiles table
SELECT id, email, full_name, company, plan, created_at
FROM profiles
WHERE email = 'dinesh@iaindex.org';

-- Check they have matching IDs
SELECT
  u.id as auth_id,
  u.email as auth_email,
  p.id as profile_id,
  p.email as profile_email,
  p.full_name
FROM auth.users u
LEFT JOIN profiles p ON u.id = p.id
WHERE u.email = 'dinesh@iaindex.org';
```

---

## What Each Component Does

### Supabase Auth (`auth.users`)
- **Managed by Supabase** - you can't directly insert here
- Handles password hashing, JWT tokens, email verification
- Created via Supabase Auth API or Dashboard

### Profiles Table (`public.profiles`)
- **Managed by your app** - stores application-specific user data
- Automatically created by trigger when user signs up
- Linked to `auth.users` via foreign key
- You can update this table directly

### The Flow:
```
User signs up
    ↓
Supabase Auth creates user in auth.users
    ↓
Trigger (on_auth_user_created) fires
    ↓
Profile auto-created in profiles table
    ↓
Backend can update profile with additional data
```

---

## Troubleshooting

### "Invalid API key"
- **Cause:** Supabase anon key is wrong or expired
- **Fix:** Get fresh key from Supabase Dashboard → Settings → API

### "Registration failed with status 500"
- **Cause:** Email provider not enabled OR invalid API key
- **Fix:** Enable Email provider + update API key

### "Email already registered"
- **Cause:** User exists in auth.users
- **Fix:** Use different email OR delete user from Supabase Dashboard

### "Profile not found"
- **Cause:** Trigger didn't fire
- **Fix:** Verify trigger exists (query in Verification Queries section)

---

## Quick Win: Test Without Backend

Test Supabase Auth directly to verify it's working:

```bash
# Get your anon key from Supabase Dashboard
ANON_KEY="your-anon-key-here"

# Test signup
curl -X POST https://casuupkmbqytgqnksnwd.supabase.co/auth/v1/signup \
  -H "apikey: $ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@iaindex.org",
    "password": "SecurePass123"
  }' | jq '.'
```

If this works, then Supabase Auth is configured correctly, and you just need to update the Azure environment variables.

---

## Summary

**To get authentication working:**

1. ✅ Get fresh Supabase API keys (Settings → API)
2. ✅ Enable Email provider (Authentication → Providers)
3. ✅ Update Azure environment with fresh keys
4. ✅ Test registration

**OR**

1. ✅ Enable Email provider
2. ✅ Create user manually via Dashboard
3. ✅ Test login immediately

**The backend code is ready - it just needs valid Supabase credentials and enabled Email provider!**

---

## Next Steps After Auth Works

Once authentication is working:

1. Deploy scan tool frontend to scan.iaindex.org
2. Deploy dashboard frontend to app.iaindex.org
3. Configure email provider (SendGrid/Resend)
4. End-to-end testing
5. Launch! 🚀

**You're 99% there!** Just need to enable Email provider and verify API keys. 🎯
