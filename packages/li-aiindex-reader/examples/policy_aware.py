"""
AIIndex v1.1 Policy-Aware Usage Example (Python/LlamaIndex)

Demonstrates:
- Policy discovery and enforcement
- Handling 403 Forbidden responses
- Parsing denial receipts
- Retrying with different intents
- Respecting rate limits
- Automatic receipt signing
- Render fallback support
"""

import time
from aiindex_llama import AIIndexReader, AIIndexReceiptSigner, PolicyEnforcer
from aiindex_llama.types import (
    Purpose,
    PurposeType,
    Attribution,
    AttributionMethod,
    PolicyViolationError,
    RateLimitError,
)


def policy_aware_example():
    """Demonstrate AIIndex v1.1 policy-aware features."""
    print("=== AIIndex v1.1 Policy-Aware Example (Python) ===\n")

    # Example 1: Basic policy-aware reader
    print("1. Basic Policy-Aware Reader")
    try:
        reader = AIIndexReader(
            client_id="my-python-app",
            intent="retrieval",
            respect_policy_blocks=True,
            enable_render_fallback=True,
            timeout=10,
        )

        document = reader.fetch("example.com")
        print(f"✓ Successfully fetched document for {document.domain}")
        print(f"  Publisher: {document.publisher.name if document.publisher else 'N/A'}")
        print(f"  Pages: {len(document.pages) if document.pages else 0}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n")

    # Example 2: Handling Policy Violations
    print("2. Handling Policy Violations (403 Forbidden)")
    try:
        reader = AIIndexReader(
            client_id="training-bot",
            intent="training",
            respect_policy_blocks=True,
        )

        document = reader.fetch("restricted-site.com")
    except PolicyViolationError as e:
        print(f"✗ Policy Violation: {e}")
        print(f"  Action: {e.action}")
        print(f"  Intent: {e.intent}")
        if e.denial_receipt:
            print(f"  Reason: {e.denial_receipt.reason}")
            print(f"  Policy URL: {e.denial_receipt.policy_url}")
            if e.denial_receipt.retry_after:
                print(f"  Retry After: {e.denial_receipt.retry_after}s")
            if e.denial_receipt.alternative_endpoint:
                print(f"  Alternative: {e.denial_receipt.alternative_endpoint}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n")

    # Example 3: Retry with Different Intent
    print("3. Retry with Different Intent")
    test_domain = "flexible-policy-site.com"

    # First try with training
    try:
        reader = AIIndexReader(
            client_id="smart-bot",
            intent="training",
            respect_policy_blocks=True,
        )

        print('Attempting with "training" intent...')
        document = reader.fetch(test_domain)
        print("✓ Training access allowed")
    except PolicyViolationError as e:
        print(f"✗ Training blocked: {e}")
        print('  Retrying with "retrieval" intent...')

        # Retry with retrieval
        try:
            reader2 = AIIndexReader(
                client_id="smart-bot",
                intent="retrieval",
                respect_policy_blocks=True,
            )

            document = reader2.fetch(test_domain)
            print("✓ Retrieval access allowed")
        except Exception as retry_error:
            print(f"✗ Retrieval also blocked: {retry_error}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n")

    # Example 4: Rate Limiting
    print("4. Rate Limiting Example")
    try:
        reader = AIIndexReader(
            client_id="rate-limited-bot",
            respect_policy_blocks=True,
        )

        print("Making multiple requests...")
        for i in range(1, 6):
            try:
                document = reader.fetch("rate-limited-site.com")
                print(f"✓ Request {i} succeeded")
            except RateLimitError as e:
                print(f"⏱ Rate limited on request {i}")
                print(f"  Message: {e}")
                print(f"  Retry after: {e.retry_after}s")
                print(f"  Waiting...")
                time.sleep(e.retry_after)
                print(f"  Retrying...")
                document = reader.fetch("rate-limited-site.com")
                print(f"✓ Retry succeeded")
            except Exception as e:
                raise e
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n")

    # Example 5: Automatic Receipt Signing
    print("5. Automatic Receipt Signing")
    try:
        # Generate a keypair (in production, load from secure storage)
        private_pem, public_pem = AIIndexReceiptSigner.generate_keypair("ES256")
        print("✓ Generated keypair")

        reader = AIIndexReader(
            client_id="receipt-bot",
            intent="retrieval",
            respect_policy_blocks=True,
        )

        document = reader.fetch("receipt-required-site.com")
        print(f"✓ Fetched document")
        print(f"  Document: {document.domain}")

        # Manually create and post a receipt
        signer = AIIndexReceiptSigner(
            client_id="receipt-bot",
            private_key_pem=private_pem,
            key_id="key-001",
            intent="retrieval",
        )

        purpose = Purpose(
            type=PurposeType.RETRIEVAL,
            description="Loading content for RAG application",
            commercial=False,
        )

        attribution = Attribution(
            method=AttributionMethod.CITATION,
            citation_text=f"Data from {document.domain}",
        )

        receipt, posted = signer.create_and_post_receipt(
            document=document,
            url=f"https://{document.domain}/ai-index.json",
            purpose=purpose,
            attribution=attribution,
            intent="retrieval",
        )

        print(f"✓ Created receipt: {receipt.receipt_id}")
        print(f"  Posted to webhook: {posted}")
        print(f"  Signature algorithm: {receipt.signature.algorithm.value}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n")

    # Example 6: Render Fallback
    print("6. Render Fallback Support")
    try:
        reader = AIIndexReader(
            client_id="fallback-bot",
            enable_render_fallback=True,
            intent="retrieval",
        )

        # Try to fetch from a site without ai-index.json
        document = reader.fetch("no-aiindex-site.com")

        if document.metadata and document.metadata.get("source") == "render-fallback":
            print("✓ Used render fallback")
            print(f"  Domain: {document.domain}")
            if document.pages and len(document.pages) > 0:
                print(f"  Content length: {len(document.pages[0].summary or '')} chars")
            if document.metadata.get("rendered_at"):
                print(f"  Rendered at: {document.metadata['rendered_at']}")
        else:
            print("✓ Fetched from ai-index.json")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n")

    # Example 7: Direct Policy Enforcement
    print("7. Direct Policy Enforcement")
    try:
        with PolicyEnforcer(timeout=10) as enforcer:
            # Fetch policy
            policy = enforcer.fetch_policy("example.com")

            if policy:
                print("✓ Fetched policy")
                print(f"  Version: {policy.version}")
                print(f"  Training: {policy.policy.training or 'not specified'}")
                print(f"  Retrieval: {policy.policy.retrieval or 'not specified'}")
                print(f"  Require signed receipts: {policy.receipts.require_signed if policy.receipts else False}")

                # Evaluate for specific intent
                allowed, requires_attribution, _ = enforcer.evaluate_policy(
                    "example.com", "training"
                )
                print(f"  Training allowed: {allowed}")
                print(f"  Requires attribution: {requires_attribution}")

                # Check rate limits
                if policy.policy.rate_limit:
                    print("  Rate limits:")
                    if policy.policy.rate_limit.requests_per_minute:
                        print(f"    - {policy.policy.rate_limit.requests_per_minute} req/min")
                    if policy.policy.rate_limit.delay_ms:
                        print(f"    - {policy.policy.rate_limit.delay_ms}ms delay between requests")
            else:
                print("  No policy found (default allow)")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n")

    # Example 8: Context Manager Usage
    print("8. Context Manager Usage")
    try:
        with AIIndexReader(
            client_id="context-manager-app",
            intent="retrieval",
            respect_policy_blocks=True,
        ) as reader:
            document = reader.fetch("example.com")
            print(f"✓ Fetched document using context manager")
            print(f"  Domain: {document.domain}")
            print(f"  Version: {document.version}")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    policy_aware_example()
