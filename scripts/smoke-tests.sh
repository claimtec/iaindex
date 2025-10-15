#!/bin/bash

# AIIndex v1.1 Smoke Tests
# Usage: ./smoke-tests.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}

# Set base URLs based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    API_URL="https://api.aiindex.org"
    WEB_URL="https://aiindex.org"
    DOCS_URL="https://docs.aiindex.org"
else
    API_URL="https://aiindex-api-staging.fly.dev"
    WEB_URL="https://aiindex-staging.vercel.app"
    DOCS_URL="https://docs-aiindex-staging.netlify.app"
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    TESTS_RUN=$((TESTS_RUN + 1))

    printf "Testing: %-50s " "$name"

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")

    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_code, got $response)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test with headers
test_endpoint_with_headers() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    TESTS_RUN=$((TESTS_RUN + 1))

    printf "Testing: %-50s " "$name"

    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "X-AIIndex-Version: v1.1" \
        -H "X-AIIndex-Client-ID: smoke-test" \
        "$url" || echo "000")

    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_code, got $response)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo "============================================"
echo "AIIndex v1.1 Smoke Tests - $ENVIRONMENT"
echo "============================================"
echo ""

# API Tests
echo "=== API Tests ($API_URL) ==="
test_endpoint "Health check" "$API_URL/health"
test_endpoint "API root" "$API_URL/"
test_endpoint "Verified domains" "$API_URL/v1/verified-domains"
test_endpoint_with_headers "Version negotiation (v1.1)" "$API_URL/v1/verified-domains"
test_endpoint "OpenAPI docs" "$API_URL/docs"
echo ""

# Dashboard Tests
echo "=== Dashboard Tests ($WEB_URL) ==="
test_endpoint "Home page" "$WEB_URL/"
test_endpoint "Login page" "$WEB_URL/login"
echo ""

# Documentation Tests
echo "=== Documentation Tests ($DOCS_URL) ==="
test_endpoint "Docs home" "$DOCS_URL/"
test_endpoint "Intro page" "$DOCS_URL/intro"
echo ""

# Summary
echo "============================================"
echo "Test Summary"
echo "============================================"
echo "Total tests run: $TESTS_RUN"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
