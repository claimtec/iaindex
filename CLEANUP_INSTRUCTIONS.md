# Repository Cleanup Instructions

## Current Status

I've created a clean public repository at `/tmp/iaindex-public` with only:
- ✅ Node.js SDK (`packages/sdk-nodejs`)
- ✅ Python SDK (`packages/sdk-python`)
- ✅ CLI tool (`packages/cli`)
- ✅ WordPress plugin (`packages/wordpress-plugin`)
- ✅ Examples (`examples/`)
- ✅ Clean README.md
- ✅ LICENSE file
- ✅ .gitignore

**All backend code, infrastructure, and sensitive files have been excluded.**

## What Was Removed

The following were NOT included in the public repository:
- ❌ Backend API code (`apps/api/`)
- ❌ Web dashboard (`apps/web/`)
- ❌ Documentation site (`apps/docs/`)
- ❌ Infrastructure configs (Terraform, Docker Compose, deploy scripts)
- ❌ .env files with real credentials
- ❌ Database migrations
- ❌ Internal documentation files
- ❌ Test files and reports
- ❌ Agent configurations

## Sensitive Data Found (Now Removed)

The old repository contained:

1. **Database credentials** in `apps/api/.env`:
   - DATABASE_URL with password: `Rockford@85`
   - SUPABASE_KEY (JWT token)

2. **API secrets** in `apps/api/.env`:
   - SECRET_KEY: `7c2d3451ee210eaf1208a0ba3becfef80abd5ca1ff6a47094cda84927fc053c5`

3. **Supabase credentials** in `apps/web/.env.local`:
   - NEXT_PUBLIC_SUPABASE_URL
   - NEXT_PUBLIC_SUPABASE_ANON_KEY

## Next Steps

### 1. Delete Old Repository

Go to: https://github.com/dineshanchetty/iaindex/settings

1. Scroll to bottom → "Danger Zone"
2. Click "Delete this repository"
3. Type `dineshanchetty/iaindex` to confirm
4. Click "I understand the consequences, delete this repository"

### 2. Create New Clean Repository

Go to: https://github.com/new

Settings:
- **Owner**: dineshanchetty
- **Repository name**: `iaindex`
- **Description**: IAIndex - Client SDKs and tools for transparent AI content tracking
- **Visibility**: **Public** ✅
- **Do NOT** check any initialization boxes (no README, .gitignore, or license)

Click **Create repository**

### 3. Deploy Clean Repository

```bash
cd /tmp/iaindex-public

# Add remote
git remote add origin https://github.com/dineshanchetty/iaindex.git

# Push to GitHub
git push -u origin main

# Create and push tag
git tag -a v1.0.0 -m "IAIndex v1.0.0 - Initial Release"
git push origin v1.0.0

# Create release with WordPress plugin
gh release create v1.0.0 \
  --title "IAIndex v1.0.0 - Initial Release" \
  --notes "First stable release of IAIndex client libraries" \
  releases/iaindex-wordpress-plugin-v1.0.0.zip
```

Or run the automated script:
```bash
cd /tmp/iaindex-public
./deploy-to-github.sh
```

### 4. Rotate Exposed Credentials

⚠️ **IMPORTANT**: The following credentials were exposed and should be rotated:

1. **Supabase Database Password**: `Rockford@85`
   - Go to: https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/settings/database
   - Change the `postgres` user password
   - Update Azure Container App secrets

2. **API SECRET_KEY**: `7c2d3451ee210eaf1208a0ba3becfef80abd5ca1ff6a47094cda84927fc053c5`
   - Generate new key: `openssl rand -hex 32`
   - Update Azure Container App secrets

3. **Supabase Anon Key**: The JWT token was exposed
   - This is less critical (it's meant to be public)
   - But consider regenerating in Supabase settings if concerned

To update Azure secrets:
```bash
az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets \
    "database-url=<NEW_DATABASE_URL>" \
    "secret-key=<NEW_SECRET_KEY>"

az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars \
    "DATABASE_URL=secretref:database-url" \
    "SECRET_KEY=secretref:secret-key"
```

### 5. Verify Clean Repository

After deployment, verify:
```bash
# Clone the new repository
git clone https://github.com/dineshanchetty/iaindex.git /tmp/verify-iaindex
cd /tmp/verify-iaindex

# Check for sensitive data
grep -r "Rockford" . || echo "✅ No passwords found"
grep -r "7c2d3451ee210eaf" . || echo "✅ No secret keys found"
grep -r "casuupkmbqytgqnksnwd" . || echo "✅ No Supabase URLs found"
find . -name ".env" | grep -v ".example" || echo "✅ No .env files found"
```

## Summary

✅ **Created clean public repository** with only client libraries
⚠️ **Old repository needs to be deleted manually**
⚠️ **Exposed credentials need to be rotated**
⚠️ **New repository needs to be pushed to GitHub**

The new repository is ready at: `/tmp/iaindex-public`
