---
sidebar_position: 3
title: Cryptographic Signatures
---

# Cryptographic Signatures

IAIndex uses cryptographic signatures to ensure authenticity, integrity, and non-repudiation of all protocol messages.

## Signature Algorithms

### Ed25519 (Recommended)

- **Key Size**: 256 bits
- **Signature Size**: 64 bytes
- **Speed**: Very fast signing and verification
- **Security**: High security level

```javascript
const nacl = require('tweetnacl');

// Generate keypair
const keypair = nacl.sign.keyPair();
const publicKey = keypair.publicKey;
const privateKey = keypair.secretKey;

// Sign data
const message = Buffer.from('data to sign');
const signature = nacl.sign.detached(message, privateKey);

// Verify signature
const isValid = nacl.sign.detached.verify(message, signature, publicKey);
```

### RSA-2048

- **Key Size**: 2048 bits
- **Signature Size**: 256 bytes
- **Speed**: Slower than Ed25519
- **Security**: Widely trusted

```javascript
const crypto = require('crypto');

// Generate keypair
const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});

// Sign data
const sign = crypto.createSign('SHA256');
sign.update('data to sign');
const signature = sign.sign(privateKey, 'base64');

// Verify signature
const verify = crypto.createVerify('SHA256');
verify.update('data to sign');
const isValid = verify.verify(publicKey, signature, 'base64');
```

## Canonical JSON

Before signing, data must be canonicalized to ensure consistent signatures:

```javascript
function canonicalJSON(obj) {
  // Sort keys recursively
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(canonicalJSON);
  }
  
  const sorted = {};
  Object.keys(obj).sort().forEach(key => {
    sorted[key] = canonicalJSON(obj[key]);
  });
  
  return sorted;
}

// Canonicalize and serialize
const canonical = canonicalJSON(data);
const payload = JSON.stringify(canonical);
```

## Key Management

### Key Generation

Generate keys securely:

```bash
# Ed25519
openssl genpkey -algorithm Ed25519 -out private.pem
openssl pkey -in private.pem -pubout -out public.pem

# RSA-2048
openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private.pem -out public.pem
```

### Key Storage

**Private Keys**: 
- Store encrypted at rest
- Use HSM or key management service for production
- Never commit to version control
- Rotate regularly (annually recommended)

**Public Keys**:
- Embed in index files
- Publish via HTTPS
- Include in receipts
- No encryption needed

### Key Rotation

Plan for key rotation:

```json
{
  "keys": [
    {
      "id": "key-2025-01",
      "algorithm": "Ed25519",
      "publicKey": "...",
      "validFrom": "2025-01-01T00:00:00Z",
      "validUntil": "2026-01-01T00:00:00Z",
      "status": "active"
    },
    {
      "id": "key-2024-01",
      "algorithm": "Ed25519",
      "publicKey": "...",
      "validFrom": "2024-01-01T00:00:00Z",
      "validUntil": "2025-01-01T00:00:00Z",
      "status": "retired"
    }
  ]
}
```

## Signature Verification

### Step-by-Step Verification

1. **Extract signature** from the message
2. **Canonicalize** the message payload
3. **Retrieve public key** from publisher/client
4. **Verify signature** using the public key
5. **Check timestamp** to prevent replay attacks

```javascript
async function verifySignature(message) {
  // 1. Extract signature
  const { signature, signatureAlgorithm, ...payload } = message;
  
  // 2. Canonicalize payload
  const canonical = JSON.stringify(
    canonicalJSON(payload),
    Object.keys(payload).sort()
  );
  
  // 3. Get public key
  const publicKey = await getPublicKey(payload.publisher);
  
  // 4. Verify
  const isValid = await verify(canonical, signature, publicKey, signatureAlgorithm);
  
  // 5. Check timestamp
  const timestamp = new Date(payload.timestamp);
  const now = new Date();
  const fiveMinutes = 5 * 60 * 1000;
  
  if (Math.abs(now - timestamp) > fiveMinutes) {
    throw new Error('Timestamp out of acceptable range');
  }
  
  return isValid;
}
```

## Timestamp Validation

Prevent replay attacks by validating timestamps:

- **Accept window**: ±5 minutes from current time
- **Store processed IDs**: Prevent duplicate processing
- **Use monotonic IDs**: Include nonces or sequence numbers

```javascript
const processedReceipts = new Set();

function validateTimestamp(receipt) {
  // Check if already processed
  if (processedReceipts.has(receipt.receiptId)) {
    throw new Error('Duplicate receipt');
  }
  
  // Validate timestamp
  const timestamp = new Date(receipt.timestamp);
  const now = new Date();
  const maxAge = 5 * 60 * 1000; // 5 minutes
  
  if (Math.abs(now - timestamp) > maxAge) {
    throw new Error('Receipt timestamp too old or in future');
  }
  
  // Mark as processed
  processedReceipts.add(receipt.receiptId);
  
  return true;
}
```

## Security Best Practices

### 1. Key Security

- Use hardware security modules (HSM) for private keys
- Implement key rotation policies
- Monitor key usage and access
- Use separate keys for different purposes

### 2. Algorithm Selection

- Prefer Ed25519 for new implementations
- Support multiple algorithms for compatibility
- Stay updated on cryptographic standards
- Plan migration paths for deprecated algorithms

### 3. Signature Verification

- Always verify signatures before processing
- Check certificate/key validity periods
- Implement replay attack prevention
- Log verification failures for security monitoring

### 4. Error Handling

```javascript
try {
  const isValid = await verifySignature(receipt);
  if (!isValid) {
    logger.warn('Invalid signature', { receiptId: receipt.receiptId });
    return { error: 'Invalid signature' };
  }
} catch (error) {
  logger.error('Signature verification error', { error, receiptId: receipt.receiptId });
  return { error: 'Verification failed' };
}
```

## Testing Signatures

Use test vectors for validation:

```javascript
describe('Signature Verification', () => {
  it('should verify valid Ed25519 signature', async () => {
    const testReceipt = {
      receiptId: 'test-123',
      timestamp: '2025-01-17T12:00:00Z',
      // ... other fields
    };
    
    const signature = await sign(testReceipt, testPrivateKey);
    const isValid = await verify(testReceipt, signature, testPublicKey);
    
    expect(isValid).toBe(true);
  });
  
  it('should reject tampered message', async () => {
    const testReceipt = { /* ... */ };
    const signature = await sign(testReceipt, testPrivateKey);
    
    // Tamper with message
    testReceipt.timestamp = '2025-01-18T12:00:00Z';
    
    const isValid = await verify(testReceipt, signature, testPublicKey);
    
    expect(isValid).toBe(false);
  });
});
```

## Related Documentation

- [JSON Schema](./schema.md)
- [Receipt Format](./receipts.md)
- [API Authentication](../api/authentication.md)
