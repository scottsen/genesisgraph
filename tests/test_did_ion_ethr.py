"""
Integration tests for did:ion and did:ethr resolution

Tests complete resolution flow including:
- Valid DID document resolution for did:ion
- Valid DID document resolution for did:ethr
- Multiple public key formats
- Key selection by ID
- Error handling and edge cases
"""

import base64
import json
from unittest.mock import Mock, patch

import pytest

from genesisgraph.did_resolver import DIDResolver
from genesisgraph.errors import ValidationError


class TestDIDIonIntegration:
    """Integration tests for did:ion resolution"""

    def test_resolve_did_ion_with_base58_key(self):
        """Test successful did:ion resolution with publicKeyBase58"""
        # Ed25519 public key (32 bytes)
        test_public_key = b'\x12\x34\x56\x78' * 8  # 32 bytes

        # Base58 encode the key
        def base58_encode(data):
            ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(data, 'big')
            if num == 0:
                return '1' * len(data)
            result = ''
            while num > 0:
                num, remainder = divmod(num, 58)
                result = ALPHABET[remainder] + result
            # Add leading '1's for leading zero bytes
            for byte in data:
                if byte == 0:
                    result = '1' + result
                else:
                    break
            return result

        key_base58 = base58_encode(test_public_key)

        # Mock DID document (ION format)
        did = "did:ion:EiDahaOGH-liLLdDtTxEAdc8i-cfCz-WUcQdRJheMVNn3A"
        did_document = {
            "id": did,
            "verificationMethod": [{
                "id": f"{did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyBase58": key_base58
            }]
        }

        # ION resolver returns a resolution result wrapper
        resolution_result = {
            "didDocument": did_document,
            "didDocumentMetadata": {},
            "didResolutionMetadata": {
                "contentType": "application/did+json"
            }
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = json.dumps(resolution_result).encode()
            mock_response.json.return_value = resolution_result
            mock_get.return_value = mock_response

            resolver = DIDResolver()
            public_key = resolver.resolve_to_public_key(did)

            assert public_key == test_public_key
            # Verify correct URL was called
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            assert args[0] == f'https://ion.tbd.website/identifiers/{did}'
            assert kwargs['verify'] is True
            assert kwargs['allow_redirects'] is False

    def test_resolve_did_ion_with_jwk(self):
        """Test did:ion resolution with publicKeyJwk"""
        test_public_key = b'\xab\xcd\xef\x01' * 8  # 32 bytes

        # Encode as JWK (base64url without padding)
        x_b64 = base64.urlsafe_b64encode(test_public_key).decode().rstrip('=')

        did = "did:ion:EiAnKD8-jfdd0MDcZUjAbRgaThBrMxPTFOxcnfJhI7Ukaw"
        did_document = {
            "id": did,
            "verificationMethod": [{
                "id": "#key-1",
                "type": "JsonWebKey2020",
                "controller": did,
                "publicKeyJwk": {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": x_b64
                }
            }]
        }

        # Direct DID document format (without resolution wrapper)
        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/did+json'}
            mock_response.content = json.dumps(did_document).encode()
            mock_response.json.return_value = did_document
            mock_get.return_value = mock_response

            resolver = DIDResolver()
            public_key = resolver.resolve_to_public_key(did, '#key-1')

            assert public_key == test_public_key

    def test_resolve_did_ion_invalid_format(self):
        """Test did:ion with invalid DID format"""
        with patch('genesisgraph.did_resolver.requests.get'):
            resolver = DIDResolver()

            with pytest.raises(ValidationError, match="Invalid did:ion format"):
                resolver._resolve_did_ion("did:web:example.com")

    def test_resolve_did_ion_network_error(self):
        """Test did:ion resolution with network error"""
        import requests as req_module
        did = "did:ion:EiDahaOGH-liLLdDtTxEAdc8i-cfCz-WUcQdRJheMVNn3A"

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.side_effect = req_module.RequestException("Network error")

            resolver = DIDResolver()
            with pytest.raises(ValidationError, match="Failed to fetch did:ion document"):
                resolver.resolve_to_public_key(did)

    def test_resolve_did_ion_invalid_json(self):
        """Test did:ion resolution with invalid JSON response"""
        did = "did:ion:EiDahaOGH-liLLdDtTxEAdc8i-cfCz-WUcQdRJheMVNn3A"

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = b'invalid json{'
            mock_response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)
            mock_get.return_value = mock_response

            resolver = DIDResolver()
            with pytest.raises(ValidationError, match="Invalid JSON in did:ion document"):
                resolver.resolve_to_public_key(did)

    def test_resolve_did_ion_rate_limiting(self):
        """Test rate limiting for did:ion resolution"""
        did = "did:ion:EiDahaOGH-liLLdDtTxEAdc8i-cfCz-WUcQdRJheMVNn3A"
        test_public_key = b'\x12\x34\x56\x78' * 8

        def base58_encode(data):
            ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(data, 'big')
            result = ''
            while num > 0:
                num, remainder = divmod(num, 58)
                result = ALPHABET[remainder] + result
            return result

        did_document = {
            "id": did,
            "verificationMethod": [{
                "id": "#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyBase58": base58_encode(test_public_key)
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = json.dumps(did_document).encode()
            mock_response.json.return_value = did_document
            mock_get.return_value = mock_response

            # Create resolver with low rate limit and no caching
            resolver = DIDResolver(rate_limit=2, cache_ttl=0)

            # First two calls should succeed
            resolver.resolve_to_public_key(did, '#key-1')
            resolver.resolve_to_public_key(did, '#key-1')

            # Third call should fail due to rate limit
            with pytest.raises(ValidationError, match="Rate limit exceeded"):
                resolver.resolve_to_public_key(did, '#key-1')


class TestDIDEthrIntegration:
    """Integration tests for did:ethr resolution"""

    def test_resolve_did_ethr_with_base58_key(self):
        """Test successful did:ethr resolution with publicKeyBase58"""
        # Ed25519 public key (32 bytes)
        test_public_key = b'\x98\x76\x54\x32' * 8  # 32 bytes

        # Base58 encode the key
        def base58_encode(data):
            ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(data, 'big')
            if num == 0:
                return '1' * len(data)
            result = ''
            while num > 0:
                num, remainder = divmod(num, 58)
                result = ALPHABET[remainder] + result
            for byte in data:
                if byte == 0:
                    result = '1' + result
                else:
                    break
            return result

        key_base58 = base58_encode(test_public_key)

        # Mock DID document (Ethereum format)
        did = "did:ethr:0xf3beac30c498d9e26865f34fcaa57dbb935b0d74"
        did_document = {
            "id": did,
            "verificationMethod": [{
                "id": f"{did}#controller",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyBase58": key_base58
            }]
        }

        # Universal Resolver returns a resolution result wrapper
        resolution_result = {
            "didDocument": did_document,
            "didDocumentMetadata": {},
            "didResolutionMetadata": {
                "contentType": "application/did+ld+json"
            }
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = json.dumps(resolution_result).encode()
            mock_response.json.return_value = resolution_result
            mock_get.return_value = mock_response

            resolver = DIDResolver()
            public_key = resolver.resolve_to_public_key(did)

            assert public_key == test_public_key
            # Verify correct URL was called
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            assert args[0] == f'https://dev.uniresolver.io/1.0/identifiers/{did}'
            assert kwargs['verify'] is True
            assert kwargs['allow_redirects'] is False

    def test_resolve_did_ethr_with_multibase_key(self):
        """Test did:ethr resolution with publicKeyMultibase"""
        test_public_key = b'\xaa\xbb\xcc\xdd' * 8  # 32 bytes

        def base58_encode(data):
            ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(data, 'big')
            result = ''
            while num > 0:
                num, remainder = divmod(num, 58)
                result = ALPHABET[remainder] + result
            return result

        key_multibase = 'z' + base58_encode(test_public_key)

        # did:ethr with chain ID
        did = "did:ethr:0x5:0xf3beac30c498d9e26865f34fcaa57dbb935b0d74"
        did_document = {
            "id": did,
            "verificationMethod": [{
                "id": "#owner",
                "type": "Ed25519VerificationKey2018",
                "controller": did,
                "publicKeyMultibase": key_multibase
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/did+json'}
            mock_response.content = json.dumps(did_document).encode()
            mock_response.json.return_value = did_document
            mock_get.return_value = mock_response

            resolver = DIDResolver()
            # Should auto-detect #owner key
            public_key = resolver.resolve_to_public_key(did)

            assert public_key == test_public_key

    def test_resolve_did_ethr_with_jwk(self):
        """Test did:ethr resolution with publicKeyJwk"""
        test_public_key = b'\x11\x22\x33\x44' * 8  # 32 bytes

        # Encode as JWK (base64url without padding)
        x_b64 = base64.urlsafe_b64encode(test_public_key).decode().rstrip('=')

        did = "did:ethr:mainnet:0x1234567890abcdef1234567890abcdef12345678"
        did_document = {
            "id": did,
            "verificationMethod": [{
                "id": "#key-1",
                "type": "JsonWebKey2020",
                "controller": did,
                "publicKeyJwk": {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": x_b64
                }
            }]
        }

        resolution_result = {
            "didDocument": did_document
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = json.dumps(resolution_result).encode()
            mock_response.json.return_value = resolution_result
            mock_get.return_value = mock_response

            resolver = DIDResolver()
            # Should auto-detect #key-1
            public_key = resolver.resolve_to_public_key(did)

            assert public_key == test_public_key

    def test_resolve_did_ethr_invalid_format(self):
        """Test did:ethr with invalid DID format"""
        with patch('genesisgraph.did_resolver.requests.get'):
            resolver = DIDResolver()

            with pytest.raises(ValidationError, match="Invalid did:ethr format"):
                resolver._resolve_did_ethr("did:ion:EiDahaOGH")

    def test_resolve_did_ethr_network_error(self):
        """Test did:ethr resolution with network error"""
        import requests as req_module
        did = "did:ethr:0xf3beac30c498d9e26865f34fcaa57dbb935b0d74"

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_get.side_effect = req_module.RequestException("Network timeout")

            resolver = DIDResolver()
            with pytest.raises(ValidationError, match="Failed to fetch did:ethr document"):
                resolver.resolve_to_public_key(did)

    def test_resolve_did_ethr_missing_key(self):
        """Test did:ethr resolution when no matching key is found"""
        did = "did:ethr:0xf3beac30c498d9e26865f34fcaa57dbb935b0d74"

        # DID document with no verification methods
        did_document = {
            "id": did,
            "verificationMethod": []
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = json.dumps(did_document).encode()
            mock_response.json.return_value = did_document
            mock_get.return_value = mock_response

            resolver = DIDResolver()
            with pytest.raises(ValidationError, match="Could not find public key"):
                resolver.resolve_to_public_key(did)

    def test_resolve_did_ethr_with_specific_key_id(self):
        """Test did:ethr resolution with specific key ID"""
        test_public_key = b'\xde\xad\xbe\xef' * 8  # 32 bytes

        def base58_encode(data):
            ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(data, 'big')
            result = ''
            while num > 0:
                num, remainder = divmod(num, 58)
                result = ALPHABET[remainder] + result
            return result

        did = "did:ethr:0xf3beac30c498d9e26865f34fcaa57dbb935b0d74"
        did_document = {
            "id": did,
            "verificationMethod": [
                {
                    "id": "#key-1",
                    "type": "Ed25519VerificationKey2020",
                    "controller": did,
                    "publicKeyBase58": base58_encode(b'\x00' * 32)  # Wrong key
                },
                {
                    "id": "#key-2",
                    "type": "Ed25519VerificationKey2020",
                    "controller": did,
                    "publicKeyBase58": base58_encode(test_public_key)  # Correct key
                }
            ]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = json.dumps(did_document).encode()
            mock_response.json.return_value = did_document
            mock_get.return_value = mock_response

            resolver = DIDResolver()
            # Request specific key
            public_key = resolver.resolve_to_public_key(did, '#key-2')

            assert public_key == test_public_key

    def test_resolve_did_ethr_custom_resolver(self):
        """Test did:ethr with custom resolver endpoint"""
        test_public_key = b'\xca\xfe\xba\xbe' * 8  # 32 bytes

        def base58_encode(data):
            ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(data, 'big')
            result = ''
            while num > 0:
                num, remainder = divmod(num, 58)
                result = ALPHABET[remainder] + result
            return result

        did = "did:ethr:0xf3beac30c498d9e26865f34fcaa57dbb935b0d74"
        did_document = {
            "id": did,
            "verificationMethod": [{
                "id": "#controller",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyBase58": base58_encode(test_public_key)
            }]
        }

        custom_resolver_url = "https://custom-resolver.example.com/resolve/"

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = json.dumps(did_document).encode()
            mock_response.json.return_value = did_document
            mock_get.return_value = mock_response

            # Use custom resolver
            resolver = DIDResolver(ethr_resolver=custom_resolver_url)
            public_key = resolver.resolve_to_public_key(did)

            assert public_key == test_public_key
            # Verify custom resolver was used
            args, _ = mock_get.call_args
            assert args[0] == f'{custom_resolver_url}{did}'


class TestDIDCaching:
    """Test caching behavior for did:ion and did:ethr"""

    def test_did_ion_caching(self):
        """Test that did:ion results are cached"""
        did = "did:ion:EiDahaOGH-liLLdDtTxEAdc8i-cfCz-WUcQdRJheMVNn3A"
        test_public_key = b'\x12\x34\x56\x78' * 8

        def base58_encode(data):
            ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(data, 'big')
            result = ''
            while num > 0:
                num, remainder = divmod(num, 58)
                result = ALPHABET[remainder] + result
            return result

        did_document = {
            "id": did,
            "verificationMethod": [{
                "id": "#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyBase58": base58_encode(test_public_key)
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = json.dumps(did_document).encode()
            mock_response.json.return_value = did_document
            mock_get.return_value = mock_response

            resolver = DIDResolver(cache_ttl=300)

            # First call - should hit network
            public_key1 = resolver.resolve_to_public_key(did, '#key-1')
            assert public_key1 == test_public_key
            assert mock_get.call_count == 1

            # Second call - should use cache
            public_key2 = resolver.resolve_to_public_key(did, '#key-1')
            assert public_key2 == test_public_key
            assert mock_get.call_count == 1  # No additional calls

    def test_did_ethr_caching(self):
        """Test that did:ethr results are cached"""
        did = "did:ethr:0xf3beac30c498d9e26865f34fcaa57dbb935b0d74"
        test_public_key = b'\x98\x76\x54\x32' * 8

        def base58_encode(data):
            ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = int.from_bytes(data, 'big')
            result = ''
            while num > 0:
                num, remainder = divmod(num, 58)
                result = ALPHABET[remainder] + result
            return result

        did_document = {
            "id": did,
            "verificationMethod": [{
                "id": "#controller",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyBase58": base58_encode(test_public_key)
            }]
        }

        with patch('genesisgraph.did_resolver.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.content = json.dumps(did_document).encode()
            mock_response.json.return_value = did_document
            mock_get.return_value = mock_response

            resolver = DIDResolver(cache_ttl=300)

            # First call - should hit network
            public_key1 = resolver.resolve_to_public_key(did)
            assert public_key1 == test_public_key
            assert mock_get.call_count == 1

            # Second call - should use cache
            public_key2 = resolver.resolve_to_public_key(did)
            assert public_key2 == test_public_key
            assert mock_get.call_count == 1  # No additional calls
