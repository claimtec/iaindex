"""
IAIndex SDK Quickstart Example

This example demonstrates the complete workflow for both publishers and AI clients.
"""

from aiindex import IAIndexPublisher, IAIndexClient, generate_keypair
from datetime import datetime, timezone


def publisher_example():
    """Example for content publishers"""
    print("=" * 60)
    print("PUBLISHER EXAMPLE")
    print("=" * 60)
    print()

    # 1. Generate keypair for publisher
    print("1. Generating ECDSA keypair for publisher...")
    pub_private_key, pub_public_key = generate_keypair()
    print(f"   Private key (first 20 chars): {pub_private_key[:20]}...")
    print(f"   Public key (first 20 chars): {pub_public_key[:20]}...")
    print()

    # 2. Initialize publisher
    print("2. Initializing publisher...")
    publisher = IAIndexPublisher(
        domain='example-publisher.com',
        private_key=pub_private_key,
        name='Example Publisher',
        contact='contact@example-publisher.com'
    )
    print(f"   Publisher domain: {publisher.domain}")
    print(f"   Publisher name: {publisher.name}")
    print()

    # 3. Add content entries
    print("3. Adding content entries...")
    entry1_id = publisher.add_entry({
        'url': 'https://example-publisher.com/article1',
        'title': 'Understanding AI Index',
        'author': 'Jane Smith',
        'published_date': '2025-01-15T10:00:00Z',
        'license': {'type': 'CC-BY-4.0'}
    })
    print(f"   Added entry 1: {entry1_id}")

    entry2_id = publisher.add_entry({
        'url': 'https://example-publisher.com/article2',
        'title': 'Best Practices for Content Attribution',
        'author': 'John Doe',
        'published_date': '2025-01-16T14:30:00Z',
        'license': {'type': 'CC-BY-NC-4.0'}
    })
    print(f"   Added entry 2: {entry2_id}")
    print()

    # 4. Generate signed index
    print("4. Generating signed index...")
    index = publisher.generate_index()
    print(f"   Index version: {index['version']}")
    print(f"   Number of entries: {len(index['entries'])}")
    print(f"   Generated at: {index['generated_at']}")
    print(f"   Signature (first 40 chars): {index['signature'][:40]}...")
    print()

    return publisher, pub_private_key, pub_public_key, index


def client_example():
    """Example for AI clients"""
    print("=" * 60)
    print("AI CLIENT EXAMPLE")
    print("=" * 60)
    print()

    # 1. Generate keypair for client
    print("1. Generating ECDSA keypair for AI client...")
    client_private_key, client_public_key = generate_keypair()
    print(f"   Private key (first 20 chars): {client_private_key[:20]}...")
    print(f"   Public key (first 20 chars): {client_public_key[:20]}...")
    print()

    # 2. Initialize client
    print("2. Initializing AI client...")
    client = IAIndexClient(
        client_id='example-ai-client-001',
        private_key=client_private_key,
        name='Example AI System',
        organization='Example AI Corp'
    )
    print(f"   Client ID: {client.client_id}")
    print(f"   Client name: {client.name}")
    print(f"   Organization: {client.organization}")
    print()

    # 3. Access content
    print("3. Accessing content...")
    url = 'https://example.com'
    print(f"   Fetching: {url}")
    content = client.access_content(url)
    print(f"   URL: {content['url']}")
    print(f"   Publisher domain: {content['publisher_domain']}")
    print(f"   Accessed at: {content['accessed_at']}")
    if content.get('title'):
        print(f"   Title: {content['title']}")
    print()

    # 4. Send usage receipt (this will attempt to contact the API)
    print("4. Sending usage receipt...")
    usage = {
        'purpose': 'training',
        'context': 'language-model-pretraining',
        'model': 'example-llm-v1',
        'tokens': 1500
    }
    print(f"   Purpose: {usage['purpose']}")
    print(f"   Context: {usage['context']}")

    try:
        success = client.send_receipt(content, usage)
        if success:
            print("   Receipt sent and verified successfully!")
        else:
            print("   Receipt sent but verification failed (publisher may not be verified)")
    except Exception as e:
        print(f"   Note: Receipt submission failed: {e}")
        print("   This is expected if the publisher is not registered with the API")
    print()

    return client, client_private_key, client_public_key


def signature_verification_example(publisher, client_private_key, client_public_key):
    """Example of signature verification"""
    print("=" * 60)
    print("SIGNATURE VERIFICATION EXAMPLE")
    print("=" * 60)
    print()

    # Create a mock receipt from the client
    print("1. Creating mock receipt from AI client...")
    from aiindex.crypto import CryptoUtils
    import uuid

    receipt_data = {
        "receipt_id": str(uuid.uuid4()),
        "publisher_domain": publisher.domain,
        "article_url": "https://example-publisher.com/article1",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    print(f"   Receipt ID: {receipt_data['receipt_id']}")
    print(f"   Article URL: {receipt_data['article_url']}")
    print()

    # Sign the receipt
    print("2. Signing receipt with client's private key...")
    signature = CryptoUtils.sign_data(receipt_data, client_private_key)
    print(f"   Signature (first 40 chars): {signature[:40]}...")
    print()

    # Complete receipt
    receipt = {
        **receipt_data,
        "signature": signature,
        "client_public_key": client_public_key
    }

    # Publisher verifies the receipt
    print("3. Publisher verifying receipt signature...")
    is_valid = publisher.verify_receipt(receipt)
    print(f"   Verification result: {'VALID' if is_valid else 'INVALID'}")
    print()

    # Test with tampered data
    print("4. Testing with tampered receipt data...")
    tampered_receipt = receipt.copy()
    tampered_receipt['article_url'] = 'https://different-url.com/article'
    is_valid_tampered = publisher.verify_receipt(tampered_receipt)
    print(f"   Verification result: {'VALID' if is_valid_tampered else 'INVALID (as expected)'}")
    print()


def main():
    """Run all examples"""
    print()
    print("=" * 60)
    print("IAIndex SDK - Complete Quickstart Example")
    print("=" * 60)
    print()
    print("This example demonstrates:")
    print("1. Publisher workflow: Generate keys, add entries, create index")
    print("2. AI Client workflow: Generate keys, access content, send receipts")
    print("3. Signature verification between publisher and client")
    print()

    try:
        # Publisher example
        publisher, pub_private, pub_public, index = publisher_example()

        # Client example
        client, client_private, client_public = client_example()

        # Signature verification
        signature_verification_example(publisher, client_private, client_public)

        print("=" * 60)
        print("EXAMPLE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Save your keys securely (use environment variables)")
        print("2. Register your publisher domain with the API")
        print("3. Integrate into your production systems")
        print("4. Monitor receipts via the API")
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
