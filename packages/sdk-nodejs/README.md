# IAIndex SDK for Node.js

Official IAIndex SDK for Node.js applications. Track and verify AI content usage with cryptographic receipts and attestations.

## Features

- **Publisher Tools**: Register and verify content with cryptographic signatures
- **Client Tools**: Access content and send usage receipts
- **ECDSA Signing**: Secure cryptographic signatures using secp256k1
- **Receipt Generation**: Automatic receipt creation and submission
- **API Integration**: Seamless integration with IAIndex API
- **TypeScript Support**: Full TypeScript definitions included

## Installation

```bash
npm install @iaindex/sdk
# or
yarn add @iaindex/sdk
```

## Quick Start

### For Publishers

```javascript
const { IAIndexPublisher, CryptoUtils } = require('@iaindex/sdk');

// Generate a key pair (or use existing private key)
const keyPair = CryptoUtils.generateKeyPair();

// Initialize publisher
const publisher = new IAIndexPublisher({
  domain: 'yourdomain.com',
  privateKey: keyPair.privateKey,
  name: 'Your Publication',
  contact: 'contact@yourdomain.com'
});

// Initialize connection to API
await publisher.initialize();

// Add content entries
await publisher.addEntry({
  url: 'https://yourdomain.com/article',
  title: 'Article Title',
  author: 'Author Name',
  publishedDate: new Date().toISOString(),
  license: { type: 'CC-BY-4.0' }
});

// Generate signed index file
const index = await publisher.generateIndex();
console.log('Index generated:', index);
```

### For AI Clients

```javascript
const { IAIndexClient, CryptoUtils } = require('@iaindex/sdk');

// Generate a key pair (or use existing private key)
const keyPair = CryptoUtils.generateKeyPair();

// Initialize client
const client = new IAIndexClient({
  clientId: 'your-client-id',
  privateKey: keyPair.privateKey,
  name: 'Your AI Model',
  organization: 'Your Organization'
});

// Initialize connection to API
await client.initialize();

// Access content and get metadata
const content = await client.accessContent('https://example.com/article');

// Send usage receipt
await client.sendReceipt(content, {
  purpose: 'training',
  context: 'language-model-pretraining',
  modelId: 'my-model-v1'
});
```

## API Reference

### IAIndexPublisher

#### Constructor

```typescript
new IAIndexPublisher(options: PublisherOptions)
```

**Options:**
- `domain` (string): Your verified domain
- `privateKey` (string): Private key for signing (hex string)
- `name` (string): Publisher name
- `contact` (string): Contact email
- `apiBaseUrl` (string, optional): Custom API base URL

#### Methods

**`async initialize(): Promise<void>`**

Initialize publisher and authenticate with API. Must be called before other operations.

**`async addEntry(entry: ContentEntry): Promise<string>`**

Add a content entry to the index.

```typescript
const entryId = await publisher.addEntry({
  url: 'https://example.com/article',
  title: 'Article Title',
  author: 'Author Name',
  publishedDate: '2024-01-01T00:00:00Z',
  content: 'Article content...',
  license: {
    type: 'CC-BY-4.0',
    terms: 'Attribution required'
  }
});
```

**`async generateIndex(): Promise<IndexFile>`**

Generate a signed index file containing all entries.

```typescript
const index = await publisher.generateIndex();
// Returns: { domain, publisher, entries, signature, timestamp, version }
```

**`async verifyReceipt(receipt: Receipt): Promise<boolean>`**

Verify a receipt signature.

```typescript
const isValid = await publisher.verifyReceipt(receipt);
```

**`getEntries(): ContentEntry[]`**

Get all added entries.

**`getPublicKey(): string`**

Get the publisher's public key.

**`getDomain(): string`**

Get the publisher's domain.

### IAIndexClient

#### Constructor

```typescript
new IAIndexClient(options: ClientOptions)
```

**Options:**
- `clientId` (string): Unique client identifier
- `privateKey` (string): Private key for signing (hex string)
- `name` (string, optional): Client/model name
- `organization` (string, optional): Organization name
- `apiBaseUrl` (string, optional): Custom API base URL

#### Methods

**`async initialize(): Promise<void>`**

Initialize client and authenticate with API. Must be called before other operations.

**`async accessContent(url: string): Promise<ContentMetadata>`**

Access content and retrieve metadata.

```typescript
const metadata = await client.accessContent('https://example.com/article');
// Returns: { url, title, author, publishedDate, license, publisher }
```

**`async sendReceipt(content: ContentMetadata, usage: UsageInfo): Promise<boolean>`**

Send a usage receipt for accessed content.

```typescript
const success = await client.sendReceipt(content, {
  purpose: 'training',  // 'training' | 'inference' | 'research'
  context: 'language-model-pretraining',
  datasetId: 'dataset-v1',
  modelId: 'model-v1'
});
```

**`async getVerifiedPublishers(): Promise<any[]>`**

Get list of verified publishers.

**`getClientId(): string`**

Get the client ID.

**`getPublicKey(): string`**

Get the client's public key.

### CryptoUtils

Utility class for cryptographic operations.

#### Methods

**`static generateKeyPair(): KeyPair`**

Generate a new ECDSA key pair.

```typescript
const keyPair = CryptoUtils.generateKeyPair();
// Returns: { privateKey: string, publicKey: string }
```

**`static sign(data: string | object, privateKey: string): string`**

Sign data with a private key.

**`static verify(data: string | object, signature: string, publicKey: string): boolean`**

Verify a signature with a public key.

**`static getPublicKey(privateKey: string): string`**

Derive public key from private key.

**`static hash(data: string | object): string`**

Generate SHA-256 hash of data.

**`static generateId(): string`**

Generate a random ID.

## TypeScript Support

The SDK is written in TypeScript and includes full type definitions.

```typescript
import { IAIndexPublisher, IAIndexClient, CryptoUtils, ContentEntry } from '@iaindex/sdk';

const entry: ContentEntry = {
  url: 'https://example.com/article',
  title: 'Article Title',
  author: 'Author Name',
  publishedDate: new Date().toISOString(),
  license: { type: 'CC-BY-4.0' }
};
```

## Examples

### Complete Publisher Example

```javascript
const { IAIndexPublisher, CryptoUtils } = require('@iaindex/sdk');

async function main() {
  // Generate or load key pair
  const keyPair = CryptoUtils.generateKeyPair();
  console.log('Private Key:', keyPair.privateKey);
  console.log('Public Key:', keyPair.publicKey);

  // Create publisher
  const publisher = new IAIndexPublisher({
    domain: 'myblog.com',
    privateKey: keyPair.privateKey,
    name: 'My Blog',
    contact: 'admin@myblog.com'
  });

  // Initialize
  await publisher.initialize();
  console.log('Publisher initialized');

  // Add multiple entries
  const entries = [
    {
      url: 'https://myblog.com/post-1',
      title: 'First Post',
      author: 'John Doe',
      publishedDate: '2024-01-01T00:00:00Z',
      license: { type: 'CC-BY-4.0' }
    },
    {
      url: 'https://myblog.com/post-2',
      title: 'Second Post',
      author: 'Jane Smith',
      publishedDate: '2024-01-02T00:00:00Z',
      license: { type: 'MIT' }
    }
  ];

  for (const entry of entries) {
    const entryId = await publisher.addEntry(entry);
    console.log('Added entry:', entryId);
  }

  // Generate index
  const index = await publisher.generateIndex();
  console.log('Generated index with', index.entries.length, 'entries');

  // Save index to file
  const fs = require('fs');
  fs.writeFileSync('iaindex.json', JSON.stringify(index, null, 2));
}

main().catch(console.error);
```

### Complete Client Example

```javascript
const { IAIndexClient, CryptoUtils } = require('@iaindex/sdk');

async function main() {
  // Generate or load key pair
  const keyPair = CryptoUtils.generateKeyPair();

  // Create client
  const client = new IAIndexClient({
    clientId: 'my-ai-model',
    privateKey: keyPair.privateKey,
    name: 'My AI Model',
    organization: 'My Company'
  });

  // Initialize
  await client.initialize();
  console.log('Client initialized');

  // Access content
  const url = 'https://example.com/article';
  const content = await client.accessContent(url);
  console.log('Accessed content:', content);

  // Send receipt
  const success = await client.sendReceipt(content, {
    purpose: 'training',
    context: 'pre-training dataset collection',
    datasetId: 'dataset-2024-01',
    modelId: 'my-model-v1.0'
  });

  console.log('Receipt sent:', success);

  // Get verified publishers
  const publishers = await client.getVerifiedPublishers();
  console.log('Verified publishers:', publishers.length);
}

main().catch(console.error);
```

## Environment Variables

You can store your private keys and API configuration in environment variables:

```javascript
const publisher = new IAIndexPublisher({
  domain: 'yourdomain.com',
  privateKey: process.env.IAINDEX_PRIVATE_KEY,
  name: 'Your Publication',
  contact: process.env.PUBLISHER_CONTACT,
  apiBaseUrl: process.env.IAINDEX_API_URL // optional
});
```

## Error Handling

```javascript
try {
  await publisher.addEntry(entry);
} catch (error) {
  console.error('Failed to add entry:', error.message);
}
```

## Testing

Run the test suite:

```bash
npm test
```

Run tests with coverage:

```bash
npm test -- --coverage
```

## API Base URL

The default API base URL is:
```
https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
```

You can override this by passing `apiBaseUrl` in the constructor options.

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://iaindex.dev/docs
- GitHub: https://github.com/claimtec/iaindex
- Issues: https://github.com/claimtec/iaindex/issues

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.
