-- Create profiles table to extend Supabase auth.users
-- This is the proper way to handle user data in Supabase

-- Drop the old users table (it was incorrectly created in public schema)
DROP TABLE IF EXISTS users CASCADE;

-- Create profiles table linked to auth.users
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    company VARCHAR(100),
    plan VARCHAR(50) DEFAULT 'free',
    stripe_customer_id VARCHAR(255) UNIQUE,
    email_verified BOOLEAN DEFAULT FALSE,
    email_notifications BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_stripe_customer ON profiles(stripe_customer_id);
CREATE INDEX idx_profiles_plan ON profiles(plan);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users can read their own profile
CREATE POLICY profiles_select_own ON profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY profiles_update_own ON profiles
    FOR UPDATE
    USING (auth.uid() = id);

-- Service role can insert profiles (during registration)
CREATE POLICY profiles_service_insert ON profiles
    FOR INSERT
    WITH CHECK (true);

-- Trigger to auto-create profile when user signs up via Supabase Auth
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, email_verified)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.email_confirmed_at IS NOT NULL
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger on auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Update existing tables to reference profiles instead of users
ALTER TABLE subscriptions DROP CONSTRAINT IF EXISTS subscriptions_user_id_fkey;
ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

ALTER TABLE websites DROP CONSTRAINT IF EXISTS websites_user_id_fkey;
ALTER TABLE websites ADD CONSTRAINT websites_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

ALTER TABLE usage_tracking DROP CONSTRAINT IF EXISTS usage_tracking_user_id_fkey;
ALTER TABLE usage_tracking ADD CONSTRAINT usage_tracking_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

ALTER TABLE api_keys DROP CONSTRAINT IF EXISTS api_keys_user_id_fkey;
ALTER TABLE api_keys ADD CONSTRAINT api_keys_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

ALTER TABLE reports DROP CONSTRAINT IF EXISTS reports_user_id_fkey;
ALTER TABLE reports ADD CONSTRAINT reports_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;

-- Update RLS policies to use profiles
DROP POLICY IF EXISTS subscriptions_select_own ON subscriptions;
CREATE POLICY subscriptions_select_own ON subscriptions
    FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS websites_select_own ON websites;
CREATE POLICY websites_select_own ON websites
    FOR SELECT
    USING (user_id = auth.uid() OR user_id IS NULL);

DROP POLICY IF EXISTS websites_insert_own ON websites;
CREATE POLICY websites_insert_own ON websites
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS websites_update_own ON websites;
CREATE POLICY websites_update_own ON websites
    FOR UPDATE
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS websites_delete_own ON websites;
CREATE POLICY websites_delete_own ON websites
    FOR DELETE
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS usage_tracking_select_own ON usage_tracking;
CREATE POLICY usage_tracking_select_own ON usage_tracking
    FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS api_keys_select_own ON api_keys;
CREATE POLICY api_keys_select_own ON api_keys
    FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS api_keys_insert_own ON api_keys;
CREATE POLICY api_keys_insert_own ON api_keys
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS api_keys_update_own ON api_keys;
CREATE POLICY api_keys_update_own ON api_keys
    FOR UPDATE
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS api_keys_delete_own ON api_keys;
CREATE POLICY api_keys_delete_own ON api_keys
    FOR DELETE
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS reports_select_own ON reports;
CREATE POLICY reports_select_own ON reports
    FOR SELECT
    USING (user_id = auth.uid());

DROP POLICY IF EXISTS reports_insert_own ON reports;
CREATE POLICY reports_insert_own ON reports
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT SELECT, UPDATE ON profiles TO authenticated;
GRANT ALL ON profiles TO service_role;

-- Comments
COMMENT ON TABLE profiles IS 'User profiles extending auth.users with application-specific data';
COMMENT ON COLUMN profiles.id IS 'References auth.users(id)';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Profiles table created successfully!';
    RAISE NOTICE 'Trigger created to auto-populate profiles from auth.users';
    RAISE NOTICE 'All foreign keys updated to reference profiles instead of users';
    RAISE NOTICE 'Next step: Update backend code to use Supabase Auth for registration/login';
END $$;
