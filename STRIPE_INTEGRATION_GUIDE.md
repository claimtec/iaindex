# Stripe Payment Integration - Complete Setup Guide

**Version:** 1.0
**Last Updated:** October 18, 2025
**Status:** Integration Complete - Ready for Testing

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Files Created](#files-created)
4. [Database Schema](#database-schema)
5. [Environment Variables](#environment-variables)
6. [Stripe Dashboard Setup](#stripe-dashboard-setup)
7. [Local Testing](#local-testing)
8. [Deployment](#deployment)
9. [Testing Checklist](#testing-checklist)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Stripe integration provides a complete subscription billing system with the following features:

- **3 Pricing Tiers:**
  - Starter: $29/month (1 website, weekly checks)
  - Professional: $79/month (5 websites, daily checks, API access)
  - Agency: $199/month (50 websites, real-time monitoring, white-label)

- **Payment Features:**
  - Stripe Checkout for subscription creation
  - Webhook handlers for all payment events
  - Customer portal for subscription management
  - Subscription cancellation/reactivation
  - Payment history tracking
  - Email notifications (ready for integration)

---

## Architecture

### Frontend (Next.js - apps/scan)

```
/pricing → Displays pricing tiers
  ↓
/api/create-checkout → Creates Stripe Checkout Session
  ↓
Stripe Checkout (hosted by Stripe)
  ↓
/welcome → Success page after payment
```

### Backend (FastAPI - apps/api)

```
Stripe Webhook → /api/subscriptions/webhook/*
  ↓
Updates database (users, subscriptions, payment_history)
  ↓
Sends emails (optional)
```

### Database Flow

```
1. User completes checkout
2. Webhook creates user in `users` table
3. Subscription created in `subscriptions` table
4. Payments logged in `payment_history` table
5. User can access dashboard with subscription
```

---

## Files Created

### Frontend (apps/scan)

| File | Purpose | Status |
|------|---------|--------|
| `/app/pricing/page.tsx` | Pricing page with 3 tiers | ✅ Complete |
| `/app/welcome/page.tsx` | Success page after checkout | ✅ Complete |
| `/app/api/create-checkout/route.ts` | Create Stripe Checkout Session | ✅ Complete |
| `/app/api/webhook/route.ts` | Stripe webhook handler (frontend) | ✅ Complete |
| `/lib/stripe.ts` | Stripe configuration and plans | ✅ Complete |
| `/.env.example` | Environment variables template | ✅ Complete |

### Backend (apps/api)

| File | Purpose | Status |
|------|---------|--------|
| `/src/routes/subscriptions.py` | Subscription management routes | ✅ Complete |
| `/src/config.py` | Stripe configuration | ✅ Complete |
| `/requirements.txt` | Includes stripe>=11.0.0 | ✅ Complete |

### Database

| File | Purpose | Status |
|------|---------|--------|
| `/migrations/002_add_subscriptions.sql` | Users, subscriptions, payment_history tables | ✅ Complete |

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT,
  stripe_customer_id TEXT UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Subscriptions Table

```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT UNIQUE NOT NULL,
  stripe_customer_id TEXT NOT NULL,
  plan TEXT NOT NULL, -- 'starter', 'professional', 'agency'
  status TEXT NOT NULL, -- 'active', 'canceled', 'past_due', etc.
  current_period_start TIMESTAMPTZ NOT NULL,
  current_period_end TIMESTAMPTZ NOT NULL,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Payment History Table

```sql
CREATE TABLE payment_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
  stripe_invoice_id TEXT UNIQUE,
  amount INTEGER NOT NULL, -- Amount in cents
  currency TEXT NOT NULL DEFAULT 'usd',
  status TEXT NOT NULL, -- 'succeeded', 'failed', 'pending', 'refunded'
  attempt_count INTEGER DEFAULT 1,
  paid_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Helper Functions

- `get_active_subscription(user_id)` - Get active subscription for user
- `has_active_subscription(user_id)` - Check if user has active subscription
- `get_plan_limits(plan)` - Get plan limits (websites, frequency, API access)

---

## Environment Variables

### Frontend (apps/scan/.env)

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxx  # From Stripe Dashboard
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx  # From Stripe Webhook settings

# Stripe Price IDs (create these in Stripe Dashboard)
NEXT_PUBLIC_STRIPE_PRICE_STARTER=price_xxxxxxxxx
NEXT_PUBLIC_STRIPE_PRICE_PRO=price_xxxxxxxxx
NEXT_PUBLIC_STRIPE_PRICE_AGENCY=price_xxxxxxxxx

# Application URLs
NEXT_PUBLIC_SITE_URL=http://localhost:3001
NEXT_PUBLIC_APP_URL=https://app.iaindex.org
NEXT_PUBLIC_API_URL=http://localhost:8000

# API Authentication (shared secret for webhook auth)
API_SECRET_KEY=your-random-secret-key-here
```

### Backend (apps/api/.env)

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# Application URLs
APP_URL=https://app.iaindex.org
SITE_URL=http://localhost:3001

# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT Configuration (REQUIRED - generate with: openssl rand -hex 32)
SECRET_KEY=your-64-character-secret-key-here
```

---

## Stripe Dashboard Setup

### Step 1: Create Stripe Account

1. Go to [https://dashboard.stripe.com/register](https://dashboard.stripe.com/register)
2. Sign up for a Stripe account
3. Verify your email address
4. Switch to **Test Mode** (toggle in top right)

### Step 2: Create Products and Prices

#### Create Starter Plan ($29/month)

1. Go to **Products** → **Add Product**
2. Product Details:
   - Name: `IAIndex Starter`
   - Description: `1 website, weekly AI visibility checks`
3. Pricing:
   - Model: `Recurring`
   - Price: `$29.00`
   - Billing period: `Monthly`
   - Currency: `USD`
4. Click **Save Product**
5. Copy the **Price ID** (starts with `price_`)
6. Add to `.env` as `NEXT_PUBLIC_STRIPE_PRICE_STARTER`

#### Create Professional Plan ($79/month)

1. Go to **Products** → **Add Product**
2. Product Details:
   - Name: `IAIndex Professional`
   - Description: `5 websites, daily checks, API access`
3. Pricing:
   - Model: `Recurring`
   - Price: `$79.00`
   - Billing period: `Monthly`
   - Currency: `USD`
4. Click **Save Product**
5. Copy the **Price ID** (starts with `price_`)
6. Add to `.env` as `NEXT_PUBLIC_STRIPE_PRICE_PRO`

#### Create Agency Plan ($199/month)

1. Go to **Products** → **Add Product**
2. Product Details:
   - Name: `IAIndex Agency`
   - Description: `50 websites, real-time monitoring, white-label`
3. Pricing:
   - Model: `Recurring`
   - Price: `$199.00`
   - Billing period: `Monthly`
   - Currency: `USD`
4. Click **Save Product**
5. Copy the **Price ID** (starts with `price_`)
6. Add to `.env` as `NEXT_PUBLIC_STRIPE_PRICE_AGENCY`

### Step 3: Get API Keys

1. Go to **Developers** → **API Keys**
2. Copy **Publishable key** (starts with `pk_test_`)
   - Add to `.env` as `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
3. Click **Reveal test key** for **Secret key** (starts with `sk_test_`)
   - Add to `.env` as `STRIPE_SECRET_KEY`

### Step 4: Configure Webhooks

#### For Local Development (using Stripe CLI)

1. Install Stripe CLI: [https://stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli)
2. Login to Stripe CLI:
   ```bash
   stripe login
   ```
3. Forward webhooks to local server:
   ```bash
   stripe listen --forward-to http://localhost:3001/api/webhook
   ```
4. Copy the webhook signing secret (starts with `whsec_`)
5. Add to `.env` as `STRIPE_WEBHOOK_SECRET`

#### For Production (hosted webhook)

1. Go to **Developers** → **Webhooks**
2. Click **Add Endpoint**
3. Endpoint URL: `https://scan.iaindex.org/api/webhook`
4. Events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add Endpoint**
6. Copy the **Signing Secret** (starts with `whsec_`)
7. Add to production `.env` as `STRIPE_WEBHOOK_SECRET`

### Step 5: Configure Customer Portal

1. Go to **Settings** → **Billing** → **Customer Portal**
2. Click **Activate test link**
3. Configure portal features:
   - ✅ Subscription cancellation
   - ✅ Subscription pause
   - ✅ Payment method update
   - ✅ Invoice history
4. Save settings

---

## Local Testing

### Step 1: Apply Database Migration

```bash
# Connect to your Supabase database
psql "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres"

# Or use Supabase SQL Editor
# Copy and paste the contents of migrations/002_add_subscriptions.sql
```

### Step 2: Start Backend API

```bash
cd apps/api

# Install dependencies
pip install -r requirements.txt

# Set environment variables (copy from .env.example)
cp .env.example .env
# Edit .env with your actual values

# Start the API
uvicorn src.main:app --reload --port 8000
```

### Step 3: Start Frontend

```bash
cd apps/scan

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your actual Stripe keys

# Start the dev server
npm run dev
```

### Step 4: Start Stripe Webhook Forwarding

```bash
# In a new terminal
stripe listen --forward-to http://localhost:3001/api/webhook
```

### Step 5: Test the Payment Flow

1. Open browser: `http://localhost:3001/pricing`
2. Enter your email address
3. Click "Get Started" on any plan
4. Use Stripe test card:
   - Card Number: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., `12/34`)
   - CVC: Any 3 digits (e.g., `123`)
   - ZIP: Any 5 digits (e.g., `12345`)
5. Complete checkout
6. You should be redirected to `/welcome` page
7. Check terminal logs for webhook events
8. Verify database:
   ```sql
   SELECT * FROM users;
   SELECT * FROM subscriptions;
   SELECT * FROM payment_history;
   ```

---

## Deployment

### Frontend (Azure Static Web Apps or Vercel)

#### Environment Variables to Set:

```bash
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
NEXT_PUBLIC_STRIPE_PRICE_STARTER=price_xxxxxxxxxxxxx
NEXT_PUBLIC_STRIPE_PRICE_PRO=price_xxxxxxxxxxxxx
NEXT_PUBLIC_STRIPE_PRICE_AGENCY=price_xxxxxxxxxxxxx
NEXT_PUBLIC_SITE_URL=https://scan.iaindex.org
NEXT_PUBLIC_APP_URL=https://app.iaindex.org
NEXT_PUBLIC_API_URL=https://api.iaindex.org
API_SECRET_KEY=your-production-secret-key
```

### Backend (Azure Container Apps)

#### Environment Variables to Set:

```bash
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
APP_URL=https://app.iaindex.org
SITE_URL=https://scan.iaindex.org
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SECRET_KEY=your-64-character-production-secret-key
```

### Stripe Production Setup

1. **Switch to Live Mode** in Stripe Dashboard
2. **Recreate Products** in Live Mode (same as test mode)
3. **Get Live API Keys** from Developers → API Keys
4. **Create Live Webhook** pointing to production URL
5. **Test with real credit card** (use small amount first)

---

## Testing Checklist

### Manual Testing

- [ ] **Pricing Page Loads** - http://localhost:3001/pricing
- [ ] **Email Input Works** - Can enter email address
- [ ] **Checkout Session Created** - Clicking "Get Started" redirects to Stripe
- [ ] **Stripe Checkout Loads** - Stripe hosted page appears
- [ ] **Test Payment Success** - Using test card `4242 4242 4242 4242`
- [ ] **Redirect to Welcome Page** - After successful payment
- [ ] **User Created in Database** - Check `users` table
- [ ] **Subscription Created** - Check `subscriptions` table
- [ ] **Webhook Events Received** - Check terminal logs
- [ ] **Backend Webhook Endpoints Work** - Check API logs

### Test Card Numbers

| Card Number | Description |
|-------------|-------------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0025 0000 3155` | 3D Secure authentication required |
| `4000 0000 0000 9995` | Declined (insufficient funds) |
| `4000 0000 0000 0002` | Declined (generic decline) |

### Webhook Events to Test

- [ ] `checkout.session.completed` - User subscribes
- [ ] `customer.subscription.updated` - Subscription changes
- [ ] `customer.subscription.deleted` - Subscription canceled
- [ ] `invoice.payment_succeeded` - Payment succeeds
- [ ] `invoice.payment_failed` - Payment fails

### Subscription Management Testing

- [ ] **Get Current Subscription** - `GET /api/subscriptions/current`
- [ ] **Create Portal Session** - `POST /api/subscriptions/create-portal-session`
- [ ] **Cancel Subscription** - `POST /api/subscriptions/cancel`
- [ ] **Reactivate Subscription** - `POST /api/subscriptions/reactivate`

---

## API Endpoints

### Frontend Routes (Next.js API Routes)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/create-checkout` | POST | Create Stripe Checkout Session |
| `/api/webhook` | POST | Handle Stripe webhooks (frontend) |

### Backend Routes (FastAPI)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/subscriptions/current` | GET | Get current user subscription | Yes (JWT) |
| `/api/subscriptions/create-portal-session` | POST | Create billing portal session | Yes (JWT) |
| `/api/subscriptions/cancel` | POST | Cancel subscription at period end | Yes (JWT) |
| `/api/subscriptions/reactivate` | POST | Reactivate canceled subscription | Yes (JWT) |
| `/api/subscriptions/webhook/checkout-completed` | POST | Handle checkout completion | Yes (API Key) |
| `/api/subscriptions/webhook/subscription-updated` | POST | Handle subscription update | Yes (API Key) |
| `/api/subscriptions/webhook/subscription-deleted` | POST | Handle subscription deletion | Yes (API Key) |
| `/api/subscriptions/webhook/payment-succeeded` | POST | Handle successful payment | Yes (API Key) |
| `/api/subscriptions/webhook/payment-failed` | POST | Handle failed payment | Yes (API Key) |

---

## Troubleshooting

### Issue: Checkout button does nothing

**Solution:** Check browser console for errors. Verify:
- Stripe price IDs are set in `.env`
- Email address is entered
- API endpoint `/api/create-checkout` is accessible

### Issue: Webhook events not received

**Solution:**
- Check Stripe CLI is running: `stripe listen --forward-to http://localhost:3001/api/webhook`
- Verify webhook secret in `.env`
- Check terminal for webhook event logs

### Issue: User not created in database

**Solution:**
- Check backend API logs
- Verify Supabase connection
- Check `API_SECRET_KEY` matches between frontend and backend
- Verify database migration has been applied

### Issue: Payment succeeds but subscription not active

**Solution:**
- Check webhook handler logs
- Verify subscription status in Stripe Dashboard
- Check `subscriptions` table in database
- Ensure webhook endpoint is reachable

### Issue: "Invalid signature" error on webhook

**Solution:**
- Verify `STRIPE_WEBHOOK_SECRET` is correct
- Ensure webhook secret matches the one in Stripe Dashboard
- Check that raw body is being passed to signature verification

### Issue: Billing portal doesn't work

**Solution:**
- Enable Customer Portal in Stripe Dashboard
- Verify user has `stripe_customer_id` in database
- Check `APP_URL` is set correctly in environment variables

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] All environment variables configured in production
- [ ] Database migration applied to production database
- [ ] Stripe products created in Live Mode
- [ ] Stripe webhook configured for production URL
- [ ] Test payment flow in staging environment
- [ ] Customer portal configured in Stripe
- [ ] SSL/HTTPS enabled for all domains

### Post-Deployment

- [ ] Verify pricing page loads: https://scan.iaindex.org/pricing
- [ ] Test checkout with real credit card (small amount)
- [ ] Verify webhook events are received
- [ ] Check user and subscription created in database
- [ ] Test billing portal access
- [ ] Test subscription cancellation
- [ ] Monitor error logs for 24 hours
- [ ] Set up Stripe email notifications
- [ ] Configure Stripe Dashboard alerts

### Monitoring

- [ ] Set up Stripe webhook monitoring
- [ ] Configure alerts for failed payments
- [ ] Monitor subscription churn rate
- [ ] Track successful conversions
- [ ] Set up revenue tracking

---

## Support and Resources

### Stripe Documentation

- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Webhook Events](https://stripe.com/docs/webhooks)
- [Customer Portal](https://stripe.com/docs/billing/subscriptions/customer-portal)
- [Test Cards](https://stripe.com/docs/testing)

### IAIndex Resources

- Backend API: `/apps/api/src/routes/subscriptions.py`
- Frontend Integration: `/apps/scan/app/api/`
- Database Schema: `/migrations/002_add_subscriptions.sql`

### Contact

For issues or questions, contact the development team or create an issue in the project repository.

---

**Last Updated:** October 18, 2025
**Next Review:** Before Production Launch
