import { NextRequest, NextResponse } from 'next/server';
import { stripe, getPlanByPriceId } from '@/lib/stripe';
import Stripe from 'stripe';

// Get raw body as buffer
async function getRawBody(request: NextRequest): Promise<Buffer> {
  const arrayBuffer = await request.arrayBuffer();
  return Buffer.from(arrayBuffer);
}

export async function POST(request: NextRequest) {
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!webhookSecret) {
    console.error('Missing STRIPE_WEBHOOK_SECRET environment variable');
    return NextResponse.json(
      { error: 'Webhook secret not configured' },
      { status: 500 }
    );
  }

  try {
    const body = await getRawBody(request);
    const signature = request.headers.get('stripe-signature');

    if (!signature) {
      return NextResponse.json(
        { error: 'Missing stripe-signature header' },
        { status: 400 }
      );
    }

    // Verify webhook signature
    let event: Stripe.Event;
    try {
      event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
    } catch (err) {
      console.error('Webhook signature verification failed:', err);
      return NextResponse.json(
        { error: 'Invalid signature' },
        { status: 400 }
      );
    }

    // Handle different event types
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutSessionCompleted(event.data.object as Stripe.Checkout.Session);
        break;

      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object as Stripe.Subscription);
        break;

      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object as Stripe.Subscription);
        break;

      case 'invoice.payment_succeeded':
        await handleInvoicePaymentSucceeded(event.data.object as Stripe.Invoice);
        break;

      case 'invoice.payment_failed':
        await handleInvoicePaymentFailed(event.data.object as Stripe.Invoice);
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('Webhook error:', error);
    return NextResponse.json(
      { error: 'Webhook processing failed' },
      { status: 500 }
    );
  }
}

async function handleCheckoutSessionCompleted(session: Stripe.Checkout.Session) {
  console.log('Checkout session completed:', session.id);

  const email = session.customer_email;
  const customerId = session.customer as string;
  const subscriptionId = session.subscription as string;
  const plan = session.metadata?.plan;

  if (!email || !plan) {
    console.error('Missing email or plan in session metadata');
    return;
  }

  try {
    // Call backend API to create/update user and subscription
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.iaindex.org';
    const apiKey = process.env.API_SECRET_KEY;

    const response = await fetch(`${apiUrl}/api/subscriptions/webhook/checkout-completed`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        email,
        customerId,
        subscriptionId,
        plan,
        sessionId: session.id,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create user: ${response.statusText}`);
    }

    console.log(`User created/updated for ${email}`);

    // Send welcome email (you can implement this using your email service)
    await sendWelcomeEmail(email, plan);
  } catch (error) {
    console.error('Error handling checkout completion:', error);
    // Log to your error tracking service
  }
}

async function handleSubscriptionUpdated(subscription: Stripe.Subscription) {
  console.log('Subscription updated:', subscription.id);

  const customerId = subscription.customer as string;
  const status = subscription.status;
  const currentPeriodStart = new Date((subscription as any).current_period_start * 1000);
  const currentPeriodEnd = new Date((subscription as any).current_period_end * 1000);
  const cancelAtPeriodEnd = (subscription as any).cancel_at_period_end;

  // Get plan from price ID
  const priceId = subscription.items.data[0]?.price.id;
  const plan = priceId ? getPlanByPriceId(priceId) : null;

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.iaindex.org';
    const apiKey = process.env.API_SECRET_KEY;

    const response = await fetch(`${apiUrl}/api/subscriptions/webhook/subscription-updated`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        subscriptionId: subscription.id,
        customerId,
        plan,
        status,
        currentPeriodStart,
        currentPeriodEnd,
        cancelAtPeriodEnd,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to update subscription: ${response.statusText}`);
    }

    console.log(`Subscription updated for ${customerId}`);
  } catch (error) {
    console.error('Error handling subscription update:', error);
  }
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  console.log('Subscription deleted:', subscription.id);

  const customerId = subscription.customer as string;

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.iaindex.org';
    const apiKey = process.env.API_SECRET_KEY;

    const response = await fetch(`${apiUrl}/api/subscriptions/webhook/subscription-deleted`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        subscriptionId: subscription.id,
        customerId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete subscription: ${response.statusText}`);
    }

    console.log(`Subscription deleted for ${customerId}`);

    // Send cancellation confirmation email
    // await sendCancellationEmail(customerEmail);
  } catch (error) {
    console.error('Error handling subscription deletion:', error);
  }
}

async function handleInvoicePaymentSucceeded(invoice: Stripe.Invoice) {
  console.log('Invoice payment succeeded:', invoice.id);

  const customerId = invoice.customer as string;
  const subscriptionId = (invoice as any).subscription as string;

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.iaindex.org';
    const apiKey = process.env.API_SECRET_KEY;

    const response = await fetch(`${apiUrl}/api/subscriptions/webhook/payment-succeeded`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        invoiceId: invoice.id,
        customerId,
        subscriptionId,
        amount: invoice.amount_paid,
        currency: invoice.currency,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to process payment: ${response.statusText}`);
    }

    console.log(`Payment processed for ${customerId}`);
  } catch (error) {
    console.error('Error handling payment success:', error);
  }
}

async function handleInvoicePaymentFailed(invoice: Stripe.Invoice) {
  console.log('Invoice payment failed:', invoice.id);

  const customerId = invoice.customer as string;
  const subscriptionId = (invoice as any).subscription as string;

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.iaindex.org';
    const apiKey = process.env.API_SECRET_KEY;

    const response = await fetch(`${apiUrl}/api/subscriptions/webhook/payment-failed`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        invoiceId: invoice.id,
        customerId,
        subscriptionId,
        attemptCount: invoice.attempt_count,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to process payment failure: ${response.statusText}`);
    }

    console.log(`Payment failure processed for ${customerId}`);

    // Send payment failure notification email
    // await sendPaymentFailedEmail(customerEmail);
  } catch (error) {
    console.error('Error handling payment failure:', error);
  }
}

async function sendWelcomeEmail(email: string, plan: string) {
  // Implement email sending logic here
  // You can use services like SendGrid, Postmark, AWS SES, etc.
  console.log(`Sending welcome email to ${email} for plan: ${plan}`);

  // Example implementation (placeholder):
  // const emailService = getEmailService();
  // await emailService.send({
  //   to: email,
  //   subject: 'Welcome to IAIndex!',
  //   template: 'welcome',
  //   data: { plan },
  // });
}
