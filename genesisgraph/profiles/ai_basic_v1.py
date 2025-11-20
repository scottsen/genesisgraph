"""
AI Basic Profile Validator (gg-ai-basic-v1)

Validates AI/ML pipeline workflows for compliance with best practices
and regulatory requirements (FDA 21 CFR Part 11, etc.).
"""

from typing import Dict, List, Set
from .base import BaseProfileValidator


class AIBasicV1Validator(BaseProfileValidator):
    """
    Validator for gg-ai-basic-v1 profile

    This profile enforces requirements for AI/ML pipelines including:
    - Required parameters for AI operations (temperature, model identity, etc.)
    - Human review requirements for high-risk decisions
    - Attestation requirements for AI-generated content
    - Data lineage tracking for training and inference
    """

    profile_id = "gg-ai-basic-v1"
    profile_version = "1.0.0"

    # Required parameters for AI operations
    REQUIRED_PARAMS = {
        'ai_inference': [
            'temperature',
            'top_p',
            'prompt_length_chars',
            'model_name',
            'model_version'
        ],
        'ai_retrieval': [
            'query_length_chars',
            'max_results',
            'similarity_threshold'
        ],
        'ai_moderation': [
            'categories',
            'threshold'
        ],
        'ai_training': [
            'dataset_size',
            'training_duration_seconds',
            'validation_split',
            'model_architecture'
        ],
    }

    # Operations that require human review
    HUMAN_REVIEW_REQUIRED = {
        'ai_inference',  # When used for high-stakes decisions
    }

    # Allowed tool types for AI operations
    ALLOWED_TOOL_TYPES = {
        'AIModel',
        'Software',
        'Human',
        'Service'
    }

    # Required attestation modes for AI operations
    REQUIRED_ATTESTATION_MODES = {
        'signed',
        'verifiable',
        'zk'
    }

    def _validate_operations(self, operations: List[Dict]) -> List[str]:
        """Validate AI-specific operation requirements"""
        errors = []

        # Track if we have human review in the workflow
        has_human_review = any(
            op.get('type') == 'human_review'
            for op in operations
        )

        for op in operations:
            op_type = op.get('type')
            op_id = op.get('id', '<unknown>')

            # Check required parameters for AI operations
            if op_type in self.REQUIRED_PARAMS:
                required = self.REQUIRED_PARAMS[op_type]
                param_errors = self._check_required_parameters(op, required)
                errors.extend(param_errors)

                # Validate specific parameter values
                parameters = op.get('parameters', {})
                if not parameters.get('_redacted'):
                    # Temperature should be between 0 and 2
                    if 'temperature' in parameters:
                        temp = parameters['temperature']
                        if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                            errors.append(
                                f"Operation '{op_id}': temperature must be between 0 and 2, got {temp}"
                            )

                    # Top_p should be between 0 and 1
                    if 'top_p' in parameters:
                        top_p = parameters['top_p']
                        if not isinstance(top_p, (int, float)) or top_p < 0 or top_p > 1:
                            errors.append(
                                f"Operation '{op_id}': top_p must be between 0 and 1, got {top_p}"
                            )

                    # Similarity threshold should be between 0 and 1
                    if 'similarity_threshold' in parameters:
                        threshold = parameters['similarity_threshold']
                        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
                            errors.append(
                                f"Operation '{op_id}': similarity_threshold must be between 0 and 1, got {threshold}"
                            )

            # Check attestation requirements for AI operations
            if op_type in ['ai_inference', 'ai_training', 'ai_moderation']:
                attestation = op.get('attestation')
                if not attestation:
                    self.warnings.append(
                        f"Operation '{op_id}': AI operations should have attestation for compliance"
                    )
                else:
                    attest_errors = self._check_attestation_mode(
                        op,
                        self.REQUIRED_ATTESTATION_MODES
                    )
                    # Convert to warnings for flexibility
                    for error in attest_errors:
                        self.warnings.append(error.replace("not allowed", "recommended"))

            # Check for human review requirement
            if op_type in self.HUMAN_REVIEW_REQUIRED:
                # Check if this operation's outputs go to a human review
                outputs = op.get('outputs', [])
                has_review_downstream = self._check_human_review_downstream(
                    outputs, operations
                )
                if not has_review_downstream and not has_human_review:
                    self.warnings.append(
                        f"Operation '{op_id}': AI inference operations should include "
                        f"human review for high-stakes decisions (FDA 21 CFR Part 11)"
                    )

        return errors

    def _validate_tools(self, tools: List[Dict]) -> List[str]:
        """Validate tool requirements for AI operations"""
        errors = []

        # Check for AI model tools
        ai_models = [t for t in tools if t.get('type') == 'AIModel']

        for model in ai_models:
            model_id = model.get('id', '<unknown>')

            # AI models should have version information
            if 'version' not in model:
                errors.append(
                    f"Tool '{model_id}': AIModel tools must specify version for reproducibility"
                )

            # AI models should have identity (DID or URI)
            if 'did' not in model and 'uri' not in model:
                self.warnings.append(
                    f"Tool '{model_id}': AIModel tools should have 'did' or 'uri' for identity verification"
                )

        return errors

    def _validate_entities(self, entities: List[Dict]) -> List[str]:
        """Validate entity requirements for AI workflows"""
        errors = []

        # Check for Dataset and Model entities
        for entity in entities:
            entity_type = entity.get('type')
            entity_id = entity.get('id', '<unknown>')

            # Datasets should have hash for integrity
            if entity_type == 'Dataset':
                if 'hash' not in entity:
                    errors.append(
                        f"Entity '{entity_id}': Dataset entities must have 'hash' for data integrity (FDA 21 CFR Part 11)"
                    )

            # AI Models should have version and hash
            if entity_type == 'Model':
                if 'version' not in entity:
                    errors.append(
                        f"Entity '{entity_id}': Model entities must have 'version' for reproducibility"
                    )
                if 'hash' not in entity:
                    self.warnings.append(
                        f"Entity '{entity_id}': Model entities should have 'hash' for integrity verification"
                    )

        return errors

    def _check_human_review_downstream(
        self,
        outputs: List[str],
        operations: List[Dict]
    ) -> bool:
        """
        Check if any of the outputs flow to a human_review operation

        Args:
            outputs: List of output entity IDs
            operations: All operations in the workflow

        Returns:
            True if human review is found downstream
        """
        # Build a graph of entity flows
        for op in operations:
            if op.get('type') == 'human_review':
                inputs = op.get('inputs', [])
                # Check if any of our outputs are inputs to human review
                if any(output_id in inputs for output_id in outputs):
                    return True

        return False

    def _validate_custom(self, data: Dict) -> List[str]:
        """Custom validation for AI workflows"""
        errors = []

        # Check for required metadata
        metadata = data.get('metadata', {})

        # AI workflows should declare their purpose
        if 'description' not in metadata:
            self.warnings.append(
                "AI workflows should include 'metadata.description' for transparency"
            )

        # Check for responsible AI metadata
        if 'responsible_ai' in metadata:
            responsible_ai = metadata['responsible_ai']

            # Validate bias assessment
            if 'bias_assessment' in responsible_ai:
                bias = responsible_ai['bias_assessment']
                if not isinstance(bias, dict):
                    errors.append(
                        "metadata.responsible_ai.bias_assessment must be an object"
                    )

            # Validate fairness metrics
            if 'fairness_metrics' in responsible_ai:
                fairness = responsible_ai['fairness_metrics']
                if not isinstance(fairness, dict):
                    errors.append(
                        "metadata.responsible_ai.fairness_metrics must be an object"
                    )

        return errors
