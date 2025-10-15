---
sidebar_position: 2
title: Receipt Format
---

# Receipt Format

Receipts are cryptographically signed documents that prove an AI system accessed specific content. They provide transparency and enable attribution tracking.

## Receipt Structure

```json
{
  "version": "1.0.0",
  "receiptId": "7f9c1234-abcd-4321-9876-543210fedcba",
  "timestamp": "2025-01-17T14:30:00.000Z",
  "content": {
    "entryId": "550e8400-e29b-41d4-a716-446655440000",
    "url": "https://example.com/article-1",
    "contentHash": "sha256:abc123...",
    "publisher": "example.com"
  },
  "client": {
    "id": "client-uuid-here",
    "name": "AI Model Name",
    "version": "1.0.0",
    "organization": "AI Company Inc",
    "publicKey": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
  },
  "usage": {
    "purpose": "training",
    "context": "language-model-pretraining",
    "datasetId": "dataset-2025-01",
    "modelId": "model-v1.0"
  },
  "signature": "base64-encoded-signature",
  "signatureAlgorithm": "Ed25519"
}
```

## Field Definitions

### Root Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Receipt format version |
| `receiptId` | string (UUID) | Yes | Unique receipt identifier |
| `timestamp` | string (ISO 8601) | Yes | Access timestamp |
| `content` | object | Yes | Content information |
| `client` | object | Yes | AI client information |
| `usage` | object | Yes | Usage details |
| `signature` | string | Yes | Cryptographic signature |
| `signatureAlgorithm` | string | Yes | Signature algorithm used |

### Content Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entryId` | string (UUID) | Yes | IAIndex entry ID |
| `url` | string (URL) | Yes | Content URL |
| `contentHash` | string | Yes | SHA-256 hash of accessed content |
| `publisher` | string | Yes | Publisher domain |

### Client Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID) | Yes | Unique client identifier |
| `name` | string | Yes | Client name/model name |
| `version` | string | Yes | Client version |
| `organization` | string | Yes | Organization name |
| `publicKey` | string | Yes | Client's public key |

### Usage Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `purpose` | string | Yes | "training", "inference", "research" |
| `context` | string | Yes | Specific use case |
| `datasetId` | string | No | Dataset identifier |
| `modelId` | string | No | Model identifier |

## Usage Purposes

### Training
Content used for training AI models:

```json
{
  "purpose": "training",
  "context": "language-model-pretraining",
  "datasetId": "common-crawl-2025-01",
  "modelId": "gpt-next-v1"
}
```

### Inference
Content used during model inference:

```json
{
  "purpose": "inference",
  "context": "rag-retrieval",
  "queryId": "query-abc123",
  "sessionId": "session-xyz789"
}
```

### Research
Content used for research purposes:

```json
{
  "purpose": "research",
  "context": "benchmark-evaluation",
  "studyId": "study-2025-q1",
  "researcherId": "researcher-123"
}
```

## Signature Algorithm

Receipts must be signed using one of these algorithms:

- **Ed25519** (Recommended): Fast, secure, small signatures
- **RSA-2048**: Widely supported, larger signatures
- **ECDSA-P256**: Good balance of size and security

### Signature Generation

```javascript
const nacl = require('tweetnacl');
const { encodeBase64 } = require('tweetnacl-util');

// Generate receipt payload
const receipt = {
  version: '1.0.0',
  receiptId: generateUUID(),
  timestamp: new Date().toISOString(),
  content: { /* ... */ },
  client: { /* ... */ },
  usage: { /* ... */ }
};

// Create canonical JSON (sorted keys, no whitespace)
const canonicalPayload = JSON.stringify(receipt, Object.keys(receipt).sort());

// Sign with private key
const signature = nacl.sign.detached(
  Buffer.from(canonicalPayload),
  privateKey
);

// Add signature to receipt
receipt.signature = encodeBase64(signature);
receipt.signatureAlgorithm = 'Ed25519';
```

### Signature Verification

```javascript
const { verifyReceipt } = require('@iaindex/sdk');

const isValid = await verifyReceipt(receipt, clientPublicKey);

if (isValid) {
  console.log('Receipt verified successfully');
} else {
  console.error('Invalid receipt signature');
}
```

## Receipt Submission

Receipts are submitted to the publisher's webhook endpoint:

```bash
POST https://example.com/api/iaindex/receipt
Content-Type: application/json

{
  "version": "1.0.0",
  "receiptId": "...",
  // ... rest of receipt
}
```

### Response Codes

| Code | Description |
|------|-------------|
| 200 | Receipt accepted |
| 400 | Invalid receipt format |
| 401 | Invalid signature |
| 404 | Content not found |
| 429 | Rate limit exceeded |
| 500 | Server error |

## Receipt Storage

Publishers should store receipts with:

1. **Original Receipt**: Complete JSON
2. **Indexed Fields**: For querying
3. **Verification Status**: Signature verification result
4. **Metadata**: Processing timestamp, notes

Example database schema:

```sql
CREATE TABLE receipts (
  id UUID PRIMARY KEY,
  receipt_id UUID UNIQUE NOT NULL,
  content_id UUID NOT NULL,
  client_id UUID NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  purpose VARCHAR(50) NOT NULL,
  signature TEXT NOT NULL,
  verified BOOLEAN NOT NULL,
  raw_receipt JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_receipts_content_id ON receipts(content_id);
CREATE INDEX idx_receipts_client_id ON receipts(client_id);
CREATE INDEX idx_receipts_timestamp ON receipts(timestamp);
```

## Best Practices

1. **Verify Immediately**: Validate signatures upon receipt
2. **Store Originals**: Keep complete receipt JSON
3. **Index for Queries**: Enable fast lookups by content/client
4. **Monitor Patterns**: Track unusual access patterns
5. **Respect Privacy**: Handle PII in receipts appropriately
6. **Archive Old Receipts**: Implement retention policies

## Receipt Batching

For high-volume scenarios, clients can batch receipts:

```json
{
  "version": "1.0.0",
  "batchId": "batch-uuid",
  "receipts": [
    { /* receipt 1 */ },
    { /* receipt 2 */ },
    { /* receipt 3 */ }
  ],
  "signature": "batch-signature",
  "signatureAlgorithm": "Ed25519"
}
```

Each receipt in the batch is individually signed, plus the entire batch has a signature.

## Related Documentation

- [Cryptographic Signatures](./signatures.md)
- [Receiving Receipts](../publishers/receiving-receipts.md)
- [API Reference: Receipts](../api/receipts.md)
