/**
 * Example usage of LangChain AIIndex Reader
 */

import { AIIndexReader, AIIndexReceiptSigner, AIIndexLoader } from '../src';

// Example 1: Basic document reading
async function basicReading() {
  console.log('=== Basic Reading ===\n');

  const reader = new AIIndexReader({
    validateSchema: true,
    timeout: 10000,
  });

  try {
    // Fetch ai-index.json from a domain
    const document = await reader.fetch('example.com');

    console.log('Publisher:', document.publisher?.name);
    console.log('Domain:', document.domain);
    console.log('Pages:', document.pages?.length || 0);
    console.log('Entities:', document.entities?.length || 0);
    console.log('FAQs:', document.faq?.length || 0);
  } catch (error) {
    console.error('Error:', error);
  }
}

// Example 2: Batch reading multiple sites
async function batchReading() {
  console.log('\n=== Batch Reading ===\n');

  const reader = new AIIndexReader();

  const urls = [
    'https://example.com/ai-index.json',
    'https://another-site.com/ai-index.json',
    'https://third-site.com/ai-index.json',
  ];

  const results = await reader.fetchBatch(urls);

  results.forEach((result) => {
    if (result.document) {
      console.log(`✓ ${result.url}: ${result.document.publisher?.name}`);
    } else {
      console.log(`✗ ${result.url}: ${result.error}`);
    }
  });
}

// Example 3: Create and sign receipts
async function receiptSigning() {
  console.log('\n=== Receipt Signing ===\n');

  // Generate a keypair (do this once and store securely)
  const { privateKey, publicKey } = await AIIndexReceiptSigner.generateKeyPair('ES256');
  console.log('Generated keypair');
  console.log('Public key:', publicKey.substring(0, 50) + '...');

  // Create signer
  const signer = new AIIndexReceiptSigner({
    clientId: 'my-langchain-app',
    clientName: 'My LangChain Application',
    clientVersion: '1.0.0',
    privateKeyPem: privateKey,
    keyId: 'key-001',
    algorithm: 'ES256',
  });

  await signer.initialize();

  // Fetch document
  const reader = new AIIndexReader();
  const document = await reader.fetch('example.com');

  // Create and post receipt
  const { receipt, posted } = await signer.createAndPostReceipt(document, {
    url: 'https://example.com/ai-index.json',
    statusCode: 200,
    pagesAccessed: ['https://example.com/about', 'https://example.com/contact'],
    purpose: {
      type: 'inference',
      description: 'RAG application for customer support',
      commercial: true,
    },
    attribution: {
      method: 'citation',
      citation_text: 'Information from Example.com',
      url: 'https://example.com',
    },
  });

  console.log('Receipt ID:', receipt.receipt_id);
  console.log('Posted to webhook:', posted);

  // Verify receipt
  const isValid = await AIIndexReceiptSigner.verifyReceipt(receipt, publicKey);
  console.log('Receipt valid:', isValid);
}

// Example 4: LangChain document loader
async function langchainLoader() {
  console.log('\n=== LangChain Document Loader ===\n');

  // Basic loading
  const loader = new AIIndexLoader('example.com', {
    validateSchema: true,
    includeMetadata: true,
    filterContentType: ['article', 'documentation'],
    maxPages: 10,
  });

  const documents = await loader.load();

  console.log(`Loaded ${documents.length} documents`);

  documents.forEach((doc, index) => {
    console.log(`\nDocument ${index + 1}:`);
    console.log('Type:', doc.metadata.type);
    console.log('Content preview:', doc.pageContent.substring(0, 100) + '...');
  });
}

// Example 5: LangChain loader with receipts
async function langchainLoaderWithReceipts() {
  console.log('\n=== LangChain Loader with Receipts ===\n');

  // Generate keypair
  const { privateKey, publicKey } = await AIIndexReceiptSigner.generateKeyPair('ES256');

  const loader = new AIIndexLoader('example.com', {
    validateSchema: true,
    autoSendReceipt: true,
    clientId: 'my-rag-app',
    clientName: 'My RAG Application',
    clientVersion: '1.0.0',
    privateKeyPem: privateKey,
    keyId: 'key-001',
    algorithm: 'ES256',
    includeMetadata: true,
  });

  // This will automatically create and send a receipt
  const documents = await loader.load();

  console.log(`Loaded ${documents.length} documents with automatic receipt`);
}

// Example 6: Load by document type
async function loadByType() {
  console.log('\n=== Load By Type ===\n');

  const loader = new AIIndexLoader('example.com');

  const { publisher, entities, pages, faqs } = await loader.loadByType();

  console.log('Publisher document:', publisher ? '✓' : '✗');
  console.log('Entity documents:', entities.length);
  console.log('Page documents:', pages.length);
  console.log('FAQ documents:', faqs.length);

  // Use specific document types
  if (faqs.length > 0) {
    console.log('\nFirst FAQ:');
    console.log(faqs[0].pageContent);
  }
}

// Example 7: Batch loading multiple sites
async function batchLoading() {
  console.log('\n=== Batch Loading ===\n');

  const urls = [
    'https://example.com/ai-index.json',
    'https://another-site.com/ai-index.json',
  ];

  const documents = await AIIndexLoader.loadBatch(urls, {
    validateSchema: true,
    includeMetadata: true,
    maxPages: 5,
  });

  console.log(`Loaded ${documents.length} documents from ${urls.length} sites`);

  // Group by source
  const bySite = documents.reduce((acc, doc) => {
    const source = doc.metadata.ai_index_source || doc.metadata.source;
    if (!acc[source]) acc[source] = [];
    acc[source].push(doc);
    return acc;
  }, {} as Record<string, any[]>);

  Object.entries(bySite).forEach(([site, docs]) => {
    console.log(`${site}: ${docs.length} documents`);
  });
}

// Example 8: Integration with LangChain chains
async function langchainIntegration() {
  console.log('\n=== LangChain Integration ===\n');

  // Load documents
  const loader = new AIIndexLoader('example.com', {
    includeMetadata: true,
    filterContentType: ['article', 'documentation'],
  });

  const documents = await loader.load();

  console.log(`Loaded ${documents.length} documents`);

  // These documents can now be used with:
  // - Vector stores (e.g., Chroma, Pinecone, Weaviate)
  // - Text splitters
  // - Embeddings
  // - RAG chains
  // - QA chains

  console.log('\nReady for use with:');
  console.log('- Vector stores (Chroma, Pinecone, etc.)');
  console.log('- Text splitters');
  console.log('- Embeddings');
  console.log('- RAG chains');
}

// Run all examples
async function main() {
  console.log('AIIndex LangChain Reader Examples\n');
  console.log('===================================\n');

  // Uncomment to run specific examples:

  // await basicReading();
  // await batchReading();
  // await receiptSigning();
  // await langchainLoader();
  // await langchainLoaderWithReceipts();
  // await loadByType();
  // await batchLoading();
  // await langchainIntegration();

  console.log('\nNote: Uncomment examples in main() to run them.');
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export {
  basicReading,
  batchReading,
  receiptSigning,
  langchainLoader,
  langchainLoaderWithReceipts,
  loadByType,
  batchLoading,
  langchainIntegration,
};
