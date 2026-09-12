'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { billingAPI } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import {
  CreditCard,
  Download,
  Check,
  Zap,
  TrendingUp,
  ExternalLink,
  Loader2
} from 'lucide-react';

const plans = [
  {
    name: 'Free',
    price: 0,
    interval: 'month',
    features: [
      '1 website',
      '10 visibility checks/month',
      'Basic schema generation',
      'Email support',
    ],
  },
  {
    name: 'Starter',
    price: 29,
    interval: 'month',
    features: [
      '5 websites',
      '100 visibility checks/month',
      'Advanced schema generation',
      'Priority email support',
      'API access',
    ],
    popular: true,
  },
  {
    name: 'Pro',
    price: 99,
    interval: 'month',
    features: [
      '20 websites',
      'Unlimited visibility checks',
      'Advanced schema generation',
      'Priority support',
      'API access',
      'Custom reports',
      'White-label options',
    ],
  },
  {
    name: 'Enterprise',
    price: 299,
    interval: 'month',
    features: [
      'Unlimited websites',
      'Unlimited visibility checks',
      'Advanced schema generation',
      '24/7 dedicated support',
      'API access',
      'Custom reports',
      'White-label options',
      'Custom integrations',
      'SLA guarantee',
    ],
  },
];

export default function BillingPage() {
  const { data: subscription, isLoading: subLoading } = useQuery({
    queryKey: ['subscription'],
    queryFn: async () => {
      const response = await billingAPI.getSubscription();
      return response.data.subscription;
    },
  });

  const { data: invoices, isLoading: invoicesLoading } = useQuery({
    queryKey: ['invoices'],
    queryFn: async () => {
      const response = await billingAPI.getInvoices();
      return response.data.invoices || [];
    },
  });

  const handleUpgrade = async (plan: string) => {
    try {
      const response = await billingAPI.createCheckoutSession(plan);
      if (response.data?.url) {
        window.location.href = response.data.url;
      }
    } catch (err) {
      console.error('Failed to create checkout session:', err);
    }
  };

  const handleManageSubscription = async () => {
    try {
      const response = await billingAPI.createPortalSession();
      if (response.data?.url) {
        window.open(response.data.url, '_blank');
      }
    } catch (err) {
      console.error('Failed to open portal:', err);
    }
  };

  const currentPlan = subscription?.plan || 'free';
  const usage = {
    websites: 3,
    websitesLimit: currentPlan === 'free' ? 1 : currentPlan === 'starter' ? 5 : currentPlan === 'pro' ? 20 : 999,
    checks: 45,
    checksLimit: currentPlan === 'free' ? 10 : currentPlan === 'starter' ? 100 : 999,
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Billing & Subscription</h1>
        <p className="text-gray-600 mt-1">
          Manage your subscription and billing information
        </p>
      </div>

      {/* Current plan */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Current Plan</CardTitle>
              <CardDescription>
                {subscription?.status === 'active' ? 'Your subscription is active' : 'Upgrade to unlock more features'}
              </CardDescription>
            </div>
            {subscription && (
              <Button onClick={handleManageSubscription} variant="outline">
                <ExternalLink size={16} className="mr-2" />
                Manage Subscription
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">Plan</p>
              <p className="text-2xl font-bold text-gray-900 capitalize">{currentPlan}</p>
            </div>
            {subscription?.currentPeriodEnd && (
              <div>
                <p className="text-sm text-gray-600 mb-1">Renews On</p>
                <p className="text-lg font-semibold text-gray-900">
                  {formatDate(subscription.currentPeriodEnd)}
                </p>
              </div>
            )}
            <div>
              <p className="text-sm text-gray-600 mb-1">Status</p>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                subscription?.status === 'active' ? 'bg-success/10 text-success' :
                subscription?.status === 'past_due' ? 'bg-warning/10 text-warning' :
                'bg-gray-100 text-gray-600'
              }`}>
                {subscription?.status || 'free'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Usage */}
      <Card>
        <CardHeader>
          <CardTitle>Usage This Month</CardTitle>
          <CardDescription>Track your current usage against plan limits</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-900">Websites</span>
              <span className="text-sm text-gray-600">
                {usage.websites} / {usage.websitesLimit === 999 ? '∞' : usage.websitesLimit}
              </span>
            </div>
            <Progress value={(usage.websites / usage.websitesLimit) * 100} />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-900">Visibility Checks</span>
              <span className="text-sm text-gray-600">
                {usage.checks} / {usage.checksLimit === 999 ? '∞' : usage.checksLimit}
              </span>
            </div>
            <Progress value={(usage.checks / usage.checksLimit) * 100} />
          </div>
        </CardContent>
      </Card>

      {/* Available plans */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`relative ${
                plan.popular ? 'border-primary shadow-lg' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-primary text-white px-3 py-1 rounded-full text-xs font-medium">
                    Most Popular
                  </span>
                </div>
              )}
              <CardHeader>
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                <div className="mt-2">
                  <span className="text-4xl font-bold text-gray-900">
                    ${plan.price}
                  </span>
                  <span className="text-gray-600">/{plan.interval}</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm">
                      <Check size={16} className="text-success mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  onClick={() => handleUpgrade(plan.name.toLowerCase())}
                  className="w-full"
                  variant={plan.name.toLowerCase() === currentPlan ? 'outline' : 'default'}
                  disabled={plan.name.toLowerCase() === currentPlan}
                >
                  {plan.name.toLowerCase() === currentPlan ? 'Current Plan' : 'Upgrade'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Payment method */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard size={20} />
            Payment Method
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-12 h-8 bg-gradient-to-br from-primary to-secondary rounded flex items-center justify-center">
                <CreditCard size={20} className="text-white" />
              </div>
              <div>
                <p className="font-medium text-gray-900">•••• •••• •••• 4242</p>
                <p className="text-sm text-gray-600">Expires 12/25</p>
              </div>
            </div>
            <Button variant="outline" size="sm">
              Update
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Invoice history */}
      <Card>
        <CardHeader>
          <CardTitle>Invoice History</CardTitle>
          <CardDescription>Download your past invoices</CardDescription>
        </CardHeader>
        <CardContent>
          {invoicesLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : invoices && Array.isArray(invoices) && invoices.length > 0 ? (
            <div className="space-y-3">
              {invoices.map((invoice: any) => (
                <div
                  key={invoice.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      {formatDate(invoice.date)}
                    </p>
                    <p className="text-sm text-gray-600">
                      {formatCurrency(invoice.amount)} •{' '}
                      <span className={`${
                        invoice.status === 'paid' ? 'text-success' :
                        invoice.status === 'pending' ? 'text-warning' :
                        'text-danger'
                      }`}>
                        {invoice.status}
                      </span>
                    </p>
                  </div>
                  {invoice.invoiceUrl && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(invoice.invoiceUrl, '_blank')}
                    >
                      <Download size={16} className="mr-2" />
                      Download
                    </Button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <CreditCard size={32} className="mx-auto mb-2 opacity-20" />
              <p className="text-sm">No invoices yet</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
