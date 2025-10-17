# IAIndex End-to-End Test Suite

Automated test script that validates the complete IAIndex user journey against the live API.

## What It Tests

1. **API Health** - Verifies API is reachable and responding
2. **Domain Verification Initiation** - Tests starting the verification process
3. **Verification Status Check** - Tests checking verification status
4. **Verified Domains List** - Tests retrieving all verified publishers
5. **Receipt Submission** - Tests submitting cryptographic receipts
6. **Receipt Retrieval** - Tests querying submitted receipts
7. **Publisher Analytics** - Tests analytics for specific domain
8. **System Analytics** - Tests system-wide statistics

## Prerequisites

- Python 3.8+
- pip
- IAIndex API key (recommended)
- Network access to IAIndex API

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
```

Edit `.env`:
```env
API_BASE_URL=https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
API_KEY=your-api-key-here
TEST_DOMAIN=e2e-test-example.com
SECRET_KEY=test-secret-key
```

## Usage

### Run all tests

```bash
python test.py
```

### Run with verbose output

```bash
python test.py -v
```

### Expected Output

```
╔════════════════════════════════════════════════════════════════════╗
║                  IAIndex End-to-End Test Suite                    ║
╚════════════════════════════════════════════════════════════════════╝

API Base URL: https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
Test Domain:  e2e-test-example.com
API Key:      Set

======================================================================
Test 1: API Health Check
======================================================================

Test: API Reachability
  ✓ PASS API is healthy (Status: 200)

======================================================================
Test 2: Domain Verification Initiation
======================================================================

Test: Initiate domain verification
  ✓ PASS Verification initiated successfully
  ℹ INFO Domain: e2e-test-example.com
  ℹ INFO Token: abc123...
  ℹ INFO Method: dns_txt
  ℹ INFO Status: pending

... (more tests) ...

======================================================================
Test Summary
======================================================================

Total Tests:    8
Passed:         8
Failed:         0
Warnings:       2

Pass Rate:      100.0%

✓ ALL TESTS PASSED!
```

## Test Details

### Test 1: API Health

Verifies that the API is reachable and responding.

**Endpoint:** `GET /health`

**Expected:** 200 OK

### Test 2: Domain Verification Initiation

Initiates domain verification for a test domain.

**Endpoint:** `POST /v1/publishers/verify`

**Payload:**
```json
{
  "domain": "e2e-test-example.com",
  "method": "dns_txt",
  "contact_email": "test@example.com"
}
```

**Expected:** 200/201 OK or 409 Conflict (if already initiated)

### Test 3: Verification Status Check

Checks the status of domain verification.

**Endpoint:** `GET /v1/publishers/verify/{token}`

**Expected:** 200 OK or 404 Not Found (for test domains)

### Test 4: Verified Domains List

Retrieves list of all verified publishers.

**Endpoint:** `GET /v1/publishers/verified-domains`

**Expected:** 200 OK with domains array

### Test 5: Receipt Submission

Submits a test receipt with valid signature.

**Endpoint:** `POST /v1/receipts/ingest`

**Payload:**
```json
{
  "receipt_id": "uuid-v4",
  "publisher_domain": "e2e-test-example.com",
  "article_url": "https://e2e-test-example.com/article",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "signature": "hmac-sha256-signature",
  "metadata": {
    "client_id": "e2e-test",
    "test_run": true
  }
}
```

**Expected:** 201 Created (or failure if domain not verified)

### Test 6: Receipt Retrieval

Queries submitted receipts.

**Endpoint:** `GET /v1/receipts?limit=10`

**Expected:** 200 OK with receipts array

### Test 7: Publisher Analytics

Queries analytics for test domain.

**Endpoint:** `GET /v1/analytics?domain=e2e-test-example.com&days=30`

**Expected:** 200 OK or 404 Not Found (for new domains)

### Test 8: System Analytics

Queries system-wide statistics.

**Endpoint:** `GET /v1/analytics/summary?days=30`

**Expected:** 200 OK with system statistics

## Interpreting Results

### All Passed
```
✓ ALL TESTS PASSED!
```
The API is functioning correctly and all endpoints are working as expected.

### Some Failed
```
✗ SOME TESTS FAILED

Failed tests:
  - Receipt Submission: Publisher not verified
```
Check the specific failure messages. Some failures are expected (e.g., test domain not being verified).

### Warnings
Warnings indicate expected behaviors:
- "Domain already has verification initiated" - Test domain was used before
- "Token not found" - Test token doesn't exist (expected)
- "Publisher not found" - Test domain not verified (expected)

## Exit Codes

- **0** - All tests passed
- **1** - One or more tests failed

Use in CI/CD:
```bash
python test.py
if [ $? -eq 0 ]; then
  echo "Tests passed"
else
  echo "Tests failed"
  exit 1
fi
```

## Continuous Integration

### GitHub Actions

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd examples/e2e-test
          pip install -r requirements.txt
      - name: Run tests
        env:
          API_KEY: ${{ secrets.IAINDEX_API_KEY }}
        run: |
          cd examples/e2e-test
          python test.py
```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY test.py .
COPY .env .

CMD ["python", "test.py"]
```

Run:
```bash
docker build -t iaindex-e2e-test .
docker run -e API_KEY=$API_KEY iaindex-e2e-test
```

## Common Issues

### API Key Not Set

**Issue:** Tests fail with authentication errors

**Solution:** Set `API_KEY` in `.env` file

### API Not Reachable

**Issue:** Test 1 fails with connection error

**Solution:**
- Check network connectivity
- Verify API_BASE_URL is correct
- Check if API is down

### Test Domain Conflicts

**Issue:** "Domain already has verification initiated"

**Solution:**
- Use a different TEST_DOMAIN
- Or continue - this is expected behavior

### Receipt Submission Fails

**Issue:** Receipt rejected with "Publisher not verified"

**Solution:** This is expected if test domain is not actually verified. The test validates the API behavior.

## Extending Tests

### Add New Test

```python
def test_custom_feature():
    """Test 9: Custom feature"""
    print_header("Test 9: Custom Feature")
    print_test("Test custom functionality")

    response = make_request('GET', '/v1/custom/endpoint')

    if response and response.status_code == 200:
        print_pass("Custom test passed")
        record_test("Custom Feature", True)
        return True
    else:
        print_fail("Custom test failed")
        record_test("Custom Feature", False)
        return False

# Add to main():
test_custom_feature()
```

### Custom Assertions

```python
def assert_field(data: dict, field: str, expected_type: type):
    """Assert field exists and has correct type"""
    if field not in data:
        print_fail(f"Field '{field}' missing")
        return False

    if not isinstance(data[field], expected_type):
        print_fail(f"Field '{field}' has wrong type")
        return False

    print_pass(f"Field '{field}' validated")
    return True
```

## Troubleshooting

### Enable Debug Output

Modify `make_request()` to print requests:

```python
def make_request(method: str, endpoint: str, **kwargs):
    url = f"{API_BASE_URL}{endpoint}"
    print(f"DEBUG: {method} {url}")
    print(f"DEBUG: Headers: {headers}")
    print(f"DEBUG: Body: {kwargs.get('json')}")

    response = requests.request(...)
    print(f"DEBUG: Response: {response.status_code} {response.text[:200]}")

    return response
```

### Save Test Results

```python
import json

# At end of main():
with open('test-results.json', 'w') as f:
    json.dump(test_results, f, indent=2)
```

## Resources

- [IAIndex API Documentation](https://docs.iaindex.org/api)
- [Quickstart Guide](https://docs.iaindex.org/quickstart)
- [GitHub Issues](https://github.com/iaindex/iaindex/issues)

## Support

- GitHub: [github.com/iaindex/iaindex](https://github.com/iaindex/iaindex)
- Discord: [discord.gg/iaindex](https://discord.gg/iaindex)
- Email: support@iaindex.com

## License

MIT
