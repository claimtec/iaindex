#!/usr/bin/env python3
"""
IAIndex SDK - Complete Usage Example

This example demonstrates the full workflow for both publishers and AI clients
using the IAIndex Python SDK.

Prerequisites:
- Install the SDK: pip install -e .
- Or use the verification script to test without full installation
"""

def example_1_generate_keys():
    """Example 1: Generate cryptographic keys"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Generate Cryptographic Keys")
    print("=" * 70)

    from aiindex.crypto import generate_keypair

    # Generate a keypair for a publisher
    pub_private, pub_public = generate_keypair()
    print("\nPublisher Keys Generated:")
    print(f"  Private Key (save securely!): {pub_private[:30]}...")
    print(f"  Public Key: {pub_public[:30]}...")

    # Generate a keypair for an AI client
    client_private, client_public = generate_keypair()
    print("\nAI Client Keys Generated:")
    print(f"  Private Key (save securely!): {client_private[:30]}...")
    print(f"  Public Key: {client_public[:30]}...")

    return {
        'publisher': {'private': pub_private, 'public': pub_public},
        'client': {'private': client_private, 'public': client_public}
    }


def example_2_publisher_setup(keys):
    """Example 2: Set up a publisher"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Publisher Setup")
    print("=" * 70)

    from aiindex.publisher import IAIndexPublisher

    # Create publisher instance
    publisher = IAIndexPublisher(
        domain='example-news.com',
        private_key=keys['publisher']['private'],
        name='Example News Organization',
        contact='api@example-news.com'
    )

    print(f"\nPublisher Created:")
    print(f"  Domain: {publisher.domain}")
    print(f"  Name: {publisher.name}")
    print(f"  Contact: {publisher.contact}")

    # Note: In production, you would call publisher.initialize() here
    # to register with the IAIndex API and start domain verification

    return publisher


def example_3_add_content(publisher):
    """Example 3: Add content entries"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Add Content Entries")
    print("=" * 70)

    # Add multiple articles
    articles = [
        {
            'url': 'https://example-news.com/articles/ai-breakthrough',
            'title': 'Major AI Breakthrough Announced',
            'author': 'Jane Smith',
            'published_date': '2025-01-15T10:00:00Z',
            'license': {'type': 'CC-BY-4.0', 'url': 'https://creativecommons.org/licenses/by/4.0/'}
        },
        {
            'url': 'https://example-news.com/articles/tech-trends',
            'title': '2025 Technology Trends',
            'author': 'John Doe',
            'published_date': '2025-01-16T14:30:00Z',
            'license': {'type': 'CC-BY-NC-4.0'}
        },
        {
            'url': 'https://example-news.com/articles/climate-update',
            'title': 'Climate Action Update',
            'author': 'Alice Johnson',
            'published_date': '2025-01-17T09:15:00Z',
            'license': {'type': 'CC-BY-4.0'}
        }
    ]

    print(f"\nAdding {len(articles)} articles to index...")
    entry_ids = []
    for article in articles:
        entry_id = publisher.add_entry(article)
        entry_ids.append(entry_id)
        print(f"  ✓ Added: {article['title']} (ID: {entry_id[:12]}...)")

    print(f"\nTotal entries in index: {len(publisher.entries)}")
    return entry_ids


def example_4_generate_index(publisher):
    """Example 4: Generate signed index"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Generate Signed Index")
    print("=" * 70)

    import json

    # Generate the index
    index = publisher.generate_index()

    print("\nIndex Generated:")
    print(f"  Version: {index['version']}")
    print(f"  Publisher: {index['publisher']['name']}")
    print(f"  Entries: {len(index['entries'])}")
    print(f"  Generated: {index['generated_at']}")
    print(f"  Signature: {index['signature'][:40]}...")

    # Save to file
    index_json = json.dumps(index, indent=2, default=str)
    print(f"\nIndex size: {len(index_json)} bytes")

    # In production, you would save this to:
    # - Your website at https://yourdomain.com/ai-index.json
    # - Or reference it via <link rel="aiindex" href="/ai-index.json">

    return index


def example_5_client_setup(keys):
    """Example 5: Set up an AI client"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: AI Client Setup")
    print("=" * 70)

    from aiindex.client import IAIndexClient

    # Create client instance
    client = IAIndexClient(
        client_id='example-ai-v1',
        private_key=keys['client']['private'],
        name='Example AI System',
        organization='Example AI Corp'
    )

    print(f"\nAI Client Created:")
    print(f"  Client ID: {client.client_id}")
    print(f"  Name: {client.name}")
    print(f"  Organization: {client.organization}")
    print(f"  Public Key: {client.public_key[:30]}...")

    return client


def example_6_access_content(client):
    """Example 6: Access content"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Access Content")
    print("=" * 70)

    # Simulate accessing content
    url = 'https://example-news.com/articles/ai-breakthrough'
    print(f"\nAccessing: {url}")

    content = client.access_content(url)

    print(f"\nContent Metadata Retrieved:")
    print(f"  URL: {content['url']}")
    print(f"  Publisher Domain: {content['publisher_domain']}")
    print(f"  Accessed At: {content['accessed_at']}")
    print(f"  Client ID: {content['client_id']}")

    return content


def example_7_send_receipt(client, content):
    """Example 7: Send usage receipt"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Send Usage Receipt")
    print("=" * 70)

    # Define usage information
    usage = {
        'purpose': 'training',
        'context': 'language-model-pretraining',
        'model': 'example-llm-v2',
        'tokens': 1500,
        'dataset': 'web-crawl-2025'
    }

    print("\nUsage Information:")
    for key, value in usage.items():
        print(f"  {key}: {value}")

    # Note: This will attempt to send to the live API
    # In production, ensure your publisher is verified first
    print("\nAttempting to send receipt...")
    print("(Note: This requires publisher domain verification in the live API)")

    try:
        success = client.send_receipt(content, usage)
        if success:
            print("  ✓ Receipt sent and verified successfully!")
        else:
            print("  ! Receipt sent but verification failed")
            print("    (Publisher may not be verified in the API)")
    except Exception as e:
        print(f"  ! Receipt submission failed: {str(e)[:60]}...")
        print("    This is expected if publisher is not registered")


def example_8_verify_receipt(publisher, client):
    """Example 8: Publisher verifies receipt"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Publisher Verifies Receipt")
    print("=" * 70)

    from aiindex.crypto import CryptoUtils
    from datetime import datetime, timezone
    import uuid

    # Create a receipt
    receipt_data = {
        "receipt_id": str(uuid.uuid4()),
        "publisher_domain": publisher.domain,
        "article_url": "https://example-news.com/articles/ai-breakthrough",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    print("\nCreating receipt...")
    print(f"  Receipt ID: {receipt_data['receipt_id']}")
    print(f"  Article: {receipt_data['article_url']}")

    # Client signs the receipt
    signature = CryptoUtils.sign_data(receipt_data, client._IAIndexClient__private_key)
    receipt = {
        **receipt_data,
        "signature": signature,
        "client_public_key": client.public_key
    }

    print("\nPublisher verifying receipt...")
    is_valid = publisher.verify_receipt(receipt)

    if is_valid:
        print("  ✓ Receipt is VALID")
        print("  Publisher can now:")
        print("    - Record the usage")
        print("    - Track attribution")
        print("    - Monitor AI access")
    else:
        print("  ✗ Receipt is INVALID")


def example_9_complete_workflow():
    """Example 9: Complete end-to-end workflow"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Complete End-to-End Workflow")
    print("=" * 70)

    from aiindex.crypto import generate_keypair, CryptoUtils
    from aiindex.publisher import IAIndexPublisher
    from aiindex.client import IAIndexClient
    from datetime import datetime, timezone
    import uuid

    print("\n1. Publisher generates keys and creates profile")
    pub_private, pub_public = generate_keypair()
    publisher = IAIndexPublisher(
        domain='complete-example.com',
        private_key=pub_private,
        name='Complete Example Publisher',
        contact='contact@complete-example.com'
    )
    print(f"   ✓ Publisher: {publisher.domain}")

    print("\n2. Publisher adds content")
    for i in range(3):
        publisher.add_entry({
            'url': f'https://complete-example.com/article-{i+1}',
            'title': f'Article {i+1}',
            'author': f'Author {i+1}',
            'published_date': datetime.now(timezone.utc).isoformat()
        })
    print(f"   ✓ Added {len(publisher.entries)} articles")

    print("\n3. Publisher generates signed index")
    index = publisher.generate_index()
    print(f"   ✓ Index generated with signature")

    print("\n4. AI client generates keys and creates profile")
    client_private, client_public = generate_keypair()
    client = IAIndexClient(
        client_id='complete-example-ai',
        private_key=client_private,
        name='Complete Example AI'
    )
    print(f"   ✓ Client: {client.client_id}")

    print("\n5. Client accesses content")
    content = client.access_content('https://complete-example.com/article-1')
    print(f"   ✓ Accessed: {content['url']}")

    print("\n6. Client creates and signs receipt")
    receipt_data = {
        "receipt_id": str(uuid.uuid4()),
        "publisher_domain": publisher.domain,
        "article_url": content['url'],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    signature = CryptoUtils.sign_data(receipt_data, client_private)
    receipt = {
        **receipt_data,
        "signature": signature,
        "client_public_key": client_public
    }
    print(f"   ✓ Receipt created: {receipt['receipt_id'][:20]}...")

    print("\n7. Publisher verifies receipt")
    is_valid = publisher.verify_receipt(receipt)
    print(f"   ✓ Receipt verified: {is_valid}")

    print("\n8. Complete workflow successful!")
    print("   Publisher can now:")
    print("     • Track AI usage")
    print("     • Require attribution")
    print("     • Monitor access patterns")
    print("     • Ensure compliance")


def main():
    """Main function to run all examples"""
    print("\n" + "=" * 70)
    print("IAIndex Python SDK - Complete Usage Examples")
    print("=" * 70)
    print("\nThese examples demonstrate:")
    print("  • Cryptographic key generation")
    print("  • Publisher setup and content management")
    print("  • Index generation and signing")
    print("  • AI client setup")
    print("  • Content access and receipt generation")
    print("  • Receipt verification")
    print("  • Complete end-to-end workflow")

    try:
        # Run examples sequentially
        keys = example_1_generate_keys()
        publisher = example_2_publisher_setup(keys)
        example_3_add_content(publisher)
        index = example_4_generate_index(publisher)
        client = example_5_client_setup(keys)
        content = example_6_access_content(client)
        example_7_send_receipt(client, content)
        example_8_verify_receipt(publisher, client)
        example_9_complete_workflow()

        # Final summary
        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nNext Steps:")
        print("  1. Register your domain with the IAIndex API")
        print("  2. Complete domain verification")
        print("  3. Deploy ai-index.json to your website")
        print("  4. Start tracking AI usage with receipts")
        print("\nAPI Documentation:")
        print("  https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io/docs")
        print()

    except Exception as e:
        print(f"\n✗ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Ensure we can import the modules
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))

    main()
