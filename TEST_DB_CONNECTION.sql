-- Test database connection and verify backend can write to users table

-- First, check if we can manually insert a user (simulating what the backend does)
INSERT INTO users (email, password_hash, full_name, plan)
VALUES (
    'test-manual@iaindex.org',
    'hashed_password_here',
    'Manual Test User',
    'free'
)
RETURNING id, email, full_name, created_at;

-- If this works, the issue is in the backend code, not the database
-- If this fails, there's still a database permission issue

-- Clean up test user
DELETE FROM users WHERE email = 'test-manual@iaindex.org';
