# IA Index Verification API

A FastAPI-based verification system for receipt management, publisher verification, and cryptographic attestations.

## Features

### Core Functionality
- **Receipt Ingestion & Verification**: Accept and verify publisher receipts with cryptographic signatures
- **Publisher Domain Verification**: Verify domain ownership via DNS TXT records, HTML meta tags, or file upload
- **Analytics Dashboard**: Track receipt statistics, verification rates, and publisher activity
- **Merkle Tree Attestations**: Generate daily Merkle roots for cryptographic proof of receipts
- **Authentication**: JWT token and API key-based authentication
- **Rate Limiting**: Protection against API abuse with configurable limits

### Security Features
- HMAC and RSA signature verification
- JWT token authentication
- API key validation
- CORS configuration
- Request validation with Pydantic models
- Secure token generation for domain verification

## API Endpoints

### Authentication
- `POST /v1/auth/login` - Login and obtain JWT token

### Receipt Management
- `POST /v1/receipts/ingest` - Verify and store receipts
- `GET /v1/receipts` - List receipts with filters (domain, date range, status)

### Publisher Verification
- `POST /v1/publishers/verify` - Initiate domain verification
- `GET /v1/publishers/verify/{token}` - Check verification status
- `GET /v1/verified-domains` - Public list of verified publishers

### Analytics
- `GET /v1/analytics` - Publisher-specific analytics
- `GET /v1/analytics/summary` - System-wide analytics

### Attestations
- `GET /v1/attestations/{date}` - Get Merkle root for specific date
- `GET /v1/attestations/{date}/receipts/{receipt_id}/proof` - Get Merkle proof for receipt
- `GET /v1/attestations` - List all attestations

### System
- `GET /health` - Health check endpoint
- `GET /` - API information
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Installation

### Prerequisites
- Python 3.11+
- Supabase account
- DNS access for domain verification

### Local Development

1. **Clone and navigate to the API directory**
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/apps/api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the development server**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Deployment

1. **Build the Docker image**
```bash
docker build -t iaindex-api .
```

2. **Run with Docker Compose**
```bash
docker-compose up -d
```

3. **View logs**
```bash
docker-compose logs -f api
```

4. **Stop services**
```bash
docker-compose down
```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# CORS
CORS_ORIGINS=http://localhost:3000,https://iaindex.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60/minute
RATE_LIMIT_PER_HOUR=1000/hour

# Verification
VERIFICATION_TOKEN_EXPIRY_HOURS=48
DNS_VERIFICATION_PREFIX=iaindex-verification
```

## Database Schema

### Required Supabase Tables

**publishers**
```sql
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
```

**receipts**
```sql
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
```

**attestations**
```sql
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
```

## Usage Examples

### 1. Publisher Domain Verification

```bash
# Initiate verification
curl -X POST "http://localhost:8000/v1/publishers/verify" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "method": "dns_txt",
    "contact_email": "admin@example.com"
  }'

# Response includes verification token and instructions
# Add DNS TXT record: iaindex-verification=<token>

# Check verification status
curl "http://localhost:8000/v1/publishers/verify/{token}"
```

### 2. Receipt Ingestion

```bash
curl -X POST "http://localhost:8000/v1/receipts/ingest" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "receipt_id": "rec_123456",
    "publisher_domain": "example.com",
    "article_url": "https://example.com/article",
    "timestamp": "2025-10-13T10:00:00Z",
    "signature": "hmac-signature-here",
    "metadata": {
      "author": "John Doe",
      "category": "news"
    }
  }'
```

### 3. Get Analytics

```bash
# Publisher analytics
curl "http://localhost:8000/v1/analytics?domain=example.com&days=30" \
  -H "X-API-Key: your-api-key"

# System-wide analytics
curl "http://localhost:8000/v1/analytics/summary?days=30" \
  -H "X-API-Key: your-api-key"
```

### 4. Get Daily Attestation

```bash
# Get Merkle root for specific date
curl "http://localhost:8000/v1/attestations/2025-10-13"

# Get Merkle proof for specific receipt
curl "http://localhost:8000/v1/attestations/2025-10-13/receipts/rec_123456/proof"
```

### 5. Authentication

```bash
# Login to get JWT token
curl -X POST "http://localhost:8000/v1/auth/login?username=admin&password=changeme"

# Use JWT token
curl "http://localhost:8000/v1/receipts" \
  -H "Authorization: Bearer <jwt-token>"
```

## Architecture

### Project Structure
```
apps/api/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and settings
│   ├── routes/
│   │   ├── receipts.py         # Receipt management endpoints
│   │   ├── analytics.py        # Analytics endpoints
│   │   ├── publishers.py       # Publisher verification endpoints
│   │   └── attestations.py     # Attestation endpoints
│   ├── models/
│   │   ├── receipt.py          # Receipt data models
│   │   └── publisher.py        # Publisher data models
│   ├── services/
│   │   ├── verification.py     # Domain verification service
│   │   ├── signature.py        # Signature verification service
│   │   └── merkle.py           # Merkle tree service
│   └── middleware/
│       └── auth.py             # Authentication middleware
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
├── .env.example                # Environment variables example
└── README.md                   # This file
```

### Key Components

1. **Signature Verification**: HMAC and RSA signature verification for receipts
2. **Domain Verification**: DNS TXT record verification for publisher domains
3. **Merkle Trees**: Daily attestations with cryptographic proof
4. **Rate Limiting**: slowapi-based rate limiting per minute/hour
5. **Authentication**: JWT tokens and API keys
6. **Supabase Integration**: PostgreSQL database with real-time capabilities

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Style
```bash
# Format code
black src/

# Lint code
flake8 src/
pylint src/
```

### Type Checking
```bash
mypy src/
```

## Production Deployment

### Security Checklist
- [ ] Change SECRET_KEY to a strong random value
- [ ] Use HTTPS only
- [ ] Set DEBUG=False
- [ ] Configure proper CORS origins
- [ ] Implement rate limiting with Redis backend
- [ ] Set up monitoring and logging
- [ ] Use environment variables for all secrets
- [ ] Enable Supabase Row Level Security (RLS)
- [ ] Implement proper user authentication
- [ ] Set up backup strategy

### Performance Optimization
- Use multiple workers: `--workers 4`
- Enable Gunicorn for production
- Use Redis for rate limiting
- Configure database connection pooling
- Implement caching for frequent queries
- Set up CDN for static assets

### Monitoring
- Health check endpoint: `/health`
- Structured logging with timestamps
- Request/response logging
- Error tracking (Sentry, etc.)
- Performance metrics (Prometheus, etc.)

## API Response Formats

### Success Response
```json
{
  "receipt_id": "rec_123456",
  "status": "verified",
  "verified": true,
  "message": "Receipt verified and stored",
  "timestamp": "2025-10-13T10:00:00Z"
}
```

### Error Response
```json
{
  "error": "Publisher not verified",
  "status_code": 400,
  "timestamp": "2025-10-13T10:00:00Z"
}
```

## Rate Limits

Default rate limits:
- General endpoints: 60 requests/minute
- Analytics endpoints: 1000 requests/hour
- Public endpoints: 100 requests/minute

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets

## Support

For issues, questions, or contributions:
- Documentation: http://localhost:8000/docs
- GitHub Issues: [Your repo URL]
- Email: support@iaindex.com

## License

[Your License Here]

## Changelog

### Version 1.0.0 (2025-10-13)
- Initial release
- Receipt ingestion and verification
- Publisher domain verification
- Analytics endpoints
- Merkle tree attestations
- JWT/API key authentication
- Rate limiting
- Docker support
