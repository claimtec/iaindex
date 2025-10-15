---
sidebar_position: 3
title: Receiving Receipts
---

# Receiving Receipts

Set up receipt handling to track AI usage of your content.

## Receipt Endpoint

Configure a webhook endpoint to receive usage receipts:

```javascript
const express = require('express');
const { verifyReceipt } = require('@iaindex/sdk');

const app = express();
app.use(express.json());

app.post('/api/iaindex/receipt', async (req, res) => {
  try {
    const receipt = req.body;
    
    // Verify signature
    const isValid = await verifyReceipt(receipt);
    
    if (!isValid) {
      return res.status(401).json({ error: 'Invalid signature' });
    }
    
    // Store receipt
    await storeReceipt(receipt);
    
    // Send confirmation
    res.json({ received: true, receiptId: receipt.receiptId });
    
  } catch (error) {
    console.error('Receipt processing error:', error);
    res.status(500).json({ error: 'Processing failed' });
  }
});

app.listen(3000);
```

## Receipt Processing

### Validation

```javascript
async function processReceipt(receipt) {
  // 1. Verify signature
  if (!await verifyReceipt(receipt)) {
    throw new Error('Invalid signature');
  }
  
  // 2. Check timestamp
  const receiptAge = Date.now() - new Date(receipt.timestamp);
  if (receiptAge > 5 * 60 * 1000) {
    throw new Error('Receipt too old');
  }
  
  // 3. Verify content exists
  const content = await findContent(receipt.content.entryId);
  if (!content) {
    throw new Error('Content not found');
  }
  
  // 4. Check for duplicates
  if (await receiptExists(receipt.receiptId)) {
    throw new Error('Duplicate receipt');
  }
  
  return true;
}
```

### Storage

```javascript
async function storeReceipt(receipt) {
  await db.query(`
    INSERT INTO receipts (
      receipt_id, content_id, client_id, timestamp,
      purpose, signature, raw_receipt
    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
  `, [
    receipt.receiptId,
    receipt.content.entryId,
    receipt.client.id,
    receipt.timestamp,
    receipt.usage.purpose,
    receipt.signature,
    JSON.stringify(receipt)
  ]);
}
```

## Analytics

### Usage Reports

```javascript
// Get usage by content
async function getContentUsage(contentId) {
  const { rows } = await db.query(`
    SELECT
      client_id,
      COUNT(*) as access_count,
      MIN(timestamp) as first_access,
      MAX(timestamp) as last_access
    FROM receipts
    WHERE content_id = $1
    GROUP BY client_id
  `, [contentId]);
  
  return rows;
}

// Get usage by client
async function getClientActivity(clientId) {
  const { rows } = await db.query(`
    SELECT
      DATE(timestamp) as date,
      COUNT(*) as receipts,
      purpose
    FROM receipts
    WHERE client_id = $1
    GROUP BY DATE(timestamp), purpose
    ORDER BY date DESC
  `, [clientId]);
  
  return rows;
}
```

### Dashboard

```javascript
app.get('/api/analytics/dashboard', async (req, res) => {
  const stats = {
    totalReceipts: await getTotalReceipts(),
    uniqueClients: await getUniqueClients(),
    topContent: await getTopContent(10),
    recentActivity: await getRecentActivity(50),
    usageByPurpose: await getUsageByPurpose()
  };
  
  res.json(stats);
});
```

## Notifications

### Email Alerts

```javascript
const { sendEmail } = require('./email');

async function notifyNewClient(receipt) {
  const client = receipt.client;
  
  await sendEmail({
    to: 'admin@yourdomain.com',
    subject: 'New AI Client Accessing Content',
    html: `
      <h2>New Client Activity</h2>
      <p><strong>Client:</strong> ${client.name}</p>
      <p><strong>Organization:</strong> ${client.organization}</p>
      <p><strong>Content:</strong> ${receipt.content.url}</p>
      <p><strong>Purpose:</strong> ${receipt.usage.purpose}</p>
    `
  });
}
```

### Webhook Forwarding

```javascript
async function forwardReceipt(receipt) {
  await fetch('https://your-analytics-platform.com/webhook', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event: 'iaindex.receipt',
      data: receipt
    })
  });
}
```

## Related Documentation

- [Receipt Format](../protocol/receipts.md)
- [API Reference](../api/receipts.md)
- [Analytics API](../api/analytics.md)
