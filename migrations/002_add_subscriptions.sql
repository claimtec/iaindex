-- =====================================================
-- Migration: Add Subscriptions and Users Tables
-- Version: 002
-- Description: Creates tables for user management and subscription handling
-- =====================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- USERS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT, -- Optional, for future authentication
  stripe_customer_id TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id);

-- =====================================================
-- SUBSCRIPTIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT UNIQUE NOT NULL,
  stripe_customer_id TEXT NOT NULL,
  plan TEXT NOT NULL, -- 'starter', 'professional', 'agency'
  status TEXT NOT NULL, -- 'active', 'canceled', 'past_due', 'trialing', 'incomplete'
  current_period_start TIMESTAMPTZ NOT NULL,
  current_period_end TIMESTAMPTZ NOT NULL,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT valid_plan CHECK (plan IN ('starter', 'professional', 'agency')),
  CONSTRAINT valid_status CHECK (status IN ('active', 'canceled', 'past_due', 'trialing', 'incomplete', 'incomplete_expired', 'unpaid'))
);

-- Create indexes for subscriptions table
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer_id ON subscriptions(stripe_customer_id);

-- =====================================================
-- PAYMENT HISTORY TABLE (Optional - for audit trail)
-- =====================================================

CREATE TABLE IF NOT EXISTS payment_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
  stripe_invoice_id TEXT UNIQUE,
  amount INTEGER NOT NULL, -- Amount in cents
  currency TEXT NOT NULL DEFAULT 'usd',
  status TEXT NOT NULL, -- 'succeeded', 'failed', 'pending'
  attempt_count INTEGER DEFAULT 1,
  paid_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT valid_payment_status CHECK (status IN ('succeeded', 'failed', 'pending', 'refunded'))
);

-- Create indexes for payment_history table
CREATE INDEX IF NOT EXISTS idx_payment_history_subscription_id ON payment_history(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_stripe_invoice_id ON payment_history(stripe_invoice_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_status ON payment_history(status);

-- =====================================================
-- UPDATED_AT TRIGGERS
-- =====================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for subscriptions table
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own data
CREATE POLICY users_select_own ON users
    FOR SELECT
    USING (auth.uid() = id);

-- Policy: Users can update their own data
CREATE POLICY users_update_own ON users
    FOR UPDATE
    USING (auth.uid() = id);

-- Policy: Service role can do everything
CREATE POLICY users_all_service_role ON users
    FOR ALL
    USING (auth.role() = 'service_role');

-- Enable RLS on subscriptions table
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own subscriptions
CREATE POLICY subscriptions_select_own ON subscriptions
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Service role can do everything
CREATE POLICY subscriptions_all_service_role ON subscriptions
    FOR ALL
    USING (auth.role() = 'service_role');

-- Enable RLS on payment_history table
ALTER TABLE payment_history ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own payment history
CREATE POLICY payment_history_select_own ON payment_history
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM subscriptions
            WHERE subscriptions.id = payment_history.subscription_id
            AND subscriptions.user_id = auth.uid()
        )
    );

-- Policy: Service role can do everything
CREATE POLICY payment_history_all_service_role ON payment_history
    FOR ALL
    USING (auth.role() = 'service_role');

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to get active subscription for a user
CREATE OR REPLACE FUNCTION get_active_subscription(p_user_id UUID)
RETURNS TABLE (
    id UUID,
    plan TEXT,
    status TEXT,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.plan,
        s.status,
        s.current_period_end,
        s.cancel_at_period_end
    FROM subscriptions s
    WHERE s.user_id = p_user_id
    AND s.status = 'active'
    ORDER BY s.created_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has active subscription
CREATE OR REPLACE FUNCTION has_active_subscription(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    active_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO active_count
    FROM subscriptions
    WHERE user_id = p_user_id
    AND status = 'active';

    RETURN active_count > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get subscription limits based on plan
CREATE OR REPLACE FUNCTION get_plan_limits(p_plan TEXT)
RETURNS TABLE (
    max_websites INTEGER,
    check_frequency TEXT,
    api_access BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        CASE
            WHEN p_plan = 'starter' THEN 1
            WHEN p_plan = 'professional' THEN 5
            WHEN p_plan = 'agency' THEN 50
            ELSE 0
        END AS max_websites,
        CASE
            WHEN p_plan = 'starter' THEN 'weekly'
            WHEN p_plan = 'professional' THEN 'daily'
            WHEN p_plan = 'agency' THEN 'realtime'
            ELSE 'none'
        END AS check_frequency,
        CASE
            WHEN p_plan IN ('professional', 'agency') THEN TRUE
            ELSE FALSE
        END AS api_access;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =====================================================
-- GRANTS
-- =====================================================

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;

-- Grant table permissions
GRANT ALL ON users TO postgres, service_role;
GRANT SELECT ON users TO anon, authenticated;

GRANT ALL ON subscriptions TO postgres, service_role;
GRANT SELECT ON subscriptions TO authenticated;

GRANT ALL ON payment_history TO postgres, service_role;
GRANT SELECT ON payment_history TO authenticated;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE users IS 'User accounts with Stripe integration';
COMMENT ON TABLE subscriptions IS 'Active and historical subscriptions';
COMMENT ON TABLE payment_history IS 'Payment transaction history for audit trail';

COMMENT ON COLUMN users.stripe_customer_id IS 'Stripe customer ID for billing';
COMMENT ON COLUMN subscriptions.cancel_at_period_end IS 'Whether subscription is set to cancel at end of billing period';
COMMENT ON COLUMN payment_history.amount IS 'Payment amount in cents';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Insert migration record (if you have a migrations table)
-- INSERT INTO migrations (version, name, applied_at)
-- VALUES (2, 'add_subscriptions', NOW())
-- ON CONFLICT (version) DO NOTHING;
