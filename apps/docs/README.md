# IAIndex Documentation

Official documentation for the IAIndex protocol - a transparent AI training attribution protocol.

## Overview

This documentation site is built with [Docusaurus 3](https://docusaurus.io/), a modern static website generator optimized for technical documentation.

## Features

- **Comprehensive Documentation**: Complete protocol specification, guides, and API reference
- **Multiple SDKs**: Node.js and Python SDK documentation
- **Plugin Guides**: Integration guides for WordPress, Webflow, Shopify, and more
- **AI Client Integration**: LangChain and LlamaIndex integration guides
- **Search Functionality**: Algolia-powered search (requires configuration)
- **Dark Mode**: Built-in dark mode support
- **Versioned Docs**: Support for multiple documentation versions
- **Code Syntax Highlighting**: Prism-powered syntax highlighting
- **Responsive Design**: Mobile-friendly responsive layout

## Documentation Structure

```
docs/
├── intro.md                    # Introduction and overview
├── quickstart.md              # 5-minute quick start guide
├── protocol/                  # Protocol specification
│   ├── schema.md             # JSON schema
│   ├── receipts.md           # Receipt format
│   └── signatures.md         # Cryptographic signatures
├── publishers/                # Publisher guides
│   ├── domain-verification.md
│   ├── generating-index.md
│   └── receiving-receipts.md
├── sdks/                      # SDK documentation
│   ├── nodejs.md
│   └── python.md
├── plugins/                   # Website builder plugins
│   ├── wordpress.md
│   ├── webflow.md
│   ├── bubble.md
│   ├── wix.md
│   ├── squarespace.md
│   ├── shopify.md
│   ├── framer.md
│   └── ghost.md
├── clients/                   # AI client integration
│   ├── langchain.md
│   └── llamaindex.md
├── api/                       # API reference
│   ├── authentication.md
│   ├── receipts.md
│   ├── analytics.md
│   └── attestations.md
└── compliance/                # Legal and compliance
    ├── gdpr.md
    ├── popia.md
    └── terms.md
```

## Local Development

### Prerequisites

- Node.js 20.0 or higher
- npm or yarn

### Installation

```bash
cd apps/docs
npm install
```

### Start Development Server

```bash
npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

The site will be available at: http://localhost:3000

### Build for Production

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static hosting service.

### Serve Production Build Locally

```bash
npm run serve
```

### Type Checking

```bash
npm run typecheck
```

## Configuration

### Main Configuration

Edit `docusaurus.config.ts` to customize:

- Site metadata (title, tagline, URL)
- Navigation structure
- Footer links
- Theme settings
- Search configuration
- Analytics integration
- Plugin configuration

### Sidebar Navigation

Edit `sidebars.ts` to modify the sidebar structure.

### Custom Styling

Edit `src/css/custom.css` to customize colors, fonts, and styles.

## Search Setup

To enable search functionality:

1. Sign up for [Algolia DocSearch](https://docsearch.algolia.com/)
2. Update `docusaurus.config.ts` with your Algolia credentials:
   ```javascript
   algolia: {
     appId: 'YOUR_APP_ID',
     apiKey: 'YOUR_SEARCH_API_KEY',
     indexName: 'iaindex',
   }
   ```

## Analytics Setup

To enable Google Analytics:

1. Get your Google Analytics tracking ID
2. Update `docusaurus.config.ts`:
   ```javascript
   gtag: {
     trackingID: 'G-XXXXXXXXXX',
     anonymizeIP: true,
   }
   ```

## Deployment

### GitHub Pages

```bash
GIT_USER=<Your GitHub username> npm run deploy
```

### Netlify

1. Connect your repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `build`

### Vercel

1. Import your repository to Vercel
2. Vercel will auto-detect Docusaurus
3. Deploy!

### AWS S3 + CloudFront

```bash
npm run build
aws s3 sync build/ s3://your-bucket-name --delete
```

### Docker

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t iaindex-docs .
docker run -p 80:80 iaindex-docs
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-doc`
3. Make your changes
4. Test locally: `npm start`
5. Build to verify: `npm run build`
6. Commit your changes: `git commit -am 'Add new documentation'`
7. Push to the branch: `git push origin feature/new-doc`
8. Submit a pull request

## Documentation Guidelines

### Writing Style

- Use clear, concise language
- Provide code examples for all features
- Include both explanatory text and practical examples
- Use active voice
- Be consistent with terminology

### Code Examples

- Provide examples in multiple languages where applicable
- Use syntax highlighting with language tags
- Include complete, runnable examples
- Add comments to explain complex code

### Formatting

- Use proper markdown syntax
- Include frontmatter in all docs:
  ```yaml
  ---
  sidebar_position: 1
  title: Page Title
  ---
  ```
- Use headings hierarchically (H1 → H2 → H3)
- Add line breaks between sections

### Links

- Use relative links for internal pages: `[Link](./page.md)`
- Use absolute URLs for external links
- Check all links before committing

## Troubleshooting

### Build Fails

- Clear cache: `npm run clear`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check for broken links in markdown files

### Search Not Working

- Verify Algolia credentials in config
- Ensure Algolia has indexed your site
- Check browser console for errors

### Styling Issues

- Clear browser cache
- Check custom CSS syntax
- Verify class names match Docusaurus theme

## Resources

- [Docusaurus Documentation](https://docusaurus.io/)
- [Markdown Guide](https://www.markdownguide.org/)
- [MDX Documentation](https://mdxjs.com/)
- [Prism Language Support](https://prismjs.com/#supported-languages)

## Support

- [GitHub Issues](https://github.com/claimtec/iaindex/issues)
- [Discord Community](https://discord.gg/iaindex)
- [Email Support](mailto:support@iaindex.com)

## License

This documentation is licensed under the MIT License. See the LICENSE file for details.

---

Built with [Docusaurus](https://docusaurus.io/) by [Claimtec](https://claimtec.com)
