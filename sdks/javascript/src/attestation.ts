import { AttestationData, AttestationMode } from './types';

/**
 * Represents an attestation in a GenesisGraph document
 */
export class Attestation {
  mode: AttestationMode;
  timestamp: string;
  signer?: string;
  signature?: string;
  delegation?: string;
  claims?: any;
  transparency?: any[];
  tee?: any;
  multisig?: any;

  constructor(data: AttestationData) {
    const validModes: AttestationMode[] = ['basic', 'signed', 'verifiable', 'zk'];
    if (!validModes.includes(data.mode)) {
      throw new Error(`Invalid attestation mode: ${data.mode}`);
    }

    if (['signed', 'verifiable', 'zk'].includes(data.mode)) {
      if (!data.signer || !data.signature) {
        throw new Error(`Mode '${data.mode}' requires both signer and signature`);
      }
    }

    this.mode = data.mode;
    this.timestamp = data.timestamp || new Date().toISOString();
    this.signer = data.signer;
    this.signature = data.signature;
    this.delegation = data.delegation;
    this.claims = data.claims;
    this.transparency = data.transparency;
    this.tee = data.tee;
    this.multisig = data.multisig;
  }

  /**
   * Convert attestation to plain object
   */
  toJSON(): AttestationData {
    const result: AttestationData = {
      mode: this.mode,
      timestamp: this.timestamp,
    };

    if (this.signer) result.signer = this.signer;
    if (this.signature) result.signature = this.signature;
    if (this.delegation) result.delegation = this.delegation;
    if (this.claims) result.claims = this.claims;
    if (this.transparency) result.transparency = this.transparency;
    if (this.tee) result.tee = this.tee;
    if (this.multisig) result.multisig = this.multisig;

    return result;
  }
}
