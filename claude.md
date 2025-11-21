# Claude Code Guide for GenesisGraph

This document provides guidance for working with the GenesisGraph codebase using Claude Code.

## Project Overview

**GenesisGraph** is an open standard for cryptographically verifiable process provenance. It enables proving how things were made across AI pipelines, manufacturing, scientific research, healthcare, and other workflows where "show me how you made this" matters.

**Key Innovation:** Three-level selective disclosure (A/B/C) enables proving compliance without revealing trade secrets—solving the "certification vs IP protection" dilemma.

**Version:** v0.3.0 (November 2025)
**License:** Apache 2.0 (code), CC-BY 4.0 (specification)

## Tech Stack

- **Language:** Python 3.8+
- **Key Dependencies:**
  - PyYAML (6.0+) - YAML parsing
  - jsonschema (4.17+) - Schema validation
  - cryptography (41.0+) - Signatures, hashing
- **Optional Features:**
  - CLI: click, rich
  - Credentials: sd-jwt, jwcrypto, zksk (BBS+, ZK proofs)
  - Development: pytest, pytest-cov, black, ruff, mypy

## Quick Commands

```bash
# Install for development
pip install -e .

# Install with all features
pip install -e ".[dev,cli,credentials,blake3]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=genesisgraph --cov-report=term-missing

# Validate a workflow
gg validate examples/level-a-full-disclosure.gg.yaml

# Validate with profile checking
gg validate workflow.gg.yaml --verify-profile --profile gg-ai-basic-v1

# Format code
black genesisgraph tests

# Lint code
ruff check genesisgraph tests

# Type check
mypy genesisgraph
```

## Available Tools

### Progressive Reveal CLI

Located in `tools/progressive-reveal-cli/`, this is a powerful command-line tool for exploring files at different levels of detail. It's particularly useful when analyzing large configuration files, data files, or complex code files in the GenesisGraph repository.

#### Installation

```bash
cd tools/progressive-reveal-cli
pip install -e .
```

#### Usage

The tool provides 4 progressive levels of file exploration:

**Level 0: Metadata** - Quick overview of file characteristics
```bash
reveal path/to/file.yaml
```
Shows: filename, type, size, modification date, line count, SHA256 hash

**Level 1: Structure** - Structural synopsis without content
```bash
reveal path/to/file.yaml --level 1
```
For different file types, shows:
- YAML/JSON: Top-level keys, nesting depth, object/array counts
- Python: Imports, classes, functions, top-level assignments
- Markdown: Headings hierarchy, paragraph/code block/list counts
- Text: Line count, word count, estimated type

**Level 2: Preview** - Content preview with key sections
```bash
reveal path/to/file.py --level 2
```
Shows a condensed view of important content (e.g., class/function signatures, docstrings)

**Level 3: Full Content** - Complete file content with pagination
```bash
reveal path/to/file.md --level 3 --page-size 50
```
Full file content with configurable page size

#### Filtering with Grep

All levels support regex-based filtering:

```bash
# Find specific patterns in structure
reveal config.yaml --level 1 --grep "database"

# Preview with context around matches
reveal app.py --level 2 --grep "class" --context 2

# Full content filtered by pattern
reveal README.md --level 3 --grep "installation" --context 5
```

#### Common Workflows

**Exploring configuration files:**
```bash
# Start with metadata to understand size/type
reveal pyproject.toml

# Check structure to see all configuration sections
reveal pyproject.toml --level 1

# Preview specific sections
reveal pyproject.toml --level 2 --grep "dependencies"

# View full content when needed
reveal pyproject.toml --level 3
```

**Understanding Python modules:**
```bash
# See module structure (imports, classes, functions)
reveal genesisgraph/core.py --level 1

# Preview class/function signatures with docstrings
reveal genesisgraph/core.py --level 2

# Find specific implementations
reveal genesisgraph/core.py --level 3 --grep "def process" --context 10
```

**Analyzing documentation:**
```bash
# See document structure (headings, sections)
reveal README.md --level 1

# Preview introduction and key sections
reveal README.md --level 2

# Find specific topics
reveal README.md --level 3 --grep "API" --context 3
```

## Tips for Working with GenesisGraph

1. **Start Small**: Use `reveal` with level 0 or 1 to understand file structure before diving into full content
2. **Use Grep**: Filter large files with `--grep` to focus on relevant sections
3. **Progressive Exploration**: Follow the natural progression (metadata → structure → preview → full content)
4. **Context Lines**: Use `--context` to see code around matches for better understanding

## Code Structure

### Core Modules (`genesisgraph/`)

- **`builder.py`** - Fluent API for constructing GenesisGraph documents programmatically
- **`validator.py`** - Schema validation, signature verification, DID resolution
- **`did_resolver.py`** - DID resolution for identity verification (did:key, did:web, did:ion, did:ethr)
- **`transparency_log.py`** - RFC 6962 Certificate Transparency integration, Merkle proofs
- **`cli.py`** - Command-line interface (gg command)
- **`errors.py`** - Custom exception classes

### Subpackages

- **`compliance/`** - Compliance checkers (FDA 21 CFR 11, ISO 9001)
- **`credentials/`** - SD-JWT, BBS+ signatures, zero-knowledge proofs
- **`profiles/`** - Industry-specific validators (gg-ai-basic-v1, gg-cam-v1)

### Key Test Coverage

- **363 comprehensive tests** across all modules
- **76% overall coverage**
- High-coverage modules: SD-JWT (98%), BBS+ (99%), ZKP (97%), Builder (93%), DID resolution (90%)

## Repository Structure

```
genesisgraph/
├── genesisgraph/           # Main package source code
│   ├── compliance/         # Compliance checkers (FDA, ISO)
│   ├── credentials/        # SD-JWT, BBS+, ZK proofs
│   └── profiles/           # Industry validators
├── tests/                  # Test suite (363 tests, 76% coverage)
├── docs/                   # Documentation
│   ├── PROFILE_VALIDATORS.md
│   ├── SELECTIVE_DISCLOSURE.md
│   ├── TRANSPARENCY_LOG.md
│   └── DID_WEB_GUIDE.md
├── tools/                  # Development tools
│   └── progressive-reveal-cli/
├── examples/               # Example workflows (.gg.yaml files)
├── scripts/                # Verification scripts
├── spec/                   # Specification (MAIN_SPEC.md - 24,317 lines)
├── schema/                 # JSON Schema definitions
└── pyproject.toml          # Project configuration
```

## Key Documentation

Essential docs for understanding the project:

- **`README.md`** - Project overview, quick start, value proposition
- **`QUICKSTART.md`** - 5-minute tutorial (simplest examples)
- **`ROADMAP.md`** - PRIMARY ROADMAP - v0.3.0 → v1.0 development plan
- **`CRITICAL_GAPS_ANALYSIS.md`** - Strategic analysis of 10 gaps for v1.0
- **`spec/MAIN_SPEC.md`** - Complete specification (24,317 lines)
- **`USE_CASES.md`** - Real-world integrations (AI, manufacturing, science)
- **`FAQ.md`** - Common questions ("Why not PROV-O?", "Do I need blockchain?")
- **`STRATEGIC_CONTEXT.md`** - Big picture, adoption strategy, 5-year vision

## Important Patterns

### Selective Disclosure Levels

GenesisGraph supports three disclosure levels (see `examples/`):

1. **Level A (Full Disclosure)** - `level-a-full-disclosure.gg.yaml`
   - All parameters visible, complete workflow transparency
   - Use for: Internal audit, research collaboration

2. **Level B (Partial Envelope)** - `level-b-partial-envelope.gg.yaml`
   - Parameters redacted, policy claims visible
   - Use for: Regulatory compliance, limited IP exposure

3. **Level C (Sealed Subgraph)** - `level-c-sealed-subgraph.gg.yaml`
   - Entire pipeline segments hidden with Merkle commitments
   - Use for: Supply chain, high-value IP, multi-party trust

### Example Workflows

Notable examples in `examples/`:

- **`workflow-with-did-web.gg.yaml`** - Enterprise workflow with did:web identity
- **`sd-jwt-attestation.gg.yaml`** - Selective disclosure with SD-JWT
- **`bbs-plus-attestation.gg.yaml`** - Privacy-preserving BBS+ signatures
- **`zkp-ai-safety-attestation.gg.yaml`** - Zero-knowledge proof for AI safety
- **`zkp-manufacturing-qc-attestation.gg.yaml`** - ZK proof for manufacturing QC

## Common Development Tasks

### Adding New Features

1. Create module in appropriate location (`genesisgraph/`, `genesisgraph/credentials/`, etc.)
2. Write tests in `tests/` matching module structure
3. Run `pytest` to verify tests pass
4. Run `mypy genesisgraph` to check types
5. Run `black .` and `ruff check .` for formatting/linting

### Working with Cryptography

Core cryptographic operations are in:
- `genesisgraph/validator.py` - Ed25519 signature verification
- `genesisgraph/credentials/sd_jwt.py` - SD-JWT selective disclosure
- `genesisgraph/credentials/bbs_plus.py` - BBS+ signatures
- `genesisgraph/credentials/zkp_templates.py` - Zero-knowledge proofs
- `genesisgraph/transparency_log.py` - Merkle tree operations

### Working with DIDs

DID resolution is centralized in `genesisgraph/did_resolver.py`:
- Supports: did:key, did:web, did:ion, did:ethr
- SSRF protection, rate limiting, TLS validation for did:web
- Universal Resolver support for did:ion
- Multi-network support for did:ethr

## Working with Claude Code

When Claude Code is exploring the GenesisGraph codebase, it can use the Progressive Reveal CLI to:
- Quickly understand file structure without reading entire files
- Filter large configuration or data files for specific sections
- Get file metadata to make informed decisions about what to analyze
- Preview code structure before making modifications

This is especially useful for large files where full content might be overwhelming or unnecessary for the task at hand.

### Recommended Workflow for Claude

1. **Start with README.md** - Understand project purpose and value
2. **Check ROADMAP.md** - Understand current priorities and v1.0 goals
3. **Review relevant docs/** - For specific features (DID, transparency logs, profiles, etc.)
4. **Explore examples/** - See practical usage patterns
5. **Use Progressive Reveal CLI** - For large spec files or detailed exploration
6. **Run tests frequently** - `pytest` ensures changes don't break existing functionality
