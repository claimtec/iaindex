# Websites API Testing Guide

This document provides test commands for the new `/v1/websites` CRUD endpoints.

## Base URL
- Local: `http://localhost:8000`
- Staging: `https://api-staging.iaindex.org`
- Production: `https://api.iaindex.org`

## Environment Variables
Set your API base URL:
```bash
export API_URL=http://localhost:8000
```

## Test Commands

### 1. Create Website (POST /v1/websites)

**Anonymous (no auth required):**
```bash
curl -X POST "${API_URL}/v1/websites" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "url": "https://example.com",
    "business_name": "Example Business",
    "business_type": "LocalBusiness",
    "keywords": ["keyword1", "keyword2"],
    "location": {
      "city": "San Francisco",
      "country": "USA"
    }
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "uuid-here",
  "domain": "example.com",
  "url": "https://example.com",
  "business_name": "Example Business",
  "business_type": "LocalBusiness",
  "keywords": ["keyword1", "keyword2"],
  "location": {"city": "San Francisco", "country": "USA"},
  "schema_markup": null,
  "visibility_score": null,
  "last_visibility_check": null,
  "schema_generated_at": null,
  "created_at": "2025-10-18T16:00:00",
  "updated_at": "2025-10-18T16:00:00"
}
```

**If domain exists (returns existing):**
```bash
# Same as above - will return existing website with 201 status
```

### 2. Get Website by ID (GET /v1/websites/{website_id})

```bash
export WEBSITE_ID="your-website-id-here"

curl -X GET "${API_URL}/v1/websites/${WEBSITE_ID}" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": "uuid-here",
  "domain": "example.com",
  "url": "https://example.com",
  "business_name": "Example Business",
  "business_type": "LocalBusiness",
  "keywords": ["keyword1", "keyword2"],
  "location": {"city": "San Francisco", "country": "USA"},
  "schema_markup": {...},
  "visibility_score": 75,
  "last_visibility_check": "2025-10-18T15:00:00",
  "schema_generated_at": "2025-10-18T14:00:00",
  "created_at": "2025-10-18T10:00:00",
  "updated_at": "2025-10-18T15:00:00"
}
```

### 3. List Websites (GET /v1/websites)

**Anonymous (returns all public websites):**
```bash
curl -X GET "${API_URL}/v1/websites?page=1&page_size=20" \
  -H "Content-Type: application/json"
```

**Authenticated (returns user's websites):**
```bash
export API_KEY="your-api-key-here"

curl -X GET "${API_URL}/v1/websites?page=1&page_size=20" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}"
```

**Expected Response (200 OK):**
```json
{
  "websites": [
    {
      "id": "uuid-1",
      "domain": "example.com",
      "url": "https://example.com",
      "business_name": "Example Business",
      "business_type": "LocalBusiness",
      "keywords": ["keyword1", "keyword2"],
      "location": {"city": "San Francisco", "country": "USA"},
      "schema_markup": {...},
      "visibility_score": 75,
      "last_visibility_check": "2025-10-18T15:00:00",
      "schema_generated_at": "2025-10-18T14:00:00",
      "created_at": "2025-10-18T10:00:00",
      "updated_at": "2025-10-18T15:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### 4. Update Website (PUT /v1/websites/{website_id})

**Requires authentication:**
```bash
export WEBSITE_ID="your-website-id-here"
export API_KEY="your-api-key-here"

curl -X PUT "${API_URL}/v1/websites/${WEBSITE_ID}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "business_name": "Updated Business Name",
    "keywords": ["new-keyword1", "new-keyword2", "new-keyword3"]
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": "uuid-here",
  "domain": "example.com",
  "url": "https://example.com",
  "business_name": "Updated Business Name",
  "business_type": "LocalBusiness",
  "keywords": ["new-keyword1", "new-keyword2", "new-keyword3"],
  "location": {"city": "San Francisco", "country": "USA"},
  "schema_markup": {...},
  "visibility_score": 75,
  "last_visibility_check": "2025-10-18T15:00:00",
  "schema_generated_at": "2025-10-18T14:00:00",
  "created_at": "2025-10-18T10:00:00",
  "updated_at": "2025-10-18T16:30:00"
}
```

### 5. Delete Website (DELETE /v1/websites/{website_id})

**Requires authentication:**
```bash
export WEBSITE_ID="your-website-id-here"
export API_KEY="your-api-key-here"

curl -X DELETE "${API_URL}/v1/websites/${WEBSITE_ID}" \
  -H "X-API-Key: ${API_KEY}"
```

**Expected Response (204 No Content):**
```
(Empty response body)
```

## Integration with Visibility Check

After creating a website, you can run a visibility check:

```bash
export WEBSITE_ID="your-website-id-here"
export API_KEY="your-api-key-here"

curl -X POST "${API_URL}/v1/visibility/check" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d '{
    "website_id": "'"${WEBSITE_ID}"'",
    "queries": ["your business name", "your product"],
    "platforms": ["chatgpt", "perplexity"]
  }'
```

## Error Responses

### 404 Not Found
```json
{
  "error": "Website with ID abc-123 not found",
  "status_code": 404,
  "timestamp": "2025-10-18T16:00:00"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid or missing authentication credentials",
  "status_code": 401,
  "timestamp": "2025-10-18T16:00:00"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to create website: [error details]",
  "status_code": 500,
  "timestamp": "2025-10-18T16:00:00"
}
```

## Rate Limits

All endpoints have rate limiting:
- **POST**: 60 requests per minute
- **GET**: 60 requests per minute
- **PUT**: 60 requests per minute
- **DELETE**: 60 requests per minute

Rate limit headers are returned in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1697644800
```

## Notes

1. **POST /v1/websites** is idempotent - if domain exists, it returns the existing website
2. **POST /v1/websites** supports anonymous access for easy onboarding
3. **GET /v1/websites/{id}** and **GET /v1/websites** support optional authentication
4. **PUT** and **DELETE** require authentication
5. Domain is automatically extracted from URL and normalized (removes www., converts to lowercase)
6. CSRF protection is disabled for POST /v1/websites to support anonymous access
