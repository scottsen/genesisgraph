import { OperationData } from './types';
import { Entity } from './entity';
import { Tool } from './tool';
import { Attestation } from './attestation';

/**
 * Represents an operation in a GenesisGraph document
 */
export class Operation {
  id: string;
  type: string;
  inputs: string[];
  outputs: string[];
  tool?: string;
  parameters: Record<string, any> | { _redacted: true };
  fidelity?: any;
  metrics: Record<string, any>;
  attestation?: Attestation;
  sealed?: any;
  reproducibility?: any;
  work_proof?: any;
  resource_usage?: any;
  realized_capability?: any;
  metadata: Record<string, any>;

  constructor(data: OperationData) {
    this.id = data.id;
    this.type = data.type;
    this.inputs = data.inputs || [];
    this.outputs = data.outputs || [];
    this.tool = data.tool;
    this.parameters = data.parameters || {};
    this.fidelity = data.fidelity;
    this.metrics = data.metrics || {};
    this.attestation = data.attestation ? new Attestation(data.attestation) : undefined;
    this.sealed = data.sealed;
    this.reproducibility = data.reproducibility;
    this.work_proof = data.work_proof;
    this.resource_usage = data.resource_usage;
    this.realized_capability = data.realized_capability;
    this.metadata = data.metadata || {};
  }

  /**
   * Add an input entity
   */
  addInput(entity: string | Entity): this {
    const ref = typeof entity === 'string' ? entity : entity.reference();
    this.inputs.push(ref);
    return this;
  }

  /**
   * Add an output entity
   */
  addOutput(entity: string | Entity): this {
    const ref = typeof entity === 'string' ? entity : entity.reference();
    this.outputs.push(ref);
    return this;
  }

  /**
   * Set the tool for this operation
   */
  setTool(tool: string | Tool): this {
    this.tool = typeof tool === 'string' ? tool : tool.reference();
    return this;
  }

  /**
   * Set operation parameters
   */
  setParameters(parameters: Record<string, any>): this {
    this.parameters = parameters;
    return this;
  }

  /**
   * Set operation attestation
   */
  setAttestation(attestation: Attestation): this {
    this.attestation = attestation;
    return this;
  }

  /**
   * Redact parameters for selective disclosure
   */
  redactParameters(): this {
    this.parameters = { _redacted: true };
    return this;
  }

  /**
   * Convert operation to plain object
   */
  toJSON(): OperationData {
    const result: OperationData = {
      id: this.id,
      type: this.type,
    };

    if (this.inputs.length > 0) result.inputs = this.inputs;
    if (this.outputs.length > 0) result.outputs = this.outputs;
    if (this.tool) result.tool = this.tool;
    if (this.parameters) result.parameters = this.parameters;
    if (this.fidelity) result.fidelity = this.fidelity;
    if (Object.keys(this.metrics).length > 0) result.metrics = this.metrics;
    if (this.attestation) result.attestation = this.attestation.toJSON();
    if (this.sealed) result.sealed = this.sealed;
    if (this.reproducibility) result.reproducibility = this.reproducibility;
    if (this.work_proof) result.work_proof = this.work_proof;
    if (this.resource_usage) result.resource_usage = this.resource_usage;
    if (this.realized_capability) result.realized_capability = this.realized_capability;
    if (Object.keys(this.metadata).length > 0) result.metadata = this.metadata;

    return result;
  }
}
