---
sidebar_position: 1
title: Authentication
---

# API Authentication

IAIndex API uses API keys and cryptographic signatures for authentication.

## API Keys

### Generate API Key

```http
POST /api/v1/auth/keys
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "name": "Production Key",
  "scope": ["read", "write"],
  "expiresIn": "1y"
}
```

Response:
```json
{
  "apiKey": "ia_live_abc123...",
  "keyId": "key_xyz789",
  "scope": ["read", "write"],
  "expiresAt": "2026-01-17T12:00:00Z"
}
```

### Using API Keys

Include in request headers:

```http
GET /api/v1/publisher/entries
Authorization: Bearer ia_live_abc123...
```

## Signature Authentication

For webhook receipts, use cryptographic signatures:

```javascript
const crypto = require('crypto');

function signRequest(payload, privateKey) {
  const signature = crypto
    .createSign('SHA256')
    .update(JSON.stringify(payload))
    .sign(privateKey, 'base64');
  
  return signature;
}

// Include in request
fetch('/api/v1/receipts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-IAIndex-Signature': signature
  },
  body: JSON.stringify(payload)
});
```

## Rate Limits

| Tier | Requests/minute | Requests/day |
|------|----------------|--------------|
| Free | 60 | 10,000 |
| Pro | 300 | 100,000 |
| Enterprise | Custom | Unlimited |

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642431600
```

## Error Codes

| Code | Description |
|------|-------------|
| 401 | Invalid or missing API key |
| 403 | Insufficient permissions |
| 429 | Rate limit exceeded |
