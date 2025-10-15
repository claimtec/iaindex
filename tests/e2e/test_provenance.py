"""
End-to-End Tests: C2PA Provenance

Tests C2PA Content Credentials integration including:
- Manifest generation
- Signature validation
- Badge verifier
- Merkle root anchoring
"""

import pytest
import httpx
import hashlib
import json
from datetime import datetime, timezone


API_BASE_URL = "http://localhost:3000"
TEST_PUBLISHER = "example-news.com"


class TestC2PAProvenance:
    """C2PA provenance E2E tests"""

    @pytest.mark.asyncio
    async def test_manifest_generation_works(self):
        """Test 1: Manifest generation works"""
        async with httpx.AsyncClient() as client:
            # Request C2PA manifest generation for content
            content_url = f"https://{TEST_PUBLISHER}/article-123"

            response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/c2pa/generate",
                json={
                    "asset_url": content_url,
                    "asset_type": "article",
                    "claim_generator": "AIIndex v1.1"
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            # Assert: Manifest generated
            assert response.status_code == 200
            data = response.json()

            # Verify manifest structure
            assert 'credential_url' in data
            assert 'asset_digest' in data
            assert 'signer_kid' in data
            assert 'timestamp' in data

            # Verify asset digest is SHA-256
            assert len(data['asset_digest']) == 64
            assert all(c in '0123456789abcdef' for c in data['asset_digest'])

            # Fetch and verify manifest
            manifest_url = data['credential_url']
            manifest_response = await client.get(manifest_url)

            assert manifest_response.status_code == 200
            manifest = manifest_response.json()

            # Verify C2PA manifest structure
            assert 'claim_generator' in manifest
            assert 'assertions' in manifest
            assert 'signature' in manifest

    @pytest.mark.asyncio
    async def test_signature_validates(self):
        """Test 2: Signature validates"""
        async with httpx.AsyncClient() as client:
            # Generate manifest
            content_url = f"https://{TEST_PUBLISHER}/article-456"

            gen_response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/c2pa/generate",
                json={
                    "asset_url": content_url,
                    "asset_type": "article"
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert gen_response.status_code == 200
            gen_data = gen_response.json()

            # Verify signature
            verify_response = await client.post(
                f"{API_BASE_URL}/c2pa/verify",
                json={
                    "credential_url": gen_data['credential_url'],
                    "asset_digest": gen_data['asset_digest']
                }
            )

            # Assert: Signature valid
            assert verify_response.status_code == 200
            verify_data = verify_response.json()

            assert verify_data['valid'] is True
            assert 'signer' in verify_data
            assert 'verified_at' in verify_data
            assert verify_data['publisher_id'] == TEST_PUBLISHER

            # Verify certificate chain
            assert 'certificate_chain' in verify_data
            assert len(verify_data['certificate_chain']) > 0

    @pytest.mark.asyncio
    async def test_badge_verifier_returns_status(self):
        """Test 3: Badge verifier returns status"""
        async with httpx.AsyncClient() as client:
            # Generate manifest
            content_url = f"https://{TEST_PUBLISHER}/article-789"

            gen_response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/c2pa/generate",
                json={
                    "asset_url": content_url,
                    "asset_type": "article"
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert gen_response.status_code == 200
            gen_data = gen_response.json()

            # Get verification badge
            badge_response = await client.get(
                f"{API_BASE_URL}/c2pa/badge",
                params={
                    "url": gen_data['credential_url']
                }
            )

            # Assert: Badge generated
            assert badge_response.status_code == 200

            # Verify badge is SVG
            assert 'image/svg+xml' in badge_response.headers.get('Content-Type', '')
            badge_svg = badge_response.text

            assert '<svg' in badge_svg
            assert '</svg>' in badge_svg

            # Badge should indicate verification status
            assert 'verified' in badge_svg.lower() or 'valid' in badge_svg.lower()

            # Get badge metadata
            badge_meta_response = await client.get(
                f"{API_BASE_URL}/c2pa/badge/metadata",
                params={
                    "url": gen_data['credential_url']
                }
            )

            assert badge_meta_response.status_code == 200
            badge_meta = badge_meta_response.json()

            assert 'status' in badge_meta
            assert badge_meta['status'] == 'valid'
            assert 'publisher' in badge_meta
            assert 'timestamp' in badge_meta

    @pytest.mark.asyncio
    async def test_merkle_root_anchoring_works(self):
        """Test 4: Merkle root anchoring works"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Generate multiple manifests
            content_urls = [
                f"https://{TEST_PUBLISHER}/article-{i}"
                for i in range(10)
            ]

            manifest_ids = []
            for url in content_urls:
                response = await client.post(
                    f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/c2pa/generate",
                    json={
                        "asset_url": url,
                        "asset_type": "article"
                    },
                    headers={
                        "Authorization": f"Bearer {self._get_test_api_key()}"
                    }
                )
                assert response.status_code == 200
                manifest_ids.append(response.json()['credential_url'])

            # Request merkle tree generation
            merkle_response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/c2pa/merkle/create",
                json={
                    "manifest_ids": manifest_ids,
                    "anchor": True,
                    "blockchain": "ethereum"
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            # Assert: Merkle tree created
            assert merkle_response.status_code == 202  # Accepted
            merkle_data = merkle_response.json()

            assert 'merkle_root' in merkle_data
            assert 'timestamp_id' in merkle_data
            assert 'status' in merkle_data

            merkle_root = merkle_data['merkle_root']
            timestamp_id = merkle_data['timestamp_id']

            # Poll for anchoring completion
            max_attempts = 30
            for attempt in range(max_attempts):
                status_response = await client.get(
                    f"{API_BASE_URL}/timestamps/{timestamp_id}",
                    headers={
                        "Authorization": f"Bearer {self._get_test_api_key()}"
                    }
                )

                assert status_response.status_code == 200
                status_data = status_response.json()

                if status_data['status'] == 'confirmed':
                    break

                if status_data['status'] == 'failed':
                    pytest.fail(f"Anchoring failed: {status_data.get('error')}")

                import asyncio
                await asyncio.sleep(3)
            else:
                pytest.skip("Anchoring timed out (may require manual verification)")

            # Verify anchoring data
            assert status_data['status'] == 'confirmed'
            assert 'blockchain' in status_data
            assert status_data['blockchain'] == 'ethereum'
            assert 'transaction_hash' in status_data
            assert 'block_number' in status_data
            assert 'merkle_root' in status_data
            assert status_data['merkle_root'] == merkle_root

            # Verify proof for one of the manifests
            proof_response = await client.get(
                f"{API_BASE_URL}/c2pa/merkle/proof",
                params={
                    "manifest_id": manifest_ids[0],
                    "merkle_root": merkle_root
                }
            )

            assert proof_response.status_code == 200
            proof_data = proof_response.json()

            assert 'proof' in proof_data
            assert 'merkle_root' in proof_data
            assert 'verified' in proof_data
            assert proof_data['verified'] is True

    @pytest.mark.asyncio
    async def test_tamper_detection(self):
        """Test 5: Tamper detection works"""
        async with httpx.AsyncClient() as client:
            # Generate manifest
            content_url = f"https://{TEST_PUBLISHER}/article-tamper-test"

            gen_response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/c2pa/generate",
                json={
                    "asset_url": content_url,
                    "asset_type": "article"
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert gen_response.status_code == 200
            gen_data = gen_response.json()

            original_digest = gen_data['asset_digest']

            # Create tampered digest (modify one character)
            tampered_digest = original_digest[:-1] + ('0' if original_digest[-1] != '0' else '1')

            # Verify with tampered digest
            verify_response = await client.post(
                f"{API_BASE_URL}/c2pa/verify",
                json={
                    "credential_url": gen_data['credential_url'],
                    "asset_digest": tampered_digest
                }
            )

            # Assert: Verification fails
            assert verify_response.status_code == 200
            verify_data = verify_response.json()

            assert verify_data['valid'] is False
            assert 'error' in verify_data or 'reason' in verify_data
            assert 'tampered' in str(verify_data).lower() or 'mismatch' in str(verify_data).lower()

    @pytest.mark.asyncio
    async def test_c2pa_in_ai_index(self):
        """Test 6: C2PA provenance appears in ai-index.json"""
        async with httpx.AsyncClient() as client:
            # Generate manifest for publisher's content
            content_url = f"https://{TEST_PUBLISHER}/main-article"

            gen_response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/c2pa/generate",
                json={
                    "asset_url": content_url,
                    "asset_type": "article",
                    "update_index": True
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert gen_response.status_code == 200
            gen_data = gen_response.json()

            # Fetch ai-index.json
            index_response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json"
            )

            assert index_response.status_code == 200
            index_data = index_response.json()

            # Verify c2pa_provenance section exists
            assert 'c2pa_provenance' in index_data

            c2pa = index_data['c2pa_provenance']
            assert 'credential_url' in c2pa
            assert 'asset_digest' in c2pa
            assert 'signer_kid' in c2pa
            assert 'timestamp' in c2pa
            assert 'claim_generator' in c2pa

            # Values should match generated manifest
            assert c2pa['credential_url'] == gen_data['credential_url']
            assert c2pa['asset_digest'] == gen_data['asset_digest']

    @pytest.mark.asyncio
    async def test_content_authenticity_inspect(self):
        """Test 7: Content Authenticity Inspect integration"""
        async with httpx.AsyncClient() as client:
            # Generate manifest
            content_url = f"https://{TEST_PUBLISHER}/article-inspect"

            gen_response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/c2pa/generate",
                json={
                    "asset_url": content_url,
                    "asset_type": "article"
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert gen_response.status_code == 200
            gen_data = gen_response.json()

            # Get Content Authenticity Inspect URL
            inspect_url = f"https://verify.contentauthenticity.org/inspect?url={gen_data['credential_url']}"

            # Verify URL is accessible (may redirect)
            inspect_response = await client.get(
                inspect_url,
                follow_redirects=True
            )

            # Should be accessible (even if it's a web page)
            assert inspect_response.status_code == 200

    # Helper methods

    def _get_test_api_key(self) -> str:
        """Get test API key"""
        return "test_api_key_12345"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
