import { Entity } from './entity';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

describe('Entity', () => {
  describe('constructor', () => {
    it('should create an entity with file', () => {
      const entity = new Entity({
        id: 'test_data',
        type: 'Dataset',
        version: '1.0',
        file: './data.csv',
        hash: 'sha256:abc123',
      });

      expect(entity.id).toBe('test_data');
      expect(entity.type).toBe('Dataset');
      expect(entity.version).toBe('1.0');
      expect(entity.file).toBe('./data.csv');
      expect(entity.hash).toBe('sha256:abc123');
    });

    it('should create an entity with uri', () => {
      const entity = new Entity({
        id: 'remote_data',
        type: 'Dataset',
        version: '2.0',
        uri: 's3://bucket/data.parquet',
        hash: 'sha256:def456',
      });

      expect(entity.uri).toBe('s3://bucket/data.parquet');
      expect(entity.file).toBeUndefined();
    });

    it('should throw error if neither file nor uri is provided', () => {
      expect(() => {
        new Entity({
          id: 'test',
          type: 'Dataset',
          version: '1',
        });
      }).toThrow("must have either 'file' or 'uri'");
    });

    it('should handle derived_from', () => {
      const entity = new Entity({
        id: 'child',
        type: 'Dataset',
        version: '1',
        file: './child.csv',
        derived_from: ['parent1@1', 'parent2@2'],
      });

      expect(entity.derived_from).toEqual(['parent1@1', 'parent2@2']);
    });

    it('should handle metadata', () => {
      const entity = new Entity({
        id: 'data',
        type: 'Dataset',
        version: '1',
        file: './data.csv',
        metadata: { rows: 1000, columns: 50 },
      });

      expect(entity.metadata).toEqual({ rows: 1000, columns: 50 });
    });
  });

  describe('reference', () => {
    it('should return correct reference string', () => {
      const entity = new Entity({
        id: 'data',
        type: 'Dataset',
        version: '1.5',
        file: './data.csv',
      });

      expect(entity.reference()).toBe('data@1.5');
    });
  });

  describe('computeHash', () => {
    it('should compute sha256 hash', () => {
      const tempFile = path.join(os.tmpdir(), 'test-entity.txt');
      fs.writeFileSync(tempFile, 'test content', 'utf8');

      try {
        const entity = new Entity({
          id: 'data',
          type: 'Text',
          version: '1',
          file: tempFile,
        });

        entity.computeHash('sha256');

        expect(entity.hash).toBeDefined();
        expect(entity.hash).toMatch(/^sha256:[a-f0-9]+$/);
      } finally {
        fs.unlinkSync(tempFile);
      }
    });

    it('should throw error if no file path available', () => {
      const entity = new Entity({
        id: 'data',
        type: 'Text',
        version: '1',
        uri: 's3://bucket/data',
      });

      expect(() => {
        entity.computeHash();
      }).toThrow('No file path available');
    });
  });

  describe('toJSON', () => {
    it('should serialize entity correctly', () => {
      const entity = new Entity({
        id: 'data',
        type: 'Dataset',
        version: '1',
        file: './data.csv',
        hash: 'sha256:abc123',
        derived_from: ['parent@1'],
        metadata: { key: 'value' },
      });

      const json = entity.toJSON();

      expect(json).toEqual({
        id: 'data',
        type: 'Dataset',
        version: '1',
        file: './data.csv',
        hash: 'sha256:abc123',
        derived_from: ['parent@1'],
        metadata: { key: 'value' },
      });
    });

    it('should not include empty arrays or objects', () => {
      const entity = new Entity({
        id: 'data',
        type: 'Dataset',
        version: '1',
        file: './data.csv',
      });

      const json = entity.toJSON();

      expect(json.derived_from).toBeUndefined();
      expect(json.metadata).toBeUndefined();
    });
  });
});
