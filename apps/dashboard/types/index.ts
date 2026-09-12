export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  subscription?: Subscription;
}

export interface Subscription {
  plan: 'free' | 'starter' | 'pro' | 'enterprise';
  status: 'active' | 'cancelled' | 'past_due';
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
}

export interface Website {
  id: string;
  domain: string;
  name: string;
  description?: string;
  industry?: string;
  logo?: string;
  visibilityScore: number;
  lastScanDate: string;
  status: 'active' | 'pending' | 'error';
  hasSchema: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Schema {
  id: string;
  websiteId: string;
  schemaMarkup: any;
  isValid: boolean;
  validationErrors?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface VisibilityCheck {
  id: string;
  websiteId: string;
  platform: 'chatgpt' | 'perplexity' | 'claude' | 'gemini';
  query: string;
  mentioned: boolean;
  position?: number;
  context?: string;
  checkedAt: string;
}

export interface VisibilityHistory {
  date: string;
  score: number;
  platformScores: {
    chatgpt: number;
    perplexity: number;
    claude: number;
    gemini: number;
  };
}

export interface Activity {
  id: string;
  type: 'schema_generated' | 'visibility_check' | 'website_added' | 'scan_completed';
  websiteId?: string;
  websiteName?: string;
  message: string;
  timestamp: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface DashboardStats {
  totalWebsites: number;
  averageVisibilityScore: number;
  activeScansThisMonth: number;
  recommendationsPending: number;
}

export interface BillingInvoice {
  id: string;
  date: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
  invoiceUrl?: string;
}

export interface ApiKey {
  id: string;
  key: string;
  name: string;
  createdAt: string;
  lastUsed?: string;
  expiresAt?: string;
}
