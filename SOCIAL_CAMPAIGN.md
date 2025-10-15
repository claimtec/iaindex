# AIIndex v1.1 Social Media Campaign

## Twitter/X Campaign (5 Tweets)

### Tweet 1: Launch Announcement
The web needs a consent layer for AI.

Today we're launching AIIndex v1.1 — the first open protocol enabling websites to control AI access with cryptographic proof.

Set policies. Get receipts. Build trust.

🧵 Thread on what this means 👇

[Link: aiindex.org]

#AIConsent #WebStandards

---

### Tweet 2: The Problem
2/ The problem: Publishers can't control how AI systems use their content.

No difference between training vs. search. No proof of access. No recourse when violated.

Meanwhile, legal disputes escalate: NYT, Getty, Reddit vs. AI platforms.

The web needs infrastructure for AI consent.

---

### Tweet 3: The Solution
3/ AIIndex solves this with 3 breakthroughs:

🛡️ Granular policies (block training, allow retrieval)
🔐 Cryptographic receipts (signed proof of every access)
🌐 Provenance tracking (C2PA + blockchain attestation)

Think robots.txt, but with enforcement and proof.

[Visual: Policy toggle screenshot]

---

### Tweet 4: Ecosystem + Availability
4/ Deploy in minutes:

✅ 8 CMS plugins (WordPress, Shopify, Webflow, Bubble, Wix, Squarespace, Framer, Ghost)
✅ 2 AI connectors (LangChain, LlamaIndex)
✅ Production APIs (FastAPI, Next.js dashboard)

Free tier available. Verified tier $25/mo.

Start: aiindex.org/beta

---

### Tweet 5: Call to Action
5/ AIIndex is open protocol + proprietary verification.

Core schema is MIT-licensed. Commercial extensions (dashboard, bot reputation, fraud detection) are SaaS.

We're defining a category, not competing in an existing one.

Join us: aiindex.org

[End thread]

---

## LinkedIn Posts (2)

### LinkedIn Post 1: Announcement (Professional Tone)

**Headline**: Introducing AIIndex v1.1 – The Consent Layer for AI Search

Today marks a significant milestone in web infrastructure. We're launching AIIndex v1.1, the first open protocol that enables websites to set granular policies for AI access while providing cryptographic proof of every interaction.

**The Challenge**: With the EU AI Act taking effect in 2025 and high-profile disputes between publishers and AI platforms (The New York Times, Getty Images, Reddit), the web urgently needs consent infrastructure designed for AI—not retrofitted from crawler-era solutions.

**Our Solution**:
• **Granular Consent Management**: Publishers set training and retrieval policies at protocol level
• **Cryptographic Receipts**: Every AI access generates signed, verifiable proof
• **Provenance Tracking**: C2PA integration + blockchain attestation for immutable audit trails

**Ecosystem Coverage**: We've launched with 8 CMS plugins (WordPress, Shopify, Webflow, Bubble.io, Wix, Squarespace, Framer, Ghost) and 2 AI framework connectors (LangChain, LlamaIndex). Installation takes minutes.

**Regulatory Alignment**: AIIndex is GDPR-compliant by design and EU AI Act ready. Publishers using our protocol have auditable proof of consent—a defense in litigation and a signal to regulators.

**Technical Innovation**: Unlike proprietary platforms, AIIndex is built as an open protocol. The core JSON schema is MIT-licensed. Commercial extensions (verification API, dashboard, bot reputation) are proprietary SaaS.

We're not just building a product—we're defining a category. AIIndex is to AI consent what HTTPS was to encryption: a foundational protocol that every website will eventually adopt.

Learn more: aiindex.org
Technical docs: docs.aiindex.org
Publisher beta: aiindex.org/beta

#AIConsent #WebInfrastructure #EUAIACT #GDPR #OpenProtocol #ContentProvenance

---

### LinkedIn Post 2: Technical Deep Dive (Developer Audience)

**Headline**: How AIIndex Works: Protocol + Proof + Policy (Technical Overview)

For developers building AI applications: AIIndex provides the consent layer you need for compliant data access. Here's how it works technically.

**Discovery**: AI clients check `/.well-known/aiindex-policy.json` before accessing content. The policy file specifies:
```json
{
  "policy": {
    "training": "block",
    "retrieval": "allow"
  },
  "receipts": {
    "require_signed": true,
    "webhook_url": "https://example.com/receipts"
  }
}
```

**Enforcement**: If the client violates policy (e.g., requests training when blocked), the server returns HTTP 403 with a signed denial receipt. The receipt includes:
- Denial reason
- Policy URL
- Retry instructions
- RSA-SHA256 signature

**Receipts**: Valid access generates a cryptographic receipt with content hash, timestamp, and client identity. Receipts are:
1. Signed by client (ES256/RS256)
2. POSTed to webhook URL
3. Logged in verification API
4. Aggregated to daily Merkle tree
5. Anchored to Bitcoin blockchain (OpenTimestamps)

**Integration**: Install via NPM/PyPI, or use framework connectors:
```bash
npm install @aiindex/sdk
pip install aiindex-sdk
```

LangChain and LlamaIndex have native support—policy discovery and receipt signing are automatic.

**Why It Matters**: With EU AI Act and GDPR requiring documented consent, AIIndex provides the infrastructure layer that makes compliance scalable. No more ad-hoc solutions or legal uncertainty.

Open source core (MIT), commercial verification SaaS. Full docs at docs.aiindex.org.

We're hiring engineers who care about web standards and trust infrastructure. DM me if interested.

#WebDevelopment #AIEngineering #OpenSource #Compliance #DeveloperTools

---

## Press-Linked Summary Paragraph (For PR Distribution)

**AIIndex Launches v1.1: The Consent Layer for AI Search**

AIIndex today announced the general availability of v1.1, the first open protocol enabling websites to control AI access with cryptographic proof. With the EU AI Act taking effect in 2025 and escalating publisher-AI disputes, AIIndex provides the trust infrastructure the web needs. The platform launches with 8 CMS plugins (WordPress, Shopify, Webflow, Bubble.io, Wix, Squarespace, Framer, Ghost), 2 AI connectors (LangChain, LlamaIndex), and production APIs. Publishers set granular training/retrieval policies; AI clients receive signed receipts; all interactions are logged and blockchain-anchored. The protocol is MIT-licensed with proprietary commercial extensions. Free tier available, verified tier $25/month. Learn more at aiindex.org or read the full press release at [link].

---

## Tweet Threads (Bonus: Technical + Compliance)

### Technical Thread (3 tweets)

**T1**: How AIIndex enforces consent at protocol level:

1. Publisher sets policy in ai-index.json
2. AI client fetches /.well-known/aiindex-policy.json
3. Client respects OR receives HTTP 403 with signed denial
4. Valid access = cryptographic receipt (ES256 signature)

It's technically enforced, not advisory.

**T2**: Why cryptographic receipts matter:

Each receipt includes:
- Content hash (SHA-256 of accessed data)
- Timestamp (ISO 8601, must be within 5min)
- Client identity + signature
- Intent (training vs. retrieval)

Receipts are immutable, auditable, and legally defensible.

**T3**: Provenance tracking works like this:

Daily receipts → Merkle tree → Bitcoin blockchain anchor (OpenTimestamps)

Result: Immutable proof that "Client X accessed Content Y at Time Z with Intent W"

Perfect for compliance (GDPR Art 30) and litigation defense.

[End thread]

---

### Compliance Thread (3 tweets)

**C1**: The EU AI Act (effective 2025) requires:
- Transparency in training data sources
- User notification of AI interactions
- Records of processing

AIIndex provides all three via cryptographic receipts and policy enforcement.

Compliance as infrastructure, not paperwork.

**C2**: GDPR requires documented consent (Art 6) and records of processing (Art 30).

AIIndex gives publishers:
✅ Explicit policy declarations
✅ Signed receipts as proof
✅ Blockchain-anchored audit trail

Turn regulatory burden into competitive advantage.

**C3**: US Copyright Office guidance (expected 2025) will likely require:
- Attribution for AI training
- Opt-in/opt-out mechanisms
- Consent documentation

AIIndex provides the infrastructure layer that makes these requirements scalable.

Get ahead of regulation: aiindex.org/beta

[End thread]

---

## Reddit/HN Post (Long-Form Community)

**Title**: [Launch] AIIndex v1.1 – Open protocol for AI consent with cryptographic receipts

**Body**:

Hey everyone, we just launched AIIndex v1.1, and I wanted to share it with the community that cares deeply about web standards and open protocols.

**What it is**: AIIndex is the first protocol that lets websites control how AI systems access their content. Think robots.txt, but with:
- Enforcement (HTTP 403 if policy violated)
- Differentiation (training vs. retrieval)
- Proof (cryptographic receipts for every access)

**Why it matters**: With EU AI Act taking effect next year and all the publisher-AI lawsuits (NYT, Getty, Reddit), the web needs consent infrastructure designed for AI—not retrofitted from 30-year-old crawler protocols.

**How it works**:
1. Publisher installs plugin (WordPress, Shopify, etc.) or uses SDK
2. Sets policy: "Block training, allow retrieval, require signed receipts"
3. AI client discovers policy via `/.well-known/aiindex-policy.json`
4. Client respects policy or gets HTTP 403 with signed denial receipt
5. Valid access generates receipt with content hash + timestamp
6. Receipt logged, aggregated to Merkle tree, anchored to Bitcoin

**Tech stack**: Protocol is MIT-licensed JSON schema. Verification API is FastAPI + Supabase + Redis. Dashboard is Next.js. We have SDKs for Node/Python and connectors for LangChain/LlamaIndex.

**Openness**: Core protocol is open source. Commercial extensions (dashboard, bot reputation, fraud detection) are SaaS. "Open core" model.

We're defining a category here, not competing with Prerender or Diffbot. This is infrastructure, not a product.

Full docs: docs.aiindex.org
Spec: aiindex.org/spec
GitHub: [coming soon]

Would love feedback from this community. We're engineers who care about standards, not marketers who care about hype.

[End post]

---

## Instagram/Visual Social (Carousel Concept)

**Slide 1**: AIIndex logo + "The Consent Layer for AI Search"
**Slide 2**: Problem visual (publisher vs. AI platform tug-of-war)
**Slide 3**: Solution visual (policy toggle UI screenshot)
**Slide 4**: Technical flow diagram (policy → enforcement → receipt → blockchain)
**Slide 5**: Ecosystem logos (WordPress, Shopify, LangChain, etc.)
**Slide 6**: CTA ("Start Free Beta – aiindex.org")

**Caption**: The web needs a consent layer for AI. We built it. Open protocol + cryptographic proof + policy enforcement. Deploy in minutes with plugins for WordPress, Shopify, and 6 more platforms. Link in bio. #AIConsent #WebStandards #OpenProtocol

---

## Social Media Calendar (First 2 Weeks)

**Day 0 (Launch)**:
- Tweet thread (5 tweets)
- LinkedIn post 1 (announcement)
- Reddit/HN post
- Instagram carousel

**Day 1**:
- Technical thread (3 tweets)
- Repost with developer quotes

**Day 2**:
- Compliance thread (3 tweets)
- LinkedIn post 2 (technical deep dive)

**Day 3-4**:
- User testimonials (if available)
- Plugin installation tutorials

**Day 5-7**:
- Case study snippets
- Dashboard screenshot highlights

**Week 2**:
- Partnerships announcements (WordPress, Shopify)
- Press coverage reposts
- Community engagement (reply to all mentions)

---

## Hashtag Strategy

**Primary**: #AIConsent #AIIndex #WebStandards
**Secondary**: #EUAIACT #GDPR #OpenProtocol #ContentProvenance
**Technical**: #WebDev #OpenSource #APIDesign #DevTools
**Trending**: #AI #MachineLearning #Copyright #PublisherRights

---

**Campaign Theme**: "Defining the Consent-Aware Web"
**Tone**: Confident, technical, visionary (like Cloudflare, Stripe, or OpenAI)
**Unified CTA**: aiindex.org/beta
