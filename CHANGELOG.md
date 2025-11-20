# Changelog

All notable changes to GenesisGraph will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.4.0] - 2025-11-20

### Added

- **Formal Threat Model & Security Posture** ([docs/THREAT_MODEL.md](docs/THREAT_MODEL.md))
  - Comprehensive adversary model covering 7 attacker classes
  - Security levels (GG-SEC-1 through GG-SEC-4) for different risk profiles
  - Attack-defense matrix for common threat vectors
  - Trust assumptions documentation
  - Failure modes and mitigations
  - Security review framework for enterprise adoption

- **Delegation & Authorization Model** ([docs/DELEGATION_AND_AUTHORIZATION.md](docs/DELEGATION_AND_AUTHORIZATION.md))
  - Complete delegation chain framework for multi-agent ecosystems
  - Authorization proof schema for operation-level access control
  - Policy integration with OPA (Open Policy Agent) and AWS Cedar
  - Constraint enforcement and validation (rate limits, data scope, time windows)
  - Verifiable credentials (VC) and ZCAP-LD integration
  - New `gg-delegation-v1` profile for delegation-aware provenance
  - Closes the "authority → accountability" loop for AI agents

- **Agent Provenance Extension (GG-Agent-v1)** ([docs/AGENT_PROVENANCE_EXTENSION.md](docs/AGENT_PROVENANCE_EXTENSION.md))
  - Full specification for AI agent provenance (multi-turn conversations, reasoning traces, tool use)
  - Agent object model with capabilities, constraints, and delegation
  - Reasoning trace provenance with selective disclosure (sealed steps with Merkle commitments)
  - Agent memory & state tracking (checkpoints, memory evolution)
  - Multi-turn conversation provenance (entity chains for each turn)
  - Agent-to-tool delegation chains with policy evaluation
  - Safety & alignment attestations (certification, runtime checks)
  - New operation types: `agent_reasoning_step`, `agent_tool_invocation`, `agent_memory_update`, `human_review`, `safety_evaluation`
  - New entity types: `AgentMemorySnapshot`, `UserMessage`, `AgentResponse`, `ReasoningTrace`
  - Positions GenesisGraph as THE standard for AI agent governance

- **Lifecycle & Revocation Framework** ([docs/LIFECYCLE_AND_REVOCATION.md](docs/LIFECYCLE_AND_REVOCATION.md))
  - Temporal validation ("Was this tool version safe at the time of use?")
  - Entity lifecycle tracking (created, active, deprecated, revoked, expired states)
  - Tool lifecycle with CVE tracking and security advisories
  - Attestation revocation with transparency log integration
  - Revocation registry architecture and API
  - Temporal validation at specific points in time (`--at-time` parameter)
  - Freshness requirements for real-time use cases
  - Replacement chains and revocation propagation

- **Governance Framework** ([GOVERNANCE.md](GOVERNANCE.md))
  - Multi-stakeholder board structure (9 seats across AI, manufacturing, research, government, civil society)
  - Anti-capture safeguards (no single-entity control, term limits, geographic diversity)
  - Vendor neutrality requirements (Apache 2.0 reference implementations, no proprietary extensions)
  - Fork rights and trademark policy
  - Compatibility certification program ("GenesisGraph Compatible v0.X")
  - Succession planning and emergency procedures
  - Foundation funding model (membership tiers, government grants, cost-recovery services)
  - Community participation framework (working groups, contribution process)
  - Dispute resolution mechanisms (4-level escalation)
  - Prevents capture by large actors (AWS, Azure, Google, defense contractors)

- **Comprehensive Example: Medical AI Assistant Session** ([examples/agent-medical-assistant-session.gg.yaml](examples/agent-medical-assistant-session.gg.yaml))
  - 24-turn conversation with drug interaction analysis
  - HIPAA delegation chain (Hospital → Doctor → AI Agent)
  - Reasoning traces with selective disclosure (proprietary prompts sealed)
  - Tool use authorization (medical database, drug interaction checker)
  - Human-in-the-loop review at critical decision points
  - Runtime safety evaluation (harmful content, PII leakage, policy compliance)
  - Memory checkpoints tracking conversation state evolution
  - Multi-witness attestation (agent + human signatures)
  - Transparency log anchoring for audit trail

- **Critical Gaps Analysis for v1.0** ([CRITICAL_GAPS_ANALYSIS.md](CRITICAL_GAPS_ANALYSIS.md))
  - Comprehensive analysis identifying 10 strategic gaps and improvements
  - Roadmap for addressing gaps in v1.0 release
  - Positions GenesisGraph for global adoption and multi-agent AI governance

### Changed

- **README.md**: Updated to v0.4.0 with references to new strategic documentation
- **Documentation Structure**: Added 5 major new documents totaling ~12,000 words of specifications
- **Security Posture**: Moved from implicit to explicit security guarantees with formal threat model

### Impact

This release represents a **strategic leap** for GenesisGraph:

1. **Enterprise Readiness**: Threat model enables security teams to evaluate GenesisGraph
2. **AI Governance**: Agent provenance positions GenesisGraph as THE standard for AI agent accountability
3. **Regulatory Compliance**: Delegation + lifecycle frameworks enable HIPAA, FDA, AS9100D compliance
4. **Long-Term Sustainability**: Governance framework prevents vendor capture, ensures community control
5. **Temporal Trust**: Revocation framework enables forensic analysis ("Was this safe when we used it?")

**Addresses Critical Gaps:**
- Gap #1: Threat Model & Security Posture ✅
- Gap #2: Delegation & Authorization ✅
- Gap #3: Lifecycle & Revocation ✅
- Gap #8: Anti-Capture Governance ✅
- Gap #9: Agent Provenance ✅

**Next Steps for v1.0:**
- Implement reference validators for new profiles (`gg-delegation-v1`, `gg-agent-v1`)
- Build revocation registry infrastructure
- Create template system for common patterns (Gap #5)
- Formal semantics documentation (Gap #6)
- Economic model and marketplace (Gap #10)

---

## [0.3.0] - 2025-11-20

### Added

- **Additional DID Methods: ION and Ethereum** (PR #21)
  - ION (Sidetree on Bitcoin) DID resolution with Universal Resolver support
  - Ethereum DID resolution with multi-network support (mainnet, sepolia, polygon)
  - Comprehensive test coverage with 574 new tests
  - Full integration with existing DID resolver infrastructure
  - Support for both direct resolution and Universal Resolver fallback

- **Zero-Knowledge Proof Templates** (PR #20)
  - Template system for zero-knowledge compliance proofs
  - Range proof templates for proving parameter bounds without revealing values
  - Integration with existing profile validator system
  - Examples demonstrating ZK proof usage in compliance scenarios

- **Python and JavaScript SDK Libraries** (PR #19, closed #14)
  - Python builder API with fluent interface for programmatic document creation
  - Comprehensive type hints and validation in Python SDK
  - JavaScript/TypeScript SDK with full type definitions
  - Entity, Operation, Tool, and Attestation builders with method chaining
  - YAML and JSON export/import capabilities
  - 48 comprehensive tests with 93% code coverage for Python builder
  - Full documentation in `SDK-DEVELOPMENT-GUIDE.md` (1,368 lines)
  - Quick reference guide in `SDK-QUICK-REFERENCE.md` (477 lines)
  - Example code in `examples/python_sdk_quickstart.py` and `sdks/javascript/examples/quickstart.ts`
  - Enables programmatic integration for CI/CD pipelines and automation tools

- **Industry-Specific Profile Validators** (PR #18, closed #12)
  - `gg-ai-basic-v1`: AI/ML pipeline validation with FDA 21 CFR Part 11 support
  - `gg-cam-v1`: Computer-aided manufacturing validation with ISO-9001 compliance
  - Profile registry with automatic profile detection based on operation types
  - ISO 9001:2015 compliance validator for quality management systems
  - FDA 21 CFR Part 11 compliance validator for electronic records and signatures
  - Privacy-preserving validation with redacted parameter support
  - CLI integration with `--verify-profile` and `--profile` flags
  - Comprehensive test suite covering AI, manufacturing, and compliance validators
  - Full documentation in `docs/PROFILE_VALIDATORS.md`
  - Automated compliance checking for enterprise customers and regulatory use cases

- **SD-JWT and BBS+ Selective Disclosure** (PR #17, closed #10)
  - SD-JWT (Selective Disclosure JWT) implementation following IETF draft specification
  - BBS+ signature support for privacy-preserving credential verification
  - Predicate proofs for range validation without revealing exact values
  - Zero-knowledge range proofs with configurable boundaries
  - Privacy-preserving validation with selective claim disclosure
  - Integration with GenesisGraph attestation format
  - 1,385 new tests covering SD-JWT, BBS+, and predicate operations
  - Full documentation in `docs/SELECTIVE_DISCLOSURE.md` (469 lines)
  - Example attestations demonstrating SD-JWT, BBS+, and predicate usage
  - Optional `credentials` extra dependencies for advanced cryptographic features

### Fixed
- Test mocking code duplication eliminated (PR #22, closed #16)
  - Refactored DID resolution mocking to eliminate code duplication
  - Improved test maintainability and consistency

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

