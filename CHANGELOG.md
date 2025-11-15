# Changelog

All notable changes to GenesisGraph will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### In Progress
- Working towards v0.1 Public Working Draft
- Implementing improvements from 10-week enhancement plan

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

