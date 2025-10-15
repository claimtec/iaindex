---
sidebar_position: 4
title: Attestations API
---

# Attestations API

Manage cryptographic attestations for content and receipts.

## Create Attestation

```http
POST /api/v1/attestations
Authorization: Bearer ia_live_...
Content-Type: application/json

{
  "entryId": "...",
  "attestationType": "content-verification",
  "metadata": {}
}
```

## Verify Attestation

```http
POST /api/v1/attestations/verify
Content-Type: application/json

{
  "attestation": "...",
  "signature": "..."
}
```

Response:
```json
{
  "valid": true,
  "attestationType": "content-verification",
  "timestamp": "2025-01-17T12:00:00Z"
}
```
