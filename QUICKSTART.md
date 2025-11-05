# GenesisGraph Quick Start

**Get up and running with verifiable process provenance in 5 minutes.**

---

## What is GenesisGraph?

GenesisGraph is a **standard format for proving how things were made**. Think of it as a verifiable recipe that cryptographically documents:

- What was produced (artifacts)
- How it was transformed (operations)
- Which tools did the work (software, hardware, humans)
- With what fidelity and loss (precision tracking)
- Signed by whom (cryptographic attestation)

**Use it for:** AI pipelines, manufacturing, scientific research, content authenticity, or any workflow where "prove how you made this" matters.

---

## Your First GenesisGraph Document (2 minutes)

Let's create the simplest possible provenance document: converting a CAD file to STL.

### Step 1: Create `guitar_hanger.gg.yaml`

```yaml
spec_version: 0.1.0

tools:
  - id: freecad
    type: Software
    version: 0.21.2

entities:
  - id: guitar_hanger.fcstd
    type: CADModel
    version: 1.0
    hash: sha256:a1b2c3d4...

  - id: guitar_hanger.stl
    type: Mesh3D
    version: 1.0
    hash: sha256:e5f6g7h8...
    derived_from: [guitar_hanger.fcstd@1.0]

operations:
  - id: export_stl
    type: mesh_export
    inputs: [guitar_hanger.fcstd@1.0]
    outputs: [guitar_hanger.stl@1.0]
    tool: freecad@0.21.2
    parameters:
      tolerance_mm: 0.1
      mesh_deviation: 0.01
    attestation:
      mode: basic
      timestamp: 2025-10-31T10:00:00Z
```

**That's it!** You now have verifiable provenance for your CAD export.

### Step 2: What did we just create?

- **Tool**: FreeCAD 0.21.2 (the software that did the work)
- **Entities**: CAD file → STL mesh (input and output artifacts)
- **Operation**: Export with specific parameters (what happened)
- **Attestation**: Basic timestamp (when it happened)

This document proves:
✓ Which version of FreeCAD was used
✓ What tolerance settings were applied
✓ When the export happened
✓ The exact hash of both files

---

## Level Up: Add Human Review (3 minutes)

Let's add a human approval step to show multi-stage workflows:

```yaml
spec_version: 0.1.0

tools:
  - id: freecad
    type: Software
    version: 0.21.2

  - id: qa_engineer
    type: Human
    identity:
      did: did:person:jane_doe
      role: Quality Assurance Engineer

entities:
  - id: guitar_hanger.fcstd
    type: CADModel
    version: 1.0
    hash: sha256:a1b2c3d4...

  - id: guitar_hanger_draft.stl
    type: Mesh3D
    version: draft
    hash: sha256:e5f6g7h8...
    derived_from: [guitar_hanger.fcstd@1.0]

  - id: guitar_hanger_approved.stl
    type: Mesh3D
    version: 1.0
    hash: sha256:i9j0k1l2...
    derived_from: [guitar_hanger_draft.stl@draft]

operations:
  - id: export_stl
    type: mesh_export
    inputs: [guitar_hanger.fcstd@1.0]
    outputs: [guitar_hanger_draft.stl@draft]
    tool: freecad@0.21.2
    parameters:
      tolerance_mm: 0.1
    attestation:
      mode: basic
      timestamp: 2025-10-31T10:00:00Z

  - id: qa_review
    type: human_review
    inputs: [guitar_hanger_draft.stl@draft]
    outputs: [guitar_hanger_approved.stl@1.0]
    tool: qa_engineer@
    parameters:
      review_type: geometry_inspection
      approval_granted: true
      issues_found: 0
    attestation:
      mode: signed
      signer: did:person:jane_doe
      signature: ed25519:sig_aabbccdd...
      timestamp: 2025-10-31T10:15:00Z
```

**What changed?**

- Added a **Human tool** (QA engineer)
- Created **three entities** (CAD → draft STL → approved STL)
- Added **QA review operation** with cryptographic signature
- Now you can prove a human reviewed and approved the output

**Why this matters:** Regulators ask "who approved this?" and you have cryptographic proof.

---

## Understanding the Four Pillars

Every GenesisGraph document has four core components:

### 1. **Entity** (What was made)

Artifacts in your workflow: files, datasets, models, physical parts.

```yaml
- id: medical_corpus
  type: Dataset
  version: 2025-10-15
  hash: sha256:abc123...
  uri: s3://medical-kb/corpus.parquet
```

### 2. **Operation** (How it was transformed)

Transformations that produce new entities from existing ones.

```yaml
- id: op_inference
  type: ai_inference
  inputs: [prompt@1.0, model@3.0]
  outputs: [answer@1.0]
  tool: llama3_70b@3.0
  parameters:
    temperature: 0.2
    max_tokens: 512
```

### 3. **Tool / Agent** (Who/what did the work)

Software, hardware, AI models, or humans.

```yaml
- id: llama3_70b
  type: AIModel
  vendor: Meta
  version: 3.0
  capabilities:
    max_tokens: 8192
    temperature_range: [0.0, 2.0]
```

### 4. **Attestation** (Proof of trust)

Cryptographic evidence: timestamps, signatures, DIDs.

```yaml
attestation:
  mode: signed
  signer: did:person:dr_sarah_chen
  signature: ed25519:sig_xyz...
  timestamp: 2025-10-31T14:25:36Z
```

---

## Real-World Use Cases

### AI Pipeline Provenance

Prove your AI answer came from:
- ✓ 12 retrieval iterations (not one ChatGPT query)
- ✓ Specific model version with temperature=0.2
- ✓ Human clinician review and approval
- ✓ All timestamped and signed

**See:** `examples/level-a-full-disclosure.gg.yaml`

### Manufacturing Traceability

Prove your aerospace part:
- ✓ Came from approved CAD version
- ✓ Was machined on certified equipment
- ✓ Meets ISO-9001 tolerance requirements
- ✓ WITHOUT revealing proprietary toolpaths

**See:** `examples/level-c-sealed-subgraph.gg.yaml`

### Scientific Reproducibility

Prove your research figure:
- ✓ Used exact dataset snapshot
- ✓ Ran specific preprocessing script
- ✓ Applied documented statistical model
- ✓ All steps reproducible from git commits

---

## Selective Disclosure: The Killer Feature

**Problem:** "I need to prove compliance, but I can't reveal my trade secrets."

**Solution:** GenesisGraph supports three disclosure levels:

### Level A: Full Disclosure

All parameters visible. Use for internal audit, open research, collaboration.

```yaml
parameters:
  temperature: 0.2
  prompt: "You are a medical assistant..."
  model: llama3-70b
```

### Level B: Partial Attestation

Parameters hidden, policy compliance claims visible.

```yaml
parameters:
  _redacted: true
claims:
  temperature_constraint: "temperature ≤ 0.3: satisfied"
  medical_license_verified: true
```

### Level C: Sealed Subgraph

Entire proprietary pipeline replaced with Merkle commitment.

```yaml
sealed_subgraph:
  merkle_root: sha256:abc123...
  leaves_exposed: [input_hash, output_hash]
policy_assertions:
  iso_9001: pass
  as9100_rev_d: pass
```

**Read more:** `spec/MAIN_SPEC.md` §9.2

---

## Next Steps

### 1. Read the Full Specification

`spec/MAIN_SPEC.md` - Complete standard with all features

### 2. Explore Examples

- `examples/level-a-full-disclosure.gg.yaml` - AI medical Q&A pipeline
- `examples/level-b-partial-envelope.gg.yaml` - AI with hidden prompts
- `examples/level-c-sealed-subgraph.gg.yaml` - Manufacturing with sealed CAM

### 3. Try Verification Scripts

```bash
# Install dependencies
pip install pyyaml cryptography

# Verify sealed subgraph
python scripts/verify_sealed_subgraph.py examples/level-c-sealed-subgraph.gg.yaml

# Verify transparency anchoring
python scripts/verify_transparency_anchoring.py examples/level-b-partial-envelope.gg.yaml
```

### 4. Integrate with Your Tool

See `USE_CASES.md` for integration guides:
- **TiaCAD Integration** - Reference implementation for CAD/CAM provenance
- **AI Pipeline Wrapper** - Add provenance to OpenAI/Anthropic calls
- **Scientific Workflow** - Track research data pipelines

### 5. Validate Your Documents

Use the JSON Schema validator:

```bash
# Install validator
npm install -g ajv-cli

# Validate your document
ajv validate -s schema/genesisgraph-core-v0.1.yaml -d your_workflow.gg.yaml
```

---

## FAQ

**Q: Do I need blockchain?**
A: No. GenesisGraph works with simple hashes and timestamps. Add cryptography (signatures, DIDs) when you need it.

**Q: Why not just use PROV-O?**
A: PROV-O is great for semantic web but lacks: (1) selective disclosure, (2) capability tracking, (3) loss/fidelity semantics. GenesisGraph is the practical bridge to PROV-O.

**Q: Can I start simple and add trust later?**
A: Yes! Progressive trust modes: basic → signed → verifiable → zk. Start with timestamps, upgrade to cryptography when needed.

**Q: What if my tool doesn't support GenesisGraph?**
A: Write a wrapper! See TiaCAD integration (200 lines) in `USE_CASES.md`.

**More questions?** See `FAQ.md`

---

## Get Help

- **Specification:** `spec/MAIN_SPEC.md`
- **Strategic Context:** `STRATEGIC_CONTEXT.md` (why this matters, adoption strategy)
- **Use Cases:** `USE_CASES.md` (deep dives on AI, manufacturing, science)
- **Schema:** `schema/genesisgraph-core-v0.1.yaml`

---

## License

Apache 2.0 - Free to use, modify, and distribute.

---

**You're ready!** Start creating verifiable provenance for your workflows.

> Every artifact has a beginning. GenesisGraph is how we prove it.
