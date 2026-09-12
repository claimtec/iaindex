-- Temporarily disable the trigger so user creation works
-- Run this in Supabase SQL Editor

-- Disable the trigger completely
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Trigger disabled';
    RAISE NOTICE '✅ Now try creating a user via Dashboard';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️ NOTE: You will need to manually create profiles after this:';
    RAISE NOTICE '';
    RAISE NOTICE 'INSERT INTO profiles (id, email, full_name, company, plan)';
    RAISE NOTICE 'SELECT id, email, ''Full Name'', ''Company'', ''free''';
    RAISE NOTICE 'FROM auth.users';
    RAISE NOTICE 'WHERE email = ''user@example.com'';';
END $$;
