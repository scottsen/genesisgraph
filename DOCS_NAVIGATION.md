# Documentation Navigation Guide

**Last Updated:** 2025-11-21

This guide helps you navigate GenesisGraph documentation using **incremental reveal** principles - start simple, add depth progressively.

## 🎯 Quick Start: Choose Your Learning Path

### Path 1: "I Want to Try It" (10 minutes)
**For:** Developers who learn by doing

1. [Quickstart](docs/getting-started/quickstart.md) (5 min) - Guitar hanger example
2. [Examples](docs/getting-started/examples.md) (5 min) - Hands-on code
3. Try: `genesisgraph validate examples/basic-pipeline.gg.yaml`

### Path 2: "I Need to Understand It" (20 minutes)
**For:** Engineers evaluating adoption

1. [README](README.md) (5 min) - What is GenesisGraph?
2. [Disclosure Levels](docs/user-guide/disclosure-levels.md) (10 min) - A/B/C model explained
3. [User Guide Overview](docs/user-guide/overview.md) (5 min) - Feature landscape

### Path 3: "I'm Building With It" (45 minutes)
**For:** Developers integrating GenesisGraph

1. [Architecture](docs/developer-guide/architecture.md) (15 min) - System design
2. [Use Cases](docs/use-cases.md) (15 min) - Integration patterns
3. [SDK Quick Reference](docs/reference/sdk-quick-reference.md) (15 min) - API lookup

### Path 4: "I'm Making Decisions" (30 minutes)
**For:** Executives, product managers, researchers

1. [FAQ](docs/faq.md) (10 min) - Common objections answered
2. [Vision](docs/strategic/vision.md) (15 min) - Why this matters
3. [Roadmap](docs/strategic/roadmap.md) (5 min) - Maturity & timeline

---

## 📚 Documentation Structure — Four Layers

GenesisGraph documentation follows **incremental reveal**: each layer builds on the previous.

### Layer 1: Essential Basics (5-10 minutes)
**Goal:** Understand what GenesisGraph is and why it matters

| Document | Purpose | Time |
|----------|---------|------|
| [Installation](docs/getting-started/installation.md) | Set up SDKs | 2 min |
| [Quickstart](docs/getting-started/quickstart.md) | Simplest tutorial | 5 min |
| [Examples](docs/getting-started/examples.md) | Hands-on code | 5 min |
| **[Disclosure Levels](docs/user-guide/disclosure-levels.md)** | **Core innovation: A/B/C model** | **10 min** |

**Key Concept:** Three-level selective disclosure (A=full, B=verified, C=zero-knowledge)

---

### Layer 2: User Guidance (15-45 minutes)
**Goal:** Learn how to use GenesisGraph features effectively

| Document | Purpose | Time |
|----------|---------|------|
| [User Guide Overview](docs/user-guide/overview.md) | Feature landscape | 15 min |
| [DID & Identity](docs/user-guide/did-web-guide.md) | Enterprise identity (did:web) | 15 min |
| [Selective Disclosure](docs/user-guide/selective-disclosure.md) | SD-JWT, BBS+, cryptography | 20 min |
| [Transparency Logs](docs/user-guide/transparency-log.md) | RFC 6962 audit trails | 15 min |
| [Profile Validators](docs/user-guide/profile-validators.md) | Industry compliance | 15 min |
| [Use Cases](docs/use-cases.md) | Real-world integrations | 15 min |
| [FAQ](docs/faq.md) | Common questions | 10 min |

**Key Skills:** Choose disclosure level, set up identity, implement features

---

### Layer 3: Technical Depth (30-90 minutes)
**Goal:** Understand architecture and integrate with your systems

| Document | Purpose | Time |
|----------|---------|------|
| [Architecture](docs/developer-guide/architecture.md) | System design | 30 min |
| [Contributing](docs/developer-guide/contributing.md) | Contribution guidelines | 15 min |
| [Security](docs/developer-guide/security.md) | Security model | 20 min |
| [Troubleshooting](docs/developer-guide/troubleshooting.md) | Common issues | 15 min |
| [SDK Development Guide](docs/reference/sdk-development-guide.md) | Extend SDKs | 45 min |
| [SDK Quick Reference](docs/reference/sdk-quick-reference.md) | API lookup | 15 min |
| [Implementation Status](docs/reference/implementation-summary.md) | Feature coverage | 10 min |
| [Main Specification](docs/specifications/main-spec.md) | Formal standard | 60 min |
| [ZKP Templates](docs/specifications/zkp-templates.md) | Zero-knowledge proofs | 30 min |

**Key Skills:** Integrate GenesisGraph, extend functionality, understand formal spec

---

### Layer 4: Strategic Context (20-60 minutes)
**Goal:** Understand vision, roadmap, and planning for adoption

| Document | Purpose | Time |
|----------|---------|------|
| [Vision](docs/strategic/vision.md) | Why it matters, 5-year plan | 20 min |
| [Roadmap](docs/strategic/roadmap.md) | v0.3.0 → v1.0 development | 25 min |
| [Critical Gaps](docs/strategic/critical-gaps.md) | Strategic gaps analysis | 30 min |

**Key Insights:** Adoption strategy, maturity level, investment planning

---

## 🧭 Navigation by Role

### Developers
```
1. [Quickstart](docs/getting-started/quickstart.md)
2. [Examples](docs/getting-started/examples.md)
3. [Architecture](docs/developer-guide/architecture.md)
4. [SDK Reference](docs/reference/sdk-quick-reference.md)
```

### Decision-Makers
```
1. [FAQ](docs/faq.md)
2. [Use Cases](docs/use-cases.md)
3. [Vision](docs/strategic/vision.md)
4. [Roadmap](docs/strategic/roadmap.md)
```

### AI/ML Engineers
```
1. [Disclosure Levels](docs/user-guide/disclosure-levels.md)
2. [Use Cases: AI Pipelines](docs/use-cases.md#ai-pipelines)
3. [Profile Validators](docs/user-guide/profile-validators.md)
4. [Selective Disclosure](docs/user-guide/selective-disclosure.md)
```

### Researchers
```
1. [Main Specification](docs/specifications/main-spec.md)
2. [Selective Disclosure](docs/user-guide/selective-disclosure.md)
3. [ZKP Templates](docs/specifications/zkp-templates.md)
4. [Architecture](docs/developer-guide/architecture.md)
```

---

## 📖 Progressive Reading Tools

### Progressive Reveal CLI
Consume documentation at your own pace:

```bash
# Install
cd tools/progressive-reveal-cli && pip install -e .

# Explore at different depth levels
reveal docs/getting-started/quickstart.md --level 1   # Structure only
reveal docs/user-guide/overview.md --level 2          # With previews
reveal docs/faq.md --level 3 --grep "blockchain"     # Full search
```

**Full guide:** [Document Explorer Guide](DOCUMENT_EXPLORER_GUIDE.md)

---

## 🗺️ Documentation Map

```
README.md (Entry point)
├── Layer 1: Getting Started
│   ├── Installation
│   ├── Quickstart
│   ├── Examples
│   └── ⭐ Disclosure Levels (Core concept)
│
├── Layer 2: User Guidance
│   ├── User Guide Overview
│   ├── Feature Guides
│   │   ├── DID & Identity
│   │   ├── Selective Disclosure
│   │   ├── Transparency Logs
│   │   └── Profile Validators
│   ├── Use Cases & Integration
│   └── FAQ
│
├── Layer 3: Technical Depth
│   ├── Developer Guide
│   │   ├── Architecture
│   │   ├── Contributing
│   │   ├── Security
│   │   └── Troubleshooting
│   ├── Reference
│   │   ├── SDK Development
│   │   ├── SDK Quick Reference
│   │   └── Implementation Status
│   └── Specifications
│       ├── Main Spec (formal)
│       └── ZKP Templates
│
└── Layer 4: Strategic Context
    ├── Vision (why it matters)
    ├── Roadmap (v0.3 → v1.0)
    └── Critical Gaps (planning)
```

---

## 🔍 Finding What You Need

### "I want to understand the core innovation"
→ [Disclosure Levels (A/B/C)](docs/user-guide/disclosure-levels.md)

### "I need to see real examples"
→ [Use Cases](docs/use-cases.md)
→ [Examples](docs/getting-started/examples.md)

### "I have questions"
→ [FAQ](docs/faq.md)
→ [Troubleshooting](docs/developer-guide/troubleshooting.md)

### "I'm integrating GenesisGraph"
→ [Architecture](docs/developer-guide/architecture.md)
→ [SDK Quick Reference](docs/reference/sdk-quick-reference.md)

### "I need the formal specification"
→ [Main Specification](docs/specifications/main-spec.md)

### "I'm evaluating for adoption"
→ [Vision](docs/strategic/vision.md)
→ [Roadmap](docs/strategic/roadmap.md)
→ [FAQ](docs/faq.md)

---

## 📦 Related Files

- **[README.md](README.md)** - Main entry point with progressive learning paths
- **[mkdocs.yml](mkdocs.yml)** - MkDocs site configuration (matches this structure)
- **[DOCUMENT_EXPLORER_GUIDE.md](DOCUMENT_EXPLORER_GUIDE.md)** - Progressive reveal CLI guide
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

---

**Need help?** Start with the [README](README.md) or jump to your role-specific path above!
