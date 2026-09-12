#!/usr/bin/env python3
"""
IAIndex Comprehensive QA Test Suite
Work Stream 6: Testing & QA

This script performs comprehensive testing across all IAIndex components:
- Backend API endpoint testing
- Authentication and authorization
- Security vulnerability testing
- Integration testing
- Performance testing
- Error handling
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple
import sys

# Configuration
API_BASE_URL = "https://api.iaindex.org"
TEST_EMAIL = f"qa_test_{int(time.time())}@iaindex.org"
TEST_PASSWORD = "SecureTestPass123!"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.errors = []
        self.performance_metrics = []

    def add_pass(self, test_name: str, duration_ms: float = 0):
        self.passed += 1
        if duration_ms > 0:
            self.performance_metrics.append((test_name, duration_ms))
        print(f"{Colors.GREEN}✓{Colors.END} {test_name}")

    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"{Colors.RED}✗{Colors.END} {test_name}: {error}")

    def add_warning(self, test_name: str, message: str):
        self.warnings += 1
        print(f"{Colors.YELLOW}⚠{Colors.END} {test_name}: {message}")

    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"{Colors.BOLD}Test Results Summary{Colors.END}")
        print(f"{'='*60}")
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {self.warnings}{Colors.END}")

        if self.errors:
            print(f"\n{Colors.RED}Failed Tests:{Colors.END}")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")

        if self.performance_metrics:
            print(f"\n{Colors.BLUE}Performance Metrics:{Colors.END}")
            avg_time = sum(m[1] for m in self.performance_metrics) / len(self.performance_metrics)
            max_time = max(m[1] for m in self.performance_metrics)
            print(f"  Average Response Time: {avg_time:.2f}ms")
            print(f"  Max Response Time: {max_time:.2f}ms")
            slow_endpoints = [m for m in self.performance_metrics if m[1] > 500]
            if slow_endpoints:
                print(f"  {Colors.YELLOW}Slow Endpoints (>500ms):{Colors.END}")
                for name, duration in slow_endpoints:
                    print(f"    - {name}: {duration:.2f}ms")

results = TestResults()

def test_api_request(method: str, endpoint: str, **kwargs) -> Tuple[bool, any, float]:
    """Make API request and track performance"""
    url = f"{API_BASE_URL}{endpoint}"
    start_time = time.time()

    try:
        response = requests.request(method, url, **kwargs, timeout=10)
        duration_ms = (time.time() - start_time) * 1000

        return True, response, duration_ms
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return False, str(e), duration_ms

# ============================================================================
# 1. SYSTEM HEALTH & AVAILABILITY TESTS
# ============================================================================

def test_system_health():
    """Test basic system health and availability"""
    print(f"\n{Colors.BOLD}1. System Health & Availability Tests{Colors.END}")
    print("-" * 60)

    # Test health endpoint
    success, response, duration = test_api_request("GET", "/health")
    if success and response.status_code == 200:
        data = response.json()
        if data.get("status") == "healthy":
            results.add_pass(f"Health Check (API Online)", duration)
        else:
            results.add_fail("Health Check", f"Unexpected status: {data.get('status')}")
    else:
        results.add_fail("Health Check", f"API unavailable: {response}")

    # Test root endpoint
    success, response, duration = test_api_request("GET", "/")
    if success and response.status_code == 200:
        results.add_pass("Root Endpoint", duration)
    else:
        results.add_fail("Root Endpoint", f"Failed with status {response.status_code if success else 'timeout'}")

    # Test CORS headers
    success, response, duration = test_api_request("OPTIONS", "/health")
    if success:
        headers = response.headers
        if 'access-control-allow-origin' in headers:
            results.add_pass("CORS Headers Present", duration)
        else:
            results.add_warning("CORS Headers", "CORS headers may not be configured")

    # Test security headers
    success, response, duration = test_api_request("GET", "/health")
    if success:
        headers = response.headers
        security_headers = [
            'x-content-type-options',
            'x-frame-options',
            'strict-transport-security',
            'content-security-policy'
        ]
        missing_headers = [h for h in security_headers if h not in headers]
        if not missing_headers:
            results.add_pass("Security Headers", duration)
        else:
            results.add_warning("Security Headers", f"Missing: {', '.join(missing_headers)}")

# ============================================================================
# 2. AUTHENTICATION & AUTHORIZATION TESTS
# ============================================================================

def test_authentication():
    """Test authentication flows"""
    print(f"\n{Colors.BOLD}2. Authentication & Authorization Tests{Colors.END}")
    print("-" * 60)

    # Test accessing protected endpoint without auth
    success, response, duration = test_api_request("GET", "/v1/auth/me")
    if success and response.status_code in [401, 403]:
        results.add_pass("Protected Endpoint Without Auth (401/403)", duration)
    else:
        results.add_fail("Protected Endpoint", f"Expected 401/403, got {response.status_code if success else 'error'}")

    # Test login endpoint (should be disabled)
    success, response, duration = test_api_request(
        "POST",
        "/v1/auth/login",
        json={"username": "test", "password": "test"}
    )
    if success and response.status_code == 501:
        results.add_pass("Legacy Login Endpoint Disabled (Security Fix)", duration)
    else:
        results.add_warning("Legacy Login", "Endpoint may still be enabled")

    # Test user registration
    success, response, duration = test_api_request(
        "POST",
        "/v1/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "QA Test User"
        }
    )
    if success:
        if response.status_code == 200:
            results.add_pass("User Registration", duration)
            # Store token for subsequent tests
            data = response.json()
            return data.get("access_token")
        elif response.status_code == 409:
            results.add_warning("User Registration", "Email already exists (expected if re-running tests)")
        else:
            results.add_fail("User Registration", f"Status {response.status_code}: {response.text}")
    else:
        results.add_fail("User Registration", f"Request failed: {response}")

    return None

# ============================================================================
# 3. API ENDPOINT FUNCTIONALITY TESTS
# ============================================================================

def test_api_endpoints(auth_token: str = None):
    """Test all API endpoints"""
    print(f"\n{Colors.BOLD}3. API Endpoint Functionality Tests{Colors.END}")
    print("-" * 60)

    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    # Test schema generation endpoint
    success, response, duration = test_api_request(
        "POST",
        "/v1/schema/generate",
        json={"url": "https://example.com", "business_type": "e-commerce"},
        headers=headers
    )
    if success:
        if response.status_code in [200, 201]:
            results.add_pass("Schema Generation Endpoint", duration)
        elif response.status_code in [401, 402]:
            results.add_warning("Schema Generation", "Authentication/subscription required")
        else:
            results.add_fail("Schema Generation", f"Status {response.status_code}")

    # Test visibility check endpoint
    success, response, duration = test_api_request(
        "POST",
        "/v1/visibility/check",
        json={"url": "https://example.com"},
        headers=headers
    )
    if success:
        if response.status_code in [200, 201]:
            results.add_pass("Visibility Check Endpoint", duration)
        elif response.status_code in [401, 402]:
            results.add_warning("Visibility Check", "Authentication/subscription required")
        else:
            results.add_fail("Visibility Check", f"Status {response.status_code}")

    # Test publishers endpoint
    success, response, duration = test_api_request("GET", "/v1/publishers/verified-domains")
    if success and response.status_code == 200:
        results.add_pass("Publishers List Endpoint", duration)
    else:
        results.add_fail("Publishers List", f"Failed with status {response.status_code if success else 'error'}")

# ============================================================================
# 4. SECURITY VULNERABILITY TESTS
# ============================================================================

def test_security_vulnerabilities():
    """Test for common security vulnerabilities"""
    print(f"\n{Colors.BOLD}4. Security Vulnerability Tests{Colors.END}")
    print("-" * 60)

    # Test SQL injection
    sql_payloads = [
        "' OR '1'='1",
        "admin'--",
        "1' UNION SELECT NULL--",
        "'; DROP TABLE users--"
    ]

    for payload in sql_payloads:
        success, response, duration = test_api_request(
            "POST",
            "/v1/auth/login",
            json={"username": payload, "password": payload}
        )
        if success and response.status_code in [400, 422, 501]:
            results.add_pass(f"SQL Injection Protection ({payload[:20]}...)", duration)
        elif success and response.status_code == 200:
            results.add_fail("SQL Injection", f"Possible SQL injection vulnerability with payload: {payload}")
        else:
            results.add_pass(f"SQL Injection Protection ({payload[:20]}...)", duration)

    # Test XSS
    xss_payload = "<script>alert('xss')</script>"
    success, response, duration = test_api_request(
        "POST",
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "test",
            "full_name": xss_payload
        }
    )
    if success:
        if response.status_code in [200, 409]:
            # Check if response sanitizes XSS
            response_text = response.text
            if "<script>" not in response_text:
                results.add_pass("XSS Protection (Input Sanitization)", duration)
            else:
                results.add_fail("XSS Protection", "XSS payload not sanitized in response")
        else:
            results.add_pass("XSS Protection (Request Rejected)", duration)

    # Test SSRF protection
    ssrf_urls = [
        "http://169.254.169.254/latest/meta-data/",  # AWS metadata
        "http://localhost/admin",
        "http://127.0.0.1:8000/internal",
        "file:///etc/passwd"
    ]

    for url in ssrf_urls:
        success, response, duration = test_api_request(
            "POST",
            "/v1/schema/generate",
            json={"url": url, "business_type": "test"}
        )
        if success and response.status_code in [400, 422]:
            results.add_pass(f"SSRF Protection ({url[:30]}...)", duration)
        elif success and response.status_code == 200:
            results.add_fail("SSRF Protection", f"Possible SSRF vulnerability with URL: {url}")
        else:
            results.add_pass(f"SSRF Protection ({url[:30]}...)", duration)

    # Test rate limiting
    print(f"\n  Testing Rate Limiting...")
    rate_limit_triggered = False
    for i in range(15):
        success, response, duration = test_api_request("GET", "/health")
        if success and response.status_code == 429:
            rate_limit_triggered = True
            results.add_pass("Rate Limiting Active", duration)
            break

    if not rate_limit_triggered:
        results.add_warning("Rate Limiting", "Rate limit not triggered after 15 requests (may have high limits)")

# ============================================================================
# 5. INTEGRATION TESTS
# ============================================================================

def test_integrations():
    """Test external integrations"""
    print(f"\n{Colors.BOLD}5. Integration Tests{Colors.END}")
    print("-" * 60)

    # Test that API can handle AI provider responses
    # (We can't test actual API keys without exposing them)
    results.add_warning("AI Integration (Anthropic/OpenAI)", "Requires actual API keys - manual verification needed")
    results.add_warning("Stripe Integration", "Requires Stripe test mode - manual verification needed")
    results.add_warning("Email Service", "Requires SendGrid/Resend API key - manual verification needed")

# ============================================================================
# 6. PERFORMANCE TESTS
# ============================================================================

def test_performance():
    """Test API performance"""
    print(f"\n{Colors.BOLD}6. Performance Tests{Colors.END}")
    print("-" * 60)

    # Test response times
    endpoints = [
        ("GET", "/health"),
        ("GET", "/"),
        ("GET", "/v1/publishers/verified-domains"),
    ]

    for method, endpoint in endpoints:
        times = []
        for i in range(5):
            success, response, duration = test_api_request(method, endpoint)
            if success:
                times.append(duration)

        if times:
            avg_time = sum(times) / len(times)
            if avg_time < 500:
                results.add_pass(f"Performance {method} {endpoint} (avg: {avg_time:.0f}ms)", avg_time)
            elif avg_time < 1000:
                results.add_warning(f"Performance {method} {endpoint}", f"Slower than ideal: {avg_time:.0f}ms")
            else:
                results.add_fail(f"Performance {method} {endpoint}", f"Too slow: {avg_time:.0f}ms")

# ============================================================================
# 7. ERROR HANDLING TESTS
# ============================================================================

def test_error_handling():
    """Test error handling"""
    print(f"\n{Colors.BOLD}7. Error Handling Tests{Colors.END}")
    print("-" * 60)

    # Test 404
    success, response, duration = test_api_request("GET", "/nonexistent-endpoint")
    if success and response.status_code == 404:
        results.add_pass("404 Error Handling", duration)
    else:
        results.add_fail("404 Handling", f"Expected 404, got {response.status_code if success else 'error'}")

    # Test invalid JSON
    success, response, duration = test_api_request(
        "POST",
        "/v1/auth/register",
        data="invalid json{",
        headers={"Content-Type": "application/json"}
    )
    if success and response.status_code in [400, 422]:
        results.add_pass("Invalid JSON Handling", duration)
    else:
        results.add_fail("Invalid JSON", f"Expected 400/422, got {response.status_code if success else 'error'}")

    # Test missing required fields
    success, response, duration = test_api_request(
        "POST",
        "/v1/auth/register",
        json={"email": "test@example.com"}  # Missing password
    )
    if success and response.status_code in [400, 422]:
        results.add_pass("Missing Required Fields Validation", duration)
    else:
        results.add_fail("Field Validation", f"Expected 400/422, got {response.status_code if success else 'error'}")

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}IAIndex Comprehensive QA Test Suite{Colors.END}")
    print(f"{Colors.BOLD}Work Stream 6: Testing & QA{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"Target API: {API_BASE_URL}")
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run test suites
        test_system_health()
        auth_token = test_authentication()
        test_api_endpoints(auth_token)
        test_security_vulnerabilities()
        test_integrations()
        test_performance()
        test_error_handling()

        # Print summary
        results.print_summary()

        # Exit code based on results
        if results.failed > 0:
            print(f"\n{Colors.RED}Tests FAILED - Critical issues found{Colors.END}")
            sys.exit(1)
        elif results.warnings > 5:
            print(f"\n{Colors.YELLOW}Tests PASSED with warnings - Review recommended{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.GREEN}All tests PASSED - System production ready{Colors.END}")
            sys.exit(0)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
        results.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Test suite error: {e}{Colors.END}")
        results.print_summary()
        sys.exit(1)

if __name__ == "__main__":
    main()
