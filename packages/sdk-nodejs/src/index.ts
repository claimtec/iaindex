/**
 * IAIndex SDK for Node.js
 * Official SDK for tracking and verifying AI content usage
 */

export { IAIndexPublisher } from './publisher';
export { IAIndexClient } from './client';
export { CryptoUtils } from './crypto';

export * from './types';

// Re-export commonly used types
export type {
  PublisherOptions,
  ClientOptions,
  ContentEntry,
  ContentMetadata,
  UsageInfo,
  Receipt,
  IndexFile,
  KeyPair,
  AuthToken,
} from './types';
