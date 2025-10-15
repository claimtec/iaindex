/**
 * AIIndex SDK - Official Node.js SDK for AIIndex
 *
 * @packageDocumentation
 */

export { AIIndexGenerator } from './generator';
export { SignatureManager } from './signer';
export { ReceiptHandler } from './receipts';
export { Validator } from './validator';

export type {
  AIIndexConfig,
  AIIndexFile,
  CrawlOptions,
  GeneratorOptions,
  ValidationResult,
  ValidationError,
  ValidationWarning,
  SignatureOptions,
  KeyPair,
  Receipt,
  ReceiptHandlerOptions,
  WebhookServerOptions,
  CLIConfig,
} from './types';

// Version
export const VERSION = '1.0.0';

// Default exports for convenience
import { AIIndexGenerator } from './generator';
import { SignatureManager } from './signer';
import { ReceiptHandler } from './receipts';
import { Validator } from './validator';

export default {
  AIIndexGenerator,
  SignatureManager,
  ReceiptHandler,
  Validator,
  VERSION,
};
