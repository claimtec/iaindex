-- ============================================================================
-- Migration 003: Analytics Tables
-- ============================================================================
-- Description: Tables for visibility scans, scan results, and analytics
-- Run this AFTER 002_email_automation.sql
-- ============================================================================

BEGIN;

-- ============================================================================
-- VISIBILITY SCANS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS visibility_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id TEXT UNIQUE NOT NULL,
    website_id UUID REFERENCES websites(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    overall_score INTEGER,
    chatgpt_score INTEGER,
    perplexity_score INTEGER,
    claude_score INTEGER,
    gemini_score INTEGER,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SCAN RESULTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS scan_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID REFERENCES visibility_scans(id) ON DELETE CASCADE,
    platform TEXT NOT NULL CHECK (platform IN ('chatgpt', 'perplexity', 'claude', 'gemini')),
    score INTEGER CHECK (score >= 0 AND score <= 100),
    mentioned BOOLEAN DEFAULT FALSE,
    position INTEGER,
    query TEXT,
    response_snippet TEXT,
    recommendations JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- ANALYTICS EVENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    website_id UUID REFERENCES websites(id) ON DELETE SET NULL,
    event_data JSONB DEFAULT '{}',
    session_id TEXT,
    ip_address_hash TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_visibility_scans_scan_id ON visibility_scans(scan_id);
CREATE INDEX IF NOT EXISTS idx_visibility_scans_website_id ON visibility_scans(website_id);
CREATE INDEX IF NOT EXISTS idx_visibility_scans_user_id ON visibility_scans(user_id);
CREATE INDEX IF NOT EXISTS idx_visibility_scans_status ON visibility_scans(status);
CREATE INDEX IF NOT EXISTS idx_visibility_scans_created_at ON visibility_scans(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id ON scan_results(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_results_platform ON scan_results(platform);
CREATE INDEX IF NOT EXISTS idx_scan_results_score ON scan_results(score);
CREATE INDEX IF NOT EXISTS idx_scan_results_mentioned ON scan_results(mentioned);

CREATE INDEX IF NOT EXISTS idx_analytics_events_event_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_website_id ON analytics_events(website_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_events_session_id ON analytics_events(session_id);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE visibility_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE scan_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- Service role can access all data
CREATE POLICY visibility_scans_service ON visibility_scans FOR ALL USING (true);
CREATE POLICY scan_results_service ON scan_results FOR ALL USING (true);
CREATE POLICY analytics_events_service ON analytics_events FOR ALL USING (true);

-- Users can view their own scans
CREATE POLICY "Users can view their own scans"
    ON visibility_scans FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own scans"
    ON visibility_scans FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can view scan results for their scans
CREATE POLICY "Users can view their own scan results"
    ON scan_results FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM visibility_scans
            WHERE visibility_scans.id = scan_results.scan_id
            AND visibility_scans.user_id = auth.uid()
        )
    );

-- Users can view their own analytics events
CREATE POLICY "Users can view their own analytics events"
    ON analytics_events FOR SELECT
    USING (auth.uid() = user_id);

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

GRANT ALL ON visibility_scans TO authenticated;
GRANT ALL ON scan_results TO authenticated;
GRANT ALL ON analytics_events TO authenticated;

GRANT ALL ON visibility_scans TO anon;
GRANT ALL ON scan_results TO anon;
GRANT ALL ON analytics_events TO anon;

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT 'Migration 003 completed successfully!' as message;
SELECT
    'visibility_scans' as table_name,
    COUNT(*) as row_count
FROM visibility_scans
UNION ALL
SELECT 'scan_results', COUNT(*) FROM scan_results
UNION ALL
SELECT 'analytics_events', COUNT(*) FROM analytics_events;
