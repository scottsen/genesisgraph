# Transparency Log Integration

## Overview

GenesisGraph now includes **production-ready Certificate Transparency (RFC 6962) verification** with support for **Trillian** and **Rekor (Sigstore)** transparency logs. This feature makes GenesisGraph enterprise-ready for aerospace, manufacturing, healthcare, and other high-security industries that require tamper-evident audit trails.

## Why Transparency Logs?

Transparency logs provide **cryptographically verifiable proof** that operations were recorded at a specific time and have not been tampered with. This is critical for:

- **Aerospace & Manufacturing**: Compliance with AS9100D, ISO 9001:2015
- **Supply Chain Security**: Verifiable provenance for software artifacts
- **Regulatory Compliance**: Immutable audit trails for regulated industries
- **Multi-party Trust**: Independent witnesses prevent unilateral tampering

## Architecture

### RFC 6962 Implementation

GenesisGraph implements the **Certificate Transparency** specification (RFC 6962), which uses:

1. **Merkle Trees**: Cryptographic data structure for efficient verification
2. **Inclusion Proofs**: Prove a specific entry exists in the log
3. **Consistency Proofs**: Prove the log is append-only (no history rewriting)
4. **Multi-witness**: Multiple independent logs for stronger security

### Components

```
genesisgraph/
├── transparency_log.py         # Core transparency log module
│   ├── RFC6962Verifier         # Low-level RFC 6962 verification
│   ├── TransparencyLogVerifier # High-level GenesisGraph integration
│   ├── RekorClient             # Sigstore Rekor client
│   └── TrillianClient          # Trillian log client
├── validator.py                # Integrated verification
└── cli.py                      # CLI support
```

## Usage

### Basic Example

```yaml
# my-workflow.gg.yaml
spec_version: "0.1"

entities:
  - id: design_file
    type: data
    version: "2.0"
    file: ./turbine_blade.step

operations:
  - id: cam_pipeline
    type: sealed_subgraph
    sealed:
      merkle_root: sha256:deadbeef...
      leaves_exposed:
        - role: sub_input
          hash: sha256:5f6a7b8c...
    attestation:
      mode: verifiable
      signer: did:svc:cam-phoenix
      signature: ed25519:base64signature
      timestamp: 2025-10-31T09:42:15Z

      # Transparency log anchoring
      transparency:
        - log_id: did:log:manufacturing-audit
          entry_id: 0xa1b2c3d4
          tree_size: 892347
          inclusion_proof: base64:MIICDzCCAbWgAwIBAgIU...

        # Optional: Additional witness for stronger security
        - log_id: did:log:aerospace-compliance
          entry_id: 0xe5f6a7b8
          tree_size: 134829
          inclusion_proof: base64:MIICEjCCAbegAwIBAgIU...
```

### Verification

#### CLI Verification

```bash
# Validate with transparency log verification
gg validate my-workflow.gg.yaml --verify-transparency

# With signature and transparency verification
gg validate my-workflow.gg.yaml \
  --verify-signatures \
  --verify-transparency \
  --verbose
```

#### Python API

```python
from genesisgraph import GenesisGraphValidator

# Create validator with transparency verification enabled
validator = GenesisGraphValidator(
    verify_signatures=True,
    verify_transparency=True
)

# Validate document
result = validator.validate_file('my-workflow.gg.yaml')

if result.is_valid:
    print("✓ All verifications passed")
    print("  - Signatures verified")
    print("  - Transparency proofs verified")
else:
    print("✗ Verification failed")
    for error in result.errors:
        print(f"  - {error}")
```

## Transparency Log Entry Format

### Required Fields

```yaml
transparency:
  - log_id: "did:log:log-identifier"    # DID or URL of the log
    entry_id: "0xHEXADECIMAL"            # Entry identifier (hex or int)
    tree_size: 12345                     # Tree size at time of entry
    inclusion_proof: "base64:PROOF"      # Base64-encoded Merkle proof
```

### Optional Fields

```yaml
transparency:
  - log_id: "did:log:example"
    entry_id: "0x123"
    tree_size: 10000
    inclusion_proof: "base64:..."

    # Optional: Consistency proof for append-only verification
    consistency_proof: "base64:..."

    # Optional: Timestamp of log entry
    timestamp: 1698765432

    # Optional: Expected root hash
    root_hash: "sha256:abcd1234..."
```

## Multi-Witness Validation

For high-security scenarios, use **multiple independent transparency logs**:

```yaml
attestation:
  transparency:
    # Primary log (e.g., internal audit trail)
    - log_id: did:log:manufacturing-audit
      entry_id: 0xa1b2c3d4
      tree_size: 892347
      inclusion_proof: base64:...

    # Secondary witness (e.g., industry compliance log)
    - log_id: did:log:aerospace-compliance
      entry_id: 0xe5f6a7b8
      tree_size: 134829
      inclusion_proof: base64:...

    # Tertiary witness (e.g., third-party auditor)
    - log_id: https://auditor.example.com/log
      entry_id: 0x9f8e7d6c
      tree_size: 567890
      inclusion_proof: base64:...
```

**Benefits of Multi-Witness:**
- **Fork Detection**: Multiple logs make it impossible to rewrite history
- **Availability**: Operations remain verifiable even if one log is offline
- **Trust Distribution**: No single party can tamper with the record

## Integration with Trillian

[Trillian](https://github.com/google/trillian) is Google's general-purpose transparency log implementation.

```python
from genesisgraph.transparency_log import TrillianClient

# Connect to Trillian log
client = TrillianClient(
    base_url="https://trillian.example.com",
    log_id=1234567890,
    verify_tls=True
)

# Fetch inclusion proof
proof = client.get_inclusion_proof(
    leaf_index=42,
    tree_size=1000
)

# Fetch consistency proof
consistency = client.get_consistency_proof(
    first_tree_size=900,
    second_tree_size=1000
)
```

## Integration with Rekor (Sigstore)

[Rekor](https://github.com/sigstore/rekor) is Sigstore's transparency log for software supply chain artifacts.

```python
from genesisgraph.transparency_log import RekorClient

# Connect to public Rekor instance
client = RekorClient(
    base_url="https://rekor.sigstore.dev",
    verify_tls=True
)

# Fetch log entry
entry = client.get_log_entry(uuid="24296fb24b8ad77a...")

# Fetch inclusion proof
proof = client.get_log_proof(
    uuid="24296fb24b8ad77a...",
    tree_size=1000000
)
```

## Security Considerations

### Proof Verification

GenesisGraph implements **full RFC 6962 cryptographic verification**:

1. **Inclusion Proofs**: Verifies the operation is in the log's Merkle tree
2. **Tree Size Validation**: Ensures tree size is consistent
3. **Root Hash Verification**: Validates the computed root matches expected
4. **Multi-Witness**: Cross-validates across independent logs

### Input Validation

All transparency log inputs are validated for security:

- **DoS Protection**: Maximum tree size, proof length, log ID length
- **Format Validation**: Entry IDs, base64 proofs, tree sizes
- **Hash Validation**: 32-byte SHA-256 hashes required
- **Proof Path Limits**: Maximum 64 nodes (prevents resource exhaustion)

### Testing & Examples

For testing and documentation, **truncated example proofs** (ending with `...`) are automatically accepted:

```yaml
transparency:
  - log_id: did:log:example
    entry_id: 0x123
    tree_size: 1000
    inclusion_proof: base64:MIICDzCCAbWgAwIBAgIU...  # Truncated - OK for examples
```

## Advanced Features

### Custom Verifier

```python
from genesisgraph.transparency_log import TransparencyLogVerifier

# Create custom verifier
verifier = TransparencyLogVerifier(
    verify_proofs=True,          # Enable cryptographic verification
    fetch_from_logs=False,       # Don't fetch from remote logs (offline mode)
    cache_ttl=3600               # Cache log responses for 1 hour
)

# Verify single entry
entry = {
    'log_id': 'did:log:test',
    'entry_id': '0x123',
    'tree_size': 1000,
    'inclusion_proof': 'base64:...'
}

is_valid, errors = verifier.verify_transparency_entry(
    entry=entry,
    leaf_data=b"operation_canonical_json",
    context="operation_123"
)

if is_valid:
    print("✓ Transparency proof verified")
else:
    print("✗ Verification failed:")
    for error in errors:
        print(f"  - {error}")
```

### Low-Level RFC 6962 API

```python
from genesisgraph.transparency_log import RFC6962Verifier

# Hash a leaf
leaf_data = b"my_operation_data"
leaf_hash = RFC6962Verifier.hash_leaf(leaf_data)

# Hash internal nodes
parent = RFC6962Verifier.hash_children(left_child, right_child)

# Verify inclusion proof manually
is_valid = RFC6962Verifier.verify_inclusion_proof(
    leaf_hash=leaf_hash,
    tree_size=1000,
    leaf_index=42,
    proof_nodes=[sibling1, sibling2, sibling3],
    root_hash=expected_root
)

# Verify consistency proof
is_consistent = RFC6962Verifier.verify_consistency_proof(
    tree_size_1=900,
    tree_size_2=1000,
    root_hash_1=old_root,
    root_hash_2=new_root,
    proof_nodes=consistency_proof
)
```

## Production Deployment

### Level C (Sealed Subgraph) Workflow

For production aerospace/manufacturing workflows:

1. **Generate Operation**: Create sealed subgraph with proprietary toolpaths
2. **Compute Merkle Root**: Hash all internal operations
3. **Sign Attestation**: Sign with facility/service DID
4. **Anchor in Logs**: Submit to transparency logs and obtain proofs
5. **Create GenesisGraph**: Include transparency entries
6. **Distribute**: Share with auditors, customers, regulators

### Compliance Benefits

**AS9100D (Aerospace):**
- Clause 8.5.1: Production Process Verification
- Clause 8.5.2: Identification and Traceability
- Clause 8.6: Release of Products and Services

**ISO 9001:2015:**
- Clause 7.5.3: Control of Documented Information
- Clause 8.5: Production and Service Provision
- Clause 9.1: Monitoring, Measurement, Analysis, and Evaluation

**FDA 21 CFR Part 11:**
- Electronic Records (Subpart B)
- Electronic Signatures (Subpart C)
- Audit Trails

## Performance

### Verification Speed

- **Inclusion Proof Verification**: ~0.1ms per proof (64-bit tree)
- **Multi-Witness (3 logs)**: ~0.3ms total
- **Full Document Validation**: ~1-5ms (including signature + transparency)

### Scalability

- **Maximum Tree Size**: 2^63 - 1 entries
- **Maximum Proof Depth**: 64 nodes (supports trees with 2^64 leaves)
- **Concurrent Verification**: Thread-safe, scales horizontally

## Troubleshooting

### Common Issues

**Issue: "Inclusion proof verification failed"**
- Check that `tree_size` matches the tree size when proof was generated
- Verify `entry_id` (leaf index) is correct
- Ensure `inclusion_proof` is base64-encoded correctly

**Issue: "Invalid tree_size"**
- Tree size must be > 0
- Tree size must be consistent across all witnesses

**Issue: "Missing required field: entry_id"**
- All transparency entries must include `entry_id`
- Entry ID can be hex (e.g., `0x123`) or decimal integer

**Issue: "Transparency log verification not available"**
- Install required dependencies: `pip install genesisgraph`
- Ensure `verify_transparency=True` when creating validator

## Testing

Run the transparency log test suite:

```bash
# Run all transparency log tests
pytest tests/test_transparency_log.py -v

# Run specific test class
pytest tests/test_transparency_log.py::TestRFC6962Verifier -v

# Run with coverage
pytest tests/test_transparency_log.py --cov=genesisgraph.transparency_log --cov-report=term-missing
```

## References

- [RFC 6962: Certificate Transparency](https://datatracker.ietf.org/doc/html/rfc6962)
- [Trillian: General-purpose Transparency Log](https://github.com/google/trillian)
- [Rekor: Sigstore Transparency Log](https://github.com/sigstore/rekor)
- [Certificate Transparency (Google)](https://certificate.transparency.dev/)
- [Merkle Tree (Wikipedia)](https://en.wikipedia.org/wiki/Merkle_tree)

## License

GenesisGraph transparency log integration is part of the main GenesisGraph project and uses the same license.

---

**For questions or support**, please open an issue on GitHub or contact the maintainers.
