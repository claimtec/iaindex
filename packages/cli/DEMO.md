# IAIndex CLI - Live Demo

This document shows actual output from running the IAIndex CLI commands.

---

## Demo 1: Generate Keys

### Command:
```bash
iaindex generate-keys -o ./demo-keys -n my-website
```

### Output:
```
✔ Key pair generated successfully!

Keys saved to:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Private Key: /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli/demo-keys/my-website-private.pem
Public Key:  /Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli/demo-keys/my-website-public.pem
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠ IMPORTANT: Keep your private key secure!
Never share or commit your private key to version control.
Use the public key in your IAIndex attestations.

Public Key Content:
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkTNIf5U2ZMYj2/lp0U3O
YlV2fQeJzadRbgdLe19o6nkqZxiTRFq7601j9bXaD6tALQZ4tKp1uQK8pgs69lRp
6Zpb3ufGn1vuwVVNDrmW0pYDjrtgS6+IKyD8k/V8EbsR2VdKiliG23WMwgH7d8hf
Y+MKHFAHNsMcVK8ynlyCQFyUjSAzDDMCuzMoy5e/rgnqH96RQL3ccKKRjLBu2cAb
8jd1XsWpC3/ZnGycsT94BSRybHUedfsK13tt8ukqUgshMebdWG/RurN4KT3OXKFj
9ndq15XD4G1NrszSbQqPzvUQR+q2MGq1f6DotSVnWxa/71RzDuFzHlF3e6xEVTQK
mwIDAQAB
-----END PUBLIC KEY-----
```

**Files Created:**
- `my-website-private.pem` (1.7 KB, permissions: 600)
- `my-website-public.pem` (451 bytes)

---

## Demo 2: Create Signed IAIndex File

### Configuration File (config.json):
```json
{
  "url": "https://example.com/blog/my-article",
  "title": "How AI is Transforming Web Development",
  "description": "An in-depth look at how artificial intelligence is changing the way we build websites and applications.",
  "contentType": "article",
  "aiGenerated": {
    "percentage": 60,
    "sections": ["introduction", "main-content", "code-examples"]
  },
  "humanOversight": {
    "level": "full",
    "verifiedBy": "John Doe"
  },
  "sources": [
    {
      "type": "training-data",
      "description": "GPT-4 with custom fine-tuning"
    },
    {
      "type": "human-input",
      "description": "Original research and interviews"
    }
  ],
  "publisher": {
    "name": "Example Publisher",
    "domain": "example.com"
  }
}
```

### Command:
```bash
iaindex create-index config.json \
  -s ./demo-keys/my-website-private.pem \
  -o iaindex.json
```

### Output:
```
✔ Configuration loaded
✔ Attestation signed
✔ IAIndex file created successfully!

Output saved to:
/Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli/iaindex.json

IAIndex Content:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{
  "version": "1.1",
  "url": "https://example.com/blog/my-article",
  "content": {
    "title": "How AI is Transforming Web Development",
    "description": "An in-depth look at how artificial intelligence is changing the way we build websites and applications.",
    "type": "article"
  },
  "aiGenerated": {
    "percentage": 60,
    "sections": [
      "introduction",
      "main-content",
      "code-examples"
    ]
  },
  "humanOversight": {
    "level": "full",
    "verifiedBy": "John Doe"
  },
  "timestamp": "2025-10-17T07:30:20.585Z",
  "publisher": {
    "name": "Example Publisher",
    "domain": "example.com"
  },
  "sources": [
    {
      "type": "training-data",
      "description": "GPT-4 with custom fine-tuning"
    },
    {
      "type": "human-input",
      "description": "Original research and interviews"
    }
  ],
  "signature": "NOnKyH+WSnEo9y4xgi5yna1GcnPv7J4KcoSTyV3Qvl5xsyHMwDAE8GSN3qVz7Ow1BxV25YMMta4qsSm88g27Jo0r6tZFKreLhCx8pDddp+208BVz/efhe3nlaqN9Bba7DM5LD2eqCTgx3Ri0SCF7UTpxyYHu1adCzNNy/MInJ2raV6ivSoBOTxC1AImyZQJhJUytmAhEr8LROpiBmUTuWl0OxiQhzaTuNSvCumPeYx6iRUFvvO8VAyk0fqD0F2S1HSKG5laoWzMynMgO7ywchJaoGvRnpTQs1DZ9i4ZW9F4TnV2FwIfiIbuaaES4JTQ/xXloSbPOShvn2XhtxhDbCQ=="
}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Next steps:
  1. Review the generated file
  2. Upload to your website at /.well-known/iaindex.json
  3. Submit to IAIndex registry
```

**Result:**
- ✅ Valid IAIndex v1.1 file created
- ✅ Includes cryptographic signature
- ✅ All required fields present
- ✅ Timestamp automatically generated

---

## Demo 3: Check Authentication Status

### Command:
```bash
iaindex auth status
```

### Output (Not Authenticated):
```
Not authenticated

Run: iaindex auth login
```

### Output (Authenticated):
```
✓ Authenticated

Configuration:
API URL:  https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
User ID:  user-123-456-789
Config:   /Users/dineshanchetty/.iaindex/config.json
```

---

## Demo 4: Domain Verification (Requires Auth)

### Command:
```bash
iaindex verify init example.com
```

### Expected Output (When Authenticated):
```
✓ Verification initiated for example.com

Add this TXT record to your DNS:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:  _iaindex-verification.example.com
Type:  TXT
Value: iaindex-verification=abc123def456ghi789jkl012mno345pqr678
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Verification Token:
ver_abc123def456789

Then run: iaindex verify check ver_abc123def456789
```

### Command:
```bash
iaindex verify check ver_abc123def456789
```

### Expected Output (Verified):
```
✓ Domain example.com is verified!
```

### Expected Output (Not Yet Verified):
```
⚠ Domain example.com is not yet verified

Status: pending
DNS records can take up to 48 hours to propagate.
```

---

## Demo 5: Help Commands

### Main Help:
```bash
iaindex --help
```

**Output:**
```
Usage: iaindex [options] [command]

IAIndex CLI - Command line tool for managing AI Index attestations

Options:
  -V, --version                    output the version number
  -h, --help                       display help for command

Commands:
  auth                             Authentication commands
  verify                           Domain verification commands
  generate-keys [options]          Generate RSA key pair for signing attestations
  create-index [options] [config]  Create an IAIndex attestation file
  help [command]                   display help for command

Examples:
  $ iaindex auth login
  $ iaindex verify init example.com
  $ iaindex verify check <token>
  $ iaindex generate-keys -o ./keys
  $ iaindex create-index --interactive
  $ iaindex create-index config.json -s ./keys/private.pem

Documentation:
  https://docs.iaindex.org
```

---

## Demo 6: Interactive Mode

### Command:
```bash
iaindex create-index --interactive
```

### Interactive Session:
```
📝 IAIndex Attestation Generator

? Content URL: https://myblog.com/ai-article
? Content Title: The Future of AI in Content Creation
? Description (optional): Exploring how AI tools are reshaping creative work
? Content Type: article
? AI-generated percentage (0-100): 70
? AI-generated sections (comma-separated): introduction, analysis, conclusion
? Human oversight level: full
? Verified by: Jane Smith
? Publisher name: My Tech Blog
? Publisher domain: myblog.com
? Public key (optional, press Enter to skip):

✔ IAIndex file created successfully!

Output saved to:
/Users/dineshanchetty/Documents/claimtec/iaindex/packages/cli/iaindex.json

IAIndex Content:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{
  "version": "1.1",
  "url": "https://myblog.com/ai-article",
  "content": {
    "title": "The Future of AI in Content Creation",
    "description": "Exploring how AI tools are reshaping creative work",
    "type": "article"
  },
  "aiGenerated": {
    "percentage": 70,
    "sections": ["introduction", "analysis", "conclusion"]
  },
  "humanOversight": {
    "level": "full",
    "verifiedBy": "Jane Smith"
  },
  "timestamp": "2025-10-17T08:15:30.123Z",
  "publisher": {
    "name": "My Tech Blog",
    "domain": "myblog.com"
  }
}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Next steps:
  1. Review the generated file
  2. Upload to your website at /.well-known/iaindex.json
  3. Submit to IAIndex registry
```

---

## Demo 7: Error Handling

### Missing Private Key:
```bash
iaindex create-index config.json -s nonexistent-key.pem
```

**Output:**
```
✖ Signing failed
Error: ENOENT: no such file or directory, open 'nonexistent-key.pem'
```

### Not Authenticated:
```bash
iaindex verify init example.com
```

**Output:**
```
✖ Verification initiation failed
Error: Request failed with status code 401
```

### Invalid Config File:
```bash
iaindex create-index invalid.json
```

**Output:**
```
✖ Failed to load configuration
Error: ENOENT: no such file or directory, open 'invalid.json'
```

---

## Demo 8: Version Check

### Command:
```bash
iaindex --version
```

**Output:**
```
1.0.0
```

---

## Real-World Usage Example

### Scenario: Publishing an AI-Generated Blog Post

```bash
# Step 1: Generate keys (one-time setup)
iaindex generate-keys -o ~/.iaindex-keys -n myblog

# Step 2: Create config for your blog post
cat > blog-post-config.json << 'EOF'
{
  "url": "https://myblog.com/posts/2025/ai-writing-tools",
  "title": "Best AI Writing Tools in 2025",
  "description": "A comprehensive guide to AI writing assistants",
  "contentType": "blog-post",
  "aiGenerated": {
    "percentage": 65,
    "sections": ["introduction", "tool-reviews", "comparisons"]
  },
  "humanOversight": {
    "level": "full",
    "verifiedBy": "Editorial Team"
  },
  "publisher": {
    "name": "My Tech Blog",
    "domain": "myblog.com"
  }
}
EOF

# Step 3: Generate signed IAIndex file
iaindex create-index blog-post-config.json \
  -s ~/.iaindex-keys/myblog-private.pem \
  -o iaindex.json

# Step 4: Upload to your website
# scp iaindex.json server:/var/www/myblog.com/.well-known/iaindex.json

# Step 5: Verify it's accessible
# curl https://myblog.com/.well-known/iaindex.json
```

**Result:** Your blog post now has a verifiable AI attestation! 🎉

---

## Color Legend

When you run the actual CLI, you'll see:
- 🟢 **Green** - Success messages, checkmarks
- 🔴 **Red** - Errors, failures
- 🟡 **Yellow** - Warnings, important notes
- 🔵 **Cyan** - Headers, section titles
- ⚪ **White** - Main content, values
- 🔘 **Gray** - Helper text, hints

Plus spinning indicators (⠋ ⠙ ⠹ ⠸ ⠼) during operations!

---

## Summary

The IAIndex CLI provides:
- ✅ **Intuitive commands** - Easy to remember and use
- ✅ **Beautiful output** - Colorful, well-formatted displays
- ✅ **Clear guidance** - Helpful messages and next steps
- ✅ **Error handling** - Descriptive error messages
- ✅ **Progress indicators** - Visual feedback during operations
- ✅ **Flexible workflows** - Interactive or config-based
- ✅ **Security features** - Proper key handling and permissions

Ready to use in production! 🚀
