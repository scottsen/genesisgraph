# GenesisGraph Use Cases & Integration Guide

Real-world examples of GenesisGraph implementations across AI, manufacturing, science, and media.

---

## Table of Contents

1. [TiaCAD: Reference Implementation for Parametric CAD/CAM](#tiacad-reference-implementation)
2. [AI Pipeline Provenance](#ai-pipeline-provenance)
3. [Scientific Research Workflows](#scientific-research-workflows)
4. [Content Authenticity & Media](#content-authenticity--media)
5. [Supply Chain Verification](#supply-chain-verification)
6. [Integration Patterns](#integration-patterns)

---

## TiaCAD: Reference Implementation

**Status:** Production implementation in progress
**Why it matters:** First complete CAD→CAM→Manufacturing provenance system
**Killer feature:** Proves ISO-9001/AS9100 compliance without revealing proprietary toolpaths

### Overview

[TiaCAD](../tiacad) is a declarative parametric CAD/CAM system that generates GenesisGraph provenance documents for the entire design-to-manufacturing pipeline.

**The pipeline:**
```
Design YAML → CAD Build → STL Export → CAM Toolpaths → G-code → CNC Machining → CMM Inspection
     ↓            ↓            ↓              ↓             ↓            ↓                ↓
All steps captured in verifiable provenance with selective disclosure
```

### Why TiaCAD is the Perfect Fit

1. **Complete Pipeline**: Design (CAD) → Toolpaths (CAM) → Manufacturing (G-code)
2. **Declarative YAML**: Every step explicit, versionable, reviewable
3. **Parametric**: Design parameters flow through entire pipeline
4. **Open Format**: YAML + JSON + STL/STEP/3MF (no vendor lock-in)

**Result:** TiaCAD emits complete, verifiable provenance from first sketch to final part.

### Example: Hobby Use (Level A - Full Disclosure)

A maker creates a guitar wall hanger using TiaCAD.

#### Input: `guitar_hanger.yaml`

```yaml
metadata:
  name: guitar_hanger
  version: 1.0

parameters:
  plate_width: 100
  plate_height: 75
  mounting_holes: 2

geometry:
  - type: box
    dimensions: [plate_width, plate_height, 10]
  # ... more geometry ...
```

#### Generated Provenance: `guitar_hanger.gg.yaml`

```yaml
spec_version: 0.1.0
profile: gg-cam-basic-v1

tools:
  - id: tiacad
    type: Software
    version: 2.0.0
    capabilities:
      cad:
        primitives: [box, cylinder, sphere, text]
        operations: [boolean, pattern, transform]
        tolerance_mm: 0.001

entities:
  - id: guitar_hanger.yaml
    type: CADDefinition
    version: 1.0
    file: ./guitar_hanger.yaml
    hash: sha256:a1b2c3d4...

  - id: guitar_hanger.stl
    type: Mesh3D
    version: 1.0
    file: ./output/guitar_hanger.stl
    hash: sha256:d4e5f6...
    derived_from: [guitar_hanger.yaml@1.0]

  - id: guitar_hanger.nc
    type: GCode
    version: 1.0
    file: ./output/guitar_hanger.nc
    hash: sha256:g7h8i9...
    derived_from: [guitar_hanger.stl@1.0]

operations:
  - id: cad_build
    type: parametric_cad_generation
    inputs: [guitar_hanger.yaml@1.0]
    outputs: [guitar_hanger.stl@1.0]
    tool: tiacad@2.0.0
    parameters:
      plate_width: 100
      plate_height: 75
      mounting_holes: 2
    attestation:
      mode: basic
      timestamp: 2025-10-31T10:00:00Z

  - id: cam_generate
    type: toolpath_generation
    inputs: [guitar_hanger.stl@1.0]
    outputs: [guitar_hanger.nc@1.0]
    tool: tiacad_cam@0.1.0
    parameters:
      material: hardwood_maple
      tool_diameter_mm: 6.35
      feed_rate_mm_min: 1000
    attestation:
      mode: basic
      timestamp: 2025-10-31T10:05:00Z
```

**Usage:** Version control, reproducibility, learning

**CLI Command:**
```bash
tiacad build guitar_hanger.yaml --export-provenance
# ✓ CAD: output/guitar_hanger.stl
# ✓ Provenance: output/guitar_hanger.gg.yaml
```

### Example: Aerospace Production (Level C - Sealed Subgraph)

An aerospace supplier must prove ISO-9001/AS9100 compliance without revealing proprietary CAM toolpaths.

#### The Challenge

- **Requirement:** Prove compliance to auditors/customers
- **Constraint:** CAM toolpaths are trade secrets (competitive advantage)
- **Solution:** Level C selective disclosure with sealed subgraph

#### Generated Provenance (Abbreviated)

```yaml
spec_version: 0.1.0
profile: gg-cam-aerospace-v1

context:
  environment: rhel:8.5
  location: facility-phoenix-line3

tools:
  - id: fusion360
    type: Software
    vendor: Autodesk
    version: 2.0.16700

  - id: proprietary_cam_processor
    type: Software
    vendor: InternalCAM
    version: 4.2.1
    # Tool exists, but parameters will be sealed

  - id: haas_vf2
    type: CNCMachine
    vendor: Haas
    model: VF-2
    serial: SN-12345
    capabilities:
      tolerance_mm: 0.01
      max_spindle_rpm: 8100

entities:
  - id: bracket_cad
    type: CADModel
    version: 3.1.2
    file: ./models/bracket_v3.1.2.step
    hash: sha256:1a2b3c4d...

  - id: bracket_mesh
    type: Mesh3D
    version: 3.1.2
    hash: sha256:5e6f7g8h...
    derived_from: [bracket_cad@3.1.2]

  - id: bracket_gcode
    type: GCode
    version: 3.1.2
    hash: sha256:9i0j1k2l...
    derived_from: [bracket_mesh@3.1.2]

  - id: bracket_part
    type: PhysicalPart
    version: 3.1.2
    serial_number: BRK-7075-001-A-0001
    derived_from: [bracket_gcode@3.1.2]

operations:
  - id: op_tessellate_001
    type: tessellation
    inputs: [bracket_cad@3.1.2]
    outputs: [bracket_mesh@3.1.2]
    tool: fusion360@2.0.16700
    parameters:
      tolerance_mm: 0.05
      surface_deviation_mm: 0.02
    fidelity:
      expected: geometric_approximation
      actual:
        max_deviation_mm: 0.018
    attestation:
      mode: signed
      signer: did:org:aerospace-supplier-inc
      signature: ed25519:sig1_aabbccdd
      timestamp: 2025-10-31T08:00:00Z

  # ⚠️ PROPRIETARY OPERATION - SEALED SUBGRAPH ⚠️
  - id: op_cam_toolpath_001
    type: toolpath_generation
    inputs: [bracket_mesh@3.1.2]
    outputs: [bracket_gcode@3.1.2]
    tool: proprietary_cam_processor@4.2.1

    # Parameters are SEALED (Merkle commitment)
    sealed_subgraph:
      merkle_root: sha256:abc123def456789...
      leaves_exposed:
        - input_hash: sha256:5e6f7g8h...
        - output_hash: sha256:9i0j1k2l...
      algorithm: sha256_merkle_tree

    # Policy compliance VISIBLE (without revealing how)
    policy_assertions:
      - claim: iso_9001_process_conformance
        result: pass
        auditor: did:org:bsi-certification
        timestamp: 2025-10-15T00:00:00Z

      - claim: as9100_rev_d_toolpath_validation
        result: pass
        auditor: did:org:nadcap-accreditation
        timestamp: 2025-10-20T00:00:00Z

      - claim: tool_wear_within_limits
        result: pass
        metric: tool_condition_index
        threshold: ">= 0.95"
        actual: 0.98

    # Cryptographic proof WITHOUT parameters
    attestation:
      mode: verifiable
      signer: did:org:aerospace-supplier-inc
      signature: ed25519:sig2_proprietary_sealed
      timestamp: 2025-10-31T09:00:00Z
      tee_quote:
        platform: intel_sgx
        enclave_hash: sha256:enclave123...
        report_data: sha256:report456...

  - id: op_cnc_machining_001
    type: cnc_machining
    inputs: [bracket_gcode@3.1.2]
    outputs: [bracket_part@3.1.2]
    tool: haas_vf2@SN-12345

    parameters:
      program: bracket_gcode@3.1.2
      material: aluminum_7075_t6
      spindle_speed_rpm: 6000
      coolant: enabled

    realized_capability:
      tolerance_mm: 0.008  # Actual measured
      surface_finish_ra_um: 1.2

    fidelity:
      expected: physical_realization
      actual:
        measured_dimensions_mm: [100.002, 50.001, 25.003]
        tolerance_satisfied: true
        inspection_method: cmm_zeiss_contura_g2

    attestation:
      mode: verifiable
      signer: did:person:machinist_john_smith
      signature: ed25519:sig3_machining
      timestamp: 2025-10-31T11:30:00Z
      witnesses:
        - did:person:inspector_alice_jones
        - did:machine:cmm_zeiss_001

metadata:
  work_order: WO-2025-10-31-BRK-001
  customer: AerospaceCorp
  part_number: BRK-7075-001-A
  compliance_frameworks:
    - ISO-9001
    - AS9100D
  disclosure_level: sealed_subgraph
  proprietary_claim: "CAM toolpath generation algorithms are trade secrets"
  auditor_access: policy_compliance_and_hashes_only
  retention_policy: 25_years
```

### What This Achieves

**Auditors/Customers see:**
- ✓ CAD version used (bracket_cad@3.1.2)
- ✓ Mesh tessellation parameters (visible)
- ✓ **ISO-9001 compliance: PASS**
- ✓ **AS9100D compliance: PASS**
- ✓ Tool wear within limits: PASS
- ✓ CNC machine ID and settings
- ✓ Measured tolerances from CMM inspection
- ✓ All cryptographically signed
- ✓ TEE attestation (Intel SGX enclave)

**Auditors/Customers DON'T see:**
- ✗ Proprietary CAM algorithms
- ✗ Toolpath optimization strategies
- ✗ Feed rate calculations
- ✗ Adaptive machining parameters

**Business Impact:**
- **Competitive advantage preserved** (toolpath IP protected)
- **Customer trust established** (provable compliance)
- **Audit cost reduced** (machine-verifiable claims)
- **Recertification enabled** (portable compliance proof)

### TiaCAD Implementation Architecture

```
┌─────────────────────────────────────────────────────────┐
│ TiaCAD Core                                             │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ YAML Parser  │→ │ CAD Builder  │→ │ STL Export   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                  ↓                  ↓          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ GenesisGraph Provenance Writer                   │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  • Entity Builder (track all artifacts)          │  │
│  │  • Operation Builder (capture transformations)   │  │
│  │  • Tool Builder (record software versions)       │  │
│  │  • Attestation Builder (timestamps/signatures)   │  │
│  │  • Sealing Module (Merkle commitments for IP)    │  │
│  └──────────────────────────────────────────────────┘  │
│         ↓                                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Output: design.gg.yaml                           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Code snippet** (Python implementation):

```python
# tiacad_core/provenance/genesisgraph_writer.py

class GenesisGraphWriter:
    """Export TiaCAD document as GenesisGraph provenance"""

    def __init__(self, tiacad_doc: TiaCADDocument):
        self.tiacad_doc = tiacad_doc
        self.entities = []
        self.operations = []
        self.tools = []

    def write(self, output_path: str,
              attestation_mode: str = "basic",
              seal_cam: bool = False):
        """
        Write GenesisGraph document.

        Args:
            output_path: Path for .gg.yaml file
            attestation_mode: basic, signed, verifiable
            seal_cam: If True, seal CAM parameters with Merkle commitment
        """
        gg_doc = {
            'spec_version': '0.1.0',
            'profile': 'gg-cam-basic-v1',
            'tools': self._build_tools(),
            'entities': self._build_entities(),
            'operations': self._build_operations(attestation_mode, seal_cam)
        }

        with open(output_path, 'w') as f:
            yaml.dump(gg_doc, f, sort_keys=False)

    def _build_operations(self, attestation_mode, seal_cam):
        """Build operations section"""
        operations = []

        # CAD build operation (always visible)
        cad_op = {
            'id': 'cad_build',
            'type': 'parametric_cad_generation',
            'inputs': [f"{self.tiacad_doc.metadata['name']}.yaml@1.0"],
            'outputs': [f"{self.tiacad_doc.metadata['name']}.stl@1.0"],
            'tool': 'tiacad@' + get_tiacad_version(),
            'parameters': self.tiacad_doc.parameters,
            'attestation': self._build_attestation(attestation_mode)
        }
        operations.append(cad_op)

        # CAM operation (optionally sealed)
        if self.tiacad_doc.cam:
            if seal_cam:
                cam_op = self._build_sealed_cam_operation(attestation_mode)
            else:
                cam_op = self._build_cam_operation(attestation_mode)
            operations.append(cam_op)

        return operations

    def _build_sealed_cam_operation(self, attestation_mode):
        """Build CAM operation with sealed parameters"""
        from .sealing import create_merkle_commitment

        # Extract CAM parameters to seal
        cam_params = self.tiacad_doc.cam.parameters

        # Create Merkle commitment
        merkle_root = create_merkle_commitment(cam_params)

        return {
            'id': 'cam_toolpath_generation',
            'type': 'toolpath_generation',
            'inputs': [f"{self.tiacad_doc.metadata['name']}.stl@1.0"],
            'outputs': [f"{self.tiacad_doc.metadata['name']}.nc@1.0"],
            'tool': 'tiacad_cam@' + get_cam_version(),
            'sealed_subgraph': {
                'merkle_root': merkle_root,
                'leaves_exposed': [
                    {'input_hash': self._get_input_hash()},
                    {'output_hash': self._get_output_hash()}
                ]
            },
            'policy_assertions': self._build_policy_assertions(),
            'attestation': self._build_attestation(attestation_mode)
        }
```

**CLI Usage:**

```bash
# Basic provenance (hobby use)
tiacad build design.yaml --export-provenance

# Signed provenance (professional)
tiacad build design.yaml --export-provenance --provenance-mode signed

# Sealed CAM parameters (aerospace/IP protection)
tiacad build design.yaml --export-provenance --seal-cam --provenance-mode verifiable
```

### Roadmap

**Phase 1 (Months 1-2):** Basic provenance export
- ✓ CLI flag: `--export-provenance`
- ✓ Capture entities, operations, tools
- ✓ Basic attestation (timestamp + hash)

**Phase 2 (Months 3-4):** CAM integration
- Full pipeline: CAD → STL → G-code provenance
- Fidelity tracking (CAD tolerance → realized tolerance)

**Phase 3 (Months 5-6):** Cryptographic trust
- Digital signatures (Ed25519)
- DID-based identity
- Multi-party attestation

**Phase 4 (Months 7-8):** Selective disclosure
- Merkle commitments for proprietary parameters
- Policy assertion framework
- TEE attestation support

**Phase 5 (Months 9-10):** Manufacturing integration
- CNC machine integration
- CMM inspection capture
- Real-time provenance updates

### Value Proposition

| Stakeholder | Without GenesisGraph | With GenesisGraph |
|-------------|---------------------|-------------------|
| **Maker** | Manual documentation | Automatic provenance export |
| **Professional Shop** | Tribal knowledge | Verifiable process records |
| **Aerospace Supplier** | IP vs compliance dilemma | Provable compliance + IP protection |
| **Auditor** | "Trust us" claims | Machine-verifiable proof |
| **Customer** | Supplier risk | Cryptographic assurance |

**Full integration details:** See `/sessions/zoduke-1031/TIACAD_GENESISGRAPH_INTEGRATION.md`

---

## AI Pipeline Provenance

**Problem:** Customers say "$2000? You just used AI."
**Solution:** Cryptographic proof of work effort and human oversight

### Use Case: Prompt Engineering Proof-of-Work

A consultant creates a medical Q&A system using sophisticated RAG pipeline.

#### What Needs Proving

- ✓ 12 retrieval iterations (not one ChatGPT query)
- ✓ 47 medical documents analyzed
- ✓ 8-step reasoning chain
- ✓ 37 fact-checks against corpus
- ✓ 2.3 hours of expert clinician review
- ✓ All timestamped and signed

#### GenesisGraph Solution

```yaml
spec_version: 0.1.0
profile: gg-ai-basic-v1

tools:
  - id: proprietary_retrieval
    type: Software
    vendor: InternalAI
    version: 3.2.1

  - id: llama3_70b
    type: AIModel
    vendor: Meta
    version: 3.0

  - id: dr_sarah_chen
    type: Human
    identity:
      did: did:person:dr_sarah_chen
      certificate: "Medical License CA-MD-98765"

entities:
  - id: medical_corpus
    type: Dataset
    version: 2025-10-15
    hash: sha256:a1b2c3d4...

  - id: retrieval_results
    type: Dataset
    version: "1"
    hash: sha256:f1e2d3c4...
    derived_from: [medical_corpus@2025-10-15]

  - id: raw_answer
    type: Text
    version: "1"
    hash: sha256:fedcba09...
    derived_from: [retrieval_results@1]

  - id: final_answer
    type: Text
    version: "1"
    hash: sha256:99887766...
    derived_from: [raw_answer@1]

operations:
  - id: op_retrieval_001
    type: ai_retrieval
    inputs: [medical_corpus@2025-10-15]
    outputs: [retrieval_results@1]
    tool: proprietary_retrieval@3.2.1
    parameters:
      query: "What are the contraindications for metformin in patients with CKD?"
      iterations: 12  # Proof of work!
      max_results: 10
      similarity_threshold: 0.75
    metrics:
      documents_analyzed: 47
      results_returned: 8
      max_similarity: 0.92
      avg_similarity: 0.81
      latency_ms: 245
    attestation:
      mode: signed
      signer: did:svc:retrieval-prod
      signature: ed25519:sig1_aabbccdd
      timestamp: 2025-10-31T14:23:11Z

  - id: op_inference_001
    type: ai_inference
    inputs: [retrieval_results@1]
    outputs: [raw_answer@1]
    tool: llama3_70b@3.0
    parameters:
      temperature: 0.2  # Conservative for medical
      reasoning_steps: 8  # Proof of thoughtful generation
    metrics:
      inference_time_ms: 1823
      fact_checks_performed: 37  # Proof of diligence
    attestation:
      mode: signed
      signer: did:model:llama3-70b-instruct
      signature: ed25519:sig2_eeffaabb
      timestamp: 2025-10-31T14:23:13Z

  - id: op_human_review_001
    type: human_review
    inputs: [raw_answer@1]
    outputs: [final_answer@1]
    tool: dr_sarah_chen@
    parameters:
      review_type: medical_accuracy
      review_duration_hours: 2.3  # Proof of expert time
      approval_granted: true
    attestation:
      mode: verifiable
      signer: did:person:dr_sarah_chen
      signature: ed25519:sig4_aabbccdd99887766
      timestamp: 2025-10-31T16:39:00Z

metadata:
  request_id: req-2025-10-31-14-23-11-xyz
  compliance_framework: HIPAA
```

### Business Impact

**Before GenesisGraph:**
- Client: "This seems like ChatGPT could do it for $20."
- You: "No, we did extensive research and expert review."
- Client: "Can you prove it?"
- You: "Trust us."

**With GenesisGraph:**
- Client: "Can you prove your process?"
- You: "Here's the cryptographic proof: 12 retrieval iterations, 47 documents, 37 fact-checks, 2.3 hours expert review. All signed."
- Client: "Verified. Invoice approved."

### Python Wrapper Pattern

```python
# openai_with_provenance.py

from openai import OpenAI
from genesisgraph import GenesisGraphWriter
import hashlib
import datetime

class OpenAIWithProvenance:
    """OpenAI client that automatically generates GenesisGraph provenance"""

    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.gg = GenesisGraphWriter()

    def chat_completion(self, messages, model="gpt-4", **kwargs):
        """Chat completion with provenance tracking"""

        # Record request
        request_hash = self._hash_messages(messages)
        self.gg.add_entity(
            id=f"prompt_{request_hash[:8]}",
            type="TextPrompt",
            hash=request_hash
        )

        # Call OpenAI
        start_time = datetime.datetime.utcnow()
        response = self.client.chat.completions.create(
            messages=messages,
            model=model,
            **kwargs
        )
        end_time = datetime.datetime.utcnow()

        # Record response
        response_text = response.choices[0].message.content
        response_hash = self._hash_text(response_text)
        self.gg.add_entity(
            id=f"response_{response_hash[:8]}",
            type="TextResponse",
            hash=response_hash,
            derived_from=[f"prompt_{request_hash[:8]}"]
        )

        # Record operation
        self.gg.add_operation(
            id=f"op_inference_{request_hash[:8]}",
            type="ai_inference",
            inputs=[f"prompt_{request_hash[:8]}"],
            outputs=[f"response_{response_hash[:8]}"],
            tool=f"{model}@{response.model}",
            parameters={
                "temperature": kwargs.get("temperature", 1.0),
                "max_tokens": kwargs.get("max_tokens"),
            },
            metrics={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "latency_ms": (end_time - start_time).total_seconds() * 1000
            },
            attestation={
                "mode": "basic",
                "timestamp": end_time.isoformat() + "Z"
            }
        )

        return response

    def export_provenance(self, path):
        """Export GenesisGraph document"""
        self.gg.write(path)

# Usage
client = OpenAIWithProvenance(api_key="sk-...")

response = client.chat_completion(
    messages=[{"role": "user", "content": "Explain quantum entanglement"}],
    model="gpt-4",
    temperature=0.2
)

# Export provenance
client.export_provenance("quantum_explanation.gg.yaml")
```

---

## Scientific Research Workflows

**Problem:** "Can you reproduce your figure from the paper?"
**Solution:** Machine-verifiable provenance from dataset to publication

### Use Case: Neuroimaging Study

A researcher publishes fMRI study on cognitive decline.

```yaml
spec_version: 0.1.0
profile: gg-science-v1

tools:
  - id: fsl
    type: Software
    vendor: FMRIB
    version: 6.0.5
    citation: "Jenkinson et al. (2012) NeuroImage"

  - id: custom_analysis
    type: Software
    version: 1.2.0
    repository: github.com/lab/fmri-analysis
    commit: a1b2c3d4

  - id: matplotlib
    type: Software
    version: 3.7.1

entities:
  - id: raw_fmri_dicom
    type: Dataset
    version: 2024-03-15
    uri: s3://study-data/raw_dicom/
    hash: sha256:raw123...
    subjects: 42
    sessions: 168

  - id: preprocessed_nifti
    type: Dataset
    version: 2024-04-01
    hash: sha256:nifti456...
    derived_from: [raw_fmri_dicom@2024-03-15]

  - id: statistical_map
    type: NiftiImage
    version: 2024-04-15
    hash: sha256:statmap789...
    derived_from: [preprocessed_nifti@2024-04-01]

  - id: figure_3_panel_b
    type: Image
    version: final
    file: figures/figure_3b.png
    hash: sha256:fig3b012...
    derived_from: [statistical_map@2024-04-15]

operations:
  - id: op_preprocessing
    type: fmri_preprocessing
    inputs: [raw_fmri_dicom@2024-03-15]
    outputs: [preprocessed_nifti@2024-04-01]
    tool: fsl@6.0.5
    parameters:
      motion_correction: mcflirt
      slice_timing: true
      spatial_smoothing_mm: 5.0
      high_pass_filter_sec: 100
    fidelity:
      expected: lossless
      actual:
        motion_outliers_removed: 3
        mean_fd_mm: 0.18
    attestation:
      mode: signed
      signer: did:person:grad_student_alice
      timestamp: 2024-04-01T12:00:00Z

  - id: op_statistical_analysis
    type: glm_analysis
    inputs: [preprocessed_nifti@2024-04-01]
    outputs: [statistical_map@2024-04-15]
    tool: custom_analysis@1.2.0
    parameters:
      model: two_sample_t_test
      covariates: [age, sex, education_years]
      multiple_comparison_correction: cluster_fwe
      alpha: 0.05
    metrics:
      significant_clusters: 2
      max_t_value: 5.67
      cluster_size_voxels: [423, 187]
    attestation:
      mode: signed
      signer: did:person:grad_student_alice
      timestamp: 2024-04-15T16:30:00Z

  - id: op_figure_generation
    type: visualization
    inputs: [statistical_map@2024-04-15]
    outputs: [figure_3_panel_b@final]
    tool: matplotlib@3.7.1
    parameters:
      colormap: hot
      threshold_t: 3.1
      slice_coordinates: [40, -20, 10]
      dpi: 300
    attestation:
      mode: signed
      signer: did:person:pi_professor_bob
      timestamp: 2024-05-01T09:00:00Z
      review_type: publication_ready_approval

metadata:
  doi: 10.1234/neuroscience.2024.5678
  publication: "Journal of Cognitive Neuroscience"
  ethics_approval: IRB-2023-0542
  data_sharing_statement: "Preprocessed data available at OpenNeuro.org/ds004321"
```

### Reproducibility Benefits

1. **Exact preprocessing parameters** (FSL version, smoothing kernel)
2. **Statistical model specification** (covariates, corrections)
3. **Figure generation settings** (colormap, threshold, coordinates)
4. **Software versions** (FSL 6.0.5, matplotlib 3.7.1, custom analysis commit a1b2c3d4)
5. **Approvals tracked** (grad student → PI review)

**Result:** Reviewers can verify figures, editors can enforce data sharing, future researchers can reproduce exactly.

---

## Content Authenticity & Media

**Problem:** "Is this video deepfaked?"
**Solution:** C2PA-style provenance with step-by-step editing history

### Use Case: Body Camera Footage

Police department needs to prove body camera footage is unaltered chain-of-custody.

```yaml
spec_version: 0.1.0
profile: gg-media-c2pa-v1

tools:
  - id: bodycam_axon_3
    type: HardwareDevice
    vendor: Axon
    model: Body3
    serial: BC-2024-0542
    firmware: 2.4.1

  - id: adobe_premiere
    type: Software
    vendor: Adobe
    version: 24.1.0

  - id: evidence_manager
    type: Software
    vendor: Evidence.com
    version: 8.2.0

entities:
  - id: raw_footage
    type: Video
    version: original
    hash: sha256:raw_footage_abc123...
    duration_seconds: 847
    resolution: 1920x1080
    framerate: 30

  - id: redacted_footage
    type: Video
    version: redacted
    hash: sha256:redacted_def456...
    derived_from: [raw_footage@original]

  - id: evidence_package
    type: Archive
    version: final
    hash: sha256:evidence_package_ghi789...
    derived_from: [redacted_footage@redacted]

operations:
  - id: op_capture
    type: video_capture
    inputs: []
    outputs: [raw_footage@original]
    tool: bodycam_axon_3@BC-2024-0542
    parameters:
      gps_location: [38.5816, -121.4944]
      timestamp_utc: 2025-10-30T03:42:15Z
      officer_id: badge_7421
    attestation:
      mode: verifiable
      signer: did:device:bodycam_bc_2024_0542
      signature: ed25519:device_sig_001
      timestamp: 2025-10-30T03:42:15Z
      chain_of_custody_initiated: true

  - id: op_redaction
    type: video_editing
    inputs: [raw_footage@original]
    outputs: [redacted_footage@redacted]
    tool: adobe_premiere@24.1.0
    parameters:
      redactions:
        - type: face_blur
          frames: [1230, 1450]
          reason: bystander_privacy
        - type: audio_mute
          time_range: [42.5, 47.3]
          reason: witness_identity_protection
      no_content_alteration: true
      metadata_preserved: true
    attestation:
      mode: verifiable
      signer: did:person:evidence_tech_sarah
      signature: ed25519:tech_sig_002
      timestamp: 2025-10-30T14:20:00Z
      witnesses:
        - did:person:supervisor_lieutenant_jones

  - id: op_archive
    type: evidence_packaging
    inputs: [redacted_footage@redacted]
    outputs: [evidence_package@final]
    tool: evidence_manager@8.2.0
    parameters:
      case_number: CASE-2025-10-30-042
      retention_years: 50
      access_control: restricted_court_order_only
    attestation:
      mode: verifiable
      signer: did:org:police_department_evidence_unit
      signature: ed25519:evidence_sig_003
      timestamp: 2025-10-30T15:00:00Z
      legal_hold: true

metadata:
  case_number: CASE-2025-10-30-042
  incident_date: 2025-10-30
  disclosure_level: full_chain_of_custody
  c2pa_manifest_version: 2.0
  legal_attestation: "Complete chain of custody maintained per department policy 4.2.1"
```

### Legal Benefits

- ✓ Proves device identity (body camera serial, firmware version)
- ✓ GPS timestamp from hardware (not editable metadata)
- ✓ All edits logged (redactions for privacy, not content alteration)
- ✓ Multi-party attestation (tech + supervisor)
- ✓ Court-admissible provenance

---

## Integration Patterns

### Pattern 1: Wrapper (AI APIs)

Wrap existing APIs (OpenAI, Anthropic, Hugging Face) with provenance tracking.

**When to use:** You don't control the tool, just consume its API
**Effort:** 200 lines of code
**Example:** See "Python Wrapper Pattern" above

### Pattern 2: Native Export (TiaCAD)

Tool natively emits GenesisGraph documents as part of build/export.

**When to use:** You control the tool's codebase
**Effort:** 500-1000 lines (depending on complexity)
**Example:** TiaCAD implementation

### Pattern 3: Post-Hoc Reconstruction

Reconstruct provenance from logs, git commits, build artifacts.

**When to use:** Legacy systems, forensic analysis
**Effort:** Variable (depends on log quality)
**Example:** Scientific workflow reconstruction from Jupyter notebooks

### Pattern 4: Pipeline Orchestrator

Workflow engine (Airflow, Prefect, Nextflow) emits provenance for each step.

**When to use:** Multi-tool pipelines, CI/CD systems
**Effort:** 300-500 lines (orchestrator plugin)
**Example:** Airflow DAG → GenesisGraph converter

---

## Cross-Domain Value Summary

| Domain | Pain Point | GenesisGraph Solution | Disclosure Level |
|--------|-----------|---------------------|------------------|
| **AI/ML** | Can't prove model provenance | Verifiable chain: data → model → output → review | A or B |
| **Manufacturing** | Digital thread fragmented | Portable provenance across CAD/CAM/QC | C (sealed) |
| **Science** | Papers not reproducible | Attach signed `.gg.yaml` with exact lineage | A (full) |
| **Regulators** | Can't audit AI systems | Standard format for "show me the human in the loop" | B (partial) |
| **Web3/Crypto** | Need off-chain proofs | Anchor GenesisGraph on-chain, keep details off | C (sealed) |
| **Media/Creative** | AI content lacks attribution | C2PA-compatible provenance for generative workflows | A or B |
| **Supply Chain** | Can't verify claims | Cryptographic proof of process compliance | B or C |

---

## Next Steps

1. **Read QUICKSTART.md** - 5-minute tutorial
2. **Review examples/** - Level A/B/C implementations
3. **Study TiaCAD integration** - Complete reference implementation
4. **Try Python wrapper** - Add provenance to your AI workflows
5. **Read FAQ.md** - Common questions answered

---

## Contributing

GenesisGraph succeeds when multiple tools adopt it. If you integrate GenesisGraph into your project:

1. **Share your implementation** - PRs welcome for examples/
2. **Report integration challenges** - Help improve developer experience
3. **Propose domain profiles** - Create gg-bio, gg-chem, etc.

---

## License

Apache 2.0 - Free to use, modify, and distribute.

---

> Every artifact has a beginning. GenesisGraph is how we prove it.
