# GenesisGraph: Threat Model & Security Posture

**Version:** 1.0
**Status:** Production
**Last Updated:** 2025-11-20

---

## Executive Summary

GenesisGraph is a **provenance standard** for verifiable process tracking across AI, manufacturing, research, and supply chains. This document defines:

1. **Who we protect against** (adversary model)
2. **What we protect** (security goals)
3. **How we protect it** (mechanisms)
4. **What we don't protect** (non-goals)
5. **Security levels** (GG-SEC-1 through GG-SEC-4)

**Key Insight:** GenesisGraph is NOT a security tool itself—it's a **verifiable audit trail format**. Security comes from cryptographic primitives (signatures, hashes, transparency logs, TEEs) that users compose.

---

## Table of Contents

1. [Security Goals](#security-goals)
2. [Adversary Model](#adversary-model)
3. [Attack-Defense Matrix](#attack-defense-matrix)
4. [Security Levels (GG-SEC)](#security-levels-gg-sec)
5. [Trust Assumptions](#trust-assumptions)
6. [Failure Modes & Mitigations](#failure-modes--mitigations)
7. [Out of Scope](#out-of-scope)
8. [Security Review History](#security-review-history)

---

## Security Goals

GenesisGraph provides the following security guarantees when properly implemented:

### 1. **Integrity** (Primary Goal)
- **Definition:** Provenance graphs cannot be modified without detection
- **Mechanism:** Cryptographic hashes (SHA-256), digital signatures (Ed25519)
- **Guarantee:** Any tampering with entities, operations, or attestations breaks hash chains or signature verification

### 2. **Non-Repudiation** (Primary Goal)
- **Definition:** Signers cannot deny creating attestations
- **Mechanism:** Digital signatures with DID-based identity, optional transparency log anchoring
- **Guarantee:** Signed attestations are cryptographically bound to signer's identity

### 3. **Auditability** (Primary Goal)
- **Definition:** Process history is verifiable by third parties
- **Mechanism:** Complete DAG of inputs → operations → outputs, with timestamps and version tracking
- **Guarantee:** Auditors can reconstruct and verify the entire provenance chain

### 4. **Privacy** (Secondary Goal)
- **Definition:** Sensitive details can be hidden while maintaining verifiability
- **Mechanism:** Selective disclosure (Levels A/B/C), sealed subgraphs with Merkle commitments, SD-JWT, BBS+
- **Guarantee:** Trade secrets can be protected while still proving policy compliance

### 5. **Temporal Ordering** (Secondary Goal)
- **Definition:** Establish relative ordering of operations
- **Mechanism:** Timestamps, transparency log tree positions
- **Guarantee:** Can prove operation O1 happened before O2 (if both anchored in same log)

### 6. **Accountability** (Tertiary Goal)
- **Definition:** Identify responsible parties for each operation
- **Mechanism:** DID-based attribution, delegation chains, multisig attestations
- **Guarantee:** Can trace decision authority back through delegation hierarchy

---

## Adversary Model

### Adversary Capabilities

We consider adversaries with the following capabilities:

| Capability | Description | Threat Level |
|------------|-------------|--------------|
| **Computational** | Standard computing power (no quantum) | Moderate |
| **Network** | Can intercept, delay, or drop network traffic | High |
| **Insider** | May have valid credentials, limited system access | High |
| **Cryptographic** | Can attempt brute force, collision attacks on weak hashes | Moderate |
| **Social Engineering** | Can trick users into signing malicious content | High |
| **Supply Chain** | Can compromise tool vendors, libraries | Very High |
| **Nation-State** | Unlimited budget, targeted attacks, zero-days | Very High (out-of-scope for most deployments) |

### Adversary Classes

#### 1. **Malicious Tool Vendors** 🔴 HIGH THREAT

**Attack Vector:**
- Tool claims to perform operation O but actually does operation O'
- Tool falsifies parameter values in generated provenance
- Tool omits inputs/outputs from provenance graph

**Example:**
```yaml
# Tool claims:
operations:
  - id: op_inference
    tool: llama3-70b@3.0
    parameters:
      temperature: 0.2  # Claimed
    # Reality: Actually used temperature=1.5

# Tool omits:
# - Hidden network call to log prompts externally
# - Undeclared input from proprietary fine-tuning data
```

**Defenses:**
- TEE attestation quotes (tool runs in trusted execution environment)
- Reproducible execution verification (re-run and compare outputs)
- Execution trace hashing (hash of actual runtime logs)
- Tool reputation scoring (registry tracks vendor dispute history)

**Residual Risk:** **Medium** - TEE/reproducibility helps but requires infrastructure

---

#### 2. **Supply Chain Attackers** 🔴 HIGH THREAT

**Attack Vector:**
- Inject fake entities into provenance graph (dataset poisoning)
- Substitute high-quality entity with low-quality version (same hash, different content via collision)
- Compromise entity registry to map hashes to wrong content

**Example:**
```yaml
entities:
  - id: medical_corpus
    version: 2025-10-15
    hash: sha256:abc123...  # Attacker found collision
    # Points to poisoned dataset instead of legitimate one
```

**Defenses:**
- Strong hash functions (SHA-256, SHA-3, BLAKE3 - collision-resistant)
- Entity registry with transparency log (all entries append-only, auditable)
- Content addressing with IPFS/CID (hash → content is verifiable)
- Provenance of entities (datasets have their own `.gg.yaml` files)

**Residual Risk:** **Low** - SHA-256 collision resistance + transparency logs are strong

---

#### 3. **Nation-State Adversaries** 🔴 VERY HIGH THREAT (Limited Scope)

**Attack Vector:**
- Compromise DID registries (control identity infrastructure)
- Compromise transparency log operators (rewrite history)
- Exploit cryptographic weaknesses (quantum attacks, zero-days)
- Legal compulsion (force signing of false attestations)

**Example:**
- Nation-state compromises `did:web` resolver, returns attacker's public key
- Transparency log operator colluded to provide fake inclusion proofs

**Defenses:**
- Multi-party witness networks (requires compromising ≥ 2/3 of independent operators)
- DID method diversity (use `did:key`, `did:ion`, `did:ethr` - not just `did:web`)
- Cryptographic agility (support post-quantum algorithms when standardized)
- Decentralized transparency logs (no single point of control)

**Residual Risk:** **High** - Nation-state adversaries with sustained effort can succeed
**Mitigation Strategy:** Use **Security Level GG-SEC-4** for high-stakes scenarios

---

#### 4. **AI Agents (Deceptive Provenance)** 🟡 MEDIUM THREAT

**Attack Vector:**
- AI agent generates syntactically valid but semantically deceptive provenance
- Agent claims to have used tool X but actually used tool Y
- Agent omits reasoning steps to hide unsafe decision-making

**Example:**
```yaml
# Agent claims:
operations:
  - id: op_reasoning
    agent: assistant_alpha
    reasoning:
      steps:
        - "Analyzed user request for medical advice"
        - "Consulted trusted medical database"
        - "Verified against FDA guidelines"

# Reality:
# - Agent hallucinated medical facts
# - Never consulted database
# - No FDA verification occurred
```

**Defenses:**
- Mandatory execution trace hashing (must include actual tool calls)
- Policy evaluation with independent verifiers (OPA, Cedar policy engines)
- Human-in-the-loop attestations (require human approval for high-stakes decisions)
- Agent capability constraints (delegation chains limit what agents can do)

**Residual Risk:** **Medium** - Requires trusted execution infrastructure
**See:** Agent Provenance Extension (Gap #9) for full mitigation strategy

---

#### 5. **Colluding Signers (Multisig Fraud)** 🟡 MEDIUM THREAT

**Attack Vector:**
- Multiple parties collude to sign false attestations
- Threshold signature bypassed (e.g., 2-of-3 multisig with 2 compromised keys)

**Example:**
```yaml
attestation:
  multisig:
    threshold: 2
    signers:
      - did:person:engineer  # Compromised
      - did:person:qa        # Compromised
      - did:person:manager   # Honest, but outvoted
  # Result: False attestation passes verification
```

**Defenses:**
- **High thresholds** (use 3-of-5 or 4-of-7 for critical operations)
- **Role diversity** (require different organizational roles)
- **Time separation** (signatures must be at least N hours apart)
- **Independent verification** (third-party auditor must also sign)
- **Reputation weighting** (signers with high reputation required)

**Residual Risk:** **Low-Medium** - High thresholds + role diversity make collusion difficult

---

#### 6. **Temporal Attackers (Log Wrapping, Timestamp Spoofing)** 🟡 MEDIUM THREAT

**Attack Vector:**
- Create provenance with backdated timestamps
- Use old transparency log tree state to hide subsequent revocations
- "Log wrapping" - present old inclusion proof as current

**Example:**
```yaml
attestation:
  timestamp: 2025-10-01T10:00:00Z  # Backdated by 1 month
  transparency:
    - log_id: did:log:internal
      tree_size: 10000  # Old tree state
      # Attacker hides that tool was revoked at tree_size: 15000
```

**Defenses:**
- **Trusted timestamping** (RFC 3161 timestamp authorities)
- **Consistency proofs** (verify log hasn't been tampered with since inclusion)
- **Freshness requirements** (verifier requires recent tree_size)
- **Multi-log witnessing** (cross-reference timestamps across independent logs)

**Residual Risk:** **Low** - Consistency proofs + multi-log witnessing are strong

---

#### 7. **Replay Attackers (Reusing Old Provenance)** 🟢 LOW THREAT

**Attack Vector:**
- Reuse valid provenance bundle from 2024 in 2025
- Claim current compliance using expired credentials

**Example:**
```yaml
# Provenance created 2024-06-15
operations:
  - id: op_manufacturing
    tool: freecad@0.21.2  # Had CVE discovered 2024-12-01
    # Attacker reuses this provenance in 2025 claiming "still valid"
```

**Defenses:**
- **Lifecycle metadata** (entities/tools have `valid_until` timestamps)
- **Revocation checking** (verifier must check revocation lists)
- **Temporal validation** (verify provenance is fresh, not stale)
- **Nonce inclusion** (operations include unique identifiers)

**Residual Risk:** **Very Low** - Lifecycle framework prevents this

---

## Attack-Defense Matrix

| Attack Vector | Current Defense | Strength | Future Improvement |
|--------------|----------------|----------|-------------------|
| **Parameter Falsification** | Signatures, hashes | ⭐⭐⭐ | Add execution traces |
| **Input Omission** | DAG validation | ⭐⭐ | Add input closure proofs |
| **Tool Substitution** | Tool versioning | ⭐⭐⭐ | Add TEE attestations |
| **Entity Poisoning** | SHA-256 hashing | ⭐⭐⭐⭐ | Add content addressing |
| **Timestamp Spoofing** | Transparency logs | ⭐⭐⭐⭐ | Add trusted timestamps |
| **DID Registry Compromise** | Multi-method DIDs | ⭐⭐⭐ | Add DID diversity requirements |
| **Transparency Log Tampering** | Merkle proofs | ⭐⭐⭐⭐ | Add multi-log witnessing |
| **Multisig Collusion** | Threshold signatures | ⭐⭐⭐ | Add role diversity |
| **Replay Attacks** | Lifecycle metadata | ⭐⭐⭐⭐ | Add nonce requirements |
| **Agent Deception** | Schema validation | ⭐ | Add execution trace hashing |

**Legend:**
⭐ = Weak / ⭐⭐ = Moderate / ⭐⭐⭐ = Strong / ⭐⭐⭐⭐ = Very Strong

---

## Security Levels (GG-SEC)

GenesisGraph defines **four security levels** for different risk profiles:

### **GG-SEC-1: Basic** (Low Assurance)

**Guarantees:**
- Hash integrity (SHA-256)
- Timestamp ordering (ISO 8601)
- Schema validation

**NOT Guaranteed:**
- Signature authenticity (could be self-signed or missing)
- Non-repudiation
- Freshness

**Use Cases:**
- Internal development workflows
- Low-stakes experimentation
- Educational examples

**Example:**
```yaml
spec_version: 0.4.0
security_level: GG-SEC-1

entities:
  - id: data
    hash: sha256:abc123...

attestation:
  mode: basic
  timestamp: 2025-11-20T10:00:00Z
```

---

### **GG-SEC-2: Signed** (Medium Assurance)

**Guarantees:**
- All GG-SEC-1 guarantees
- Digital signatures (Ed25519)
- DID-based identity
- Non-repudiation

**NOT Guaranteed:**
- Temporal ordering (no transparency logs)
- Revocation checking
- Multisig consensus

**Use Cases:**
- Customer deliverables with attribution
- Internal audit trails
- Research reproducibility

**Example:**
```yaml
spec_version: 0.4.0
security_level: GG-SEC-2

attestation:
  mode: signed
  signer: did:web:example.com
  signature: ed25519:abc123...
  timestamp: 2025-11-20T10:00:00Z
```

---

### **GG-SEC-3: Verifiable** (High Assurance)

**Guarantees:**
- All GG-SEC-2 guarantees
- Transparency log anchoring (RFC 6962)
- Inclusion/consistency proofs
- Multi-log witnessing (≥2 independent logs)
- Revocation checking

**NOT Guaranteed:**
- Trusted execution (no TEE quotes)
- Quantum resistance

**Use Cases:**
- Regulatory compliance (FDA, ISO, AS9100D)
- Supply chain provenance
- Cross-organizational verification
- AI safety audits

**Example:**
```yaml
spec_version: 0.4.0
security_level: GG-SEC-3

attestation:
  mode: verifiable
  signer: did:web:example.com
  signature: ed25519:abc123...
  transparency:
    - log_id: did:log:rekor
      entry_id: 0x5f2c8a91
      tree_size: 428934
      inclusion_proof: base64:...
    - log_id: did:log:compliance
      entry_id: 0x7a3d9c12
      tree_size: 892471
      inclusion_proof: base64:...
  multisig:
    threshold: 2
    signers: [did:person:engineer, did:person:qa, did:person:manager]
```

---

### **GG-SEC-4: Maximum** (Very High Assurance)

**Guarantees:**
- All GG-SEC-3 guarantees
- TEE attestation quotes (Intel SGX, AMD SEV, AWS Nitro)
- Zero-knowledge proofs of policy compliance
- Byzantine fault tolerance (≥3f+1 witnesses)
- Post-quantum cryptography (when available)

**Use Cases:**
- National security applications
- Critical infrastructure
- High-value IP protection
- Multi-party computation provenance

**Example:**
```yaml
spec_version: 0.4.0
security_level: GG-SEC-4

attestation:
  mode: verifiable
  signer: did:web:example.com
  signature: ed25519:abc123...
  tee:
    technology: intel_sgx
    quote: base64:...
    enclave_measurement: sha256:def456...
  transparency:
    - log_id: did:log:rekor
      # ... (2+ logs)
  multisig:
    threshold: 3
    signers: [did:person:engineer, did:person:qa, did:person:manager, did:person:auditor]
  zk_proof:
    type: policy_compliance
    proof: base64:...
    public_inputs:
      policy_id: iso-9001-2015
      result: pass
```

---

## Trust Assumptions

GenesisGraph security depends on the following trust assumptions:

### 1. **Cryptographic Primitives**
- **Assumption:** SHA-256 is collision-resistant, Ed25519 is unforgeable
- **Validity:** True under current cryptanalysis (2025)
- **Mitigation:** Cryptographic agility (support SHA-3, BLAKE3, post-quantum signatures)

### 2. **DID Resolution**
- **Assumption:** DID resolvers return correct public keys
- **Validity:** Depends on DID method (`did:key` is self-verifying, `did:web` requires DNS/TLS trust)
- **Mitigation:** Use diverse DID methods, prefer `did:key` or `did:ion` for high security

### 3. **Transparency Log Operators**
- **Assumption:** ≥1 of N log operators is honest (for single-log), ≥2/3 honest (for multi-log)
- **Validity:** True if operators are independent (different jurisdictions, organizations)
- **Mitigation:** Multi-log witnessing, consistency proof validation

### 4. **TEE Hardware**
- **Assumption:** Intel SGX/AMD SEV/AWS Nitro enclaves are secure
- **Validity:** True for side-channel-resistant code, false if vulnerable to Spectre/Meltdown variants
- **Mitigation:** Use latest TEE versions, apply patches, combine with other mechanisms

### 5. **Human Judgment**
- **Assumption:** Human reviewers act honestly and competently
- **Validity:** Depends on incentives, training, oversight
- **Mitigation:** Multi-party review, role separation, reputation tracking

### 6. **Tool Vendors**
- **Assumption:** Tools generate honest provenance (or run in TEEs)
- **Validity:** False for adversarial vendors
- **Mitigation:** Tool reputation scoring, reproducible execution, execution traces

---

## Failure Modes & Mitigations

### Failure Mode 1: **Private Key Compromise**

**Scenario:** Attacker steals private key used for signing attestations

**Impact:**
- Can create false attestations signed with legitimate identity
- Can impersonate entity/organization

**Mitigations:**
1. **Key Rotation:** Rotate signing keys every 90 days
2. **Revocation Lists:** Publish compromised keys to revocation registry
3. **Hardware Security Modules (HSMs):** Store keys in tamper-resistant hardware
4. **Multisig:** Require multiple signatures (compromise of 1 key insufficient)
5. **Transparency Logs:** All attestations logged (compromise detectable via audit)

**Residual Risk:** Low if multisig + HSMs used

---

### Failure Mode 2: **Transparency Log Compromise**

**Scenario:** Transparency log operator tampers with tree (adds/removes entries)

**Impact:**
- False inclusion proofs
- History rewriting

**Mitigations:**
1. **Multi-Log Witnessing:** Anchor in ≥2 independent logs (both must be compromised)
2. **Consistency Proofs:** Verifiers check tree hasn't forked
3. **Gossip Protocols:** Monitors cross-check tree heads
4. **Public Audit:** Logs are append-only and auditable by anyone

**Residual Risk:** Very Low if ≥2 independent logs used

---

### Failure Mode 3: **TEE Vulnerabilities**

**Scenario:** New side-channel attack (e.g., Spectre variant) bypasses TEE isolation

**Impact:**
- Attacker extracts secrets from enclave
- TEE attestation quotes no longer trustworthy

**Mitigations:**
1. **Defense in Depth:** Don't rely solely on TEEs (combine with multisig, transparency logs)
2. **Patching:** Apply firmware updates promptly
3. **Diverse TEE Technologies:** Use multiple TEE types (SGX + SEV + Nitro)
4. **Remote Attestation:** Verify enclave measurements match expected values

**Residual Risk:** Medium (side-channels are ongoing research area)

---

### Failure Mode 4: **Schema Downgrade Attack**

**Scenario:** Attacker modifies `spec_version` to use older, less secure schema

**Impact:**
- Bypass new security requirements
- Use deprecated/vulnerable features

**Mitigations:**
1. **Minimum Version Enforcement:** Verifiers reject documents below minimum version
2. **Deprecation Warnings:** Clear timeline for sunsetting old versions
3. **Schema Hashing:** Include schema hash in document (prevents substitution)

**Residual Risk:** Very Low if validators enforce minimum versions

---

### Failure Mode 5: **Social Engineering (Tricked Signing)**

**Scenario:** Attacker tricks user into signing malicious provenance

**Impact:**
- Legitimate signature on false claims

**Mitigations:**
1. **Preview Before Signing:** Show human-readable summary of what will be signed
2. **Multi-Party Review:** Require independent reviewers
3. **Attestation Templates:** Use pre-approved templates (reduce ad-hoc signing)
4. **Rate Limiting:** Limit signing frequency (prevents bulk signing)

**Residual Risk:** Medium (social engineering always a risk)

---

## Out of Scope

GenesisGraph **does NOT protect against:**

### 1. **Compromise of Underlying Systems**
- If the operating system is compromised, provenance generation cannot be trusted
- **Mitigation:** Use secure boot, attestation, trusted computing base reduction

### 2. **Confidentiality of Disclosed Information**
- GenesisGraph focuses on **integrity** and **selective disclosure**, not encryption
- Level A/B disclosure reveals certain information intentionally
- **Mitigation:** Use Level C (sealed subgraphs) or encrypt provenance documents

### 3. **Denial of Service (DoS)**
- Attackers can flood transparency logs, registries, or verifiers
- **Mitigation:** Rate limiting, proof-of-work, economic costs

### 4. **Quantum Attacks**
- Current cryptography (SHA-256, Ed25519) vulnerable to quantum computers
- **Mitigation:** Cryptographic agility, post-quantum algorithms when standardized

### 5. **Legal Compulsion**
- Governments can force signing of false attestations
- **Mitigation:** Multi-jurisdiction witnessing, transparency logs (makes compulsion visible)

### 6. **Physical Access Attacks**
- Attacker with physical access can compromise hardware
- **Mitigation:** Tamper-evident seals, HSMs, secure facilities

---

## Security Review History

| Date | Reviewer | Scope | Findings |
|------|----------|-------|----------|
| 2025-11-20 | Internal | Threat model v1.0 | Initial security posture defined |
| TBD | External | Cryptographic review | Pending |
| TBD | External | Schema security audit | Pending |

**Next Review:** Recommended before v1.0 release (external security audit)

---

## Security Contact

**Report security vulnerabilities to:**
- **Email:** security@genesisgraph.dev
- **PGP Key:** [See SECURITY.md](../SECURITY.md)
- **Response Time:** 48 hours for critical issues

**Public Disclosure Timeline:**
- Day 0: Receive report
- Day 1-7: Assess severity, develop fix
- Day 7-30: Deploy patches, notify affected parties
- Day 90: Public disclosure (CVE assignment if applicable)

---

## References

1. **RFC 6962:** Certificate Transparency (transparency log design)
2. **SLSA:** Supply-chain Levels for Software Artifacts (security level inspiration)
3. **STRIDE:** Microsoft threat modeling framework
4. **W3C DID Core:** Decentralized Identifier specification
5. **NIST 800-63:** Digital Identity Guidelines

---

**Document Status:** Production
**Intended Audience:** Security teams, auditors, compliance officers, integrators
**License:** CC-BY 4.0

---

**Version History:**
- 1.0 (2025-11-20): Initial threat model and security posture definition
