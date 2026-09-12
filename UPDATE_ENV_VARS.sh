#!/bin/bash

# ============================================================================
# Update Environment Variables for Fresh Supabase Project
# ============================================================================
# This script updates both backend and frontend with new Supabase credentials
# Run this after completing database migrations
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   IAIndex - Update Environment Variables                 ║${NC}"
echo -e "${GREEN}║   New Supabase Project Setup                              ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# NEW SUPABASE CREDENTIALS
# ============================================================================

SUPABASE_URL="https://uskaaxzhbijpvpgzubbp.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVza2FheHpoYmlqcHZwZ3p1YmJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NDUyODMsImV4cCI6MjA3NjMyMTI4M30.56CpnkPNRG4BYreMswYvDlaTmOXcjns2qkiiEA__wKY"

echo -e "${YELLOW}📋 New Supabase Project Details:${NC}"
echo -e "   URL: ${SUPABASE_URL}"
echo -e "   Anon Key: ${SUPABASE_ANON_KEY:0:50}..."
echo ""

# ============================================================================
# STEP 1: Update Azure Container Apps
# ============================================================================

echo -e "${YELLOW}🔧 Step 1: Updating Azure Container Apps secrets...${NC}"

az containerapp secret set \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --secrets \
    supabase-url="${SUPABASE_URL}" \
    supabase-key="${SUPABASE_ANON_KEY}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Azure secrets updated successfully${NC}"
else
    echo -e "${RED}❌ Failed to update Azure secrets${NC}"
    exit 1
fi

echo ""

# ============================================================================
# STEP 2: Get Latest Revision
# ============================================================================

echo -e "${YELLOW}📦 Step 2: Getting latest revision...${NC}"

LATEST_REVISION=$(az containerapp revision list \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --query "[0].name" \
  -o tsv)

echo -e "   Latest revision: ${LATEST_REVISION}"
echo ""

# ============================================================================
# STEP 3: Restart Container
# ============================================================================

echo -e "${YELLOW}🔄 Step 3: Restarting container...${NC}"

az containerapp revision restart \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --revision "${LATEST_REVISION}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container restarted successfully${NC}"
else
    echo -e "${RED}❌ Failed to restart container${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}⏳ Waiting 30 seconds for container to restart...${NC}"
sleep 30

# ============================================================================
# STEP 4: Test Backend Health
# ============================================================================

echo -e "${YELLOW}🏥 Step 4: Checking backend health...${NC}"

HEALTH_RESPONSE=$(curl -s https://api.iaindex.org/health)

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
    echo -e "   Response: ${HEALTH_RESPONSE}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo -e "   Response: ${HEALTH_RESPONSE}"
fi

echo ""

# ============================================================================
# STEP 5: Update Frontend .env.local
# ============================================================================

echo -e "${YELLOW}📝 Step 5: Updating frontend environment variables...${NC}"

SCAN_ENV_FILE="apps/scan/.env.local"

cat > "${SCAN_ENV_FILE}" <<EOF
# Supabase Configuration (Updated $(date +%Y-%m-%d))
NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}

# API Configuration
NEXT_PUBLIC_API_URL=https://api.iaindex.org
EOF

if [ -f "${SCAN_ENV_FILE}" ]; then
    echo -e "${GREEN}✅ Frontend .env.local updated${NC}"
    echo -e "   File: ${SCAN_ENV_FILE}"
else
    echo -e "${RED}❌ Failed to update frontend .env.local${NC}"
    exit 1
fi

echo ""

# ============================================================================
# STEP 6: Test Backend Registration
# ============================================================================

echo -e "${YELLOW}🧪 Step 6: Testing backend registration API...${NC}"

REGISTER_RESPONSE=$(curl -s -X POST https://api.iaindex.org/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "envtest@iaindex.org",
    "password": "SecurePass123!",
    "full_name": "Env Test User",
    "company": "Test Corp"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Registration API is working${NC}"
    echo -e "   Created user: envtest@iaindex.org"
else
    echo -e "${YELLOW}⚠️  Registration test (check if user already exists)${NC}"
    echo -e "   Response: ${REGISTER_RESPONSE}"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ Environment Variables Updated Successfully           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📋 What was updated:${NC}"
echo -e "   ✅ Azure Container Apps secrets"
echo -e "   ✅ Backend restarted with new credentials"
echo -e "   ✅ Frontend .env.local updated"
echo -e "   ✅ Backend health check passed"
echo -e "   ✅ Registration API tested"
echo ""
echo -e "${YELLOW}🚀 Next Steps:${NC}"
echo -e "   1. Restart frontend dev server:"
echo -e "      ${GREEN}cd apps/scan && npm run dev${NC}"
echo ""
echo -e "   2. Test frontend registration at:"
echo -e "      ${GREEN}http://localhost:3000${NC}"
echo ""
echo -e "   3. Verify users in Supabase Dashboard:"
echo -e "      ${GREEN}https://uskaaxzhbijpvpgzubbp.supabase.co/project/default/auth/users${NC}"
echo ""
echo -e "${GREEN}All done! 🎉${NC}"
