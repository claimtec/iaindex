/**
 * Core types for AIIndex SDK
 */

export interface AIIndexConfig {
  version: string;
  name: string;
  description: string;
  url: string;
  capabilities?: string[];
  categories?: string[];
  contact?: {
    email?: string;
    url?: string;
  };
  apiEndpoint?: string;
  authentication?: {
    type: 'none' | 'api-key' | 'oauth2';
    details?: Record<string, any>;
  };
  pricing?: {
    model: 'free' | 'subscription' | 'pay-per-use';
    details?: string;
  };
  metadata?: Record<string, any>;
}

export interface AIIndexFile extends AIIndexConfig {
  generated: string;
  signature?: string;
  signedBy?: {
    publicKey: string;
    algorithm: string;
  };
}

export interface CrawlOptions {
  maxPages?: number;
  maxDepth?: number;
  includePatterns?: string[];
  excludePatterns?: string[];
  followExternalLinks?: boolean;
  timeout?: number;
  userAgent?: string;
}

export interface GeneratorOptions {
  baseUrl: string;
  config?: Partial<AIIndexConfig>;
  crawlOptions?: CrawlOptions;
}

export interface ValidationResult {
  valid: boolean;
  errors?: ValidationError[];
  warnings?: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
}

export interface SignatureOptions {
  algorithm?: 'ES256' | 'ES384' | 'ES512';
  keyFormat?: 'jwk' | 'pem';
}

export interface KeyPair {
  publicKey: string;
  privateKey: string;
  algorithm: string;
}

export interface Receipt {
  id: string;
  agentId: string;
  timestamp: string;
  action: 'view' | 'click' | 'interaction';
  metadata?: Record<string, any>;
}

export interface ReceiptHandlerOptions {
  apiEndpoint: string;
  apiKey?: string;
  autoForward?: boolean;
  retryAttempts?: number;
  retryDelay?: number;
}

export interface WebhookServerOptions {
  port?: number;
  path?: string;
  apiKey?: string;
  onReceipt?: (receipt: Receipt) => void | Promise<void>;
}

export interface CLIConfig {
  version?: string;
  name?: string;
  description?: string;
  url?: string;
  capabilities?: string[];
  categories?: string[];
  outputPath?: string;
  privateKeyPath?: string;
  publicKeyPath?: string;
  apiEndpoint?: string;
  webhookPort?: number;
  webhookPath?: string;
}
