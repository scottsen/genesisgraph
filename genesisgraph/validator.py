"""
GenesisGraph Validator

Validates GenesisGraph documents against schema and performs integrity checks.
"""

import hashlib
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import yaml

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from .errors import ValidationError, SchemaError, HashError


class GenesisGraphValidator:
    """
    Validates GenesisGraph documents

    Example:
        >>> validator = GenesisGraphValidator()
        >>> result = validator.validate_file("workflow.gg.yaml")
        >>> if result.is_valid:
        ...     print("Valid!")
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize validator

        Args:
            schema_path: Path to JSON Schema file. If None, uses bundled schema.
        """
        self.schema_path = schema_path
        self.schema = None

        if JSONSCHEMA_AVAILABLE and schema_path:
            self._load_schema(schema_path)

    def _load_schema(self, schema_path: str):
        """Load JSON Schema from file"""
        try:
            with open(schema_path, 'r') as f:
                self.schema = yaml.safe_load(f)
        except Exception as e:
            raise SchemaError(f"Failed to load schema: {e}")

    def validate_file(self, file_path: str) -> "ValidationResult":
        """
        Validate a GenesisGraph file

        Args:
            file_path: Path to .gg.yaml file

        Returns:
            ValidationResult with validation details
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Failed to load file: {e}"],
                warnings=[],
                data=None
            )

        return self.validate(data, file_path=file_path)

    def validate(self, data: Dict, file_path: Optional[str] = None) -> "ValidationResult":
        """
        Validate a GenesisGraph document

        Args:
            data: Parsed YAML data
            file_path: Optional path to source file (for hash verification)

        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []

        # 1. Basic structure validation
        if not isinstance(data, dict):
            errors.append("Document must be a YAML object")
            return ValidationResult(False, errors, warnings, data)

        # 2. Check required top-level fields
        if 'spec_version' not in data:
            errors.append("Missing required field: spec_version")
        else:
            spec_version = data['spec_version']
            if not isinstance(spec_version, str):
                errors.append("spec_version must be a string")
            elif not re.match(r'^\d+\.\d+\.\d+$', spec_version):
                warnings.append(f"spec_version '{spec_version}' does not follow semver format")

        # 3. Validate entities
        entities = data.get('entities', [])
        if not isinstance(entities, list):
            errors.append("entities must be a list")
        else:
            entity_errors = self._validate_entities(entities, file_path)
            errors.extend(entity_errors)

        # 4. Validate operations
        operations = data.get('operations', [])
        if not isinstance(operations, list):
            errors.append("operations must be a list")
        else:
            op_errors = self._validate_operations(operations)
            errors.extend(op_errors)

        # 5. Validate tools
        tools = data.get('tools', [])
        if not isinstance(tools, list):
            errors.append("tools must be a list")
        else:
            tool_errors = self._validate_tools(tools)
            errors.extend(tool_errors)

        # 6. JSON Schema validation (if available)
        if JSONSCHEMA_AVAILABLE and self.schema:
            try:
                jsonschema.validate(instance=data, schema=self.schema)
            except jsonschema.ValidationError as e:
                errors.append(f"Schema validation failed: {e.message}")
            except jsonschema.SchemaError as e:
                warnings.append(f"Schema itself is invalid: {e.message}")
        elif not JSONSCHEMA_AVAILABLE:
            warnings.append("jsonschema not installed - skipping schema validation")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, data)

    def _validate_entities(self, entities: List[Dict], file_path: Optional[str]) -> List[str]:
        """Validate entity definitions"""
        errors = []
        entity_ids = set()

        for i, entity in enumerate(entities):
            if not isinstance(entity, dict):
                errors.append(f"Entity {i} must be an object")
                continue

            # Check required fields
            entity_id = entity.get('id')
            if not entity_id:
                errors.append(f"Entity {i} missing required field: id")
            else:
                if entity_id in entity_ids:
                    errors.append(f"Duplicate entity id: {entity_id}")
                entity_ids.add(entity_id)

            if 'type' not in entity:
                errors.append(f"Entity '{entity_id}' missing required field: type")

            if 'version' not in entity:
                errors.append(f"Entity '{entity_id}' missing required field: version")

            # Check that entity has either file or uri
            if 'file' not in entity and 'uri' not in entity:
                errors.append(f"Entity '{entity_id}' must have either 'file' or 'uri'")

            # Validate hash format
            if 'hash' in entity:
                hash_val = entity['hash']
                if not self._is_valid_hash(hash_val):
                    errors.append(f"Entity '{entity_id}' has invalid hash format: {hash_val}")

            # Verify file hash if file is local and accessible
            if file_path and 'file' in entity and 'hash' in entity:
                file_errors = self._verify_file_hash(entity, file_path)
                errors.extend(file_errors)

        return errors

    def _validate_operations(self, operations: List[Dict]) -> List[str]:
        """Validate operation definitions"""
        errors = []
        op_ids = set()

        for i, op in enumerate(operations):
            if not isinstance(op, dict):
                errors.append(f"Operation {i} must be an object")
                continue

            # Check required fields
            op_id = op.get('id')
            if not op_id:
                errors.append(f"Operation {i} missing required field: id")
            else:
                if op_id in op_ids:
                    errors.append(f"Duplicate operation id: {op_id}")
                op_ids.add(op_id)

            if 'type' not in op:
                errors.append(f"Operation '{op_id}' missing required field: type")

            # Check inputs/outputs (not required for sealed_subgraph)
            op_type = op.get('type')
            if op_type != 'sealed_subgraph':
                if 'inputs' not in op:
                    errors.append(f"Operation '{op_id}' missing field: inputs")
                if 'outputs' not in op:
                    errors.append(f"Operation '{op_id}' missing field: outputs")

            # Validate attestation if present
            if 'attestation' in op:
                attest_errors = self._validate_attestation(op['attestation'], op_id)
                errors.extend(attest_errors)

        return errors

    def _validate_tools(self, tools: List[Dict]) -> List[str]:
        """Validate tool definitions"""
        errors = []
        tool_ids = set()

        for i, tool in enumerate(tools):
            if not isinstance(tool, dict):
                errors.append(f"Tool {i} must be an object")
                continue

            # Check required fields
            tool_id = tool.get('id')
            if not tool_id:
                errors.append(f"Tool {i} missing required field: id")
            else:
                if tool_id in tool_ids:
                    errors.append(f"Duplicate tool id: {tool_id}")
                tool_ids.add(tool_id)

            if 'type' not in tool:
                errors.append(f"Tool '{tool_id}' missing required field: type")
            else:
                tool_type = tool['type']
                valid_types = ['Software', 'Machine', 'Human', 'AIModel', 'Service']
                if tool_type not in valid_types:
                    errors.append(f"Tool '{tool_id}' has invalid type: {tool_type}")

        return errors

    def _validate_attestation(self, attestation: Dict, context: str) -> List[str]:
        """Validate attestation block"""
        errors = []

        if not isinstance(attestation, dict):
            errors.append(f"{context}: attestation must be an object")
            return errors

        mode = attestation.get('mode', 'basic')
        valid_modes = ['basic', 'signed', 'verifiable', 'zk']
        if mode not in valid_modes:
            errors.append(f"{context}: invalid attestation mode: {mode}")

        # Check mode-specific requirements
        if mode in ['signed', 'verifiable', 'zk']:
            if 'signer' not in attestation:
                errors.append(f"{context}: attestation mode '{mode}' requires 'signer'")
            if 'signature' not in attestation:
                errors.append(f"{context}: attestation mode '{mode}' requires 'signature'")

        return errors

    def _is_valid_hash(self, hash_str: str) -> bool:
        """Check if hash string is valid format"""
        if not isinstance(hash_str, str):
            return False

        # Format: algorithm:hexdigest
        pattern = r'^(sha256|sha512|blake3):[a-f0-9]+$'
        return bool(re.match(pattern, hash_str))

    def _verify_file_hash(self, entity: Dict, base_path: str) -> List[str]:
        """Verify file hash matches declared hash"""
        errors = []

        entity_id = entity.get('id', 'unknown')
        file_path = entity['file']
        declared_hash = entity['hash']

        # Make path relative to base document
        if not os.path.isabs(file_path):
            doc_dir = os.path.dirname(base_path)
            full_path = os.path.join(doc_dir, file_path)
        else:
            full_path = file_path

        if not os.path.exists(full_path):
            errors.append(f"Entity '{entity_id}': file not found: {file_path}")
            return errors

        try:
            # Extract algorithm and expected hash
            algo, expected_hex = declared_hash.split(':', 1)

            # Compute file hash
            if algo == 'sha256':
                hasher = hashlib.sha256()
            elif algo == 'sha512':
                hasher = hashlib.sha512()
            elif algo == 'blake3':
                errors.append(f"Entity '{entity_id}': blake3 not yet supported")
                return errors
            else:
                errors.append(f"Entity '{entity_id}': unsupported hash algorithm: {algo}")
                return errors

            with open(full_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)

            computed_hex = hasher.hexdigest()

            if computed_hex != expected_hex:
                errors.append(
                    f"Entity '{entity_id}': hash mismatch\n"
                    f"  Declared: {expected_hex}\n"
                    f"  Computed: {computed_hex}"
                )

        except Exception as e:
            errors.append(f"Entity '{entity_id}': failed to verify hash: {e}")

        return errors


class ValidationResult:
    """Result of validation"""

    def __init__(
        self,
        is_valid: bool,
        errors: List[str],
        warnings: List[str],
        data: Optional[Dict]
    ):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
        self.data = data

    def __bool__(self):
        return self.is_valid

    def __repr__(self):
        status = "VALID" if self.is_valid else "INVALID"
        return f"ValidationResult({status}, {len(self.errors)} errors, {len(self.warnings)} warnings)"

    def format_report(self) -> str:
        """Format a human-readable validation report"""
        lines = []

        if self.is_valid:
            lines.append("✓ Validation PASSED")
        else:
            lines.append("❌ Validation FAILED")

        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  • {error}")

        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  • {warning}")

        return "\n".join(lines)


def validate(file_path: str, schema_path: Optional[str] = None) -> ValidationResult:
    """
    Convenience function to validate a GenesisGraph file

    Args:
        file_path: Path to .gg.yaml file
        schema_path: Optional path to schema

    Returns:
        ValidationResult

    Example:
        >>> from genesisgraph import validate
        >>> result = validate("workflow.gg.yaml")
        >>> print(result.format_report())
    """
    validator = GenesisGraphValidator(schema_path=schema_path)
    return validator.validate_file(file_path)
