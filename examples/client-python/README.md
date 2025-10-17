# IAIndex AI Client Example (Python)

Complete working example for AI applications that access publisher content and send cryptographic receipts.

## Features

- Fetch AI-Index files from publishers
- Access content with proper tracking
- Generate cryptographic receipts
- Submit receipts to IAIndex verification network
- Verify receipt submission
- List verified publishers

## Prerequisites

- Python 3.8+
- pip
- IAIndex API key (optional, but recommended)

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```env
API_BASE_URL=https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io
API_KEY=your-api-key-here
CLIENT_ID=my-ai-client
CLIENT_VERSION=1.0.0
SECRET_KEY=demo-secret
```

## Usage

### Run the complete demo

```bash
python main.py
```

This demonstrates:
1. Fetching verified publishers
2. Accessing AI-Index files
3. Reading content
4. Generating and sending receipts
5. Verifying receipt submission

### Use as a library

```python
from main import IAIndexClient

# Initialize client
client = IAIndexClient(
    api_key='your-api-key',
    client_id='my-ai-app'
)

# Fetch AI-Index
ai_index = client.fetch_ai_index('example.com')

# Access content
content = client.access_content('https://example.com/article')

# Send receipt
receipt = client.send_receipt(
    publisher_domain='example.com',
    article_url='https://example.com/article',
    metadata={
        'client_id': 'my-ai-app',
        'access_type': 'read'
    }
)

# Verify receipt
if receipt:
    verification = client.verify_receipt(receipt['receipt_id'])
```

## Integration Examples

### With LangChain

```python
from langchain.document_loaders import WebBaseLoader
from main import IAIndexClient

client = IAIndexClient()

# Load document
loader = WebBaseLoader('https://example.com/article')
docs = loader.load()

# Send receipt
client.send_receipt(
    publisher_domain='example.com',
    article_url='https://example.com/article',
    metadata={'client': 'langchain', 'doc_count': len(docs)}
)
```

### With LlamaIndex

```python
from llama_index import SimpleWebPageReader
from main import IAIndexClient

client = IAIndexClient()

# Load documents
documents = SimpleWebPageReader(html_to_text=True).load_data(
    ['https://example.com/article']
)

# Send receipt
for doc in documents:
    client.send_receipt(
        publisher_domain='example.com',
        article_url=doc.doc_id,
        metadata={'client': 'llamaindex'}
    )
```

### Custom RAG Pipeline

```python
from main import IAIndexClient

def rag_pipeline(query: str, sources: list):
    client = IAIndexClient()

    # Retrieve and process documents
    documents = []
    for source_url in sources:
        # Parse domain from URL
        domain = urlparse(source_url).netloc

        # Check for AI-Index
        ai_index = client.fetch_ai_index(domain)

        # Fetch content
        content = fetch_content(source_url)  # Your implementation
        documents.append(content)

        # Send receipt
        client.send_receipt(
            publisher_domain=domain,
            article_url=source_url,
            metadata={
                'query': query,
                'retrieval_method': 'vector_search'
            }
        )

    # Generate answer
    answer = generate_answer(query, documents)
    return answer
```

## Receipt Generation

Receipts use HMAC-SHA256 signatures:

```python
import hmac
import hashlib

def generate_signature(receipt_id: str, domain: str,
                      url: str, timestamp: str, secret: str) -> str:
    """Generate receipt signature"""
    data = f"{receipt_id}:{domain}:{url}:{timestamp}"
    return hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
```

Receipt format:
```json
{
  "receipt_id": "uuid-v4",
  "publisher_domain": "example.com",
  "article_url": "https://example.com/article",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "signature": "hex-encoded-hmac-signature",
  "metadata": {
    "client_id": "my-ai-client",
    "client_version": "1.0.0"
  }
}
```

## Best Practices

### 1. Always Check for AI-Index

```python
ai_index = client.fetch_ai_index(domain)
if ai_index:
    # Publisher participates in IAIndex
    # Respect their preferences
    pass
```

### 2. Send Receipts Immediately

```python
# Right after accessing content
content = access_content(url)
client.send_receipt(domain, url)
```

### 3. Include Meaningful Metadata

```python
metadata = {
    'client_id': 'my-rag-system',
    'client_version': '2.0.0',
    'query': 'user query',
    'retrieval_method': 'semantic_search',
    'embedding_model': 'text-embedding-ada-002',
    'tokens_used': 1500
}
```

### 4. Handle Errors Gracefully

```python
try:
    receipt = client.send_receipt(domain, url)
    if not receipt:
        # Log failure, but continue
        logger.warning(f"Receipt failed for {url}")
except Exception as e:
    # Don't let receipt failures break your pipeline
    logger.error(f"Receipt error: {e}")
```

### 5. Respect Rate Limits

```python
import time

for url in urls:
    client.send_receipt(domain, url)
    time.sleep(0.1)  # 10 requests/second
```

## Testing

Run tests with pytest:

```bash
# Install test dependencies
pip install pytest pytest-mock

# Run tests
pytest test_client.py -v
```

## Common Issues

### 1. Receipt Verification Fails

**Issue**: Receipt is rejected with "Publisher not verified"

**Solution**:
- Check that the publisher domain is verified
- Use `client.get_verified_publishers()` to see verified domains
- Ensure domain matches exactly (no www vs non-www mismatch)

### 2. Signature Verification Fails

**Issue**: Receipt status is "failed" due to signature mismatch

**Solution**:
- Ensure SECRET_KEY matches publisher's verification key
- Check timestamp format is ISO 8601
- Verify signature data order: `receipt_id:domain:url:timestamp`

### 3. AI-Index Not Found

**Issue**: `fetch_ai_index()` returns None

**Solution**:
- Verify the publisher has deployed `ai-index.json` at root
- Check both HTTPS and HTTP
- Ensure no CORS issues (shouldn't affect server-side)

## Performance Considerations

### Batch Receipt Submission

For high-volume scenarios:

```python
from concurrent.futures import ThreadPoolExecutor

def send_receipt_batch(urls: list):
    client = IAIndexClient()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for url in urls:
            domain = urlparse(url).netloc
            future = executor.submit(
                client.send_receipt, domain, url
            )
            futures.append(future)

        results = [f.result() for f in futures]

    return results
```

### Caching AI-Index Files

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_ai_index(domain: str):
    client = IAIndexClient()
    return client.fetch_ai_index(domain)
```

## Resources

- [IAIndex Documentation](https://docs.aiindex.org)
- [API Reference](https://docs.aiindex.org/api)
- [Protocol Specification](https://docs.aiindex.org/spec)
- [Best Practices for AI Clients](https://docs.aiindex.org/ai-clients)

## Support

- GitHub Issues: [github.com/iaindex/iaindex](https://github.com/iaindex/iaindex)
- Discord: [discord.gg/iaindex](https://discord.gg/iaindex)
- Email: support@iaindex.com

## License

MIT
