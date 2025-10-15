---
sidebar_position: 2
title: POPIA Compliance
---

# POPIA Compliance

IAIndex complies with South Africa's Protection of Personal Information Act (POPIA).

## Information Processing

IAIndex processes information in accordance with POPIA's conditions:
- Accountability
- Processing limitation
- Purpose specification
- Further processing limitation
- Information quality
- Openness
- Security safeguards
- Data subject participation

## Personal Information

IAIndex processes:
- Contact details (email addresses)
- Usage data (access patterns)
- Technical data (IP addresses, timestamps)

## Rights of Data Subjects

### Right to Access
Request access to your information:
```http
GET /api/v1/user/information
```

### Right to Correction
Correct inaccurate information:
```http
PATCH /api/v1/user/information
```

### Right to Deletion
Request deletion:
```http
DELETE /api/v1/user/account
```

## Cross-Border Transfer

Data may be transferred outside South Africa with appropriate safeguards.

## Contact

Information Officer: privacy@iaindex.com
