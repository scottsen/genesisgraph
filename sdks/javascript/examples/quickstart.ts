#!/usr/bin/env ts-node
/**
 * GenesisGraph JavaScript SDK Quickstart
 *
 * This example demonstrates how to use the JavaScript SDK to build GenesisGraph documents.
 */

import { GenesisGraph, Entity, Operation, Tool, Attestation } from '../src';

function example1MinimalDocument() {
  console.log('Example 1: Minimal Document');
  console.log('='.repeat(50));

  // Create a new document
  const gg = new GenesisGraph({ specVersion: '0.1.0' });

  // Add a tool
  const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
  gg.addTool(tool);

  // Add input entity
  const inputEntity = new Entity({
    id: 'input_data',
    type: 'Dataset',
    version: '1',
    uri: 's3://my-bucket/input.csv',
    hash: 'sha256:abc123',
  });
  gg.addEntity(inputEntity);

  // Add output entity
  const outputEntity = new Entity({
    id: 'output_data',
    type: 'Dataset',
    version: '1',
    file: './output.json',
    hash: 'sha256:def456',
    derived_from: [inputEntity.reference()],
  });
  gg.addEntity(outputEntity);

  // Add operation
  const op = new Operation({ id: 'op1', type: 'transform' });
  op.addInput(inputEntity).addOutput(outputEntity).setTool(tool);
  gg.addOperation(op);

  // Output as YAML
  console.log(gg.toYAML());
  console.log();
}

function example2AIInference() {
  console.log('Example 2: AI Inference Pipeline');
  console.log('='.repeat(50));

  // Create document with AI profile
  const gg = new GenesisGraph({ specVersion: '0.1.0' });
  gg.setProfile('gg-ai-basic-v1');
  gg.setContext({
    environment: 'docker://ubuntu:22.04',
    hardware: 'nvidia_a100',
    location: 'datacenter-us-west-2',
  });

  // Add AI model tool
  const llamaTool = new Tool({
    id: 'llama3_70b',
    type: 'AIModel',
    vendor: 'Meta',
    version: '3.0',
    capabilities: {
      inference: {
        max_tokens: 8192,
        temperature_range: [0.0, 2.0],
        top_p_range: [0.0, 1.0],
      },
    },
    identity: { did: 'did:model:llama3-70b-instruct' },
  });
  gg.addTool(llamaTool);

  // Add entities
  const retrievalResults = new Entity({
    id: 'retrieval_results',
    type: 'Dataset',
    version: '1',
    file: './retrieval_results.json',
    hash: 'sha256:f1e2d3c4b5a6',
  });

  const promptTemplate = new Entity({
    id: 'prompt_template',
    type: 'TextTemplate',
    version: '1.3.0',
    file: './templates/medical_qa_prompt.txt',
    hash: 'sha256:1234567890ab',
  });

  const answer = new Entity({
    id: 'answer',
    type: 'Text',
    version: '1',
    file: './answer.txt',
    hash: 'sha256:fedcba098765',
    derived_from: [retrievalResults.reference(), promptTemplate.reference()],
  });

  gg.addEntity(retrievalResults);
  gg.addEntity(promptTemplate);
  gg.addEntity(answer);

  // Add AI inference operation
  const attestation = new Attestation({
    mode: 'signed',
    signer: 'did:model:llama3-70b-instruct',
    signature: 'ed25519:sig_example_abc123',
    timestamp: '2025-10-31T14:23:13Z',
  });

  const op = new Operation({ id: 'op_inference_001', type: 'ai_inference' });
  op.addInput(retrievalResults);
  op.addInput(promptTemplate);
  op.addOutput(answer);
  op.setTool(llamaTool);
  op.setParameters({
    temperature: 0.2,
    top_p: 0.9,
    max_tokens: 512,
    system_prompt: 'You are a medical information assistant.',
  });
  op.setAttestation(attestation);

  op.metrics = {
    inference_time_ms: 1823,
    tokens_per_second: 212.4,
  };

  op.resource_usage = {
    cpu_seconds: 0.8,
    gpu_ms: 1823,
    memory_mb: 4096,
    energy_kj_estimate: 12.4,
  };

  gg.addOperation(op);

  // Save to file
  gg.saveYAML('ai_inference_example.gg.yaml');
  console.log('Saved to: ai_inference_example.gg.yaml');
  console.log();
}

function example3Manufacturing() {
  console.log('Example 3: Manufacturing Workflow');
  console.log('='.repeat(50));

  const gg = new GenesisGraph({ specVersion: '0.1.0' });
  gg.setProfile('gg-cam-v1');

  // Add CAD software tool
  const cadTool = new Tool({
    id: 'fusion360',
    type: 'Software',
    vendor: 'Autodesk',
    version: '2.0.18157',
    capabilities: {
      tessellation: {
        max_tolerance_mm: 0.001,
        formats: ['STL', 'OBJ', '3MF'],
      },
    },
  });
  gg.addTool(cadTool);

  // Add slicer tool
  const slicerTool = new Tool({
    id: 'prusa_slicer',
    type: 'Software',
    vendor: 'Prusa Research',
    version: '2.6.1',
  });
  gg.addTool(slicerTool);

  // Add entities
  const cadModel = new Entity({
    id: 'widget_cad',
    type: 'CADModel',
    version: '3.1',
    file: './models/widget_v3.1.f3d',
    hash: 'sha256:cad_hash_123',
  });

  const mesh = new Entity({
    id: 'widget_mesh',
    type: 'Mesh3D',
    version: '1',
    file: './meshes/widget.stl',
    hash: 'sha256:mesh_hash_456',
    derived_from: [cadModel.reference()],
  });

  const gcode = new Entity({
    id: 'widget_gcode',
    type: 'GCode',
    version: '1',
    file: './gcode/widget.gcode',
    hash: 'sha256:gcode_hash_789',
    derived_from: [mesh.reference()],
  });

  gg.addEntity(cadModel);
  gg.addEntity(mesh);
  gg.addEntity(gcode);

  // Add tessellation operation
  const op1 = new Operation({ id: 'op_tessellation_001', type: 'tessellation' });
  op1.addInput(cadModel);
  op1.addOutput(mesh);
  op1.setTool(cadTool);
  op1.setParameters({
    tolerance_mm: 0.05,
    output_format: 'STL',
    mesh_quality: 'high',
  });
  op1.fidelity = {
    expected: 'geometric_approximation',
    actual: {
      tolerance_mm: 0.05,
      surface_finish_ra: 0.8,
    },
  };
  gg.addOperation(op1);

  // Add slicing operation
  const op2 = new Operation({ id: 'op_slicing_001', type: 'slicing' });
  op2.addInput(mesh);
  op2.addOutput(gcode);
  op2.setTool(slicerTool);
  op2.setParameters({
    layer_height_mm: 0.2,
    infill_percent: 20,
    print_speed_mm_s: 50,
  });
  gg.addOperation(op2);

  console.log(gg.toYAML());
  console.log();
}

function example4SelectiveDisclosure() {
  console.log('Example 4: Selective Disclosure (Level B)');
  console.log('='.repeat(50));

  const gg = new GenesisGraph({ specVersion: '0.1.0' });
  gg.setProfile('gg-ai-basic-v1');

  const tool = new Tool({ id: 'proprietary_ai', type: 'AIModel', version: '1.0' });
  gg.addTool(tool);

  const inputEntity = new Entity({
    id: 'input',
    type: 'Dataset',
    version: '1',
    uri: 's3://data/input.csv',
    hash: 'sha256:input_hash',
  });

  const outputEntity = new Entity({
    id: 'output',
    type: 'Dataset',
    version: '1',
    file: './output.json',
    hash: 'sha256:output_hash',
    derived_from: [inputEntity.reference()],
  });

  gg.addEntity(inputEntity);
  gg.addEntity(outputEntity);

  // Create operation with policy claims instead of full parameters
  const op = new Operation({ id: 'op1', type: 'ai_inference' });
  op.addInput(inputEntity);
  op.addOutput(outputEntity);
  op.setTool(tool);

  // Redact sensitive parameters
  op.redactParameters();

  // Add attestation with policy claims
  const attestation = new Attestation({
    mode: 'verifiable',
    signer: 'did:org:acme-corp',
    signature: 'ed25519:sig_policy_check',
    timestamp: '2025-10-31T14:23:11Z',
  });

  attestation.claims = {
    policy: 'gg-ai-basic-v1',
    results: {
      temperature: { lte: 0.3, satisfied: true },
      content_moderation: { category: 'safe', result: 'pass' },
    },
  };

  op.setAttestation(attestation);
  gg.addOperation(op);

  console.log(gg.toYAML());
  console.log();
}

function example5LoadAndModify() {
  console.log('Example 5: Load and Modify Existing Document');
  console.log('='.repeat(50));

  // First, create and save a document
  const gg1 = new GenesisGraph({ specVersion: '0.1.0' });
  const tool = new Tool({ id: 'tool1', type: 'Software', version: '1.0' });
  gg1.addTool(tool);
  gg1.saveYAML('temp_example.gg.yaml');

  // Load the document
  const gg2 = GenesisGraph.loadYAML('temp_example.gg.yaml');

  // Add more content
  const newTool = new Tool({ id: 'tool2', type: 'Software', version: '2.0' });
  gg2.addTool(newTool);

  const entity = new Entity({
    id: 'data',
    type: 'Dataset',
    version: '1',
    file: './data.csv',
    hash: 'sha256:data_hash',
  });
  gg2.addEntity(entity);

  console.log('Modified document:');
  console.log(gg2.toYAML());
  console.log();
}

function main() {
  example1MinimalDocument();
  example2AIInference();
  example3Manufacturing();
  example4SelectiveDisclosure();
  example5LoadAndModify();
}

main();
