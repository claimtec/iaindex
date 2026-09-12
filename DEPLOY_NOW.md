# Deploy IAIndex v2.0 Backend - Quick Guide

## Current Status
✅ Anthropic API key configured in Azure secrets
✅ Backend code complete with schema generation + visibility checking
✅ Database migration applied to Supabase
⏳ Ready to deploy

---

## Step 1: Start Docker Desktop

Before deploying, you need to start Docker Desktop:
1. Open Docker Desktop application
2. Wait for it to start (whale icon in menu bar should be steady)
3. Verify it's running: `docker ps`

---

## Step 2: Build & Deploy Backend

Once Docker is running, execute these commands:

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# Build the Docker image
docker build -t iaindexacr.azurecr.io/iaindex-api:v2.0 -f apps/api/Dockerfile apps/api

# Login to Azure Container Registry
az acr login --name iaindexacr

# Push the image
docker push iaindexacr.azurecr.io/iaindex-api:v2.0

# Update Container App with new image
az containerapp update \
  --name aiindex-api \
  --resource-group iaindex-rg \
  --image iaindexacr.azurecr.io/iaindex-api:v2.0
```

**Expected time:** 5-10 minutes

---

## Step 3: Verify Deployment

Test the new endpoints:

### Health Check
```bash
curl https://api.iaindex.org/health
```

### Test Schema Generation
```bash
# First, get your API key
curl -X POST https://api.iaindex.org/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'

# Save the API key from response, then test schema generation
curl -X POST https://api.iaindex.org/v1/schema/generate \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "business_name": "Example Business",
    "business_type": "LocalBusiness"
  }'
```

You should see:
- Generated JSON-LD schema markup
- AI-powered recommendations
- Impact scores

---

## Optional: Add OpenAI & Perplexity Keys

If you have OpenAI and Perplexity API keys for full visibility checking:

```bash
# Update secrets
az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets \
    "openai-key=YOUR_OPENAI_KEY" \
    "perplexity-key=YOUR_PERPLEXITY_KEY"

# Restart to apply
az containerapp revision restart \
  --name aiindex-api \
  --resource-group aiindex-rg
```

**Note:** With just Anthropic, you get:
- ✅ Full schema generation
- ✅ AI-powered recommendations
- ⚠️ Limited visibility checking (mock data until OpenAI/Perplexity added)

---

## What's Working Now

### With Anthropic Key Only:
1. **Schema Generation** ✅
   - POST `/v1/schema/generate`
   - Claude-powered JSON-LD creation
   - Website scraping & analysis
   - AI recommendations

2. **Schema Validation** ✅
   - POST `/v1/schema/validate`
   - Check schema.org compliance

3. **Website Management** ✅
   - POST `/v1/schema/websites`
   - GET `/v1/schema/websites`
   - PATCH `/v1/schema/{website_id}`

### Requires OpenAI/Perplexity:
- ⏳ Full AI visibility checking
- ⏳ ChatGPT mention tracking
- ⏳ Perplexity mention tracking
- ⏳ Real visibility scores (currently returns mock data)

---

## Troubleshooting

### Docker build fails
```bash
# Check Docker is running
docker ps

# If not, start Docker Desktop
open -a Docker
```

### Container won't start
```bash
# View logs
az containerapp logs show -n aiindex-api -g iaindex-rg --follow

# Check status
az containerapp show -n aiindex-api -g aiindex-rg --query "properties.runningStatus"
```

### API returns 500 error
```bash
# Check environment variables
az containerapp show -n aiindex-api -g iaindex-rg --query "properties.template.containers[0].env"

# Verify Anthropic key is set
az containerapp secret list -n aiindex-api -g iaindex-rg
```

---

## Next: Deploy Scan Tool

After backend is live, deploy the free scan tool:

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/scan

# Run deployment script
./deploy-azure.sh
```

This will:
1. Build Next.js app
2. Deploy to Azure Static Web Apps
3. Provide URL for scan.iaindex.org setup

---

## Summary

**Minimum to launch (with just Anthropic):**
- Schema generation works ✅
- Can help businesses improve AI visibility ✅
- Recommendations engine works ✅
- Can start converting customers ✅

**Full platform (add OpenAI + Perplexity later):**
- Real visibility tracking
- ChatGPT/Perplexity mention monitoring
- Historical trend analysis
- Complete product offering

**You can launch with Anthropic-only and add other providers as you grow!**
