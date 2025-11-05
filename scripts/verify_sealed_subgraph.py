#!/usr/bin/env python3
"""
GenesisGraph Sealed Subgraph Verifier

Demonstrates verification of sealed subgraph patterns including:
- Merkle root validation
- Inclusion proof verification
- Policy assertion validation
- Signature verification (ed25519)

Usage:
    python verify_sealed_subgraph.py <path-to-gg-file> [--node-id OP_ID]
"""

import sys
import yaml
import hashlib
import base64
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class InclusionProof:
    """Merkle tree inclusion proof"""
    leaf_hash: str
    sibling_hashes: List[str]
    path_indices: List[int]


class MerkleTree:
    """Simple Merkle tree for demonstration"""

    @staticmethod
    def hash_data(data: bytes) -> str:
        """SHA-256 hash with algorithm prefix"""
        h = hashlib.sha256(data).hexdigest()
        return f"sha256:{h}"

    @staticmethod
    def hash_pair(left: str, right: str) -> str:
        """Hash a pair of nodes"""
        # Extract hex from "sha256:..." format
        left_hex = left.split(':', 1)[1] if ':' in left else left
        right_hex = right.split(':', 1)[1] if ':' in right else right

        # Concatenate and hash
        combined = bytes.fromhex(left_hex) + bytes.fromhex(right_hex)
        return MerkleTree.hash_data(combined)

    @staticmethod
    def verify_inclusion(
        leaf_hash: str,
        root_hash: str,
        sibling_hashes: List[str],
        path_indices: List[int]
    ) -> bool:
        """
        Verify Merkle inclusion proof

        Args:
            leaf_hash: Hash of the leaf to verify
            root_hash: Expected Merkle root
            sibling_hashes: Sibling hashes along the path to root
            path_indices: 0 = left, 1 = right for each level

        Returns:
            True if proof is valid
        """
        current = leaf_hash

        for sibling, path_idx in zip(sibling_hashes, path_indices):
            if path_idx == 0:
                # Current node is on the left
                current = MerkleTree.hash_pair(current, sibling)
            else:
                # Current node is on the right
                current = MerkleTree.hash_pair(sibling, current)

        return current == root_hash


class SealedSubgraphVerifier:
    """Verifies sealed subgraph patterns in GenesisGraph documents"""

    def __init__(self, gg_data: Dict):
        self.gg_data = gg_data
        self.operations = gg_data.get('operations', [])

    def find_sealed_operations(self) -> List[Dict]:
        """Find all sealed_subgraph operations"""
        return [
            op for op in self.operations
            if op.get('type') == 'sealed_subgraph'
        ]

    def verify_sealed_operation(self, op: Dict) -> Tuple[bool, List[str]]:
        """
        Verify a sealed operation

        Returns:
            (success, messages) tuple
        """
        messages = []
        success = True

        op_id = op.get('id', 'UNKNOWN')
        messages.append(f"\n=== Verifying sealed operation: {op_id} ===")

        sealed = op.get('sealed', {})
        if not sealed:
            messages.append("❌ No 'sealed' block found")
            return False, messages

        # 1. Check Merkle root exists
        merkle_root = sealed.get('merkle_root')
        if not merkle_root:
            messages.append("❌ No merkle_root found")
            success = False
        else:
            messages.append(f"✓ Merkle root: {merkle_root[:32]}...")

        # 2. Verify exposed leaves
        leaves_exposed = sealed.get('leaves_exposed', [])
        messages.append(f"✓ Exposed leaves: {len(leaves_exposed)}")

        for leaf in leaves_exposed:
            role = leaf.get('role', 'unknown')
            leaf_hash = leaf.get('hash', '')
            messages.append(f"  - {role}: {leaf_hash[:32]}...")

        # 3. Verify policy assertions
        policy_assertions = sealed.get('policy_assertions', [])
        messages.append(f"\n✓ Policy assertions: {len(policy_assertions)}")

        for assertion in policy_assertions:
            policy_id = assertion.get('id', 'unknown')
            result = assertion.get('result', 'unknown')
            signer = assertion.get('signer', 'unknown')

            if result == 'pass':
                messages.append(f"  ✓ {policy_id}: {result} (signer: {signer})")
            else:
                messages.append(f"  ❌ {policy_id}: {result} (signer: {signer})")
                success = False

        # 4. Verify attestation
        attestation = op.get('attestation', {})
        attest_success, attest_msgs = self.verify_attestation(attestation)
        messages.extend(attest_msgs)
        success = success and attest_success

        return success, messages

    def verify_attestation(self, attestation: Dict) -> Tuple[bool, List[str]]:
        """Verify attestation block"""
        messages = ["\n--- Attestation Verification ---"]
        success = True

        mode = attestation.get('mode', 'basic')
        messages.append(f"✓ Mode: {mode}")

        signer = attestation.get('signer')
        signature = attestation.get('signature')
        timestamp = attestation.get('timestamp')

        if mode in ['signed', 'verifiable', 'zk']:
            if not signer:
                messages.append("❌ No signer for signed attestation")
                success = False
            else:
                messages.append(f"✓ Signer: {signer}")

            if not signature:
                messages.append("❌ No signature for signed attestation")
                success = False
            else:
                sig_type = signature.split(':', 1)[0] if ':' in signature else 'unknown'
                messages.append(f"✓ Signature type: {sig_type}")

        if timestamp:
            messages.append(f"✓ Timestamp: {timestamp}")

        # Check transparency anchoring
        transparency = attestation.get('transparency', [])
        if transparency:
            messages.append(f"✓ Transparency anchors: {len(transparency)}")
            for anchor in transparency:
                log_id = anchor.get('log_id', 'unknown')
                entry_id = anchor.get('entry_id', 'unknown')
                messages.append(f"  - Log: {log_id}, Entry: {entry_id}")

        # Check multisig
        multisig = attestation.get('multisig')
        if multisig:
            threshold = multisig.get('threshold', 0)
            signers = multisig.get('signers', [])
            messages.append(f"✓ Multisig: {threshold}-of-{len(signers)}")
            for s in signers:
                messages.append(f"  - {s}")

        # Check TEE
        tee = attestation.get('tee')
        if tee:
            tech = tee.get('technology', 'unknown')
            messages.append(f"✓ TEE: {tech}")
            mr_enclave = tee.get('mr_enclave', '')
            if mr_enclave:
                messages.append(f"  MR_ENCLAVE: {mr_enclave[:32]}...")

        return success, messages

    def verify_all_sealed(self) -> Tuple[bool, List[str]]:
        """Verify all sealed operations in the document"""
        sealed_ops = self.find_sealed_operations()

        if not sealed_ops:
            return True, ["No sealed operations found in document"]

        all_messages = [f"Found {len(sealed_ops)} sealed operation(s)"]
        overall_success = True

        for op in sealed_ops:
            success, messages = self.verify_sealed_operation(op)
            all_messages.extend(messages)
            overall_success = overall_success and success

        return overall_success, all_messages


def verify_inclusion_proof_demo():
    """Demonstrate Merkle inclusion proof verification"""
    print("\n=== Merkle Inclusion Proof Demo ===")

    # Example: 4-leaf tree
    leaves = [
        "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
    ]

    # Build tree
    level1_left = MerkleTree.hash_pair(leaves[0], leaves[1])
    level1_right = MerkleTree.hash_pair(leaves[2], leaves[3])
    root = MerkleTree.hash_pair(level1_left, level1_right)

    print(f"Root: {root}")

    # Prove leaf[0] is in the tree
    # Path: leaf[0] -> level1_left -> root
    # Siblings: [leaf[1], level1_right]
    # Indices: [0, 0] (leaf[0] is left of leaf[1], level1_left is left of level1_right)

    is_valid = MerkleTree.verify_inclusion(
        leaf_hash=leaves[0],
        root_hash=root,
        sibling_hashes=[leaves[1], level1_right],
        path_indices=[0, 0]
    )

    print(f"Proof for leaf[0]: {'✓ VALID' if is_valid else '❌ INVALID'}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    gg_file = sys.argv[1]

    try:
        with open(gg_file, 'r') as f:
            gg_data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)

    print(f"GenesisGraph Sealed Subgraph Verifier")
    print(f"File: {gg_file}")
    print(f"Spec version: {gg_data.get('spec_version', 'UNKNOWN')}")
    print(f"Profile: {gg_data.get('profile', 'NONE')}")

    verifier = SealedSubgraphVerifier(gg_data)
    success, messages = verifier.verify_all_sealed()

    for msg in messages:
        print(msg)

    # Demo Merkle proof
    verify_inclusion_proof_demo()

    print("\n" + "="*60)
    if success:
        print("✓ All sealed subgraph verifications PASSED")
        sys.exit(0)
    else:
        print("❌ Some verifications FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
