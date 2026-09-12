-- Email Preferences Table
-- Manages user email notification preferences and unsubscribe settings

CREATE TABLE IF NOT EXISTS email_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,

    -- Subscription preferences
    marketing_emails BOOLEAN DEFAULT true,
    product_updates BOOLEAN DEFAULT true,
    weekly_reports BOOLEAN DEFAULT true,
    visibility_alerts BOOLEAN DEFAULT true,
    transactional_emails BOOLEAN DEFAULT true, -- Cannot be disabled (legal requirement)

    -- Unsubscribe settings
    unsubscribed_all BOOLEAN DEFAULT false,
    unsubscribe_token TEXT UNIQUE,
    unsubscribed_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id),
    UNIQUE(email)
);

-- Add indexes for performance
CREATE INDEX idx_email_preferences_user_id ON email_preferences(user_id);
CREATE INDEX idx_email_preferences_email ON email_preferences(email);
CREATE INDEX idx_email_preferences_unsubscribe_token ON email_preferences(unsubscribe_token);

-- Function to generate unsubscribe token
CREATE OR REPLACE FUNCTION generate_unsubscribe_token()
RETURNS TEXT AS $$
BEGIN
    RETURN encode(gen_random_bytes(32), 'base64');
END;
$$ LANGUAGE plpgsql;

-- Trigger to generate unsubscribe token on insert
CREATE OR REPLACE FUNCTION set_unsubscribe_token()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.unsubscribe_token IS NULL THEN
        NEW.unsubscribe_token := generate_unsubscribe_token();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER email_preferences_set_token
    BEFORE INSERT ON email_preferences
    FOR EACH ROW
    EXECUTE FUNCTION set_unsubscribe_token();

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_email_preferences_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER email_preferences_updated_at
    BEFORE UPDATE ON email_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_email_preferences_timestamp();

-- RLS Policies
ALTER TABLE email_preferences ENABLE ROW LEVEL SECURITY;

-- Users can view their own preferences
CREATE POLICY email_preferences_select_own
    ON email_preferences
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can update their own preferences
CREATE POLICY email_preferences_update_own
    ON email_preferences
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can insert their own preferences
CREATE POLICY email_preferences_insert_own
    ON email_preferences
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Service role can manage all preferences (for system operations)
CREATE POLICY email_preferences_service_all
    ON email_preferences
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Function to create default preferences for new users
CREATE OR REPLACE FUNCTION create_default_email_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO email_preferences (user_id, email)
    VALUES (NEW.id, NEW.email)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create default preferences when user signs up
CREATE TRIGGER create_user_email_preferences
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION create_default_email_preferences();

-- Helper view for easy querying
CREATE OR REPLACE VIEW email_preferences_summary AS
SELECT
    ep.user_id,
    ep.email,
    ep.marketing_emails,
    ep.product_updates,
    ep.weekly_reports,
    ep.visibility_alerts,
    ep.transactional_emails,
    ep.unsubscribed_all,
    ep.unsubscribed_at,
    ep.created_at,
    ep.updated_at,
    CASE
        WHEN ep.unsubscribed_all THEN 'Unsubscribed from all'
        WHEN NOT ep.marketing_emails AND NOT ep.product_updates
             AND NOT ep.weekly_reports AND NOT ep.visibility_alerts THEN 'Minimal emails'
        ELSE 'Active subscriber'
    END as subscription_status
FROM email_preferences ep;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON email_preferences TO authenticated;
GRANT SELECT ON email_preferences_summary TO authenticated;

COMMENT ON TABLE email_preferences IS 'User email notification preferences and unsubscribe settings';
COMMENT ON COLUMN email_preferences.marketing_emails IS 'Promotional and marketing emails';
COMMENT ON COLUMN email_preferences.product_updates IS 'Product announcements and updates';
COMMENT ON COLUMN email_preferences.weekly_reports IS 'Weekly visibility reports';
COMMENT ON COLUMN email_preferences.visibility_alerts IS 'Alerts for significant visibility changes';
COMMENT ON COLUMN email_preferences.transactional_emails IS 'Payment confirmations, account emails (cannot be disabled)';
COMMENT ON COLUMN email_preferences.unsubscribe_token IS 'Unique token for one-click unsubscribe links';
