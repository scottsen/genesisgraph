# Industry-Specific Profile Validators

## Overview

GenesisGraph now includes industry-specific profile validators that provide automated compliance checking for different industries and use cases. This feature implements **Phase 5** of the validation pipeline, enabling standardized validation for AI pipelines, manufacturing workflows, and other specialized domains.

## Available Profiles

### 1. gg-ai-basic-v1 (AI/ML Pipelines)

The AI Basic profile (`gg-ai-basic-v1`) validates AI/ML pipeline workflows for compliance with best practices and regulatory requirements.

**Required Parameters:**

- **ai_inference operations:**
  - `temperature` (0.0-2.0): Controls randomness in model outputs
  - `top_p` (0.0-1.0): Nucleus sampling parameter
  - `prompt_length_chars`: Length of input prompt in characters
  - `model_name`: Name of the AI model
  - `model_version`: Version of the AI model

- **ai_retrieval operations:**
  - `query_length_chars`: Length of search query
  - `max_results`: Maximum number of results to return
  - `similarity_threshold` (0.0-1.0): Minimum similarity score

- **ai_moderation operations:**
  - `categories`: List of moderation categories
  - `threshold`: Moderation threshold value

- **ai_training operations:**
  - `dataset_size`: Size of training dataset
  - `training_duration_seconds`: Training duration
  - `validation_split`: Validation data split ratio
  - `model_architecture`: Architecture description

**Compliance Features:**

- FDA 21 CFR Part 11 support for electronic records
- Human review requirement checking for high-stakes decisions
- Data lineage and model versioning validation
- Attestation mode verification (signed/verifiable/zk)

**Example:**

```yaml
spec_version: "0.2.0"
metadata:
  profile: gg-ai-basic-v1
  description: "AI inference pipeline"

entities:
  - id: input_data
    type: Dataset
    version: "1.0"
    hash: "sha256:abc123..."
    file: data.json

operations:
  - id: inference1
    type: ai_inference
    inputs: [input_data]
    outputs: [result]
    tool: gpt4
    parameters:
      temperature: 0.7
      top_p: 0.9
      prompt_length_chars: 1024
      model_name: "gpt-4"
      model_version: "2024-01"
    attestation:
      mode: signed
      attester: "did:example:ai-operator"
      timestamp: "2024-01-01T00:00:00Z"
      claim: "AI inference performed according to protocol"

tools:
  - id: gpt4
    type: AIModel
    version: "2024-01"
    did: "did:example:openai"
```

### 2. gg-cam-v1 (Computer-Aided Manufacturing)

The CAM profile (`gg-cam-v1`) validates manufacturing workflows for ISO-9001 compliance and industry best practices.

**Required Parameters:**

- **cnc_machining operations:**
  - `tolerance_mm`: Dimensional tolerance in millimeters
  - `material`: Material specification
  - `feed_rate_mm_per_min`: Feed rate
  - `spindle_speed_rpm`: Spindle speed
  - `tool_number`: Tool number reference

- **additive_manufacturing operations:**
  - `layer_height_mm`: Layer height in millimeters
  - `material`: Material specification
  - `temperature_celsius`: Process temperature
  - `print_speed_mm_per_s`: Print speed

- **tessellation operations:**
  - `max_chord_error_mm`: Maximum chord error
  - `max_angle_deg`: Maximum angle deviation

- **quality_inspection operations:**
  - `inspection_type`: Type of inspection
  - `acceptance_criteria`: Acceptance criteria reference
  - `measurement_uncertainty_mm`: Measurement uncertainty

**Compliance Features:**

- ISO 9001:2015 quality management validation
- Machine calibration verification
- Material traceability tracking
- Quality control checkpoint validation
- Critical operation attestation requirements

**Example:**

```yaml
spec_version: "0.2.0"
metadata:
  profile: gg-cam-v1
  quality_standard: "ISO-9001:2015"
  part_number: "PN-12345"
  approved_by: "QA Manager"

entities:
  - id: cad_model
    type: CADModel
    version: "2.0"
    hash: "sha256:def456..."
    file: part.step

operations:
  - id: machining1
    type: cnc_machining
    inputs: [cad_model]
    outputs: [machined_part]
    tool: cnc_mill
    parameters:
      tolerance_mm: 0.05
      material: "aluminum-6061"
      feed_rate_mm_per_min: 1000
      spindle_speed_rpm: 3000
      tool_number: 5
      post_processor: "fanuc"
    attestation:
      mode: signed
      attester: "did:example:machine-operator"
      timestamp: "2024-01-01T10:00:00Z"

  - id: inspection1
    type: quality_inspection
    inputs: [machined_part]
    outputs: [approved_part]
    parameters:
      inspection_type: "dimensional"
      acceptance_criteria: "ISO-9001"
      measurement_uncertainty_mm: 0.01
    attestation:
      mode: signed
      attester: "did:example:qc-inspector"
      timestamp: "2024-01-01T11:00:00Z"

tools:
  - id: cnc_mill
    type: Machine
    did: "did:example:mill-001"
    metadata:
      calibration_date: "2024-01-01"
      calibration_certificate: "CERT-2024-001"
      last_maintenance_date: "2024-01-01"
```

## Compliance Validators

### ISO 9001:2015 Validator

The ISO 9001 validator checks compliance with quality management system requirements:

- **Clause 7.5** - Documented Information
- **Clause 8.5.2** - Identification and Traceability
- **Clause 7.1.5** - Monitoring and Measuring Resources
- **Clause 8.5** - Production and Service Provision
- **Clause 8.6** - Release of Products and Services

**Compliance Levels:**
- `fully-compliant`: No errors or warnings
- `substantially-compliant`: No errors, 1-3 warnings
- `partially-compliant`: No errors, 4+ warnings
- `non-compliant`: Has errors

### FDA 21 CFR Part 11 Validator

The FDA 21 CFR Part 11 validator checks compliance with electronic records and signatures regulations:

- **§11.10(a)** - System Validation
- **§11.10(c)** - Protection of Records
- **§11.10(e)** - Audit Trails
- **§11.10(k)** - Data Integrity
- **§11.50** - Signature Manifestations
- **§11.70** - Signature/Record Linking

**Key Requirements:**
- Strong cryptographic hashes (SHA-256 or better)
- Timestamped attestations
- Attester identification (DID)
- Signature binding to records
- Audit trail completeness

## Usage

### Command Line

```bash
# Validate with profile auto-detection
genesisgraph validate workflow.gg.yaml --verify-profile

# Validate with specific profile
genesisgraph validate workflow.gg.yaml --verify-profile --profile gg-ai-basic-v1

# Combine with other validations
genesisgraph validate workflow.gg.yaml \
  --verify-profile \
  --verify-signatures \
  --verify-transparency \
  --verbose
```

### Python API

```python
from genesisgraph import GenesisGraphValidator

# Create validator with profile validation enabled
validator = GenesisGraphValidator(
    verify_profile=True,
    profile_id='gg-ai-basic-v1'  # Optional: auto-detects if not specified
)

# Validate a file
result = validator.validate_file('workflow.gg.yaml')

if result.is_valid:
    print("✓ Validation passed (including profile validation)")
else:
    print("✗ Validation failed")
    for error in result.errors:
        print(f"  - {error}")
```

### Profile Registry

```python
from genesisgraph.profiles import ProfileRegistry

# Create registry
registry = ProfileRegistry()

# List available profiles
profiles = registry.list_profiles()
print(f"Available profiles: {profiles}")
# Output: ['gg-ai-basic-v1', 'gg-cam-v1']

# Validate with specific profile
result = registry.validate_with_profile(data, profile_id='gg-cam-v1')

# Validate with compliance standards
compliance_results = registry.validate_with_compliance(
    data,
    compliance_standards=['ISO-9001', 'FDA-21-CFR-11']
)

for standard, result in compliance_results.items():
    print(f"{standard}: {result['compliance_level']}")
```

### Direct Compliance Validation

```python
from genesisgraph.compliance import ISO9001Validator, FDA21CFR11Validator

# ISO 9001 validation
iso_validator = ISO9001Validator()
iso_result = iso_validator.validate(data)

print(f"ISO 9001 Compliance: {iso_result['compliance_level']}")
print(f"Errors: {len(iso_result['errors'])}")
print(f"Warnings: {len(iso_result['warnings'])}")

# FDA 21 CFR Part 11 validation
fda_validator = FDA21CFR11Validator()
fda_result = fda_validator.validate(data)

print(f"FDA 21 CFR Part 11 Compliance: {fda_result['compliance_level']}")
```

## Profile Auto-Detection

Profiles can be automatically detected based on:

1. **Explicit declaration** in metadata:
   ```yaml
   metadata:
     profile: gg-ai-basic-v1
   ```

2. **Operation types** in the workflow:
   - AI operations (`ai_inference`, `ai_training`, etc.) → `gg-ai-basic-v1`
   - Manufacturing operations (`cnc_machining`, `additive_manufacturing`, etc.) → `gg-cam-v1`

3. **Compliance standards** in metadata:
   ```yaml
   metadata:
     compliance_standards:
       - ISO-9001
       - FDA-21-CFR-11
   ```

## Creating Custom Profiles

You can create custom profile validators by extending `BaseProfileValidator`:

```python
from genesisgraph.profiles.base import BaseProfileValidator

class CustomProfileValidator(BaseProfileValidator):
    profile_id = "custom-profile-v1"
    profile_version = "1.0.0"

    def _validate_operations(self, operations):
        errors = []
        # Add custom validation logic
        for op in operations:
            # Check operation requirements
            pass
        return errors

    def _validate_tools(self, tools):
        errors = []
        # Add custom tool validation
        return errors

# Register with registry
from genesisgraph.profiles import ProfileRegistry
registry = ProfileRegistry()
registry.register(CustomProfileValidator)
```

## Privacy-Preserving Validation

Profile validators support privacy-preserving workflows using redacted parameters:

```yaml
operations:
  - id: inference1
    type: ai_inference
    inputs: [data]
    outputs: [result]
    parameters:
      _redacted: true  # Parameters are redacted for privacy
    attestation:
      mode: verifiable
      attester: "did:example:operator"
      claim: "AI inference performed with approved parameters"
      policy_claims:
        - "temperature between 0.5 and 1.0"
        - "model version approved by regulatory authority"
```

When `_redacted: true` is present, validators check policy claims instead of actual parameter values.

## Roadmap

Future profiles planned for v0.3:

- **gg-sci-v1**: Scientific reproducibility
- **gg-supply-v1**: Supply chain traceability
- **gg-health-v1**: Healthcare and HIPAA compliance
- **gg-finance-v1**: Financial services and SOX compliance

## References

- [GenesisGraph Specification §10.2](../spec/MAIN_SPEC.md) - Profile Declaration
- [GenesisGraph Specification §11](../spec/MAIN_SPEC.md) - Roadmap
- [ISO 9001:2015](https://www.iso.org/standard/62085.html) - Quality Management Systems
- [FDA 21 CFR Part 11](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/part-11-electronic-records-electronic-signatures-scope-and-application) - Electronic Records and Signatures
