-- AIIndex Seed Data
-- This script populates the database with sample data for development and testing
-- PostgreSQL / Supabase compatible

-- Clear existing data (comment out for production)
TRUNCATE TABLE audit_log, daily_aggregates, receipts, publisher_keys, api_keys, publishers, clients, merkle_roots CASCADE;

-- ============================================
-- PUBLISHERS
-- ============================================

-- Insert 10 verified publishers
INSERT INTO publishers (id, domain, publisher_id, email, name, api_key_hash, verified, verification_method, verified_at, subscription_tier, metadata) VALUES
  -- 1. Tech Blog
  ('550e8400-e29b-41d4-a716-446655440000', 'example-blog.com', 'example-blog.com', 'hello@example-blog.com', 'Tech Insights Blog', '$2b$10$abcdef1234567890', true, 'dns', '2025-10-01 00:00:00+00', 'verified', '{"cms": "WordPress", "content_license": "CC BY 4.0"}'),

  -- 2. E-commerce Store
  ('550e8400-e29b-41d4-a716-446655440001', 'techgear-shop.com', 'techgear-shop.com', 'support@techgear-shop.com', 'TechGear Shop', '$2b$10$abcdef1234567891', true, 'file', '2025-10-02 00:00:00+00', 'verified', '{"platform": "Shopify", "product_count": 150}'),

  -- 3. Documentation Site
  ('550e8400-e29b-41d4-a716-446655440002', 'cloudforge-docs.dev', 'cloudforge-docs.dev', 'docs@cloudforge.dev', 'CloudForge Documentation', '$2b$10$abcdef1234567892', true, 'dns', '2025-10-03 00:00:00+00', 'verified', '{"platform": "Docusaurus", "version": "2.5.0"}'),

  -- 4. News Site
  ('550e8400-e29b-41d4-a716-446655440003', 'technews-daily.com', 'technews-daily.com', 'editor@technews-daily.com', 'TechNews Daily', '$2b$10$abcdef1234567893', true, 'meta', '2025-09-28 00:00:00+00', 'verified', '{"cms": "Ghost", "posts_count": 500}'),

  -- 5. Educational Platform
  ('550e8400-e29b-41d4-a716-446655440004', 'learncode.io', 'learncode.io', 'info@learncode.io', 'LearnCode', '$2b$10$abcdef1234567894', true, 'dns', '2025-09-25 00:00:00+00', 'enterprise', '{"platform": "Custom", "courses": 50}'),

  -- 6. API Provider
  ('550e8400-e29b-41d4-a716-446655440005', 'apiforge.dev', 'apiforge.dev', 'support@apiforge.dev', 'APIForge', '$2b$10$abcdef1234567895', true, 'dns', '2025-09-20 00:00:00+00', 'enterprise', '{"api_endpoints": 150, "rate_limit": "10000/day"}'),

  -- 7. SaaS Product
  ('550e8400-e29b-41d4-a716-446655440006', 'taskmaster.app', 'taskmaster.app', 'hello@taskmaster.app', 'TaskMaster', '$2b$10$abcdef1234567896', true, 'file', '2025-09-15 00:00:00+00', 'verified', '{"product_type": "SaaS", "users": 50000}'),

  -- 8. Research Organization
  ('550e8400-e29b-41d4-a716-446655440007', 'ai-research-lab.org', 'ai-research-lab.org', 'contact@ai-research-lab.org', 'AI Research Lab', '$2b$10$abcdef1234567897', true, 'dns', '2025-09-10 00:00:00+00', 'verified', '{"papers": 100, "datasets": 20}'),

  -- 9. Media Company
  ('550e8400-e29b-41d4-a716-446655440008', 'digitalmedia-hub.com', 'digitalmedia-hub.com', 'info@digitalmedia-hub.com', 'Digital Media Hub', '$2b$10$abcdef1234567898', true, 'meta', '2025-09-05 00:00:00+00', 'verified', '{"content_types": ["video", "audio", "text"]}'),

  -- 10. Open Source Project
  ('550e8400-e29b-41d4-a716-446655440009', 'opensource-toolkit.dev', 'opensource-toolkit.dev', 'maintainers@opensource-toolkit.dev', 'OpenSource Toolkit', '$2b$10$abcdef1234567899', true, 'dns', '2025-09-01 00:00:00+00', 'verified', '{"license": "MIT", "stars": 15000}');

-- ============================================
-- PUBLISHER KEYS (for signature verification)
-- ============================================

INSERT INTO publisher_keys (publisher_id, kid, public_key, algorithm, active) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'example-blog-2025', '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----', 'ES256', true),
  ('550e8400-e29b-41d4-a716-446655440001', 'techgear-shop-2025', '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----', 'ES256', true),
  ('550e8400-e29b-41d4-a716-446655440002', 'cloudforge-docs-2025', '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----', 'ES256', true),
  ('550e8400-e29b-41d4-a716-446655440003', 'technews-2025', '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----', 'ES256', true),
  ('550e8400-e29b-41d4-a716-446655440004', 'learncode-2025', '-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----', 'ES256', true);

-- ============================================
-- AI CLIENTS
-- ============================================

INSERT INTO clients (id, client_id, client_name, organization, verified, metadata) VALUES
  ('650e8400-e29b-41d4-a716-446655440000', 'openai-gpt4', 'GPT-4', 'OpenAI', true, '{"model": "gpt-4", "version": "2024-05"}'),
  ('650e8400-e29b-41d4-a716-446655440001', 'anthropic-claude', 'Claude', 'Anthropic', true, '{"model": "claude-3-opus", "version": "2024-02"}'),
  ('650e8400-e29b-41d4-a716-446655440002', 'google-gemini', 'Gemini Pro', 'Google', true, '{"model": "gemini-pro", "version": "1.5"}'),
  ('650e8400-e29b-41d4-a716-446655440003', 'meta-llama', 'Llama 3', 'Meta', true, '{"model": "llama-3-70b", "version": "3.0"}'),
  ('650e8400-e29b-41d4-a716-446655440004', 'perplexity-ai', 'Perplexity AI', 'Perplexity', true, '{"model": "pplx-70b-online"}'),
  ('650e8400-e29b-41d4-a716-446655440005', 'custom-crawler-1', 'Custom LLM Crawler', 'Independent', false, '{"purpose": "research"}');

-- ============================================
-- RECEIPTS (100 receipts over 30 days)
-- ============================================

-- Helper function to generate random timestamps over the past 30 days
-- We'll generate 100 receipts distributed across publishers and clients

-- Receipts for example-blog.com
INSERT INTO receipts (receipt_id, publisher_id, publisher_domain, client_id, client_name, timestamp, access_url, content_hash, signature_valid, signature_algorithm, purpose_type, commercial, raw_receipt, metadata)
SELECT
  'receipt-blog-' || generate_series || '-' || substr(md5(random()::text), 1, 8),
  '550e8400-e29b-41d4-a716-446655440000',
  'example-blog.com',
  CASE (random() * 5)::int
    WHEN 0 THEN 'openai-gpt4'
    WHEN 1 THEN 'anthropic-claude'
    WHEN 2 THEN 'google-gemini'
    WHEN 3 THEN 'meta-llama'
    WHEN 4 THEN 'perplexity-ai'
    ELSE 'custom-crawler-1'
  END,
  CASE (random() * 5)::int
    WHEN 0 THEN 'GPT-4'
    WHEN 1 THEN 'Claude'
    WHEN 2 THEN 'Gemini Pro'
    WHEN 3 THEN 'Llama 3'
    WHEN 4 THEN 'Perplexity AI'
    ELSE 'Custom LLM Crawler'
  END,
  NOW() - (random() * INTERVAL '30 days'),
  'https://example-blog.com/.well-known/ai-index.json',
  'sha256:' || substr(md5(random()::text), 1, 32),
  (random() > 0.1)::boolean, -- 90% valid signatures
  'ES256',
  CASE (random() * 3)::int
    WHEN 0 THEN 'inference'
    WHEN 1 THEN 'training'
    WHEN 2 THEN 'research'
    ELSE 'indexing'
  END,
  (random() > 0.3)::boolean, -- 70% commercial use
  jsonb_build_object(
    'version', '1.0',
    'access', jsonb_build_object(
      'status_code', 200,
      'pages_accessed', array['https://example-blog.com/posts/introduction-to-ai-agents']
    )
  ),
  jsonb_build_object('user_agent', 'AIIndexSDK/1.0', 'request_id', 'req-' || substr(md5(random()::text), 1, 16))
FROM generate_series(1, 25);

-- Receipts for techgear-shop.com
INSERT INTO receipts (receipt_id, publisher_id, publisher_domain, client_id, client_name, timestamp, access_url, content_hash, signature_valid, signature_algorithm, purpose_type, commercial, raw_receipt, metadata)
SELECT
  'receipt-shop-' || generate_series || '-' || substr(md5(random()::text), 1, 8),
  '550e8400-e29b-41d4-a716-446655440001',
  'techgear-shop.com',
  CASE (random() * 5)::int
    WHEN 0 THEN 'openai-gpt4'
    WHEN 1 THEN 'anthropic-claude'
    WHEN 2 THEN 'google-gemini'
    WHEN 3 THEN 'perplexity-ai'
    ELSE 'custom-crawler-1'
  END,
  CASE (random() * 5)::int
    WHEN 0 THEN 'GPT-4'
    WHEN 1 THEN 'Claude'
    WHEN 2 THEN 'Gemini Pro'
    WHEN 3 THEN 'Perplexity AI'
    ELSE 'Custom LLM Crawler'
  END,
  NOW() - (random() * INTERVAL '30 days'),
  'https://techgear-shop.com/.well-known/ai-index.json',
  'sha256:' || substr(md5(random()::text), 1, 32),
  (random() > 0.05)::boolean, -- 95% valid signatures
  'ES256',
  'inference', -- E-commerce mostly inference
  true, -- Always commercial for e-commerce
  jsonb_build_object(
    'version', '1.0',
    'access', jsonb_build_object(
      'status_code', 200,
      'pages_accessed', array['https://techgear-shop.com/products/mechanical-keyboard-pro']
    )
  ),
  jsonb_build_object('user_agent', 'AIIndexSDK/1.0', 'product_queries', true)
FROM generate_series(1, 30);

-- Receipts for cloudforge-docs.dev
INSERT INTO receipts (receipt_id, publisher_id, publisher_domain, client_id, client_name, timestamp, access_url, content_hash, signature_valid, signature_algorithm, purpose_type, commercial, raw_receipt, metadata)
SELECT
  'receipt-docs-' || generate_series || '-' || substr(md5(random()::text), 1, 8),
  '550e8400-e29b-41d4-a716-446655440002',
  'cloudforge-docs.dev',
  CASE (random() * 4)::int
    WHEN 0 THEN 'openai-gpt4'
    WHEN 1 THEN 'anthropic-claude'
    WHEN 2 THEN 'google-gemini'
    ELSE 'perplexity-ai'
  END,
  CASE (random() * 4)::int
    WHEN 0 THEN 'GPT-4'
    WHEN 1 THEN 'Claude'
    WHEN 2 THEN 'Gemini Pro'
    ELSE 'Perplexity AI'
  END,
  NOW() - (random() * INTERVAL '30 days'),
  'https://cloudforge-docs.dev/.well-known/ai-index.json',
  'sha256:' || substr(md5(random()::text), 1, 32),
  (random() > 0.08)::boolean, -- 92% valid signatures
  'ES256',
  CASE (random() * 2)::int
    WHEN 0 THEN 'inference'
    ELSE 'research'
  END,
  (random() > 0.5)::boolean, -- 50% commercial
  jsonb_build_object(
    'version', '1.0',
    'access', jsonb_build_object(
      'status_code', 200,
      'pages_accessed', array['https://cloudforge-docs.dev/docs/getting-started']
    )
  ),
  jsonb_build_object('user_agent', 'AIIndexSDK/1.0', 'documentation_query', true)
FROM generate_series(1, 20);

-- Receipts for other publishers
INSERT INTO receipts (receipt_id, publisher_id, publisher_domain, client_id, client_name, timestamp, access_url, content_hash, signature_valid, signature_algorithm, purpose_type, commercial, raw_receipt, metadata)
SELECT
  'receipt-misc-' || generate_series || '-' || substr(md5(random()::text), 1, 8),
  CASE (random() * 6)::int
    WHEN 0 THEN '550e8400-e29b-41d4-a716-446655440003'
    WHEN 1 THEN '550e8400-e29b-41d4-a716-446655440004'
    WHEN 2 THEN '550e8400-e29b-41d4-a716-446655440005'
    WHEN 3 THEN '550e8400-e29b-41d4-a716-446655440006'
    WHEN 4 THEN '550e8400-e29b-41d4-a716-446655440007'
    ELSE '550e8400-e29b-41d4-a716-446655440008'
  END,
  CASE (random() * 6)::int
    WHEN 0 THEN 'technews-daily.com'
    WHEN 1 THEN 'learncode.io'
    WHEN 2 THEN 'apiforge.dev'
    WHEN 3 THEN 'taskmaster.app'
    WHEN 4 THEN 'ai-research-lab.org'
    ELSE 'digitalmedia-hub.com'
  END,
  CASE (random() * 5)::int
    WHEN 0 THEN 'openai-gpt4'
    WHEN 1 THEN 'anthropic-claude'
    WHEN 2 THEN 'google-gemini'
    WHEN 3 THEN 'meta-llama'
    ELSE 'perplexity-ai'
  END,
  CASE (random() * 5)::int
    WHEN 0 THEN 'GPT-4'
    WHEN 1 THEN 'Claude'
    WHEN 2 THEN 'Gemini Pro'
    WHEN 3 THEN 'Llama 3'
    ELSE 'Perplexity AI'
  END,
  NOW() - (random() * INTERVAL '30 days'),
  'https://example.com/.well-known/ai-index.json',
  'sha256:' || substr(md5(random()::text), 1, 32),
  (random() > 0.12)::boolean, -- 88% valid signatures
  'ES256',
  CASE (random() * 3)::int
    WHEN 0 THEN 'inference'
    WHEN 1 THEN 'training'
    ELSE 'research'
  END,
  (random() > 0.4)::boolean, -- 60% commercial
  jsonb_build_object(
    'version', '1.0',
    'access', jsonb_build_object('status_code', 200)
  ),
  jsonb_build_object('user_agent', 'AIIndexSDK/1.0')
FROM generate_series(1, 25);

-- ============================================
-- API KEYS
-- ============================================

INSERT INTO api_keys (publisher_id, key_hash, key_prefix, name, scopes, active) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', '$2b$10$apikey1234567890', 'sk_blog_', 'Production API Key', ARRAY['read', 'write'], true),
  ('550e8400-e29b-41d4-a716-446655440001', '$2b$10$apikey1234567891', 'sk_shop_', 'Production API Key', ARRAY['read', 'write'], true),
  ('550e8400-e29b-41d4-a716-446655440002', '$2b$10$apikey1234567892', 'sk_docs_', 'Production API Key', ARRAY['read', 'write'], true),
  ('550e8400-e29b-41d4-a716-446655440000', '$2b$10$apikey1234567893', 'sk_blog_test_', 'Test API Key', ARRAY['read'], true),
  ('550e8400-e29b-41d4-a716-446655440001', '$2b$10$apikey1234567894', 'sk_shop_test_', 'Test API Key', ARRAY['read'], true);

-- ============================================
-- DAILY AGGREGATES (for analytics)
-- ============================================

-- Aggregate receipts by day (run the aggregate function for past 30 days)
DO $$
DECLARE
  day_offset INTEGER;
BEGIN
  FOR day_offset IN 0..29 LOOP
    PERFORM aggregate_daily_receipts((CURRENT_DATE - day_offset * INTERVAL '1 day')::DATE);
  END LOOP;
END $$;

-- ============================================
-- MERKLE ROOTS (daily attestations)
-- ============================================

-- Generate merkle roots for the past 30 days
INSERT INTO merkle_roots (date, root_hash, receipt_count, artifact_url)
SELECT
  (CURRENT_DATE - generate_series * INTERVAL '1 day')::DATE,
  'merkle_' || substr(md5(random()::text), 1, 32),
  (random() * 20)::int + 5,
  'https://artifacts.aiindex.org/' || to_char(CURRENT_DATE - generate_series * INTERVAL '1 day', 'YYYY-MM-DD') || '.json'
FROM generate_series(0, 29);

-- ============================================
-- AUDIT LOG
-- ============================================

-- Sample audit entries
INSERT INTO audit_log (publisher_id, action, resource_type, resource_id, success, metadata) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'RECEIPT_RECEIVED', 'receipt', 'receipt-blog-1', true, '{"client": "openai-gpt4"}'),
  ('550e8400-e29b-41d4-a716-446655440001', 'API_KEY_CREATED', 'api_key', 'sk_shop_test_', true, '{}'),
  ('550e8400-e29b-41d4-a716-446655440002', 'PUBLISHER_VERIFIED', 'publisher', 'cloudforge-docs.dev', true, '{"method": "dns"}'),
  ('550e8400-e29b-41d4-a716-446655440000', 'AI_INDEX_REGENERATED', 'ai_index', 'example-blog.com', true, '{}'),
  ('550e8400-e29b-41d4-a716-446655440001', 'RECEIPT_VALIDATION_FAILED', 'receipt', 'receipt-shop-invalid', false, '{"error": "invalid signature"}');

-- ============================================
-- VERIFICATION
-- ============================================

-- Display summary
SELECT
  'Publishers' as entity, COUNT(*) as count
FROM publishers
UNION ALL
SELECT 'Receipts', COUNT(*) FROM receipts
UNION ALL
SELECT 'Clients', COUNT(*) FROM clients
UNION ALL
SELECT 'Daily Aggregates', COUNT(*) FROM daily_aggregates
UNION ALL
SELECT 'Merkle Roots', COUNT(*) FROM merkle_roots
UNION ALL
SELECT 'Publisher Keys', COUNT(*) FROM publisher_keys
UNION ALL
SELECT 'API Keys', COUNT(*) FROM api_keys
UNION ALL
SELECT 'Audit Logs', COUNT(*) FROM audit_log;

-- Display sample data
SELECT
  p.name as publisher,
  COUNT(r.id) as total_receipts,
  COUNT(r.id) FILTER (WHERE r.signature_valid = true) as valid_receipts,
  COUNT(DISTINCT r.client_id) as unique_clients
FROM publishers p
LEFT JOIN receipts r ON p.id = r.publisher_id
GROUP BY p.id, p.name
ORDER BY total_receipts DESC;
