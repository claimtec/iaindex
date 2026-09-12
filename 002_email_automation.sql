-- ============================================================================
-- Migration 002: Email Automation Tables
-- ============================================================================
-- Description: Tables for email preferences, drip campaigns, and analytics
-- Run this AFTER 000_FRESH_PROJECT_MIGRATION.sql and 001_schema_pivot_migration.sql
-- ============================================================================

BEGIN;

-- ============================================================================
-- EMAIL PREFERENCES TABLE
-- ============================================================================

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

-- ============================================================================
-- DRIP CAMPAIGNS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS drip_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- DRIP CAMPAIGN EMAILS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS drip_campaign_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES drip_campaigns(id) ON DELETE CASCADE,
    day_offset INTEGER NOT NULL,
    subject TEXT NOT NULL,
    template_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- EMAIL ANALYTICS TABLE
-- ============================================================================

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

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_email_preferences_user_id ON email_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_email_preferences_email ON email_preferences(email);
CREATE INDEX IF NOT EXISTS idx_email_preferences_unsubscribed ON email_preferences(unsubscribed_all);
CREATE INDEX IF NOT EXISTS idx_drip_campaign_emails_campaign ON drip_campaign_emails(campaign_id);
CREATE INDEX IF NOT EXISTS idx_email_analytics_user_id ON email_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_email_analytics_created_at ON email_analytics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_email_analytics_event_type ON email_analytics(event_type);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER email_preferences_updated_at
    BEFORE UPDATE ON email_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER drip_campaigns_updated_at
    BEFORE UPDATE ON drip_campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE email_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE drip_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE drip_campaign_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_analytics ENABLE ROW LEVEL SECURITY;

-- Service role can access all email data
CREATE POLICY email_preferences_service ON email_preferences FOR ALL USING (true);
CREATE POLICY drip_campaigns_service ON drip_campaigns FOR ALL USING (true);
CREATE POLICY drip_campaign_emails_service ON drip_campaign_emails FOR ALL USING (true);
CREATE POLICY email_analytics_service ON email_analytics FOR ALL USING (true);

-- Users can view and update their own email preferences
CREATE POLICY "Users can view their own email preferences"
    ON email_preferences FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own email preferences"
    ON email_preferences FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can view drip campaigns
CREATE POLICY "Users can view drip campaigns"
    ON drip_campaigns FOR SELECT
    USING (true);

CREATE POLICY "Users can view campaign emails"
    ON drip_campaign_emails FOR SELECT
    USING (true);

-- Users can view their own email analytics
CREATE POLICY "Users can view their own email analytics"
    ON email_analytics FOR SELECT
    USING (auth.uid() = user_id);

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

GRANT ALL ON email_preferences TO authenticated;
GRANT ALL ON drip_campaigns TO authenticated;
GRANT ALL ON drip_campaign_emails TO authenticated;
GRANT ALL ON email_analytics TO authenticated;

GRANT ALL ON email_preferences TO anon;
GRANT ALL ON drip_campaigns TO anon;
GRANT ALL ON drip_campaign_emails TO anon;
GRANT ALL ON email_analytics TO anon;

-- ============================================================================
-- SEED DATA: Create default onboarding drip campaign
-- ============================================================================

INSERT INTO drip_campaigns (name, description, active)
VALUES
    ('Onboarding', 'Welcome new users and guide them through AI visibility features', true)
ON CONFLICT DO NOTHING;

-- Get the campaign ID and insert emails
DO $$
DECLARE
    campaign_id_var UUID;
BEGIN
    SELECT id INTO campaign_id_var FROM drip_campaigns WHERE name = 'Onboarding' LIMIT 1;

    IF campaign_id_var IS NOT NULL THEN
        INSERT INTO drip_campaign_emails (campaign_id, day_offset, subject, template_name)
        VALUES
            (campaign_id_var, 0, 'Welcome to IAIndex - Get Started with AI Visibility', 'onboarding_day_0'),
            (campaign_id_var, 1, 'Quick Win: Run Your First AI Visibility Scan', 'onboarding_day_1'),
            (campaign_id_var, 3, 'Understanding Your Visibility Score', 'onboarding_day_3'),
            (campaign_id_var, 7, 'Weekly Report: Your AI Visibility Progress', 'onboarding_day_7')
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT 'Migration 002 completed successfully!' as message;
SELECT
    'email_preferences' as table_name,
    COUNT(*) as row_count
FROM email_preferences
UNION ALL
SELECT 'drip_campaigns', COUNT(*) FROM drip_campaigns
UNION ALL
SELECT 'drip_campaign_emails', COUNT(*) FROM drip_campaign_emails
UNION ALL
SELECT 'email_analytics', COUNT(*) FROM email_analytics;
