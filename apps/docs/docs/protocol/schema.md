---
sidebar_position: 1
title: JSON Schema
---

# IAIndex JSON Schema

The IAIndex protocol uses a standardized JSON schema for all index entries. This ensures interoperability across different implementations.

## Index File Structure

The root index file (`iaindex.json`) contains metadata about the publisher and a list of content entries:

```json
{
  "version": "1.0.0",
  "publisher": {
    "domain": "example.com",
    "name": "Example Publications",
    "contact": "contact@example.com",
    "publicKey": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
    "verificationUrl": "https://example.com/.well-known/iaindex-verification.txt"
  },
  "entries": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "https://example.com/article-1",
      "title": "Article Title",
      "author": "Author Name",
      "publishedDate": "2025-01-15T10:00:00Z",
      "modifiedDate": "2025-01-16T14:30:00Z",
      "contentHash": "sha256:abc123...",
      "license": {
        "type": "CC-BY-4.0",
        "terms": "https://creativecommons.org/licenses/by/4.0/",
        "commercial": true,
        "derivatives": true,
        "attribution": true
      },
      "access": {
        "method": "webhook",
        "url": "https://example.com/api/iaindex/receipt",
        "requiresReceipt": true
      },
      "metadata": {
        "category": "Technology",
        "tags": ["AI", "Machine Learning"],
        "language": "en",
        "readingTime": 5
      }
    }
  ],
  "signature": "base64-encoded-signature",
  "signedAt": "2025-01-17T12:00:00Z"
}
```

## Field Definitions

### Publisher Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | Yes | Publisher's verified domain |
| `name` | string | Yes | Publisher's display name |
| `contact` | string | Yes | Contact email address |
| `publicKey` | string | Yes | RSA/Ed25519 public key (PEM format) |
| `verificationUrl` | string | No | URL to domain verification file |

### Entry Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID) | Yes | Unique identifier for the entry |
| `url` | string (URL) | Yes | Canonical URL of the content |
| `title` | string | Yes | Content title |
| `author` | string | Yes | Author name(s) |
| `publishedDate` | string (ISO 8601) | Yes | Publication timestamp |
| `modifiedDate` | string (ISO 8601) | No | Last modification timestamp |
| `contentHash` | string | Yes | SHA-256 hash of content |
| `license` | object | Yes | Licensing information |
| `access` | object | Yes | Access control settings |
| `metadata` | object | No | Additional metadata |

### License Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | License type (SPDX identifier) |
| `terms` | string (URL) | Yes | URL to full license terms |
| `commercial` | boolean | Yes | Allow commercial use |
| `derivatives` | boolean | Yes | Allow derivative works |
| `attribution` | boolean | Yes | Require attribution |
| `customTerms` | string | No | Additional license terms |

### Access Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `method` | string | Yes | Access method: "webhook", "api", "public" |
| `url` | string (URL) | Yes | Endpoint for receipt submission |
| `requiresReceipt` | boolean | Yes | Whether receipt is mandatory |
| `apiKey` | string | No | API key for authentication |
| `rateLimit` | object | No | Rate limiting configuration |

## Content Hash

The content hash ensures integrity and allows detection of modifications:

```javascript
// Example: Generate content hash
const crypto = require('crypto');

const content = 'Your article content...';
const hash = crypto
  .createHash('sha256')
  .update(content)
  .digest('hex');

console.log(`sha256:${hash}`);
```

## License Types

Common license types (SPDX identifiers):

- `CC-BY-4.0` - Creative Commons Attribution 4.0
- `CC-BY-SA-4.0` - Creative Commons Attribution-ShareAlike 4.0
- `CC-BY-NC-4.0` - Creative Commons Attribution-NonCommercial 4.0
- `MIT` - MIT License
- `Apache-2.0` - Apache License 2.0
- `proprietary` - Custom/proprietary license
- `all-rights-reserved` - All rights reserved

## Version History

### Version 1.0.0 (Current)

Initial release of the IAIndex protocol schema.

## Validation

Use the official JSON Schema validator:

```bash
npm install -g @iaindex/validator

iaindex-validate iaindex.json
```

Or programmatically:

```javascript
const { validateIndex } = require('@iaindex/validator');

const isValid = await validateIndex(indexData);
if (!isValid) {
  console.error('Invalid index:', validateIndex.errors);
}
```

## Extensions

Publishers can add custom fields under the `x-` prefix:

```json
{
  "x-customField": "custom value",
  "x-internalId": "internal-123"
}
```

Custom fields are ignored by validators but preserved in the index.

## Best Practices

1. **Keep URLs Canonical**: Use the primary URL for each piece of content
2. **Update Hashes**: Regenerate content hashes when content changes
3. **Use Standard Licenses**: Prefer SPDX identifiers when possible
4. **Include Metadata**: Rich metadata improves discoverability
5. **Sign Regularly**: Re-sign your index daily or when updated
6. **Validate Before Publishing**: Always validate before deployment

## Related Documentation

- [Receipt Format](./receipts.md)
- [Cryptographic Signatures](./signatures.md)
- [Generating Indexes](../publishers/generating-index.md)
