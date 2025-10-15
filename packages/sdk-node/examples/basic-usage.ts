/**
 * Basic usage example for @aiindex/sdk
 */

import {
  AIIndexGenerator,
  SignatureManager,
  Validator,
  ReceiptHandler,
} from '../src/index';
import * as fs from 'fs/promises';

async function main() {
  console.log('AIIndex SDK - Basic Usage Example\n');

  // 1. Generate AI Index from website
  console.log('1. Generating AI Index...');
  const generator = new AIIndexGenerator({
    baseUrl: 'https://example.com',
    config: {
      name: 'Example AI Service',
      description: 'An example AI service demonstrating AIIndex',
      capabilities: ['natural-language-processing', 'text-generation'],
      categories: ['ai', 'productivity'],
    },
    crawlOptions: {
      maxPages: 10,
      maxDepth: 2,
    },
  });

  const aiIndex = await generator.generate();
  console.log('Generated:', aiIndex.name);

  // 2. Validate the generated file
  console.log('\n2. Validating AI Index...');
  const validator = new Validator();
  const validationResult = validator.validate(aiIndex);

  if (validationResult.valid) {
    console.log('Validation: PASSED');
  } else {
    console.log('Validation: FAILED');
    console.log('Errors:', validationResult.errors);
    return;
  }

  // 3. Generate keys and sign
  console.log('\n3. Signing AI Index...');
  const signer = new SignatureManager();
  const keyPair = await signer.generateKeyPair({ keyFormat: 'jwk' });

  // Save keys
  await fs.mkdir('./keys', { recursive: true });
  await fs.writeFile('./keys/private-key.json', keyPair.privateKey);
  await fs.writeFile('./keys/public-key.json', keyPair.publicKey);
  console.log('Keys saved to ./keys/');

  // Sign the file
  const signedAiIndex = await signer.signFile(aiIndex);
  console.log('File signed successfully');

  // 4. Save to file
  console.log('\n4. Saving to file...');
  await fs.writeFile(
    './ai-index.json',
    JSON.stringify(signedAiIndex, null, 2)
  );
  console.log('Saved to ./ai-index.json');

  // 5. Verify signature
  console.log('\n5. Verifying signature...');
  const isValid = await signer.verifyFile(signedAiIndex);
  console.log('Signature valid:', isValid);

  // 6. Create and handle receipts
  console.log('\n6. Receipt handling example...');
  const receipt = ReceiptHandler.createReceipt(
    'agent-123',
    'view',
    { page: 'homepage', source: 'direct' }
  );
  console.log('Receipt created:', receipt.id);

  // Start webhook server (optional - commented out for example)
  /*
  const handler = new ReceiptHandler({
    apiEndpoint: 'https://api.aiindex.com',
    autoForward: true,
  });

  await handler.startWebhookServer({
    port: 3000,
    path: '/webhook/receipts',
    onReceipt: async (receipt) => {
      console.log('Receipt received:', receipt);
    },
  });
  console.log('Webhook server started on port 3000');
  */

  console.log('\nExample completed successfully!');
}

main().catch(console.error);
