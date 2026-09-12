#!/bin/bash
set -e

echo "🚀 Deploying IAIndex Free Scan Tool to Azure Static Web Apps..."

# Configuration
RESOURCE_GROUP="iaindex-rg"
LOCATION="eastus"
APP_NAME="iaindex-scan"

# Build the Next.js app
echo "📦 Building Next.js application..."
npm run build

# Check if Static Web App exists
echo "🔍 Checking if Static Web App exists..."
if az staticwebapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "✅ Static Web App already exists"
else
    echo "📝 Creating Static Web App..."
    az staticwebapp create \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Free \
        --source https://github.com/dineshanchetty/iaindex \
        --branch main \
        --app-location "/apps/scan" \
        --output-location ".next" \
        --login-with-github
fi

# Get deployment token
echo "🔑 Getting deployment token..."
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.apiKey" -o tsv)

echo "📤 Deploying to Azure Static Web Apps..."
npx @azure/static-web-apps-cli deploy \
    --app-location . \
    --output-location .next \
    --deployment-token $DEPLOYMENT_TOKEN

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at: https://$APP_NAME.azurestaticapps.net"
echo ""
echo "Next steps:"
echo "1. Configure custom domain: scan.iaindex.org"
echo "2. Add CNAME record pointing to: $APP_NAME.azurestaticapps.net"
echo "3. Verify custom domain in Azure Portal"
