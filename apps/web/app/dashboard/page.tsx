import { getAnalytics } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { OverviewChart } from '@/components/charts/overview-chart'
import { formatCurrency } from '@/lib/utils'
import { Receipt, CheckCircle, DollarSign, TrendingUp } from 'lucide-react'

export const dynamic = 'force-dynamic'

export default async function DashboardPage() {
  const analytics = await getAnalytics()

  const stats = [
    {
      title: 'Total Receipts',
      value: analytics.totalReceipts.toLocaleString(),
      icon: Receipt,
      description: 'All time receipts',
    },
    {
      title: 'Verified Receipts',
      value: analytics.verifiedReceipts.toLocaleString(),
      icon: CheckCircle,
      description: `${((analytics.verifiedReceipts / analytics.totalReceipts) * 100 || 0).toFixed(1)}% verification rate`,
    },
    {
      title: 'Total Amount',
      value: formatCurrency(analytics.totalAmount),
      icon: DollarSign,
      description: 'All time transaction value',
    },
    {
      title: 'Average Amount',
      value: formatCurrency(analytics.averageAmount || 0),
      icon: TrendingUp,
      description: 'Per receipt average',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard Overview</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's what's happening with your receipts.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Receipt Activity</CardTitle>
            <CardDescription>Daily receipt volume and amounts (last 30 days)</CardDescription>
          </CardHeader>
          <CardContent>
            <OverviewChart data={analytics.dailyStats} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Merchants</CardTitle>
            <CardDescription>Merchants by transaction volume</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.topMerchants.slice(0, 5).map((merchant, index) => (
                <div key={merchant.name} className="flex items-center">
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium leading-none">{merchant.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {merchant.count} receipts
                    </p>
                  </div>
                  <div className="ml-auto font-medium">
                    {formatCurrency(merchant.amount)}
                  </div>
                </div>
              ))}
              {analytics.topMerchants.length === 0 && (
                <p className="text-center text-sm text-muted-foreground">
                  No merchant data available
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
