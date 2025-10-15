#!/usr/bin/env python3
"""
Generate Test Receipts for AIIndex

This script generates 100 fake receipt JSON files for testing purposes.
Receipts are distributed across different publishers, clients, and time periods.

Usage:
    python generate-test-receipts.py [--output-dir ./receipts] [--count 100]
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import hashlib

# Sample publishers
PUBLISHERS = [
    {"id": "example-blog.com", "domain": "example-blog.com", "name": "Tech Insights Blog"},
    {"id": "techgear-shop.com", "domain": "techgear-shop.com", "name": "TechGear Shop"},
    {"id": "cloudforge-docs.dev", "domain": "cloudforge-docs.dev", "name": "CloudForge Documentation"},
    {"id": "technews-daily.com", "domain": "technews-daily.com", "name": "TechNews Daily"},
    {"id": "learncode.io", "domain": "learncode.io", "name": "LearnCode"},
    {"id": "apiforge.dev", "domain": "apiforge.dev", "name": "APIForge"},
    {"id": "taskmaster.app", "domain": "taskmaster.app", "name": "TaskMaster"},
    {"id": "ai-research-lab.org", "domain": "ai-research-lab.org", "name": "AI Research Lab"},
    {"id": "digitalmedia-hub.com", "domain": "digitalmedia-hub.com", "name": "Digital Media Hub"},
    {"id": "opensource-toolkit.dev", "domain": "opensource-toolkit.dev", "name": "OpenSource Toolkit"}
]

# Sample AI clients
CLIENTS = [
    {"id": "openai-gpt4", "name": "GPT-4", "version": "2024-05", "organization": "OpenAI"},
    {"id": "anthropic-claude", "name": "Claude", "version": "2024-02", "organization": "Anthropic"},
    {"id": "google-gemini", "name": "Gemini Pro", "version": "1.5", "organization": "Google"},
    {"id": "meta-llama", "name": "Llama 3", "version": "3.0", "organization": "Meta"},
    {"id": "perplexity-ai", "name": "Perplexity AI", "version": "1.0", "organization": "Perplexity"},
]

# Purpose types
PURPOSE_TYPES = [
    {"type": "inference", "desc": "Answering user query in real-time", "commercial_likely": 0.7},
    {"type": "training", "desc": "Training or fine-tuning language model", "commercial_likely": 0.9},
    {"type": "research", "desc": "Academic or commercial research", "commercial_likely": 0.4},
    {"type": "indexing", "desc": "Building search index or knowledge base", "commercial_likely": 0.6},
]

# Sample page URLs by publisher type
PAGE_URLS = {
    "blog": [
        "/posts/introduction-to-ai-agents",
        "/posts/langchain-best-practices",
        "/posts/prompt-engineering-guide",
        "/posts/rag-systems-explained",
        "/posts/web-scraping-ethics"
    ],
    "ecommerce": [
        "/products/mechanical-keyboard-pro",
        "/products/wireless-mouse-elite",
        "/products/usb-c-hub-pro",
        "/products/laptop-stand-aluminum",
        "/products/webcam-4k-pro"
    ],
    "docs": [
        "/docs/getting-started",
        "/docs/installation",
        "/docs/api-reference",
        "/docs/deploying-applications",
        "/docs/cli-reference"
    ],
    "generic": [
        "/about",
        "/pricing",
        "/features",
        "/blog",
        "/contact"
    ]
}

def generate_content_hash():
    """Generate a random SHA-256 hash"""
    random_data = str(random.random()).encode()
    return hashlib.sha256(random_data).hexdigest()

def generate_signature():
    """Generate a fake signature (base64-like string)"""
    random_bytes = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/', k=88))
    return random_bytes + '=='

def get_publisher_type(domain):
    """Determine publisher type from domain"""
    if 'blog' in domain or 'news' in domain:
        return 'blog'
    elif 'shop' in domain:
        return 'ecommerce'
    elif 'docs' in domain:
        return 'docs'
    else:
        return 'generic'

def generate_receipt(index, start_date):
    """Generate a single receipt"""
    # Select random publisher and client
    publisher = random.choice(PUBLISHERS)
    client = random.choice(CLIENTS)
    purpose = random.choice(PURPOSE_TYPES)

    # Generate timestamp (distributed over past 30 days)
    days_ago = random.uniform(0, 30)
    timestamp = start_date - timedelta(days=days_ago)

    # Determine if signature is valid (90% valid, 10% invalid for testing)
    signature_valid = random.random() > 0.1

    # Commercial use probability based on purpose type
    commercial = random.random() < purpose["commercial_likely"]

    # Select appropriate page URLs
    publisher_type = get_publisher_type(publisher["domain"])
    page_list = PAGE_URLS.get(publisher_type, PAGE_URLS["generic"])
    pages_accessed = random.sample(page_list, k=random.randint(1, 3))
    pages_accessed = [f"https://{publisher['domain']}{page}" for page in pages_accessed]

    # Build receipt
    receipt = {
        "version": "1.0",
        "receipt_id": str(uuid.uuid4()),
        "publisher_id": publisher["id"],
        "publisher_domain": publisher["domain"],
        "client_id": client["id"],
        "client_name": client["name"],
        "client_version": client["version"],
        "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "access": {
            "url": f"https://{publisher['domain']}/.well-known/ai-index.json",
            "method": "GET",
            "status_code": 200,
            "content_hash": generate_content_hash(),
            "pages_accessed": pages_accessed
        },
        "purpose": {
            "type": purpose["type"],
            "description": purpose["desc"],
            "commercial": commercial
        },
        "attribution": {
            "method": random.choice(["citation", "link", "inline"]),
            "citation_text": f"Information from {publisher['name']}",
            "url": f"https://{publisher['domain']}"
        },
        "signature": {
            "algorithm": "ES256",
            "kid": f"{publisher['id']}-2025",
            "signature": generate_signature(),
            "payload_hash": generate_content_hash()
        },
        "metadata": {
            "user_agent": f"AIIndexSDK/1.0 ({client['organization']})",
            "sdk_version": "1.0.0",
            "request_id": f"req-{uuid.uuid4().hex[:16]}"
        }
    }

    # Add validity marker for testing (not part of actual receipt spec)
    receipt["_test_metadata"] = {
        "index": index,
        "signature_valid": signature_valid,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    return receipt

def generate_receipts(count=100, output_dir="./receipts"):
    """Generate multiple receipts and save to files"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Generating {count} test receipts...")
    print(f"Output directory: {output_path.absolute()}")

    start_date = datetime.utcnow()
    receipts = []

    # Generate receipts
    for i in range(count):
        receipt = generate_receipt(i + 1, start_date)
        receipts.append(receipt)

        # Save individual receipt file
        filename = f"receipt-{i+1:03d}-{receipt['receipt_id'][:8]}.json"
        filepath = output_path / filename

        with open(filepath, 'w') as f:
            json.dump(receipt, f, indent=2)

        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{count} receipts...")

    # Save all receipts in a single file
    all_receipts_file = output_path / "all-receipts.json"
    with open(all_receipts_file, 'w') as f:
        json.dump(receipts, f, indent=2)

    # Generate summary statistics
    stats = generate_statistics(receipts)
    stats_file = output_path / "statistics.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\n✓ Generated {count} receipts")
    print(f"  Individual files: {count}")
    print(f"  Combined file: all-receipts.json")
    print(f"  Statistics: statistics.json")
    print(f"\nStatistics Summary:")
    print(f"  Valid signatures: {stats['valid_signatures']}/{count} ({stats['valid_signature_rate']:.1%})")
    print(f"  Commercial use: {stats['commercial_uses']}/{count} ({stats['commercial_use_rate']:.1%})")
    print(f"  Unique publishers: {stats['unique_publishers']}")
    print(f"  Unique clients: {stats['unique_clients']}")
    print(f"  Purpose breakdown: {json.dumps(stats['purpose_breakdown'], indent=4)}")

def generate_statistics(receipts):
    """Generate statistics from receipts"""
    stats = {
        "total_receipts": len(receipts),
        "valid_signatures": sum(1 for r in receipts if r["_test_metadata"]["signature_valid"]),
        "commercial_uses": sum(1 for r in receipts if r["purpose"]["commercial"]),
        "unique_publishers": len(set(r["publisher_id"] for r in receipts)),
        "unique_clients": len(set(r["client_id"] for r in receipts)),
        "purpose_breakdown": {},
        "client_breakdown": {},
        "publisher_breakdown": {}
    }

    # Calculate rates
    stats["valid_signature_rate"] = stats["valid_signatures"] / stats["total_receipts"]
    stats["commercial_use_rate"] = stats["commercial_uses"] / stats["total_receipts"]

    # Purpose breakdown
    for receipt in receipts:
        purpose = receipt["purpose"]["type"]
        stats["purpose_breakdown"][purpose] = stats["purpose_breakdown"].get(purpose, 0) + 1

    # Client breakdown
    for receipt in receipts:
        client = receipt["client_name"]
        stats["client_breakdown"][client] = stats["client_breakdown"].get(client, 0) + 1

    # Publisher breakdown
    for receipt in receipts:
        publisher = receipt["publisher_id"]
        stats["publisher_breakdown"][publisher] = stats["publisher_breakdown"].get(publisher, 0) + 1

    return stats

def main():
    parser = argparse.ArgumentParser(description="Generate test AIIndex receipts")
    parser.add_argument(
        "--output-dir",
        default="./receipts",
        help="Output directory for receipt files (default: ./receipts)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of receipts to generate (default: 100)"
    )

    args = parser.parse_args()

    generate_receipts(count=args.count, output_dir=args.output_dir)

if __name__ == "__main__":
    main()
