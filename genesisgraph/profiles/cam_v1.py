"""
Computer-Aided Manufacturing Profile Validator (gg-cam-v1)

Validates manufacturing workflows for compliance with ISO-9001 quality standards
and industry best practices.
"""

from typing import Dict, List

from .base import BaseProfileValidator


class CAMv1Validator(BaseProfileValidator):
    """
    Validator for gg-cam-v1 profile

    This profile enforces requirements for manufacturing workflows including:
    - Tolerance and dimensional accuracy tracking (ISO-9001)
    - Machine tool identification and calibration
    - Material traceability
    - Post-processor validation for CNC operations
    - Quality control checkpoints
    """

    profile_id = "gg-cam-v1"
    profile_version = "1.0.0"

    # Required parameters for manufacturing operations
    REQUIRED_PARAMS = {
        'cnc_machining': [
            'tolerance_mm',
            'material',
            'feed_rate_mm_per_min',
            'spindle_speed_rpm',
            'tool_number'
        ],
        'additive_manufacturing': [
            'layer_height_mm',
            'material',
            'temperature_celsius',
            'print_speed_mm_per_s'
        ],
        'tessellation': [
            'max_chord_error_mm',
            'max_angle_deg'
        ],
        'slicing': [
            'layer_height_mm',
            'infill_percent'
        ],
        'post_processing': [
            'operation_type',
            'target_finish_ra_um'  # Surface roughness in micrometers
        ],
        'quality_inspection': [
            'inspection_type',
            'acceptance_criteria',
            'measurement_uncertainty_mm'
        ]
    }

    # Operations requiring calibration verification
    CALIBRATION_REQUIRED = {
        'cnc_machining',
        'additive_manufacturing',
        'quality_inspection'
    }

    # Allowed tool types for manufacturing
    ALLOWED_TOOL_TYPES = {
        'Machine',
        'Software',
        'Human'
    }

    # Required attestation modes for manufacturing operations
    REQUIRED_ATTESTATION_MODES = {
        'signed',
        'verifiable'
    }

    def _validate_operations(self, operations: List[Dict]) -> List[str]:
        """Validate manufacturing-specific operation requirements"""
        errors = []

        # Track quality checkpoints
        has_quality_inspection = any(
            op.get('type') == 'quality_inspection'
            for op in operations
        )

        if not has_quality_inspection:
            self.warnings.append(
                "Manufacturing workflows should include 'quality_inspection' operations for ISO-9001 compliance"
            )

        for op in operations:
            op_type = op.get('type')
            op_id = op.get('id', '<unknown>')

            # Check required parameters for manufacturing operations
            if op_type in self.REQUIRED_PARAMS:
                required = self.REQUIRED_PARAMS[op_type]
                param_errors = self._check_required_parameters(op, required)
                errors.extend(param_errors)

                # Validate specific parameter values
                parameters = op.get('parameters', {})
                if not parameters.get('_redacted'):
                    # Tolerance must be positive
                    if 'tolerance_mm' in parameters:
                        tolerance = parameters['tolerance_mm']
                        if not isinstance(tolerance, (int, float)) or tolerance <= 0:
                            errors.append(
                                f"Operation '{op_id}': tolerance_mm must be a positive number, got {tolerance}"
                            )

                    # Feed rate must be positive
                    if 'feed_rate_mm_per_min' in parameters:
                        feed_rate = parameters['feed_rate_mm_per_min']
                        if not isinstance(feed_rate, (int, float)) or feed_rate <= 0:
                            errors.append(
                                f"Operation '{op_id}': feed_rate_mm_per_min must be positive, got {feed_rate}"
                            )

                    # Spindle speed must be positive
                    if 'spindle_speed_rpm' in parameters:
                        speed = parameters['spindle_speed_rpm']
                        if not isinstance(speed, (int, float)) or speed <= 0:
                            errors.append(
                                f"Operation '{op_id}': spindle_speed_rpm must be positive, got {speed}"
                            )

                    # Layer height must be positive
                    if 'layer_height_mm' in parameters:
                        layer_height = parameters['layer_height_mm']
                        if not isinstance(layer_height, (int, float)) or layer_height <= 0:
                            errors.append(
                                f"Operation '{op_id}': layer_height_mm must be positive, got {layer_height}"
                            )

                    # Temperature must be reasonable (0-500°C for most processes)
                    if 'temperature_celsius' in parameters:
                        temp = parameters['temperature_celsius']
                        if not isinstance(temp, (int, float)) or temp < 0 or temp > 500:
                            self.warnings.append(
                                f"Operation '{op_id}': temperature_celsius {temp} is outside typical range (0-500)"
                            )

                    # Infill must be between 0 and 100%
                    if 'infill_percent' in parameters:
                        infill = parameters['infill_percent']
                        if not isinstance(infill, (int, float)) or infill < 0 or infill > 100:
                            errors.append(
                                f"Operation '{op_id}': infill_percent must be between 0 and 100, got {infill}"
                            )

            # Check calibration requirements
            if op_type in self.CALIBRATION_REQUIRED:
                tool_ref = op.get('tool')
                if tool_ref:
                    # Tool should have calibration metadata
                    self._add_calibration_warning(op_id, tool_ref)

            # Check attestation for critical operations
            if op_type in ['cnc_machining', 'additive_manufacturing', 'quality_inspection']:
                attestation = op.get('attestation')
                if not attestation:
                    errors.append(
                        f"Operation '{op_id}': Critical manufacturing operations must have attestation (ISO-9001)"
                    )
                else:
                    mode = attestation.get('mode')
                    if mode not in self.REQUIRED_ATTESTATION_MODES:
                        errors.append(
                            f"Operation '{op_id}': Manufacturing operations require 'signed' or 'verifiable' attestation, got '{mode}'"
                        )

            # CNC operations should reference a post-processor
            if op_type == 'cnc_machining':
                parameters = op.get('parameters', {})
                if 'post_processor' not in parameters and not parameters.get('_redacted'):
                    self.warnings.append(
                        f"Operation '{op_id}': CNC operations should specify 'post_processor' for machine compatibility"
                    )

        return errors

    def _validate_tools(self, tools: List[Dict]) -> List[str]:
        """Validate tool requirements for manufacturing"""
        errors = []

        # Check for machine tools
        machines = [t for t in tools if t.get('type') == 'Machine']

        for machine in machines:
            machine_id = machine.get('id', '<unknown>')

            # Machines must have identity (DID or URI)
            if 'did' not in machine and 'uri' not in machine:
                errors.append(
                    f"Tool '{machine_id}': Machine tools must have 'did' or 'uri' for identification (ISO-9001)"
                )

            # Machines should have calibration metadata
            metadata = machine.get('metadata', {})
            if 'calibration_date' not in metadata:
                self.warnings.append(
                    f"Tool '{machine_id}': Machine tools should have 'metadata.calibration_date' for ISO-9001 compliance"
                )

            if 'calibration_certificate' not in metadata:
                self.warnings.append(
                    f"Tool '{machine_id}': Machine tools should have 'metadata.calibration_certificate' reference"
                )

            # Check for maintenance records
            if 'last_maintenance_date' not in metadata:
                self.warnings.append(
                    f"Tool '{machine_id}': Machine tools should have 'metadata.last_maintenance_date' for ISO-9001 compliance"
                )

        return errors

    def _validate_entities(self, entities: List[Dict]) -> List[str]:
        """Validate entity requirements for manufacturing workflows"""
        errors = []

        # Check for CADModel and Mesh entities
        for entity in entities:
            entity_type = entity.get('type')
            entity_id = entity.get('id', '<unknown>')

            # CAD models should have hash for integrity (ISO-9001)
            if entity_type == 'CADModel':
                if 'hash' not in entity:
                    errors.append(
                        f"Entity '{entity_id}': CADModel entities must have 'hash' for version control (ISO-9001)"
                    )

                # Should have version information
                if 'version' not in entity:
                    self.warnings.append(
                        f"Entity '{entity_id}': CADModel entities should have 'version' for change tracking"
                    )

            # Mesh entities should track fidelity loss
            if entity_type == 'Mesh':
                if 'fidelity' not in entity:
                    self.warnings.append(
                        f"Entity '{entity_id}': Mesh entities should specify 'fidelity' to track geometric accuracy"
                    )
                else:
                    fidelity = entity['fidelity']
                    if 'type' in fidelity and fidelity['type'] == 'geometric_approximation':
                        if 'max_deviation_mm' not in fidelity:
                            self.warnings.append(
                                f"Entity '{entity_id}': geometric_approximation should specify 'max_deviation_mm'"
                            )

            # Material entities should have specifications
            if entity_type == 'Material':
                metadata = entity.get('metadata', {})
                if 'material_grade' not in metadata:
                    self.warnings.append(
                        f"Entity '{entity_id}': Material entities should specify 'metadata.material_grade'"
                    )
                if 'material_certificate' not in metadata:
                    self.warnings.append(
                        f"Entity '{entity_id}': Material entities should reference 'metadata.material_certificate' for traceability"
                    )

        return errors

    def _add_calibration_warning(self, op_id: str, tool_ref: str):
        """Helper to add calibration warning"""
        self.warnings.append(
            f"Operation '{op_id}': Tool '{tool_ref}' should have calibration metadata for ISO-9001 compliance"
        )

    def _validate_custom(self, data: Dict) -> List[str]:
        """Custom validation for manufacturing workflows"""
        errors = []

        # Check for required manufacturing metadata
        metadata = data.get('metadata', {})

        # Manufacturing workflows should declare quality standards
        if 'quality_standard' not in metadata:
            self.warnings.append(
                "Manufacturing workflows should include 'metadata.quality_standard' (e.g., 'ISO-9001:2015')"
            )

        # Check for part identification
        if 'part_number' not in metadata:
            self.warnings.append(
                "Manufacturing workflows should include 'metadata.part_number' for traceability"
            )

        # Check for material traceability
        if 'material_lot_number' in metadata:
            # If specified, should also have supplier info
            if 'material_supplier' not in metadata:
                self.warnings.append(
                    "When 'material_lot_number' is specified, 'material_supplier' should also be included"
                )

        # Validate ISO-9001 specific metadata
        if 'iso_9001' in metadata:
            iso_meta = metadata['iso_9001']

            # Check for quality records
            if 'quality_records' in iso_meta:
                if not isinstance(iso_meta['quality_records'], list):
                    errors.append(
                        "metadata.iso_9001.quality_records must be an array"
                    )

            # Check for nonconformance tracking
            if 'nonconformances' in iso_meta:
                if not isinstance(iso_meta['nonconformances'], list):
                    errors.append(
                        "metadata.iso_9001.nonconformances must be an array"
                    )

        return errors
