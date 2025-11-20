# GenesisGraph Specification Blueprint

**Working Draft — October 2025**
**Subtitle:** The Open Standard for Verifiable Process Provenance

---

## 0. What This Document Is

This document is the blueprint for the GenesisGraph standard.

It defines:

* What GenesisGraph is
* Why it matters in the real world
* The core data model
* How it's serialized, validated, signed, and audited
* How it will be governed as an open standard

It is meant as the one document future contributors, companies, auditors, and regulators can align on before we split into "formal spec," "schema," "profiles," etc.

Think of this as the playbook.

---

## 1. The Problem GenesisGraph Solves

### 1.1 Today's reality

Everything we build now is the result of a pipeline:

* AI answers come from chains of retrieval, prompts, models, and post-processing.
* Parts on a factory floor come from CAD → CAM → toolpaths → machine instructions → QC.
* Research results come from datasets → scripts → model fits → plots → conclusions.
* Content authenticity claims ("this video is real") come from editing timelines and export chains.

These pipelines:

* Cross multiple tools, file formats, vendors, people, and revisions.
* Are lossy. Every step throws information away.
* Are rarely documented in a way that's portable, reviewable, or cryptographically trustworthy.

That creates real pain:

**Regulators ask:**
"How was this model trained?"
"Where was human oversight?"
"Can you prove you followed procedure?"

**Customers ask:**
"Can you show this part was made on the certified line with the approved process?"

**Internal teams ask:**
"We shipped this answer to a user. Can we reproduce how we got it?"

### 1.2 The missing piece

What's missing isn't "more metadata."
What's missing is a standard way to describe — and prove — **how an artifact came to exist.**

That's what GenesisGraph is.

---

## 2. What GenesisGraph Is

**GenesisGraph** is an open, human-readable, cryptographically attestable format that describes *how something was produced*.

It captures:

* What was made
* How it was transformed
* Which tools and agents did the transforming
* Under what settings
* With what expected and actual fidelity
* Signed by whom

You can think of GenesisGraph as a **verifiable recipe of production**:

* For a software build
* For a machined part
* For an AI-generated answer
* For a scientific figure in a paper

GenesisGraph does **not** replace your CAD, STL, CSV, PDF, or model files.
It points to them, versions them, and explains the chain that produced them.

### 2.1 Design tagline

**GenesisGraph = provenance + versioning + capabilities + trust.**

---

## 3. Where GenesisGraph Is Immediately Useful

To keep this concrete, here are four "day one" use cases.

### 3.1 AI / model output audit

A regulated AI assistant answers a medical question.
You store:

* Which retrieval corpus version was used
* Which model (and its version/hash)
* Which prompt template version
* Which post-processor edited tone or removed disallowed claims
* The human sign-off that approved the final answer

Later, when someone asks "Who approved this?" or "Was a clinician in the loop?" — you don't scramble. You show the provenance graph.

### 3.2 Manufacturing traceability

A metal bracket for aerospace is machined.
You store:

* Which CAD version it came from
* Which CAM strategy/postprocessor generated G-code
* Which physical machine cut it (machine ID + firmware version)
* Which tolerances were promised vs actually measured

Now you can prove conformance and unlock recertification / supplier trust without sending proprietary toolpaths.

### 3.3 Scientific reproducibility

A plot in a paper is challenged.
You show:

* Which dataset snapshot was used
* Which preprocessing script ran
* Which statistical model fit those features
* Which notebook turned that into a figure

This is better than "we swear we ran a script." It's machine-verifiable.

### 3.4 Content authenticity / anti-disinformation

A video is claimed to be "unaltered body cam footage."
You show:

* Original ingest asset
* Every edit operation
* Export settings
* Signatures of the approving authority

That's C2PA-style claims, but with step-by-step process provenance instead of just a final watermark.

---

## 4. Core Model (The Four Pillars)

GenesisGraph represents process history as a directed acyclic graph of nodes.

### 4.1 Entity

**What it is:**
An artifact "at rest."

Examples:
A CAD file, a dataset snapshot, a mesh export, a G-code file, a fine-tuned model, a PDF report, an intermediate text answer.

Minimal shape in YAML:

```yaml
- id: gearbox.step
  type: CADModel
  version: 2.0.0
  file: ./parts/gearbox.step
  hash: sha256:0123abcd...
```

Key points:

* `id`: local name for this entity
* `version`: semantic or freeform
* `file` or `uri`: where to find it
* `hash`: cryptographic content hash
* `derived_from`: optional lineage

Why this matters:
You now have a tamper-evident handle on "what exactly were we working with?"

---

### 4.2 Operation

**What it is:**
A transformation step that *takes entities in and produces entities out.*

Examples:

* "Tessellate CAD → mesh."
* "Slice mesh → G-code."
* "Run inference and moderation pipeline."
* "Generate chart from dataset."

Minimal shape:

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
```

Notes:

* `parameters` captures how the tool was configured.
* `fidelity` captures expected loss ("this is an approximation") and actual measured loss.
* `attestation` captures who takes responsibility.

Why this matters:
This is the audit log step everyone always wishes they had when something goes wrong.

---

### 4.3 Tool / Agent

**What it is:**
The actor that performed an operation.
Could be:

* A CNC machine
* A slicer or CAD exporter
* An AI model
* A human reviewer

Example:

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
```

Why this matters:
You aren't just saying "something produced this."
You're saying *this exact machine/agent did*, with known capabilities and identity.

This is huge for:

* chain-of-custody
* regulated AI ("show me the human in the loop")
* aerospace/defense tolerancing
* lab accreditation

---

### 4.4 Attestation

**What it is:**
A verifiable statement of integrity and/or authorization.

Example:

```yaml
attestation:
  mode: verifiable
  signer: did:person:alex
  signature: ed25519:...
  timestamp: 2025-10-31T16:12:04Z
  delegation: did:org:example
```

Modes:

* `basic` — Just timestamp + hash.
* `signed` — Cryptographic signature.
* `verifiable` — Signatures tied to decentralized IDs (DIDs), verifiable credentials.
* `zk` — Zero-knowledge assertion, e.g. "this was done by an ISO 13485-certified facility" without revealing which one.

Why this matters:
Attestation lets you prove:

* "A licensed human actually approved this decision."
* "This part really was machined on Line 3, not a cheaper subcontractor."
* "This AI answer really came from the model we say it did."

---

## 5. Expressing Capability and Loss (Why GenesisGraph Is More Than W3C PROV-O)

Two big ideas in GenesisGraph are not first-class in most provenance systems:

### 5.1 Capability (what a tool *can* do vs what it *did* do)

Tools declare potential capabilities:

```yaml
capabilities:
  print:
    min_layer_height_mm: 0.05
    max_nozzle_diameter_mm: 0.8
    infill_patterns: [gyroid, grid]
```

Operations declare realized capability:

```yaml
realized_capability:
  print:
    layer_height_mm: 0.15
    nozzle_diameter_mm: 0.4
```

Why this matters:

* For AI: "Model claims safety filtering," vs "We ran it with temperature 0.2 and a moderation pass."
* For manufacturing: "Machine can hold ±0.01 mm," vs "We actually ran ±0.02 mm on this job."

You can prove you *stayed within allowed limits.*

### 5.2 Fidelity / loss tracking

Loss is not an afterthought. It's surfaced:

```yaml
fidelity:
  expected: geometric_approximation
  actual:
    tolerance_mm: 0.02
    surface_finish_ra: 0.8
```

Examples:

* CAD → mesh (geometric approximation)
* 32-bit float → 8-bit quantized model (compression_loss)
* Long document → RAG summary (summarization_loss)

Why this matters:

* Legal defensibility ("we told you this was approximate")
* Scientific honesty
* Quality control
* Safety audits for AI summarization and redaction

---

## 6. How a Full GenesisGraph Document Looks

At the top level, a GenesisGraph file (usually `*.gg.yaml`) includes:

```yaml
spec_version: 0.1.0

profile: gg-ai-basic-v1
imports:
  - https://genesisgraph.dev/ns/core/0.1
  - https://genesisgraph.dev/ns/ai/0.1

namespaces:
  ai:  https://genesisgraph.dev/ns/ai/0.1
  cam: https://genesisgraph.dev/ns/cam/0.1

context:
  environment: docker://ubuntu:22.04
  hardware: nvidia_a100
  location: lab3@berkeley
  software_env: conda:pytorch_2.1

tools:
  - ...
entities:
  - ...
operations:
  - ...
```

Why this matters:

* `context` lets you recreate the environment.
* `profile` lets auditors apply domain rules (e.g. "AI inference provenance must include prompt and model identity").
* `imports` and `namespaces` let GenesisGraph stay small and modular while different industries plug in their vocabularies.

---

## 7. Validation, Signing, and Verification

### 7.1 Authoring format

* Human authors/editors work in YAML.
* Machines can ingest/emit JSON.
* JSON is considered canonical for signing.

### 7.2 Validation

We publish a JSON Schema (in YAML form) called `genesisgraph.schema.yaml`.

Validators run:

```bash
gg validate experiment.gg.yaml
```

That checks:

* Required fields are present
* `entities[]`, `tools[]`, `operations[]` conform to spec
* Types and formats (e.g. timestamps, hashes) are well-formed

### 7.3 Signing

Any node — or the whole file — can be signed.

```bash
gg sign --node operations/op_tessellate_01 --mode verifiable
```

This attaches `attestation` info and a cryptographic signature.

### 7.4 Verification

```bash
gg verify --all experiment.gg.yaml
```

This confirms the hashes, timestamps, and signatures haven't been tampered with.

Why this matters:

* You can hand a regulator or customer a self-verifying bundle.
* You get auditability without exposing full IP (you can include hashes + ZK proofs instead of raw content).

---

## 8. Interoperability With Existing Standards

GenesisGraph is not trying to re-invent provenance for its own sake.
It's trying to be the **practical spine** that ties existing systems together.

| External standard / ecosystem           | How it maps                                                                                    |
| --------------------------------------- | ---------------------------------------------------------------------------------------------- |
| W3C PROV-O                              | Entity → prov:Entity; Operation → prov:Activity; Tool → prov:Agent                             |
| SLSA / SPDX / CycloneDX (software)      | Build provenance and dependency metadata live inside `operations`+`tools`.                     |
| C2PA (media authenticity)               | `attestation` can embed or link to C2PA claims.                                                |
| STEP-NC, MTConnect, QIF (manufacturing) | Machine/tooling/process metadata aligns with `tools.capabilities` and `operations.parameters`. |
| JSON-LD                                 | GenesisGraph graphs can be exported to RDF with `genesisgraph.context.jsonld`.                 |

Why this matters:
GenesisGraph is positioned as glue, not replacement.

---

## 9. Trust, Compliance, and Selective Disclosure

### 9.1 Attestation levels

GenesisGraph supports increasing levels of trust:

1. **basic**
   "Here's what happened, timestamped."
2. **signed**
   "Here's what happened, and I signed it."
3. **verifiable**
   "Here's what happened, I signed it, and you can verify my DID / credential."
4. **zk**
   "I can prove it was compliant without revealing sensitive details."

This is intentionally friendly to:

* Regulated AI systems
* Medical devices
* Aerospace & defense parts
* High-value IP you can't casually expose

### 9.2 Selective Disclosure Patterns

GenesisGraph defines three disclosure patterns that enable integrity and compliance proofs without full pipeline exposure:

#### 9.2.1 Hash-Only Lineage (Sealed Subgraph)

A sealed operation replaces a private subgraph and contains a commitment (Merkle root) to the hidden nodes and edges.

**Requirements:**
* Implementations **MUST** sign the sealed node
* Implementations **MAY** expose input/output digests as leaves
* Implementations **SHOULD** support inclusion proofs for specific digests without revealing other leaves

**Use cases:**
* Protecting proprietary prompt engineering chains
* Hiding supplier-specific manufacturing parameters
* Redacting sensitive research methodologies while maintaining integrity

**Structure:**

```yaml
operations:
  - id: op_redacted_seg
    type: sealed_subgraph
    sealed:
      merkle_root: sha256:7f3a...
      leaves_exposed:
        - role: sub_input
          hash: sha256:a1b2...
        - role: sub_output
          hash: sha256:c3d4...
      policy_assertions:
        - id: gg-ai-basic-v1
          result: pass
          signer: did:org:supplierA
          evidence_hash: sha256:deadbeef...
    attestation:
      mode: signed
      signer: did:org:supplierA
      timestamp: 2025-10-31T16:12:04Z
```

#### 9.2.2 Partial Attestation Envelope

An operation **MAY** include a signed policy result envelope containing claim-minimized fields (e.g., limit checks, boolean compliance outcomes).

**Requirements:**
* Envelopes **MUST** bind to the operation digest
* Envelopes **MAY** use SD-JWT or BBS+ for selective disclosure of individual claims
* Claims **SHOULD** be verifiable independently of full parameter disclosure

**Use cases:**
* Proving AI model temperature constraints without revealing exact prompts
* Demonstrating manufacturing tolerance compliance without exposing toolpaths
* Showing regulatory compliance without disclosing trade secrets

**Structure:**

```yaml
operations:
  - id: op_infer_42
    type: ai_inference
    inputs: [retrieval.snapshot@2025-10-25]
    outputs: [answer.txt@7]
    parameters:
      _redacted: true
    attestation:
      mode: signed
      signer: did:org:healthsys
      timestamp: 2025-10-31T11:02:19Z
      claims:
        policy: gg-ai-basic-v1
        results:
          prompt_length_chars: {lte: 4000, satisfied: true}
          temperature: {lte: 0.3, satisfied: true}
          moderation: {category: "medical", result: "pass"}
      signature: ed25519:...
```

#### 9.2.3 Transparency Anchoring

Operations and sealed subgraphs **MAY** be anchored to one or more append-only logs.

**Requirements:**
* Implementations **MUST** record inclusion/consistency proof material sufficient for offline verification
* Implementations **SHOULD** support multiple independent logs for cross-verification
* Proof material **MUST** include log_id, entry_id, tree_size, and inclusion_proof

**Use cases:**
* Time-ordering operations across organizational boundaries
* Non-repudiation of process execution
* Audit trails for regulated industries
* Multi-party witness requirements

**Structure:**

```yaml
operations:
  - id: op_slice
    type: slicing
    attestation:
      mode: signed
      signer: did:org:vendorB
      timestamp: 2025-10-31T10:00:00Z
      transparency:
        - log_id: did:log:corpA
          entry_id: 0x5f2c...
          tree_size: 128734
          inclusion_proof: base64:MIIB...
        - log_id: did:log:independent1
          entry_id: 0x98aa...
          tree_size: 451203
          inclusion_proof: base64:MHIB...
```

### 9.3 Proof-of-Execution Options

To strengthen claims that a specific binary/configuration executed, implementations **MAY** attach:

#### 9.3.1 Reproducible Run Metadata

Enables deterministic re-execution to verify outputs.

```yaml
context:
  environment: docker://ubuntu:22.04@sha256:...
  software_env: conda:pytorch_2.1#sha256:...
operations:
  - id: op_fit
    parameters: {_redacted: true}
    outputs: [model.safetensors@5]
    metrics: {train_steps: 2000}
    reproducibility:
      expected_output_hash: sha256:abcd...
      rerun_allowed_until: 2026-12-31
```

#### 9.3.2 TEE Attestation Quotes

Binds execution to trusted hardware environments.

```yaml
attestation:
  mode: signed
  signer: did:org:vendorC
  tee:
    technology: amd_sev_snp
    mr_enclave: 0x12ab...
    quote: base64:AAA...
    binds:
      inputs_root: sha256:1122...
      code_hash: sha256:3344...
```

#### 9.3.3 Multi-Witness / Threshold Signatures

Requires m-of-n witnesses to co-sign operation execution.

```yaml
attestation:
  mode: signed
  multisig:
    threshold: 2
    signers:
      - did:svc:buildfarm#key1
      - did:bot:qa
      - did:person:clinician_alex
```

### 9.4 Proof-of-Work and Proof-of-Effort

Implementations **MAY** attach optional effort signals (e.g., resource usage, VDF proofs) for rate-limiting or fairness.

**Important:** These signals **MUST NOT** be treated as substitutes for cryptographic integrity or execution proofs.

```yaml
work_proof:
  type: vdf_wesolowski
  difficulty: 2^30
  input: sha256:prev_step_hash
  output: base64:...
  verifier: "wesolowski-v1"
resource_usage:
  cpu_seconds: 312.4
  gpu_ms: 58200
  energy_kj_estimate: 940
```

### 9.5 Disclosure Level Negotiation

GenesisGraph defines three standard disclosure levels:

1. **Level A — Full Exposure**
   Complete nodes, parameters, hashes, and signatures visible.

2. **Level B — Partial Envelope**
   Parameters hidden; policy claims and output hashes exposed; optional transparency anchors.

3. **Level C — Sealed Subgraph**
   Nodes replaced with sealed_subgraph commitments; policy results, anchors, and optional PoX included.

Profiles **MAY** specify minimum acceptable disclosure levels per operation type (e.g., "gg-ai-basic-v1 requires ≥ Level B for inference operations; Level C permitted for prompt engineering steps").

---

## 10. Governance and Open Standardization

We don't want GenesisGraph to be "a vendor's format."
We want it to become boring infrastructure — like SPDX, like PROV-O.

### 10.1 Governance model

* Open license:

  * Spec text: CC-BY 4.0
  * Reference code & schemas: Apache 2.0
* A community-led working group
* A Change Control Board (CCB) that reviews schema changes and new domain profiles

### 10.2 Registry

GenesisGraph will publish and version:

* Core schema
* Domain profiles (`gg-ai`, `gg-cam`, `gg-sci`, etc.)
* Namespace definitions

All under:

* `https://genesisgraph.dev/spec/`
* `https://genesisgraph.dev/schema/`
* `https://genesisgraph.dev/ns/`

### 10.3 Versioning policy (semantic)

* Patch = clarifications only
* Minor = backward compatible addition
* Major = breaking change

This gives implementers confidence that a `gg-ai-basic-v1` profile won't silently mutate.

---

## 11. Roadmap

| Version | What ships                                                     | Why it matters                                    |
| ------- | -------------------------------------------------------------- | ------------------------------------------------- |
| v0.1    | Core model + schema + CLI skeleton                             | Prove viability; early pilots                     |
| v0.2    | Domain profiles + trust scoring rules                          | Cross-industry adoption, AI + manufacturing       |
| v0.3    | Cross-graph linking + ZK / selective disclosure patterns       | Supply chain / subcontractor safe sharing         |
| v0.4    | JSON-LD vocabulary + conformance test suite                    | Interop with PROV-O and policy tooling            |
| v1.0    | Formal foundation handoff (W3C Community Group / LF AI & Data) | Long-term stability + multistakeholder governance |

---

## 12. Conformance Classes

We define three kinds of "GenesisGraph compatible":

1. **Compliant Document**

   * Validates against the GenesisGraph core schema (and, if declared, a profile schema).
   * Includes at least one `Entity`, `Operation`, `Tool`.

2. **Compliant Validator**

   * Can parse and validate a GenesisGraph document.
   * Can verify cryptographic attestations.

3. **Compliant Signer**

   * Can add attestations following the signature rules and canonicalization rules.

These classes make procurement and compliance easier:

* "Vendor must produce a Compliant Document for every delivered AI model."
* "Auditor must run a Compliant Validator before sign-off."

---

## 13. Implementation Guidance

### 13.1 Reference CLI

A minimal `gg` CLI SHOULD support:

```bash
gg validate run.gg.yaml
gg sign --node operations/op_infer
gg verify run.gg.yaml --all
gg viz run.gg.yaml
gg export run.gg.yaml --as jsonld > run.prov.jsonld
```

### 13.2 Developer ergonomics

* Author in YAML.
* Commit alongside outputs / manufactured parts / model runs.
* Treat GenesisGraph files as part of your release artifact.

### 13.3 Security posture

* Hashes and timestamps prevent silent edits.
* DID-based attestation supports chain-of-custody and regulated human oversight.
* ZK modes prepare GenesisGraph for sensitive suppliers and high-IP environments.

This is all doable with mainstream crypto primitives like Ed25519 and SHA-256. You don't need blockchains to start.

---

## 14. Summary

GenesisGraph makes process provenance:

* portable
* reviewable
* cryptographically attestable
* auditable across organizations

It turns "we think this was made correctly" into "here's proof."

And it does that across AI, manufacturing, science, media, and supply chain — in one shared language.

> Every artifact has a beginning.
> GenesisGraph is how we prove it.

---

## 15. Appendix (Normative Building Blocks)

Below are the core structural bits that will become their own standalone docs in the formal standard.

### 15.1 Minimal entity/tool/operation schema (abridged)

```yaml
spec_version: 0.1.0

tools:
  - id: fusion_exporter
    type: Software
    vendor: Autodesk
    version: 1.1.3

entities:
  - id: gearbox.step
    type: CADModel
    version: 2.0.0
    file: ./parts/gearbox.step
    hash: sha256:0123abcd...

  - id: gearbox.3mf
    type: Mesh
    version: "4"
    file: ./parts/gearbox.3mf
    hash: sha256:89ab45cd...
    derived_from: [gearbox.step@2.0.0]

operations:
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
```

This is a valid "happy path" GenesisGraph document.

### 15.2 GenesisGraph JSON Schema (core ideas)

* Requires `spec_version`, `entities[]`, `operations[]`, `tools[]`.
* Enforces formats for IDs, hashes, DIDs, timestamps.
* Ensures each `Entity` is either a `file` or a `uri` (with a hash).
* Controls vocabularies for `attestation.mode` and `fidelity.expected`.

This schema is published as `genesisgraph.schema.yaml` and is considered normative.

### 15.3 Profiles

Profiles (e.g. `gg-ai-basic-v1`, `gg-cam-v1`) extend the core schema:

* Can require domain-specific fields.
* Can lock down vocabularies (e.g. an AI profile MAY REQUIRE that inference operations record `temperature` and `prompt_ref`).
* Are versioned and published in the public namespace registry.

Profiles prevent the core from bloating, while still letting a regulator, buyer, or large customer say:
"We only accept parts / AI outputs / analyses with GenesisGraph profile **X**."
