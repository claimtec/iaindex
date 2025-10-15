import { verifyReceipt } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatDate } from '@/lib/utils'
import { CheckCircle, XCircle, BadgeCheck, Calendar, DollarSign, Store } from 'lucide-react'
import { notFound } from 'next/navigation'

export default async function VerifyPage({ params }: { params: { id: string } }) {
  const receipt = await verifyReceipt(params.id)

  if (!receipt) {
    notFound()
  }

  const isVerified = receipt.status === 'verified'

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="container mx-auto max-w-3xl py-12">
        <div className="mb-8 text-center">
          <div className="mb-4 flex justify-center">
            <BadgeCheck className="h-16 w-16 text-primary" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Receipt Verification</h1>
          <p className="text-muted-foreground">
            Independently verified receipt information
          </p>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Verification Status</CardTitle>
                <CardDescription>Receipt ID: {receipt.id}</CardDescription>
              </div>
              {isVerified ? (
                <Badge className="bg-green-500">
                  <CheckCircle className="mr-1 h-4 w-4" />
                  Verified
                </Badge>
              ) : (
                <Badge variant="destructive">
                  <XCircle className="mr-1 h-4 w-4" />
                  {receipt.status}
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {isVerified ? (
              <div className="rounded-lg bg-green-500/10 p-4">
                <p className="text-sm text-green-600 dark:text-green-400">
                  This receipt has been independently verified and confirmed as authentic.
                  All information displayed below has been validated through our verification
                  system.
                </p>
              </div>
            ) : (
              <div className="rounded-lg bg-destructive/10 p-4">
                <p className="text-sm text-destructive">
                  This receipt could not be verified. The information may be incomplete or
                  invalid. Please contact the merchant for assistance.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Receipt Details</CardTitle>
            <CardDescription>Transaction information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start space-x-3">
              <Store className="mt-0.5 h-5 w-5 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm font-medium">Merchant</p>
                <p className="text-lg">{receipt.merchant}</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <DollarSign className="mt-0.5 h-5 w-5 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm font-medium">Amount</p>
                <p className="text-lg">{formatCurrency(receipt.amount)}</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <Calendar className="mt-0.5 h-5 w-5 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm font-medium">Transaction Date</p>
                <p className="text-lg">{formatDate(receipt.date)}</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <BadgeCheck className="mt-0.5 h-5 w-5 text-muted-foreground" />
              <div className="flex-1">
                <p className="text-sm font-medium">Verification Method</p>
                <p className="text-lg">{receipt.verification_method}</p>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Category</span>
                <Badge variant="outline">{receipt.category}</Badge>
              </div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Verified On</span>
                <span className="text-sm">{formatDate(receipt.created_at)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>About Verification</CardTitle>
            <CardDescription>How we verify receipts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>
                This receipt has been verified using IAIndex's advanced verification system.
                Our verification process includes:
              </p>
              <ul className="list-inside list-disc space-y-1">
                <li>Merchant authentication and validation</li>
                <li>Transaction amount and date verification</li>
                <li>Digital signature validation</li>
                <li>Blockchain-based timestamp recording</li>
              </ul>
              <p className="mt-4 text-xs">
                Verification ID: {receipt.id} | Last Updated: {formatDate(receipt.created_at)}
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="mt-8 text-center">
          <p className="text-xs text-muted-foreground">
            Powered by IAIndex Receipt Verification System
          </p>
        </div>
      </div>
    </div>
  )
}
