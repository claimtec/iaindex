# Critical Security Fixes - Implementation Guide

**Priority:** IMMEDIATE - Deploy within 24-48 hours
**Severity:** Critical vulnerabilities that allow complete system compromise

---

## Fix #1: Remove Hardcoded Admin Credentials

### Current Vulnerable Code

**File:** `apps/api/src/main.py` (Lines 171-199)

```python
@app.post("/v1/auth/login", tags=["authentication"])
@limiter.limit(settings.rate_limit_per_minute)
async def login(request: Request, username: str, password: str):
    from .middleware.auth import AuthService

    # TODO: Implement proper authentication
    # This is a placeholder - implement database lookup and password verification
    if username == "admin" and password == "changeme":
        token = AuthService.create_access_token(
            data={"sub": username, "type": "user"}
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )
```

### Fixed Code

**File:** `apps/api/src/main.py`

Replace the entire login function with:

```python
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/v1/auth/login", tags=["authentication"], response_model=dict)
@limiter.limit("5/minute")  # Strict rate limit for auth
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Secure login endpoint with proper password hashing

    Returns JWT token for authenticated access.
    Rate limited to 5 attempts per minute to prevent brute force.
    """
    from .middleware.auth import AuthService

    try:
        # Query user from database
        user_result = supabase.table("users").select(
            "id, username, password_hash, locked_until, failed_attempts"
        ).eq("username", form_data.username).execute()

        if not user_result.data:
            # Log failed attempt with timing-safe comparison
            logger.warning(f"Login attempt for non-existent user: {form_data.username}")
            await asyncio.sleep(0.5)  # Prevent username enumeration
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user = user_result.data[0]

        # Check if account is locked
        if user.get('locked_until'):
            locked_until = datetime.fromisoformat(user['locked_until'])
            if datetime.utcnow() < locked_until:
                logger.warning(f"Login attempt for locked account: {form_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account locked until {locked_until.isoformat()}"
                )

        # Verify password
        if not pwd_context.verify(form_data.password, user['password_hash']):
            # Increment failed attempts
            failed_attempts = user.get('failed_attempts', 0) + 1

            # Lock account after 5 failed attempts
            update_data = {"failed_attempts": failed_attempts}
            if failed_attempts >= 5:
                locked_until = datetime.utcnow() + timedelta(minutes=15)
                update_data["locked_until"] = locked_until.isoformat()
                logger.error(f"Account locked after 5 failed attempts: {form_data.username}")

            supabase.table("users").update(update_data).eq("id", user['id']).execute()

            logger.warning(
                f"Failed login attempt {failed_attempts} for user: {form_data.username}"
            )

            await asyncio.sleep(0.5)  # Prevent timing attacks
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Successful login - reset failed attempts
        supabase.table("users").update({
            "failed_attempts": 0,
            "locked_until": None,
            "last_login_at": datetime.utcnow().isoformat()
        }).eq("id", user['id']).execute()

        # Create access token
        token = AuthService.create_access_token(
            data={
                "sub": user['username'],
                "user_id": user['id'],
                "type": "user"
            }
        )

        logger.info(f"Successful login for user: {form_data.username}")

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )
```

### Database Migration for Users Table

**File:** `migrations/002_add_users_table.sql`

```sql
-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE
);

-- Create index for faster lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can only view their own data
CREATE POLICY "Users can view own data"
    ON users FOR SELECT
    USING (auth.uid() = id);

-- Only service role can insert/update users
CREATE POLICY "Service role manages users"
    ON users FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create admin user (UPDATE PASSWORD IMMEDIATELY!)
-- Generate password hash: python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('CHANGE_THIS_PASSWORD'))"
INSERT INTO users (username, email, password_hash) VALUES (
    'admin',
    'admin@iaindex.com',
    '$2b$12$CHANGE_THIS_TO_REAL_HASH'
) ON CONFLICT (username) DO NOTHING;
```

---

## Fix #2: Secure JWT Secret Key

### Current Vulnerable Code

**File:** `apps/api/src/config.py` (Line 19)

```python
secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
```

### Fixed Code

**File:** `apps/api/src/config.py`

```python
import secrets
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # Security - JWT Secret
    secret_key: Optional[str] = Field(
        default=None,
        description="JWT secret key - REQUIRED in production"
    )

    # ... other settings ...

    def __post_init__(self):
        """Validate critical settings"""
        # Ensure secret_key is set
        if not self.secret_key:
            self.secret_key = os.getenv("SECRET_KEY")

        if not self.secret_key:
            if self.debug:
                # Only for local development
                self.secret_key = secrets.token_urlsafe(64)
                logger.warning(
                    "⚠️  Using auto-generated JWT secret key. "
                    "NOT suitable for production! Set SECRET_KEY environment variable."
                )
            else:
                # Fail fast in production
                raise ValueError(
                    "SECRET_KEY environment variable must be set in production. "
                    "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
                )

        # Validate secret key strength
        if len(self.secret_key) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long. "
                f"Current length: {len(self.secret_key)}"
            )
```

### Generate New Secret Key

Run this command to generate a cryptographically secure secret:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Update Environment Variables

**File:** `.env.production` (DO NOT commit to git!)

```bash
# CRITICAL: Generate new secret with command above
SECRET_KEY=<PASTE_GENERATED_SECRET_HERE>
```

### Azure Key Vault Setup

```bash
# Install Azure CLI
az login

# Create Key Vault
az keyvault create \
    --name iaindex-production-vault \
    --resource-group iaindex-rg \
    --location eastus

# Store secret
SECRET_VALUE=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
az keyvault secret set \
    --vault-name iaindex-production-vault \
    --name jwt-secret-key \
    --value "$SECRET_VALUE"

# Grant Container App access
az containerapp identity assign \
    --name iaindex-api \
    --resource-group iaindex-rg

PRINCIPAL_ID=$(az containerapp identity show \
    --name iaindex-api \
    --resource-group iaindex-rg \
    --query principalId -o tsv)

az keyvault set-policy \
    --name iaindex-production-vault \
    --object-id $PRINCIPAL_ID \
    --secret-permissions get list
```

### Update Application to Use Key Vault

**File:** `apps/api/src/config.py`

Add at the top:

```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret_from_keyvault(secret_name: str, vault_url: str = None) -> Optional[str]:
    """Retrieve secret from Azure Key Vault"""
    if not vault_url:
        vault_url = os.getenv("AZURE_KEYVAULT_URL")

    if not vault_url:
        return None

    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)
        secret = client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        logger.error(f"Failed to retrieve secret from Key Vault: {e}")
        return None

class Settings(BaseSettings):
    # Try Key Vault first, then env var
    secret_key: str = Field(
        default_factory=lambda: (
            get_secret_from_keyvault("jwt-secret-key") or
            os.getenv("SECRET_KEY") or
            None
        )
    )
```

---

## Fix #3: Implement Secure API Key Validation

### Current Vulnerable Code

**File:** `apps/api/src/middleware/auth.py` (Lines 86-98)

```python
@staticmethod
def verify_api_key(api_key: str) -> bool:
    # TODO: Implement database lookup for API keys
    return len(api_key) >= 32
```

### Fixed Code

**File:** `apps/api/src/middleware/auth.py`

Replace the `verify_api_key` method:

```python
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

class AuthService:
    """Authentication service"""

    @staticmethod
    async def verify_api_key(api_key: str, supabase: Client) -> Dict[str, Any]:
        """
        Verify API key against database

        Args:
            api_key: API key to verify
            supabase: Supabase client

        Returns:
            API key metadata if valid

        Raises:
            HTTPException: If API key is invalid
        """
        # Hash the API key for database lookup
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        try:
            # Query API key from database
            result = supabase.table("api_keys").select("*").eq(
                "key_hash", key_hash
            ).eq("active", True).execute()

            if not result.data:
                logger.warning(f"Invalid API key attempt: {key_hash[:16]}...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key",
                    headers={"WWW-Authenticate": "ApiKey"}
                )

            api_key_data = result.data[0]

            # Check expiration
            if api_key_data.get('expires_at'):
                expires_at = datetime.fromisoformat(api_key_data['expires_at'])
                if expires_at < datetime.utcnow():
                    logger.warning(
                        f"Expired API key used: {api_key_data.get('name')} "
                        f"(expired: {expires_at.isoformat()})"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="API key expired",
                        headers={"WWW-Authenticate": "ApiKey"}
                    )

            # Check rate limit
            if api_key_data.get('rate_limit'):
                # TODO: Implement rate limit checking with Redis
                pass

            # Update last used timestamp (async, don't wait)
            supabase.table("api_keys").update({
                "last_used_at": datetime.utcnow().isoformat(),
                "request_count": (api_key_data.get('request_count', 0) + 1)
            }).eq("id", api_key_data['id']).execute()

            logger.info(f"API key validated: {api_key_data.get('name')}")
            return api_key_data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"API key verification error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )

    @staticmethod
    def generate_api_key() -> tuple[str, str]:
        """
        Generate new API key

        Returns:
            Tuple of (api_key, key_hash)
        """
        # Generate cryptographically secure API key
        api_key = f"sk_live_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return api_key, key_hash
```

### Update Dependency Function

**File:** `apps/api/src/middleware/auth.py`

```python
async def get_api_key(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Dependency to verify API key or JWT token

    Returns:
        API key metadata or user info
    """
    # Try JWT first
    if credentials:
        try:
            payload = AuthService.verify_token(credentials.credentials)
            return {
                "auth_type": "jwt",
                "user_id": payload.get("user_id"),
                "username": payload.get("sub")
            }
        except HTTPException:
            pass

    # Try API key
    if api_key:
        api_key_data = await AuthService.verify_api_key(api_key, supabase)
        return {
            "auth_type": "api_key",
            "api_key_id": api_key_data['id'],
            "user_id": api_key_data.get('user_id'),
            "scopes": api_key_data.get('scopes', []),
            "name": api_key_data.get('name')
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer, ApiKey"}
    )
```

### Database Migration for API Keys

**File:** `migrations/003_add_api_keys_table.sql`

```sql
-- Create API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    scopes TEXT[] DEFAULT '{}',
    active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 1000,
    request_count BIGINT DEFAULT 0,
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_active ON api_keys(active) WHERE active = true;

-- Enable RLS
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Users can view their own API keys
CREATE POLICY "Users can view own API keys"
    ON api_keys FOR SELECT
    USING (auth.uid() = user_id);

-- Users can create their own API keys
CREATE POLICY "Users can create own API keys"
    ON api_keys FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own API keys (deactivate, rename)
CREATE POLICY "Users can update own API keys"
    ON api_keys FOR UPDATE
    USING (auth.uid() = user_id);

-- Service role can manage all API keys
CREATE POLICY "Service role manages all API keys"
    ON api_keys FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_api_keys_updated_at ON api_keys;
CREATE TRIGGER update_api_keys_updated_at
    BEFORE UPDATE ON api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL ON api_keys TO authenticated;
GRANT SELECT ON api_keys TO service_role;
```

---

## Fix #4: Rotate Exposed Supabase Credentials

### Immediate Actions

1. **Rotate Supabase Anon Key**

```bash
# In Supabase Dashboard:
# 1. Go to Settings > API
# 2. Click "Reset" on anon/public key
# 3. Copy new key
```

2. **Remove from Git History**

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# Remove production env files from git
git rm --cached apps/web/.env.production
git rm --cached apps/api/.env.production

# Update .gitignore
cat >> .gitignore << 'EOF'

# Production environment files (NEVER commit!)
*.env.production
*.env.staging
.env.local
.env

# Azure secrets
*.pfx
*.pem
keys/
EOF

# Commit changes
git add .gitignore
git commit -m "security: Remove production env files and update gitignore"

# CRITICAL: Rewrite history to remove secrets
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch apps/web/.env.production apps/api/.env.production" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (DANGER: Only if repo is not shared!)
# git push origin --force --all
```

3. **Update Environment Variables**

**For Azure Container Apps:**

```bash
# Update API environment variables
az containerapp update \
    --name iaindex-api \
    --resource-group iaindex-rg \
    --set-env-vars \
    "SECRET_KEY=secretref:jwt-secret-key" \
    "SUPABASE_URL=secretref:supabase-url" \
    "SUPABASE_KEY=secretref:supabase-anon-key" \
    "OPENAI_API_KEY=secretref:openai-api-key"

# Set secrets
az containerapp secret set \
    --name iaindex-api \
    --resource-group iaindex-rg \
    --secrets \
    jwt-secret-key="<NEW_JWT_SECRET>" \
    supabase-url="<SUPABASE_URL>" \
    supabase-anon-key="<NEW_ROTATED_KEY>" \
    openai-api-key="<OPENAI_KEY>"
```

---

## Fix #5: Fix Database RLS Policies

### Current Vulnerable Code

**File:** `migrations/001_schema_pivot_migration.sql` (Lines 129-131, 144-146, 162-164)

```sql
CREATE POLICY "System can insert mentions"
    ON ai_mentions FOR INSERT
    WITH CHECK (true);

CREATE POLICY "System can insert recommendations"
    ON recommendations FOR INSERT
    WITH CHECK (true);

GRANT ALL ON websites TO anon;
GRANT ALL ON ai_mentions TO anon;
GRANT ALL ON recommendations TO anon;
```

### Fixed Database Migration

**File:** `migrations/004_fix_rls_policies.sql`

```sql
-- CRITICAL: Fix overly permissive RLS policies

-- 1. REVOKE ALL GRANTS FROM ANONYMOUS USERS
REVOKE ALL ON websites FROM anon;
REVOKE ALL ON ai_mentions FROM anon;
REVOKE ALL ON recommendations FROM anon;
REVOKE ALL ON publishers FROM anon;
REVOKE ALL ON receipts FROM anon;
REVOKE ALL ON merkle_roots FROM anon;

-- 2. DROP DANGEROUS POLICIES
DROP POLICY IF EXISTS "System can insert mentions" ON ai_mentions;
DROP POLICY IF EXISTS "System can insert recommendations" ON recommendations;

-- 3. CREATE PROPER RLS POLICIES FOR AI_MENTIONS
CREATE POLICY "Users can insert mentions for their websites"
    ON ai_mentions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM websites
            WHERE websites.id = ai_mentions.website_id
            AND websites.user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can insert all mentions"
    ON ai_mentions FOR INSERT
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- 4. CREATE PROPER RLS POLICIES FOR RECOMMENDATIONS
CREATE POLICY "Users can insert recommendations for their websites"
    ON recommendations FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM websites
            WHERE websites.id = recommendations.website_id
            AND websites.user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can insert all recommendations"
    ON recommendations FOR INSERT
    WITH CHECK (auth.jwt()->>'role' = 'service_role');

-- 5. ADD RLS TO PUBLISHERS TABLE
ALTER TABLE publishers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Publishers can view own data"
    ON publishers FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Public can view verified publishers"
    ON publishers FOR SELECT
    USING (domain_verified = true);

CREATE POLICY "Publishers can manage own data"
    ON publishers FOR ALL
    USING (auth.uid() = user_id);

-- 6. ADD RLS TO RECEIPTS TABLE
ALTER TABLE receipts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Publishers can view their receipts"
    ON receipts FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM publishers
            WHERE publishers.domain = receipts.publisher_domain
            AND publishers.user_id = auth.uid()
        )
    );

CREATE POLICY "Publishers can insert their receipts"
    ON receipts FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM publishers
            WHERE publishers.domain = receipts.publisher_domain
            AND publishers.user_id = auth.uid()
        )
    );

-- 7. ADD RLS TO MERKLE_ROOTS TABLE (Public read-only)
ALTER TABLE merkle_roots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can view merkle roots"
    ON merkle_roots FOR SELECT
    USING (true);

CREATE POLICY "Service role can manage merkle roots"
    ON merkle_roots FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- 8. GRANT PROPER PERMISSIONS TO AUTHENTICATED USERS
GRANT SELECT, INSERT, UPDATE, DELETE ON websites TO authenticated;
GRANT SELECT, INSERT ON ai_mentions TO authenticated;
GRANT SELECT, INSERT ON recommendations TO authenticated;
GRANT SELECT ON publishers TO authenticated;
GRANT INSERT, SELECT ON receipts TO authenticated;
GRANT SELECT ON merkle_roots TO authenticated;

-- 9. GRANT SERVICE ROLE FULL ACCESS
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;

-- 10. ADD user_id TO PUBLISHERS TABLE IF NOT EXISTS
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'publishers' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE publishers ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
        CREATE INDEX idx_publishers_user_id ON publishers(user_id);
    END IF;
END $$;

-- Verify RLS is enabled on all tables
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

### Test RLS Policies

**File:** `tests/test_rls_policies.sql`

```sql
-- Test RLS policies as anonymous user
SET ROLE anon;

-- Should FAIL (no anonymous access)
INSERT INTO websites (domain, url, user_id) VALUES ('test.com', 'https://test.com', NULL);
-- Expected: ERROR: new row violates row-level security policy

-- Should FAIL (no anonymous access)
INSERT INTO ai_mentions (website_id, platform, query) VALUES (gen_random_uuid(), 'chatgpt', 'test');
-- Expected: ERROR: new row violates row-level security policy

-- Reset role
RESET ROLE;

-- Test as authenticated user
SET ROLE authenticated;
SET request.jwt.claims.sub = 'test-user-id';

-- Should SUCCEED (user owns website)
INSERT INTO websites (domain, url, user_id) VALUES ('test.com', 'https://test.com', 'test-user-id');
-- Expected: SUCCESS

RESET ROLE;
```

---

## Deployment Checklist

Before deploying these fixes to production:

- [ ] Generate new JWT secret key
- [ ] Rotate Supabase anon key
- [ ] Rotate all third-party API keys
- [ ] Set up Azure Key Vault
- [ ] Run database migrations
- [ ] Test authentication locally
- [ ] Test API key validation
- [ ] Verify RLS policies
- [ ] Remove .env files from git
- [ ] Update .gitignore
- [ ] Run security scan
- [ ] Deploy to staging
- [ ] Test on staging
- [ ] Deploy to production
- [ ] Monitor error logs
- [ ] Update documentation

---

## Emergency Rollback Plan

If issues occur after deployment:

1. **Rollback Container App:**
```bash
az containerapp revision list --name iaindex-api --resource-group iaindex-rg
az containerapp revision activate --name <previous-revision> --resource-group iaindex-rg
```

2. **Rollback Database:**
```bash
# Connect to Supabase
psql "<connection-string>"

# Rollback migration
BEGIN;
-- Drop policies created in migration 004
-- Restore previous grants
ROLLBACK;  -- or COMMIT if verified
```

3. **Restore from Backup:**
```bash
# Restore from Supabase backup
# Dashboard > Settings > Backups > Restore
```

---

**CRITICAL: Test all changes in staging environment before production deployment!**
