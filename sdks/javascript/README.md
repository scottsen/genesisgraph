# GenesisGraph JavaScript/TypeScript SDK

Universal Verifiable Process Provenance SDK for JavaScript and TypeScript.

[![npm version](https://img.shields.io/npm/v/@genesisgraph/sdk.svg)](https://www.npmjs.com/package/@genesisgraph/sdk)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Installation

```bash
npm install @genesisgraph/sdk
```

## Quick Start

```typescript
import { GenesisGraph, Entity, Operation, Tool } from '@genesisgraph/sdk';

// Create a new GenesisGraph document
const gg = new GenesisGraph({ specVersion: '0.1.0' });

// Add a tool
const tool = new Tool({
  id: 'mytool',
  type: 'Software',
  version: '1.0',
});
gg.addTool(tool);

// Add input entity
const input = new Entity({
  id: 'input_data',
  type: 'Dataset',
  version: '1',
  uri: 's3://my-bucket/input.csv',
  hash: 'sha256:abc123',
});
gg.addEntity(input);

// Add output entity
const output = new Entity({
  id: 'output_data',
  type: 'Dataset',
  version: '1',
  file: './output.json',
  derived_from: [input.reference()],
});
gg.addEntity(output);

// Add operation
const op = new Operation({ id: 'op1', type: 'transform' });
op.addInput(input).addOutput(output).setTool(tool);
gg.addOperation(op);

// Export as YAML
console.log(gg.toYAML());

// Save to file
gg.saveYAML('workflow.gg.yaml');
```

## Features

- ✅ **Type-Safe**: Full TypeScript support with complete type definitions
- ✅ **Fluent API**: Chainable methods for easy document construction
- ✅ **YAML & JSON**: Support for both YAML and JSON formats
- ✅ **Hash Computation**: Built-in support for computing file hashes
- ✅ **Validation**: Schema-compliant document generation
- ✅ **Zero Dependencies**: Only requires `js-yaml` for YAML parsing

## API Reference

### GenesisGraph

Main class for building GenesisGraph documents.

```typescript
const gg = new GenesisGraph({
  specVersion: '0.1.0',
  profile: 'gg-ai-basic-v1',
  context: {
    environment: 'docker://ubuntu:22.04',
    hardware: 'nvidia_a100',
  },
});
```

**Methods:**
- `addTool(tool: Tool)` - Add a tool to the document
- `addEntity(entity: Entity)` - Add an entity to the document
- `addOperation(operation: Operation)` - Add an operation to the document
- `setProfile(profile: string)` - Set the profile identifier
- `setContext(context: Record<string, any>)` - Set execution context
- `addNamespace(prefix: string, uri: string)` - Add namespace mapping
- `addImport(uri: string)` - Add namespace import
- `toYAML(options?)` - Convert to YAML string
- `toJSON()` - Convert to plain object
- `saveYAML(path: string)` - Save to YAML file
- `saveJSON(path: string)` - Save to JSON file

**Static Methods:**
- `GenesisGraph.fromYAML(yamlStr: string)` - Parse from YAML string
- `GenesisGraph.fromJSON(data: object)` - Create from plain object
- `GenesisGraph.loadYAML(path: string)` - Load from YAML file
- `GenesisGraph.loadJSON(path: string)` - Load from JSON file

### Entity

Represents an artifact in a GenesisGraph document.

```typescript
const entity = new Entity({
  id: 'medical_corpus',
  type: 'Dataset',
  version: '2025-10-15',
  uri: 's3://medical-kb/corpus.parquet',
  hash: 'sha256:a1b2c3d4...',
  derived_from: ['parent@1.0'],
  metadata: { rows: 1000000 },
});
```

**Methods:**
- `reference()` - Get reference string (`id@version`)
- `computeHash(algorithm: 'sha256' | 'sha512')` - Compute file hash
- `toJSON()` - Convert to plain object

### Tool

Represents a tool/agent in a GenesisGraph document.

```typescript
const tool = new Tool({
  id: 'llama3_70b',
  type: 'AIModel',
  vendor: 'Meta',
  version: '3.0',
  capabilities: {
    max_tokens: 8192,
    temperature_range: [0.0, 2.0],
  },
  identity: {
    did: 'did:model:llama3-70b-instruct',
  },
});
```

**Tool Types:**
- `Software`
- `Machine`
- `Human`
- `AIModel`
- `Service`

**Methods:**
- `reference()` - Get reference string (`id@version`)
- `toJSON()` - Convert to plain object

### Operation

Represents an operation in a GenesisGraph document.

```typescript
const op = new Operation({ id: 'op1', type: 'ai_inference' });
op.addInput(inputEntity)
  .addOutput(outputEntity)
  .setTool(tool)
  .setParameters({ temperature: 0.2, max_tokens: 512 });

op.metrics = { inference_time_ms: 1823 };
op.resource_usage = { gpu_ms: 1823, memory_mb: 4096 };
```

**Methods:**
- `addInput(entity: Entity | string)` - Add input entity
- `addOutput(entity: Entity | string)` - Add output entity
- `setTool(tool: Tool | string)` - Set tool reference
- `setParameters(params: object)` - Set operation parameters
- `setAttestation(attestation: Attestation)` - Set attestation
- `redactParameters()` - Redact parameters for selective disclosure
- `toJSON()` - Convert to plain object

### Attestation

Represents an attestation in a GenesisGraph document.

```typescript
const attestation = new Attestation({
  mode: 'signed',
  signer: 'did:model:llama3-70b-instruct',
  signature: 'ed25519:sig_abc123...',
  timestamp: '2025-10-31T14:23:11Z',
});
```

**Attestation Modes:**
- `basic` - Timestamp only
- `signed` - Digital signature (requires signer + signature)
- `verifiable` - Verifiable credential (requires signer + signature)
- `zk` - Zero-knowledge proof (requires signer + signature)

**Methods:**
- `toJSON()` - Convert to plain object

## Examples

### AI Inference Pipeline

```typescript
import { GenesisGraph, Entity, Operation, Tool, Attestation } from '@genesisgraph/sdk';

const gg = new GenesisGraph({ specVersion: '0.1.0' });
gg.setProfile('gg-ai-basic-v1');

const llama = new Tool({
  id: 'llama3_70b',
  type: 'AIModel',
  vendor: 'Meta',
  version: '3.0',
  capabilities: {
    inference: {
      max_tokens: 8192,
      temperature_range: [0.0, 2.0],
    },
  },
});
gg.addTool(llama);

const input = new Entity({
  id: 'question',
  type: 'Text',
  version: '1',
  file: './question.txt',
});

const output = new Entity({
  id: 'answer',
  type: 'Text',
  version: '1',
  file: './answer.txt',
  derived_from: [input.reference()],
});

gg.addEntity(input).addEntity(output);

const attestation = new Attestation({
  mode: 'signed',
  signer: 'did:model:llama3-70b',
  signature: 'ed25519:sig_...',
  timestamp: new Date().toISOString(),
});

const op = new Operation({ id: 'inference_001', type: 'ai_inference' });
op.addInput(input)
  .addOutput(output)
  .setTool(llama)
  .setParameters({
    temperature: 0.2,
    max_tokens: 512,
  })
  .setAttestation(attestation);

op.metrics = { inference_time_ms: 1823 };
gg.addOperation(op);

gg.saveYAML('ai_inference.gg.yaml');
```

### Manufacturing Workflow

```typescript
const gg = new GenesisGraph({ specVersion: '0.1.0' });
gg.setProfile('gg-cam-v1');

const cadTool = new Tool({
  id: 'fusion360',
  type: 'Software',
  vendor: 'Autodesk',
  version: '2.0.18157',
});

const cad = new Entity({
  id: 'widget_cad',
  type: 'CADModel',
  version: '3.1',
  file: './models/widget.f3d',
});

const mesh = new Entity({
  id: 'widget_mesh',
  type: 'Mesh3D',
  version: '1',
  file: './meshes/widget.stl',
  derived_from: [cad.reference()],
});

gg.addTool(cadTool).addEntity(cad).addEntity(mesh);

const op = new Operation({ id: 'tessellation_001', type: 'tessellation' });
op.addInput(cad)
  .addOutput(mesh)
  .setTool(cadTool)
  .setParameters({
    tolerance_mm: 0.05,
    output_format: 'STL',
  });

op.fidelity = {
  expected: 'geometric_approximation',
  actual: { tolerance_mm: 0.05 },
};

gg.addOperation(op);
gg.saveYAML('manufacturing.gg.yaml');
```

### Selective Disclosure (Level B)

```typescript
const gg = new GenesisGraph({ specVersion: '0.1.0' });

const tool = new Tool({ id: 'proprietary_ai', type: 'AIModel', version: '1.0' });
gg.addTool(tool);

const input = new Entity({
  id: 'input',
  type: 'Dataset',
  version: '1',
  uri: 's3://data/input.csv',
});

const output = new Entity({
  id: 'output',
  type: 'Dataset',
  version: '1',
  file: './output.json',
  derived_from: [input.reference()],
});

gg.addEntity(input).addEntity(output);

const op = new Operation({ id: 'op1', type: 'ai_inference' });
op.addInput(input).addOutput(output).setTool(tool);

// Redact sensitive parameters
op.redactParameters();

// Add policy claims instead
const attestation = new Attestation({
  mode: 'verifiable',
  signer: 'did:org:acme-corp',
  signature: 'ed25519:sig_...',
  timestamp: new Date().toISOString(),
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

gg.saveYAML('selective_disclosure.gg.yaml');
```

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage

# Lint
npm run lint

# Format
npm run format
```

## License

Apache 2.0 - See [LICENSE](../../LICENSE) for details.

## Links

- [GenesisGraph Specification](https://genesisgraph.dev)
- [Python SDK](../../genesisgraph)
- [GitHub Repository](https://github.com/genesisgraph/genesisgraph)
- [Issue Tracker](https://github.com/genesisgraph/genesisgraph/issues)
