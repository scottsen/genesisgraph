"""
Security tests for GenesisGraph

Tests security vulnerabilities and mitigations including:
- Path traversal attacks
- SSRF attacks in DID resolution
- DoS via large inputs
- Input validation bypasses
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock

from genesisgraph.validator import GenesisGraphValidator, MAX_ENTITIES, MAX_OPERATIONS, MAX_ID_LENGTH
from genesisgraph.did_resolver import DIDResolver, BLOCKED_HOSTS, BLOCKED_NETWORKS
from genesisgraph.errors import ValidationError


class TestPathTraversalProtection:
    """Test path traversal attack prevention"""

    def test_parent_directory_reference_blocked(self):
        """Test that ../ references are blocked"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid document file
            doc_path = os.path.join(tmpdir, 'test.gg.yaml')
            with open(doc_path, 'w') as f:
                f.write('')

            # Try to access parent directory
            data = {
                'spec_version': '0.1.0',
                'entities': [
                    {
                        'id': 'malicious',
                        'type': 'File',
                        'version': '1',
                        'file': '../../../etc/passwd',
                        'hash': 'sha256:' + '0' * 64
                    }
                ],
                'operations': [],
                'tools': []
            }

            validator = GenesisGraphValidator()
            result = validator.validate(data, file_path=doc_path)

            assert not result.is_valid
            assert any('parent directory' in err.lower() for err in result.errors)

    def test_absolute_path_blocked(self):
        """Test that absolute paths are blocked"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = os.path.join(tmpdir, 'test.gg.yaml')
            with open(doc_path, 'w') as f:
                f.write('')

            # Try to use absolute path
            data = {
                'spec_version': '0.1.0',
                'entities': [
                    {
                        'id': 'malicious',
                        'type': 'File',
                        'version': '1',
                        'file': '/etc/passwd',
                        'hash': 'sha256:' + '0' * 64
                    }
                ],
                'operations': [],
                'tools': []
            }

            validator = GenesisGraphValidator()
            result = validator.validate(data, file_path=doc_path)

            assert not result.is_valid
            assert any('absolute path' in err.lower() for err in result.errors)

    def test_path_traversal_with_normalized_path(self):
        """Test path traversal using various encoding"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = os.path.join(tmpdir, 'test.gg.yaml')
            with open(doc_path, 'w') as f:
                f.write('')

            # Try various path traversal techniques
            malicious_paths = [
                '../../etc/passwd',
                './../../../etc/passwd',
                'subdir/../../etc/passwd',
                './../../etc/passwd',
            ]

            for malicious_path in malicious_paths:
                data = {
                    'spec_version': '0.1.0',
                    'entities': [
                        {
                            'id': 'malicious',
                            'type': 'File',
                            'version': '1',
                            'file': malicious_path,
                            'hash': 'sha256:' + '0' * 64
                        }
                    ],
                    'operations': [],
                    'tools': []
                }

                validator = GenesisGraphValidator()
                result = validator.validate(data, file_path=doc_path)

                assert not result.is_valid, f"Path traversal not blocked: {malicious_path}"
                assert any(
                    'parent directory' in err.lower() or 'traversal' in err.lower()
                    for err in result.errors
                ), f"Wrong error for path: {malicious_path}"

    def test_valid_relative_path_allowed(self):
        """Test that valid relative paths are allowed"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = os.path.join(tmpdir, 'test.gg.yaml')
            test_file = os.path.join(tmpdir, 'data.txt')

            with open(doc_path, 'w') as f:
                f.write('')
            with open(test_file, 'w') as f:
                f.write('test data')

            data = {
                'spec_version': '0.1.0',
                'entities': [
                    {
                        'id': 'safe',
                        'type': 'File',
                        'version': '1',
                        'file': 'data.txt',
                        'hash': 'sha256:' + '0' * 64  # Wrong hash, but path should be allowed
                    }
                ],
                'operations': [],
                'tools': []
            }

            validator = GenesisGraphValidator()
            result = validator.validate(data, file_path=doc_path)

            # Should fail on hash mismatch, not path traversal
            if not result.is_valid:
                assert not any(
                    'traversal' in err.lower() or 'absolute path' in err.lower()
                    for err in result.errors
                )


class TestSSRFProtection:
    """Test SSRF protection in DID resolver"""

    def test_localhost_blocked(self):
        """Test that localhost is blocked"""
        resolver = DIDResolver()

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:localhost:test')

        assert 'blocked host' in str(exc_info.value).lower()

    def test_127_0_0_1_blocked(self):
        """Test that 127.0.0.1 is blocked"""
        resolver = DIDResolver()

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:127.0.0.1:test')

        assert 'blocked host' in str(exc_info.value).lower()

    def test_aws_metadata_service_blocked(self):
        """Test that AWS metadata service IP is blocked"""
        resolver = DIDResolver()

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:169.254.169.254:latest:meta-data')

        assert 'blocked host' in str(exc_info.value).lower()

    def test_private_network_10_blocked(self):
        """Test that 10.0.0.0/8 network is blocked"""
        resolver = DIDResolver()

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:10.0.0.1:test')

        assert 'blocked host' in str(exc_info.value).lower()

    def test_private_network_192_168_blocked(self):
        """Test that 192.168.0.0/16 network is blocked"""
        resolver = DIDResolver()

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:192.168.1.1:test')

        assert 'blocked host' in str(exc_info.value).lower()

    def test_private_network_172_16_blocked(self):
        """Test that 172.16.0.0/12 network is blocked"""
        resolver = DIDResolver()

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:172.16.0.1:test')

        assert 'blocked host' in str(exc_info.value).lower()

    def test_ipv6_localhost_blocked(self):
        """Test that IPv6 localhost is blocked"""
        # Note: did:web doesn't have a standard way to represent IPv6 addresses
        # We test that the blocking logic works when called directly
        resolver = DIDResolver()

        # Test the blocking function directly
        assert resolver._is_blocked_host('::1')
        assert resolver._is_blocked_host('::ffff:127.0.0.1')


class TestRateLimiting:
    """Test rate limiting in DID resolver"""

    @patch('genesisgraph.did_resolver.requests.get')
    def test_rate_limit_enforced(self, mock_get):
        """Test that rate limiting is enforced"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.content = b'{"verificationMethod": []}'
        mock_response.json.return_value = {"verificationMethod": []}
        mock_get.return_value = mock_response

        resolver = DIDResolver(rate_limit=5)

        # Make requests up to the limit
        for i in range(5):
            try:
                resolver.resolve_to_public_key(f'did:web:example.com:user{i}')
            except ValidationError:
                pass  # We expect key extraction to fail, but not rate limiting

        # Next request should be rate limited
        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:example.com:user6')

        assert 'rate limit' in str(exc_info.value).lower()


class TestCacheTTL:
    """Test cache TTL implementation"""

    def test_cache_expires_after_ttl(self):
        """Test that cache entries expire after TTL"""
        resolver = DIDResolver(cache_ttl=1)  # 1 second TTL

        # Resolve a did:key (doesn't require network)
        did = 'did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK'
        result1 = resolver.resolve_to_public_key(did)

        # Should be cached
        assert did in resolver._cache

        # Simulate time passing
        import time
        cached_value, cached_time = resolver._cache[did]
        resolver._cache[did] = (cached_value, cached_time - 2)  # Expire the cache

        # Next resolution should not use expired cache
        result2 = resolver.resolve_to_public_key(did)

        # Results should be same (same DID), but cache was refreshed
        assert result1 == result2


class TestDoSProtection:
    """Test DoS protection via input limits"""

    def test_too_many_entities_rejected(self):
        """Test that documents with too many entities are rejected"""
        data = {
            'spec_version': '0.1.0',
            'entities': [
                {
                    'id': f'entity_{i}',
                    'type': 'File',
                    'version': '1',
                    'uri': f'http://example.com/file{i}'
                }
                for i in range(MAX_ENTITIES + 1)
            ],
            'operations': [],
            'tools': []
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('too many entities' in err.lower() for err in result.errors)

    def test_too_many_operations_rejected(self):
        """Test that documents with too many operations are rejected"""
        data = {
            'spec_version': '0.1.0',
            'entities': [],
            'operations': [
                {
                    'id': f'op_{i}',
                    'type': 'Transform',
                    'inputs': [],
                    'outputs': []
                }
                for i in range(MAX_OPERATIONS + 1)
            ],
            'tools': []
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('too many operations' in err.lower() for err in result.errors)

    def test_id_too_long_rejected(self):
        """Test that IDs that are too long are rejected"""
        data = {
            'spec_version': '0.1.0',
            'entities': [
                {
                    'id': 'x' * (MAX_ID_LENGTH + 1),
                    'type': 'File',
                    'version': '1',
                    'uri': 'http://example.com/file'
                }
            ],
            'operations': [],
            'tools': []
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('too long' in err.lower() for err in result.errors)

    def test_base58_too_long_rejected(self):
        """Test that overly long base58 strings are rejected"""
        from genesisgraph.did_resolver import DIDResolver, MAX_BASE58_LENGTH

        resolver = DIDResolver()
        long_base58 = '1' * (MAX_BASE58_LENGTH + 1)
        malicious_did = f'did:key:z{long_base58}'

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key(malicious_did)

        assert 'too long' in str(exc_info.value).lower()

    def test_did_too_long_rejected(self):
        """Test that overly long DIDs are rejected"""
        from genesisgraph.did_resolver import DIDResolver, MAX_DID_LENGTH

        resolver = DIDResolver()
        long_did = 'did:key:' + 'z' * (MAX_DID_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key(long_did)

        assert 'too long' in str(exc_info.value).lower()


class TestContentTypeValidation:
    """Test Content-Type validation for DID web resolution"""

    @patch('genesisgraph.did_resolver.requests.get')
    def test_invalid_content_type_rejected(self, mock_get):
        """Test that non-JSON content types are rejected"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.content = b'<html>Not JSON</html>'
        mock_get.return_value = mock_response

        resolver = DIDResolver()

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:example.com')

        assert 'content type' in str(exc_info.value).lower()

    @patch('genesisgraph.did_resolver.requests.get')
    def test_valid_content_type_accepted(self, mock_get):
        """Test that valid JSON content types are accepted"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.content = b'{"verificationMethod": []}'
        mock_response.json.return_value = {"verificationMethod": []}
        mock_get.return_value = mock_response

        resolver = DIDResolver()

        # Should not raise content type error (will raise key not found)
        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:example.com')

        # Error should be about missing key, not content type
        assert 'content type' not in str(exc_info.value).lower()

    @patch('genesisgraph.did_resolver.requests.get')
    def test_response_size_limit_enforced(self, mock_get):
        """Test that overly large responses are rejected"""
        from genesisgraph.did_resolver import MAX_RESPONSE_SIZE

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.content = b'x' * (MAX_RESPONSE_SIZE + 1)
        mock_get.return_value = mock_response

        resolver = DIDResolver()

        with pytest.raises(ValidationError) as exc_info:
            resolver.resolve_to_public_key('did:web:example.com')

        assert 'too large' in str(exc_info.value).lower()


class TestTLSValidation:
    """Test TLS certificate validation"""

    @patch('genesisgraph.did_resolver.requests.get')
    def test_verify_tls_enabled(self, mock_get):
        """Test that TLS verification is enabled"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.content = b'{"verificationMethod": []}'
        mock_response.json.return_value = {"verificationMethod": []}
        mock_get.return_value = mock_response

        resolver = DIDResolver()

        try:
            resolver.resolve_to_public_key('did:web:example.com')
        except ValidationError:
            pass  # Expected to fail on key extraction

        # Verify that requests.get was called with verify=True
        mock_get.assert_called()
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs.get('verify') is True

    @patch('genesisgraph.did_resolver.requests.get')
    def test_redirects_disabled(self, mock_get):
        """Test that redirects are disabled"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.content = b'{"verificationMethod": []}'
        mock_response.json.return_value = {"verificationMethod": []}
        mock_get.return_value = mock_response

        resolver = DIDResolver()

        try:
            resolver.resolve_to_public_key('did:web:example.com')
        except ValidationError:
            pass  # Expected to fail on key extraction

        # Verify that requests.get was called with allow_redirects=False
        mock_get.assert_called()
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs.get('allow_redirects') is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
