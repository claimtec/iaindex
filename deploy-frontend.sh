#!/bin/bash
set -e

# Azure Configuration
RESOURCE_GROUP="aiindex-rg"
LOCATION="eastus"
ACR_NAME="cafc3cb1336eacr"
ENVIRONMENT_NAME="aiindex-env"

# App Configuration
WEB_APP_NAME="iaindex-dashboard"
SCAN_APP_NAME="iaindex-scan"

echo "===== Building and Deploying Frontend Apps to Azure Container Apps ====="

# Login to Azure
echo "Logging into Azure..."
az account show || az login

# Login to ACR
echo "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

# Build and push web app
echo "Building web app..."
cd apps/web
docker buildx build --platform linux/amd64 -t $ACR_NAME.azurecr.io/iaindex-web:latest --push .
cd ../..

# Build and push scan app
echo "Building scan app..."
cd apps/scan
docker buildx build --platform linux/amd64 -t $ACR_NAME.azurecr.io/iaindex-scan:latest --push .
cd ../..

# Check if web container app exists
WEB_EXISTS=$(az containerapp show --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP 2>/dev/null && echo "yes" || echo "no")

if [ "$WEB_EXISTS" = "yes" ]; then
  echo "Updating existing web app..."
  az containerapp update \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_NAME.azurecr.io/iaindex-web:latest \
    --set-env-vars \
      NEXT_PUBLIC_SUPABASE_URL="https://uskaaxzhbijpvpgzubbp.supabase.co" \
      NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVza2FheHpoYmlqcHZwZ3p1YmJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NDUyODMsImV4cCI6MjA3NjMyMTI4M30.56CpnkPNRG4BYreMswYvDlaTmOXcjns2qkiiEA__wKY" \
      NEXT_PUBLIC_API_URL="https://api.iaindex.org"
else
  echo "Creating new web app..."
  az containerapp create \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_NAME.azurecr.io/iaindex-web:latest \
    --target-port 3000 \
    --ingress external \
    --registry-server $ACR_NAME.azurecr.io \
    --env-vars \
      NEXT_PUBLIC_SUPABASE_URL="https://uskaaxzhbijpvpgzubbp.supabase.co" \
      NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVza2FheHpoYmlqcHZwZ3p1YmJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NDUyODMsImV4cCI6MjA3NjMyMTI4M30.56CpnkPNRG4BYreMswYvDlaTmOXcjns2qkiiEA__wKY" \
      NEXT_PUBLIC_API_URL="https://api.iaindex.org" \
    --cpu 0.5 \
    --memory 1Gi \
    --min-replicas 1 \
    --max-replicas 3
fi

# Check if scan container app exists
SCAN_EXISTS=$(az containerapp show --name $SCAN_APP_NAME --resource-group $RESOURCE_GROUP 2>/dev/null && echo "yes" || echo "no")

if [ "$SCAN_EXISTS" = "yes" ]; then
  echo "Updating existing scan app..."
  az containerapp update \
    --name $SCAN_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_NAME.azurecr.io/iaindex-scan:latest \
    --set-env-vars \
      NEXT_PUBLIC_SUPABASE_URL="https://uskaaxzhbijpvpgzubbp.supabase.co" \
      NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVza2FheHpoYmlqcHZwZ3p1YmJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NDUyODMsImV4cCI6MjA3NjMyMTI4M30.56CpnkPNRG4BYreMswYvDlaTmOXcjns2qkiiEA__wKY" \
      NEXT_PUBLIC_API_URL="https://api.iaindex.org"
else
  echo "Creating new scan app..."
  az containerapp create \
    --name $SCAN_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_NAME.azurecr.io/iaindex-scan:latest \
    --target-port 3000 \
    --ingress external \
    --registry-server $ACR_NAME.azurecr.io \
    --env-vars \
      NEXT_PUBLIC_SUPABASE_URL="https://uskaaxzhbijpvpgzubbp.supabase.co" \
      NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVza2FheHpoYmlqcHZwZ3p1YmJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NDUyODMsImV4cCI6MjA3NjMyMTI4M30.56CpnkPNRG4BYreMswYvDlaTmOXcjns2qkiiEA__wKY" \
      NEXT_PUBLIC_API_URL="https://api.iaindex.org" \
    --cpu 0.5 \
    --memory 1Gi \
    --min-replicas 1 \
    --max-replicas 3
fi

# Get URLs
echo ""
echo "===== Deployment Complete ====="
echo ""
echo "Web Dashboard URL:"
az containerapp show --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv 2>/dev/null || echo "Not deployed as container app"
echo ""
echo "Scan App URL:"
az containerapp show --name $SCAN_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv 2>/dev/null || echo "Not deployed as container app"
