import { NextRequest, NextResponse } from 'next/server';
import { stripe, PLANS, validatePlan } from '@/lib/stripe';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { plan, email } = body;

    // Validate required fields
    if (!plan || !email) {
      return NextResponse.json(
        { error: 'Missing required fields: plan and email' },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email address' },
        { status: 400 }
      );
    }

    // Validate plan
    if (!validatePlan(plan)) {
      return NextResponse.json(
        { error: 'Invalid plan. Must be one of: starter, professional, agency' },
        { status: 400 }
      );
    }

    const selectedPlan = PLANS[plan];

    // Get base URLs from environment
    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3001';
    const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://app.iaindex.org';

    // Create Stripe checkout session
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [
        {
          price: selectedPlan.priceId,
          quantity: 1,
        },
      ],
      customer_email: email,
      success_url: `${siteUrl}/welcome?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${siteUrl}/pricing?canceled=true`,
      metadata: {
        plan,
        email,
      },
      subscription_data: {
        metadata: {
          plan,
          email,
        },
      },
      allow_promotion_codes: true,
      billing_address_collection: 'auto',
    });

    return NextResponse.json({
      sessionId: session.id,
      url: session.url,
    });
  } catch (error) {
    console.error('Checkout error:', error);

    // Return appropriate error message
    if (error instanceof Error) {
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    );
  }
}
