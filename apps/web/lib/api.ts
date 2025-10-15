import { createClient } from '@/lib/supabase/client'

export interface Receipt {
  id: string
  merchant: string
  amount: number
  date: string
  status: 'verified' | 'pending' | 'failed'
  category: string
  verification_method: string
  created_at: string
}

export interface AnalyticsData {
  totalReceipts: number
  verifiedReceipts: number
  totalAmount: number
  averageAmount: number
  topMerchants: Array<{ name: string; count: number; amount: number }>
  categoryBreakdown: Array<{ category: string; count: number; amount: number }>
  dailyStats: Array<{ date: string; count: number; amount: number }>
}

export interface Settings {
  domain: string
  domain_verified: boolean
  api_key: string
  webhook_url: string
  webhook_secret: string
}

export async function getReceipts(filters?: {
  search?: string
  status?: string
  dateFrom?: string
  dateTo?: string
}): Promise<Receipt[]> {
  const supabase = createClient()

  let query = supabase
    .from('receipts')
    .select('*')
    .order('created_at', { ascending: false })

  if (filters?.search) {
    query = query.ilike('merchant', `%${filters.search}%`)
  }

  if (filters?.status) {
    query = query.eq('status', filters.status)
  }

  if (filters?.dateFrom) {
    query = query.gte('date', filters.dateFrom)
  }

  if (filters?.dateTo) {
    query = query.lte('date', filters.dateTo)
  }

  const { data, error } = await query

  if (error) {
    console.error('Error fetching receipts:', error)
    return []
  }

  return data || []
}

export async function getAnalytics(): Promise<AnalyticsData> {
  const supabase = createClient()

  const { data: receipts } = await supabase
    .from('receipts')
    .select('*')
    .order('created_at', { ascending: false })

  if (!receipts || receipts.length === 0) {
    return {
      totalReceipts: 0,
      verifiedReceipts: 0,
      totalAmount: 0,
      averageAmount: 0,
      topMerchants: [],
      categoryBreakdown: [],
      dailyStats: [],
    }
  }

  const verifiedReceipts = receipts.filter(r => r.status === 'verified')
  const totalAmount = receipts.reduce((sum, r) => sum + r.amount, 0)

  // Calculate top merchants
  const merchantMap = new Map<string, { count: number; amount: number }>()
  receipts.forEach(r => {
    const existing = merchantMap.get(r.merchant) || { count: 0, amount: 0 }
    merchantMap.set(r.merchant, {
      count: existing.count + 1,
      amount: existing.amount + r.amount,
    })
  })
  const topMerchants = Array.from(merchantMap.entries())
    .map(([name, data]) => ({ name, ...data }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5)

  // Calculate category breakdown
  const categoryMap = new Map<string, { count: number; amount: number }>()
  receipts.forEach(r => {
    const existing = categoryMap.get(r.category) || { count: 0, amount: 0 }
    categoryMap.set(r.category, {
      count: existing.count + 1,
      amount: existing.amount + r.amount,
    })
  })
  const categoryBreakdown = Array.from(categoryMap.entries())
    .map(([category, data]) => ({ category, ...data }))
    .sort((a, b) => b.amount - a.amount)

  // Calculate daily stats for last 30 days
  const dailyMap = new Map<string, { count: number; amount: number }>()
  receipts.forEach(r => {
    const date = r.created_at.split('T')[0]
    const existing = dailyMap.get(date) || { count: 0, amount: 0 }
    dailyMap.set(date, {
      count: existing.count + 1,
      amount: existing.amount + r.amount,
    })
  })
  const dailyStats = Array.from(dailyMap.entries())
    .map(([date, data]) => ({ date, ...data }))
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(-30)

  return {
    totalReceipts: receipts.length,
    verifiedReceipts: verifiedReceipts.length,
    totalAmount,
    averageAmount: totalAmount / receipts.length,
    topMerchants,
    categoryBreakdown,
    dailyStats,
  }
}

export async function getSettings(): Promise<Settings | null> {
  const supabase = createClient()

  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return null

  const { data, error } = await supabase
    .from('settings')
    .select('*')
    .eq('user_id', user.id)
    .single()

  if (error) {
    console.error('Error fetching settings:', error)
    return null
  }

  return data
}

export async function updateSettings(settings: Partial<Settings>): Promise<boolean> {
  const supabase = createClient()

  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return false

  const { error } = await supabase
    .from('settings')
    .upsert({
      user_id: user.id,
      ...settings,
      updated_at: new Date().toISOString(),
    })

  if (error) {
    console.error('Error updating settings:', error)
    return false
  }

  return true
}

export async function verifyReceipt(receiptId: string): Promise<any> {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('receipts')
    .select('*')
    .eq('id', receiptId)
    .single()

  if (error) {
    console.error('Error verifying receipt:', error)
    return null
  }

  return data
}
