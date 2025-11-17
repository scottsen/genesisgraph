# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

**Note:** GenesisGraph is currently in **alpha** (v0.1.x). While we take security seriously, the API and security guarantees may change before the 1.0 release.

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in GenesisGraph, please report it by emailing:

**security@genesisgraph.dev** (or create a private security advisory on GitHub)

Please include:
- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any suggested fixes (optional)

### What to expect:
- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 5 business days
- **Fix timeline:** Depends on severity
  - Critical: 7-14 days
  - High: 14-30 days
  - Medium: 30-60 days
  - Low: Next scheduled release

We will keep you informed throughout the process and credit you in the security advisory (unless you prefer to remain anonymous).

## Security Considerations

### Trust Model

GenesisGraph provides **verifiable provenance**, not **trusted execution**. Understanding this distinction is critical:

#### What GenesisGraph Provides
- **Cryptographic proof** that a document matches its declared structure
- **Integrity verification** through hash chains and signatures
- **Attestation validation** that signatures match declared signers
- **Format compliance** checking against schema definitions

#### What GenesisGraph Does NOT Provide
- **Trusted execution environment** - We verify signatures, not that operations executed correctly
- **Signer identity verification** - We validate signatures, but don't verify the signer's real-world identity (beyond DID resolution)
- **Content authenticity** - We verify hashes match, not that content is truthful or accurate
- **Replay protection** - Documents can be re-submitted unless you implement timestamp checking

### Disclosure Levels and Security

GenesisGraph supports three disclosure levels, each with different security characteristics:

#### Level A: Full Disclosure
**Security Profile:** Maximum transparency, minimum privacy

- ✅ **Strengths:**
  - Complete auditability
  - Independent verification possible
  - Full reproducibility

- ⚠️ **Risks:**
  - Trade secrets exposed
  - Privacy-sensitive data visible
  - Competitive intelligence leakage

**Use when:** Internal audits, academic research, open-source projects

#### Level B: Partial Envelope (Redacted Parameters)
**Security Profile:** Balanced transparency and privacy

- ✅ **Strengths:**
  - Policy compliance provable without parameter disclosure
  - Reduced IP exposure
  - Regulatory compliance possible

- ⚠️ **Risks:**
  - Claims unverifiable without trusted issuer
  - Parameter manipulation harder to detect
  - Requires trust in redacting party

**Use when:** Regulatory compliance, limited IP exposure acceptable

#### Level C: Sealed Subgraph
**Security Profile:** Maximum privacy, cryptographic commitments

- ✅ **Strengths:**
  - Complete IP protection
  - Merkle commitments provide integrity
  - Zero-knowledge proofs possible

- ⚠️ **Risks:**
  - No independent verification of sealed content
  - Requires strong trust in TEE/multisig attestations
  - Sealed content could contain anything

**Use when:** High-value IP, supply chain security, multi-party trust required

### Cryptographic Assumptions

GenesisGraph's security relies on the following cryptographic assumptions:

#### Hash Functions
- **SHA-256:** Collision resistance assumed (NIST FIPS 180-4)
- **SHA-512:** Collision resistance assumed (NIST FIPS 180-4)
- **Blake3:** Fast, parallel-friendly (used when performance matters)

**Risk:** Collision attacks could allow hash substitution. We consider SHA-256 secure through 2030+ based on current research.

#### Digital Signatures
- **Ed25519:** Default signature algorithm (RFC 8032)
  - 128-bit security level
  - Deterministic signatures (no RNG vulnerabilities)
  - Fast verification

**Risk:** Private key compromise allows signature forgery. Use hardware key storage (HSM, YubiKey) for high-value signatures.

#### DID Resolution
- **did:key** - Self-describing keys (no resolution needed)
- **did:web** - Web-based DIDs (depends on HTTPS security)

**Risk:** DID resolution attacks (MITM, DNS hijacking) could substitute public keys. Always verify DIDs through multiple channels for high-stakes verification.

### Threat Model

#### In-Scope Threats (GenesisGraph Protects Against)

1. **Document Tampering**
   - **Threat:** Attacker modifies provenance document after signing
   - **Protection:** Hash chains, digital signatures
   - **Validation:** `gg validate` detects modifications

2. **Hash Substitution**
   - **Threat:** Attacker replaces entity hash with different file
   - **Protection:** Cryptographic hash verification
   - **Validation:** File hash verification in validator

3. **Signature Forgery**
   - **Threat:** Attacker creates fake signatures
   - **Protection:** Ed25519 signature verification
   - **Validation:** Cryptographic signature checking (when `verify_signatures=True`)

4. **Schema Violations**
   - **Threat:** Malformed documents bypass validation
   - **Protection:** JSON Schema enforcement
   - **Validation:** Schema validation in validator

#### Out-of-Scope Threats (GenesisGraph Does NOT Protect Against)

1. **Sybil Attacks / Identity Spoofing**
   - **Threat:** Attacker creates fake DID claiming to be trusted party
   - **Mitigation:** External identity verification (PKI, web-of-trust)
   - **Status:** Not implemented (planned for v0.2+)

2. **Private Key Compromise**
   - **Threat:** Attacker steals signer's private key
   - **Mitigation:** Hardware key storage, key rotation
   - **Status:** User responsibility

3. **Timestamp Manipulation**
   - **Threat:** Attacker backdates or future-dates signatures
   - **Mitigation:** Transparency logs, trusted timestamping (RFC 3161)
   - **Status:** Partially implemented (transparency log support in schema, not yet verified)

4. **Replay Attacks**
   - **Threat:** Attacker re-submits old valid provenance
   - **Mitigation:** Timestamp checking, nonce-based freshness
   - **Status:** Not implemented (application-level responsibility)

5. **Side-Channel Attacks**
   - **Threat:** Timing attacks, power analysis on signature verification
   - **Mitigation:** Constant-time crypto implementations
   - **Status:** Relies on `cryptography` library (uses BoringSSL/OpenSSL constant-time primitives)

6. **Supply Chain Attacks on Dependencies**
   - **Threat:** Compromised `cryptography`, `pyyaml`, `jsonschema` packages
   - **Mitigation:** Dependency pinning, SBOMs, reproducible builds
   - **Status:** Partial (version pinning in pyproject.toml, no SBOM yet)

## Best Practices

### For Users (Verifying Provenance)

1. **Always enable signature verification for critical workflows**
   ```python
   from genesisgraph import GenesisGraphValidator

   validator = GenesisGraphValidator(verify_signatures=True, use_schema=True)
   result = validator.validate_file("critical-workflow.gg.yaml")
   ```

2. **Verify file hashes match declared values**
   - Use `gg validate --strict` to enable all checks
   - Manually verify critical file hashes: `sha256sum file.stl`

3. **Check signer identities through multiple channels**
   - Don't trust DIDs blindly
   - Verify `did:web` through HTTPS + certificate pinning
   - Use established PKI for high-stakes verification

4. **Implement timestamp checking for replay protection**
   ```python
   from datetime import datetime, timedelta

   # Example: reject documents older than 24 hours
   if 'attestation' in operation:
       timestamp = operation['attestation'].get('timestamp')
       if timestamp:
           age = datetime.now() - datetime.fromisoformat(timestamp)
           if age > timedelta(hours=24):
               raise ValueError("Provenance too old")
   ```

5. **Use transparency logs for non-repudiation**
   - Anchor critical provenance to transparency logs
   - Verify inclusion proofs
   - Check consistency proofs for log integrity

### For Creators (Generating Provenance)

1. **Protect private keys**
   - Use hardware security modules (HSM) for production
   - Never commit private keys to version control
   - Rotate keys periodically (every 90-180 days)

2. **Use Level C (Sealed Subgraph) for trade secrets**
   ```yaml
   operations:
     - id: op_proprietary_cam
       type: sealed_subgraph
       sealed:
         merkle_root: sha256:deadbeef...
         policy_assertions:
           - id: iso-9001-2015
             result: pass
             signer: did:org:facility
   ```

3. **Always include timestamps in attestations**
   ```yaml
   attestation:
     mode: signed
     signer: did:key:z6Mk...
     signature: ed25519:Aw8F...
     timestamp: 2025-11-17T10:30:00Z  # ISO 8601
   ```

4. **Use TEE attestations for sealed subgraphs**
   - Intel SGX, AMD SEV, or ARM TrustZone
   - Include TEE quote in attestation:
   ```yaml
   attestation:
     tee:
       technology: sgx
       quote: base64encodedquote...
   ```

5. **Implement multisig for critical operations**
   ```yaml
   attestation:
     multisig:
       threshold: 2
       signers:
         - did:org:engineer
         - did:org:qa-manager
         - did:org:security-officer
   ```

### For Developers (Integrating GenesisGraph)

1. **Pin cryptographic dependencies**
   ```toml
   dependencies = [
       "cryptography>=41.0.0,<42.0.0",  # Pin major version
       "pyyaml>=6.0,<7.0",
   ]
   ```

2. **Validate schemas before use**
   ```python
   validator = GenesisGraphValidator(use_schema=True)
   result = validator.validate(data)
   if not result.is_valid:
       # Handle validation errors
   ```

3. **Use secure random for key generation**
   ```python
   from cryptography.hazmat.primitives.asymmetric import ed25519

   # GOOD: Uses OS-provided CSPRNG
   private_key = ed25519.Ed25519PrivateKey.generate()

   # BAD: Never seed from weak sources
   # import random; random.seed(12345)  # ❌ INSECURE
   ```

4. **Implement defense in depth**
   - Don't rely solely on GenesisGraph for security
   - Combine with access controls, audit logs, network security
   - Validate provenance at multiple trust boundaries

5. **Monitor for cryptographic deprecation**
   - Track NIST recommendations: https://www.nist.gov/programs-projects/post-quantum-cryptography
   - Plan migration to post-quantum signatures (CRYSTALS-Dilithium, etc.)
   - Subscribe to GenesisGraph security advisories

## Security Features

### Current Implementation (v0.1.x)

- ✅ **Ed25519 signature format validation** - Checks signature format, not yet verifying
- ✅ **SHA-256/SHA-512 hash verification** - Computes and compares file hashes
- ✅ **JSON Schema validation** - Enforces document structure
- ✅ **Attestation mode validation** - Validates basic, signed, verifiable, zk modes
- ✅ **Merkle commitment format checking** - Validates sealed subgraph structure
- ⚠️ **Cryptographic signature verification** - Partially implemented (format only, not cryptographic verification)

### Planned (v0.2.0)

- 🔄 **Full Ed25519 signature verification** - Cryptographic verification of signatures
- 🔄 **DID resolution** - `did:key` and `did:web` support
- 🔄 **Transparency log verification** - CT-style inclusion proof checking
- 🔄 **TEE quote verification** - Intel SGX, AMD SEV validation
- 🔄 **Multisig verification** - Threshold signature validation

### Future Roadmap (v0.3+)

- 📋 **Zero-knowledge proofs** - ZK-SNARK/STARK policy proofs
- 📋 **Post-quantum signatures** - CRYSTALS-Dilithium, Falcon
- 📋 **Hardware key integration** - YubiKey, HSM support
- 📋 **Timestamp authorities** - RFC 3161 trusted timestamping
- 📋 **Revocation checking** - Certificate/key revocation lists

## Known Limitations

### Current Version (v0.1.0)

1. **Signature verification incomplete**
   - Status: Format validation only, not cryptographic verification
   - Impact: Forged signatures not detected
   - Mitigation: Use external signature verification tools
   - Fix: Planned for v0.2.0 (this is being addressed in the current work)

2. **No DID resolution**
   - Status: DIDs accepted but not resolved to public keys
   - Impact: Can't verify signer identity
   - Mitigation: Manually verify DIDs out-of-band
   - Fix: Planned for v0.2.0

3. **No transparency log verification**
   - Status: Transparency log fields accepted but not verified
   - Impact: Can't verify non-repudiation claims
   - Mitigation: Use external transparency log tools
   - Fix: Planned for v0.2.0

4. **No TEE quote verification**
   - Status: TEE quotes accepted but not verified
   - Impact: Can't verify sealed subgraph execution in trusted hardware
   - Mitigation: Use vendor-provided TEE verification tools
   - Fix: Planned for v0.3.0

5. **No multisig verification**
   - Status: Multisig format accepted but not verified
   - Impact: Can't enforce threshold signature requirements
   - Mitigation: Verify signatures individually
   - Fix: Planned for v0.2.0

### By Design

1. **No identity verification**
   - GenesisGraph verifies signatures, not real-world identities
   - Use external PKI/identity systems

2. **No trusted execution**
   - GenesisGraph verifies documents, not that operations executed correctly
   - Use TEE attestations for execution guarantees

3. **No confidentiality**
   - GenesisGraph provides integrity, not encryption
   - Use TLS/encryption for data in transit, disk encryption for data at rest

## Security Advisories

We will publish security advisories through:
- GitHub Security Advisories: https://github.com/scottsen/genesisgraph/security/advisories
- Mailing list: security-announce@genesisgraph.dev (to be set up)
- CVE database: When applicable

**No security advisories have been published for GenesisGraph at this time.**

## Additional Resources

- **Cryptography Library Security:** https://cryptography.io/en/latest/security/
- **NIST Post-Quantum Cryptography:** https://csrc.nist.gov/projects/post-quantum-cryptography
- **DID Security Considerations:** https://www.w3.org/TR/did-core/#security-considerations
- **Certificate Transparency:** https://certificate.transparency.dev/
- **OWASP Cryptographic Storage Cheat Sheet:** https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html

## Contact

- Security issues: **security@genesisgraph.dev**
- General questions: https://github.com/scottsen/genesisgraph/discussions
- Bug reports: https://github.com/scottsen/genesisgraph/issues

---

**Last Updated:** 2025-11-17
**Version:** 1.0
