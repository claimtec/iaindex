import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-09-30.clover' as any,
});

export const PLANS = {
  starter: {
    priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_STARTER!,
    name: 'Starter',
    price: 29,
    features: [
      '1 website',
      'Weekly visibility checks',
      'Email reports',
      'Basic schema recommendations',
      'ChatGPT & Perplexity tracking'
    ],
    maxWebsites: 1,
    checkFrequency: 'weekly',
  },
  professional: {
    priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_PRO!,
    name: 'Professional',
    price: 79,
    features: [
      '5 websites',
      'Daily visibility checks',
      'Advanced analytics',
      'API access',
      'Priority support',
      'All AI platforms tracking'
    ],
    maxWebsites: 5,
    checkFrequency: 'daily',
    popular: true,
  },
  agency: {
    priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_AGENCY!,
    name: 'Agency',
    price: 199,
    features: [
      '50 websites',
      'Real-time monitoring',
      'White-label reports',
      'Client portals',
      'Dedicated account manager',
      'Custom integrations'
    ],
    maxWebsites: 50,
    checkFrequency: 'realtime',
  },
} as const;

export type PlanType = keyof typeof PLANS;

export function getPlanByPriceId(priceId: string): PlanType | null {
  const planEntry = Object.entries(PLANS).find(
    ([, plan]) => plan.priceId === priceId
  );
  return planEntry ? (planEntry[0] as PlanType) : null;
}

export function validatePlan(plan: string): plan is PlanType {
  return plan in PLANS;
}
