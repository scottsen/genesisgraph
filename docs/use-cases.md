# GenesisGraph Use Cases & Integration Guide

Real-world examples of GenesisGraph implementations across AI, manufacturing, science, and media.

---

## Table of Contents

1. [AI Pipeline Provenance](#ai-pipeline-provenance)
2. [Scientific Research Workflows](#scientific-research-workflows)
3. [Content Authenticity & Media](#content-authenticity--media)
4. [Supply Chain Verification](#supply-chain-verification)
5. [Integration Patterns](#integration-patterns)

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

### Pattern 2: Native Export

Tool natively emits GenesisGraph documents as part of build/export.

**When to use:** You control the tool's codebase
**Effort:** 500-1000 lines (depending on complexity)
**Example:** Custom tool with built-in provenance export

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
3. **Try Python wrapper** - Add provenance to your AI workflows
4. **Read FAQ.md** - Common questions answered

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
