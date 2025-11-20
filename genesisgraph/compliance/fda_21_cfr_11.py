"""
FDA 21 CFR Part 11 Compliance Validator

Validates GenesisGraph workflows for FDA 21 CFR Part 11 compliance
(Electronic Records and Electronic Signatures).
"""

from typing import Dict, List, Any


class FDA21CFR11Validator:
    """
    Validator for FDA 21 CFR Part 11 compliance

    21 CFR Part 11 establishes requirements for:
    - Electronic records (§11.10)
    - Electronic signatures (§11.50, §11.70)
    - Audit trails (§11.10(e))
    - System validation (§11.10(a))
    - Data integrity and security (§11.10(c), §11.30)
    """

    def __init__(self):
        """Initialize the FDA 21 CFR Part 11 validator"""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate FDA 21 CFR Part 11 compliance

        Args:
            data: Parsed GenesisGraph document

        Returns:
            Dictionary with validation results:
            {
                'is_valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'compliance_level': str
            }
        """
        self.errors = []
        self.warnings = []

        # §11.10(a) - System Validation
        self._validate_system_validation(data)

        # §11.10(c) - Protection of Records
        self._validate_record_protection(data)

        # §11.10(e) - Audit Trails
        self._validate_audit_trails(data)

        # §11.50 - Signature Manifestations
        self._validate_signature_manifestations(data)

        # §11.70 - Signature/Record Linking
        self._validate_signature_linking(data)

        # §11.10(k) - Data Integrity
        self._validate_data_integrity(data)

        # Determine compliance level
        compliance_level = self._determine_compliance_level()

        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'compliance_level': compliance_level,
            'standard': 'FDA 21 CFR Part 11'
        }

    def _validate_system_validation(self, data: Dict[str, Any]):
        """Validate system validation requirements (§11.10(a))"""
        metadata = data.get('metadata', {})

        # System should be validated
        if 'system_validation' in metadata:
            validation = metadata['system_validation']

            if not isinstance(validation, dict):
                self.errors.append(
                    "21 CFR §11.10(a): metadata.system_validation must be an object"
                )
            else:
                # Should document validation protocol
                if 'validation_protocol' not in validation:
                    self.warnings.append(
                        "21 CFR §11.10(a): Should document validation protocol (metadata.system_validation.validation_protocol)"
                    )

                # Should document validation date
                if 'validation_date' not in validation:
                    self.warnings.append(
                        "21 CFR §11.10(a): Should document validation date (metadata.system_validation.validation_date)"
                    )
        else:
            self.warnings.append(
                "21 CFR §11.10(a): Should document system validation (metadata.system_validation)"
            )

    def _validate_record_protection(self, data: Dict[str, Any]):
        """Validate protection of records (§11.10(c))"""
        entities = data.get('entities', [])

        # Records should have integrity protection (hash)
        for entity in entities:
            entity_id = entity.get('id', '<unknown>')
            entity_type = entity.get('type')

            # Critical data types should have hash
            if entity_type in ['Dataset', 'Model', 'CADModel', 'Document']:
                if 'hash' not in entity:
                    self.errors.append(
                        f"21 CFR §11.10(c): Entity '{entity_id}' ({entity_type}) must have 'hash' for record integrity protection"
                    )

        # Should use secure hash algorithm
        for entity in entities:
            if 'hash' in entity:
                hash_val = entity['hash']
                # Check for weak hash algorithms
                if hash_val.startswith('md5:') or hash_val.startswith('sha1:'):
                    self.warnings.append(
                        f"21 CFR §11.10(c): Entity '{entity.get('id')}' uses weak hash algorithm (md5/sha1). Use SHA-256 or stronger."
                    )

    def _validate_audit_trails(self, data: Dict[str, Any]):
        """Validate audit trail requirements (§11.10(e))"""
        operations = data.get('operations', [])

        # Critical operations should have attestation (audit trail)
        for op in operations:
            op_id = op.get('id', '<unknown>')
            op_type = op.get('type')

            # Critical operations require audit trails
            if op_type in ['ai_inference', 'cnc_machining', 'quality_inspection',
                          'human_review', 'additive_manufacturing']:
                attestation = op.get('attestation')

                if not attestation:
                    self.errors.append(
                        f"21 CFR §11.10(e): Operation '{op_id}' ({op_type}) must have attestation for audit trail"
                    )
                else:
                    # Audit trail should include timestamp
                    if 'timestamp' not in attestation:
                        self.errors.append(
                            f"21 CFR §11.10(e): Operation '{op_id}' attestation must include timestamp for audit trail"
                        )

                    # Should include operator identification
                    if 'attester' not in attestation:
                        self.errors.append(
                            f"21 CFR §11.10(e): Operation '{op_id}' attestation must identify the person performing the action (attester)"
                        )

        # Should have transparency log anchoring for tamper detection
        metadata = data.get('metadata', {})
        if 'transparency_log' not in metadata:
            self.warnings.append(
                "21 CFR §11.10(e): Should use transparency log anchoring for tamper-evident audit trails (metadata.transparency_log)"
            )

    def _validate_signature_manifestations(self, data: Dict[str, Any]):
        """Validate signature manifestations (§11.50)"""
        operations = data.get('operations', [])

        for op in operations:
            attestation = op.get('attestation')

            if attestation:
                # Signed attestations should show signature information
                mode = attestation.get('mode')
                if mode in ['signed', 'verifiable']:
                    # Should include signer identity
                    if 'attester' not in attestation:
                        self.errors.append(
                            f"21 CFR §11.50: Attestation for operation '{op.get('id')}' must include attester (signer) identity"
                        )

                    # Should include meaning of signature
                    if 'claim' not in attestation:
                        self.warnings.append(
                            f"21 CFR §11.50: Attestation for operation '{op.get('id')}' should include 'claim' (meaning of signature)"
                        )

                    # Should include timestamp
                    if 'timestamp' not in attestation:
                        self.errors.append(
                            f"21 CFR §11.50: Attestation for operation '{op.get('id')}' must include timestamp"
                        )

    def _validate_signature_linking(self, data: Dict[str, Any]):
        """Validate signature/record linking (§11.70)"""
        operations = data.get('operations', [])

        for op in operations:
            attestation = op.get('attestation')

            if attestation:
                mode = attestation.get('mode')

                # Electronic signatures must be cryptographically linked
                if mode in ['signed', 'verifiable']:
                    if 'signature' not in attestation:
                        self.errors.append(
                            f"21 CFR §11.70: Attestation for operation '{op.get('id')}' must include cryptographic signature"
                        )

                    # Should use strong signature algorithm
                    if 'algorithm' in attestation:
                        algo = attestation['algorithm']
                        if algo not in ['Ed25519', 'ES256', 'ES384', 'ES512', 'RS256']:
                            self.warnings.append(
                                f"21 CFR §11.70: Operation '{op.get('id')}' uses non-standard signature algorithm '{algo}'"
                            )

                    # Signature must be bound to record
                    if 'signed_data_hash' not in attestation and 'canonical_hash' not in attestation:
                        self.warnings.append(
                            f"21 CFR §11.70: Attestation for operation '{op.get('id')}' should include hash of signed data for binding"
                        )

    def _validate_data_integrity(self, data: Dict[str, Any]):
        """Validate data integrity requirements (§11.10(k))"""
        entities = data.get('entities', [])
        operations = data.get('operations', [])

        # Check for proper data chain
        entity_ids = {e.get('id') for e in entities if e.get('id')}

        for op in operations:
            inputs = op.get('inputs', [])
            outputs = op.get('outputs', [])

            # All inputs should reference existing entities
            for input_id in inputs:
                if input_id not in entity_ids:
                    self.warnings.append(
                        f"21 CFR §11.10(k): Operation '{op.get('id')}' references non-existent input '{input_id}'"
                    )

            # All outputs should be defined as entities
            for output_id in outputs:
                if output_id not in entity_ids:
                    self.warnings.append(
                        f"21 CFR §11.10(k): Operation '{op.get('id')}' references non-existent output '{output_id}'"
                    )

        # Check for hash integrity on critical entities
        for entity in entities:
            entity_type = entity.get('type')
            entity_id = entity.get('id', '<unknown>')

            if entity_type in ['Dataset', 'Model', 'Document']:
                if 'hash' not in entity:
                    self.errors.append(
                        f"21 CFR §11.10(k): Critical entity '{entity_id}' must have 'hash' for data integrity verification"
                    )

    def _determine_compliance_level(self) -> str:
        """Determine the compliance level based on errors and warnings"""
        if len(self.errors) > 0:
            return "non-compliant"
        elif len(self.warnings) == 0:
            return "fully-compliant"
        elif len(self.warnings) <= 3:
            return "substantially-compliant"
        else:
            return "partially-compliant"
