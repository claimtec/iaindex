# AIIndex Python SDK

Python SDK for the [AIIndex Protocol](https://aiindex.org) - Create AI-readable website metadata, manage access control, and handle cryptographic signatures for verifiable AI content indexing.

## Features

- **AIIndexGenerator**: Crawl websites and automatically extract metadata
- **SignatureManager**: ECDSA (ES256) and RSA (RS256) signature support
- **ReceiptHandler**: Webhook server for receiving AI access receipts
- **Validator**: JSON schema validation for documents and receipts
- **CLI Tool**: `aiindex-gen` command-line interface
- **Type Safety**: Full Pydantic models with type hints
- **Python 3.8+**: Modern Python with async support

## Installation

```bash
pip install aiindex-sdk
```

Or install from source:

```bash
cd packages/sdk-python
pip install -e .
```

## Quick Start

### 1. Generate an AI-index.json file

```python
from aiindex import AIIndexGenerator

# Create generator
generator = AIIndexGenerator(
    publisher_id="example.com",
    domain="example.com"
)

# Crawl your website
generator.crawl("https://example.com", max_pages=20, max_depth=3)

# Extract metadata
generator.extract_metadata("https://example.com")

# Build and save
doc = generator.build()
with open("ai-index.json", "w") as f:
    f.write(generator.to_json())
```

### 2. Sign your document

```python
from aiindex import SignatureManager

# Create manager and generate keypair
manager = SignatureManager()
private_key, public_key = manager.generate_keypair("ES256")

# Save keys
manager.save_key(private_key, "private.pem")
manager.save_key(public_key, "public.pem")

# Sign document
import json
with open("ai-index.json") as f:
    doc = json.load(f)

signed_doc = manager.sign_document(doc, private_key, "key-123", "ES256")

with open("ai-index.json", "w") as f:
    json.dump(signed_doc, f, indent=2)
```

### 3. Validate a document

```python
from aiindex import Validator

validator = Validator()
is_valid, errors = validator.validate_json_file("ai-index.json")

if is_valid:
    print("Valid AI-index.json!")
else:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### 4. Handle access receipts

```python
from aiindex import ReceiptHandler

# Create handler
handler = ReceiptHandler(validate=True)

# Register callback
def on_receipt(receipt):
    print(f"Received receipt from {receipt['client_id']}")
    print(f"Publisher: {receipt['publisher_id']}")

handler.on_receipt(on_receipt)

# Start webhook server
handler.start_server(port=8080)
```

## CLI Usage

The SDK includes a comprehensive CLI tool called `aiindex-gen`:

### Initialize a new file

```bash
aiindex-gen init --domain example.com --publisher-id example.com
```

### Build from website crawl

```bash
aiindex-gen build https://example.com --max-pages 20 --max-depth 3
```

### Verify a document

```bash
aiindex-gen verify ai-index.json
```

### Sign a document

```bash
# Generate new keypair and sign
aiindex-gen sign ai-index.json --key-id key-123 --generate-key --algorithm ES256

# Sign with existing key
aiindex-gen sign ai-index.json --key-id key-123 --private-key private.pem
```

### Start webhook server

```bash
aiindex-gen serve --port 8080
```

### Display document info

```bash
aiindex-gen info ai-index.json
```

## Advanced Usage

### Create custom entities

```python
from aiindex import AIIndexGenerator, Entity, EntityType

generator = AIIndexGenerator("example.com", "example.com")

# Add entities
generator.add_entity(Entity(
    type=EntityType.ORGANIZATION,
    name="Example Corp",
    description="A leading technology company",
    url="https://example.com/about"
))

generator.add_entity(Entity(
    type=EntityType.PRODUCT,
    name="Example Product",
    description="Our flagship product",
    url="https://example.com/products/example"
))
```

### Add FAQ entries

```python
generator.add_faq(
    question="What is AIIndex?",
    answer="AIIndex is a protocol for AI-readable website metadata.",
    category="General"
)

generator.add_faq(
    question="How do I get started?",
    answer="Install the SDK and run aiindex-gen init.",
    category="Getting Started"
)
```

### Create and send receipts

```python
from aiindex import ReceiptClient, SignatureManager

# Setup client
client = ReceiptClient(
    client_id="my-ai-app",
    client_name="My AI Application",
    version="1.0.0"
)

# Generate keypair
manager = SignatureManager()
private_key, public_key = manager.generate_keypair("ES256")

# Create receipt
receipt = client.create_access_receipt(
    publisher_id="example.com",
    url="https://example.com/ai-index.json",
    private_key=private_key,
    key_id="client-key-123",
    status_code=200,
    purpose_type="inference",
    purpose_description="Using content for AI responses",
    commercial=True,
    attribution_method="citation"
)

# Send to webhook
client.send(receipt, "https://example.com/webhook")
```

### Verify signatures

```python
from aiindex import SignatureManager
import json

manager = SignatureManager()

# Load document and public key
with open("ai-index.json") as f:
    doc = json.load(f)

public_key = manager.load_key("public.pem")

# Verify
is_valid = manager.verify_document(doc, public_key)
print(f"Signature valid: {is_valid}")
```

### Custom access policies

```python
from aiindex import AIIndexGenerator, AccessPolicy

generator = AIIndexGenerator("example.com", "example.com")

# Set access policy
doc = generator.build()
doc.access_policy = AccessPolicy(
    allowed=True,
    attribution_required=True,
    commercial_use=True,
    receipt_required=True,
    webhook_url="https://example.com/webhook"
)

# Save with policy
with open("ai-index.json", "w") as f:
    f.write(doc.model_dump_json(exclude_none=True, indent=2))
```

## API Reference

### AIIndexGenerator

```python
class AIIndexGenerator:
    def __init__(self, publisher_id: str, domain: str, user_agent: str = "AIIndexGenerator/1.0")
    def crawl(self, start_url: str, max_pages: int = 10, max_depth: int = 3) -> int
    def extract_metadata(self, url: str) -> Dict
    def add_entity(self, entity: Entity) -> None
    def add_faq(self, question: str, answer: str, category: Optional[str] = None) -> None
    def build(self) -> AIIndexDocument
    def to_dict(self) -> Dict
    def to_json(self) -> str
```

### SignatureManager

```python
class SignatureManager:
    def generate_keypair(self, algorithm: str = "ES256") -> Tuple[bytes, bytes]
    def sign(self, data: Dict, private_key_pem: bytes, kid: str, algorithm: str = "ES256") -> Signature
    def verify(self, data: Dict, signature: Signature, public_key_pem: bytes) -> bool
    def sign_document(self, document: Dict, private_key_pem: bytes, kid: str, algorithm: str = "ES256") -> Dict
    def verify_document(self, document: Dict, public_key_pem: bytes) -> bool
    def save_key(self, key_pem: bytes, filepath: str) -> None
    def load_key(self, filepath: str) -> bytes
```

### Validator

```python
class Validator:
    def __init__(self, schema_dir: Optional[str] = None)
    def validate_document(self, document: Dict) -> Tuple[bool, Optional[List[str]]]
    def validate_receipt(self, receipt: Dict) -> Tuple[bool, Optional[List[str]]]
    def validate_json_file(self, filepath: str) -> Tuple[bool, Optional[List[str]]]
    def validate_access_policy(self, policy: Dict) -> Tuple[bool, Optional[List[str]]]
    def validate_signature(self, signature: Dict) -> Tuple[bool, Optional[List[str]]]
```

### ReceiptHandler

```python
class ReceiptHandler:
    def __init__(self, validate: bool = True)
    def on_receipt(self, callback: Callable[[Dict], None]) -> None
    def start_server(self, host: str = '0.0.0.0', port: int = 8080, debug: bool = False) -> None
    def start_server_background(self, host: str = '0.0.0.0', port: int = 8080) -> Thread
    def get_receipts(self) -> list[Dict]
    def clear_receipts(self) -> None
```

### ReceiptClient

```python
class ReceiptClient:
    def __init__(self, client_id: str, client_name: str, version: str = "1.0.0")
    def create_access_receipt(
        self,
        publisher_id: str,
        url: str,
        private_key: bytes,
        key_id: str,
        **kwargs
    ) -> Receipt
    def send(self, receipt: Receipt, webhook_url: str) -> bool
```

## Type Definitions

The SDK uses Pydantic models for type safety:

- `AIIndexDocument`: Complete AI-index document
- `Publisher`: Publisher information
- `Entity`: Structured entity (Person, Organization, Product, etc.)
- `Page`: Indexed page metadata
- `FAQ`: Frequently asked question
- `AccessPolicy`: AI access control policy
- `Signature`: Cryptographic signature
- `Receipt`: Access receipt
- `Access`: Access details
- `Purpose`: Purpose of AI access
- `Attribution`: Attribution details

## Examples

See the `examples/` directory for complete examples:

- `basic_usage.py`: Basic document generation
- `crawl_website.py`: Website crawling and metadata extraction
- `signing.py`: Cryptographic signing and verification
- `receipts.py`: Receipt handling and webhook server
- `validation.py`: Document validation

## Development

### Setup development environment

```bash
# Clone repository
git clone https://github.com/aiindex/aiindex.git
cd iaindex/packages/sdk-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Run tests

```bash
pytest tests/
```

### Format code

```bash
black aiindex/
```

### Type checking

```bash
mypy aiindex/
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Links

- **Documentation**: https://aiindex.org/docs
- **GitHub**: https://github.com/aiindex/aiindex
- **PyPI**: https://pypi.org/project/aiindex-sdk/
- **Issues**: https://github.com/aiindex/aiindex/issues

## Support

- Email: contact@aiindex.org
- Discord: https://discord.gg/aiindex
- Twitter: [@aiindex](https://twitter.com/aiindex)
