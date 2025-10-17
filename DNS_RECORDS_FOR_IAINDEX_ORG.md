# DNS Records for iaindex.org

## Records to Add to Your DNS Provider

Add these **TWO** records to `iaindex.org` DNS management:

---

## Record 1: TXT Record (Verification)

This proves you own the domain.

| Field | Value |
|-------|-------|
| **Record Type** | `TXT` |
| **Hostname** | `asuid.api` |
| **Destination/Value** | `B7FF4D19E9BF907C04E7247E144E1AC3DBFF63CE40C3FA3723E45A31127E58D6` |
| **TTL** | `3600` (or default) |

**Full domain created**: `asuid.api.iaindex.org`

---

## Record 2: CNAME Record (Routing)

This points your API domain to Azure Container Apps.

| Field | Value |
|-------|-------|
| **Record Type** | `CNAME` |
| **Hostname** | `api` |
| **Destination/Value** | `aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io` |
| **TTL** | `3600` (or default) |

**Full domain created**: `api.iaindex.org`

---

## Visual Guide

### Your DNS Panel Should Look Like This:

```
TXT Records:
Hostname                TTL     Record Type    Destination
asuid.api               3600    TXT           B7FF4D19E9BF907C04E7247E144E1AC3DBFF63CE40C3FA3723E45A31127E58D6

CNAME Records:
Hostname    TTL     Record Type    Destination
api         3600    CNAME         aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
```

---

## Step-by-Step Instructions

### Step 1: Add TXT Record

1. Click **"Add Record"** in your DNS panel
2. Select **Record Type: TXT**
3. **Hostname**: `asuid.api`
4. **Destination/Value**: `B7FF4D19E9BF907C04E7247E144E1AC3DBFF63CE40C3FA3723E45A31127E58D6`
5. **TTL**: `3600` (or leave default)
6. **Save**

### Step 2: Add CNAME Record

1. Click **"Add Record"** in your DNS panel
2. Select **Record Type: CNAME**
3. **Hostname**: `api`
4. **Destination/Value**: `aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io`
5. **TTL**: `3600` (or leave default)
6. **Save**

---

## Important Notes

### About the TXT Record

- **Purpose**: Proves domain ownership to Azure
- **Hostname**: Must be exactly `asuid.api` (not `asuid.api.iaindex.org`)
- **Temporary**: Can be removed after verification (but safe to keep)

### About the CNAME Record

- **Purpose**: Routes `api.iaindex.org` to your Azure Container App
- **Hostname**: Must be exactly `api` (not `api.iaindex.org`)
- **Permanent**: Keep this record for the API to work

### DNS Propagation

- **Typical Time**: 5-15 minutes
- **Maximum Time**: Up to 24-48 hours
- **Check Status**: Use `nslookup api.iaindex.org` or online DNS checkers

---

## After Adding Records

### Verification Test Commands

Wait 5-10 minutes after adding records, then test:

```bash
# Test TXT record
nslookup -type=TXT asuid.api.iaindex.org

# Expected output should contain:
# B7FF4D19E9BF907C04E7247E144E1AC3DBFF63CE40C3FA3723E45A31127E58D6

# Test CNAME record
nslookup api.iaindex.org

# Expected output should show:
# api.iaindex.org canonical name = aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
```

### Once DNS is Propagated

**Let me know when you've added the records**, and I'll:
1. Verify the domain in Azure
2. Bind the SSL certificate
3. Test the custom domain
4. Update SDK packages with new URL

---

## Quick Copy-Paste Values

### TXT Record Value:
```
B7FF4D19E9BF907C04E7247E144E1AC3DBFF63CE40C3FA3723E45A31127E58D6
```

### CNAME Record Value:
```
aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
```

---

## What Happens Next?

1. ✅ **You add DNS records** (TXT + CNAME)
2. ⏳ **DNS propagates** (5-15 minutes)
3. ✅ **I verify in Azure** (1 command)
4. ✅ **Azure provisions SSL certificate** (automatic, 10-15 minutes)
5. ✅ **Custom domain live**: `https://api.iaindex.org`

---

## Final Result

After setup:
- ✅ `https://api.iaindex.org/health` - Your professional API endpoint
- ✅ `https://api.iaindex.org/docs` - API documentation
- ✅ `https://api.iaindex.org/v1/*` - All API endpoints
- ✅ Free SSL certificate (auto-renewing)
- ✅ Same functionality as Azure default URL

**Old URL** (still works): `https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io`
**New URL** (after setup): `https://api.iaindex.org` ✨

---

**Status**: Waiting for DNS records to be added
**Action**: Add the 2 records above, then let me know!
