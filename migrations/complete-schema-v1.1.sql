-- AIIndex v1.1 - Complete Database Schema
-- Description: Full schema including base tables + v1.1 enhancements
-- Use this for fresh installations

BEGIN;

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- BASE TABLES (v1.0)
-- ============================================================================

-- Publishers table
CREATE TABLE IF NOT EXISTS publishers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    domain VARCHAR(255) UNIQUE NOT NULL,
    domain_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    verification_method VARCHAR(50) DEFAULT 'dns',
    api_key VARCHAR(255) UNIQUE,
    webhook_url TEXT,
    webhook_secret VARCHAR(255),
    subscription_tier VARCHAR(50) DEFAULT 'free',

    -- v1.1 enhancements
    c2pa_enabled BOOLEAN DEFAULT FALSE,
    embeddings_enabled BOOLEAN DEFAULT FALSE,
    render_mode VARCHAR(20) DEFAULT 'none' CHECK (render_mode IN ('none', 'edge', 'local')),
    policy_config JSONB DEFAULT jsonb_build_object(
        'training', 'allow',
        'retrieval', 'allow',
        'attribution_required', true,
        'commercial_use', true
    ),

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Receipts table
CREATE TABLE IF NOT EXISTS receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id VARCHAR(255) UNIQUE NOT NULL,
    publisher_id UUID REFERENCES publishers(id) ON DELETE CASCADE,
    client_id VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    content_hash VARCHAR(64),
    purpose_type VARCHAR(50) CHECK (purpose_type IN ('training', 'retrieval', 'analysis')),
    commercial BOOLEAN DEFAULT FALSE,
    signature TEXT NOT NULL,
    signature_algorithm VARCHAR(50) DEFAULT 'ES256',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address_hash VARCHAR(64),
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Merkle trees table
CREATE TABLE IF NOT EXISTS merkle_roots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    root_hash VARCHAR(64) UNIQUE NOT NULL,
    leaf_count INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Merkle tree nodes (for verification)
CREATE TABLE IF NOT EXISTS merkle_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    root_id UUID REFERENCES merkle_roots(id) ON DELETE CASCADE,
    receipt_id UUID REFERENCES receipts(id) ON DELETE CASCADE,
    node_hash VARCHAR(64) NOT NULL,
    level INTEGER NOT NULL,
    position INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- v1.1 TABLES
-- ============================================================================

-- Bot reputation system
CREATE TABLE IF NOT EXISTS bot_reputation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'neutral' CHECK (status IN ('verified', 'trusted', 'neutral', 'suspicious', 'blocked')),
    reputation_score NUMERIC(5,2) DEFAULT 50.0 CHECK (reputation_score >= 0 AND reputation_score <= 100),
    violation_count INTEGER DEFAULT 0 CHECK (violation_count >= 0),
    last_violation TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    blocked_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Violation records
CREATE TABLE IF NOT EXISTS violation_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    violation_id VARCHAR(255) UNIQUE NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    violation_type VARCHAR(50) NOT NULL CHECK (violation_type IN (
        'fraud_attempt', 'invalid_signature', 'policy_violation',
        'rate_limit_abuse', 'content_scraping', 'suspicious_pattern'
    )),
    description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity >= 1 AND severity <= 10),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    CONSTRAINT fk_client FOREIGN KEY (client_id)
        REFERENCES bot_reputation(client_id) ON DELETE CASCADE
);

-- Fraud detection logs
CREATE TABLE IF NOT EXISTS fraud_detection_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id VARCHAR(255) UNIQUE NOT NULL,
    fraud_type VARCHAR(50) NOT NULL CHECK (fraud_type IN (
        'content_hash_mismatch', 'clock_skew', 'signature_reuse',
        'batch_fraud', 'duplicate_receipt', 'invalid_signature',
        'suspicious_pattern', 'rate_anomaly'
    )),
    severity INTEGER NOT NULL CHECK (severity >= 1 AND severity <= 10),
    description TEXT NOT NULL,
    client_id VARCHAR(255),
    receipt_id VARCHAR(255),
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evidence JSONB DEFAULT '{}',
    action_taken VARCHAR(100),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Merkle timestamp anchoring (Bitcoin, Ethereum, etc.)
CREATE TABLE IF NOT EXISTS merkle_timestamps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merkle_root_id UUID REFERENCES merkle_roots(id) ON DELETE CASCADE,
    blockchain VARCHAR(50) NOT NULL CHECK (blockchain IN ('bitcoin', 'ethereum', 'polygon', 'solana', 'custom')),
    transaction_hash VARCHAR(255) NOT NULL,
    block_number BIGINT,
    block_timestamp TIMESTAMP WITH TIME ZONE,
    anchor_url TEXT,
    verification_url TEXT,
    cost_usd NUMERIC(10,4),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Publishers indexes
CREATE INDEX IF NOT EXISTS idx_publishers_domain ON publishers(domain);
CREATE INDEX IF NOT EXISTS idx_publishers_user ON publishers(user_id);
CREATE INDEX IF NOT EXISTS idx_publishers_api_key ON publishers(api_key);
CREATE INDEX IF NOT EXISTS idx_publishers_verified ON publishers(domain_verified);
CREATE INDEX IF NOT EXISTS idx_publishers_policy_config ON publishers USING GIN (policy_config);

-- Receipts indexes
CREATE INDEX IF NOT EXISTS idx_receipts_publisher ON receipts(publisher_id);
CREATE INDEX IF NOT EXISTS idx_receipts_client ON receipts(client_id);
CREATE INDEX IF NOT EXISTS idx_receipts_receipt_id ON receipts(receipt_id);
CREATE INDEX IF NOT EXISTS idx_receipts_timestamp ON receipts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_receipts_purpose ON receipts(purpose_type);
CREATE INDEX IF NOT EXISTS idx_receipts_commercial ON receipts(commercial);

-- Merkle roots indexes
CREATE INDEX IF NOT EXISTS idx_merkle_roots_hash ON merkle_roots(root_hash);
CREATE INDEX IF NOT EXISTS idx_merkle_roots_timestamp ON merkle_roots(timestamp DESC);

-- Merkle nodes indexes
CREATE INDEX IF NOT EXISTS idx_merkle_nodes_root ON merkle_nodes(root_id);
CREATE INDEX IF NOT EXISTS idx_merkle_nodes_receipt ON merkle_nodes(receipt_id);

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

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp triggers
CREATE TRIGGER publishers_updated_at
    BEFORE UPDATE ON publishers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER bot_reputation_updated_at
    BEFORE UPDATE ON bot_reputation
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- SEED DATA
-- ============================================================================

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
BEGIN
    -- Get or create reputation record
    SELECT * INTO v_reputation FROM bot_reputation WHERE client_id = p_client_id;

    IF NOT FOUND THEN
        INSERT INTO bot_reputation (client_id) VALUES (p_client_id)
        RETURNING * INTO v_reputation;
    END IF;

    -- Calculate penalty
    v_penalty := CASE p_violation_type
        WHEN 'fraud_attempt' THEN 30.0
        WHEN 'invalid_signature' THEN 15.0
        WHEN 'policy_violation' THEN 10.0
        WHEN 'rate_limit_abuse' THEN 5.0
        WHEN 'content_scraping' THEN 8.0
        WHEN 'suspicious_pattern' THEN 5.0
        ELSE 5.0
    END * (p_severity / 5.0);

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
        blocked_at = CASE WHEN (reputation_score - v_penalty) < 20 THEN NOW() ELSE blocked_at END,
        updated_at = NOW()
    WHERE client_id = p_client_id;

    -- Insert violation record
    INSERT INTO violation_records (
        violation_id, client_id, violation_type, description, severity, metadata
    ) VALUES (
        p_client_id || ':' || EXTRACT(EPOCH FROM NOW()),
        p_client_id, p_violation_type, p_description, p_severity, p_metadata
    );

    RETURN (SELECT status = 'blocked' FROM bot_reputation WHERE client_id = p_client_id);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE publishers ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE merkle_roots ENABLE ROW LEVEL SECURITY;
ALTER TABLE merkle_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_reputation ENABLE ROW LEVEL SECURITY;
ALTER TABLE violation_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE fraud_detection_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE merkle_timestamps ENABLE ROW LEVEL SECURITY;

-- Service role can access all data
CREATE POLICY publishers_service ON publishers FOR ALL USING (true);
CREATE POLICY receipts_service ON receipts FOR ALL USING (true);
CREATE POLICY merkle_roots_service ON merkle_roots FOR ALL USING (true);
CREATE POLICY merkle_nodes_service ON merkle_nodes FOR ALL USING (true);
CREATE POLICY bot_reputation_service ON bot_reputation FOR ALL USING (true);
CREATE POLICY violation_records_service ON violation_records FOR ALL USING (true);
CREATE POLICY fraud_logs_service ON fraud_detection_logs FOR ALL USING (true);
CREATE POLICY merkle_timestamps_service ON merkle_timestamps FOR ALL USING (true);

-- ============================================================================
-- VIEWS FOR DASHBOARD
-- ============================================================================

-- Bot reputation summary
CREATE OR REPLACE VIEW bot_reputation_summary AS
SELECT
    status,
    COUNT(*) as client_count,
    AVG(reputation_score) as avg_score,
    SUM(violation_count) as total_violations,
    COUNT(*) FILTER (WHERE last_violation > NOW() - INTERVAL '7 days') as recent_violations
FROM bot_reputation
GROUP BY status;

-- Fraud alerts summary
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

-- Publisher policy summary
CREATE OR REPLACE VIEW publisher_policy_summary AS
SELECT
    p.id,
    p.domain,
    p.domain_verified as verified,
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
-- VERIFICATION
-- ============================================================================

SELECT 'Schema created successfully!' as message;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
