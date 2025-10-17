-- Enable public read access to verified publishers
-- Run this in Supabase SQL Editor

-- Drop existing RLS policies if any
DROP POLICY IF EXISTS "Public read access to verified publishers" ON publishers;
DROP POLICY IF EXISTS "Public read access to receipts" ON receipts;

-- Enable RLS on publishers table (if not already enabled)
ALTER TABLE publishers ENABLE ROW LEVEL SECURITY;

-- Allow public read access to verified publishers
CREATE POLICY "Public read access to verified publishers"
ON publishers FOR SELECT
USING (domain_verified = true);

-- Enable RLS on receipts table (if not already enabled)
ALTER TABLE receipts ENABLE ROW LEVEL SECURITY;

-- Allow public read access to all receipts (for listing/statistics)
CREATE POLICY "Public read access to receipts"
ON receipts FOR SELECT
USING (true);

-- Note: INSERT/UPDATE/DELETE operations still require authentication
-- Only SELECT (read) operations are allowed publicly
