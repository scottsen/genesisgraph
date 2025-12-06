"""
Tests for signature verification and DID resolution

Tests cover:
- DID resolution (did:key, did:web)
- Ed25519 signature verification
- Canonical JSON encoding
- Error handling and edge cases
"""

import base64
import json

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from genesisgraph.did_resolver import DIDResolver, resolve_did_to_public_key
from genesisgraph.errors import ValidationError
from genesisgraph.validator import GenesisGraphValidator


class TestDIDResolver:
    """Tests for DID resolution"""

    def test_resolve_did_key_valid(self):
        """Test resolving a valid did:key identifier"""
        resolver = DIDResolver()

        # Generate a test keypair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes_raw()

        # Create did:key from public key
        # Format: did:key:z<base58btc(0xed01 + public_key)>
        multicodec_key = b'\xed\x01' + public_key_bytes
        did = f"did:key:z{self._base58_encode(multicodec_key)}"

        # Resolve DID
        resolved_key = resolver.resolve_to_public_key(did)

        # Should match original public key
        assert resolved_key == public_key_bytes

    def test_resolve_did_key_invalid_multibase(self):
        """Test did:key with invalid multibase encoding"""
        resolver = DIDResolver()

        # Use 'x' prefix instead of 'z' (unsupported encoding)
        did = "did:key:xInvalidEncoding"

        with pytest.raises(ValidationError, match="Unsupported multibase encoding"):
            resolver.resolve_to_public_key(did)

    def test_resolve_did_key_invalid_multicodec(self):
        """Test did:key with wrong key type"""
        resolver = DIDResolver()

        # Create key with wrong multicodec (0xabcd instead of 0xed01)
        wrong_multicodec = b'\xab\xcd' + b'\x00' * 32
        did = f"did:key:z{self._base58_encode(wrong_multicodec)}"

        with pytest.raises(ValidationError, match="Unsupported key type"):
            resolver.resolve_to_public_key(did)

    def test_resolve_did_key_too_short(self):
        """Test did:key with insufficient bytes"""
        resolver = DIDResolver()

        # Create key that's too short
        short_key = b'\xed'  # Only 1 byte
        did = f"did:key:z{self._base58_encode(short_key)}"

        with pytest.raises(ValidationError, match="did:key too short"):
            resolver.resolve_to_public_key(did)

    def test_resolve_invalid_did_format(self):
        """Test DID without did: prefix"""
        resolver = DIDResolver()

        with pytest.raises(ValidationError, match="Invalid DID format"):
            resolver.resolve_to_public_key("key:z6Mk...")

    def test_resolve_unsupported_method(self):
        """Test unsupported DID method"""
        resolver = DIDResolver()

        with pytest.raises(ValidationError, match="Unsupported DID method"):
            resolver.resolve_to_public_key("did:btcr:xxcl-lzpq-q83a-0d5")

    def test_convenience_function(self):
        """Test resolve_did_to_public_key convenience function"""
        # Generate test key
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes_raw()

        # Create did:key
        multicodec_key = b'\xed\x01' + public_key_bytes
        did = f"did:key:z{self._base58_encode(multicodec_key)}"

        # Use convenience function
        resolved = resolve_did_to_public_key(did)
        assert resolved == public_key_bytes

    def test_cache_works(self):
        """Test that DID resolution caching works"""
        resolver = DIDResolver()

        # Generate test key
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes_raw()

        multicodec_key = b'\xed\x01' + public_key_bytes
        did = f"did:key:z{self._base58_encode(multicodec_key)}"

        # First resolution
        result1 = resolver.resolve_to_public_key(did)

        # Second resolution (should hit cache)
        result2 = resolver.resolve_to_public_key(did)

        assert result1 == result2 == public_key_bytes

        # Clear cache and verify it's empty
        resolver.clear_cache()
        assert len(resolver._cache) == 0

    @staticmethod
    def _base58_encode(data: bytes) -> str:
        """Encode bytes to base58btc (for test did:key generation)"""
        ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

        # Convert bytes to integer
        num = int.from_bytes(data, 'big')

        # Convert to base58
        if num == 0:
            return '1'

        result = []
        while num > 0:
            num, remainder = divmod(num, 58)
            result.append(ALPHABET[remainder])

        # Add leading '1's for leading zero bytes
        for byte in data:
            if byte == 0:
                result.append('1')
            else:
                break

        return ''.join(reversed(result))


class TestSignatureVerification:
    """Tests for Ed25519 signature verification"""

    def test_valid_signature_verification(self):
        """Test verification of a valid Ed25519 signature"""
        # Generate keypair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes_raw()

        # Create did:key from public key
        multicodec_key = b'\xed\x01' + public_key_bytes
        did = f"did:key:z{self._base58_encode(multicodec_key)}"

        # Create operation to sign
        operation_data = {
            "id": "op_test",
            "type": "process",
            "inputs": ["input1"],
            "outputs": ["output1"]
        }

        # Compute canonical JSON
        canonical_json = json.dumps(operation_data, sort_keys=True, separators=(',', ':'))
        message = canonical_json.encode('utf-8')

        # Sign
        signature_bytes = private_key.sign(message)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

        # Create attestation
        attestation = {
            "mode": "signed",
            "signer": did,
            "signature": f"ed25519:{signature_b64}",
            "timestamp": "2025-11-17T10:00:00Z"
        }

        # Add attestation to operation
        operation_data["attestation"] = attestation

        # Validate with signature verification enabled
        validator = GenesisGraphValidator(verify_signatures=True)
        errors = validator._validate_attestation(attestation, "op_test", operation_data)

        # Should have no errors
        assert len(errors) == 0

    def test_invalid_signature_detection(self):
        """Test detection of invalid signature"""
        # Generate keypair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes_raw()

        # Create did:key
        multicodec_key = b'\xed\x01' + public_key_bytes
        did = f"did:key:z{self._base58_encode(multicodec_key)}"

        # Create operation
        operation_data = {
            "id": "op_test",
            "type": "process",
            "inputs": ["input1"],
            "outputs": ["output1"]
        }

        # Sign DIFFERENT data
        wrong_message = b"This is the wrong message"
        signature_bytes = private_key.sign(wrong_message)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

        # Create attestation
        attestation = {
            "mode": "signed",
            "signer": did,
            "signature": f"ed25519:{signature_b64}",
            "timestamp": "2025-11-17T10:00:00Z"
        }

        operation_data["attestation"] = attestation

        # Validate with signature verification
        validator = GenesisGraphValidator(verify_signatures=True)
        errors = validator._validate_attestation(attestation, "op_test", operation_data)

        # Should have signature verification error
        assert any("signature verification failed" in err.lower() for err in errors)

    def test_malformed_signature_base64(self):
        """Test handling of malformed base64 signature"""
        # Generate keypair for DID
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes_raw()

        multicodec_key = b'\xed\x01' + public_key_bytes
        did = f"did:key:z{self._base58_encode(multicodec_key)}"

        # Create operation
        operation_data = {
            "id": "op_test",
            "type": "process",
            "inputs": ["input1"],
            "outputs": ["output1"],
            "attestation": {
                "mode": "signed",
                "signer": did,
                "signature": "ed25519:NOT_VALID_BASE64!!!",
                "timestamp": "2025-11-17T10:00:00Z"
            }
        }

        # Validate
        validator = GenesisGraphValidator(verify_signatures=True)
        errors = validator._validate_attestation(
            operation_data["attestation"], "op_test", operation_data
        )

        # Should have decoding error
        assert any("failed to decode signature" in err.lower() for err in errors)

    def test_mock_signature_accepted(self):
        """Test that mock signatures are accepted for testing"""
        operation_data = {
            "id": "op_test",
            "type": "process",
            "inputs": ["input1"],
            "outputs": ["output1"],
            "attestation": {
                "mode": "signed",
                "signer": "did:key:z6MkTest",
                "signature": "ed25519:mock:test-signature",
                "timestamp": "2025-11-17T10:00:00Z"
            }
        }

        validator = GenesisGraphValidator(verify_signatures=True)
        errors = validator._validate_attestation(
            operation_data["attestation"], "op_test", operation_data
        )

        # Mock signatures should not generate errors
        assert len(errors) == 0

    def test_signature_verification_disabled(self):
        """Test that signatures are not verified when verify_signatures=False"""
        operation_data = {
            "id": "op_test",
            "type": "process",
            "inputs": ["input1"],
            "outputs": ["output1"],
            "attestation": {
                "mode": "signed",
                "signer": "did:key:z6MkTest",
                "signature": "ed25519:invalid_signature_data",
                "timestamp": "2025-11-17T10:00:00Z"
            }
        }

        # Verify signatures is FALSE by default
        validator = GenesisGraphValidator(verify_signatures=False)
        errors = validator._validate_attestation(
            operation_data["attestation"], "op_test", operation_data
        )

        # Should only check format, not verify cryptographically
        # Invalid base64 format should be caught during format validation
        assert len(errors) == 0  # Format validation happens only when verify_signatures=True

    def test_missing_signer_field(self):
        """Test handling of missing signer field"""
        operation_data = {
            "id": "op_test",
            "type": "process",
            "inputs": ["input1"],
            "outputs": ["output1"],
            "attestation": {
                "mode": "signed",
                "signature": "ed25519:mockdata",
                "timestamp": "2025-11-17T10:00:00Z"
            }
        }

        validator = GenesisGraphValidator(verify_signatures=False)
        errors = validator._validate_attestation(
            operation_data["attestation"], "op_test", operation_data
        )

        # Should report missing signer
        assert any("requires 'signer'" in err for err in errors)

    @staticmethod
    def _base58_encode(data: bytes) -> str:
        """Encode bytes to base58btc"""
        ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        num = int.from_bytes(data, 'big')
        if num == 0:
            return '1'
        result = []
        while num > 0:
            num, remainder = divmod(num, 58)
            result.append(ALPHABET[remainder])
        for byte in data:
            if byte == 0:
                result.append('1')
            else:
                break
        return ''.join(reversed(result))


class TestCanonicalJSON:
    """Tests for canonical JSON encoding"""

    def test_canonical_json_key_sorting(self):
        """Test that keys are sorted alphabetically"""
        validator = GenesisGraphValidator()

        data = {"z": 1, "a": 2, "m": 3}
        canonical = validator._canonical_json(data)

        assert canonical == '{"a":2,"m":3,"z":1}'

    def test_canonical_json_no_whitespace(self):
        """Test that canonical JSON has no whitespace"""
        validator = GenesisGraphValidator()

        data = {"key": "value", "number": 42}
        canonical = validator._canonical_json(data)

        # Should have no spaces
        assert ' ' not in canonical
        assert '\n' not in canonical
        assert '\t' not in canonical

    def test_canonical_json_nested(self):
        """Test canonical JSON with nested objects"""
        validator = GenesisGraphValidator()

        data = {
            "operation": {
                "type": "process",
                "id": "op1"
            },
            "inputs": ["a", "b"]
        }

        canonical = validator._canonical_json(data)

        # Keys should be sorted at all levels
        assert canonical == '{"inputs":["a","b"],"operation":{"id":"op1","type":"process"}}'

    def test_canonical_json_deterministic(self):
        """Test that canonical JSON is deterministic"""
        validator = GenesisGraphValidator()

        data = {"z": 1, "a": 2, "m": 3}

        # Compute canonical JSON multiple times
        canonical1 = validator._canonical_json(data)
        canonical2 = validator._canonical_json(data)
        canonical3 = validator._canonical_json(data)

        # Should always be identical
        assert canonical1 == canonical2 == canonical3


class TestIntegrationSignatureVerification:
    """Integration tests for full signature verification workflow"""

    def test_full_document_with_signature(self):
        """Test validation of complete document with signed operation"""
        # Generate keypair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes_raw()

        # Create did:key
        multicodec_key = b'\xed\x01' + public_key_bytes
        did = f"did:key:z{self._base58_encode(multicodec_key)}"

        # Create operation to sign
        operation_data = {
            "id": "op_signed_process",
            "type": "process",
            "inputs": ["gg:file:project:input.txt"],
            "outputs": ["gg:file:project:output.txt"]
        }

        # Sign operation
        canonical_json = json.dumps(operation_data, sort_keys=True, separators=(',', ':'))
        message = canonical_json.encode('utf-8')
        signature_bytes = private_key.sign(message)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

        # Add attestation
        operation_data["attestation"] = {
            "mode": "signed",
            "signer": did,
            "signature": f"ed25519:{signature_b64}",
            "timestamp": "2025-11-17T10:00:00Z"
        }

        # Create complete document
        document = {
            "spec_version": "0.1.0",
            "entities": [
                {
                    "id": "gg:file:project:input.txt",
                    "type": "File",
                    "version": "1",
                    "uri": "file:///tmp/input.txt"
                },
                {
                    "id": "gg:file:project:output.txt",
                    "type": "File",
                    "version": "1",
                    "uri": "file:///tmp/output.txt"
                }
            ],
            "operations": [operation_data],
            "tools": []
        }

        # Validate with signature verification
        validator = GenesisGraphValidator(verify_signatures=True)
        result = validator.validate(document)

        # Should be valid
        assert result.is_valid
        assert len(result.errors) == 0

    def test_tampered_document_detection(self):
        """Test that tampering with signed document is detected"""
        # Generate keypair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes_raw()

        # Create did:key
        multicodec_key = b'\xed\x01' + public_key_bytes
        did = f"did:key:z{self._base58_encode(multicodec_key)}"

        # Create and sign operation
        operation_data = {
            "id": "op_process",
            "type": "process",
            "inputs": ["input1"],
            "outputs": ["output1"]
        }

        canonical_json = json.dumps(operation_data, sort_keys=True, separators=(',', ':'))
        message = canonical_json.encode('utf-8')
        signature_bytes = private_key.sign(message)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')

        operation_data["attestation"] = {
            "mode": "signed",
            "signer": did,
            "signature": f"ed25519:{signature_b64}",
            "timestamp": "2025-11-17T10:00:00Z"
        }

        # NOW TAMPER: Change the outputs after signing
        operation_data["outputs"] = ["tampered_output"]

        document = {
            "spec_version": "0.1.0",
            "entities": [],
            "operations": [operation_data],
            "tools": []
        }

        # Validate
        validator = GenesisGraphValidator(verify_signatures=True)
        result = validator.validate(document)

        # Should detect tampering
        assert not result.is_valid
        assert any("signature verification failed" in err.lower() for err in result.errors)

    @staticmethod
    def _base58_encode(data: bytes) -> str:
        """Encode bytes to base58btc"""
        ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        num = int.from_bytes(data, 'big')
        if num == 0:
            return '1'
        result = []
        while num > 0:
            num, remainder = divmod(num, 58)
            result.append(ALPHABET[remainder])
        for byte in data:
            if byte == 0:
                result.append('1')
            else:
                break
        return ''.join(reversed(result))
