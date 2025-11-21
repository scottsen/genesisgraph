# GenesisGraph Documentation

Welcome to the GenesisGraph documentation! GenesisGraph is an **open standard for proving how things were made** with cryptographically verifiable provenance.

## What is GenesisGraph?

GenesisGraph provides verifiable provenance for:

- **AI Pipelines** - Prove how AI models generated outputs
- **Manufacturing** - Document production processes with IP protection
- **Scientific Research** - Enable reproducible research
- **Healthcare** - Track medical data processing chains
- **Supply Chains** - Verify product origins and handling

## Key Features

✅ **Cryptographic Verification** - Hashes, signatures, timestamps  
✅ **Selective Disclosure** - Prove compliance without revealing trade secrets  
✅ **Transparency Logs** - Tamper-evident audit trails (RFC 6962)  
✅ **Industry Profiles** - AI/ML (FDA 21 CFR), Manufacturing (ISO 9001)  
✅ **Progressive Trust** - Start simple, add cryptography as needed  

## Quick Links

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __5-Minute Quickstart__

    ---

    Get started with a simple example and validate your first document

    [:octicons-arrow-right-24: Quickstart Guide](getting-started/quickstart.md)

-   :fontawesome-brands-python:{ .lg .middle } __API Reference__

    ---

    Complete Python SDK documentation with examples

    [:octicons-arrow-right-24: API Docs](api-reference/validator.md)

-   :material-book-open-variant:{ .lg .middle } __User Guide__

    ---

    Learn about validation, disclosure levels, and cryptographic features

    [:octicons-arrow-right-24: User Guide](user-guide/overview.md)

-   :material-code-braces:{ .lg .middle } __Developer Guide__

    ---

    Architecture, testing, and contribution guidelines

    [:octicons-arrow-right-24: Developer Guide](developer-guide/architecture.md)

</div>

## The Innovation: Selective Disclosure

GenesisGraph solves the **"certification vs IP protection" dilemma** with three disclosure levels:

| Level | Description | Use When |
|-------|-------------|----------|
| **Level A: Full Disclosure** | All details visible | Internal audits, research collaboration |
| **Level B: Partial Envelope** | Policy claims visible, parameters hidden | Regulatory compliance |
| **Level C: Sealed Subgraph** | Merkle commitments + TEE attestations | High-value IP, supply chains |

This enables proving **ISO 9001 compliance without revealing manufacturing toolpaths**, or **AI safety compliance without exposing proprietary prompts**.

## Installation

=== "Python"

    ```bash
    pip install genesisgraph
    ```

=== "JavaScript/TypeScript"

    ```bash
    npm install @genesisgraph/sdk
    ```

=== "CLI Tool"

    ```bash
    pip install genesisgraph[cli]
    gg --version
    ```

## Simple Example

```python
from genesisgraph import GenesisGraph, Entity, Operation, Tool

# Create a document
gg = GenesisGraph(spec_version="0.1.0")

# Add entities
input_data = Entity(id="data", type="Dataset", version="1", file="./data.csv")
gg.add_entity(input_data)

# Add operations
transform = Operation(
    id="process",
    type="transformation",
    inputs=["data"],
    outputs=["result"]
)
gg.add_operation(transform)

# Export
gg.save_yaml("workflow.gg.yaml")
```

Validate:

```bash
gg validate workflow.gg.yaml
# ✓ Validation PASSED
```

## Use Cases

<div class="grid cards" markdown>

-   :material-robot:{ .lg .middle } __AI Pipelines__

    ---

    Prove how AI models generated outputs, with selective disclosure of prompts

    [:octicons-arrow-right-24: AI Use Cases](use-cases/ai-pipelines.md)

-   :material-cube-outline:{ .lg .middle } __Manufacturing__

    ---

    ISO 9001 compliance with sealed CAM toolpaths

    [:octicons-arrow-right-24: Manufacturing](use-cases/manufacturing.md)

-   :material-flask:{ .lg .middle } __Scientific Research__

    ---

    Reproducible research with full parameter disclosure

    [:octicons-arrow-right-24: Science](use-cases/scientific-research.md)

</div>

## Community & Support

- **GitHub**: [github.com/scottsen/genesisgraph](https://github.com/scottsen/genesisgraph)
- **Issues**: [Report bugs](https://github.com/scottsen/genesisgraph/issues)
- **Discussions**: [Community forum](https://github.com/scottsen/genesisgraph/discussions)

## Next Steps

1. **New users**: Start with the [Quickstart Guide](getting-started/quickstart.md)
2. **Developers**: Read the [Architecture Documentation](developer-guide/architecture.md)
3. **Enterprise**: Review [Security Considerations](developer-guide/security.md)
4. **Researchers**: See the [Main Specification](specifications/main-spec.md)

---

**Current Version:** v0.3.0  
**License:** Apache 2.0 (code), CC-BY 4.0 (specification)
