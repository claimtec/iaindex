---
sidebar_position: 2
title: Quick Start Guide
---

# Quick Start Guide

Get up and running with IAIndex in under 5 minutes. This guide will walk you through setting up your first IAIndex integration.

## Prerequisites

Before you begin, ensure you have:

- A domain you control
- Node.js 18+ or Python 3.8+ installed
- Basic understanding of REST APIs
- A text editor or IDE

## Step 1: Domain Verification

First, verify you own your domain by adding a TXT record to your DNS:

```bash
# Install the IAIndex CLI
npm install -g @iaindex/cli

# Generate verification token
iaindex verify init yourdomain.com
```

This will output a DNS TXT record like:

```
iaindex-verification=abc123def456...
```

Add this to your domain's DNS records, then verify:

```bash
iaindex verify check yourdomain.com
```

## Step 2: Install the SDK

Choose your preferred language:

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="nodejs" label="Node.js" default>

```bash
npm install @iaindex/sdk
```

</TabItem>
<TabItem value="python" label="Python">

```bash
pip install iaindex-sdk
```

</TabItem>
</Tabs>

## Step 3: Initialize Your Publisher Profile

Create a publisher configuration:

<Tabs>
<TabItem value="nodejs" label="Node.js" default>

```javascript
const { IAIndexPublisher } = require('@iaindex/sdk');

const publisher = new IAIndexPublisher({
  domain: 'yourdomain.com',
  privateKey: process.env.IAINDEX_PRIVATE_KEY,
  name: 'Your Publication Name',
  contact: 'contact@yourdomain.com'
});

await publisher.initialize();
```

</TabItem>
<TabItem value="python" label="Python">

```python
from iaindex import IAIndexPublisher

publisher = IAIndexPublisher(
    domain='yourdomain.com',
    private_key=os.environ['IAINDEX_PRIVATE_KEY'],
    name='Your Publication Name',
    contact='contact@yourdomain.com'
)

publisher.initialize()
```

</TabItem>
</Tabs>

## Step 4: Create Your First Index Entry

Add content to the IAIndex:

<Tabs>
<TabItem value="nodejs" label="Node.js" default>

```javascript
const entry = await publisher.createEntry({
  url: 'https://yourdomain.com/article-1',
  title: 'Your Article Title',
  author: 'Author Name',
  publishedDate: '2025-01-15T10:00:00Z',
  content: 'Article content or summary...',
  license: {
    type: 'CC-BY-4.0',
    terms: 'https://creativecommons.org/licenses/by/4.0/'
  }
});

console.log('Entry created:', entry.id);
```

</TabItem>
<TabItem value="python" label="Python">

```python
entry = publisher.create_entry(
    url='https://yourdomain.com/article-1',
    title='Your Article Title',
    author='Author Name',
    published_date='2025-01-15T10:00:00Z',
    content='Article content or summary...',
    license={
        'type': 'CC-BY-4.0',
        'terms': 'https://creativecommons.org/licenses/by/4.0/'
    }
)

print(f'Entry created: {entry.id}')
```

</TabItem>
</Tabs>

## Step 5: Publish Your Index

Publish your index file to make it discoverable:

<Tabs>
<TabItem value="nodejs" label="Node.js" default>

```javascript
// Generate and sign the index
await publisher.generateIndex();

// The index will be saved to ./iaindex.json
// Host this file at: https://yourdomain.com/.well-known/iaindex.json
```

</TabItem>
<TabItem value="python" label="Python">

```python
# Generate and sign the index
publisher.generate_index()

# The index will be saved to ./iaindex.json
# Host this file at: https://yourdomain.com/.well-known/iaindex.json
```

</TabItem>
</Tabs>

## Step 6: Host the Index File

Upload the generated `iaindex.json` file to your web server at:

```
https://yourdomain.com/.well-known/iaindex.json
```

Ensure it's accessible via HTTPS and returns proper CORS headers:

```
Access-Control-Allow-Origin: *
Content-Type: application/json
```

## Step 7: Receive Receipts

Set up a webhook endpoint to receive usage receipts:

<Tabs>
<TabItem value="nodejs" label="Node.js" default>

```javascript
const express = require('express');
const app = express();

app.post('/webhooks/iaindex/receipt', async (req, res) => {
  const receipt = req.body;
  
  // Verify the receipt signature
  const isValid = await publisher.verifyReceipt(receipt);
  
  if (isValid) {
    console.log('Valid receipt received:', {
      contentId: receipt.contentId,
      clientId: receipt.clientId,
      timestamp: receipt.timestamp
    });
    
    // Store the receipt in your database
    await storeReceipt(receipt);
    
    res.status(200).json({ received: true });
  } else {
    res.status(400).json({ error: 'Invalid signature' });
  }
});

app.listen(3000);
```

</TabItem>
<TabItem value="python" label="Python">

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhooks/iaindex/receipt', methods=['POST'])
def receive_receipt():
    receipt = request.json
    
    # Verify the receipt signature
    is_valid = publisher.verify_receipt(receipt)
    
    if is_valid:
        print(f'Valid receipt received: {receipt["contentId"]}')
        
        # Store the receipt in your database
        store_receipt(receipt)
        
        return jsonify({'received': True}), 200
    else:
        return jsonify({'error': 'Invalid signature'}), 400

app.run(port=3000)
```

</TabItem>
</Tabs>

## Next Steps

Congratulations! You've successfully set up IAIndex. Here's what to explore next:

### For Publishers
- [Domain Verification Guide](./publishers/domain-verification.md)
- [Generating Comprehensive Indexes](./publishers/generating-index.md)
- [Receiving and Processing Receipts](./publishers/receiving-receipts.md)

### For Developers
- [Protocol Specification](./protocol/schema.md)
- [SDK Documentation](./sdks/nodejs.md)
- [API Reference](./api/authentication.md)

### For Website Owners
- [WordPress Plugin](./plugins/wordpress.md)
- [Webflow Integration](./plugins/webflow.md)
- [Other CMS Plugins](./plugins/shopify.md)

## Troubleshooting

### DNS Verification Fails

If domain verification fails:
1. Ensure the TXT record is properly added
2. Wait 5-10 minutes for DNS propagation
3. Check with `dig TXT yourdomain.com`

### Index File Not Accessible

If your index file isn't accessible:
1. Verify the file is at `/.well-known/iaindex.json`
2. Check HTTPS is enabled
3. Ensure proper CORS headers are set
4. Test with: `curl -i https://yourdomain.com/.well-known/iaindex.json`

### Receipt Verification Fails

If receipts fail verification:
1. Check the signature algorithm matches
2. Ensure you're using the correct public key
3. Verify the timestamp is recent (within 5 minutes)

## Support

Need help? Here are your options:

- [Documentation](/)
- [GitHub Issues](https://github.com/claimtec/iaindex/issues)
- [Discord Community](https://discord.gg/iaindex)
- [Email Support](mailto:support@iaindex.com)
