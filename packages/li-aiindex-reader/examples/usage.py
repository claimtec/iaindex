"""
Example usage of LlamaIndex AIIndex Loader
"""

from aiindex_llama import AIIndexReader, AIIndexReceiptSigner, AIIndexLoader, Purpose, Attribution


def basic_reading():
    """Example 1: Basic document reading"""
    print("=== Basic Reading ===\n")

    reader = AIIndexReader(timeout=10, validate_schema=True)

    try:
        # Fetch ai-index.json from a domain
        document = reader.fetch("example.com")

        print(f"Publisher: {document.publisher.name if document.publisher else 'N/A'}")
        print(f"Domain: {document.domain}")
        print(f"Pages: {len(document.pages) if document.pages else 0}")
        print(f"Entities: {len(document.entities) if document.entities else 0}")
        print(f"FAQs: {len(document.faq) if document.faq else 0}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        reader.close()


def batch_reading():
    """Example 2: Batch reading multiple sites"""
    print("\n=== Batch Reading ===\n")

    reader = AIIndexReader()

    urls = [
        "https://example.com/ai-index.json",
        "https://another-site.com/ai-index.json",
        "https://third-site.com/ai-index.json",
    ]

    results = reader.fetch_batch(urls)

    for result in results:
        if "document" in result:
            doc = result["document"]
            print(f"✓ {result['url']}: {doc.publisher.name if doc.publisher else 'N/A'}")
        else:
            print(f"✗ {result['url']}: {result['error']}")

    reader.close()


def receipt_signing():
    """Example 3: Create and sign receipts"""
    print("\n=== Receipt Signing ===\n")

    # Generate a keypair (do this once and store securely)
    private_key, public_key = AIIndexReceiptSigner.generate_keypair("ES256")
    print("Generated keypair")
    print(f"Public key: {public_key[:50].decode()}...")

    # Create signer
    signer = AIIndexReceiptSigner(
        client_id="my-llamaindex-app",
        client_name="My LlamaIndex Application",
        client_version="1.0.0",
        private_key_pem=private_key,
        key_id="key-001",
        algorithm="ES256",
    )

    # Fetch document
    reader = AIIndexReader()
    document = reader.fetch("example.com")

    # Create and post receipt
    receipt, posted = signer.create_and_post_receipt(
        document=document,
        url="https://example.com/ai-index.json",
        status_code=200,
        pages_accessed=["https://example.com/about", "https://example.com/contact"],
        purpose=Purpose(
            type="inference",
            description="RAG application for customer support",
            commercial=True,
        ),
        attribution=Attribution(
            method="citation",
            citation_text="Information from Example.com",
            url="https://example.com",
        ),
    )

    print(f"Receipt ID: {receipt.receipt_id}")
    print(f"Posted to webhook: {posted}")

    # Verify receipt
    is_valid = AIIndexReceiptSigner.verify_receipt(receipt, public_key)
    print(f"Receipt valid: {is_valid}")

    reader.close()
    signer.close()


def llamaindex_loader():
    """Example 4: LlamaIndex document loader"""
    print("\n=== LlamaIndex Document Loader ===\n")

    # Basic loading
    loader = AIIndexLoader(
        url="example.com",
        validate_schema=True,
        include_metadata=True,
        filter_content_type=["article", "documentation"],
        max_pages=10,
    )

    documents = loader.load_data()

    print(f"Loaded {len(documents)} documents")

    for i, doc in enumerate(documents):
        print(f"\nDocument {i + 1}:")
        print(f"Type: {doc.metadata.get('type', 'N/A')}")
        print(f"Content preview: {doc.text[:100]}...")


def llamaindex_loader_with_receipts():
    """Example 5: LlamaIndex loader with receipts"""
    print("\n=== LlamaIndex Loader with Receipts ===\n")

    # Generate keypair
    private_key, public_key = AIIndexReceiptSigner.generate_keypair("ES256")

    loader = AIIndexLoader(
        url="example.com",
        validate_schema=True,
        auto_send_receipt=True,
        client_id="my-rag-app",
        client_name="My RAG Application",
        client_version="1.0.0",
        private_key_pem=private_key,
        key_id="key-001",
        algorithm="ES256",
        include_metadata=True,
    )

    # This will automatically create and send a receipt
    documents = loader.load_data()

    print(f"Loaded {len(documents)} documents with automatic receipt")


def load_by_type():
    """Example 6: Load by document type"""
    print("\n=== Load By Type ===\n")

    loader = AIIndexLoader(url="example.com")

    result = loader.load_by_type()

    print(f"Publisher document: {'✓' if result['publisher'] else '✗'}")
    print(f"Entity documents: {len(result['entities'])}")
    print(f"Page documents: {len(result['pages'])}")
    print(f"FAQ documents: {len(result['faqs'])}")

    # Use specific document types
    if result["faqs"]:
        print("\nFirst FAQ:")
        print(result["faqs"][0].text)


def batch_loading():
    """Example 7: Batch loading multiple sites"""
    print("\n=== Batch Loading ===\n")

    urls = [
        "https://example.com/ai-index.json",
        "https://another-site.com/ai-index.json",
    ]

    documents = AIIndexLoader.load_batch(
        urls=urls,
        validate_schema=True,
        include_metadata=True,
        max_pages=5,
    )

    print(f"Loaded {len(documents)} documents from {len(urls)} sites")

    # Group by source
    by_site = {}
    for doc in documents:
        source = doc.metadata.get("ai_index_source", doc.metadata.get("source"))
        if source not in by_site:
            by_site[source] = []
        by_site[source].append(doc)

    for site, docs in by_site.items():
        print(f"{site}: {len(docs)} documents")


def llamaindex_integration():
    """Example 8: Integration with LlamaIndex components"""
    print("\n=== LlamaIndex Integration ===\n")

    # Load documents
    loader = AIIndexLoader(
        url="example.com",
        include_metadata=True,
        filter_content_type=["article", "documentation"],
    )

    documents = loader.load_data()

    print(f"Loaded {len(documents)} documents")

    # These documents can now be used with:
    # - Vector stores (e.g., Chroma, Pinecone, Weaviate)
    # - Indexes (VectorStoreIndex, SummaryIndex, etc.)
    # - Query engines
    # - Chat engines
    # - Agents

    print("\nReady for use with:")
    print("- Vector stores (Chroma, Pinecone, Weaviate, etc.)")
    print("- Indexes (VectorStoreIndex, SummaryIndex)")
    print("- Query engines")
    print("- Chat engines")
    print("- Agents")

    # Example: Create a vector store index
    # from llama_index.core import VectorStoreIndex
    # index = VectorStoreIndex.from_documents(documents)
    # query_engine = index.as_query_engine()
    # response = query_engine.query("What is this about?")


def context_manager_usage():
    """Example 9: Using context managers"""
    print("\n=== Context Manager Usage ===\n")

    # Reader with context manager
    with AIIndexReader() as reader:
        document = reader.fetch("example.com")
        print(f"Fetched document from {document.domain}")

    # Signer with context manager
    private_key, public_key = AIIndexReceiptSigner.generate_keypair("ES256")

    with AIIndexReceiptSigner(
        client_id="my-app",
        private_key_pem=private_key,
        key_id="key-001",
    ) as signer:
        with AIIndexReader() as reader:
            document = reader.fetch("example.com")
            receipt, posted = signer.create_and_post_receipt(
                document=document,
                url="https://example.com/ai-index.json",
            )
            print(f"Receipt ID: {receipt.receipt_id}")


def main():
    """Run all examples"""
    print("AIIndex LlamaIndex Loader Examples")
    print("===================================\n")

    # Uncomment to run specific examples:

    # basic_reading()
    # batch_reading()
    # receipt_signing()
    # llamaindex_loader()
    # llamaindex_loader_with_receipts()
    # load_by_type()
    # batch_loading()
    # llamaindex_integration()
    # context_manager_usage()

    print("\nNote: Uncomment examples in main() to run them.")


if __name__ == "__main__":
    main()
