# Existing IAIndex Infrastructure Audit
## What We Have vs What We Need

---

## 🏗️ CURRENT INFRASTRUCTURE

### 1. **Backend API** (✅ Production Ready)
**Location**: `/apps/api/`
**Tech Stack**: FastAPI, Python, Supabase, Azure Container Apps
**Status**: Live at https://api.iaindex.org

**Current Routes:**
```
/v1/publishers/verify           - Domain verification
/v1/publishers/check            - Check verification status
/v1/publishers/verified         - List verified publishers
/v1/receipts/submit             - Submit receipt
/v1/receipts/verify             - Verify receipt
/v1/analytics/receipts          - Receipt analytics
/v1/attestations/daily          - Daily attestations
```

**What's Useful:**
- ✅ Authentication system (API keys, JWT)
- ✅ Rate limiting middleware
- ✅ Domain verification service (DNS/HTML/File)
- ✅ Database schema (publishers table)
- ✅ Supabase integration
- ✅ CORS configured
- ✅ Azure deployment pipeline

**What Needs to Change:**
- ❌ Receipt-focused routes → Schema generation routes
- ❌ Attestation/cryptography → AI visibility checking
- ❌ Focus on tracking → Focus on optimization

---

### 2. **Database Schema** (Supabase/PostgreSQL)
**Current Tables:**
```sql
publishers (
  id, domain, verification_token,
  domain_verified, created_at, updated_at
)

receipts (
  id, content_url, publisher_domain,
  ai_model, timestamp, signature, verified
)

attestations (
  id, date, merkle_root, receipt_count,
  created_at
)
```

**What's Useful:**
- ✅ Publishers table (can extend)
- ✅ Domain verification system

**What Needs Adding:**
```sql
-- New table for schema tracking
websites (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES auth.users,
  url TEXT NOT NULL,
  domain TEXT NOT NULL,
  business_name TEXT,
  business_type TEXT, -- ecommerce, local, blog
  schema_markup JSONB, -- Generated schema
  last_scraped_at TIMESTAMP,
  visibility_score INT DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Track AI visibility
ai_mentions (
  id UUID PRIMARY KEY,
  website_id UUID REFERENCES websites,
  platform TEXT, -- chatgpt, perplexity, claude
  query TEXT, -- What user asked
  mentioned BOOLEAN,
  checked_at TIMESTAMP
)

-- Store optimization recommendations
recommendations (
  id UUID PRIMARY KEY,
  website_id UUID REFERENCES websites,
  type TEXT, -- add_faq, improve_desc, etc
  priority INT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP
)
```

---

### 3. **SDKs** (✅ Published on npm/PyPI)
**Node.js SDK**: https://www.npmjs.com/package/iaindex-sdk@1.0.0
**Python SDK**: https://pypi.org/project/aiindex-sdk@1.0.0
**CLI**: https://www.npmjs.com/package/iaindex-cli@1.0.0

**Current Features:**
```javascript
// Receipt submission focused
const client = new IAIndexClient({ apiBaseUrl });
await client.submitReceipt(receiptData);
await client.verifyReceipt(receiptId);
```

**What Needs Adding:**
```javascript
// Schema generation focused
const client = new IAIndexClient({ apiKey });

// Generate schema from URL
const schema = await client.generateSchema('https://myshop.com');

// Check AI visibility
const visibility = await client.checkVisibility({
  domain: 'myshop.com',
  keywords: ['ceramic mugs', 'handmade pottery']
});

// Get recommendations
const tips = await client.getRecommendations('myshop.com');
```

---

### 4. **WordPress Plugin** (✅ Built)
**Location**: `/packages/wordpress-plugin/`
**Status**: v1.0.0 available on GitHub releases

**Current Features:**
- ✅ Admin settings page
- ✅ API key configuration
- ✅ Post metadata handling
- ✅ Receipt submission on publish

**What Needs Changing:**
```php
// OLD: Submit receipts
function submit_receipt($post_id) {
    // Submit to /v1/receipts/submit
}

// NEW: Generate and inject schema
function generate_schema($post_id) {
    // Call /v1/schema/generate
    // Store in post meta
    // Inject in wp_head
}

// NEW: Check visibility
function check_ai_visibility() {
    // Call /v1/visibility/check
    // Show in dashboard widget
}
```

---

### 5. **Documentation Site** (✅ Live)
**URL**: https://docs.iaindex.org
**Tech**: Docusaurus, Azure Static Web Apps
**Status**: Production ready

**What Needs Updating:**
- ❌ Receipt/attestation docs → Schema optimization docs
- ❌ Cryptography focus → AI visibility focus
- ❌ Technical audience → SMB audience

---

### 6. **Infrastructure** (✅ Production Ready)
**API Hosting**: Azure Container Apps
- Custom domain: api.iaindex.org
- Auto-scaling
- SSL certificate
- Environment variables configured

**Docs Hosting**: Azure Static Web Apps
- Custom domain: docs.iaindex.org
- SSL certificate
- CI/CD via GitHub

**Database**: Supabase
- PostgreSQL database
- RLS enabled
- Connection pooling

**What's Perfect:**
- ✅ All production infrastructure ready
- ✅ Custom domains configured
- ✅ SSL certificates active
- ✅ Deployment pipelines working

---

## 🔄 REUSABILITY MATRIX

### ✅ **80% Can Be Reused**

| Component | Reuse % | Changes Needed |
|-----------|---------|----------------|
| **API Infrastructure** | 95% | Just add new routes |
| **Authentication** | 100% | No changes |
| **Rate Limiting** | 100% | No changes |
| **Domain Verification** | 100% | Perfect for publisher verification |
| **Database Connection** | 100% | No changes |
| **Deployment Pipeline** | 100% | No changes |
| **Documentation Site** | 70% | Update content only |
| **WordPress Plugin Shell** | 80% | Change API calls |
| **SDK Structure** | 90% | Add new methods |

### ❌ **20% Needs New Development**

| Component | Status | Effort |
|-----------|--------|--------|
| **Schema Generator** | NEW | 2 weeks |
| **AI Visibility Checker** | NEW | 2 weeks |
| **Claude API Integration** | NEW | 1 week |
| **New Database Tables** | NEW | 3 days |
| **Dashboard UI** | NEW | 2 weeks |
| **WordPress Plugin Updates** | MODIFY | 1 week |

---

## 📋 WHAT TO KEEP vs CHANGE vs ADD

### ✅ **KEEP (No Changes)**

**1. Core Infrastructure:**
- ✅ FastAPI application structure
- ✅ Supabase client setup
- ✅ Authentication middleware
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ Azure deployment
- ✅ SSL certificates
- ✅ Custom domains

**2. Domain Verification:**
- ✅ `/v1/publishers/verify` - Perfect for SMB onboarding
- ✅ DNS/HTML/File verification methods
- ✅ Verification token generation
- ✅ Domain validation logic

**3. Authentication:**
- ✅ API key system
- ✅ JWT tokens
- ✅ User authentication

---

### 🔄 **MODIFY (Repurpose)**

**1. Publishers Table:**
```sql
-- ADD these columns:
ALTER TABLE publishers ADD COLUMN user_id UUID;
ALTER TABLE publishers ADD COLUMN business_name TEXT;
ALTER TABLE publishers ADD COLUMN business_type TEXT;
ALTER TABLE publishers ADD COLUMN keywords TEXT[];
ALTER TABLE publishers ADD COLUMN location TEXT;
ALTER TABLE publishers ADD COLUMN visibility_score INT DEFAULT 0;
```

**2. Receipts Routes → Schema Routes:**
```python
# OLD: /v1/receipts/submit
# NEW: /v1/schema/generate

@router.post("/schema/generate")
async def generate_schema(
    url: HttpUrl,
    api_key: str = Depends(get_api_key)
):
    # Use Claude to scrape and generate schema
    pass
```

**3. Analytics Routes → Visibility Routes:**
```python
# OLD: /v1/analytics/receipts
# NEW: /v1/visibility/check

@router.post("/visibility/check")
async def check_visibility(
    domain: str,
    keywords: List[str],
    api_key: str = Depends(get_api_key)
):
    # Test queries in ChatGPT/Perplexity
    pass
```

---

### ➕ **ADD (New Development)**

**1. New API Routes:**
```python
# Schema Generation
POST /v1/schema/generate
GET  /v1/schema/{website_id}
PUT  /v1/schema/{website_id}

# AI Visibility
POST /v1/visibility/check
GET  /v1/visibility/score/{website_id}
GET  /v1/visibility/mentions/{website_id}

# Recommendations
GET  /v1/recommendations/{website_id}
POST /v1/recommendations/{website_id}/complete

# Website Management
GET  /v1/websites
POST /v1/websites
PUT  /v1/websites/{website_id}
DELETE /v1/websites/{website_id}
```

**2. New Services:**
```python
# services/schema_generator.py
class SchemaGeneratorService:
    async def scrape_website(url: str) -> dict
    async def generate_schema(scraped_data: dict) -> dict
    async def validate_schema(schema: dict) -> bool

# services/ai_visibility.py
class AIVisibilityService:
    async def check_chatgpt(query: str, domain: str) -> bool
    async def check_perplexity(query: str, domain: str) -> bool
    async def calculate_score(mentions: dict) -> int

# services/recommendations.py
class RecommendationService:
    def analyze_schema(schema: dict) -> List[Recommendation]
    def analyze_content(html: str) -> List[Recommendation]
```

**3. New Database Tables:**
```sql
-- See "Database Schema" section above
CREATE TABLE websites (...);
CREATE TABLE ai_mentions (...);
CREATE TABLE recommendations (...);
```

**4. Dashboard Frontend:**
```typescript
// NEW: Next.js dashboard
/dashboard
  /websites
    /[id]
      /schema
      /visibility
      /recommendations
  /settings
  /billing
```

---

## 🚀 MIGRATION ROADMAP

### **Phase 1: Backend API Extension (Week 1-2)**
**Keep Running:** Current API (no breaking changes)
**Add New Routes:**
- [ ] POST /v1/schema/generate (Claude integration)
- [ ] POST /v1/visibility/check (AI testing)
- [ ] GET /v1/websites (CRUD)

**Database Migration:**
```sql
-- Run these migrations (non-breaking)
CREATE TABLE websites (...);
CREATE TABLE ai_mentions (...);
CREATE TABLE recommendations (...);

-- Extend publishers table
ALTER TABLE publishers ADD COLUMN ...;
```

**Testing:**
- [ ] Test schema generation with 10 real websites
- [ ] Test AI visibility checks
- [ ] Verify performance (< 5s per request)

---

### **Phase 2: SDK Updates (Week 2-3)**
**Backward Compatible:**
```javascript
// OLD methods still work
client.submitReceipt() // Keep for compatibility

// NEW methods added
client.generateSchema() // New
client.checkVisibility() // New
```

**Publish:**
- [ ] iaindex-sdk@1.1.0 (backward compatible)
- [ ] aiindex-sdk@1.1.0 (Python)
- [ ] iaindex-cli@1.1.0

---

### **Phase 3: WordPress Plugin Update (Week 3-4)**
**New Features:**
- [ ] Schema auto-generation on post publish
- [ ] Visibility dashboard widget
- [ ] Recommendations in admin

**Migration:**
- [ ] Auto-update via WordPress.org (when available)
- [ ] Migration script for existing users

---

### **Phase 4: Frontend Dashboard (Week 4-6)**
**New Build:**
- [ ] Next.js app (separate from docs)
- [ ] Deploy to Azure Static Web Apps
- [ ] Domain: app.iaindex.org

---

### **Phase 5: Documentation Update (Week 6)**
**Content Changes:**
- [ ] Update all examples (schema focus)
- [ ] New getting started guides
- [ ] API reference updates
- [ ] Remove attestation/receipt docs

---

## 💰 COST OF PIVOT

### Development Time:
- **API Routes**: 2 weeks
- **Database Migrations**: 3 days
- **SDK Updates**: 1 week
- **WordPress Plugin**: 1 week
- **Dashboard Frontend**: 2 weeks
- **Documentation**: 3 days
- **Testing**: 1 week

**Total**: ~8 weeks for MVP
**With existing infra**: ~6 weeks (25% faster)

### New Costs:
- **Claude API**: ~$0.001 per scrape = $100/mo for 100K scrapes
- **ChatGPT API**: ~$0.002 per visibility check = $200/mo
- **Total new costs**: ~$300/mo in APIs

### Infrastructure (Already Paid):
- ✅ Azure Container Apps: $0/mo (free tier)
- ✅ Supabase: $0/mo (free tier, can scale to $25/mo)
- ✅ Domains: Already purchased
- ✅ SSL: Free (Azure managed)

---

## 🎯 RECOMMENDATION: GRADUAL MIGRATION

### **Approach: Side-by-Side**
```
┌────────────────────────────────────┐
│  Current API (Keep Running)        │
│  - /v1/receipts/* (deprecated)     │
│  - /v1/attestations/* (deprecated) │
│  - /v1/publishers/* (keep)         │
└────────────────────────────────────┘
              ↓
┌────────────────────────────────────┐
│  New API (Add Routes)              │
│  + /v1/schema/*                    │
│  + /v1/visibility/*                │
│  + /v1/websites/*                  │
└────────────────────────────────────┘
```

**Benefits:**
- ✅ No breaking changes
- ✅ Can A/B test
- ✅ Gradual migration of users
- ✅ Keep existing customers happy
- ✅ Learn from real usage

---

## ✅ SUMMARY

### **What We Have (80% Complete)**
- ✅ Production API infrastructure
- ✅ Authentication & rate limiting
- ✅ Domain verification system
- ✅ Database & hosting
- ✅ Custom domains & SSL
- ✅ SDK framework
- ✅ WordPress plugin shell
- ✅ Documentation site

### **What We Need (20% New)**
- ❌ Schema generation service
- ❌ AI visibility checker
- ❌ Claude/ChatGPT API integration
- ❌ Dashboard UI
- ❌ New database tables
- ❌ Updated SDKs/docs

### **Effort Required**
- **With existing infra**: 6 weeks
- **From scratch**: 12+ weeks
- **Savings**: 50% time saved

### **Cost**
- **Infrastructure**: $0 (already have)
- **New APIs**: ~$300/mo (Claude + ChatGPT)
- **Development**: 6 weeks engineer time

---

## 🚦 NEXT STEP

**Should we:**
1. ✅ **Start with Phase 1** (Backend API extension)
2. ✅ **Keep old routes running** (backward compatibility)
3. ✅ **Add new features side-by-side**
4. ✅ **Test with 10 beta users**
5. ✅ **Gradually migrate**

**Want me to start building Phase 1 (Backend API)?**
- New schema generation endpoint
- Claude integration
- AI visibility checker
- New database migrations

Ready to begin?
