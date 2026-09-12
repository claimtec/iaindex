# Stripe Integration - Quick Start Guide

## 5-Minute Setup

This guide gets you up and running with Stripe payments in 5 minutes.

## Prerequisites

- Stripe account (sign up at https://stripe.com)
- Supabase project

## Step 1: Get Stripe Keys (2 minutes)

1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy these values:
   - **Publishable key** (starts with `pk_test_`)
   - **Secret key** (starts with `sk_test_`)

## Step 2: Create Products (2 minutes)

1. Go to https://dashboard.stripe.com/test/products
2. Click "Add product" and create:

   **Product 1: Starter**
   - Name: `IAIndex Starter`
   - Price: `$29.00 USD`
   - Recurring: Monthly
   - Copy the **Price ID** (starts with `price_`)

   **Product 2: Professional**
   - Name: `IAIndex Professional`
   - Price: `$79.00 USD`
   - Recurring: Monthly
   - Copy the **Price ID**

   **Product 3: Agency**
   - Name: `IAIndex Agency`
   - Price: `$199.00 USD`
   - Recurring: Monthly
   - Copy the **Price ID**

## Step 3: Configure Environment (1 minute)

### Frontend - `apps/scan/.env.local`

```bash
# Copy from .env.example
cp apps/scan/.env.example apps/scan/.env.local

# Edit and fill in:
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
NEXT_PUBLIC_STRIPE_PRICE_STARTER=price_YOUR_STARTER_ID
NEXT_PUBLIC_STRIPE_PRICE_PRO=price_YOUR_PRO_ID
NEXT_PUBLIC_STRIPE_PRICE_AGENCY=price_YOUR_AGENCY_ID

# Leave webhook secret empty for now
STRIPE_WEBHOOK_SECRET=

# Set URLs
NEXT_PUBLIC_SITE_URL=http://localhost:3001
NEXT_PUBLIC_APP_URL=https://app.iaindex.org
NEXT_PUBLIC_API_URL=http://localhost:8000
API_SECRET_KEY=your-random-secret-key-123
```

### Backend - `apps/api/.env`

```bash
# Copy from .env.example
cp apps/api/.env.example apps/api/.env

# Add Stripe keys
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
APP_URL=https://app.iaindex.org
SITE_URL=http://localhost:3001
```

## Step 4: Run Database Migration (30 seconds)

1. Go to your Supabase project: https://app.supabase.com
2. Click "SQL Editor"
3. Click "New query"
4. Copy and paste the entire content of:
   `migrations/002_add_subscriptions.sql`
5. Click "Run"

Verify tables were created:
```sql
SELECT * FROM users LIMIT 1;
SELECT * FROM subscriptions LIMIT 1;
```

## Step 5: Test It! (5 minutes)

### Terminal 1: Start Frontend
```bash
cd apps/scan
npm install  # if not done already
npm run dev
```

### Terminal 2: Start Backend
```bash
cd apps/api
pip install -r requirements.txt  # if not done already
uvicorn src.main:app --reload
```

### Terminal 3: Stripe Webhooks
```bash
# Install Stripe CLI (one time)
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to local
stripe listen --forward-to localhost:3001/api/webhook

# IMPORTANT: Copy the webhook signing secret (whsec_...)
# and add it to apps/scan/.env.local as STRIPE_WEBHOOK_SECRET
```

### Test the Flow

1. Open http://localhost:3001/pricing
2. Enter your email
3. Click "Get Started" on any plan
4. Use test card: `4242 4242 4242 4242`
5. Expiry: `12/25`, CVC: `123`, ZIP: `12345`
6. Complete checkout
7. You should be redirected to `/welcome`
8. Check your database - you should see a new user and subscription!

```sql
-- In Supabase SQL Editor
SELECT * FROM users ORDER BY created_at DESC LIMIT 1;
SELECT * FROM subscriptions ORDER BY created_at DESC LIMIT 1;
```

## Troubleshooting

### Checkout Button Not Working?
- Check browser console for errors
- Verify all environment variables are set
- Make sure frontend is running on port 3001

### Webhook Not Receiving Events?
- Is Stripe CLI running? (`stripe listen...`)
- Did you add `STRIPE_WEBHOOK_SECRET` to `.env.local`?
- Check the Stripe CLI terminal for incoming events

### Database Errors?
- Did you run the migration?
- Check Supabase logs
- Verify RLS policies are enabled

### Payment Not Recording?
- Check webhook handler logs in browser console
- Verify `API_SECRET_KEY` is set
- Make sure backend API is running

## Test Cards

| Card Number | Result |
|------------|--------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Declined |
| 4000 0027 6000 3184 | 3D Secure |

## Next Steps

Once basic checkout is working:

1. **Set up proper webhooks:**
   - Deploy to staging/production
   - Configure webhook in Stripe Dashboard
   - Point to your public URL

2. **Test subscription management:**
   ```bash
   # Get current subscription
   curl http://localhost:8000/api/subscriptions/current \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

   # Create billing portal
   curl -X POST http://localhost:8000/api/subscriptions/create-portal-session \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Implement email notifications:**
   - Welcome email on signup
   - Payment receipt
   - Cancellation confirmation

4. **Add monitoring:**
   - Failed payments
   - Subscription churn
   - Revenue metrics

5. **Go live:**
   - Switch to live Stripe keys
   - Update webhook URL
   - Test with real card

## Production Checklist

Before going live:

- [ ] Switch to live Stripe keys
- [ ] Create live products and prices
- [ ] Update all price IDs
- [ ] Configure production webhook URL
- [ ] Enable HTTPS
- [ ] Test with real credit card
- [ ] Set up monitoring
- [ ] Configure email notifications
- [ ] Review security settings
- [ ] Test cancellation flow

## Need Help?

- Check `STRIPE_SETUP.md` for detailed setup instructions
- Check `STRIPE_IMPLEMENTATION_SUMMARY.md` for architecture details
- Review Stripe documentation: https://stripe.com/docs
- Check Stripe logs: https://dashboard.stripe.com/test/logs
- Check webhook events: https://dashboard.stripe.com/test/webhooks

## Common Commands

```bash
# Test Stripe CLI
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_succeeded

# View Stripe logs
stripe logs tail

# Test webhook endpoint
curl -X POST http://localhost:3001/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "ping"}'
```

---

**That's it!** You should now have a working Stripe integration. 🎉

For production deployment, see `STRIPE_SETUP.md`.
