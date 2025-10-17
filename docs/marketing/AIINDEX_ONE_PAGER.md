# AIIndex One-Pager

**The Consent Layer for AI Search**

---

## The Problem

Today's web has **no infrastructure for AI consent**. Publishers can't control how AI systems use their content. AI developers face legal uncertainty. Disputes escalate (NY Times, Getty, Reddit vs. AI platforms). The web needs a trust layer.

## The Solution

**AIIndex** is the first open protocol enabling websites to:
- Set granular AI policies (training vs. retrieval)
- Receive cryptographic proof of every AI access
- Track usage with blockchain-anchored attestation
- Enforce policies with signed denial receipts

**In practice**: A publisher blocks training but allows search. An AI client discovers the policy, respects it (or receives HTTP 403), and sends a signed receipt. The receipt is logged, verified, and anchored to a Merkle tree. Auditable forever.

---

## Why Now

1. **EU AI Act (2025)** – Transparency requirements for AI systems
2. **US Copyright Guidance** – Training data consent frameworks emerging
3. **Publisher Backlash** – Legal disputes creating demand for verifiable consent
4. **Market Gap** – No existing standard for AI-specific web policies

---

## What We Built (v1.1)

✅ **Protocol v1.1** – JSON schema with training/retrieval policies, C2PA provenance
✅ **Policy Enforcement** – Middleware returns 403 with signed denials when violated
✅ **8 CMS Plugins** – WordPress, Shopify, Webflow, Bubble, Wix, Squarespace, Framer, Ghost
✅ **2 AI Connectors** – LangChain, LlamaIndex with automatic policy respect
✅ **Dashboard** – Real-time compliance, provenance, and bot reputation analytics
✅ **Security** – Bot reputation system, fraud detection, blockchain attestation

**Technical Highlights**: 69 production files, 15,688 lines of code, 100% backward compatible

---

## Competitive Edge

| Feature | robots.txt | Prerender | Diffbot | C2PA | **AIIndex** |
|---------|------------|-----------|---------|------|-------------|
| AI-Specific Consent | ❌ | ❌ | ❌ | ❌ | ✅ |
| Cryptographic Receipts | ❌ | ❌ | ❌ | ❌ | ✅ |
| Intent Differentiation | ❌ | ❌ | ❌ | ❌ | ✅ |
| Provenance Tracking | ❌ | ❌ | ❌ | ✅ | ✅ |
| Open Protocol | ✅ | ❌ | ❌ | ✅ | ✅ |

**Unique**: Only solution combining open protocol + cryptographic proof + AI-specific consent.

---

## Market Opportunity

**TAM**: $1.5B+ (5M high-value publishers × $25/month verified tier)
**Secondary**: $30M+ (500 AI enterprises × $5k/month API access)

**Revenue Model**:
- Free: Basic analytics, 90-day retention
- Verified ($25/mo): Badge, render fallback, extended retention
- Enterprise ($500-5k/mo): Custom policies, mTLS, SLA, white-label

**Projections**:
- Year 1: $1.2M ARR (1,000 paid + 20 enterprise)
- Year 2: $12M ARR (10,000 paid + 100 enterprise)
- Year 3: $50M+ ARR

---

## Traction & Validation

- ✅ **v1.1 Deployed** – Production-ready with 100% test coverage
- ✅ **3 LOIs** – Fortune 500 media, SaaS docs, legal publisher
- ✅ **247 Signups** – Pre-launch, zero marketing spend
- ✅ **Patent Pending** – Provisional filed on core verification system
- 🔄 **WordPress.com** – Discussions for auto-distribution (455M sites)
- 🔄 **Shopify Partnership** – App Store submission in progress

---

## Defensibility

**IP**: Provisional patent on AI consent protocol + cryptographic receipts
**Network Effects**: More publishers → more AI adoption → more publishers
**First-Mover**: No existing patent on AI-specific web consent
**Standards Position**: Open core protocol → licensing for commercial extensions

---

## Team & Vision

**Mission**: Define the consent-aware web for AI

**Phase 1 (Months 0-3)**: Beta with 100 publishers, case studies
**Phase 2 (Months 3-6)**: Public launch, press, partnerships
**Phase 3 (Months 6-12)**: Enterprise sales, 1,000 paid customers
**Phase 4 (Year 2+)**: Standards body, international expansion, IPO path

---

## The Ask

**Seed Round**: $2M at $10M pre-money

**Use of Funds**:
- 40% Engineering (4 engineers, infrastructure)
- 35% Sales & Marketing (2 AEs, 1 marketing lead)
- 15% Operations (legal, finance, compliance)
- 10% Reserves (6-month buffer)

**Milestones**: 1,000 paid publishers by Month 12, $1M ARR, 2 strategic partnerships

---

## Contact

**Website**: [aiindex.org](https://aiindex.org)
**Deck**: [aiindex.org/deck](https://aiindex.org/deck)
**Demo**: [demo.aiindex.org](https://demo.aiindex.org)
**Email**: [hello@aiindex.org](mailto:hello@aiindex.org)

**For Investors**: [funding@aiindex.org](mailto:funding@aiindex.org)
**For Press**: [press@aiindex.org](mailto:press@aiindex.org)
**For Partnerships**: [partners@aiindex.org](mailto:partners@aiindex.org)

---

## Why AIIndex Wins

1. **Category Creation** – First AI consent protocol (like robots.txt was for crawlers)
2. **Regulatory Tailwind** – EU AI Act, copyright guidance drive adoption
3. **Two-Sided Network** – Publishers need consent, AI needs compliance
4. **Open + Commercial** – Protocol is open, premium features are proprietary
5. **Technical Moat** – Patent + deep CMS integrations + first-mover advantage

---

**AIIndex v1.1 – Deployed. Verified. Trusted.**

*Confidential – For qualified investors and strategic partners*
*Last updated: October 13, 2025*
