# @aiindex/lc-aiindex-reader

LangChain document loader for AIIndex - Read and process AI-readable website metadata with automatic receipt generation and cryptographic verification.

## Features

- Fetch and parse `ai-index.json` files from websites
- Automatic JSON schema validation
- Convert to LangChain Document format
- Receipt generation with ES256/RS256 signatures
- Auto-send receipts to publisher webhooks
- Batch document loading
- Comprehensive metadata extraction
- Network error handling with retries
- TypeScript support

## Installation

```bash
npm install @aiindex/lc-aiindex-reader langchain @langchain/core
```

## Quick Start

### Basic Document Loading

```typescript
import { AIIndexLoader } from '@aiindex/lc-aiindex-reader';

// Load documents from a website
const loader = new AIIndexLoader('example.com', {
  validateSchema: true,
  includeMetadata: true,
});

const documents = await loader.load();

console.log(`Loaded ${documents.length} documents`);
```

### With Automatic Receipts

```typescript
import { AIIndexLoader, AIIndexReceiptSigner } from '@aiindex/lc-aiindex-reader';

// Generate keypair (do once, store securely)
const { privateKey, publicKey } = await AIIndexReceiptSigner.generateKeyPair('ES256');

// Load with automatic receipt generation
const loader = new AIIndexLoader('example.com', {
  autoSendReceipt: true,
  clientId: 'my-app',
  clientName: 'My RAG Application',
  privateKeyPem: privateKey,
  keyId: 'key-001',
  algorithm: 'ES256',
});

const documents = await loader.load();
```

## Core Classes

### AIIndexReader

Fetch and parse `ai-index.json` files with validation.

```typescript
import { AIIndexReader } from '@aiindex/lc-aiindex-reader';

const reader = new AIIndexReader({
  timeout: 10000,
  validateSchema: true,
});

// Fetch single document
const document = await reader.fetch('example.com');

// Batch fetch
const results = await reader.fetchBatch([
  'https://site1.com/ai-index.json',
  'https://site2.com/ai-index.json',
]);

// Probe for availability
const exists = await reader.probe('example.com');

// Extract specific data
const pageUrls = reader.extractPageUrls(document);
const people = reader.extractEntitiesByType(document, 'Person');
const faqs = reader.getFaqByCategory(document, 'pricing');
```

### AIIndexReceiptSigner

Create and sign cryptographic receipts for AI access tracking.

```typescript
import { AIIndexReceiptSigner } from '@aiindex/lc-aiindex-reader';

// Generate keypair
const { privateKey, publicKey } = await AIIndexReceiptSigner.generateKeyPair('ES256');

// Create signer
const signer = new AIIndexReceiptSigner({
  clientId: 'my-app',
  clientName: 'My Application',
  clientVersion: '1.0.0',
  privateKeyPem: privateKey,
  keyId: 'key-001',
  algorithm: 'ES256',
  webhookRetries: 3,
  webhookTimeout: 10000,
});

await signer.initialize();

// Create and post receipt
const { receipt, posted } = await signer.createAndPostReceipt(document, {
  url: 'https://example.com/ai-index.json',
  statusCode: 200,
  pagesAccessed: ['https://example.com/about'],
  purpose: {
    type: 'inference',
    description: 'RAG application',
    commercial: true,
  },
  attribution: {
    method: 'citation',
    citation_text: 'Data from Example.com',
  },
});

// Verify receipt
const isValid = await AIIndexReceiptSigner.verifyReceipt(receipt, publicKey);
```

### AIIndexLoader

LangChain document loader with advanced filtering.

```typescript
import { AIIndexLoader } from '@aiindex/lc-aiindex-reader';

const loader = new AIIndexLoader('example.com', {
  validateSchema: true,
  includeMetadata: true,
  filterContentType: ['article', 'documentation'],
  maxPages: 10,
  chunkSize: 1000,
});

// Load all documents
const documents = await loader.load();

// Load by type
const { publisher, entities, pages, faqs } = await loader.loadByType();

// Batch load multiple sites
const allDocs = await AIIndexLoader.loadBatch([
  'https://site1.com/ai-index.json',
  'https://site2.com/ai-index.json',
], {
  maxPages: 5,
});
```

## Configuration Options

### AIIndexReaderOptions

```typescript
{
  timeout?: number;              // Request timeout (default: 10000ms)
  validateSchema?: boolean;      // Enable schema validation (default: true)
  autoSendReceipt?: boolean;     // Auto-send receipts (default: false)
  clientId?: string;             // Client identifier
  clientName?: string;           // Client display name
  clientVersion?: string;        // Client version
  privateKeyPem?: string;        // Private key for signing
  keyId?: string;                // Key identifier
  algorithm?: 'ES256' | 'RS256'; // Signature algorithm (default: ES256)
}
```

### AIIndexLoaderOptions

Extends `AIIndexReaderOptions` with:

```typescript
{
  chunkSize?: number;           // Document chunk size
  includeMetadata?: boolean;    // Include metadata in documents (default: true)
  filterContentType?: string[]; // Filter pages by content type
  maxPages?: number;            // Max number of pages to load
}
```

## LangChain Integration

Use loaded documents with any LangChain component:

```typescript
import { AIIndexLoader } from '@aiindex/lc-aiindex-reader';
import { Chroma } from '@langchain/community/vectorstores/chroma';
import { OpenAIEmbeddings } from '@langchain/openai';

// Load documents
const loader = new AIIndexLoader('example.com');
const documents = await loader.load();

// Create vector store
const vectorStore = await Chroma.fromDocuments(
  documents,
  new OpenAIEmbeddings(),
  { collectionName: 'aiindex' }
);

// Use in RAG chain
const retriever = vectorStore.asRetriever();
```

## Document Structure

Each LangChain document includes:

```typescript
{
  pageContent: string;  // Formatted text content
  metadata: {
    source: string;           // Original URL
    type: string;             // 'publisher' | 'entity' | 'page' | 'faq'
    title?: string;           // Document title
    content_type?: string;    // Page content type
    author?: string;          // Page author
    published?: string;       // Publication date
    modified?: string;        // Last modified date
    tags?: string[];          // Content tags
    entity_type?: string;     // Entity type (for entities)
    entity_name?: string;     // Entity name (for entities)
    category?: string;        // FAQ category (for FAQs)
    ai_index_source: string;  // Source ai-index.json URL
  }
}
```

## Receipt Format

Receipts follow the AIIndex protocol:

```typescript
{
  version: "1.0",
  receipt_id: "uuid-v4",
  publisher_id: "example.com",
  client_id: "my-app",
  timestamp: "2024-01-01T00:00:00Z",
  access: {
    url: "https://example.com/ai-index.json",
    method: "GET",
    status_code: 200,
    content_hash: "sha256-hash"
  },
  purpose: {
    type: "inference",
    description: "RAG application",
    commercial: true
  },
  attribution: {
    method: "citation",
    citation_text: "Data from Example.com"
  },
  signature: {
    algorithm: "ES256",
    kid: "key-001",
    signature: "base64-jws",
    document_hash: "sha256-hash",
    signed_at: "2024-01-01T00:00:00Z"
  }
}
```

## Error Handling

All methods include comprehensive error handling:

```typescript
try {
  const documents = await loader.load();
} catch (error) {
  if (error.message.includes('HTTP 404')) {
    console.error('ai-index.json not found');
  } else if (error.message.includes('Network error')) {
    console.error('Connection failed');
  } else if (error.message.includes('Schema validation')) {
    console.error('Invalid document format');
  }
}
```

## Advanced Usage

### Custom Validation

```typescript
const reader = new AIIndexReader({ validateSchema: true });
const document = await reader.fetch('example.com');

const validation = reader.validate(document);
if (!validation.valid) {
  console.error('Validation errors:', validation.errors);
}
```

### Content Hash Verification

```typescript
const reader = new AIIndexReader();
const document = await reader.fetch('example.com');
const hash = await reader.getContentHash(document);
console.log('Content hash:', hash);
```

### Batch Receipt Creation

```typescript
const results = await signer.createAndPostReceiptsBatch([
  { document: doc1, options: { url: url1 } },
  { document: doc2, options: { url: url2 } },
]);

results.forEach((result, index) => {
  console.log(`Receipt ${index + 1}: ${result.posted ? 'Posted' : 'Failed'}`);
});
```

## TypeScript Support

Full TypeScript definitions included:

```typescript
import type {
  AIIndexDocument,
  Receipt,
  ValidationResult,
  AIIndexLoaderOptions,
} from '@aiindex/lc-aiindex-reader';
```

## Examples

See `examples/usage.ts` for complete examples including:

- Basic reading
- Batch operations
- Receipt signing and verification
- LangChain integration
- RAG chains
- Vector store usage

## License

MIT

## Links

- Documentation: https://docs.aiindex.org
- GitHub: https://github.com/aiindex/lc-aiindex-reader
- AIIndex Protocol: https://aiindex.org
