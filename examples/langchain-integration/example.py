"""
IAIndex + LangChain Integration Examples

Demonstrates how to use IAIndexLoader with LangChain for:
1. Basic document loading with receipt tracking
2. RAG pipelines with IAIndex
3. Multi-document loading
4. Custom metadata extraction
"""

import os
from dotenv import load_dotenv
from iaindex_loader import IAIndexLoader, load_with_iaindex

# Load environment
load_dotenv()

# Uncomment if using OpenAI for embeddings/chat
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.chains import RetrievalQA
# from langchain.llms import OpenAI


def example_basic_loading():
    """
    Example 1: Basic document loading with receipt tracking
    """
    print('\n' + '='*60)
    print('Example 1: Basic Document Loading')
    print('='*60 + '\n')

    # Single URL with convenience function
    docs = load_with_iaindex(
        url="https://example.com/article",
        client_id="example-app"
    )

    if docs:
        doc = docs[0]
        print(f"✓ Loaded document:")
        print(f"  Source: {doc.metadata['source']}")
        print(f"  Domain: {doc.metadata['domain']}")
        print(f"  IAIndex Verified: {doc.metadata.get('iaindex_verified', False)}")
        print(f"  Content length: {len(doc.page_content)} chars")
        print(f"\nContent preview:")
        print(doc.page_content[:200] + "...")


def example_multi_document():
    """
    Example 2: Load multiple documents with receipt tracking
    """
    print('\n' + '='*60)
    print('Example 2: Multi-Document Loading')
    print('='*60 + '\n')

    urls = [
        "https://example.com/article-1",
        "https://example.com/article-2",
        "https://example.com/article-3"
    ]

    loader = IAIndexLoader(
        urls=urls,
        client_id="multi-doc-example"
    )

    docs = loader.load()

    print(f"✓ Loaded {len(docs)} documents")
    for i, doc in enumerate(docs, 1):
        print(f"\n  Document {i}:")
        print(f"    URL: {doc.metadata['source']}")
        print(f"    Verified: {doc.metadata.get('iaindex_verified', False)}")
        if doc.metadata.get('iaindex_title'):
            print(f"    Title: {doc.metadata['iaindex_title']}")


def example_custom_metadata():
    """
    Example 3: Custom metadata extraction
    """
    print('\n' + '='*60)
    print('Example 3: Custom Metadata Extraction')
    print('='*60 + '\n')

    def extract_metadata(soup, response):
        """Extract custom metadata from page"""
        metadata = {}

        # Extract meta tags
        if soup.find('meta', property='og:title'):
            metadata['og_title'] = soup.find('meta', property='og:title')['content']

        if soup.find('meta', property='og:description'):
            metadata['og_description'] = soup.find('meta', property='og:description')['content']

        # Extract author from meta or article
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            metadata['author'] = author_meta.get('content')

        # Count links
        metadata['link_count'] = len(soup.find_all('a'))

        # Response headers
        metadata['content_type'] = response.headers.get('content-type')
        metadata['response_time_ms'] = response.elapsed.total_seconds() * 1000

        return metadata

    loader = IAIndexLoader(
        urls=["https://example.com/article"],
        client_id="custom-metadata-example",
        metadata_extractor=extract_metadata
    )

    docs = loader.load()

    if docs:
        doc = docs[0]
        print("✓ Loaded document with custom metadata:")
        print(f"  Source: {doc.metadata['source']}")
        print(f"  Custom metadata:")
        for key, value in doc.metadata.items():
            if key.startswith('og_') or key in ['author', 'link_count', 'response_time_ms']:
                print(f"    {key}: {value}")


def example_rag_pipeline():
    """
    Example 4: RAG pipeline with IAIndex (requires OpenAI API key)
    """
    print('\n' + '='*60)
    print('Example 4: RAG Pipeline with IAIndex')
    print('='*60 + '\n')

    if not os.getenv('OPENAI_API_KEY'):
        print("⚠ OpenAI API key not found. Skipping RAG example.")
        print("  Set OPENAI_API_KEY in .env to run this example.")
        return

    print("Note: This example requires OpenAI API key and is commented out by default.")
    print("Uncomment the imports and code below to run it.\n")

    # Uncomment to run:
    """
    # Load documents with IAIndex tracking
    urls = [
        "https://example.com/doc1",
        "https://example.com/doc2",
        "https://example.com/doc3"
    ]

    loader = IAIndexLoader(
        urls=urls,
        client_id="rag-example"
    )
    docs = loader.load()

    # Create embeddings
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Create QA chain
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0),
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )

    # Ask question
    query = "What are the main topics covered?"
    result = qa({"query": query})

    print(f"Question: {query}")
    print(f"Answer: {result['result']}")
    print(f"\nSources:")
    for doc in result['source_documents']:
        print(f"  - {doc.metadata['source']}")
        if doc.metadata.get('iaindex_verified'):
            print(f"    ✓ IAIndex verified")
    """


def example_disable_receipts():
    """
    Example 5: Load documents without sending receipts
    """
    print('\n' + '='*60)
    print('Example 5: Loading Without Receipts')
    print('='*60 + '\n')

    loader = IAIndexLoader(
        urls=["https://example.com/article"],
        client_id="no-receipts-example",
        send_receipts=False  # Disable receipt sending
    )

    docs = loader.load()

    print("✓ Documents loaded without sending receipts")
    print("  (Use for testing or when receipts are not needed)")


def example_with_langchain_splitter():
    """
    Example 6: Use with LangChain text splitters
    """
    print('\n' + '='*60)
    print('Example 6: Text Splitting with IAIndex')
    print('='*60 + '\n')

    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # Load documents
    loader = IAIndexLoader(
        urls=["https://example.com/long-article"],
        client_id="text-splitter-example"
    )
    docs = loader.load()

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)

    print(f"✓ Split {len(docs)} documents into {len(splits)} chunks")
    print(f"  Original document length: {len(docs[0].page_content)} chars")
    print(f"  Number of chunks: {len(splits)}")
    print(f"  Receipt sent: Once per original document")


def main():
    """Run all examples"""
    print('\n╔════════════════════════════════════════════════════════════╗')
    print('║  IAIndex + LangChain Integration Examples                 ║')
    print('╚════════════════════════════════════════════════════════════╝')

    examples = [
        ("Basic Loading", example_basic_loading),
        ("Multi-Document", example_multi_document),
        ("Custom Metadata", example_custom_metadata),
        ("RAG Pipeline", example_rag_pipeline),
        ("Disable Receipts", example_disable_receipts),
        ("Text Splitting", example_with_langchain_splitter)
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n✗ Error in {name} example: {e}")

    print('\n╔════════════════════════════════════════════════════════════╗')
    print('║  Examples Complete!                                        ║')
    print('╚════════════════════════════════════════════════════════════╝\n')

    print('Key Takeaways:')
    print('1. IAIndexLoader automatically sends receipts for verified publishers')
    print('2. Works seamlessly with existing LangChain workflows')
    print('3. Supports custom metadata extraction')
    print('4. Can be disabled for testing or special cases')
    print('5. Integrates with all LangChain components (splitters, embeddings, etc.)\n')


if __name__ == '__main__':
    main()
