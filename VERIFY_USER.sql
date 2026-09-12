-- Verify the user was created successfully
-- Run this in Supabase SQL Editor

-- Check auth.users
SELECT 'User in auth.users:' as check;
SELECT
    id,
    email,
    email_confirmed_at,
    created_at
FROM auth.users
WHERE email = 'dinesh@iaindex.org';

-- Check auth.identities
SELECT 'Identity in auth.identities:' as check;
SELECT
    id,
    user_id,
    provider,
    created_at
FROM auth.identities
WHERE identity_data->>'email' = 'dinesh@iaindex.org';

-- Check profiles
SELECT 'Profile in profiles:' as check;
SELECT
    id,
    email,
    full_name,
    company,
    plan,
    created_at
FROM profiles
WHERE email = 'dinesh@iaindex.org';
