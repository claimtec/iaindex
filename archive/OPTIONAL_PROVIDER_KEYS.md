# Optional Provider Keys Guide

**Status:** Core functionality works without these keys
**Purpose:** Enable advanced v1.1 features

---

## Currently Configured (Required) ✅

These are already configured and working:

| Key | Status | Purpose |
|-----|--------|---------|
| `SUPABASE_URL` | ✅ Configured | Database and authentication |
| `SUPABASE_KEY` | ✅ Configured | Supabase anon key |
| `DATABASE_URL` | ✅ Configured | PostgreSQL connection |
| `SECRET_KEY` | ✅ Configured | JWT token signing |

---

## Optional v1.1 Features (Not Yet Configured)

These enable advanced features but are **NOT required** for core functionality:

### 1. **Redis** (Rate Limiting & Caching)

**Status:** ⚠️ Using in-memory fallback
**Impact:** Rate limiting works but doesn't persist across container restarts

```bash
# Environment Variables
REDIS_URL=redis://your-redis-host:6379
```

**Options:**
- **Azure Cache for Redis** (~$15-30/month)
  ```bash
  az redis create \
    --name aiindex-cache \
    --resource-group aiindex-rg \
    --location eastus \
    --sku Basic \
    --vm-size c0
  ```
- **Upstash Redis** (Free tier available)
- **Redis Cloud** (Free tier: 30MB)

**When to add:** If you see rate limiting issues or need persistent caching

---

### 2. **OpenAI** (Embeddings for Semantic Search)

**Status:** ⚠️ Optional - Semantic search disabled without it
**Feature:** v1.1 Embeddings service for content similarity search

```bash
# Environment Variables
OPENAI_API_KEY=sk-...
```

**Get Key:** https://platform.openai.com/api-keys

**Cost:**
- Embeddings: ~$0.0001 per 1K tokens
- For 10,000 receipts: ~$1-5/month

**When to add:** If you want semantic search capabilities for receipts

---

### 3. **Pinecone** (Vector Database for Semantic Search)

**Status:** ⚠️ Optional - Works with OpenAI embeddings
**Feature:** Store and search receipt embeddings

```bash
# Environment Variables
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=aiindex-vectors
PINECONE_ENVIRONMENT=us-west1-gcp
```

**Get Key:** https://www.pinecone.io/

**Cost:**
- Free tier: 100K vectors, 5GB storage
- Serverless: Pay per use (~$0.10-5/month for typical usage)

**When to add:** If you enable OpenAI embeddings and want vector search

---

### 4. **Cloudflare** (Screenshot/Rendering Service)

**Status:** ⚠️ Optional - Screenshots disabled without it
**Feature:** Generate visual snapshots of receipts

```bash
# Environment Variables
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_API_TOKEN=your-token
```

**Get Credentials:** https://dash.cloudflare.com/

**Cost:**
- Browser Rendering API: $5 per 1 million requests
- For 1,000 screenshots/month: ~$0.005

**When to add:** If you want visual snapshots of receipt content

---

### 5. **AWS S3** (Snapshot Storage)

**Status:** ⚠️ Optional - Local storage fallback
**Feature:** Store generated snapshots in S3

```bash
# Environment Variables
S3_BUCKET_SNAPSHOTS=aiindex-snapshots
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
```

**Cost:**
- S3 Standard: $0.023 per GB/month
- For 1GB of snapshots: ~$0.023/month

**Alternative:** Use **Azure Blob Storage** instead:
```bash
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER=snapshots
```

**When to add:** If you enable Cloudflare rendering and need persistent storage

---

### 6. **C2PA** (Content Provenance & Authenticity)

**Status:** ⚠️ Optional - Provenance disabled without it
**Feature:** Cryptographic content authentication

```bash
# Environment Variables
C2PA_PRIVATE_KEY_PATH=/app/keys/c2pa_private.pem
C2PA_CERTIFICATE_PATH=/app/keys/c2pa_cert.pem
```

**Setup:**
1. Generate certificates using C2PA tool
2. Store in Azure Key Vault or mount as volume

**Cost:** Free (self-hosted signing)

**When to add:** If you need cryptographic proof of content authenticity

---

### 7. **Sentry** (Error Monitoring)

**Status:** ⚠️ Optional - Basic logging without it
**Feature:** Advanced error tracking and performance monitoring

```bash
# Environment Variables
SENTRY_DSN=https://...@sentry.io/project
```

**Get DSN:** https://sentry.io/

**Cost:**
- Free tier: 5K events/month
- Developer: $26/month for 50K events

**When to add:** For production error tracking and monitoring

---

## Recommended Setup Priority

### Phase 1: Launch (Current) ✅
- ✅ Supabase (database)
- ✅ Core API functionality
- ✅ Dashboard
- ✅ Documentation

**Status:** Production-ready for basic usage

---

### Phase 2: Growth (Next 1-2 weeks)
Add these as usage grows:

1. **Redis** - For better rate limiting and caching
   - Cost: ~$15-30/month
   - Impact: Better performance and reliability

2. **Sentry** - For error monitoring
   - Cost: Free tier sufficient
   - Impact: Better debugging and uptime

---

### Phase 3: Advanced Features (Month 2+)
Add these when you need specific features:

3. **OpenAI + Pinecone** - For semantic search
   - Cost: ~$5-10/month combined
   - Impact: Enhanced search capabilities

4. **Cloudflare + S3/Azure Storage** - For snapshots
   - Cost: ~$5-10/month
   - Impact: Visual receipt verification

5. **C2PA** - For provenance
   - Cost: Free (self-hosted)
   - Impact: Cryptographic authenticity

---

## How to Add Optional Keys

### Step 1: Get the API Keys
Sign up for the service and generate API keys (links provided above)

### Step 2: Add to Azure as Secrets
```bash
az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets \
    "openai-api-key=sk-your-key" \
    "pinecone-api-key=your-key" \
    "cloudflare-api-token=your-token"
```

### Step 3: Update Environment Variables
```bash
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars \
    "OPENAI_API_KEY=secretref:openai-api-key" \
    "PINECONE_API_KEY=secretref:pinecone-api-key" \
    "CLOUDFLARE_API_TOKEN=secretref:cloudflare-api-token"
```

### Step 4: Restart Container
```bash
REVISION=$(az containerapp show --name aiindex-api --resource-group aiindex-rg --query "properties.latestRevisionName" -o tsv)
az containerapp revision restart \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --revision "$REVISION"
```

---

## Testing Optional Features

### Test Semantic Search (requires OpenAI + Pinecone)
```bash
curl -X POST "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "find receipts about image training",
    "limit": 10
  }'
```

### Test Screenshot Generation (requires Cloudflare)
```bash
curl -X POST "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/receipts/{id}/snapshot" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Cost Summary

### Current Monthly Costs
- Azure Container Apps (API): ~$30-60
- Azure Container Apps (Dashboard): ~$15-30
- Azure Static Web Apps (Docs): $0 (free tier)
- Supabase: $0 (free tier) or $25 (Pro)
- **Total: $45-115/month**

### With All Optional Features
- Current: $45-115
- Redis: +$15-30
- OpenAI: +$5
- Pinecone: +$0 (free tier)
- Cloudflare: +$5
- S3/Azure Storage: +$5
- Sentry: +$0 (free tier)
- **Total: $75-165/month**

---

## Feature Availability Matrix

| Feature | Without Keys | With Keys |
|---------|-------------|-----------|
| **Receipt Submission** | ✅ Full | ✅ Full |
| **Domain Verification** | ✅ Full | ✅ Full |
| **Analytics** | ✅ Full | ✅ Full |
| **Rate Limiting** | ⚠️ In-memory | ✅ Persistent (Redis) |
| **Semantic Search** | ❌ Disabled | ✅ Enabled (OpenAI+Pinecone) |
| **Visual Snapshots** | ❌ Disabled | ✅ Enabled (Cloudflare+S3) |
| **Content Provenance** | ❌ Disabled | ✅ Enabled (C2PA) |
| **Error Tracking** | ⚠️ Basic logs | ✅ Advanced (Sentry) |

---

## Recommendations

### For MVP/Testing (Current State) ✅
**No additional keys needed** - Current setup is production-ready for basic usage

### For Beta Launch (Within 2 weeks)
**Add:**
1. Redis (better reliability)
2. Sentry (error monitoring)

**Cost: +$15-30/month**

### For Full Production (Month 2+)
**Add all features based on user demand**

**Cost: +$60-80/month total**

---

## Support

If you decide to add any optional features, let me know and I'll help you configure them!

**Current Status:** ✅ Production-ready without any optional keys
