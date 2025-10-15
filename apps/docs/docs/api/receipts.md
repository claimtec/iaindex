---
sidebar_position: 2
title: Receipts API
---

# Receipts API

Submit and query usage receipts.

## Submit Receipt

```http
POST /api/v1/receipts
Content-Type: application/json

{
  "version": "1.0.0",
  "receiptId": "...",
  "timestamp": "2025-01-17T14:30:00Z",
  "content": { "entryId": "...", "url": "..." },
  "client": { "id": "...", "name": "..." },
  "usage": { "purpose": "training" },
  "signature": "..."
}
```

Response:
```json
{
  "received": true,
  "receiptId": "...",
  "processedAt": "2025-01-17T14:30:01Z"
}
```

## Query Receipts

```http
GET /api/v1/receipts?contentId={id}&startDate={date}
Authorization: Bearer ia_live_...
```

Response:
```json
{
  "receipts": [
    {
      "receiptId": "...",
      "timestamp": "...",
      "client": { "name": "..." },
      "usage": { "purpose": "training" }
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "perPage": 20
  }
}
```

## Batch Submit

```http
POST /api/v1/receipts/batch
Content-Type: application/json

{
  "receipts": [
    { /* receipt 1 */ },
    { /* receipt 2 */ }
  ]
}
```
