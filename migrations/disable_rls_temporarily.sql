-- Temporary fix: Disable RLS on all auth-related tables
-- This allows the backend to register users without auth.uid() existing yet
-- You can re-enable RLS later with proper service role policies

-- Disable RLS on users table (already done, but included for completeness)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Disable RLS on subscriptions (in case user creation creates a subscription)
ALTER TABLE subscriptions DISABLE ROW LEVEL SECURITY;

-- Disable RLS on websites (users might create websites during onboarding)
ALTER TABLE websites DISABLE ROW LEVEL SECURITY;

-- Disable RLS on other user-related tables
ALTER TABLE api_keys DISABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking DISABLE ROW LEVEL SECURITY;
ALTER TABLE reports DISABLE ROW LEVEL SECURITY;

-- Disable RLS on email tables
ALTER TABLE email_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE drip_campaigns DISABLE ROW LEVEL SECURITY;

-- Verify RLS is disabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('users', 'subscriptions', 'websites', 'api_keys', 'usage_tracking', 'reports', 'email_preferences', 'drip_campaigns')
ORDER BY tablename;

-- Expected output: All tables should show rowsecurity = false
