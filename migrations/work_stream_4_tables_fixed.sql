-- Migration for Work Stream 4: Backend API Enhancements
-- This migration creates all necessary tables for authentication, user management,
-- usage tracking, reports, and API keys

-- ============================================================================
-- 0. Create schema_migrations table if it doesn't exist
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    description TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 1. Users Table (if not exists)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
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

-- Index on email for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer ON users(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see and update their own data
DROP POLICY IF EXISTS users_select_own ON users;
CREATE POLICY users_select_own ON users
    FOR SELECT
    USING (id = auth.uid()::uuid);

DROP POLICY IF EXISTS users_update_own ON users;
CREATE POLICY users_update_own ON users
    FOR UPDATE
    USING (id = auth.uid()::uuid);

-- ============================================================================
-- 2. Subscriptions Table (if not exists)
-- ============================================================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255) NOT NULL,
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- Enable RLS
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own subscriptions
DROP POLICY IF EXISTS subscriptions_select_own ON subscriptions;
CREATE POLICY subscriptions_select_own ON subscriptions
    FOR SELECT
    USING (user_id = auth.uid()::uuid);

-- ============================================================================
-- 3. Websites Table (enhance existing if needed)
-- ============================================================================
-- Add user_id if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'websites' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE websites ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
        CREATE INDEX idx_websites_user ON websites(user_id);
    END IF;
END $$;

-- Enable RLS on websites if not already enabled
ALTER TABLE websites ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only manage their own websites
DROP POLICY IF EXISTS websites_select_own ON websites;
CREATE POLICY websites_select_own ON websites
    FOR SELECT
    USING (user_id = auth.uid()::uuid OR user_id IS NULL);

DROP POLICY IF EXISTS websites_insert_own ON websites;
CREATE POLICY websites_insert_own ON websites
    FOR INSERT
    WITH CHECK (user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS websites_update_own ON websites;
CREATE POLICY websites_update_own ON websites
    FOR UPDATE
    USING (user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS websites_delete_own ON websites;
CREATE POLICY websites_delete_own ON websites
    FOR DELETE
    USING (user_id = auth.uid()::uuid);

-- ============================================================================
-- 4. Usage Tracking Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms FLOAT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_usage_user_date ON usage_tracking(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_endpoint ON usage_tracking(endpoint);
CREATE INDEX IF NOT EXISTS idx_usage_created_at ON usage_tracking(created_at DESC);

-- Enable RLS
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own usage
DROP POLICY IF EXISTS usage_tracking_select_own ON usage_tracking;
CREATE POLICY usage_tracking_select_own ON usage_tracking
    FOR SELECT
    USING (user_id = auth.uid()::uuid);

-- ============================================================================
-- 5. API Keys Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_hash TEXT NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    scopes JSONB,
    active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON api_keys(key_prefix);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(active);

-- Enable RLS
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only manage their own API keys
DROP POLICY IF EXISTS api_keys_select_own ON api_keys;
CREATE POLICY api_keys_select_own ON api_keys
    FOR SELECT
    USING (user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS api_keys_insert_own ON api_keys;
CREATE POLICY api_keys_insert_own ON api_keys
    FOR INSERT
    WITH CHECK (user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS api_keys_update_own ON api_keys;
CREATE POLICY api_keys_update_own ON api_keys
    FOR UPDATE
    USING (user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS api_keys_delete_own ON api_keys;
CREATE POLICY api_keys_delete_own ON api_keys
    FOR DELETE
    USING (user_id = auth.uid()::uuid);

-- ============================================================================
-- 6. Reports Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    website_id UUID NOT NULL REFERENCES websites(id) ON DELETE CASCADE,
    report_url TEXT NOT NULL,
    visibility_score INTEGER,
    file_size_kb INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_reports_user ON reports(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_website ON reports(website_id);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC);

-- Enable RLS
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own reports
DROP POLICY IF EXISTS reports_select_own ON reports;
CREATE POLICY reports_select_own ON reports
    FOR SELECT
    USING (user_id = auth.uid()::uuid);

DROP POLICY IF EXISTS reports_insert_own ON reports;
CREATE POLICY reports_insert_own ON reports
    FOR INSERT
    WITH CHECK (user_id = auth.uid()::uuid);

-- ============================================================================
-- 7. AI Mentions Table (enhance existing if needed)
-- ============================================================================
-- Ensure website_id relationship exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'ai_mentions'
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%website%'
    ) THEN
        -- Check if ai_mentions table exists first
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_mentions') THEN
            ALTER TABLE ai_mentions
            ADD CONSTRAINT fk_ai_mentions_website
            FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE;
        END IF;
    END IF;
END $$;

-- Enable RLS only if table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_mentions') THEN
        ALTER TABLE ai_mentions ENABLE ROW LEVEL SECURITY;
    END IF;
END $$;

-- RLS Policy: Users can see mentions for their websites
DROP POLICY IF EXISTS ai_mentions_select_own ON ai_mentions;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_mentions') THEN
        EXECUTE 'CREATE POLICY ai_mentions_select_own ON ai_mentions
            FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM websites
                    WHERE websites.id = ai_mentions.website_id
                    AND websites.user_id = auth.uid()::uuid
                )
            )';
    END IF;
END $$;

-- ============================================================================
-- 8. Recommendations Table (enhance existing if needed)
-- ============================================================================
-- Ensure website_id relationship exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'recommendations'
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%website%'
    ) THEN
        -- Check if recommendations table exists first
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'recommendations') THEN
            ALTER TABLE recommendations
            ADD CONSTRAINT fk_recommendations_website
            FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE;
        END IF;
    END IF;
END $$;

-- Enable RLS only if table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'recommendations') THEN
        ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
    END IF;
END $$;

-- RLS Policy: Users can see recommendations for their websites
DROP POLICY IF EXISTS recommendations_select_own ON recommendations;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'recommendations') THEN
        EXECUTE 'CREATE POLICY recommendations_select_own ON recommendations
            FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM websites
                    WHERE websites.id = recommendations.website_id
                    AND websites.user_id = auth.uid()::uuid
                )
            )';
    END IF;
END $$;

-- ============================================================================
-- 9. Functions and Triggers
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_api_keys_updated_at ON api_keys;
CREATE TRIGGER update_api_keys_updated_at
    BEFORE UPDATE ON api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 10. Grant Permissions
-- ============================================================================

-- Grant permissions to authenticated users (if auth.users exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'auth' AND table_name = 'users') THEN
        GRANT SELECT, INSERT, UPDATE ON users TO authenticated;
        GRANT SELECT ON subscriptions TO authenticated;
        GRANT SELECT, INSERT, UPDATE, DELETE ON websites TO authenticated;
        GRANT SELECT ON usage_tracking TO authenticated;
        GRANT SELECT, INSERT, UPDATE, DELETE ON api_keys TO authenticated;
        GRANT SELECT, INSERT ON reports TO authenticated;
        GRANT SELECT ON ai_mentions TO authenticated;
        GRANT SELECT ON recommendations TO authenticated;
    END IF;
END $$;

-- Grant permissions to service role (for backend operations)
DO $$
BEGIN
    GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
EXCEPTION
    WHEN undefined_object THEN
        -- service_role doesn't exist, skip
        NULL;
END $$;

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Insert migration record
INSERT INTO schema_migrations (version, description, executed_at)
VALUES ('004', 'Work Stream 4: Backend API enhancements - auth, users, usage tracking, reports, API keys', NOW())
ON CONFLICT (version) DO NOTHING;

-- Add comments
COMMENT ON TABLE users IS 'User accounts with authentication and profile data';
COMMENT ON TABLE subscriptions IS 'Stripe subscription records linked to users';
COMMENT ON TABLE usage_tracking IS 'API usage tracking for rate limiting and analytics';
COMMENT ON TABLE api_keys IS 'User-generated API keys for programmatic access';
COMMENT ON TABLE reports IS 'Generated PDF reports for website visibility analysis';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration 004 completed successfully!';
    RAISE NOTICE 'Created tables: users, subscriptions, usage_tracking, api_keys, reports';
    RAISE NOTICE 'Enhanced tables: websites, ai_mentions, recommendations';
    RAISE NOTICE 'Next steps: Apply email migrations (create_email_preferences.sql, create_drip_campaigns.sql)';
END $$;
