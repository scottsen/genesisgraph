# GenesisGraph SDK Development Guide

**Version:** 0.2.0 Public Working Draft  
**Last Updated:** November 2025  
**Purpose:** Complete reference for building SDK libraries for the GenesisGraph format

---

## 1. DIRECTORY STRUCTURE

```
genesisgraph/
├── spec/
│   └── MAIN_SPEC.md                     # 887-line complete specification
├── schema/
│   └── genesisgraph-core-v0.1.yaml      # JSON Schema in YAML format (normative)
├── docs/
│   ├── DID_WEB_GUIDE.md                # did:web identity integration guide
│   └── TRANSPARENCY_LOG.md              # RFC 6962 transparency log support
├── examples/
│   ├── level-a-full-disclosure.gg.yaml      # Full transparency (AI pipeline example)
│   ├── level-b-partial-envelope.gg.yaml     # Policy claims only (hidden prompts)
│   ├── level-c-sealed-subgraph.gg.yaml      # Sealed subgraph (manufacturing example)
│   ├── workflow-with-did-web.gg.yaml        # did:web identities (aerospace workflow)
│   ├── did-web-example.json                 # Sample DID document
│   └── did-web-organization.json            # Organization DID with multiple keys
├── genesisgraph/ (Python reference implementation)
│   ├── validator.py                    # 788 lines: schema validation, signatures
│   ├── did_resolver.py                 # 498 lines: did:key, did:web resolution
│   ├── transparency_log.py             # 758 lines: RFC 6962 verification
│   ├── cli.py                          # 222 lines: CLI interface
│   ├── errors.py                       # Custom exception types
│   └── __init__.py                     # Public API
├── scripts/
│   ├── verify_sealed_subgraph.py       # Merkle inclusion proof verification
│   └── verify_transparency_anchoring.py # Transparency log anchor verification
└── tests/                              # Comprehensive test suite
```

---

## 2. CORE DATA MODEL (Four Pillars)

### 2.1 Entity (What was made)

Artifacts "at rest" in your workflow. Can be files, datasets, models, parts, or any artifact.

**Structure:**
```yaml
- id: gearbox.step
  type: CADModel
  version: 2.0.0
  file: ./parts/gearbox.step              # OR uri: (external reference)
  hash: sha256:0123abcd...
  derived_from: [parent_entity@version]   # Optional lineage
  metadata: {}                             # Optional domain-specific
```

**Required Fields:**
- `id`: Local identifier (unique within document, max 256 chars)
- `type`: Entity type string (e.g., CADModel, Dataset, AIModel, Text, Mesh)
- `version`: Semantic or freeform version string
- One of: `file` (local path) OR `uri` (remote URL)

**Optional Fields:**
- `hash`: Cryptographic hash in format `{algorithm}:{hexdigest}` (e.g., `sha256:abc123...`)
  - Supported algorithms: `sha256`, `sha512`, `blake3`
  - Pattern: `^(sha256|sha512|blake3):[a-f0-9]+$`
- `derived_from`: Array of parent entity references in format `id@version`
- `metadata`: Free-form object for domain-specific attributes

**Key Pattern - References:**
- Entities are referenced as `id@version` throughout operations
- Example: `medical_corpus@2025-10-15`, `gearbox.step@2.0.0`

---

### 2.2 Operation (How it was transformed)

A transformation step that takes input entities and produces output entities.

**Structure:**
```yaml
- id: op_tessellate_01
  type: tessellation
  inputs:  [gearbox.step@2.0.0]
  outputs: [gearbox.3mf@4]
  tool: fusion_exporter@1.1.3
  parameters:
    tolerance_mm: 0.05
  fidelity:
    expected: geometric_approximation
    actual:
      tolerance_mm: 0.05
  metrics:
    mesh_triangles: 124000
  attestation:
    mode: signed
    signer: did:person:alex
    signature: ed25519:abc123==
    timestamp: 2025-10-31T16:12:04Z
  realized_capability:
    tolerance_mm: 0.05
```

**Required Fields:**
- `id`: Operation identifier (unique within document)
- `type`: Operation type string (e.g., tessellation, ai_inference, cnc_machining)

**Optional But Common:**
- `inputs`: Array of entity references in format `id@version`
- `outputs`: Array of entity references in format `id@version`
- `tool`: Tool reference in format `id@version`
- `parameters`: Object containing operation parameters (or `{_redacted: true}` for Level B/C)
- `fidelity`: Expected vs. actual loss tracking
  - `expected`: One of: `lossless`, `geometric_approximation`, `compression_loss`, `summarization_loss`, `quantization_loss`, `sampling_loss`, `custom`
  - `actual`: Object with measured metrics
- `metrics`: Measured outcome metrics (domain-specific)
- `attestation`: Trust/proof information (see Attestation section)
- `realized_capability`: Actual capability used (subset of tool capabilities)

**Advanced Fields (for high-value operations):**
- `sealed`: Sealed subgraph for Level C disclosure (see §2.2.1)
- `reproducibility`: Expected output hash, rerun timeline, tolerance
- `work_proof`: Computational proof (VDF, hashcash)
- `resource_usage`: CPU, GPU, memory, energy metrics

#### 2.2.1 Sealed Subgraph (Level C Disclosure)

Replaces a proprietary pipeline segment with a Merkle commitment while exposing policy compliance.

**Structure:**
```yaml
- id: op_cam_pipeline_sealed
  type: sealed_subgraph
  sealed:
    merkle_root: sha256:deadbeef1234...
    leaves_exposed:
      - role: sub_input
        hash: sha256:input_hash...
      - role: sub_output
        hash: sha256:output_hash...
      - role: intermediate
        hash: sha256:optional_intermediate...
    policy_assertions:
      - id: gg-cam-v1
        result: pass
        signer: did:svc:cam-phoenix
        evidence_hash: sha256:policy_evidence...
  attestation:
    mode: verifiable
    signer: did:svc:cam-phoenix
    signature: ed25519:...
    timestamp: 2025-10-31T09:42:15Z
    multisig:
      threshold: 2
      signers: [did:person:engineer1, did:person:manager]
```

---

### 2.3 Tool / Agent (Who/what did the work)

The actor that performed an operation: software, hardware, AI model, or human.

**Structure:**
```yaml
- id: haas_vf2
  type: Machine
  vendor: Haas
  version: 2.3.1
  capabilities:
    cam:
      axes: 5
      tolerance_mm: 0.01
      materials: [Al6061, Ti6Al4V]
  identity:
    did: did:machine:vf2
    certificate: "ISO-9001-Certified"
  metadata: {}
```

**Required Fields:**
- `id`: Tool identifier
- `type`: One of: `Software`, `Machine`, `Human`, `AIModel`, `Service`

**Optional But Important:**
- `vendor`: Vendor/manufacturer name
- `version`: Version string
- `capabilities`: Object describing what the tool can do
  - Domain-specific (e.g., `print`, `inference`, `cam`)
  - Examples: `max_tokens`, `temperature_range`, `tolerance_mm`, `axes`
- `identity`: Trust anchors
  - `did`: Decentralized identifier (format: `did:{method}:{identifier}`)
  - `certificate`: Certification or license string
- `metadata`: Free-form attributes

---

### 2.4 Attestation (Proof of trust/integrity)

Cryptographically verifiable statements of integrity and authorization.

**Structure:**
```yaml
attestation:
  mode: signed
  signer: did:person:alice
  signature: ed25519:abc123...
  timestamp: 2025-10-31T14:25:36Z
  delegation: did:org:hospital
  claims:
    policy: gg-ai-basic-v1
    results:
      temperature: {lte: 0.3, satisfied: true}
      prompt_length_chars: {lte: 4000, satisfied: true}
  transparency:
    - log_id: did:log:corpA
      entry_id: 0x5f2c8a91
      tree_size: 128734
      inclusion_proof: base64:MIIB...
  multisig:
    threshold: 2
    signers: [did:person:alice, did:person:bob]
  tee:
    technology: intel_sgx
    mr_enclave: 0x12ab...
    quote: base64:AAA...
  work_proof:
    type: vdf_wesolowski
    difficulty: "2^30"
    input: sha256:...
    output: base64:...
```

**Required Fields:**
- `mode`: One of: `basic`, `signed`, `verifiable`, `zk`
- `timestamp`: ISO 8601 datetime

**Conditional Requirements (based on mode):**
- `signed` / `verifiable` / `zk`: MUST include `signer` and `signature`
- `basic`: MUST NOT include `signer` or `signature`

**Signature Format:**
- Pattern: `^(ed25519|ecdsa|rsa):.+$`
- Examples: `ed25519:sig_aabbccdd`, `ecdsa:sig_xyz...`

**Optional Fields:**
- `signer`: DID of the signer
- `signature`: Cryptographic signature
- `delegation`: DID of delegated authority
- `claims`: Attestation claims (policy compliance results)
- `transparency`: Array of transparency log entries (RFC 6962)
- `multisig`: Multi-signature requirement
- `tee`: Trusted execution environment attestation (Intel SGX, AMD SEV, etc.)
- `work_proof`: Computational proof requirement

---

## 3. ROOT DOCUMENT STRUCTURE

**Minimal valid GenesisGraph document:**
```yaml
spec_version: 0.1.0

tools:
  - id: mytool
    type: Software
    version: 1.0

entities:
  - id: input.txt
    type: Text
    version: 1
    hash: sha256:abc123...

  - id: output.txt
    type: Text
    version: 1
    hash: sha256:def456...

operations:
  - id: op1
    type: transform
    inputs: [input.txt@1]
    outputs: [output.txt@1]
    tool: mytool@1.0
```

**Complete root document structure:**
```yaml
spec_version: 0.1.0              # Required: Semantic version (X.Y.Z format)

profile: gg-ai-basic-v1          # Optional: Profile identifier

imports:                         # Optional: Namespace imports
  - https://genesisgraph.dev/ns/core/0.1
  - https://genesisgraph.dev/ns/ai/0.1

namespaces:                      # Optional: Local namespace mappings
  ai: https://genesisgraph.dev/ns/ai/0.1

context:                         # Optional: Execution context
  environment: docker://ubuntu:22.04@sha256:abc123...
  hardware: nvidia_a100
  location: datacenter-us-west-2
  software_env: conda:pytorch_2.1#sha256:...

tools:                           # Array of Tool objects
  - id: ...
    type: ...
    ...

entities:                        # Array of Entity objects
  - id: ...
    type: ...
    ...

operations:                      # Array of Operation objects
  - id: ...
    type: ...
    ...

metadata:                        # Optional: Document-level metadata
  request_id: req-2025-10-31-14-23-11-xyz
  compliance_framework: HIPAA
  retention_policy: 7_years
```

---

## 4. VALIDATION & SCHEMA

### 4.1 JSON Schema

The normative schema is in YAML format: `schema/genesisgraph-core-v0.1.yaml`

**Key validation rules:**
1. `spec_version` must match pattern `^\d+\.\d+\.\d+$`
2. Entities must have either `file` or `uri` (not both required, one required)
3. Hashes must match pattern `^(sha256|sha512|blake3):[a-f0-9]+$`
4. DIDs must match pattern `^did:[a-z0-9]+:[a-zA-Z0-9._-]+$`
5. Timestamps must be valid ISO 8601 format
6. Attestation mode determines required/optional fields

### 4.2 Python Validator Reference

```python
from genesisgraph import GenesisGraphValidator, validate

# Basic usage
validator = GenesisGraphValidator()
result = validator.validate_file("workflow.gg.yaml")

# With schema validation
validator = GenesisGraphValidator(use_schema=True)

# With signature verification
validator = GenesisGraphValidator(verify_signatures=True)

# With transparency log verification
validator = GenesisGraphValidator(verify_transparency=True)

# Check results
if result.is_valid:
    print("Valid!")
else:
    print(result.format_report())
```

**ValidationResult attributes:**
- `is_valid: bool` - Overall validity
- `errors: List[str]` - Validation errors
- `warnings: List[str]` - Non-fatal issues
- `data: Dict` - Parsed document
- `format_report() -> str` - Human-readable report

---

## 5. SELECTIVE DISCLOSURE PATTERNS

GenesisGraph defines three disclosure levels for privacy-preserving provenance:

### 5.1 Level A: Full Disclosure

**Use case:** Internal audit, open research, collaboration  
**What's visible:** All parameters, metrics, configurations, signatures

```yaml
operations:
  - id: op_inference_001
    parameters:
      temperature: 0.2
      prompt: "You are a medical assistant..."
      max_tokens: 512
```

### 5.2 Level B: Partial Attestation Envelope

**Use case:** Prove compliance without revealing trade secrets  
**What's hidden:** Operation parameters  
**What's visible:** Input/output hashes, policy compliance claims, metrics

```yaml
operations:
  - id: op_inference_001
    parameters:
      _redacted: true
    attestation:
      mode: signed
      claims:
        policy: gg-ai-basic-v1
        results:
          temperature: {lte: 0.3, satisfied: true}
          prompt_length_chars: {lte: 4000, satisfied: true}
      transparency:
        - log_id: did:log:audit
          entry_id: 0x5f2c...
          tree_size: 428934
          inclusion_proof: base64:...
```

### 5.3 Level C: Sealed Subgraph

**Use case:** Hide proprietary pipeline while maintaining integrity  
**What's hidden:** Entire subgraph (multiple operations)  
**What's visible:** Input/output hashes, Merkle root, policy assertions

```yaml
operations:
  - id: op_proprietary_pipeline_sealed
    type: sealed_subgraph
    sealed:
      merkle_root: sha256:deadbeef...
      leaves_exposed:
        - role: sub_input
          hash: sha256:input_hash...
        - role: sub_output
          hash: sha256:output_hash...
      policy_assertions:
        - id: iso-9001-2015
          result: pass
          signer: did:org:facility
          evidence_hash: sha256:...
    attestation:
      mode: verifiable
      multisig:
        threshold: 2
        signers: [did:person:engineer, did:person:manager]
```

---

## 6. ENTITY TYPES (Common Examples)

### Data / Knowledge
- `Dataset` - Data collection (CSV, Parquet, HDF5)
- `DataSnapshot` - Point-in-time data version
- `CorpusSnapshot` - Knowledge base snapshot
- `TextTemplate` - Prompt or template

### Models / AI
- `AIModel` - Neural network, LLM, classifier
- `Model` - Generic machine learning model
- `FineTunedModel` - Model after training

### Manufacturing / CAD
- `CADModel` - STEP, IGES, Fusion design file
- `Mesh` - 3D mesh, STL, OBJ
- `Mesh3D` - Explicit 3D mesh
- `GCode` - CNC machining instructions
- `PhysicalPart` - Manufactured or built part

### Media / Content
- `Text` - Text output or document
- `Image` - Raster image
- `Video` - Video file
- `Audio` - Audio recording

### Validation / QC
- `InspectionReport` - Quality control or inspection report
- `VerificationReport` - Validation/test results
- `Certificate` - Compliance or certification document

### Custom
Any custom string following the pattern `[A-Z][a-zA-Z0-9]*`

---

## 7. OPERATION TYPES (Common Examples)

### AI / ML
- `ai_retrieval` - Vector search, RAG retrieval
- `ai_inference` - Model inference, generation
- `ai_moderation` - Content moderation, filtering
- `ai_training` - Model training, fine-tuning
- `ai_evaluation` - Benchmark/evaluation run

### Manufacturing / CAD
- `tessellation` - CAD to mesh conversion
- `slicing` - Model slicing (3D print)
- `cnc_machining` - Subtractive manufacturing
- `3d_printing` - Additive manufacturing
- `quality_inspection` - QC measurement

### Data / Processing
- `data_preparation` - Preprocessing, cleaning
- `data_filtering` - Selection, subsetting
- `aggregation` - Combining datasets
- `analysis` - Statistical analysis

### Human
- `human_review` - Expert review
- `human_annotation` - Labeling, tagging
- `human_approval` - Authorization, sign-off

### Custom
Any custom string following the pattern `[a-z_]+`

---

## 8. DID RESOLUTION & IDENTITY

GenesisGraph supports W3C Decentralized Identifiers (DIDs) for identity and trust.

### Supported DID Methods

#### did:key (Self-describing keys)
No resolution needed; key material embedded in DID.

```
Format: did:key:z{base58-multicodec-encoded-key}

Example:
  did:key:z6Mkfr9fBhVu1gVx3bRR5MNhkB3EsN8hM6x3ZQfXz6Kh3TwM

Usage:
  - No HTTPS required (works offline)
  - Key material publicly available in DID itself
  - Good for: Single-use keys, internal systems, testing
```

**Resolution process:**
1. Decode base58 substring
2. Parse multicodec prefix (0xED for Ed25519)
3. Extract 32-byte public key

#### did:web (Web-based identities)
Resolves to DID document hosted on organization's domain via HTTPS.

```
Format: did:web:{domain}:{optional:path:segments}

Examples:
  did:web:aerospace.example.com
  did:web:aerospace.example.com:engineering:john_smith

Resolution:
  1. Request: https://aerospace.example.com/.well-known/did.json
  2. Or path variant: https://aerospace.example.com/engineering/john_smith/did.json
  3. Returns DID document with verificationMethod array
  4. Extract publicKeyJwk or publicKeyPem
```

**DID Document Structure:**
```json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:web:aerospace.example.com",
  "verificationMethod": [
    {
      "id": "did:web:aerospace.example.com#key-1",
      "type": "Ed25519VerificationKey2020",
      "controller": "did:web:aerospace.example.com",
      "publicKeyJwk": {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": "base64-encoded-key"
      }
    }
  ]
}
```

### Python DID Resolution

```python
from genesisgraph.did_resolver import DIDResolver

resolver = DIDResolver(timeout=10, cache_ttl=300)

# Resolve to public key
public_key = resolver.resolve_to_public_key("did:web:example.com:user1")

# Use for signature verification
verified = resolver.verify_signature(
    message=data,
    signature=sig,
    did="did:web:example.com:user1"
)
```

**Security features:**
- SSRF protection (blocks localhost, private networks)
- Rate limiting (10 requests/minute by default)
- Response size limits (1MB max)
- Caching with TTL (5 minutes default)

---

## 9. CRYPTOGRAPHIC SIGNING

### Supported Algorithms

- **Ed25519** - Recommended (EdDSA, 256-bit keys)
- **ECDSA** - P-256 (Elliptic Curve)
- **RSA** - 2048+ bits (legacy support)

### Signature Process

1. **Canonicalize** operation data to deterministic JSON (no whitespace, sorted keys)
2. **Hash** canonicalized data with SHA-256
3. **Sign** hash with private key
4. **Encode** signature as base64
5. **Attach** to attestation

**Signature format:**
```
{algorithm}:{base64-encoded-signature}

Examples:
  ed25519:sig_aabbccdd
  ecdsa:sig_xyz...
  rsa:sig_longbase64...
```

### Python Signing (Reference Implementation)

```python
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64
import json

def sign_operation(operation_data, private_key_pem):
    # Canonicalize
    canonical = json.dumps(operation_data, sort_keys=True, separators=(',', ':'))
    
    # Load key
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    
    # Sign
    signature = private_key.sign(canonical.encode())
    
    # Encode
    return f"ed25519:{base64.b64encode(signature).decode()}"
```

---

## 10. TRANSPARENCY LOG ANCHORING (RFC 6962)

Append-only logs for non-repudiation and time-ordering across organizational boundaries.

**Use cases:**
- Audit trails for regulated industries
- Time-ordering operations across organizations
- Non-repudiation of process execution
- Multi-party witness requirements

**Structure:**
```yaml
attestation:
  transparency:
    - log_id: did:log:corpA
      entry_id: 0x5f2c8a91
      tree_size: 128734
      inclusion_proof: base64:MIIB...
      consistency_proof: base64:MIIB...  # Optional
```

**Fields:**
- `log_id`: DID or URI identifying the log
- `entry_id`: Entry sequence number in log
- `tree_size`: Total tree size at time of inclusion
- `inclusion_proof`: Base64-encoded RFC 6962 inclusion proof
- `consistency_proof`: Optional consistency proof (for multiple logs)

**Verification process:**
1. Fetch log at tree_size
2. Verify inclusion proof against Merkle tree
3. Optionally verify consistency across multiple logs
4. Confirm operation hash matches leaf node

---

## 11. ATTESTATION MODES

### Mode: basic
Simple timestamp, no cryptography required.

```yaml
attestation:
  mode: basic
  timestamp: 2025-10-31T14:25:36Z
```

**Use case:** Trusted environments where HTTPS/audit logs are sufficient

### Mode: signed
Cryptographically signed by the signer.

```yaml
attestation:
  mode: signed
  signer: did:key:z6Mk...
  signature: ed25519:sig_aabbccdd
  timestamp: 2025-10-31T14:25:36Z
```

**Use case:** Operations performed by specific tools/services

### Mode: verifiable
Signed and verifiable via resolvable DID (did:web, etc.)

```yaml
attestation:
  mode: verifiable
  signer: did:web:example.com:user1
  signature: ed25519:sig_aabbccdd
  timestamp: 2025-10-31T14:25:36Z
  delegation: did:org:example-corp
```

**Use case:** Operations requiring verifiable human/organizational authority

### Mode: zk
Zero-knowledge proof of compliance (advanced).

```yaml
attestation:
  mode: zk
  timestamp: 2025-10-31T14:25:36Z
  # Additional zk proof material (implementation-defined)
```

**Use case:** Prove compliance without revealing parameters

---

## 12. FIDELITY & LOSS TRACKING

Explicitly capture what information is lost or approximated at each step.

```yaml
fidelity:
  expected: geometric_approximation
  actual:
    tolerance_mm: 0.05
    surface_finish_ra: 0.8
```

**Expected loss types:**
- `lossless` - No information loss
- `geometric_approximation` - CAD → mesh (tolerance specified)
- `compression_loss` - Model quantization, model compression
- `summarization_loss` - Text summarization, RAG
- `quantization_loss` - Bit depth reduction
- `sampling_loss` - Statistical sampling
- `custom` - Domain-specific loss

**Actual metrics:** Domain-specific measured loss values

**Why it matters:**
- Legal defensibility ("we disclosed the approximation")
- Quality control during downstream use
- Scientific honesty in research
- Safety audits for AI summarization/redaction

---

## 13. PROFILES & DOMAIN-SPECIFIC EXTENSIONS

Profiles extend the core schema for specific domains/industries.

### Standard Profiles (v0.2)

**gg-ai-basic-v1**
- For AI/ML inference pipelines
- Requires: model identity, temperature/prompt settings, human review
- Supports: retrieval, inference, moderation operations

**gg-cam-v1**
- For manufacturing workflows
- Requires: tool capabilities, tolerance specifications, QC results
- Supports: tessellation, slicing, machining operations

**gg-sci-v1** (planned)
- For scientific reproducibility
- Will require: dataset snapshots, preprocessing scripts, model parameters

**gg-media-v1** (planned)
- For content authenticity (C2PA integration)
- Will require: edit operations, export settings, creator identity

### Custom Profiles

Organizations can define their own profiles:

```yaml
profile: myorg-custom-v1

# Profile document (myorg-custom-v1.schema.yaml)
title: MyOrg Custom Profile
extends: gg-ai-basic-v1
required_fields:
  operations:
    - required: [internal_review_id]
      description: "Must track internal review gate"
vocabularies:
  custom_op_types: [internal_review, compliance_check]
```

---

## 14. FILE FORMAT & SERIALIZATION

### Authoring Format: YAML

Human-friendly format for creating documents.

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
    hash: sha256:abc123...
operations:
  - id: op1
    type: transform
```

**Filename convention:** `*.gg.yaml`

### Canonical Format: JSON

Deterministic format for signing and verification.

**Rules for canonicalization:**
1. No whitespace (single-line output)
2. Keys sorted alphabetically
3. UTF-8 encoding
4. Separators: `,` and `:`

```json
{"entities":[{"hash":"sha256:abc123","id":"input","type":"Text","version":"1"}],"operations":...}
```

### Storage Format: Either

Both YAML and JSON are valid for storage/transmission. Convert between formats as needed.

```bash
# YAML to JSON
python -c "import yaml, json; print(json.dumps(yaml.safe_load(open('x.yaml'))))"

# JSON to YAML
python -c "import yaml, json; print(yaml.dump(json.load(open('x.json'))))"
```

---

## 15. SECURITY CONSIDERATIONS FOR SDK DEVELOPERS

### Input Validation

**Size limits (prevent DoS):**
- Max entities: 10,000
- Max operations: 10,000
- Max tools: 1,000
- Max ID length: 256 characters
- Max hash length: 512 characters
- Max signature length: 4,096 characters

### Signature Verification

**Always verify in critical contexts:**
```python
validator = GenesisGraphValidator(verify_signatures=True)
result = validator.validate(data)
if not result.is_valid:
    raise ValidationError(result.format_report())
```

### DID Resolution Security

**SSRF Protection (did:web):**
- Blocks: localhost, 127.0.0.1, 169.254.169.254 (AWS metadata)
- Blocks: Private networks (10.0.0.0/8, 192.168.0.0/16, etc.)
- Timeout: 10 seconds per request
- Response limit: 1MB max

**Rate limiting:**
- 10 requests per minute by default
- Implement backoff on 429 responses

### Hash Verification

**Always verify file hashes when available:**
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

## 16. INTEGRATION PATTERNS FOR SDK BUILDERS

### Pattern 1: Wrapper (Post-Hoc)

Wrap existing tool calls to generate GenesisGraph documents after execution.

```python
# Pseudo-code
def wrapped_inference(model, prompt, temperature):
    start_time = time.time()
    result = model.generate(prompt, temperature=temperature)
    end_time = time.time()
    
    # Generate GenesisGraph document
    operation = {
        "id": f"op_inference_{uuid()}",
        "type": "ai_inference",
        "inputs": ["prompt@1"],
        "outputs": ["result@1"],
        "tool": f"{model.name}@{model.version}",
        "parameters": {
            "temperature": temperature,
            "prompt_length": len(prompt)
        },
        "metrics": {
            "latency_ms": (end_time - start_time) * 1000
        }
    }
    
    return result, operation
```

**Pros:**
- No changes to existing code
- Works with third-party tools
- Fastest to implement

**Cons:**
- May miss internal details
- Post-hoc tracing possible
- Limited fidelity information

### Pattern 2: Native Integration

Integrate GenesisGraph directly into tool/SDK.

```python
class GenesisGraphAIModel:
    def __init__(self, model, operations_list):
        self.model = model
        self.operations = operations_list
    
    def generate(self, prompt, temperature):
        start = time.time()
        result = self.model.generate(prompt, temperature=temperature)
        elapsed = time.time() - start
        
        # Record operation
        self.operations.append({
            "type": "ai_inference",
            "inputs": [prompt],
            "outputs": [result],
            "parameters": {"temperature": temperature},
            "metrics": {"latency_ms": elapsed * 1000}
        })
        
        return result
```

**Pros:**
- Complete information capture
- Better performance tracking
- Fine-grained control

**Cons:**
- Requires code changes to tool
- SDK dependency
- More maintenance

### Pattern 3: Operator / Plugin

Provide hooks in tool for GenesisGraph observers.

```python
class GenesisGraphObserver:
    def on_operation_start(self, operation_id, inputs, parameters):
        pass
    
    def on_operation_end(self, operation_id, outputs, metrics):
        pass

# Tool registration
model.register_observer(GenesisGraphObserver())
```

**Pros:**
- Non-invasive
- Real-time observation
- Pluggable architecture

**Cons:**
- Requires observer support in tool
- May have performance overhead

---

## 17. EXAMPLE WALKTHROUGH: Medical AI Pipeline

**Scenario:** Regulated medical Q&A system with human review

**Design considerations:**
1. Retrieval from corpus (version controlled)
2. Inference with controlled parameters
3. Moderation filtering
4. Human clinician review (signed approval)
5. Level B disclosure (policy claims visible, prompts hidden)

**Document structure:**

```yaml
spec_version: 0.1.0
profile: gg-ai-basic-v1

context:
  environment: docker://ubuntu:22.04@sha256:abc...
  hardware: nvidia_a100
  location: datacenter-us-west-2

tools:
  - id: retrieval_engine
    type: Software
    vendor: InternalAI
    version: 3.2.1
    capabilities:
      search:
        max_results: 100
        vector_similarity: cosine

  - id: llama3_70b
    type: AIModel
    vendor: Meta
    version: 3.0
    capabilities:
      inference:
        max_tokens: 8192
        temperature_range: [0.0, 2.0]

  - id: moderation_filter
    type: Software
    vendor: InternalAI
    version: 2.1.0

  - id: clinician_reviewer
    type: Human
    identity:
      did: did:person:dr_sarah_chen

entities:
  - id: medical_corpus
    type: Dataset
    version: 2025-10-15
    uri: s3://kb/corpus.parquet
    hash: sha256:a1b2c3d4...

  - id: retrieval_results
    type: Dataset
    version: 1
    hash: sha256:f1e2d3c4...
    derived_from: [medical_corpus@2025-10-15]

  - id: raw_answer
    type: Text
    version: 1
    hash: sha256:fedcba09...
    derived_from: [retrieval_results@1]

  - id: moderated_answer
    type: Text
    version: 1
    hash: sha256:aabbccdd...
    derived_from: [raw_answer@1]

  - id: final_answer
    type: Text
    version: 1
    hash: sha256:99887766...
    derived_from: [moderated_answer@1]

operations:
  # Level B: Parameters redacted
  - id: op_retrieval_001
    type: ai_retrieval
    inputs: [medical_corpus@2025-10-15]
    outputs: [retrieval_results@1]
    tool: retrieval_engine@3.2.1
    parameters:
      _redacted: true
    attestation:
      mode: signed
      signer: did:svc:retrieval-prod
      signature: ed25519:sig1_...
      timestamp: 2025-10-31T14:23:11Z
      claims:
        policy: gg-ai-basic-v1
        results:
          max_results: {lte: 20, satisfied: true}
          similarity_threshold: {gte: 0.7, satisfied: true}

  - id: op_inference_001
    type: ai_inference
    inputs: [retrieval_results@1]
    outputs: [raw_answer@1]
    tool: llama3_70b@3.0
    parameters:
      _redacted: true
    attestation:
      mode: signed
      claims:
        policy: gg-ai-basic-v1
        results:
          temperature: {lte: 0.3, satisfied: true}
          prompt_length: {lte: 4000, satisfied: true}

  - id: op_moderation_001
    type: ai_moderation
    inputs: [raw_answer@1]
    outputs: [moderated_answer@1]
    tool: moderation_filter@2.1.0
    parameters:
      _redacted: true
    attestation:
      mode: signed
      claims:
        policy: gg-ai-basic-v1
        results:
          harmful_content: {result: "pass"}

  # Human review with verifiable signature
  - id: op_human_review_001
    type: human_review
    inputs: [moderated_answer@1]
    outputs: [final_answer@1]
    tool: clinician_reviewer@
    parameters:
      approval_granted: true
      review_time_seconds: 142
    attestation:
      mode: verifiable
      signer: did:person:dr_sarah_chen
      signature: ed25519:sig4_...
      timestamp: 2025-10-31T14:25:36Z
      delegation: did:org:hospital-system

metadata:
  compliance_framework: HIPAA
  disclosure_level: partial_envelope
```

**Key points:**
- Corpus version pinned (reproducibility)
- Parameters redacted (Level B)
- Policy compliance claims visible
- Human review verifiable with DID
- All timestamps recorded
- Metrics available for audit

---

## 18. QUICK REFERENCE: Common Patterns

### Pattern: File-based Workflow

```yaml
entities:
  - id: source_code
    type: SourceCode
    version: 1.0
    file: ./src/main.py
    hash: sha256:abc123...

operations:
  - id: op_test
    type: automated_test
    inputs: [source_code@1.0]
    outputs: [test_results@1]
    tool: pytest@7.0
    metrics:
      tests_passed: 42
      tests_failed: 0
```

### Pattern: External/Remote Reference

```yaml
entities:
  - id: huggingface_model
    type: AIModel
    version: 2.0
    uri: https://huggingface.co/meta-llama/Llama-2-7b
    hash: sha256:abc123...  # Model checkpoint hash
```

### Pattern: Multi-step Transformation

```yaml
entities:
  - id: raw_data
    type: Dataset
    version: 1
    derived_from: []
  
  - id: cleaned_data
    type: Dataset
    version: 1
    derived_from: [raw_data@1]
  
  - id: features
    type: Dataset
    version: 1
    derived_from: [cleaned_data@1]

operations:
  - id: op_clean
    inputs: [raw_data@1]
    outputs: [cleaned_data@1]
  
  - id: op_featurize
    inputs: [cleaned_data@1]
    outputs: [features@1]
```

### Pattern: Parallel Operations

```yaml
operations:
  - id: op_task_a
    inputs: [shared_input@1]
    outputs: [output_a@1]
  
  - id: op_task_b
    inputs: [shared_input@1]
    outputs: [output_b@1]
  
  - id: op_combine
    inputs: [output_a@1, output_b@1]
    outputs: [final_output@1]
```

---

## 19. RECOMMENDED NEXT STEPS FOR SDK BUILDERS

1. **Study the examples**
   - Review all 3 disclosure levels: `examples/level-*.gg.yaml`
   - Understand entity relationships and lineage

2. **Choose your integration pattern**
   - Wrapper (easiest)
   - Native (most complete)
   - Observer (most flexible)

3. **Implement core data structures**
   - Entity class/struct
   - Operation class/struct
   - Tool class/struct
   - Attestation class/struct

4. **Add validation**
   - Schema validation (use bundled JSON Schema)
   - Hash verification when possible
   - Signature verification for trusted operations

5. **Support YAML/JSON serialization**
   - Parse YAML input
   - Generate valid YAML/JSON output
   - Support round-trip conversion

6. **Add signature support (optional but recommended)**
   - Implement Ed25519 signing
   - Add DID resolution (at minimum did:key)
   - Verify signatures for critical operations

7. **Write documentation**
   - Show examples for your domain
   - Document integration pattern used
   - Create quick-start guide

8. **Test thoroughly**
   - Validate against schema
   - Test signature verification
   - Test round-trip serialization

---

## 20. USEFUL RESOURCES

**Core Documentation**
- `/home/user/genesisgraph/spec/MAIN_SPEC.md` - Complete specification (887 lines)
- `/home/user/genesisgraph/schema/genesisgraph-core-v0.1.yaml` - Normative JSON Schema
- `/home/user/genesisgraph/QUICKSTART.md` - 5-minute tutorial

**Examples**
- `/home/user/genesisgraph/examples/level-a-full-disclosure.gg.yaml` - AI medical Q&A
- `/home/user/genesisgraph/examples/level-b-partial-envelope.gg.yaml` - Partial disclosure
- `/home/user/genesisgraph/examples/level-c-sealed-subgraph.gg.yaml` - Manufacturing
- `/home/user/genesisgraph/examples/workflow-with-did-web.gg.yaml` - did:web identities

**Standards & References**
- W3C DID Core: https://www.w3.org/TR/did-core/
- did:key Method: https://w3c-ccg.github.io/did-method-key/
- did:web Method: https://w3c-ccg.github.io/did-method-web/
- RFC 6962 (Certificate Transparency / Merkle Logs): https://tools.ietf.org/html/rfc6962

**Related Specs**
- W3C PROV-O (ontology): https://www.w3.org/TR/prov-o/
- SPDX (software supply chain): https://spdx.dev/
- C2PA (media authenticity): https://c2pa.org/
- SLSA (build integrity): https://slsa.dev/

---

## Summary

GenesisGraph is designed to be:
- **Simple to start:** Basic document with just IDs and hashes
- **Progressive:** Add trust gradually (timestamps → signatures → DIDs)
- **Domain-agnostic:** Apply to AI, manufacturing, science, media
- **Privacy-preserving:** Three disclosure levels without compromising integrity
- **Standardized:** W3C-aligned formats, open governance model

For SDK developers, focus on:
1. Parsing/generating valid YAML/JSON structure
2. Implementing the four data types (Entity, Operation, Tool, Attestation)
3. Supporting validation against the normative schema
4. Optional: signature verification and DID resolution
5. Clear documentation with domain-specific examples

Start simple, build iteratively, and leverage the reference implementation for guidance.

