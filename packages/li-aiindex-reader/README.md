# aiindex-llama

LlamaIndex data loader for AIIndex - Read and process AI-readable website metadata with automatic receipt generation and cryptographic verification.

## Features

- Fetch and parse `ai-index.json` files from websites
- Automatic Pydantic schema validation
- Convert to LlamaIndex Document format
- Receipt generation with ES256/RS256 signatures
- Auto-send receipts to publisher webhooks
- Batch document loading
- Async support
- Comprehensive metadata extraction
- Network error handling with retries
- Context manager support
- Full type hints

## Installation

```bash
pip install aiindex-llama llama-index-core
```

## Quick Start

### Basic Document Loading

```python
from aiindex_llama import AIIndexLoader

# Load documents from a website
loader = AIIndexLoader(
    url="example.com",
    validate_schema=True,
    include_metadata=True,
)

documents = loader.load_data()

print(f"Loaded {len(documents)} documents")
```

### With Automatic Receipts

```python
from aiindex_llama import AIIndexLoader, AIIndexReceiptSigner

# Generate keypair (do once, store securely)
private_key, public_key = AIIndexReceiptSigner.generate_keypair("ES256")

# Load with automatic receipt generation
loader = AIIndexLoader(
    url="example.com",
    auto_send_receipt=True,
    client_id="my-app",
    client_name="My RAG Application",
    private_key_pem=private_key,
    key_id="key-001",
    algorithm="ES256",
)

documents = loader.load_data()
```

## Core Classes

### AIIndexReader

Fetch and parse `ai-index.json` files with validation.

```python
from aiindex_llama import AIIndexReader

reader = AIIndexReader(timeout=10, validate_schema=True)

# Fetch single document
document = reader.fetch("example.com")

# Batch fetch
results = reader.fetch_batch([
    "https://site1.com/ai-index.json",
    "https://site2.com/ai-index.json",
])

# Probe for availability
exists = reader.probe("example.com")

# Extract specific data
page_urls = reader.extract_page_urls(document)
people = reader.extract_entities_by_type(document, "Person")
faqs = reader.get_faq_by_category(document, "pricing")

# Context manager support
with AIIndexReader() as reader:
    document = reader.fetch("example.com")
```

### AIIndexReceiptSigner

Create and sign cryptographic receipts for AI access tracking.

```python
from aiindex_llama import AIIndexReceiptSigner, Purpose, Attribution

# Generate keypair
private_key, public_key = AIIndexReceiptSigner.generate_keypair("ES256")

# Create signer
signer = AIIndexReceiptSigner(
    client_id="my-app",
    client_name="My Application",
    client_version="1.0.0",
    private_key_pem=private_key,
    key_id="key-001",
    algorithm="ES256",
    webhook_retries=3,
    webhook_timeout=10,
)

# Create and post receipt
receipt, posted = signer.create_and_post_receipt(
    document=document,
    url="https://example.com/ai-index.json",
    status_code=200,
    pages_accessed=["https://example.com/about"],
    purpose=Purpose(
        type="inference",
        description="RAG application",
        commercial=True,
    ),
    attribution=Attribution(
        method="citation",
        citation_text="Data from Example.com",
    ),
)

# Verify receipt
is_valid = AIIndexReceiptSigner.verify_receipt(receipt, public_key)

# Context manager support
with AIIndexReceiptSigner(
    client_id="my-app",
    private_key_pem=private_key,
    key_id="key-001",
) as signer:
    receipt, posted = signer.create_and_post_receipt(document, url)
```

### AIIndexLoader

LlamaIndex data loader with advanced filtering.

```python
from aiindex_llama import AIIndexLoader

loader = AIIndexLoader(
    url="example.com",
    validate_schema=True,
    include_metadata=True,
    filter_content_type=["article", "documentation"],
    max_pages=10,
)

# Load all documents
documents = loader.load_data()

# Load by type
result = loader.load_by_type()
publisher_doc = result["publisher"]
entity_docs = result["entities"]
page_docs = result["pages"]
faq_docs = result["faqs"]

# Batch load multiple sites
all_docs = AIIndexLoader.load_batch(
    urls=[
        "https://site1.com/ai-index.json",
        "https://site2.com/ai-index.json",
    ],
    max_pages=5,
)
```

## Configuration Options

### AIIndexReader Parameters

```python
AIIndexReader(
    timeout=10,              # Request timeout in seconds
    validate_schema=True,    # Enable Pydantic validation
    user_agent=None,         # Custom User-Agent header
)
```

### AIIndexLoader Parameters

```python
AIIndexLoader(
    url="example.com",           # URL or domain of ai-index.json
    timeout=10,                  # Request timeout in seconds
    validate_schema=True,        # Enable schema validation
    include_metadata=True,       # Include metadata in documents
    filter_content_type=None,    # Filter pages by content type
    max_pages=None,              # Max number of pages to load
    auto_send_receipt=False,     # Auto-send receipts
    client_id=None,              # Client identifier
    client_name=None,            # Client display name
    client_version=None,         # Client version
    private_key_pem=None,        # Private key for signing (bytes)
    key_id=None,                 # Key identifier
    algorithm="ES256",           # Signature algorithm
)
```

## LlamaIndex Integration

Use loaded documents with any LlamaIndex component:

```python
from aiindex_llama import AIIndexLoader
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding

# Load documents
loader = AIIndexLoader(url="example.com")
documents = loader.load_data()

# Create vector store index
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=OpenAIEmbedding(),
)

# Create query engine
query_engine = index.as_query_engine()
response = query_engine.query("What is this about?")

# Create chat engine
chat_engine = index.as_chat_engine()
response = chat_engine.chat("Tell me about the company")
```

## Document Structure

Each LlamaIndex document includes:

```python
Document(
    text="Formatted text content",
    metadata={
        "source": "URL",              # Original URL
        "type": "page",               # 'publisher' | 'entity' | 'page' | 'faq'
        "title": "Page Title",        # Document title
        "content_type": "article",    # Page content type
        "author": "Author Name",      # Page author
        "published": "2024-01-01",    # Publication date
        "modified": "2024-01-02",     # Last modified date
        "tags": ["tag1", "tag2"],     # Content tags
        "entity_type": "Person",      # Entity type (for entities)
        "entity_name": "John Doe",    # Entity name (for entities)
        "category": "pricing",        # FAQ category (for FAQs)
        "ai_index_source": "URL",     # Source ai-index.json URL
    }
)
```

## Receipt Format

Receipts follow the AIIndex protocol:

```python
Receipt(
    version="1.0",
    receipt_id="uuid-v4",
    publisher_id="example.com",
    client_id="my-app",
    timestamp=datetime.utcnow(),
    access=Access(
        url="https://example.com/ai-index.json",
        method="GET",
        status_code=200,
        content_hash="sha256-hash"
    ),
    purpose=Purpose(
        type="inference",
        description="RAG application",
        commercial=True
    ),
    attribution=Attribution(
        method="citation",
        citation_text="Data from Example.com"
    ),
    signature=Signature(
        algorithm="ES256",
        kid="key-001",
        signature="base64-signature",
        document_hash="sha256-hash",
        signed_at=datetime.utcnow()
    )
)
```

## Error Handling

All methods include comprehensive error handling:

```python
try:
    documents = loader.load_data()
except Exception as e:
    if "HTTP 404" in str(e):
        print("ai-index.json not found")
    elif "Network error" in str(e):
        print("Connection failed")
    elif "Schema validation" in str(e):
        print("Invalid document format")
```

## Advanced Usage

### Custom Validation

```python
reader = AIIndexReader(validate_schema=True)
document = reader.fetch("example.com")

validation = reader.validate_document(document.model_dump())
if not validation["valid"]:
    print("Validation errors:", validation["errors"])
```

### Content Hash Verification

```python
reader = AIIndexReader()
document = reader.fetch("example.com")
hash_value = reader.get_content_hash(document)
print(f"Content hash: {hash_value}")
```

### Batch Receipt Creation

```python
results = signer.create_and_post_receipts_batch([
    {"document": doc1, "url": url1},
    {"document": doc2, "url": url2},
])

for result in results:
    if result.get("posted"):
        print(f"Receipt posted: {result['receipt'].receipt_id}")
    else:
        print(f"Failed: {result.get('error')}")
```

### Filter by Content Type

```python
loader = AIIndexLoader(
    url="example.com",
    filter_content_type=["article", "documentation"],
    max_pages=20,
)

documents = loader.load_data()
```

## Type Hints

Full type hints included for better IDE support:

```python
from aiindex_llama import (
    AIIndexDocument,
    Receipt,
    Purpose,
    Attribution,
    Entity,
    Page,
    FAQ,
)
```

## Examples

See `examples/usage.py` for complete examples including:

- Basic reading and parsing
- Batch operations
- Receipt signing and verification
- LlamaIndex integration
- RAG applications
- Query engines
- Chat engines

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black aiindex_llama
isort aiindex_llama

# Type checking
mypy aiindex_llama
```

## License

MIT

## Links

- Documentation: https://docs.aiindex.org
- GitHub: https://github.com/aiindex/li-aiindex-reader
- AIIndex Protocol: https://aiindex.org
- LlamaIndex: https://www.llamaindex.ai
