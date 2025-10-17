# @iaindex/cli

Command line tool for managing AI Index attestations.

## Installation

```bash
npm install -g @iaindex/cli
```

Or use directly with npx:

```bash
npx @iaindex/cli [command]
```

## Quick Start

### 1. Authenticate

```bash
iaindex auth login
```

### 2. Verify Your Domain

```bash
# Initialize verification
iaindex verify init example.com

# Check verification status
iaindex verify check <verification-token>
```

### 3. Generate Keys

```bash
iaindex generate-keys -o ./keys -n mykeys
```

This will create:
- `mykeys-private.pem` - Keep this secure!
- `mykeys-public.pem` - Use in your attestations

### 4. Create an Index

#### Interactive Mode

```bash
iaindex create-index --interactive
```

#### From Config File

```bash
iaindex create-index config.json -s ./keys/mykeys-private.pem -o ./iaindex.json
```

## Commands

### Authentication

```bash
# Login to IAIndex
iaindex auth login

# Check authentication status
iaindex auth status

# Logout
iaindex auth logout
```

### Domain Verification

```bash
# Initialize domain verification
iaindex verify init <domain>

# Check verification status
iaindex verify check <token>
```

### Key Generation

```bash
# Generate RSA key pair
iaindex generate-keys [options]

Options:
  -o, --output <dir>   Output directory for keys (default: current directory)
  -n, --name <name>    Base name for key files (default: "iaindex")
```

### Index Creation

```bash
# Create index interactively
iaindex create-index --interactive

# Create from config file
iaindex create-index <config.json> [options]

Options:
  -i, --interactive      Interactive mode with prompts
  -o, --output <file>    Output file path (default: "./iaindex.json")
  -s, --sign <key>       Path to private key for signing
```

## Configuration File Format

See `examples/config.json` for a complete example:

```json
{
  "url": "https://example.com/blog/my-article",
  "title": "Article Title",
  "description": "Article description",
  "contentType": "article",
  "aiGenerated": {
    "percentage": 60,
    "sections": ["introduction", "main-content"]
  },
  "humanOversight": {
    "level": "full",
    "verifiedBy": "John Doe"
  },
  "publisher": {
    "name": "Example Publisher",
    "domain": "example.com"
  }
}
```

## API Configuration

The CLI uses the following API endpoint by default:

```
https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
```

Configuration is stored in `~/.iaindex/config.json`

## Examples

### Complete Workflow

```bash
# 1. Login
iaindex auth login

# 2. Verify your domain
iaindex verify init mysite.com
# Add DNS TXT record, then:
iaindex verify check <token>

# 3. Generate keys
iaindex generate-keys -o ./keys

# 4. Create an index
iaindex create-index examples/config.json -s ./keys/iaindex-private.pem

# 5. Upload iaindex.json to your website at /.well-known/iaindex.json
```

## License

MIT
