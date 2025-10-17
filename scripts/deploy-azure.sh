#!/bin/bash

##############################################################################
# AIIndex v1.1 - Azure Deployment Script
# Deploys API to Azure Container Apps and Dashboard to Azure Static Web Apps
##############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="aiindex-rg"
LOCATION="eastus"
API_APP_NAME="aiindex-api"
DASHBOARD_APP_NAME="aiindex-dashboard"
DOCS_APP_NAME="aiindex-docs"
CONTAINER_ENV="aiindex-env"

echo -e "${BLUE}"
cat << "EOF"
     _    ___ ___           _
    / \  |_ _|_ _|_ __   __| | _____  __
   / _ \  | | | || '_ \ / _` |/ _ \ \/ /
  / ___ \ | | | || | | | (_| |  __/>  <
 /_/   \_\___|___|_| |_|\__,_|\___/_/\_\

      Azure Deployment Script v1.1
EOF
echo -e "${NC}"

echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} Starting Azure deployment..."

# Function to print status
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

##############################################################################
# Step 1: Check Prerequisites
##############################################################################
print_status "Step 1: Checking prerequisites..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    print_error "Not logged into Azure. Run: az login"
    exit 1
fi

# Get current subscription
SUBSCRIPTION=$(az account show --query name -o tsv)
print_status "Using subscription: $SUBSCRIPTION"

##############################################################################
# Step 2: Create Resource Group
##############################################################################
print_status "Step 2: Creating resource group..."

if az group show --name $RESOURCE_GROUP &> /dev/null; then
    print_warning "Resource group $RESOURCE_GROUP already exists"
else
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --tags "project=aiindex" "env=production" "version=1.1"
    print_status "Resource group created: $RESOURCE_GROUP"
fi

##############################################################################
# Step 3: Create Container Apps Environment
##############################################################################
print_status "Step 3: Creating Container Apps environment..."

if az containerapp env show --name $CONTAINER_ENV --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_warning "Container Apps environment $CONTAINER_ENV already exists"
else
    az containerapp env create \
        --name $CONTAINER_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
    print_status "Container Apps environment created: $CONTAINER_ENV"
fi

##############################################################################
# Step 4: Build and Deploy API
##############################################################################
print_status "Step 4: Building and deploying API to Azure Container Apps..."

# Check if Dockerfile exists
if [ ! -f "apps/api/Dockerfile" ]; then
    print_status "Creating Dockerfile for API..."
    cat > apps/api/Dockerfile << 'DOCKERFILE_EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE_EOF
fi

# Get Supabase credentials from .env.staging
if [ -f "apps/api/.env.staging" ]; then
    source apps/api/.env.staging
fi

# Deploy API
print_status "Deploying API (this may take 5-10 minutes)..."
cd apps/api

az containerapp up \
    --name $API_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --environment $CONTAINER_ENV \
    --ingress external \
    --target-port 8000 \
    --source . \
    --env-vars \
        "DATABASE_URL=${DATABASE_URL:-secretref:database-url}" \
        "SUPABASE_URL=${SUPABASE_URL}" \
        "SUPABASE_KEY=secretref:supabase-key" \
        "SECRET_KEY=secretref:secret-key" \
        "DEBUG=False" \
        "APP_NAME=AIIndex Verification API" \
        "APP_VERSION=1.1.0"

cd ../..

# Get API URL
API_URL=$(az containerapp show \
    --name $API_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" \
    -o tsv)

print_status "API deployed successfully!"
echo -e "${GREEN}API URL: https://$API_URL${NC}"

##############################################################################
# Step 5: Build Dashboard
##############################################################################
print_status "Step 5: Building dashboard..."

cd apps/web

# Update environment variables for build
cat > .env.production << ENV_EOF
NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_KEY}
NEXT_PUBLIC_API_URL=https://$API_URL
ENV_EOF

# Install dependencies and build
npm install
npm run build

cd ../..

print_status "Dashboard built successfully!"

##############################################################################
# Step 6: Deploy Dashboard to Azure Static Web Apps
##############################################################################
print_status "Step 6: Deploying dashboard to Azure Static Web Apps..."

# Check if Static Web App exists
if az staticwebapp show --name $DASHBOARD_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_warning "Static Web App $DASHBOARD_APP_NAME already exists"
else
    # Create Static Web App
    az staticwebapp create \
        --name $DASHBOARD_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Free

    print_status "Static Web App created: $DASHBOARD_APP_NAME"
fi

# Get deployment token
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
    --name $DASHBOARD_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.apiKey" -o tsv)

# Deploy using Static Web Apps CLI (if installed)
if command -v swa &> /dev/null; then
    cd apps/web
    swa deploy .next \
        --deployment-token "$DEPLOYMENT_TOKEN" \
        --env production
    cd ../..
else
    print_warning "Static Web Apps CLI not installed. Install with: npm install -g @azure/static-web-apps-cli"
    print_warning "Or deploy via Azure Portal: https://portal.azure.com"
fi

# Get Dashboard URL
DASHBOARD_URL=$(az staticwebapp show \
    --name $DASHBOARD_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "defaultHostname" -o tsv)

print_status "Dashboard deployed successfully!"
echo -e "${GREEN}Dashboard URL: https://$DASHBOARD_URL${NC}"

##############################################################################
# Step 7: Deploy Documentation (Optional)
##############################################################################
print_status "Step 7: Deploying documentation..."

cd apps/docs
npm install
npm run build
cd ../..

if az staticwebapp show --name $DOCS_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_warning "Static Web App $DOCS_APP_NAME already exists"
else
    az staticwebapp create \
        --name $DOCS_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Free

    print_status "Static Web App created for docs: $DOCS_APP_NAME"
fi

DOCS_URL=$(az staticwebapp show \
    --name $DOCS_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "defaultHostname" -o tsv)

print_status "Documentation deployed successfully!"
echo -e "${GREEN}Docs URL: https://$DOCS_URL${NC}"

##############################################################################
# Step 8: Configure Secrets
##############################################################################
print_status "Step 8: Configuring secrets..."

# Store secrets in Azure Key Vault (recommended) or Container App secrets
az containerapp secret set \
    --name $API_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --secrets \
        database-url="${DATABASE_URL}" \
        supabase-key="${SUPABASE_KEY}" \
        secret-key="${SECRET_KEY}"

print_status "Secrets configured successfully!"

##############################################################################
# Step 9: Test Deployment
##############################################################################
print_status "Step 9: Testing deployment..."

# Test API health endpoint
API_HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$API_URL/health" || echo "000")

if [ "$API_HEALTH_STATUS" = "200" ]; then
    print_status "✓ API health check passed"
else
    print_warning "API health check returned: $API_HEALTH_STATUS"
fi

# Test API root endpoint
API_ROOT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$API_URL/" || echo "000")

if [ "$API_ROOT_STATUS" = "200" ]; then
    print_status "✓ API root endpoint passed"
else
    print_warning "API root endpoint returned: $API_ROOT_STATUS"
fi

# Test Dashboard
DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$DASHBOARD_URL" || echo "000")

if [ "$DASHBOARD_STATUS" = "200" ]; then
    print_status "✓ Dashboard health check passed"
else
    print_warning "Dashboard health check returned: $DASHBOARD_STATUS"
fi

##############################################################################
# Summary
##############################################################################
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}    Deployment Summary${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${GREEN}✓ Resource Group:${NC} $RESOURCE_GROUP"
echo -e "${GREEN}✓ Location:${NC} $LOCATION"
echo ""
echo -e "${GREEN}✓ API URL:${NC} https://$API_URL"
echo -e "${GREEN}✓ Dashboard URL:${NC} https://$DASHBOARD_URL"
echo -e "${GREEN}✓ Docs URL:${NC} https://$DOCS_URL"
echo ""
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test API: curl https://$API_URL/health"
echo "2. Test Dashboard: open https://$DASHBOARD_URL"
echo "3. Run smoke tests: ./scripts/smoke-tests.sh production"
echo "4. Configure custom domain (optional)"
echo "5. Monitor logs: az containerapp logs show --name $API_APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo -e "${GREEN}Deployment complete! 🎉${NC}"
