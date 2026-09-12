# Supabase Auth Fix - Implementation Guide

**Issue:** Backend was trying to create `users` table in `public` schema, but Supabase manages users in `auth` schema.

**Solution:** Create `profiles` table that extends `auth.users` with application-specific data.

---

## Step 1: Apply Database Migration (5 minutes)

Run this migration in Supabase SQL Editor:

**File:** `/migrations/create_profiles_table.sql`

This will:
- ✅ Drop the incorrect `users` table
- ✅ Create `profiles` table linked to `auth.users`
- ✅ Set up trigger to auto-create profiles when users sign up
- ✅ Update all foreign keys to reference `profiles`
- ✅ Configure proper RLS policies

---

## Step 2: Update Backend Code (Two Options)

### Option A: Use New Supabase Auth Service (Recommended)

**Update:** `/apps/api/src/routes/auth.py`

Replace the import:
```python
# OLD:
from ..services.auth_service import AuthenticationService

# NEW:
from ..services.auth_service_supabase import SupabaseAuthService as AuthenticationService
```

**Benefits:**
- ✅ Uses proper Supabase Auth
- ✅ Email verification built-in
- ✅ Password reset built-in
- ✅ Social auth ready (Google, GitHub, etc.)
- ✅ Admin dashboard for user management

### Option B: Quick Fix (Keep Current Code, Minimal Changes)

**Update:** `/apps/api/src/services/auth_service.py`

Change line 87 (in register method):
```python
# OLD:
result = self.supabase.table("users").insert({
    ...
}).execute()

# NEW:
# First create auth user
auth_response = self.supabase.auth.sign_up({
    "email": email,
    "password": password
})

# Then update profile
result = self.supabase.table("profiles").update({
    "full_name": full_name,
    "company": company,
    "plan": "free"
}).eq("id", str(auth_response.user.id)).execute()
```

**Recommendation:** Use Option A for production (proper Supabase Auth integration)

---

## Step 3: Enable Supabase Auth Email Provider

1. Go to Supabase Dashboard → Authentication → Providers
2. Enable **Email** provider
3. Configure email templates (optional):
   - Confirmation email
   - Password reset email
   - Magic link email

**Email Template Settings:**
- Sender name: IAIndex
- From email: noreply@iaindex.org
- Confirm sign up: Enabled (for email verification)

---

## Step 4: Test the Fix

### Test Registration:
```bash
curl -X POST https://api.iaindex.org/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@iaindex.org",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

**Expected Response:**
```json
{
  "user": {
    "id": "uuid-here",
    "email": "test@iaindex.org",
    "full_name": "Test User",
    "email_verified": false
  },
  "access_token": "eyJ...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### Test Login:
```bash
curl -X POST https://api.iaindex.org/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@iaindex.org",
    "password": "SecurePass123"
  }'
```

**Expected Response:** Same as registration (with access_token)

### Test Get Profile:
```bash
TOKEN="your-access-token"

curl -X GET https://api.iaindex.org/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "email": "test@iaindex.org",
  "full_name": "Test User",
  "plan": "free",
  "email_verified": false
}
```

---

## Step 5: Verify Profile Trigger

Check that profiles are auto-created when users sign up:

```sql
-- View auth.users
SELECT id, email, created_at FROM auth.users ORDER BY created_at DESC LIMIT 5;

-- View profiles (should match)
SELECT id, email, full_name, created_at FROM profiles ORDER BY created_at DESC LIMIT 5;

-- They should have matching IDs
```

---

## Step 6: Deploy Updated Backend

### Build new Docker image:
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# Build for AMD64 (Azure requirement)
docker buildx build --platform linux/amd64 \
  -t iaindex-api:v2.2.0-auth-fix \
  -f apps/api/Dockerfile \
  apps/api

# Tag for Azure Container Registry
docker tag iaindex-api:v2.2.0-auth-fix cafc3cb1336eacr.azurecr.io/iaindex-api:v2.2.0-auth-fix

# Push to registry
docker push cafc3cb1336eacr.azurecr.io/iaindex-api:v2.2.0-auth-fix
```

### Deploy to Azure:
```bash
az containerapp update \
  --name iaindex-api \
  --resource-group aiindex-rg \
  --image cafc3cb1336eacr.azurecr.io/iaindex-api:v2.2.0-auth-fix
```

**Deployment time:** 3-5 minutes

---

## Step 7: Configure Environment Variables (If Not Set)

Ensure these are set in Azure Container Apps:

```bash
az containerapp update \
  --name iaindex-api \
  --resource-group aiindex-rg \
  --set-env-vars \
    SUPABASE_URL="https://casuupkmbqytgqnksnwd.supabase.co" \
    SUPABASE_KEY="your-anon-key" \
    SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

---

## What This Fixes

### Before (Broken):
```
User Registration → Insert into public.users → ❌ FAIL (table managed by Supabase)
```

### After (Working):
```
User Registration → Supabase Auth (auth.users) → ✅ SUCCESS
                  ↓
                  Trigger auto-creates profile → public.profiles → ✅ SUCCESS
```

---

## Benefits of This Approach

1. **Proper Supabase Integration** - Uses built-in auth system
2. **Email Verification** - Built-in, no custom code needed
3. **Password Reset** - Built-in magic link
4. **Social Auth Ready** - Can add Google, GitHub, etc. easily
5. **Admin Dashboard** - Manage users in Supabase Dashboard
6. **Security** - Supabase handles password hashing, token management
7. **Scalable** - Proven auth system used by thousands of apps

---

## RLS Policies Explained

### profiles table:
- ✅ `profiles_select_own` - Users can read their own profile (auth.uid() = id)
- ✅ `profiles_update_own` - Users can update their own profile
- ✅ `profiles_service_insert` - Service role can create profiles (during registration)

### Other tables:
- ✅ All tables now reference `profiles(id)` instead of `users(id)`
- ✅ RLS policies use `auth.uid()` to check ownership
- ✅ Service role bypasses RLS for backend operations

---

## Troubleshooting

### Issue: "User already exists" during sign up
**Cause:** Email already registered in auth.users
**Fix:** Use a different email or delete user from Supabase Dashboard

### Issue: "Profile not found" after login
**Cause:** Trigger didn't fire or profile wasn't created
**Fix:** Manually create profile:
```sql
INSERT INTO profiles (id, email)
SELECT id, email FROM auth.users WHERE email = 'user@example.com';
```

### Issue: "Invalid token" when accessing protected routes
**Cause:** Token expired or invalid
**Fix:** Login again to get new token

---

## Next Steps

After authentication is working:

1. ✅ Test registration and login
2. ✅ Verify profile creation
3. ✅ Test protected endpoints
4. Deploy frontend applications
5. Configure email templates in Supabase
6. Enable email verification requirement (optional)
7. Set up social auth providers (optional)

---

**Estimated Time:** 15-30 minutes (including deployment)

**Status After Fix:** Authentication fully functional with proper Supabase integration ✅
