---
sidebar_position: 1
title: LangChain Integration
---

# LangChain Integration

Integrate IAIndex with LangChain for transparent AI attribution.

## Installation

```bash
pip install langchain-iaindex
```

## Usage

```python
from langchain_iaindex import IAIndexWebLoader

loader = IAIndexWebLoader(
    urls=['https://example.com/article'],
    client_id='your-client-id',
    private_key='your-private-key',
    send_receipts=True
)

documents = loader.load()
```

## Configuration

```python
loader = IAIndexWebLoader(
    urls=urls,
    client_id='client-id',
    private_key=private_key,
    send_receipts=True,
    usage_purpose='training',
    usage_context='rag-retrieval',
    model_id='gpt-4'
)
```

## Examples

See [LangChain Examples](https://github.com/claimtec/iaindex/tree/main/examples/langchain)
