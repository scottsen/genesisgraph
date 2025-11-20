#!/usr/bin/env python3
"""
GenesisGraph Python SDK Quickstart

This example demonstrates how to use the Python SDK to build GenesisGraph documents.
"""

from genesisgraph import GenesisGraph, Entity, Operation, Tool, Attestation


def example_1_minimal_document():
    """Create a minimal valid GenesisGraph document."""
    print("Example 1: Minimal Document")
    print("=" * 50)

    # Create a new document
    gg = GenesisGraph(spec_version="0.1.0")

    # Add a tool
    tool = Tool(id="mytool", type="Software", version="1.0")
    gg.add_tool(tool)

    # Add input entity
    input_entity = Entity(
        id="input_data",
        type="Dataset",
        version="1",
        uri="s3://my-bucket/input.csv",
        hash="sha256:abc123",
    )
    gg.add_entity(input_entity)

    # Add output entity
    output_entity = Entity(
        id="output_data",
        type="Dataset",
        version="1",
        file="./output.json",
        hash="sha256:def456",
        derived_from=[input_entity.reference()],
    )
    gg.add_entity(output_entity)

    # Add operation
    op = Operation(id="op1", type="transform")
    op.add_input(input_entity).add_output(output_entity).set_tool(tool)
    gg.add_operation(op)

    # Output as YAML
    print(gg.to_yaml())
    print()


def example_2_ai_inference():
    """Create an AI inference pipeline document."""
    print("Example 2: AI Inference Pipeline")
    print("=" * 50)

    # Create document with AI profile
    gg = GenesisGraph(spec_version="0.1.0")
    gg.set_profile("gg-ai-basic-v1")
    gg.set_context({
        "environment": "docker://ubuntu:22.04",
        "hardware": "nvidia_a100",
        "location": "datacenter-us-west-2",
    })

    # Add AI model tool
    llama_tool = Tool(
        id="llama3_70b",
        type="AIModel",
        vendor="Meta",
        version="3.0",
        capabilities={
            "inference": {
                "max_tokens": 8192,
                "temperature_range": [0.0, 2.0],
                "top_p_range": [0.0, 1.0],
            }
        },
        identity={"did": "did:model:llama3-70b-instruct"},
    )
    gg.add_tool(llama_tool)

    # Add entities
    retrieval_results = Entity(
        id="retrieval_results",
        type="Dataset",
        version="1",
        file="./retrieval_results.json",
        hash="sha256:f1e2d3c4b5a6",
    )

    prompt_template = Entity(
        id="prompt_template",
        type="TextTemplate",
        version="1.3.0",
        file="./templates/medical_qa_prompt.txt",
        hash="sha256:1234567890ab",
    )

    answer = Entity(
        id="answer",
        type="Text",
        version="1",
        file="./answer.txt",
        hash="sha256:fedcba098765",
        derived_from=[retrieval_results.reference(), prompt_template.reference()],
    )

    gg.add_entity(retrieval_results)
    gg.add_entity(prompt_template)
    gg.add_entity(answer)

    # Add AI inference operation
    attestation = Attestation(
        mode="signed",
        signer="did:model:llama3-70b-instruct",
        signature="ed25519:sig_example_abc123",
    )

    op = (
        Operation(id="op_inference_001", type="ai_inference")
        .add_input(retrieval_results)
        .add_input(prompt_template)
        .add_output(answer)
        .set_tool(llama_tool)
        .set_parameters({
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": 512,
            "system_prompt": "You are a medical information assistant.",
        })
        .set_attestation(attestation)
    )

    op.metrics = {
        "inference_time_ms": 1823,
        "tokens_per_second": 212.4,
    }

    op.resource_usage = {
        "cpu_seconds": 0.8,
        "gpu_ms": 1823,
        "memory_mb": 4096,
        "energy_kj_estimate": 12.4,
    }

    gg.add_operation(op)

    # Save to file
    gg.save_yaml("ai_inference_example.gg.yaml")
    print("Saved to: ai_inference_example.gg.yaml")
    print()


def example_3_manufacturing():
    """Create a manufacturing workflow document."""
    print("Example 3: Manufacturing Workflow")
    print("=" * 50)

    gg = GenesisGraph(spec_version="0.1.0")
    gg.set_profile("gg-cam-v1")

    # Add CAD software tool
    cad_tool = Tool(
        id="fusion360",
        type="Software",
        vendor="Autodesk",
        version="2.0.18157",
        capabilities={
            "tessellation": {
                "max_tolerance_mm": 0.001,
                "formats": ["STL", "OBJ", "3MF"],
            }
        },
    )
    gg.add_tool(cad_tool)

    # Add slicer tool
    slicer_tool = Tool(
        id="prusa_slicer",
        type="Software",
        vendor="Prusa Research",
        version="2.6.1",
    )
    gg.add_tool(slicer_tool)

    # Add entities
    cad_model = Entity(
        id="widget_cad",
        type="CADModel",
        version="3.1",
        file="./models/widget_v3.1.f3d",
        hash="sha256:cad_hash_123",
    )

    mesh = Entity(
        id="widget_mesh",
        type="Mesh3D",
        version="1",
        file="./meshes/widget.stl",
        hash="sha256:mesh_hash_456",
        derived_from=[cad_model.reference()],
    )

    gcode = Entity(
        id="widget_gcode",
        type="GCode",
        version="1",
        file="./gcode/widget.gcode",
        hash="sha256:gcode_hash_789",
        derived_from=[mesh.reference()],
    )

    gg.add_entity(cad_model)
    gg.add_entity(mesh)
    gg.add_entity(gcode)

    # Add tessellation operation
    op1 = (
        Operation(id="op_tessellation_001", type="tessellation")
        .add_input(cad_model)
        .add_output(mesh)
        .set_tool(cad_tool)
        .set_parameters({
            "tolerance_mm": 0.05,
            "output_format": "STL",
            "mesh_quality": "high",
        })
    )
    op1.fidelity = {
        "expected": "geometric_approximation",
        "actual": {
            "tolerance_mm": 0.05,
            "surface_finish_ra": 0.8,
        },
    }
    gg.add_operation(op1)

    # Add slicing operation
    op2 = (
        Operation(id="op_slicing_001", type="slicing")
        .add_input(mesh)
        .add_output(gcode)
        .set_tool(slicer_tool)
        .set_parameters({
            "layer_height_mm": 0.2,
            "infill_percent": 20,
            "print_speed_mm_s": 50,
        })
    )
    gg.add_operation(op2)

    print(gg.to_yaml())
    print()


def example_4_selective_disclosure():
    """Create a document with selective disclosure (redacted parameters)."""
    print("Example 4: Selective Disclosure (Level B)")
    print("=" * 50)

    gg = GenesisGraph(spec_version="0.1.0")
    gg.set_profile("gg-ai-basic-v1")

    tool = Tool(id="proprietary_ai", type="AIModel", version="1.0")
    gg.add_tool(tool)

    input_entity = Entity(
        id="input",
        type="Dataset",
        version="1",
        uri="s3://data/input.csv",
        hash="sha256:input_hash",
    )

    output_entity = Entity(
        id="output",
        type="Dataset",
        version="1",
        file="./output.json",
        hash="sha256:output_hash",
        derived_from=[input_entity.reference()],
    )

    gg.add_entity(input_entity)
    gg.add_entity(output_entity)

    # Create operation with policy claims instead of full parameters
    op = (
        Operation(id="op1", type="ai_inference")
        .add_input(input_entity)
        .add_output(output_entity)
        .set_tool(tool)
    )

    # Redact sensitive parameters
    op.redact_parameters()

    # Add attestation with policy claims
    attestation = Attestation(
        mode="verifiable",
        signer="did:org:acme-corp",
        signature="ed25519:sig_policy_check",
    )
    attestation.claims = {
        "policy": "gg-ai-basic-v1",
        "results": {
            "temperature": {"lte": 0.3, "satisfied": True},
            "content_moderation": {"category": "safe", "result": "pass"},
        },
    }
    op.set_attestation(attestation)

    gg.add_operation(op)

    print(gg.to_yaml())
    print()


def example_5_load_and_modify():
    """Load an existing document and modify it."""
    print("Example 5: Load and Modify Existing Document")
    print("=" * 50)

    # First, create and save a document
    gg1 = GenesisGraph(spec_version="0.1.0")
    tool = Tool(id="tool1", type="Software", version="1.0")
    gg1.add_tool(tool)
    gg1.save_yaml("temp_example.gg.yaml")

    # Load the document
    gg2 = GenesisGraph.load_yaml("temp_example.gg.yaml")

    # Add more content
    new_tool = Tool(id="tool2", type="Software", version="2.0")
    gg2.add_tool(new_tool)

    entity = Entity(
        id="data",
        type="Dataset",
        version="1",
        file="./data.csv",
        hash="sha256:data_hash",
    )
    gg2.add_entity(entity)

    print("Modified document:")
    print(gg2.to_yaml())
    print()


def example_6_validation():
    """Validate a GenesisGraph document."""
    print("Example 6: Document Validation")
    print("=" * 50)

    # Create a valid document
    gg = GenesisGraph(spec_version="0.1.0")
    tool = Tool(id="mytool", type="Software", version="1.0")
    entity = Entity(id="data", type="Dataset", version="1", file="./data.csv")
    op = Operation(id="op1", type="transform")

    gg.add_tool(tool)
    gg.add_entity(entity)
    gg.add_operation(op)

    # Validate
    result = gg.validate(use_schema=True)

    if result.is_valid:
        print("✓ Document is valid!")
    else:
        print("✗ Document has errors:")
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    print()


def main():
    """Run all examples."""
    example_1_minimal_document()
    example_2_ai_inference()
    example_3_manufacturing()
    example_4_selective_disclosure()
    example_5_load_and_modify()
    example_6_validation()


if __name__ == "__main__":
    main()
