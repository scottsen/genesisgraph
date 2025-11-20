/**
 * Type definitions for GenesisGraph
 */

export type ToolType = 'Software' | 'Machine' | 'Human' | 'AIModel' | 'Service';

export type AttestationMode = 'basic' | 'signed' | 'verifiable' | 'zk';

export type FidelityExpected =
  | 'lossless'
  | 'geometric_approximation'
  | 'compression_loss'
  | 'summarization_loss'
  | 'quantization_loss'
  | 'sampling_loss'
  | 'custom';

export type TEETechnology =
  | 'intel_sgx'
  | 'amd_sev_snp'
  | 'amd_sev_es'
  | 'arm_trustzone'
  | 'aws_nitro';

export type WorkProofType = 'vdf_wesolowski' | 'vdf_pietrzak' | 'hashcash' | 'custom';

export type LeafRole = 'sub_input' | 'sub_output' | 'intermediate';

export type PolicyResult = 'pass' | 'fail' | 'unknown';

export interface EntityData {
  id: string;
  type: string;
  version: string;
  file?: string;
  uri?: string;
  hash?: string;
  derived_from?: string[];
  metadata?: Record<string, any>;
}

export interface ToolData {
  id: string;
  type: ToolType;
  vendor?: string;
  version?: string;
  capabilities?: Record<string, any>;
  identity?: {
    did?: string;
    certificate?: string;
  };
  metadata?: Record<string, any>;
}

export interface AttestationClaimsData {
  policy: string;
  results?: Record<string, any>;
}

export interface TransparencyEntryData {
  log_id: string;
  entry_id: string;
  tree_size: number;
  inclusion_proof: string;
  consistency_proof?: string;
}

export interface TEEAttestationData {
  technology: TEETechnology;
  mr_enclave?: string;
  quote: string;
  binds?: {
    inputs_root?: string;
    code_hash?: string;
  };
}

export interface MultisigData {
  threshold: number;
  signers: string[];
}

export interface WorkProofData {
  type: WorkProofType;
  difficulty?: string;
  input: string;
  output: string;
  verifier?: string;
}

export interface AttestationData {
  mode: AttestationMode;
  timestamp: string;
  signer?: string;
  signature?: string;
  delegation?: string;
  claims?: AttestationClaimsData;
  transparency?: TransparencyEntryData[];
  tee?: TEEAttestationData;
  multisig?: MultisigData;
}

export interface FidelityData {
  expected?: FidelityExpected;
  actual?: Record<string, any>;
}

export interface ResourceUsageData {
  cpu_seconds?: number;
  gpu_ms?: number;
  memory_mb?: number;
  energy_kj_estimate?: number;
  custom_metrics?: Record<string, any>;
}

export interface ReproducibilityData {
  expected_output_hash?: string;
  rerun_allowed_until?: string;
  deterministic?: boolean;
  tolerance?: Record<string, any>;
}

export interface SealedSubgraphData {
  merkle_root: string;
  leaves_exposed?: Array<{
    role: LeafRole;
    hash: string;
  }>;
  policy_assertions?: Array<{
    id: string;
    result: PolicyResult;
    signer: string;
    evidence_hash?: string;
  }>;
}

export interface OperationData {
  id: string;
  type: string;
  inputs?: string[];
  outputs?: string[];
  tool?: string;
  parameters?: Record<string, any> | { _redacted: true };
  fidelity?: FidelityData;
  metrics?: Record<string, any>;
  attestation?: AttestationData;
  sealed?: SealedSubgraphData;
  reproducibility?: ReproducibilityData;
  work_proof?: WorkProofData;
  resource_usage?: ResourceUsageData;
  realized_capability?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface ContextData {
  environment?: string;
  hardware?: string;
  location?: string;
  software_env?: string;
  custom?: Record<string, any>;
}

export interface GenesisGraphData {
  spec_version: string;
  profile?: string;
  imports?: string[];
  namespaces?: Record<string, string>;
  context?: ContextData;
  tools?: ToolData[];
  entities?: EntityData[];
  operations?: OperationData[];
  metadata?: Record<string, any>;
}
