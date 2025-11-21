# Zero-Knowledge Proof Templates

GenesisGraph provides **zero-knowledge proof (ZKP) templates** for common compliance scenarios. These templates enable proving policy compliance without revealing sensitive parameters—solving the "certification vs IP protection" dilemma.

## Overview

ZKP templates are pre-built proof configurations for common use cases:

| Template | Use Case | Standards | Proves |
|----------|----------|-----------|--------|
| **ai_safety** | AI model safety | Internal policies | temp ≤ 1.0, tokens ≤ 100K, approved models |
| **ai_compliance** | AI regulatory compliance | FDA 21 CFR 11, AI Act | temp in range, prompt limits, human review |
| **manufacturing_qc** | Manufacturing QC | AS9100D, ISO 9001 | tolerances, hardness, operator certification |
| **research_bounds** | Research reproducibility | IRB, statistical standards | sample size, p-value, methodology approval |

---

## Quick Start

### Installation

```bash
pip install genesisgraph[credentials]
```

### Basic Usage

```python
from genesisgraph.credentials import get_template, apply_template

# Get AI safety template
template = get_template("ai_safety")

# Your actual values (kept private)
claims = {
    "temperature": 0.7,           # Proprietary tuning
    "max_tokens": 4096,           # Configuration secret
    "model": "claude-sonnet-4.5"  # Which model used
}

# Create ZKP proofs
proofs = apply_template(template, claims)

# All proofs satisfied?
all_satisfied = all(p.satisfied for p in proofs)

# Export for verification (actual values NOT included)
zkp_data = [p.to_dict() for p in proofs]
```

**Key Point:** The `proofs` contain cryptographic commitments, but NOT the actual values (0.7, 4096, "claude-sonnet-4.5"). Verifiers can confirm compliance without seeing your secrets.

---

## Available Templates

### 1. AI Safety Template

**Purpose:** Prove AI model follows safety guidelines

**Policy:** `ai-safety-v1`

**Required Claims:**
- `temperature` - Model randomness parameter
- `max_tokens` - Output length limit
- `model` - Model identifier

**Constraints:**
- Temperature ≤ 1.0 (prevent excessive randomness)
- Max tokens ≤ 100,000 (prevent resource abuse)
- Model in approved list (only vetted models)

**Example:**

```python
from genesisgraph.credentials import get_ai_safety_template, apply_template

template = get_ai_safety_template()

claims = {
    "temperature": 0.5,
    "max_tokens": 2048,
    "model": "claude-sonnet-4.5"
}

proofs = apply_template(template, claims)
# Returns 3 ZKP proofs, one per claim
```

**Use Cases:**
- Internal AI safety reviews
- External audits without revealing config
- Compliance with AI safety policies

---

### 2. AI Compliance Template

**Purpose:** Prove regulatory compliance (FDA 21 CFR 11, AI Act)

**Policy:** `ai-compliance-fda-21-cfr-11`

**Required Claims:**
- `temperature` - Model randomness
- `prompt_length` - Input prompt length
- `human_review_required` - Human oversight flag

**Constraints:**
- Temperature in [0.0, 0.7] (deterministic outputs)
- Prompt length ≤ 50,000 (prevent injection)
- Human review required = True (high-stakes decisions)

**Example:**

```python
from genesisgraph.credentials import get_ai_compliance_template, apply_template

template = get_ai_compliance_template()

claims = {
    "temperature": 0.3,
    "prompt_length": 15000,
    "human_review_required": True
}

proofs = apply_template(template, claims)
```

**Use Cases:**
- Medical AI compliance (FDA 21 CFR Part 11)
- Financial AI compliance (regulatory oversight)
- High-stakes decision systems (human-in-the-loop)

---

### 3. Manufacturing QC Template

**Purpose:** Prove manufacturing quality control compliance

**Policy:** `manufacturing-qc-as9100d`

**Required Claims:**
- `tolerance_mm` - Dimensional tolerance (millimeters)
- `hardness_hrc` - Material hardness (Rockwell C)
- `operator_certified` - Operator certification status

**Constraints:**
- Tolerance in [-0.01, 0.01] mm (ISO 2768)
- Hardness ≥ 55 HRC (material spec)
- Operator certified = True (AS9100D requirement)

**Example:**

```python
from genesisgraph.credentials import get_manufacturing_qc_template, apply_template

template = get_manufacturing_qc_template()

claims = {
    "tolerance_mm": 0.005,      # ±0.005mm
    "hardness_hrc": 60,         # 60 HRC
    "operator_certified": True
}

proofs = apply_template(template, claims)
```

**Use Cases:**
- Aerospace part certification (AS9100D)
- Medical device manufacturing (ISO 13485)
- Automotive quality control (IATF 16949)

---

### 4. Research Bounds Template

**Purpose:** Prove research meets methodological standards

**Policy:** `research-reproducibility-v1`

**Required Claims:**
- `sample_size` - Number of samples
- `p_value` - Statistical significance
- `methodology_approved` - IRB/ethics approval

**Constraints:**
- Sample size ≥ 30 (statistical power)
- p-value ≤ 0.05 (significance threshold)
- Methodology approved = True (ethics compliance)

**Example:**

```python
from genesisgraph.credentials import get_research_bounds_template, apply_template

template = get_research_bounds_template()

claims = {
    "sample_size": 120,
    "p_value": 0.03,
    "methodology_approved": True
}

proofs = apply_template(template, claims)
```

**Use Cases:**
- Pre-publication review (prove rigor without revealing results)
- Clinical trial compliance (FDA, IRB)
- Research funding validation (NIH, NSF)

---

## ZKP Proof Types

GenesisGraph supports five types of zero-knowledge proofs:

### 1. Range Proof

Prove value is in [min, max] without revealing exact value.

```python
from genesisgraph.credentials import create_range_proof

proof = create_range_proof(
    claim_name="temperature",
    actual_value=0.7,       # Hidden
    min_value=0.0,          # Public
    max_value=1.0,          # Public
)

assert proof.satisfied == True
# actual_value NOT in proof
```

### 2. Threshold Proof

Prove value meets threshold (≤, ≥, <, >) without revealing exact value.

```python
from genesisgraph.credentials import create_threshold_proof

proof = create_threshold_proof(
    claim_name="max_tokens",
    actual_value=2048,      # Hidden
    threshold=4096,         # Public
    comparison="lte",       # ≤
)

assert proof.satisfied == True
```

### 3. Set Membership Proof

Prove value is in allowed set without revealing which one.

```python
from genesisgraph.credentials import create_set_membership_proof

proof = create_set_membership_proof(
    claim_name="model",
    actual_value="claude-sonnet-4.5",  # Hidden which one
    allowed_set=["gpt-4", "claude-sonnet-4.5", "gemini-pro"],  # Public
)

assert proof.satisfied == True
```

### 4. Equality Proof

Prove value equals expected without revealing (useful for boolean flags).

```python
from genesisgraph.credentials import apply_template

# Equality proofs created automatically in templates
# E.g., operator_certified == True
```

### 5. Composite Proof

Combine multiple proofs with AND/OR logic.

```python
from genesisgraph.credentials import create_composite_proof

temp_proof = create_threshold_proof("temperature", 0.5, 1.0, "lte")
token_proof = create_threshold_proof("max_tokens", 2048, 4096, "lte")

composite = create_composite_proof([temp_proof, token_proof], logic="and")
assert composite.satisfied == True  # Both must be satisfied
```

---

## Verification

### Without Value Disclosure

```python
from genesisgraph.credentials import verify_zkp_proof

# Verifier sees proof without values
result = verify_zkp_proof(proof)

assert result["valid"] == True
assert result["satisfied"] == True
assert result["value_disclosed"] == False  # No value revealed
```

### With Value Disclosure (Auditing)

```python
# For auditing, holder can choose to disclose value
result = verify_zkp_proof(proof, disclosed_value=0.7)

assert result["valid"] == True
assert result["commitment_verified"] == True  # Proves value matches commitment
```

---

## Integration with GenesisGraph

ZKP templates integrate seamlessly with GenesisGraph attestations:

```yaml
# .gg.yaml file
operations:
  - id: ai_inference
    type: inference
    inputs: [query@1.0]
    outputs: [response@1.0]

    # Parameters hidden via ZKP
    parameters:
      _redacted: true

    # ZKP template attestation
    attestation:
      mode: zkp-template
      timestamp: "2025-01-20T12:00:00Z"

      zkp_template:
        template: ai_safety
        policy_id: ai-safety-v1

        proofs:
          - claim_name: temperature
            proof_type: threshold
            threshold: 1.0
            satisfied: true
            commitment: 7f3a8b2c1d4e5f6a...
            # actual value NOT included

          - claim_name: max_tokens
            proof_type: threshold
            threshold: 100000
            satisfied: true
            commitment: 1a2b3c4d5e6f7a8b...

          - claim_name: model
            proof_type: set_membership
            allowed_set: [gpt-4, claude-sonnet-4.5, gemini-pro]
            satisfied: true
            commitment: 9e8d7c6b5a4f3e2d...

        composite_proof:
          logic: and
          satisfied: true
          proof_count: 3
```

---

## Custom Templates

Create your own templates for domain-specific compliance:

```python
from genesisgraph.credentials import ZKPTemplate, TemplateType, apply_template

# Define custom template
custom_template = ZKPTemplate(
    template_type=TemplateType.CUSTOM,
    name="HIPAA PHI Protection",
    description="Prove HIPAA compliance for PHI processing",
    required_claims=["encryption_strength", "access_logged", "audit_enabled"],
    proof_specs={
        "encryption_strength": {
            "type": "threshold",
            "threshold": 256,
            "comparison": "gte",
            "rationale": "HIPAA requires AES-256",
        },
        "access_logged": {
            "type": "equality",
            "expected_value": True,
            "rationale": "HIPAA audit trail requirement",
        },
        "audit_enabled": {
            "type": "equality",
            "expected_value": True,
            "rationale": "HIPAA monitoring requirement",
        },
    },
    policy_id="hipaa-phi-v1",
    version="1.0",
)

# Apply custom template
claims = {
    "encryption_strength": 256,
    "access_logged": True,
    "audit_enabled": True,
}

proofs = apply_template(custom_template, claims)
```

---

## Comparison: ZKP Templates vs Other Methods

| Method | IP Protection | Compliance Proof | Unlinkability | Complexity |
|--------|---------------|------------------|---------------|------------|
| **Full Disclosure** | ❌ None | ✅ Full | ❌ No | ★☆☆☆ |
| **Predicates** | ✅ Good | ✅ Good | ❌ No | ★★☆☆ |
| **ZKP Templates** | ✅ **Excellent** | ✅ **Excellent** | ❌ No | ★★★☆ |
| **BBS+ Signatures** | ✅ Excellent | ✅ Good | ✅ **Yes** | ★★★★ |

**When to Use:**

- **ZKP Templates**: Default choice for compliance scenarios
- **Predicates**: Simple range proofs, single claims
- **BBS+**: When unlinkability required (anti-correlation)
- **Combine ZKP + BBS+**: Maximum privacy (policy compliance + unlinkability)

---

## Security Considerations

### Cryptographic Commitments

ZKP templates use **commitment schemes** (SHA-256 hash of value + salt):

```
commitment = SHA-256(salt || value)
```

**Properties:**
- ✅ **Binding**: Cannot change value without changing commitment
- ✅ **Hiding**: Commitment reveals nothing about value
- ✅ **Verifiable**: Holder can later disclose value to verify commitment

### Limitations

⚠️ **Important:** This implementation provides **practical ZKP templates** using commitment-based proofs. For production systems requiring formal security guarantees:

- **Range proofs**: Use Bulletproofs or zkSNARKs
- **Set membership**: Use accumulators (RSA, Merkle)
- **Complex policies**: Use zkSNARKs (Groth16, PLONK)

The current implementation is suitable for:
- ✅ Enterprise IP protection
- ✅ Regulatory compliance documentation
- ✅ Audit trails with selective disclosure
- ✅ Multi-party verification workflows

Not suitable for:
- ❌ High-security cryptographic protocols
- ❌ Blockchain/cryptocurrency applications
- ❌ Systems requiring formal security proofs

---

## Examples

See complete examples:

- **AI Safety:** `examples/zkp-ai-safety-attestation.gg.yaml`
- **Manufacturing:** `examples/zkp-manufacturing-qc-attestation.gg.yaml`

---

## API Reference

### Template Functions

```python
# Get template by name
template = get_template("ai_safety")

# List all templates
templates = list_templates()

# Apply template to claims
proofs = apply_template(template, claims)

# Verify proof
result = verify_zkp_proof(proof, disclosed_value=None)
```

### Individual Proof Functions

```python
# Create individual proofs
range_proof = create_range_proof(claim, value, min, max)
threshold_proof = create_threshold_proof(claim, value, threshold, "lte")
set_proof = create_set_membership_proof(claim, value, allowed_set)
composite_proof = create_composite_proof(proofs, logic="and")
```

### Template Classes

```python
from genesisgraph.credentials import ZKPProof, ZKPTemplate, ZKPType, TemplateType

# See docstrings for complete API
help(ZKPProof)
help(ZKPTemplate)
```

---

## Roadmap

**v0.3 (Current):**
- ✅ Commitment-based ZKP templates
- ✅ 4 pre-built templates (AI, manufacturing, research)
- ✅ Composite proofs (AND/OR logic)
- ✅ Verification with optional disclosure

**v0.4 (Planned):**
- [ ] Bulletproofs integration (true range proofs)
- [ ] zkSNARK templates (complex policies)
- [ ] Accumulator-based set membership
- [ ] Interactive proof protocols

**v0.5 (Future):**
- [ ] Groth16 zkSNARKs
- [ ] Recursive proof composition
- [ ] Cross-chain verification
- [ ] Hardware acceleration (GPU)

---

## References

- **Commitment Schemes**: [Cryptographic Commitments (Wikipedia)](https://en.wikipedia.org/wiki/Commitment_scheme)
- **Bulletproofs**: [Bulletproofs Paper](https://eprint.iacr.org/2017/1066.pdf)
- **zkSNARKs**: [zkSNARKs Explained](https://z.cash/technology/zksnarks/)
- **GenesisGraph Spec**: `spec/MAIN_SPEC.md` §9.2 (Selective Disclosure)

---

## Support

For questions or issues:

- **GitHub Issues**: https://github.com/scottsen/genesisgraph/issues
- **Documentation**: https://genesisgraph.dev
- **Email**: support@genesisgraph.dev

---

**Last Updated:** 2025-11-20
**Version:** 0.3.0
