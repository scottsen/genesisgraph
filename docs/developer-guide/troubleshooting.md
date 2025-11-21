# Troubleshooting Guide

This guide covers common issues and solutions when using GenesisGraph.

## Installation Issues

### Python Version Compatibility

**Problem:** `ERROR: Package requires a different Python`

**Solution:**
```bash
# Check your Python version
python --version

# GenesisGraph requires Python 3.8+
# Upgrade if needed or use a virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install genesisgraph
```

### Dependency Conflicts

**Problem:** `ERROR: Cannot install genesisgraph due to conflicting dependencies`

**Solution:**
```bash
# Create a fresh virtual environment
python -m venv fresh_venv
source fresh_venv/bin/activate
pip install --upgrade pip
pip install genesisgraph
```

### Platform-Specific Issues

#### Windows

**Problem:** `'gg' is not recognized as an internal or external command`

**Solution:**
```bash
# Ensure Scripts directory is in PATH
python -m genesisgraph.cli validate workflow.gg.yaml

# Or use full path
C:\Users\YourName\venv\Scripts\gg validate workflow.gg.yaml
```

#### macOS

**Problem:** `cryptography` installation fails with OpenSSL errors

**Solution:**
```bash
# Install OpenSSL via Homebrew
brew install openssl

# Set environment variables
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
pip install genesisgraph
```

#### Linux

**Problem:** `cryptography` requires Rust compiler

**Solution:**
```bash
# Install build dependencies
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
pip install genesisgraph
```

## Validation Errors

### "entities must be a list"

**Problem:** YAML structure is incorrect

**Bad:**
```yaml
entities:
  my_file:
    type: File
```

**Good:**
```yaml
entities:
  - id: my_file
    type: File
```

### "Invalid hash format"

**Problem:** Hash not in `algorithm:hexdigest` format

**Bad:**
```yaml
hash: abc123def456
```

**Good:**
```yaml
hash: sha256:abc123def456789...
```

**Supported algorithms:**
- `sha256` (recommended)
- `sha512` (for extra security)
- `blake3` (requires optional dependency)

### "File not found"

**Problem:** Relative file paths not resolved correctly

**Solution:**
```yaml
# Use paths relative to the .gg.yaml file location
entities:
  - id: my_data
    type: Dataset
    version: "1"
    file: ./data/input.csv  # Relative to document directory
    hash: sha256:...
```

**Security note:** Absolute paths and parent directory references (`..`) are blocked for security.

### "Schema validation failed"

**Problem:** Document doesn't match JSON Schema

**Common causes:**
1. Missing required fields (`spec_version`, `id`, `type`, `version`)
2. Wrong field types (e.g., string instead of list)
3. Invalid enum values (e.g., wrong `mode` in attestation)

**Solution:**
```bash
# Enable schema validation with detailed errors
gg validate workflow.gg.yaml --schema
```

## CLI Issues

### Command not found

**Problem:** `gg: command not found`

**Solution:**
```bash
# Option 1: Reinstall with pip user install
pip install --user genesisgraph

# Option 2: Use as module
python -m genesisgraph.cli validate workflow.gg.yaml

# Option 3: Check PATH
echo $PATH
# Add to PATH if needed (Linux/macOS):
export PATH="$HOME/.local/bin:$PATH"
```

### Click not installed (fallback mode)

**Problem:** `Click library not available - using fallback CLI`

**Impact:** Basic CLI works but without rich formatting

**Solution:**
```bash
# Install CLI extras
pip install genesisgraph[cli]
```

### Unicode errors in output

**Problem:** `UnicodeEncodeError` when displaying validation results

**Solution:**
```bash
# Set UTF-8 encoding (Linux/macOS)
export PYTHONIOENCODING=utf-8

# Windows (PowerShell)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## Signature Verification Issues

### "cryptography library not available"

**Problem:** Signature verification requires cryptography library

**Solution:**
```bash
# Install with all dependencies
pip install genesisgraph

# Or explicitly
pip install cryptography
```

### "Failed to resolve signer DID"

**Problem:** DID can't be resolved to public key

**Common causes:**
1. Invalid DID format
2. DID method not supported (only `did:key`, `did:web`, `did:ion`, `did:ethr` supported)
3. Network issues (for `did:web`)

**Solution:**
```bash
# Verify DID format
# Good: did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK
# Bad: did:example:invalid

# For did:web, ensure domain is accessible
curl https://example.com/.well-known/did.json

# Test with mock signature for development
attestation:
  mode: signed
  signer: did:key:test
  signature: ed25519:mock:test_signature
```

### "Signature verification failed"

**Problem:** Signature doesn't match the data

**Common causes:**
1. Data was modified after signing
2. Wrong public key
3. Incorrect canonical JSON representation

**Solution:**
```bash
# Verify the data hasn't been modified
# Re-sign with correct key
# Ensure canonical JSON matches (check with --debug)
```

## Performance Issues

### Large file validation slow

**Problem:** Validation takes minutes for large documents

**Solution:**
```bash
# Disable hash verification for initial testing
# (Note: This reduces security guarantees)

# Optimize by:
# 1. Reducing number of entities
# 2. Using URI references instead of file paths
# 3. Disabling signature verification during development
```

### Memory usage high

**Problem:** Python process uses excessive memory

**Solution:**
```yaml
# Break large workflows into smaller documents
# Use references between documents

# Document 1: preprocessing.gg.yaml
entities:
  - id: raw_data
    ...

# Document 2: inference.gg.yaml  
entities:
  - id: processed_data
    derived_from: raw_data@preprocessing.gg.yaml
```

## Debug Mode

### Enable debug logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from genesisgraph import GenesisGraphValidator
validator = GenesisGraphValidator()
```

### Verbose output

```bash
# More detailed error messages
gg validate workflow.gg.yaml --verbose

# Show warnings
gg validate workflow.gg.yaml --warnings
```

## Profile Validation Issues

### "Profile validation failed"

**Problem:** Document doesn't meet industry-specific profile requirements

**Solution:**
```bash
# Check which profile is being validated
gg validate workflow.gg.yaml --verify-profile --verbose

# Explicitly specify profile
gg validate workflow.gg.yaml --verify-profile --profile gg-ai-basic-v1

# See profile requirements
cat docs/PROFILE_VALIDATORS.md
```

## Transparency Log Issues

### "Transparency log verification not available"

**Problem:** Transparency log module not imported

**Solution:**
```bash
# Ensure full installation
pip install genesisgraph

# Check import
python -c "from genesisgraph.transparency_log import TransparencyLogVerifier"
```

### "Inclusion proof verification failed"

**Problem:** RFC 6962 Merkle proof doesn't verify

**Common causes:**
1. Proof is outdated (tree has grown)
2. Leaf data doesn't match
3. Tree size mismatch

**Solution:**
```bash
# Re-fetch fresh inclusion proof from log
# Verify canonical JSON representation matches
# Check tree_size is consistent
```

## Common Workarounds

### Skip hash verification (development only)

```python
from genesisgraph import GenesisGraphValidator

validator = GenesisGraphValidator()
# Don't pass file_path to skip hash verification
result = validator.validate(data)  # No file_path parameter
```

### Use mock signatures for testing

```yaml
attestation:
  mode: signed
  signer: did:key:mock
  signature: ed25519:mock:test_sig_abc123
  timestamp: "2025-11-20T12:00:00Z"
```

### Disable schema validation

```python
validator = GenesisGraphValidator(use_schema=False)
result = validator.validate_file("workflow.gg.yaml")
```

## Getting Help

### Check documentation

- **Quickstart:** [QUICKSTART.md](../../QUICKSTART.md)
- **Specification:** [spec/MAIN_SPEC.md](../../spec/MAIN_SPEC.md)
- **FAQ:** [FAQ.md](../../FAQ.md)

### Community support

- **GitHub Issues:** https://github.com/scottsen/genesisgraph/issues
- **Discussions:** https://github.com/scottsen/genesisgraph/discussions

### Report bugs

Include:
1. GenesisGraph version (`pip show genesisgraph`)
2. Python version (`python --version`)
3. Operating system
4. Minimal reproducible example
5. Full error message

```bash
# Get version info
pip show genesisgraph
python --version
uname -a  # Linux/macOS
# or
systeminfo  # Windows
```

## Known Limitations

### Not yet implemented

- Blake3 hash support (requires optional dependency)
- ECDSA and RSA signature algorithms (only Ed25519 supported)
- did:ethr full resolution (partial support via Universal Resolver)
- Zero-knowledge proof verification (templates provided, verification coming in v0.4)

### Performance

- Hash verification on large files (>1GB) may be slow
- Recursive subgraph validation not optimized
- No parallel validation of multiple documents

### Platform support

- Windows: Limited testing, some path issues
- ARM64: Cryptography compilation may require additional steps

---

**Last updated:** 2025-11-20
**Applies to:** GenesisGraph v0.3.0+
