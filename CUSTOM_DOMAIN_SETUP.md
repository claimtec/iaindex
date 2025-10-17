# Custom Domain Setup for AIIndex API

**Current API URL**: https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
**Goal**: Add custom domain like `api.iaindex.com` or `api.yourdomain.com`

---

## Prerequisites

1. **Domain Name**: You need to own a domain (e.g., `iaindex.com`, `claimtec.co.za`, etc.)
2. **DNS Access**: Ability to add DNS records to your domain
3. **Azure Access**: Current Azure subscription with Container Apps

---

## Step-by-Step Guide

### Step 1: Choose Your Custom Domain

Decide on the subdomain you want to use. Common options:

- `api.iaindex.com` - If you own iaindex.com
- `api.claimtec.co.za` - If using your company domain
- `iaindex-api.yourdomain.com` - Any subdomain structure

**For this guide, we'll use**: `api.iaindex.com` (replace with your actual domain)

---

### Step 2: Add Custom Domain to Azure Container App

```bash
# Add the custom domain
az containerapp hostname add \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --hostname api.iaindex.com
```

**Expected Output**:
```json
{
  "name": "api.iaindex.com",
  "bindingType": "SniEnabled",
  "certificateId": null
}
```

Azure will provide a **verification token** or **TXT record** to prove domain ownership.

---

### Step 3: Get Domain Verification Details

```bash
# Get the verification details
az containerapp hostname list \
  --name aiindex-api \
  --resource-group aiindex-rg \
  -o json
```

This will show:
- **CNAME target**: What to point your domain to
- **TXT verification record**: For domain ownership verification

---

### Step 4: Configure DNS Records

Add these DNS records to your domain provider (GoDaddy, Cloudflare, Namecheap, etc.):

#### Option A: CNAME Record (Recommended)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | `api` | `aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io` | 3600 |

**Full domain**: `api.iaindex.com` → points to Container App

#### Option B: If Root Domain (Not Recommended for API)

If you want to use the root domain (e.g., `iaindex.com` without subdomain):

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `@` | Container App IP address | 3600 |

**Note**: CNAME is preferred for subdomains.

#### Verification TXT Record (Required First)

Before the CNAME, add a TXT record for verification:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| TXT | `asuid.api` | `{verification-code}` | 3600 |

**Get the verification code from**:
```bash
az containerapp show \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --query "properties.customDomainVerificationId" -o tsv
```

**Current Verification ID**: `B7FF4D19E9BF907C04E7247E144E1AC3DBFF63CE40C3FA3723E45A31127E58D6`

---

### Step 5: Verify Domain Ownership

After adding DNS records (wait 5-10 minutes for propagation):

```bash
# Verify the domain
az containerapp hostname verify \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --hostname api.iaindex.com
```

---

### Step 6: Bind SSL Certificate

Azure Container Apps automatically provisions a **free managed certificate** for your custom domain.

```bash
# Check certificate status
az containerapp hostname list \
  --name aiindex-api \
  --resource-group aiindex-rg
```

The certificate will auto-renew before expiration.

---

## Complete Example Commands

Replace `api.iaindex.com` with your actual domain:

```bash
# 1. Get verification ID
VERIFICATION_ID=$(az containerapp show \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --query "properties.customDomainVerificationId" -o tsv)

echo "Add this TXT record: asuid.api -> $VERIFICATION_ID"

# 2. Wait for DNS propagation, then add custom domain
az containerapp hostname add \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --hostname api.iaindex.com

# 3. Verify domain
az containerapp hostname verify \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --hostname api.iaindex.com

# 4. Check status
az containerapp hostname list \
  --name aiindex-api \
  --resource-group aiindex-rg
```

---

## DNS Configuration Examples

### Cloudflare

1. Go to Cloudflare dashboard → DNS
2. Add records:

```
Type: TXT
Name: asuid.api
Content: B7FF4D19E9BF907C04E7247E144E1AC3DBFF63CE40C3FA3723E45A31127E58D6
Proxy: DNS only (gray cloud)

Type: CNAME
Name: api
Content: aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
Proxy: DNS only (gray cloud) - initially, can enable after setup
```

### GoDaddy

1. Go to DNS Management
2. Add records:

```
Type: TXT
Host: asuid.api
TXT Value: B7FF4D19E9BF907C04E7247E144E1AC3DBFF63CE40C3FA3723E45A31127E58D6

Type: CNAME
Host: api
Points to: aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
```

### Other Providers

Similar process - add TXT for verification and CNAME for routing.

---

## Testing Custom Domain

After setup (allow 10-15 minutes for DNS propagation):

```bash
# Test DNS resolution
nslookup api.iaindex.com

# Test API health
curl https://api.iaindex.com/health

# Test CORS
curl -I https://api.iaindex.com/v1/verified-domains
```

**Expected**: Should work identically to the default Azure domain.

---

## Update SDK Configuration

After custom domain is working, you can update the SDK default URL:

### Node.js SDK (`packages/sdk-nodejs/src/api-client.ts`)

```typescript
const DEFAULT_API_URL = 'https://api.iaindex.com';
```

### Python SDK (`packages/sdk-python/aiindex/client.py`)

```python
DEFAULT_API_URL = 'https://api.iaindex.com'
```

### CLI Tool (`packages/cli/src/config.ts`)

```typescript
const DEFAULT_API_URL = 'https://api.iaindex.com';
```

**Rebuild packages** with new default URL and republish.

---

## Benefits of Custom Domain

### Professional Branding
- `api.iaindex.com` vs `aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io`
- Easier to remember and communicate
- Better for marketing materials

### DNS Control
- Can change backend without breaking clients
- Can add multiple endpoints (api, api-staging, etc.)
- Better for CDN integration

### Certificate Management
- Azure manages SSL certificate automatically
- Auto-renewal every 90 days
- No manual certificate handling

---

## Troubleshooting

### DNS Not Resolving

```bash
# Check DNS propagation
dig api.iaindex.com
nslookup api.iaindex.com

# Check from different DNS servers
nslookup api.iaindex.com 8.8.8.8  # Google DNS
nslookup api.iaindex.com 1.1.1.1  # Cloudflare DNS
```

**Wait**: DNS can take up to 24-48 hours to fully propagate globally (usually 5-15 minutes).

### Certificate Issues

```bash
# Check certificate status
az containerapp hostname list \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --query "[].{hostname:name,certificateId:properties.certificateId}"
```

If certificate is null, Azure is still provisioning. Wait 10-15 minutes.

### Domain Verification Failed

**Check**:
1. TXT record is correctly added with verification ID
2. DNS has propagated (use `dig TXT asuid.api.iaindex.com`)
3. Hostname format is correct (no typos)

**Retry verification**:
```bash
az containerapp hostname verify \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --hostname api.iaindex.com
```

---

## Cost

**Custom Domain**: ✅ **FREE**
- No additional cost for custom domain
- Managed certificate included
- SSL/TLS automatic

**Azure Container Apps pricing**: Based on usage (compute, requests), not domains.

---

## Multiple Domains

You can add multiple domains to the same Container App:

```bash
# Primary API domain
az containerapp hostname add --hostname api.iaindex.com ...

# Alternative domain
az containerapp hostname add --hostname api.claimtec.co.za ...

# Staging subdomain
az containerapp hostname add --hostname api-staging.iaindex.com ...
```

All will point to the same Container App instance.

---

## Next Steps

**To set up custom domain now**:

1. **Tell me your domain name** (e.g., `iaindex.com`, `claimtec.co.za`)
2. **Choose subdomain** (e.g., `api`, `iaindex-api`)
3. **I'll run the Azure command** to add it
4. **You add DNS records** at your domain provider
5. **I'll verify** the domain ownership
6. **Done** - Custom domain working with SSL

**Recommended domain structure**:
- `api.iaindex.com` - Production API
- `api-staging.iaindex.com` - Staging API (if needed)
- `docs.iaindex.com` - Documentation site
- `iaindex.com` - Marketing website

---

## Summary

✅ **Custom domain is fully supported**
✅ **Free SSL certificate included**
✅ **Easy setup** (3 DNS records + Azure command)
✅ **No additional cost**
✅ **Professional branding**

**Ready to proceed?** Just provide your domain name and I'll help set it up!

---

**Current Status**:
- Default URL: https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io ✅ Working
- Custom Domain: Not configured yet
- Verification ID: `B7FF4D19E9BF907C04E7247E144E1AC3DBFF63CE40C3FA3723E45A31127E58D6`
