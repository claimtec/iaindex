'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { PolicyChart } from '@/components/charts/policy-chart'
import { IntentBreakdown } from '@/components/charts/intent-breakdown'
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import {
  FileText,
  Download,
  Calendar,
  Shield,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Activity,
} from 'lucide-react'
import { Select } from '@/components/ui/select'

// Mock data - in production, this would come from an API
const complianceData = {
  summary: {
    totalRequests: 45823,
    allowedRequests: 38901,
    deniedRequests: 6922,
    complianceRate: 84.9,
  },
  timeSeriesData: [
    { date: '2025-10-06', allowed: 5234, denied: 892 },
    { date: '2025-10-07', allowed: 5891, denied: 1023 },
    { date: '2025-10-08', allowed: 6123, denied: 987 },
    { date: '2025-10-09', allowed: 5678, denied: 856 },
    { date: '2025-10-10', allowed: 5912, denied: 1145 },
    { date: '2025-10-11', allowed: 6034, denied: 923 },
    { date: '2025-10-12', allowed: 6029, denied: 1096 },
  ],
  intentBreakdown: [
    { name: 'Retrieval', value: 28934, percentage: 63.1 },
    { name: 'Training', value: 12456, percentage: 27.2 },
    { name: 'Scraping', value: 3245, percentage: 7.1 },
    { name: 'Unknown', value: 1188, percentage: 2.6 },
  ],
  topDeniedClients: [
    { name: 'scraperbot-v2', requests: 2341, violations: 2341 },
    { name: 'unknown-crawler', requests: 1823, violations: 1823 },
    { name: 'data-harvester', requests: 1456, violations: 1456 },
    { name: 'ml-trainer-bot', requests: 892, violations: 892 },
    { name: 'content-copier', requests: 410, violations: 410 },
  ],
  violationTypes: [
    { type: 'blocked_training', count: 3245, percentage: 46.9 },
    { type: 'rate_limit_exceeded', count: 1823, percentage: 26.3 },
    { type: 'blocklist_match', count: 1156, percentage: 16.7 },
    { type: 'missing_receipt', count: 456, percentage: 6.6 },
    { type: 'invalid_pattern', count: 242, percentage: 3.5 },
  ],
}

export default function CompliancePage() {
  const [dateRange, setDateRange] = useState('7d')
  const [exportFormat, setExportFormat] = useState<'pdf' | 'csv'>('csv')

  const handleExport = () => {
    // In production, this would trigger actual export
    console.log(`Exporting compliance report as ${exportFormat}`)
    alert(`Exporting compliance report as ${exportFormat.toUpperCase()}...`)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Compliance Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor policy compliance and access patterns
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export Report
          </Button>
          <Button variant="outline">
            <Calendar className="mr-2 h-4 w-4" />
            {dateRange === '7d' ? 'Last 7 Days' : dateRange === '30d' ? 'Last 30 Days' : 'Custom'}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {complianceData.summary.totalRequests.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Last 7 days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Allowed</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {complianceData.summary.allowedRequests.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {((complianceData.summary.allowedRequests / complianceData.summary.totalRequests) * 100).toFixed(1)}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Denied</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {complianceData.summary.deniedRequests.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {((complianceData.summary.deniedRequests / complianceData.summary.totalRequests) * 100).toFixed(1)}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {complianceData.summary.complianceRate}%
            </div>
            <Badge variant="default" className="mt-1 bg-green-600">
              Healthy
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Policy Compliance Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Policy Compliance Over Time</CardTitle>
          <CardDescription>
            Allowed vs denied requests by date
          </CardDescription>
        </CardHeader>
        <CardContent>
          <PolicyChart data={complianceData.timeSeriesData} variant="line" />
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* Intent Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Intent Type Breakdown</CardTitle>
            <CardDescription>
              Distribution of request intents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <IntentBreakdown data={complianceData.intentBreakdown} />
            <div className="mt-4 space-y-2">
              {complianceData.intentBreakdown.map((intent) => (
                <div
                  key={intent.name}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-muted-foreground">{intent.name}</span>
                  <span className="font-medium">
                    {intent.value.toLocaleString()} ({intent.percentage.toFixed(1)}%)
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Denied Clients */}
        <Card>
          <CardHeader>
            <CardTitle>Top Denied Clients</CardTitle>
            <CardDescription>
              Clients with most policy violations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart
                data={complianceData.topDeniedClients}
                layout="vertical"
                margin={{ left: 100 }}
              >
                <XAxis type="number" stroke="#888888" fontSize={12} />
                <YAxis
                  type="category"
                  dataKey="name"
                  stroke="#888888"
                  fontSize={12}
                  width={100}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="rounded-lg border bg-background p-2 shadow-sm">
                          <div className="grid gap-2">
                            <div className="flex flex-col">
                              <span className="text-[0.70rem] uppercase text-muted-foreground">
                                Client
                              </span>
                              <span className="font-bold">
                                {payload[0].payload.name}
                              </span>
                            </div>
                            <div className="flex flex-col">
                              <span className="text-[0.70rem] uppercase text-muted-foreground">
                                Violations
                              </span>
                              <span className="font-bold text-red-600">
                                {payload[0].payload.violations}
                              </span>
                            </div>
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Bar dataKey="violations" fill="hsl(0, 84%, 60%)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Violation Types */}
      <Card>
        <CardHeader>
          <CardTitle>Violation Types</CardTitle>
          <CardDescription>
            Breakdown of policy violation reasons
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {complianceData.violationTypes.map((violation) => (
              <div key={violation.type} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <span className="font-medium capitalize">
                      {violation.type.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">
                      {violation.count.toLocaleString()} violations
                    </span>
                    <Badge variant="outline">{violation.percentage.toFixed(1)}%</Badge>
                  </div>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full bg-red-600"
                    style={{ width: `${violation.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Stacked Area Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Request Intent Over Time</CardTitle>
          <CardDescription>
            Stacked view of allowed and denied requests
          </CardDescription>
        </CardHeader>
        <CardContent>
          <PolicyChart data={complianceData.timeSeriesData} variant="area" />
        </CardContent>
      </Card>

      {/* Export Options */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Export Compliance Report
          </CardTitle>
          <CardDescription>
            Download detailed compliance reports for auditing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Button
              variant="outline"
              className="h-20 flex-col"
              onClick={() => {
                setExportFormat('pdf')
                handleExport()
              }}
            >
              <FileText className="h-6 w-6 mb-2" />
              <span>Export as PDF</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col"
              onClick={() => {
                setExportFormat('csv')
                handleExport()
              }}
            >
              <FileText className="h-6 w-6 mb-2" />
              <span>Export as CSV</span>
            </Button>
          </div>
          <p className="text-xs text-muted-foreground text-center">
            Reports include all compliance metrics, violation details, and client information
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
