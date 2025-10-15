---
sidebar_position: 1
title: Domain Verification
---

# Domain Verification

Before publishing content to IAIndex, you must verify ownership of your domain. This ensures authenticity and prevents impersonation.

## Why Domain Verification?

Domain verification:
- Proves you control the domain
- Prevents unauthorized publishers
- Establishes trust in the ecosystem
- Enables cryptographic attribution

## Verification Methods

### Method 1: DNS TXT Record (Recommended)

Add a TXT record to your DNS:

```bash
# Install IAIndex CLI
npm install -g @iaindex/cli

# Generate verification token
iaindex verify init yourdomain.com
```

Output:
```
Add this TXT record to your DNS:

Name: _iaindex-verification
Type: TXT
Value: iaindex-verification=abc123def456ghi789...
TTL: 3600
```

#### Add the DNS Record

**Using Cloudflare:**
1. Log into Cloudflare Dashboard
2. Select your domain
3. Go to DNS → Records
4. Click "Add record"
5. Type: TXT
6. Name: `_iaindex-verification`
7. Content: `iaindex-verification=abc123...`
8. TTL: Auto
9. Click "Save"

**Using AWS Route 53:**
```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "_iaindex-verification.yourdomain.com",
        "Type": "TXT",
        "TTL": 3600,
        "ResourceRecords": [{
          "Value": "\"iaindex-verification=abc123...\""
        }]
      }
    }]
  }'
```

#### Verify the Record

Wait 5-10 minutes for DNS propagation, then:

```bash
iaindex verify check yourdomain.com
```

Output:
```
✓ DNS record found
✓ Verification token matches
✓ Domain verified successfully!

Your verification ID: ver_xyz789...
```

### Method 2: HTTPS Well-Known File

Host a verification file at:
```
https://yourdomain.com/.well-known/iaindex-verification.txt
```

```bash
# Generate verification file
iaindex verify file yourdomain.com > verification.txt

# Upload to your web server
cp verification.txt /var/www/html/.well-known/iaindex-verification.txt
```

File content:
```
iaindex-verification=abc123def456ghi789...
domain=yourdomain.com
timestamp=2025-01-17T12:00:00Z
```

Verify:
```bash
iaindex verify check yourdomain.com --method=file
```

### Method 3: Meta Tag (Not Recommended)

Add to your homepage `<head>`:

```html
<meta name="iaindex-verification" content="abc123def456ghi789..." />
```

This method is less reliable as it requires scraping your homepage.

## Multi-Domain Verification

Verify multiple domains or subdomains:

```bash
# Main domain
iaindex verify init example.com

# Subdomain
iaindex verify init blog.example.com

# Multiple domains
iaindex verify init example.com,example.org,example.net
```

## Verification Status

Check verification status:

```bash
iaindex verify status yourdomain.com
```

Output:
```
Domain: yourdomain.com
Status: Verified
Method: DNS TXT
Verified At: 2025-01-17T12:00:00Z
Expires: 2026-01-17T12:00:00Z
Verification ID: ver_xyz789...
```

## Renewal and Expiration

Verifications expire after 1 year:

- **90 days before expiration**: Warning emails sent
- **30 days before**: Urgent warning
- **At expiration**: Domain marked as unverified

Renew verification:
```bash
iaindex verify renew yourdomain.com
```

## Troubleshooting

### DNS Record Not Found

```bash
# Check DNS propagation
dig TXT _iaindex-verification.yourdomain.com

# Or use online tools
# https://dnschecker.org
```

Common issues:
- DNS propagation delay (wait 5-30 minutes)
- Incorrect record name (must be `_iaindex-verification`)
- Missing quotes in TXT value
- Wrong DNS zone/subdomain

### File Not Accessible

```bash
# Test file accessibility
curl https://yourdomain.com/.well-known/iaindex-verification.txt
```

Common issues:
- File not in correct directory
- Web server blocking `.well-known` directory
- HTTPS not configured
- Incorrect file permissions

### Multiple Domain Errors

If verifying multiple domains:
- Each domain needs separate TXT record
- Subdomains inherit parent verification (optional)
- Use comma-separated list for bulk verification

## Security Considerations

1. **Protect Verification Tokens**: Treat as secrets
2. **Use HTTPS**: Always serve verification files over HTTPS
3. **Monitor Expiration**: Set up renewal reminders
4. **Revoke When Needed**: Revoke verification if domain sold
5. **Audit Regularly**: Review verified domains quarterly

## Programmatic Verification

Automate verification in your application:

```javascript
const { IAIndexPublisher } = require('@iaindex/sdk');

const publisher = new IAIndexPublisher({
  domain: 'yourdomain.com',
  privateKey: process.env.IAINDEX_PRIVATE_KEY
});

// Check verification status
const isVerified = await publisher.checkVerification();

if (!isVerified) {
  // Generate verification token
  const token = await publisher.generateVerificationToken();
  
  console.log('Add this DNS record:');
  console.log(`Name: _iaindex-verification`);
  console.log(`Type: TXT`);
  console.log(`Value: ${token}`);
  
  // Wait for user to add record
  // Then verify
  await publisher.verifyDomain();
}
```

## API Reference

### Generate Verification Token

```http
POST /api/v1/verification/generate
Content-Type: application/json

{
  "domain": "yourdomain.com",
  "method": "dns"
}
```

Response:
```json
{
  "token": "iaindex-verification=abc123...",
  "method": "dns",
  "record": {
    "name": "_iaindex-verification",
    "type": "TXT",
    "value": "iaindex-verification=abc123..."
  }
}
```

### Check Verification

```http
GET /api/v1/verification/check?domain=yourdomain.com
```

Response:
```json
{
  "verified": true,
  "domain": "yourdomain.com",
  "method": "dns",
  "verifiedAt": "2025-01-17T12:00:00Z",
  "expiresAt": "2026-01-17T12:00:00Z"
}
```

## Related Documentation

- [Generating Index Files](./generating-index.md)
- [Publishing Your First Entry](../quickstart.md)
- [API Authentication](../api/authentication.md)
