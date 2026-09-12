-- Complete migration for all missing tables
-- Run this in Supabase SQL Editor to fix the registration error

-- 1. Email Preferences Table (REQUIRED for Supabase Auth)
CREATE TABLE IF NOT EXISTS email_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    marketing_emails BOOLEAN DEFAULT true,
    product_updates BOOLEAN DEFAULT true,
    weekly_reports BOOLEAN DEFAULT true,
    visibility_alerts BOOLEAN DEFAULT true,
    transactional_emails BOOLEAN DEFAULT true,
    unsubscribed_all BOOLEAN DEFAULT false,
    unsubscribe_token TEXT UNIQUE DEFAULT encode(gen_random_bytes(32), 'base64'),
    unsubscribed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id),
    UNIQUE(email)
);

-- 2. Drip Campaigns Table
CREATE TABLE IF NOT EXISTS drip_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Drip Campaign Emails Table
CREATE TABLE IF NOT EXISTS drip_campaign_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES drip_campaigns(id) ON DELETE CASCADE,
    day_offset INTEGER NOT NULL,
    subject TEXT NOT NULL,
    template_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Email Analytics Table
CREATE TABLE IF NOT EXISTS email_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    event_type TEXT NOT NULL,
    email_type TEXT,
    campaign_id UUID REFERENCES drip_campaigns(id) ON DELETE SET NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Disable RLS on all new tables for now (simplify initial setup)
ALTER TABLE email_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE drip_campaigns DISABLE ROW LEVEL SECURITY;
ALTER TABLE drip_campaign_emails DISABLE ROW LEVEL SECURITY;
ALTER TABLE email_analytics DISABLE ROW LEVEL SECURITY;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_email_preferences_user_id ON email_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_email_preferences_email ON email_preferences(email);
CREATE INDEX IF NOT EXISTS idx_drip_campaign_emails_campaign ON drip_campaign_emails(campaign_id);
CREATE INDEX IF NOT EXISTS idx_email_analytics_user_id ON email_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_email_analytics_created_at ON email_analytics(created_at);

-- Grant permissions
GRANT ALL ON email_preferences TO authenticated;
GRANT ALL ON email_preferences TO service_role;
GRANT ALL ON drip_campaigns TO authenticated;
GRANT ALL ON drip_campaigns TO service_role;
GRANT ALL ON drip_campaign_emails TO authenticated;
GRANT ALL ON drip_campaign_emails TO service_role;
GRANT ALL ON email_analytics TO authenticated;
GRANT ALL ON email_analytics TO service_role;

-- Verify tables exist
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('email_preferences', 'drip_campaigns', 'drip_campaign_emails', 'email_analytics');

    RAISE NOTICE '✅ Created % email-related tables', table_count;
    RAISE NOTICE '✅ Tables: email_preferences, drip_campaigns, drip_campaign_emails, email_analytics';
    RAISE NOTICE '✅ RLS disabled for testing';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Now try user registration again!';
    RAISE NOTICE 'curl -X POST https://api.iaindex.org/v1/auth/register -H "Content-Type: application/json" -d ''{"email":"your@email.com","password":"SecurePass123","full_name":"Your Name"}''';
END $$;
