# Enable Supabase Auth - Quick Guide

## Current Issue

The backend is trying to manually insert users into the `profiles` table, but Supabase requires users to be created via Supabase Auth first. The trigger will then automatically create the profile.

## Solution: Enable Supabase Auth Email Provider

### Step 1: Enable Email Auth in Supabase (2 minutes)

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `casuupkmbqytgqnksnwd`
3. Click **Authentication** in the left sidebar
4. Click **Providers**
5. Find **Email** provider
6. **Enable** the Email provider
7. **Confirm email** setting:
   - ✅ Enable if you want users to verify their email (recommended for production)
   - ❌ Disable for testing (users can login immediately)

**For Testing (Recommended):**
- Disable "Confirm email" requirement
- You can enable it later for production

### Step 2: Test Registration via Supabase Auth

Once email provider is enabled, you can test registration in two ways:

#### Option A: Use Supabase Auth Directly (Fastest Test)

Go to Supabase Dashboard → Authentication → Users → Add User

- Email: `test@iaindex.org`
- Password: `SecurePass123`
- Auto Confirm User: ✅ Yes

Click "Create User"

**Expected Result:**
- User created in `auth.users`
- Trigger auto-creates profile in `profiles` table

**Verify:**
```sql
-- Check auth.users
SELECT id, email, created_at FROM auth.users WHERE email = 'test@iaindex.org';

-- Check profiles (should have matching entry)
SELECT id, email, full_name, created_at FROM profiles WHERE email = 'test@iaindex.org';
```

#### Option B: Use Backend API (After Auth Enabled)

The backend needs to be updated to use Supabase Auth SDK instead of manual inserts.

**Quick Fix for Backend:**

Replace `/apps/api/src/services/auth_service.py` register_user method with:

```python
async def register_user(
    self,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    company: Optional[str] = None
) -> Dict[str, Any]:
    """Register user using Supabase Auth"""
    try:
        # Use Supabase Auth to create user
        from gotrue import SyncGoTrueClient

        # Sign up via Supabase Auth
        auth_response = self.supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if not auth_response.user:
            raise DatabaseError(detail="Failed to create user")

        user_id = str(auth_response.user.id)

        # Update profile with additional data (trigger will have created it)
        if full_name or company:
            update_data = {}
            if full_name:
                update_data["full_name"] = full_name
            if company:
                update_data["company"] = company

            self.supabase.table("profiles").update(update_data).eq("id", user_id).execute()

        # Get full profile
        result = self.supabase.table("profiles").select("*").eq("id", user_id).execute()

        return result.data[0] if result.data else {}

    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise DatabaseError(detail=f"Failed to register user: {str(e)}")
```

### Step 3: Alternative - Use Service Role Key for Manual Inserts

If you don't want to use Supabase Auth yet, you can bypass RLS by using the service role key:

**Update backend to use service role for registration:**

In `/apps/api/src/config.py`, ensure you have:
```python
supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
```

In `/apps/api/src/services/auth_service.py`:
```python
# For user creation, use service role client (bypasses RLS)
from supabase import create_client

service_supabase = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key  # Use service role instead of anon key
)

# Then use service_supabase.table("profiles").insert(...) for registration
```

### Step 4: Test After Fix

```bash
curl -X POST https://api.iaindex.org/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@iaindex.org",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

**Expected Response (Success):**
```json
{
  "user": {
    "id": "uuid-here",
    "email": "test@iaindex.org",
    "full_name": "Test User",
    "plan": "free"
  },
  "access_token": "eyJ...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

## Recommended Approach

**For Quick Testing:**
1. Enable Supabase Email Auth (Step 1)
2. Manually create a test user via Supabase Dashboard
3. Test login with that user

**For Production:**
1. Enable Supabase Email Auth
2. Update backend to use Supabase Auth SDK (use `auth_service_supabase.py`)
3. Redeploy backend
4. Test full registration flow

## Troubleshooting

### Error: "Failed to register user"
**Cause:** RLS policies blocking inserts, or Supabase Auth not enabled
**Fix:** Enable email provider OR use service role key

### Error: "relation auth.users does not exist"
**Cause:** Supabase Auth not initialized
**Fix:** Enable any auth provider in Supabase Dashboard (this initializes auth.users)

### Error: "Profile not found after registration"
**Cause:** Trigger didn't fire
**Fix:** Verify trigger exists:
```sql
SELECT * FROM pg_trigger WHERE tgname = 'on_auth_user_created';
```

## Summary

**Fastest Path to Working Auth:**
1. ✅ Enable Email provider in Supabase Dashboard (2 min)
2. ✅ Create test user via Dashboard (1 min)
3. ✅ Test login with backend (1 min)

**Production Path:**
1. Enable Email provider
2. Deploy updated backend with Supabase Auth SDK
3. Configure email templates
4. Test full flow

**Current Status:** Backend deployed with `profiles` table support, just needs Supabase Auth enabled to work.
