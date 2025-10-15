---
sidebar_position: 1
title: GDPR Compliance
---

# GDPR Compliance

IAIndex is designed to comply with the General Data Protection Regulation (GDPR).

## Data Collection

IAIndex collects:
- Publisher domain information
- Content metadata (titles, URLs, authors)
- Usage receipts (access timestamps, client information)

## Legal Basis

Processing is based on:
- **Legitimate Interest**: Attribution and transparency
- **Consent**: Where explicitly provided
- **Contract**: For paid services

## Data Subject Rights

### Right to Access
Publishers can access all their data via API:
```http
GET /api/v1/publisher/data
```

### Right to Rectification
Update incorrect data:
```http
PATCH /api/v1/publisher/entries/{id}
```

### Right to Erasure
Delete data:
```http
DELETE /api/v1/publisher/entries/{id}
```

### Right to Data Portability
Export all data:
```http
GET /api/v1/publisher/export
```

## Data Retention

- Index entries: Retained while publisher account active
- Receipts: Retained for 7 years for audit purposes
- Logs: Retained for 90 days

## Data Processors

IAIndex uses these processors:
- AWS (hosting)
- Cloudflare (CDN)
- SendGrid (email)

## Security Measures

- End-to-end encryption
- Access controls
- Regular security audits
- Incident response plan

## Contact

Data Protection Officer: privacy@iaindex.com
