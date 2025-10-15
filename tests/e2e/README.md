# End-to-End Tests

Comprehensive E2E tests for AIIndex v1.1 features.

## Test Coverage

### Policy Enforcement (`test_policy_enforcement.py`)
- ✅ Allowed retrieval returns 200
- ✅ Blocked training returns 403 with denial receipt
- ✅ Missing required receipt returns 403
- ✅ Rate limit returns 429
- ✅ Allowlist bypass works
- ✅ Blocklist returns 403
- ✅ Policy version negotiation
- ✅ Conditional access with offer

### Render Fallback (`test_rendering.py`)
- ✅ Render snapshot creates content_hash
- ✅ Cache returns ETag
- ✅ Rendered text populates ai-index.json
- ✅ S3 storage works
- ✅ Batch render multiple pages
- ✅ Render mode local fallback
- ✅ Render TTL expiration

### Embeddings (`test_embeddings.py`)
- ✅ Build embeddings creates vectors
- ✅ Semantic query returns results
- ✅ Manifest URL is valid
- ✅ Only verified publishers can build
- ✅ Embeddings incremental update
- ✅ Embeddings model compatibility
- ✅ Vector export formats

### C2PA Provenance (`test_provenance.py`)
- ✅ Manifest generation works
- ✅ Signature validates
- ✅ Badge verifier returns status
- ✅ Merkle root anchoring works
- ✅ Tamper detection
- ✅ C2PA in ai-index.json
- ✅ Content Authenticity Inspect integration

### Complete Flow (`test_full_flow.py`)
- ✅ Full publisher workflow
- ✅ Flow with fraud detection
- ✅ Flow with invalid signature

## Setup

### Prerequisites

1. **API Server Running**
   ```bash
   cd apps/api
   python -m uvicorn src.main:app --reload
   ```

2. **Database Setup**
   ```bash
   # Run migrations
   psql iaindex_db < migrations/v1.0-to-v1.1.sql
   ```

3. **Environment Variables**
   ```bash
   export API_BASE_URL=http://localhost:3000
   export TEST_PUBLISHER_API_KEY=test_api_key_12345
   export TEST_VERIFIED_API_KEY=test_verified_api_key_12345
   ```

### Install Dependencies

```bash
cd tests/e2e
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

```bash
pytest -v
```

### Run Specific Test Suite

```bash
# Policy enforcement tests
pytest test_policy_enforcement.py -v

# Rendering tests
pytest test_rendering.py -v

# Embeddings tests
pytest test_embeddings.py -v

# Provenance tests
pytest test_provenance.py -v

# Complete flow test
pytest test_full_flow.py -v
```

### Run Single Test

```bash
pytest test_policy_enforcement.py::TestPolicyEnforcement::test_allowed_retrieval_returns_200 -v
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Run in Parallel

```bash
pip install pytest-xdist
pytest -n auto -v
```

### Generate HTML Report

```bash
pytest --html=report.html --self-contained-html
```

## Configuration

### pytest.ini

Configure test behavior in `pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
timeout = 300
log_cli = true
log_cli_level = INFO
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `http://localhost:3000` | API server URL |
| `TEST_PUBLISHER_API_KEY` | `test_api_key_12345` | Test API key |
| `TEST_VERIFIED_API_KEY` | `test_verified_api_key_12345` | Verified publisher key |
| `TEST_TIMEOUT` | `30` | Request timeout (seconds) |

## Test Data

Tests use the following test publishers:

- `example-blog.com` - Basic blog with articles
- `example-spa.com` - SPA with dynamic content (rendering tests)
- `example-docs.com` - Documentation site (embeddings tests)
- `example-news.com` - News site (provenance tests)
- `complete-flow-test.com` - Complete flow test
- `test-publisher.com` - Generic test publisher

## Troubleshooting

### Tests Fail with Connection Refused

**Solution:** Ensure API server is running:

```bash
curl http://localhost:3000/health
```

### Tests Timeout

**Solution:** Increase timeout in pytest.ini or environment:

```bash
export TEST_TIMEOUT=60
pytest -v
```

### Database Errors

**Solution:** Reset database and run migrations:

```bash
psql iaindex_db < migrations/v1.0-to-v1.1.sql
```

### Import Errors

**Solution:** Ensure dependencies installed:

```bash
pip install -r requirements.txt
```

## CI/CD Integration

### GitHub Actions

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: iaindex_test
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r tests/e2e/requirements.txt

      - name: Run migrations
        run: |
          psql -h localhost -U postgres -d iaindex_test < migrations/v1.0-to-v1.1.sql

      - name: Start API server
        run: |
          cd apps/api
          python -m uvicorn src.main:app &
          sleep 5

      - name: Run E2E tests
        run: |
          cd tests/e2e
          pytest -v --html=report.html

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: tests/e2e/report.html
```

## Test Statistics

**Total Tests:** 38
**Total Assertions:** ~200
**Estimated Runtime:** 5-10 minutes
**Coverage Target:** >80%

## Contributing

When adding new features, please add corresponding E2E tests:

1. Create test file in `tests/e2e/`
2. Follow naming convention: `test_<feature>.py`
3. Use async/await for HTTP requests
4. Add docstrings to test methods
5. Update this README with new test coverage

## License

Same as main AIIndex project.
