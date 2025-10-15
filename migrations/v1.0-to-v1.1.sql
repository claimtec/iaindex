-- AIIndex v1.0 to v1.1 Database Migration
-- Description: Adds policy enforcement, bot reputation, fraud detection, and provenance features
-- Safe to run multiple times (idempotent)

BEGIN;

-- ============================================================================
-- PUBLISHERS TABLE ENHANCEMENTS
-- ============================================================================

-- Add new columns to publishers table for v1.1 features
DO $$
BEGIN
    -- C2PA provenance enabled flag
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'publishers' AND column_name = 'c2pa_enabled') THEN
        ALTER TABLE publishers ADD COLUMN c2pa_enabled BOOLEAN DEFAULT FALSE;
    END IF;

    -- Embeddings feature enabled flag
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'publishers' AND column_name = 'embeddings_enabled') THEN
        ALTER TABLE publishers ADD COLUMN embeddings_enabled BOOLEAN DEFAULT FALSE;
    END IF;

    -- Render mode for dynamic content (none, edge, local)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'publishers' AND column_name = 'render_mode') THEN
        ALTER TABLE publishers ADD COLUMN render_mode VARCHAR(20) DEFAULT 'none';
        ALTER TABLE publishers ADD CONSTRAINT check_render_mode
            CHECK (render_mode IN ('none', 'edge', 'local'));
    END IF;

    -- Policy configuration as JSONB
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'publishers' AND column_name = 'policy_config') THEN
        ALTER TABLE publishers ADD COLUMN policy_config JSONB DEFAULT jsonb_build_object(
            'training', 'allow',
            'retrieval', 'allow',
            'attribution_required', true,
            'commercial_use', true
        );
    END IF;
END $$;

-- ============================================================================
-- BOT REPUTATION SYSTEM
-- ============================================================================

-- Bot reputation table
CREATE TABLE IF NOT EXISTS bot_reputation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'neutral',
    reputation_score NUMERIC(5,2) DEFAULT 50.0 CHECK (reputation_score >= 0 AND reputation_score <= 100),
    violation_count INTEGER DEFAULT 0 CHECK (violation_count >= 0),
    last_violation TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    blocked_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_status CHECK (status IN ('verified', 'trusted', 'neutral', 'suspicious', 'blocked'))
);

-- Violation records table
CREATE TABLE IF NOT EXISTS violation_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    violation_id VARCHAR(255) UNIQUE NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    violation_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity >= 1 AND severity <= 10),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    CONSTRAINT fk_client FOREIGN KEY (client_id)
        REFERENCES bot_reputation(client_id) ON DELETE CASCADE,
    CONSTRAINT check_violation_type CHECK (violation_type IN (
        'fraud_attempt', 'invalid_signature', 'policy_violation',
        'rate_limit_abuse', 'content_scraping', 'suspicious_pattern'
    ))
);

-- ============================================================================
-- FRAUD DETECTION SYSTEM
-- ============================================================================

-- Fraud detection logs table
CREATE TABLE IF NOT EXISTS fraud_detection_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id VARCHAR(255) UNIQUE NOT NULL,
    fraud_type VARCHAR(50) NOT NULL,
    severity INTEGER NOT NULL CHECK (severity >= 1 AND severity <= 10),
    description TEXT NOT NULL,
    client_id VARCHAR(255),
    receipt_id VARCHAR(255),
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evidence JSONB DEFAULT '{}',
    action_taken VARCHAR(100),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT check_fraud_type CHECK (fraud_type IN (
        'content_hash_mismatch', 'clock_skew', 'signature_reuse',
        'batch_fraud', 'duplicate_receipt', 'invalid_signature',
        'suspicious_pattern', 'rate_anomaly'
    ))
);

-- ============================================================================
-- MERKLE TIMESTAMP ANCHORING
-- ============================================================================

-- Merkle timestamps for external anchoring (Bitcoin, Ethereum, etc.)
CREATE TABLE IF NOT EXISTS merkle_timestamps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merkle_root_id UUID REFERENCES merkle_roots(id) ON DELETE CASCADE,
    blockchain VARCHAR(50) NOT NULL,
    transaction_hash VARCHAR(255) NOT NULL,
    block_number BIGINT,
    block_timestamp TIMESTAMP WITH TIME ZONE,
    anchor_url TEXT,
    verification_url TEXT,
    cost_usd NUMERIC(10,4),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    CONSTRAINT check_blockchain CHECK (blockchain IN ('bitcoin', 'ethereum', 'polygon', 'solana', 'custom')),
    CONSTRAINT check_status CHECK (status IN ('pending', 'confirmed', 'failed'))
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Bot reputation indexes
CREATE INDEX IF NOT EXISTS idx_bot_reputation_client ON bot_reputation(client_id);
CREATE INDEX IF NOT EXISTS idx_bot_reputation_status ON bot_reputation(status);
CREATE INDEX IF NOT EXISTS idx_bot_reputation_score ON bot_reputation(reputation_score);
CREATE INDEX IF NOT EXISTS idx_bot_reputation_updated ON bot_reputation(updated_at DESC);

-- Violation records indexes
CREATE INDEX IF NOT EXISTS idx_violations_client ON violation_records(client_id);
CREATE INDEX IF NOT EXISTS idx_violations_type ON violation_records(violation_type);
CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violation_records(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_violations_severity ON violation_records(severity);

-- Fraud detection logs indexes
CREATE INDEX IF NOT EXISTS idx_fraud_logs_client ON fraud_detection_logs(client_id);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_receipt ON fraud_detection_logs(receipt_id);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_type ON fraud_detection_logs(fraud_type);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_detected ON fraud_detection_logs(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_severity ON fraud_detection_logs(severity);
CREATE INDEX IF NOT EXISTS idx_fraud_logs_resolved ON fraud_detection_logs(resolved);

-- Merkle timestamp indexes
CREATE INDEX IF NOT EXISTS idx_merkle_timestamps_root ON merkle_timestamps(merkle_root_id);
CREATE INDEX IF NOT EXISTS idx_merkle_timestamps_blockchain ON merkle_timestamps(blockchain);
CREATE INDEX IF NOT EXISTS idx_merkle_timestamps_status ON merkle_timestamps(status);
CREATE INDEX IF NOT EXISTS idx_merkle_timestamps_created ON merkle_timestamps(created_at DESC);

-- Enhanced receipts indexes for v1.1
CREATE INDEX IF NOT EXISTS idx_receipts_purpose ON receipts(purpose_type);
CREATE INDEX IF NOT EXISTS idx_receipts_commercial ON receipts(commercial);

-- Publishers policy config index (GIN for JSONB queries)
CREATE INDEX IF NOT EXISTS idx_publishers_policy_config ON publishers USING GIN (policy_config);

-- ============================================================================
-- UPDATE TRIGGERS
-- ============================================================================

-- Update trigger for bot_reputation
DROP TRIGGER IF EXISTS bot_reputation_updated_at ON bot_reputation;
CREATE TRIGGER bot_reputation_updated_at
    BEFORE UPDATE ON bot_reputation
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- BACKFILL DATA (Default Policies)
-- ============================================================================

-- Backfill policy_config for existing publishers (allow-all default)
UPDATE publishers
SET policy_config = jsonb_build_object(
    'training', 'allow',
    'retrieval', 'allow',
    'attribution_required', true,
    'commercial_use', true
)
WHERE policy_config IS NULL;

-- Initialize verified AI clients in bot_reputation
INSERT INTO bot_reputation (client_id, status, reputation_score, verified_at, metadata)
VALUES
    ('openai-gpt', 'verified', 100.0, NOW(), '{"name": "OpenAI GPT", "verified": true}'),
    ('anthropic-claude', 'verified', 100.0, NOW(), '{"name": "Anthropic Claude", "verified": true}'),
    ('google-gemini', 'verified', 100.0, NOW(), '{"name": "Google Gemini", "verified": true}'),
    ('meta-llama', 'verified', 100.0, NOW(), '{"name": "Meta Llama", "verified": true}'),
    ('cohere-ai', 'verified', 100.0, NOW(), '{"name": "Cohere AI", "verified": true}'),
    ('perplexity-ai', 'verified', 95.0, NOW(), '{"name": "Perplexity AI", "verified": true}'),
    ('you-com', 'verified', 95.0, NOW(), '{"name": "You.com Search", "verified": true}')
ON CONFLICT (client_id) DO NOTHING;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get client reputation
CREATE OR REPLACE FUNCTION get_client_reputation(p_client_id VARCHAR)
RETURNS TABLE (
    client_id VARCHAR,
    status VARCHAR,
    reputation_score NUMERIC,
    violation_count INTEGER,
    is_allowed BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        br.client_id,
        br.status,
        br.reputation_score,
        br.violation_count,
        (br.status != 'blocked' AND br.reputation_score >= 20.0) as is_allowed
    FROM bot_reputation br
    WHERE br.client_id = p_client_id;
END;
$$ LANGUAGE plpgsql;

-- Function to record a violation
CREATE OR REPLACE FUNCTION record_violation(
    p_client_id VARCHAR,
    p_violation_type VARCHAR,
    p_description TEXT,
    p_severity INTEGER,
    p_metadata JSONB DEFAULT '{}'
) RETURNS BOOLEAN AS $$
DECLARE
    v_reputation bot_reputation%ROWTYPE;
    v_penalty NUMERIC;
    v_should_block BOOLEAN := FALSE;
BEGIN
    -- Get or create reputation record
    SELECT * INTO v_reputation FROM bot_reputation WHERE client_id = p_client_id;

    IF NOT FOUND THEN
        INSERT INTO bot_reputation (client_id) VALUES (p_client_id)
        RETURNING * INTO v_reputation;
    END IF;

    -- Calculate penalty based on violation type
    v_penalty := CASE p_violation_type
        WHEN 'fraud_attempt' THEN 30.0
        WHEN 'invalid_signature' THEN 15.0
        WHEN 'policy_violation' THEN 10.0
        WHEN 'rate_limit_abuse' THEN 5.0
        WHEN 'content_scraping' THEN 8.0
        WHEN 'suspicious_pattern' THEN 5.0
        ELSE 5.0
    END;

    -- Apply severity multiplier
    v_penalty := v_penalty * (p_severity / 5.0);

    -- Reduce penalty for verified clients
    IF v_reputation.status = 'verified' THEN
        v_penalty := v_penalty * 0.5;
    END IF;

    -- Update reputation
    UPDATE bot_reputation
    SET
        reputation_score = GREATEST(0, reputation_score - v_penalty),
        violation_count = violation_count + 1,
        last_violation = NOW(),
        status = CASE
            WHEN (reputation_score - v_penalty) < 20 THEN 'blocked'
            WHEN (reputation_score - v_penalty) < 40 AND status != 'verified' THEN 'suspicious'
            ELSE status
        END,
        blocked_at = CASE
            WHEN (reputation_score - v_penalty) < 20 THEN NOW()
            ELSE blocked_at
        END,
        updated_at = NOW()
    WHERE client_id = p_client_id
    RETURNING * INTO v_reputation;

    -- Auto-block after 5 violations (unless verified)
    IF v_reputation.violation_count >= 5 AND v_reputation.status != 'verified' THEN
        UPDATE bot_reputation
        SET status = 'blocked', blocked_at = NOW(), updated_at = NOW()
        WHERE client_id = p_client_id;
        v_should_block := TRUE;
    END IF;

    -- Insert violation record
    INSERT INTO violation_records (
        violation_id, client_id, violation_type, description, severity, metadata
    ) VALUES (
        p_client_id || ':' || EXTRACT(EPOCH FROM NOW()),
        p_client_id, p_violation_type, p_description, p_severity, p_metadata
    );

    RETURN v_should_block;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE bot_reputation ENABLE ROW LEVEL SECURITY;
ALTER TABLE violation_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE fraud_detection_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE merkle_timestamps ENABLE ROW LEVEL SECURITY;

-- Admins can see all data (service role)
CREATE POLICY bot_reputation_admin ON bot_reputation FOR ALL USING (true);
CREATE POLICY violation_records_admin ON violation_records FOR ALL USING (true);
CREATE POLICY fraud_logs_admin ON fraud_detection_logs FOR ALL USING (true);
CREATE POLICY merkle_timestamps_admin ON merkle_timestamps FOR ALL USING (true);

-- ============================================================================
-- VIEWS FOR DASHBOARD
-- ============================================================================

-- Bot reputation summary view
CREATE OR REPLACE VIEW bot_reputation_summary AS
SELECT
    status,
    COUNT(*) as client_count,
    AVG(reputation_score) as avg_score,
    SUM(violation_count) as total_violations,
    COUNT(*) FILTER (WHERE last_violation > NOW() - INTERVAL '7 days') as recent_violations
FROM bot_reputation
GROUP BY status;

-- Fraud alerts summary view
CREATE OR REPLACE VIEW fraud_alerts_summary AS
SELECT
    fraud_type,
    COUNT(*) as alert_count,
    AVG(severity) as avg_severity,
    COUNT(*) FILTER (WHERE resolved = FALSE) as unresolved_count,
    COUNT(*) FILTER (WHERE detected_at > NOW() - INTERVAL '24 hours') as last_24h_count
FROM fraud_detection_logs
GROUP BY fraud_type
ORDER BY alert_count DESC;

-- Publisher policy summary view
CREATE OR REPLACE VIEW publisher_policy_summary AS
SELECT
    p.id,
    p.domain,
    p.verified,
    p.subscription_tier,
    p.c2pa_enabled,
    p.embeddings_enabled,
    p.render_mode,
    p.policy_config->>'training' as training_policy,
    p.policy_config->>'retrieval' as retrieval_policy,
    (p.policy_config->>'attribution_required')::boolean as attribution_required,
    (p.policy_config->>'commercial_use')::boolean as commercial_use,
    COUNT(r.id) as total_receipts,
    COUNT(r.id) FILTER (WHERE r.created_at > NOW() - INTERVAL '7 days') as receipts_last_7d
FROM publishers p
LEFT JOIN receipts r ON p.id = r.publisher_id
GROUP BY p.id;

COMMIT;

-- ============================================================================
-- MIGRATION VERIFICATION
-- ============================================================================

-- Verify all new columns exist
DO $$
BEGIN
    ASSERT (SELECT COUNT(*) FROM information_schema.columns
            WHERE table_name = 'publishers' AND column_name = 'c2pa_enabled') = 1,
            'Column publishers.c2pa_enabled not created';

    ASSERT (SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'bot_reputation') = 1,
            'Table bot_reputation not created';

    ASSERT (SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'fraud_detection_logs') = 1,
            'Table fraud_detection_logs not created';

    ASSERT (SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'merkle_timestamps') = 1,
            'Table merkle_timestamps not created';

    RAISE NOTICE 'Migration v1.0 to v1.1 completed successfully!';
END $$;
