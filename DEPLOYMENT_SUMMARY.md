# IAIndex Documentation & Security Update Summary

## ✅ Completed

### 1. FastAPI Docs Disabled in Production
Updated [/Users/dineshanchetty/Documents/claimtec/iaindex/apps/api/src/main.py](file:///Users/dineshanchetty/Documents/claimtec/iaindex/apps/api/src/main.py):
```python
# Disable interactive docs in production for security
docs_url="/docs" if settings.debug else None,
redoc_url="/redoc" if settings.debug else None,
openapi_url="/openapi.json" if settings.debug else None,
```

**Result**: When `DEBUG=False` (production), FastAPI will not expose `/docs`, `/redoc`, or `/openapi.json` endpoints.

### 2. Docusaurus Config Updated
Updated all GitHub URLs in [/Users/dineshanchetty/Documents/claimtec/iaindex/apps/docs/docusaurus.config.ts](file:///Users/dineshanchetty/Documents/claimtec/iaindex/apps/docs/docusaurus.config.ts):
- `url`: `https://docs.iaindex.org` (was docs.iaindex.com)
- `organizationName`: `dineshanchetty` (was claimtec)
- All GitHub links updated to `https://github.com/dineshanchetty/iaindex`
- Edit URLs updated to point to correct paths

### 3. Public Repository README Updated
Updated [/tmp/iaindex-public/README.md](file:///tmp/iaindex-public/README.md):
- API Documentation link: `https://docs.iaindex.org` (was api.iaindex.org/docs)
- Added complete documentation link
- Added API reference link to Docusaurus docs
- Updated support section

### 4. Clean Public Repository Created
Location: `/tmp/iaindex-public`
- Contains only SDKs, CLI, WordPress plugin, and examples
- No backend code, infrastructure, or sensitive data
- 102 files committed
- Ready to push to GitHub

## ⏳ Pending Tasks

### 1. Configure Custom Domain for Docs
Add DNS records for `docs.iaindex.org`:

**CNAME Record**:
```
Name: docs
Type: CNAME
Value: green-mushroom-003870c0f.1.azurestaticapps.net.
TTL: 3600
```

**TXT Record** (for verification):
Get verification token from Azure:
```bash
az staticwebapp hostname list --name aiindex-docs --resource-group aiindex-rg
```

Then add:
```
Name: asuid.docs
Type: TXT
Value: <verification-token>
TTL: 3600
```

### 2. Bind Custom Domain in Azure
```bash
az staticwebapp hostname set \
  --name aiindex-docs \
  --resource-group aiindex-rg \
  --hostname docs.iaindex.org
```

### 3. Rebuild and Redeploy Docs
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/docs
npm run build
swa deploy build --app-name aiindex-docs --resource-group aiindex-rg --env production
```

### 4. Redeploy API (Disable /docs Endpoint)
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/api

# Build new Docker image
docker build -t aiindex-api:v1.0.1 .

# Push to Azure Container Registry (if using ACR)
# OR trigger Azure Container App revision update
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars "DEBUG=False"

# This will create a new revision with /docs disabled
```

### 5. Delete Old GitHub Repository & Push Clean One

**Step 1**: Delete old repository
1. Go to https://github.com/dineshanchetty/iaindex/settings
2. Scroll to "Danger Zone"
3. Click "Delete this repository"
4. Type `dineshanchetty/iaindex` to confirm
5. Delete

**Step 2**: Create new empty repository
1. Go to https://github.com/new
2. Name: `iaindex`
3. Description: IAIndex - Client SDKs and tools for transparent AI content tracking
4. **Public** visibility
5. Do NOT initialize with anything
6. Create

**Step 3**: Push clean repository
```bash
cd /tmp/iaindex-public
git remote add origin https://github.com/dineshanchetty/iaindex.git
git push -u origin main

# Create and push v1.0.0 tag
git tag -a v1.0.0 -m "IAIndex v1.0.0 - Initial Release"
git push origin v1.0.0

# Create release with WordPress plugin
gh release create v1.0.0 \
  --title "IAIndex v1.0.0 - Initial Release" \
  --notes "First stable release - see README.md" \
  releases/iaindex-wordpress-plugin-v1.0.0.zip
```

### 6. Rotate Exposed Credentials

⚠️ **CRITICAL**: The following credentials were exposed in the old repository:

1. **Database Password**: `Rockford@85`
2. **API SECRET_KEY**: `7c2d3451ee210eaf1208a0ba3becfef80abd5ca1ff6a47094cda84927fc053c5`
3. **Supabase Anon Key**: JWT token

**To rotate**:
```bash
# Generate new secret key
NEW_SECRET_KEY=$(openssl rand -hex 32)

# Update Azure secrets
az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets \
    "secret-key=$NEW_SECRET_KEY" \
    "database-url=<NEW_DATABASE_URL_WITH_NEW_PASSWORD>"

# Update environment variables
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars \
    "SECRET_KEY=secretref:secret-key" \
    "DATABASE_URL=secretref:database-url"
```

Change Supabase password:
1. Go to https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/settings/database
2. Change postgres password
3. Update connection string in Azure

## 📊 Architecture Overview

### Documentation Flow
```
User → docs.iaindex.org (Azure Static Web App)
     → Docusaurus site with comprehensive docs
     → Links to GitHub repo, npm packages, PyPI
```

### API Access
```
User → api.iaindex.org (Azure Container App)
     → FastAPI backend
     → /docs disabled in production (security)
     → Only API endpoints accessible
```

### GitHub Repository
```
github.com/dineshanchetty/iaindex (Public)
├── packages/
│   ├── sdk-nodejs/    (iaindex-sdk on npm)
│   ├── sdk-python/    (aiindex-sdk on PyPI)
│   ├── cli/           (iaindex-cli on npm)
│   └── wordpress-plugin/
├── examples/
│   ├── publisher-nodejs/
│   └── client-python/
└── releases/
    └── iaindex-wordpress-plugin-v1.0.0.zip
```

## 🔒 Security Improvements

1. ✅ FastAPI interactive docs disabled in production
2. ✅ Backend code not published to public GitHub
3. ✅ Infrastructure configs kept private
4. ⏳ Exposed credentials need rotation
5. ✅ Clean public repository with only client libraries

## 📚 Documentation Sites

- **docs.iaindex.org** - Complete Docusaurus documentation (pending DNS)
- **api.iaindex.org** - Production API (no /docs in production)
- **github.com/dineshanchetty/iaindex** - Public repository with SDKs

## Next Action

1. Add DNS records for `docs.iaindex.org`
2. Bind custom domain in Azure
3. Rebuild and redeploy docs
4. Delete old GitHub repo and push clean one
5. Rotate exposed credentials

All configuration files have been updated and are ready for deployment!
