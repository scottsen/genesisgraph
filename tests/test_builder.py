"""Tests for the GenesisGraph Builder API."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from genesisgraph import (
    Attestation,
    Entity,
    GenesisGraph,
    Operation,
    Tool,
)


class TestEntity:
    """Test Entity class."""

    def test_create_entity_with_file(self):
        """Test creating an entity with a file path."""
        entity = Entity(
            id="test_data",
            type="Dataset",
            version="1.0",
            file="./data.csv",
            hash="sha256:abc123",
        )
        assert entity.id == "test_data"
        assert entity.type == "Dataset"
        assert entity.version == "1.0"
        assert entity.file == "./data.csv"
        assert entity.hash == "sha256:abc123"

    def test_create_entity_with_uri(self):
        """Test creating an entity with a URI."""
        entity = Entity(
            id="remote_data",
            type="Dataset",
            version="2.0",
            uri="s3://bucket/data.parquet",
            hash="sha256:def456",
        )
        assert entity.uri == "s3://bucket/data.parquet"
        assert entity.file is None

    def test_entity_requires_file_or_uri(self):
        """Test that entity requires either file or uri."""
        with pytest.raises(ValueError, match="must have either 'file' or 'uri'"):
            Entity(id="test", type="Dataset", version="1")

    def test_entity_reference(self):
        """Test entity reference generation."""
        entity = Entity(id="data", type="Dataset", version="1.5", file="./data.csv")
        assert entity.reference() == "data@1.5"

    def test_entity_derived_from(self):
        """Test entity with derived_from."""
        parent1 = Entity(id="parent1", type="Dataset", version="1", file="./p1.csv")
        parent2 = Entity(id="parent2", type="Dataset", version="2", file="./p2.csv")

        child = Entity(
            id="child",
            type="Dataset",
            version="1",
            file="./child.csv",
            derived_from=[parent1.reference(), parent2.reference()],
        )

        assert child.derived_from == ["parent1@1", "parent2@2"]

    def test_entity_metadata(self):
        """Test entity with metadata."""
        entity = Entity(
            id="data",
            type="Dataset",
            version="1",
            file="./data.csv",
            metadata={"rows": 1000, "columns": 50},
        )
        assert entity.metadata == {"rows": 1000, "columns": 50}

    def test_entity_to_dict(self):
        """Test entity serialization to dict."""
        entity = Entity(
            id="data",
            type="Dataset",
            version="1",
            file="./data.csv",
            hash="sha256:abc123",
            derived_from=["parent@1"],
            metadata={"key": "value"},
        )

        result = entity.to_dict()
        assert result == {
            "id": "data",
            "type": "Dataset",
            "version": "1",
            "file": "./data.csv",
            "hash": "sha256:abc123",
            "derived_from": ["parent@1"],
            "metadata": {"key": "value"},
        }

    def test_compute_hash(self):
        """Test hash computation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            entity = Entity(id="data", type="Text", version="1", file=temp_path)
            entity.compute_hash("sha256")

            assert entity.hash is not None
            assert entity.hash.startswith("sha256:")
        finally:
            Path(temp_path).unlink()

    def test_compute_hash_invalid_algorithm(self):
        """Test hash computation with invalid algorithm."""
        entity = Entity(id="data", type="Text", version="1", file="./test.txt")
        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            entity.compute_hash("md5")


class TestTool:
    """Test Tool class."""

    def test_create_tool(self):
        """Test creating a tool."""
        tool = Tool(
            id="llama3",
            type="AIModel",
            vendor="Meta",
            version="3.0",
            capabilities={"max_tokens": 8192},
        )

        assert tool.id == "llama3"
        assert tool.type == "AIModel"
        assert tool.vendor == "Meta"
        assert tool.version == "3.0"
        assert tool.capabilities == {"max_tokens": 8192}

    def test_tool_types(self):
        """Test valid tool types."""
        valid_types = ["Software", "Machine", "Human", "AIModel", "Service"]
        for tool_type in valid_types:
            tool = Tool(id="test", type=tool_type)
            assert tool.type == tool_type

    def test_tool_invalid_type(self):
        """Test invalid tool type raises error."""
        with pytest.raises(ValueError, match="Invalid tool type"):
            Tool(id="test", type="InvalidType")

    def test_tool_reference(self):
        """Test tool reference generation."""
        tool = Tool(id="mytool", type="Software", version="1.0")
        assert tool.reference() == "mytool@1.0"

        tool_no_version = Tool(id="mytool", type="Software")
        assert tool_no_version.reference() == "mytool@"

    def test_tool_with_identity(self):
        """Test tool with identity information."""
        tool = Tool(
            id="reviewer",
            type="Human",
            identity={
                "did": "did:person:alice",
                "certificate": "License-123",
            },
        )

        assert tool.identity["did"] == "did:person:alice"
        assert tool.identity["certificate"] == "License-123"

    def test_tool_to_dict(self):
        """Test tool serialization to dict."""
        tool = Tool(
            id="llama3",
            type="AIModel",
            vendor="Meta",
            version="3.0",
            capabilities={"max_tokens": 8192},
            identity={"did": "did:model:llama3"},
            metadata={"fine_tuned": False},
        )

        result = tool.to_dict()
        assert result["id"] == "llama3"
        assert result["type"] == "AIModel"
        assert result["vendor"] == "Meta"
        assert result["version"] == "3.0"
        assert result["capabilities"] == {"max_tokens": 8192}
        assert result["identity"] == {"did": "did:model:llama3"}
        assert result["metadata"] == {"fine_tuned": False}


class TestAttestation:
    """Test Attestation class."""

    def test_create_basic_attestation(self):
        """Test creating a basic attestation."""
        attestation = Attestation(mode="basic")
        assert attestation.mode == "basic"
        assert attestation.timestamp is not None

    def test_create_signed_attestation(self):
        """Test creating a signed attestation."""
        attestation = Attestation(
            mode="signed",
            signer="did:key:abc123",
            signature="ed25519:sig_xyz",
        )

        assert attestation.mode == "signed"
        assert attestation.signer == "did:key:abc123"
        assert attestation.signature == "ed25519:sig_xyz"

    def test_signed_attestation_requires_signer_and_signature(self):
        """Test that signed mode requires signer and signature."""
        with pytest.raises(ValueError, match="requires both signer and signature"):
            Attestation(mode="signed", signer="did:key:abc123")

        with pytest.raises(ValueError, match="requires both signer and signature"):
            Attestation(mode="signed", signature="ed25519:sig_xyz")

    def test_attestation_invalid_mode(self):
        """Test invalid attestation mode."""
        with pytest.raises(ValueError, match="Invalid attestation mode"):
            Attestation(mode="invalid_mode")

    def test_attestation_with_custom_timestamp(self):
        """Test attestation with custom timestamp."""
        timestamp = "2025-10-31T14:23:11Z"
        attestation = Attestation(mode="basic", timestamp=timestamp)
        assert attestation.timestamp == timestamp

    def test_attestation_to_dict(self):
        """Test attestation serialization to dict."""
        attestation = Attestation(
            mode="verifiable",
            signer="did:person:alice",
            signature="ed25519:sig123",
            delegation="did:org:hospital",
            timestamp="2025-10-31T14:23:11Z",
        )

        result = attestation.to_dict()
        assert result["mode"] == "verifiable"
        assert result["signer"] == "did:person:alice"
        assert result["signature"] == "ed25519:sig123"
        assert result["delegation"] == "did:org:hospital"
        assert result["timestamp"] == "2025-10-31T14:23:11Z"


class TestOperation:
    """Test Operation class."""

    def test_create_operation(self):
        """Test creating an operation."""
        op = Operation(id="op1", type="ai_inference")
        assert op.id == "op1"
        assert op.type == "ai_inference"

    def test_operation_add_input(self):
        """Test adding inputs to operation."""
        entity = Entity(id="data", type="Dataset", version="1", file="./data.csv")
        op = Operation(id="op1", type="transform")
        op.add_input(entity)

        assert op.inputs == ["data@1"]

    def test_operation_add_output(self):
        """Test adding outputs to operation."""
        entity = Entity(id="result", type="Dataset", version="1", file="./result.csv")
        op = Operation(id="op1", type="transform")
        op.add_output(entity)

        assert op.outputs == ["result@1"]

    def test_operation_set_tool(self):
        """Test setting tool for operation."""
        tool = Tool(id="mytool", type="Software", version="1.0")
        op = Operation(id="op1", type="transform")
        op.set_tool(tool)

        assert op.tool == "mytool@1.0"

    def test_operation_chaining(self):
        """Test method chaining."""
        tool = Tool(id="mytool", type="Software", version="1.0")
        input_entity = Entity(id="input", type="Dataset", version="1", file="./in.csv")
        output_entity = Entity(id="output", type="Dataset", version="1", file="./out.csv")

        op = (
            Operation(id="op1", type="transform")
            .add_input(input_entity)
            .add_output(output_entity)
            .set_tool(tool)
            .set_parameters({"param": "value"})
        )

        assert op.inputs == ["input@1"]
        assert op.outputs == ["output@1"]
        assert op.tool == "mytool@1.0"
        assert op.parameters == {"param": "value"}

    def test_operation_redact_parameters(self):
        """Test parameter redaction."""
        op = Operation(id="op1", type="transform", parameters={"secret": "value"})
        op.redact_parameters()

        assert op.parameters == {"_redacted": True}

    def test_operation_with_attestation(self):
        """Test operation with attestation."""
        attestation = Attestation(
            mode="signed",
            signer="did:key:abc",
            signature="ed25519:sig",
        )

        op = Operation(id="op1", type="transform")
        op.set_attestation(attestation)

        result = op.to_dict()
        assert "attestation" in result
        assert result["attestation"]["mode"] == "signed"

    def test_operation_to_dict(self):
        """Test operation serialization to dict."""
        op = Operation(
            id="op1",
            type="ai_inference",
            inputs=["input@1"],
            outputs=["output@1"],
            tool="llama3@3.0",
            parameters={"temperature": 0.2},
            metrics={"latency_ms": 100},
        )

        result = op.to_dict()
        assert result["id"] == "op1"
        assert result["type"] == "ai_inference"
        assert result["inputs"] == ["input@1"]
        assert result["outputs"] == ["output@1"]
        assert result["tool"] == "llama3@3.0"
        assert result["parameters"] == {"temperature": 0.2}
        assert result["metrics"] == {"latency_ms": 100}


class TestGenesisGraph:
    """Test GenesisGraph builder class."""

    def test_create_minimal_document(self):
        """Test creating a minimal valid document."""
        gg = GenesisGraph(spec_version="0.1.0")
        assert gg.spec_version == "0.1.0"

    def test_add_tool(self):
        """Test adding a tool to the document."""
        gg = GenesisGraph(spec_version="0.1.0")
        tool = Tool(id="mytool", type="Software", version="1.0")
        gg.add_tool(tool)

        assert len(gg.tools) == 1
        assert gg.tools[0].id == "mytool"

    def test_add_entity(self):
        """Test adding an entity to the document."""
        gg = GenesisGraph(spec_version="0.1.0")
        entity = Entity(id="data", type="Dataset", version="1", file="./data.csv")
        gg.add_entity(entity)

        assert len(gg.entities) == 1
        assert gg.entities[0].id == "data"

    def test_add_operation(self):
        """Test adding an operation to the document."""
        gg = GenesisGraph(spec_version="0.1.0")
        op = Operation(id="op1", type="transform")
        gg.add_operation(op)

        assert len(gg.operations) == 1
        assert gg.operations[0].id == "op1"

    def test_method_chaining(self):
        """Test method chaining for fluent API."""
        tool = Tool(id="mytool", type="Software", version="1.0")
        entity = Entity(id="data", type="Dataset", version="1", file="./data.csv")
        op = Operation(id="op1", type="transform")

        gg = (
            GenesisGraph(spec_version="0.1.0")
            .set_profile("gg-ai-basic-v1")
            .add_tool(tool)
            .add_entity(entity)
            .add_operation(op)
        )

        assert gg.profile == "gg-ai-basic-v1"
        assert len(gg.tools) == 1
        assert len(gg.entities) == 1
        assert len(gg.operations) == 1

    def test_set_context(self):
        """Test setting execution context."""
        gg = GenesisGraph(spec_version="0.1.0")
        gg.set_context({
            "environment": "docker://ubuntu:22.04",
            "hardware": "nvidia_a100",
        })

        assert gg.context["environment"] == "docker://ubuntu:22.04"
        assert gg.context["hardware"] == "nvidia_a100"

    def test_add_namespace(self):
        """Test adding namespace mappings."""
        gg = GenesisGraph(spec_version="0.1.0")
        gg.add_namespace("ai", "https://genesisgraph.dev/ns/ai/0.1")

        assert gg.namespaces["ai"] == "https://genesisgraph.dev/ns/ai/0.1"

    def test_add_import(self):
        """Test adding namespace imports."""
        gg = GenesisGraph(spec_version="0.1.0")
        gg.add_import("https://genesisgraph.dev/ns/core/0.1")

        assert "https://genesisgraph.dev/ns/core/0.1" in gg.imports

    def test_to_dict(self):
        """Test document serialization to dict."""
        tool = Tool(id="mytool", type="Software", version="1.0")
        entity = Entity(id="data", type="Dataset", version="1", file="./data.csv")
        op = Operation(id="op1", type="transform")

        gg = GenesisGraph(spec_version="0.1.0")
        gg.add_tool(tool)
        gg.add_entity(entity)
        gg.add_operation(op)

        result = gg.to_dict()
        assert result["spec_version"] == "0.1.0"
        assert len(result["tools"]) == 1
        assert len(result["entities"]) == 1
        assert len(result["operations"]) == 1

    def test_to_yaml(self):
        """Test document serialization to YAML."""
        gg = GenesisGraph(spec_version="0.1.0")
        tool = Tool(id="mytool", type="Software", version="1.0")
        gg.add_tool(tool)

        yaml_str = gg.to_yaml()
        assert "spec_version: 0.1.0" in yaml_str
        assert "mytool" in yaml_str

        # Verify it's valid YAML
        data = yaml.safe_load(yaml_str)
        assert data["spec_version"] == "0.1.0"

    def test_to_json(self):
        """Test document serialization to JSON."""
        gg = GenesisGraph(spec_version="0.1.0")
        tool = Tool(id="mytool", type="Software", version="1.0")
        gg.add_tool(tool)

        json_str = gg.to_json()
        assert "spec_version" in json_str
        assert "mytool" in json_str

        # Verify it's valid JSON
        data = json.loads(json_str)
        assert data["spec_version"] == "0.1.0"

    def test_to_canonical_json(self):
        """Test canonical JSON generation."""
        gg = GenesisGraph(spec_version="0.1.0")
        tool = Tool(id="mytool", type="Software", version="1.0")
        gg.add_tool(tool)

        canonical = gg.to_canonical_json()

        # Canonical JSON should have no whitespace and sorted keys
        assert " " not in canonical or canonical.count(" ") < 5
        data = json.loads(canonical)
        assert data["spec_version"] == "0.1.0"

    def test_save_and_load_yaml(self):
        """Test saving and loading YAML files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            # Create and save
            gg = GenesisGraph(spec_version="0.1.0")
            tool = Tool(id="mytool", type="Software", version="1.0")
            gg.add_tool(tool)
            gg.save_yaml(temp_path)

            # Load and verify
            loaded = GenesisGraph.load_yaml(temp_path)
            assert loaded.spec_version == "0.1.0"
            assert len(loaded.tools) == 1
            assert loaded.tools[0].id == "mytool"
        finally:
            Path(temp_path).unlink()

    def test_save_and_load_json(self):
        """Test saving and loading JSON files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            # Create and save
            gg = GenesisGraph(spec_version="0.1.0")
            tool = Tool(id="mytool", type="Software", version="1.0")
            gg.add_tool(tool)
            gg.save_json(temp_path)

            # Load and verify
            loaded = GenesisGraph.load_json(temp_path)
            assert loaded.spec_version == "0.1.0"
            assert len(loaded.tools) == 1
            assert loaded.tools[0].id == "mytool"
        finally:
            Path(temp_path).unlink()

    def test_from_yaml(self):
        """Test creating document from YAML string."""
        yaml_str = """
spec_version: 0.1.0
tools:
  - id: mytool
    type: Software
    version: 1.0
entities:
  - id: data
    type: Dataset
    version: "1"
    file: ./data.csv
operations:
  - id: op1
    type: transform
"""
        gg = GenesisGraph.from_yaml(yaml_str)
        assert gg.spec_version == "0.1.0"
        assert len(gg.tools) == 1
        assert len(gg.entities) == 1
        assert len(gg.operations) == 1

    def test_from_json(self):
        """Test creating document from JSON string."""
        json_str = """
{
  "spec_version": "0.1.0",
  "tools": [
    {"id": "mytool", "type": "Software", "version": "1.0"}
  ]
}
"""
        gg = GenesisGraph.from_json(json_str)
        assert gg.spec_version == "0.1.0"
        assert len(gg.tools) == 1

    def test_complete_workflow(self):
        """Test a complete workflow construction."""
        # Create document
        gg = GenesisGraph(spec_version="0.1.0")
        gg.set_profile("gg-ai-basic-v1")
        gg.set_context({
            "environment": "docker://ubuntu:22.04",
            "hardware": "nvidia_a100",
        })

        # Add tool
        tool = Tool(
            id="llama3",
            type="AIModel",
            vendor="Meta",
            version="3.0",
            capabilities={"max_tokens": 8192},
        )
        gg.add_tool(tool)

        # Add entities
        input_data = Entity(
            id="medical_corpus",
            type="Dataset",
            version="2025-10-15",
            uri="s3://medical-kb/corpus.parquet",
            hash="sha256:abc123",
        )

        output_data = Entity(
            id="answer",
            type="Text",
            version="1",
            file="./answer.txt",
            hash="sha256:def456",
            derived_from=[input_data.reference()],
        )

        gg.add_entity(input_data)
        gg.add_entity(output_data)

        # Add operation
        attestation = Attestation(
            mode="signed",
            signer="did:model:llama3",
            signature="ed25519:sig123",
        )

        op = Operation(id="op1", type="ai_inference")
        op.add_input(input_data)
        op.add_output(output_data)
        op.set_tool(tool)
        op.set_parameters({"temperature": 0.2, "max_tokens": 512})
        op.set_attestation(attestation)
        gg.add_operation(op)

        # Verify document structure
        result = gg.to_dict()
        assert result["spec_version"] == "0.1.0"
        assert result["profile"] == "gg-ai-basic-v1"
        assert len(result["tools"]) == 1
        assert len(result["entities"]) == 2
        assert len(result["operations"]) == 1
        assert result["operations"][0]["attestation"]["mode"] == "signed"


class TestIntegration:
    """Integration tests."""

    def test_round_trip_yaml(self):
        """Test YAML round-trip conversion."""
        # Create document
        gg1 = GenesisGraph(spec_version="0.1.0")
        tool = Tool(id="mytool", type="Software", version="1.0")
        entity = Entity(id="data", type="Dataset", version="1", file="./data.csv")
        gg1.add_tool(tool)
        gg1.add_entity(entity)

        # Convert to YAML and back
        yaml_str = gg1.to_yaml()
        gg2 = GenesisGraph.from_yaml(yaml_str)

        # Verify they're equivalent
        assert gg1.to_dict() == gg2.to_dict()

    def test_round_trip_json(self):
        """Test JSON round-trip conversion."""
        # Create document
        gg1 = GenesisGraph(spec_version="0.1.0")
        tool = Tool(id="mytool", type="Software", version="1.0")
        entity = Entity(id="data", type="Dataset", version="1", file="./data.csv")
        gg1.add_tool(tool)
        gg1.add_entity(entity)

        # Convert to JSON and back
        json_str = gg1.to_json()
        gg2 = GenesisGraph.from_json(json_str)

        # Verify they're equivalent
        assert gg1.to_dict() == gg2.to_dict()
