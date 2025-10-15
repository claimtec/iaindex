"""
AIIndexLoader - LlamaIndex data loader for AIIndex
"""

from typing import List, Optional, Dict, Any

from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document

from .reader import AIIndexReader
from .signer import AIIndexReceiptSigner
from .types import AIIndexDocument, Page, Entity, FAQ, Purpose, Attribution


class AIIndexLoader(BaseReader):
    """
    LlamaIndex data loader for AIIndex documents.

    Loads ai-index.json files and converts them to LlamaIndex Document format.
    Supports automatic receipt generation and posting to webhooks.

    Example:
        >>> loader = AIIndexLoader(
        ...     url="example.com",
        ...     include_metadata=True,
        ...     auto_send_receipt=True,
        ...     client_id="my-app",
        ...     private_key_pem=private_key,
        ...     key_id="key-001"
        ... )
        >>> documents = loader.load_data()
    """

    def __init__(
        self,
        url: str,
        timeout: int = 10,
        validate_schema: bool = True,
        include_metadata: bool = True,
        filter_content_type: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
        auto_send_receipt: bool = False,
        client_id: Optional[str] = None,
        client_name: Optional[str] = None,
        client_version: Optional[str] = None,
        private_key_pem: Optional[bytes] = None,
        key_id: Optional[str] = None,
        algorithm: str = "ES256",
    ):
        """
        Initialize AIIndexLoader.

        Args:
            url: URL or domain of ai-index.json
            timeout: Request timeout in seconds
            validate_schema: Enable schema validation
            include_metadata: Include metadata in documents
            filter_content_type: Filter pages by content type
            max_pages: Maximum number of pages to load
            auto_send_receipt: Automatically send receipts
            client_id: Client identifier (required if auto_send_receipt=True)
            client_name: Client display name
            client_version: Client version
            private_key_pem: Private key for signing receipts
            key_id: Key identifier
            algorithm: Signature algorithm
        """
        super().__init__()
        self.url = url
        self.include_metadata = include_metadata
        self.filter_content_type = filter_content_type
        self.max_pages = max_pages
        self.auto_send_receipt = auto_send_receipt

        # Initialize reader
        self.reader = AIIndexReader(
            timeout=timeout,
            validate_schema=validate_schema,
        )

        # Initialize signer if needed
        self.signer = None
        if auto_send_receipt and private_key_pem and key_id and client_id:
            self.signer = AIIndexReceiptSigner(
                client_id=client_id,
                client_name=client_name or "LlamaIndex AIIndex Client",
                client_version=client_version or "1.0.0",
                private_key_pem=private_key_pem,
                key_id=key_id,
                algorithm=algorithm,
            )

    def load_data(self) -> List[Document]:
        """
        Load documents from ai-index.json.

        Returns:
            List of LlamaIndex Document objects
        """
        # Fetch the ai-index.json document
        aiindex_doc = self.reader.fetch(self.url)

        # Create receipt if signer is available
        if self.signer and self.auto_send_receipt:
            self._create_and_send_receipt(aiindex_doc)

        # Convert to LlamaIndex documents
        documents = self._convert_to_documents(aiindex_doc)

        return documents

    def _convert_to_documents(self, aiindex_doc: AIIndexDocument) -> List[Document]:
        """Convert AIIndex document to LlamaIndex Document format."""
        documents = []

        # Add publisher information as a document
        if aiindex_doc.publisher:
            publisher_content = self._format_publisher(aiindex_doc)
            documents.append(
                Document(
                    text=publisher_content,
                    metadata=self._build_metadata(aiindex_doc, "publisher") if self.include_metadata else {},
                )
            )

        # Add entities as documents
        if aiindex_doc.entities:
            for entity in aiindex_doc.entities:
                entity_content = self._format_entity(entity)
                documents.append(
                    Document(
                        text=entity_content,
                        metadata=self._build_entity_metadata(entity, aiindex_doc) if self.include_metadata else {},
                    )
                )

        # Add pages as documents
        if aiindex_doc.pages:
            pages = aiindex_doc.pages

            # Filter by content type if specified
            if self.filter_content_type:
                pages = [
                    page for page in pages
                    if page.content_type and page.content_type.value in self.filter_content_type
                ]

            # Limit number of pages if specified
            if self.max_pages and self.max_pages > 0:
                pages = pages[:self.max_pages]

            for page in pages:
                page_content = self._format_page(page)
                documents.append(
                    Document(
                        text=page_content,
                        metadata=self._build_page_metadata(page, aiindex_doc) if self.include_metadata else {},
                    )
                )

        # Add FAQs as documents
        if aiindex_doc.faq:
            for faq_item in aiindex_doc.faq:
                faq_content = self._format_faq(faq_item)
                documents.append(
                    Document(
                        text=faq_content,
                        metadata=self._build_faq_metadata(faq_item, aiindex_doc) if self.include_metadata else {},
                    )
                )

        return documents

    def _format_publisher(self, aiindex_doc: AIIndexDocument) -> str:
        """Format publisher information as text."""
        pub = aiindex_doc.publisher
        if not pub:
            return ""

        content = f"# {pub.name or aiindex_doc.domain}\n\n"

        if pub.description:
            content += f"{pub.description}\n\n"

        if pub.url:
            content += f"Website: {pub.url}\n"

        if pub.contact and pub.contact.email:
            content += f"Contact: {pub.contact.email}\n"

        return content.strip()

    def _format_entity(self, entity: Entity) -> str:
        """Format entity information as text."""
        content = f"# {entity.name}\n\n"
        content += f"Type: {entity.type.value}\n\n"

        if entity.description:
            content += f"{entity.description}\n\n"

        if entity.url:
            content += f"URL: {entity.url}\n"

        if entity.properties:
            content += "\nAdditional Information:\n"
            for key, value in entity.properties.items():
                content += f"- {key}: {value}\n"

        return content.strip()

    def _format_page(self, page: Page) -> str:
        """Format page information as text."""
        content = f"# {page.title}\n\n"

        if page.description:
            content += f"{page.description}\n\n"

        if page.summary:
            content += f"{page.summary}\n\n"

        content += f"URL: {page.url}\n"

        if page.author:
            content += f"Author: {page.author}\n"

        if page.published:
            content += f"Published: {page.published}\n"

        if page.tags:
            content += f"Tags: {', '.join(page.tags)}\n"

        return content.strip()

    def _format_faq(self, faq: FAQ) -> str:
        """Format FAQ item as text."""
        content = f"Q: {faq.question}\n\n"
        content += f"A: {faq.answer}"

        if faq.category:
            content += f"\n\nCategory: {faq.category}"

        return content.strip()

    def _build_metadata(self, aiindex_doc: AIIndexDocument, doc_type: str) -> Dict[str, Any]:
        """Build metadata for publisher document."""
        return {
            "source": self.url,
            "type": doc_type,
            "publisher_id": aiindex_doc.publisher_id,
            "domain": aiindex_doc.domain,
            "last_updated": aiindex_doc.last_updated.isoformat(),
        }

    def _build_entity_metadata(self, entity: Entity, aiindex_doc: AIIndexDocument) -> Dict[str, Any]:
        """Build metadata for entity document."""
        return {
            "source": self.url,
            "type": "entity",
            "entity_type": entity.type.value,
            "entity_name": entity.name,
            "entity_url": str(entity.url) if entity.url else None,
            "ai_index_source": self.url,
        }

    def _build_page_metadata(self, page: Page, aiindex_doc: AIIndexDocument) -> Dict[str, Any]:
        """Build metadata for page document."""
        return {
            "source": str(page.url),
            "type": "page",
            "title": page.title,
            "content_type": page.content_type.value if page.content_type else None,
            "author": page.author,
            "published": page.published.isoformat() if page.published else None,
            "modified": page.modified.isoformat() if page.modified else None,
            "tags": page.tags,
            "ai_index_source": self.url,
        }

    def _build_faq_metadata(self, faq: FAQ, aiindex_doc: AIIndexDocument) -> Dict[str, Any]:
        """Build metadata for FAQ document."""
        return {
            "source": self.url,
            "type": "faq",
            "category": faq.category,
            "ai_index_source": self.url,
        }

    def _create_and_send_receipt(self, aiindex_doc: AIIndexDocument) -> None:
        """Create and send receipt to publisher."""
        if not self.signer:
            return

        try:
            self.signer.create_and_post_receipt(
                document=aiindex_doc,
                url=self.url,
                status_code=200,
                purpose=Purpose(
                    type="inference",
                    description="Document loading for LlamaIndex application",
                    commercial=False,
                ),
                attribution=Attribution(
                    method="citation",
                    citation_text=f"Data from {aiindex_doc.domain}",
                ),
            )
        except Exception as e:
            print(f"Failed to send receipt: {e}")
            # Don't fail the entire load operation if receipt fails

    def load_by_type(self) -> Dict[str, Any]:
        """
        Load and organize documents by type.

        Returns:
            Dictionary with keys: 'publisher', 'entities', 'pages', 'faqs'
        """
        all_docs = self.load_data()

        return {
            "publisher": next((doc for doc in all_docs if doc.metadata.get("type") == "publisher"), None),
            "entities": [doc for doc in all_docs if doc.metadata.get("type") == "entity"],
            "pages": [doc for doc in all_docs if doc.metadata.get("type") == "page"],
            "faqs": [doc for doc in all_docs if doc.metadata.get("type") == "faq"],
        }

    @staticmethod
    def load_batch(
        urls: List[str],
        timeout: int = 10,
        validate_schema: bool = True,
        include_metadata: bool = True,
        filter_content_type: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
    ) -> List[Document]:
        """
        Load multiple ai-index.json files in batch.

        Args:
            urls: List of URLs or domains
            timeout: Request timeout
            validate_schema: Enable schema validation
            include_metadata: Include metadata in documents
            filter_content_type: Filter pages by content type
            max_pages: Max pages per site

        Returns:
            List of all loaded documents
        """
        documents = []

        for url in urls:
            try:
                loader = AIIndexLoader(
                    url=url,
                    timeout=timeout,
                    validate_schema=validate_schema,
                    include_metadata=include_metadata,
                    filter_content_type=filter_content_type,
                    max_pages=max_pages,
                )
                docs = loader.load_data()
                documents.extend(docs)
            except Exception as e:
                print(f"Failed to load {url}: {e}")

        return documents
