"""Tests for GenesisGraph validator"""

import pytest
from genesisgraph import GenesisGraphValidator, validate
from genesisgraph.errors import ValidationError, SchemaError


class TestGenesisGraphValidator:
    """Test GenesisGraphValidator class"""

    def test_validator_creation(self):
        """Test creating a validator"""
        validator = GenesisGraphValidator()
        assert validator is not None

    def test_validate_minimal_document(self):
        """Test validating a minimal valid document"""
        data = {
            'spec_version': '0.1.0',
            'tools': [],
            'entities': [],
            'operations': []
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_spec_version(self):
        """Test document missing spec_version"""
        data = {
            'tools': [],
            'entities': [],
            'operations': []
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('spec_version' in error for error in result.errors)

    def test_invalid_spec_version_format(self):
        """Test invalid spec_version format"""
        data = {
            'spec_version': 'invalid',
            'tools': [],
            'entities': [],
            'operations': []
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        # Should pass validation but have a warning
        assert result.is_valid
        assert any('semver' in warning.lower() for warning in result.warnings)

    def test_validate_entity_with_id(self):
        """Test entity with required fields"""
        data = {
            'spec_version': '0.1.0',
            'entities': [
                {
                    'id': 'test_entity',
                    'type': 'Dataset',
                    'version': '1.0',
                    'file': 'test.txt',
                    'hash': 'sha256:' + '0' * 64
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert result.is_valid

    def test_entity_missing_id(self):
        """Test entity without id"""
        data = {
            'spec_version': '0.1.0',
            'entities': [
                {
                    'type': 'Dataset',
                    'version': '1.0',
                    'file': 'test.txt'
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('id' in error.lower() for error in result.errors)

    def test_entity_missing_type(self):
        """Test entity without type"""
        data = {
            'spec_version': '0.1.0',
            'entities': [
                {
                    'id': 'test',
                    'version': '1.0',
                    'file': 'test.txt'
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('type' in error for error in result.errors)

    def test_entity_duplicate_id(self):
        """Test duplicate entity IDs"""
        data = {
            'spec_version': '0.1.0',
            'entities': [
                {
                    'id': 'test',
                    'type': 'Dataset',
                    'version': '1.0',
                    'file': 'test1.txt'
                },
                {
                    'id': 'test',
                    'type': 'Dataset',
                    'version': '2.0',
                    'file': 'test2.txt'
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('duplicate' in error.lower() for error in result.errors)

    def test_entity_invalid_hash_format(self):
        """Test entity with invalid hash format"""
        data = {
            'spec_version': '0.1.0',
            'entities': [
                {
                    'id': 'test',
                    'type': 'Dataset',
                    'version': '1.0',
                    'file': 'test.txt',
                    'hash': 'invalid_hash'
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('hash' in error.lower() for error in result.errors)

    def test_entity_needs_file_or_uri(self):
        """Test entity must have file or uri"""
        data = {
            'spec_version': '0.1.0',
            'entities': [
                {
                    'id': 'test',
                    'type': 'Dataset',
                    'version': '1.0'
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('file' in error.lower() or 'uri' in error.lower()
                   for error in result.errors)

    def test_operation_basic(self):
        """Test basic operation validation"""
        data = {
            'spec_version': '0.1.0',
            'operations': [
                {
                    'id': 'op1',
                    'type': 'transformation',
                    'inputs': ['a@1'],
                    'outputs': ['b@1']
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert result.is_valid

    def test_operation_missing_id(self):
        """Test operation without id"""
        data = {
            'spec_version': '0.1.0',
            'operations': [
                {
                    'type': 'transformation',
                    'inputs': ['a@1'],
                    'outputs': ['b@1']
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid

    def test_operation_duplicate_id(self):
        """Test duplicate operation IDs"""
        data = {
            'spec_version': '0.1.0',
            'operations': [
                {'id': 'op1', 'type': 'transform', 'inputs': ['a@1'], 'outputs': ['b@1']},
                {'id': 'op1', 'type': 'transform', 'inputs': ['b@1'], 'outputs': ['c@1']},
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('duplicate' in error.lower() for error in result.errors)

    def test_sealed_subgraph_no_inputs_required(self):
        """Test sealed_subgraph doesn't require inputs/outputs"""
        data = {
            'spec_version': '0.1.0',
            'operations': [
                {
                    'id': 'sealed_op',
                    'type': 'sealed_subgraph',
                    'sealed': {
                        'merkle_root': 'sha256:' + '0' * 64
                    }
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert result.is_valid

    def test_tool_basic(self):
        """Test basic tool validation"""
        data = {
            'spec_version': '0.1.0',
            'tools': [
                {
                    'id': 'python',
                    'type': 'Software',
                    'version': '3.11'
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert result.is_valid

    def test_tool_invalid_type(self):
        """Test tool with invalid type"""
        data = {
            'spec_version': '0.1.0',
            'tools': [
                {
                    'id': 'invalid',
                    'type': 'InvalidType'
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('invalid type' in error.lower() for error in result.errors)

    def test_attestation_basic_mode(self):
        """Test basic attestation mode"""
        data = {
            'spec_version': '0.1.0',
            'operations': [
                {
                    'id': 'op1',
                    'type': 'transform',
                    'inputs': ['a@1'],
                    'outputs': ['b@1'],
                    'attestation': {
                        'mode': 'basic',
                        'timestamp': '2025-10-31T10:00:00Z'
                    }
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert result.is_valid

    def test_attestation_signed_requires_signer(self):
        """Test signed attestation requires signer"""
        data = {
            'spec_version': '0.1.0',
            'operations': [
                {
                    'id': 'op1',
                    'type': 'transform',
                    'inputs': ['a@1'],
                    'outputs': ['b@1'],
                    'attestation': {
                        'mode': 'signed',
                        'timestamp': '2025-10-31T10:00:00Z'
                    }
                }
            ]
        }

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert not result.is_valid
        assert any('signer' in error.lower() for error in result.errors)

    def test_validation_result_bool(self):
        """Test ValidationResult bool conversion"""
        data = {'spec_version': '0.1.0'}

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        assert bool(result) is True
        assert result.is_valid is True

    def test_validation_result_format_report(self):
        """Test ValidationResult format_report"""
        data = {'spec_version': '0.1.0'}

        validator = GenesisGraphValidator()
        result = validator.validate(data)

        report = result.format_report()
        assert '✓' in report or 'PASSED' in report


class TestValidateFunction:
    """Test the validate convenience function"""

    def test_validate_function_nonexistent_file(self):
        """Test validate function with nonexistent file"""
        result = validate('nonexistent.yaml')

        assert not result.is_valid
        assert len(result.errors) > 0


class TestExampleFiles:
    """Test validation of example files"""

    def test_level_a_example_structure(self):
        """Test level A example has valid structure (ignoring file refs)"""
        import yaml
        with open('examples/level-a-full-disclosure.gg.yaml', 'r') as f:
            data = yaml.safe_load(f)

        # Basic structure checks
        assert 'spec_version' in data
        assert 'entities' in data
        assert 'operations' in data
        assert 'tools' in data

        # Check it has expected content
        assert len(data['entities']) == 6
        assert len(data['operations']) == 4
        assert len(data['tools']) == 4

    def test_level_b_example_structure(self):
        """Test level B example has valid structure"""
        import yaml
        with open('examples/level-b-partial-envelope.gg.yaml', 'r') as f:
            data = yaml.safe_load(f)

        # Basic structure checks
        assert 'spec_version' in data
        assert data.get('profile') == 'gg-ai-basic-v1'
        assert len(data.get('entities', [])) == 5
        assert len(data.get('operations', [])) == 4

    def test_level_c_example_structure(self):
        """Test level C example has valid structure"""
        import yaml
        with open('examples/level-c-sealed-subgraph.gg.yaml', 'r') as f:
            data = yaml.safe_load(f)

        # Basic structure checks
        assert 'spec_version' in data
        assert data.get('profile') == 'gg-cam-v1'

        # Check for sealed operation
        ops = data.get('operations', [])
        sealed_ops = [op for op in ops if op.get('type') == 'sealed_subgraph']
        assert len(sealed_ops) == 1

        # Check sealed operation has required fields
        sealed_op = sealed_ops[0]
        assert 'sealed' in sealed_op
        assert 'merkle_root' in sealed_op['sealed']
