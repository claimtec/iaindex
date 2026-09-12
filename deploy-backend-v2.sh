#!/bin/bash
set -e

echo "🚀 Deploying IAIndex Backend v2.0..."
echo ""

# Check Docker is running
echo "🐳 Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Build Docker image
echo "📦 Building Docker image..."
docker build -t iaindexacr.azurecr.io/iaindex-api:v2.0 -f apps/api/Dockerfile apps/api
echo "✅ Image built successfully"
echo ""

# Login to Azure Container Registry
echo "🔐 Logging into Azure Container Registry..."
az acr login --name iaindexacr
echo "✅ Logged in"
echo ""

# Push image
echo "⬆️  Pushing image to Azure Container Registry..."
docker push iaindexacr.azurecr.io/iaindex-api:v2.0
echo "✅ Image pushed"
echo ""

# Update Container App
echo "🔄 Updating Azure Container App..."
az containerapp update \
  --name aiindex-api \
  --resource-group aiindex-rg \
  --image iaindexacr.azurecr.io/iaindex-api:v2.0
echo "✅ Container App updated"
echo ""

# Wait for deployment
echo "⏳ Waiting for deployment to complete..."
sleep 10
echo ""

# Check health
echo "🏥 Checking API health..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://api.iaindex.org/health)
if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ API is healthy (HTTP $HTTP_STATUS)"
else
    echo "⚠️  API returned HTTP $HTTP_STATUS"
    echo "Check logs: az containerapp logs show -n aiindex-api -g aiindex-rg --follow"
fi
echo ""

echo "🎉 Deployment complete!"
echo ""
echo "📊 Next steps:"
echo "1. Test schema generation: curl -X POST https://api.iaindex.org/v1/schema/generate"
echo "2. Deploy scan tool: cd apps/scan && ./deploy-azure.sh"
echo "3. Monitor logs: az containerapp logs show -n aiindex-api -g aiindex-rg --follow"
echo ""
echo "🌐 Your API: https://api.iaindex.org"
echo "📚 Documentation: https://docs.iaindex.org"
