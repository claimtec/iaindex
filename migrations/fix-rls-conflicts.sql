-- Fix RLS policy conflicts
-- The old "publishers_service" and "receipts_service" policies are interfering

-- Drop the old conflicting policies
DROP POLICY IF EXISTS "publishers_service" ON publishers;
DROP POLICY IF EXISTS "receipts_service" ON receipts;

-- Drop and recreate our public access policies to ensure they're correct
DROP POLICY IF EXISTS "Public read access to verified publishers" ON publishers;
DROP POLICY IF EXISTS "Public read access to receipts" ON receipts;

-- Recreate with correct configuration
CREATE POLICY "Public read access to verified publishers"
ON publishers FOR SELECT
TO public
USING (domain_verified = true);

CREATE POLICY "Public read access to receipts"
ON receipts FOR SELECT
TO public
USING (true);

-- For authenticated operations, create separate policies
-- (These allow authenticated users to INSERT/UPDATE/DELETE)
CREATE POLICY "Authenticated users can manage publishers"
ON publishers FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

CREATE POLICY "Authenticated users can manage receipts"
ON receipts FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);
