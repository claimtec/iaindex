-- Diagnostic queries to find the auth issue
-- Run these in Supabase SQL Editor

-- 1. Check if auth schema exists and is accessible
SELECT 'Auth schema check:' as test;
SELECT schema_name, schema_owner
FROM information_schema.schemata
WHERE schema_name = 'auth';

-- 2. Check auth.users table structure
SELECT 'Auth.users table structure:' as test;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'auth'
AND table_name = 'users'
ORDER BY ordinal_position;

-- 3. Check for any triggers on auth.users that might be failing
SELECT 'Triggers on auth.users:' as test;
SELECT
    trigger_name,
    event_manipulation,
    action_statement
FROM information_schema.triggers
WHERE event_object_schema = 'auth'
AND event_object_table = 'users';

-- 4. Check if our handle_new_user trigger exists
SELECT 'Our custom trigger:' as test;
SELECT * FROM pg_trigger WHERE tgname = 'on_auth_user_created';

-- 5. Check if the trigger function exists and is valid
SELECT 'Trigger function:' as test;
SELECT
    proname as function_name,
    pg_get_functiondef(oid) as function_definition
FROM pg_proc
WHERE proname = 'handle_new_user';

-- 6. Try to manually insert into profiles to test permissions
SELECT 'Testing profiles table insert:' as test;
-- This will fail if there's a constraint issue
DO $$
DECLARE
    test_id UUID := gen_random_uuid();
BEGIN
    -- Try to insert a test profile
    INSERT INTO profiles (id, email, plan)
    VALUES (test_id, 'test-diagnostic@example.com', 'free');

    -- If successful, clean up
    DELETE FROM profiles WHERE id = test_id;

    RAISE NOTICE 'SUCCESS: Profiles table insert works!';
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'ERROR: Profiles table insert failed: %', SQLERRM;
END $$;

-- 7. Check RLS policies on profiles
SELECT 'RLS policies on profiles:' as test;
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'profiles';

-- 8. Check if profiles table has RLS enabled
SELECT 'RLS status on profiles:' as test;
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE tablename = 'profiles';

-- 9. List all tables in public schema
SELECT 'All tables in public schema:' as test;
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
