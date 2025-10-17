# Schema Fixes Applied - October 17, 2025

## Overview

Fixed 4 critical database schema mismatches discovered during end-to-end testing that were blocking key API workflows.

---

## Issues Fixed

### 1. ✅ Contact Email Column Mismatch (publishers.py)

**Location:** `/apps/api/src/routes/publishers.py` line 82

**Issue:** Code tried to insert `contact_email` field that doesn't exist in the `publishers` table

**Error:**
```
Could not find the 'contact_email' column of the 'publishers' relation
```

**Fix:** Removed `"contact_email": verify_request.contact_email` from verification_data dict

**Files Changed:**
- `apps/api/src/routes/publishers.py`

---

### 2. ✅ Verified Column Mismatch (receipts.py)

**Location:** `/apps/api/src/routes/receipts.py` line 71

**Issue:** Code queried `verified` column but actual column name is `domain_verified`

**Error:**
```
column publishers.verified does not exist
```

**Fix:** Changed `.eq("verified", True)` to `.eq("domain_verified", True)`

**Files Changed:**
- `apps/api/src/routes/receipts.py`

---

### 3. ✅ Verified Column Mismatch (analytics.py)

**Location:** `/apps/api/src/routes/analytics.py` line 139

**Issue:** Same as receipts.py - queried `verified` instead of `domain_verified`

**Error:**
```
column publishers.verified does not exist
```

**Fix:** Changed `.eq("verified", True)` to `.eq("domain_verified", True)`

**Files Changed:**
- `apps/api/src/routes/analytics.py`

---

### 4. ✅ Attestations Table Mismatch (attestations.py)

**Location:** `/apps/api/src/routes/attestations.py` lines 68, 130, 273

**Issue:** Code referenced `attestations` table but actual table name is `merkle_roots`

**Error:**
```
relation "attestations" does not exist
```

**Fix:** Changed all references from `"attestations"` to `"merkle_roots"`

**Lines Changed:**
- Line 68: `supabase.table("attestations")` → `supabase.table("merkle_roots")`
- Line 130: `supabase.table("attestations")` → `supabase.table("merkle_roots")`
- Line 273: `supabase.table("attestations")` → `supabase.table("merkle_roots")`

**Files Changed:**
- `apps/api/src/routes/attestations.py`

---

## Root Cause Analysis

These mismatches occurred because:

1. **Schema Evolution:** The database schema evolved during development but code wasn't fully updated
2. **Naming Conventions:** Inconsistent naming between `verified` vs `domain_verified`
3. **Table Rename:** `attestations` table was renamed to `merkle_roots` to better reflect its purpose
4. **Incomplete Migration:** The v1.0-to-v1.1 migration removed some fields that code still referenced

---

## Testing Results

### Before Fixes
- **Pass Rate:** 58% (7/12 tests)
- **Blocked Workflows:**
  - Publisher verification
  - Receipt submission
  - Analytics summary
  - Attestation creation/retrieval

### After Fixes (Expected)
- **Pass Rate:** 92% (11/12 tests)
- **Unblocked Workflows:**
  - ✅ Publisher verification
  - ✅ Receipt submission
  - ✅ Analytics summary
  - ✅ Attestation operations

---

## Deployment

### Build Image
```bash
az acr build \
  --registry cafc3cb1336eacr \
  --resource-group aiindex-rg \
  --image aiindex-api:schema-fixes \
  --image aiindex-api:latest \
  --file apps/api/Dockerfile \
  apps/api
```

### Update Container
```bash
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --image cafc3cb1336eacr.azurecr.io/aiindex-api:latest
```

### Restart
```bash
REVISION=$(az containerapp show --name aiindex-api --resource-group aiindex-rg --query "properties.latestRevisionName" -o tsv)
az containerapp revision restart \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --revision "$REVISION"
```

---

## Verification Commands

### Test Publisher Verification
```bash
TOKEN=$(curl -X POST "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/auth/login" \
  -d "username=admin&password=changeme" | jq -r .access_token)

curl -X POST "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/publishers/verify" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "method": "dns_txt",
    "contact_email": "admin@example.com"
  }'
```

### Test Receipt Submission
```bash
curl -X POST "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/receipts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "publisher_domain": "example.com",
    "content_id": "article-123",
    "content_url": "https://example.com/article-123",
    "client_id": "test-bot-001",
    "timestamp": "2025-10-17T06:00:00Z",
    "usage_type": "training",
    "signature": "test_signature"
  }'
```

### Test Analytics
```bash
curl "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/v1/analytics/summary" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Prevention Measures

To prevent similar issues in the future:

### 1. Schema Documentation
- **Action:** Keep database schema documented in code comments
- **Location:** Add schema comments at top of each route file

### 2. Type Safety
- **Action:** Use Pydantic models that match database schema
- **Benefit:** Catch mismatches at development time

### 3. Integration Tests
- **Action:** Add tests that verify API works with actual database
- **Benefit:** Catch schema mismatches before deployment

### 4. Schema Validation
- **Action:** Run schema validation script before deployment
- **Script:**
```python
# scripts/validate-schema.py
def validate_schema():
    """Compare code column references with actual database schema"""
    # Check all .eq(), .select(), .insert() calls
    # Verify columns exist in database
    pass
```

---

## Related Documentation

- [End-to-End Test Report](./END_TO_END_TEST_REPORT.md) - Full test results
- [Database Schema](./migrations/complete-schema-v1.1.sql) - Current schema
- [API Routes](./apps/api/src/routes/) - Fixed route files

---

## Summary

All 4 schema mismatches have been fixed and deployed. The API should now work correctly for:
- ✅ Publisher domain verification
- ✅ Receipt submission and validation
- ✅ Analytics and reporting
- ✅ Merkle tree attestations

**Status:** Ready for retesting
