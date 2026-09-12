# Stripe Payment Integration Setup

This document provides comprehensive instructions for setting up and configuring the Stripe payment integration for IAIndex.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Stripe Configuration](#stripe-configuration)
4. [Database Setup](#database-setup)
5. [Testing](#testing)
6. [Production Deployment](#production-deployment)

## Prerequisites

- Stripe account (sign up at https://stripe.com)
- Supabase project with database access
- Node.js 18+ and Python 3.9+ installed
- Access to deploy webhooks (public URL required)

## Environment Variables

### Frontend (Scan Tool) - `.env.local`

Add the following to `/apps/scan/.env.local`:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_... # Your Stripe secret key (test mode)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_... # Your Stripe publishable key (test mode)
STRIPE_WEBHOOK_SECRET=whsec_... # Your webhook signing secret

# Stripe Price IDs (create these in Stripe Dashboard)
NEXT_PUBLIC_STRIPE_PRICE_STARTER=price_... # Starter plan price ID
NEXT_PUBLIC_STRIPE_PRICE_PRO=price_... # Professional plan price ID
NEXT_PUBLIC_STRIPE_PRICE_AGENCY=price_... # Agency plan price ID

# Application URLs
NEXT_PUBLIC_SITE_URL=http://localhost:3001 # Scan tool URL
NEXT_PUBLIC_APP_URL=https://app.iaindex.org # Dashboard URL
NEXT_PUBLIC_API_URL=http://localhost:8000 # API URL

# API Authentication
API_SECRET_KEY=your-secret-key-here # Shared secret for webhook authentication
```

### Backend (API) - `.env`

Add the following to `/apps/api/.env`:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_... # Your Stripe secret key (test mode)
STRIPE_WEBHOOK_SECRET=whsec_... # Your webhook signing secret (optional, for direct webhook handling)

# Application URLs
APP_URL=https://app.iaindex.org # Dashboard URL
SITE_URL=http://localhost:3001 # Scan tool URL

# Existing Supabase configuration
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## Stripe Configuration

### 1. Create Stripe Account

1. Sign up at https://stripe.com
2. Complete business verification (for production)
3. Enable test mode for development

### 2. Create Products and Prices

Navigate to Stripe Dashboard → Products and create three products:

#### Starter Plan
- **Product Name:** IAIndex Starter
- **Price:** $29.00 USD
- **Billing Period:** Monthly recurring
- **Price ID:** Copy this to `NEXT_PUBLIC_STRIPE_PRICE_STARTER`

#### Professional Plan
- **Product Name:** IAIndex Professional
- **Price:** $79.00 USD
- **Billing Period:** Monthly recurring
- **Price ID:** Copy this to `NEXT_PUBLIC_STRIPE_PRICE_PRO`

#### Agency Plan
- **Product Name:** IAIndex Agency
- **Price:** $199.00 USD
- **Billing Period:** Monthly recurring
- **Price ID:** Copy this to `NEXT_PUBLIC_STRIPE_PRICE_AGENCY`

### 3. Configure Webhook

1. Navigate to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. **Endpoint URL:** `https://your-domain.com/api/webhook`
4. **Events to send:**
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the **Signing secret** to `STRIPE_WEBHOOK_SECRET`

### 4. Get API Keys

1. Navigate to Stripe Dashboard → Developers → API keys
2. Copy **Publishable key** (starts with `pk_test_`) to `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
3. Copy **Secret key** (starts with `sk_test_`) to `STRIPE_SECRET_KEY`

## Database Setup

### 1. Run Migration

Apply the subscription migration to your Supabase database:

```bash
# Using Supabase CLI
supabase db push

# Or manually in Supabase SQL Editor
# Copy and paste the contents of migrations/002_add_subscriptions.sql
```

### 2. Verify Tables

Ensure the following tables were created:
- `users`
- `subscriptions`
- `payment_history`

### 3. Test Helper Functions

```sql
-- Test getting active subscription
SELECT * FROM get_active_subscription('user-uuid-here');

-- Test checking if user has active subscription
SELECT has_active_subscription('user-uuid-here');

-- Test getting plan limits
SELECT * FROM get_plan_limits('professional');
```

## Testing

### 1. Test Mode Setup

Stripe provides test mode for safe testing without real charges:

**Test Cards:**
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- 3D Secure: `4000 0027 6000 3184`

**Test Details:**
- Expiry: Any future date (e.g., 12/25)
- CVC: Any 3 digits (e.g., 123)
- ZIP: Any 5 digits (e.g., 12345)

### 2. Local Webhook Testing

Use Stripe CLI to forward webhooks to localhost:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:3001/api/webhook

# This will output a webhook signing secret
# Copy it to STRIPE_WEBHOOK_SECRET
```

### 3. Test Checkout Flow

1. Start the scan tool: `cd apps/scan && npm run dev`
2. Navigate to http://localhost:3001/pricing
3. Enter test email address
4. Click "Get Started" on any plan
5. Use test card `4242 4242 4242 4242`
6. Complete checkout
7. Verify redirect to welcome page
8. Check database for user and subscription records

### 4. Test Webhook Handling

```bash
# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_succeeded
```

### 5. Test Subscription Management

1. Get current subscription:
   ```bash
   curl http://localhost:8000/api/subscriptions/current \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

2. Create billing portal session:
   ```bash
   curl -X POST http://localhost:8000/api/subscriptions/create-portal-session \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. Cancel subscription:
   ```bash
   curl -X POST http://localhost:8000/api/subscriptions/cancel \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

## Production Deployment

### 1. Switch to Live Mode

1. Complete Stripe account activation
2. Create production products and prices
3. Update environment variables with live keys:
   - `sk_live_...` for secret key
   - `pk_live_...` for publishable key
4. Update webhook endpoint to production URL

### 2. Security Checklist

- [ ] All API keys are in environment variables (not hardcoded)
- [ ] Webhook signature verification is enabled
- [ ] HTTPS is enforced on all endpoints
- [ ] Database RLS policies are enabled
- [ ] Rate limiting is configured
- [ ] Error messages don't expose sensitive data
- [ ] Logging excludes sensitive information

### 3. Webhook Configuration

Update webhook endpoint in Stripe Dashboard:
```
https://scan.iaindex.org/api/webhook
```

Ensure the webhook secret is updated in production environment variables.

### 4. Environment Variables Checklist

Frontend (Scan Tool):
```bash
STRIPE_SECRET_KEY=sk_live_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PRICE_STARTER=price_...
NEXT_PUBLIC_STRIPE_PRICE_PRO=price_...
NEXT_PUBLIC_STRIPE_PRICE_AGENCY=price_...
NEXT_PUBLIC_SITE_URL=https://scan.iaindex.org
NEXT_PUBLIC_APP_URL=https://app.iaindex.org
NEXT_PUBLIC_API_URL=https://api.iaindex.org
API_SECRET_KEY=your-production-secret
```

Backend (API):
```bash
STRIPE_SECRET_KEY=sk_live_...
APP_URL=https://app.iaindex.org
SITE_URL=https://scan.iaindex.org
```

### 5. Monitoring

Set up monitoring for:
- Failed webhook deliveries (Stripe Dashboard)
- Payment failures
- Subscription cancellations
- Database errors

### 6. Testing in Production

1. Create a test subscription with a real card
2. Verify webhook events are received
3. Test billing portal access
4. Test subscription cancellation
5. Verify email notifications
6. Cancel test subscription

## Troubleshooting

### Webhook Not Receiving Events

1. Check webhook URL is publicly accessible
2. Verify webhook secret is correct
3. Check Stripe Dashboard → Webhooks for failed deliveries
4. Test with Stripe CLI: `stripe listen --forward-to your-url`

### Checkout Session Fails

1. Verify price IDs are correct
2. Check Stripe API keys are valid
3. Ensure success/cancel URLs are correct
4. Review browser console for errors

### Database Errors

1. Verify migration was applied successfully
2. Check RLS policies allow operations
3. Ensure Supabase connection is configured
4. Review API logs for detailed errors

### Payment Not Recording

1. Check webhook is receiving events
2. Verify API authentication for webhooks
3. Review webhook handler logs
4. Check database permissions

## Support

For issues:
1. Review Stripe Dashboard logs
2. Check application logs
3. Test with Stripe CLI
4. Contact Stripe Support for platform issues
5. Review Stripe documentation: https://stripe.com/docs

## Additional Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Stripe API Reference](https://stripe.com/docs/api)
