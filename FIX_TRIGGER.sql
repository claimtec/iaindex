-- Fix the handle_new_user trigger to prevent failures
-- Run this in Supabase SQL Editor

-- First, drop the existing trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Drop the existing function
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Create a simpler, more robust trigger function
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    -- Try to insert into profiles, ignore if it fails
    INSERT INTO public.profiles (id, email, email_verified)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.email_confirmed_at IS NOT NULL
    )
    ON CONFLICT (id) DO NOTHING;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        -- Log the error but don't fail the user creation
        RAISE WARNING 'Failed to create profile for user %: %', NEW.id, SQLERRM;
        RETURN NEW;
END;
$$;

-- Recreate the trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Test message
DO $$
BEGIN
    RAISE NOTICE '✅ Trigger recreated with error handling';
    RAISE NOTICE '✅ Now try creating a user via Dashboard';
    RAISE NOTICE '';
    RAISE NOTICE 'If it still fails, run this to disable the trigger completely:';
    RAISE NOTICE 'DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;';
END $$;
