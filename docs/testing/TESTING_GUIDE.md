# IAIndex Local Testing Guide

## Current Status

**Backend API:** ✅ Live at https://api.iaindex.org
**Scan Tool:** ✅ Running at http://localhost:3001
**What Works:** Mock data flow (free scan)
**What's Missing:** Payment flow, user dashboard, PDF reports

---

## Test the Free Scan Flow (What We Have)

### 1. Visit Landing Page
Open: http://localhost:3001

**What to test:**
- ✅ Hero section loads
- ✅ URL input form appears
- ✅ Features section visible
- ✅ FAQ section loads
- ✅ Trust indicators showing

### 2. Enter URL and Scan
1. Enter a URL (e.g., `https://example.com`)
2. Click "Scan Now"
3. Should redirect to `/scan/[url]`

**What to test:**
- ✅ Animated progress bar
- ✅ 4-step scanning animation
- ✅ Auto-redirect to results after ~6 seconds

### 3. View Results
Should land on `/results/[id]` page

**What to test:**
- ✅ Visibility score displays (0-100)
- ✅ Animated circular gauge
- ✅ Platform scores (ChatGPT, Perplexity, Claude)
- ✅ Top 3 recommendations with priority badges
- ✅ Email capture form
- ✅ "Fix My Visibility Score" CTA
- ✅ "Scan Another Website" button
- ✅ Social share buttons

### 4. Email Capture
Fill in email and submit

**What to test:**
- ✅ Email validation
- ✅ Success message appears
- ⚠️ Email is logged to console (not sent yet)

**Current Limitation:**
- Results page may lose data on refresh (in-memory storage)
- No actual backend integration yet

---

## What Works with Mock Data

### Free Scan Tool ✅
- Landing page with conversion optimization
- URL scanning with animated progress
- Results page with visibility scores
- Platform breakdown (ChatGPT, Perplexity, Claude)
- Top 3 recommendations with impact scores
- Email capture form (UI only)
- Social sharing buttons (UI only)

### Backend API ✅
- Schema generation (real Claude API)
- AI visibility checking (real OpenAI API)
- Website management
- Authentication
- Rate limiting

---

## What's Missing for Full Launch

### 1. **Payment Integration (Critical)**

**Stripe Setup Needed:**
```typescript
// apps/scan/lib/stripe.ts
import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-10-28.acacia',
});

// Pricing plans
export const PLANS = {
  starter: 'price_xxx', // $29/mo
  professional: 'price_xxx', // $79/mo
  agency: 'price_xxx', // $199/mo
};
```

**Checkout Flow:**
1. User clicks "Fix My Visibility Score"
2. Select plan (Starter/Pro/Agency)
3. Stripe Checkout
4. Payment success → Create account
5. Redirect to dashboard

**Files to Create:**
- `apps/scan/app/pricing/page.tsx` - Pricing page
- `apps/scan/app/checkout/page.tsx` - Stripe checkout
- `apps/scan/app/api/create-checkout/route.ts` - Create Stripe session
- `apps/scan/app/api/webhook/route.ts` - Handle Stripe webhooks
- `apps/api/src/routes/subscriptions.py` - Subscription management

### 2. **User Dashboard (app.iaindex.org)**

**Pages Needed:**
- `/login` - User login
- `/signup` - User registration
- `/dashboard` - Overview with stats
- `/websites` - List of websites
- `/websites/[id]` - Website details
- `/websites/[id]/schema` - Schema management
- `/websites/[id]/visibility` - Visibility tracking
- `/settings` - Account settings
- `/billing` - Subscription & billing

**Key Features:**
- View all websites
- Generate/update schemas
- View visibility trends (charts)
- Download PDF reports
- Manage subscription
- API key management

**Tech Stack:**
- Next.js 14 (same as scan tool)
- TailwindCSS
- Recharts (for graphs)
- React Query (data fetching)

### 3. **PDF Report Generation**

**When User Enters Email:**
1. Generate detailed PDF report
2. Email it to user
3. Include upgrade CTA in email

**PDF Contents:**
- Executive summary
- Current visibility score
- Platform breakdown with charts
- Detailed recommendations (10+ items)
- Competitor comparison
- Implementation guide
- Upgrade offer

**Files to Create:**
- `apps/api/src/services/pdf_generator.py` - PDF creation
- `apps/api/src/services/email_service.py` - Email delivery
- `apps/api/src/routes/reports.py` - Report endpoints

**Dependencies:**
- `reportlab` or `weasyprint` (Python PDF)
- `sendgrid` or `resend` (Email delivery)

### 4. **Backend Updates**

**New Routes Needed:**
```python
# User Management
POST /v1/auth/register
POST /v1/auth/login
GET /v1/auth/me
PATCH /v1/auth/update-profile

# Subscriptions (Stripe Integration)
POST /v1/subscriptions/create-checkout
POST /v1/subscriptions/webhook (Stripe)
GET /v1/subscriptions/current
POST /v1/subscriptions/cancel
POST /v1/subscriptions/update

# Reports
POST /v1/reports/generate
GET /v1/reports/{report_id}
POST /v1/reports/email

# User Websites (extend existing)
GET /v1/users/websites
POST /v1/users/websites/{id}/scan
GET /v1/users/websites/{id}/reports
```

**Database Tables to Add:**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  password_hash TEXT,
  stripe_customer_id TEXT,
  created_at TIMESTAMPTZ
);

CREATE TABLE subscriptions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  stripe_subscription_id TEXT,
  plan TEXT, -- 'starter', 'professional', 'agency'
  status TEXT, -- 'active', 'canceled', 'past_due'
  current_period_end TIMESTAMPTZ
);

CREATE TABLE reports (
  id UUID PRIMARY KEY,
  website_id UUID REFERENCES websites(id),
  pdf_url TEXT,
  generated_at TIMESTAMPTZ
);
```

### 5. **Email Automation**

**Drip Campaign:**
- Day 0: PDF report delivery
- Day 1: "Did you see your score?"
- Day 3: Case study email
- Day 7: Limited discount offer
- Day 14: "Your competitors are ahead"

**Tool:** SendGrid, Mailchimp, or Resend

### 6. **Analytics & Tracking**

**Events to Track:**
- Page views (landing, results)
- Scan initiated
- Scan completed
- Email submitted
- Upgrade clicked
- Payment completed
- User churn

**Tools:**
- Google Analytics
- Mixpanel or Amplitude
- Stripe analytics

---

## Complete Flow (What We Need to Build)

### Free User Journey
1. ✅ Visit scan.iaindex.org
2. ✅ Enter URL → See scanning animation
3. ✅ View results with visibility score
4. ✅ See top 3 recommendations
5. ⏳ Enter email → Receive PDF report
6. ⏳ Click "Upgrade" in email → Pricing page
7. ⏳ Select plan → Stripe checkout
8. ⏳ Payment success → Account created
9. ⏳ Redirect to dashboard

### Paid User Journey
1. ⏳ Login to app.iaindex.org
2. ⏳ Add website
3. ⏳ Click "Generate Schema" → See AI-generated schema
4. ⏳ Copy/paste schema to website
5. ⏳ Click "Check Visibility" → See real-time results
6. ⏳ View trends over time (charts)
7. ⏳ Download detailed PDF report
8. ⏳ Manage subscription in billing settings

---

## Testing Checklist

### Current (Mock Data)
- [ ] Landing page loads correctly
- [ ] URL input validation works
- [ ] Scanning animation plays
- [ ] Results page shows scores
- [ ] Recommendations display
- [ ] Email form validation
- [ ] Mobile responsive

### To Build & Test
- [ ] Stripe test mode checkout
- [ ] Account creation after payment
- [ ] Login/logout flow
- [ ] Dashboard loads with data
- [ ] Schema generation from dashboard
- [ ] Visibility checking from dashboard
- [ ] PDF report generation
- [ ] Email delivery
- [ ] Subscription management
- [ ] Upgrade/downgrade plans
- [ ] Cancel subscription

---

## Development Priority

### Phase 1: Payments (Week 1)
**Goal:** Convert free scans to paying customers

1. Set up Stripe account
2. Create pricing page
3. Build checkout flow
4. Implement webhooks
5. Test payment flow end-to-end

**Deliverable:** User can pay and get account

### Phase 2: Dashboard (Week 2)
**Goal:** Paid users can manage websites

1. Build authentication
2. Create dashboard layout
3. Website management UI
4. Schema generation interface
5. Visibility tracking UI

**Deliverable:** Functional user dashboard

### Phase 3: PDF Reports (Week 3)
**Goal:** Deliver value to free users

1. PDF generation service
2. Email delivery integration
3. Report templates
4. Automated email drip

**Deliverable:** Email capture → PDF delivery works

### Phase 4: Polish & Launch (Week 4)
**Goal:** Ready for public launch

1. Analytics integration
2. Error handling
3. Loading states
4. Email templates
5. Final testing

**Deliverable:** Production-ready product

---

## Quick Test Commands

### Test Backend API
```bash
# Health check
curl https://api.iaindex.org/health

# Schema generation (need API key)
curl -X POST https://api.iaindex.org/v1/schema/generate \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"url": "https://example.com"}'
```

### Test Scan Tool Locally
```bash
# Start dev server
cd apps/scan
npm run dev

# Open browser
open http://localhost:3001
```

### Build for Production
```bash
cd apps/scan
npm run build
npm start
```

---

## Next Steps

**What should we build first?**

1. **Stripe Integration** → Start getting revenue
2. **User Dashboard** → Deliver paid value
3. **PDF Reports** → Improve free conversion
4. **All of the above** → Complete product

Let me know which to prioritize!
