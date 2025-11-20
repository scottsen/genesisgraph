"""
Profile Registry

Manages discovery and execution of industry-specific profile validators.
"""

from typing import Dict, List, Optional, Type
from .base import BaseProfileValidator, ProfileValidationResult
from .ai_basic_v1 import AIBasicV1Validator
from .cam_v1 import CAMv1Validator


class ProfileRegistry:
    """
    Registry for profile validators

    Manages profile discovery, registration, and execution.
    Supports both built-in profiles and custom profile plugins.
    """

    def __init__(self):
        """Initialize the profile registry"""
        self._validators: Dict[str, Type[BaseProfileValidator]] = {}
        self._register_builtin_profiles()

    def _register_builtin_profiles(self):
        """Register built-in profile validators"""
        self.register(AIBasicV1Validator)
        self.register(CAMv1Validator)

    def register(self, validator_class: Type[BaseProfileValidator]):
        """
        Register a profile validator class

        Args:
            validator_class: Profile validator class (subclass of BaseProfileValidator)
        """
        # Create temporary instance to get profile_id
        temp_instance = validator_class()
        profile_id = temp_instance.profile_id

        self._validators[profile_id] = validator_class

    def get_validator(self, profile_id: str) -> Optional[BaseProfileValidator]:
        """
        Get a validator instance for a profile

        Args:
            profile_id: Profile identifier (e.g., "gg-ai-basic-v1")

        Returns:
            Validator instance or None if profile not found
        """
        validator_class = self._validators.get(profile_id)
        if validator_class:
            return validator_class()
        return None

    def list_profiles(self) -> List[str]:
        """
        List all registered profile IDs

        Returns:
            List of profile identifiers
        """
        return list(self._validators.keys())

    def validate_with_profile(
        self,
        data: Dict,
        profile_id: Optional[str] = None
    ) -> ProfileValidationResult:
        """
        Validate data with a specific profile or auto-detect profile

        Args:
            data: Parsed GenesisGraph document
            profile_id: Optional profile ID. If None, attempts auto-detection.

        Returns:
            ProfileValidationResult
        """
        # Auto-detect profile if not specified
        if profile_id is None:
            profile_id = self._detect_profile(data)

        if profile_id is None:
            # No profile detected or specified
            return ProfileValidationResult(
                is_valid=True,
                errors=[],
                warnings=["No profile specified or detected - skipping profile validation"],
                profile_id="none",
                profile_version="0.0.0"
            )

        # Get validator
        validator = self.get_validator(profile_id)
        if validator is None:
            return ProfileValidationResult(
                is_valid=False,
                errors=[f"Profile '{profile_id}' not found in registry"],
                warnings=[],
                profile_id=profile_id,
                profile_version="unknown"
            )

        # Run validation
        return validator.validate_profile(data)

    def _detect_profile(self, data: Dict) -> Optional[str]:
        """
        Auto-detect the appropriate profile based on workflow content

        Args:
            data: Parsed GenesisGraph document

        Returns:
            Detected profile ID or None
        """
        # Check metadata for explicit profile declaration
        metadata = data.get('metadata', {})
        if 'profile' in metadata:
            return metadata['profile']

        # Auto-detect based on operation types
        operations = data.get('operations', [])
        op_types = {op.get('type') for op in operations}

        # AI profile indicators
        ai_ops = {'ai_inference', 'ai_retrieval', 'ai_moderation', 'ai_training'}
        if op_types & ai_ops:
            return 'gg-ai-basic-v1'

        # Manufacturing profile indicators
        cam_ops = {'cnc_machining', 'additive_manufacturing', 'tessellation',
                  'slicing', 'post_processing', 'quality_inspection'}
        if op_types & cam_ops:
            return 'gg-cam-v1'

        # No profile detected
        return None

    def validate_with_compliance(
        self,
        data: Dict,
        compliance_standards: Optional[List[str]] = None
    ) -> Dict:
        """
        Validate compliance with regulatory standards

        Args:
            data: Parsed GenesisGraph document
            compliance_standards: List of standards to validate against
                                 (e.g., ['ISO-9001', 'FDA-21-CFR-11'])

        Returns:
            Dictionary with compliance results for each standard
        """
        from ..compliance import ISO9001Validator, FDA21CFR11Validator

        results = {}

        # Auto-detect standards if not specified
        if compliance_standards is None:
            compliance_standards = self._detect_compliance_standards(data)

        # Validate against each standard
        for standard in compliance_standards:
            if standard.upper() in ['ISO-9001', 'ISO-9001:2015', 'ISO9001']:
                validator = ISO9001Validator()
                results['ISO-9001'] = validator.validate(data)

            elif standard.upper() in ['FDA-21-CFR-11', '21-CFR-11', 'CFR11']:
                validator = FDA21CFR11Validator()
                results['FDA-21-CFR-11'] = validator.validate(data)

            else:
                results[standard] = {
                    'is_valid': False,
                    'errors': [f"Unknown compliance standard: {standard}"],
                    'warnings': [],
                    'compliance_level': 'unknown'
                }

        return results

    def _detect_compliance_standards(self, data: Dict) -> List[str]:
        """
        Auto-detect applicable compliance standards

        Args:
            data: Parsed GenesisGraph document

        Returns:
            List of detected compliance standards
        """
        standards = []
        metadata = data.get('metadata', {})

        # Check for explicit standard declaration
        if 'compliance_standards' in metadata:
            return metadata['compliance_standards']

        if 'quality_standard' in metadata:
            std = metadata['quality_standard']
            if 'ISO' in std.upper():
                standards.append('ISO-9001')

        # Detect based on operation types
        operations = data.get('operations', [])
        op_types = {op.get('type') for op in operations}

        # Manufacturing workflows often need ISO-9001
        cam_ops = {'cnc_machining', 'additive_manufacturing', 'quality_inspection'}
        if op_types & cam_ops:
            if 'ISO-9001' not in standards:
                standards.append('ISO-9001')

        # AI/medical workflows often need FDA compliance
        ai_ops = {'ai_inference', 'ai_training'}
        if op_types & ai_ops:
            # Check if this looks like a regulated industry
            if any('medical' in str(metadata.get('industry', '')).lower() or
                  'healthcare' in str(metadata.get('industry', '')).lower() or
                  'pharmaceutical' in str(metadata.get('industry', '')).lower()
                  for _ in [True]):
                standards.append('FDA-21-CFR-11')

        # Check for electronic signatures (strong FDA indicator)
        has_signatures = any(
            op.get('attestation', {}).get('mode') in ['signed', 'verifiable']
            for op in operations
        )
        if has_signatures and 'FDA-21-CFR-11' not in standards:
            # Only add if we see quality/regulated indicators
            if metadata.get('quality_standard') or metadata.get('compliance'):
                standards.append('FDA-21-CFR-11')

        return standards
