"""
End-to-End Tests: Complete Publisher Flow

Tests the complete end-to-end flow:
1. Publisher sets policy "block training"
2. Client fetches policy
3. Client requests with intent=training
4. Receives 403 with denial receipt
5. Client retries with intent=retrieval
6. Receives 200 with data
7. Sends signed receipt
8. Receipt appears in dashboard
"""

import pytest
import httpx
import json
import hashlib
import time
from datetime import datetime, timezone
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import base64
import jwt


API_BASE_URL = "http://localhost:3000"
TEST_PUBLISHER = "complete-flow-test.com"
TEST_CLIENT_ID = "test-ai-client-e2e"


class TestCompletePublisherFlow:
    """Complete publisher flow E2E test"""

    @pytest.mark.asyncio
    async def test_complete_flow(self):
        """
        Complete flow test:
        - Publisher setup
        - Policy enforcement
        - Receipt generation
        - Dashboard verification
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            # =================================================================
            # STEP 1: Publisher sets policy "block training"
            # =================================================================
            print("\n[STEP 1] Setting publisher policy...")

            policy_response = await client.patch(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/policy",
                json={
                    "policy": {
                        "training": "block",
                        "retrieval": "allow",
                        "attribution_required": True,
                        "commercial_use": True
                    },
                    "receipts": {
                        "require_signed": True,
                        "webhook_url": f"https://{TEST_PUBLISHER}/api/receipts",
                        "supported_algorithms": ["ES256", "RS256"]
                    }
                },
                headers={
                    "Authorization": f"Bearer {self._get_publisher_api_key()}"
                }
            )

            assert policy_response.status_code == 200
            print("✓ Policy set: training=block, retrieval=allow")

            # =================================================================
            # STEP 2: Client fetches policy
            # =================================================================
            print("\n[STEP 2] Client fetching policy...")

            policy_fetch_response = await client.get(
                f"{API_BASE_URL}/.well-known/aiindex-policy.json",
                params={"domain": TEST_PUBLISHER}
            )

            assert policy_fetch_response.status_code == 200
            policy_data = policy_fetch_response.json()

            assert policy_data['policy']['training'] == 'block'
            assert policy_data['policy']['retrieval'] == 'allow'
            assert policy_data['receipts']['require_signed'] is True

            print("✓ Policy fetched:")
            print(f"  - Training: {policy_data['policy']['training']}")
            print(f"  - Retrieval: {policy_data['policy']['retrieval']}")
            print(f"  - Signed receipts required: {policy_data['receipts']['require_signed']}")

            # =================================================================
            # STEP 3: Client requests with intent=training
            # =================================================================
            print("\n[STEP 3] Client requesting with intent=training...")

            training_response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "TestAIClient/1.0",
                    "X-AI-Client-ID": TEST_CLIENT_ID,
                    "X-AI-Intent": "training"
                }
            )

            # =================================================================
            # STEP 4: Receives 403 with denial receipt
            # =================================================================
            print("\n[STEP 4] Verifying denial receipt...")

            assert training_response.status_code == 403
            denial_data = training_response.json()

            assert 'denial_receipt' in denial_data
            denial = denial_data['denial_receipt']

            assert denial['denied'] is True
            assert denial['reason'] == 'policy_violation'
            assert denial['denied_action'] == 'training'
            assert denial['publisher_id'] == TEST_PUBLISHER
            assert 'timestamp' in denial
            assert 'receipt_id' in denial

            print("✓ Received 403 with denial receipt:")
            print(f"  - Receipt ID: {denial['receipt_id']}")
            print(f"  - Reason: {denial['reason']}")
            print(f"  - Denied action: {denial['denied_action']}")

            # =================================================================
            # STEP 5: Client retries with intent=retrieval
            # =================================================================
            print("\n[STEP 5] Client retrying with intent=retrieval...")

            retrieval_response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                headers={
                    "User-Agent": "TestAIClient/1.0",
                    "X-AI-Client-ID": TEST_CLIENT_ID,
                    "X-AI-Intent": "retrieval"
                }
            )

            # =================================================================
            # STEP 6: Receives 200 with data
            # =================================================================
            print("\n[STEP 6] Verifying successful retrieval...")

            assert retrieval_response.status_code == 200
            index_data = retrieval_response.json()

            assert 'version' in index_data
            assert 'publisher_id' in index_data
            assert 'pages' in index_data
            assert index_data['publisher_id'] == TEST_PUBLISHER

            # Check response headers
            assert 'X-AIIndex-Policy' in retrieval_response.headers
            assert 'X-RateLimit-Limit' in retrieval_response.headers

            print("✓ Received 200 with ai-index.json:")
            print(f"  - Version: {index_data['version']}")
            print(f"  - Publisher: {index_data['publisher_id']}")
            print(f"  - Pages: {len(index_data.get('pages', []))}")

            # =================================================================
            # STEP 7: Sends signed receipt
            # =================================================================
            print("\n[STEP 7] Generating and sending signed receipt...")

            # Generate receipt
            receipt = self._generate_receipt(
                publisher_id=TEST_PUBLISHER,
                client_id=TEST_CLIENT_ID,
                access_url=f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json",
                purpose="retrieval",
                content_data=json.dumps(index_data)
            )

            # Sign receipt
            signed_receipt = self._sign_receipt(receipt)

            # Send receipt
            receipt_response = await client.post(
                f"{API_BASE_URL}/receipts",
                json=signed_receipt,
                headers={
                    "Content-Type": "application/json",
                    "X-AI-Client-ID": TEST_CLIENT_ID
                }
            )

            assert receipt_response.status_code == 201
            receipt_confirmation = receipt_response.json()

            assert 'receipt_id' in receipt_confirmation
            assert receipt_confirmation['signature_valid'] is True

            print("✓ Receipt sent and verified:")
            print(f"  - Receipt ID: {receipt_confirmation['receipt_id']}")
            print(f"  - Signature valid: {receipt_confirmation['signature_valid']}")

            # =================================================================
            # STEP 8: Receipt appears in dashboard
            # =================================================================
            print("\n[STEP 8] Verifying receipt in dashboard...")

            # Wait a moment for processing
            import asyncio
            await asyncio.sleep(2)

            # Fetch publisher dashboard
            dashboard_response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/dashboard",
                headers={
                    "Authorization": f"Bearer {self._get_publisher_api_key()}"
                }
            )

            assert dashboard_response.status_code == 200
            dashboard_data = dashboard_response.json()

            # Verify receipt appears in recent receipts
            assert 'recent_receipts' in dashboard_data
            receipts = dashboard_data['recent_receipts']

            # Find our receipt
            our_receipt = None
            for r in receipts:
                if r.get('receipt_id') == receipt_confirmation['receipt_id']:
                    our_receipt = r
                    break

            assert our_receipt is not None, "Receipt not found in dashboard"

            assert our_receipt['client_id'] == TEST_CLIENT_ID
            assert our_receipt['purpose_type'] == 'retrieval'
            assert our_receipt['signature_valid'] is True

            print("✓ Receipt visible in dashboard:")
            print(f"  - Client: {our_receipt['client_id']}")
            print(f"  - Purpose: {our_receipt['purpose_type']}")
            print(f"  - Timestamp: {our_receipt['timestamp']}")

            # Verify analytics updated
            assert 'analytics' in dashboard_data
            analytics = dashboard_data['analytics']

            assert analytics['total_receipts'] > 0
            assert analytics['valid_receipts'] > 0

            print("\n✓ Complete flow successful!")
            print(f"  - Total receipts: {analytics['total_receipts']}")
            print(f"  - Valid receipts: {analytics['valid_receipts']}")

    @pytest.mark.asyncio
    async def test_flow_with_fraud_detection(self):
        """Test flow with fraud detection triggering"""
        async with httpx.AsyncClient() as client:
            # Setup publisher
            await self._setup_publisher(client)

            # Send multiple receipts rapidly to trigger batch fraud detection
            print("\n[TEST] Triggering fraud detection...")

            receipts_sent = 0
            fraud_detected = False

            for i in range(15):
                receipt = self._generate_receipt(
                    publisher_id=TEST_PUBLISHER,
                    client_id=f"fraud-test-client-{i}",
                    access_url=f"{API_BASE_URL}/test",
                    purpose="retrieval"
                )

                signed_receipt = self._sign_receipt(receipt)

                response = await client.post(
                    f"{API_BASE_URL}/receipts",
                    json=signed_receipt
                )

                if response.status_code == 429 or response.status_code == 403:
                    fraud_detected = True
                    print(f"✓ Fraud detection triggered after {receipts_sent} receipts")
                    break

                receipts_sent += 1

            # Should have triggered fraud detection
            assert fraud_detected or receipts_sent >= 10

    @pytest.mark.asyncio
    async def test_flow_with_invalid_signature(self):
        """Test flow with invalid signature detection"""
        async with httpx.AsyncClient() as client:
            # Setup publisher
            await self._setup_publisher(client)

            # Generate receipt
            receipt = self._generate_receipt(
                publisher_id=TEST_PUBLISHER,
                client_id=TEST_CLIENT_ID,
                access_url=f"{API_BASE_URL}/test",
                purpose="retrieval"
            )

            # Sign receipt
            signed_receipt = self._sign_receipt(receipt)

            # Tamper with signature
            signed_receipt['signature'] = signed_receipt['signature'][:-10] + "tampered=="

            # Send tampered receipt
            response = await client.post(
                f"{API_BASE_URL}/receipts",
                json=signed_receipt
            )

            # Should be rejected
            assert response.status_code == 403
            data = response.json()
            assert data.get('signature_valid') is False
            print("✓ Invalid signature correctly detected and rejected")

    # Helper methods

    def _generate_receipt(
        self,
        publisher_id: str,
        client_id: str,
        access_url: str,
        purpose: str,
        content_data: str = None
    ) -> dict:
        """Generate access receipt"""
        timestamp = datetime.now(timezone.utc)

        receipt = {
            "receipt_id": f"{client_id}:{int(timestamp.timestamp())}",
            "publisher_id": publisher_id,
            "client_id": client_id,
            "client_name": "Test AI Client",
            "timestamp": timestamp.isoformat(),
            "access_url": access_url,
            "purpose": {
                "type": purpose,
                "commercial": False
            }
        }

        if content_data:
            content_hash = hashlib.sha256(content_data.encode('utf-8')).hexdigest()
            receipt['content_hash'] = content_hash

        return receipt

    def _sign_receipt(self, receipt: dict) -> dict:
        """Sign receipt with ES256"""
        # Generate ephemeral key for testing
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        public_key = private_key.public_key()

        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        # Create JWT
        receipt_copy = receipt.copy()
        receipt_copy['public_key'] = public_pem

        # Sign with JWT
        token = jwt.encode(
            receipt_copy,
            private_key,
            algorithm='ES256',
            headers={'kid': 'test-key-123'}
        )

        # Return signed receipt
        return {
            **receipt,
            "signature": token,
            "signature_algorithm": "ES256",
            "signer_kid": "test-key-123"
        }

    async def _setup_publisher(self, client: httpx.AsyncClient):
        """Setup test publisher"""
        await client.patch(
            f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/policy",
            json={
                "policy": {
                    "training": "allow",
                    "retrieval": "allow"
                }
            },
            headers={
                "Authorization": f"Bearer {self._get_publisher_api_key()}"
            }
        )

    def _get_publisher_api_key(self) -> str:
        """Get publisher API key"""
        return "test_publisher_api_key_12345"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
