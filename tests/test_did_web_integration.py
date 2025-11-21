"""
Integration tests for did:web resolution

Tests complete did:web resolution flow including:
- Valid DID document resolution
- Multiple public key formats (base58, multibase, JWK)
- Key selection by ID
- End-to-end signature verification with did:web
"""

import json
import base64
from unittest.mock import Mock, patch
import pytest

from genesisgraph.did_resolver import DIDResolver
from genesisgraph.errors import ValidationError
from genesisgraph.validator import GenesisGraphValidator


class TestDIDWebIntegration:
    """Integration tests for did:web resolution"""

    def test_resolve_did_web_with_base58_key(self, mock_http_response, base58_encode):
        """Test successful did:web resolution with publicKeyBase58"""
        # Ed25519 public key (32 bytes)
        test_public_key = b'\x12\x34\x56\x78' * 8  # 32 bytes

        key_base58 = base58_encode(test_public_key)

        # Mock DID document
        did_document = {
            "id": "did:web:example.com",
            "verificationMethod": [{
                "id": "did:web:example.com#keys-1",
                "type": "Ed25519VerificationKey2020",
                "controller": "did:web:example.com",
                "publicKeyBase58": key_base58
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.return_value = mock_http_response(json_data=did_document)

            resolver = DIDResolver()
            public_key = resolver.resolve_to_public_key('did:web:example.com')

            assert public_key == test_public_key
            # Verify correct URL was called
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            assert args[0] == 'https://example.com/.well-known/did.json'
            assert kwargs['verify'] is True
            assert kwargs['allow_redirects'] is False

    def test_resolve_did_web_with_multibase_key(self, mock_http_response, base58_encode):
        """Test did:web resolution with publicKeyMultibase"""
        test_public_key = b'\xab\xcd\xef\x01' * 8  # 32 bytes

        key_multibase = 'z' + base58_encode(test_public_key)

        did_document = {
            "id": "did:web:example.com",
            "verificationMethod": [{
                "id": "#keys-1",
                "type": "Ed25519VerificationKey2018",
                "controller": "did:web:example.com",
                "publicKeyMultibase": key_multibase
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.return_value = mock_http_response(
                content_type='application/did+json',
                json_data=did_document
            )

            resolver = DIDResolver()
            public_key = resolver.resolve_to_public_key('did:web:example.com', '#keys-1')

            assert public_key == test_public_key

    def test_resolve_did_web_with_jwk(self, mock_http_response):
        """Test did:web resolution with publicKeyJwk (JSON Web Key)"""
        test_public_key = b'\xff\xee\xdd\xcc' * 8  # 32 bytes

        # Encode as JWK (base64url without padding)
        x_b64 = base64.urlsafe_b64encode(test_public_key).decode().rstrip('=')

        did_document = {
            "id": "did:web:enterprise.example.com",
            "verificationMethod": [{
                "id": "did:web:enterprise.example.com#key-1",
                "type": "JsonWebKey2020",
                "controller": "did:web:enterprise.example.com",
                "publicKeyJwk": {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": x_b64
                }
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.return_value = mock_http_response(json_data=did_document)

            resolver = DIDResolver()
            public_key = resolver.resolve_to_public_key(
                'did:web:enterprise.example.com',
                '#key-1'
            )

            assert public_key == test_public_key

    def test_resolve_did_web_with_path(self, mock_http_response, base58_encode):
        """Test did:web with path components: did:web:example.com:user:alice"""
        test_public_key = b'\x11\x22\x33\x44' * 8

        did_document = {
            "id": "did:web:example.com:user:alice",
            "verificationMethod": [{
                "id": "#keys-1",
                "type": "Ed25519VerificationKey2020",
                "controller": "did:web:example.com:user:alice",
                "publicKeyBase58": base58_encode(test_public_key)
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.return_value = mock_http_response(json_data=did_document)

            resolver = DIDResolver()
            public_key = resolver.resolve_to_public_key('did:web:example.com:user:alice')

            assert public_key == test_public_key
            # Verify path was correctly converted to URL
            mock_get.assert_called_once()
            args, _ = mock_get.call_args
            assert args[0] == 'https://example.com/user/alice/did.json'

    def test_end_to_end_signature_verification_with_did_web(self, mock_http_response, base58_encode):
        """Test complete signature verification flow using did:web"""
        # This is a more complete integration test that verifies the entire chain:
        # did:web resolution -> public key extraction -> signature verification

        # Generate a test Ed25519 key pair (in practice, use ed25519 library)
        # For this test, we'll mock the verification
        test_public_key = b'\xaa\xbb\xcc\xdd' * 8

        did_document = {
            "id": "did:web:hospital.example.com",
            "verificationMethod": [{
                "id": "did:web:hospital.example.com#keys-1",
                "type": "Ed25519VerificationKey2020",
                "controller": "did:web:hospital.example.com",
                "publicKeyBase58": base58_encode(test_public_key)
            }]
        }

        # Mock the HTTP request for DID document
        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.return_value = mock_http_response(json_data=did_document)

            # Mock ed25519 verification
            with patch('genesisgraph.validator.ed25519') as mock_ed25519:
                mock_verify = Mock()
                mock_ed25519.Ed25519PublicKey.from_public_bytes.return_value = mock_verify

                validator = GenesisGraphValidator(verify_signatures=True)

                attestation = {
                    'signer': 'did:web:hospital.example.com',
                    'signature': f'ed25519:{base64.b64encode(b"fake_signature" * 8).decode()}',
                    'timestamp': '2025-10-15T14:30:00Z'
                }

                operation_data = {
                    'id': 'op_test_001',
                    'tool': {'name': 'test_tool'},
                    'inputs': [],
                    'outputs': []
                }

                context = 'Operation op_test_001'

                # This should resolve did:web and attempt verification
                errors = validator._verify_signature(attestation, operation_data, context)

                # Print errors for debugging
                if errors:
                    print(f"Verification errors: {errors}")

                # Verify DID was resolved
                mock_get.assert_called_once()
                # Verify ed25519 verification was attempted with correct key
                mock_ed25519.Ed25519PublicKey.from_public_bytes.assert_called_once_with(test_public_key)

    def test_multiple_verification_methods(self, mock_http_response, base58_encode):
        """Test DID document with multiple keys, selecting specific one"""
        key1 = b'\x11' * 32
        key2 = b'\x22' * 32

        did_document = {
            "id": "did:web:multi.example.com",
            "verificationMethod": [
                {
                    "id": "#auth-key",
                    "type": "Ed25519VerificationKey2020",
                    "controller": "did:web:multi.example.com",
                    "publicKeyBase58": base58_encode(key1)
                },
                {
                    "id": "#signing-key",
                    "type": "Ed25519VerificationKey2020",
                    "controller": "did:web:multi.example.com",
                    "publicKeyBase58": base58_encode(key2)
                }
            ]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.return_value = mock_http_response(json_data=did_document)

            resolver = DIDResolver()

            # Resolve with specific key ID
            public_key = resolver.resolve_to_public_key(
                'did:web:multi.example.com',
                '#signing-key'
            )

            assert public_key == key2  # Should get key2, not key1

    def test_caching_works_for_did_web(self, mock_http_response, base58_encode):
        """Test that did:web results are cached to reduce network calls"""
        test_public_key = b'\x99' * 32

        did_document = {
            "id": "did:web:cached.example.com",
            "verificationMethod": [{
                "id": "#keys-1",
                "type": "Ed25519VerificationKey2020",
                "controller": "did:web:cached.example.com",
                "publicKeyBase58": base58_encode(test_public_key)
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.return_value = mock_http_response(json_data=did_document)

            resolver = DIDResolver(cache_ttl=300)

            # First call - should hit network
            public_key1 = resolver.resolve_to_public_key('did:web:cached.example.com')
            assert public_key1 == test_public_key
            assert mock_get.call_count == 1

            # Second call - should use cache
            public_key2 = resolver.resolve_to_public_key('did:web:cached.example.com')
            assert public_key2 == test_public_key
            assert mock_get.call_count == 1  # Still only 1 call

    def test_invalid_key_type_rejected(self, mock_http_response):
        """Test that non-Ed25519 keys are rejected"""
        did_document = {
            "id": "did:web:example.com",
            "verificationMethod": [{
                "id": "#keys-1",
                "type": "EcdsaSecp256k1VerificationKey2019",  # Not Ed25519
                "controller": "did:web:example.com",
                "publicKeyBase58": "abcd1234"
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.return_value = mock_http_response(json_data=did_document)

            resolver = DIDResolver()

            with pytest.raises(ValidationError) as exc:
                resolver.resolve_to_public_key('did:web:example.com')

            assert 'Unsupported key type' in str(exc.value)

    def test_key_not_found(self, mock_http_response):
        """Test error when requested key ID doesn't exist"""
        did_document = {
            "id": "did:web:example.com",
            "verificationMethod": [{
                "id": "#keys-1",
                "type": "Ed25519VerificationKey2020",
                "controller": "did:web:example.com",
                "publicKeyBase58": "abcd1234"
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.return_value = mock_http_response(json_data=did_document)

            resolver = DIDResolver()

            with pytest.raises(ValidationError) as exc:
                resolver.resolve_to_public_key('did:web:example.com', '#wrong-key')

            assert 'Key #wrong-key not found' in str(exc.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
