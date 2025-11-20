# Changelog

All notable changes to GenesisGraph will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Removed
- TiaCAD integration references from all documentation (closed #15)
  - Removed TiaCAD section from USE_CASES.md
  - Removed TiaCAD examples from README.md, QUICKSTART.md, FAQ.md
  - Removed TiaCAD reference implementation from MAIN_SPEC.md
  - Rationale: TiaCAD scope too small compared to GenesisGraph's broader vision

---

## [0.2.0] - 2025-11-19

### Added
- **Certificate Transparency Log Integration** (RFC 6962)
  - Production-ready transparency log verification supporting Trillian and Rekor (Sigstore)
  - Merkle tree inclusion and consistency proofs for tamper-evident audit trails
  - Multi-log witness support for cross-organizational verification
  - Offline verification capability with cached proofs
  - 666 comprehensive tests covering all RFC 6962 operations
  - Full documentation in `docs/TRANSPARENCY_LOG.md`
  - Enterprise-ready for aerospace (AS9100D), manufacturing (ISO 9001:2015), healthcare (FDA 21 CFR Part 11)

- **did:web Support for Organization Identities**
  - Resolution of `did:web` identifiers for organizational public keys
  - Support for multiple key formats: publicKeyBase58, publicKeyMultibase, publicKeyJwk
  - End-to-end signature verification with did:web resolution
  - Integration with existing DID resolver infrastructure
  - 435 comprehensive tests including edge cases and error handling
  - Full documentation in `docs/DID_WEB_GUIDE.md`
  - Example workflows demonstrating organization identity verification

- **Production Signature Verification**
  - Full Ed25519 cryptographic signature verification
  - DID resolution for `did:key` identifiers (self-describing keys)
  - Canonical JSON encoding for signed data (RFC 8785-style)
  - Comprehensive test suite (20 tests) covering DID resolution, signature verification, and edge cases
  - Support for mock signatures in testing mode
  - `DIDResolver` class with caching and multiple DID method support

- **Security Documentation**
  - `SECURITY.md`: Comprehensive security policy and vulnerability reporting process
  - Threat model documentation (in-scope and out-of-scope threats)
  - Security best practices for users, creators, and developers
  - Cryptographic assumptions and disclosure level security considerations
  - Known limitations and security roadmap

### Changed
- **Validator Enhancement**
  - `GenesisGraphValidator` now supports production-ready signature verification when `verify_signatures=True`
  - Added `did_resolver` attribute for DID-based public key lookup
  - Improved error messages for signature verification failures
  - Added `_canonical_json()` method for deterministic JSON encoding
- **Documentation Updates**
  - Updated README.md to v0.2 Public Working Draft
  - Reorganized implementation roadmap to clearly show v0.1, v0.1.1, and v0.2 completions
  - Updated roadmap: v0.3 next steps now focus on SD-JWT/BBS+, ZK proofs, and profile validators

### Fixed
- Signature verification now performs actual cryptographic validation (was stub in v0.1.0-alpha)

---

## [0.1.0-alpha] - 2025-11-15

### Added

- **10-Week Improvement Plan** (PR #2)
  - `IMPROVEMENT_PLAN.md`: Comprehensive 5-phase enhancement roadmap
  - Phase 1: Critical fixes (schema validation, signature verification, security docs)
  - Phase 2: Testing & quality (90%+ coverage, strict typing, pre-commit hooks)
  - Phase 3: Documentation infrastructure (API docs, architecture, troubleshooting)
  - Phase 4: Enhanced features (DID resolution, Blake3, profile validators)
  - Phase 5: Release preparation (PyPI publishing, video tutorial, outreach)
  - Effort estimates: 82-118 hours total
  - Target: Move project health from 8/10 to 9.5/10

- **Core Validation Library & Production Infrastructure** (PR #1)
  - Complete GenesisGraph specification implementation
  - Three-level selective disclosure system (A/B/C tiers)
  - Cryptographic signature verification (Ed25519)
  - JSON Schema validation for all document types
  - Profile system (minimal, standard, extended)
  - CLI tools for validation and verification
  - Comprehensive test suite
  - Production-ready error handling and logging

### Documentation

- **Comprehensive Documentation Suite**:
  - `README.md`: Project overview, quick start, core concepts
  - `QUICKSTART.md`: 5-minute getting started guide
  - `STRATEGIC_CONTEXT.md`: Problem statement, value proposition, competitive analysis
  - `USE_CASES.md`: Real-world applications across industries
  - `FAQ.md`: Common questions and answers
  - `IMPLEMENTATION_SUMMARY.md`: Technical implementation details
  - `CONTRIBUTING.md`: Contribution guidelines
  - `spec/MAIN_SPEC.md`: Complete technical specification

- **Beth Search Integration**:
  - Added frontmatter to all major documentation files
  - Enables TIA knowledge graph discovery
  - Improved cross-project search and linking

### Core Features

- **Universal Verifiable Process Provenance**:
  - Prove how things were made without revealing trade secrets
  - Works across AI pipelines, manufacturing, scientific research, CAD/CAM
  - Open standard for process tracking and verification

- **Selective Disclosure System**:
  - Level A: Public claims (what was made, key properties)
  - Level B: Redacted process graph (structure without secrets)
  - Level C: Cryptographically signed full process (auditors only)
  - Enables compliance certification while protecting IP

- **Cryptographic Guarantees**:
  - Ed25519 signature verification
  - Hash-based process integrity checking
  - Tamper-evident provenance chains

---

## [0.0.1] - 2025-10-31

### Added
- Initial project structure
- Core specification development
- Basic documentation framework

---

**Repository**: https://github.com/scottsen/genesisgraph
**TIA Project**: `/home/scottsen/src/tia/.tia/projects/genesisgraph.yaml`
**License**: MIT (to be confirmed)

