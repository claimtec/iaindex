"""
IAIndex AI Client Example

This example demonstrates how AI applications should:
1. Access content from publishers
2. Generate and send cryptographic receipts
3. Verify receipt submission
"""

import os
import json
import hashlib
import hmac
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', 'https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io')
API_KEY = os.getenv('API_KEY', '')
CLIENT_ID = os.getenv('CLIENT_ID', 'my-ai-client')
CLIENT_VERSION = os.getenv('CLIENT_VERSION', '1.0.0')
SECRET_KEY = os.getenv('SECRET_KEY', 'demo-secret')


class IAIndexClient:
    """
    IAIndex client for AI applications

    Handles content access and automatic receipt generation.
    """

    def __init__(self, api_key: str = None, client_id: str = None):
        """
        Initialize IAIndex client

        Args:
            api_key: Optional API key for authenticated requests
            client_id: Unique identifier for this AI client
        """
        self.api_key = api_key or API_KEY
        self.client_id = client_id or CLIENT_ID
        self.base_url = API_BASE_URL
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            })

    def fetch_ai_index(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Fetch AI-Index file from a publisher's domain

        Args:
            domain: Publisher domain (e.g., 'example.com')

        Returns:
            Parsed AI-Index data or None if not found
        """
        print(f"\n=== Fetching AI-Index from {domain} ===\n")

        # Try HTTPS first, then HTTP
        for protocol in ['https', 'http']:
            url = f"{protocol}://{domain}/ai-index.json"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Successfully fetched AI-Index from {url}")
                    print(f"  Publisher: {data.get('publisher', {}).get('name', 'Unknown')}")
                    print(f"  Pages: {len(data.get('pages', []))}")
                    print(f"  Version: {data.get('version', 'Unknown')}")
                    return data
            except Exception as e:
                continue

        print(f"✗ Failed to fetch AI-Index from {domain}")
        return None

    def access_content(self, article_url: str) -> Optional[Dict[str, Any]]:
        """
        Access content and extract relevant information

        In a real implementation, this would:
        - Fetch the content
        - Extract structured data
        - Parse metadata

        Args:
            article_url: URL of the article to access

        Returns:
            Content metadata
        """
        print(f"\n=== Accessing Content ===")
        print(f"URL: {article_url}\n")

        try:
            response = requests.get(article_url, timeout=10)

            # In a real implementation, parse the content here
            # For demo purposes, return basic metadata

            content_data = {
                'url': article_url,
                'status_code': response.status_code,
                'content_length': len(response.content),
                'accessed_at': datetime.utcnow().isoformat(),
                'client_id': self.client_id
            }

            print(f"✓ Content accessed successfully")
            print(f"  Status: {response.status_code}")
            print(f"  Size: {len(response.content)} bytes")

            return content_data

        except Exception as e:
            print(f"✗ Failed to access content: {e}")
            return None

    def generate_signature(self, receipt_id: str, domain: str,
                          article_url: str, timestamp: str) -> str:
        """
        Generate HMAC signature for receipt

        Args:
            receipt_id: Unique receipt identifier
            domain: Publisher domain
            article_url: Article URL
            timestamp: ISO 8601 timestamp

        Returns:
            Hex-encoded signature
        """
        signature_data = f"{receipt_id}:{domain}:{article_url}:{timestamp}"
        signature = hmac.new(
            SECRET_KEY.encode(),
            signature_data.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def send_receipt(self, publisher_domain: str, article_url: str,
                     metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Generate and send a cryptographic receipt to IAIndex

        Args:
            publisher_domain: Publisher's verified domain
            article_url: URL of accessed article
            metadata: Optional additional metadata

        Returns:
            Receipt response or None if failed
        """
        print(f"\n=== Sending Receipt ===\n")

        # Generate receipt
        receipt_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Generate signature
        signature = self.generate_signature(
            receipt_id, publisher_domain, article_url, timestamp
        )

        # Build receipt payload
        receipt_data = {
            'receipt_id': receipt_id,
            'publisher_domain': publisher_domain,
            'article_url': article_url,
            'timestamp': timestamp,
            'signature': signature,
            'metadata': metadata or {
                'client_id': self.client_id,
                'client_version': CLIENT_VERSION
            }
        }

        print(f"Receipt ID: {receipt_id}")
        print(f"Publisher: {publisher_domain}")
        print(f"Article: {article_url}")
        print(f"Timestamp: {timestamp}")

        try:
            response = self.session.post(
                f"{self.base_url}/v1/receipts/ingest",
                json=receipt_data
            )

            if response.status_code == 201:
                result = response.json()
                print(f"\n✓ Receipt sent successfully!")
                print(f"  Status: {result.get('status')}")
                print(f"  Verified: {result.get('verified')}")
                print(f"  Message: {result.get('message')}")

                if result.get('merkle_root'):
                    print(f"  Merkle Root: {result.get('merkle_root')}")

                return result
            else:
                print(f"\n✗ Receipt submission failed: {response.status_code}")
                print(f"  Error: {response.json()}")
                return None

        except Exception as e:
            print(f"\n✗ Receipt submission error: {e}")
            return None

    def verify_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify a submitted receipt

        Args:
            receipt_id: Receipt ID to verify

        Returns:
            Receipt details or None if not found
        """
        print(f"\n=== Verifying Receipt ===")
        print(f"Receipt ID: {receipt_id}\n")

        try:
            response = self.session.get(
                f"{self.base_url}/v1/receipts",
                params={'limit': 100}
            )

            if response.status_code == 200:
                data = response.json()
                receipts = data.get('receipts', [])

                # Find the receipt
                receipt = next(
                    (r for r in receipts if r['receipt_id'] == receipt_id),
                    None
                )

                if receipt:
                    print(f"✓ Receipt found!")
                    print(f"  Status: {receipt.get('status')}")
                    print(f"  Verified: {receipt.get('verified')}")
                    print(f"  Created: {receipt.get('created_at')}")
                    return receipt
                else:
                    print(f"✗ Receipt not found")
                    return None
            else:
                print(f"✗ Receipt verification failed: {response.status_code}")
                return None

        except Exception as e:
            print(f"✗ Receipt verification error: {e}")
            return None

    def get_verified_publishers(self) -> List[Dict[str, Any]]:
        """
        Get list of verified publishers

        Returns:
            List of verified publisher domains
        """
        print(f"\n=== Fetching Verified Publishers ===\n")

        try:
            response = self.session.get(
                f"{self.base_url}/v1/publishers/verified-domains"
            )

            if response.status_code == 200:
                data = response.json()
                publishers = data.get('domains', [])

                print(f"✓ Found {len(publishers)} verified publishers")

                for pub in publishers[:5]:  # Show first 5
                    print(f"\n  {pub['domain']}")
                    print(f"    Verified: {pub['verified_at']}")
                    print(f"    Receipts: {pub['receipt_count']}")

                if len(publishers) > 5:
                    print(f"\n  ... and {len(publishers) - 5} more")

                return publishers
            else:
                print(f"✗ Failed to fetch publishers: {response.status_code}")
                return []

        except Exception as e:
            print(f"✗ Error fetching publishers: {e}")
            return []


def demo_workflow():
    """
    Demonstrate complete AI client workflow
    """
    print('╔════════════════════════════════════════════╗')
    print('║  IAIndex AI Client Example                ║')
    print('╚════════════════════════════════════════════╝')

    # Initialize client
    client = IAIndexClient()

    # Step 1: Get verified publishers
    publishers = client.get_verified_publishers()

    if not publishers:
        print("\n⚠ No verified publishers found. The example will use a demo domain.")
        demo_domain = "example.com"
    else:
        demo_domain = publishers[0]['domain']

    # Step 2: Fetch AI-Index (this would normally succeed for verified publishers)
    print(f"\n⚠ Note: Fetching AI-Index from {demo_domain}")
    print("In production, ensure the domain has deployed their ai-index.json file")
    ai_index = client.fetch_ai_index(demo_domain)

    # Step 3: Access content
    demo_article = f"https://{demo_domain}/article-1"
    print(f"\n⚠ Note: Accessing demo article URL")
    content = client.access_content(demo_article)

    # Step 4: Send receipt
    if content:
        receipt_result = client.send_receipt(
            publisher_domain=demo_domain,
            article_url=demo_article,
            metadata={
                'client_id': CLIENT_ID,
                'client_version': CLIENT_VERSION,
                'content_type': 'article',
                'access_type': 'read'
            }
        )

        # Step 5: Verify receipt
        if receipt_result and receipt_result.get('receipt_id'):
            import time
            print("\nWaiting 2 seconds before verification...")
            time.sleep(2)
            client.verify_receipt(receipt_result['receipt_id'])

    print('\n╔════════════════════════════════════════════╗')
    print('║  Demo Complete!                            ║')
    print('╚════════════════════════════════════════════╝\n')

    print('Best Practices for AI Clients:')
    print('1. Always check for ai-index.json before accessing content')
    print('2. Send receipts immediately after content access')
    print('3. Include meaningful metadata (client ID, version, etc.)')
    print('4. Handle receipt failures gracefully')
    print('5. Respect rate limits and publisher preferences\n')


if __name__ == '__main__':
    demo_workflow()
