# PRESS RELEASE

**FOR IMMEDIATE RELEASE**

## AIIndex v1.1 Launches – The Consent Layer for AI Search

**Open Protocol Enables Websites to Control AI Access with Cryptographic Proof, Launches with Support for WordPress, Shopify, LangChain, and Seven More Platforms**

**October 13, 2025** — AIIndex today announced the general availability of v1.1, the first open protocol that enables websites to set granular policies for AI access while providing cryptographic proof of every interaction. With the EU AI Act taking effect in 2025 and escalating disputes between publishers and AI platforms, AIIndex provides the trust infrastructure the web needs to navigate the AI era.

### The Problem: A Web Without AI Consent

Today's web infrastructure was built for human browsers, not AI systems. Publishers have no standardized way to control whether their content is used for model training versus search retrieval, no proof of AI access, and no recourse when policies are violated. Meanwhile, AI developers face legal uncertainty and ad-hoc solutions for attribution and compliance.

Recent high-profile disputes—The New York Times vs. OpenAI, Getty Images vs. Stability AI, and Reddit's API restrictions—highlight the urgent need for consent infrastructure. Yet existing solutions like robots.txt lack AI-specific controls, while proprietary platforms force publishers into black-box agreements.

"The web needs a consent layer for AI, just as it needed robots.txt for crawlers in 1994," said the AIIndex team. "But this time, we need cryptographic proof, not just suggestions."

### The Solution: Protocol + Proof + Policy

AIIndex v1.1 introduces three breakthrough capabilities:

**Granular Consent Management**: Publishers set training and retrieval policies at the protocol level via a simple JSON file (`ai-index.json`) or well-known endpoint (`/.well-known/aiindex-policy.json`). A publisher can block training while allowing search, or require signed receipts for all access—choices that are technically enforced, not advisory.

**Cryptographic Receipts**: Every AI access generates a signed, verifiable receipt that includes content hash, timestamp, and client identity. These receipts are logged, aggregated into daily Merkle trees, and anchored to Bitcoin blockchain via OpenTimestamps—creating an immutable audit trail.

**Provenance Tracking**: AIIndex integrates with C2PA Content Credentials (the standard backed by Adobe, Microsoft, and the BBC) and provides automatic bot reputation scoring. Bad actors are blocked after five violations; verified clients like OpenAI and Anthropic receive priority access.

### Regulatory Timing: Compliance as Advantage

AIIndex's launch coincides with major regulatory shifts. The EU AI Act (effective 2025) requires transparency in AI training data and user notification of AI interactions. GDPR Article 6 and 7 require documented consent for data processing. The US Copyright Office is developing guidance on AI training and fair use.

"Regulatory compliance is typically a cost center," said the team. "AIIndex turns it into a competitive advantage. Publishers using our protocol have auditable proof of consent—a defense in litigation and a signal to regulators."

AIIndex is designed to be GDPR-compliant by default, with no raw IP storage, hash-based anonymization, and configurable retention policies. The platform's cryptographic receipts provide the "records of processing" required under GDPR Article 30.

### Technical Innovation: Open Core, Commercial Extensions

Unlike proprietary platforms, AIIndex is built as an open protocol. The core JSON schema, receipt format, and policy discovery mechanism are MIT-licensed and published at [aiindex.org/spec](https://aiindex.org/spec). This enables any developer to implement AIIndex support without licensing fees.

Commercial extensions—including the verification API, dashboard analytics, bot reputation system, and enterprise features—are proprietary SaaS offerings. This "open core" model enables ecosystem growth while protecting revenue streams.

The v1.1 release includes:
- **Enhanced Protocol Schema** with training/retrieval differentiation, C2PA provenance, and embeddings manifest
- **Policy Enforcement Middleware** that returns HTTP 403 with signed denial receipts when policies are violated
- **Eight CMS Plugins**: WordPress, Shopify, Webflow, Bubble.io, Wix, Squarespace, Framer, Ghost
- **Two AI Framework Connectors**: LangChain and LlamaIndex with automatic policy discovery and receipt signing
- **Render Fallback**: Edge rendering via Cloudflare for JavaScript-heavy sites
- **Semantic Search**: Optional embeddings layer with vector storage (Pinecone/Weaviate)
- **Bot Reputation System**: Automatic blocking of bad actors, allowlist for verified clients

### Early Adoption and Partnerships

AIIndex has received three letters of intent from enterprise publishers, including a Fortune 500 media company, a SaaS documentation platform, and a legal publisher. The platform is in discussions with WordPress.com for automated plugin distribution to 455 million sites and has submitted to the Shopify App Store partner program.

"We're not just building a product—we're defining a category," the team noted. "AIIndex is to AI consent what HTTPS was to encryption: a foundational protocol that every website will eventually adopt."

### Intellectual Property and Defensibility

AIIndex has filed a provisional patent on "Method and System for Cryptographic Verification of AI Content Access with Intent-Based Policy Enforcement." The patent covers five key innovations: intent differentiation at protocol level, cryptographic receipt generation with content hash binding, policy evaluation with signed denial receipts, Merkle tree attestation with external timestamping, and bot reputation scoring with automatic enforcement.

The company's defensibility comes from first-mover advantage (no existing patent on AI consent protocols), network effects (more publishers drive more AI adoption drives more publishers), and deep integration with existing infrastructure (WordPress commands 43% of web market share).

### Availability and Pricing

AIIndex v1.1 is available immediately at [aiindex.org](https://aiindex.org). The platform offers three tiers:

- **Free**: Basic analytics, 90-day receipt retention
- **Verified** ($25/month): Verification badge, extended retention, render fallback
- **Enterprise** ($500-$5,000/month): Custom policies, mTLS, SLA, white-label

SDKs are available on NPM (`@aiindex/sdk`) and PyPI (`aiindex-sdk`). Plugins can be installed from WordPress.org, Shopify App Store, and platform-specific marketplaces.

### About AIIndex

AIIndex is the open protocol for AI-readable web data with cryptographic verification. The platform enables websites to control how AI systems access, attribute, and train on their content while providing verifiable proof of every interaction. AIIndex is backed by provisional patent protection and supported by a growing ecosystem of publishers, AI developers, and infrastructure partners.

### Media Contact

Press inquiries: [press@aiindex.org](mailto:press@aiindex.org)
Press kit: [aiindex.org/press](https://aiindex.org/press)
Demo environment: [demo.aiindex.org](https://demo.aiindex.org)

### Additional Resources

- Technical documentation: [docs.aiindex.org](https://docs.aiindex.org)
- Developer portal: [aiindex.org/developers](https://aiindex.org/developers)
- Publisher beta program: [aiindex.org/beta](https://aiindex.org/beta)
- Executive brief: [aiindex.org/brief](https://aiindex.org/brief)

**###**

*AIIndex v1.1 – Deployed. Verified. Trusted.*
