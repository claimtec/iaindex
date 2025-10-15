# @aiindex/sdk

Official Node.js SDK for AIIndex - Generate and manage AI Index files for AI agent discovery.

## Installation

```bash
npm install @aiindex/sdk
```

## Features

- **CLI Tool**: `aiindex-gen` command-line tool for easy AI Index file management
- **TypeScript Support**: Full TypeScript definitions included
- **Website Crawler**: Automatically extract metadata from your website
- **Cryptographic Signing**: ECDSA P-256 signatures for file integrity
- **Receipt Handling**: Built-in webhook server for receipt management
- **Validation**: Schema validation for AI Index files
- **Dual Module Support**: Works with both ESM and CommonJS

## Quick Start

### CLI Usage

#### 1. Initialize Configuration

```bash
npx aiindex-gen init
```

This creates an `aiindex.config.json` file with default settings.

#### 2. Generate AI Index File

```bash
npx aiindex-gen build --url https://your-website.com
```

Or use the configuration file:

```bash
npx aiindex-gen build
```

#### 3. Validate Generated File

```bash
npx aiindex-gen verify ai-index.json
```

#### 4. Sign Your AI Index File

Generate keys and sign in one step:

```bash
npx aiindex-gen sign --generate-keys
```

Or use existing keys:

```bash
npx aiindex-gen sign --key ./keys/private-key.json
```

#### 5. Start Webhook Server

```bash
npx aiindex-gen serve --port 3000 --forward
```

## Programmatic Usage

### Generate AI Index File

```typescript
import { AIIndexGenerator } from '@aiindex/sdk';

const generator = new AIIndexGenerator({
  baseUrl: 'https://your-website.com',
  config: {
    name: 'My AI Service',
    description: 'A powerful AI service for natural language processing',
    capabilities: ['natural-language-processing', 'text-analysis'],
    categories: ['ai', 'nlp'],
  },
  crawlOptions: {
    maxPages: 50,
    maxDepth: 3,
  },
});

const aiIndex = await generator.generate();
console.log(aiIndex);
```

### Sign AI Index File

```typescript
import { SignatureManager } from '@aiindex/sdk';

const signer = new SignatureManager();

// Generate new key pair
const keyPair = await signer.generateKeyPair({ keyFormat: 'jwk' });
console.log('Public Key:', keyPair.publicKey);
console.log('Private Key:', keyPair.privateKey);

// Sign AI Index file
const signedAiIndex = await signer.signFile(aiIndex);

// Verify signature
const isValid = await signer.verifyFile(signedAiIndex);
console.log('Signature valid:', isValid);
```

### Handle Receipts

```typescript
import { ReceiptHandler } from '@aiindex/sdk';

const handler = new ReceiptHandler({
  apiEndpoint: 'https://api.aiindex.com',
  apiKey: 'your-api-key',
  autoForward: true,
});

// Start webhook server
await handler.startWebhookServer({
  port: 3000,
  path: '/webhook/receipts',
  onReceipt: async (receipt) => {
    console.log('Receipt received:', receipt);
    // Custom processing logic here
  },
});

// Manually forward receipt
const receipt = ReceiptHandler.createReceipt(
  'agent-id-123',
  'view',
  { page: 'homepage' }
);
await handler.forwardReceipt(receipt);
```

### Validate AI Index File

```typescript
import { Validator } from '@aiindex/sdk';
import * as fs from 'fs/promises';

const validator = new Validator();

// Validate from object
const result = validator.validate(aiIndex);
if (!result.valid) {
  console.error('Validation errors:', result.errors);
}

// Validate from JSON file
const json = await fs.readFile('ai-index.json', 'utf-8');
const schemaResult = validator.validateSchema(json);
console.log('Valid:', schemaResult.valid);
```

## Configuration File

The `aiindex.config.json` file structure:

```json
{
  "version": "1.0",
  "name": "My AI Service",
  "description": "A powerful AI service",
  "url": "https://example.com",
  "capabilities": [
    "natural-language-processing",
    "machine-learning"
  ],
  "categories": ["ai", "nlp"],
  "outputPath": "./ai-index.json",
  "privateKeyPath": "./keys/private-key.json",
  "publicKeyPath": "./keys/public-key.json",
  "apiEndpoint": "https://api.aiindex.com",
  "webhookPort": 3000,
  "webhookPath": "/webhook/receipts"
}
```

## CLI Commands

### `init`

Create a new configuration file.

```bash
aiindex-gen init [options]

Options:
  -o, --output <path>  Output path for config file (default: "./aiindex.config.json")
```

### `build`

Generate AI Index file from website or configuration.

```bash
aiindex-gen build [options]

Options:
  -c, --config <path>  Path to configuration file (default: "./aiindex.config.json")
  -u, --url <url>      Website URL to crawl
  -o, --output <path>  Output path for AI Index file
  --no-crawl           Skip website crawling, use config only
```

### `verify`

Validate AI Index file.

```bash
aiindex-gen verify [file] [options]

Arguments:
  file                 Path to AI Index file (default: "./ai-index.json")

Options:
  --check-signature    Verify cryptographic signature
```

### `sign`

Add cryptographic signature to AI Index file.

```bash
aiindex-gen sign [file] [options]

Arguments:
  file                    Path to AI Index file (default: "./ai-index.json")

Options:
  -k, --key <path>        Path to private key file
  --generate-keys         Generate new key pair
  --key-output <path>     Output directory for generated keys (default: "./keys")
```

### `serve`

Start local webhook server to receive receipts.

```bash
aiindex-gen serve [options]

Options:
  -p, --port <port>       Port to listen on (default: "3000")
  --path <path>           Webhook endpoint path (default: "/webhook/receipts")
  -c, --config <path>     Path to configuration file (default: "./aiindex.config.json")
  --api-key <key>         API key for authentication
  --forward               Forward receipts to AIIndex API
```

## API Reference

### AIIndexGenerator

Class for generating AI Index files by crawling websites.

**Constructor Options:**
- `baseUrl`: Website URL to crawl (required)
- `config`: Partial AI Index configuration
- `crawlOptions`: Crawl behavior options
  - `maxPages`: Maximum pages to crawl (default: 50)
  - `maxDepth`: Maximum crawl depth (default: 3)
  - `includePatterns`: URL patterns to include
  - `excludePatterns`: URL patterns to exclude
  - `followExternalLinks`: Follow external links (default: false)
  - `timeout`: Request timeout in ms (default: 10000)
  - `userAgent`: Custom user agent string

**Methods:**
- `generate()`: Generate AI Index file

### SignatureManager

Class for cryptographic signing using ECDSA P-256.

**Constructor:**
- `algorithm`: Signature algorithm (default: 'ES256')

**Methods:**
- `generateKeyPair(options?)`: Generate new key pair
- `loadPrivateKey(key, algorithm?)`: Load private key from string
- `loadPublicKey(key, algorithm?)`: Load public key from string
- `sign(data)`: Sign data
- `verify(signature, publicKey?)`: Verify signature
- `signFile(aiIndex)`: Sign AI Index file
- `verifyFile(aiIndex)`: Verify signed AI Index file
- `exportPublicKey()`: Export public key as JWK string
- `exportPrivateKey()`: Export private key as JWK string

### ReceiptHandler

Class for receiving and forwarding receipts.

**Constructor Options:**
- `apiEndpoint`: AIIndex API endpoint (required)
- `apiKey`: API authentication key
- `autoForward`: Auto-forward receipts (default: true)
- `retryAttempts`: Number of retry attempts (default: 3)
- `retryDelay`: Delay between retries in ms (default: 1000)

**Methods:**
- `forwardReceipt(receipt)`: Forward single receipt
- `forwardReceiptsBatch(receipts)`: Forward multiple receipts
- `startWebhookServer(options)`: Start webhook server
- `stopWebhookServer()`: Stop webhook server

**Static Methods:**
- `createReceipt(agentId, action, metadata?)`: Create receipt object

### Validator

Class for validating AI Index files.

**Methods:**
- `validate(data)`: Validate AI Index data object
- `validateSchema(json)`: Validate JSON string

## TypeScript Types

The SDK exports comprehensive TypeScript types:

```typescript
import type {
  AIIndexConfig,
  AIIndexFile,
  CrawlOptions,
  GeneratorOptions,
  ValidationResult,
  SignatureOptions,
  KeyPair,
  Receipt,
  ReceiptHandlerOptions,
  WebhookServerOptions,
  CLIConfig,
} from '@aiindex/sdk';
```

## Examples

### Complete Workflow

```typescript
import {
  AIIndexGenerator,
  SignatureManager,
  Validator,
  ReceiptHandler,
} from '@aiindex/sdk';
import * as fs from 'fs/promises';

// 1. Generate AI Index
const generator = new AIIndexGenerator({
  baseUrl: 'https://myservice.com',
  config: {
    name: 'My AI Service',
    description: 'Advanced AI capabilities',
    capabilities: ['nlp', 'ml'],
  },
});
const aiIndex = await generator.generate();

// 2. Validate
const validator = new Validator();
const validationResult = validator.validate(aiIndex);
if (!validationResult.valid) {
  throw new Error('Invalid AI Index');
}

// 3. Sign
const signer = new SignatureManager();
const keyPair = await signer.generateKeyPair();
await fs.writeFile('private-key.json', keyPair.privateKey);
await fs.writeFile('public-key.json', keyPair.publicKey);

const signedAiIndex = await signer.signFile(aiIndex);
await fs.writeFile('ai-index.json', JSON.stringify(signedAiIndex, null, 2));

// 4. Start receipt handler
const handler = new ReceiptHandler({
  apiEndpoint: 'https://api.aiindex.com',
  autoForward: true,
});

await handler.startWebhookServer({
  port: 3000,
  onReceipt: async (receipt) => {
    console.log('Receipt:', receipt);
  },
});
```

## License

MIT

## Support

- Documentation: [https://aiindex.com/docs](https://aiindex.com/docs)
- Issues: [https://github.com/aiindex/sdk-node/issues](https://github.com/aiindex/sdk-node/issues)
- Email: support@aiindex.com

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.
