# Stripe Integration - Quick Reference Card

**Status:** ✅ Integration Complete - Ready for Testing

---

## 5-Minute Setup

### 1. Stripe Dashboard (5 min)

1. Sign up: https://dashboard.stripe.com/register
2. Switch to Test Mode
3. Create 3 products ($29, $79, $199/month)
4. Copy price IDs and API keys

### 2. Database Migration (2 min)

```bash
psql "your-supabase-url" < migrations/002_add_subscriptions.sql
```

### 3. Configure Environment (3 min)

```bash
# apps/scan/.env.local
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_STRIPE_PRICE_STARTER=price_...
NEXT_PUBLIC_STRIPE_PRICE_PRO=price_...
NEXT_PUBLIC_STRIPE_PRICE_AGENCY=price_...

# apps/api/.env
STRIPE_SECRET_KEY=sk_test_...
SECRET_KEY=$(openssl rand -hex 32)
```

### 4. Start Services (2 min)

```bash
# Terminal 1
cd apps/api && uvicorn src.main:app --reload

# Terminal 2
cd apps/scan && npm run dev

# Terminal 3
stripe listen --forward-to http://localhost:3001/api/webhook
```

### 5. Test (3 min)

- Go to: http://localhost:3001/pricing
- Card: 4242 4242 4242 4242
- Expiry: 12/34, CVC: 123

---

## Test Cards

| Card | Result |
|------|--------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 9995 | Declined |

---

## API Endpoints

**Frontend:**
- POST /api/create-checkout
- POST /api/webhook

**Backend:**
- GET /api/subscriptions/current
- POST /api/subscriptions/cancel
- POST /api/subscriptions/create-portal-session

---

## Pricing Tiers

| Plan | Price | Websites | Frequency |
|------|-------|----------|-----------|
| Starter | $29/mo | 1 | Weekly |
| Professional | $79/mo | 5 | Daily |
| Agency | $199/mo | 50 | Real-time |

---

## Full Docs

- Setup: `/STRIPE_INTEGRATION_GUIDE.md`
- Testing: `/STRIPE_TESTING_REPORT.md`
