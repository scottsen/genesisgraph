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

**v0.2 Public Working Draft — November 2025**

GenesisGraph is an **open standard for proving how things were made**. It provides cryptographically verifiable provenance for AI pipelines, manufacturing, scientific research, healthcare, and any workflow where "show me how you made this" matters.

**The Innovation:** Three-level selective disclosure (A/B/C) enables proving compliance without revealing trade secrets—solving the "certification vs IP protection" dilemma that blocks adoption in regulated industries.

---

## 🚀 Quick Start

**New to GenesisGraph?** Start here:

1. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute tutorial with simplest possible examples
2. **[USE_CASES.md](USE_CASES.md)** - Real-world integrations (AI, science, media)
3. **[FAQ.md](FAQ.md)** - Common questions: "Why not PROV-O?", "Do I need blockchain?", etc.
4. **[spec/MAIN_SPEC.md](spec/MAIN_SPEC.md)** - Complete specification (886 lines)
5. **[STRATEGIC_CONTEXT.md](STRATEGIC_CONTEXT.md)** - Why this matters, adoption strategy, 5-year vision

**Enterprise users:** See **[docs/DID_WEB_GUIDE.md](docs/DID_WEB_GUIDE.md)** for did:web support - use your organization's domain for identity management.

**Want to integrate?** See `USE_CASES.md` §Integration Patterns for wrapper/native/post-hoc approaches.

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

This package contains the complete v0.2 implementation:

## Directory Structure

```
genesisgraph/
├── spec/
│   └── MAIN_SPEC.md              # Updated specification with §9.2 selective disclosure
├── schema/
│   └── genesisgraph-core-v0.1.yaml  # Core schema with selective disclosure support
├── docs/
│   └── DID_WEB_GUIDE.md          # Complete guide for did:web usage
├── examples/
│   ├── level-a-full-disclosure.gg.yaml     # Level A: Full transparency
│   ├── level-b-partial-envelope.gg.yaml    # Level B: Policy claims only
│   ├── level-c-sealed-subgraph.gg.yaml     # Level C: Sealed subgraph with commitments
│   ├── workflow-with-did-web.gg.yaml       # Enterprise workflow using did:web
│   ├── did-web-example.json                # Sample DID document
│   └── did-web-organization.json           # Organization DID document with multiple keys
├── scripts/
│   ├── verify_sealed_subgraph.py           # Merkle inclusion proof verifier
│   └── verify_transparency_anchoring.py    # Transparency log anchor verifier
└── genesisgraph/
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

See **[docs/PROFILE_VALIDATORS.md](docs/PROFILE_VALIDATORS.md)** for complete documentation.

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

See **[docs/SELECTIVE_DISCLOSURE.md](docs/SELECTIVE_DISCLOSURE.md)** for complete documentation and examples.

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

**Documentation:** See [docs/TRANSPARENCY_LOG.md](docs/TRANSPARENCY_LOG.md) for detailed usage and API reference.

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

This package represents the **v0.2** deliverables for selective disclosure:

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

**Completed (v0.2):**
- [x] Certificate Transparency log integration (RFC 6962) - production-ready Trillian and Rekor support
- [x] Merkle tree inclusion and consistency proofs for tamper-evident audit trails
- [x] Multi-log witness support for cross-organizational verification
- [x] Offline verification capability with cached proofs
- [x] 666 comprehensive tests covering all RFC 6962 operations
- [x] Full documentation in `docs/TRANSPARENCY_LOG.md`
- [x] Enterprise-ready for regulated industries (AS9100D, ISO 9001:2015, FDA 21 CFR Part 11)
- [x] Additional DID methods (did:ion, did:ethr) with comprehensive test coverage
- [x] ION (Sidetree on Bitcoin) DID resolution with Universal Resolver support
- [x] Ethereum DID resolution with multi-network support

**v0.3 Features:**
- [x] SD-JWT / BBS+ selective disclosure (cryptographic privacy) — ✅ **Completed**
- [x] Profile-specific validators (gg-ai-basic-v1, gg-cam-v1) — ✅ **Completed**
- [x] Python/JavaScript SDK libraries — ✅ **Completed**
- [x] ZK proof-of-policy templates (zero-knowledge compliance) — ✅ **Completed**
- [x] Additional DID methods (did:ion, did:ethr) — ✅ **Completed**

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

**See:** `USE_CASES.md` for complete examples with code.

---

## 🔬 Reference Implementations

### Python Wrapper (AI Pipelines)

200-line wrapper for OpenAI/Anthropic APIs:

```python
client = OpenAIWithProvenance(api_key)
response = client.chat_completion(messages=[...])
client.export_provenance("workflow.gg.yaml")
```

**Details:** `USE_CASES.md` §AI Pipeline Provenance

---

## 📚 Documentation Guide

| Document | Purpose | Audience | Time |
|----------|---------|----------|------|
| **QUICKSTART.md** | Simplest tutorial | Developers new to GenesisGraph | 5 min |
| **USE_CASES.md** | Real integrations | Teams evaluating adoption | 15 min |
| **FAQ.md** | Common objections | Decision-makers, skeptics | 10 min |
| **MAIN_SPEC.md** | Complete standard | Implementers, auditors | 45 min |
| **STRATEGIC_CONTEXT.md** | Big picture | Executives, investors | 20 min |

---

## 🛠️ Next Steps

### For Developers

1. Read `QUICKSTART.md` (5 minutes)
2. Try simplest example (guitar hanger CAD export)
3. Explore `examples/` directory
4. Run verification scripts
5. Integrate with your tool (see `USE_CASES.md` §Integration Patterns)

### For Decision-Makers

1. Read `FAQ.md` (10 minutes) - addresses "Why not PROV-O?", "Do I need blockchain?"
2. Review `USE_CASES.md` - see real-world integration examples
3. Read `STRATEGIC_CONTEXT.md` (20 minutes) - understand adoption strategy, 5-year vision
4. Evaluate business value for your domain (AI, manufacturing, research, etc.)

### For Researchers

1. Read `spec/MAIN_SPEC.md` §9.2 - selective disclosure patterns (normative)
2. Review examples: Level A (full), Level B (partial), Level C (sealed)
3. Try verification scripts: `scripts/verify_sealed_subgraph.py`
4. Explore schema: `schema/genesisgraph-core-v0.1.yaml`

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
