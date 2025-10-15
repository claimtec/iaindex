---
sidebar_position: 2
title: LlamaIndex Integration
---

# LlamaIndex Integration

Integrate IAIndex with LlamaIndex for transparent AI attribution.

## Installation

```bash
pip install llama-index-iaindex
```

## Usage

```python
from llama_index.readers.iaindex import IAIndexReader

reader = IAIndexReader(
    client_id='your-client-id',
    private_key='your-private-key'
)

documents = reader.load_data(urls=['https://example.com/article'])
```

## Configuration

```python
reader = IAIndexReader(
    client_id='client-id',
    private_key=private_key,
    send_receipts=True,
    usage_purpose='inference',
    usage_context='rag-retrieval'
)
```

## Examples

See [LlamaIndex Examples](https://github.com/claimtec/iaindex/tree/main/examples/llamaindex)
