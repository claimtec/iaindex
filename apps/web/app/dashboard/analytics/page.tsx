import { getAnalytics } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { OverviewChart } from '@/components/charts/overview-chart'
import { CategoryChart } from '@/components/charts/category-chart'
import { Badge } from '@/components/ui/badge'
import { formatCurrency } from '@/lib/utils'

export const dynamic = 'force-dynamic'

export default async function AnalyticsPage() {
  const analytics = await getAnalytics()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">
          Detailed insights into your receipt data
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Verification Rate</CardTitle>
            <CardDescription>Percentage of verified receipts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">
              {((analytics.verifiedReceipts / analytics.totalReceipts) * 100 || 0).toFixed(1)}%
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              {analytics.verifiedReceipts} of {analytics.totalReceipts} receipts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Revenue</CardTitle>
            <CardDescription>All time transaction value</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">
              {formatCurrency(analytics.totalAmount)}
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              From {analytics.totalReceipts} receipts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Average Transaction</CardTitle>
            <CardDescription>Average receipt amount</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">
              {formatCurrency(analytics.averageAmount || 0)}
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              Per receipt average
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Daily Trends</CardTitle>
          <CardDescription>Receipt volume and amounts over time</CardDescription>
        </CardHeader>
        <CardContent>
          <OverviewChart data={analytics.dailyStats} />
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Category Breakdown</CardTitle>
            <CardDescription>Spending by category</CardDescription>
          </CardHeader>
          <CardContent>
            <CategoryChart data={analytics.categoryBreakdown} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Merchants</CardTitle>
            <CardDescription>Highest transaction volumes</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics.topMerchants.map((merchant, index) => (
                <div key={merchant.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                      {index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{merchant.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {merchant.count} receipts
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">
                      {formatCurrency(merchant.amount)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatCurrency(merchant.amount / merchant.count)} avg
                    </p>
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

      <Card>
        <CardHeader>
          <CardTitle>Category Summary</CardTitle>
          <CardDescription>Spending breakdown by category</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {analytics.categoryBreakdown.map((category) => (
              <div
                key={category.category}
                className="flex items-center justify-between rounded-lg border p-4"
              >
                <div>
                  <p className="text-sm font-medium">{category.category}</p>
                  <p className="text-xs text-muted-foreground">
                    {category.count} receipts
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold">
                    {formatCurrency(category.amount)}
                  </p>
                  <Badge variant="outline" className="mt-1">
                    {((category.amount / analytics.totalAmount) * 100).toFixed(1)}%
                  </Badge>
                </div>
              </div>
            ))}
            {analytics.categoryBreakdown.length === 0 && (
              <p className="col-span-full text-center text-sm text-muted-foreground">
                No category data available
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* v1.1 Features */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Source Breakdown</CardTitle>
            <CardDescription>Verified vs unknown client sources</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-green-600" />
                  <span className="text-sm">Verified Clients</span>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold">12,456</p>
                  <p className="text-xs text-muted-foreground">73.2%</p>
                </div>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                <div className="h-full bg-green-600" style={{ width: '73.2%' }} />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-yellow-600" />
                  <span className="text-sm">Unknown Clients</span>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold">4,567</p>
                  <p className="text-xs text-muted-foreground">26.8%</p>
                </div>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                <div className="h-full bg-yellow-600" style={{ width: '26.8%' }} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Fraud Detection Alerts</CardTitle>
            <CardDescription>Recent suspicious activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-800 dark:bg-red-950">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-red-600 text-white text-xs">
                  !</div>
                <div className="flex-1">
                  <p className="text-sm font-medium">High Rate Limit Breach</p>
                  <p className="text-xs text-muted-foreground">
                    Client exceeded 1000 req/min threshold
                  </p>
                </div>
                <Badge variant="destructive" className="text-xs">
                  Critical
                </Badge>
              </div>

              <div className="flex items-start gap-3 rounded-lg border border-yellow-200 bg-yellow-50 p-3 dark:border-yellow-800 dark:bg-yellow-950">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-yellow-600 text-white text-xs">
                  !</div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Suspicious Pattern</p>
                  <p className="text-xs text-muted-foreground">
                    Unusual access pattern detected
                  </p>
                </div>
                <Badge variant="secondary" className="text-xs">
                  Warning
                </Badge>
              </div>

              <div className="flex items-start gap-3 rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-950">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-white text-xs">
                  i
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">New Client Detected</p>
                  <p className="text-xs text-muted-foreground">
                    Unregistered client attempting access
                  </p>
                </div>
                <Badge variant="outline" className="text-xs">
                  Info
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Bot Reputation</CardTitle>
          <CardDescription>Client reputation scores and violation history</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left text-sm font-medium">Client ID</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Reputation</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Requests</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Violations</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="px-4 py-3 text-sm font-mono">googlebot</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-bold text-green-600">98</div>
                      <div className="h-2 w-20 overflow-hidden rounded-full bg-secondary">
                        <div className="h-full bg-green-600" style={{ width: '98%' }} />
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">8,234</td>
                  <td className="px-4 py-3 text-sm">12</td>
                  <td className="px-4 py-3">
                    <Badge variant="default" className="bg-green-600">Trusted</Badge>
                  </td>
                </tr>
                <tr className="border-b">
                  <td className="px-4 py-3 text-sm font-mono">bingbot</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-bold text-green-600">95</div>
                      <div className="h-2 w-20 overflow-hidden rounded-full bg-secondary">
                        <div className="h-full bg-green-600" style={{ width: '95%' }} />
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">6,123</td>
                  <td className="px-4 py-3 text-sm">28</td>
                  <td className="px-4 py-3">
                    <Badge variant="default" className="bg-green-600">Trusted</Badge>
                  </td>
                </tr>
                <tr className="border-b">
                  <td className="px-4 py-3 text-sm font-mono">ml-crawler-beta</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-bold text-yellow-600">67</div>
                      <div className="h-2 w-20 overflow-hidden rounded-full bg-secondary">
                        <div className="h-full bg-yellow-600" style={{ width: '67%' }} />
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">3,456</td>
                  <td className="px-4 py-3 text-sm">892</td>
                  <td className="px-4 py-3">
                    <Badge variant="secondary">Monitored</Badge>
                  </td>
                </tr>
                <tr className="border-b">
                  <td className="px-4 py-3 text-sm font-mono">scraperbot-v2</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-bold text-red-600">12</div>
                      <div className="h-2 w-20 overflow-hidden rounded-full bg-secondary">
                        <div className="h-full bg-red-600" style={{ width: '12%' }} />
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">2,341</td>
                  <td className="px-4 py-3 text-sm">2,341</td>
                  <td className="px-4 py-3">
                    <Badge variant="destructive">Blocked</Badge>
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-sm font-mono">unknown-agent</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-bold text-red-600">8</div>
                      <div className="h-2 w-20 overflow-hidden rounded-full bg-secondary">
                        <div className="h-full bg-red-600" style={{ width: '8%' }} />
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">1,823</td>
                  <td className="px-4 py-3 text-sm">1,823</td>
                  <td className="px-4 py-3">
                    <Badge variant="destructive">Blocked</Badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
