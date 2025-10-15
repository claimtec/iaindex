"""
End-to-End Tests: Render Fallback

Tests dynamic content rendering features including:
- Render snapshot creation
- Cache with ETag
- Rendered text in ai-index.json
- S3 storage
"""

import pytest
import httpx
import hashlib
from datetime import datetime, timezone


API_BASE_URL = "http://localhost:3000"
TEST_PUBLISHER = "example-spa.com"  # SPA publisher with dynamic content


class TestRenderFallback:
    """Render fallback E2E tests"""

    @pytest.mark.asyncio
    async def test_render_snapshot_creates_content_hash(self):
        """Test 1: Render snapshot creates content_hash"""
        async with httpx.AsyncClient() as client:
            # Request render of a dynamic page
            page_url = f"https://{TEST_PUBLISHER}/dashboard"

            response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render",
                json={
                    "url": page_url,
                    "mode": "edge"
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            # Assert: Render successful
            assert response.status_code == 200
            data = response.json()

            assert 'rendered_text' in data
            assert 'content_hash' in data
            assert len(data['rendered_text']) > 0

            # Verify content_hash matches rendered content
            computed_hash = hashlib.sha256(
                data['rendered_text'].encode('utf-8')
            ).hexdigest()
            assert data['content_hash'] == computed_hash

            # Verify metadata
            assert 'rendered_at' in data
            assert 'render_time_ms' in data
            assert 'storage_url' in data

    @pytest.mark.asyncio
    async def test_cache_returns_etag(self):
        """Test 2: Cache returns ETag"""
        async with httpx.AsyncClient() as client:
            # First request: render and cache
            page_url = f"https://{TEST_PUBLISHER}/products"

            response1 = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render",
                json={
                    "url": page_url,
                    "mode": "edge",
                    "cache_ttl": 3600
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert response1.status_code == 200
            etag1 = response1.headers.get('ETag')
            assert etag1 is not None

            # Second request: should return cached version with same ETag
            response2 = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render/{page_url}",
                headers={
                    "If-None-Match": etag1
                }
            )

            # Assert: 304 Not Modified
            assert response2.status_code == 304

            # Third request: without ETag should return cached content
            response3 = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render/{page_url}"
            )

            assert response3.status_code == 200
            etag3 = response3.headers.get('ETag')
            assert etag3 == etag1

            # Verify cache headers
            assert 'X-Cache' in response3.headers
            assert response3.headers['X-Cache'] == 'HIT'

    @pytest.mark.asyncio
    async def test_rendered_text_populates_ai_index(self):
        """Test 3: Rendered text populates ai-index.json"""
        async with httpx.AsyncClient() as client:
            # Render a page
            page_url = f"https://{TEST_PUBLISHER}/about"

            render_response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render",
                json={
                    "url": page_url,
                    "mode": "edge",
                    "update_index": True
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert render_response.status_code == 200
            render_data = render_response.json()

            # Fetch ai-index.json
            index_response = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/ai-index.json"
            )

            assert index_response.status_code == 200
            index_data = index_response.json()

            # Find the rendered page in index
            page_found = False
            for page in index_data.get('pages', []):
                if page['url'] == page_url:
                    page_found = True
                    assert 'rendered_text' in page
                    assert page['rendered_text'] == render_data['rendered_text']
                    assert page['content_hash'] == render_data['content_hash']
                    break

            assert page_found, f"Page {page_url} not found in index"

            # Verify render_fallback section updated
            assert 'render_fallback' in index_data
            assert index_data['render_fallback']['mode'] == 'edge'
            assert 'last_rendered_at' in index_data['render_fallback']

    @pytest.mark.asyncio
    async def test_s3_storage_works(self):
        """Test 4: S3 storage works"""
        async with httpx.AsyncClient() as client:
            # Render with S3 storage
            page_url = f"https://{TEST_PUBLISHER}/blog/article-1"

            response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render",
                json={
                    "url": page_url,
                    "mode": "edge",
                    "storage": "s3",
                    "bucket": "aiindex-renders"
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Verify S3 URL returned
            assert 'storage_url' in data
            storage_url = data['storage_url']
            assert storage_url.startswith('https://') or storage_url.startswith('s3://')
            assert 'aiindex-renders' in storage_url

            # Verify content accessible from S3
            if storage_url.startswith('https://'):
                s3_response = await client.get(storage_url)
                assert s3_response.status_code == 200
                s3_content = s3_response.text

                # Content should match rendered text
                assert s3_content == data['rendered_text']

                # Verify content hash
                computed_hash = hashlib.sha256(s3_content.encode('utf-8')).hexdigest()
                assert computed_hash == data['content_hash']

    @pytest.mark.asyncio
    async def test_batch_render_multiple_pages(self):
        """Test 5: Batch render multiple pages"""
        async with httpx.AsyncClient() as client:
            # Batch render request
            pages = [
                f"https://{TEST_PUBLISHER}/page1",
                f"https://{TEST_PUBLISHER}/page2",
                f"https://{TEST_PUBLISHER}/page3"
            ]

            response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render/batch",
                json={
                    "urls": pages,
                    "mode": "edge",
                    "update_index": True
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Verify all pages rendered
            assert 'results' in data
            assert len(data['results']) == len(pages)

            for result in data['results']:
                assert result['status'] == 'success'
                assert 'rendered_text' in result
                assert 'content_hash' in result
                assert 'url' in result

            # Verify batch statistics
            assert 'total' in data
            assert 'successful' in data
            assert 'failed' in data
            assert data['successful'] == len(pages)

    @pytest.mark.asyncio
    async def test_render_mode_local_fallback(self):
        """Test 6: Render mode local fallback"""
        async with httpx.AsyncClient() as client:
            # Configure local render mode
            await client.patch(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/config",
                json={
                    "render_fallback": {
                        "mode": "local",
                        "browser_path": "/usr/bin/chromium"
                    }
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            # Request render
            page_url = f"https://{TEST_PUBLISHER}/dynamic-page"

            response = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render",
                json={
                    "url": page_url
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Verify rendered with local mode
            assert 'render_mode' in data
            assert data['render_mode'] == 'local'

    @pytest.mark.asyncio
    async def test_render_ttl_expiration(self):
        """Test 7: Render TTL expiration"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Render with short TTL
            page_url = f"https://{TEST_PUBLISHER}/ttl-test"

            response1 = await client.post(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render",
                json={
                    "url": page_url,
                    "mode": "edge",
                    "cache_ttl": 2  # 2 seconds
                },
                headers={
                    "Authorization": f"Bearer {self._get_test_api_key()}"
                }
            )

            assert response1.status_code == 200
            etag1 = response1.headers.get('ETag')

            # Immediate request should return cached
            response2 = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render/{page_url}"
            )
            assert response2.headers.get('X-Cache') == 'HIT'

            # Wait for TTL expiration
            import asyncio
            await asyncio.sleep(3)

            # Request after TTL should re-render
            response3 = await client.get(
                f"{API_BASE_URL}/publishers/{TEST_PUBLISHER}/render/{page_url}"
            )
            assert response3.headers.get('X-Cache') == 'MISS'
            etag3 = response3.headers.get('ETag')

            # ETag may differ if content changed
            # (or same if content identical)

    # Helper methods

    def _get_test_api_key(self) -> str:
        """Get test API key"""
        return "test_api_key_12345"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
