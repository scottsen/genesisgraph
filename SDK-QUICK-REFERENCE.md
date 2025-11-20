# GenesisGraph SDK Quick Reference

**Version:** 0.2.0  
**For SDK Developers Building GenesisGraph Libraries**

---

## The Four Pillars of GenesisGraph

Every GenesisGraph document contains four core data types:

### 1. ENTITY (What was made)
```yaml
- id: medical_corpus
  type: Dataset
  version: 2025-10-15
  uri: s3://kb/corpus.parquet
  hash: sha256:a1b2c3d4...
  derived_from: [parent@version]
```
**Key:** Referenced as `id@version` throughout document

### 2. OPERATION (How it was transformed)
```yaml
- id: op_inference_001
  type: ai_inference
  inputs: [retrieval_results@1]
  outputs: [answer@1]
  tool: llama3@3.0
  parameters: {temperature: 0.2}
  attestation: {mode: signed, ...}
```
**Key:** Links inputs → outputs via tool

### 3. TOOL (Who/what did the work)
```yaml
- id: llama3_70b
  type: AIModel
  vendor: Meta
  version: 3.0
  capabilities: {max_tokens: 8192, temperature_range: [0, 2]}
  identity: {did: did:model:llama3}
```
**Key:** Define what tool CAN do; operations show what it DID do

### 4. ATTESTATION (Proof of trust)
```yaml
attestation:
  mode: signed                    # basic|signed|verifiable|zk
  signer: did:person:alice
  signature: ed25519:sig_abc...
  timestamp: 2025-10-31T14:25:36Z
  claims: {policy: gg-ai-basic-v1, results: {...}}
```
**Key:** Progressive trust: timestamp → signature → DID → ZK proof

---

## Minimal Valid Document

```yaml
spec_version: 0.1.0

tools:
  - id: mytool
    type: Software
    version: 1.0

entities:
  - id: input
    type: Text
    version: 1
    hash: sha256:abc...

  - id: output
    type: Text
    version: 1
    hash: sha256:def...

operations:
  - id: op1
    type: transform
    inputs: [input@1]
    outputs: [output@1]
    tool: mytool@1.0
```

---

## Validation Checklist

- [ ] `spec_version` format: `X.Y.Z` (semantic version)
- [ ] All entities have: `id`, `type`, `version`, and (`file` OR `uri`)
- [ ] All operations have: `id`, `type`
- [ ] All tools have: `id`, `type` (one of: Software|Machine|Human|AIModel|Service)
- [ ] All hashes format: `{algo}:{hexdigest}` where algo = sha256|sha512|blake3
- [ ] Entity references format: `id@version`
- [ ] Attestation mode ∈ [basic, signed, verifiable, zk]
- [ ] If mode=signed|verifiable|zk: must have `signer` and `signature`
- [ ] Timestamps are valid ISO 8601

---

## Three Disclosure Levels

### Level A: Full Disclosure
All parameters visible. Use for: internal audit, open research
```yaml
parameters:
  temperature: 0.2
  prompt: "You are a medical assistant..."
```

### Level B: Partial Envelope
Parameters hidden, policy claims visible
```yaml
parameters:
  _redacted: true
attestation:
  claims:
    policy: gg-ai-basic-v1
    results:
      temperature: {lte: 0.3, satisfied: true}
```

### Level C: Sealed Subgraph
Entire pipeline sealed with Merkle root
```yaml
type: sealed_subgraph
sealed:
  merkle_root: sha256:deadbeef...
  leaves_exposed:
    - role: sub_input
      hash: sha256:...
    - role: sub_output
      hash: sha256:...
```

---

## Common Entity Types

**Data/Knowledge:** Dataset, DataSnapshot, CorpusSnapshot, TextTemplate

**AI/Models:** AIModel, Model, FineTunedModel

**Manufacturing:** CADModel, Mesh, Mesh3D, GCode, PhysicalPart

**Media:** Text, Image, Video, Audio

**Validation:** InspectionReport, VerificationReport, Certificate

**Custom:** Any [A-Z][a-zA-Z0-9]* string

---

## Common Operation Types

**AI/ML:** ai_retrieval, ai_inference, ai_moderation, ai_training, ai_evaluation

**Manufacturing:** tessellation, slicing, cnc_machining, 3d_printing, quality_inspection

**Data:** data_preparation, data_filtering, aggregation, analysis

**Human:** human_review, human_annotation, human_approval

**Custom:** Any [a-z_]+ string

---

## DIDs (Decentralized Identifiers)

### did:key (Self-describing, no resolution needed)
```
did:key:z6Mkfr9fBhVu1gVx3bRR5MNhkB3EsN8hM6x3ZQfXz6Kh3TwM
```
- No HTTPS required
- Good for: testing, single-use keys
- Key embedded in DID itself

### did:web (Organization identity)
```
did:web:aerospace.example.com
did:web:aerospace.example.com:engineering:john_smith
```
- Resolves to HTTPS: `/.well-known/did.json` or `/path/did.json`
- Good for: persistent organizational identity
- Returns DID document with public keys

---

## Fidelity / Loss Types

Explicitly track what information is lost at each step:

- `lossless` - No loss
- `geometric_approximation` - CAD → mesh (tolerance_mm: 0.05)
- `compression_loss` - Model quantization
- `summarization_loss` - Text summarization, RAG
- `quantization_loss` - Bit depth reduction
- `sampling_loss` - Statistical sampling
- `custom` - Domain-specific

**Example:**
```yaml
fidelity:
  expected: geometric_approximation
  actual:
    tolerance_mm: 0.05
    surface_finish_ra: 0.8
```

---

## Standard Profiles

**gg-ai-basic-v1** (v0.2)
- AI/ML inference pipelines
- Requires: model identity, temperature/prompt controls, human review
- Supports: retrieval, inference, moderation

**gg-cam-v1** (v0.2)
- Manufacturing workflows
- Requires: tool capabilities, tolerances, QC results
- Supports: tessellation, slicing, machining

**gg-sci-v1**, **gg-media-v1** (planned)

---

## Python API (Reference Implementation)

```python
from genesisgraph import GenesisGraphValidator

# Validate a document
validator = GenesisGraphValidator(
    use_schema=True,              # Enable JSON Schema validation
    verify_signatures=True,        # Check signatures
    verify_transparency=True       # Verify transparency logs
)

result = validator.validate_file("workflow.gg.yaml")

if result.is_valid:
    print("Valid!")
else:
    print(result.format_report())
```

**ValidationResult:**
- `is_valid: bool` - Overall valid?
- `errors: List[str]` - Critical errors
- `warnings: List[str]` - Non-fatal issues
- `data: Dict` - Parsed document

---

## Integration Patterns

### Pattern 1: Wrapper (Easiest)
Wrap existing tool calls, generate GenesisGraph after execution
- Pros: No code changes, works with third-party tools
- Cons: May miss internal details

### Pattern 2: Native (Complete)
Integrate directly into tool/SDK, track operations in real-time
- Pros: Complete information, fine-grained control
- Cons: Requires code changes

### Pattern 3: Observer/Plugin (Flexible)
Provide hooks for GenesisGraph observers
- Pros: Non-invasive, pluggable
- Cons: Requires observer support

---

## Signing & Verification

### Signature Format
```
{algorithm}:{base64-signature}

Examples:
  ed25519:sig_aabbccdd
  ecdsa:sig_xyz...
```

### Supported Algorithms
- **Ed25519** (recommended)
- **ECDSA** (P-256)
- **RSA** (2048+)

### Python Signing
```python
import json, base64
from cryptography.hazmat.primitives.asymmetric import ed25519

# Canonicalize (sorted keys, no whitespace)
canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))

# Sign
signature = private_key.sign(canonical.encode())

# Encode
sig_str = f"ed25519:{base64.b64encode(signature).decode()}"
```

---

## Security for SDK Developers

### Input Validation Limits
- Max entities: 10,000
- Max operations: 10,000
- Max tools: 1,000
- Max ID length: 256 chars
- Max hash length: 512 chars
- Max signature length: 4,096 chars

### DID Resolution Security (did:web)
- Blocks: localhost, 127.0.0.1, 169.254.169.254
- Blocks: Private networks (10.0.0.0/8, 192.168.0.0/16, etc.)
- Timeout: 10 seconds
- Response limit: 1MB

### Always Verify Hash When Available
```python
import hashlib

def verify_hash(file_path, expected_hash):
    algo, expected = expected_hash.split(':')
    hasher = hashlib.new(algo)
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest() == expected
```

---

## File Formats

### YAML (Human-friendly, authoring)
```yaml
spec_version: 0.1.0
tools: [...]
entities: [...]
operations: [...]
```
**Filename:** `*.gg.yaml`

### JSON (Canonical, for signing)
```json
{"spec_version":"0.1.0","tools":[...],"entities":[...],"operations":[...]}
```
- Single-line (no whitespace)
- Keys sorted alphabetically
- Used for canonicalization

### Conversion
```bash
# YAML → JSON
python -c "import yaml, json; print(json.dumps(yaml.safe_load(open('x.yaml'))))"

# JSON → YAML
python -c "import yaml, json; print(yaml.dump(json.load(open('x.json'))))"
```

---

## Transparency Logs (RFC 6962)

Anchor operations to append-only logs for non-repudiation and time-ordering:

```yaml
attestation:
  transparency:
    - log_id: did:log:corpA
      entry_id: 0x5f2c8a91
      tree_size: 128734
      inclusion_proof: base64:MIIB...
```

**Use cases:**
- Audit trails for regulated industries
- Time-ordering across organizations
- Non-repudiation of operations
- Multi-party witness

---

## Document Structure at a Glance

```yaml
spec_version: 0.1.0               # Required

profile: gg-ai-basic-v1           # Optional: domain profile
imports: [...]                    # Optional: namespaces
namespaces: {...}                 # Optional: local mappings
context: {...}                    # Optional: execution environment

tools: [...]                       # Define actors/tools
entities: [...]                    # Define artifacts
operations: [...]                  # Define transformations

metadata: {...}                    # Optional: document metadata
```

---

## Key Insights for SDK Developers

1. **Start Simple**
   - Minimal document: spec_version + tool + entity + operation
   - Add trust progressively (timestamps → signatures → DIDs)

2. **Reference Everything**
   - Use `id@version` references to connect entities
   - Enables directed acyclic graph (DAG) of provenance

3. **Progressive Disclosure**
   - Not all data needs to be visible (Level A/B/C)
   - Can prove compliance without revealing trade secrets

4. **Capability Tracking**
   - Tool `capabilities` describe POTENTIAL (what tool CAN do)
   - Operation `realized_capability` describes ACTUAL (what it DID do)
   - Enables compliance checking: "Did we stay within allowed parameters?"

5. **Loss Tracking**
   - Every transformation has loss/approximation
   - Explicitly track with `fidelity` field
   - Legally defensible: "We disclosed the approximation"

6. **Profiles > Core Schema**
   - Core schema is lightweight
   - Domain-specific requirements go in profiles (gg-ai-basic-v1, etc.)
   - Keep core stable, profiles can evolve

---

## Resources

**Full Reference:** `/home/user/genesisgraph/SDK-DEVELOPMENT-GUIDE.md` (1,368 lines)

**Specification:** `/home/user/genesisgraph/spec/MAIN_SPEC.md` (887 lines)

**Schema:** `/home/user/genesisgraph/schema/genesisgraph-core-v0.1.yaml`

**Examples:**
- Level A (Full): `/home/user/genesisgraph/examples/level-a-full-disclosure.gg.yaml`
- Level B (Partial): `/home/user/genesisgraph/examples/level-b-partial-envelope.gg.yaml`
- Level C (Sealed): `/home/user/genesisgraph/examples/level-c-sealed-subgraph.gg.yaml`
- did:web: `/home/user/genesisgraph/examples/workflow-with-did-web.gg.yaml`

**Python Implementation:** `/home/user/genesisgraph/genesisgraph/` (2,318 lines)

---

## Implementation Checklist for New SDKs

- [ ] Parse YAML/JSON input
- [ ] Validate against schema
- [ ] Generate valid YAML/JSON output
- [ ] Support round-trip conversion
- [ ] Hash verification (when applicable)
- [ ] DID resolution (at least did:key)
- [ ] Signature verification
- [ ] Entity relationship validation (inputs/outputs exist)
- [ ] Tool reference validation
- [ ] Attestation mode validation
- [ ] Documentation with domain examples
- [ ] Integration examples (wrapper/native/observer)

---

**Next Step:** Read the full guide at `/home/user/genesisgraph/SDK-DEVELOPMENT-GUIDE.md`
