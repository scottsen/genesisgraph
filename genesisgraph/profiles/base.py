"""
Base Profile Validator

Provides the base class and interface for industry-specific profile validators.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Set


@dataclass
class ProfileValidationResult:
    """Result of profile validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    profile_id: str
    profile_version: str

    def format_report(self) -> str:
        """Format validation result as a human-readable report"""
        lines = [
            f"Profile Validation: {self.profile_id} v{self.profile_version}",
            f"Status: {'VALID' if self.is_valid else 'INVALID'}",
            ""
        ]

        if self.errors:
            lines.append("Errors:")
            for error in self.errors:
                lines.append(f"  - {error}")
            lines.append("")

        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        return "\n".join(lines)


class BaseProfileValidator(ABC):
    """
    Base class for industry-specific profile validators

    Profile validators provide specialized validation rules for specific industries
    and use cases (e.g., AI/ML pipelines, manufacturing, healthcare, supply chain).

    Subclasses should implement:
    - profile_id: Unique identifier (e.g., "gg-ai-basic-v1")
    - profile_version: Semantic version (e.g., "1.0.0")
    - _validate_operations(): Profile-specific operation validation
    - _validate_tools(): Profile-specific tool validation
    - _validate_entities(): Profile-specific entity validation (optional)
    """

    profile_id: str = "base"
    profile_version: str = "1.0.0"

    def __init__(self):
        """Initialize the profile validator"""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_profile(self, data: Dict[str, Any]) -> ProfileValidationResult:
        """
        Main validation entry point

        Args:
            data: Parsed GenesisGraph document

        Returns:
            ProfileValidationResult with validation details
        """
        self.errors = []
        self.warnings = []

        # Validate entities
        entities = data.get('entities', [])
        if entities:
            entity_errors = self._validate_entities(entities)
            self.errors.extend(entity_errors)

        # Validate operations
        operations = data.get('operations', [])
        if operations:
            op_errors = self._validate_operations(operations)
            self.errors.extend(op_errors)

        # Validate tools
        tools = data.get('tools', [])
        if tools:
            tool_errors = self._validate_tools(tools)
            self.errors.extend(tool_errors)

        # Run custom validation logic
        custom_errors = self._validate_custom(data)
        self.errors.extend(custom_errors)

        is_valid = len(self.errors) == 0

        return ProfileValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            profile_id=self.profile_id,
            profile_version=self.profile_version
        )

    def _validate_entities(self, entities: List[Dict]) -> List[str]:
        """
        Validate entity definitions (override in subclass if needed)

        Args:
            entities: List of entity definitions

        Returns:
            List of error messages
        """
        return []

    @abstractmethod
    def _validate_operations(self, operations: List[Dict]) -> List[str]:
        """
        Validate operation definitions (must override in subclass)

        Args:
            operations: List of operation definitions

        Returns:
            List of error messages
        """

    @abstractmethod
    def _validate_tools(self, tools: List[Dict]) -> List[str]:
        """
        Validate tool definitions (must override in subclass)

        Args:
            tools: List of tool definitions

        Returns:
            List of error messages
        """

    def _validate_custom(self, data: Dict[str, Any]) -> List[str]:
        """
        Custom validation logic (override in subclass if needed)

        Args:
            data: Full GenesisGraph document

        Returns:
            List of error messages
        """
        return []

    def _check_required_parameters(
        self,
        op: Dict,
        required_params: List[str],
        allow_redacted: bool = True
    ) -> List[str]:
        """
        Helper to check required parameters in an operation

        Args:
            op: Operation definition
            required_params: List of required parameter names
            allow_redacted: If True, skip checks if parameters are redacted

        Returns:
            List of error messages
        """
        errors = []
        op_id = op.get('id', '<unknown>')
        parameters = op.get('parameters', {})

        # Skip if redacted (privacy-preserving mode)
        if allow_redacted and parameters.get('_redacted'):
            return errors

        # Check for required parameters
        for param in required_params:
            if param not in parameters:
                errors.append(
                    f"Operation '{op_id}': missing required parameter '{param}' "
                    f"for profile {self.profile_id}"
                )

        return errors

    def _check_tool_type(self, tool: Dict, allowed_types: Set[str]) -> List[str]:
        """
        Helper to check if a tool has an allowed type

        Args:
            tool: Tool definition
            allowed_types: Set of allowed tool types

        Returns:
            List of error messages
        """
        errors = []
        tool_id = tool.get('id', '<unknown>')
        tool_type = tool.get('type')

        if tool_type and tool_type not in allowed_types:
            errors.append(
                f"Tool '{tool_id}': type '{tool_type}' not allowed by profile {self.profile_id}. "
                f"Allowed types: {', '.join(sorted(allowed_types))}"
            )

        return errors

    def _check_attestation_mode(
        self,
        op: Dict,
        required_modes: Set[str]
    ) -> List[str]:
        """
        Helper to check attestation mode requirements

        Args:
            op: Operation definition
            required_modes: Set of required attestation modes

        Returns:
            List of error messages
        """
        errors = []
        op_id = op.get('id', '<unknown>')
        attestation = op.get('attestation', {})
        mode = attestation.get('mode')

        if mode and mode not in required_modes:
            errors.append(
                f"Operation '{op_id}': attestation mode '{mode}' not allowed by profile {self.profile_id}. "
                f"Required modes: {', '.join(sorted(required_modes))}"
            )

        return errors
