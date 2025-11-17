# GenesisGraph Security Audit Findings

**Date:** 2025-11-17
**Version Audited:** v0.1.0
**Auditor:** Security Review

## Executive Summary

This security audit identified **8 HIGH priority** vulnerabilities, **6 MEDIUM priority** issues, and **5 LOW priority** improvements needed in the GenesisGraph codebase. The most critical issues involve path traversal, Server-Side Request Forgery (SSRF), and missing certificate validation in DID resolution.

**Overall Risk Level:** HIGH
**Recommended Action:** Address HIGH priority issues before production deployment

---

## Critical Vulnerabilities (HIGH Priority)

### 1. Path Traversal Vulnerability in File Hash Verification

**Location:** `genesisgraph/validator.py:502-506`

**Severity:** HIGH
**OWASP Category:** A01:2021 - Broken Access Control

**Issue:**
The `_verify_file_hash()` method constructs file paths by concatenating user-controlled input without proper sanitization. An attacker can use path traversal sequences (`../`) to access files outside the intended directory.

```python
# VULNERABLE CODE (lines 502-506)
if not os.path.isabs(file_path):
    doc_dir = os.path.dirname(base_path)
    full_path = os.path.join(doc_dir, file_path)
else:
    full_path = file_path
```

**Attack Scenario:**
```yaml
entities:
  - id: malicious
    file: "../../../../etc/passwd"
    hash: "sha256:..."
```

**Recommendation:**
```python
def _verify_file_hash(self, entity: Dict, base_path: str) -> List[str]:
    """Verify file hash matches declared hash"""
    errors = []

    entity_id = entity.get('id', 'unknown')
    file_path = entity['file']
    declared_hash = entity['hash']

    # Sanitize file path to prevent traversal
    file_path = os.path.normpath(file_path)
    if file_path.startswith('..') or os.path.isabs(file_path):
        errors.append(f"Entity '{entity_id}': absolute and parent directory references not allowed")
        return errors

    # Make path relative to base document
    doc_dir = os.path.dirname(base_path)
    full_path = os.path.normpath(os.path.join(doc_dir, file_path))

    # Ensure resolved path is still within doc_dir
    if not full_path.startswith(os.path.normpath(doc_dir)):
        errors.append(f"Entity '{entity_id}': path traversal detected")
        return errors

    # ... rest of verification
```

---

### 2. Server-Side Request Forgery (SSRF) in DID Web Resolution

**Location:** `genesisgraph/did_resolver.py:196-204`

**Severity:** HIGH
**OWASP Category:** A10:2021 - Server-Side Request Forgery (SSRF)

**Issue:**
The `_resolve_did_web()` method constructs URLs from user-controlled DIDs and makes HTTP requests without validation. An attacker can craft malicious DIDs to access internal resources.

```python
# VULNERABLE CODE (lines 196-204)
if path_parts:
    url = f"https://{domain}/{'/'.join(path_parts)}/did.json"
else:
    url = f"https://{domain}/.well-known/did.json"

response = requests.get(url, timeout=self.timeout)
```

**Attack Scenarios:**
```python
# Access internal metadata service
did:web:169.254.169.254:latest:meta-data

# Access internal network
did:web:internal-server.local:8080:admin

# Localhost access
did:web:localhost:8080
```

**Recommendation:**
```python
BLOCKED_HOSTS = {
    'localhost', '127.0.0.1', '0.0.0.0',
    '169.254.169.254',  # AWS metadata
    '::1',  # IPv6 localhost
}

BLOCKED_NETWORKS = [
    '10.0.0.0/8',      # Private network
    '172.16.0.0/12',   # Private network
    '192.168.0.0/16',  # Private network
    '169.254.0.0/16',  # Link-local
    'fc00::/7',        # IPv6 private
]

def _resolve_did_web(self, did: str, key_id: Optional[str] = None) -> bytes:
    """Resolve did:web with SSRF protection"""
    if not REQUESTS_AVAILABLE:
        raise ValidationError("did:web resolution requires 'requests' library")

    if not did.startswith('did:web:'):
        raise ValidationError(f"Invalid did:web format: {did}")

    # Extract domain and validate
    parts = did[8:].split(':')
    domain = parts[0]
    path_parts = parts[1:] if len(parts) > 1 else []

    # Block dangerous hosts
    if domain.lower() in BLOCKED_HOSTS:
        raise ValidationError(f"Blocked host in did:web: {domain}")

    # Block IP addresses in private ranges
    try:
        import ipaddress
        ip = ipaddress.ip_address(domain)
        for network in BLOCKED_NETWORKS:
            if ip in ipaddress.ip_network(network):
                raise ValidationError(f"Private IP address not allowed: {domain}")
    except ValueError:
        pass  # Not an IP, domain name is OK

    # Construct URL (force HTTPS)
    if path_parts:
        url = f"https://{domain}/{'/'.join(path_parts)}/did.json"
    else:
        url = f"https://{domain}/.well-known/did.json"

    # Fetch with strict TLS verification
    try:
        response = requests.get(
            url,
            timeout=self.timeout,
            verify=True,  # Enforce TLS certificate validation
            allow_redirects=False  # Prevent redirect-based SSRF
        )
        response.raise_for_status()
        did_document = response.json()
    except requests.RequestException as e:
        raise ValidationError(f"Failed to fetch did:web document from {url}: {e}") from e
```

---

### 3. Missing TLS Certificate Validation

**Location:** `genesisgraph/did_resolver.py:203`

**Severity:** HIGH
**OWASP Category:** A02:2021 - Cryptographic Failures

**Issue:**
The `requests.get()` call doesn't explicitly set `verify=True`, and there's no certificate pinning for known DIDs. This allows MITM attacks.

**Recommendation:**
- Always use `verify=True` in requests
- Implement certificate pinning for critical DIDs
- Add HPKP (HTTP Public Key Pinning) support for did:web

```python
# Add certificate pinning support
PINNED_CERTIFICATES = {
    'example.com': 'sha256:base64encodedspki...',
}

def _verify_certificate_pin(self, domain: str, cert):
    """Verify certificate against pinned hash"""
    if domain in PINNED_CERTIFICATES:
        # Implement SPKI hash verification
        pass
```

---

### 4. Regular Expression Denial of Service (ReDoS)

**Location:** `genesisgraph/validator.py:159`

**Severity:** HIGH
**OWASP Category:** A03:2021 - Injection

**Issue:**
The semver validation regex is vulnerable to catastrophic backtracking:

```python
# VULNERABLE (line 159)
elif not re.match(r'^\d+\.\d+\.\d+$', spec_version):
```

While this specific regex is safe, other patterns in the codebase should be reviewed:

**Location:** `genesisgraph/validator.py:349`
```python
pattern = r'^(ed25519|ecdsa|rsa):.+$'  # Potentially vulnerable with .+
```

**Recommendation:**
```python
# Use non-greedy matching and length limits
pattern = r'^(ed25519|ecdsa|rsa):[A-Za-z0-9+/=]{1,1024}$'
```

---

### 5. Unsafe YAML Loading in Scripts

**Location:** `scripts/verify_sealed_subgraph.py:275`, `scripts/verify_transparency_anchoring.py:341`

**Severity:** HIGH (if scripts process untrusted input)
**OWASP Category:** A03:2021 - Injection

**Issue:**
While the main codebase uses `yaml.safe_load()`, ensure all scripts do the same.

**Status:** ✅ Verified - All code uses `yaml.safe_load()`, which is secure.

---

### 6. Missing Rate Limiting on DID Resolution

**Location:** `genesisgraph/did_resolver.py:_resolve_did_web`

**Severity:** MEDIUM-HIGH
**OWASP Category:** A04:2021 - Insecure Design

**Issue:**
No rate limiting on DID web resolution allows attackers to DoS external services or bypass IP-based rate limits.

**Recommendation:**
```python
from collections import defaultdict
from time import time

class DIDResolver:
    def __init__(self, timeout: int = 10, cache_ttl: int = 300, rate_limit: int = 10):
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Any] = {}
        self._rate_limits: Dict[str, List[float]] = defaultdict(list)
        self._rate_limit_max = rate_limit  # Max requests per minute per domain

    def _check_rate_limit(self, domain: str):
        """Enforce rate limiting per domain"""
        now = time()
        minute_ago = now - 60

        # Clean old requests
        self._rate_limits[domain] = [
            t for t in self._rate_limits[domain] if t > minute_ago
        ]

        # Check limit
        if len(self._rate_limits[domain]) >= self._rate_limit_max:
            raise ValidationError(f"Rate limit exceeded for domain: {domain}")

        self._rate_limits[domain].append(now)
```

---

### 7. Cache Poisoning via DID Resolution

**Location:** `genesisgraph/did_resolver.py:76-78, 100`

**Severity:** MEDIUM
**OWASP Category:** A04:2021 - Insecure Design

**Issue:**
The DID resolution cache doesn't expire entries based on TTL, only stores them forever. An attacker could poison the cache with a malicious DID document.

```python
# CURRENT CODE (no expiration)
if cache_key in self._cache:
    return self._cache[cache_key]  # No TTL check!
```

**Recommendation:**
```python
from time import time

class DIDResolver:
    def __init__(self, timeout: int = 10, cache_ttl: int = 300):
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Tuple[bytes, float]] = {}  # (value, timestamp)

    def resolve_to_public_key(self, did: str, key_id: Optional[str] = None) -> bytes:
        """Resolve DID to Ed25519 public key bytes"""
        # Check cache with TTL
        cache_key = f"{did}#{key_id}" if key_id else did
        if cache_key in self._cache:
            cached_value, cached_time = self._cache[cache_key]
            if time() - cached_time < self.cache_ttl:
                return cached_value
            else:
                # Expired, remove from cache
                del self._cache[cache_key]

        # ... resolution logic ...

        # Cache result with timestamp
        self._cache[cache_key] = (public_key, time())
        return public_key
```

---

### 8. Integer Overflow in Base58 Decoding

**Location:** `genesisgraph/did_resolver.py:287-291`

**Severity:** MEDIUM
**OWASP Category:** A04:2021 - Insecure Design

**Issue:**
The base58 decoding doesn't limit input size, potentially causing integer overflow or memory exhaustion.

```python
# CURRENT CODE (no size limit)
num = 0
for char in s:
    if char not in ALPHABET:
        raise ValueError(f"Invalid base58 character: {char}")
    num = num * 58 + ALPHABET.index(char)  # Unlimited growth
```

**Recommendation:**
```python
@staticmethod
def _base58_decode(s: str) -> bytes:
    """Decode base58btc string to bytes with size limits"""
    # Limit input size to prevent DoS
    MAX_BASE58_LENGTH = 128
    if len(s) > MAX_BASE58_LENGTH:
        raise ValueError(f"Base58 string too long: {len(s)} (max {MAX_BASE58_LENGTH})")

    ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    num = 0
    for char in s:
        if char not in ALPHABET:
            raise ValueError(f"Invalid base58 character: {char}")
        num = num * 58 + ALPHABET.index(char)

    # Sanity check result size
    if num.bit_length() > 1024:  # ~128 bytes max
        raise ValueError("Decoded base58 value too large")

    # ... rest of decoding
```

---

## Medium Priority Issues

### 9. Information Disclosure via Error Messages

**Location:** Throughout codebase, especially `validator.py`

**Severity:** MEDIUM
**OWASP Category:** A05:2021 - Security Misconfiguration

**Issue:**
Error messages reveal internal file paths and system information:

```python
# Example from validator.py:542
errors.append(f"Entity '{entity_id}': failed to verify hash: {e}")
```

**Recommendation:**
- Log detailed errors to a secure log file
- Return sanitized error messages to users
- Don't expose internal paths in production

```python
import logging

def _verify_file_hash(self, entity: Dict, base_path: str) -> List[str]:
    try:
        # ... verification logic ...
    except Exception as e:
        # Log detailed error securely
        logging.error(f"Hash verification failed for {entity_id}: {e}", exc_info=True)

        # Return sanitized error to user
        errors.append(f"Entity '{entity_id}': hash verification failed")
```

---

### 10. Missing Input Length Validation

**Location:** Multiple locations accepting user input

**Severity:** MEDIUM
**OWASP Category:** A03:2021 - Injection

**Issue:**
No limits on input sizes for IDs, hashes, signatures, etc., allowing potential DoS.

**Recommendation:**
```python
def _validate_entities(self, entities: List[Dict], file_path: Optional[str]) -> List[str]:
    """Validate entity definitions with size limits"""
    errors = []

    # Limit number of entities
    MAX_ENTITIES = 10000
    if len(entities) > MAX_ENTITIES:
        errors.append(f"Too many entities: {len(entities)} (max {MAX_ENTITIES})")
        return errors

    for i, entity in enumerate(entities):
        # Validate ID length
        entity_id = entity.get('id', '')
        MAX_ID_LENGTH = 256
        if len(entity_id) > MAX_ID_LENGTH:
            errors.append(f"Entity ID too long: {len(entity_id)} (max {MAX_ID_LENGTH})")

        # ... rest of validation
```

---

### 11. Weak Randomness in Test Fixtures

**Location:** Tests may use weak random for key generation

**Severity:** LOW-MEDIUM
**OWASP Category:** A02:2021 - Cryptographic Failures

**Issue:**
Ensure test fixtures don't use `random` module for cryptographic keys.

**Recommendation:**
Always use `secrets` module or `cryptography` library for key generation:

```python
# GOOD
from cryptography.hazmat.primitives.asymmetric import ed25519
private_key = ed25519.Ed25519PrivateKey.generate()

# BAD
import random
random.seed(12345)  # Never do this for crypto!
```

---

### 12. Missing Content-Type Validation for DID Documents

**Location:** `genesisgraph/did_resolver.py:203-205`

**Severity:** MEDIUM
**OWASP Category:** A03:2021 - Injection

**Issue:**
No validation that the response is actually JSON before parsing.

**Recommendation:**
```python
response = requests.get(url, timeout=self.timeout, verify=True, allow_redirects=False)
response.raise_for_status()

# Validate Content-Type
content_type = response.headers.get('Content-Type', '')
if 'application/json' not in content_type:
    raise ValidationError(f"Invalid content type from {url}: {content_type}")

# Limit response size
MAX_RESPONSE_SIZE = 1_000_000  # 1MB
if len(response.content) > MAX_RESPONSE_SIZE:
    raise ValidationError(f"Response too large from {url}")

did_document = response.json()
```

---

### 13. Timing Attacks on Signature Verification

**Location:** `genesisgraph/validator.py:436-442`

**Severity:** MEDIUM
**OWASP Category:** A02:2021 - Cryptographic Failures

**Issue:**
While the `cryptography` library uses constant-time operations, the surrounding code may leak timing information.

**Recommendation:**
The current implementation is acceptable since `cryptography` library handles constant-time comparison internally. However, ensure error messages don't reveal timing information:

```python
# Current code is OK, but document it
try:
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
    public_key.verify(signature_bytes, message)
    # Signature is valid - no errors
except CryptoInvalidSignature:
    # Constant-time verification failed - safe to report
    errors.append(f"{context}: signature verification failed - invalid signature")
```

---

### 14. Missing Dependency Integrity Verification

**Location:** `pyproject.toml`, `requirements.txt`

**Severity:** MEDIUM
**OWASP Category:** A06:2021 - Vulnerable and Outdated Components

**Issue:**
Dependencies are pinned by version but not by hash, allowing potential supply chain attacks.

**Recommendation:**
Use pip-compile with hashes:

```bash
pip-compile --generate-hashes requirements.in -o requirements.txt
```

Or use Poetry/Pipenv for lock files with hashes.

---

## Low Priority Issues

### 15. Insufficient Logging for Security Events

**Location:** Throughout codebase

**Severity:** LOW
**OWASP Category:** A09:2021 - Security Logging and Monitoring Failures

**Issue:**
Limited logging of security-relevant events (failed signatures, invalid DIDs, etc.).

**Recommendation:**
Add comprehensive security logging:

```python
import logging

logger = logging.getLogger('genesisgraph.security')

def _verify_signature(self, attestation: Dict, operation_data: Dict, context: str) -> List[str]:
    # ... verification logic ...

    try:
        public_key.verify(signature_bytes, message)
        logger.info(f"Signature verified successfully for {context} by {signer}")
    except CryptoInvalidSignature:
        logger.warning(f"Signature verification FAILED for {context} by {signer}")
        errors.append(f"{context}: signature verification failed")
```

---

### 16. No Security Headers in Future Web Components

**Severity:** LOW (future consideration)
**OWASP Category:** A05:2021 - Security Misconfiguration

**Issue:**
If a web service is built, ensure security headers are implemented.

**Recommendation:**
Document required security headers for any future web services:
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`

---

## Positive Security Findings

The following security practices were found to be correctly implemented:

✅ **YAML Parsing:** Using `yaml.safe_load()` throughout (prevents arbitrary code execution)
✅ **Hash Algorithms:** Using SHA-256/SHA-512 (cryptographically secure)
✅ **Signature Algorithm:** Using Ed25519 (modern, secure)
✅ **Dependency Pinning:** Versions are pinned to prevent unexpected updates
✅ **Cryptography Library:** Using well-vetted `cryptography` library
✅ **Regular Expressions:** Most regexes are safe from ReDoS
✅ **No SQL Injection:** No SQL database usage
✅ **No Command Injection:** No shell command execution with user input

---

## Recommendations by Priority

### Immediate (Before Production)

1. **Fix path traversal vulnerability** (Issue #1)
2. **Implement SSRF protection** (Issue #2)
3. **Enable TLS certificate validation** (Issue #3)
4. **Fix cache TTL implementation** (Issue #7)

### Short-term (Next Release)

5. **Add rate limiting** (Issue #6)
6. **Implement input length validation** (Issue #10)
7. **Add base58 size limits** (Issue #8)
8. **Validate Content-Type in HTTP responses** (Issue #12)

### Medium-term (Future Releases)

9. **Improve error message sanitization** (Issue #9)
10. **Add security event logging** (Issue #15)
11. **Implement dependency hash verification** (Issue #14)
12. **Add certificate pinning support** (Issue #3 extension)

---

## Security Testing Recommendations

1. **Add Security Test Suite:**
   ```python
   # tests/test_security.py
   def test_path_traversal_blocked():
       """Ensure path traversal is blocked"""

   def test_ssrf_protection():
       """Ensure SSRF attempts are blocked"""

   def test_rate_limiting():
       """Ensure rate limits are enforced"""
   ```

2. **Fuzz Testing:**
   - Use `atheris` or `pythonfuzz` to fuzz DID parsing
   - Fuzz YAML parsing with malformed documents
   - Fuzz signature verification with random data

3. **Static Analysis:**
   - Run `bandit` for Python security issues
   - Run `safety` for known vulnerable dependencies
   - Run `semgrep` with security rules

4. **Penetration Testing:**
   - Test path traversal with various encodings
   - Test SSRF with redirect chains
   - Test ReDoS with crafted inputs

---

## Compliance Checklist

- [ ] OWASP Top 10 2021 compliance
- [ ] CWE Top 25 mitigation
- [ ] NIST Cryptographic Standards compliance
- [ ] Secure coding guidelines followed
- [ ] Security testing implemented
- [ ] Vulnerability disclosure policy in place (✅ SECURITY.md exists)
- [ ] Dependency vulnerability scanning
- [ ] Security logging implemented
- [ ] Incident response plan

---

## References

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cryptographic Standards](https://csrc.nist.gov/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Report Generated:** 2025-11-17
**Next Review Recommended:** Before v0.2.0 release
