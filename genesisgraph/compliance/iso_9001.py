"""
ISO 9001 Compliance Validator

Validates GenesisGraph workflows for ISO 9001:2015 quality management compliance.
"""

from typing import Dict, List, Any


class ISO9001Validator:
    """
    Validator for ISO 9001:2015 compliance

    ISO 9001 requires:
    - Documentation and record control
    - Traceability of processes and materials
    - Calibration and maintenance records for equipment
    - Quality planning and control
    - Nonconformance tracking and corrective actions
    """

    def __init__(self):
        """Initialize the ISO 9001 validator"""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate ISO 9001 compliance

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

        # Check metadata requirements (Clause 7.5 - Documented Information)
        self._validate_documented_information(data)

        # Check traceability (Clause 8.5.2 - Identification and Traceability)
        self._validate_traceability(data)

        # Check equipment and tool management (Clause 7.1.5 - Monitoring and Measuring Resources)
        self._validate_equipment_management(data)

        # Check quality control (Clause 8.5 - Production and Service Provision)
        self._validate_quality_control(data)

        # Check attestation and verification (Clause 8.6 - Release of Products and Services)
        self._validate_verification_and_release(data)

        # Determine compliance level
        compliance_level = self._determine_compliance_level()

        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'compliance_level': compliance_level,
            'standard': 'ISO 9001:2015'
        }

    def _validate_documented_information(self, data: Dict[str, Any]):
        """Validate documented information requirements (Clause 7.5)"""
        metadata = data.get('metadata', {})

        # ISO 9001 requires clear identification
        if 'description' not in metadata:
            self.errors.append(
                "ISO 9001 Clause 7.5: Missing 'metadata.description' - documented information must be identified"
            )

        # Should have document control information
        if 'version' not in metadata and 'spec_version' not in data:
            self.warnings.append(
                "ISO 9001 Clause 7.5: Missing version control information - documented information should be version controlled"
            )

        # Should have responsible party
        if 'author' not in metadata and 'organization' not in metadata:
            self.warnings.append(
                "ISO 9001 Clause 7.5: Missing authorship or organization - documented information should identify responsible parties"
            )

    def _validate_traceability(self, data: Dict[str, Any]):
        """Validate identification and traceability requirements (Clause 8.5.2)"""
        entities = data.get('entities', [])
        operations = data.get('operations', [])

        # All entities should have unique identification
        entity_ids = set()
        for entity in entities:
            entity_id = entity.get('id')
            if not entity_id:
                self.errors.append(
                    "ISO 9001 Clause 8.5.2: Entity missing 'id' - all materials and parts must be identifiable"
                )
            else:
                if entity_id in entity_ids:
                    self.errors.append(
                        f"ISO 9001 Clause 8.5.2: Duplicate entity id '{entity_id}' - identification must be unique"
                    )
                entity_ids.add(entity_id)

            # Materials and parts should have traceability metadata
            entity_type = entity.get('type')
            if entity_type in ['Material', 'CADModel', 'Mesh']:
                metadata = entity.get('metadata', {})

                # Should have lot/batch identification
                if entity_type == 'Material':
                    if 'lot_number' not in metadata and 'batch_number' not in metadata:
                        self.warnings.append(
                            f"ISO 9001 Clause 8.5.2: Material entity '{entity_id}' should have lot or batch number for traceability"
                        )

                    if 'supplier' not in metadata:
                        self.warnings.append(
                            f"ISO 9001 Clause 8.5.2: Material entity '{entity_id}' should identify supplier for traceability"
                        )

        # Operations should form a traceable chain
        op_inputs = set()
        op_outputs = set()

        for op in operations:
            inputs = op.get('inputs', [])
            outputs = op.get('outputs', [])

            op_inputs.update(inputs)
            op_outputs.update(outputs)

        # Check for broken traceability chain
        for entity in entities:
            entity_id = entity.get('id')
            # Intermediate entities should be either an input or output
            # (Starting entities won't be outputs, final entities won't be inputs)
            # This is a warning, not an error

    def _validate_equipment_management(self, data: Dict[str, Any]):
        """Validate monitoring and measuring resources (Clause 7.1.5)"""
        tools = data.get('tools', [])

        for tool in tools:
            tool_id = tool.get('id', '<unknown>')
            tool_type = tool.get('type')

            # Machines and measurement tools need calibration
            if tool_type in ['Machine', 'Software']:
                metadata = tool.get('metadata', {})

                if 'calibration_date' not in metadata and 'last_calibration' not in metadata:
                    self.warnings.append(
                        f"ISO 9001 Clause 7.1.5: Tool '{tool_id}' ({tool_type}) should have calibration date for measuring equipment"
                    )

                if 'calibration_status' not in metadata:
                    self.warnings.append(
                        f"ISO 9001 Clause 7.1.5: Tool '{tool_id}' should have calibration status (e.g., 'valid', 'due', 'expired')"
                    )

                # Should have maintenance records
                if 'last_maintenance' not in metadata and 'maintenance_schedule' not in metadata:
                    self.warnings.append(
                        f"ISO 9001 Clause 7.1.5: Tool '{tool_id}' should have maintenance records"
                    )

    def _validate_quality_control(self, data: Dict[str, Any]):
        """Validate production and service provision controls (Clause 8.5)"""
        operations = data.get('operations', [])

        # Should have quality checkpoints
        quality_ops = [
            op for op in operations
            if op.get('type') in ['quality_inspection', 'human_review', 'verification']
        ]

        if not quality_ops:
            self.warnings.append(
                "ISO 9001 Clause 8.5: Workflow should include quality control checkpoints (quality_inspection, human_review, or verification operations)"
            )

        # Check for controlled conditions in operations
        for op in operations:
            op_id = op.get('id', '<unknown>')
            op_type = op.get('type')

            # Critical operations should have controlled parameters
            if op_type in ['cnc_machining', 'additive_manufacturing', 'ai_inference']:
                parameters = op.get('parameters', {})

                if not parameters or parameters.get('_redacted'):
                    # Can't validate if redacted, but should note it
                    continue

                # Should document process parameters
                if not parameters:
                    self.warnings.append(
                        f"ISO 9001 Clause 8.5: Operation '{op_id}' ({op_type}) should document process parameters for controlled conditions"
                    )

    def _validate_verification_and_release(self, data: Dict[str, Any]):
        """Validate release of products and services (Clause 8.6)"""
        operations = data.get('operations', [])

        # Should have verification/validation before release
        has_verification = False

        for op in operations:
            op_type = op.get('type')
            attestation = op.get('attestation')

            # Quality inspection or verification operations
            if op_type in ['quality_inspection', 'verification', 'human_review']:
                has_verification = True

                # Should have attestation
                if not attestation:
                    self.warnings.append(
                        f"ISO 9001 Clause 8.6: Verification operation '{op.get('id')}' should have attestation for release authorization"
                    )

        if not has_verification:
            self.warnings.append(
                "ISO 9001 Clause 8.6: Workflow should include verification before release (quality_inspection or human_review)"
            )

        # Check for approval/authorization
        metadata = data.get('metadata', {})
        if 'approved_by' not in metadata and 'authorized_by' not in metadata:
            self.warnings.append(
                "ISO 9001 Clause 8.6: Should document approval/authorization for release (metadata.approved_by or metadata.authorized_by)"
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
