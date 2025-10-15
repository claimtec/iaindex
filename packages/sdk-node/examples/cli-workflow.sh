#!/bin/bash
# Example workflow using the aiindex-gen CLI tool

echo "AIIndex CLI Workflow Example"
echo "=============================="
echo ""

# Step 1: Initialize configuration
echo "Step 1: Initialize configuration"
npx aiindex-gen init
echo ""

# Step 2: Edit the configuration file
echo "Step 2: Edit aiindex.config.json with your service details"
echo "(Skipping for this example)"
echo ""

# Step 3: Build AI Index file
echo "Step 3: Build AI Index file"
npx aiindex-gen build --url https://example.com
echo ""

# Step 4: Verify the generated file
echo "Step 4: Verify the generated file"
npx aiindex-gen verify ai-index.json
echo ""

# Step 5: Generate keys and sign
echo "Step 5: Generate keys and sign the file"
npx aiindex-gen sign --generate-keys
echo ""

# Step 6: Verify signature
echo "Step 6: Verify signature"
npx aiindex-gen verify ai-index.json --check-signature
echo ""

# Step 7: Start webhook server
echo "Step 7: Start webhook server (Ctrl+C to stop)"
npx aiindex-gen serve --port 3000 --forward
