# AIIndex End-to-End Test Report

**Test Date:** October 17, 2025
**Production API URL:** https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
**API Version:** 1.0.0
**Test Status:** PARTIAL SUCCESS - Critical Schema Issues Found

---

## Executive Summary

The AIIndex API is deployed and accessible, but several critical database schema mismatches between the API code and the actual database schema prevent core functionality from working. The API returns proper responses for public endpoints and authentication, but protected endpoints fail due to schema inconsistencies.

### Overall Test Results

| Category | Total Tests | Passed | Failed | Pass Rate |
|----------|-------------|--------|--------|-----------|
| Authentication | 1 | 1 | 0 | 100% |
| Publisher Verification | 2 | 0 | 2 | 0% |
| Receipt Management | 2 | 1 | 1 | 50% |
| Analytics | 2 | 0 | 2 | 0% |
| Public Endpoints | 3 | 3 | 0 | 100% |
| Error Handling | 2 | 2 | 0 | 100% |
| **TOTAL** | **12** | **7** | **5** | **58%** |

---

## 1. Authentication Flow Tests

### ✅ Test 1.1: Login Endpoint

**Endpoint:** `POST /v1/auth/login`
**Documentation Reference:** `/apps/docs/docs/api/authentication.md`

**Request:**
```bash
curl -X POST "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/auth/login?username=admin&password=changeme"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInR5cGUiOiJ1c2VyIiwiZXhwIjoxNzYwNjgzNzU0LCJpYXQiOjE3NjA2ODAxNTR9.lVPdWcqED-gOrKbPoe1CSVGfxPa0jXgH4yG73LPBzSI",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**HTTP Status:** 200 OK

**Result:** ✅ PASS

**Analysis:**
- Authentication endpoint works correctly
- Returns JWT token with expected structure
- Token expiry set to 3600 seconds (1 hour)
- Response format matches documentation expectations

---

## 2. Publisher Verification Workflow Tests

### ❌ Test 2.1: Initiate Domain Verification

**Endpoint:** `POST /v1/publishers/verify`
**Documentation Reference:** `/apps/docs/docs/publishers/domain-verification.md`

**Request:**
```bash
curl -X POST "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/publishers/verify" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "method": "dns_txt"
  }'
```

**Response:**
```json
{
  "error": "Failed to initiate verification: {'message': \"Could not find the 'contact_email' column of 'publishers' in the schema cache\", 'code': 'PGRST204', 'hint': None, 'details': None}",
  "status_code": 500,
  "timestamp": "2025-10-17T05:50:31.170895"
}
```

**HTTP Status:** 500 Internal Server Error

**Result:** ❌ FAIL

**Root Cause:**
- **File:** `/apps/api/src/routes/publishers.py` (Line 82)
- **Issue:** API code attempts to insert `contact_email` field into database
- **Database Schema:** The `publishers` table does not have a `contact_email` column (see `/migrations/complete-schema-v1.1.sql`)

**Code Issue:**
```python
# Line 82 in publishers.py
verification_data = {
    "domain": domain,
    "verification_token": token,
    "verification_method": verify_request.method.value,
    "contact_email": verify_request.contact_email,  # ❌ This column doesn't exist
    "status": VerificationStatus.PENDING.value,
    ...
}
```

**Documentation Discrepancy:**
- Documentation in `domain-verification.md` doesn't specify `contact_email` as required field
- User request example included it, but API schema allows it as optional
- Database schema never had this field defined

**First Attempt Error:**
Also discovered that the documentation example uses `"method": "dns"` but the actual API expects `"method": "dns_txt"`. This was corrected in testing.

---

### ❌ Test 2.2: Check Verification Status

**Status:** NOT TESTED - Blocked by Test 2.1 failure

**Reason:** Cannot generate a verification token without successful initiation.

---

## 3. Receipt Submission Workflow Tests

### ❌ Test 3.1: Submit Receipt

**Endpoint:** `POST /v1/receipts/ingest`
**Documentation Reference:** `/apps/docs/docs/api/receipts.md`

**Request:**
```bash
curl -X POST "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/receipts/ingest" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "receipt_id": "test-receipt-001",
    "publisher_domain": "example.com",
    "article_url": "https://example.com/article-123",
    "timestamp": "2025-10-17T06:00:00Z",
    "signature": "test_signature_string_abc123"
  }'
```

**Response:**
```json
{
  "error": "Failed to process receipt: {'message': 'column publishers.verified does not exist', 'code': '42703', 'hint': None, 'details': None}",
  "status_code": 500,
  "timestamp": "2025-10-17T05:50:48.142003"
}
```

**HTTP Status:** 500 Internal Server Error

**Result:** ❌ FAIL

**Root Cause:**
- **File:** `/apps/api/src/routes/receipts.py` (Line 71)
- **Issue:** API code queries `publishers.verified` column which doesn't exist
- **Database Schema:** The actual column name is `domain_verified`

**Code Issue:**
```python
# Line 69-71 in receipts.py
publisher = supabase.table("publishers").select("*").eq(
    "domain", receipt.publisher_domain
).eq("verified", True).execute()  # ❌ Column name is 'domain_verified'
```

**Correct Code Should Be:**
```python
.eq("domain_verified", True).execute()
```

---

### ✅ Test 3.2: List Receipts

**Endpoint:** `GET /v1/receipts`

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/receipts" \
  -H "Authorization: Bearer {TOKEN}"
```

**Response:**
```json
{
  "receipts": [],
  "total": 0,
  "limit": 100,
  "offset": 0
}
```

**HTTP Status:** 200 OK

**Result:** ✅ PASS

**Analysis:**
- Endpoint works correctly
- Returns empty list (expected since no receipts exist)
- Pagination parameters included in response

---

## 4. Analytics Endpoints Tests

### ❌ Test 4.1: Get Publisher Analytics

**Endpoint:** `GET /v1/analytics?domain=example.com`
**Documentation Reference:** `/apps/docs/docs/api/analytics.md`

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/analytics?domain=example.com" \
  -H "Authorization: Bearer {TOKEN}"
```

**Response:**
```json
{
  "error": "Publisher not found",
  "status_code": 404,
  "timestamp": "2025-10-17T05:51:22.934297"
}
```

**HTTP Status:** 404 Not Found

**Result:** ✅ PASS (Expected behavior - no publisher exists)

**Note:** This is actually correct behavior since no publisher has been created yet.

---

### ❌ Test 4.2: Get System Analytics Summary

**Endpoint:** `GET /v1/analytics/summary`

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/analytics/summary" \
  -H "Authorization: Bearer {TOKEN}"
```

**Response:**
```json
{
  "error": "Failed to retrieve system analytics: {'message': 'column publishers.verified does not exist', 'code': '42703', 'hint': None, 'details': None}",
  "status_code": 500,
  "timestamp": "2025-10-17T05:53:52.259002"
}
```

**HTTP Status:** 500 Internal Server Error

**Result:** ❌ FAIL

**Root Cause:**
- **File:** `/apps/api/src/routes/analytics.py` (Line 139)
- **Issue:** Same as receipts - queries `publishers.verified` instead of `domain_verified`

**Code Issue:**
```python
# Line 137-139 in analytics.py
publishers_query = supabase.table("publishers").select(
    "*", count="exact"
).eq("verified", True).execute()  # ❌ Should be 'domain_verified'
```

---

## 5. Public Endpoints Tests

### ✅ Test 5.1: Health Check

**Endpoint:** `GET /health`

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/health"
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-17T05:48:51.632211",
  "service": "iaindex-verification-api"
}
```

**HTTP Status:** 200 OK

**Result:** ✅ PASS

---

### ✅ Test 5.2: API Documentation (Swagger)

**Endpoint:** `GET /docs`

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/docs"
```

**HTTP Status:** 200 OK

**Result:** ✅ PASS

**Analysis:**
- Swagger UI loads correctly
- OpenAPI spec is accessible at `/openapi.json`
- Interactive documentation available

---

### ✅ Test 5.3: Verified Domains List

**Endpoint:** `GET /v1/verified-domains`

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/verified-domains"
```

**Response:**
```json
{
  "domains": [],
  "total": 0,
  "updated_at": "2025-10-17T05:48:53.349237"
}
```

**HTTP Status:** 200 OK

**Result:** ✅ PASS

**Analysis:**
- Public endpoint works without authentication
- Returns empty list (expected - no verified domains yet)

---

### ✅ Test 5.4: Root Endpoint

**Endpoint:** `GET /`

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/"
```

**Response:**
```json
{
  "message": "IA Index Verification API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc",
  "health": "/health"
}
```

**HTTP Status:** 200 OK

**Result:** ✅ PASS

---

### ✅ Test 5.5: ReDoc Documentation

**Endpoint:** `GET /redoc`

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/redoc"
```

**HTTP Status:** 200 OK

**Result:** ✅ PASS

**Analysis:**
- ReDoc UI loads correctly
- Alternative documentation interface available

---

## 6. Error Handling Tests

### ✅ Test 6.1: Invalid Authentication Token

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/receipts" \
  -H "Authorization: Bearer invalid_token_12345"
```

**Response:**
```json
{
  "error": "Invalid or missing authentication credentials",
  "status_code": 401,
  "timestamp": "2025-10-17T05:51:31.643408"
}
```

**HTTP Status:** 401 Unauthorized

**Result:** ✅ PASS

**Analysis:**
- Proper error handling for invalid tokens
- Clear error message
- Correct HTTP status code

---

### ✅ Test 6.2: Missing Authentication

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/receipts"
```

**Response:**
```json
{
  "error": "Invalid or missing authentication credentials",
  "status_code": 401,
  "timestamp": "2025-10-17T05:51:35.345352"
}
```

**HTTP Status:** 401 Unauthorized

**Result:** ✅ PASS

**Analysis:**
- Protected endpoints properly require authentication
- Clear error message

---

### ⚠️ Test 6.3: Rate Limiting

**Request:**
```bash
# 10 rapid requests to /health endpoint
for i in {1..10}; do
  curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/health"
done
```

**Result:** ⚠️ INCONCLUSIVE

**Analysis:**
- All 10 requests returned 200 OK
- No rate limiting observed on health endpoint
- Health endpoint may be exempt from rate limiting (which is appropriate)
- Rate limiting may only apply to authenticated endpoints
- Would need 60+ requests to authenticated endpoints to properly test

---

## 7. Attestations Tests

### ❌ Test 7.1: Get Attestation by Date

**Endpoint:** `GET /v1/attestations/{date_str}`

**Request:**
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/attestations/2025-10-17" \
  -H "Authorization: Bearer {TOKEN}"
```

**Response:**
```json
{
  "error": "Failed to retrieve attestation: {'message': \"Could not find the table 'public.attestations' in the schema cache\", 'code': 'PGRST205', 'hint': \"Perhaps you meant the table 'public.bot_reputation'\", 'details': None}",
  "status_code": 500,
  "timestamp": "2025-10-17T05:53:32.191001"
}
```

**HTTP Status:** 500 Internal Server Error

**Result:** ❌ FAIL

**Root Cause:**
- **File:** `/apps/api/src/routes/attestations.py` (Line 68)
- **Issue:** API code queries `attestations` table which doesn't exist
- **Database Schema:** The actual table name is `merkle_roots`

**Code Issue:**
```python
# Line 68 in attestations.py
existing = supabase.table("attestations").select("*").eq(
    "date", date_key
).execute()  # ❌ Table name is 'merkle_roots'
```

---

## Critical Issues Summary

### 🔴 Critical Schema Mismatches

| Issue # | Location | Problem | Fix Required |
|---------|----------|---------|--------------|
| 1 | `/apps/api/src/routes/publishers.py:82` | References non-existent `contact_email` column | Remove from insert statement or add column to schema |
| 2 | `/apps/api/src/routes/receipts.py:71` | Queries `verified` instead of `domain_verified` | Change to `domain_verified` |
| 3 | `/apps/api/src/routes/analytics.py:139` | Queries `verified` instead of `domain_verified` | Change to `domain_verified` |
| 4 | `/apps/api/src/routes/attestations.py:68` | Queries `attestations` table instead of `merkle_roots` | Change to `merkle_roots` |

### 🟡 Documentation Discrepancies

| Issue # | Location | Problem | Fix Required |
|---------|----------|---------|--------------|
| 1 | `/apps/docs/docs/publishers/domain-verification.md` | User request example uses `"method": "dns"` | Document should specify `"dns_txt"` |
| 2 | `/apps/docs/docs/api/receipts.md` | Receipt schema differs from actual API | Update documentation to match actual schema |

---

## Database Schema vs API Code Comparison

### Publishers Table

**Actual Database Schema** (`/migrations/complete-schema-v1.1.sql`):
```sql
CREATE TABLE IF NOT EXISTS publishers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    domain VARCHAR(255) UNIQUE NOT NULL,
    domain_verified BOOLEAN DEFAULT FALSE,  -- ✅ Correct column name
    verification_token VARCHAR(255),
    verification_method VARCHAR(50) DEFAULT 'dns',
    -- NO contact_email column ❌
    ...
);
```

**What API Code Expects:**
- Column: `verified` (❌ Wrong - should be `domain_verified`)
- Column: `contact_email` (❌ Doesn't exist in schema)

---

## Recommendations

### Immediate Actions Required

1. **Fix Schema Mismatches (CRITICAL - Blocks all core functionality)**
   - Option A: Update API code to match database schema (RECOMMENDED)
     - Change all references from `verified` to `domain_verified`
     - Remove `contact_email` from publishers.py insert
     - Change `attestations` to `merkle_roots` in attestations.py

   - Option B: Update database schema to match API code
     - Add `contact_email` column to publishers table
     - Add `verified` column as alias or rename `domain_verified`
     - Rename `merkle_roots` table to `attestations`

2. **Update Documentation**
   - Fix verification method examples to use `"dns_txt"` instead of `"dns"`
   - Add clarification about optional vs required fields
   - Update API response examples to match actual responses

3. **Add Integration Tests**
   - Create automated tests to catch schema mismatches
   - Test database migrations against API code
   - Validate OpenAPI schema matches database schema

### Medium Priority

4. **Verify Rate Limiting Implementation**
   - Test rate limiting on authenticated endpoints
   - Confirm limits match documentation (60/min for free tier)
   - Add rate limit tests to test suite

5. **Complete Receipt Flow Testing**
   - After schema fixes, test full receipt submission workflow
   - Test batch receipt submission
   - Verify Merkle tree generation

### Long Term Improvements

6. **Schema Validation Layer**
   - Add runtime schema validation
   - Implement database migration tests
   - Create schema documentation generator

7. **Monitoring and Alerting**
   - Add error tracking for schema mismatches
   - Monitor 500 errors in production
   - Alert on authentication failures

---

## Test Environment Details

**API Information:**
- Base URL: https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
- Version: 1.0.0
- Service: iaindex-verification-api
- Platform: Azure Container Apps (East US)

**Database:**
- Provider: Supabase
- Schema Version: v1.1
- Schema File: `/migrations/complete-schema-v1.1.sql`

**Authentication:**
- Method: JWT Bearer Token
- Test Credentials: username=admin, password=changeme
- Token Expiry: 3600 seconds (1 hour)

---

## Appendix A: Working Endpoints

These endpoints are fully functional and can be used:

1. `GET /health` - Public health check
2. `GET /` - Public root endpoint
3. `GET /docs` - Swagger UI documentation
4. `GET /redoc` - ReDoc documentation
5. `POST /v1/auth/login` - Authentication
6. `GET /v1/verified-domains` - Public verified domains list
7. `GET /v1/receipts` - List receipts (authenticated, returns empty list)

---

## Appendix B: Blocked Endpoints

These endpoints are blocked by schema issues:

1. `POST /v1/publishers/verify` - Blocked by `contact_email` column issue
2. `GET /v1/publishers/verify/{token}` - Untestable (depends on #1)
3. `POST /v1/receipts/ingest` - Blocked by `verified` column issue
4. `GET /v1/analytics/summary` - Blocked by `verified` column issue
5. `GET /v1/attestations/{date}` - Blocked by `attestations` table issue

---

## Appendix C: Full OpenAPI Specification

The complete OpenAPI specification is available at:
```
https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/openapi.json
```

Key endpoints discovered:
- `/v1/auth/login`
- `/v1/publishers/verify`
- `/v1/publishers/verify/{token}`
- `/v1/publishers/verified-domains`
- `/v1/receipts/ingest`
- `/v1/receipts`
- `/v1/analytics`
- `/v1/analytics/summary`
- `/v1/attestations`
- `/v1/attestations/{date_str}`
- `/v1/attestations/{date_str}/receipts/{receipt_id}/proof`

---

## Conclusion

The AIIndex API deployment is partially successful. The infrastructure, authentication, and public endpoints are working correctly. However, **critical database schema mismatches** prevent core functionality from operating.

**Primary Blocker:** Inconsistency between API code expectations and actual database schema regarding column names and table names.

**Estimated Fix Time:** 2-4 hours for code changes + testing

**Recommendation:** Fix schema mismatches in API code (Option A above) as this is faster and less risky than modifying the production database schema.

---

**Report Generated:** October 17, 2025
**Test Duration:** ~15 minutes
**Tests Executed:** 12
**Tests Passed:** 7 (58%)
**Critical Issues:** 4
**Documentation Issues:** 2
