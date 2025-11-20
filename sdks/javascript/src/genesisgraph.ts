import { GenesisGraphData } from './types';
import { Entity } from './entity';
import { Tool } from './tool';
import { Operation } from './operation';
import * as yaml from 'js-yaml';
import * as fs from 'fs';

/**
 * Main builder class for constructing GenesisGraph documents
 *
 * @example
 * ```typescript
 * const gg = new GenesisGraph({ specVersion: '0.1.0' });
 * const tool = new Tool({ id: 'mytool', type: 'Software', version: '1.0' });
 * gg.addTool(tool);
 *
 * const entity = new Entity({
 *   id: 'data',
 *   type: 'Dataset',
 *   version: '1',
 *   uri: 's3://bucket/data',
 * });
 * gg.addEntity(entity);
 *
 * const yaml = gg.toYAML();
 * ```
 */
export class GenesisGraph {
  spec_version: string;
  profile?: string;
  imports: string[];
  namespaces: Record<string, string>;
  context: Record<string, any>;
  metadata: Record<string, any>;
  tools: Tool[];
  entities: Entity[];
  operations: Operation[];

  constructor(options: {
    specVersion?: string;
    profile?: string;
    imports?: string[];
    namespaces?: Record<string, string>;
    context?: Record<string, any>;
    metadata?: Record<string, any>;
  } = {}) {
    this.spec_version = options.specVersion || '0.1.0';
    this.profile = options.profile;
    this.imports = options.imports || [];
    this.namespaces = options.namespaces || {};
    this.context = options.context || {};
    this.metadata = options.metadata || {};
    this.tools = [];
    this.entities = [];
    this.operations = [];
  }

  /**
   * Add a tool to the document
   */
  addTool(tool: Tool): this {
    this.tools.push(tool);
    return this;
  }

  /**
   * Add an entity to the document
   */
  addEntity(entity: Entity): this {
    this.entities.push(entity);
    return this;
  }

  /**
   * Add an operation to the document
   */
  addOperation(operation: Operation): this {
    this.operations.push(operation);
    return this;
  }

  /**
   * Set the profile identifier
   */
  setProfile(profile: string): this {
    this.profile = profile;
    return this;
  }

  /**
   * Set the execution context
   */
  setContext(context: Record<string, any>): this {
    this.context = context;
    return this;
  }

  /**
   * Add a namespace mapping
   */
  addNamespace(prefix: string, uri: string): this {
    this.namespaces[prefix] = uri;
    return this;
  }

  /**
   * Add a namespace import
   */
  addImport(uri: string): this {
    this.imports.push(uri);
    return this;
  }

  /**
   * Convert the document to a plain object
   */
  toJSON(): GenesisGraphData {
    const result: GenesisGraphData = {
      spec_version: this.spec_version,
    };

    if (this.profile) result.profile = this.profile;
    if (this.imports.length > 0) result.imports = this.imports;
    if (Object.keys(this.namespaces).length > 0) result.namespaces = this.namespaces;
    if (Object.keys(this.context).length > 0) result.context = this.context;
    if (this.tools.length > 0) result.tools = this.tools.map((t) => t.toJSON());
    if (this.entities.length > 0) result.entities = this.entities.map((e) => e.toJSON());
    if (this.operations.length > 0) result.operations = this.operations.map((o) => o.toJSON());
    if (Object.keys(this.metadata).length > 0) result.metadata = this.metadata;

    return result;
  }

  /**
   * Convert the document to YAML format
   */
  toYAML(options?: yaml.DumpOptions): string {
    const defaultOptions: yaml.DumpOptions = {
      sortKeys: false,
      lineWidth: -1,
      ...options,
    };
    return yaml.dump(this.toJSON(), defaultOptions);
  }

  /**
   * Convert to canonical JSON format for signing
   */
  toCanonicalJSON(): string {
    return JSON.stringify(this.toJSON(), Object.keys(this.toJSON()).sort(), 0);
  }

  /**
   * Save the document to a YAML file
   */
  saveYAML(path: string, options?: yaml.DumpOptions): void {
    fs.writeFileSync(path, this.toYAML(options), 'utf8');
  }

  /**
   * Save the document to a JSON file
   */
  saveJSON(path: string, space: number = 2): void {
    fs.writeFileSync(path, JSON.stringify(this.toJSON(), null, space), 'utf8');
  }

  /**
   * Create a GenesisGraph document from a plain object
   */
  static fromJSON(data: GenesisGraphData): GenesisGraph {
    const gg = new GenesisGraph({
      specVersion: data.spec_version,
      profile: data.profile,
      imports: data.imports,
      namespaces: data.namespaces,
      context: data.context,
      metadata: data.metadata,
    });

    // Add tools
    if (data.tools) {
      for (const toolData of data.tools) {
        gg.addTool(new Tool(toolData));
      }
    }

    // Add entities
    if (data.entities) {
      for (const entityData of data.entities) {
        gg.addEntity(new Entity(entityData));
      }
    }

    // Add operations
    if (data.operations) {
      for (const opData of data.operations) {
        gg.addOperation(new Operation(opData));
      }
    }

    return gg;
  }

  /**
   * Create a GenesisGraph document from a YAML string
   */
  static fromYAML(yamlStr: string): GenesisGraph {
    const data = yaml.load(yamlStr) as GenesisGraphData;
    return GenesisGraph.fromJSON(data);
  }

  /**
   * Load a GenesisGraph document from a YAML file
   */
  static loadYAML(path: string): GenesisGraph {
    const content = fs.readFileSync(path, 'utf8');
    return GenesisGraph.fromYAML(content);
  }

  /**
   * Load a GenesisGraph document from a JSON file
   */
  static loadJSON(path: string): GenesisGraph {
    const content = fs.readFileSync(path, 'utf8');
    const data = JSON.parse(content) as GenesisGraphData;
    return GenesisGraph.fromJSON(data);
  }
}
