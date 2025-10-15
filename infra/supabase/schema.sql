-- AIIndex Database Schema
-- PostgreSQL / Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Publishers table
CREATE TABLE publishers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain VARCHAR(255) UNIQUE NOT NULL,
    publisher_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    api_key_hash VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    verification_method VARCHAR(50), -- 'dns', 'file', 'meta'
    verified_at TIMESTAMP WITH TIME ZONE,
    subscription_tier VARCHAR(50) DEFAULT 'free', -- 'free', 'verified', 'enterprise'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Publisher keys table (for signature verification)
CREATE TABLE publisher_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publisher_id UUID REFERENCES publishers(id) ON DELETE CASCADE,
    kid VARCHAR(255) NOT NULL, -- Key ID
    public_key TEXT NOT NULL, -- PEM format
    algorithm VARCHAR(10) NOT NULL, -- 'ES256', 'RS256'
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(publisher_id, kid)
);

-- Receipts table
CREATE TABLE receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id VARCHAR(255) UNIQUE NOT NULL,
    publisher_id UUID REFERENCES publishers(id) ON DELETE CASCADE,
    publisher_domain VARCHAR(255) NOT NULL,
    client_id VARCHAR(255) NOT NULL,
    client_name VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    access_url TEXT,
    content_hash VARCHAR(255),
    response_hash VARCHAR(255), -- Hash of entire receipt
    signature_valid BOOLEAN,
    signature_algorithm VARCHAR(10),
    purpose_type VARCHAR(50), -- 'training', 'inference', 'research', etc.
    commercial BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_receipt JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'
);

-- Daily aggregates for analytics
CREATE TABLE daily_aggregates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publisher_id UUID REFERENCES publishers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_receipts INTEGER DEFAULT 0,
    valid_receipts INTEGER DEFAULT 0,
    invalid_receipts INTEGER DEFAULT 0,
    unique_clients INTEGER DEFAULT 0,
    commercial_uses INTEGER DEFAULT 0,
    client_breakdown JSONB DEFAULT '{}', -- {client_id: count}
    purpose_breakdown JSONB DEFAULT '{}', -- {purpose: count}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(publisher_id, date)
);

-- Merkle roots table (daily attestations)
CREATE TABLE merkle_roots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE UNIQUE NOT NULL,
    root_hash VARCHAR(255) NOT NULL,
    receipt_count INTEGER NOT NULL,
    artifact_url TEXT,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Client registry (known AI clients)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id VARCHAR(255) UNIQUE NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    organization VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    public_key TEXT, -- For signature verification
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- API keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publisher_id UUID REFERENCES publishers(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL, -- First few chars for identification
    name VARCHAR(255),
    scopes TEXT[] DEFAULT ARRAY['read', 'write'], -- Permission scopes
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publisher_id UUID REFERENCES publishers(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    ip_hash VARCHAR(255), -- Hashed IP for privacy
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX idx_receipts_publisher ON receipts(publisher_id);
CREATE INDEX idx_receipts_timestamp ON receipts(timestamp DESC);
CREATE INDEX idx_receipts_client ON receipts(client_id);
CREATE INDEX idx_receipts_created ON receipts(created_at DESC);
CREATE INDEX idx_receipts_valid ON receipts(signature_valid);

CREATE INDEX idx_publishers_domain ON publishers(domain);
CREATE INDEX idx_publishers_verified ON publishers(verified);

CREATE INDEX idx_aggregates_publisher_date ON daily_aggregates(publisher_id, date DESC);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_publisher ON api_keys(publisher_id);

-- Functions

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER publishers_updated_at
    BEFORE UPDATE ON publishers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Aggregate receipts daily (run via cron)
CREATE OR REPLACE FUNCTION aggregate_daily_receipts(target_date DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO daily_aggregates (
        publisher_id,
        date,
        total_receipts,
        valid_receipts,
        invalid_receipts,
        unique_clients,
        commercial_uses,
        client_breakdown,
        purpose_breakdown
    )
    SELECT
        publisher_id,
        target_date,
        COUNT(*) as total_receipts,
        COUNT(*) FILTER (WHERE signature_valid = TRUE) as valid_receipts,
        COUNT(*) FILTER (WHERE signature_valid = FALSE) as invalid_receipts,
        COUNT(DISTINCT client_id) as unique_clients,
        COUNT(*) FILTER (WHERE commercial = TRUE) as commercial_uses,
        jsonb_object_agg(client_id, client_count) as client_breakdown,
        jsonb_object_agg(purpose_type, purpose_count) as purpose_breakdown
    FROM (
        SELECT
            publisher_id,
            client_id,
            purpose_type,
            commercial,
            signature_valid,
            COUNT(*) as client_count,
            COUNT(*) as purpose_count
        FROM receipts
        WHERE DATE(timestamp) = target_date
        GROUP BY publisher_id, client_id, purpose_type, commercial, signature_valid
    ) subquery
    GROUP BY publisher_id
    ON CONFLICT (publisher_id, date) DO UPDATE SET
        total_receipts = EXCLUDED.total_receipts,
        valid_receipts = EXCLUDED.valid_receipts,
        invalid_receipts = EXCLUDED.invalid_receipts,
        unique_clients = EXCLUDED.unique_clients,
        commercial_uses = EXCLUDED.commercial_uses,
        client_breakdown = EXCLUDED.client_breakdown,
        purpose_breakdown = EXCLUDED.purpose_breakdown;
END;
$$ LANGUAGE plpgsql;

-- Row Level Security (RLS) policies

ALTER TABLE publishers ENABLE ROW LEVEL SECURITY;
ALTER TABLE receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_aggregates ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Publishers can only see their own data
CREATE POLICY publishers_select_own ON publishers
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY receipts_select_own ON receipts
    FOR SELECT USING (
        publisher_id IN (SELECT id FROM publishers WHERE auth.uid()::text = id::text)
    );

CREATE POLICY aggregates_select_own ON daily_aggregates
    FOR SELECT USING (
        publisher_id IN (SELECT id FROM publishers WHERE auth.uid()::text = id::text)
    );

-- Views

-- Publisher dashboard summary
CREATE VIEW publisher_summary AS
SELECT
    p.id,
    p.domain,
    p.publisher_id,
    p.verified,
    p.subscription_tier,
    COUNT(r.id) as total_receipts,
    COUNT(DISTINCT r.client_id) as unique_clients,
    COUNT(r.id) FILTER (WHERE r.signature_valid = TRUE) as valid_receipts,
    MAX(r.timestamp) as last_receipt_at
FROM publishers p
LEFT JOIN receipts r ON p.id = r.publisher_id
GROUP BY p.id;

-- Recent activity view
CREATE VIEW recent_receipts AS
SELECT
    r.id,
    r.receipt_id,
    r.timestamp,
    r.client_name,
    r.purpose_type,
    r.signature_valid,
    p.domain as publisher_domain
FROM receipts r
JOIN publishers p ON r.publisher_id = p.id
ORDER BY r.timestamp DESC
LIMIT 1000;
