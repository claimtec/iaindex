-- Find ALL triggers and functions that might be interfering
-- Run this in Supabase SQL Editor

-- 1. Find ALL triggers on auth.users (not just ours)
SELECT
    'ALL TRIGGERS ON auth.users:' as info,
    t.tgname as trigger_name,
    p.proname as function_name,
    pg_get_triggerdef(t.oid) as trigger_definition
FROM pg_trigger t
JOIN pg_proc p ON t.tgfoid = p.oid
JOIN pg_class c ON t.tgrelid = c.oid
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE n.nspname = 'auth'
AND c.relname = 'users'
AND NOT t.tgisinternal
ORDER BY t.tgname;

-- 2. Find all functions in public schema that might be triggered
SELECT
    'FUNCTIONS IN PUBLIC SCHEMA:' as info,
    proname as function_name,
    prosrc as source_code
FROM pg_proc
WHERE pronamespace = 'public'::regnamespace
AND proname LIKE '%user%' OR proname LIKE '%email%' OR proname LIKE '%profile%'
ORDER BY proname;

-- 3. Check for foreign key constraints that might be failing
SELECT
    'FOREIGN KEY CONSTRAINTS ON PROFILES:' as info,
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_name = 'profiles'
AND tc.constraint_type = 'FOREIGN KEY';

-- 4. Test if we can insert directly into auth.users (DANGEROUS - this is just a test)
SELECT 'ATTEMPTING TEST INSERT INTO AUTH.USERS:' as info;

DO $$
DECLARE
    test_id UUID := gen_random_uuid();
    test_email TEXT := 'test-' || test_id::TEXT || '@diagnostic.local';
BEGIN
    -- Try to insert directly (will fail with proper error message)
    INSERT INTO auth.users (
        instance_id,
        id,
        aud,
        role,
        email,
        encrypted_password,
        email_confirmed_at,
        raw_app_meta_data,
        raw_user_meta_data,
        created_at,
        updated_at
    ) VALUES (
        '00000000-0000-0000-0000-000000000000',
        test_id,
        'authenticated',
        'authenticated',
        test_email,
        crypt('testpassword', gen_salt('bf')),
        now(),
        '{"provider":"email","providers":["email"]}',
        '{}',
        now(),
        now()
    );

    -- Clean up if successful
    DELETE FROM auth.users WHERE id = test_id;

    RAISE NOTICE 'SUCCESS: Can insert into auth.users!';

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'FAILED: Cannot insert into auth.users';
    RAISE NOTICE 'Error: %', SQLERRM;
    RAISE NOTICE 'Detail: %', SQLSTATE;
END $$;
