# SD-JWT & BBS+ Selective Disclosure

GenesisGraph supports advanced cryptographic selective disclosure methods to enable privacy-preserving verifiable provenance. This document explains the selective disclosure features and how to use them.

## Overview

Selective disclosure allows proving claims about data or operations **without revealing the exact values**. This is critical for:

- **Enterprise IP Protection**: Prove model compliance without revealing proprietary parameters
- **Regulatory Compliance**: Demonstrate policy adherence while protecting trade secrets
- **Privacy Preservation**: Share minimal necessary information with verifiers
- **Anti-Correlation**: Prevent tracking across multiple verifications (BBS+)

## Supported Methods

GenesisGraph implements three selective disclosure methods:

| Method | Standard | Unlinkable | Use Case |
|--------|----------|-----------|----------|
| **SD-JWT** | IETF RFC | No | Standard web authentication, OAuth/OIDC integration |
| **Predicates** | Custom | No | Range proofs (e.g., "temp ≤ 0.3"), compliance checking |
| **BBS+** | IETF/W3C Draft | **Yes** | Privacy-critical scenarios, anti-tracking |

## Installation

Install the credentials module:

```bash
pip install genesisgraph[credentials]
```

This installs:
- `sd-jwt` - IETF SD-JWT reference implementation
- `jwcrypto` - JWT/JWK handling
- `zksk` - Zero-knowledge proof toolkit
- `petlib` - Pairing-based cryptography (for BBS+)

## 1. SD-JWT (Selective Disclosure JWT)

### What is SD-JWT?

SD-JWT is an IETF standard for selective disclosure within JSON Web Tokens. It uses hash-based commitments to enable:
- Selective revelation of claims
- Cryptographic verification of disclosed claims
- Compatibility with existing JWT infrastructure

### When to Use SD-JWT

✅ **Use SD-JWT when:**
- Integrating with OAuth/OIDC systems
- Need for standard JWT compatibility
- Rapid deployment is priority
- Linkability is acceptable

❌ **Don't use SD-JWT when:**
- Anti-correlation is critical
- Need to prevent tracking across verifiers
- Require true unlinkability

### Creating SD-JWT Attestations

```python
from genesisgraph.credentials.sd_jwt import SDJWTIssuer

# Create issuer
issuer = SDJWTIssuer(issuer_did="did:web:api.anthropic.com")

# Define claims
claims = {
    "model": "claude-sonnet-4.5",      # Always disclosed
    "temperature": 0.25,                # Selectively disclosable
    "max_tokens": 4096,                 # Selectively disclosable
    "prompt_hash": "sha256:abc123"     # Always disclosed
}

# Create SD-JWT
sd_jwt = issuer.create_sd_jwt(
    claims=claims,
    selectively_disclosable=["temperature", "max_tokens"],
    validity_seconds=86400  # 24 hours
)
```

### Using SD-JWT in GenesisGraph

```yaml
attestation:
  mode: sd-jwt
  timestamp: "2025-01-20T12:00:00Z"
  sd_jwt:
    sd_jwt: "eyJhbGc..."  # The SD-JWT token
    disclosures:
      - claim_name: temperature
        claim_value: 0.25
        salt: random_salt
        hash: sha256:hash_commitment
    issuer: did:web:api.anthropic.com
    algorithm: EdDSA
```

### Verifying SD-JWT

```python
from genesisgraph.credentials.sd_jwt import SDJWTVerifier

verifier = SDJWTVerifier(trusted_issuers=["did:web:api.anthropic.com"])

# Verify with selective disclosure
result = verifier.verify_sd_jwt(
    sd_jwt_data=sd_jwt,
    disclosed_claims=["temperature"]  # Only disclose temperature
)

if result["valid"]:
    print(f"Temperature: {result['claims']['temperature']}")
    # max_tokens is NOT disclosed
```

## 2. Predicate Disclosure

### What are Predicates?

Predicate disclosure allows proving **relationships** without revealing exact values:
- "temperature ≤ 0.3" without revealing temperature = 0.25
- "age ≥ 18" without revealing age = 25
- "score in range [80, 100]" without revealing score = 95

This is the **key privacy feature** for enterprise IP protection.

### When to Use Predicates

✅ **Use predicates when:**
- Need to prove compliance with thresholds
- Want to hide exact parameter values
- Require IP protection while proving policy adherence
- Need verifiable compliance without value disclosure

### Creating Predicate Proofs

```python
from genesisgraph.credentials.predicates import create_predicate

# Prove temperature <= 0.3 without revealing exact value
proof = create_predicate(
    claim_name="temperature",
    actual_value=0.25,           # Actual value (hidden)
    predicate_type="lte",         # Less than or equal
    threshold=0.3,                # Public threshold
    disclose_value=False          # Don't reveal 0.25
)

print(proof.satisfied)  # True - predicate is satisfied
print(proof.disclosed_value)  # None - value is hidden
print(proof.commitment)  # Cryptographic commitment to actual value
```

### Supported Predicate Types

```python
PredicateType.LESS_THAN           # <
PredicateType.LESS_THAN_OR_EQUAL  # <=
PredicateType.GREATER_THAN        # >
PredicateType.GREATER_THAN_OR_EQUAL  # >=
PredicateType.EQUAL               # ==
PredicateType.NOT_EQUAL           # !=
PredicateType.IN_RANGE            # value in [min, max]
PredicateType.IN_SET              # value in {set}
```

### Using Predicates in GenesisGraph

```yaml
attestation:
  mode: predicate
  timestamp: "2025-01-20T12:00:00Z"
  predicate_proofs:
    - claim_name: temperature
      predicate: lte
      threshold: 0.3
      satisfied: true
      commitment: sha256:commitment_hash
      disclosed: false
      # value: null  (hidden)

    - claim_name: prompt_length
      predicate: lte
      threshold: 100000
      satisfied: true
      commitment: sha256:another_hash
      disclosed: false
```

### Batch Creating Predicates

```python
from genesisgraph.credentials.predicates import batch_create_predicates

claims = {
    "temperature": 0.25,
    "max_tokens": 4096,
    "top_p": 0.9
}

predicates = {
    "temperature": {"type": "lte", "threshold": 0.3},
    "max_tokens": {"type": "lte", "threshold": 8192},
    "top_p": {"type": "in_range", "threshold": [0.0, 1.0]}
}

proofs = batch_create_predicates(claims, predicates)
# All proofs created in one call
```

## 3. BBS+ Signatures

### What is BBS+?

BBS+ (Boneh-Boyen-Shacham) signatures enable:
- **Unlinkable presentations**: Each verification is unlinkable to others
- **Selective disclosure**: Choose which attributes to reveal per presentation
- **Zero-knowledge proofs**: Cryptographic proofs without revealing signature

### When to Use BBS+

✅ **Use BBS+ when:**
- Anti-correlation is critical
- Need to prevent tracking across verifiers
- Privacy regulations require unlinkability
- Multiple presentations from same credential expected

❌ **Don't use BBS+ when:**
- Linkability is acceptable
- Working with standard JWT infrastructure
- Rapid deployment needed (SD-JWT is simpler)

### Creating BBS+ Credentials

```python
from genesisgraph.credentials.bbs_plus import BBSPlusIssuer, BBSPlusVerifier

# Issue credential
issuer = BBSPlusIssuer(issuer_did="did:web:api.anthropic.com")

attributes = {
    "model": "claude-sonnet-4.5",
    "temperature": 0.25,
    "max_tokens": 4096,
    "prompt_hash": "sha256:secret"
}

credential = issuer.issue_credential(attributes)
```

### Creating Unlinkable Presentations

```python
verifier = BBSPlusVerifier()

# Presentation 1: For public verifier (minimal disclosure)
presentation1 = verifier.create_presentation(
    credential=credential,
    disclosed_attributes=["model"]
)

# Presentation 2: For auditor (more disclosure)
presentation2 = verifier.create_presentation(
    credential=credential,
    disclosed_attributes=["model", "temperature", "max_tokens"]
)

# Presentation 3: For regulator
presentation3 = verifier.create_presentation(
    credential=credential,
    disclosed_attributes=["model"]
)

# presentation1 and presentation3 are UNLINKABLE even though
# they disclose the same attributes!
```

### Using BBS+ in GenesisGraph

```yaml
attestation:
  mode: bbs-plus
  timestamp: "2025-01-20T12:00:00Z"
  bbs_plus:
    issuer: did:web:api.anthropic.com
    proof:
      proof: "hex_encoded_zero_knowledge_proof"
      revealed_messages:
        "0": "claude-sonnet-4.5"  # Index 0 disclosed
        # Indices 1, 2, 3 not disclosed
      disclosed_indices: [0]
      public_key: "hex_public_key"
      nonce: "random_nonce"
    attribute_order:
      - model           # Index 0
      - temperature     # Index 1
      - max_tokens      # Index 2
      - prompt_hash     # Index 3
```

## Comparison: SD-JWT vs BBS+ vs Predicates

| Feature | SD-JWT | Predicates | BBS+ |
|---------|--------|-----------|------|
| **Selective Disclosure** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Unlinkable** | ❌ No | ❌ No | ✅ **Yes** |
| **Range Proofs** | ❌ No | ✅ **Yes** | ❌ No |
| **Standard** | IETF RFC | Custom | IETF/W3C Draft |
| **Maturity** | High | Medium | Medium |
| **Complexity** | Low | Low | High |
| **Use Case** | Auth tokens | Compliance | Privacy-critical |

### Decision Guide

**Choose SD-JWT if:**
- You need OAuth/OIDC compatibility
- Standard JWT infrastructure is required
- Linkability is acceptable

**Choose Predicates if:**
- You need to prove "temperature ≤ 0.3" without revealing 0.25
- IP protection is critical
- Compliance verification required

**Choose BBS+ if:**
- Anti-correlation is required
- Preventing tracking is critical
- Multiple verifications expected

**Combine them!**
- SD-JWT + Predicates: Standard tokens with range proofs
- BBS+ + Predicates: Unlinkable presentations with range proofs

## Use Case: Enterprise AI Compliance

### Scenario

**Problem**: Company uses AI with proprietary parameters. Must prove compliance to regulator without revealing trade secrets.

**Requirements**:
1. Prove temperature ≤ 0.3 (regulation)
2. Don't reveal exact temperature value (IP protection)
3. Multiple verifications by different auditors (anti-correlation)
4. Verifiable audit trail (transparency logs)

### Solution

```python
from genesisgraph.credentials.bbs_plus import BBSPlusIssuer, BBSPlusVerifier
from genesisgraph.credentials.predicates import create_predicate

# Step 1: Issue BBS+ credential
issuer = BBSPlusIssuer(issuer_did="did:web:company.com")
attributes = {
    "model": "claude-sonnet-4.5",
    "temperature": 0.25,
    "max_tokens": 4096
}
credential = issuer.issue_credential(attributes)

# Step 2: Create predicate proofs
temp_proof = create_predicate(
    "temperature", 0.25, "lte", 0.3, disclose_value=False
)

# Step 3: Create unlinkable presentation for Auditor 1
verifier = BBSPlusVerifier()
presentation1 = verifier.create_presentation(
    credential, disclosed_attributes=["model"]
)

# Step 4: Create different unlinkable presentation for Auditor 2
presentation2 = verifier.create_presentation(
    credential, disclosed_attributes=["model"]
)

# presentation1 and presentation2 are unlinkable!
# But both prove same underlying credential
```

### Benefits

✅ **IP Protected**: Exact temperature value never revealed
✅ **Compliance Proven**: Predicate proves temperature ≤ 0.3
✅ **Anti-Correlation**: Auditors cannot link their verifications
✅ **Transparency**: All verifications logged immutably

## Integration with GenesisGraph

All three methods integrate seamlessly with GenesisGraph's attestation system:

```yaml
# Level A: Full disclosure
attestation:
  mode: signed
  signature: ed25519:...
  parameters: {...}  # All visible

# Level B: SD-JWT selective disclosure
attestation:
  mode: sd-jwt
  sd_jwt: {...}  # Some claims hidden

# Level C: Predicate disclosure
attestation:
  mode: predicate
  predicate_proofs: [...]  # Prove thresholds, hide values

# Level D: BBS+ unlinkable disclosure
attestation:
  mode: bbs-plus
  bbs_plus: {...}  # Unlinkable presentations
```

## Security Considerations

### SD-JWT

- ✅ Cryptographically secure hash commitments
- ✅ Prevents tampering with disclosed claims
- ⚠️ Signatures are linkable (can track across verifications)
- ⚠️ Requires trusted time for expiry checks

### Predicates

- ✅ Commitment-based value hiding
- ✅ Verifiable satisfaction without value disclosure
- ⚠️ Not true zero-knowledge (simplified implementation)
- ⚠️ For production ZK range proofs, use Bulletproofs/zkSNARKs

### BBS+

- ✅ True unlinkability via zero-knowledge proofs
- ✅ Prevents correlation attacks
- ✅ Minimal disclosure principle
- ⚠️ More complex cryptography (BLS12-381 curves)
- ⚠️ Requires careful nonce management

## Performance

| Method | Signing | Verification | Proof Size |
|--------|---------|-------------|-----------|
| SD-JWT | Fast | Fast | Medium |
| Predicates | Fast | Fast | Small |
| BBS+ | Medium | Medium | Large |

## References

- **SD-JWT**: [IETF draft-ietf-oauth-selective-disclosure-jwt](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-selective-disclosure-jwt)
- **BBS+ Signatures**: [IETF draft-irtf-cfrg-bbs-signatures](https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-bbs-signatures)
- **W3C DI-BBS**: [Data Integrity BBS Cryptosuites](https://w3c.github.io/vc-di-bbs/)
- **GenesisGraph Schema**: `schema/genesisgraph-core-v0.1.yaml`

## Examples

See `examples/` directory:
- `sd-jwt-attestation.gg.yaml` - SD-JWT selective disclosure
- `predicate-attestation.gg.yaml` - Range proofs for compliance
- `bbs-plus-attestation.gg.yaml` - Unlinkable presentations

## Support

For issues or questions:
- GitHub Issues: https://github.com/genesisgraph/genesisgraph/issues
- Documentation: https://genesisgraph.dev
- Specification: [IETF SD-JWT](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-selective-disclosure-jwt)
