import { GenesisGraph } from './genesisgraph';
import { Entity } from './entity';
import { Tool } from './tool';
import { Operation } from './operation';
import { Attestation } from './attestation';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

describe('GenesisGraph', () => {
  describe('constructor', () => {
    it('should create minimal document', () => {
      const gg = new GenesisGraph({ specVersion: '0.1.0' });
      expect(gg.spec_version).toBe('0.1.0');
    });

    it('should use default spec version', () => {
      const gg = new GenesisGraph();
      expect(gg.spec_version).toBe('0.1.0');
    });

    it('should accept profile', () => {
      const gg = new GenesisGraph({
        specVersion: '0.1.0',
        profile: 'gg-ai-basic-v1',
      });
      expect(gg.profile).toBe('gg-ai-basic-v1');
    });
  });

  describe('addTool', () => {
    it('should add a tool', () => {
      const gg = new GenesisGraph();
      const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
      gg.addTool(tool);

      expect(gg.tools).toHaveLength(1);
      expect(gg.tools[0].id).toBe('mytool');
    });
  });

  describe('addEntity', () => {
    it('should add an entity', () => {
      const gg = new GenesisGraph();
      const entity = new Entity({
        id: 'data',
        type: 'Dataset',
        version: '1',
        file: './data.csv',
      });
      gg.addEntity(entity);

      expect(gg.entities).toHaveLength(1);
      expect(gg.entities[0].id).toBe('data');
    });
  });

  describe('addOperation', () => {
    it('should add an operation', () => {
      const gg = new GenesisGraph();
      const op = new Operation({ id: 'op1', type: 'transform' });
      gg.addOperation(op);

      expect(gg.operations).toHaveLength(1);
      expect(gg.operations[0].id).toBe('op1');
    });
  });

  describe('method chaining', () => {
    it('should support fluent API', () => {
      const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
      const entity = new Entity({
        id: 'data',
        type: 'Dataset',
        version: '1',
        file: './data.csv',
      });
      const op = new Operation({ id: 'op1', type: 'transform' });

      const gg = new GenesisGraph({ specVersion: '0.1.0' })
        .setProfile('gg-ai-basic-v1')
        .addTool(tool)
        .addEntity(entity)
        .addOperation(op);

      expect(gg.profile).toBe('gg-ai-basic-v1');
      expect(gg.tools).toHaveLength(1);
      expect(gg.entities).toHaveLength(1);
      expect(gg.operations).toHaveLength(1);
    });
  });

  describe('setContext', () => {
    it('should set execution context', () => {
      const gg = new GenesisGraph();
      gg.setContext({
        environment: 'docker://ubuntu:22.04',
        hardware: 'nvidia_a100',
      });

      expect(gg.context.environment).toBe('docker://ubuntu:22.04');
      expect(gg.context.hardware).toBe('nvidia_a100');
    });
  });

  describe('addNamespace', () => {
    it('should add namespace mapping', () => {
      const gg = new GenesisGraph();
      gg.addNamespace('ai', 'https://genesisgraph.dev/ns/ai/0.1');

      expect(gg.namespaces.ai).toBe('https://genesisgraph.dev/ns/ai/0.1');
    });
  });

  describe('addImport', () => {
    it('should add namespace import', () => {
      const gg = new GenesisGraph();
      gg.addImport('https://genesisgraph.dev/ns/core/0.1');

      expect(gg.imports).toContain('https://genesisgraph.dev/ns/core/0.1');
    });
  });

  describe('toJSON', () => {
    it('should serialize to plain object', () => {
      const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
      const entity = new Entity({
        id: 'data',
        type: 'Dataset',
        version: '1',
        file: './data.csv',
      });
      const op = new Operation({ id: 'op1', type: 'transform' });

      const gg = new GenesisGraph({ specVersion: '0.1.0' });
      gg.addTool(tool);
      gg.addEntity(entity);
      gg.addOperation(op);

      const json = gg.toJSON();

      expect(json.spec_version).toBe('0.1.0');
      expect(json.tools).toHaveLength(1);
      expect(json.entities).toHaveLength(1);
      expect(json.operations).toHaveLength(1);
    });
  });

  describe('toYAML', () => {
    it('should serialize to YAML', () => {
      const gg = new GenesisGraph({ specVersion: '0.1.0' });
      const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
      gg.addTool(tool);

      const yaml = gg.toYAML();

      expect(yaml).toContain('spec_version: 0.1.0');
      expect(yaml).toContain('mytool');
    });
  });

  describe('save and load', () => {
    const tempDir = os.tmpdir();

    it('should save and load YAML', () => {
      const yamlPath = path.join(tempDir, 'test-gg.yaml');

      const gg1 = new GenesisGraph({ specVersion: '0.1.0' });
      const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
      gg1.addTool(tool);
      gg1.saveYAML(yamlPath);

      const gg2 = GenesisGraph.loadYAML(yamlPath);

      expect(gg2.spec_version).toBe('0.1.0');
      expect(gg2.tools).toHaveLength(1);
      expect(gg2.tools[0].id).toBe('mytool');

      fs.unlinkSync(yamlPath);
    });

    it('should save and load JSON', () => {
      const jsonPath = path.join(tempDir, 'test-gg.json');

      const gg1 = new GenesisGraph({ specVersion: '0.1.0' });
      const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
      gg1.addTool(tool);
      gg1.saveJSON(jsonPath);

      const gg2 = GenesisGraph.loadJSON(jsonPath);

      expect(gg2.spec_version).toBe('0.1.0');
      expect(gg2.tools).toHaveLength(1);
      expect(gg2.tools[0].id).toBe('mytool');

      fs.unlinkSync(jsonPath);
    });
  });

  describe('fromYAML', () => {
    it('should parse YAML string', () => {
      const yamlStr = `
spec_version: 0.1.0
tools:
  - id: mytool
    type: Software
    version: "1.0"
entities:
  - id: data
    type: Dataset
    version: "1"
    file: ./data.csv
operations:
  - id: op1
    type: transform
`;

      const gg = GenesisGraph.fromYAML(yamlStr);

      expect(gg.spec_version).toBe('0.1.0');
      expect(gg.tools).toHaveLength(1);
      expect(gg.entities).toHaveLength(1);
      expect(gg.operations).toHaveLength(1);
    });
  });

  describe('complete workflow', () => {
    it('should build a complete AI inference document', () => {
      const gg = new GenesisGraph({ specVersion: '0.1.0' });
      gg.setProfile('gg-ai-basic-v1');
      gg.setContext({
        environment: 'docker://ubuntu:22.04',
        hardware: 'nvidia_a100',
      });

      const tool = new Tool({
        id: 'llama3',
        type: 'AIModel',
        vendor: 'Meta',
        version: '3.0',
        capabilities: { max_tokens: 8192 },
      });
      gg.addTool(tool);

      const inputData = new Entity({
        id: 'medical_corpus',
        type: 'Dataset',
        version: '2025-10-15',
        uri: 's3://medical-kb/corpus.parquet',
        hash: 'sha256:abc123',
      });

      const outputData = new Entity({
        id: 'answer',
        type: 'Text',
        version: '1',
        file: './answer.txt',
        hash: 'sha256:def456',
        derived_from: [inputData.reference()],
      });

      gg.addEntity(inputData);
      gg.addEntity(outputData);

      const attestation = new Attestation({
        mode: 'signed',
        signer: 'did:model:llama3',
        signature: 'ed25519:sig123',
        timestamp: '2025-10-31T14:23:11Z',
      });

      const op = new Operation({ id: 'op1', type: 'ai_inference' });
      op.addInput(inputData);
      op.addOutput(outputData);
      op.setTool(tool);
      op.setParameters({ temperature: 0.2, max_tokens: 512 });
      op.setAttestation(attestation);
      gg.addOperation(op);

      const json = gg.toJSON();

      expect(json.spec_version).toBe('0.1.0');
      expect(json.profile).toBe('gg-ai-basic-v1');
      expect(json.tools).toHaveLength(1);
      expect(json.entities).toHaveLength(2);
      expect(json.operations).toHaveLength(1);
      expect(json.operations![0].attestation?.mode).toBe('signed');
    });
  });

  describe('round trip', () => {
    it('should support YAML round trip', () => {
      const gg1 = new GenesisGraph({ specVersion: '0.1.0' });
      const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
      const entity = new Entity({
        id: 'data',
        type: 'Dataset',
        version: '1',
        file: './data.csv',
      });
      gg1.addTool(tool);
      gg1.addEntity(entity);

      const yaml = gg1.toYAML();
      const gg2 = GenesisGraph.fromYAML(yaml);

      expect(gg1.toJSON()).toEqual(gg2.toJSON());
    });
  });
});
