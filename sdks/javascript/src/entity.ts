import { EntityData } from './types';
import * as crypto from 'crypto';
import * as fs from 'fs';

/**
 * Represents an entity (artifact) in a GenesisGraph document
 */
export class Entity {
  id: string;
  type: string;
  version: string;
  file?: string;
  uri?: string;
  hash?: string;
  derived_from: string[];
  metadata: Record<string, any>;

  constructor(data: EntityData) {
    if (!data.file && !data.uri) {
      throw new Error("Entity must have either 'file' or 'uri'");
    }

    this.id = data.id;
    this.type = data.type;
    this.version = data.version;
    this.file = data.file;
    this.uri = data.uri;
    this.hash = data.hash;
    this.derived_from = data.derived_from || [];
    this.metadata = data.metadata || {};
  }

  /**
   * Get the reference string for this entity (id@version)
   */
  reference(): string {
    return `${this.id}@${this.version}`;
  }

  /**
   * Compute and set the hash for this entity's file
   * @param algorithm Hash algorithm (sha256, sha512, blake3)
   * @param filePath Path to file (uses this.file if not provided)
   */
  computeHash(algorithm: 'sha256' | 'sha512' = 'sha256', filePath?: string): this {
    const path = filePath || this.file;
    if (!path) {
      throw new Error('No file path available for hashing');
    }

    const fileBuffer = fs.readFileSync(path);
    const hashSum = crypto.createHash(algorithm);
    hashSum.update(fileBuffer);
    const hex = hashSum.digest('hex');

    this.hash = `${algorithm}:${hex}`;
    return this;
  }

  /**
   * Convert entity to plain object
   */
  toJSON(): EntityData {
    const result: EntityData = {
      id: this.id,
      type: this.type,
      version: this.version,
    };

    if (this.file) result.file = this.file;
    if (this.uri) result.uri = this.uri;
    if (this.hash) result.hash = this.hash;
    if (this.derived_from.length > 0) result.derived_from = this.derived_from;
    if (Object.keys(this.metadata).length > 0) result.metadata = this.metadata;

    return result;
  }
}
