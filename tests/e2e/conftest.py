"""
Pytest configuration for E2E tests
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator
import httpx


# Test configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000")
TEST_TIMEOUT = 30.0


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide HTTP client for tests"""
    async with httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=TEST_TIMEOUT
    ) as client:
        yield client


@pytest.fixture
def test_publisher():
    """Test publisher domain"""
    return "test-publisher.com"


@pytest.fixture
def test_client_id():
    """Test client ID"""
    return "test-ai-client"


@pytest.fixture
def publisher_api_key():
    """Test publisher API key"""
    return os.getenv("TEST_PUBLISHER_API_KEY", "test_api_key_12345")


@pytest.fixture
def verified_api_key():
    """Test verified publisher API key"""
    return os.getenv("TEST_VERIFIED_API_KEY", "test_verified_api_key_12345")


@pytest.fixture(autouse=True)
async def cleanup_test_data(http_client: httpx.AsyncClient, test_publisher: str):
    """Cleanup test data after each test"""
    yield

    # Cleanup is performed after test completes
    # In production, you might want to clean up test publishers, receipts, etc.
    # For now, we'll just pass
    pass


@pytest.fixture
async def setup_test_publisher(
    http_client: httpx.AsyncClient,
    test_publisher: str,
    publisher_api_key: str
):
    """Setup a test publisher with default configuration"""
    # Create or update test publisher
    response = await http_client.post(
        f"/publishers",
        json={
            "domain": test_publisher,
            "email": "test@example.com",
            "name": "Test Publisher"
        },
        headers={
            "Authorization": f"Bearer {publisher_api_key}"
        }
    )

    # May already exist, which is fine
    assert response.status_code in [200, 201, 409]

    # Set default policy
    policy_response = await http_client.patch(
        f"/publishers/{test_publisher}/policy",
        json={
            "policy": {
                "training": "allow",
                "retrieval": "allow",
                "attribution_required": True,
                "commercial_use": True
            }
        },
        headers={
            "Authorization": f"Bearer {publisher_api_key}"
        }
    )

    assert policy_response.status_code in [200, 201]

    yield test_publisher

    # Cleanup after test
    # (optional: delete test publisher)


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers automatically
    for item in items:
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.integration)
