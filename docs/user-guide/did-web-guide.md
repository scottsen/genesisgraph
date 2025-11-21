# did:web Support in GenesisGraph

## Overview

GenesisGraph now supports **did:web** for organization-level identities and integration with existing PKI infrastructure. This is critical for enterprise trust chains and enables organizations to use their existing domain infrastructure for identity management.

## What is did:web?

**did:web** is a DID (Decentralized Identifier) method that uses web domains to host DID documents. Unlike did:key (which embeds the public key in the identifier itself), did:web resolves identities via HTTPS.

### Format

```
did:web:example.com                    → https://example.com/.well-known/did.json
did:web:example.com:user:alice         → https://example.com/user/alice/did.json
did:web:hospital.example.com:dept:radiology → https://hospital.example.com/dept/radiology/did.json
```

### Key Benefits

1. **Organization-Level Identities**: Use your domain as a trust anchor
2. **Existing PKI Integration**: Leverage existing certificate infrastructure
3. **Key Rotation**: Update keys without changing the identifier
4. **Multi-Key Support**: Different keys for different purposes
5. **Enterprise Trust Chains**: Critical for regulated industries

## Quick Start

### 1. Create a DID Document

Create a file at `https://yourdomain.com/.well-known/did.json`:

```json
{
  "id": "did:web:yourdomain.com",
  "verificationMethod": [{
    "id": "did:web:yourdomain.com#keys-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:web:yourdomain.com",
    "publicKeyBase58": "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
  }],
  "authentication": ["#keys-1"],
  "assertionMethod": ["#keys-1"]
}
```

### 2. Use in GenesisGraph

```yaml
operations:
  - id: op_quality_check_001
    tool:
      name: visual_inspection
      version: 2.1.0
    attestation:
      signer: did:web:manufacturing.example.com
      signature: ed25519:sig_base64encodedvalue...
      timestamp: '2025-10-15T14:30:00Z'
```

### 3. Verify Signatures

```python
from genesisgraph.validator import GraphValidator

validator = GraphValidator(verify_signatures=True)
result = validator.validate_file('production.gg.yaml')

if result.is_valid:
    print("✓ Signature verified using did:web identity")
```

## DID Document Formats

GenesisGraph supports three public key formats in DID documents:

### Format 1: publicKeyBase58 (Recommended)

```json
{
  "id": "did:web:example.com",
  "verificationMethod": [{
    "id": "#keys-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:web:example.com",
    "publicKeyBase58": "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
  }]
}
```

### Format 2: publicKeyMultibase

```json
{
  "id": "did:web:example.com",
  "verificationMethod": [{
    "id": "#keys-1",
    "type": "Ed25519VerificationKey2018",
    "controller": "did:web:example.com",
    "publicKeyMultibase": "zH3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
  }]
}
```

### Format 3: publicKeyJwk (JSON Web Key)

```json
{
  "id": "did:web:example.com",
  "verificationMethod": [{
    "id": "#keys-1",
    "type": "JsonWebKey2020",
    "controller": "did:web:example.com",
    "publicKeyJwk": {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo"
    }
  }]
}
```

## Enterprise Use Cases

### 1. Manufacturing Quality Control

**Scenario**: Aerospace manufacturer with multiple facilities

```yaml
# production_batch_2024_q4.gg.yaml
operations:
  - id: op_final_inspection
    tool:
      name: cmm_inspection
      version: 5.2.1
    attestation:
      signer: did:web:facility-phoenix.aerospace.example.com
      signature: ed25519:sig_...
      timestamp: '2025-10-15T14:30:00Z'
      delegation: did:web:aerospace.example.com
```

**DID Document** at `https://facility-phoenix.aerospace.example.com/.well-known/did.json`:

```json
{
  "id": "did:web:facility-phoenix.aerospace.example.com",
  "verificationMethod": [
    {
      "id": "#qc-signing-key",
      "type": "Ed25519VerificationKey2020",
      "controller": "did:web:facility-phoenix.aerospace.example.com",
      "publicKeyBase58": "QCKeyBase58EncodedValue..."
    },
    {
      "id": "#admin-key",
      "type": "Ed25519VerificationKey2020",
      "controller": "did:web:facility-phoenix.aerospace.example.com",
      "publicKeyBase58": "AdminKeyBase58EncodedValue..."
    }
  ],
  "authentication": ["#admin-key"],
  "assertionMethod": ["#qc-signing-key"]
}
```

### 2. Hospital System Medical AI

**Scenario**: Multi-hospital system with centralized AI governance

```yaml
# patient_qa_workflow.gg.yaml
operations:
  - id: op_inference_001
    tool:
      name: llama3-70b-instruct
      version: 1.0
    attestation:
      signer: did:web:ai.hospital-system.example.com
      signature: ed25519:sig_...
      timestamp: '2025-10-15T14:30:00Z'

  - id: op_human_review
    tool:
      name: human_reviewer
    attestation:
      signer: did:web:hospital-west.example.com:staff:dr_chen
      signature: ed25519:sig_...
      timestamp: '2025-10-15T14:32:00Z'
      delegation: did:web:hospital-west.example.com
```

### 3. Research Lab Data Integrity

**Scenario**: University research lab publishing verifiable datasets

```yaml
# experiment_2024_genomics.gg.yaml
operations:
  - id: op_sequencing
    tool:
      name: illumina_novaseq
      version: 6000
    attestation:
      signer: did:web:genomics.university.edu:lab:protein-folding
      signature: ed25519:sig_...
      timestamp: '2025-10-15T14:30:00Z'
```

## Security Features

GenesisGraph's did:web resolver includes comprehensive security protections:

### 1. SSRF Protection

Blocks resolution to private/internal networks:
- ✓ Blocks localhost, 127.0.0.1, private IPs
- ✓ Blocks AWS metadata service (169.254.169.254)
- ✓ Blocks private network ranges (10.0.0.0/8, 192.168.0.0/16, 172.16.0.0/12)
- ✓ Blocks IPv6 localhost and link-local addresses

```python
# These will be rejected:
resolver.resolve_to_public_key('did:web:localhost')
resolver.resolve_to_public_key('did:web:192.168.1.1')
resolver.resolve_to_public_key('did:web:169.254.169.254')
```

### 2. TLS Certificate Validation

All did:web resolutions **require valid TLS certificates**:
- ✓ HTTPS-only (no HTTP fallback)
- ✓ Certificate verification enabled
- ✓ No redirects allowed (prevents SSRF)

### 3. Rate Limiting

Per-domain rate limiting to prevent abuse:
- Default: 10 requests per minute per domain
- Configurable: `DIDResolver(rate_limit=20)`

```python
resolver = DIDResolver(rate_limit=10)  # 10 req/min per domain
```

### 4. Content Validation

Strict validation of responses:
- ✓ Content-Type must be `application/json` or `application/did+json`
- ✓ Response size limit: 1MB maximum
- ✓ Valid JSON structure required

### 5. Caching with TTL

Results are cached to reduce network calls:
- Default TTL: 300 seconds (5 minutes)
- Configurable: `DIDResolver(cache_ttl=600)`

```python
resolver = DIDResolver(cache_ttl=600)  # 10 minute cache
```

## API Reference

### DIDResolver

```python
from genesisgraph.did_resolver import DIDResolver

# Create resolver
resolver = DIDResolver(
    timeout=10,        # HTTP timeout in seconds
    cache_ttl=300,     # Cache TTL in seconds
    rate_limit=10      # Max requests per minute per domain
)

# Resolve DID to public key
public_key = resolver.resolve_to_public_key(
    did='did:web:example.com',
    key_id='#keys-1'  # Optional, defaults to '#keys-1'
)

# Clear cache
resolver.clear_cache()
```

### Convenience Function

```python
from genesisgraph.did_resolver import resolve_did_to_public_key

# One-shot resolution
public_key = resolve_did_to_public_key('did:web:example.com')
```

### Integration with GraphValidator

```python
from genesisgraph.validator import GraphValidator

# Validator automatically uses DIDResolver
validator = GraphValidator(verify_signatures=True)

# Validates signatures using both did:key and did:web
result = validator.validate_file('workflow.gg.yaml')

if result.is_valid:
    print("✓ All signatures verified")
else:
    for error in result.errors:
        print(f"✗ {error}")
```

## Generating Ed25519 Keys

### Using Python (ed25519 library)

```python
import ed25519
import base58

# Generate new key pair
signing_key, verifying_key = ed25519.create_keypair()

# Export public key as base58
public_key_bytes = verifying_key.to_bytes()
public_key_base58 = base58.b58encode(public_key_bytes).decode()

print(f"Public Key (base58): {public_key_base58}")
print(f"Use in DID document: publicKeyBase58: {public_key_base58}")

# Save private key securely
with open('signing_key.pem', 'wb') as f:
    f.write(signing_key.to_bytes())
```

### Using OpenSSL

```bash
# Generate Ed25519 private key
openssl genpkey -algorithm ED25519 -out private_key.pem

# Extract public key
openssl pkey -in private_key.pem -pubout -out public_key.pem

# Convert to raw bytes (32 bytes) and base58 encode
# (requires additional tooling)
```

## Migration from did:key

If you're currently using did:key, migration is straightforward:

### Before (did:key)

```yaml
attestation:
  signer: did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK
  signature: ed25519:sig_...
```

### After (did:web)

1. Create DID document at your domain
2. Update GenesisGraph files:

```yaml
attestation:
  signer: did:web:yourdomain.com
  signature: ed25519:sig_...
```

### Key Advantages

- **Key Rotation**: Update keys without changing references
- **Multiple Keys**: Different keys for different purposes
- **Organizational Identity**: Clear association with your domain
- **Compliance**: Better for regulated industries

## Testing

Run the did:web integration tests:

```bash
# Run all did:web tests
python -m pytest tests/test_did_web_integration.py -v

# Run specific test
python -m pytest tests/test_did_web_integration.py::TestDIDWebIntegration::test_resolve_did_web_with_base58_key -v

# Run security tests
python -m pytest tests/test_security.py -k "web" -v
```

## Troubleshooting

### Error: "Failed to fetch did:web document"

**Cause**: Network issue, invalid domain, or missing DID document

**Solution**:
1. Verify DID document is accessible: `curl https://yourdomain.com/.well-known/did.json`
2. Check HTTPS certificate is valid
3. Verify Content-Type header is `application/json` or `application/did+json`

### Error: "Blocked host in did:web for security reasons"

**Cause**: Attempting to resolve to a private/internal address

**Solution**: Only use public domains for did:web. For testing, use public test domains or mock the resolver.

### Error: "Rate limit exceeded"

**Cause**: Too many requests to the same domain

**Solution**: Increase rate limit or wait:
```python
resolver = DIDResolver(rate_limit=20)  # Increase limit
```

### Error: "Unsupported key type"

**Cause**: DID document contains non-Ed25519 key

**Solution**: GenesisGraph currently only supports Ed25519. Ensure your DID document uses:
- `type: "Ed25519VerificationKey2020"` or
- `type: "Ed25519VerificationKey2018"` or
- `type: "JsonWebKey2020"` with `kty: "OKP"`, `crv: "Ed25519"`

## Best Practices

### 1. Use Separate Keys for Different Purposes

```json
{
  "verificationMethod": [
    {
      "id": "#signing-key",
      "type": "Ed25519VerificationKey2020",
      "publicKeyBase58": "..."
    },
    {
      "id": "#authentication-key",
      "type": "Ed25519VerificationKey2020",
      "publicKeyBase58": "..."
    }
  ],
  "assertionMethod": ["#signing-key"],
  "authentication": ["#authentication-key"]
}
```

### 2. Implement Key Rotation

Update your DID document periodically:
- Add new key to `verificationMethod`
- Transition signing to new key
- Keep old key for verification of historical signatures
- Remove old key after grace period

### 3. Use Subdomain Structure for Organizations

```
did:web:aerospace.example.com                    # Root org
did:web:facility-phoenix.aerospace.example.com   # Facility
did:web:facility-phoenix.aerospace.example.com:qc  # Department
```

### 4. Include Service Endpoints

```json
{
  "id": "did:web:example.com",
  "verificationMethod": [...],
  "service": [{
    "id": "#provenance-api",
    "type": "GenesisGraphAPI",
    "serviceEndpoint": "https://api.example.com/provenance/v1"
  }]
}
```

### 5. Monitor DID Resolution

- Set up monitoring for DID document availability
- Use CDN for high-availability
- Implement backup resolution methods

## Specification References

- [W3C DID Core Specification](https://www.w3.org/TR/did-core/)
- [did:web Method Specification](https://w3c-ccg.github.io/did-method-web/)
- [Ed25519 Verification Key 2020](https://w3c-ccg.github.io/lds-ed25519-2020/)
- [JSON Web Key (JWK) RFC 7517](https://tools.ietf.org/html/rfc7517)

## Support

For questions or issues:
- GitHub Issues: https://github.com/yourusername/genesisgraph/issues
- Documentation: https://genesisgraph.dev/docs
- Security: security@genesisgraph.dev
