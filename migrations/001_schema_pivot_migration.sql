-- IAIndex Schema Pivot Migration
-- Adds tables for schema markup automation and AI visibility tracking

-- Create websites table for managing publisher websites
CREATE TABLE IF NOT EXISTS websites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    domain TEXT NOT NULL,
    url TEXT NOT NULL,
    business_name TEXT,
    business_type TEXT,
    keywords TEXT[],
    location JSONB,
    schema_markup JSONB,
    visibility_score INTEGER DEFAULT 0,
    last_scraped_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, domain)
);

-- Create index for faster lookups
CREATE INDEX idx_websites_user_id ON websites(user_id);
CREATE INDEX idx_websites_domain ON websites(domain);

-- Create ai_mentions table for tracking AI search engine mentions
CREATE TABLE IF NOT EXISTS ai_mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID REFERENCES websites(id) ON DELETE CASCADE,
    platform TEXT NOT NULL, -- 'chatgpt', 'perplexity', 'claude', 'gemini'
    query TEXT NOT NULL,
    mentioned BOOLEAN DEFAULT FALSE,
    position INTEGER, -- position in response if mentioned
    context_snippet TEXT,
    checked_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_ai_mentions_website_id ON ai_mentions(website_id);
CREATE INDEX idx_ai_mentions_platform ON ai_mentions(platform);
CREATE INDEX idx_ai_mentions_checked_at ON ai_mentions(checked_at DESC);

-- Create recommendations table for optimization suggestions
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    website_id UUID REFERENCES websites(id) ON DELETE CASCADE,
    type TEXT NOT NULL, -- 'schema', 'content', 'metadata', 'seo'
    priority TEXT NOT NULL DEFAULT 'medium', -- 'critical', 'high', 'medium', 'low'
    title TEXT NOT NULL,
    description TEXT,
    action_items JSONB,
    impact_score INTEGER, -- 0-100
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_recommendations_website_id ON recommendations(website_id);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);
CREATE INDEX idx_recommendations_completed ON recommendations(completed);

-- Extend publishers table with new fields
ALTER TABLE publishers
ADD COLUMN IF NOT EXISTS business_name TEXT,
ADD COLUMN IF NOT EXISTS business_type TEXT,
ADD COLUMN IF NOT EXISTS keywords TEXT[],
ADD COLUMN IF NOT EXISTS location JSONB,
ADD COLUMN IF NOT EXISTS schema_markup JSONB,
ADD COLUMN IF NOT EXISTS visibility_score INTEGER DEFAULT 0;

-- Create updated_at trigger function if not exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
DROP TRIGGER IF EXISTS update_websites_updated_at ON websites;
CREATE TRIGGER update_websites_updated_at
    BEFORE UPDATE ON websites
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_recommendations_updated_at ON recommendations;
CREATE TRIGGER update_recommendations_updated_at
    BEFORE UPDATE ON recommendations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS)
ALTER TABLE websites ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_mentions ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for websites
CREATE POLICY "Users can view their own websites"
    ON websites FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own websites"
    ON websites FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own websites"
    ON websites FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own websites"
    ON websites FOR DELETE
    USING (auth.uid() = user_id);

-- RLS Policies for ai_mentions
CREATE POLICY "Users can view mentions for their websites"
    ON ai_mentions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM websites
            WHERE websites.id = ai_mentions.website_id
            AND websites.user_id = auth.uid()
        )
    );

CREATE POLICY "System can insert mentions"
    ON ai_mentions FOR INSERT
    WITH CHECK (true);

-- RLS Policies for recommendations
CREATE POLICY "Users can view recommendations for their websites"
    ON recommendations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM websites
            WHERE websites.id = recommendations.website_id
            AND websites.user_id = auth.uid()
        )
    );

CREATE POLICY "System can insert recommendations"
    ON recommendations FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can update recommendations for their websites"
    ON recommendations FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM websites
            WHERE websites.id = recommendations.website_id
            AND websites.user_id = auth.uid()
        )
    );

-- Grant permissions
GRANT ALL ON websites TO authenticated;
GRANT ALL ON ai_mentions TO authenticated;
GRANT ALL ON recommendations TO authenticated;
GRANT ALL ON websites TO anon;
GRANT ALL ON ai_mentions TO anon;
GRANT ALL ON recommendations TO anon;

-- Comments for documentation
COMMENT ON TABLE websites IS 'Publisher websites for schema optimization and AI visibility tracking';
COMMENT ON TABLE ai_mentions IS 'Tracks when and where websites are mentioned by AI search engines';
COMMENT ON TABLE recommendations IS 'AI-generated optimization recommendations for websites';
COMMENT ON COLUMN websites.visibility_score IS 'Overall AI visibility score (0-100)';
COMMENT ON COLUMN ai_mentions.position IS 'Position in AI response where website was mentioned';
COMMENT ON COLUMN recommendations.impact_score IS 'Expected impact of implementing recommendation (0-100)';
