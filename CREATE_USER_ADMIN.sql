-- Create user manually via SQL (bypass Supabase Auth UI)
-- This creates the user directly in auth.users

-- REPLACE THESE VALUES:
-- - USER_EMAIL: the email address
-- - USER_PASSWORD: the password (will be hashed)

DO $$
DECLARE
    new_user_id UUID := gen_random_uuid();
    user_email TEXT := 'dinesh@iaindex.org';  -- CHANGE THIS
    user_password TEXT := 'SecurePass123';     -- CHANGE THIS
BEGIN
    -- Insert into auth.users
    INSERT INTO auth.users (
        instance_id,
        id,
        aud,
        role,
        email,
        encrypted_password,
        email_confirmed_at,
        confirmation_sent_at,
        recovery_sent_at,
        email_change_sent_at,
        raw_app_meta_data,
        raw_user_meta_data,
        is_super_admin,
        created_at,
        updated_at,
        phone,
        phone_confirmed_at,
        phone_change,
        phone_change_sent_at,
        confirmed_at,
        email_change,
        email_change_confirm_status,
        banned_until,
        reauthentication_sent_at,
        reauthentication_token,
        is_sso_user,
        deleted_at
    ) VALUES (
        '00000000-0000-0000-0000-000000000000',
        new_user_id,
        'authenticated',
        'authenticated',
        user_email,
        crypt(user_password, gen_salt('bf')),  -- Hash the password
        now(),  -- Confirm email immediately
        now(),
        now(),
        now(),
        jsonb_build_object('provider', 'email', 'providers', array['email']),
        '{}'::jsonb,
        false,
        now(),
        now(),
        null,
        null,
        '',
        null,
        now(),
        '',
        0,
        null,
        null,
        '',
        false,
        null
    );

    -- Insert into auth.identities
    INSERT INTO auth.identities (
        id,
        user_id,
        identity_data,
        provider,
        last_sign_in_at,
        created_at,
        updated_at
    ) VALUES (
        new_user_id,
        new_user_id,
        jsonb_build_object('sub', new_user_id::text, 'email', user_email),
        'email',
        now(),
        now(),
        now()
    );

    -- Create profile
    INSERT INTO profiles (id, email, full_name, company, plan)
    VALUES (
        new_user_id,
        user_email,
        'Dinesh Anchetty',  -- CHANGE THIS
        'ClaimTec',          -- CHANGE THIS
        'free'
    );

    RAISE NOTICE '✅ SUCCESS!';
    RAISE NOTICE 'User created: %', user_email;
    RAISE NOTICE 'User ID: %', new_user_id;
    RAISE NOTICE 'Password: %', user_password;
    RAISE NOTICE '';
    RAISE NOTICE 'You can now login with these credentials!';

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE '❌ FAILED!';
    RAISE NOTICE 'Error: %', SQLERRM;
    RAISE NOTICE 'Detail: %', SQLSTATE;
END $$;
