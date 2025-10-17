# IAIndex CLI - Installation Guide

## Quick Installation

### Option 1: Use from Source (Current Setup)

The CLI is already built and ready to use:

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli
node bin/iaindex.js [command]
```

### Option 2: Link Globally (Recommended for Development)

Make the `iaindex` command available globally:

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli
npm link
```

Now you can use `iaindex` from anywhere:

```bash
iaindex --help
iaindex generate-keys
iaindex create-index --interactive
```

### Option 3: Install from npm (When Published)

Once published to npm registry:

```bash
npm install -g @iaindex/cli
```

---

## Prerequisites

- **Node.js**: Version 14.0.0 or higher
- **npm**: Usually comes with Node.js
- **Operating System**: macOS, Linux, or Windows

### Check Your Node.js Version

```bash
node --version
```

Should show v14.0.0 or higher.

---

## Installation Steps (From Source)

### 1. Navigate to the Package

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli
```

### 2. Install Dependencies

```bash
npm install
```

This installs all required dependencies (79 packages).

### 3. Build the Project

```bash
npm run build
```

This compiles TypeScript to JavaScript in the `dist/` directory.

### 4. Verify Installation

```bash
npm test
```

Should display the help output.

### 5. (Optional) Link Globally

```bash
npm link
```

This creates a global symlink so you can use `iaindex` from anywhere.

---

## Post-Installation

### Test the CLI

```bash
# If linked globally
iaindex --version

# Or use directly
node bin/iaindex.js --version
```

Should display: `1.0.0`

### Run Your First Command

```bash
iaindex generate-keys -o ~/test-keys
```

This creates a test key pair in your home directory.

---

## Uninstallation

### Remove Global Link

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli
npm unlink
```

### Remove Package (if installed globally from npm)

```bash
npm uninstall -g @iaindex/cli
```

---

## Troubleshooting

### Issue: "Command not found: iaindex"

**Solution 1**: Use the full path
```bash
node /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli/bin/iaindex.js
```

**Solution 2**: Link globally
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli
npm link
```

**Solution 3**: Add to PATH
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli/bin"
```

### Issue: "Cannot find module"

**Solution**: Rebuild the project
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli
npm install
npm run build
```

### Issue: Permission Denied

**Solution**: Make the bin file executable
```bash
chmod +x /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli/bin/iaindex.js
```

### Issue: TypeScript Compilation Errors

**Solution**: Ensure TypeScript is installed
```bash
npm install --save-dev typescript
npm run build
```

---

## Development Setup

### Watch Mode (Auto-rebuild on Changes)

```bash
npm run dev
```

This watches for file changes and rebuilds automatically.

### Running Tests

```bash
# Basic test
npm test

# Full test suite
./test-cli.sh
```

### Making Changes

1. Edit files in `src/`
2. Run `npm run build` or use watch mode
3. Test with `node bin/iaindex.js`

---

## Directory Structure After Installation

```
packages/cli/
├── bin/
│   └── iaindex.js              # Executable
├── dist/                       # Compiled JavaScript
│   ├── index.js
│   ├── api.js
│   ├── config.js
│   ├── crypto.js
│   └── commands/
│       ├── auth.js
│       ├── verify.js
│       ├── keys.js
│       └── index-gen.js
├── src/                        # TypeScript source
├── node_modules/               # Dependencies (79 packages)
├── examples/                   # Example configs
├── package.json
└── README.md
```

---

## Configuration Files

### User Config Location

After first run, a config file is created at:
```
~/.iaindex/config.json
```

This stores:
- API endpoint URL
- Authentication token (after login)
- User ID

### Default Configuration

```json
{
  "apiBaseUrl": "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io"
}
```

---

## Publishing to npm (For Maintainers)

### 1. Login to npm

```bash
npm login
```

### 2. Publish

```bash
npm publish --access public
```

### 3. Verify

```bash
npm info @iaindex/cli
```

---

## System Requirements

### Minimum Requirements
- **Node.js**: 14.0.0+
- **Disk Space**: ~50 MB (with node_modules)
- **Memory**: 512 MB
- **Network**: Internet connection for API calls

### Recommended Requirements
- **Node.js**: 18.0.0+ (LTS)
- **Disk Space**: 100 MB
- **Memory**: 1 GB

---

## Platform-Specific Notes

### macOS
- ✅ Fully supported
- No additional setup required
- Private key permissions set automatically (600)

### Linux
- ✅ Fully supported
- May need to run with `sudo` for global installation
- Private key permissions set automatically (600)

### Windows
- ✅ Supported with minor differences
- Private key permissions not automatically set
- Use Git Bash or PowerShell
- Paths use backslashes: `C:\Users\...`

---

## Dependencies

### Production Dependencies (Installed Automatically)
- `axios` - HTTP client for API calls
- `chalk` - Terminal colors
- `commander` - CLI framework
- `inquirer` - Interactive prompts
- `ora` - Loading spinners

### Development Dependencies
- `typescript` - TypeScript compiler
- `@types/node` - Node.js type definitions
- `@types/inquirer` - Inquirer type definitions

**Total**: 79 packages
**Size**: ~25 MB in node_modules

---

## Getting Help

### Built-in Help

```bash
iaindex --help
iaindex auth --help
iaindex verify --help
iaindex generate-keys --help
iaindex create-index --help
```

### Documentation

- **README**: Basic usage
- **USAGE_GUIDE**: Comprehensive guide
- **DEMO**: Example outputs
- **TEST_REPORT**: Validation results

### Support

- Documentation: https://docs.iaindex.org
- Issues: https://github.com/iaindex/cli/issues
- API: https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io

---

## Quick Start After Installation

```bash
# 1. Check it works
iaindex --version

# 2. Generate keys
iaindex generate-keys -o ~/iaindex-keys

# 3. Create an index interactively
iaindex create-index --interactive

# 4. Or from a config file
iaindex create-index examples/config.json \
  -s ~/iaindex-keys/iaindex-private.pem \
  -o iaindex.json
```

---

## Upgrading

### From Source

```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli
git pull
npm install
npm run build
```

### From npm (When Published)

```bash
npm update -g @iaindex/cli
```

---

## Verification

### Verify Installation is Complete

Run all these commands successfully:

```bash
✓ iaindex --version          # Should show: 1.0.0
✓ iaindex --help            # Should show: help text
✓ iaindex auth status       # Should show: Not authenticated
✓ npm test                  # Should show: help text
```

If all show expected output, installation is successful! 🎉

---

**Package**: @iaindex/cli v1.0.0
**Location**: /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli/
**Status**: ✅ Ready to Use
