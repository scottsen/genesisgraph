"""
GenesisGraph Builder API

Provides a fluent Python API for constructing GenesisGraph documents.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


class Entity:
    """Represents an entity (artifact) in a GenesisGraph document."""

    def __init__(
        self,
        id: str,
        type: str,
        version: str,
        file: Optional[str] = None,
        uri: Optional[str] = None,
        hash: Optional[str] = None,
        derived_from: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Create an entity.

        Args:
            id: Local identifier for this entity
            type: Entity type (e.g., Dataset, AIModel, CADModel)
            version: Version string
            file: Local file path (required if uri not provided)
            uri: Remote URI (required if file not provided)
            hash: Cryptographic hash in format "algo:hexdigest"
            derived_from: List of parent entity references in format "id@version"
            metadata: Additional domain-specific metadata
        """
        if not file and not uri:
            raise ValueError("Entity must have either 'file' or 'uri'")

        self.id = id
        self.type = type
        self.version = version
        self.file = file
        self.uri = uri
        self.hash = hash
        self.derived_from = derived_from or []
        self.metadata = metadata or {}

    def reference(self) -> str:
        """Get the reference string for this entity (id@version)."""
        return f"{self.id}@{self.version}"

    def compute_hash(
        self, algorithm: str = "sha256", file_path: Optional[str] = None
    ) -> "Entity":
        """
        Compute and set the hash for this entity's file.

        Args:
            algorithm: Hash algorithm (sha256, sha512, blake3)
            file_path: Path to file (uses self.file if not provided)

        Returns:
            Self for method chaining
        """
        if algorithm not in ["sha256", "sha512", "blake3"]:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        path = file_path or self.file
        if not path:
            raise ValueError("No file path available for hashing")

        hasher = hashlib.new(algorithm)
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        self.hash = f"{algorithm}:{hasher.hexdigest()}"
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary format."""
        result: Dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "version": self.version,
        }

        if self.file:
            result["file"] = self.file
        if self.uri:
            result["uri"] = self.uri
        if self.hash:
            result["hash"] = self.hash
        if self.derived_from:
            result["derived_from"] = self.derived_from
        if self.metadata:
            result["metadata"] = self.metadata

        return result


class Tool:
    """Represents a tool/agent in a GenesisGraph document."""

    def __init__(
        self,
        id: str,
        type: str,
        vendor: Optional[str] = None,
        version: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        identity: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Create a tool.

        Args:
            id: Tool identifier
            type: Tool type (Software, Machine, Human, AIModel, Service)
            vendor: Vendor name
            version: Version string
            capabilities: Capability declarations
            identity: Identity information (did, certificate)
            metadata: Additional metadata
        """
        if type not in ["Software", "Machine", "Human", "AIModel", "Service"]:
            raise ValueError(f"Invalid tool type: {type}")

        self.id = id
        self.type = type
        self.vendor = vendor
        self.version = version
        self.capabilities = capabilities or {}
        self.identity = identity or {}
        self.metadata = metadata or {}

    def reference(self) -> str:
        """Get the reference string for this tool (id@version)."""
        if self.version:
            return f"{self.id}@{self.version}"
        return f"{self.id}@"

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format."""
        result: Dict[str, Any] = {
            "id": self.id,
            "type": self.type,
        }

        if self.vendor:
            result["vendor"] = self.vendor
        if self.version:
            result["version"] = self.version
        if self.capabilities:
            result["capabilities"] = self.capabilities
        if self.identity:
            result["identity"] = self.identity
        if self.metadata:
            result["metadata"] = self.metadata

        return result


class Attestation:
    """Represents an attestation in a GenesisGraph document."""

    def __init__(
        self,
        mode: str,
        timestamp: Optional[str] = None,
        signer: Optional[str] = None,
        signature: Optional[str] = None,
        delegation: Optional[str] = None,
        claims: Optional[Dict[str, Any]] = None,
        transparency: Optional[List[Dict[str, Any]]] = None,
        tee: Optional[Dict[str, Any]] = None,
        multisig: Optional[Dict[str, Any]] = None,
    ):
        """
        Create an attestation.

        Args:
            mode: Attestation mode (basic, signed, verifiable, zk)
            timestamp: ISO 8601 timestamp
            signer: DID of the signer
            signature: Signature in format "algorithm:signature"
            delegation: DID of delegating authority
            claims: Policy attestation claims
            transparency: Transparency log entries
            tee: TEE attestation
            multisig: Multi-signature configuration
        """
        if mode not in ["basic", "signed", "verifiable", "zk"]:
            raise ValueError(f"Invalid attestation mode: {mode}")

        if mode in ["signed", "verifiable", "zk"] and (not signer or not signature):
            raise ValueError(f"Mode '{mode}' requires both signer and signature")

        self.mode = mode
        self.timestamp = timestamp or datetime.utcnow().isoformat() + "Z"
        self.signer = signer
        self.signature = signature
        self.delegation = delegation
        self.claims = claims
        self.transparency = transparency
        self.tee = tee
        self.multisig = multisig

    def to_dict(self) -> Dict[str, Any]:
        """Convert attestation to dictionary format."""
        result: Dict[str, Any] = {
            "mode": self.mode,
            "timestamp": self.timestamp,
        }

        if self.signer:
            result["signer"] = self.signer
        if self.signature:
            result["signature"] = self.signature
        if self.delegation:
            result["delegation"] = self.delegation
        if self.claims:
            result["claims"] = self.claims
        if self.transparency:
            result["transparency"] = self.transparency
        if self.tee:
            result["tee"] = self.tee
        if self.multisig:
            result["multisig"] = self.multisig

        return result


class Operation:
    """Represents an operation in a GenesisGraph document."""

    def __init__(
        self,
        id: str,
        type: str,
        inputs: Optional[List[Union[str, Entity]]] = None,
        outputs: Optional[List[Union[str, Entity]]] = None,
        tool: Optional[Union[str, Tool]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        fidelity: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        attestation: Optional[Union[Attestation, Dict[str, Any]]] = None,
        sealed: Optional[Dict[str, Any]] = None,
        reproducibility: Optional[Dict[str, Any]] = None,
        work_proof: Optional[Dict[str, Any]] = None,
        resource_usage: Optional[Dict[str, Any]] = None,
        realized_capability: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Create an operation.

        Args:
            id: Operation identifier
            type: Operation type (e.g., ai_inference, tessellation)
            inputs: Input entity references
            outputs: Output entity references
            tool: Tool reference
            parameters: Operation parameters
            fidelity: Fidelity/loss tracking
            metrics: Measured metrics
            attestation: Operation attestation
            sealed: Sealed subgraph information
            reproducibility: Reproducibility metadata
            work_proof: Proof of work
            resource_usage: Resource usage metrics
            realized_capability: Actual capability used
            metadata: Additional metadata
        """
        self.id = id
        self.type = type
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.tool = tool
        self.parameters = parameters or {}
        self.fidelity = fidelity
        self.metrics = metrics or {}
        self.attestation = attestation
        self.sealed = sealed
        self.reproducibility = reproducibility
        self.work_proof = work_proof
        self.resource_usage = resource_usage
        self.realized_capability = realized_capability
        self.metadata = metadata or {}

    def add_input(self, entity: Union[str, Entity]) -> "Operation":
        """Add an input entity. Returns self for chaining."""
        ref = entity.reference() if isinstance(entity, Entity) else entity
        self.inputs.append(ref)
        return self

    def add_output(self, entity: Union[str, Entity]) -> "Operation":
        """Add an output entity. Returns self for chaining."""
        ref = entity.reference() if isinstance(entity, Entity) else entity
        self.outputs.append(ref)
        return self

    def set_tool(self, tool: Union[str, Tool]) -> "Operation":
        """Set the tool for this operation. Returns self for chaining."""
        self.tool = tool.reference() if isinstance(tool, Tool) else tool
        return self

    def set_parameters(self, parameters: Dict[str, Any]) -> "Operation":
        """Set operation parameters. Returns self for chaining."""
        self.parameters = parameters
        return self

    def set_attestation(self, attestation: Union[Attestation, Dict[str, Any]]) -> "Operation":
        """Set operation attestation. Returns self for chaining."""
        self.attestation = attestation
        return self

    def redact_parameters(self) -> "Operation":
        """Redact parameters for selective disclosure. Returns self for chaining."""
        self.parameters = {"_redacted": True}
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary format."""
        result: Dict[str, Any] = {
            "id": self.id,
            "type": self.type,
        }

        if self.inputs:
            result["inputs"] = self.inputs
        if self.outputs:
            result["outputs"] = self.outputs
        if self.tool:
            result["tool"] = self.tool
        if self.parameters:
            result["parameters"] = self.parameters
        if self.fidelity:
            result["fidelity"] = self.fidelity
        if self.metrics:
            result["metrics"] = self.metrics
        if self.attestation:
            if isinstance(self.attestation, Attestation):
                result["attestation"] = self.attestation.to_dict()
            else:
                result["attestation"] = self.attestation
        if self.sealed:
            result["sealed"] = self.sealed
        if self.reproducibility:
            result["reproducibility"] = self.reproducibility
        if self.work_proof:
            result["work_proof"] = self.work_proof
        if self.resource_usage:
            result["resource_usage"] = self.resource_usage
        if self.realized_capability:
            result["realized_capability"] = self.realized_capability
        if self.metadata:
            result["metadata"] = self.metadata

        return result


class GenesisGraph:
    """
    Main builder class for constructing GenesisGraph documents.

    Example:
        >>> gg = GenesisGraph(spec_version="0.1.0")
        >>> tool = Tool(id="mytool", type="Software", version="1.0")
        >>> gg.add_tool(tool)
        >>> entity = Entity(id="data", type="Dataset", version="1", uri="s3://bucket/data")
        >>> gg.add_entity(entity)
        >>> op = Operation(id="op1", type="transform")
        >>> op.add_input(entity).set_tool(tool)
        >>> gg.add_operation(op)
        >>> yaml_output = gg.to_yaml()
    """

    def __init__(
        self,
        spec_version: str = "0.1.0",
        profile: Optional[str] = None,
        imports: Optional[List[str]] = None,
        namespaces: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Create a GenesisGraph document builder.

        Args:
            spec_version: GenesisGraph specification version
            profile: Profile identifier (e.g., gg-ai-basic-v1)
            imports: Namespace imports
            namespaces: Namespace mappings
            context: Execution context
            metadata: Document-level metadata
        """
        self.spec_version = spec_version
        self.profile = profile
        self.imports = imports or []
        self.namespaces = namespaces or {}
        self.context = context or {}
        self.metadata = metadata or {}
        self.tools: List[Tool] = []
        self.entities: List[Entity] = []
        self.operations: List[Operation] = []

    def add_tool(self, tool: Tool) -> "GenesisGraph":
        """Add a tool to the document. Returns self for chaining."""
        self.tools.append(tool)
        return self

    def add_entity(self, entity: Entity) -> "GenesisGraph":
        """Add an entity to the document. Returns self for chaining."""
        self.entities.append(entity)
        return self

    def add_operation(self, operation: Operation) -> "GenesisGraph":
        """Add an operation to the document. Returns self for chaining."""
        self.operations.append(operation)
        return self

    def set_profile(self, profile: str) -> "GenesisGraph":
        """Set the profile identifier. Returns self for chaining."""
        self.profile = profile
        return self

    def set_context(self, context: Dict[str, Any]) -> "GenesisGraph":
        """Set the execution context. Returns self for chaining."""
        self.context = context
        return self

    def add_namespace(self, prefix: str, uri: str) -> "GenesisGraph":
        """Add a namespace mapping. Returns self for chaining."""
        self.namespaces[prefix] = uri
        return self

    def add_import(self, uri: str) -> "GenesisGraph":
        """Add a namespace import. Returns self for chaining."""
        self.imports.append(uri)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary."""
        result: Dict[str, Any] = {
            "spec_version": self.spec_version,
        }

        if self.profile:
            result["profile"] = self.profile
        if self.imports:
            result["imports"] = self.imports
        if self.namespaces:
            result["namespaces"] = self.namespaces
        if self.context:
            result["context"] = self.context
        if self.tools:
            result["tools"] = [tool.to_dict() for tool in self.tools]
        if self.entities:
            result["entities"] = [entity.to_dict() for entity in self.entities]
        if self.operations:
            result["operations"] = [op.to_dict() for op in self.operations]
        if self.metadata:
            result["metadata"] = self.metadata

        return result

    def to_yaml(self, **kwargs) -> str:
        """
        Convert the document to YAML format.

        Args:
            **kwargs: Additional arguments passed to yaml.dump()

        Returns:
            YAML string representation
        """
        defaults = {
            "default_flow_style": False,
            "sort_keys": False,
            "allow_unicode": True,
        }
        defaults.update(kwargs)
        return yaml.dump(self.to_dict(), **defaults)

    def to_json(self, **kwargs) -> str:
        """
        Convert the document to JSON format.

        Args:
            **kwargs: Additional arguments passed to json.dumps()

        Returns:
            JSON string representation
        """
        defaults = {
            "indent": 2,
            "sort_keys": False,
        }
        defaults.update(kwargs)
        return json.dumps(self.to_dict(), **defaults)

    def to_canonical_json(self) -> str:
        """
        Convert to canonical JSON format for signing.

        Returns:
            Canonical JSON string (sorted keys, no whitespace)
        """
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def save_yaml(self, path: Union[str, Path], **kwargs) -> None:
        """Save the document to a YAML file."""
        with open(path, "w") as f:
            f.write(self.to_yaml(**kwargs))

    def save_json(self, path: Union[str, Path], **kwargs) -> None:
        """Save the document to a JSON file."""
        with open(path, "w") as f:
            f.write(self.to_json(**kwargs))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenesisGraph":
        """Create a GenesisGraph document from a dictionary."""
        gg = cls(
            spec_version=data.get("spec_version", "0.1.0"),
            profile=data.get("profile"),
            imports=data.get("imports"),
            namespaces=data.get("namespaces"),
            context=data.get("context"),
            metadata=data.get("metadata"),
        )

        # Add tools
        for tool_data in data.get("tools", []):
            tool = Tool(**tool_data)
            gg.add_tool(tool)

        # Add entities
        for entity_data in data.get("entities", []):
            entity = Entity(**entity_data)
            gg.add_entity(entity)

        # Add operations
        for op_data in data.get("operations", []):
            operation = Operation(**op_data)
            gg.add_operation(operation)

        return gg

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "GenesisGraph":
        """Create a GenesisGraph document from a YAML string."""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    @classmethod
    def from_json(cls, json_str: str) -> "GenesisGraph":
        """Create a GenesisGraph document from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def load_yaml(cls, path: Union[str, Path]) -> "GenesisGraph":
        """Load a GenesisGraph document from a YAML file."""
        with open(path) as f:
            return cls.from_yaml(f.read())

    @classmethod
    def load_json(cls, path: Union[str, Path]) -> "GenesisGraph":
        """Load a GenesisGraph document from a JSON file."""
        with open(path) as f:
            return cls.from_json(f.read())

    def validate(self, **kwargs) -> Any:
        """
        Validate the document using GenesisGraphValidator.

        Args:
            **kwargs: Additional arguments passed to the validator

        Returns:
            ValidationResult object
        """
        from .validator import GenesisGraphValidator

        validator = GenesisGraphValidator(**kwargs)
        return validator.validate(self.to_dict())
