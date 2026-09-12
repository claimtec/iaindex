-- Drip Campaign Tables
-- Manages automated email sequences for user onboarding and conversion

-- Main drip campaign tracking table
CREATE TABLE IF NOT EXISTS drip_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    website_url TEXT NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Nullable for non-registered users

    -- Campaign details
    campaign_type TEXT NOT NULL DEFAULT 'free_scan_conversion', -- Type of drip campaign
    current_step INTEGER DEFAULT 0, -- Current step in the sequence (0 = not started)
    total_steps INTEGER DEFAULT 5, -- Total steps in this campaign
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'unsubscribed')),

    -- Scan details (for context in emails)
    visibility_score INTEGER,
    scan_date TIMESTAMPTZ,

    -- Timing controls
    started_at TIMESTAMPTZ DEFAULT NOW(),
    next_send_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    paused_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_step CHECK (current_step >= 0 AND current_step <= total_steps)
);

-- Individual email sends within campaigns
CREATE TABLE IF NOT EXISTS drip_campaign_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES drip_campaigns(id) ON DELETE CASCADE,

    -- Email details
    step_number INTEGER NOT NULL,
    email_type TEXT NOT NULL, -- e.g., 'day1_followup', 'day3_case_study'
    subject TEXT NOT NULL,
    to_email TEXT NOT NULL,

    -- Send status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'bounced', 'opened', 'clicked')),
    scheduled_for TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,

    -- Tracking
    provider TEXT, -- 'sendgrid' or 'resend'
    provider_message_id TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Email analytics tracking
CREATE TABLE IF NOT EXISTS email_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_email_id UUID REFERENCES drip_campaign_emails(id) ON DELETE SET NULL,

    -- Email identification
    email_type TEXT NOT NULL, -- Type of email (drip, transactional, alert, etc.)
    to_email TEXT NOT NULL,
    subject TEXT,

    -- Tracking events
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    bounced_at TIMESTAMPTZ,
    complained_at TIMESTAMPTZ, -- Spam complaint
    unsubscribed_at TIMESTAMPTZ,

    -- Provider data
    provider TEXT, -- 'sendgrid', 'resend'
    provider_message_id TEXT,
    bounce_reason TEXT,
    click_url TEXT, -- URL that was clicked

    -- User context
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX idx_drip_campaigns_email ON drip_campaigns(email);
CREATE INDEX idx_drip_campaigns_status ON drip_campaigns(status);
CREATE INDEX idx_drip_campaigns_next_send ON drip_campaigns(next_send_at) WHERE status = 'active';
CREATE INDEX idx_drip_campaigns_user_id ON drip_campaigns(user_id);

CREATE INDEX idx_drip_campaign_emails_campaign_id ON drip_campaign_emails(campaign_id);
CREATE INDEX idx_drip_campaign_emails_status ON drip_campaign_emails(status);
CREATE INDEX idx_drip_campaign_emails_scheduled ON drip_campaign_emails(scheduled_for) WHERE status = 'pending';
CREATE INDEX idx_drip_campaign_emails_provider_id ON drip_campaign_emails(provider_message_id);

CREATE INDEX idx_email_analytics_email ON email_analytics(to_email);
CREATE INDEX idx_email_analytics_type ON email_analytics(email_type);
CREATE INDEX idx_email_analytics_user_id ON email_analytics(user_id);
CREATE INDEX idx_email_analytics_sent_at ON email_analytics(sent_at);
CREATE INDEX idx_email_analytics_provider_id ON email_analytics(provider_message_id);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_drip_campaign_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER drip_campaigns_updated_at
    BEFORE UPDATE ON drip_campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_drip_campaign_timestamp();

CREATE TRIGGER drip_campaign_emails_updated_at
    BEFORE UPDATE ON drip_campaign_emails
    FOR EACH ROW
    EXECUTE FUNCTION update_drip_campaign_timestamp();

-- Function to schedule next email in campaign
CREATE OR REPLACE FUNCTION schedule_next_drip_email(
    p_campaign_id UUID,
    p_days_delay INTEGER
)
RETURNS VOID AS $$
DECLARE
    v_campaign drip_campaigns%ROWTYPE;
    v_next_step INTEGER;
    v_email_type TEXT;
BEGIN
    -- Get campaign details
    SELECT * INTO v_campaign FROM drip_campaigns WHERE id = p_campaign_id;

    IF v_campaign.id IS NULL THEN
        RAISE EXCEPTION 'Campaign not found: %', p_campaign_id;
    END IF;

    -- Check if campaign is complete
    IF v_campaign.current_step >= v_campaign.total_steps THEN
        UPDATE drip_campaigns
        SET status = 'completed', completed_at = NOW()
        WHERE id = p_campaign_id;
        RETURN;
    END IF;

    -- Determine next step
    v_next_step := v_campaign.current_step + 1;

    -- Map step to email type
    v_email_type := CASE v_next_step
        WHEN 1 THEN 'day1_followup'
        WHEN 2 THEN 'day3_case_study'
        WHEN 3 THEN 'day7_discount'
        WHEN 4 THEN 'day14_urgency'
        ELSE 'unknown'
    END;

    -- Schedule the email
    INSERT INTO drip_campaign_emails (
        campaign_id,
        step_number,
        email_type,
        subject,
        to_email,
        scheduled_for
    ) VALUES (
        p_campaign_id,
        v_next_step,
        v_email_type,
        CASE v_email_type
            WHEN 'day1_followup' THEN 'Did You Review Your AI Visibility Report?'
            WHEN 'day3_case_study' THEN 'How One Company Increased AI Visibility by 127%'
            WHEN 'day7_discount' THEN 'Special Offer: 20% Off Your First Month'
            WHEN 'day14_urgency' THEN 'Your Competitors Are Pulling Ahead'
            ELSE 'IAIndex Update'
        END,
        v_campaign.email,
        NOW() + (p_days_delay || ' days')::INTERVAL
    );

    -- Update campaign
    UPDATE drip_campaigns
    SET
        current_step = v_next_step,
        next_send_at = NOW() + (p_days_delay || ' days')::INTERVAL
    WHERE id = p_campaign_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create new drip campaign for free scan users
CREATE OR REPLACE FUNCTION create_free_scan_campaign(
    p_email TEXT,
    p_website_url TEXT,
    p_visibility_score INTEGER,
    p_user_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_campaign_id UUID;
BEGIN
    -- Create campaign
    INSERT INTO drip_campaigns (
        email,
        website_url,
        user_id,
        campaign_type,
        visibility_score,
        scan_date,
        current_step,
        total_steps,
        next_send_at
    ) VALUES (
        p_email,
        p_website_url,
        p_user_id,
        'free_scan_conversion',
        p_visibility_score,
        NOW(),
        0,
        4, -- 4 follow-up emails (Day 0 is immediate PDF)
        NOW() + INTERVAL '1 day'
    )
    RETURNING id INTO v_campaign_id;

    -- Schedule Day 1 email
    PERFORM schedule_next_drip_email(v_campaign_id, 1);

    RETURN v_campaign_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get emails ready to send
CREATE OR REPLACE FUNCTION get_pending_drip_emails()
RETURNS TABLE (
    id UUID,
    campaign_id UUID,
    email_type TEXT,
    to_email TEXT,
    subject TEXT,
    website_url TEXT,
    visibility_score INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dce.id,
        dce.campaign_id,
        dce.email_type,
        dce.to_email,
        dce.subject,
        dc.website_url,
        dc.visibility_score
    FROM drip_campaign_emails dce
    JOIN drip_campaigns dc ON dc.id = dce.campaign_id
    WHERE dce.status = 'pending'
      AND dce.scheduled_for <= NOW()
      AND dc.status = 'active'
    ORDER BY dce.scheduled_for ASC
    LIMIT 100;
END;
$$ LANGUAGE plpgsql;

-- RLS Policies
ALTER TABLE drip_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE drip_campaign_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_analytics ENABLE ROW LEVEL SECURITY;

-- Users can view their own campaigns
CREATE POLICY drip_campaigns_select_own
    ON drip_campaigns
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY drip_campaign_emails_select_own
    ON drip_campaign_emails
    FOR SELECT
    USING (campaign_id IN (SELECT id FROM drip_campaigns WHERE user_id = auth.uid()));

CREATE POLICY email_analytics_select_own
    ON email_analytics
    FOR SELECT
    USING (auth.uid() = user_id);

-- Service role can manage all campaigns (for system operations)
CREATE POLICY drip_campaigns_service_all
    ON drip_campaigns
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY drip_campaign_emails_service_all
    ON drip_campaign_emails
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY email_analytics_service_all
    ON email_analytics
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Grant permissions
GRANT SELECT ON drip_campaigns TO authenticated;
GRANT SELECT ON drip_campaign_emails TO authenticated;
GRANT SELECT ON email_analytics TO authenticated;

-- Analytics views
CREATE OR REPLACE VIEW drip_campaign_stats AS
SELECT
    dc.campaign_type,
    dc.status,
    COUNT(*) as total_campaigns,
    AVG(dc.current_step) as avg_step_reached,
    COUNT(*) FILTER (WHERE dc.status = 'completed') as completed_count,
    COUNT(*) FILTER (WHERE dc.status = 'unsubscribed') as unsubscribed_count,
    AVG(EXTRACT(EPOCH FROM (dc.completed_at - dc.started_at))/86400) as avg_days_to_complete
FROM drip_campaigns dc
GROUP BY dc.campaign_type, dc.status;

CREATE OR REPLACE VIEW email_performance AS
SELECT
    dce.email_type,
    COUNT(*) as total_sent,
    COUNT(*) FILTER (WHERE dce.status = 'sent') as successfully_sent,
    COUNT(*) FILTER (WHERE dce.status = 'failed') as failed,
    COUNT(*) FILTER (WHERE dce.status = 'bounced') as bounced,
    COUNT(*) FILTER (WHERE dce.status = 'opened') as opened,
    COUNT(*) FILTER (WHERE dce.status = 'clicked') as clicked,
    ROUND(100.0 * COUNT(*) FILTER (WHERE dce.status = 'opened') / NULLIF(COUNT(*) FILTER (WHERE dce.status = 'sent'), 0), 2) as open_rate,
    ROUND(100.0 * COUNT(*) FILTER (WHERE dce.status = 'clicked') / NULLIF(COUNT(*) FILTER (WHERE dce.status = 'sent'), 0), 2) as click_rate
FROM drip_campaign_emails dce
GROUP BY dce.email_type;

GRANT SELECT ON drip_campaign_stats TO authenticated;
GRANT SELECT ON email_performance TO authenticated;

COMMENT ON TABLE drip_campaigns IS 'Automated email campaign tracking for user onboarding and conversion';
COMMENT ON TABLE drip_campaign_emails IS 'Individual email sends within drip campaigns';
COMMENT ON TABLE email_analytics IS 'Email delivery and engagement analytics';
COMMENT ON FUNCTION create_free_scan_campaign IS 'Creates a new drip campaign for free scan users';
COMMENT ON FUNCTION schedule_next_drip_email IS 'Schedules the next email in a drip campaign sequence';
COMMENT ON FUNCTION get_pending_drip_emails IS 'Returns all emails ready to be sent';
