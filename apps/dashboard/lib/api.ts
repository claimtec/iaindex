import axios from 'axios';
import type {
  Website,
  Schema,
  VisibilityCheck,
  VisibilityHistory,
  DashboardStats,
  Activity,
  User,
  ApiKey,
  BillingInvoice,
  ApiResponse,
  PaginatedResponse
} from '@/types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'https://api.iaindex.org',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and we have a refresh token, try to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (typeof window !== 'undefined') {
        const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');

        if (refreshToken) {
          try {
            const response = await authAPI.refreshToken(refreshToken);
            const { access_token } = response.data;

            // Update stored token
            if (localStorage.getItem('auth_token')) {
              localStorage.setItem('auth_token', access_token);
            } else {
              sessionStorage.setItem('auth_token', access_token);
            }

            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return api(originalRequest);
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            localStorage.removeItem('auth_token');
            localStorage.removeItem('refresh_token');
            sessionStorage.removeItem('auth_token');
            sessionStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        } else {
          // No refresh token, redirect to login
          localStorage.removeItem('auth_token');
          sessionStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth API - Updated to match backend endpoints
export const authAPI = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string; refresh_token: string; token_type: string; user: User }>('/v1/auth/login', { email, password }),

  signup: (email: string, password: string, full_name: string) =>
    api.post<{ access_token: string; refresh_token: string; token_type: string; user: User }>('/v1/auth/register', {
      email,
      password,
      full_name
    }),

  logout: () =>
    api.post('/v1/auth/logout'),

  getProfile: () =>
    api.get<User>('/v1/auth/me'),

  updateProfile: (data: Partial<User>) =>
    api.patch<User>('/v1/auth/update', data),

  refreshToken: (refresh_token: string) =>
    api.post<{ access_token: string; refresh_token: string; token_type: string; user: User }>('/v1/auth/refresh', { refresh_token }),
};

// Websites API - Updated to match backend schema routes
export const websitesAPI = {
  list: (params?: { page?: number; page_size?: number; search?: string }) =>
    api.get<{ websites: Website[]; total: number; page: number }>('/v1/schema/websites', { params }),

  get: (id: string) =>
    api.get<{ website: Website }>(`/v1/schema/${id}`),

  create: (data: { domain: string; name?: string; description?: string; industry?: string }) =>
    api.post<{ website: Website }>('/v1/schema/websites', data),

  update: (id: string, data: Partial<Website>) =>
    api.patch<{ website: Website }>(`/v1/schema/${id}`, data),

  delete: (id: string) =>
    api.delete<{ message: string }>(`/v1/schema/${id}`),
};

// Schema API - Updated to match backend endpoints
export const schemaAPI = {
  get: (websiteId: string) =>
    api.get<{ website: Website }>(`/v1/schema/${websiteId}`),

  generate: (websiteId: string, data?: any) =>
    api.post<{ schema: any; website: Website }>('/v1/schema/generate', { website_id: websiteId, ...data }),

  validate: (schemaMarkup: any) =>
    api.post<{ valid: boolean; errors?: string[]; warnings?: string[] }>('/v1/schema/validate', { schema_markup: schemaMarkup }),

  update: (websiteId: string, schemaMarkup: any) =>
    api.patch<{ website: Website }>(`/v1/schema/${websiteId}`, { schema_markup: schemaMarkup }),
};

// Visibility API - Updated to match backend endpoints
export const visibilityAPI = {
  check: (websiteId: string, queries: string[]) =>
    api.post<{ checks: VisibilityCheck[]; summary: any }>('/v1/visibility/check', {
      website_id: websiteId,
      queries
    }),

  getHistory: (websiteId: string, params?: { days?: number }) =>
    api.get<{ history: VisibilityHistory[]; website: Website }>(`/v1/visibility/${websiteId}/history`, { params }),

  getChecks: (websiteId: string, params?: { page?: number; page_size?: number }) =>
    api.get<{ checks: VisibilityCheck[]; total: number }>(`/v1/visibility/${websiteId}`, { params }),

  getDetail: (websiteId: string) =>
    api.get<{ website: Website; recent_checks: VisibilityCheck[] }>(`/v1/visibility/${websiteId}`),
};

// Analytics/Dashboard API - Using users endpoint for now
export const analyticsAPI = {
  getDashboardStats: () =>
    api.get<{ stats: DashboardStats }>('/v1/users/me/usage'),

  getRecentActivity: (params?: { limit?: number }) =>
    api.get<{ activities: Activity[] }>('/v1/analytics/receipts', { params }),

  getVisibilityTrend: (days: number = 30) =>
    api.get<{ trend: VisibilityHistory[] }>('/v1/analytics/visibility-trend', {
      params: { days }
    }),

  getWebsites: () =>
    api.get<{ websites: Website[]; total: number; plan_limit: number }>('/v1/users/me/websites'),
};

// API Keys - Updated to match backend endpoints
export const apiKeysAPI = {
  list: () =>
    api.get<ApiKey[]>('/v1/users/me/api-keys'),

  create: (name: string, scopes?: string[]) =>
    api.post<ApiKey>('/v1/users/me/api-keys', { name, scopes }),

  revoke: (id: string) =>
    api.delete<{ message: string }>(`/v1/users/me/api-keys/${id}`),
};

// Billing - Updated to match subscription endpoints
export const billingAPI = {
  getSubscription: () =>
    api.get<{ subscription: any }>('/api/subscriptions/current'),

  getInvoices: () =>
    api.get<{ invoices: BillingInvoice[] }>('/api/subscriptions/invoices'),

  createCheckoutSession: (plan: string) =>
    api.post<{ url: string; session_id: string }>('/api/subscriptions/checkout', { plan }),

  createPortalSession: () =>
    api.post<{ url: string }>('/api/subscriptions/create-portal-session'),

  cancelSubscription: () =>
    api.post<{ message: string }>('/api/subscriptions/cancel'),

  reactivateSubscription: () =>
    api.post<{ message: string }>('/api/subscriptions/reactivate'),
};

export default api;
