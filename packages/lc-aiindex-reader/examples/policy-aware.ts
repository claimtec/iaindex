/**
 * AIIndex v1.1 Policy-Aware Usage Example
 *
 * Demonstrates:
 * - Policy discovery and enforcement
 * - Handling 403 Forbidden responses
 * - Parsing denial receipts
 * - Retrying with different intents
 * - Respecting rate limits
 * - Automatic receipt signing
 * - Render fallback support
 */

import {
  AIIndexReader,
  AIIndexReceiptSigner,
  AIIndexLoader,
  PolicyEnforcer,
  RenderFallbackAdapter,
  PolicyViolationError,
  RateLimitError,
} from '../src/index';

async function policyAwareExample() {
  console.log('=== AIIndex v1.1 Policy-Aware Example ===\n');

  // Example 1: Basic policy-aware reader
  console.log('1. Basic Policy-Aware Reader');
  try {
    const reader = new AIIndexReader({
      clientId: 'my-app-v1',
      clientName: 'My AI Application',
      clientVersion: '1.0.0',
      intent: 'retrieval', // Specify intent upfront
      respectPolicyBlocks: true, // Enforce policy blocks
      enableRenderFallback: true, // Enable render fallback
      timeout: 10000,
    });

    const document = await reader.fetch('example.com');
    console.log(`✓ Successfully fetched document for ${document.domain}`);
    console.log(`  Publisher: ${document.publisher?.name}`);
    console.log(`  Pages: ${document.pages?.length || 0}`);
  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);
  }

  console.log('\n');

  // Example 2: Handling Policy Violations
  console.log('2. Handling Policy Violations (403 Forbidden)');
  try {
    const reader = new AIIndexReader({
      clientId: 'training-bot',
      intent: 'training', // Training intent
      respectPolicyBlocks: true,
    });

    await reader.fetch('restricted-site.com');
  } catch (error: any) {
    if (error instanceof PolicyViolationError) {
      console.log(`✗ Policy Violation: ${error.message}`);
      console.log(`  Action: ${error.action}`);
      console.log(`  Intent: ${error.intent}`);
      if (error.denialReceipt) {
        console.log(`  Reason: ${error.denialReceipt.reason}`);
        console.log(`  Policy URL: ${error.denialReceipt.policy_url}`);
        if (error.denialReceipt.retry_after) {
          console.log(`  Retry After: ${error.denialReceipt.retry_after}s`);
        }
        if (error.denialReceipt.alternative_endpoint) {
          console.log(`  Alternative: ${error.denialReceipt.alternative_endpoint}`);
        }
      }
    } else {
      console.error(`✗ Error: ${error.message}`);
    }
  }

  console.log('\n');

  // Example 3: Retry with Different Intent
  console.log('3. Retry with Different Intent');
  const testDomain = 'flexible-policy-site.com';

  // First try with training
  try {
    const reader = new AIIndexReader({
      clientId: 'smart-bot',
      intent: 'training',
      respectPolicyBlocks: true,
    });

    console.log('Attempting with "training" intent...');
    await reader.fetch(testDomain);
    console.log('✓ Training access allowed');
  } catch (error: any) {
    if (error instanceof PolicyViolationError) {
      console.log(`✗ Training blocked: ${error.message}`);
      console.log('  Retrying with "retrieval" intent...');

      // Retry with retrieval
      try {
        const reader2 = new AIIndexReader({
          clientId: 'smart-bot',
          intent: 'retrieval',
          respectPolicyBlocks: true,
        });

        await reader2.fetch(testDomain);
        console.log('✓ Retrieval access allowed');
      } catch (retryError: any) {
        console.error(`✗ Retrieval also blocked: ${retryError.message}`);
      }
    }
  }

  console.log('\n');

  // Example 4: Rate Limiting
  console.log('4. Rate Limiting Example');
  try {
    const reader = new AIIndexReader({
      clientId: 'rate-limited-bot',
      respectPolicyBlocks: true,
    });

    console.log('Making multiple requests...');
    for (let i = 1; i <= 5; i++) {
      try {
        await reader.fetch('rate-limited-site.com');
        console.log(`✓ Request ${i} succeeded`);
      } catch (error: any) {
        if (error instanceof RateLimitError) {
          console.log(`⏱ Rate limited on request ${i}`);
          console.log(`  Message: ${error.message}`);
          console.log(`  Retry after: ${error.retryAfter}s`);
          console.log(`  Waiting...`);
          await new Promise((resolve) => setTimeout(resolve, error.retryAfter * 1000));
          console.log(`  Retrying...`);
          await reader.fetch('rate-limited-site.com');
          console.log(`✓ Retry succeeded`);
        } else {
          throw error;
        }
      }
    }
  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);
  }

  console.log('\n');

  // Example 5: Automatic Receipt Signing
  console.log('5. Automatic Receipt Signing');
  try {
    // Generate a keypair (in production, load from secure storage)
    const { privateKey, publicKey } = await AIIndexReceiptSigner.generateKeyPair('ES256');
    console.log('✓ Generated keypair');

    const reader = new AIIndexReader({
      clientId: 'receipt-bot',
      clientName: 'Receipt-Enabled Bot',
      clientVersion: '2.0.0',
      intent: 'retrieval',
      autoSendReceipt: true, // Enable auto-receipt
      privateKeyPem: privateKey,
      keyId: 'key-001',
      algorithm: 'ES256',
    });

    const document = await reader.fetch('receipt-required-site.com');
    console.log(`✓ Fetched document and auto-signed receipt`);
    console.log(`  Document: ${document.domain}`);

    // Manually create and post a receipt
    const signer = new AIIndexReceiptSigner({
      clientId: 'receipt-bot',
      privateKeyPem: privateKey,
      keyId: 'key-001',
      intent: 'retrieval',
    });

    await signer.initialize();

    const { receipt, posted } = await signer.createAndPostReceipt(document, {
      url: 'https://receipt-required-site.com/ai-index.json',
      intent: 'retrieval',
      purpose: {
        type: 'retrieval',
        description: 'Loading content for RAG application',
        commercial: false,
      },
      attribution: {
        method: 'citation',
        citation_text: `Data from ${document.domain}`,
      },
    });

    console.log(`✓ Created receipt: ${receipt.receipt_id}`);
    console.log(`  Posted to webhook: ${posted}`);
    console.log(`  Signature algorithm: ${receipt.signature.algorithm}`);
  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);
  }

  console.log('\n');

  // Example 6: Render Fallback
  console.log('6. Render Fallback Support');
  try {
    const reader = new AIIndexReader({
      clientId: 'fallback-bot',
      enableRenderFallback: true,
      intent: 'retrieval',
    });

    // Try to fetch from a site without ai-index.json
    const document = await reader.fetch('no-aiindex-site.com');

    if (document.metadata?.source === 'render-fallback') {
      console.log('✓ Used render fallback');
      console.log(`  Domain: ${document.domain}`);
      console.log(`  Content length: ${document.pages?.[0]?.summary?.length || 0} chars`);
      console.log(`  Rendered at: ${document.metadata.rendered_at}`);
    } else {
      console.log('✓ Fetched from ai-index.json');
    }
  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);
  }

  console.log('\n');

  // Example 7: Direct Policy Enforcement
  console.log('7. Direct Policy Enforcement');
  try {
    const enforcer = new PolicyEnforcer(10000);

    // Fetch policy
    const policy = await enforcer.fetchPolicy('example.com');

    if (policy) {
      console.log('✓ Fetched policy');
      console.log(`  Version: ${policy.version}`);
      console.log(`  Training: ${policy.policy.training || 'not specified'}`);
      console.log(`  Retrieval: ${policy.policy.retrieval || 'not specified'}`);
      console.log(`  Require signed receipts: ${policy.receipts?.require_signed || false}`);

      // Evaluate for specific intent
      const evaluation = await enforcer.evaluatePolicy('example.com', 'training');
      console.log(`  Training allowed: ${evaluation.allowed}`);
      console.log(`  Requires attribution: ${evaluation.requiresAttribution}`);

      // Check rate limits
      if (policy.policy.rate_limit) {
        console.log('  Rate limits:');
        if (policy.policy.rate_limit.requests_per_minute) {
          console.log(`    - ${policy.policy.rate_limit.requests_per_minute} req/min`);
        }
        if (policy.policy.rate_limit.delay_ms) {
          console.log(`    - ${policy.policy.rate_limit.delay_ms}ms delay between requests`);
        }
      }
    } else {
      console.log('  No policy found (default allow)');
    }
  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);
  }

  console.log('\n');

  // Example 8: LangChain Loader with Policy Awareness
  console.log('8. LangChain Loader with Policy Awareness');
  try {
    const loader = new AIIndexLoader('https://example.com/ai-index.json', {
      clientId: 'langchain-app',
      clientName: 'My LangChain App',
      intent: 'retrieval',
      respectPolicyBlocks: true,
      enableRenderFallback: true,
      autoSendReceipt: false, // Don't auto-send for this example
      includeMetadata: true,
      maxPages: 10,
    });

    const documents = await loader.load();
    console.log(`✓ Loaded ${documents.length} LangChain documents`);

    // Filter by type
    const { publisher, entities, pages, faqs } = await loader.loadByType();
    console.log(`  Publisher docs: ${publisher ? 1 : 0}`);
    console.log(`  Entity docs: ${entities.length}`);
    console.log(`  Page docs: ${pages.length}`);
    console.log(`  FAQ docs: ${faqs.length}`);
  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);
  }

  console.log('\n=== Example Complete ===');
}

// Run the example
if (require.main === module) {
  policyAwareExample().catch(console.error);
}

export default policyAwareExample;
