-- Quick fix: Create email_preferences table
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS email_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    marketing_emails BOOLEAN DEFAULT true,
    product_updates BOOLEAN DEFAULT true,
    weekly_reports BOOLEAN DEFAULT true,
    visibility_alerts BOOLEAN DEFAULT true,
    transactional_emails BOOLEAN DEFAULT true,
    unsubscribed_all BOOLEAN DEFAULT false,
    unsubscribe_token TEXT UNIQUE DEFAULT encode(gen_random_bytes(32), 'base64'),
    unsubscribed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id),
    UNIQUE(email)
);

-- Disable RLS for now (simplify testing)
ALTER TABLE email_preferences DISABLE ROW LEVEL SECURITY;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'email_preferences table created!';
    RAISE NOTICE 'Now try registration again.';
END $$;
