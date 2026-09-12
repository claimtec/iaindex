-- Simpler user creation that handles errors better
-- Run this in Supabase SQL Editor

DO $$
DECLARE
    new_user_id UUID := gen_random_uuid();
    user_email TEXT := 'dinesh@iaindex.org';
    user_password TEXT := 'SecurePass123';
BEGIN
    RAISE NOTICE 'Starting user creation for: %', user_email;

    -- Step 1: Insert into auth.users
    BEGIN
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
            updated_at,
            confirmation_token,
            recovery_token,
            email_change_token_new,
            email_change
        ) VALUES (
            '00000000-0000-0000-0000-000000000000',
            new_user_id,
            'authenticated',
            'authenticated',
            user_email,
            crypt(user_password, gen_salt('bf')),
            now(),
            '{"provider":"email","providers":["email"]}'::jsonb,
            '{}'::jsonb,
            now(),
            now(),
            '',
            '',
            '',
            ''
        );
        RAISE NOTICE '✅ Step 1: Created user in auth.users';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Step 1 FAILED: %', SQLERRM;
        RAISE EXCEPTION 'Failed at step 1';
    END;

    -- Step 2: Insert into auth.identities
    BEGIN
        INSERT INTO auth.identities (
            id,
            user_id,
            identity_data,
            provider,
            last_sign_in_at,
            created_at,
            updated_at
        ) VALUES (
            gen_random_uuid(),
            new_user_id,
            format('{"sub":"%s","email":"%s"}', new_user_id, user_email)::jsonb,
            'email',
            now(),
            now(),
            now()
        );
        RAISE NOTICE '✅ Step 2: Created identity in auth.identities';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Step 2 FAILED: %', SQLERRM;
        RAISE EXCEPTION 'Failed at step 2';
    END;

    -- Step 3: Insert/Update profile
    BEGIN
        INSERT INTO profiles (id, email, full_name, company, plan)
        VALUES (
            new_user_id,
            user_email,
            'Dinesh Anchetty',
            'ClaimTec',
            'free'
        )
        ON CONFLICT (id) DO UPDATE
        SET
            email = EXCLUDED.email,
            full_name = EXCLUDED.full_name,
            company = EXCLUDED.company,
            updated_at = now();

        RAISE NOTICE '✅ Step 3: Created/updated profile';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Step 3 FAILED: %', SQLERRM;
        -- Don't raise exception here, profile might already exist
    END;

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE '✅ SUCCESS! User created successfully';
    RAISE NOTICE '═══════════════════════════════════════';
    RAISE NOTICE 'Email: %', user_email;
    RAISE NOTICE 'Password: %', user_password;
    RAISE NOTICE 'User ID: %', new_user_id;
    RAISE NOTICE '';
    RAISE NOTICE 'You can now login!';

END $$;
