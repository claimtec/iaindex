# AIIndex Connectors - Quick Reference

## Installation

### LangChain (TypeScript)
```bash
npm install @aiindex/lc-aiindex-reader langchain @langchain/core
```

### LlamaIndex (Python)
```bash
pip install aiindex-llama llama-index-core
```

---

## Basic Usage

### LangChain - Simple Load

```typescript
import { AIIndexLoader } from '@aiindex/lc-aiindex-reader';

const loader = new AIIndexLoader('example.com');
const documents = await loader.load();

// Use with LangChain
import { Chroma } from '@langchain/community/vectorstores/chroma';
const vectorStore = await Chroma.fromDocuments(documents, embeddings);
```

### LlamaIndex - Simple Load

```python
from aiindex_llama import AIIndexLoader

loader = AIIndexLoader(url="example.com")
documents = loader.load_data()

# Use with LlamaIndex
from llama_index.core import VectorStoreIndex
index = VectorStoreIndex.from_documents(documents)
```

---

## With Automatic Receipts

### LangChain

```typescript
import { AIIndexLoader, AIIndexReceiptSigner } from '@aiindex/lc-aiindex-reader';

// Generate keypair once
const { privateKey, publicKey } = await AIIndexReceiptSigner.generateKeyPair('ES256');

// Load with receipts
const loader = new AIIndexLoader('example.com', {
  autoSendReceipt: true,
  clientId: 'my-app',
  privateKeyPem: privateKey,
  keyId: 'key-001',
});

const documents = await loader.load();
```

### LlamaIndex

```python
from aiindex_llama import AIIndexLoader, AIIndexReceiptSigner

# Generate keypair once
private_key, public_key = AIIndexReceiptSigner.generate_keypair("ES256")

# Load with receipts
loader = AIIndexLoader(
    url="example.com",
    auto_send_receipt=True,
    client_id="my-app",
    private_key_pem=private_key,
    key_id="key-001",
)

documents = loader.load_data()
```

---

## Manual Receipt Creation

### LangChain

```typescript
import { AIIndexReader, AIIndexReceiptSigner } from '@aiindex/lc-aiindex-reader';

const reader = new AIIndexReader();
const document = await reader.fetch('example.com');

const signer = new AIIndexReceiptSigner({
  clientId: 'my-app',
  privateKeyPem: privateKey,
  keyId: 'key-001',
});

await signer.initialize();

const { receipt, posted } = await signer.createAndPostReceipt(document, {
  url: 'https://example.com/ai-index.json',
  purpose: { type: 'inference', commercial: true },
  attribution: { method: 'citation', citation_text: 'From Example.com' },
});
```

### LlamaIndex

```python
from aiindex_llama import AIIndexReader, AIIndexReceiptSigner, Purpose, Attribution

reader = AIIndexReader()
document = reader.fetch("example.com")

signer = AIIndexReceiptSigner(
    client_id="my-app",
    private_key_pem=private_key,
    key_id="key-001",
)

receipt, posted = signer.create_and_post_receipt(
    document=document,
    url="https://example.com/ai-index.json",
    purpose=Purpose(type="inference", commercial=True),
    attribution=Attribution(method="citation", citation_text="From Example.com"),
)
```

---

## Batch Loading

### LangChain

```typescript
import { AIIndexLoader } from '@aiindex/lc-aiindex-reader';

const documents = await AIIndexLoader.loadBatch([
  'site1.com',
  'site2.com',
  'site3.com',
], {
  includeMetadata: true,
  maxPages: 5,
});
```

### LlamaIndex

```python
from aiindex_llama import AIIndexLoader

documents = AIIndexLoader.load_batch(
    urls=["site1.com", "site2.com", "site3.com"],
    include_metadata=True,
    max_pages=5,
)
```

---

## Load by Type

### LangChain

```typescript
const loader = new AIIndexLoader('example.com');
const { publisher, entities, pages, faqs } = await loader.loadByType();

console.log(`Pages: ${pages.length}`);
console.log(`Entities: ${entities.length}`);
```

### LlamaIndex

```python
loader = AIIndexLoader(url="example.com")
result = loader.load_by_type()

print(f"Pages: {len(result['pages'])}")
print(f"Entities: {len(result['entities'])}")
```

---

## Filter Content

### LangChain

```typescript
const loader = new AIIndexLoader('example.com', {
  filterContentType: ['article', 'documentation'],
  maxPages: 20,
});
```

### LlamaIndex

```python
loader = AIIndexLoader(
    url="example.com",
    filter_content_type=["article", "documentation"],
    max_pages=20,
)
```

---

## Extract Specific Data

### LangChain

```typescript
const reader = new AIIndexReader();
const document = await reader.fetch('example.com');

const pageUrls = reader.extractPageUrls(document);
const people = reader.extractEntitiesByType(document, 'Person');
const faqs = reader.getFaqByCategory(document, 'pricing');
```

### LlamaIndex

```python
reader = AIIndexReader()
document = reader.fetch("example.com")

page_urls = reader.extract_page_urls(document)
people = reader.extract_entities_by_type(document, "Person")
faqs = reader.get_faq_by_category(document, "pricing")
```

---

## Configuration Options

### LangChain AIIndexLoader

```typescript
new AIIndexLoader(url, {
  timeout: 10000,                    // Request timeout (ms)
  validateSchema: true,              // Validate schema
  includeMetadata: true,             // Include metadata
  filterContentType: ['article'],    // Filter pages
  maxPages: 10,                      // Max pages
  autoSendReceipt: false,            // Auto-send receipts
  clientId: 'my-app',                // Client ID
  clientName: 'My App',              // Client name
  privateKeyPem: '...',              // Private key
  keyId: 'key-001',                  // Key ID
  algorithm: 'ES256',                // Signature algorithm
})
```

### LlamaIndex AIIndexLoader

```python
AIIndexLoader(
    url="example.com",
    timeout=10,                       # Request timeout (sec)
    validate_schema=True,             # Validate schema
    include_metadata=True,            # Include metadata
    filter_content_type=["article"],  # Filter pages
    max_pages=10,                     # Max pages
    auto_send_receipt=False,          # Auto-send receipts
    client_id="my-app",               # Client ID
    client_name="My App",             # Client name
    private_key_pem=b"...",           # Private key (bytes)
    key_id="key-001",                 # Key ID
    algorithm="ES256",                # Signature algorithm
)
```

---

## Complete Examples

### LangChain: RAG with OpenAI

```typescript
import { AIIndexLoader } from '@aiindex/lc-aiindex-reader';
import { ChatOpenAI } from '@langchain/openai';
import { RetrievalQAChain } from 'langchain/chains';
import { MemoryVectorStore } from 'langchain/vectorstores/memory';
import { OpenAIEmbeddings } from '@langchain/openai';

// Load documents
const loader = new AIIndexLoader('example.com', {
  autoSendReceipt: true,
  clientId: 'my-rag-app',
  privateKeyPem: privateKey,
  keyId: 'key-001',
});

const docs = await loader.load();

// Create vector store
const vectorStore = await MemoryVectorStore.fromDocuments(
  docs,
  new OpenAIEmbeddings()
);

// Create QA chain
const model = new ChatOpenAI({ modelName: 'gpt-4' });
const chain = RetrievalQAChain.fromLLM(
  model,
  vectorStore.asRetriever()
);

const response = await chain.call({
  query: "What does this company do?",
});

console.log(response.text);
```

### LlamaIndex: Query Engine

```python
from aiindex_llama import AIIndexLoader
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Load documents
loader = AIIndexLoader(
    url="example.com",
    auto_send_receipt=True,
    client_id="my-rag-app",
    private_key_pem=private_key,
    key_id="key-001",
)

documents = loader.load_data()

# Create index
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=OpenAIEmbedding(),
)

# Create query engine
query_engine = index.as_query_engine(
    llm=OpenAI(model="gpt-4")
)

response = query_engine.query("What does this company do?")
print(response)
```

---

## Document Metadata

Both connectors provide rich metadata on documents:

```typescript
// LangChain
document.metadata = {
  source: "https://example.com/page",
  type: "page",                    // 'publisher' | 'entity' | 'page' | 'faq'
  title: "Page Title",
  content_type: "article",
  author: "John Doe",
  published: "2024-01-01",
  tags: ["tag1", "tag2"],
  ai_index_source: "https://example.com/ai-index.json",
}
```

```python
# LlamaIndex
document.metadata = {
    "source": "https://example.com/page",
    "type": "page",                    # 'publisher' | 'entity' | 'page' | 'faq'
    "title": "Page Title",
    "content_type": "article",
    "author": "John Doe",
    "published": "2024-01-01",
    "tags": ["tag1", "tag2"],
    "ai_index_source": "https://example.com/ai-index.json",
}
```

---

## Receipt Verification

### LangChain

```typescript
import { AIIndexReceiptSigner } from '@aiindex/lc-aiindex-reader';

const isValid = await AIIndexReceiptSigner.verifyReceipt(receipt, publicKey);
console.log(`Receipt valid: ${isValid}`);
```

### LlamaIndex

```python
from aiindex_llama import AIIndexReceiptSigner

is_valid = AIIndexReceiptSigner.verify_receipt(receipt, public_key)
print(f"Receipt valid: {is_valid}")
```

---

## Error Handling

### LangChain

```typescript
try {
  const documents = await loader.load();
} catch (error) {
  if (error.message.includes('HTTP 404')) {
    console.error('ai-index.json not found');
  } else if (error.message.includes('Network error')) {
    console.error('Connection failed');
  }
}
```

### LlamaIndex

```python
try:
    documents = loader.load_data()
except Exception as e:
    if "HTTP 404" in str(e):
        print("ai-index.json not found")
    elif "Network error" in str(e):
        print("Connection failed")
```

---

## Context Managers (Python Only)

```python
# Reader
with AIIndexReader() as reader:
    document = reader.fetch("example.com")

# Signer
with AIIndexReceiptSigner(
    client_id="my-app",
    private_key_pem=private_key,
    key_id="key-001",
) as signer:
    receipt, posted = signer.create_and_post_receipt(document, url)
```

---

## Key Generation

### LangChain (ES256)

```typescript
const { privateKey, publicKey } = await AIIndexReceiptSigner.generateKeyPair('ES256');
// Save these securely
```

### LlamaIndex (ES256)

```python
private_key, public_key = AIIndexReceiptSigner.generate_keypair("ES256")
# Save these securely
```

---

## Support

- Documentation: https://docs.aiindex.org
- GitHub Issues: https://github.com/aiindex/
- Protocol Spec: https://aiindex.org

---

## License

MIT License - Both packages
