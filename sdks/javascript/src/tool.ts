import { ToolData, ToolType } from './types';

/**
 * Represents a tool/agent in a GenesisGraph document
 */
export class Tool {
  id: string;
  type: ToolType;
  vendor?: string;
  version?: string;
  capabilities: Record<string, any>;
  identity: {
    did?: string;
    certificate?: string;
  };
  metadata: Record<string, any>;

  constructor(data: ToolData) {
    const validTypes: ToolType[] = ['Software', 'Machine', 'Human', 'AIModel', 'Service'];
    if (!validTypes.includes(data.type)) {
      throw new Error(`Invalid tool type: ${data.type}`);
    }

    this.id = data.id;
    this.type = data.type;
    this.vendor = data.vendor;
    this.version = data.version;
    this.capabilities = data.capabilities || {};
    this.identity = data.identity || {};
    this.metadata = data.metadata || {};
  }

  /**
   * Get the reference string for this tool (id@version)
   */
  reference(): string {
    if (this.version) {
      return `${this.id}@${this.version}`;
    }
    return `${this.id}@`;
  }

  /**
   * Convert tool to plain object
   */
  toJSON(): ToolData {
    const result: ToolData = {
      id: this.id,
      type: this.type,
    };

    if (this.vendor) result.vendor = this.vendor;
    if (this.version) result.version = this.version;
    if (Object.keys(this.capabilities).length > 0) result.capabilities = this.capabilities;
    if (Object.keys(this.identity).length > 0) result.identity = this.identity;
    if (Object.keys(this.metadata).length > 0) result.metadata = this.metadata;

    return result;
  }
}
