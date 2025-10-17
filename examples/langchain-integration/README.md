# IAIndex + LangChain Integration

Custom LangChain document loader that automatically sends cryptographic receipts to IAIndex when loading content from verified publishers.

## Features

- Seamless integration with LangChain
- Automatic receipt generation and submission
- AI-Index file detection and caching
- Custom metadata extraction
- Support for all LangChain components (splitters, embeddings, chains)
- Optional receipt tracking (can be disabled)

## Prerequisites

- Python 3.8+
- LangChain
- IAIndex API key (optional but recommended)

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

```bash
cp .env.example .env
```

Edit `.env`:
```env
API_BASE_URL=https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
API_KEY=your-api-key-here
CLIENT_ID=langchain-iaindex
SECRET_KEY=demo-secret
OPENAI_API_KEY=your-openai-key  # Optional for RAG examples
```

## Quick Start

### Basic Usage

```python
from iaindex_loader import load_with_iaindex

# Load a single document
docs = load_with_iaindex("https://example.com/article")

# Receipt automatically sent if publisher is verified
print(f"Loaded: {docs[0].metadata['source']}")
print(f"IAIndex Verified: {docs[0].metadata['iaindex_verified']}")
```

### Multiple Documents

```python
from iaindex_loader import IAIndexLoader

loader = IAIndexLoader(
    urls=[
        "https://example.com/article-1",
        "https://example.com/article-2",
        "https://example.com/article-3"
    ],
    client_id="my-rag-app"
)

docs = loader.load()
# Receipts sent for each URL from verified publishers
```

## Advanced Usage

### With Vector Stores

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from iaindex_loader import IAIndexLoader

# Load documents with IAIndex tracking
loader = IAIndexLoader(
    urls=your_urls,
    client_id="my-app"
)
docs = loader.load()

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(docs, embeddings)

# Use for retrieval
retriever = vectorstore.as_retriever()
```

### With RAG Pipeline

```python
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from iaindex_loader import IAIndexLoader

# Load and index documents
loader = IAIndexLoader(urls=your_urls, client_id="rag-app")
docs = loader.load()

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(docs, embeddings)

# Create QA chain
qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

# Query
result = qa({"query": "Your question here"})
```

### With Text Splitters

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from iaindex_loader import IAIndexLoader

# Load documents
loader = IAIndexLoader(urls=your_urls)
docs = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits = text_splitter.split_documents(docs)

# Receipt is sent once per original document, not per chunk
```

### Custom Metadata Extraction

```python
from iaindex_loader import IAIndexLoader

def extract_metadata(soup, response):
    """Extract custom metadata from page"""
    return {
        'og_title': soup.find('meta', property='og:title')['content'],
        'word_count': len(soup.get_text().split()),
        'response_time': response.elapsed.total_seconds()
    }

loader = IAIndexLoader(
    urls=your_urls,
    metadata_extractor=extract_metadata
)
docs = loader.load()
```

### Disable Receipt Tracking

```python
from iaindex_loader import IAIndexLoader

# Load without sending receipts (e.g., for testing)
loader = IAIndexLoader(
    urls=your_urls,
    send_receipts=False
)
docs = loader.load()
```

## Document Metadata

Each loaded document includes rich metadata:

```python
{
    'source': 'https://example.com/article',
    'domain': 'example.com',
    'title': 'Article Title',
    'loaded_at': '2025-01-15T10:30:00.000Z',
    'client_id': 'my-app',
    'iaindex_verified': True,
    'publisher': 'Example Publisher',
    'iaindex_title': 'Title from AI-Index',
    'iaindex_description': 'Description from AI-Index',
    'iaindex_author': 'Author Name',
    'iaindex_published': '2025-01-15',
    'iaindex_tags': ['ai', 'ml', 'nlp']
}
```

## API Reference

### IAIndexLoader

Main loader class for loading documents with IAIndex tracking.

**Parameters:**
- `urls` (List[str]): URLs to load
- `client_id` (str): Unique client identifier
- `api_key` (str): IAIndex API key
- `api_base_url` (str): IAIndex API base URL
- `secret_key` (str): Secret for signing receipts
- `send_receipts` (bool): Whether to send receipts (default: True)
- `metadata_extractor` (callable): Optional custom metadata extractor

**Methods:**
- `load()`: Load all documents and return list of Document objects

### IAIndexWebLoader

Convenience class for loading a single URL.

```python
from iaindex_loader import IAIndexWebLoader

loader = IAIndexWebLoader(
    url="https://example.com/article",
    client_id="my-app"
)
docs = loader.load()
```

### load_with_iaindex()

Convenience function for quick loading.

```python
from iaindex_loader import load_with_iaindex

docs = load_with_iaindex(
    url="https://example.com/article",
    client_id="my-app"
)
```

## Examples

Run the included examples:

```bash
# Run all examples
python example.py

# Or run individual examples by uncommenting them in the file
```

Examples include:
1. Basic document loading
2. Multi-document loading
3. Custom metadata extraction
4. RAG pipeline integration
5. Loading without receipts
6. Text splitting integration

## How It Works

### 1. AI-Index Detection

When loading a URL, the loader:
1. Extracts the domain from the URL
2. Attempts to fetch `https://domain.com/ai-index.json`
3. Caches the result to avoid repeated requests

### 2. Content Loading

The loader:
1. Fetches the page content
2. Parses HTML with BeautifulSoup
3. Extracts text content
4. Removes navigation, scripts, and style elements

### 3. Metadata Extraction

Combines:
- Standard metadata (URL, domain, title)
- AI-Index metadata (if available)
- Custom metadata (if extractor provided)

### 4. Receipt Generation

For verified publishers:
1. Generates unique receipt ID (UUID)
2. Creates HMAC-SHA256 signature
3. Sends receipt to IAIndex API
4. Logs result (success/failure)

### 5. Document Return

Returns LangChain Document object with:
- Cleaned text content
- Rich metadata
- Source attribution

## Best Practices

### 1. Set Client ID

Always identify your application:

```python
loader = IAIndexLoader(
    urls=urls,
    client_id="my-company-rag-system-v2"
)
```

### 2. Handle Errors Gracefully

Receipt failures shouldn't break your pipeline:

```python
# Loader handles errors internally and logs them
# Your code continues even if receipts fail
docs = loader.load()
```

### 3. Cache AI-Index Files

The loader automatically caches AI-Index files per domain to avoid repeated requests.

### 4. Respect Rate Limits

For bulk loading, add delays:

```python
import time

for url in large_url_list:
    docs = load_with_iaindex(url)
    time.sleep(0.1)  # 10 requests/second
```

### 5. Use Metadata Effectively

Filter documents by verification status:

```python
verified_docs = [
    doc for doc in docs
    if doc.metadata.get('iaindex_verified')
]
```

## Integration Patterns

### Pattern 1: RAG with Attribution

```python
def rag_with_attribution(query: str, sources: List[str]):
    # Load with tracking
    loader = IAIndexLoader(urls=sources)
    docs = loader.load()

    # Create QA chain
    qa = create_qa_chain(docs)
    result = qa(query)

    # Include attribution
    verified_sources = [
        doc.metadata['source']
        for doc in result['source_documents']
        if doc.metadata.get('iaindex_verified')
    ]

    return {
        'answer': result['result'],
        'verified_sources': verified_sources
    }
```

### Pattern 2: Incremental Indexing

```python
def index_new_articles(new_urls: List[str]):
    loader = IAIndexLoader(urls=new_urls)
    docs = loader.load()

    # Add to existing vector store
    vectorstore.add_documents(docs)

    # Receipts automatically sent
    return len(docs)
```

### Pattern 3: Multi-Source RAG

```python
def multi_source_rag(query: str):
    sources = get_relevant_sources(query)

    # Load from multiple publishers
    loader = IAIndexLoader(urls=sources)
    docs = loader.load()

    # Group by verification status
    verified = [d for d in docs if d.metadata['iaindex_verified']]
    unverified = [d for d in docs if not d.metadata['iaindex_verified']]

    # Prioritize verified sources
    return create_answer(query, verified + unverified)
```

## Troubleshooting

### Receipts Not Being Sent

**Check:**
1. Is publisher domain verified? Use API to check
2. Is `send_receipts=True`? (default)
3. Is API key valid?
4. Check logs for error messages

### AI-Index Not Found

**Check:**
1. Does publisher have `ai-index.json` at domain root?
2. Is it accessible via HTTPS?
3. Is JSON valid?

### Metadata Missing

**Check:**
1. Is HTML well-formed?
2. Are expected tags present?
3. Use custom metadata extractor for special cases

## Performance Optimization

### Parallel Loading

```python
from concurrent.futures import ThreadPoolExecutor

def load_parallel(urls: List[str], max_workers: int = 10):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(load_with_iaindex, url)
            for url in urls
        ]
        results = [f.result() for f in futures]

    return [doc for docs in results for doc in docs]
```

### Caching

AI-Index files are automatically cached per domain during the loader's lifetime. For longer-term caching:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_ai_index(domain: str):
    # Implement caching logic
    pass
```

## Resources

- [LangChain Documentation](https://python.langchain.com)
- [IAIndex Documentation](https://docs.iaindex.org)
- [IAIndex API Reference](https://docs.iaindex.org/api)

## Support

- GitHub: [github.com/iaindex/iaindex](https://github.com/iaindex/iaindex)
- Discord: [discord.gg/iaindex](https://discord.gg/iaindex)

## License

MIT
