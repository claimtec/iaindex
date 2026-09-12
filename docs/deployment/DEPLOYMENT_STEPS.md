# IAIndex v2.0 Deployment Steps

## ✅ Completed
- [x] Database migration applied to Supabase
- [x] Backend code implemented (services, routes, models)
- [x] Dependencies added to requirements.txt
- [x] Config updated with AI provider keys
- [x] Azure secrets created (placeholder keys)

## 🔄 Next Steps

### Step 1: Get AI Provider API Keys

You need to obtain API keys from three providers:

**1. Anthropic (Claude) - For Schema Generation**
- Sign up: https://console.anthropic.com/
- Create API key in Settings → API Keys
- Expected cost: ~$50-150/mo for first 100 users
- Copy the key (starts with `sk-ant-`)

**2. OpenAI (ChatGPT) - For Visibility Checking**
- Sign up: https://platform.openai.com/
- Create API key in API Keys section
- Expected cost: ~$50-100/mo for first 100 users
- Copy the key (starts with `sk-`)

**3. Perplexity - For Visibility Checking**
- Sign up: https://www.perplexity.ai/settings/api
- Create API key
- Expected cost: ~$30-75/mo for first 100 users
- Copy the key (starts with `pplx-`)

### Step 2: Update Azure Secrets with Real Keys

Once you have the API keys, run:

```bash
az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets \
    "anthropic-key=YOUR_REAL_ANTHROPIC_KEY" \
    "openai-key=YOUR_REAL_OPENAI_KEY" \
    "perplexity-key=YOUR_REAL_PERPLEXITY_KEY"
```

Replace `YOUR_REAL_*_KEY` with the actual keys.

### Step 3: Update Environment Variables

```bash
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars \
    "ANTHROPIC_API_KEY=secretref:anthropic-key" \
    "OPENAI_API_KEY=secretref:openai-key" \
    "PERPLEXITY_API_KEY=secretref:perplexity-key"
```

### Step 4: Deploy Updated Backend

Build and push the new Docker image:

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex

# Build the image
docker build -t iaindexacr.azurecr.io/iaindex-api:v2.0 -f apps/api/Dockerfile apps/api

# Login to Azure Container Registry
az acr login --name iaindexacr

# Push the image
docker push iaindexacr.azurecr.io/iaindex-api:v2.0

# Update the container app to use new image
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --image iaindexacr.azurecr.io/iaindex-api:v2.0
```

### Step 5: Verify Deployment

Test the new endpoints:

```bash
# Health check
curl https://api.iaindex.org/health

# Test schema generation (replace YOUR_API_KEY)
curl -X POST https://api.iaindex.org/v1/schema/generate \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "business_name": "Example Business",
    "business_type": "LocalBusiness"
  }'
```

## 📝 Quick Deploy Script

Create a file `deploy-v2.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Deploying IAIndex v2.0..."

# Build
echo "📦 Building Docker image..."
docker build -t iaindexacr.azurecr.io/iaindex-api:v2.0 -f apps/api/Dockerfile apps/api

# Login
echo "🔐 Logging into Azure Container Registry..."
az acr login --name iaindexacr

# Push
echo "⬆️  Pushing image..."
docker push iaindexacr.azurecr.io/iaindex-api:v2.0

# Update
echo "🔄 Updating container app..."
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --image iaindexacr.azurecr.io/iaindex-api:v2.0

echo "✅ Deployment complete!"
echo "🔍 Check status: az containerapp show -n aiindex-api -g aiindex-rg"
echo "📊 View logs: az containerapp logs show -n aiindex-api -g aiindex-rg --follow"
```

Make it executable:
```bash
chmod +x deploy-v2.sh
```

Then run:
```bash
./deploy-v2.sh
```

## 🧪 Testing the New Features

### Test Schema Generation

```bash
# Register a website
curl -X POST https://api.iaindex.org/v1/schema/websites \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "url": "https://example.com",
    "business_name": "Example Business",
    "business_type": "LocalBusiness",
    "keywords": ["example", "business", "service"]
  }'

# Save the website_id from response

# Generate schema
curl -X POST https://api.iaindex.org/v1/schema/generate \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "business_name": "Example Business",
    "business_type": "LocalBusiness"
  }'
```

### Test Visibility Checking

```bash
# Check AI visibility
curl -X POST https://api.iaindex.org/v1/visibility/check \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "website_id": "YOUR_WEBSITE_ID",
    "queries": ["example business", "example service"],
    "platforms": ["chatgpt", "perplexity"]
  }'

# Get visibility history
curl https://api.iaindex.org/v1/visibility/YOUR_WEBSITE_ID \
  -H "X-API-Key: YOUR_API_KEY"
```

## 🎯 Post-Deployment

Once deployed and tested:

1. **Update documentation site** - Add new API endpoints to docs.iaindex.org
2. **Update SDKs** - Add new methods to iaindex-sdk (Node.js) and aiindex-sdk (Python)
3. **Build free scan tool** - Create simple landing page for lead generation
4. **Update WordPress plugin** - Auto-generate schema on publish
5. **Launch marketing** - Free scan tool, Product Hunt, SEO outreach

## 💰 Cost Estimates

**Current Azure costs:** ~$30-50/mo
- Container Apps
- Container Registry
- Static Web Apps

**New AI API costs:** ~$130-325/mo (first 100 users)
- Anthropic (Claude): ~$50-150/mo
- OpenAI (ChatGPT): ~$50-100/mo
- Perplexity: ~$30-75/mo

**Total:** ~$160-375/mo to serve first 100 users
**Revenue potential:** $2,900/mo (100 users @ $29/mo average)
**Profit margin:** 86-94%

## 🆘 Troubleshooting

**If deployment fails:**
```bash
# Check container app status
az containerapp show -n aiindex-api -g aiindex-rg --query "properties.runningStatus"

# View logs
az containerapp logs show -n aiindex-api -g aiindex-rg --follow

# Restart if needed
az containerapp revision restart -n aiindex-api -g aiindex-rg
```

**If API keys don't work:**
```bash
# Verify secrets are set
az containerapp secret list -n aiindex-api -g aiindex-rg

# Verify environment variables
az containerapp show -n aiindex-api -g aiindex-rg --query "properties.template.containers[0].env"
```

## 📞 API Key Status

Run this to check if keys are configured:
```bash
curl https://api.iaindex.org/health
# Should return providers status
```
