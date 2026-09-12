# DNS Setup for docs.iaindex.org

## ✅ GitHub Repository Complete!

Your clean public repository is now live:
- **Repository**: https://github.com/dineshanchetty/iaindex
- **Release**: https://github.com/dineshanchetty/iaindex/releases/tag/v1.0.0
- **WordPress Plugin**: Attached to v1.0.0 release

## 📋 Next Step: Configure docs.iaindex.org

### DNS Records to Add

Go to your DNS provider panel for `iaindex.org` and add these records:

#### 1. CNAME Record for docs subdomain
```
Name/Host: docs
Type: CNAME
Value: green-mushroom-003870c0f.1.azurestaticapps.net.
TTL: 3600 (or Auto)
```

**Important**: Add the trailing dot (`.`) at the end of the value!

#### 2. TXT Record for verification
First, get the verification token:
```bash
az staticwebapp secrets list --name aiindex-docs --resource-group aiindex-rg
```

This will return a validation token. Then add:
```
Name/Host: asuid.docs
Type: TXT
Value: <validation-token-from-above>
TTL: 3600 (or Auto)
```

### After Adding DNS Records

Wait 5-10 minutes for DNS propagation, then verify:
```bash
# Check CNAME
nslookup docs.iaindex.org

# Should show: green-mushroom-003870c0f.1.azurestaticapps.net
```

### Bind Custom Domain in Azure

Once DNS records are added and propagated:
```bash
az staticwebapp hostname set \
  --name aiindex-docs \
  --resource-group aiindex-rg \
  --hostname docs.iaindex.org
```

Azure will automatically provision a free SSL certificate (may take 5-10 minutes).

### Rebuild and Deploy Docs

With the updated configuration:
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/docs

# Rebuild with new URLs
npm run build

# Deploy to production
swa deploy build \
  --app-name aiindex-docs \
  --resource-group aiindex-rg \
  --env production
```

## 🔐 Security: Redeploy API (Disable /docs)

The FastAPI `/docs` endpoint has been disabled in the code, but you need to redeploy:

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/api

# Ensure DEBUG=False
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars "DEBUG=False"
```

This creates a new revision with `/docs` disabled in production.

## ⚠️ Critical: Rotate Exposed Credentials

The old repository exposed these credentials - they MUST be rotated:

### 1. Generate New Secret Key
```bash
NEW_SECRET_KEY=$(openssl rand -hex 32)
echo "New Secret Key: $NEW_SECRET_KEY"
```

### 2. Change Supabase Database Password
1. Go to: https://supabase.com/dashboard/project/casuupkmbqytgqnksnwd/settings/database
2. Click "Reset database password"
3. Generate a new strong password
4. Save it securely

### 3. Update Azure Container App Secrets
```bash
# Update secrets
az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets \
    "secret-key=<NEW_SECRET_KEY_FROM_STEP_1>" \
    "database-url=postgresql://postgres.<PROJECT_ID>:<NEW_PASSWORD>@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

# Apply secrets to environment variables
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars \
    "SECRET_KEY=secretref:secret-key" \
    "DATABASE_URL=secretref:database-url"
```

This will create a new revision with the updated credentials.

## ✅ Verification Checklist

After completing all steps:

- [ ] DNS records added for docs.iaindex.org
- [ ] Custom domain bound in Azure Static Web Apps
- [ ] SSL certificate provisioned (automatic)
- [ ] Docs rebuilt and deployed with new URLs
- [ ] Docs accessible at https://docs.iaindex.org
- [ ] API redeployed with /docs disabled
- [ ] FastAPI /docs returns 404 at https://api.iaindex.org/docs
- [ ] Database password rotated in Supabase
- [ ] SECRET_KEY rotated in Azure
- [ ] API still working with new credentials

## 🎉 Final Result

Once complete, your architecture will be:

```
Documentation: https://docs.iaindex.org
    ↓ (Docusaurus, Azure Static Web Apps)
    ↓ Links to GitHub and npm packages

Public API: https://api.iaindex.org
    ↓ (FastAPI, Azure Container Apps)
    ↓ /docs disabled in production
    ↓ Only API endpoints accessible

GitHub: https://github.com/dineshanchetty/iaindex
    ↓ (Clean public repository)
    ↓ SDKs, CLI, WordPress plugin, examples only
    ↓ No backend code or sensitive data

Packages:
    - npm: iaindex-sdk, iaindex-cli
    - PyPI: aiindex-sdk
    - WordPress: Download from GitHub releases
```

## Need Help?

If you encounter issues:
1. Check DNS propagation: `nslookup docs.iaindex.org`
2. Check SSL status: `az staticwebapp hostname show --name aiindex-docs --resource-group aiindex-rg --hostname docs.iaindex.org`
3. Check API health: `curl https://api.iaindex.org/health`
4. View logs: `az containerapp logs show --name aiindex-api --resource-group aiindex-rg --tail 50`
