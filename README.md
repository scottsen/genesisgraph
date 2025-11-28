---
project: genesisgraph
type: software
status: active
beth_topics:
- genesisgraph
- software
tags:
- provenance
- verification
- standard
- compliance
- cryptography
- development
- code
---

# GenesisGraph: Universal Verifiable Process Provenance

**v0.3.0 — November 2025**

GenesisGraph is an **open standard for proving how things were made**. It provides cryptographically verifiable provenance for AI pipelines, manufacturing, scientific research, healthcare, and any workflow where "show me how you made this" matters.

**The Innovation:** Three-level selective disclosure (A/B/C) enables proving compliance without revealing trade secrets—solving the "certification vs IP protection" dilemma that blocks adoption in regulated industries.

---

## Part of the Semantic Infrastructure Lab

**GenesisGraph** is a production component of the [Semantic Infrastructure Lab (SIL)](https://github.com/semantic-infrastructure-lab/sil) — building the semantic substrate for intelligent systems.

**Role in the Semantic OS:**
- **Cross-Cutting:** Provenance infrastructure (enables verifiable transformations across all layers)

**SIL Principles Applied:**
- ✅ **Clarity** — Explicit process representation, no hidden transformations
- ✅ **Simplicity** — Minimal standard (graphs, hashes, signatures)
- ✅ **Composability** — Graphs compose, selective disclosure composes
- ✅ **Correctness** — 363 tests, cryptographic verification
- ✅ **Verifiability** — Core mission: provable computational correctness

**Quick Links:** [SIL Manifesto](https://github.com/semantic-infrastructure-lab/sil/blob/main/docs/canonical/MANIFESTO.md) • [Unified Architecture](https://github.com/semantic-infrastructure-lab/sil/blob/main/docs/architecture/UNIFIED_ARCHITECTURE_GUIDE.md) • [Project Index](https://github.com/semantic-infrastructure-lab/sil/blob/main/projects/PROJECT_INDEX.md)

---

## 🚀 Quick Start — Choose Your Path

**New to GenesisGraph?** Follow this progressive learning path:

### Layer 1: Essential Basics (5-10 minutes)
Start here to understand what GenesisGraph is and why it matters:

1. **[5-Minute Quickstart](docs/getting-started/quickstart.md)** - Simplest possible example (CAD file export)
2. **[Disclosure Levels (A/B/C)](docs/user-guide/disclosure-levels.md)** - **Core innovation**: Choose what to reveal

### Layer 2: User Guidance (15-30 minutes)
Learn how to use GenesisGraph features effectively:

3. **[User Guide Overview](docs/user-guide/overview.md)** - Progressive feature introduction
4. **[Examples & Use Cases](docs/use-cases.md)** - Real-world integrations (AI, manufacturing, research)
5. **[FAQ](docs/faq.md)** - Common questions: "Why not PROV-O?", "Do I need blockchain?"

### Layer 3: Technical Depth (30-60 minutes)
Understand the architecture and integrate with your systems:

6. **[Architecture](docs/developer-guide/architecture.md)** - System design and components
7. **[Main Specification](docs/specifications/main-spec.md)** - Complete formal standard
8. **[SDK References](docs/reference/sdk-quick-reference.md)** - API quick lookup

### Layer 4: Strategic Context (20-45 minutes)
Explore vision, roadmap, and planning for decision-makers:

9. **[Vision & Why It Matters](docs/strategic/vision.md)** - 5-year adoption strategy
10. **[Roadmap](docs/strategic/roadmap.md)** - 📍 **PRIMARY ROADMAP** - v0.3.0 → v1.0
11. **[Critical Gaps Analysis](docs/strategic/critical-gaps.md)** - Strategic gaps for v1.0

---

### 🎯 Quick Navigation by Role

<table>
<tr>
<td><strong>👨‍💻 Developers</strong><br/>
→ <a href="docs/getting-started/quickstart.md">Quickstart</a><br/>
→ <a href="docs/getting-started/examples.md">Examples</a><br/>
→ <a href="docs/developer-guide/architecture.md">Architecture</a>
</td>
<td><strong>🏢 Decision-Makers</strong><br/>
→ <a href="docs/faq.md">FAQ</a><br/>
→ <a href="docs/use-cases.md">Use Cases</a><br/>
→ <a href="docs/strategic/vision.md">Vision</a>
</td>
</tr>
<tr>
<td><strong>🤖 AI/ML Engineers</strong><br/>
→ <a href="docs/user-guide/disclosure-levels.md">Disclosure Levels</a><br/>
→ <a href="docs/use-cases.md#ai-pipelines">AI Examples</a><br/>
→ <a href="docs/user-guide/profile-validators.md">AI Validators</a>
</td>
<td><strong>🔬 Researchers</strong><br/>
→ <a href="docs/specifications/main-spec.md">Specification</a><br/>
→ <a href="docs/user-guide/selective-disclosure.md">Cryptography</a><br/>
→ <a href="docs/specifications/zkp-templates.md">ZKP Templates</a>
</td>
</tr>
</table>

---

### 📖 Explore Documentation Incrementally

Use our Progressive Reveal CLI to consume docs at your own pace:

```bash
# Install the tool
cd tools/progressive-reveal-cli && pip install -e .

# Explore by depth level
reveal docs/getting-started/quickstart.md --level 1   # See structure
reveal docs/user-guide/overview.md --level 2          # Preview content
reveal docs/faq.md --level 3 --grep "blockchain"     # Search topics
```

**Full guide:** [Document Explorer Guide](DOCUMENT_EXPLORER_GUIDE.md)

---

## 📚 SDK Libraries

GenesisGraph provides official SDKs for easy integration:

### Python SDK

```bash
pip install genesisgraph
```

```python
from genesisgraph import GenesisGraph, Entity, Operation, Tool

# Create a document
gg = GenesisGraph(spec_version="0.1.0")

# Add a tool
tool = Tool(id="mytool", type="Software", version="1.0")
gg.add_tool(tool)

# Add entities and operations
entity = Entity(id="data", type="Dataset", version="1", file="./data.csv")
gg.add_entity(entity)

# Export
yaml_output = gg.to_yaml()
gg.save_yaml("workflow.gg.yaml")
```

**Features:** Full builder API, validation, DID resolution, signature verification, transparency log integration

**Docs:** See [examples/python_sdk_quickstart.py](examples/python_sdk_quickstart.py)

### JavaScript/TypeScript SDK

```bash
npm install @genesisgraph/sdk
```

```typescript
import { GenesisGraph, Entity, Operation, Tool } from '@genesisgraph/sdk';

// Create a document
const gg = new GenesisGraph({ specVersion: '0.1.0' });

// Add a tool
const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
gg.addTool(tool);

// Add entities and operations
const entity = new Entity({ id: 'data', type: 'Dataset', version: '1', file: './data.csv' });
gg.addEntity(entity);

// Export
const yaml = gg.toYAML();
gg.saveYAML('workflow.gg.yaml');
```

**Features:** Full TypeScript support, fluent API, YAML/JSON conversion, hash computation

**Docs:** See [sdks/javascript/README.md](sdks/javascript/README.md) and [sdks/javascript/examples/quickstart.ts](sdks/javascript/examples/quickstart.ts)

---

## 📦 What's Included

This package contains the complete v0.3 implementation with:

- **363 comprehensive tests** across all modules
- **76% overall test coverage** (up from 71%)
- **Production-ready cryptographic features:** SD-JWT (98% coverage), BBS+ (99% coverage), ZKP templates (97% coverage)
- **Enterprise validation:** Profile validators (AI, manufacturing), compliance checkers (FDA 21 CFR 11, ISO 9001)
- **Multi-DID support:** did:key, did:web, did:ion, did:ethr with 90% coverage
- **Transparency log integration:** RFC 6962 verification with 48% coverage on complex Merkle proof algorithms
- **Builder API:** Python and JavaScript SDKs with 93% coverage

## Directory Structure

```
genesisgraph/
├── docs/                          # Organized documentation (see mkdocs.yml)
│   ├── getting-started/           # Layer 1: Essential basics
│   │   ├── installation.md
│   │   ├── quickstart.md
│   │   └── examples.md
│   ├── user-guide/                # Layer 2: Feature guides
│   │   ├── overview.md
│   │   ├── disclosure-levels.md   # A/B/C model explained
│   │   ├── did-web-guide.md       # Enterprise identity
│   │   ├── selective-disclosure.md # SD-JWT, BBS+ cryptography
│   │   ├── transparency-log.md     # RFC 6962 audit trails
│   │   └── profile-validators.md   # Industry compliance
│   ├── developer-guide/           # Layer 3: Architecture & integration
│   │   ├── architecture.md
│   │   ├── contributing.md
│   │   ├── security.md
│   │   └── troubleshooting.md
│   ├── reference/                 # API & SDK reference
│   │   ├── sdk-development-guide.md
│   │   ├── sdk-quick-reference.md
│   │   └── implementation-summary.md
│   ├── specifications/            # Formal definitions
│   │   ├── main-spec.md           # Complete specification
│   │   └── zkp-templates.md       # Zero-knowledge proofs
│   ├── strategic/                 # Layer 4: Vision & planning
│   │   ├── vision.md
│   │   ├── roadmap.md
│   │   └── critical-gaps.md
│   ├── use-cases.md               # Real-world examples
│   └── faq.md                     # Common questions
├── schema/
│   └── genesisgraph-core-v0.1.yaml  # Core schema with selective disclosure
├── examples/
│   ├── level-a-full-disclosure.gg.yaml     # Level A: Full transparency
│   ├── level-b-partial-envelope.gg.yaml    # Level B: Verified privacy
│   ├── level-c-sealed-subgraph.gg.yaml     # Level C: Zero-knowledge
│   └── workflow-with-did-web.gg.yaml       # Enterprise workflow
├── scripts/
│   ├── verify_sealed_subgraph.py           # Merkle inclusion proof verifier
│   └── verify_transparency_anchoring.py    # Transparency log anchor verifier
└── genesisgraph/                  # Python SDK implementation
    ├── did_resolver.py             # DID resolution (did:key, did:web, did:ion, did:ethr)
    └── validator.py                # Signature verification with DID support
```

## Industry-Specific Profile Validators

GenesisGraph now includes **Phase 5 validation** with industry-specific profile validators for automated compliance checking:

### Available Profiles

- **gg-ai-basic-v1**: AI/ML pipeline validation
  - Required parameters for AI operations (temperature, model version, etc.)
  - FDA 21 CFR Part 11 compliance for electronic records
  - Human review requirement checking for high-stakes decisions
  - Data lineage and model versioning validation

- **gg-cam-v1**: Computer-aided manufacturing validation
  - ISO 9001:2015 quality management compliance
  - Tolerance and dimensional accuracy tracking
  - Machine calibration and maintenance verification
  - Quality control checkpoint validation

### Compliance Standards

- **ISO 9001:2015**: Quality management systems validation
- **FDA 21 CFR Part 11**: Electronic records and signatures compliance

### Usage

```bash
# Auto-detect and validate profile
genesisgraph validate workflow.gg.yaml --verify-profile

# Validate with specific profile
genesisgraph validate workflow.gg.yaml --verify-profile --profile gg-ai-basic-v1

# Python API
from genesisgraph import GenesisGraphValidator
validator = GenesisGraphValidator(verify_profile=True, profile_id='gg-cam-v1')
result = validator.validate_file('manufacturing.gg.yaml')
```

See **[Profile Validators Guide](docs/user-guide/profile-validators.md)** for complete documentation.

---

## Cryptographic Privacy Features

GenesisGraph now supports **SD-JWT and BBS+ selective disclosure** for advanced privacy-preserving provenance:

### SD-JWT (Selective Disclosure JWT)

Implements IETF SD-JWT draft specification for cryptographically hiding claim values while maintaining verifiability:

- **Selective claim disclosure**: Reveal only necessary information to verifiers
- **Holder binding**: Prevent credential replay attacks
- **Standard-compliant**: Follows IETF draft specification
- **Integration**: Works seamlessly with GenesisGraph attestations

### BBS+ Signatures

Privacy-preserving credentials with unlinkable selective disclosure:

- **Zero-knowledge proofs**: Prove properties without revealing values
- **Unlinkable presentations**: Each disclosure is cryptographically unlinkable
- **Predicate proofs**: Range proofs (e.g., "age > 21" without revealing exact age)
- **Pairing-based cryptography**: Industry-standard BBS+ implementation

### Usage

```python
from genesisgraph.credentials.sd_jwt import SDJWTIssuer, SDJWTVerifier
from genesisgraph.credentials.bbs_plus import BBSPlusIssuer

# Create SD-JWT with selective disclosure
issuer = SDJWTIssuer(issuer_did="did:web:example.com")
sd_jwt = issuer.create_sd_jwt(
    claims={"temperature": 0.7, "model": "gpt-4"},
    disclosable_claims=["temperature"]  # Hide model, reveal temperature
)
```

See **[Selective Disclosure Guide](docs/user-guide/selective-disclosure.md)** for complete documentation and examples.

**Note:** Requires optional `credentials` dependencies: `pip install genesisgraph[credentials]`

---

## What's New: Selective Disclosure Patterns

The updated specification (§9.2) defines three practical patterns for privacy-preserving provenance:

### 1. Hash-Only Lineage (Sealed Subgraph)

**Purpose:** Hide proprietary pipeline segments while maintaining integrity and proving policy compliance.

**Key features:**
- Merkle root commitment over hidden subgraph
- Selective exposure of input/output digests
- Policy assertion claims with independent signatures
- Optional inclusion proofs without revealing full tree

**Use cases:**
- Proprietary AI prompt engineering chains
- Manufacturing toolpath IP protection
- Research methodology redaction

**Example:** `examples/level-c-sealed-subgraph.gg.yaml`

### 2. Partial Attestation Envelope

**Purpose:** Prove policy compliance without revealing exact parameters.

**Key features:**
- Parameters marked as `_redacted: true`
- Policy result envelopes with claim-minimized fields
- Limit checks (≤, ≥) instead of exact values
- Optional SD-JWT/BBS+ for attribute-level disclosure

**Use cases:**
- AI model temperature constraints without prompt exposure
- Manufacturing tolerance compliance without toolpath details
- Regulatory compliance without trade secret disclosure

**Example:** `examples/level-b-partial-envelope.gg.yaml`

### 3. Transparency Anchoring

**Purpose:** Provide time-ordering, non-repudiation, and multi-party witness without exposing content.

**Key features:**
- RFC 6962-style (Certificate Transparency) inclusion proofs
- Multi-log witness support
- Offline verification capability
- Consistency proofs for append-only guarantees
- **Production-ready Trillian and Rekor (Sigstore) integration**

**Use cases:**
- Cross-organizational audit trails
- Regulated industry compliance (AS9100D, ISO 9001:2015, FDA 21 CFR Part 11)
- Supply chain time-stamping
- Multi-party verification requirements

**Example:** All levels can use transparency anchoring (see Level B and C examples)

**Documentation:** See [Transparency Log Guide](docs/user-guide/transparency-log.md) for detailed usage and API reference.

## Disclosure Levels

| Level | Description | Parameters | Policy Claims | Commitments | Use When |
|-------|-------------|-----------|---------------|-------------|----------|
| **A** | Full Disclosure | ✓ Visible | ✓ Visible | ✗ Not needed | Internal audit, research collaboration |
| **B** | Partial Envelope | ✗ Redacted | ✓ Visible | ✗ Not needed | Regulatory compliance, limited IP exposure |
| **C** | Sealed Subgraph | ✗ Hidden | ✓ Visible | ✓ Merkle root | Supply chain, high-value IP, multi-party trust |

## Schema Extensions

The updated core schema (`schema/genesisgraph-core-v0.1.yaml`) adds:

### New Operation Types
- `sealed_subgraph` — Replaces hidden pipeline segments

### New Attestation Fields
```yaml
attestation:
  claims:                    # Policy result envelope
    policy: <profile-id>
    results: <claim-set>
  transparency:              # Transparency log anchors (array)
    - log_id: <did-or-uri>
      entry_id: <hex>
      tree_size: <int>
      inclusion_proof: <base64>
  multisig:                  # Multi-witness signatures
    threshold: <m>
    signers: [<did>, ...]
  tee:                       # TEE attestation quotes
    technology: <sgx|sev|...>
    quote: <base64>
```

### New Operation Fields
```yaml
operations:
  - sealed:                  # Sealed subgraph commitment
      merkle_root: <hash>
      leaves_exposed:
        - role: <input|output|intermediate>
          hash: <hash>
      policy_assertions:
        - id: <policy-id>
          result: <pass|fail>
          signer: <did>
  - reproducibility:         # Reproducible execution metadata
      expected_output_hash: <hash>
      rerun_allowed_until: <timestamp>
  - work_proof:              # Proof-of-effort (VDF, etc.)
      type: <vdf_wesolowski|...>
      output: <base64>
  - resource_usage:          # Resource footprint
      cpu_seconds: <float>
      gpu_ms: <float>
      energy_kj_estimate: <float>
```

## Verification Scripts

### Sealed Subgraph Verifier

Validates sealed subgraph patterns and Merkle commitments.

**Usage:**
```bash
python scripts/verify_sealed_subgraph.py examples/level-c-sealed-subgraph.gg.yaml
```

**Checks:**
- ✓ Merkle root present and well-formed
- ✓ Exposed leaf hashes match expected format
- ✓ Policy assertions have valid results (pass/fail)
- ✓ Attestation signatures and timestamps
- ✓ TEE quotes and multisig requirements
- ✓ Merkle inclusion proof demonstration

**Output:**
```
=== Verifying sealed operation: op_cam_pipeline_sealed ===
✓ Merkle root: sha256:deadbeef1234567890...
✓ Exposed leaves: 2
  - sub_input: sha256:5f6a7b8c9d0e1f2a...
  - sub_output: sha256:9e8d7c6b5a4f3e2d...

✓ Policy assertions: 3
  ✓ gg-cam-v1: pass (signer: did:svc:cam-phoenix)
  ✓ iso-9001-2015: pass (signer: did:org:facility-phoenix)
  ✓ as9100d-aerospace: pass (signer: did:org:facility-phoenix)
```

### Transparency Anchoring Verifier

Validates Certificate Transparency-style log anchors.

**Usage:**
```bash
python scripts/verify_transparency_anchoring.py examples/level-b-partial-envelope.gg.yaml
```

**Checks:**
- ✓ Transparency log entries well-formed
- ✓ Inclusion proofs decodable
- ✓ Multi-log witness validation
- ✓ Consistency proof format (if present)
- ✓ CT-style inclusion proof demonstration

**Output:**
```
=== Transparency Summary ===
Anchored operations: 2
Total anchors: 3
Unique logs: 2
Log IDs:
  - did:log:internal-audit
  - did:log:aerospace-compliance

=== Operation: op_inference_001 ===
  Found 1 transparency anchor(s)
  Verifying transparency anchor:
    Log ID: did:log:internal-audit
    Entry ID: 0x5f2c8a91
    Tree size: 428934
    ✓ Inclusion proof: 512 bytes
    ✓ Transparency entry format valid
```

## Example Walkthroughs

### Level A: Full Disclosure (AI Medical Q&A)

**Scenario:** Internal audit of AI-assisted medical question answering.

**What's visible:**
- ✓ Full retrieval query and parameters
- ✓ Complete inference configuration (temperature, prompt)
- ✓ Moderation filter settings
- ✓ Human reviewer identity and approval

**Provenance chain:**
```
medical_corpus@2025-10-15
  └→ [retrieval] → retrieval_results@1
      └→ [inference + prompt] → raw_answer@1
          └→ [moderation] → moderated_answer@1
              └→ [human_review] → final_answer@1
```

**Trust basis:** Signed by medical professional (did:person:dr_sarah_chen) with delegation to hospital system.

---

### Level B: Partial Envelope (AI with Hidden Prompts)

**Scenario:** External audit of AI system with proprietary prompt engineering.

**What's visible:**
- ✗ Exact prompt text (redacted)
- ✓ Policy compliance claims (temperature ≤ 0.3, prompt length ≤ 4000 chars)
- ✓ Moderation results (pass/fail)
- ✓ Human reviewer approval
- ✓ Transparency log anchors

**What's hidden:**
- Proprietary retrieval strategies
- Internal prompt templates
- Fine-tuning details

**Trust basis:** Policy claims signed by trusted services + transparency log multi-witness.

---

### Level C: Sealed Subgraph (Manufacturing Toolpath IP)

**Scenario:** Aerospace part certification with proprietary CAM pipeline.

**What's visible:**
- ✓ Input: CAD model hash
- ✓ Output: G-code hash
- ✓ Policy assertions: gg-cam-v1, ISO-9001, AS9100D (all pass)
- ✓ TEE attestation quote (Intel SGX)
- ✓ Multi-log transparency anchors
- ✓ QC inspection results

**What's hidden:**
- ✗ Entire CAM pipeline (4+ internal operations)
- ✗ Toolpath optimization algorithms
- ✗ Feed rate strategies
- ✗ Surface finishing techniques

**Trust basis:**
- Merkle commitment binds sealed subgraph to visible I/O
- TEE quote proves execution in trusted hardware
- Multisig (2-of-3: CAM system, engineer, QA manager)
- Dual transparency logs (internal + aerospace compliance)
- VDF proof-of-effort to deter replay

**Commitments:**
```yaml
sealed:
  merkle_root: sha256:deadbeef123456...
  leaves_exposed:
    - sub_input: sha256:5f6a7b8c...  (matches bracket_mesh@5)
    - sub_output: sha256:9e8d7c6b... (matches gcode_final@1)
```

## Quick Start

### 1. Review the Specification
```bash
# Read updated §9.2 on selective disclosure
cat spec/MAIN_SPEC.md
# Jump to "## 9. Trust, Compliance, and Selective Disclosure"
```

### 2. Explore Examples
```bash
# Level A: Full transparency
cat examples/level-a-full-disclosure.gg.yaml

# Level B: Policy claims without parameters
cat examples/level-b-partial-envelope.gg.yaml

# Level C: Sealed proprietary pipeline
cat examples/level-c-sealed-subgraph.gg.yaml
```

### 3. Run Verification
```bash
# Install dependencies
pip install pyyaml

# Verify sealed subgraph
python scripts/verify_sealed_subgraph.py examples/level-c-sealed-subgraph.gg.yaml

# Verify transparency anchoring
python scripts/verify_transparency_anchoring.py examples/level-b-partial-envelope.gg.yaml
```

## Implementation Roadmap

This package represents the **v0.3.0** release:

**Completed (v0.1.0-alpha):**
- [x] Normative §9.2 specification text
- [x] Core schema extensions
- [x] Three disclosure-level examples
- [x] Basic verification scripts (Merkle, CT-style)

**Completed (v0.1.1):**
- [x] Full ed25519 signature verification
- [x] DID resolution for identity verification (did:key, did:web)
- [x] Security documentation (SECURITY.md)
- [x] Comprehensive did:web support with SSRF protection, rate limiting, and TLS validation
- [x] Integration tests and examples for did:web

**Completed (v0.2.0):**
- [x] Certificate Transparency log integration (RFC 6962) - production-ready Trillian and Rekor support
- [x] Merkle tree inclusion and consistency proofs for tamper-evident audit trails
- [x] Multi-log witness support for cross-organizational verification
- [x] Offline verification capability with cached proofs
- [x] 666 comprehensive tests covering all RFC 6962 operations
- [x] Full documentation in `docs/TRANSPARENCY_LOG.md`
- [x] Enterprise-ready for regulated industries (AS9100D, ISO 9001:2015, FDA 21 CFR Part 11)

**Completed (v0.3.0):**
- [x] SD-JWT / BBS+ selective disclosure (cryptographic privacy)
- [x] Profile-specific validators (gg-ai-basic-v1, gg-cam-v1)
- [x] Python/JavaScript SDK libraries
- [x] ZK proof-of-policy templates (zero-knowledge compliance)
- [x] Additional DID methods (did:ion, did:ethr) with comprehensive test coverage
- [x] ION (Sidetree on Bitcoin) DID resolution with Universal Resolver support
- [x] Ethereum DID resolution with multi-network support

## Comparison Matrix: Verification Strengths

| Pattern | Integrity | Time/Order | Privacy | Exec Proof | Ops Cost |
|---------|-----------|------------|---------|------------|----------|
| Hash-Only Lineage | ★★★ | ★★ (if anchored) | ★★ | ★ | ★ Low |
| Partial Envelope | ★★★ | ★★ (if anchored) | ★★★ | ★★ (trust issuer) | ★★ Medium |
| Transparency Logs | ★★★ | ★★★★ | ★★★ | ★★ | ★★ Medium |
| Reproducible Re-run | ★★★★ | ★★ | ★★ | ★★★★ | ★★★ High |
| TEE Quotes | ★★★★ | ★★ | ★★★ | ★★★★ | ★★★ High |
| Multisig | ★★★★ | ★★ | ★★★ | ★★★ | ★★ Medium |

---

## 🎯 Why GenesisGraph?

### The Problem

Every product we build today comes from a pipeline:
- **AI answers:** retrieval → prompts → models → post-processing
- **Parts:** CAD → CAM → toolpaths → CNC → QC
- **Research:** datasets → scripts → analysis → figures

But proving "here's how we made this" is hard:
- ❌ **Documentation can be edited** (no cryptographic proof)
- ❌ **Tribal knowledge** (not portable across tools)
- ❌ **Compliance vs IP dilemma** (can't prove ISO-9001 without revealing trade secrets)

### The Solution

GenesisGraph provides:
- ✅ **Cryptographic proof** (hashes, signatures, timestamps)
- ✅ **Machine verification** (auditors validate automatically)
- ✅ **Selective disclosure** (prove compliance without revealing IP)
- ✅ **Universal format** (works across AI, manufacturing, science, media)
- ✅ **Progressive trust** (start simple, add cryptography when needed)

### Real Business Value

| Stakeholder | Before | After |
|-------------|--------|-------|
| **AI Consultant** | "Trust me, I did extensive work" | "Here's cryptographic proof: 12 iterations, 47 docs, 2.3hrs expert review" |
| **Aerospace Supplier** | "Can't prove compliance without revealing CAM IP" | "Provable ISO-9001 compliance with sealed toolpaths" |
| **Researcher** | "Figure reproducibility depends on goodwill" | "Attached `.gg.yaml` with exact software versions, parameters" |
| **Auditor** | "Manual verification, slow, error-prone" | "Machine-verifiable proof, instant validation" |

**See:** [Use Cases & Integration](docs/use-cases.md) for complete examples with code.

---

## 🔬 Reference Implementations

### Python Wrapper (AI Pipelines)

200-line wrapper for OpenAI/Anthropic APIs:

```python
client = OpenAIWithProvenance(api_key)
response = client.chat_completion(messages=[...])
client.export_provenance("workflow.gg.yaml")
```

**Details:** [Use Cases](docs/use-cases.md) §AI Pipeline Provenance

---

## 📚 Documentation Guide — Organized by Incremental Reveal

| Layer | Document | Purpose | Audience | Time |
|-------|----------|---------|----------|------|
| **1** | [Quickstart](docs/getting-started/quickstart.md) | Simplest tutorial | New developers | 5 min |
| **1** | [Disclosure Levels](docs/user-guide/disclosure-levels.md) | Core A/B/C model | All users | 10 min |
| **2** | [User Guide](docs/user-guide/overview.md) | Feature overview | Implementers | 15 min |
| **2** | [Use Cases](docs/use-cases.md) | Real integrations | Teams evaluating adoption | 15 min |
| **2** | [FAQ](docs/faq.md) | Common questions | Decision-makers | 10 min |
| **3** | [Architecture](docs/developer-guide/architecture.md) | System design | Developers | 30 min |
| **3** | [Main Spec](docs/specifications/main-spec.md) | Complete standard | Implementers, auditors | 45 min |
| **4** | [Vision](docs/strategic/vision.md) | Why it matters | Executives, investors | 20 min |
| **4** | [Roadmap](docs/strategic/roadmap.md) | Development plan | Contributors | 25 min |
| **4** | [Critical Gaps](docs/strategic/critical-gaps.md) | Strategic analysis | Standards architects | 30 min |

---

## 🛠️ Next Steps — Progressive Learning Paths

### For Developers
Follow Layer 1 → 2 → 3 for systematic learning:

1. **Start:** [Quickstart](docs/getting-started/quickstart.md) (5 min) - Guitar hanger CAD export example
2. **Understand:** [Disclosure Levels](docs/user-guide/disclosure-levels.md) (10 min) - A/B/C model
3. **Explore:** [Examples](docs/getting-started/examples.md) - Hands-on code samples
4. **Integrate:** [Architecture](docs/developer-guide/architecture.md) - System integration patterns
5. **Reference:** [SDK Quick Reference](docs/reference/sdk-quick-reference.md) - API lookup

### For Decision-Makers
Evaluate business value quickly:

1. **Overview:** Read the top of this README (2 min) - Understand the innovation
2. **Questions:** [FAQ](docs/faq.md) (10 min) - "Why not PROV-O?", "Do I need blockchain?"
3. **Examples:** [Use Cases](docs/use-cases.md) (15 min) - Real-world integrations
4. **Strategy:** [Vision](docs/strategic/vision.md) (20 min) - Adoption strategy, 5-year plan
5. **Planning:** [Roadmap](docs/strategic/roadmap.md) (25 min) - Current state & v1.0 timeline

### For Researchers
Deep technical exploration:

1. **Concept:** [Disclosure Levels](docs/user-guide/disclosure-levels.md) - Three-level model
2. **Cryptography:** [Selective Disclosure](docs/user-guide/selective-disclosure.md) - SD-JWT, BBS+, ZKP
3. **Specification:** [Main Spec](docs/specifications/main-spec.md) - §9.2 selective disclosure (normative)
4. **Examples:** Review `examples/level-{a,b,c}-*.gg.yaml` files
5. **Verification:** Try `scripts/verify_sealed_subgraph.py` and `verify_transparency_anchoring.py`

---

## 🤝 Contributing

This is a **v0.2 public working draft**. Community feedback essential for success.

**Ways to contribute:**

1. **Integrate with your tool** - Share implementation patterns
2. **Report issues** - Spec ambiguities, integration challenges
3. **Create examples** - Real-world use cases from your domain
4. **Build libraries** - Python, JavaScript, Go, Rust implementations
5. **Propose profiles** - Domain-specific schemas (gg-bio, gg-chem, gg-finance)

**Feedback welcome on:**
- Schema design (are primitives sufficient?)
- Example clarity (do Levels A/B/C demonstrate value?)
- Verification scripts (what checks are missing?)
- Profile requirements (what should gg-ai-basic-v1 mandate?)

**Security:**
- See [SECURITY.md](SECURITY.md) for vulnerability reporting and security considerations
- Report security issues to: security@genesisgraph.dev

**License:** Apache 2.0 - Free to use, modify, distribute.

## License

- **Specification text:** CC-BY 4.0
- **Schema & code:** Apache 2.0

---

**Generated:** 2025-11-19
**Template:** GenesisGraph Selective Disclosure Implementation Package v0.2
