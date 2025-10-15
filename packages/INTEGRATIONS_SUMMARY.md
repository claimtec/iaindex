# AIIndex Platform Integrations Summary

This document provides an overview of the Webflow and Bubble.io integrations for AIIndex.

## Overview

Both integrations enable seamless AI Index generation and management for no-code platforms, making it easy for users to participate in the AI content ecosystem without writing code.

---

## 1. Webflow Integration

**Location**: `/packages/webflow-snippet/`

### Description
A JavaScript embed snippet that auto-generates `/ai-index.json` from Webflow CMS collections and syncs with the AIIndex API.

### Files Structure
```
webflow-snippet/
├── snippet.js          # Main integration JavaScript
├── config.html         # Visual configuration UI
├── styles.css          # Badge and UI styles
├── package.json        # NPM package configuration
└── README.md           # Complete documentation
```

### Key Features

#### 1. Auto-Generated AI Index JSON
- Fetches all Webflow CMS collections via API
- Transforms CMS data to AIIndex format
- Generates complete `/ai-index.json` file
- Includes metadata (published dates, authors, categories, tags)

#### 2. Real-Time Synchronization
- Auto-syncs on page load (configurable)
- Manual sync trigger available
- Webhook notifications on sync complete
- Status tracking and monitoring

#### 3. Visual Configuration Panel
- HTML-based configuration UI (`config.html`)
- Form inputs for all settings:
  - API key configuration
  - Domain setup
  - Webhook URL
  - Feature toggles (auto-sync, badge)
- Real-time embed code generation
- Copy-to-clipboard functionality

#### 4. Domain Verification
- Initiate verification from UI
- Visual status indicator (verified/pending/failed)
- Step-by-step verification instructions
- Automatic verification check

#### 5. Verification Badge
- Customizable appearance (dark, light, colored themes)
- Multiple sizes (small, medium, large)
- Flexible positioning (corners or inline)
- Animated options (pulse effect)
- Responsive design

#### 6. CMS Integration
- Works with any Webflow CMS collection
- Supports standard CMS fields
- Custom field mapping
- Handles rich text content
- Preserves metadata

### Setup Instructions

#### Method 1: Using Configuration UI
1. Open `config.html` in a browser
2. Enter your AIIndex API key
3. Enter your Webflow domain
4. Configure webhook URL (optional)
5. Customize badge settings
6. Copy the generated embed code
7. Paste into Webflow Custom Code (Footer)
8. Publish your site

#### Method 2: Manual Setup
```html
<!-- Add to Webflow Custom Code > Footer Code -->
<script src="https://cdn.aiindex.org/webflow/snippet.js"></script>
<script>
  window.aiIndexConfig = {
    apiKey: 'your-api-key',
    domain: 'yoursite.com',
    webhookUrl: 'https://yoursite.com/webhook',
    badgeEnabled: true,
    autoSync: true
  };
  AIIndexWebflow.init(window.aiIndexConfig);
</script>
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | *required* | Your AIIndex API key |
| `domain` | string | auto | Your site domain |
| `apiEndpoint` | string | api.aiindex.org/v1 | API endpoint |
| `webhookUrl` | string | null | Webhook notification URL |
| `badgeEnabled` | boolean | true | Show verification badge |
| `autoSync` | boolean | true | Auto-sync on load |

### Use Cases
- Blog content indexing
- Portfolio site management
- Product catalog AI accessibility
- Documentation site indexing
- Agency client sites

### Example Transformations

**Webflow CMS Item**:
```json
{
  "name": "AI Innovation in 2025",
  "slug": "/blog/ai-innovation-2025",
  "content": "Article content...",
  "published-on": "2025-10-13",
  "author": { "name": "Jane Smith" },
  "category": { "name": "Technology" },
  "tags": ["ai", "innovation"]
}
```

**AIIndex Format**:
```json
{
  "url": "https://yoursite.com/blog/ai-innovation-2025",
  "title": "AI Innovation in 2025",
  "content": "Article content...",
  "metadata": {
    "published": "2025-10-13",
    "author": "Jane Smith",
    "category": "Technology",
    "tags": ["ai", "innovation"]
  },
  "access": {
    "crawlable": true,
    "aiTrainable": true
  }
}
```

---

## 2. Bubble.io Plugin

**Location**: `/packages/bubble-plugin/`

### Description
A full-featured Bubble.io plugin providing workflow actions, visual elements, and data types for complete AIIndex integration.

### Files Structure
```
bubble-plugin/
├── manifest.json                      # Plugin manifest
├── package.json                       # NPM package configuration
├── actions/
│   ├── generate-ai-index.js          # Generate AI Index action
│   ├── send-access-receipt.js        # Send receipt action
│   └── verify-domain.js              # Verify domain action
├── elements/
│   ├── aiindex-badge.js              # Badge visual element
│   └── verification-status.js        # Status visual element
├── api/
│   └── api-connector-preset.json     # Pre-configured API calls
└── README.md                          # Complete documentation
```

### Key Features

#### 1. Workflow Actions (5 Actions)

##### a) Generate AI Index JSON
- Fetches data from Bubble database
- Transforms to AIIndex format
- Auto-syncs to AIIndex API
- Returns document count and status
- Saves JSON to Bubble file storage

**Configuration**:
```
Domain: your-site.com
Data source: Your Bubble data type
Auto-sync: Yes/No
```

**Exposed Fields**:
- `document_count` (number)
- `sync_status` (text)
- `json_url` (text)
- `last_synced` (date)

##### b) Send Access Receipt
- Tracks AI system access
- Records access type (crawl, training, etc.)
- Stores receipt in Bubble database
- Triggers custom event
- Includes metadata (IP, user agent, session)

**Configuration**:
```
Document ID: doc_123abc
AI Provider: OpenAI
Access type: crawl/training/inference/analysis
```

**Exposed Fields**:
- `receipt_id` (text)
- `status` (text)
- `timestamp` (date)

##### c) Verify Domain with AIIndex
- Initiates domain verification
- Supports multiple methods (DNS, HTML, Meta)
- Generates verification instructions
- Saves verification record
- Triggers event on success

**Configuration**:
```
Domain: your-site.com
Verification method: dns/html/meta
```

**Exposed Fields**:
- `verification_status` (text)
- `verification_token` (text)
- `instructions` (text)
- `expires_at` (date)

##### d) Get AIIndex Status
- Retrieves current sync status
- Shows verification state
- Returns document count
- Displays last sync time

**Configuration**:
```
Domain: your-site.com
```

**Exposed Fields**:
- `is_verified` (boolean)
- `document_count` (number)
- `last_sync` (date)
- `sync_status` (text)

##### e) Update AIIndex Document
- Updates specific document
- Modifies title, description, content
- Controls access settings
- Returns success status

**Configuration**:
```
Document ID: doc_123abc
Title: New title
Description: New description
Content: Updated content
Crawlable: Yes/No
AI trainable: Yes/No
```

#### 2. Visual Elements (2 Elements)

##### a) AIIndex Badge
- Displays verification badge
- Multiple themes (dark, light, purple, blue, green)
- Multiple sizes (small, medium, large)
- Flexible positioning (4 corners or inline)
- Optional pulse animation
- Responsive design

**Properties**:
```
Domain: your-site.com
Theme: dark/light/purple/blue/green
Size: small/medium/large
Position: top-left/top-right/bottom-left/bottom-right
Show pulse: Yes/No
```

##### b) Verification Status
- Real-time status display
- Shows verification state (verified/pending/failed/unverified)
- Color-coded indicators
- Optional icon display
- Compact mode available
- Displays verification date

**Properties**:
```
Domain: your-site.com
Show icon: Yes/No
Compact mode: Yes/No
```

#### 3. Data Types (2 Types)

##### a) AIIndex Document
Fields:
- `document_id` (text)
- `domain` (text)
- `url` (text)
- `title` (text)
- `description` (text)
- `content` (text)
- `published_date` (date)
- `updated_date` (date)
- `author` (text)
- `category` (text)
- `tags` (list of texts)
- `crawlable` (boolean)
- `ai_trainable` (boolean)
- `verification_status` (text)
- `last_synced` (date)

##### b) AIIndex Receipt
Fields:
- `receipt_id` (text)
- `document_id` (text)
- `ai_provider` (text)
- `access_type` (text)
- `timestamp` (date)
- `status` (text)

#### 4. API Connector Preset
Pre-configured API calls to `https://api.aiindex.org/v1`:

- **Get Documents** - Retrieve all documents for domain
- **Get Document by ID** - Retrieve specific document
- **Create Document** - Create new document
- **Update Document** - Update existing document
- **Delete Document** - Delete document
- **Verify Domain** - Initiate verification
- **Check Verification** - Check verification status
- **Get Domain Status** - Get current domain status
- **Create Receipt** - Create access receipt
- **Get Receipts** - Retrieve access receipts
- **Bulk Sync** - Sync multiple documents
- **Health Check** - Check API health

#### 5. Custom Events (3 Events)
- **AIIndex Sync Complete** - Triggered after successful sync
- **Domain Verified** - Triggered when domain is verified
- **Receipt Sent** - Triggered when receipt is sent

### Setup Instructions

#### Installation
1. Open Bubble editor
2. Go to **Plugins** tab
3. Click **Add plugins**
4. Search for "AIIndex"
5. Click **Install**

#### Configuration
1. Go to **Plugins** > **AIIndex**
2. Click **API Keys** section
3. Add your AIIndex API key
4. Save changes

#### Usage Examples

##### Auto-Sync Daily
```
Workflow: Backend workflow "Sync AIIndex Daily"
Schedule: Recurring, every day at 2 AM
Actions:
  1. Generate AI Index JSON
     - Domain: yoursite.com
     - Data source: Blog Post
     - Auto-sync: Yes
  2. Send email notification (optional)
```

##### Display Badge
```
Element: AIIndex Badge
Properties:
  - Domain: yoursite.com
  - Theme: dark
  - Size: medium
  - Position: bottom-right
  - Show pulse: No
```

##### Track AI Access
```
Workflow: When page is loaded
Condition: User agent contains "bot"
Actions:
  1. Send Access Receipt
     - Document ID: Current Page's doc ID
     - AI Provider: Detect from user agent
     - Access type: crawl
  2. Log to database (optional)
```

### Use Cases
- Blog/publication indexing
- E-commerce product catalogs
- Knowledge base documentation
- User-generated content platforms
- Membership site content
- Educational content platforms

---

## Comparison Matrix

| Feature | Webflow | Bubble.io |
|---------|---------|-----------|
| **Installation** | Copy/paste snippet | Plugin install |
| **Configuration** | HTML form UI | Bubble workflow |
| **CMS Integration** | Webflow CMS API | Bubble database |
| **Auto-Sync** | Yes | Yes (workflow) |
| **Manual Sync** | JavaScript call | Workflow action |
| **Verification Badge** | Yes (CSS/JS) | Yes (element) |
| **Status Display** | Callback function | Visual element |
| **Domain Verification** | API call | Workflow action |
| **Receipt Tracking** | API call | Workflow + DB |
| **Webhook Support** | Yes | Via API Connector |
| **Data Storage** | External | Bubble DB |
| **Custom Events** | JavaScript events | Bubble events |
| **API Access** | Direct API calls | API Connector |
| **Difficulty** | Easy | Very Easy |
| **Best For** | Design-focused sites | App-like platforms |

---

## Common Features

Both integrations provide:

1. **Automatic AI Index Generation**
   - Transform platform data to AIIndex format
   - Include full metadata
   - Handle rich content

2. **Domain Verification**
   - Multiple verification methods
   - Visual status indicators
   - Step-by-step instructions

3. **Verification Badges**
   - Customizable appearance
   - Multiple themes and sizes
   - Responsive design

4. **Access Tracking**
   - Record AI system access
   - Track access patterns
   - Generate receipts

5. **Real-time Sync**
   - Automatic or manual sync
   - Status monitoring
   - Error handling

6. **API Integration**
   - Full AIIndex API v1 support
   - Bearer token authentication
   - Comprehensive endpoints

---

## API Endpoints Used

Both integrations connect to `https://api.aiindex.org/v1`:

- `POST /documents` - Create/sync documents
- `GET /documents` - Retrieve documents
- `PUT /documents/:id` - Update document
- `DELETE /documents/:id` - Delete document
- `POST /domains/verify` - Verify domain
- `GET /domains/:domain/status` - Check status
- `POST /receipts` - Create receipt
- `GET /receipts` - Get receipts
- `GET /health` - Health check

---

## Security Considerations

### Webflow
- API keys stored in localStorage (client-side)
- Use environment variables in production
- Consider server-side proxy for sensitive operations
- Rotate keys regularly

### Bubble.io
- API keys stored securely by Bubble
- Use privacy rules for data protection
- Backend workflows for sensitive operations
- Leverage Bubble's built-in security

---

## Performance Optimization

### Webflow
- Async script loading (no page blocking)
- Cached API responses
- Lazy badge rendering
- Minimal DOM manipulation

### Bubble.io
- Background workflows for heavy operations
- Pagination for large datasets
- Cached status checks
- Efficient database queries

---

## Support & Resources

### Documentation
- Webflow: [docs.aiindex.org/webflow](https://docs.aiindex.org/webflow)
- Bubble: [docs.aiindex.org/bubble](https://docs.aiindex.org/bubble)

### Community
- Webflow Forum: [forum.webflow.com](https://forum.webflow.com)
- Bubble Forum: [forum.bubble.io](https://forum.bubble.io)

### Direct Support
- Email: support@aiindex.org
- Dashboard: [aiindex.org/dashboard](https://aiindex.org/dashboard)
- Status: [status.aiindex.org](https://status.aiindex.org)

---

## Future Enhancements

### Planned Features
- [ ] Visual workflow builder (Webflow)
- [ ] Advanced filtering options
- [ ] Multi-language support
- [ ] Analytics dashboard integration
- [ ] Custom field mapping UI
- [ ] Bulk operations UI
- [ ] Rate limiting controls
- [ ] Advanced caching strategies

### Community Requests
- [ ] Shopify integration
- [ ] Wix integration
- [ ] WordPress plugin enhancement
- [ ] Zapier integration
- [ ] Make.com integration

---

## Version Information

- **Webflow Snippet**: v1.0.0
- **Bubble.io Plugin**: v1.0.0
- **AIIndex API**: v1
- **Release Date**: 2025-10-13

---

## License

Both integrations are released under the MIT License.

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (if applicable)
5. Submit a pull request

### Webflow
Repository: [github.com/aiindex/webflow-integration](https://github.com/aiindex/webflow-integration)

### Bubble.io
Repository: [github.com/aiindex/bubble-plugin](https://github.com/aiindex/bubble-plugin)

---

## Acknowledgments

Special thanks to:
- Webflow community for feedback and testing
- Bubble.io community for feature requests
- Early adopters and beta testers
- AIIndex API team

---

**Last Updated**: 2025-10-13
**Maintained By**: AIIndex Team
