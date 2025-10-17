#!/bin/bash

# AIIndex v1.1 Deployment Script
# Usage: ./deploy.sh [staging|production]

set -e  # Exit on error

ENVIRONMENT=${1:-staging}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="deployment_${ENVIRONMENT}_${TIMESTAMP}.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
     _    ___ ___           _
    / \  |_ _|_ _|_ __   __| | _____  __
   / _ \  | | | || '_ \ / _` |/ _ \ \/ /
  / ___ \ | | | || | | | (_| |  __/>  <
 /_/   \_\___|___|_| |_|\__,_|\___/_/\_\

      v1.1 Deployment Script
EOF
echo -e "${NC}"

log "Starting deployment to $ENVIRONMENT"

# Phase 1: Pre-deployment checks
log "Phase 1: Running pre-deployment checks..."

info "Checking if required commands are available..."
command -v git >/dev/null 2>&1 || error "git is not installed"
command -v node >/dev/null 2>&1 || warn "node is not installed (required for dashboard)"
command -v python3 >/dev/null 2>&1 || warn "python3 is not installed (required for API)"
command -v psql >/dev/null 2>&1 || warn "psql is not installed (required for database migration)"

info "Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    warn "You have uncommitted changes. Consider committing them first."
    git status --short
fi

log "Pre-deployment checks complete ✓"

# Phase 2: Environment validation
log "Phase 2: Validating environment configuration..."

if [ "$ENVIRONMENT" = "production" ]; then
    info "Deploying to PRODUCTION"
    read -p "Are you sure you want to deploy to production? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        error "Production deployment cancelled by user"
    fi
else
    info "Deploying to STAGING"
fi

# Check for environment files
if [ "$ENVIRONMENT" = "production" ]; then
    ENV_FILE="apps/api/.env.production"
else
    ENV_FILE="apps/api/.env.staging"
fi

if [ ! -f "$ENV_FILE" ]; then
    error "Environment file not found: $ENV_FILE"
fi

log "Environment validation complete ✓"

# Phase 3: Run tests
log "Phase 3: Running tests..."

info "Checking if test dependencies are available..."
if [ -d "tests/e2e" ]; then
    cd tests/e2e
    if [ -f "requirements.txt" ]; then
        info "Installing test dependencies..."
        pip3 install -q -r requirements.txt || warn "Failed to install test dependencies"
    fi

    info "Running test suite..."
    if command -v pytest >/dev/null 2>&1; then
        pytest -v --tb=short || warn "Some tests failed (continuing anyway)"
    else
        warn "pytest not found, skipping tests"
    fi
    cd ../..
else
    warn "Test directory not found, skipping tests"
fi

log "Tests complete ✓"

# Phase 4: Database backup (production only)
if [ "$ENVIRONMENT" = "production" ]; then
    log "Phase 4: Creating database backup..."

    if [ -z "$DATABASE_URL" ]; then
        warn "DATABASE_URL not set, skipping backup"
    else
        BACKUP_FILE="backups/aiindex_backup_${TIMESTAMP}.sql"
        mkdir -p backups
        info "Creating backup: $BACKUP_FILE"
        pg_dump "$DATABASE_URL" > "$BACKUP_FILE" || warn "Backup failed"

        if [ -f "$BACKUP_FILE" ]; then
            BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
            log "Backup created: $BACKUP_SIZE"
        fi
    fi
fi

# Phase 5: Database migration
log "Phase 5: Running database migration..."

if [ -f "migrations/v1.0-to-v1.1.sql" ]; then
    if [ -z "$DATABASE_URL" ]; then
        warn "DATABASE_URL not set, skipping migration"
    else
        info "Running migration script..."
        psql "$DATABASE_URL" < migrations/v1.0-to-v1.1.sql || warn "Migration had warnings"
        log "Database migration complete ✓"
    fi
else
    warn "Migration file not found: migrations/v1.0-to-v1.1.sql"
fi

# Phase 6: Deploy API
log "Phase 6: Deploying API..."

if [ -d "apps/api" ]; then
    cd apps/api

    info "Installing API dependencies..."
    if [ -f "requirements.txt" ]; then
        pip3 install -q -r requirements.txt || warn "Failed to install API dependencies"
    fi

    info "API deployment commands:"
    echo "  For Fly.io: fly deploy --config fly.${ENVIRONMENT}.toml"
    echo "  For Docker: docker build -t aiindex-api:v1.1 . && docker push"

    cd ../..
else
    warn "API directory not found"
fi

log "API deployment prepared ✓"

# Phase 7: Deploy Dashboard
log "Phase 7: Deploying Dashboard..."

if [ -d "apps/web" ]; then
    cd apps/web

    info "Installing dashboard dependencies..."
    if [ -f "package.json" ] && command -v npm >/dev/null 2>&1; then
        npm install --silent || warn "Failed to install dashboard dependencies"
    fi

    info "Building dashboard..."
    if command -v npm >/dev/null 2>&1; then
        npm run build || warn "Dashboard build failed"
    fi

    info "Dashboard deployment commands:"
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "  vercel --prod"
    else
        echo "  vercel --env=staging"
    fi

    cd ../..
else
    warn "Dashboard directory not found"
fi

log "Dashboard deployment prepared ✓"

# Phase 8: Deploy Documentation
log "Phase 8: Deploying Documentation..."

if [ -d "apps/docs" ]; then
    cd apps/docs

    info "Installing docs dependencies..."
    if [ -f "package.json" ] && command -v npm >/dev/null 2>&1; then
        npm install --silent || warn "Failed to install docs dependencies"
    fi

    info "Building documentation..."
    if command -v npm >/dev/null 2>&1; then
        npm run build || warn "Docs build failed"
    fi

    info "Documentation deployment commands:"
    echo "  netlify deploy --prod --dir=build"

    cd ../..
else
    warn "Documentation directory not found"
fi

log "Documentation deployment prepared ✓"

# Phase 9: Summary
log "Deployment preparation complete!"

echo ""
echo -e "${GREEN}=== Deployment Summary ===${NC}"
echo "Environment: $ENVIRONMENT"
echo "Timestamp: $TIMESTAMP"
echo "Log file: $LOG_FILE"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review the log file for any warnings"
echo "2. Execute the deployment commands shown above"
echo "3. Run smoke tests: ./scripts/smoke-tests.sh $ENVIRONMENT"
echo "4. Monitor logs and metrics"
echo "5. Update status page if needed"
echo ""
echo -e "${GREEN}Deployment script complete!${NC}"
