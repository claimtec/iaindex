"""
Example usage of AIIndex Python SDK
"""

from aiindex import AIIndexGenerator, SignatureManager, Validator

def main():
    # 1. Create a new AI-index document
    print("1. Creating AI-index document...")
    generator = AIIndexGenerator(
        publisher_id="example.com",
        domain="example.com"
    )

    # 2. Crawl website (you can replace with your URL)
    print("2. Crawling website...")
    # Uncomment to crawl a real website:
    # num_pages = generator.crawl("https://example.com", max_pages=5, max_depth=2)
    # print(f"   Crawled {num_pages} pages")

    # 3. Extract metadata
    print("3. Extracting metadata...")
    # Uncomment to extract from real website:
    # generator.extract_metadata("https://example.com")

    # 4. Add some entities manually
    from aiindex import Entity, EntityType
    generator.add_entity(Entity(
        type=EntityType.ORGANIZATION,
        name="Example Corporation",
        description="A sample organization",
        url="https://example.com"
    ))

    # 5. Add FAQ entries
    generator.add_faq(
        question="What is AIIndex?",
        answer="AIIndex is a protocol for AI-readable website metadata.",
        category="General"
    )

    # 6. Build document
    print("4. Building document...")
    doc = generator.build()
    print(f"   Document created with {len(generator.entities)} entities")

    # 7. Generate keypair and sign
    print("5. Generating keypair and signing...")
    manager = SignatureManager()
    private_key, public_key = manager.generate_keypair("ES256")

    # Sign the document
    doc_dict = generator.to_dict()
    signed_doc = manager.sign_document(doc_dict, private_key, "example-key-1", "ES256")
    print("   Document signed successfully")

    # 8. Validate
    print("6. Validating document...")
    validator = Validator()
    is_valid, errors = validator.validate_document(signed_doc)

    if is_valid:
        print("   ✓ Document is valid!")
    else:
        print("   ✗ Validation errors:")
        for error in errors:
            print(f"     - {error}")

    # 9. Verify signature
    print("7. Verifying signature...")
    is_verified = manager.verify_document(signed_doc, public_key)
    if is_verified:
        print("   ✓ Signature is valid!")
    else:
        print("   ✗ Signature verification failed")

    # 10. Save to file
    print("8. Saving to file...")
    import json
    with open("example-ai-index.json", "w") as f:
        json.dump(signed_doc, f, indent=2, default=str)
    print("   Saved to example-ai-index.json")

    print("\nDone! Check example-ai-index.json for the result.")

if __name__ == "__main__":
    main()
