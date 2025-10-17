#!/bin/bash

# IAIndex CLI Test Script
# This script demonstrates all CLI commands

echo "=========================================="
echo "IAIndex CLI Test Suite"
echo "=========================================="
echo ""

# Test 1: Help
echo "Test 1: Display help"
echo "Command: iaindex --help"
node bin/iaindex.js --help
echo ""
echo "----------------------------------------"
echo ""

# Test 2: Auth status
echo "Test 2: Check authentication status"
echo "Command: iaindex auth status"
node bin/iaindex.js auth status
echo ""
echo "----------------------------------------"
echo ""

# Test 3: Generate keys
echo "Test 3: Generate RSA key pair"
echo "Command: iaindex generate-keys -o test-output -n demo"
node bin/iaindex.js generate-keys -o test-output -n demo
echo ""
echo "----------------------------------------"
echo ""

# Test 4: Create index from config
echo "Test 4: Create IAIndex from config file (with signing)"
echo "Command: iaindex create-index examples/config.json -o test-output/demo-iaindex.json -s test-output/demo-private.pem"
node bin/iaindex.js create-index examples/config.json -o test-output/demo-iaindex.json -s test-output/demo-private.pem
echo ""
echo "----------------------------------------"
echo ""

# Test 5: Create index without signing
echo "Test 5: Create IAIndex from config file (no signing)"
echo "Command: iaindex create-index examples/config.json -o test-output/unsigned-iaindex.json"
node bin/iaindex.js create-index examples/config.json -o test-output/unsigned-iaindex.json
echo ""
echo "----------------------------------------"
echo ""

echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo ""
echo "Generated Files:"
ls -lh test-output/
echo ""
echo "Keys generated:"
echo "  - test-output/demo-private.pem"
echo "  - test-output/demo-public.pem"
echo ""
echo "IAIndex files created:"
echo "  - test-output/demo-iaindex.json (signed)"
echo "  - test-output/unsigned-iaindex.json (unsigned)"
echo ""
echo "Configuration location: ~/.iaindex/config.json"
echo ""
echo "=========================================="
echo "API Commands (require authentication):"
echo "=========================================="
echo ""
echo "To test API commands, first authenticate:"
echo "  iaindex auth login"
echo ""
echo "Then try:"
echo "  iaindex verify init yourdomain.com"
echo "  iaindex verify check <token>"
echo ""
