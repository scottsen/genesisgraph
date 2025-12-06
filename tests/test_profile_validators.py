"""
Tests for industry-specific profile validators
"""

from genesisgraph.compliance import FDA21CFR11Validator, ISO9001Validator
from genesisgraph.profiles import ProfileRegistry
from genesisgraph.profiles.ai_basic_v1 import AIBasicV1Validator
from genesisgraph.profiles.cam_v1 import CAMv1Validator


class TestAIBasicV1Validator:
    """Tests for AI Basic v1 profile validator"""

    def test_valid_ai_inference_operation(self):
        """Test validation of a valid AI inference operation"""
        validator = AIBasicV1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [
                {
                    'id': 'dataset1',
                    'type': 'Dataset',
                    'version': '1.0',
                    'hash': 'sha256:abc123',
                    'file': 'data.json'
                },
                {
                    'id': 'model1',
                    'type': 'Model',
                    'version': '2.0',
                    'hash': 'sha256:def456',
                    'file': 'model.pkl'
                }
            ],
            'operations': [
                {
                    'id': 'inference1',
                    'type': 'ai_inference',
                    'inputs': ['dataset1'],
                    'outputs': ['model1'],
                    'tool': 'gpt4',
                    'parameters': {
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'prompt_length_chars': 1024,
                        'model_name': 'gpt-4',
                        'model_version': '2024-01'
                    },
                    'attestation': {
                        'mode': 'signed',
                        'attester': 'did:example:123',
                        'timestamp': '2024-01-01T00:00:00Z'
                    }
                }
            ],
            'tools': [
                {
                    'id': 'gpt4',
                    'type': 'AIModel',
                    'version': '2024-01',
                    'did': 'did:example:openai'
                }
            ]
        }

        result = validator.validate_profile(data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_required_parameters(self):
        """Test validation fails when required parameters are missing"""
        validator = AIBasicV1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [],
            'operations': [
                {
                    'id': 'inference1',
                    'type': 'ai_inference',
                    'inputs': [],
                    'outputs': [],
                    'parameters': {
                        'temperature': 0.7
                        # Missing top_p, prompt_length_chars, model_name, model_version
                    }
                }
            ],
            'tools': []
        }

        result = validator.validate_profile(data)
        assert not result.is_valid
        assert len(result.errors) >= 4  # Missing 4+ parameters

    def test_invalid_temperature_range(self):
        """Test validation fails for temperature outside valid range"""
        validator = AIBasicV1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [],
            'operations': [
                {
                    'id': 'inference1',
                    'type': 'ai_inference',
                    'inputs': [],
                    'outputs': [],
                    'parameters': {
                        'temperature': 3.0,  # Invalid: > 2.0
                        'top_p': 0.9,
                        'prompt_length_chars': 1024,
                        'model_name': 'gpt-4',
                        'model_version': '2024-01'
                    }
                }
            ],
            'tools': []
        }

        result = validator.validate_profile(data)
        assert not result.is_valid
        assert any('temperature' in error for error in result.errors)

    def test_dataset_without_hash(self):
        """Test warning for dataset without hash"""
        validator = AIBasicV1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [
                {
                    'id': 'dataset1',
                    'type': 'Dataset',
                    'version': '1.0',
                    'file': 'data.json'
                    # Missing hash
                }
            ],
            'operations': [],
            'tools': []
        }

        result = validator.validate_profile(data)
        assert not result.is_valid
        assert any('hash' in error.lower() for error in result.errors)

    def test_redacted_parameters_skip_validation(self):
        """Test that redacted parameters skip validation"""
        validator = AIBasicV1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [],
            'operations': [
                {
                    'id': 'inference1',
                    'type': 'ai_inference',
                    'inputs': [],
                    'outputs': [],
                    'parameters': {
                        '_redacted': True
                    }
                }
            ],
            'tools': []
        }

        result = validator.validate_profile(data)
        assert result.is_valid
        assert len(result.errors) == 0


class TestCAMv1Validator:
    """Tests for Computer-Aided Manufacturing v1 profile validator"""

    def test_valid_cnc_machining_operation(self):
        """Test validation of a valid CNC machining operation"""
        validator = CAMv1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [
                {
                    'id': 'cad1',
                    'type': 'CADModel',
                    'version': '1.0',
                    'hash': 'sha256:abc123',
                    'file': 'part.step'
                }
            ],
            'operations': [
                {
                    'id': 'cnc1',
                    'type': 'cnc_machining',
                    'inputs': ['cad1'],
                    'outputs': ['part1'],
                    'tool': 'machine1',
                    'parameters': {
                        'tolerance_mm': 0.05,
                        'material': 'aluminum-6061',
                        'feed_rate_mm_per_min': 1000,
                        'spindle_speed_rpm': 3000,
                        'tool_number': 5,
                        'post_processor': 'fanuc'
                    },
                    'attestation': {
                        'mode': 'signed',
                        'attester': 'did:example:operator',
                        'timestamp': '2024-01-01T00:00:00Z'
                    }
                },
                {
                    'id': 'qc1',
                    'type': 'quality_inspection',
                    'inputs': ['part1'],
                    'outputs': ['part1_approved'],
                    'parameters': {
                        'inspection_type': 'dimensional',
                        'acceptance_criteria': 'ISO-9001',
                        'measurement_uncertainty_mm': 0.01
                    },
                    'attestation': {
                        'mode': 'signed',
                        'signer': 'did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK',
                        'signature': 'mockbase64signature==',
                        'timestamp': '2024-01-15T10:00:00Z'
                    }
                }
            ],
            'tools': [
                {
                    'id': 'machine1',
                    'type': 'Machine',
                    'did': 'did:example:cnc-mill',
                    'metadata': {
                        'calibration_date': '2024-01-01',
                        'last_maintenance_date': '2024-01-01'
                    }
                }
            ],
            'metadata': {
                'quality_standard': 'ISO-9001:2015',
                'part_number': 'PN-12345'
            }
        }

        result = validator.validate_profile(data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_cnc_parameters(self):
        """Test validation fails when required CNC parameters are missing"""
        validator = CAMv1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [],
            'operations': [
                {
                    'id': 'cnc1',
                    'type': 'cnc_machining',
                    'inputs': [],
                    'outputs': [],
                    'parameters': {
                        'tolerance_mm': 0.05
                        # Missing material, feed_rate, spindle_speed, tool_number
                    }
                }
            ],
            'tools': []
        }

        result = validator.validate_profile(data)
        assert not result.is_valid
        assert len(result.errors) >= 4

    def test_negative_tolerance(self):
        """Test validation fails for negative tolerance"""
        validator = CAMv1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [],
            'operations': [
                {
                    'id': 'cnc1',
                    'type': 'cnc_machining',
                    'inputs': [],
                    'outputs': [],
                    'parameters': {
                        'tolerance_mm': -0.05,  # Invalid: negative
                        'material': 'aluminum',
                        'feed_rate_mm_per_min': 1000,
                        'spindle_speed_rpm': 3000,
                        'tool_number': 1
                    }
                }
            ],
            'tools': []
        }

        result = validator.validate_profile(data)
        assert not result.is_valid
        assert any('tolerance' in error.lower() for error in result.errors)

    def test_cad_model_without_hash(self):
        """Test error for CAD model without hash (ISO-9001 requirement)"""
        validator = CAMv1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [
                {
                    'id': 'cad1',
                    'type': 'CADModel',
                    'version': '1.0',
                    'file': 'part.step'
                    # Missing hash - ISO-9001 violation
                }
            ],
            'operations': [],
            'tools': []
        }

        result = validator.validate_profile(data)
        assert not result.is_valid
        assert any('hash' in error.lower() and 'iso-9001' in error.lower()
                  for error in result.errors)

    def test_critical_operation_without_attestation(self):
        """Test error for critical manufacturing operation without attestation"""
        validator = CAMv1Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [],
            'operations': [
                {
                    'id': 'cnc1',
                    'type': 'cnc_machining',
                    'inputs': [],
                    'outputs': [],
                    'parameters': {
                        'tolerance_mm': 0.05,
                        'material': 'aluminum',
                        'feed_rate_mm_per_min': 1000,
                        'spindle_speed_rpm': 3000,
                        'tool_number': 1
                    }
                    # Missing attestation - ISO-9001 requirement
                }
            ],
            'tools': []
        }

        result = validator.validate_profile(data)
        assert not result.is_valid
        assert any('attestation' in error.lower() for error in result.errors)


class TestProfileRegistry:
    """Tests for profile registry"""

    def test_registry_initialization(self):
        """Test profile registry initializes with built-in profiles"""
        registry = ProfileRegistry()

        profiles = registry.list_profiles()
        assert 'gg-ai-basic-v1' in profiles
        assert 'gg-cam-v1' in profiles

    def test_get_validator(self):
        """Test getting a validator by profile ID"""
        registry = ProfileRegistry()

        validator = registry.get_validator('gg-ai-basic-v1')
        assert validator is not None
        assert isinstance(validator, AIBasicV1Validator)

    def test_auto_detect_ai_profile(self):
        """Test auto-detection of AI profile"""
        registry = ProfileRegistry()

        data = {
            'spec_version': '0.2.0',
            'entities': [],
            'operations': [
                {'id': 'op1', 'type': 'ai_inference', 'inputs': [], 'outputs': []}
            ],
            'tools': []
        }

        profile_id = registry._detect_profile(data)
        assert profile_id == 'gg-ai-basic-v1'

    def test_auto_detect_cam_profile(self):
        """Test auto-detection of manufacturing profile"""
        registry = ProfileRegistry()

        data = {
            'spec_version': '0.2.0',
            'entities': [],
            'operations': [
                {'id': 'op1', 'type': 'cnc_machining', 'inputs': [], 'outputs': []}
            ],
            'tools': []
        }

        profile_id = registry._detect_profile(data)
        assert profile_id == 'gg-cam-v1'

    def test_explicit_profile_in_metadata(self):
        """Test explicit profile declaration in metadata"""
        registry = ProfileRegistry()

        data = {
            'spec_version': '0.2.0',
            'metadata': {
                'profile': 'gg-ai-basic-v1'
            },
            'entities': [],
            'operations': [],
            'tools': []
        }

        profile_id = registry._detect_profile(data)
        assert profile_id == 'gg-ai-basic-v1'


class TestISO9001Validator:
    """Tests for ISO 9001 compliance validator"""

    def test_compliant_workflow(self):
        """Test a fully compliant ISO 9001 workflow"""
        validator = ISO9001Validator()

        data = {
            'spec_version': '0.2.0',
            'metadata': {
                'description': 'Manufacturing workflow for Part XYZ',
                'version': '1.0.0',
                'author': 'Acme Manufacturing',
                'quality_standard': 'ISO-9001:2015',
                'part_number': 'PN-12345',
                'approved_by': 'John Smith'
            },
            'entities': [
                {
                    'id': 'material1',
                    'type': 'Material',
                    'version': '1.0',
                    'metadata': {
                        'lot_number': 'LOT-2024-001',
                        'supplier': 'Material Corp'
                    },
                    'file': 'material.json'
                }
            ],
            'operations': [
                {
                    'id': 'qc1',
                    'type': 'quality_inspection',
                    'inputs': ['material1'],
                    'outputs': ['material1_approved'],
                    'attestation': {
                        'mode': 'signed',
                        'attester': 'did:example:inspector',
                        'timestamp': '2024-01-01T00:00:00Z'
                    }
                }
            ],
            'tools': [
                {
                    'id': 'machine1',
                    'type': 'Machine',
                    'did': 'did:example:machine',
                    'metadata': {
                        'calibration_date': '2024-01-01',
                        'last_maintenance': '2024-01-01'
                    }
                }
            ]
        }

        result = validator.validate(data)
        assert result['is_valid']
        assert result['compliance_level'] in ['fully-compliant', 'substantially-compliant']


class TestFDA21CFR11Validator:
    """Tests for FDA 21 CFR Part 11 compliance validator"""

    def test_compliant_workflow(self):
        """Test a compliant FDA 21 CFR Part 11 workflow"""
        validator = FDA21CFR11Validator()

        data = {
            'spec_version': '0.2.0',
            'metadata': {
                'system_validation': {
                    'validation_protocol': 'VP-2024-001',
                    'validation_date': '2024-01-01'
                },
                'transparency_log': {
                    'log_url': 'https://ct.example.com'
                }
            },
            'entities': [
                {
                    'id': 'dataset1',
                    'type': 'Dataset',
                    'version': '1.0',
                    'hash': 'sha256:abc123',  # Strong hash
                    'file': 'data.json'
                }
            ],
            'operations': [
                {
                    'id': 'inference1',
                    'type': 'ai_inference',
                    'inputs': ['dataset1'],
                    'outputs': ['result1'],
                    'attestation': {
                        'mode': 'signed',
                        'attester': 'did:example:operator',
                        'timestamp': '2024-01-01T00:00:00Z',
                        'claim': 'Performed AI inference according to protocol',
                        'signature': 'base64-signature',
                        'algorithm': 'Ed25519'
                    }
                }
            ],
            'tools': []
        }

        result = validator.validate(data)
        assert result['is_valid']
        assert result['compliance_level'] in ['fully-compliant', 'substantially-compliant']

    def test_missing_hash_on_critical_entity(self):
        """Test failure when critical entity lacks hash"""
        validator = FDA21CFR11Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [
                {
                    'id': 'dataset1',
                    'type': 'Dataset',
                    'version': '1.0',
                    'file': 'data.json'
                    # Missing hash - 21 CFR §11.10(c) violation
                }
            ],
            'operations': [],
            'tools': []
        }

        result = validator.validate(data)
        assert not result['is_valid']
        assert any('11.10(c)' in error for error in result['errors'])

    def test_missing_attestation_timestamp(self):
        """Test failure when attestation lacks timestamp"""
        validator = FDA21CFR11Validator()

        data = {
            'spec_version': '0.2.0',
            'entities': [],
            'operations': [
                {
                    'id': 'op1',
                    'type': 'ai_inference',
                    'inputs': [],
                    'outputs': [],
                    'attestation': {
                        'mode': 'signed',
                        'attester': 'did:example:operator'
                        # Missing timestamp - 21 CFR §11.50 violation
                    }
                }
            ],
            'tools': []
        }

        result = validator.validate(data)
        assert not result['is_valid']
        assert any('timestamp' in error.lower() for error in result['errors'])
