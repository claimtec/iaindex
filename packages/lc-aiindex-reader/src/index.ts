/**
 * LangChain AIIndex Reader
 *
 * Document loader for AI-readable website metadata (ai-index.json)
 * Includes receipt generation and cryptographic verification
 */

export { AIIndexReader } from './reader';
export { AIIndexReceiptSigner } from './signer';
export { AIIndexLoader } from './loader';
export { PolicyEnforcer, parseDomain } from './policy';
export { RenderFallbackAdapter } from './renderer';

export type {
  AIIndexDocument,
  Publisher,
  Entity,
  Page,
  FAQ,
  AccessPolicy,
  Signature,
  Verification,
  Receipt,
  Access,
  Purpose,
  Attribution,
  ReceiptMetadata,
  AIIndexReaderOptions,
  AIIndexLoaderOptions,
  ValidationResult,
  ReceiptSignerOptions,
  // v1.1 Policy Types
  PolicyAction,
  PolicyRule,
  ReceiptPolicy,
  RenderFallback,
  AIIndexPolicy,
  DenialReceipt,
  RenderResponse,
  PolicyEnforcementOptions,
} from './types';

export { PolicyViolationError, RateLimitError } from './types';
