---
sidebar_position: 3
title: Analytics API
---

# Analytics API

Query usage analytics and statistics.

## Get Dashboard Stats

```http
GET /api/v1/analytics/dashboard
Authorization: Bearer ia_live_...
```

Response:
```json
{
  "totalReceipts": 1543,
  "uniqueClients": 12,
  "topContent": [
    {
      "entryId": "...",
      "url": "...",
      "title": "...",
      "receiptCount": 87
    }
  ],
  "usageByPurpose": {
    "training": 1200,
    "inference": 300,
    "research": 43
  }
}
```

## Content Usage

```http
GET /api/v1/analytics/content/{entryId}
Authorization: Bearer ia_live_...
```

## Client Activity

```http
GET /api/v1/analytics/clients/{clientId}
Authorization: Bearer ia_live_...
```

## Time Series Data

```http
GET /api/v1/analytics/timeseries?metric=receipts&interval=day
Authorization: Bearer ia_live_...
```
