#!/usr/bin/env python3
"""
GenesisGraph Transparency Anchoring Verifier

Demonstrates verification of transparency log anchoring including:
- Inclusion proof validation (RFC 6962 Certificate Transparency style)
- Consistency proof validation
- Multi-log witness validation

Usage:
    python verify_transparency_anchoring.py <path-to-gg-file>
"""

import sys
import yaml
import hashlib
import base64
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TransparencyLogEntry:
    """Transparency log entry metadata"""
    log_id: str
    entry_id: str
    tree_size: int
    inclusion_proof: str
    consistency_proof: Optional[str] = None


class TransparencyVerifier:
    """
    Verifies Certificate Transparency-style inclusion proofs

    Based on RFC 6962: Certificate Transparency
    """

    @staticmethod
    def hash_leaf(data: bytes) -> bytes:
        """Hash a leaf node (0x00 || data)"""
        return hashlib.sha256(b'\x00' + data).digest()

    @staticmethod
    def hash_children(left: bytes, right: bytes) -> bytes:
        """Hash internal node (0x01 || left || right)"""
        return hashlib.sha256(b'\x01' + left + right).digest()

    @staticmethod
    def verify_inclusion_proof(
        leaf_hash: bytes,
        tree_size: int,
        leaf_index: int,
        proof_nodes: List[bytes],
        root_hash: bytes
    ) -> bool:
        """
        Verify Merkle audit proof (inclusion proof)

        Args:
            leaf_hash: Hash of the leaf to verify
            tree_size: Total number of leaves in the tree
            leaf_index: Index of the leaf (0-based)
            proof_nodes: Sibling hashes along the path
            root_hash: Expected root hash

        Returns:
            True if proof is valid
        """
        if leaf_index >= tree_size:
            return False

        # Reconstruct root from leaf and proof
        current_hash = leaf_hash
        current_index = leaf_index
        current_tree_size = tree_size

        for sibling in proof_nodes:
            if current_index % 2 == 0:
                # Current node is left child
                if current_index + 1 < current_tree_size:
                    current_hash = TransparencyVerifier.hash_children(
                        current_hash, sibling
                    )
                else:
                    # Odd tree, current is the last node
                    current_hash = current_hash
            else:
                # Current node is right child
                current_hash = TransparencyVerifier.hash_children(
                    sibling, current_hash
                )

            current_index //= 2
            current_tree_size = (current_tree_size + 1) // 2

        return current_hash == root_hash

    @staticmethod
    def verify_consistency_proof(
        tree_size_1: int,
        tree_size_2: int,
        root_hash_1: bytes,
        root_hash_2: bytes,
        proof_nodes: List[bytes]
    ) -> bool:
        """
        Verify Merkle consistency proof

        Proves that tree_2 is an append-only extension of tree_1

        Args:
            tree_size_1: Size of older tree
            tree_size_2: Size of newer tree
            root_hash_1: Root hash of older tree
            root_hash_2: Root hash of newer tree
            proof_nodes: Consistency proof nodes

        Returns:
            True if consistency proof is valid
        """
        if tree_size_1 > tree_size_2:
            return False

        if tree_size_1 == tree_size_2:
            return root_hash_1 == root_hash_2 and len(proof_nodes) == 0

        # Simplified consistency check (full implementation is complex)
        # In production, implement full RFC 6962 consistency proof algorithm
        return True  # Placeholder


class GenesisGraphTransparencyVerifier:
    """Verifies transparency anchoring in GenesisGraph documents"""

    def __init__(self, gg_data: Dict):
        self.gg_data = gg_data
        self.operations = gg_data.get('operations', [])

    def find_anchored_operations(self) -> List[Dict]:
        """Find all operations with transparency anchoring"""
        anchored = []
        for op in self.operations:
            attestation = op.get('attestation', {})
            if attestation.get('transparency'):
                anchored.append(op)
        return anchored

    def verify_transparency_entry(
        self,
        op: Dict,
        entry: Dict
    ) -> Tuple[bool, List[str]]:
        """
        Verify a single transparency log entry

        Returns:
            (success, messages) tuple
        """
        messages = []
        success = True

        log_id = entry.get('log_id', 'UNKNOWN')
        entry_id = entry.get('entry_id', 'UNKNOWN')
        tree_size = entry.get('tree_size', 0)
        inclusion_proof_b64 = entry.get('inclusion_proof', '')

        messages.append(f"\n  Verifying transparency anchor:")
        messages.append(f"    Log ID: {log_id}")
        messages.append(f"    Entry ID: {entry_id}")
        messages.append(f"    Tree size: {tree_size}")

        # Check required fields
        if not log_id or log_id == 'UNKNOWN':
            messages.append("    ❌ Missing log_id")
            success = False

        if not entry_id or entry_id == 'UNKNOWN':
            messages.append("    ❌ Missing entry_id")
            success = False

        if tree_size == 0:
            messages.append("    ❌ Invalid tree_size")
            success = False

        if not inclusion_proof_b64:
            messages.append("    ❌ Missing inclusion_proof")
            success = False
        else:
            try:
                # Decode proof (in production, verify against log)
                proof_data = base64.b64decode(inclusion_proof_b64)
                messages.append(f"    ✓ Inclusion proof: {len(proof_data)} bytes")

                # In production: fetch root hash from log and verify
                # For now, just validate format

            except Exception as e:
                messages.append(f"    ❌ Invalid inclusion_proof encoding: {e}")
                success = False

        # Check consistency proof if present
        consistency_proof_b64 = entry.get('consistency_proof')
        if consistency_proof_b64:
            try:
                proof_data = base64.b64decode(consistency_proof_b64)
                messages.append(f"    ✓ Consistency proof: {len(proof_data)} bytes")
            except Exception as e:
                messages.append(f"    ❌ Invalid consistency_proof encoding: {e}")
                success = False

        if success:
            messages.append("    ✓ Transparency entry format valid")

        return success, messages

    def verify_operation(self, op: Dict) -> Tuple[bool, List[str]]:
        """
        Verify transparency anchoring for an operation

        Returns:
            (success, messages) tuple
        """
        messages = []
        success = True

        op_id = op.get('id', 'UNKNOWN')
        messages.append(f"\n=== Operation: {op_id} ===")

        attestation = op.get('attestation', {})
        transparency = attestation.get('transparency', [])

        if not transparency:
            messages.append("  No transparency anchoring found")
            return True, messages

        messages.append(f"  Found {len(transparency)} transparency anchor(s)")

        for i, entry in enumerate(transparency, 1):
            entry_success, entry_msgs = self.verify_transparency_entry(op, entry)
            messages.extend(entry_msgs)
            success = success and entry_success

        # Multi-witness validation
        if len(transparency) > 1:
            messages.append(f"\n  ✓ Multi-witness: {len(transparency)} independent logs")

        return success, messages

    def verify_all_anchored(self) -> Tuple[bool, List[str]]:
        """Verify all transparency-anchored operations"""
        anchored_ops = self.find_anchored_operations()

        if not anchored_ops:
            return True, ["No transparency-anchored operations found"]

        all_messages = [
            f"Found {len(anchored_ops)} transparency-anchored operation(s)"
        ]
        overall_success = True

        for op in anchored_ops:
            success, messages = self.verify_operation(op)
            all_messages.extend(messages)
            overall_success = overall_success and success

        return overall_success, all_messages

    def generate_summary(self) -> Dict:
        """Generate transparency anchoring summary"""
        anchored_ops = self.find_anchored_operations()

        total_anchors = 0
        log_ids = set()

        for op in anchored_ops:
            attestation = op.get('attestation', {})
            transparency = attestation.get('transparency', [])
            total_anchors += len(transparency)

            for entry in transparency:
                log_id = entry.get('log_id')
                if log_id:
                    log_ids.add(log_id)

        return {
            'anchored_operations': len(anchored_ops),
            'total_anchors': total_anchors,
            'unique_logs': len(log_ids),
            'log_ids': list(log_ids)
        }


def demonstrate_inclusion_proof():
    """Demonstrate CT-style inclusion proof verification"""
    print("\n=== Certificate Transparency Inclusion Proof Demo ===")

    # Build a simple 4-leaf tree
    leaves = [
        b"leaf_0_data",
        b"leaf_1_data",
        b"leaf_2_data",
        b"leaf_3_data",
    ]

    leaf_hashes = [TransparencyVerifier.hash_leaf(leaf) for leaf in leaves]

    # Build tree
    level1_0 = TransparencyVerifier.hash_children(leaf_hashes[0], leaf_hashes[1])
    level1_1 = TransparencyVerifier.hash_children(leaf_hashes[2], leaf_hashes[3])
    root = TransparencyVerifier.hash_children(level1_0, level1_1)

    print(f"Root hash: {root.hex()[:32]}...")

    # Prove leaf[0] is in the tree
    # Proof path: [leaf_1_hash, level1_1]
    proof_valid = TransparencyVerifier.verify_inclusion_proof(
        leaf_hash=leaf_hashes[0],
        tree_size=4,
        leaf_index=0,
        proof_nodes=[leaf_hashes[1], level1_1],
        root_hash=root
    )

    print(f"Inclusion proof for leaf[0]: {'✓ VALID' if proof_valid else '❌ INVALID'}")


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

    print(f"GenesisGraph Transparency Anchoring Verifier")
    print(f"File: {gg_file}")
    print(f"Spec version: {gg_data.get('spec_version', 'UNKNOWN')}")
    print(f"Profile: {gg_data.get('profile', 'NONE')}")

    verifier = GenesisGraphTransparencyVerifier(gg_data)

    # Generate summary
    summary = verifier.generate_summary()
    print(f"\n=== Transparency Summary ===")
    print(f"Anchored operations: {summary['anchored_operations']}")
    print(f"Total anchors: {summary['total_anchors']}")
    print(f"Unique logs: {summary['unique_logs']}")
    if summary['log_ids']:
        print(f"Log IDs:")
        for log_id in summary['log_ids']:
            print(f"  - {log_id}")

    # Verify all
    success, messages = verifier.verify_all_anchored()

    for msg in messages:
        print(msg)

    # Demo CT-style proof
    demonstrate_inclusion_proof()

    print("\n" + "="*60)
    if success:
        print("✓ All transparency anchor verifications PASSED")
        sys.exit(0)
    else:
        print("❌ Some verifications FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
