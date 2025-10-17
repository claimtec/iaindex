"""
IAIndex Document Loader for LangChain

Custom document loader that automatically sends receipts to IAIndex
when loading documents from verified publishers.
"""

import os
import uuid
import hmac
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import requests
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from bs4 import BeautifulSoup


class IAIndexLoader(BaseLoader):
    """
    LangChain document loader with IAIndex receipt tracking

    Automatically sends cryptographic receipts when loading content
    from IAIndex-verified publishers.

    Example:
        >>> loader = IAIndexLoader(
        ...     urls=["https://example.com/article"],
        ...     client_id="my-rag-app",
        ...     api_key="your-api-key"
        ... )
        >>> documents = loader.load()
        >>> # Receipts automatically sent for verified publishers
    """

    def __init__(
        self,
        urls: List[str] = None,
        client_id: str = None,
        api_key: str = None,
        api_base_url: str = None,
        secret_key: str = None,
        send_receipts: bool = True,
        metadata_extractor: Optional[callable] = None
    ):
        """
        Initialize IAIndex loader

        Args:
            urls: List of URLs to load
            client_id: Unique client identifier
            api_key: IAIndex API key
            api_base_url: IAIndex API base URL
            secret_key: Secret for signing receipts
            send_receipts: Whether to send receipts (default: True)
            metadata_extractor: Optional function to extract custom metadata
        """
        self.urls = urls or []
        self.client_id = client_id or os.getenv('CLIENT_ID', 'langchain-iaindex')
        self.api_key = api_key or os.getenv('API_KEY', '')
        self.api_base_url = api_base_url or os.getenv(
            'API_BASE_URL',
            'https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io'
        )
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'demo-secret')
        self.send_receipts = send_receipts
        self.metadata_extractor = metadata_extractor

        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            })

        # Cache for AI-Index files
        self._ai_index_cache: Dict[str, Optional[Dict]] = {}

    def load(self) -> List[Document]:
        """
        Load documents and send receipts

        Returns:
            List of LangChain Document objects
        """
        documents = []

        for url in self.urls:
            try:
                doc = self._load_single_url(url)
                if doc:
                    documents.append(doc)
            except Exception as e:
                print(f"Error loading {url}: {e}")

        return documents

    def _load_single_url(self, url: str) -> Optional[Document]:
        """
        Load a single URL and send receipt

        Args:
            url: URL to load

        Returns:
            LangChain Document or None
        """
        # Parse domain
        parsed = urlparse(url)
        domain = parsed.netloc

        # Check for AI-Index
        ai_index = self._get_ai_index(domain)

        # Fetch content
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text content
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()

        text = soup.get_text(separator='\n', strip=True)

        # Extract metadata
        metadata = {
            'source': url,
            'domain': domain,
            'title': soup.title.string if soup.title else None,
            'loaded_at': datetime.utcnow().isoformat(),
            'client_id': self.client_id
        }

        # Add AI-Index metadata if available
        if ai_index:
            metadata['iaindex_verified'] = True
            metadata['publisher'] = ai_index.get('publisher', {}).get('name')

            # Try to find page metadata in AI-Index
            page_info = self._find_page_in_index(url, ai_index)
            if page_info:
                metadata.update({
                    'iaindex_title': page_info.get('title'),
                    'iaindex_description': page_info.get('description'),
                    'iaindex_author': page_info.get('author'),
                    'iaindex_published': page_info.get('published_date'),
                    'iaindex_tags': page_info.get('tags')
                })
        else:
            metadata['iaindex_verified'] = False

        # Custom metadata extraction
        if self.metadata_extractor:
            custom_metadata = self.metadata_extractor(soup, response)
            metadata.update(custom_metadata)

        # Create document
        document = Document(
            page_content=text,
            metadata=metadata
        )

        # Send receipt if enabled and publisher is verified
        if self.send_receipts and ai_index:
            self._send_receipt(domain, url, metadata)

        return document

    def _get_ai_index(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get AI-Index file for domain (with caching)

        Args:
            domain: Publisher domain

        Returns:
            AI-Index data or None
        """
        # Check cache
        if domain in self._ai_index_cache:
            return self._ai_index_cache[domain]

        # Fetch AI-Index
        for protocol in ['https', 'http']:
            url = f"{protocol}://{domain}/ai-index.json"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    ai_index = response.json()
                    self._ai_index_cache[domain] = ai_index
                    return ai_index
            except Exception:
                continue

        # Cache miss
        self._ai_index_cache[domain] = None
        return None

    def _find_page_in_index(self, url: str, ai_index: Dict) -> Optional[Dict]:
        """
        Find page information in AI-Index

        Args:
            url: Page URL
            ai_index: AI-Index data

        Returns:
            Page metadata or None
        """
        pages = ai_index.get('pages', [])
        for page in pages:
            if page.get('url') == url:
                return page
        return None

    def _send_receipt(self, domain: str, url: str, metadata: Dict) -> bool:
        """
        Send receipt to IAIndex

        Args:
            domain: Publisher domain
            url: Article URL
            metadata: Document metadata

        Returns:
            True if successful
        """
        try:
            receipt_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            # Generate signature
            signature_data = f"{receipt_id}:{domain}:{url}:{timestamp}"
            signature = hmac.new(
                self.secret_key.encode(),
                signature_data.encode(),
                hashlib.sha256
            ).hexdigest()

            # Build receipt
            receipt = {
                'receipt_id': receipt_id,
                'publisher_domain': domain,
                'article_url': url,
                'timestamp': timestamp,
                'signature': signature,
                'metadata': {
                    'client_id': self.client_id,
                    'loader': 'langchain-iaindex',
                    'title': metadata.get('title')
                }
            }

            # Send to API
            response = self.session.post(
                f"{self.api_base_url}/v1/receipts/ingest",
                json=receipt
            )

            if response.status_code == 201:
                result = response.json()
                print(f"✓ Receipt sent for {url} - Status: {result.get('status')}")
                return True
            else:
                print(f"⚠ Receipt failed for {url}: {response.status_code}")
                return False

        except Exception as e:
            print(f"⚠ Receipt error for {url}: {e}")
            return False


class IAIndexWebLoader(IAIndexLoader):
    """
    Convenience class for loading web pages with IAIndex tracking

    Example:
        >>> from iaindex_loader import IAIndexWebLoader
        >>> loader = IAIndexWebLoader(
        ...     url="https://example.com/article",
        ...     client_id="my-app"
        ... )
        >>> docs = loader.load()
    """

    def __init__(self, url: str, **kwargs):
        """
        Initialize with a single URL

        Args:
            url: URL to load
            **kwargs: Additional arguments for IAIndexLoader
        """
        super().__init__(urls=[url], **kwargs)


def load_with_iaindex(url: str, **kwargs) -> List[Document]:
    """
    Convenience function to load a URL with IAIndex tracking

    Args:
        url: URL to load
        **kwargs: Additional arguments for IAIndexLoader

    Returns:
        List of documents

    Example:
        >>> from iaindex_loader import load_with_iaindex
        >>> docs = load_with_iaindex("https://example.com/article")
    """
    loader = IAIndexWebLoader(url, **kwargs)
    return loader.load()
