---
sidebar_position: 2
title: Python SDK
---

# Python SDK

Official IAIndex SDK for Python applications.

## Installation

```bash
pip install iaindex-sdk
```

## Quick Start

```python
from iaindex import IAIndexPublisher, IAIndexClient
import os

# As a publisher
publisher = IAIndexPublisher(
    domain='yourdomain.com',
    private_key=os.environ['IAINDEX_PRIVATE_KEY'],
    name='Your Publication',
    contact='contact@yourdomain.com'
)

publisher.add_entry({
    'url': 'https://yourdomain.com/article',
    'title': 'Article Title',
    'author': 'Author Name',
    'published_date': '2025-01-15T10:00:00Z',
    'license': {'type': 'CC-BY-4.0'}
})

# As an AI client
client = IAIndexClient(
    client_id='your-client-id',
    private_key=os.environ['CLIENT_PRIVATE_KEY']
)

content = client.access_content('https://example.com/article')
client.send_receipt(content, {
    'purpose': 'training',
    'context': 'language-model-pretraining'
})
```

## API Reference

### IAIndexPublisher

```python
class IAIndexPublisher:
    def __init__(self, domain, private_key, name, contact):
        pass
    
    def add_entry(self, entry: dict) -> str:
        pass
    
    def generate_index(self) -> dict:
        pass
    
    def verify_receipt(self, receipt: dict) -> bool:
        pass
```

### IAIndexClient

```python
class IAIndexClient:
    def __init__(self, client_id, private_key, name, organization):
        pass
    
    def access_content(self, url: str) -> dict:
        pass
    
    def send_receipt(self, content: dict, usage: dict) -> bool:
        pass
```

## Examples

See [GitHub Examples](https://github.com/claimtec/iaindex/tree/main/examples/python)
