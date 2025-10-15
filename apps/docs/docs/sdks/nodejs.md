---
sidebar_position: 1
title: Node.js SDK
---

# Node.js SDK

Official IAIndex SDK for Node.js applications.

## Installation

```bash
npm install @iaindex/sdk
# or
yarn add @iaindex/sdk
```

## Quick Start

```javascript
const { IAIndexPublisher, IAIndexClient } = require('@iaindex/sdk');

// As a publisher
const publisher = new IAIndexPublisher({
  domain: 'yourdomain.com',
  privateKey: process.env.IAINDEX_PRIVATE_KEY,
  name: 'Your Publication',
  contact: 'contact@yourdomain.com'
});

await publisher.addEntry({
  url: 'https://yourdomain.com/article',
  title: 'Article Title',
  author: 'Author Name',
  publishedDate: new Date().toISOString(),
  license: { type: 'CC-BY-4.0' }
});

// As an AI client
const client = new IAIndexClient({
  clientId: 'your-client-id',
  privateKey: process.env.CLIENT_PRIVATE_KEY
});

const content = await client.accessContent('https://example.com/article');
await client.sendReceipt(content, {
  purpose: 'training',
  context: 'language-model-pretraining'
});
```

## API Reference

### IAIndexPublisher

#### Constructor

```javascript
new IAIndexPublisher(options)
```

Options:
- `domain` (string): Your verified domain
- `privateKey` (string): Private key for signing
- `name` (string): Publisher name
- `contact` (string): Contact email

#### Methods

**addEntry(entry)**
```javascript
await publisher.addEntry({
  url: string,
  title: string,
  author: string,
  publishedDate: string,
  license: object
});
```

**generateIndex()**
```javascript
const index = await publisher.generateIndex();
```

**verifyReceipt(receipt)**
```javascript
const isValid = await publisher.verifyReceipt(receipt);
```

### IAIndexClient

#### Constructor

```javascript
new IAIndexClient(options)
```

Options:
- `clientId` (string): Unique client identifier
- `privateKey` (string): Private key for signing
- `name` (string): Client/model name
- `organization` (string): Organization name

#### Methods

**accessContent(url)**
```javascript
const content = await client.accessContent(url);
```

**sendReceipt(content, usage)**
```javascript
await client.sendReceipt(content, {
  purpose: 'training' | 'inference' | 'research',
  context: string,
  datasetId?: string,
  modelId?: string
});
```

## Examples

See [GitHub Examples](https://github.com/claimtec/iaindex/tree/main/examples/nodejs)
