---
sidebar_position: 2
title: Generating Index Files
---

# Generating Index Files

Learn how to create and maintain your IAIndex file for content attribution.

## Overview

The index file is a JSON document that lists all your content entries with metadata and licensing information. It's hosted at:

```
https://yourdomain.com/.well-known/iaindex.json
```

## Quick Start

```javascript
const { IAIndexPublisher } = require('@iaindex/sdk');

const publisher = new IAIndexPublisher({
  domain: 'yourdomain.com',
  privateKey: process.env.IAINDEX_PRIVATE_KEY,
  name: 'Your Publication',
  contact: 'contact@yourdomain.com'
});

// Add content entries
await publisher.addEntry({
  url: 'https://yourdomain.com/article-1',
  title: 'Article Title',
  author: 'Author Name',
  publishedDate: '2025-01-15T10:00:00Z',
  content: 'Article content...',
  license: {
    type: 'CC-BY-4.0',
    terms: 'https://creativecommons.org/licenses/by/4.0/'
  }
});

// Generate and save index
await publisher.generateIndex('./iaindex.json');
```

## Adding Content Entries

### Basic Entry

```javascript
const entry = {
  url: 'https://yourdomain.com/article',
  title: 'Article Title',
  author: 'Author Name',
  publishedDate: '2025-01-15T10:00:00Z',
  contentHash: 'sha256:abc123...',
  license: {
    type: 'CC-BY-4.0',
    terms: 'https://creativecommons.org/licenses/by/4.0/'
  }
};

await publisher.addEntry(entry);
```

### Entry with Metadata

```javascript
await publisher.addEntry({
  url: 'https://yourdomain.com/article',
  title: 'Advanced AI Techniques',
  author: 'Jane Doe',
  publishedDate: '2025-01-15T10:00:00Z',
  modifiedDate: '2025-01-16T14:30:00Z',
  content: 'Full article content...',
  license: {
    type: 'CC-BY-SA-4.0',
    terms: 'https://creativecommons.org/licenses/by-sa/4.0/',
    commercial: true,
    derivatives: true,
    attribution: true
  },
  metadata: {
    category: 'Technology',
    tags: ['AI', 'Machine Learning', 'Neural Networks'],
    language: 'en',
    readingTime: 8,
    wordCount: 2000
  }
});
```

## Bulk Import

### From CMS

```javascript
// WordPress example
const posts = await fetchWordPressPosts();

for (const post of posts) {
  await publisher.addEntry({
    url: post.link,
    title: post.title.rendered,
    author: post.author_name,
    publishedDate: post.date,
    modifiedDate: post.modified,
    content: post.content.rendered,
    license: getLicenseForPost(post)
  });
}
```

### From Database

```javascript
const { rows } = await db.query('SELECT * FROM articles WHERE published = true');

for (const article of rows) {
  await publisher.addEntry({
    url: `https://yourdomain.com/articles/${article.slug}`,
    title: article.title,
    author: article.author_name,
    publishedDate: article.published_at,
    contentHash: generateHash(article.content),
    license: article.license_config
  });
}
```

## Index Generation

### Generate Index File

```javascript
// Generate index
const index = await publisher.generateIndex();

// Save to file
await publisher.saveIndex('./iaindex.json');

// Or get as JSON
const indexJSON = JSON.stringify(index, null, 2);
```

### Incremental Updates

```javascript
// Load existing index
await publisher.loadIndex('./iaindex.json');

// Add new entries
await publisher.addEntry(newEntry);

// Update existing entry
await publisher.updateEntry(entryId, updates);

// Remove entry
await publisher.removeEntry(entryId);

// Regenerate
await publisher.generateIndex('./iaindex.json');
```

## Deployment

### Static Hosting

Upload `iaindex.json` to `/.well-known/` directory:

```bash
# Copy to web root
cp iaindex.json /var/www/html/.well-known/

# Set permissions
chmod 644 /var/www/html/.well-known/iaindex.json
```

### Dynamic Generation

Serve dynamically:

```javascript
app.get('/.well-known/iaindex.json', async (req, res) => {
  const index = await generateFreshIndex();
  res.json(index);
});
```

### CDN Deployment

```bash
# AWS S3
aws s3 cp iaindex.json s3://yourbucket/.well-known/ --acl public-read

# Cloudflare Pages
wrangler pages publish .well-known --project-name=yoursite
```

## Automation

### Scheduled Updates

```javascript
const cron = require('node-cron');

// Regenerate daily at midnight
cron.schedule('0 0 * * *', async () => {
  console.log('Regenerating IAIndex...');
  await publisher.generateIndex('./iaindex.json');
  await deployIndex();
  console.log('Index updated successfully');
});
```

### Webhook Triggers

```javascript
// Trigger on content publish
cms.on('post.published', async (post) => {
  await publisher.addEntry(convertToIAIndexEntry(post));
  await publisher.generateIndex();
  await deployIndex();
});

// Trigger on content update
cms.on('post.updated', async (post) => {
  await publisher.updateEntry(post.id, convertToIAIndexEntry(post));
  await publisher.generateIndex();
  await deployIndex();
});
```

## Best Practices

1. **Update Regularly**: Regenerate index when content changes
2. **Validate Before Deploy**: Always validate generated indexes
3. **Keep Backups**: Maintain versioned backups of indexes
4. **Monitor Size**: Split large indexes into multiple files
5. **Set Cache Headers**: Configure appropriate cache TTL
6. **Sign Fresh**: Re-sign index with each generation

## Related Documentation

- [JSON Schema](../protocol/schema.md)
- [Domain Verification](./domain-verification.md)
- [Receiving Receipts](./receiving-receipts.md)
