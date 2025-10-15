/**
 * AIIndex v1.1 Policy Discovery and Enforcement
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  AIIndexPolicy,
  AIIndexDocument,
  PolicyRule,
  PolicyAction,
  PolicyViolationError,
  RateLimitError,
  DenialReceipt,
} from './types';

export class PolicyEnforcer {
  private client: AxiosInstance;
  private policyCache: Map<string, { policy: AIIndexPolicy; expiresAt: number }> = new Map();
  private lastRequestTime: Map<string, number> = new Map();
  private requestCounts: Map<string, { minute: number; hour: number; minuteStart: number; hourStart: number }> = new Map();

  constructor(timeout: number = 10000) {
    this.client = axios.create({
      timeout,
      headers: {
        'Accept': 'application/json',
        'X-AIIndex-Version': 'v1.1',
      },
    });
  }

  /**
   * Fetch policy with fallback mechanism
   * 1. Try /.well-known/aiindex-policy.json first
   * 2. Fall back to ai-index.json policy block
   */
  async fetchPolicy(domain: string, aiIndexDoc?: AIIndexDocument): Promise<AIIndexPolicy | null> {
    // Check cache first
    const cached = this.policyCache.get(domain);
    if (cached && cached.expiresAt > Date.now()) {
      return cached.policy;
    }

    // Try well-known endpoint first
    try {
      const wellKnownUrl = `https://${domain}/.well-known/aiindex-policy.json`;
      const response = await this.client.get<AIIndexPolicy>(wellKnownUrl);

      if (response.status === 200 && response.data) {
        this.cachePolicy(domain, response.data);
        return response.data;
      }
    } catch (error) {
      // Well-known endpoint not found, fall back to ai-index.json
    }

    // Fall back to policy embedded in ai-index.json
    if (aiIndexDoc && (aiIndexDoc as any).policy) {
      const embeddedPolicy: AIIndexPolicy = {
        version: '1.1',
        domain,
        policy: (aiIndexDoc as any).policy,
        receipts: (aiIndexDoc as any).receipts,
        render_fallback: (aiIndexDoc as any).render_fallback,
        updated_at: aiIndexDoc.last_updated,
      };
      this.cachePolicy(domain, embeddedPolicy);
      return embeddedPolicy;
    }

    return null;
  }

  /**
   * Evaluate policy for a specific intent
   * @throws PolicyViolationError if access is blocked
   */
  async evaluatePolicy(
    domain: string,
    intent: 'training' | 'retrieval',
    aiIndexDoc?: AIIndexDocument
  ): Promise<{ allowed: boolean; requiresAttribution: boolean; policy: AIIndexPolicy | null }> {
    const policy = await this.fetchPolicy(domain, aiIndexDoc);

    if (!policy) {
      // No policy found, default to allow
      return { allowed: true, requiresAttribution: false, policy: null };
    }

    const action = intent === 'training' ? policy.policy.training : policy.policy.retrieval;

    switch (action) {
      case 'block':
        const denialReceipt: DenialReceipt = {
          denied: true,
          reason: `${intent} is blocked by publisher policy`,
          policy_url: `https://${domain}/.well-known/aiindex-policy.json`,
        };
        throw new (PolicyViolationError as any)(
          `Access denied: ${intent} is blocked for ${domain}`,
          'block',
          intent,
          denialReceipt
        );

      case 'require-attribution':
        return { allowed: true, requiresAttribution: true, policy };

      case 'allow':
      default:
        return { allowed: true, requiresAttribution: false, policy };
    }
  }

  /**
   * Apply rate limiting based on policy
   * @throws RateLimitError if rate limit exceeded
   */
  async applyRateLimit(domain: string, policy: AIIndexPolicy | null): Promise<void> {
    if (!policy?.policy.rate_limit) {
      return;
    }

    const rateLimit = policy.policy.rate_limit;
    const now = Date.now();

    // Check delay between requests
    if (rateLimit.delay_ms) {
      const lastRequest = this.lastRequestTime.get(domain) || 0;
      const timeSinceLastRequest = now - lastRequest;

      if (timeSinceLastRequest < rateLimit.delay_ms) {
        const waitTime = rateLimit.delay_ms - timeSinceLastRequest;
        await this.delay(waitTime);
      }

      this.lastRequestTime.set(domain, Date.now());
    }

    // Check rate limits
    let counts = this.requestCounts.get(domain);
    if (!counts) {
      counts = {
        minute: 0,
        hour: 0,
        minuteStart: now,
        hourStart: now,
      };
      this.requestCounts.set(domain, counts);
    }

    // Reset counters if time windows have passed
    if (now - counts.minuteStart >= 60000) {
      counts.minute = 0;
      counts.minuteStart = now;
    }
    if (now - counts.hourStart >= 3600000) {
      counts.hour = 0;
      counts.hourStart = now;
    }

    // Check limits
    if (rateLimit.requests_per_minute && counts.minute >= rateLimit.requests_per_minute) {
      const retryAfter = 60 - Math.floor((now - counts.minuteStart) / 1000);
      throw new (RateLimitError as any)(
        `Rate limit exceeded: ${rateLimit.requests_per_minute} requests per minute`,
        retryAfter
      );
    }

    if (rateLimit.requests_per_hour && counts.hour >= rateLimit.requests_per_hour) {
      const retryAfter = 3600 - Math.floor((now - counts.hourStart) / 1000);
      throw new (RateLimitError as any)(
        `Rate limit exceeded: ${rateLimit.requests_per_hour} requests per hour`,
        retryAfter
      );
    }

    // Increment counters
    counts.minute++;
    counts.hour++;
  }

  /**
   * Parse denial receipt from 403 response
   */
  parseDenialReceipt(error: AxiosError): DenialReceipt | null {
    if (error.response?.status === 403) {
      const data = error.response.data as any;
      if (data && typeof data === 'object') {
        return {
          denied: data.denied || true,
          reason: data.reason || 'Access denied',
          policy_url: data.policy_url,
          retry_after: data.retry_after,
          alternative_endpoint: data.alternative_endpoint,
        };
      }
    }
    return null;
  }

  /**
   * Check if receipts are required
   */
  requiresSignedReceipt(policy: AIIndexPolicy | null): boolean {
    return policy?.receipts?.require_signed === true;
  }

  /**
   * Get webhook URL from policy
   */
  getWebhookUrl(policy: AIIndexPolicy | null): string | undefined {
    return policy?.receipts?.webhook_url;
  }

  /**
   * Cache policy with 1 hour TTL
   */
  private cachePolicy(domain: string, policy: AIIndexPolicy): void {
    const expiresAt = Date.now() + 3600000; // 1 hour
    this.policyCache.set(domain, { policy, expiresAt });
  }

  /**
   * Delay helper
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Clear cache for a domain
   */
  clearCache(domain?: string): void {
    if (domain) {
      this.policyCache.delete(domain);
      this.lastRequestTime.delete(domain);
      this.requestCounts.delete(domain);
    } else {
      this.policyCache.clear();
      this.lastRequestTime.clear();
      this.requestCounts.clear();
    }
  }
}

/**
 * Parse domain from URL
 */
export function parseDomain(url: string): string {
  try {
    const urlObj = new URL(url.startsWith('http') ? url : `https://${url}`);
    return urlObj.hostname;
  } catch {
    return url.replace(/^https?:\/\//, '').split('/')[0];
  }
}
