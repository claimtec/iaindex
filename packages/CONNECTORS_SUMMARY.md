# AIIndex Connectors - LangChain & LlamaIndex

Complete implementation of AIIndex connectors for both LangChain and LlamaIndex frameworks.

## Overview

Both packages provide seamless integration with their respective frameworks, enabling AI applications to:
- Fetch and parse `ai-index.json` files from websites
- Automatically validate against JSON schema
- Convert to framework-native document formats
- Generate cryptographically signed receipts
- Auto-post receipts to publisher webhooks
- Support batch operations
- Handle network errors with retries

---

## LangChain Connector (@aiindex/lc-aiindex-reader)

### Location
`/Users/dineshanchetty/Documents/claimtec/iaindex/packages/lc-aiindex-reader/`

### Package Structure
```
lc-aiindex-reader/
├── src/
│   ├── index.ts          # Main exports
│   ├── types.ts          # TypeScript type definitions
│   ├── reader.ts         # AIIndexReader class
│   ├── signer.ts         # AIIndexReceiptSigner class
│   └── loader.ts         # AIIndexLoader class (LangChain integration)
├── examples/
│   └── usage.ts          # Comprehensive usage examples
├── package.json          # NPM package configuration
├── tsconfig.json         # TypeScript configuration
└── README.md             # Documentation
```

### Core Classes

#### 1. AIIndexReader
Fetches and validates `ai-index.json` files.

**Features:**
- HTTP client with timeout and retry
- Automatic JSON schema validation with AJV
- Batch fetching support
- Domain probing
- Content hash computation (SHA-256)
- Helper methods for data extraction

**Usage:**
```typescript
import { AIIndexReader } from '@aiindex/lc-aiindex-reader';

const reader = new AIIndexReader({
  timeout: 10000,
  validateSchema: true,
});

const document = await reader.fetch('example.com');
const pageUrls = reader.extractPageUrls(document);
```

#### 2. AIIndexReceiptSigner
Creates and signs cryptographic receipts.

**Features:**
- ES256 (ECDSA P-256) and RS256 (RSA) signatures
- JWK/PEM key format support
- Automatic receipt generation
- Webhook posting with exponential backoff
- Batch receipt creation
- Receipt verification

**Usage:**
```typescript
import { AIIndexReceiptSigner } from '@aiindex/lc-aiindex-reader';

// Generate keypair
const { privateKey, publicKey } = await AIIndexReceiptSigner.generateKeyPair('ES256');

// Create signer
const signer = new AIIndexReceiptSigner({
  clientId: 'my-app',
  clientName: 'My Application',
  privateKeyPem: privateKey,
  keyId: 'key-001',
  algorithm: 'ES256',
});

await signer.initialize();

// Create and post receipt
const { receipt, posted } = await signer.createAndPostReceipt(document, {
  url: 'https://example.com/ai-index.json',
  statusCode: 200,
  purpose: { type: 'inference', commercial: true },
  attribution: { method: 'citation', citation_text: 'Data from Example.com' },
});
```

#### 3. AIIndexLoader
LangChain document loader integration.

**Features:**
- Extends LangChain's BaseDocumentLoader
- Converts AIIndex data to LangChain Documents
- Automatic receipt generation (optional)
- Content type filtering
- Page limit control
- Load by document type
- Batch loading support

**Usage:**
```typescript
import { AIIndexLoader } from '@aiindex/lc-aiindex-reader';

const loader = new AIIndexLoader('example.com', {
  validateSchema: true,
  includeMetadata: true,
  filterContentType: ['article', 'documentation'],
  maxPages: 10,
  autoSendReceipt: true,
  clientId: 'my-app',
  privateKeyPem: privateKey,
  keyId: 'key-001',
});

const documents = await loader.load();

// Use with LangChain
import { Chroma } from '@langchain/community/vectorstores/chroma';
import { OpenAIEmbeddings } from '@langchain/openai';

const vectorStore = await Chroma.fromDocuments(
  documents,
  new OpenAIEmbeddings()
);
```

### Installation
```bash
npm install @aiindex/lc-aiindex-reader langchain @langchain/core
```

### Dependencies
- `langchain` & `@langchain/core`: LangChain framework
- `axios`: HTTP client
- `jose`: Cryptographic operations
- `ajv`: JSON schema validation
- `uuid`: UUID generation

---

## LlamaIndex Connector (aiindex-llama)

### Location
`/Users/dineshanchetty/Documents/claimtec/iaindex/packages/li-aiindex-reader/`

### Package Structure
```
li-aiindex-reader/
├── aiindex_llama/
│   ├── __init__.py       # Package exports
│   ├── types.py          # Pydantic type models
│   ├── reader.py         # AIIndexReader class
│   ├── signer.py         # AIIndexReceiptSigner class
│   └── loader.py         # AIIndexLoader class (LlamaIndex integration)
├── examples/
│   └── usage.py          # Comprehensive usage examples
├── setup.py              # Package setup
├── pyproject.toml        # Modern Python packaging
└── README.md             # Documentation
```

### Core Classes

#### 1. AIIndexReader
Fetches and validates `ai-index.json` files.

**Features:**
- Requests-based HTTP client
- Pydantic model validation
- Batch fetching support
- Domain probing
- Content hash computation (SHA-256)
- Helper methods for data extraction
- Context manager support

**Usage:**
```python
from aiindex_llama import AIIndexReader

with AIIndexReader(timeout=10, validate_schema=True) as reader:
    document = reader.fetch("example.com")
    page_urls = reader.extract_page_urls(document)
    people = reader.extract_entities_by_type(document, "Person")
```

#### 2. AIIndexReceiptSigner
Creates and signs cryptographic receipts.

**Features:**
- ES256 (ECDSA P-256) and RS256 (RSA) signatures
- PEM key format support
- Automatic receipt generation
- Webhook posting with exponential backoff
- Batch receipt creation
- Receipt verification
- Context manager support

**Usage:**
```python
from aiindex_llama import AIIndexReceiptSigner, Purpose, Attribution

# Generate keypair
private_key, public_key = AIIndexReceiptSigner.generate_keypair("ES256")

# Create signer
with AIIndexReceiptSigner(
    client_id="my-app",
    client_name="My Application",
    private_key_pem=private_key,
    key_id="key-001",
    algorithm="ES256",
) as signer:
    # Create and post receipt
    receipt, posted = signer.create_and_post_receipt(
        document=document,
        url="https://example.com/ai-index.json",
        status_code=200,
        purpose=Purpose(type="inference", commercial=True),
        attribution=Attribution(method="citation", citation_text="Data from Example.com"),
    )
```

#### 3. AIIndexLoader
LlamaIndex data loader integration.

**Features:**
- Extends LlamaIndex's BaseReader
- Converts AIIndex data to LlamaIndex Documents
- Automatic receipt generation (optional)
- Content type filtering
- Page limit control
- Load by document type
- Batch loading support
- Full type hints

**Usage:**
```python
from aiindex_llama import AIIndexLoader

loader = AIIndexLoader(
    url="example.com",
    validate_schema=True,
    include_metadata=True,
    filter_content_type=["article", "documentation"],
    max_pages=10,
    auto_send_receipt=True,
    client_id="my-app",
    private_key_pem=private_key,
    key_id="key-001",
)

documents = loader.load_data()

# Use with LlamaIndex
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is this about?")
```

### Installation
```bash
pip install aiindex-llama llama-index-core
```

### Dependencies
- `llama-index-core`: LlamaIndex framework
- `requests`: HTTP client
- `pydantic`: Data validation
- `cryptography`: Cryptographic operations
- `jsonschema`: JSON schema validation

---

## Common Features

### Both Connectors Support:

1. **Signature Algorithms**
   - ES256 (ECDSA with P-256 curve and SHA-256)
   - RS256 (RSA with SHA-256)

2. **Automatic Schema Validation**
   - Validates against AIIndex protocol schema
   - Provides detailed validation errors
   - Optional validation bypass

3. **Receipt Generation**
   - Cryptographically signed receipts
   - SHA-256 content hashing
   - UUID v4 receipt IDs
   - Timestamp tracking

4. **Webhook Integration**
   - Automatic posting to publisher webhooks
   - Exponential backoff retry logic
   - Configurable retry attempts and timeouts
   - Error handling and logging

5. **Batch Operations**
   - Batch fetching from multiple domains
   - Batch receipt creation and posting
   - Parallel processing with error isolation

6. **Network Error Handling**
   - Timeout configuration
   - Retry mechanisms
   - Connection error handling
   - HTTP status code handling

7. **Metadata Extraction**
   - Publisher information
   - Entity data (Person, Organization, Product, etc.)
   - Page content with summaries
   - FAQ items
   - Access policies

---

## Document Format

### AIIndex Document Structure
```json
{
  "version": "1.0",
  "publisher_id": "example.com",
  "domain": "example.com",
  "last_updated": "2024-01-01T00:00:00Z",
  "publisher": {
    "name": "Example Corp",
    "description": "Example company",
    "url": "https://example.com",
    "contact": { "email": "contact@example.com" }
  },
  "entities": [
    {
      "type": "Person",
      "name": "John Doe",
      "description": "CEO"
    }
  ],
  "pages": [
    {
      "url": "https://example.com/about",
      "title": "About Us",
      "content_type": "page",
      "summary": "Company information..."
    }
  ],
  "faq": [
    {
      "question": "What do you do?",
      "answer": "We provide services..."
    }
  ],
  "access_policy": {
    "allowed": true,
    "receipt_required": true,
    "webhook_url": "https://example.com/webhooks/aiindex"
  }
}
```

### Receipt Format
```json
{
  "version": "1.0",
  "receipt_id": "550e8400-e29b-41d4-a716-446655440000",
  "publisher_id": "example.com",
  "client_id": "my-app",
  "timestamp": "2024-01-01T00:00:00Z",
  "access": {
    "url": "https://example.com/ai-index.json",
    "method": "GET",
    "status_code": 200,
    "content_hash": "abc123..."
  },
  "purpose": {
    "type": "inference",
    "description": "RAG application",
    "commercial": true
  },
  "attribution": {
    "method": "citation",
    "citation_text": "Data from Example.com"
  },
  "signature": {
    "algorithm": "ES256",
    "kid": "key-001",
    "signature": "base64-encoded-signature",
    "document_hash": "sha256-hash"
  }
}
```

---

## Usage Examples

### LangChain: Basic RAG Application
```typescript
import { AIIndexLoader } from '@aiindex/lc-aiindex-reader';
import { OpenAI } from '@langchain/openai';
import { RetrievalQAChain } from 'langchain/chains';
import { HNSWLib } from '@langchain/community/vectorstores/hnswlib';
import { OpenAIEmbeddings } from '@langchain/openai';

// Load documents
const loader = new AIIndexLoader('example.com', {
  autoSendReceipt: true,
  clientId: 'my-rag-app',
  privateKeyPem: privateKey,
  keyId: 'key-001',
});

const documents = await loader.load();

// Create vector store
const vectorStore = await HNSWLib.fromDocuments(
  documents,
  new OpenAIEmbeddings()
);

// Create QA chain
const model = new OpenAI();
const chain = RetrievalQAChain.fromLLM(model, vectorStore.asRetriever());

const response = await chain.call({
  query: "What does this company do?",
});
```

### LlamaIndex: Chat Engine
```python
from aiindex_llama import AIIndexLoader
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI

# Load documents
loader = AIIndexLoader(
    url="example.com",
    auto_send_receipt=True,
    client_id="my-chat-app",
    private_key_pem=private_key,
    key_id="key-001",
)

documents = loader.load_data()

# Create index
index = VectorStoreIndex.from_documents(documents)

# Create chat engine
chat_engine = index.as_chat_engine(
    llm=OpenAI(model="gpt-4"),
    chat_mode="context"
)

response = chat_engine.chat("Tell me about this company")
print(response)
```

---

## Key Differences

| Feature | LangChain (TypeScript) | LlamaIndex (Python) |
|---------|----------------------|-------------------|
| Language | TypeScript/JavaScript | Python 3.8+ |
| Framework | LangChain | LlamaIndex |
| Validation | AJV (JSON Schema) | Pydantic |
| Crypto | jose (JWK/JWS) | cryptography (PEM) |
| HTTP | axios | requests |
| Key Format | JWK or PEM | PEM only |
| Async | Promise-based | Sync (async planned) |
| Context Mgr | No | Yes (with/as) |

---

## Testing

### LangChain Connector
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/lc-aiindex-reader
npm install
npm run build
npm test
```

### LlamaIndex Connector
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/li-aiindex-reader
pip install -e ".[dev]"
pytest
```

---

## Publishing

### LangChain to NPM
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/lc-aiindex-reader
npm run build
npm publish --access public
```

### LlamaIndex to PyPI
```bash
cd /Users/dineshanchetty/Documents/claimtec/iaindex/packages/li-aiindex-reader
python -m build
python -m twine upload dist/*
```

---

## License

Both packages are licensed under MIT License.

## Links

- AIIndex Protocol: https://aiindex.org
- Documentation: https://docs.aiindex.org
- LangChain: https://js.langchain.com
- LlamaIndex: https://www.llamaindex.ai

---

## Summary

Both connectors provide production-ready implementations for integrating AIIndex protocol into AI applications. They include:

- ✅ Complete protocol implementation
- ✅ Automatic schema validation
- ✅ Cryptographic receipt generation (ES256/RS256)
- ✅ Automatic webhook posting
- ✅ Batch operations
- ✅ Error handling with retries
- ✅ Comprehensive documentation
- ✅ Usage examples
- ✅ TypeScript/Python type safety
- ✅ Framework-native integration

The connectors are ready for immediate use in production applications.
