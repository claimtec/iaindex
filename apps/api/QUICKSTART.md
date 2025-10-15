# Quick Start Guide

Get the IA Index Verification API up and running in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- Supabase account (free tier works)
- Terminal/command line access

## Setup Steps

### 1. Install Dependencies

```bash
# Navigate to API directory
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Minimum required configuration:**
```bash
SECRET_KEY=your-super-secret-key-min-32-chars
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### 3. Set Up Database

Create these tables in Supabase SQL editor:

```sql
-- Publishers table
CREATE TABLE publishers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  domain TEXT UNIQUE NOT NULL,
  verification_token TEXT,
  verification_method TEXT,
  contact_email TEXT,
  status TEXT NOT NULL,
  verified BOOLEAN DEFAULT FALSE,
  verified_at TIMESTAMPTZ,
  verification_key TEXT,
  signature_method TEXT DEFAULT 'hmac',
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Receipts table
CREATE TABLE receipts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  receipt_id TEXT UNIQUE NOT NULL,
  publisher_domain TEXT NOT NULL,
  article_url TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  signature TEXT NOT NULL,
  status TEXT NOT NULL,
  verified BOOLEAN DEFAULT FALSE,
  receipt_hash TEXT,
  merkle_root TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Attestations table
CREATE TABLE attestations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date DATE UNIQUE NOT NULL,
  merkle_root TEXT NOT NULL,
  receipt_count INTEGER NOT NULL,
  verified_count INTEGER NOT NULL,
  tree_height INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_receipts_domain ON receipts(publisher_domain);
CREATE INDEX idx_receipts_timestamp ON receipts(timestamp);
CREATE INDEX idx_receipts_status ON receipts(status);
CREATE INDEX idx_publishers_domain ON publishers(domain);
CREATE INDEX idx_attestations_date ON attestations(date);
```

### 4. Run the API

**Option A: Using Make (recommended)**
```bash
make dev
```

**Option B: Using run script**
```bash
./run.sh dev
```

**Option C: Direct uvicorn**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the API

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or test with curl:
```bash
curl http://localhost:8000/health
```

## First API Calls

### 1. Get API Token

```bash
curl -X POST "http://localhost:8000/v1/auth/login?username=admin&password=changeme"
```

Save the returned token for subsequent requests.

### 2. Verify a Publisher Domain

```bash
curl -X POST "http://localhost:8000/v1/publishers/verify" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "method": "dns_txt"
  }'
```

Follow the instructions to add DNS TXT record.

### 3. Submit a Receipt

```bash
curl -X POST "http://localhost:8000/v1/receipts/ingest" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receipt_id": "rec_test_001",
    "publisher_domain": "example.com",
    "article_url": "https://example.com/article-1",
    "timestamp": "2025-10-13T10:00:00Z",
    "signature": "test-signature-hmac-sha256",
    "metadata": {
      "author": "John Doe",
      "category": "news"
    }
  }'
```

## Docker Deployment

### Quick Docker Start

```bash
# Build image
docker build -t iaindex-api .

# Run container
docker run -p 8000:8000 --env-file .env iaindex-api
```

### Docker Compose (Production)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Useful Commands

```bash
# Development server with auto-reload
make dev

# Production server (4 workers)
make prod

# Run tests
make test

# Format code
make format

# Clean temp files
make clean

# View all available commands
make help
```

## Next Steps

1. **Explore API Documentation**: Visit http://localhost:8000/docs
2. **Configure Security**: Change default SECRET_KEY and credentials
3. **Set Up CORS**: Update CORS_ORIGINS in .env for your frontend
4. **Enable Rate Limiting**: Configure Redis for production rate limiting
5. **Monitor Logs**: Check application logs for any issues
6. **Set Up Monitoring**: Integrate with your monitoring solution

## Common Issues

### Port Already in Use
```bash
# Change port in .env or command
uvicorn src.main:app --reload --port 8001
```

### Import Errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Connection Issues
- Verify Supabase URL and key in .env
- Check if tables are created correctly
- Ensure Supabase project is active

## Support

- **Documentation**: http://localhost:8000/docs
- **API Reference**: http://localhost:8000/redoc
- **Full README**: See README.md in this directory

## Security Notes

Before deploying to production:

1. Change SECRET_KEY to a strong random value
2. Update default login credentials
3. Enable HTTPS only
4. Set DEBUG=False
5. Configure proper CORS origins
6. Implement rate limiting with Redis
7. Enable Supabase Row Level Security

---

**Happy coding!** For detailed information, see [README.md](README.md)
