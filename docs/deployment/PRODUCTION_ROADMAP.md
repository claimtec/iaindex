# IAIndex Production Deployment - Complete Roadmap

**Goal**: Get IAIndex platform fully operational in production
**Timeline**: 2-3 days
**Current Status**: 60% complete

---

## Phase 1: Fix Critical Backend Gaps (Day 1 - Morning, 4 hours)

### Task 1.1: Create Websites CRUD Endpoint
**Time**: 2 hours
**Priority**: P0 - CRITICAL

**What to Build**:
```python
# File: apps/api/src/routes/websites.py

from fastapi import APIRouter, Depends
from supabase import Client

router = APIRouter(prefix="/v1/websites", tags=["websites"])

@router.post("/")
async def create_website(
    url: str,
    domain: str,
    supabase: Client = Depends(get_supabase_client)
):
    """Create or get existing website"""
    # Check if website exists
    existing = supabase.table("websites").select("*").eq("domain", domain).execute()

    if existing.data:
        return existing.data[0]

    # Create new website
    website = {
        "url": url,
        "domain": domain,
        "user_id": get_current_user_id(),  # optional
        "created_at": datetime.utcnow().isoformat()
    }

    result = supabase.table("websites").insert(website).execute()
    return result.data[0]

@router.get("/{website_id}")
async def get_website(website_id: str):
    """Get website by ID"""
    pass

@router.get("/")
async def list_websites():
    """List user's websites"""
    pass

@router.put("/{website_id}")
async def update_website(website_id: str):
    """Update website details"""
    pass

@router.delete("/{website_id}")
async def delete_website(website_id: str):
    """Delete website"""
    pass
```

**Steps**:
1. Create `apps/api/src/routes/websites.py`
2. Implement CRUD operations
3. Add authentication (API key or JWT)
4. Register router in `main.py`:
   ```python
   from .routes import websites
   app.include_router(websites.router)
   ```
5. Test locally
6. Deploy to Azure

**Acceptance Criteria**:
- ✅ POST /v1/websites returns website object with ID
- ✅ GET /v1/websites/{id} returns website details
- ✅ Authenticated requests only

---

### Task 1.2: Implement Login Endpoint
**Time**: 1 hour
**Priority**: P0 - CRITICAL

**What to Fix**:
```python
# File: apps/api/src/services/auth_service.py

async def login_user(self, email: str, password: str) -> Dict[str, Any]:
    """Login user using Supabase Auth"""
    try:
        response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not response.session:
            raise AuthenticationError("Invalid credentials")

        # Get profile
        profile = self.supabase.table("profiles").select("*").eq(
            "id", response.user.id
        ).execute()

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in,
            "user": profile.data[0] if profile.data else None
        }
    except Exception as e:
        raise AuthenticationError(f"Login failed: {str(e)}")
```

**Steps**:
1. Update `auth_service.py` with login implementation
2. Update `auth.py` router to call login_user()
3. Test with curl
4. Deploy to Azure

**Acceptance Criteria**:
- ✅ POST /v1/auth/login returns JWT tokens
- ✅ Returns user profile data
- ✅ Invalid credentials return 401

---

### Task 1.3: Enable API Documentation
**Time**: 15 minutes
**Priority**: P1 - HIGH

**What to Change**:
```python
# File: apps/api/src/config.py
# OR set via environment variable

debug: bool = True  # Enable docs in production (temporarily)
```

**Steps**:
1. Set `DEBUG=True` in Azure Container Apps
2. Restart container
3. Verify https://api.iaindex.org/docs loads
4. Test endpoints via Swagger UI

**Acceptance Criteria**:
- ✅ /docs shows API documentation
- ✅ Can test endpoints interactively

---

### Task 1.4: Deploy Backend Updates
**Time**: 30 minutes
**Priority**: P0 - CRITICAL

**Steps**:
```bash
# Build new Docker image
cd apps/api
docker buildx build --platform linux/amd64 \
  -t cafc3cb1336eacr.azurecr.io/iaindex-api:v2.3.0 .

# Push to registry
docker push cafc3cb1336eacr.azurecr.io/iaindex-api:v2.3.0

# Deploy to Azure
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --image cafc3cb1336eacr.azurecr.io/iaindex-api:v2.3.0

# Set DEBUG=True
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars DEBUG=True
```

**Acceptance Criteria**:
- ✅ New revision deployed
- ✅ Health check returns 200
- ✅ /v1/websites endpoint works
- ✅ /v1/auth/login endpoint works
- ✅ /docs accessible

---

## Phase 2: Deploy Frontend Apps (Day 1 - Afternoon, 4 hours)

### Task 2.1: Deploy apps/web (Dashboard)
**Time**: 2 hours
**Priority**: P0 - CRITICAL

**Steps**:
1. **Build for production**:
   ```bash
   cd apps/web
   npm run build
   # Output: .next/ folder with static files
   ```

2. **Create Azure Static Web App**:
   ```bash
   az staticwebapp create \
     --name aiindex-dashboard \
     --resource-group aiindex-rg \
     --location eastus \
     --sku Free \
     --source .next
   ```

3. **Deploy build**:
   ```bash
   az staticwebapp deploy \
     --name aiindex-dashboard \
     --resource-group aiindex-rg \
     --app-location .next
   ```

4. **Configure environment variables**:
   ```bash
   az staticwebapp appsettings set \
     --name aiindex-dashboard \
     --setting-names \
       NEXT_PUBLIC_SUPABASE_URL="https://uskaaxzhbijpvpgzubbp.supabase.co" \
       NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJ..." \
       NEXT_PUBLIC_API_URL="https://api.iaindex.org"
   ```

5. **Configure custom domain**:
   ```bash
   az staticwebapp hostname set \
     --name aiindex-dashboard \
     --resource-group aiindex-rg \
     --hostname app.iaindex.org
   ```

6. **Update DNS**:
   - Add CNAME record: `app.iaindex.org` → `[swa-url].azurestaticapps.net`

**Acceptance Criteria**:
- ✅ Dashboard accessible at https://app.iaindex.org
- ✅ Login works
- ✅ Registration works
- ✅ SSL certificate auto-provisioned

---

### Task 2.2: Deploy apps/scan (Marketing/Scan Tool)
**Time**: 2 hours
**Priority**: P0 - CRITICAL

**Steps**:
1. **Update scan app to use real backend**:
   ```typescript
   // Already updated in apps/scan/app/api/scan/route.ts
   // Just need to test after backend fix
   ```

2. **Build for production**:
   ```bash
   cd apps/scan
   npm run build
   ```

3. **Create Azure Static Web App**:
   ```bash
   az staticwebapp create \
     --name aiindex-scan \
     --resource-group aiindex-rg \
     --location eastus \
     --sku Free \
     --source .next
   ```

4. **Deploy**:
   ```bash
   az staticwebapp deploy \
     --name aiindex-scan \
     --resource-group aiindex-rg \
     --app-location .next
   ```

5. **Configure environment variables**:
   ```bash
   az staticwebapp appsettings set \
     --name aiindex-scan \
     --setting-names \
       NEXT_PUBLIC_API_URL="https://api.iaindex.org" \
       NEXT_PUBLIC_SUPABASE_URL="https://uskaaxzhbijpvpgzubbp.supabase.co" \
       NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJ..."
   ```

6. **Configure custom domain**:
   ```bash
   az staticwebapp hostname set \
     --name aiindex-scan \
     --resource-group aiindex-rg \
     --hostname scan.iaindex.org
   ```

7. **Update DNS**:
   - Add CNAME record: `scan.iaindex.org` → `[swa-url].azurestaticapps.net`

**Acceptance Criteria**:
- ✅ Scan tool accessible at https://scan.iaindex.org
- ✅ Can enter URL and run scan
- ✅ Returns real visibility data from backend
- ✅ SSL certificate auto-provisioned

---

## Phase 3: Testing & Monitoring (Day 2, 6 hours)

### Task 3.1: End-to-End User Flow Testing
**Time**: 2 hours
**Priority**: P0 - CRITICAL

**Test Scenarios**:
1. **User Registration**:
   ```
   1. Visit https://app.iaindex.org
   2. Click Sign Up
   3. Enter email, password, name
   4. Submit
   5. ✅ Profile created
   6. ✅ Redirected to dashboard
   ```

2. **User Login**:
   ```
   1. Visit https://app.iaindex.org/login
   2. Enter credentials
   3. Submit
   4. ✅ JWT tokens received
   5. ✅ Redirected to dashboard
   ```

3. **Website Visibility Scan**:
   ```
   1. Visit https://scan.iaindex.org
   2. Enter URL (e.g., example.com)
   3. Click "Scan Now"
   4. ✅ Website created in backend
   5. ✅ Visibility check triggered
   6. ✅ Real scores from ChatGPT/Perplexity
   7. ✅ Recommendations displayed
   ```

4. **Dashboard Access**:
   ```
   1. Login to https://app.iaindex.org
   2. Click "My Websites"
   3. ✅ See scanned websites
   4. Click on a website
   5. ✅ See visibility scores
   6. ✅ See historical data
   ```

**Acceptance Criteria**:
- ✅ All user flows complete without errors
- ✅ Data persists correctly in database
- ✅ Real-time updates work

---

### Task 3.2: Set Up Monitoring
**Time**: 2 hours
**Priority**: P1 - HIGH

**Application Insights**:
```bash
# Create Application Insights
az monitor app-insights component create \
  --app aiindex-insights \
  --location eastus \
  --resource-group aiindex-rg

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app aiindex-insights \
  --resource-group aiindex-rg \
  --query instrumentationKey -o tsv)

# Update Container App
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

**Configure Alerts**:
```bash
# CPU alert
az monitor metrics alert create \
  --name aiindex-cpu-alert \
  --resource-group aiindex-rg \
  --scopes /subscriptions/.../aiindex-api \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m

# Memory alert
az monitor metrics alert create \
  --name aiindex-memory-alert \
  --resource-group aiindex-rg \
  --scopes /subscriptions/.../aiindex-api \
  --condition "avg MemoryPercentage > 80" \
  --window-size 5m

# Error rate alert
az monitor metrics alert create \
  --name aiindex-error-alert \
  --resource-group aiindex-rg \
  --scopes /subscriptions/.../aiindex-api \
  --condition "total HTTP 5xx > 10" \
  --window-size 5m
```

**Acceptance Criteria**:
- ✅ Application Insights collecting data
- ✅ Alerts configured for CPU, memory, errors
- ✅ Dashboard showing metrics

---

### Task 3.3: Performance Testing
**Time**: 1 hour
**Priority**: P1 - HIGH

**Load Testing**:
```bash
# Test API performance
ab -n 1000 -c 10 https://api.iaindex.org/health

# Test visibility scanning
ab -n 100 -c 5 -p scan_payload.json \
  -T application/json \
  https://api.iaindex.org/v1/visibility/check
```

**Metrics to Check**:
- API response time: Target <500ms
- Page load time: Target <2s
- Database query time: Target <100ms
- Concurrent users: Test with 100+

**Acceptance Criteria**:
- ✅ API responds <500ms for 95% of requests
- ✅ No errors under load
- ✅ Database handles concurrent connections

---

### Task 3.4: Security Audit
**Time**: 1 hour
**Priority**: P1 - HIGH

**Checklist**:
- [ ] HTTPS enforced on all domains
- [ ] Security headers present (HSTS, CSP, etc.)
- [ ] CSRF protection enabled
- [ ] Rate limiting working
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (input sanitization)
- [ ] Secrets not exposed in logs
- [ ] RLS enabled on all database tables
- [ ] API keys properly rotated
- [ ] Abuse detection middleware re-enabled

**Re-enable Abuse Detection**:
```python
# apps/api/src/main.py
app.add_middleware(
    AbuseDetectionMiddleware,
    max_violations=10,
    violation_window_minutes=60,
    block_duration_minutes=60,
    permanent_block_threshold=50
)
```

**Acceptance Criteria**:
- ✅ All security checks pass
- ✅ No sensitive data exposed
- ✅ Abuse detection active

---

## Phase 4: Production Polish (Day 3, 4 hours)

### Task 4.1: Configure Email Provider
**Time**: 1 hour
**Priority**: P2 - MEDIUM

**Options**:
1. **SendGrid** (Recommended):
   ```bash
   # Get API key from SendGrid
   az containerapp update \
     --name aiindex-api \
     --resource-group aiindex-rg \
     --set-env-vars \
       EMAIL_PROVIDER=sendgrid \
       SENDGRID_API_KEY="SG.xxx"
   ```

2. **Resend** (Alternative):
   ```bash
   az containerapp update \
     --name aiindex-api \
     --resource-group aiindex-rg \
     --set-env-vars \
       EMAIL_PROVIDER=resend \
       RESEND_API_KEY="re_xxx"
   ```

**Test Email**:
```python
# Send test email
POST /v1/test-email
→ Should receive welcome email
```

**Acceptance Criteria**:
- ✅ Welcome emails sent on registration
- ✅ Password reset emails work
- ✅ Drip campaign emails scheduled

---

### Task 4.2: Payment Integration
**Time**: 1 hour
**Priority**: P2 - MEDIUM

**Stripe Setup**:
```bash
# Configure Stripe keys
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --set-env-vars \
    STRIPE_SECRET_KEY="sk_live_xxx" \
    STRIPE_WEBHOOK_SECRET="whsec_xxx"

# Configure frontend
az staticwebapp appsettings set \
  --name aiindex-dashboard \
  --setting-names \
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_live_xxx"
```

**Test Payment Flow**:
1. Visit https://app.iaindex.org/pricing
2. Click "Upgrade to Pro"
3. Enter test card: 4242 4242 4242 4242
4. ✅ Subscription created
5. ✅ User plan updated in database

**Acceptance Criteria**:
- ✅ Stripe checkout works
- ✅ Webhooks process payments
- ✅ Subscription status updates

---

### Task 4.3: Documentation Updates
**Time**: 1 hour
**Priority**: P3 - LOW

**Create**:
1. User Guide (how to use platform)
2. API Documentation (already in /docs)
3. Integration Guides (WordPress, Shopify, etc.)
4. Troubleshooting Guide

**Deploy docs site**:
```bash
cd apps/docs
npm run build
# Deploy to Azure Static Web Apps or existing site
```

**Acceptance Criteria**:
- ✅ User-facing documentation available
- ✅ API docs accessible
- ✅ Integration guides published

---

### Task 4.4: Final QA & Launch
**Time**: 1 hour
**Priority**: P0 - CRITICAL

**Pre-Launch Checklist**:
- [ ] All endpoints tested and working
- [ ] Frontend apps deployed and accessible
- [ ] DNS configured correctly
- [ ] SSL certificates active
- [ ] Monitoring and alerts configured
- [ ] Email provider configured
- [ ] Payment integration tested
- [ ] User flows tested end-to-end
- [ ] Performance acceptable
- [ ] Security audit complete
- [ ] Documentation published
- [ ] Backup strategy in place
- [ ] Rollback plan documented

**Go-Live**:
1. Announce launch
2. Monitor for 24 hours
3. Address any issues
4. Celebrate! 🎉

---

## Complete Timeline

### Day 1 (8 hours)
- **Morning**: Fix backend (websites endpoint, login, docs)
- **Afternoon**: Deploy frontends (apps/web, apps/scan)
- **End of Day**: Basic platform working end-to-end

### Day 2 (6 hours)
- **Morning**: End-to-end testing, bug fixes
- **Afternoon**: Monitoring, alerts, performance testing
- **End of Day**: Platform stable and monitored

### Day 3 (4 hours)
- **Morning**: Email provider, payment integration
- **Afternoon**: Final QA, documentation
- **End of Day**: Production ready, launch! 🚀

**Total**: 18 hours over 3 days

---

## Success Metrics

### Technical
- ✅ 99.9% uptime
- ✅ <500ms API response time
- ✅ <2s page load time
- ✅ Zero security vulnerabilities
- ✅ All tests passing

### Business
- ✅ Users can register and login
- ✅ Users can scan websites
- ✅ Real visibility scores returned
- ✅ Payments processed successfully
- ✅ Emails delivered

### Operational
- ✅ Monitoring active
- ✅ Alerts configured
- ✅ Logs accessible
- ✅ Backup strategy in place
- ✅ Incident response plan ready

---

## Rollback Plan

If critical issues occur:

### Backend Rollback
```bash
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --image cafc3cb1336eacr.azurecr.io/iaindex-api:v2.2.2-client-auth
```

### Frontend Rollback
```bash
# Revert to previous deployment
az staticwebapp deployment rollback \
  --name aiindex-dashboard \
  --resource-group aiindex-rg
```

### Database Rollback
```bash
# Restore from backup (create backups first!)
psql $DATABASE_URL < backup_20251018.sql
```

---

## Resources Needed

### Azure Resources
- ✅ Container App (backend) - Already exists
- ⏳ Static Web App (dashboard) - To create
- ⏳ Static Web App (scan) - To create
- ⏳ Application Insights - To create

### Third-Party Services
- ✅ Supabase (database) - Active
- ⏳ SendGrid/Resend (email) - To configure
- ⏳ Stripe (payments) - To configure

### DNS
- ✅ api.iaindex.org - Configured
- ⏳ app.iaindex.org - To configure
- ⏳ scan.iaindex.org - To configure

---

**Ready to Begin?** Start with Phase 1, Task 1.1: Create Websites Endpoint

---

**Last Updated**: October 18, 2025 - 16:00 UTC
