/**
 * Type definitions for AIIndex LangChain connector
 */

export interface AIIndexDocument {
  version: string;
  publisher_id: string;
  domain: string;
  last_updated: string;
  publisher?: Publisher;
  entities?: Entity[];
  pages?: Page[];
  faq?: FAQ[];
  access_policy?: AccessPolicy;
  signature?: Signature;
  verification?: Verification;
  metadata?: Record<string, any>;
}

export interface Publisher {
  name?: string;
  description?: string;
  url?: string;
  contact?: {
    email?: string;
    url?: string;
  };
  logo?: string;
}

export interface Entity {
  type: 'Person' | 'Organization' | 'Product' | 'Service' | 'Event' | 'Place';
  name: string;
  description?: string;
  url?: string;
  image?: string;
  properties?: Record<string, any>;
}

export interface Page {
  url: string;
  title: string;
  description?: string;
  content_type?: 'article' | 'page' | 'product' | 'documentation' | 'faq' | 'about';
  published?: string;
  modified?: string;
  author?: string;
  tags?: string[];
  summary?: string;
}

export interface FAQ {
  question: string;
  answer: string;
  category?: string;
}

export interface AccessPolicy {
  allowed: boolean;
  attribution_required: boolean;
  commercial_use: boolean;
  receipt_required: boolean;
  webhook_url?: string;
}

// AIIndex v1.1 Policy Types
export type PolicyAction = 'allow' | 'block' | 'require-attribution';

export interface PolicyRule {
  training?: PolicyAction;
  retrieval?: PolicyAction;
  rate_limit?: {
    requests_per_minute?: number;
    requests_per_hour?: number;
    delay_ms?: number;
  };
}

export interface ReceiptPolicy {
  require_signed?: boolean;
  webhook_url?: string;
  required_fields?: string[];
}

export interface RenderFallback {
  enabled?: boolean;
  mode?: 'snapshot' | 'live' | 'none';
  endpoint?: string;
}

export interface AIIndexPolicy {
  version: string;
  domain: string;
  policy: PolicyRule;
  receipts?: ReceiptPolicy;
  render_fallback?: RenderFallback;
  updated_at?: string;
}

export interface DenialReceipt {
  denied: boolean;
  reason: string;
  policy_url?: string;
  retry_after?: number;
  alternative_endpoint?: string;
}

export interface RenderResponse {
  url: string;
  rendered_text?: string;
  rendered_html?: string;
  metadata?: {
    rendered_at: string;
    cache_ttl?: number;
    [key: string]: any;
  };
}

export interface Signature {
  algorithm: 'ES256' | 'RS256';
  kid: string;
  signature: string;
  document_hash: string;
  signed_at?: string;
}

export interface Verification {
  verified?: boolean;
  verified_at?: string;
  verification_url?: string;
}

export interface Receipt {
  version: string;
  receipt_id: string;
  publisher_id: string;
  publisher_domain?: string;
  client_id: string;
  client_name?: string;
  client_version?: string;
  timestamp: string;
  access?: Access;
  purpose?: Purpose;
  attribution?: Attribution;
  signature: Signature;
  metadata?: ReceiptMetadata;
}

export interface Access {
  url?: string;
  method: 'GET' | 'POST';
  status_code?: number;
  content_hash?: string;
  pages_accessed?: string[];
}

export interface Purpose {
  type?: 'training' | 'retrieval' | 'inference' | 'research' | 'indexing' | 'other';
  description?: string;
  commercial?: boolean;
}

export interface Attribution {
  method?: 'citation' | 'link' | 'inline' | 'none';
  citation_text?: string;
  url?: string;
}

export interface ReceiptMetadata {
  user_agent?: string;
  sdk_version?: string;
  request_id?: string;
}

export interface AIIndexReaderOptions {
  timeout?: number;
  validateSchema?: boolean;
  autoSendReceipt?: boolean;
  clientId?: string;
  clientName?: string;
  clientVersion?: string;
  privateKeyPem?: string;
  keyId?: string;
  algorithm?: 'ES256' | 'RS256';
  intent?: 'training' | 'retrieval';
  respectPolicyBlocks?: boolean;
  enableRenderFallback?: boolean;
}

export interface PolicyEnforcementOptions {
  intent: 'training' | 'retrieval';
  respectBlocks?: boolean;
  respectRateLimits?: boolean;
}

export interface AIIndexLoaderOptions extends AIIndexReaderOptions {
  chunkSize?: number;
  includeMetadata?: boolean;
  filterContentType?: string[];
  maxPages?: number;
}

export interface ValidationResult {
  valid: boolean;
  errors?: Array<{
    field: string;
    message: string;
  }>;
}

export interface ReceiptSignerOptions {
  clientId: string;
  clientName?: string;
  clientVersion?: string;
  privateKeyPem: string;
  keyId: string;
  algorithm?: 'ES256' | 'RS256';
  webhookRetries?: number;
  webhookTimeout?: number;
  intent?: 'training' | 'retrieval';
}

// Custom Error Types
export class PolicyViolationError extends Error {
  constructor(
    message: string,
    public action: PolicyAction,
    public intent: string,
    public denialReceipt?: DenialReceipt
  ) {
    super(message);
    this.name = 'PolicyViolationError';
  }
}

export class RateLimitError extends Error {
  constructor(
    message: string,
    public retryAfter: number
  ) {
    super(message);
    this.name = 'RateLimitError';
  }
}
