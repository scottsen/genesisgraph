# GenesisGraph: Delegation & Authorization Model

**Version:** 1.0
**Status:** Proposed Extension for v0.4.0
**Last Updated:** 2025-11-20

---

## Executive Summary

GenesisGraph currently captures **what happened** but not **whether the agent doing it was allowed to**.

This document defines the **delegation and authorization model** for GenesisGraph, enabling provenance that answers:

- **Who authorized this operation?**
- **Under what constraints?**
- **Through what delegation chain?**
- **What policy governed the decision?**
- **Was the authority valid at the time?**

This closes the **"authority → accountability" loop** essential for AI agent ecosystems, manufacturing automation, and regulated workflows.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Core Concepts](#core-concepts)
3. [Delegation Model](#delegation-model)
4. [Authorization Proofs](#authorization-proofs)
5. [Policy Integration](#policy-integration)
6. [Schema Extensions](#schema-extensions)
7. [Implementation Examples](#implementation-examples)
8. [Security Considerations](#security-considerations)
9. [Integration with Standards](#integration-with-standards)

---

## Problem Statement

### Current Gap

```yaml
operations:
  - id: op_inference
    tool: llama3_70b@3.0
    inputs: [patient_records@2025]
    outputs: [diagnosis_suggestion@1]

    # ❌ Missing: Was this model authorized to access patient records?
    # ❌ Missing: Under what HIPAA delegation?
    # ❌ Missing: What constraints were enforced?
    # ❌ Missing: Can we prove delegation was valid at execution time?
```

### Real-World Scenarios Blocked

1. **AI Agent Authorization (Healthcare)**
   > "Prove this AI agent was authorized to access patient records under HIPAA delegation from Dr. Sarah Chen"

2. **Manufacturing Delegation**
   > "Prove the CNC operator had valid certification when machining this aerospace part"

3. **Research Data Access**
   > "Prove the postdoc had IRB approval when analyzing this human subjects dataset"

4. **Multi-Agent Workflows**
   > "Prove Agent A delegated authority to Agent B to invoke Tool C with constraints D"

---

## Core Concepts

### 1. **Delegation Chain**

A **delegation chain** is a sequence of authority transfers from an initial grantor to a final grantee.

```
Organization → Manager → Engineer → AI Agent → External Tool
```

Each link specifies:
- **Grantor** (who delegates)
- **Grantee** (who receives authority)
- **Capability** (what they can do)
- **Constraints** (under what conditions)
- **Validity Period** (when authority is active)

### 2. **Capability**

A **capability** is a permission to perform an operation class.

Examples:
- `medical_data_access` - Read patient records
- `cnc_machining` - Operate CNC machine
- `inference_with_phi` - Run inference on PHI (Protected Health Information)
- `code_execution` - Execute arbitrary code

Capabilities are **scoped** (not global).

### 3. **Constraints (Caveats)**

**Constraints** limit how a capability can be exercised.

Examples:
- **Rate limits:** `max_records_per_day: 100`
- **Data scope:** `department: cardiology_only`
- **Time windows:** `valid_hours: "09:00-17:00"`
- **Audit requirements:** `logging: required`

Inspired by **Macaroons** (bearer tokens with caveats).

### 4. **Policy Evaluation**

Before an operation executes, a **policy engine** evaluates:
- Is the delegation chain valid?
- Are all constraints satisfied?
- Are there any revocations?

The policy decision is recorded in provenance.

---

## Delegation Model

### Delegation Object Schema

```yaml
delegation_chain:
  - grantor: did:org:hospital-west
    grantee: did:person:dr_sarah_chen
    capability: medical_data_access
    credential: vc:hipaa-delegation-2025-11-15
    issued_at: 2025-01-01T00:00:00Z
    expires_at: 2025-12-31T23:59:59Z
    constraints:
      departments: [cardiology, emergency]
      data_retention: prohibited
      audit_logging: required

  - grantor: did:person:dr_sarah_chen
    grantee: did:agent:claude-assistant-alpha
    capability: inference_with_phi
    credential: vc:agent-delegation-abc123
    issued_at: 2025-11-15T08:00:00Z
    expires_at: 2025-11-15T18:00:00Z
    constraints:
      max_records_per_session: 50
      allowed_models: [claude-sonnet-4]
      purpose: diagnostic_assistance
      human_review_required: true

  - grantor: did:agent:claude-assistant-alpha
    grantee: did:svc:anthropic-inference-api
    capability: model_inference
    credential: session_token:xyz789
    issued_at: 2025-11-15T10:30:00Z
    expires_at: 2025-11-15T10:35:00Z
    constraints:
      temperature_max: 0.3
      max_tokens: 4000
      safety_filters: enabled
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `grantor` | DID | ✅ | Entity delegating authority |
| `grantee` | DID | ✅ | Entity receiving authority |
| `capability` | String | ✅ | Permission being granted |
| `credential` | URI/VC | ✅ | Verifiable credential proving delegation |
| `issued_at` | ISO 8601 | ✅ | When delegation became active |
| `expires_at` | ISO 8601 | ✅ | When delegation expires |
| `constraints` | Object | ❌ | Additional restrictions on capability |
| `revocation_registry` | URI | ❌ | Where to check if delegation was revoked |

---

## Authorization Proofs

### Operation with Authorization

```yaml
operations:
  - id: op_inference_patient_diagnosis
    type: ai_inference
    tool: claude-sonnet-4@20250929
    agent: did:agent:claude-assistant-alpha

    inputs:
      - patient_records@2025-11-15
    outputs:
      - diagnosis_suggestion@1

    parameters:
      temperature: 0.2
      max_tokens: 2000

    # 🆕 Authorization section
    authorization:
      delegated_by: did:person:dr_sarah_chen
      delegation_chain:
        - grantor: did:org:hospital-west
          grantee: did:person:dr_sarah_chen
          capability: medical_data_access
          credential: vc:hipaa-delegation-2025
          issued_at: 2025-01-01T00:00:00Z
          expires_at: 2025-12-31T23:59:59Z
          constraints:
            departments: [cardiology, emergency]

        - grantor: did:person:dr_sarah_chen
          grantee: did:agent:claude-assistant-alpha
          capability: inference_with_phi
          credential: vc:agent-delegation-abc123
          issued_at: 2025-11-15T08:00:00Z
          expires_at: 2025-11-15T18:00:00Z
          constraints:
            max_records_per_session: 50
            human_review_required: true

      # 🆕 Policy evaluation
      policy_evaluation:
        policy_id: hipaa-safe-harbor-v1
        decision: permit
        evaluated_at: 2025-11-15T10:30:22Z
        evaluator: did:svc:opa-policy-engine
        evaluation_trace: base64:eyJpbnB1dCI6eyJhZ2VudC...
        constraints_satisfied:
          - constraint: max_records_per_session
            limit: 50
            actual: 12
            satisfied: true
          - constraint: human_review_required
            required: true
            human_reviewer: did:person:dr_sarah_chen
            satisfied: true

        all_constraints_met: true

    attestation:
      mode: verifiable
      signer: did:agent:claude-assistant-alpha
      signature: ed25519:sig_abc123...
      timestamp: 2025-11-15T10:30:25Z
```

---

## Policy Integration

GenesisGraph integrates with standard policy engines:

### 1. Open Policy Agent (OPA/Rego)

```rego
# Example policy: HIPAA Safe Harbor
package genesisgraph.hipaa

default allow = false

allow {
    # Check delegation chain is complete
    valid_delegation_chain

    # Check all constraints satisfied
    all_constraints_met

    # Check human review if required
    human_review_present

    # Check no revocations
    no_revocations
}

valid_delegation_chain {
    # Delegation starts from authorized organization
    input.delegation_chain[0].grantor == "did:org:hospital-west"

    # Each link is valid
    every link in input.delegation_chain {
        link.expires_at > now()
        link.issued_at < now()
    }
}

all_constraints_met {
    # Temperature constraint
    input.operation.parameters.temperature <= 0.3

    # Record limit
    count(input.operation.inputs) <= 50
}

human_review_present {
    input.authorization.policy_evaluation.constraints_satisfied[_].constraint == "human_review_required"
    input.authorization.policy_evaluation.constraints_satisfied[_].satisfied == true
}
```

### 2. AWS Cedar

```cedar
// Example policy: Manufacturing certification required
permit (
    principal is Agent,
    action == Action::"operate_cnc",
    resource is Part
)
when {
    // Principal has valid certification
    principal.certifications.contains("cnc_operator_level_2") &&
    principal.certification_expiry > context.time &&

    // Delegation chain is valid
    context.delegation_chain.all(link =>
        link.expires_at > context.time &&
        !link.revoked
    ) &&

    // Part requires level 2 or lower
    resource.required_certification_level <= 2
};
```

### 3. Policy Evaluation Trace

The policy engine MUST record:

```yaml
policy_evaluation:
  policy_id: hipaa-safe-harbor-v1
  policy_version: 2.1.0
  policy_hash: sha256:policy_def_hash...

  decision: permit  # permit | deny
  evaluated_at: 2025-11-15T10:30:22Z
  evaluator: did:svc:opa-policy-engine

  # Full OPA evaluation trace (for auditability)
  evaluation_trace: base64:eyJpbnB1dCI6eyJhZ2VudC...

  # Human-readable constraint results
  constraints_satisfied:
    - constraint: temperature_max
      limit: 0.3
      actual: 0.2
      satisfied: true

    - constraint: max_records_per_session
      limit: 50
      actual: 12
      satisfied: true

    - constraint: human_review_required
      required: true
      reviewer: did:person:dr_sarah_chen
      review_timestamp: 2025-11-15T10:32:00Z
      satisfied: true

  all_constraints_met: true

  # If denied, why?
  denial_reason: null
```

---

## Schema Extensions

### New Top-Level Fields

```yaml
# operations.authorization (NEW)
operations:
  - id: op_example
    authorization:
      delegated_by: <DID>
      delegation_chain: [<Delegation>, ...]
      policy_evaluation: <PolicyEvaluation>
```

### Delegation Object

```yaml
delegation:
  grantor: <DID>
  grantee: <DID>
  capability: <string>
  credential: <URI or VC>
  issued_at: <ISO 8601>
  expires_at: <ISO 8601>
  constraints: <Object>
  revocation_registry: <URI>
```

### PolicyEvaluation Object

```yaml
policy_evaluation:
  policy_id: <string>
  policy_version: <semver>
  policy_hash: <hash>
  decision: <permit|deny>
  evaluated_at: <ISO 8601>
  evaluator: <DID>
  evaluation_trace: <base64>
  constraints_satisfied: [<ConstraintResult>, ...]
  all_constraints_met: <boolean>
  denial_reason: <string|null>
```

### ConstraintResult Object

```yaml
constraint_result:
  constraint: <string>
  limit: <any>
  actual: <any>
  satisfied: <boolean>
  details: <Object>
```

---

## Implementation Examples

### Example 1: AI Agent with HIPAA Delegation

**Scenario:** AI assistant analyzes patient records with explicit authorization chain.

```yaml
spec_version: 0.4.0
profile: gg-ai-delegation-v1

operations:
  - id: op_patient_analysis
    type: ai_inference
    tool: claude-sonnet-4@20250929
    agent: did:agent:claude-medical-assistant

    inputs:
      - patient_records_cardiology@2025-11-15
    outputs:
      - treatment_recommendations@1

    authorization:
      delegated_by: did:person:dr_sarah_chen
      delegation_chain:
        # Hospital → Doctor
        - grantor: did:org:hospital-west
          grantee: did:person:dr_sarah_chen
          capability: medical_data_access
          credential: vc:hipaa-delegation-2025
          issued_at: 2025-01-01T00:00:00Z
          expires_at: 2025-12-31T23:59:59Z
          constraints:
            departments: [cardiology]
            data_retention: prohibited

        # Doctor → AI Agent
        - grantor: did:person:dr_sarah_chen
          grantee: did:agent:claude-medical-assistant
          capability: inference_with_phi
          credential: vc:agent-delegation-20251115
          issued_at: 2025-11-15T08:00:00Z
          expires_at: 2025-11-15T20:00:00Z
          constraints:
            max_records_per_day: 100
            human_review_required: true
            audit_logging: required

      policy_evaluation:
        policy_id: hipaa-safe-harbor-v1
        decision: permit
        evaluated_at: 2025-11-15T10:30:22Z
        evaluator: did:svc:opa-policy-engine
        constraints_satisfied:
          - constraint: max_records_per_day
            limit: 100
            actual: 12
            satisfied: true
          - constraint: human_review_required
            required: true
            reviewer: did:person:dr_sarah_chen
            review_timestamp: 2025-11-15T11:00:00Z
            satisfied: true
        all_constraints_met: true

    attestation:
      mode: verifiable
      signer: did:person:dr_sarah_chen
      signature: ed25519:human_attestation_sig...
      timestamp: 2025-11-15T11:05:00Z
```

---

### Example 2: Manufacturing with Certification Chain

**Scenario:** CNC operator machines aerospace part with certification validation.

```yaml
spec_version: 0.4.0
profile: gg-cam-delegation-v1

operations:
  - id: op_cnc_machining
    type: subtractive_manufacturing
    tool: haas_vf2@2024.1
    operator: did:person:john_smith_operator

    inputs:
      - titanium_blank@lot_T789
    outputs:
      - turbine_blade@serial_TB-2025-001

    authorization:
      delegated_by: did:org:aerospace-facility-phoenix
      delegation_chain:
        # Facility → Lead Engineer
        - grantor: did:org:aerospace-facility-phoenix
          grantee: did:person:lead_engineer_jane
          capability: approve_critical_machining
          credential: vc:engineer-authorization-2025
          issued_at: 2025-01-01T00:00:00Z
          expires_at: 2025-12-31T23:59:59Z
          constraints:
            part_classification: [critical, flight_critical]
            certification_level_min: 2

        # Lead Engineer → Operator
        - grantor: did:person:lead_engineer_jane
          grantee: did:person:john_smith_operator
          capability: operate_cnc_level_2
          credential: vc:cnc-certification-john-smith
          issued_at: 2024-06-15T00:00:00Z
          expires_at: 2026-06-15T23:59:59Z
          constraints:
            materials: [aluminum, titanium, steel]
            max_part_value_usd: 50000
            supervision_required: false

      policy_evaluation:
        policy_id: as9100d-machining-v1
        decision: permit
        evaluated_at: 2025-11-15T14:22:00Z
        evaluator: did:svc:cedar-policy-engine
        constraints_satisfied:
          - constraint: certification_level
            required: 2
            actual: 2
            satisfied: true
          - constraint: material_approved
            allowed: [aluminum, titanium, steel]
            actual: titanium
            satisfied: true
          - constraint: certification_valid
            expires_at: 2026-06-15T23:59:59Z
            current_time: 2025-11-15T14:22:00Z
            satisfied: true
        all_constraints_met: true

    attestation:
      mode: verifiable
      multisig:
        threshold: 2
        signers:
          - did:person:john_smith_operator
          - did:person:qa_inspector_maria
      transparency:
        - log_id: did:log:aerospace-compliance
          entry_id: 0x9a8b7c6d
          inclusion_proof: base64:...
```

---

### Example 3: Research IRB Approval Chain

**Scenario:** Postdoc analyzes human subjects data with IRB delegation.

```yaml
spec_version: 0.4.0
profile: gg-research-delegation-v1

operations:
  - id: op_data_analysis
    type: statistical_analysis
    tool: python_scipy@1.11.0
    researcher: did:person:postdoc_alex

    inputs:
      - survey_responses@study_2025_01
    outputs:
      - statistical_results@preliminary

    authorization:
      delegated_by: did:org:university-irb
      delegation_chain:
        # IRB → Principal Investigator
        - grantor: did:org:university-irb
          grantee: did:person:prof_dr_chen
          capability: access_human_subjects_data
          credential: vc:irb-approval-study-2025-01
          issued_at: 2025-01-10T00:00:00Z
          expires_at: 2026-01-10T23:59:59Z
          constraints:
            study_id: study_2025_01
            data_usage: analysis_only
            publication_approval_required: true

        # PI → Postdoc
        - grantor: did:person:prof_dr_chen
          grantee: did:person:postdoc_alex
          capability: perform_analysis
          credential: vc:researcher-delegation-alex
          issued_at: 2025-03-01T00:00:00Z
          expires_at: 2025-12-31T23:59:59Z
          constraints:
            training_completed: [citi_human_subjects, data_privacy]
            supervision_level: weekly_review
            data_export: prohibited

      policy_evaluation:
        policy_id: irb-protocol-2025-01-v1
        decision: permit
        evaluated_at: 2025-11-15T09:15:00Z
        evaluator: did:svc:research-compliance-engine
        constraints_satisfied:
          - constraint: training_completed
            required: [citi_human_subjects, data_privacy]
            actual: [citi_human_subjects, data_privacy, gdpr_basics]
            satisfied: true
          - constraint: irb_approval_valid
            expires_at: 2026-01-10T23:59:59Z
            satisfied: true
          - constraint: data_export
            allowed: false
            actual: false
            satisfied: true
        all_constraints_met: true
```

---

## Security Considerations

### 1. **Delegation Chain Validation**

Verifiers MUST check:
- ✅ Each link in chain is temporally valid (issued_at < now < expires_at)
- ✅ Each grantee matches next grantor (chain is unbroken)
- ✅ No links have been revoked
- ✅ Credentials are cryptographically valid

### 2. **Constraint Enforcement**

- Constraints MUST be evaluated **before** operation execution
- Constraint violations MUST prevent operation execution
- Constraint satisfaction MUST be recorded in provenance

### 3. **Revocation Checking**

- Verifiers SHOULD check revocation registries for all credentials
- Revoked credentials invalidate the entire delegation chain
- Revocation checks SHOULD be cached with TTL

### 4. **Policy Engine Trust**

- Policy evaluator DID MUST be verifiable
- Evaluation trace MUST be cryptographically signed
- Policy definitions SHOULD be content-addressed (hash-identified)

### 5. **Replay Protection**

- Delegation chains SHOULD include nonces or operation-specific binding
- Prevent reuse of delegation proofs across operations

---

## Integration with Standards

### 1. **ZCAP-LD (W3C Authorization Capabilities)**

GenesisGraph delegation chains can reference ZCAP-LD capabilities:

```yaml
delegation_chain:
  - grantor: did:org:example
    grantee: did:person:alice
    capability: read_resource
    credential: zcap:https://example.com/zcaps/abc123
    # ZCAP-LD provides proof chain, caveats, invocation proofs
```

### 2. **Verifiable Credentials (W3C VC)**

Credentials can be full Verifiable Credentials:

```yaml
delegation_chain:
  - credential:
      type: VerifiableCredential
      issuer: did:org:hospital
      issuanceDate: 2025-01-01T00:00:00Z
      expirationDate: 2025-12-31T23:59:59Z
      credentialSubject:
        id: did:person:dr_sarah_chen
        capability: medical_data_access
        constraints:
          departments: [cardiology]
      proof:
        type: Ed25519Signature2020
        verificationMethod: did:org:hospital#key-1
        signature: base64:sig...
```

### 3. **OAuth 2.0 / OpenID Connect**

For enterprise identity integration:

```yaml
delegation_chain:
  - grantor: did:org:enterprise
    grantee: did:person:employee
    credential: oauth2_token:eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
    # OAuth token includes scopes, expiry
```

### 4. **Macaroons**

For bearer tokens with caveats:

```yaml
delegation_chain:
  - credential: macaroon:base64_encoded_macaroon
    # Macaroon includes first-party and third-party caveats
```

---

## Profile: `gg-delegation-v1`

A new profile validator for delegation-aware provenance:

**Required Fields:**
- `operations[].authorization.delegated_by`
- `operations[].authorization.delegation_chain[]`
- `operations[].authorization.policy_evaluation`

**Validation Rules:**
1. Delegation chain MUST be unbroken (grantee[n] == grantor[n+1])
2. All links MUST be temporally valid at `evaluated_at` time
3. Policy decision MUST be `permit`
4. All constraints MUST be satisfied
5. Credentials MUST be verifiable (signatures valid, not revoked)

**Usage:**
```bash
genesisgraph validate workflow.gg.yaml --verify-profile --profile gg-delegation-v1
```

---

## Future Extensions

### 1. **Conditional Delegation**

Delegations that activate only when conditions are met:

```yaml
delegation_chain:
  - grantor: did:org:factory
    grantee: did:person:operator
    capability: operate_cnc
    conditions:
      - type: geo_fence
        location: factory_floor_A
      - type: time_window
        hours: "06:00-18:00"
      - type: supervisor_presence
        required: did:person:supervisor_bob
```

### 2. **Delegation Metering**

Track usage of delegated authority:

```yaml
delegation_chain:
  - grantor: did:org:api_provider
    grantee: did:agent:assistant
    capability: api_calls
    metering:
      quota: 1000_calls_per_day
      consumed: 247
      resets_at: 2025-11-16T00:00:00Z
```

### 3. **Cross-Organization Delegation**

Delegation chains spanning organizational boundaries:

```yaml
delegation_chain:
  # Organization A delegates to Organization B
  - grantor: did:org:supplier_a
    grantee: did:org:manufacturer_b
    capability: use_proprietary_design
    credential: vc:licensing-agreement-2025
    constraints:
      derivative_works: prohibited
      jurisdiction: [US, EU]
```

---

## Conclusion

The **Delegation & Authorization Model** transforms GenesisGraph from:

> "Provenance of what happened"

to

> "Provenance of what was allowed to happen, why, and by whom"

This is **essential** for:
- ✅ AI agent ecosystems (multi-agent authorization)
- ✅ Regulated industries (HIPAA, FDA, AS9100D)
- ✅ Manufacturing (operator certification, role-based access)
- ✅ Research (IRB compliance, data access controls)
- ✅ Supply chains (cross-organizational trust)

**Next Steps:**
1. Implement `gg-delegation-v1` profile validator
2. Create examples for common delegation patterns
3. Integrate with OPA/Cedar policy engines
4. Add revocation registry support
5. Build delegation chain visualization tools

---

**Document Status:** Proposed for v0.4.0
**Intended Audience:** Implementers, security architects, compliance teams
**License:** CC-BY 4.0

---

**Version History:**
- 1.0 (2025-11-20): Initial delegation and authorization model definition
