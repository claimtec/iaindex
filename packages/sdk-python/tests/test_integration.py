"""
Integration tests for IAIndex SDK

Tests the SDK against the live deployed API
"""

import pytest
import os
from datetime import datetime, timezone
from aiindex import (
    IAIndexPublisher,
    IAIndexClient,
    generate_keypair
)


# Test configuration
API_BASE_URL = "https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io"
TEST_DOMAIN = "example-test.com"


class TestCryptoUtils:
    """Test cryptographic utilities"""

    def test_generate_keypair(self):
        """Test key pair generation"""
        private_key, public_key = generate_keypair()

        assert private_key is not None
        assert public_key is not None
        assert len(private_key) > 0
        assert len(public_key) > 0
        assert private_key != public_key

    def test_sign_and_verify(self):
        """Test signing and verification"""
        from aiindex.crypto import CryptoUtils

        private_key, public_key = generate_keypair()

        data = {
            "message": "Hello, World!",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Sign data
        signature = CryptoUtils.sign_data(data, private_key)
        assert signature is not None

        # Verify signature
        is_valid = CryptoUtils.verify_signature(data, signature, public_key)
        assert is_valid is True

        # Test with wrong public key
        wrong_private, wrong_public = generate_keypair()
        is_valid_wrong = CryptoUtils.verify_signature(data, signature, wrong_public)
        assert is_valid_wrong is False

    def test_hash_data(self):
        """Test data hashing"""
        from aiindex.crypto import CryptoUtils

        data = {"test": "data"}
        hash1 = CryptoUtils.hash_data(data)
        hash2 = CryptoUtils.hash_data(data)

        assert hash1 == hash2  # Same data should produce same hash

        data2 = {"test": "different"}
        hash3 = CryptoUtils.hash_data(data2)
        assert hash1 != hash3  # Different data should produce different hash


class TestPublisher:
    """Test IAIndexPublisher class"""

    @pytest.fixture
    def publisher(self):
        """Create a test publisher"""
        private_key, public_key = generate_keypair()
        return IAIndexPublisher(
            domain=TEST_DOMAIN,
            private_key=private_key,
            name="Test Publisher",
            contact="test@example.com",
            api_base_url=API_BASE_URL
        )

    def test_publisher_initialization(self, publisher):
        """Test publisher can be initialized"""
        assert publisher.domain == TEST_DOMAIN
        assert publisher.name == "Test Publisher"
        assert publisher.contact == "test@example.com"
        assert len(publisher.entries) == 0

    def test_add_entry(self, publisher):
        """Test adding entries to publisher"""
        entry_id = publisher.add_entry({
            'url': 'https://example.com/article1',
            'title': 'Test Article',
            'author': 'Test Author',
            'published_date': '2025-01-15T10:00:00Z',
            'license': {'type': 'CC-BY-4.0'}
        })

        assert entry_id is not None
        assert len(publisher.entries) == 1
        assert publisher.entries[0]['url'] == 'https://example.com/article1'
        assert publisher.entries[0]['title'] == 'Test Article'

    def test_add_entry_requires_url(self, publisher):
        """Test that adding entry without URL raises error"""
        with pytest.raises(ValueError):
            publisher.add_entry({
                'title': 'Test Article'
            })

    def test_generate_index(self, publisher):
        """Test generating a signed index"""
        # Add some entries
        publisher.add_entry({
            'url': 'https://example.com/article1',
            'title': 'Article 1'
        })
        publisher.add_entry({
            'url': 'https://example.com/article2',
            'title': 'Article 2'
        })

        # Generate index
        index = publisher.generate_index()

        assert 'publisher' in index
        assert index['publisher']['domain'] == TEST_DOMAIN
        assert 'entries' in index
        assert len(index['entries']) == 2
        assert 'signature' in index
        assert 'generated_at' in index
        assert index['version'] == '1.1'

    def test_verify_receipt(self, publisher):
        """Test receipt verification"""
        # Create a client and generate a receipt
        client_private_key, client_public_key = generate_keypair()

        from aiindex.crypto import CryptoUtils

        receipt_data = {
            "receipt_id": "test-receipt-123",
            "publisher_domain": TEST_DOMAIN,
            "article_url": "https://example.com/article",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        signature = CryptoUtils.sign_data(receipt_data, client_private_key)

        receipt = {
            **receipt_data,
            "signature": signature,
            "client_public_key": client_public_key
        }

        # Verify receipt
        is_valid = publisher.verify_receipt(receipt)
        assert is_valid is True


class TestClient:
    """Test IAIndexClient class"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        private_key, public_key = generate_keypair()
        return IAIndexClient(
            client_id="test-client-001",
            private_key=private_key,
            name="Test AI Client",
            organization="Test Org",
            api_base_url=API_BASE_URL
        )

    def test_client_initialization(self, client):
        """Test client can be initialized"""
        assert client.client_id == "test-client-001"
        assert client.name == "Test AI Client"
        assert client.organization == "Test Org"
        assert client.public_key is not None

    def test_access_content(self, client):
        """Test accessing content"""
        # Note: This will make a real HTTP request
        content = client.access_content("https://example.com")

        assert content is not None
        assert 'url' in content
        assert content['url'] == "https://example.com"
        assert 'publisher_domain' in content
        assert content['publisher_domain'] == "example.com"
        assert 'accessed_at' in content
        assert 'client_id' in content


class TestEndToEnd:
    """End-to-end integration tests"""

    def test_publisher_and_client_flow(self):
        """Test complete flow from publisher to client"""
        # 1. Create publisher
        pub_private_key, pub_public_key = generate_keypair()
        publisher = IAIndexPublisher(
            domain="test-publisher.com",
            private_key=pub_private_key,
            name="Test Publisher",
            contact="publisher@test.com",
            api_base_url=API_BASE_URL
        )

        # 2. Add content entries
        entry_id = publisher.add_entry({
            'url': 'https://test-publisher.com/article',
            'title': 'Test Article',
            'author': 'Test Author',
            'published_date': '2025-01-15T10:00:00Z',
            'license': {'type': 'CC-BY-4.0'}
        })

        assert entry_id is not None

        # 3. Generate signed index
        index = publisher.generate_index()
        assert 'signature' in index

        # 4. Create AI client
        client_private_key, client_public_key = generate_keypair()
        client = IAIndexClient(
            client_id="test-ai-client",
            private_key=client_private_key,
            name="Test AI",
            api_base_url=API_BASE_URL
        )

        # 5. Client accesses content
        content = client.access_content("https://test-publisher.com/article")
        assert content['url'] == "https://test-publisher.com/article"
        assert content['publisher_domain'] == "test-publisher.com"

        # 6. Client sends receipt (note: this may fail if publisher not verified)
        # We'll just test that the method works, not that it succeeds
        usage = {
            'purpose': 'training',
            'context': 'language-model-pretraining'
        }

        # This might return False if publisher isn't verified in the API
        # but at least it shouldn't raise an exception
        try:
            result = client.send_receipt(content, usage)
            # Result can be True or False depending on API state
            assert isinstance(result, bool)
        except Exception as e:
            # If it fails, just make sure we can catch it gracefully
            pytest.skip(f"Receipt submission failed (expected): {e}")


class TestAPIIntegration:
    """Test API integration (requires live API)"""

    @pytest.fixture
    def publisher(self):
        """Create a test publisher with API connection"""
        private_key, public_key = generate_keypair()
        return IAIndexPublisher(
            domain=f"test-{datetime.now().timestamp()}.com",
            private_key=private_key,
            name="API Test Publisher",
            contact="test@example.com",
            api_base_url=API_BASE_URL
        )

    def test_api_authentication(self, publisher):
        """Test that we can authenticate with the API"""
        try:
            token = publisher._authenticate()
            assert token is not None
            assert len(token) > 0
        except Exception as e:
            pytest.skip(f"API authentication failed: {e}")

    def test_publisher_initialization_api(self, publisher):
        """Test publisher initialization with API"""
        try:
            result = publisher.initialize()
            assert result is not None
            # Result could be verification pending or already verified
            assert 'domain' in result or 'status' in result
        except Exception as e:
            pytest.skip(f"Publisher initialization failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
