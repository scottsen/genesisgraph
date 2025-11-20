# GenesisGraph FAQ

Frequently asked questions about adopting, implementing, and using GenesisGraph.

---

## General Questions

### What is GenesisGraph?

GenesisGraph is an **open standard format for verifiable process provenance**. It describes how artifacts (files, parts, outputs) were produced through a chain of operations, tools, and attestations.

Think of it as a verifiable recipe that proves:
- What was made
- How it was transformed
- Which tools did the work
- With what fidelity
- Signed by whom

### Why should I use GenesisGraph instead of just documenting my process?

**Documentation can be edited.** GenesisGraph provides:

1. **Cryptographic proof** - Hashes and signatures prevent silent edits
2. **Machine verification** - Auditors/regulators can automatically validate claims
3. **Portable provenance** - Works across tools, organizations, industries
4. **Selective disclosure** - Prove compliance without revealing trade secrets
5. **Standard format** - Interoperable with PROV-O, SLSA, SPDX, C2PA

**Example:** "We followed the process" (trust-based) vs "Here's the cryptographic proof" (verifiable).

### Is this just for compliance-heavy industries?

No. GenesisGraph is valuable wherever **"prove how you made this"** matters:

- **AI consultants:** Prove you did 12 retrieval iterations, not one ChatGPT query
- **Researchers:** Reproducible publications with exact software versions
- **Makers:** Version control for parametric designs
- **Manufacturers:** Supplier trust without revealing IP
- **Content creators:** Prove authenticity of AI-generated media

**Start simple** (basic timestamps), **add trust when needed** (signatures, DIDs).

---

## Comparison Questions

### Why not just use W3C PROV-O?

**PROV-O is excellent** for semantic web applications but has gaps for practical provenance:

| Feature | PROV-O | GenesisGraph |
|---------|--------|-------------|
| **Semantic web integration** | ✓ Native RDF | ✓ Optional JSON-LD export |
| **Human-readable authoring** | ✗ RDF/XML verbose | ✓ YAML-first |
| **Selective disclosure** | ✗ Not addressed | ✓ Merkle commitments, sealed subgraphs |
| **Capability tracking** | ✗ Not standardized | ✓ First-class (tool.capabilities) |
| **Loss/fidelity semantics** | ✗ Not addressed | ✓ First-class (operation.fidelity) |
| **Progressive trust modes** | ✗ No guidance | ✓ basic → signed → verifiable → zk |
| **Cryptographic attestation** | ✗ Not specified | ✓ Timestamps, signatures, DIDs, TEE quotes |

**GenesisGraph is the practical bridge to PROV-O**, not a replacement. You can:
1. Author in GenesisGraph (YAML)
2. Validate with JSON Schema
3. Export to PROV-O (JSON-LD) when needed

### Why not just use SLSA (Supply chain Levels for Software Artifacts)?

**SLSA is great for software builds** but GenesisGraph covers more:

| Feature | SLSA | GenesisGraph |
|---------|------|-------------|
| **Software supply chain** | ✓ Perfect fit | ✓ Supported |
| **Manufacturing (physical parts)** | ✗ Not addressed | ✓ CAD/CAM/CNC provenance |
| **AI/ML pipelines** | ✗ Not addressed | ✓ Data → model → inference |
| **Scientific research** | ✗ Not addressed | ✓ Dataset → analysis → publication |
| **Media/content** | ✗ Not addressed | ✓ C2PA-compatible |
| **Selective disclosure** | ✗ Limited | ✓ Levels A/B/C |

**Use both:** GenesisGraph for your workflow, export SLSA provenance for software artifacts.

### Why not just use SPDX?

**SPDX is for software bill of materials (SBOM).** GenesisGraph is for **process provenance**.

- **SPDX:** "This binary contains these libraries"
- **GenesisGraph:** "This binary was produced by these operations with these tools"

**Use both:** SPDX for dependency tracking, GenesisGraph for build provenance.

### Why not just use C2PA (Content Provenance and Authenticity)?

**C2PA is for media files.** GenesisGraph is domain-agnostic.

| Feature | C2PA | GenesisGraph |
|---------|------|-------------|
| **Media files (images/video/audio)** | ✓ Perfect fit | ✓ Supported |
| **Manufacturing** | ✗ Not addressed | ✓ CAD/CAM/parts |
| **AI pipelines** | ✗ Not addressed | ✓ Data → model → inference |
| **Scientific workflows** | ✗ Not addressed | ✓ Dataset → analysis |
| **Cross-domain interop** | ✗ Media-specific | ✓ Universal pattern |

**GenesisGraph profile:** `gg-media-c2pa-v1` for C2PA-compatible provenance.

---

## Technical Questions

### Do I need blockchain?

**No.** GenesisGraph works with simple hashes and timestamps. Blockchain is **optional** for:

- Public transparency logs (Certificate Transparency-style)
- Immutable anchoring (Ethereum, etc.)
- Multi-party witness consensus

**Start simple:** Hashes + timestamps + signatures.
**Add blockchain later** if your use case requires public verifiability.

### What cryptography do I need?

**Minimum (Level: basic):**
- SHA-256 hashing (for content integrity)
- ISO 8601 timestamps (for ordering)

**Recommended (Level: signed):**
- Ed25519 signatures (fast, small, secure)
- X.509 certificates (PKI integration)

**Advanced (Level: verifiable):**
- Decentralized Identifiers (DIDs)
- Verifiable Credentials (VCs)

**Cutting-edge (Level: zk):**
- Zero-knowledge proofs (selective disclosure)
- TEE attestations (Intel SGX, AMD SEV)
- Merkle trees (sealed subgraphs)

**You control the complexity.** Start basic, upgrade progressively.

### Can I start simple and add trust later?

**Yes!** Progressive trust modes are core to GenesisGraph:

```yaml
# Stage 1: Basic (hobby project)
attestation:
  mode: basic
  timestamp: 2025-10-31T10:00:00Z

# Stage 2: Signed (professional)
attestation:
  mode: signed
  signer: did:person:jane_doe
  signature: ed25519:abc123...
  timestamp: 2025-10-31T10:00:00Z

# Stage 3: Verifiable (regulated industry)
attestation:
  mode: verifiable
  signer: did:person:dr_sarah_chen
  signature: ed25519:def456...
  timestamp: 2025-10-31T10:00:00Z
  delegation: did:org:hospital_system
  witnesses:
    - did:person:supervisor_bob

# Stage 4: Zero-knowledge (aerospace IP protection)
attestation:
  mode: zk
  sealed_subgraph:
    merkle_root: sha256:ghi789...
  tee_quote:
    platform: intel_sgx
    enclave_hash: sha256:jkl012...
```

### What file formats does GenesisGraph support?

**GenesisGraph doesn't replace file formats** - it points to them.

**Authoring:** YAML (human-friendly)
**Validation:** JSON Schema
**Export:** JSON, JSON-LD (PROV-O), XML (if needed)

**Referenced artifacts:** Anything with a hash (STL, PDF, CSV, MP4, DICOM, etc.)

### How do I validate a GenesisGraph document?

**Option 1: JSON Schema validator**

```bash
npm install -g ajv-cli
ajv validate -s schema/genesisgraph-core-v0.1.yaml -d workflow.gg.yaml
```

**Option 2: Python verification scripts**

```bash
pip install pyyaml cryptography
python scripts/verify_sealed_subgraph.py workflow.gg.yaml
```

**Option 3: Future CLI**

```bash
gg validate workflow.gg.yaml
gg verify workflow.gg.yaml --check-signatures
```

---

## Implementation Questions

### How hard is it to add GenesisGraph to my tool?

**It depends on your integration pattern:**

| Pattern | Effort | Example |
|---------|--------|---------|
| **Wrapper** (don't control tool) | 200 lines | Wrap OpenAI API calls |
| **Native export** (control tool) | 500-1000 lines | TiaCAD integration |
| **Post-hoc reconstruction** | Variable | Parse logs/git commits |
| **Orchestrator plugin** | 300-500 lines | Airflow DAG converter |

**Start with wrapper pattern** - easiest, fastest, no tool modifications needed.

### What programming languages are supported?

**GenesisGraph is a data format**, not a library. Use any language that can:
- Read/write YAML or JSON
- Compute SHA-256 hashes
- Generate ISO 8601 timestamps

**Example libraries:**

- **Python:** PyYAML, hashlib, datetime
- **JavaScript:** js-yaml, crypto, Date
- **Go:** gopkg.in/yaml.v3, crypto/sha256, time
- **Rust:** serde_yaml, sha2, chrono
- **Java:** SnakeYAML, MessageDigest, Instant

**Reference implementations:** See `USE_CASES.md` for Python examples.

### Can I use GenesisGraph with my existing workflow?

**Yes.** Three approaches:

**1. Wrapper (no changes to existing tools)**
```python
# Existing code
response = openai.ChatCompletion.create(...)

# With GenesisGraph wrapper
client = OpenAIWithProvenance(api_key)
response = client.chat_completion(...)
client.export_provenance("workflow.gg.yaml")
```

**2. Post-hoc (reconstruct from logs)**
```bash
# Parse existing logs/commits
parse_build_logs.py build.log > workflow.gg.yaml
```

**3. Native (modify tool to emit provenance)**
```bash
# Add --export-provenance flag
mytool build design.yaml --export-provenance
```

### What if my tool doesn't support DIDs/signatures yet?

**Start with basic attestation:**

```yaml
attestation:
  mode: basic
  timestamp: 2025-10-31T10:00:00Z
```

**Upgrade to signatures later:**

```yaml
attestation:
  mode: signed
  signer: "jane.doe@company.com"  # Email-based identity
  signature: ed25519:abc123...
  timestamp: 2025-10-31T10:00:00Z
```

**Add DIDs when needed:**

```yaml
attestation:
  mode: verifiable
  signer: did:person:jane_doe  # Decentralized identity
  signature: ed25519:def456...
  timestamp: 2025-10-31T10:00:00Z
```

---

## Selective Disclosure Questions

### What is selective disclosure?

**Selective disclosure** lets you **prove process compliance without revealing all parameters**.

**Example:** Aerospace supplier proves ISO-9001 compliance without revealing proprietary CAM toolpaths.

**Three levels:**

- **Level A (Full):** All parameters visible
- **Level B (Partial):** Parameters hidden, policy claims visible
- **Level C (Sealed):** Entire subgraph sealed with Merkle commitment

**See:** `spec/MAIN_SPEC.md` §9.2 for details.

### When should I use sealed subgraphs (Level C)?

Use Level C when you need to:

1. **Prove compliance** (ISO-9001, AS9100, FDA) without revealing **IP** (toolpaths, prompts, algorithms)
2. **Enable audits** without **competitive disadvantage**
3. **Provide transparency** to customers while **protecting trade secrets**

**Examples:**
- Manufacturing: Prove tolerance compliance, hide CNC toolpaths
- AI: Prove human-in-loop, hide proprietary prompts
- Pharmaceuticals: Prove GMP compliance, hide synthesis parameters

### How does Merkle commitment work?

**Simplified:**

1. **Hash each parameter**
   ```
   param1: "tool_diameter=6.35mm" → sha256:abc123...
   param2: "feed_rate=1000mm/min" → sha256:def456...
   param3: "spindle_rpm=6000" → sha256:ghi789...
   ```

2. **Combine into Merkle tree**
   ```
         root: sha256:xyz999...
           /              \
    sha256:abc123    sha256:def456
   ```

3. **Publish only root hash**
   ```yaml
   sealed_subgraph:
     merkle_root: sha256:xyz999...
   ```

4. **Optionally reveal specific parameters** (with inclusion proof)

**Benefit:** Auditors verify root hash matches commitment, you prove compliance without revealing all parameters.

### Can I mix disclosure levels in one document?

**Yes!** Common pattern:

```yaml
operations:
  - id: cad_build
    type: parametric_cad_generation
    parameters:  # Level A: Full disclosure
      plate_width: 100
      plate_height: 75

  - id: cam_toolpath
    type: toolpath_generation
    sealed_subgraph:  # Level C: Sealed
      merkle_root: sha256:abc123...
    policy_assertions:
      - claim: iso_9001
        result: pass

  - id: cnc_machining
    type: cnc_machining
    parameters:  # Level A: Full disclosure
      machine_id: haas_vf2_sn_12345
      material: aluminum_7075
```

**Why:** CAD parameters are public (design intent), CAM is proprietary (competitive advantage), CNC is auditable (compliance requirement).

---

## Adoption Questions

### Who is already using GenesisGraph?

**Status (v0.2):** Early adoption, reference implementations in progress.

**Current integrations:**
- **TiaCAD** (parametric CAD/CAM) - Production implementation underway
- **AI workflow wrappers** - Python reference implementations

**Future targets:**
- Scientific workflow engines (Nextflow, Snakemake)
- CI/CD platforms (GitHub Actions, GitLab CI)
- Media tools (Adobe, DaVinci Resolve)
- Manufacturing platforms (Fusion 360, Onshape)

**Adoption strategy:** Start with wrappers (don't require tool vendors), demonstrate value, vendors add native support.

### How do I convince my team/organization to adopt this?

**Focus on business value, not technology:**

**For AI teams:**
> "We can now prove to clients that our $2000 consulting fee reflects 12 retrieval iterations and expert review, not a $20 ChatGPT query. It's provable, not trust-based."

**For manufacturers:**
> "We can win aerospace contracts by proving ISO-9001 compliance without revealing our proprietary CAM toolpaths. Competitors can't match this."

**For researchers:**
> "We can attach verifiable provenance to publications, making our work reproducible and increasing citations. Reviewers can verify our exact methodology."

**For regulators/auditors:**
> "We replace 'trust us' with machine-verifiable proof. FDA/ISO audits become faster and cheaper."

**Start small:**
1. One pilot project
2. Demonstrate value (faster audits, customer trust, IP protection)
3. Expand adoption

### What's the roadmap for GenesisGraph?

**v0.2 (Current):** Public working draft
- Core specification with selective disclosure
- JSON Schema validation
- Certificate Transparency integration (RFC 6962)
- did:web organizational identity support
- Production signature verification
- Reference examples
- TiaCAD integration in progress

**v0.5 (6 months):** Community feedback
- CLI tools (`gg validate`, `gg verify`, `gg viz`)
- Python/JavaScript libraries
- 3+ production integrations
- Domain profiles (gg-ai, gg-cam, gg-bio)

**v1.0 (12 months):** Formal release
- Stable specification
- Reference implementations in 3+ languages
- 10+ tool integrations
- W3C Community Group or LF AI & Data engagement

**v2.0+ (24 months):** Ecosystem maturity
- Major platform integrations (Hugging Face, GitHub Actions)
- Formal standardization (W3C Recommendation or ISO standard)
- "Show me the GenesisGraph" becomes standard procurement language

### Can I contribute?

**Yes!** GenesisGraph succeeds through community adoption.

**Ways to contribute:**

1. **Integrate with your tool** - Share implementation guides
2. **Create domain profiles** - Formalize gg-bio, gg-chem, gg-finance
3. **Write examples** - Real-world use cases
4. **Build libraries** - Python, JavaScript, Go, Rust implementations
5. **Report issues** - Spec ambiguities, integration challenges
6. **Improve docs** - Tutorials, walkthroughs, translations

**License:** Apache 2.0 (free to use, modify, distribute)

---

## Security & Privacy Questions

### How secure is GenesisGraph?

**GenesisGraph is as secure as your cryptography:**

- **Basic mode:** Timestamp integrity (no security)
- **Signed mode:** Ed25519/RSA signatures (strong security)
- **Verifiable mode:** DID-based attestation + multi-party witness (very strong)
- **ZK mode:** Zero-knowledge proofs + TEE quotes (maximum security)

**Best practices:**
1. Use Ed25519 signatures (not SHA-1)
2. Protect private keys (HSMs for production)
3. Rotate keys regularly
4. Use DIDs for long-term identity
5. Anchor commitments in transparency logs

### Can GenesisGraph leak sensitive information?

**Only if you put it there.** GenesisGraph respects your disclosure choices:

**Level A (Full):** Everything visible (use for internal/open projects)
**Level B (Partial):** Parameters redacted, claims visible (use for regulatory compliance)
**Level C (Sealed):** Entire subgraph sealed (use for IP protection)

**Never include:**
- API keys, passwords, secrets
- PII (personal identifiable information) without consent
- ITAR/export-controlled data
- Unpublished research data

**Use parameters redaction:**
```yaml
parameters:
  _redacted: true  # Hide all parameters
claims:
  temperature_constraint: "temperature ≤ 0.3: satisfied"
```

### How does GenesisGraph handle GDPR/privacy?

**GenesisGraph is provenance, not data.** It points to artifacts, doesn't store them.

**GDPR compliance:**

1. **Don't include PII** in provenance (hash references instead)
2. **Use sealed subgraphs** for sensitive operations
3. **Redact human identities** when possible
4. **Right to erasure:** Delete artifacts, provenance stays (with broken references)

**Example (privacy-preserving):**
```yaml
entities:
  - id: patient_data
    type: Dataset
    hash: sha256:abc123...  # Hash reference, not data
    # NO: patient_name: "John Doe"

tools:
  - id: clinician
    type: Human
    identity:
      did: did:role:medical_reviewer  # Role, not individual
    # NO: name: "Dr. Sarah Chen"
```

---

## Business Questions

### How much does GenesisGraph cost?

**$0.** GenesisGraph is **Apache 2.0 open source** - free to use, modify, and distribute.

**No fees for:**
- Specification access
- Schema files
- Reference implementations
- Validation tools

**Potential future costs (optional):**
- **Commercial verification SaaS** (turnkey verifier for non-technical users)
- **Consulting/integration** (professional services)
- **Premium tooling** (enterprise-grade CLI, dashboards)

**Core standard remains free forever.**

### Who owns GenesisGraph?

**No one.** GenesisGraph is community-governed open standard.

**Current status:** Individual stewardship (v0.2 public working draft)
**Future governance:** W3C Community Group or Linux Foundation AI & Data

**No vendor lock-in. No licensing fees. No IP claims.**

### Can I use GenesisGraph commercially?

**Yes.** Apache 2.0 license permits:
- ✓ Commercial use
- ✓ Modification
- ✓ Distribution
- ✓ Private use
- ✓ Patent grant

**You can:**
- Sell tools that emit GenesisGraph
- Offer verification services
- Build SaaS platforms
- Integrate into proprietary products

**You must:**
- Include license and copyright notice
- State changes made to original

**See:** Apache 2.0 license for full terms.

---

## Still Have Questions?

**Documentation:**
- **Quick Start:** `QUICKSTART.md`
- **Use Cases:** `USE_CASES.md`
- **Specification:** `spec/MAIN_SPEC.md`
- **Strategic Context:** `STRATEGIC_CONTEXT.md`

**Examples:**
- `examples/level-a-full-disclosure.gg.yaml`
- `examples/level-b-partial-envelope.gg.yaml`
- `examples/level-c-sealed-subgraph.gg.yaml`

**Community:**
- GitHub Issues (coming soon)
- Discussions forum (coming soon)
- Slack/Discord (coming soon)

---

> Every artifact has a beginning. GenesisGraph is how we prove it.
