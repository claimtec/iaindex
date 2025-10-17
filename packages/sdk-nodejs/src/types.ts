/**
 * Type definitions for IAIndex SDK
 */

export interface PublisherOptions {
  domain: string;
  privateKey: string;
  name: string;
  contact: string;
  apiBaseUrl?: string;
}

export interface ClientOptions {
  clientId: string;
  privateKey: string;
  name?: string;
  organization?: string;
  apiBaseUrl?: string;
}

export interface ContentEntry {
  url: string;
  title: string;
  author: string;
  publishedDate: string;
  content?: string;
  license: {
    type: string;
    terms?: string;
  };
  metadata?: Record<string, any>;
}

export interface UsageInfo {
  purpose: 'training' | 'inference' | 'research';
  context: string;
  datasetId?: string;
  modelId?: string;
}

export interface ContentMetadata {
  url: string;
  title?: string;
  author?: string;
  publishedDate?: string;
  license?: {
    type: string;
    terms?: string;
  };
  publisher?: {
    domain: string;
    name: string;
  };
}

export interface Receipt {
  receiptId: string;
  publisherDomain: string;
  articleUrl: string;
  timestamp: string;
  signature: string;
  metadata?: Record<string, any>;
}

export interface IndexFile {
  domain: string;
  publisher: {
    name: string;
    contact: string;
  };
  entries: ContentEntry[];
  signature: string;
  timestamp: string;
  version: string;
}

export interface KeyPair {
  privateKey: string;
  publicKey: string;
}

export interface AuthToken {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
}
