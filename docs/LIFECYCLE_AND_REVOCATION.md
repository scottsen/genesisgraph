# GenesisGraph: Lifecycle & Revocation Framework

**Version:** 1.0
**Status:** Proposed Extension for v0.4.0
**Last Updated:** 2025-11-20

---

## Executive Summary

GenesisGraph documents currently capture **point-in-time snapshots**, but real-world trust is **temporal and dynamic**:

- Tool versions get revoked after CVE discoveries
- Datasets are found to be poisoned retroactively
- Certifications expire
- Licenses are terminated
- Transparency logs are updated after-the-fact

This document defines the **Lifecycle & Revocation Framework** for temporal validation of provenance, enabling auditors to answer:

- **"Was this tool version safe at the time of use?"**
- **"Had this dataset been revoked when the workflow ran?"**
- **"Was the license valid during execution?"**
- **"Can I trust this provenance created 6 months ago?"**

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Core Concepts](#core-concepts)
3. [Entity Lifecycle](#entity-lifecycle)
4. [Tool Lifecycle](#tool-lifecycle)
5. [Attestation Lifecycle](#attestation-lifecycle)
6. [Revocation Registry](#revocation-registry)
7. [Temporal Validation](#temporal-validation)
8. [Schema Extensions](#schema-extensions)
9. [Implementation Examples](#implementation-examples)
10. [Security Considerations](#security-considerations)

---

## Problem Statement

### Attack Scenarios

#### Scenario 1: Tool Version Revoked After Use

```yaml
# Workflow executed 2025-10-15
operations:
  - id: op_inference
    tool: ollama@2.3.1  # Used on 2025-10-15
    timestamp: 2025-10-15T14:00:00Z

# CVE-2025-12345 discovered 2025-10-20
# ollama@2.3.1 revoked 2025-10-20T00:00:00Z

# Auditor reviewing on 2025-11-01 asks:
# "Was this version safe *at the time of use*?"

# ❌ Current GenesisGraph cannot answer
```

**What's needed:**
- Revocation timestamp tracking
- Temporal validation (check if tool was valid on 2025-10-15, not now)
- Revocation reason (CVE vs. license termination vs. vendor closure)

---

#### Scenario 2: Dataset Corrupted Retroactively

```yaml
# Provenance references dataset
entities:
  - id: medical_corpus
    version: 2025-10-15
    hash: sha256:abc123...

# Dataset discovered to be poisoned on 2025-11-05
# All downstream workflows now suspect

# ❌ No revocation mechanism
# ❌ No way to mark entity as "compromised after creation"
```

**What's needed:**
- Entity revocation with timestamps
- Revocation propagation (mark all derived entities as suspect)
- Replacement entity references

---

#### Scenario 3: License Expires Mid-Execution

```yaml
tools:
  - id: proprietary_optimizer
    version: 5.2.0
    license:
      valid_from: 2025-01-01T00:00:00Z
      valid_until: 2025-06-30T23:59:59Z

operations:
  - id: op_optimize
    tool: proprietary_optimizer@5.2.0
    timestamp: 2025-07-15T10:00:00Z  # After license expiry!

# ❌ No temporal validation
```

**What's needed:**
- License validity period tracking
- Temporal policy evaluation
- Grace period support

---

#### Scenario 4: Transparency Log Consistency Proof Gaps

```yaml
attestation:
  transparency:
    - log_id: did:log:example
      entry_id: 0x5f2c8a91
      tree_size: 10000  # Log state at inclusion time

# Verifier checks 1 month later:
# - Log is now at tree_size: 50000
# - Need to prove log didn't fork between 10000 → 50000

# ❌ No consistency proof validation
```

**What's needed:**
- Consistency proof storage
- Historical tree state validation
- Fork detection

---

## Core Concepts

### 1. **Lifecycle State**

Every entity, tool, and attestation has a lifecycle:

```
Created → Active → Deprecated → Revoked/Expired
```

| State | Description | Valid for Use? |
|-------|-------------|----------------|
| **Created** | Just created, not yet active | No |
| **Active** | Fully valid and usable | Yes |
| **Deprecated** | Discouraged, but not forbidden | Yes (with warnings) |
| **Revoked** | No longer trustworthy | No |
| **Expired** | Time-based validity ended | No |

### 2. **Temporal Validity**

An artifact's validity depends on **when** it's evaluated:

```yaml
# Tool valid from 2024-01-01 to 2025-01-01
tool:
  lifecycle:
    valid_from: 2024-01-01T00:00:00Z
    valid_until: 2025-01-01T00:00:00Z

# Evaluation contexts:
# - At 2024-06-15: Valid ✓
# - At 2025-02-01: Expired ✗
# - At 2023-12-31: Not yet valid ✗
```

### 3. **Revocation vs. Expiration**

- **Expiration:** Predictable, time-based (licenses, certifications)
- **Revocation:** Unpredictable, event-based (security vulnerabilities, policy violations)

Both invalidate artifacts, but have different semantics.

### 4. **Revocation Timestamp**

Critical distinction:

```yaml
entity:
  lifecycle:
    created_at: 2025-01-01T00:00:00Z
    revoked_at: 2025-06-15T12:00:00Z
    revocation_reason: "Dataset found to contain poisoned samples"

# This entity was VALID from 2025-01-01 to 2025-06-15
# Workflows using it before 2025-06-15 are not retroactively invalid
# Workflows using it after 2025-06-15 are invalid
```

### 5. **Replacement Chains**

When artifacts are revoked, they often have replacements:

```yaml
entity:
  id: medical_corpus@v1
  lifecycle:
    revoked_at: 2025-06-15T00:00:00Z
    replacement: medical_corpus@v2
    # Points to fixed version
```

---

## Entity Lifecycle

### Entity Lifecycle Schema

```yaml
entities:
  - id: medical_corpus
    type: Dataset
    version: 2025-10-15
    hash: sha256:abc123...

    lifecycle:
      created_at: 2025-10-15T00:00:00Z
      valid_from: 2025-10-15T00:00:00Z
      valid_until: 2026-10-15T00:00:00Z  # Expiry (if applicable)

      deprecated_at: null
      deprecation_reason: null

      revoked_at: null
      revocation_reason: null
      revocation_authority: null

      replacement: null
      superseded_by: null

    provenance:
      lineage:
        - medical_corpus@2025-09-15  # Previous version
      derived_entities:
        - training_set@2025-10-16
        - test_set@2025-10-16
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `created_at` | ISO 8601 | When entity was created |
| `valid_from` | ISO 8601 | When entity becomes valid for use |
| `valid_until` | ISO 8601 | When entity expires (null = no expiry) |
| `deprecated_at` | ISO 8601 | When entity was marked deprecated |
| `deprecation_reason` | String | Why deprecated |
| `revoked_at` | ISO 8601 | When entity was revoked |
| `revocation_reason` | String | Why revoked (CVE, corruption, policy) |
| `revocation_authority` | DID | Who revoked it |
| `replacement` | Entity ID | Pointer to replacement entity |
| `superseded_by` | Entity ID | Newer version of same entity |

---

### Example: Dataset Revocation

```yaml
entities:
  # Original dataset (now revoked)
  - id: medical_corpus
    version: 2025-10-15
    hash: sha256:abc123...

    lifecycle:
      created_at: 2025-10-15T00:00:00Z
      valid_from: 2025-10-15T00:00:00Z
      valid_until: null  # No planned expiry

      revoked_at: 2025-11-05T14:30:00Z
      revocation_reason: "Data poisoning detected in 0.3% of samples (CVE-2025-98765)"
      revocation_authority: did:org:data-provider

      replacement: medical_corpus@2025-11-06-cleaned

    revocation_details:
      affected_samples: 342
      total_samples: 114203
      contamination_type: label_flipping
      detection_method: statistical_anomaly_analysis
      public_disclosure: https://provider.com/advisories/2025-11-05

  # Replacement dataset (clean)
  - id: medical_corpus
    version: 2025-11-06-cleaned
    hash: sha256:def456...

    lifecycle:
      created_at: 2025-11-06T08:00:00Z
      valid_from: 2025-11-06T08:00:00Z
      valid_until: null

      replaces: medical_corpus@2025-10-15

    provenance:
      derived_from:
        - medical_corpus@2025-10-15
      operation: filter_corrupted_samples
      samples_removed: 342
```

---

## Tool Lifecycle

### Tool Lifecycle Schema

```yaml
tools:
  - id: freecad
    type: Software
    version: 0.21.2
    vendor: FreeCAD Project

    lifecycle:
      released_at: 2024-06-01T00:00:00Z
      deprecated_at: null
      end_of_support: 2026-06-01T00:00:00Z

      revoked_at: null
      revocation_reason: null

      cve_refs: []
      security_advisories: []

      successor: freecad@0.22.0
      compatibility: backward_compatible

      license:
        type: LGPL-2.1
        valid_from: 2024-06-01T00:00:00Z
        valid_until: null  # Perpetual license
```

### Example: Tool Revocation (CVE)

```yaml
tools:
  - id: ollama
    type: Software
    version: 2.3.1
    vendor: Ollama Inc.

    lifecycle:
      released_at: 2025-09-15T00:00:00Z
      deprecated_at: 2025-10-22T00:00:00Z
      end_of_support: 2025-10-22T00:00:00Z

      revoked_at: 2025-10-20T00:00:00Z
      revocation_reason: "Critical security vulnerability (CVE-2025-12345): Remote code execution in model loading"
      revocation_authority: did:org:ollama-security-team

      cve_refs:
        - CVE-2025-12345
      security_advisories:
        - https://ollama.com/security/CVE-2025-12345

      successor: ollama@2.3.2  # Patched version
      compatibility: drop_in_replacement

    revocation_details:
      severity: critical
      cvss_score: 9.8
      exploit_available: true
      affected_versions: [2.3.0, 2.3.1]
      patch_version: 2.3.2
      workaround: "Disable remote model loading"
```

---

## Attestation Lifecycle

### Attestation Revocation

Attestations can be revoked (signature key compromised, false claims discovered):

```yaml
attestation:
  mode: verifiable
  signer: did:org:certification-body
  signature: ed25519:sig_abc123...
  timestamp: 2025-10-15T10:00:00Z

  lifecycle:
    issued_at: 2025-10-15T10:00:00Z
    expires_at: 2026-10-15T10:00:00Z

    revoked_at: 2025-11-01T14:00:00Z
    revocation_reason: "Certification body discovered fraudulent test results"
    revocation_authority: did:org:accreditation-authority

  revocation_registry: https://certs.example.com/revocations.json
  status_check_endpoint: https://certs.example.com/status/sig_abc123
```

### Revocation Registry Format

```json
{
  "registry_id": "https://certs.example.com/revocations.json",
  "updated_at": "2025-11-01T14:05:00Z",
  "revocations": [
    {
      "signature": "ed25519:sig_abc123...",
      "revoked_at": "2025-11-01T14:00:00Z",
      "reason": "Fraudulent test results discovered",
      "authority": "did:org:accreditation-authority",
      "scope": "all_attestations_from_signer"
    }
  ]
}
```

---

## Revocation Registry

### Registry Architecture

```yaml
revocation_registry:
  url: https://revocations.genesisgraph.dev/v1
  backend: transparency_log  # Rekor-compatible
  update_frequency: real_time

  entry_format:
    revoked_item_id: <entity_id | tool_id | signature>
    revoked_at: <ISO 8601>
    reason: <string>
    authority: <DID>
    evidence: <URI>
    scope: <specific | all_from_issuer>

  authentication:
    required: true
    method: did_based

  transparency:
    all_revocations_public: true
    log_id: did:log:revocations-genesisgraph
```

### Checking Revocation Status

**API Endpoint:**
```bash
GET https://revocations.genesisgraph.dev/v1/status/{item_id}

Response:
{
  "item_id": "sha256:abc123...",
  "status": "revoked",
  "revoked_at": "2025-11-01T14:00:00Z",
  "reason": "CVE-2025-12345",
  "authority": "did:org:vendor",
  "evidence": "https://vendor.com/advisories/CVE-2025-12345"
}
```

---

## Temporal Validation

### Validation at Specific Time

Verifiers MUST support `--at-time` parameter:

```bash
# Verify provenance as it was on 2025-10-15
genesisgraph validate workflow.gg.yaml \
  --at-time 2025-10-15T14:00:00Z \
  --check-revocations \
  --check-expirations
```

**Validation Logic:**

```python
def validate_at_time(provenance, validation_time):
    """Validate provenance as of a specific point in time."""

    for entity in provenance.entities:
        # Check if entity was valid at validation_time
        if entity.lifecycle.created_at > validation_time:
            raise ValidationError(f"Entity {entity.id} did not exist at {validation_time}")

        if entity.lifecycle.valid_from > validation_time:
            raise ValidationError(f"Entity {entity.id} not yet valid at {validation_time}")

        if entity.lifecycle.valid_until and entity.lifecycle.valid_until < validation_time:
            raise ValidationError(f"Entity {entity.id} expired at {validation_time}")

        # Check if entity was revoked BEFORE validation_time
        if entity.lifecycle.revoked_at and entity.lifecycle.revoked_at < validation_time:
            raise ValidationError(f"Entity {entity.id} was revoked before {validation_time}")

    for tool in provenance.tools:
        # Similar checks for tools
        if tool.lifecycle.revoked_at and tool.lifecycle.revoked_at < validation_time:
            raise ValidationError(f"Tool {tool.id} was revoked before {validation_time}")

    # Success: Provenance was valid at validation_time
    return True
```

---

### Freshness Requirements

Some use cases require **recent** provenance:

```yaml
policy:
  freshness_requirements:
    max_age_hours: 24
    # Provenance must be less than 24 hours old

validation_policy:
  at_time: now
  allow_deprecated: false
  allow_expired: false
  allow_revoked: false
  freshness_max_age: 86400  # 24 hours in seconds
```

---

## Schema Extensions

### Entity Lifecycle Fields

```yaml
entities:
  - id: <entity_id>
    lifecycle:
      created_at: <ISO 8601>
      valid_from: <ISO 8601>
      valid_until: <ISO 8601 | null>
      deprecated_at: <ISO 8601 | null>
      deprecation_reason: <string | null>
      revoked_at: <ISO 8601 | null>
      revocation_reason: <string | null>
      revocation_authority: <DID | null>
      replacement: <entity_id | null>
      superseded_by: <entity_id | null>
```

### Tool Lifecycle Fields

```yaml
tools:
  - id: <tool_id>
    lifecycle:
      released_at: <ISO 8601>
      deprecated_at: <ISO 8601 | null>
      end_of_support: <ISO 8601 | null>
      revoked_at: <ISO 8601 | null>
      revocation_reason: <string | null>
      cve_refs: [<CVE-ID>, ...]
      security_advisories: [<URI>, ...]
      successor: <tool_id | null>
      compatibility: <backward_compatible | breaking_changes | drop_in_replacement>
      license:
        type: <SPDX-ID>
        valid_from: <ISO 8601>
        valid_until: <ISO 8601 | null>
```

### Attestation Lifecycle Fields

```yaml
attestation:
  lifecycle:
    issued_at: <ISO 8601>
    expires_at: <ISO 8601 | null>
    revoked_at: <ISO 8601 | null>
    revocation_reason: <string | null>
    revocation_authority: <DID | null>
  revocation_registry: <URI>
  status_check_endpoint: <URI>
```

---

## Implementation Examples

### Example 1: Temporal Validation Script

```python
#!/usr/bin/env python3
"""Verify provenance with temporal validation."""

import sys
from datetime import datetime
from genesisgraph import GenesisGraphValidator

def main():
    if len(sys.argv) < 3:
        print("Usage: verify_lifecycle.py <file> --at-time <ISO8601>")
        sys.exit(1)

    file_path = sys.argv[1]
    validation_time = datetime.fromisoformat(sys.argv[3])

    validator = GenesisGraphValidator(
        verify_signatures=True,
        check_revocations=True,
        check_expirations=True,
        validation_time=validation_time
    )

    result = validator.validate_file(file_path)

    if result.valid:
        print(f"✓ Provenance was valid at {validation_time}")
    else:
        print(f"✗ Provenance was NOT valid at {validation_time}")
        for error in result.errors:
            print(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
# Was this workflow valid on 2025-10-15?
python scripts/verify_lifecycle.py workflow.gg.yaml \
  --at-time 2025-10-15T14:00:00Z

# Output:
# ✓ Provenance was valid at 2025-10-15T14:00:00Z
```

---

### Example 2: Revocation Propagation

When an entity is revoked, all derived entities are suspect:

```yaml
entities:
  # Original dataset (revoked)
  - id: base_dataset
    version: 2025-10-01
    lifecycle:
      revoked_at: 2025-11-01T00:00:00Z
      revocation_reason: "Data poisoning"

  # Training set (derived from base_dataset)
  - id: training_set
    version: 2025-10-05
    derived_from: [base_dataset@2025-10-01]
    lifecycle:
      created_at: 2025-10-05T00:00:00Z
      # Not explicitly revoked, but derived from revoked entity
      tainted_by: base_dataset@2025-10-01

  # Model (derived from training_set)
  - id: trained_model
    version: 2025-10-10
    derived_from: [training_set@2025-10-05]
    lifecycle:
      created_at: 2025-10-10T00:00:00Z
      # Also tainted
      tainted_by: training_set@2025-10-05

# Validator should warn:
# ⚠️  trained_model derived from revoked entity base_dataset (via training_set)
```

---

### Example 3: License Expiration

```yaml
tools:
  - id: proprietary_optimizer
    version: 5.2.0
    vendor: OptimizeCorp

    lifecycle:
      released_at: 2024-01-01T00:00:00Z

      license:
        type: Commercial
        license_key: ABC-123-XYZ-789
        valid_from: 2025-01-01T00:00:00Z
        valid_until: 2025-06-30T23:59:59Z
        seats: 5

operations:
  - id: op_optimize
    tool: proprietary_optimizer@5.2.0
    timestamp: 2025-05-15T10:00:00Z  # Within license period ✓

attestation:
  license_compliance:
    tool: proprietary_optimizer@5.2.0
    license_valid_at_execution: true
    license_expiry: 2025-06-30T23:59:59Z
    days_until_expiry: 46
```

---

## Security Considerations

### 1. **Backdating Revocations**

**Attack:** Malicious actor claims revocation happened earlier than it did.

**Defense:**
- Revocations MUST be published to transparency log
- Revocation timestamp comes from log inclusion proof
- Cannot backdate without rewriting log (detected via consistency proofs)

### 2. **Revocation Registry Compromise**

**Attack:** Attacker controls revocation registry, falsely marks artifacts as revoked.

**Defense:**
- Multi-registry witnessing (require 2+ independent registries)
- Registry entries signed by revocation authority (DID-based)
- Transparency log for all revocation events

### 3. **Revocation Check Bypass**

**Attack:** Verifier skips revocation checking.

**Defense:**
- Security policies MUST enforce revocation checking
- Profile validators (gg-sec-3+) require revocation checks
- Document MUST declare if revocation checking was skipped

### 4. **Time Manipulation**

**Attack:** Verifier uses incorrect `--at-time` to hide revocations.

**Defense:**
- Provenance SHOULD include `verified_at` timestamp in attestation
- Auditors can detect time manipulation
- Use trusted timestamp authorities (RFC 3161)

---

## Conclusion

The **Lifecycle & Revocation Framework** transforms GenesisGraph from:

> "Provenance of what happened"

to

> "Provenance of what was valid when it happened, and whether it's still valid now"

This is **essential** for:
- ✅ Forensic analysis ("Was this safe at the time?")
- ✅ Regulatory compliance (license validation, expiration tracking)
- ✅ Security incident response (revoke compromised tools/data)
- ✅ Long-term archival (understand validity in historical context)
- ✅ Supply chain security (track CVEs, revocations)

**Next Steps:**
1. Implement temporal validation in `GenesisGraphValidator`
2. Create revocation registry infrastructure
3. Add `scripts/verify_lifecycle.py` tool
4. Build revocation propagation logic
5. Integrate with CVE databases for automatic tool revocation

---

**Document Status:** Proposed for v0.4.0
**Intended Audience:** Security teams, compliance officers, auditors
**License:** CC-BY 4.0

---

**Version History:**
- 1.0 (2025-11-20): Initial lifecycle and revocation framework definition
