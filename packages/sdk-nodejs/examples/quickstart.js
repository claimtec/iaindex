/**
 * IAIndex SDK Quickstart Example
 *
 * This example demonstrates the basic usage of the IAIndex SDK
 * for both publishers and AI clients.
 */

const { IAIndexPublisher, IAIndexClient, CryptoUtils } = require('../dist');

async function publisherExample() {
  console.log('\n=== Publisher Example ===\n');

  // Generate a key pair for the publisher
  const publisherKeyPair = CryptoUtils.generateKeyPair();
  console.log('Publisher Private Key:', publisherKeyPair.privateKey);
  console.log('Publisher Public Key:', publisherKeyPair.publicKey);

  // Create publisher instance
  const publisher = new IAIndexPublisher({
    domain: 'example.com',
    privateKey: publisherKeyPair.privateKey,
    name: 'Example Publication',
    contact: 'publisher@example.com'
  });

  try {
    // Initialize publisher
    console.log('\nInitializing publisher...');
    await publisher.initialize();
    console.log('Publisher initialized successfully');

    // Add a content entry
    console.log('\nAdding content entry...');
    const entryId = await publisher.addEntry({
      url: 'https://example.com/article-1',
      title: 'Getting Started with AI Content Tracking',
      author: 'Jane Doe',
      publishedDate: new Date().toISOString(),
      content: 'This is an example article about AI content tracking...',
      license: {
        type: 'CC-BY-4.0',
        terms: 'Attribution required'
      }
    });
    console.log('Entry added with ID:', entryId);

    // Add another entry
    await publisher.addEntry({
      url: 'https://example.com/article-2',
      title: 'Understanding Digital Rights',
      author: 'John Smith',
      publishedDate: new Date().toISOString(),
      license: { type: 'MIT' }
    });
    console.log('Second entry added');

    // Generate index
    console.log('\nGenerating index file...');
    const index = await publisher.generateIndex();
    console.log('Index generated with', index.entries.length, 'entries');
    console.log('Index signature:', index.signature.substring(0, 32) + '...');

  } catch (error) {
    console.error('Publisher error:', error.message);
  }
}

async function clientExample() {
  console.log('\n\n=== AI Client Example ===\n');

  // Generate a key pair for the client
  const clientKeyPair = CryptoUtils.generateKeyPair();
  console.log('Client Private Key:', clientKeyPair.privateKey);
  console.log('Client Public Key:', clientKeyPair.publicKey);

  // Create client instance
  const client = new IAIndexClient({
    clientId: 'my-ai-client-001',
    privateKey: clientKeyPair.privateKey,
    name: 'My AI Model',
    organization: 'AI Research Lab'
  });

  try {
    // Initialize client
    console.log('\nInitializing client...');
    await client.initialize();
    console.log('Client initialized successfully');

    // Access content
    console.log('\nAccessing content...');
    const contentUrl = 'https://example.com';
    const content = await client.accessContent(contentUrl);
    console.log('Content accessed:', content.url);
    if (content.title) {
      console.log('Content title:', content.title);
    }

    // Send usage receipt
    console.log('\nSending usage receipt...');
    const receiptSent = await client.sendReceipt(content, {
      purpose: 'training',
      context: 'pre-training dataset collection',
      datasetId: 'dataset-2024-01',
      modelId: 'my-model-v1.0'
    });
    console.log('Receipt sent:', receiptSent ? 'Success' : 'Failed');

    // Get verified publishers
    console.log('\nFetching verified publishers...');
    const publishers = await client.getVerifiedPublishers();
    console.log('Found', publishers.length, 'verified publishers');

  } catch (error) {
    console.error('Client error:', error.message);
  }
}

async function main() {
  console.log('IAIndex SDK Quickstart Example');
  console.log('===============================');

  // Run publisher example
  await publisherExample();

  // Run client example
  await clientExample();

  console.log('\n\nQuickstart complete!');
}

// Run the examples
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
