# AIIndex v1.1 Pitch Deck Outline

**15 Slides | 10-Minute Pitch**

---

## Slide 1: Cover
**Title**: AIIndex
**Subtitle**: The Consent Layer for AI Search
**Tagline**: "The web needs a trust layer for AI"
**Contact**: hello@aiindex.org | aiindex.org

---

## Slide 2: The Problem
**Headline**: The Web Has No Infrastructure for AI Consent

**Bullets**:
- Publishers can't control training vs. retrieval access
- No cryptographic proof of AI interactions
- Legal disputes escalating (NYT, Getty, Reddit vs. AI platforms)
- Existing solutions (robots.txt) lack enforcement and AI-specific controls
- EU AI Act (2025) requires transparency—but no standard exists

**Visual**: Screenshot of "Block Training" toggle grayed out with question mark

---

## Slide 3: Market Timing
**Headline**: Regulatory Pressure + Publisher Backlash = Market Opportunity

**Bullets**:
- **EU AI Act (2025)**: Transparency requirements for training data
- **GDPR Articles 6/7**: Documented consent required for data processing
- **US Copyright Office**: Guidance on AI fair use expected 2025
- **High-profile lawsuits**: $3B+ in damages claimed by publishers
- **Reddit API shutdown**: 500k developers impacted

**Stat**: 75M professional publishers need compliance infrastructure **now**

---

## Slide 4: The Solution
**Headline**: AIIndex = Protocol + Proof + Policy

**3 Pillars**:
1. **Granular Consent**: Set training/retrieval policies via JSON
2. **Cryptographic Receipts**: Signed proof of every AI access
3. **Provenance Tracking**: C2PA + blockchain attestation

**Visual**: Flow diagram: Publisher sets policy → AI discovers → AI respects or denied → Receipt → Merkle tree → Blockchain

---

## Slide 5: How It Works (Technical)
**Headline**: Open Protocol, Proprietary Verification

**Steps**:
1. Publisher installs plugin (WordPress, Shopify, etc.)
2. Sets policy: "Block training, allow retrieval, require receipts"
3. AI client discovers policy via `/.well-known/aiindex-policy.json`
4. Client respects policy or receives HTTP 403 with signed denial
5. Valid access generates cryptographic receipt
6. Receipt logged, aggregated to Merkle tree, anchored to Bitcoin

**Code Snippet**:
```json
{
  "policy": {
    "training": "block",
    "retrieval": "allow"
  },
  "receipts": {
    "require_signed": true
  }
}
```

---

## Slide 6: Product Screenshots
**Headline**: Deployed and Production-Ready

**4 Panels**:
- Dashboard: Compliance chart (allowed vs. denied)
- WordPress: Policy toggle UI
- Receipt: Signed cryptographic receipt JSON
- Badge: Verification badge (Domain ✓, C2PA ✓, Merkle ✓)

---

## Slide 7: Ecosystem
**Headline**: Full-Stack: Publishers + AI Clients

**Publishers** (8 integrations):
- WordPress, Shopify, Webflow, Bubble.io
- Wix, Squarespace, Framer, Ghost

**AI Clients** (2 frameworks):
- LangChain, LlamaIndex
- Custom implementations via SDK (NPM, PyPI)

**Stat**: WordPress alone = 43% of all websites (455M sites)

---

## Slide 8: Competitive Landscape
**Headline**: AIIndex Combines Best of All Alternatives

**Table**:
| Feature | robots.txt | Prerender | Diffbot | C2PA | **AIIndex** |
|---------|------------|-----------|---------|------|-------------|
| AI Consent | ❌ | ❌ | ❌ | ❌ | ✅ |
| Receipts | ❌ | ❌ | ❌ | ❌ | ✅ |
| Provenance | ❌ | ❌ | ❌ | ✅ | ✅ |
| Open Protocol | ✅ | ❌ | ❌ | ✅ | ✅ |

**Positioning**: Only solution with open protocol + cryptographic proof + AI-specific consent

---

## Slide 9: Market Opportunity
**Headline**: $1.5B+ TAM, Two-Sided Network

**Primary Market**:
- 5M high-value publishers × $25/mo = **$1.5B ARR potential**

**Secondary Market**:
- 500 AI enterprises × $5k/mo = **$30M ARR potential**

**Revenue Model**:
- Free: Basic analytics
- Verified ($25/mo): Badge, render fallback
- Enterprise ($500-5k/mo): Custom, mTLS, SLA

---

## Slide 10: Traction
**Headline**: Momentum Before Launch

**Metrics**:
- ✅ v1.1 deployed (69 files, 20k lines of code)
- ✅ 3 LOIs from enterprise publishers (Fortune 500 media, SaaS docs, legal)
- ✅ 247 beta signups (zero marketing spend)
- ✅ Provisional patent filed on core system
- 🔄 WordPress.com partnership discussions (455M sites)
- 🔄 Shopify App Store submission in progress

**Quote**: "AIIndex solves a problem we didn't know how to articulate." — Enterprise Publisher

---

## Slide 11: Business Model
**Headline**: Open Core → Commercial Extensions

**Open Protocol** (MIT License):
- Core JSON schema, receipt format, policy discovery

**Proprietary SaaS**:
- Verification API + dashboard
- Bot reputation system
- Fraud detection algorithms
- Semantic search + embeddings
- Enterprise mTLS

**Unit Economics**:
- CAC: $50 (self-serve), $2k (enterprise)
- LTV: $900 (verified), $60k (enterprise)
- Gross margin: 80%+

---

## Slide 12: Defensibility
**Headline**: IP + Network Effects + First-Mover

**Patent**: Provisional filed on 5 key claims
- Intent differentiation (training vs. retrieval)
- Cryptographic receipt generation
- Policy enforcement with signed denials
- Merkle attestation + timestamping
- Bot reputation scoring

**Moats**:
- First-to-file in AI consent protocol space
- Network effects (publishers ↔ AI clients)
- Deep CMS integrations (WordPress 43% market share)
- Standards-track position (protocol licensing)

---

## Slide 13: Go-To-Market
**Headline**: 3-Phase Launch → 1,000 Customers in 12 Months

**Phase 1 (M0-3)**: Beta with 100 publishers, case studies
**Phase 2 (M3-6)**: Public launch (Product Hunt, TechCrunch), partnerships
**Phase 3 (M6-12)**: Enterprise sales, 1,000 paid customers, $1M ARR

**Key Partnerships**:
- WordPress.com (distribution)
- Shopify (app store)
- Cloudflare (rendering)
- LangChain (co-marketing)

---

## Slide 14: Financial Projections
**Headline**: Path to $50M ARR

**Year 1**: $1.2M ARR
- 1,000 verified ($300k)
- 20 enterprise ($900k)
- 80% gross margin

**Year 2**: $12M ARR
- 10,000 verified ($3M)
- 100 enterprise ($9M)
- Breakeven

**Year 3**: $50M+ ARR
- 100,000 verified ($30M)
- 500 enterprise ($20M)
- Profitable, scaling

**Use of Funds** ($2M seed):
- 40% Engineering (4 engineers)
- 35% Sales & Marketing (2 AEs, 1 marketing lead)
- 25% Operations + reserves

---

## Slide 15: The Ask + Vision
**Headline**: Defining the Consent-Aware Web

**The Ask**:
- **Seed Round**: $2M at $10M pre-money
- **Milestones**: 1,000 paid customers, $1M ARR, 2 strategic partnerships

**Vision**:
AIIndex becomes the standard for AI content access—analogous to:
- **robots.txt** for crawlers
- **HTTPS** for encryption
- **OAuth** for authorization

**Long-Term**: Standards body, international expansion, IPO path

**Closing Line**: "The web needs a consent layer for AI. We're building it."

**Contact**: funding@aiindex.org | cal.com/aiindex

---

## Appendix Slides (Optional)

**A1: Team** (if applicable)
**A2: Technical Deep Dive** (architecture diagram)
**A3: Customer Testimonials** (quotes)
**A4: Press Coverage** (logos: TechCrunch, Protocol, etc.)
**A5: FAQ** (common objections)

---

**Deck Design Notes**:
- **Color Scheme**: Blue (trust) + Green (verified)
- **Font**: Inter or Helvetica (clean, technical)
- **Visual Style**: Minimalist, Stripe/Cloudflare-inspired
- **Code Snippets**: Monospace, syntax highlighting
- **Charts**: Line graphs for ARR, pie charts for market
