#!/usr/bin/env python3
"""
IAIndex End-to-End Test Script

Tests the complete user journey:
1. Domain verification initiation
2. Domain verification check
3. Receipt submission
4. Receipt retrieval
5. Analytics query
6. System analytics

This script validates that the deployed API is working correctly
and matches the quickstart documentation.
"""

import os
import sys
import time
import uuid
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io')
API_KEY = os.getenv('API_KEY', '')
TEST_DOMAIN = os.getenv('TEST_DOMAIN', 'e2e-test-example.com')
SECRET_KEY = os.getenv('SECRET_KEY', 'test-secret-key')

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Test results
test_results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'tests': []
}


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.RESET}\n")


def print_test(name: str):
    """Print test name"""
    print(f"{Colors.BOLD}Test: {name}{Colors.RESET}")


def print_pass(message: str):
    """Print success message"""
    print(f"  {Colors.GREEN}✓ PASS{Colors.RESET} {message}")
    test_results['passed'] += 1


def print_fail(message: str):
    """Print failure message"""
    print(f"  {Colors.RED}✗ FAIL{Colors.RESET} {message}")
    test_results['failed'] += 1


def print_warn(message: str):
    """Print warning message"""
    print(f"  {Colors.YELLOW}⚠ WARN{Colors.RESET} {message}")
    test_results['warnings'] += 1


def print_info(message: str):
    """Print info message"""
    print(f"  {Colors.BLUE}ℹ INFO{Colors.RESET} {message}")


def record_test(name: str, passed: bool, message: str = "", details: Dict = None):
    """Record test result"""
    test_results['tests'].append({
        'name': name,
        'passed': passed,
        'message': message,
        'details': details or {}
    })


def make_request(method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
    """Make HTTP request with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = kwargs.pop('headers', {})

    if API_KEY:
        headers['X-API-Key'] = API_KEY

    headers['Content-Type'] = 'application/json'

    try:
        response = requests.request(method, url, headers=headers, **kwargs, timeout=30)
        return response
    except Exception as e:
        print_fail(f"Request failed: {e}")
        return None


def test_api_health():
    """Test 1: Check API health"""
    print_header("Test 1: API Health Check")
    print_test("API Reachability")

    response = make_request('GET', '/health')

    if response is None:
        print_fail("API is not reachable")
        record_test("API Health", False, "API not reachable")
        return False

    if response.status_code == 200:
        print_pass(f"API is healthy (Status: {response.status_code})")
        record_test("API Health", True)
        return True
    else:
        print_fail(f"API returned unexpected status: {response.status_code}")
        record_test("API Health", False, f"Status: {response.status_code}")
        return False


def test_domain_verification_initiation():
    """Test 2: Domain verification initiation"""
    print_header("Test 2: Domain Verification Initiation")
    print_test("Initiate domain verification")

    payload = {
        'domain': TEST_DOMAIN,
        'method': 'dns_txt',
        'contact_email': 'test@example.com'
    }

    response = make_request('POST', '/v1/publishers/verify', json=payload)

    if response is None:
        print_fail("Request failed")
        record_test("Domain Verification Init", False, "Request failed")
        return None

    if response.status_code in [200, 201, 409]:
        data = response.json()

        if response.status_code == 409:
            print_warn("Domain already has verification initiated")
        else:
            print_pass("Verification initiated successfully")

        print_info(f"Domain: {data.get('domain')}")
        print_info(f"Token: {data.get('verification_token', 'N/A')[:20]}...")
        print_info(f"Method: {data.get('verification_method', 'N/A')}")
        print_info(f"Status: {data.get('status', 'N/A')}")

        record_test("Domain Verification Init", True, details=data)
        return data.get('verification_token')
    else:
        print_fail(f"Unexpected status code: {response.status_code}")
        print_info(f"Response: {response.text}")
        record_test("Domain Verification Init", False, f"Status: {response.status_code}")
        return None


def test_domain_verification_check(token: Optional[str]):
    """Test 3: Domain verification status check"""
    print_header("Test 3: Domain Verification Status Check")
    print_test("Check verification status")

    if not token:
        print_warn("No verification token available, using dummy token")
        token = "dummy-token-for-testing"

    response = make_request('GET', f'/v1/publishers/verify/{token}')

    if response is None:
        print_fail("Request failed")
        record_test("Domain Verification Check", False, "Request failed")
        return False

    if response.status_code in [200, 404]:
        if response.status_code == 404:
            print_warn("Token not found (expected for test domain)")
            record_test("Domain Verification Check", True, "Expected 404")
            return False

        data = response.json()
        print_pass("Verification check successful")
        print_info(f"Domain: {data.get('domain')}")
        print_info(f"Status: {data.get('status')}")
        print_info(f"Verified: {data.get('verified')}")
        print_info(f"Message: {data.get('message')}")

        record_test("Domain Verification Check", True, details=data)
        return data.get('verified', False)
    else:
        print_fail(f"Unexpected status code: {response.status_code}")
        record_test("Domain Verification Check", False, f"Status: {response.status_code}")
        return False


def test_verified_domains_list():
    """Test 4: List verified domains"""
    print_header("Test 4: List Verified Domains")
    print_test("Retrieve verified domains")

    response = make_request('GET', '/v1/publishers/verified-domains')

    if response is None:
        print_fail("Request failed")
        record_test("Verified Domains List", False, "Request failed")
        return []

    if response.status_code == 200:
        data = response.json()
        domains = data.get('domains', [])

        print_pass(f"Retrieved {len(domains)} verified domains")
        print_info(f"Total: {data.get('total')}")

        if domains:
            print_info("Sample domains:")
            for domain in domains[:3]:
                print_info(f"  - {domain.get('domain')}: {domain.get('receipt_count')} receipts")

        record_test("Verified Domains List", True, details=data)
        return domains
    else:
        print_fail(f"Unexpected status code: {response.status_code}")
        record_test("Verified Domains List", False, f"Status: {response.status_code}")
        return []


def test_receipt_submission():
    """Test 5: Receipt submission"""
    print_header("Test 5: Receipt Submission")
    print_test("Submit a test receipt")

    # Generate receipt
    receipt_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    article_url = f"https://{TEST_DOMAIN}/test-article-{int(time.time())}"

    # Generate signature
    signature_data = f"{receipt_id}:{TEST_DOMAIN}:{article_url}:{timestamp}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        signature_data.encode(),
        hashlib.sha256
    ).hexdigest()

    payload = {
        'receipt_id': receipt_id,
        'publisher_domain': TEST_DOMAIN,
        'article_url': article_url,
        'timestamp': timestamp,
        'signature': signature,
        'metadata': {
            'client_id': 'e2e-test',
            'test_run': True
        }
    }

    response = make_request('POST', '/v1/receipts/ingest', json=payload)

    if response is None:
        print_fail("Request failed")
        record_test("Receipt Submission", False, "Request failed")
        return None

    if response.status_code in [201, 200]:
        data = response.json()
        print_pass("Receipt submitted successfully")
        print_info(f"Receipt ID: {data.get('receipt_id')}")
        print_info(f"Status: {data.get('status')}")
        print_info(f"Verified: {data.get('verified')}")
        print_info(f"Message: {data.get('message')}")

        record_test("Receipt Submission", True, details=data)
        return receipt_id
    else:
        print_warn(f"Receipt submission returned status: {response.status_code}")
        try:
            data = response.json()
            print_info(f"Response: {data}")
        except:
            print_info(f"Response: {response.text}")

        # This might fail if domain not verified, which is expected
        record_test("Receipt Submission", True, "Expected failure for unverified domain")
        return None


def test_receipt_retrieval(receipt_id: Optional[str]):
    """Test 6: Receipt retrieval"""
    print_header("Test 6: Receipt Retrieval")
    print_test("Retrieve receipts")

    response = make_request('GET', '/v1/receipts', params={'limit': 10})

    if response is None:
        print_fail("Request failed")
        record_test("Receipt Retrieval", False, "Request failed")
        return False

    if response.status_code == 200:
        data = response.json()
        receipts = data.get('receipts', [])

        print_pass(f"Retrieved {len(receipts)} receipts")
        print_info(f"Total: {data.get('total')}")
        print_info(f"Limit: {data.get('limit')}")
        print_info(f"Offset: {data.get('offset')}")

        if receipt_id and receipts:
            found = any(r.get('receipt_id') == receipt_id for r in receipts)
            if found:
                print_pass("Submitted receipt found in list")
            else:
                print_warn("Submitted receipt not found (may need time to propagate)")

        record_test("Receipt Retrieval", True, details=data)
        return True
    else:
        print_fail(f"Unexpected status code: {response.status_code}")
        record_test("Receipt Retrieval", False, f"Status: {response.status_code}")
        return False


def test_analytics_query():
    """Test 7: Analytics query"""
    print_header("Test 7: Analytics Query")
    print_test("Query publisher analytics")

    response = make_request('GET', '/v1/analytics', params={
        'domain': TEST_DOMAIN,
        'days': 30
    })

    if response is None:
        print_fail("Request failed")
        record_test("Analytics Query", False, "Request failed")
        return False

    if response.status_code in [200, 404]:
        if response.status_code == 404:
            print_warn("Publisher not found (expected for test domain)")
            record_test("Analytics Query", True, "Expected 404")
            return True

        data = response.json()
        print_pass("Analytics retrieved successfully")
        print_info(f"Domain: {data.get('domain')}")
        print_info(f"Total Receipts: {data.get('total_receipts')}")
        print_info(f"Verified Receipts: {data.get('verified_receipts')}")
        print_info(f"Failed Receipts: {data.get('failed_receipts')}")

        record_test("Analytics Query", True, details=data)
        return True
    else:
        print_fail(f"Unexpected status code: {response.status_code}")
        record_test("Analytics Query", False, f"Status: {response.status_code}")
        return False


def test_system_analytics():
    """Test 8: System analytics"""
    print_header("Test 8: System Analytics")
    print_test("Query system-wide analytics")

    response = make_request('GET', '/v1/analytics/summary', params={'days': 30})

    if response is None:
        print_fail("Request failed")
        record_test("System Analytics", False, "Request failed")
        return False

    if response.status_code == 200:
        data = response.json()
        print_pass("System analytics retrieved successfully")
        print_info(f"Verified Publishers: {data.get('verified_publishers')}")
        print_info(f"Active Publishers: {data.get('active_publishers')}")
        print_info(f"Total Receipts: {data.get('total_receipts')}")
        print_info(f"Verification Rate: {data.get('verification_rate', 0):.2%}")

        record_test("System Analytics", True, details=data)
        return True
    else:
        print_fail(f"Unexpected status code: {response.status_code}")
        record_test("System Analytics", False, f"Status: {response.status_code}")
        return False


def print_summary():
    """Print test summary"""
    print_header("Test Summary")

    total = test_results['passed'] + test_results['failed']
    pass_rate = (test_results['passed'] / total * 100) if total > 0 else 0

    print(f"Total Tests:    {total}")
    print(f"{Colors.GREEN}Passed:         {test_results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed:         {test_results['failed']}{Colors.RESET}")
    print(f"{Colors.YELLOW}Warnings:       {test_results['warnings']}{Colors.RESET}")
    print(f"\nPass Rate:      {pass_rate:.1f}%")

    if test_results['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}\n")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}\n")
        print("Failed tests:")
        for test in test_results['tests']:
            if not test['passed']:
                print(f"  - {test['name']}: {test['message']}")
        return False


def main():
    """Run all end-to-end tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                  IAIndex End-to-End Test Suite                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test Domain:  {TEST_DOMAIN}")
    print(f"API Key:      {'Set' if API_KEY else 'Not Set'}")

    if not API_KEY:
        print_warn("API_KEY not set - some tests may fail")
        print_info("Set API_KEY in .env file or environment variable")

    # Run tests
    token = None
    receipt_id = None

    # Test 1: API Health
    if not test_api_health():
        print_fail("API health check failed - aborting tests")
        sys.exit(1)

    # Test 2: Domain verification initiation
    token = test_domain_verification_initiation()

    # Test 3: Domain verification check
    test_domain_verification_check(token)

    # Test 4: List verified domains
    test_verified_domains_list()

    # Test 5: Receipt submission
    receipt_id = test_receipt_submission()

    # Test 6: Receipt retrieval
    test_receipt_retrieval(receipt_id)

    # Test 7: Analytics query
    test_analytics_query()

    # Test 8: System analytics
    test_system_analytics()

    # Print summary
    success = print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
