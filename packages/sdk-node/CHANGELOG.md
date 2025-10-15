# Changelog

All notable changes to the @aiindex/sdk project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-13

### Added
- Initial release of @aiindex/sdk
- CLI tool `aiindex-gen` with commands:
  - `init`: Create configuration file
  - `build`: Generate ai-index.json from website
  - `serve`: Start local webhook server
  - `verify`: Validate generated file
  - `sign`: Add cryptographic signature
- Core library features:
  - `AIIndexGenerator` class for website crawling and metadata extraction
  - `SignatureManager` class for ECDSA P-256 key generation and signing
  - `ReceiptHandler` class for receiving and forwarding receipts to API
  - `Validator` class for schema validation
- Full TypeScript support with comprehensive type definitions
- ESM and CommonJS dual module support
- Comprehensive documentation and examples
- Automated website crawling with configurable options
- JSON Web Signature (JWS) support using jose library
- Built-in webhook server for receipt handling
- Retry logic for API calls
- CLI with colored output using chalk and ora
- Support for both JWK and PEM key formats

### Features
- Automatically detect AI capabilities from website content
- Extract structured data (JSON-LD, microdata)
- Configurable crawl depth and page limits
- URL pattern include/exclude filtering
- Email and contact information extraction
- API endpoint detection
- Batch receipt forwarding
- Schema validation with detailed error messages
- Signature verification
- Custom user agent support
- CORS support for webhook server

## [Unreleased]

### Planned
- Unit tests with Jest
- Integration tests
- CI/CD pipeline
- Additional export formats (YAML, XML)
- Plugin system for custom extractors
- Browser-compatible version
- GraphQL API support
- Rate limiting for crawlers
- Caching layer
- Dashboard UI for monitoring
