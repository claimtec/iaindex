---
sidebar_position: 1
title: Introduction
---

# Welcome to IAIndex

IAIndex is a **transparent AI training attribution protocol** that enables content creators, publishers, and rights holders to track and verify how their content is being used by AI systems.

## The Problem

As AI models become increasingly sophisticated, the question of training data attribution has become critical. Content creators need:

- Transparency about whether their content was used in AI training
- Verification of proper licensing and attribution
- Compensation mechanisms for content usage
- Control over how their content is accessed by AI systems

## Our Solution

IAIndex provides a comprehensive protocol that addresses these challenges through:

### 1. Transparent Attribution

Every piece of content indexed in the IAIndex protocol includes cryptographically signed metadata that tracks:
- Original source and authorship
- Licensing terms
- Access permissions
- Usage receipts

### 2. Verifiable Receipts

When AI systems access content through IAIndex, they generate cryptographically signed receipts that provide:
- Proof of access
- Timestamp verification
- Model identification
- Usage context

### 3. Publisher Control

Content publishers maintain full control through:
- Domain verification
- Access policies
- Licensing terms
- Analytics and reporting

## Key Features

- **Cryptographic Verification**: All transactions are cryptographically signed for authenticity
- **Distributed Architecture**: No single point of failure or control
- **Open Protocol**: Fully documented and implementable by anyone
- **SDK Support**: Libraries for Node.js, Python, and more
- **Plugin Ecosystem**: Easy integration with WordPress, Webflow, Shopify, and other platforms
- **Compliance Ready**: Built-in support for GDPR, POPIA, and other regulations

## Who Should Use IAIndex?

### Content Publishers
News organizations, blogs, and content platforms that want to track AI usage of their content.

### AI Companies
AI model developers and providers who want to ensure transparent and ethical training data practices.

### Website Owners
Anyone running a website who wants to participate in the attribution ecosystem.

### Developers
Developers building tools and applications in the AI attribution space.

## Getting Started

Ready to integrate IAIndex? Check out our [Quick Start Guide](./quickstart.md) to get up and running in 5 minutes.

## Architecture Overview

```
┌─────────────────┐
│   Publishers    │ (Content creators and rights holders)
└────────┬────────┘
         │
         │ Publish index + signatures
         │
         ▼
┌─────────────────┐
│  IAIndex Index  │ (Distributed index of content metadata)
└────────┬────────┘
         │
         │ Query and access
         │
         ▼
┌─────────────────┐
│   AI Clients    │ (AI systems accessing content)
└────────┬────────┘
         │
         │ Generate receipts
         │
         ▼
┌─────────────────┐
│    Publishers   │ (Receive usage receipts)
└─────────────────┘
```

## Core Concepts

### Index Entry
A JSON document describing a piece of content, including metadata, licensing terms, and cryptographic signatures.

### Receipt
A cryptographically signed proof that an AI system accessed specific content, including timestamp and model information.

### Publisher
An entity that creates and publishes content and maintains an IAIndex entry for it.

### Client
An AI system or application that accesses content through the IAIndex protocol.

### Attestation
A cryptographic signature that verifies the authenticity of index entries and receipts.

## Support and Community

- [GitHub Repository](https://github.com/claimtec/iaindex)
- [Discord Community](https://discord.gg/iaindex)
- [Issue Tracker](https://github.com/claimtec/iaindex/issues)
- [Twitter](https://twitter.com/iaindex)

## License

The IAIndex protocol is open source and available under the MIT License. Individual implementations may use different licenses.

---

**Ready to dive in?** Start with our [Quick Start Guide](./quickstart.md) or explore the [Protocol Specification](./protocol/schema.md).
