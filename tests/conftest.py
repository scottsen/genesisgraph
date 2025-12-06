"""
Shared pytest fixtures and test utilities for GenesisGraph tests.

This module provides common fixtures and helper functions to reduce code
duplication across test files.
"""

import json
import os
import tempfile
from unittest.mock import Mock

import pytest
import yaml


# Helper functions
def _base58_encode_impl(data):
    """
    Base58 encode binary data.

    Used for encoding public keys in DID documents and other test scenarios.

    Args:
        data: bytes to encode

    Returns:
        Base58-encoded string
    """
    ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = int.from_bytes(data, 'big')

    # Handle zero case
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


@pytest.fixture
def base58_encode():
    """
    Fixture that provides the base58_encode function.

    Returns the base58_encode function for use in tests.
    """
    return _base58_encode_impl


# Mock response factories
@pytest.fixture
def mock_http_response():
    """
    Factory fixture for creating mock HTTP responses.

    Returns a function that creates Mock response objects with configurable
    status code, content type, and JSON data.

    Usage:
        def test_example(mock_http_response):
            response = mock_http_response(
                status_code=200,
                content_type='application/json',
                json_data={'key': 'value'}
            )
    """
    def _create_response(
        status_code=200,
        content_type='application/json',
        json_data=None,
        content=None
    ):
        """
        Create a mock HTTP response.

        Args:
            status_code: HTTP status code (default: 200)
            content_type: Content-Type header value (default: 'application/json')
            json_data: Dict to be returned by response.json() and encoded as content
            content: Raw bytes content (overrides json_data if provided)

        Returns:
            Mock response object
        """
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.headers = {'Content-Type': content_type}

        if content is not None:
            mock_response.content = content
            if content_type.startswith('application/json'):
                try:
                    mock_response.json.return_value = json.loads(content.decode())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    mock_response.json.return_value = {}
        elif json_data is not None:
            mock_response.json.return_value = json_data
            mock_response.content = json.dumps(json_data).encode()
        else:
            mock_response.content = b''
            mock_response.json.return_value = {}

        return mock_response

    return _create_response


# CLI test fixtures
@pytest.fixture
def valid_gg_file():
    """
    Create a temporary valid GenesisGraph YAML file.

    Yields the file path and automatically cleans up after the test.
    """
    data = {
        'spec_version': '0.1.0',
        'tools': [],
        'entities': [],
        'operations': []
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gg.yaml', delete=False) as f:
        yaml.dump(data, f)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def invalid_gg_file():
    """
    Create a temporary invalid GenesisGraph YAML file (missing spec_version).

    Yields the file path and automatically cleans up after the test.
    """
    data = {
        # Missing spec_version - invalid!
        'tools': [],
        'entities': [],
        'operations': []
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gg.yaml', delete=False) as f:
        yaml.dump(data, f)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def info_gg_file():
    """
    Create a GenesisGraph file with content for testing info command.

    Contains sample profile, tools, entities, and operations.
    Yields the file path and automatically cleans up after the test.
    """
    data = {
        'spec_version': '0.1.0',
        'profile': 'gg-ai-basic-v1',
        'tools': [
            {'id': 'python', 'type': 'Software', 'version': '3.11'},
            {'id': 'pytorch', 'type': 'Software', 'version': '2.0'}
        ],
        'entities': [
            {'id': 'data1', 'type': 'Dataset', 'version': '1.0', 'file': 'test.txt'}
        ],
        'operations': [
            {'id': 'op1', 'type': 'transformation', 'inputs': ['a@1'], 'outputs': ['b@1']},
            {'id': 'op2', 'type': 'inference', 'inputs': ['b@1'], 'outputs': ['c@1']}
        ]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gg.yaml', delete=False) as f:
        yaml.dump(data, f)
        yield f.name
    os.unlink(f.name)
