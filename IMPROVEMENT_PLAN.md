# GenesisGraph Improvement Plan

**Version:** 1.0
**Date:** 2025-11-15
**Status:** ⚠️ HISTORICAL REFERENCE - See [ROADMAP.md](ROADMAP.md) for current plan
**Last Updated:** 2025-11-21

---

## 🔄 Document Status Update (November 2025)

**This document was written for v0.2.0 planning but the project has since progressed to v0.3.0.**

**Current Status:**
- ✅ **Phase 4 (Enhanced Features)** has been COMPLETED
  - Blake3 hash support implemented
  - Performance optimizations completed (2-3x faster)
  - DID resolution expanded (did:ion, did:ethr)
  - Zero-knowledge proof templates added
  - Profile validators implemented (AI Basic, CAM)

- ✅ **Phase 5 (Release Preparation)** partially completed
  - v0.3.0 released to PyPI (not v0.2.0)
  - Pre-commit hooks configured
  - Comprehensive test suite (666+ tests)

**What remains relevant:**
- Phase 1-3 tactical details for code quality improvements
- Test coverage target (still at 63%, need 90%+)
- API documentation site (not yet built)
- Architecture documentation (still needed)

**👉 For current roadmap and priorities, see [ROADMAP.md](ROADMAP.md)**

This document is preserved for its detailed tactical implementation guidance, particularly for:
- Testing strategies and test case templates
- Documentation infrastructure setup
- Code quality tooling configuration

---

## Executive Summary

This document outlines a comprehensive improvement plan for the GenesisGraph project, addressing both **documentation gaps** and **implementation deficiencies** identified through thorough codebase analysis.

**Original Project Health:** 8/10 - Excellent foundation with clear improvement path
**Current Project Health (v0.3.0):** 8/10 - Many features completed, quality gaps remain
**Target Project Health (v1.0):** 9.5/10 - Production-ready with comprehensive testing and documentation

**Key Metrics:**
- Test Coverage: 63% → 90%+ ⚠️ STILL NEEDED
- Documentation Coverage: 7.5/10 → 9/10 ⚠️ STILL NEEDED
- Implementation Completeness: 70% → 95% ✅ At ~85% (v0.3.0)

---

## Implementation Phases

### Phase 1: Critical Fixes (Week 1-2)
**Goal:** Address security and reliability issues that block production use

### Phase 2: Testing & Quality (Week 3-4)
**Goal:** Achieve 90%+ test coverage and enforce code quality standards

### Phase 3: Documentation Infrastructure (Week 5-6)
**Goal:** Create developer documentation and API references

### Phase 4: Enhanced Features (Week 7-8)
**Goal:** Complete planned features and performance optimization

### Phase 5: Release Preparation (Week 9-10)
**Goal:** Prepare for v0.2.0 release and PyPI publication

---

## Detailed Task Breakdown

---

## PHASE 1: Critical Fixes

### 1.1 Enable JSON Schema Validation
**Priority:** Critical
**Effort:** 2-3 hours
**Dependencies:** None
**Files:** `genesisgraph/validator.py`

**Current Issue:**
- Schema exists at `schema/genesisgraph-core-v0.1.yaml`
- Validator shows "jsonschema not installed" warning even when jsonschema IS installed
- Schema validation infrastructure exists but is bypassed

**Tasks:**
1. Debug why schema loading is failing (validator.py:~50-70)
2. Fix schema file path resolution (may be relative path issue)
3. Enable schema validation by default in `validate()` method
4. Add test cases for schema validation errors
5. Update documentation to reflect schema validation

**Acceptance Criteria:**
- Schema validation runs on all valid/invalid documents
- Clear error messages when schema validation fails
- Test coverage for schema validation paths
- No warnings about missing jsonschema

**Testing:**
```bash
# Should validate successfully
gg validate examples/level-a-full-disclosure.gg.yaml

# Should fail with schema errors
gg validate tests/fixtures/invalid-schema.gg.yaml
```

---

### 1.2 Implement Signature Verification
**Priority:** Critical
**Effort:** 8-12 hours
**Dependencies:** None
**Files:** `genesisgraph/validator.py`, `tests/test_signature_verification.py`

**Current Issue:**
- Validator accepts `signed` attestations but doesn't verify signatures
- ed25519 signature verification not implemented
- Security feature incomplete

**Tasks:**
1. Implement ed25519 signature verification using `cryptography` library
2. Add signature format validation (base64, hex)
3. Extract public key from signer DID or embedded key
4. Verify signature over canonical JSON representation
5. Add comprehensive signature verification tests
6. Document signature format requirements

**Implementation Steps:**
```python
# genesisgraph/validator.py
def verify_signature(self, data: dict, signature: str, public_key: str) -> bool:
    """
    Verify ed25519 signature over canonical JSON

    Args:
        data: Document data to verify
        signature: Base64-encoded signature
        public_key: Base64-encoded ed25519 public key

    Returns:
        True if signature is valid

    Raises:
        SignatureError: If verification fails
    """
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    import json
    import base64

    # Canonical JSON representation
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
    message = canonical.encode('utf-8')

    # Decode signature and public key
    sig_bytes = base64.b64decode(signature)
    key_bytes = base64.b64decode(public_key)

    # Verify
    public_key_obj = ed25519.Ed25519PublicKey.from_public_bytes(key_bytes)
    try:
        public_key_obj.verify(sig_bytes, message)
        return True
    except Exception as e:
        raise SignatureError(f"Signature verification failed: {e}")
```

**Test Cases:**
- Valid signature verification
- Invalid signature detection
- Malformed signature handling
- Public key format errors
- Canonical JSON generation

**Acceptance Criteria:**
- All `signed` attestations are cryptographically verified
- Invalid signatures are rejected with clear error messages
- Test coverage for signature verification ≥ 95%
- Documentation includes signature format specification

---

### 1.3 Add SECURITY.md
**Priority:** High
**Effort:** 2-3 hours
**Dependencies:** None
**Files:** `SECURITY.md`, `README.md`

**Current Issue:**
- No security policy document
- No vulnerability reporting process
- No threat model documented

**Tasks:**
1. Create SECURITY.md with vulnerability reporting process
2. Document security considerations for each disclosure level
3. Add threat model section
4. Document cryptographic assumptions
5. Add security best practices for users
6. Link from README.md

**Template Sections:**
```markdown
# Security Policy

## Supported Versions
## Reporting a Vulnerability
## Security Considerations
### Disclosure Levels
### Cryptographic Assumptions
### Trust Model
## Best Practices
## Security Features
## Known Limitations
```

**Acceptance Criteria:**
- SECURITY.md follows GitHub security advisory format
- Clear vulnerability reporting email/process
- Threat model covers all components
- Linked from README.md

---

### 1.4 Create CHANGELOG.md
**Priority:** Medium
**Effort:** 1-2 hours
**Dependencies:** None
**Files:** `CHANGELOG.md`

**Current Issue:**
- No version history documentation
- No upgrade/migration notes
- Hard to track changes between versions

**Tasks:**
1. Create CHANGELOG.md following Keep a Changelog format
2. Document all changes from v0.1.0
3. Set up conventional commit standard
4. Add changelog generation to CI/CD
5. Link from README.md

**Format:**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.1.0] - 2025-XX-XX

### Added
- Initial release with core validation
- CLI tool (`gg` command)
- Three disclosure level examples
- Comprehensive documentation
```

**Acceptance Criteria:**
- CHANGELOG.md exists with v0.1.0 entries
- Follows Keep a Changelog format
- All significant changes documented

---

## PHASE 2: Testing & Quality

### 2.1 Increase Test Coverage to 90%+
**Priority:** Critical
**Effort:** 12-16 hours
**Dependencies:** 1.1, 1.2
**Files:** `tests/test_validator.py`, `tests/test_cli.py`, `tests/test_integration.py`

**Current State:**
- Overall coverage: 40%
- validator.py: 63%
- cli.py: 0%
- errors.py: 100%

**Target:**
- Overall coverage: 90%+
- All modules: ≥ 85%

**Tasks:**

#### 2.1.1 Add CLI Tests
**File:** `tests/test_cli.py`

```python
# Test cases needed:
- test_cli_validate_command_valid_file()
- test_cli_validate_command_invalid_file()
- test_cli_validate_command_missing_file()
- test_cli_info_command()
- test_cli_version_command()
- test_cli_exit_codes()
- test_cli_without_click_fallback()
- test_cli_output_formatting()
```

#### 2.1.2 Add File Hash Verification Tests
**File:** `tests/test_hash_verification.py`

```python
# Test cases needed:
- test_sha256_verification_valid()
- test_sha256_verification_invalid()
- test_sha512_verification_valid()
- test_file_not_found()
- test_hash_format_validation()
- test_uri_entities_skip_hash_check()
```

#### 2.1.3 Add Edge Case Tests
**File:** `tests/test_validator.py` (expand)

```python
# Additional test cases:
- test_empty_document()
- test_large_document_performance()
- test_deeply_nested_operations()
- test_unicode_in_entity_ids()
- test_special_characters_in_paths()
- test_circular_dependencies()
- test_malformed_yaml()
- test_validation_modes_progression()
```

#### 2.1.4 Add Integration Tests
**File:** `tests/test_integration.py`

```python
# End-to-end workflows:
- test_full_validation_workflow()
- test_level_a_b_c_examples_e2e()
- test_cli_to_validator_integration()
- test_verification_script_integration()
```

**Acceptance Criteria:**
- Overall test coverage ≥ 90%
- All modules have ≥ 85% coverage
- CLI has ≥ 80% coverage
- Integration tests cover main workflows
- Test suite runs in < 5 seconds

---

### 2.2 Tighten Type Checking
**Priority:** High
**Effort:** 4-6 hours
**Dependencies:** None
**Files:** `pyproject.toml`, `genesisgraph/*.py`

**Current Issue:**
- mypy has `continue-on-error: true` in CI
- `disallow_untyped_defs: false` is too lenient
- Type safety not enforced

**Tasks:**
1. Enable strict mypy configuration
2. Fix all type errors in codebase
3. Add type hints to internal helper methods
4. Remove `continue-on-error` from CI
5. Add type checking to pre-commit hooks

**Configuration Changes:**
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true        # Enable strict typing
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_calls = true
warn_redundant_casts = true
warn_unused_ignores = true
strict_optional = true
```

**CI Changes:**
```yaml
# .github/workflows/ci.yml
- name: Type check with mypy
  run: mypy genesisgraph
  # Remove: continue-on-error: true
```

**Acceptance Criteria:**
- mypy runs without errors
- All functions have type hints
- CI fails on type errors
- No `# type: ignore` comments without justification

---

### 2.3 Add Pre-commit Hooks
**Priority:** Medium
**Effort:** 2-3 hours
**Dependencies:** 2.2
**Files:** `.pre-commit-config.yaml`

**Current Issue:**
- No automated code quality checks before commit
- Easy to commit code that fails CI

**Tasks:**
1. Create `.pre-commit-config.yaml`
2. Add hooks: black, ruff, mypy, pytest
3. Document in CONTRIBUTING.md
4. Test hook installation

**Configuration:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

**Acceptance Criteria:**
- Pre-commit hooks installed successfully
- Hooks run on every commit
- Failed hooks block commits
- Documentation updated

---

### 2.4 Add Performance Benchmarks
**Priority:** Low
**Effort:** 3-4 hours
**Dependencies:** 2.1
**Files:** `tests/test_performance.py`

**Current Issue:**
- No performance testing
- Unknown scaling characteristics
- No regression detection

**Tasks:**
1. Install pytest-benchmark
2. Create benchmark tests for validation
3. Test with various document sizes (10, 100, 1000 entities)
4. Add memory profiling
5. Document expected performance

**Benchmark Tests:**
```python
# tests/test_performance.py
def test_validation_performance_small_document(benchmark):
    """Benchmark validation of 10 entities"""
    result = benchmark(validator.validate_file, "fixtures/small.gg.yaml")
    assert result.is_valid

def test_validation_performance_large_document(benchmark):
    """Benchmark validation of 1000 entities"""
    result = benchmark(validator.validate_file, "fixtures/large.gg.yaml")
    assert result.is_valid
```

**Acceptance Criteria:**
- Benchmarks for small/medium/large documents
- Performance baselines documented
- CI tracks performance regressions
- Memory usage profiled

---

## PHASE 3: Documentation Infrastructure

### 3.1 Create API Documentation Site
**Priority:** High
**Effort:** 6-8 hours
**Dependencies:** None
**Files:** `docs/`, `mkdocs.yml`, `.github/workflows/docs.yml`

**Current Issue:**
- No auto-generated API documentation
- Users must read source code to discover methods
- No hosted documentation site

**Tasks:**

#### 3.1.1 Set Up MkDocs
1. Install mkdocs-material theme
2. Create mkdocs.yml configuration
3. Set up docs/ directory structure
4. Configure autodoc for API reference

**Directory Structure:**
```
docs/
├── index.md                    # Landing page
├── getting-started/
│   ├── installation.md
│   ├── quickstart.md
│   └── examples.md
├── user-guide/
│   ├── validation.md
│   ├── cli.md
│   └── disclosure-levels.md
├── api-reference/
│   ├── validator.md
│   ├── cli.md
│   └── errors.md
├── developer-guide/
│   ├── architecture.md
│   ├── contributing.md
│   └── testing.md
├── specifications/
│   └── spec-v0.1.md
└── faq.md
```

**Configuration:**
```yaml
# mkdocs.yml
site_name: GenesisGraph Documentation
site_url: https://scottsen.github.io/genesisgraph
repo_url: https://github.com/scottsen/genesisgraph
theme:
  name: material
  palette:
    primary: indigo
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate
    - search.suggest

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true

nav:
  - Home: index.md
  - Getting Started:
      - Installation: getting-started/installation.md
      - Quickstart: getting-started/quickstart.md
  - User Guide:
      - Validation: user-guide/validation.md
      - CLI: user-guide/cli.md
  - API Reference:
      - Validator: api-reference/validator.md
      - CLI: api-reference/cli.md
  - Developer Guide:
      - Architecture: developer-guide/architecture.md
      - Contributing: developer-guide/contributing.md
```

#### 3.1.2 Generate API Documentation
1. Create API reference pages using mkdocstrings
2. Auto-generate from docstrings
3. Add code examples to API docs
4. Link related functions

**Example API Page:**
```markdown
# Validator API

::: genesisgraph.validator.GenesisGraphValidator
    options:
      show_root_heading: true
      show_source: true
      members:
        - __init__
        - validate
        - validate_file
        - validate_entities
        - validate_operations
```

#### 3.1.3 Set Up GitHub Pages Deployment
1. Create `.github/workflows/docs.yml`
2. Configure automatic deployment on push to main
3. Test deployment

**Workflow:**
```yaml
# .github/workflows/docs.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - run: pip install mkdocs-material mkdocstrings[python]
      - run: mkdocs gh-deploy --force
```

**Acceptance Criteria:**
- MkDocs site builds successfully
- API reference auto-generated from docstrings
- Deployed to GitHub Pages
- All existing docs migrated
- Search functionality works

---

### 3.2 Add Architecture Documentation
**Priority:** High
**Effort:** 4-6 hours
**Dependencies:** 3.1
**Files:** `docs/developer-guide/architecture.md`

**Current Issue:**
- No system architecture documentation
- No diagrams showing component relationships
- Hard for new contributors to understand design

**Tasks:**
1. Create architecture overview document
2. Add system architecture diagram
3. Document validation flow
4. Add class relationship diagram
5. Document data model
6. Explain design decisions

**Diagrams Needed:**

#### System Architecture
```
┌─────────────────────────────────────────────┐
│              GenesisGraph CLI               │
│                 (cli.py)                    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│          GenesisGraphValidator              │
│              (validator.py)                 │
├─────────────────────────────────────────────┤
│ • Schema Validation (JSON Schema)          │
│ • Entity Validation (IDs, types, hashes)   │
│ • Operation Validation (I/O, attestations) │
│ • Tool Validation (types, capabilities)    │
│ • Hash Verification (SHA256/512)           │
│ • Signature Verification (ed25519)         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│            Verification Scripts             │
│  • Merkle Tree (verify_sealed_subgraph.py) │
│  • Transparency Log (verify_transparency.py)│
└─────────────────────────────────────────────┘
```

#### Validation Flow
```
Input .gg.yaml File
        │
        ▼
   Parse YAML
        │
        ▼
Schema Validation ──────► [FAIL] Return errors
        │
        │ [PASS]
        ▼
Validate spec_version
        │
        ▼
Validate Entities
 • Check required fields
 • Verify hash formats
 • Compute file hashes
        │
        ▼
Validate Operations
 • Check inputs/outputs exist
 • Verify attestations
 • Check sealed subgraphs
        │
        ▼
Validate Tools
 • Check types
 • Verify capabilities
        │
        ▼
Verify Attestations
 • Basic: timestamp only
 • Signed: verify signatures
 • Verifiable: crypto checks
 • ZK: proof verification
        │
        ▼
   Return Result
   (errors/warnings)
```

#### Class Diagram
```
┌─────────────────────────────┐
│   GenesisGraphValidator     │
├─────────────────────────────┤
│ - schema: dict              │
│ - strict_mode: bool         │
├─────────────────────────────┤
│ + validate(data) → Result   │
│ + validate_file(path) → Result │
│ # validate_entities()       │
│ # validate_operations()     │
│ # validate_tools()          │
│ # verify_hash()             │
│ # verify_signature()        │
└─────────────────────────────┘
         △
         │ uses
         │
┌────────┴────────┐
│ ValidationResult │
├─────────────────┤
│ - is_valid: bool │
│ - errors: list   │
│ - warnings: list │
├─────────────────┤
│ + __bool__()    │
│ + report()      │
└─────────────────┘
```

**Content Sections:**
```markdown
# Architecture

## Overview
## Core Components
### Validator
### CLI
### Verification Scripts
## Data Model
### Entities
### Operations
### Tools
### Attestations
## Validation Flow
## Design Decisions
### Progressive Validation Modes
### Flexible Dependency Management
### Graceful Degradation
## Extension Points
## Security Architecture
```

**Acceptance Criteria:**
- Architecture document with diagrams
- Validation flow clearly documented
- Design decisions explained
- Easy for new contributors to understand

---

### 3.3 Add Inline Code Comments
**Priority:** Medium
**Effort:** 4-6 hours
**Dependencies:** None
**Files:** `genesisgraph/validator.py`, `genesisgraph/cli.py`

**Current Issue:**
- Only 2.5% inline comment density (industry standard: 10-20%)
- Complex logic lacks explanation
- Regex patterns not documented

**Tasks:**

#### 3.3.1 Add Comments to validator.py
Target areas:
1. Hash verification logic (lines ~180-220)
2. Regex patterns for ID/hash validation (lines ~120-140)
3. Attestation mode validation (lines ~280-320)
4. Sealed subgraph handling (lines ~240-260)

**Example:**
```python
# Before:
if re.match(r'^gg:[a-z0-9\-]+:[a-z0-9\-]+:[a-zA-Z0-9\-_.]+$', entity_id):
    pass

# After:
# Entity ID format: gg:<type>:<source>:<identifier>
# Examples:
#   gg:file:project:src/main.py
#   gg:model:provider:gpt-4
# Regex breakdown:
#   gg: - literal prefix
#   [a-z0-9\-]+ - type (lowercase alphanumeric + hyphen)
#   [a-z0-9\-]+ - source (lowercase alphanumeric + hyphen)
#   [a-zA-Z0-9\-_.]+ - identifier (alphanumeric + hyphen/underscore/dot)
if re.match(r'^gg:[a-z0-9\-]+:[a-z0-9\-]+:[a-zA-Z0-9\-_.]+$', entity_id):
    pass
```

#### 3.3.2 Add Comments to cli.py
Target areas:
1. Fallback CLI implementation (lines ~140-180)
2. Exit code logic (lines ~90-110)
3. Rich output formatting (lines ~50-80)

#### 3.3.3 Add Comments to Scripts
1. Merkle tree construction (`scripts/verify_sealed_subgraph.py`)
2. Transparency log verification (`scripts/verify_transparency_anchoring.py`)

**Acceptance Criteria:**
- Comment density ≥ 10% in complex modules
- All regex patterns explained
- Complex algorithms have step-by-step comments
- Non-obvious logic clarified

---

### 3.4 Create Troubleshooting Guide
**Priority:** Medium
**Effort:** 2-3 hours
**Dependencies:** None
**Files:** `docs/troubleshooting.md`

**Current Issue:**
- No troubleshooting documentation
- Common errors not documented
- Platform-specific issues unknown

**Tasks:**
1. Create troubleshooting guide
2. Document common errors and solutions
3. Add platform-specific notes
4. Include debug logging instructions

**Sections:**
```markdown
# Troubleshooting Guide

## Installation Issues
### Python Version Compatibility
### Dependency Conflicts
### Platform-Specific Issues (Windows, macOS, Linux)

## Validation Errors
### "entities must be a list"
### "Invalid hash format"
### "File not found"
### "Schema validation failed"

## CLI Issues
### Command not found (PATH issues)
### Click not installed (fallback mode)
### Unicode errors in output

## Performance Issues
### Large file validation slow
### Memory usage high

## Debug Mode
### Enable debug logging
### Verbose output

## Common Workarounds

## Getting Help
```

**Acceptance Criteria:**
- Covers 10+ common issues
- Solutions tested and verified
- Platform-specific notes included
- Linked from main documentation

---

### 3.5 Add Testing Documentation
**Priority:** Low
**Effort:** 2-3 hours
**Dependencies:** 2.1
**Files:** `docs/developer-guide/testing.md`

**Current Issue:**
- No testing strategy documentation
- Hard for contributors to write tests
- Test patterns not explained

**Tasks:**
1. Document testing strategy
2. Explain test organization
3. Provide test writing guide
4. Document fixtures and helpers
5. Add examples

**Content:**
```markdown
# Testing Guide

## Testing Philosophy
## Test Organization
### Unit Tests
### Integration Tests
### Performance Tests
## Writing Tests
### Test Naming
### Fixtures
### Assertions
## Running Tests
### Full Suite
### Specific Tests
### Coverage Reports
## CI/CD Integration
## Best Practices
```

**Acceptance Criteria:**
- Testing strategy documented
- Examples for each test type
- Fixture usage explained
- Easy for new contributors

---

## PHASE 4: Enhanced Features

### 4.1 Add DID Resolution
**Priority:** Medium
**Effort:** 8-12 hours
**Dependencies:** 1.2
**Files:** `genesisgraph/did_resolver.py`, `tests/test_did_resolver.py`

**Current Issue:**
- DID identifiers accepted but not resolved
- Can't verify identity claims
- Signer identity unverified

**Tasks:**
1. Implement DID resolver for did:key, did:web
2. Add public key extraction from DID documents
3. Integrate with signature verification
4. Add caching for resolved DIDs
5. Add comprehensive tests
6. Document supported DID methods

**Implementation:**
```python
# genesisgraph/did_resolver.py
class DIDResolver:
    """Resolve DIDs to DID documents and public keys"""

    async def resolve(self, did: str) -> dict:
        """Resolve DID to DID document"""

    def extract_public_key(self, did_doc: dict, key_id: str) -> bytes:
        """Extract public key from DID document"""
```

**Supported Methods:**
- `did:key` - Self-describing keys
- `did:web` - Web-based DIDs
- Future: `did:ethr`, `did:ion`

**Acceptance Criteria:**
- did:key and did:web resolution works
- Public keys extracted correctly
- Integrated with signature verification
- Test coverage ≥ 85%
- Documentation includes DID examples

---

### 4.2 Add Blake3 Hash Support
**Priority:** Low
**Effort:** 3-4 hours
**Dependencies:** None
**Files:** `genesisgraph/validator.py`

**Current Issue:**
- Only SHA256/SHA512 supported
- Blake3 mentioned in docs but not implemented
- Modern hash algorithm not available

**Tasks:**
1. Add blake3 dependency (optional)
2. Implement blake3 hash verification
3. Update hash format validation
4. Add tests for blake3
5. Update documentation

**Implementation:**
```python
# Hash format support:
# sha256:<hex>
# sha512:<hex>
# blake3:<hex>

if hash_value.startswith('blake3:'):
    try:
        import blake3
        computed = blake3.blake3(file_content).hexdigest()
    except ImportError:
        warnings.append("blake3 not installed - skipping verification")
```

**Acceptance Criteria:**
- Blake3 hashes verified when library available
- Graceful degradation if blake3 not installed
- Tests for blake3 verification
- Documentation updated

---

### 4.3 Add Profile Validators
**Priority:** Low
**Effort:** 6-8 hours
**Dependencies:** 2.1
**Files:** `genesisgraph/profiles/`, `tests/test_profiles.py`

**Current Issue:**
- No profile-specific validation
- AI profile (gg-ai-basic-v1) not implemented
- CAM profile (gg-cam-v1) not implemented

**Tasks:**
1. Create profile validator framework
2. Implement gg-ai-basic-v1 profile
3. Implement gg-cam-v1 profile
4. Add profile-specific validation rules
5. Add tests for each profile
6. Document profile specifications

**Structure:**
```
genesisgraph/profiles/
├── __init__.py
├── base.py                 # BaseProfileValidator
├── ai_basic_v1.py          # gg-ai-basic-v1
└── cam_v1.py               # gg-cam-v1
```

**Example Profile:**
```python
# genesisgraph/profiles/ai_basic_v1.py
class AIBasicV1ProfileValidator(BaseProfileValidator):
    """
    Validator for gg-ai-basic-v1 profile

    Required tool types: AIModel
    Required attestations: basic or signed
    Optional: model_card, dataset references
    """

    def validate_profile(self, data: dict) -> ValidationResult:
        # Profile-specific rules
        pass
```

**Acceptance Criteria:**
- Profile framework implemented
- At least 2 profiles implemented
- Profile-specific validation works
- Documentation for each profile
- Test coverage ≥ 80%

---

### 4.4 Performance Optimization
**Priority:** Low
**Effort:** 4-6 hours
**Dependencies:** 2.4
**Files:** `genesisgraph/validator.py`

**Current Issue:**
- No performance optimization
- Unknown scaling for large documents
- Potential bottlenecks not addressed

**Tasks:**
1. Profile validation performance
2. Optimize hash verification (parallel processing)
3. Add caching for repeated validations
4. Optimize regex compilation
5. Add lazy loading for large files
6. Document performance characteristics

**Optimizations:**
```python
# Cache compiled regexes
ID_PATTERN = re.compile(r'^gg:[a-z0-9\-]+:[a-z0-9\-]+:[a-zA-Z0-9\-_.]+$')

# Parallel hash verification
from concurrent.futures import ThreadPoolExecutor

def verify_hashes_parallel(self, entities: list) -> list:
    with ThreadPoolExecutor() as executor:
        results = executor.map(self.verify_hash, entities)
    return list(results)
```

**Acceptance Criteria:**
- Validation 2x faster for large documents
- Benchmarks show improvement
- Performance characteristics documented
- No regression in small file performance

---

## PHASE 5: Release Preparation

### 5.1 Create Release Workflow
**Priority:** High
**Effort:** 3-4 hours
**Dependencies:** All previous
**Files:** `.github/workflows/release.yml`

**Current Issue:**
- No automated release process
- Manual PyPI publishing error-prone
- No version bumping automation

**Tasks:**
1. Create release workflow
2. Automate version bumping
3. Automate CHANGELOG generation
4. Automate PyPI publishing
5. Create GitHub releases
6. Test on test.pypi.org first

**Workflow:**
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - name: Build package
        run: |
          pip install build twine
          python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: CHANGELOG.md
          files: dist/*
```

**Acceptance Criteria:**
- Release workflow tested on test.pypi.org
- Version bumping automated
- CHANGELOG auto-generated
- GitHub releases created automatically
- Documentation published on release

---

### 5.2 Publish to PyPI
**Priority:** High
**Effort:** 2-3 hours
**Dependencies:** 5.1
**Files:** `pyproject.toml`

**Current Issue:**
- Package not on PyPI
- Users can't `pip install genesisgraph`

**Tasks:**
1. Register on PyPI
2. Set up API token
3. Test publish to test.pypi.org
4. Publish v0.2.0 to PyPI
5. Verify installation
6. Update documentation with pip install instructions

**Testing:**
```bash
# Test on test.pypi.org
python -m build
twine upload --repository testpypi dist/*

# Install and test
pip install --index-url https://test.pypi.org/simple/ genesisgraph

# Publish to real PyPI
twine upload dist/*
```

**Acceptance Criteria:**
- Package on PyPI
- `pip install genesisgraph` works
- README displays correctly on PyPI
- All dependencies correct
- Version matches release tag

---

### 5.3 Create Getting Started Video
**Priority:** Low
**Effort:** 4-6 hours
**Dependencies:** 3.1, 5.2
**Files:** `docs/videos/`

**Current Issue:**
- No video tutorials
- Visual learners underserved
- Complex concepts hard to explain in text

**Tasks:**
1. Script 5-minute quickstart video
2. Record screen + voiceover
3. Edit and produce video
4. Upload to YouTube
5. Embed in documentation
6. Create video thumbnail

**Video Outline:**
```
0:00 - Intro: What is GenesisGraph?
0:30 - Installation (pip install)
1:00 - Creating your first .gg.yaml
2:00 - Running validation (CLI demo)
2:30 - Understanding disclosure levels
4:00 - Next steps and resources
4:30 - Outro
```

**Acceptance Criteria:**
- 5-minute video published on YouTube
- Embedded in documentation
- Clear audio and visuals
- Demonstrates key features

---

### 5.4 Community Outreach
**Priority:** Medium
**Effort:** Ongoing
**Dependencies:** 5.2
**Files:** Various

**Current Issue:**
- No community engagement
- No early adopters
- Limited feedback

**Tasks:**
1. Post on relevant subreddits (r/Python, r/MachineLearning)
2. Write blog post announcing v0.2.0
3. Create Twitter/X thread
4. Post on Hacker News
5. Reach out to potential users
6. Create demonstration notebooks

**Targets:**
- AI/ML community (Hugging Face, Papers with Code)
- Manufacturing/CAD community
- Scientific research community
- Digital provenance/authentication community

**Acceptance Criteria:**
- 3+ blog posts/announcements published
- 100+ GitHub stars
- 5+ external contributors
- 10+ issues/discussions from community

---

## Implementation Checklist

### Phase 1: Critical Fixes ✅
- [ ] 1.1 Enable JSON Schema Validation (2-3 hours)
- [ ] 1.2 Implement Signature Verification (8-12 hours)
- [ ] 1.3 Add SECURITY.md (2-3 hours)
- [ ] 1.4 Create CHANGELOG.md (1-2 hours)

**Total: 13-20 hours (2 weeks)**

### Phase 2: Testing & Quality ✅
- [ ] 2.1 Increase Test Coverage to 90%+ (12-16 hours)
  - [ ] 2.1.1 Add CLI Tests
  - [ ] 2.1.2 Add Hash Verification Tests
  - [ ] 2.1.3 Add Edge Case Tests
  - [ ] 2.1.4 Add Integration Tests
- [ ] 2.2 Tighten Type Checking (4-6 hours)
- [ ] 2.3 Add Pre-commit Hooks (2-3 hours)
- [ ] 2.4 Add Performance Benchmarks (3-4 hours)

**Total: 21-29 hours (2 weeks)**

### Phase 3: Documentation Infrastructure ✅
- [ ] 3.1 Create API Documentation Site (6-8 hours)
- [ ] 3.2 Add Architecture Documentation (4-6 hours)
- [ ] 3.3 Add Inline Code Comments (4-6 hours)
- [ ] 3.4 Create Troubleshooting Guide (2-3 hours)
- [ ] 3.5 Add Testing Documentation (2-3 hours)

**Total: 18-26 hours (2 weeks)**

### Phase 4: Enhanced Features ✅
- [ ] 4.1 Add DID Resolution (8-12 hours)
- [ ] 4.2 Add Blake3 Hash Support (3-4 hours)
- [ ] 4.3 Add Profile Validators (6-8 hours)
- [ ] 4.4 Performance Optimization (4-6 hours)

**Total: 21-30 hours (2 weeks)**

### Phase 5: Release Preparation ✅
- [ ] 5.1 Create Release Workflow (3-4 hours)
- [ ] 5.2 Publish to PyPI (2-3 hours)
- [ ] 5.3 Create Getting Started Video (4-6 hours)
- [ ] 5.4 Community Outreach (Ongoing)

**Total: 9-13 hours (2 weeks)**

---

## Overall Timeline

**Total Estimated Effort:** 82-118 hours (10-15 weeks at 8 hours/week)

**Recommended Schedule:**
- **Weeks 1-2:** Phase 1 (Critical Fixes)
- **Weeks 3-4:** Phase 2 (Testing & Quality)
- **Weeks 5-6:** Phase 3 (Documentation Infrastructure)
- **Weeks 7-8:** Phase 4 (Enhanced Features)
- **Weeks 9-10:** Phase 5 (Release Preparation)

**Milestones:**
- **Week 2:** v0.1.1 - Critical security fixes
- **Week 4:** v0.1.2 - Test coverage ≥ 90%
- **Week 6:** v0.2.0-beta - Documentation complete
- **Week 8:** v0.2.0-rc1 - All features complete
- **Week 10:** v0.2.0 - Production release

---

## Success Metrics

### Code Quality
- [ ] Test coverage ≥ 90%
- [ ] Mypy passes with strict mode
- [ ] Ruff linting passes
- [ ] No critical security issues

### Documentation
- [ ] API docs hosted and searchable
- [ ] Architecture documented with diagrams
- [ ] Troubleshooting guide with 10+ solutions
- [ ] Video tutorial published

### Features
- [ ] Signature verification working
- [ ] JSON Schema validation enabled
- [ ] DID resolution implemented
- [ ] 2+ profile validators

### Community
- [ ] Published to PyPI
- [ ] 100+ GitHub stars
- [ ] 5+ external contributors
- [ ] 10+ community issues/discussions

### Performance
- [ ] Validation < 100ms for small files
- [ ] Validation < 1s for 100 entities
- [ ] Memory usage < 50MB for typical files

---

## Risk Assessment

### High Risk Items
1. **Signature Verification Implementation** - Complex cryptography
   - **Mitigation:** Use well-tested cryptography library, extensive testing

2. **Test Coverage Target** - Significant effort required
   - **Mitigation:** Break into smaller tasks, parallel development

3. **DID Resolution** - External dependencies, network calls
   - **Mitigation:** Start with simple methods (did:key), add caching

### Medium Risk Items
4. **Documentation Site Deployment** - GitHub Pages configuration
   - **Mitigation:** Test locally first, use established tools

5. **Performance Optimization** - May introduce bugs
   - **Mitigation:** Benchmark before/after, comprehensive regression testing

### Low Risk Items
6. **CHANGELOG/SECURITY.md** - Straightforward documentation
7. **Pre-commit Hooks** - Well-established tooling
8. **Blake3 Support** - Optional feature, graceful degradation

---

## Dependencies

### External Dependencies to Add
- `mkdocs-material` - Documentation site
- `mkdocstrings[python]` - API documentation
- `blake3` (optional) - Modern hashing
- `pytest-benchmark` - Performance testing
- `pre-commit` - Git hooks

### Python Version Support
- Minimum: Python 3.8
- Tested: 3.8, 3.9, 3.10, 3.11, 3.12
- Recommended: 3.11+

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize tasks** based on project goals
3. **Create GitHub issues** for each task
4. **Assign tasks** to contributors
5. **Set up project board** for tracking
6. **Begin Phase 1** implementation

---

## Questions for Discussion

1. Should we prioritize PyPI publication before 90% test coverage?
2. Do we need DID resolution for v0.2.0 or can it wait for v0.3.0?
3. Should we focus on documentation before enhanced features?
4. What's the timeline pressure for release?
5. Are there specific use cases we should prioritize?

---

**Document Owner:** Claude (AI Assistant)
**Last Updated:** 2025-11-15
**Next Review:** After Phase 1 completion
