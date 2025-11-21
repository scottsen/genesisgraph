# Examples

This page provides hands-on examples to help you understand GenesisGraph through practical use cases.

## Quick Examples

### Example 1: Basic Provenance Graph

The simplest example is tracking a file transformation:

```yaml
# example-basic.gg.yaml
nodes:
  - id: cad-file
    type: Input
    label: "guitar-hanger.blend"

  - id: export-process
    type: Process
    label: "Blender STL Export"
    agent: "Blender 3.6.5"

  - id: stl-file
    type: Output
    label: "guitar-hanger.stl"
    hash:
      algorithm: sha256
      value: "a3f5c892..."

edges:
  - from: cad-file
    to: export-process
  - from: export-process
    to: stl-file
```

**What this shows:** Basic provenance tracking - input → process → output

### Example 2: Disclosure Levels (A/B/C)

GenesisGraph's key feature is **selective disclosure**:

```yaml
# Disclosure Level A: Full transparency
disclosure: A
nodes:
  - id: training-data
    type: Input
    label: "customer-images.zip"
    location: "s3://mybucket/data.zip"
    hash:
      algorithm: sha256
      value: "d4e5f6..."
```

```yaml
# Disclosure Level B: Verified, private details
disclosure: B
nodes:
  - id: training-data
    type: Input
    label: "customer-images.zip"
    hash:
      algorithm: sha256
      value: "d4e5f6..."
    # location omitted for privacy
```

```yaml
# Disclosure Level C: Proof without revealing anything
disclosure: C
nodes:
  - id: training-data
    type: Input
    proofs:
      - type: "hash-commitment"
        value: "proof:zkp:c7a8b9..."
    # All details hidden, only cryptographic proof shown
```

**What this shows:** How to control what information is shared

## Example Repository

Full examples with runnable code:

```bash
# Explore the examples directory
cd examples/
ls -la
```

Available examples:
- `basic-pipeline.gg.yaml` - Simple three-step process
- `disclosure-levels.gg.yaml` - A/B/C examples side-by-side
- `ai-training.gg.yaml` - ML pipeline with model provenance
- `manufacturing.gg.yaml` - CAD to production workflow

## Interactive Examples

### Try It Yourself

1. **Validate an example:**
   ```bash
   genesisgraph validate examples/basic-pipeline.gg.yaml
   ```

2. **Check different disclosure levels:**
   ```bash
   genesisgraph validate examples/disclosure-levels.gg.yaml
   ```

3. **Visualize a graph:**
   ```bash
   genesisgraph visualize examples/ai-training.gg.yaml --output graph.png
   ```

## Real-World Example Scenarios

For complete real-world integration examples, see:
- [Use Cases](../use-cases.md) - Detailed scenarios with code
- [AI Pipeline Example](../use-cases.md#ai-pipelines) - FDA-compliant ML tracking
- [Manufacturing Example](../use-cases.md#manufacturing) - ISO 9001 CAD workflow

## Next Steps

<div class="grid cards" markdown>

- **Master the concepts** → [User Guide Overview](../user-guide/overview.md)
- **Understand disclosure levels** → [Disclosure Levels (A/B/C)](../user-guide/disclosure-levels.md)
- **See real integrations** → [Use Cases & FAQ](../use-cases.md)

</div>

---

**Need Help?** Check the [FAQ](../faq.md) or [Troubleshooting Guide](../developer-guide/troubleshooting.md)
