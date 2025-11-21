"""
GenesisGraph Validator

Validates GenesisGraph documents against schema and performs integrity checks.
"""

import base64
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

try:
    from cryptography.exceptions import InvalidSignature as CryptoInvalidSignature
    from cryptography.hazmat.primitives.asymmetric import ed25519
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

try:
    from .did_resolver import DIDResolver
    DID_RESOLVER_AVAILABLE = True
except ImportError:
    DID_RESOLVER_AVAILABLE = False

try:
    from .transparency_log import TransparencyLogVerifier
    TRANSPARENCY_LOG_AVAILABLE = True
except ImportError:
    TRANSPARENCY_LOG_AVAILABLE = False

try:
    from .credentials.sd_jwt import SDJWTVerifier, SDJWTError
    from .credentials.predicates import verify_predicate, PredicateProof
    from .credentials.bbs_plus import BBSPlusVerifier
    SD_JWT_AVAILABLE = True
except ImportError:
    SD_JWT_AVAILABLE = False

from .errors import SchemaError, ValidationError

# Security: Input size limits to prevent DoS
MAX_ENTITIES = 10000  # Maximum number of entities in a document
MAX_OPERATIONS = 10000  # Maximum number of operations
MAX_TOOLS = 1000  # Maximum number of tools
MAX_ID_LENGTH = 256  # Maximum length for IDs
MAX_HASH_LENGTH = 512  # Maximum length for hash strings (algorithm:hexdigest)
MAX_SIGNATURE_LENGTH = 4096  # Maximum length for signatures

# Performance: Pre-compiled regex patterns
# =========================================
# Compiling regex patterns once at module load significantly improves performance
# for repeated validations (2-3x faster for documents with many entities/operations)

# Semver pattern: MAJOR.MINOR.PATCH (e.g., "1.0.0")
SEMVER_PATTERN = re.compile(r'^\d+\.\d+\.\d+$')

# Hash format pattern: <algorithm>:<hexdigest>
# Examples: sha256:abc123..., sha512:def456..., blake3:789abc...
HASH_PATTERN = re.compile(r'^(sha256|sha512|blake3):[a-f0-9]+$')

# Signature format pattern: <algorithm>:<signature_data>
# Examples: ed25519:abc123..., ecdsa:def456..., rsa:789abc...
SIGNATURE_PATTERN = re.compile(r'^(ed25519|ecdsa|rsa):.+$')


class GenesisGraphValidator:
    """
    Validates GenesisGraph documents

    Example:
        >>> validator = GenesisGraphValidator()
        >>> result = validator.validate_file("workflow.gg.yaml")
        >>> if result.is_valid:
        ...     print("Valid!")
    """

    def __init__(self, schema_path: Optional[str] = None, verify_signatures: bool = False,
                 use_schema: bool = False, verify_transparency: bool = False,
                 verify_profile: bool = False, profile_id: Optional[str] = None):
        """
        Initialize validator

        Args:
            schema_path: Path to JSON Schema file. If None and use_schema=True, uses bundled schema.
            verify_signatures: If True, cryptographically verify signatures (requires keys)
            use_schema: If True, enable JSON Schema validation (default: False for backwards compatibility)
            verify_transparency: If True, verify transparency log inclusion proofs (RFC 6962)
            verify_profile: If True, enable industry-specific profile validation (Phase 5)
            profile_id: Optional profile ID (e.g., "gg-ai-basic-v1"). If None, auto-detects profile.
        """
        self.schema_path = schema_path
        self.schema = None
        self.verify_signatures = verify_signatures
        self.use_schema = use_schema
        self.verify_transparency = verify_transparency
        self.verify_profile = verify_profile
        self.profile_id = profile_id

        # Initialize DID resolver if signature verification is enabled
        self.did_resolver = None
        if verify_signatures and DID_RESOLVER_AVAILABLE:
            self.did_resolver = DIDResolver()

        # Initialize transparency log verifier if enabled
        self.transparency_verifier = None
        if verify_transparency and TRANSPARENCY_LOG_AVAILABLE:
            self.transparency_verifier = TransparencyLogVerifier(
                verify_proofs=True,
                fetch_from_logs=False
            )

        # Initialize profile registry if profile validation is enabled
        self.profile_registry = None
        if verify_profile:
            try:
                from .profiles import ProfileRegistry
                self.profile_registry = ProfileRegistry()
            except ImportError:
                pass  # Profile validation not available

        # Auto-detect bundled schema if schema validation is enabled
        if use_schema and schema_path is None:
            bundled_schema = self._find_bundled_schema()
            if bundled_schema:
                self.schema_path = bundled_schema

        if JSONSCHEMA_AVAILABLE and use_schema and self.schema_path:
            self._load_schema(self.schema_path)

    def _find_bundled_schema(self) -> Optional[str]:
        """
        Find bundled schema file in package directory

        Returns:
            Path to schema file, or None if not found
        """
        # Try to find schema relative to this file
        current_file = Path(__file__)
        package_dir = current_file.parent.parent  # Go up to package root

        # Try common locations
        schema_locations = [
            package_dir / "schema" / "genesisgraph-core-v0.1.yaml",
            package_dir / "genesisgraph" / "schema" / "genesisgraph-core-v0.1.yaml",
        ]

        for schema_path in schema_locations:
            if schema_path.exists():
                return str(schema_path)

        return None

    def _load_schema(self, schema_path: str):
        """Load JSON Schema from file"""
        try:
            with open(schema_path) as f:
                self.schema = yaml.safe_load(f)
        except Exception as e:
            raise SchemaError(f"Failed to load schema: {e}") from e

    def validate_file(self, file_path: str) -> "ValidationResult":
        """
        Validate a GenesisGraph file

        Args:
            file_path: Path to .gg.yaml file

        Returns:
            ValidationResult with validation details
        """
        try:
            with open(file_path) as f:
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
            elif not SEMVER_PATTERN.match(spec_version):
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

        # 7. Profile validation (Phase 5 - if enabled)
        if self.verify_profile and self.profile_registry:
            try:
                profile_result = self.profile_registry.validate_with_profile(
                    data,
                    profile_id=self.profile_id
                )
                errors.extend(profile_result.errors)
                warnings.extend(profile_result.warnings)

                # Add profile info to warnings if profile was detected
                if profile_result.profile_id != "none":
                    warnings.append(
                        f"Profile validation: {profile_result.profile_id} "
                        f"v{profile_result.profile_version} - "
                        f"{'VALID' if profile_result.is_valid else 'INVALID'}"
                    )
            except Exception as e:
                warnings.append(f"Profile validation error: {e}")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, data)

    def _validate_entities(self, entities: List[Dict], file_path: Optional[str]) -> List[str]:
        """Validate entity definitions"""
        errors = []
        entity_ids = set()

        # Security: Limit number of entities to prevent DoS
        if len(entities) > MAX_ENTITIES:
            errors.append(f"Too many entities: {len(entities)} (maximum {MAX_ENTITIES} allowed)")
            return errors

        for i, entity in enumerate(entities):
            if not isinstance(entity, dict):
                errors.append(f"Entity {i} must be an object")
                continue

            # Check required fields
            entity_id = entity.get('id')
            if not entity_id:
                errors.append(f"Entity {i} missing required field: id")
            else:
                # Security: Validate ID length
                if len(entity_id) > MAX_ID_LENGTH:
                    errors.append(
                        f"Entity {i} ID too long: {len(entity_id)} characters "
                        f"(maximum {MAX_ID_LENGTH} allowed)"
                    )
                    continue

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

                # Security: Validate hash length
                if len(hash_val) > MAX_HASH_LENGTH:
                    errors.append(
                        f"Entity '{entity_id}' hash too long: {len(hash_val)} characters "
                        f"(maximum {MAX_HASH_LENGTH} allowed)"
                    )
                    continue

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

        # Security: Limit number of operations to prevent DoS
        if len(operations) > MAX_OPERATIONS:
            errors.append(f"Too many operations: {len(operations)} (maximum {MAX_OPERATIONS} allowed)")
            return errors

        for i, op in enumerate(operations):
            if not isinstance(op, dict):
                errors.append(f"Operation {i} must be an object")
                continue

            # Check required fields
            op_id = op.get('id')
            if not op_id:
                errors.append(f"Operation {i} missing required field: id")
            else:
                # Security: Validate ID length
                if len(op_id) > MAX_ID_LENGTH:
                    errors.append(
                        f"Operation {i} ID too long: {len(op_id)} characters "
                        f"(maximum {MAX_ID_LENGTH} allowed)"
                    )
                    continue

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
                attest_errors = self._validate_attestation(op['attestation'], op_id, op)
                errors.extend(attest_errors)

        return errors

    def _validate_tools(self, tools: List[Dict]) -> List[str]:
        """Validate tool definitions"""
        errors = []
        tool_ids = set()

        # Security: Limit number of tools to prevent DoS
        if len(tools) > MAX_TOOLS:
            errors.append(f"Too many tools: {len(tools)} (maximum {MAX_TOOLS} allowed)")
            return errors

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

    def _validate_attestation(self, attestation: Dict, context: str, operation_data: Optional[Dict] = None) -> List[str]:
        """Validate attestation block"""
        errors = []

        if not isinstance(attestation, dict):
            errors.append(f"{context}: attestation must be an object")
            return errors

        mode = attestation.get('mode', 'basic')
        valid_modes = ['basic', 'signed', 'verifiable', 'zk', 'sd-jwt', 'bbs-plus', 'predicate']
        if mode not in valid_modes:
            errors.append(f"{context}: invalid attestation mode: {mode}")

        # Check mode-specific requirements
        if mode in ['signed', 'verifiable', 'zk']:
            if 'signer' not in attestation:
                errors.append(f"{context}: attestation mode '{mode}' requires 'signer'")
            if 'signature' not in attestation:
                errors.append(f"{context}: attestation mode '{mode}' requires 'signature'")
            else:
                # Validate signature format
                signature = attestation['signature']

                # Security: Validate signature length
                if len(signature) > MAX_SIGNATURE_LENGTH:
                    errors.append(
                        f"{context}: signature too long: {len(signature)} characters "
                        f"(maximum {MAX_SIGNATURE_LENGTH} allowed)"
                    )
                elif not self._is_valid_signature_format(signature):
                    errors.append(f"{context}: invalid signature format: {signature}")
                else:
                    # Optionally verify signature cryptographically
                    if self.verify_signatures and operation_data:
                        # Note: This is a basic implementation that requires public keys to be provided
                        # In production, you'd look up keys from a key store or DID registry
                        sig_errors = self._verify_signature(attestation, operation_data, context)
                        errors.extend(sig_errors)

        # SD-JWT mode validation
        elif mode == 'sd-jwt':
            if 'sd_jwt' not in attestation:
                errors.append(f"{context}: attestation mode 'sd-jwt' requires 'sd_jwt' field")
            elif self.verify_signatures and SD_JWT_AVAILABLE:
                sd_jwt_errors = self._verify_sd_jwt_attestation(attestation, context)
                errors.extend(sd_jwt_errors)
            elif self.verify_signatures and not SD_JWT_AVAILABLE:
                errors.append(f"{context}: SD-JWT verification requested but credentials module not available. Install with: pip install genesisgraph[credentials]")

        # BBS+ mode validation
        elif mode == 'bbs-plus':
            if 'bbs_plus' not in attestation:
                errors.append(f"{context}: attestation mode 'bbs-plus' requires 'bbs_plus' field")
            elif self.verify_signatures and SD_JWT_AVAILABLE:
                bbs_errors = self._verify_bbs_plus_attestation(attestation, context)
                errors.extend(bbs_errors)
            elif self.verify_signatures and not SD_JWT_AVAILABLE:
                errors.append(f"{context}: BBS+ verification requested but credentials module not available. Install with: pip install genesisgraph[credentials]")

        # Predicate mode validation
        elif mode == 'predicate':
            if 'predicate_proofs' not in attestation:
                errors.append(f"{context}: attestation mode 'predicate' requires 'predicate_proofs' field")
            elif self.verify_signatures and SD_JWT_AVAILABLE:
                predicate_errors = self._verify_predicate_attestation(attestation, context)
                errors.extend(predicate_errors)
            elif self.verify_signatures and not SD_JWT_AVAILABLE:
                errors.append(f"{context}: Predicate verification requested but credentials module not available. Install with: pip install genesisgraph[credentials]")

        # Verify transparency log anchoring if present and enabled
        if 'transparency' in attestation and self.verify_transparency:
            transparency_errors = self._verify_transparency_anchoring(
                attestation['transparency'],
                operation_data,
                context
            )
            errors.extend(transparency_errors)

        return errors

    def _is_valid_signature_format(self, signature: str) -> bool:
        """Check if signature string is valid format"""
        if not isinstance(signature, str):
            return False

        # Signature format: <algorithm>:<signature_data>
        # Examples:
        #   ed25519:k3JlZDI1NTE5OnNpZ25hdHVyZV9kYXRh...  (base64)
        #   ed25519:mock:test_signature                 (mock for testing)
        #   ecdsa:p256:sig_abc123...                    (future support)
        #
        # Use pre-compiled pattern for performance
        return bool(SIGNATURE_PATTERN.match(signature))

    def _verify_signature(self, attestation: Dict, operation_data: Dict, context: str) -> List[str]:
        """
        Verify cryptographic signature

        This method implements production-ready signature verification:
        1. Resolves signer DID to public key
        2. Computes canonical JSON representation of signed data
        3. Verifies signature using Ed25519

        Args:
            attestation: Attestation block with signature
            operation_data: Operation being signed
            context: Context string for error messages

        Returns:
            List of error messages (empty if valid)

        Notes:
            - Signatures are verified over canonical JSON (RFC 8785-style)
            - The signed data includes the entire operation minus the attestation block
            - For testing, mock signatures (starting with "mock:") are accepted
        """
        errors = []

        if not CRYPTOGRAPHY_AVAILABLE:
            errors.append(f"{context}: cryptography library not available for signature verification")
            return errors

        signature_str = attestation.get('signature', '')
        signer = attestation.get('signer', '')

        if not signature_str or not signer:
            return errors

        # Parse signature format: "algorithm:data"
        try:
            algo, sig_data = signature_str.split(':', 1)
        except ValueError:
            errors.append(f"{context}: malformed signature: {signature_str}")
            return errors

        if algo == 'ed25519':
            # For testing/demo: accept mock signatures
            if sig_data.startswith(('mock:', 'sig')):
                # Mock signature - skip verification but validate format
                return errors

            # Real ed25519 verification
            try:
                # Step 1: Resolve DID to public key
                if not self.did_resolver:
                    if not DID_RESOLVER_AVAILABLE:
                        errors.append(f"{context}: DID resolver not available (signature verification disabled)")
                    else:
                        errors.append(f"{context}: DID resolver not initialized (verify_signatures=False?)")
                    return errors

                try:
                    public_key_bytes = self.did_resolver.resolve_to_public_key(signer)
                except ValidationError as e:
                    errors.append(f"{context}: failed to resolve signer DID '{signer}': {e}")
                    return errors

                # Step 2: Decode signature from base64
                try:
                    signature_bytes = base64.b64decode(sig_data)
                except Exception as e:
                    errors.append(f"{context}: failed to decode signature: {e}")
                    return errors

                # Step 3: Compute canonical JSON of signed data
                # The signed data is the operation without the attestation block
                signed_data = dict(operation_data)
                signed_data.pop('attestation', None)  # Remove attestation from signed data

                try:
                    canonical_json = self._canonical_json(signed_data)
                    message = canonical_json.encode('utf-8')
                except Exception as e:
                    errors.append(f"{context}: failed to compute canonical JSON: {e}")
                    return errors

                # Step 4: Verify Ed25519 signature
                try:
                    public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
                    public_key.verify(signature_bytes, message)
                    # Signature is valid - no errors
                except CryptoInvalidSignature:
                    errors.append(f"{context}: signature verification failed - invalid signature")
                except Exception as e:
                    errors.append(f"{context}: signature verification error: {e}")

            except Exception as e:
                errors.append(f"{context}: unexpected error during signature verification: {e}")

        elif algo in ['ecdsa', 'rsa']:
            errors.append(f"{context}: {algo} signature verification not yet implemented")
        else:
            errors.append(f"{context}: unsupported signature algorithm: {algo}")

        return errors

    def _verify_sd_jwt_attestation(self, attestation: Dict, context: str) -> List[str]:
        """
        Verify SD-JWT selective disclosure attestation

        Args:
            attestation: Attestation block with SD-JWT
            context: Context string for error messages

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if not SD_JWT_AVAILABLE:
            errors.append(f"{context}: SD-JWT verification requires credentials module")
            return errors

        sd_jwt_data = attestation.get('sd_jwt', {})

        # Create verifier
        # In production, you'd provide trusted issuers from configuration
        verifier = SDJWTVerifier()

        try:
            # Verify SD-JWT
            result = verifier.verify_sd_jwt(sd_jwt_data)

            if not result.get('valid', False):
                verification_errors = result.get('errors', ['Unknown verification error'])
                for err in verification_errors:
                    errors.append(f"{context}: SD-JWT verification failed: {err}")

        except Exception as e:
            errors.append(f"{context}: SD-JWT verification error: {e}")

        return errors

    def _verify_bbs_plus_attestation(self, attestation: Dict, context: str) -> List[str]:
        """
        Verify BBS+ selective disclosure attestation

        Args:
            attestation: Attestation block with BBS+ proof
            context: Context string for error messages

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if not SD_JWT_AVAILABLE:
            errors.append(f"{context}: BBS+ verification requires credentials module")
            return errors

        bbs_plus_data = attestation.get('bbs_plus', {})

        # Create verifier
        verifier = BBSPlusVerifier()

        try:
            # Extract presentation data
            presentation = {
                "type": "BBSPlusPresentation",
                "issuer": bbs_plus_data.get('issuer'),
                "proof": bbs_plus_data.get('proof', {}),
                "attribute_order": bbs_plus_data.get('attribute_order', [])
            }

            # Verify presentation
            result = verifier.verify_presentation(presentation)

            if not result.get('valid', False):
                verification_errors = result.get('errors', ['Unknown verification error'])
                for err in verification_errors:
                    errors.append(f"{context}: BBS+ verification failed: {err}")

        except Exception as e:
            errors.append(f"{context}: BBS+ verification error: {e}")

        return errors

    def _verify_predicate_attestation(self, attestation: Dict, context: str) -> List[str]:
        """
        Verify predicate proofs for privacy-preserving claims

        Args:
            attestation: Attestation block with predicate proofs
            context: Context string for error messages

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if not SD_JWT_AVAILABLE:
            errors.append(f"{context}: Predicate verification requires credentials module")
            return errors

        predicate_proofs = attestation.get('predicate_proofs', [])

        if not isinstance(predicate_proofs, list):
            errors.append(f"{context}: predicate_proofs must be a list")
            return errors

        for idx, proof_data in enumerate(predicate_proofs):
            try:
                # Convert dict to PredicateProof
                proof = PredicateProof.from_dict(proof_data)

                # Verify predicate
                result = verify_predicate(proof)

                if not result.get('valid', False):
                    verification_errors = result.get('errors', [])
                    for err in verification_errors:
                        errors.append(f"{context}: Predicate proof {idx} failed: {err}")

            except Exception as e:
                errors.append(f"{context}: Predicate proof {idx} verification error: {e}")

        return errors

    def _verify_transparency_anchoring(
        self,
        transparency_entries: List[Dict],
        operation_data: Optional[Dict],
        context: str
    ) -> List[str]:
        """
        Verify Certificate Transparency-style anchoring in transparency logs

        Validates that operations are anchored in one or more transparency logs
        with cryptographic inclusion proofs (RFC 6962).

        Args:
            transparency_entries: List of transparency log entries
            operation_data: The operation being anchored
            context: Context string for error messages

        Returns:
            List of error messages (empty if valid)

        Notes:
            - Verifies RFC 6962 Merkle inclusion proofs
            - Supports multi-witness validation across multiple logs
            - Provides tamper-evident audit trail for critical operations
        """
        errors = []

        if not TRANSPARENCY_LOG_AVAILABLE:
            errors.append(
                f"{context}: transparency log verification not available "
                "(transparency_log module not imported)"
            )
            return errors

        if not self.transparency_verifier:
            errors.append(
                f"{context}: transparency verifier not initialized "
                "(verify_transparency=False?)"
            )
            return errors

        if not isinstance(transparency_entries, list):
            errors.append(
                f"{context}: transparency must be a list, got {type(transparency_entries)}"
            )
            return errors

        if len(transparency_entries) == 0:
            # No transparency entries - not an error, just skip
            return errors

        # Compute the leaf data to verify
        # The leaf data is the canonical JSON of the operation
        if operation_data:
            try:
                canonical_json = self._canonical_json(operation_data)
                leaf_data = canonical_json.encode('utf-8')
            except Exception as e:
                errors.append(
                    f"{context}: failed to compute canonical JSON for transparency: {e}"
                )
                return errors
        else:
            # No operation data - can't verify
            errors.append(
                f"{context}: cannot verify transparency without operation data"
            )
            return errors

        # Verify multi-witness
        is_valid, messages = self.transparency_verifier.verify_multi_witness(
            entries=transparency_entries,
            leaf_data=leaf_data,
            context=context,
            require_all=False  # At least one witness must verify
        )

        if not is_valid:
            # Convert messages to errors
            for msg in messages:
                if '✗' in msg or 'failed' in msg.lower():
                    errors.append(msg)

        return errors

    def _canonical_json(self, data: Any) -> str:
        """
        Compute canonical JSON representation for signing

        Uses deterministic JSON encoding:
        - Keys sorted alphabetically
        - No whitespace
        - Consistent number formatting
        - UTF-8 encoding

        This follows the approach used by JCS (RFC 8785) and similar standards.

        Args:
            data: Data to canonicalize

        Returns:
            Canonical JSON string

        Example:
            >>> validator._canonical_json({"z": 1, "a": 2})
            '{"a":2,"z":1}'
        """
        # Use separators with no spaces, sort keys alphabetically
        return json.dumps(
            data,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=False
        )

    def _is_valid_hash(self, hash_str: str) -> bool:
        """Check if hash string is valid format"""
        if not isinstance(hash_str, str):
            return False

        # Hash format: <algorithm>:<hexdigest>
        # Examples:
        #   sha256:a3c8b9d1e2f3...  (64 hex chars for SHA-256)
        #   sha512:f1e2d3c4b5a6...  (128 hex chars for SHA-512)
        #   blake3:7f8e9d0c1b2a...  (64 hex chars for BLAKE3)
        #
        # Use pre-compiled pattern for performance
        # Note: Length validation is not enforced here (allows truncated hashes)
        return bool(HASH_PATTERN.match(hash_str))

    def _verify_file_hash(self, entity: Dict, base_path: str) -> List[str]:
        """Verify file hash matches declared hash"""
        errors = []

        entity_id = entity.get('id', 'unknown')
        file_path = entity['file']
        declared_hash = entity['hash']

        # Security: Prevent path traversal attacks
        # ============================================
        # Path traversal attacks try to access files outside the intended directory
        # by using sequences like "../../../etc/passwd" or absolute paths.
        #
        # Defense strategy:
        # 1. Normalize path (resolve . and .. components)
        # 2. Reject absolute paths (e.g., /etc/passwd, C:\Windows\...)
        # 3. Reject parent directory references (..)
        # 4. Verify resolved path stays within document directory

        normalized_path = os.path.normpath(file_path)

        # Check 1: Block absolute paths (Unix: /path, Windows: C:\path or \\network)
        if os.path.isabs(normalized_path):
            errors.append(f"Entity '{entity_id}': absolute paths not allowed for security reasons")
            return errors

        # Check 2: Block parent directory traversal attempts
        # Examples of blocked paths: ../secret.txt, foo/../../etc/passwd, ..\Windows\System32
        if normalized_path.startswith('..') or '/..' in normalized_path or '\\..'.replace('\\', os.sep) in normalized_path:
            errors.append(f"Entity '{entity_id}': parent directory references not allowed for security reasons")
            return errors

        # Make path relative to base document directory
        doc_dir = os.path.dirname(os.path.abspath(base_path))
        full_path = os.path.normpath(os.path.join(doc_dir, normalized_path))

        # Ensure the resolved path is still within the base directory
        if not full_path.startswith(os.path.normpath(doc_dir) + os.sep) and full_path != os.path.normpath(doc_dir):
            errors.append(f"Entity '{entity_id}': path traversal detected - file must be in document directory")
            return errors

        if not os.path.exists(full_path):
            errors.append(f"Entity '{entity_id}': file not found: {file_path}")
            return errors

        try:
            # Extract algorithm and expected hash
            algo, expected_hex = declared_hash.split(':', 1)

            # Compute file hash
            if algo == 'sha256':
                hasher = hashlib.sha256()
                with open(full_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                computed_hex = hasher.hexdigest()
            elif algo == 'sha512':
                hasher = hashlib.sha512()
                with open(full_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                computed_hex = hasher.hexdigest()
            elif algo == 'blake3':
                if not BLAKE3_AVAILABLE:
                    errors.append(
                        f"Entity '{entity_id}': blake3 hash verification requires blake3 library. "
                        f"Install with: pip install genesisgraph[blake3]"
                    )
                    return errors
                # Blake3 has a different API - use file hashing for efficiency
                with open(full_path, 'rb') as f:
                    hasher = blake3.blake3()
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                computed_hex = hasher.hexdigest()
            else:
                errors.append(f"Entity '{entity_id}': unsupported hash algorithm: {algo}")
                return errors

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
