"""
End-to-End Tests: Embeddings

Tests vector embeddings features including:
- Build embeddings from content
- Semantic query
- Manifest URL validation
- Verified publisher requirements
"""

import pytest
import httpx
import numpy as np
from typing import List


API_BASE_URL = "http://localhost:3000"
TEST_PUBLISHER = "example-docs.com"


class TestEmbeddings:
    """Embeddings E2E tests"""

    @pytest.mark.asyncio
    async def test_build_embeddings_creates_vectors(self):
        """Test 1: Build embeddings creates vectors"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Request embeddings build
            response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/build",
                json={
                    "model": "text-embedding-ada-002",
                    "batch_size": 100
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            # Assert: Build initiated
            assert response.status_code == 202  # Accepted
            data = response.json()

            assert 'job_id' in data
            assert 'status' in data
            assert data['status'] in ['pending', 'processing']

            job_id = data['job_id']

            # Poll for completion
            max_attempts = 30
            for attempt in range(max_attempts):
                status_response = await client.get(
                    f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/jobs/{job_id}",
                    headers={
                        "Authorization": f"Bearer {self._get_test_api_key()}"
                    }
                )

                assert status_response.status_code == 200
                status_data = status_response.json()

                if status_data['status'] == 'completed':
                    break

                if status_data['status'] == 'failed':
                    pytest.fail(f"Embeddings build failed: {status_data.get('error')}")

                import asyncio
                await asyncio.sleep(2)
            else:
                pytest.fail("Embeddings build timed out")

            # Verify completion data
            assert status_data['status'] == 'completed'
            assert 'vectors_created' in status_data
            assert status_data['vectors_created'] > 0
            assert 'manifest_url' in status_data

    @pytest.mark.asyncio
    async def test_semantic_query_returns_results(self):
        """Test 2: Semantic query returns results"""
        async with httpx.AsyncClient() as client:
            # Ensure embeddings exist
            await self._ensure_embeddings_built(client)

            # Perform semantic search
            query = "How do I implement authentication?"

            response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/search",
                json={
                    "query": query,
                    "top_k": 5,
                    "threshold": 0.7
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            # Assert: Search successful
            assert response.status_code == 200
            data = response.json()

            assert 'results' in data
            assert len(data['results']) > 0
            assert len(data['results']) <= 5

            # Verify result structure
            for result in data['results']:
                assert 'url' in result
                assert 'title' in result
                assert 'similarity' in result
                assert 'text_snippet' in result

                # Similarity should be in valid range
                assert 0.0 <= result['similarity'] <= 1.0
                assert result['similarity'] >= 0.7  # Above threshold

            # Results should be sorted by similarity (descending)
            similarities = [r['similarity'] for r in data['results']]
            assert similarities == sorted(similarities, reverse=True)

    @pytest.mark.asyncio
    async def test_manifest_url_is_valid(self):
        """Test 3: Manifest URL is valid"""
        async with httpx.AsyncClient() as client:
            # Get ai-index.json with embeddings
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json"
            )

            assert response.status_code == 200
            data = response.json()

            # Verify embeddings manifest exists
            assert 'embeddings_manifest' in data
            manifest = data['embeddings_manifest']

            assert 'model' in manifest
            assert 'dimensions' in manifest
            assert 'vector_url' in manifest
            assert 'last_updated' in manifest
            assert 'format' in manifest

            # Fetch vector data from manifest URL
            vector_url = manifest['vector_url']
            vector_response = await client.get(vector_url)

            assert vector_response.status_code == 200

            # Verify vector data format
            vector_format = manifest['format']
            if vector_format == 'json':
                vectors = vector_response.json()
                assert isinstance(vectors, list)
                assert len(vectors) > 0

                # Check first vector structure
                first_vector = vectors[0]
                assert 'id' in first_vector
                assert 'url' in first_vector
                assert 'embedding' in first_vector
                assert len(first_vector['embedding']) == manifest['dimensions']

            elif vector_format == 'parquet':
                # Parquet format - just verify content exists
                assert len(vector_response.content) > 0

    @pytest.mark.asyncio
    async def test_only_verified_publishers_can_build(self):
        """Test 4: Only verified publishers can build embeddings"""
        async with httpx.AsyncClient() as client:
            # Try to build embeddings for unverified publisher
            unverified_publisher = "unverified-site.com"

            response = await client.post(
                f"{API_BASE_URL}/publishers/{unverified_publisher}/embeddings/build",
                json={
                    "model": "text-embedding-ada-002"
                },
                headers={
                    "Authorization": f"Bearer {self._get_unverified_api_key()}"
                }
            )

            # Assert: Request rejected
            assert response.status_code == 403
            data = response.json()

            assert 'error' in data
            assert 'verified' in data['error'].lower() or 'subscription' in data['error'].lower()

    @pytest.mark.asyncio
    async def test_embeddings_incremental_update(self):
        """Test 5: Embeddings incremental update"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Initial build
            await self._ensure_embeddings_built(client)

            # Add new content to publisher
            new_page = {
                "url": f"https://{TEST_PUBLISHER}/new-article",
                "title": "New Article Title",
                "summary": "This is a new article about embeddings"
            }

            await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/pages",
                json=new_page,
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            # Request incremental update
            response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/update",
                json={
                    "mode": "incremental"
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert response.status_code == 202
            data = response.json()
            job_id = data['job_id']

            # Wait for completion
            await self._wait_for_job(client, job_id)

            # Verify new page is searchable
            search_response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/search",
                json={
                    "query": "embeddings",
                    "top_k": 10
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            results = search_response.json()['results']
            urls = [r['url'] for r in results]
            assert new_page['url'] in urls

    @pytest.mark.asyncio
    async def test_embeddings_model_compatibility(self):
        """Test 6: Embeddings model compatibility"""
        async with httpx.AsyncClient() as client:
            # List supported models
            response = await client.get(
                f"{API_BASE_URL}/embeddings/models"
            )

            assert response.status_code == 200
            data = response.json()

            assert 'models' in data
            models = data['models']

            # Verify common models are supported
            model_names = [m['name'] for m in models]
            assert 'text-embedding-ada-002' in model_names
            assert 'all-MiniLM-L6-v2' in model_names

            # Verify model metadata
            for model in models:
                assert 'name' in model
                assert 'dimensions' in model
                assert 'max_tokens' in model
                assert 'cost_per_1k_tokens' in model

    @pytest.mark.asyncio
    async def test_vector_export_formats(self):
        """Test 7: Vector export formats"""
        async with httpx.AsyncClient() as client:
            # Ensure embeddings exist
            await self._ensure_embeddings_built(client)

            # Test JSON export
            json_response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/export?format=json",
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )
            assert json_response.status_code == 200
            json_data = json_response.json()
            assert isinstance(json_data, list)

            # Test Parquet export
            parquet_response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/export?format=parquet",
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )
            assert parquet_response.status_code == 200
            assert len(parquet_response.content) > 0

            # Test NumPy export
            npy_response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/export?format=npy",
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )
            assert npy_response.status_code == 200
            assert len(npy_response.content) > 0

    # Helper methods

    async def _ensure_embeddings_built(self, client: httpx.AsyncClient):
        """Ensure embeddings are built for test publisher"""
        # Check if already built
        response = await client.get(
            f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/status",
            headers={
                "Authorization": f"Bearer {self._get_test_api_key()}"
            }
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ready':
                return

        # Build embeddings
        build_response = await client.post(
            f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/build",
            json={
                "model": "text-embedding-ada-002"
            },
            headers={
                "Authorization": f"Bearer {self._get_test_api_key()}"
            }
        )

        if build_response.status_code == 202:
            job_id = build_response.json()['job_id']
            await self._wait_for_job(client, job_id)

    async def _wait_for_job(self, client: httpx.AsyncClient, job_id: str):
        """Wait for embeddings job to complete"""
        max_attempts = 30
        for _ in range(max_attempts):
            response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/embeddings/jobs/{job_id}",
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'completed':
                    return
                if data['status'] == 'failed':
                    pytest.fail(f"Job failed: {data.get('error')}")

            import asyncio
            await asyncio.sleep(2)

        pytest.fail("Job timed out")

    def _get_test_api_key(self) -> str:
        """Get test API key for verified publisher"""
        return "test_verified_api_key_12345"

    def _get_unverified_api_key(self) -> str:
        """Get test API key for unverified publisher"""
        return "test_unverified_api_key_67890"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
