"""
Tests for transparency log integration (RFC 6962)

Tests Certificate Transparency-style verification including:
- RFC 6962 Merkle tree verification
- Inclusion proof validation
- Consistency proof validation
- Multi-witness validation
- Integration with GenesisGraph validator
"""

import hashlib

import pytest

from genesisgraph.transparency_log import (
    InvalidProofError,
    InvalidTreeError,
    RFC6962Verifier,
    TransparencyLogEntry,
    TransparencyLogVerifier,
)


class TestRFC6962Verifier:
    """Test low-level RFC 6962 Merkle tree verification"""

    def test_hash_leaf(self):
        """Test leaf hashing with 0x00 prefix"""
        data = b"test_leaf_data"
        leaf_hash = RFC6962Verifier.hash_leaf(data)

        # Should be SHA-256(0x00 || data)
        expected = hashlib.sha256(b'\x00' + data).digest()
        assert leaf_hash == expected
        assert len(leaf_hash) == 32

    def test_hash_children(self):
        """Test internal node hashing with 0x01 prefix"""
        left = b'0' * 32
        right = b'1' * 32

        node_hash = RFC6962Verifier.hash_children(left, right)

        # Should be SHA-256(0x01 || left || right)
        expected = hashlib.sha256(b'\x01' + left + right).digest()
        assert node_hash == expected
        assert len(node_hash) == 32

    def test_verify_inclusion_proof_single_leaf(self):
        """Test inclusion proof for a tree with one leaf"""
        # Tree with single leaf
        leaf_data = b"single_leaf"
        leaf_hash = RFC6962Verifier.hash_leaf(leaf_data)

        # For a single-leaf tree, the root is the leaf hash
        root_hash = leaf_hash

        # Proof should be empty for single leaf
        is_valid = RFC6962Verifier.verify_inclusion_proof(
            leaf_hash=leaf_hash,
            tree_size=1,
            leaf_index=0,
            proof_nodes=[],
            root_hash=root_hash
        )
        assert is_valid

    def test_verify_inclusion_proof_two_leaves(self):
        """Test inclusion proof for a tree with two leaves"""
        # Build a 2-leaf tree
        leaf0_data = b"leaf_0"
        leaf1_data = b"leaf_1"

        leaf0_hash = RFC6962Verifier.hash_leaf(leaf0_data)
        leaf1_hash = RFC6962Verifier.hash_leaf(leaf1_data)

        # Root = hash_children(leaf0, leaf1)
        root_hash = RFC6962Verifier.hash_children(leaf0_hash, leaf1_hash)

        # Prove leaf0 is in the tree
        # Proof path: [leaf1_hash]
        is_valid = RFC6962Verifier.verify_inclusion_proof(
            leaf_hash=leaf0_hash,
            tree_size=2,
            leaf_index=0,
            proof_nodes=[leaf1_hash],
            root_hash=root_hash
        )
        assert is_valid

        # Prove leaf1 is in the tree
        # Proof path: [leaf0_hash]
        is_valid = RFC6962Verifier.verify_inclusion_proof(
            leaf_hash=leaf1_hash,
            tree_size=2,
            leaf_index=1,
            proof_nodes=[leaf0_hash],
            root_hash=root_hash
        )
        assert is_valid

    def test_verify_inclusion_proof_four_leaves(self):
        """Test inclusion proof for a balanced 4-leaf tree"""
        # Build a 4-leaf tree
        leaves = [b"leaf_0", b"leaf_1", b"leaf_2", b"leaf_3"]
        leaf_hashes = [RFC6962Verifier.hash_leaf(leaf) for leaf in leaves]

        # Build tree
        level1_0 = RFC6962Verifier.hash_children(leaf_hashes[0], leaf_hashes[1])
        level1_1 = RFC6962Verifier.hash_children(leaf_hashes[2], leaf_hashes[3])
        root = RFC6962Verifier.hash_children(level1_0, level1_1)

        # Prove leaf[0] is in the tree
        # Proof path: [leaf_1_hash, level1_1]
        is_valid = RFC6962Verifier.verify_inclusion_proof(
            leaf_hash=leaf_hashes[0],
            tree_size=4,
            leaf_index=0,
            proof_nodes=[leaf_hashes[1], level1_1],
            root_hash=root
        )
        assert is_valid

        # Prove leaf[2] is in the tree
        # Proof path: [leaf_3_hash, level1_0]
        is_valid = RFC6962Verifier.verify_inclusion_proof(
            leaf_hash=leaf_hashes[2],
            tree_size=4,
            leaf_index=2,
            proof_nodes=[leaf_hashes[3], level1_0],
            root_hash=root
        )
        assert is_valid

    def test_verify_inclusion_proof_invalid_wrong_root(self):
        """Test that invalid proof fails with wrong root hash"""
        leaf_data = b"test_leaf"
        leaf_hash = RFC6962Verifier.hash_leaf(leaf_data)

        wrong_root = b'0' * 32  # Wrong root hash

        is_valid = RFC6962Verifier.verify_inclusion_proof(
            leaf_hash=leaf_hash,
            tree_size=1,
            leaf_index=0,
            proof_nodes=[],
            root_hash=wrong_root
        )
        assert not is_valid

    def test_verify_inclusion_proof_invalid_index_out_of_range(self):
        """Test that out-of-range index raises error"""
        leaf_hash = b'0' * 32
        root_hash = b'1' * 32

        with pytest.raises(InvalidTreeError):
            RFC6962Verifier.verify_inclusion_proof(
                leaf_hash=leaf_hash,
                tree_size=4,
                leaf_index=10,  # Out of range
                proof_nodes=[],
                root_hash=root_hash
            )

    def test_verify_inclusion_proof_invalid_negative_index(self):
        """Test that negative index raises error"""
        leaf_hash = b'0' * 32
        root_hash = b'1' * 32

        with pytest.raises(InvalidTreeError):
            RFC6962Verifier.verify_inclusion_proof(
                leaf_hash=leaf_hash,
                tree_size=4,
                leaf_index=-1,  # Negative
                proof_nodes=[],
                root_hash=root_hash
            )

    def test_verify_inclusion_proof_invalid_tree_size(self):
        """Test that invalid tree size raises error"""
        leaf_hash = b'0' * 32
        root_hash = b'1' * 32

        with pytest.raises(InvalidTreeError):
            RFC6962Verifier.verify_inclusion_proof(
                leaf_hash=leaf_hash,
                tree_size=0,  # Invalid
                leaf_index=0,
                proof_nodes=[],
                root_hash=root_hash
            )

    def test_verify_inclusion_proof_invalid_hash_length(self):
        """Test that invalid hash length raises error"""
        leaf_hash = b'short'  # Too short
        root_hash = b'1' * 32

        with pytest.raises(InvalidProofError):
            RFC6962Verifier.verify_inclusion_proof(
                leaf_hash=leaf_hash,
                tree_size=1,
                leaf_index=0,
                proof_nodes=[],
                root_hash=root_hash
            )

    def test_verify_inclusion_proof_invalid_proof_node_length(self):
        """Test that invalid proof node length raises error"""
        leaf_hash = b'0' * 32
        root_hash = b'1' * 32
        bad_proof_node = b'short'  # Too short

        with pytest.raises(InvalidProofError):
            RFC6962Verifier.verify_inclusion_proof(
                leaf_hash=leaf_hash,
                tree_size=2,
                leaf_index=0,
                proof_nodes=[bad_proof_node],
                root_hash=root_hash
            )

    def test_verify_consistency_proof_same_size(self):
        """Test consistency proof for same tree size"""
        root_hash = b'0' * 32

        # Same size should require empty proof and matching roots
        is_valid = RFC6962Verifier.verify_consistency_proof(
            tree_size_1=5,
            tree_size_2=5,
            root_hash_1=root_hash,
            root_hash_2=root_hash,
            proof_nodes=[]
        )
        assert is_valid

        # Same size with different roots should fail
        different_root = b'1' * 32
        is_valid = RFC6962Verifier.verify_consistency_proof(
            tree_size_1=5,
            tree_size_2=5,
            root_hash_1=root_hash,
            root_hash_2=different_root,
            proof_nodes=[]
        )
        assert not is_valid

    def test_verify_consistency_proof_empty_tree(self):
        """Test consistency proof with empty tree"""
        root_hash = b'0' * 32

        # Empty tree is consistent with any tree
        is_valid = RFC6962Verifier.verify_consistency_proof(
            tree_size_1=0,
            tree_size_2=10,
            root_hash_1=root_hash,
            root_hash_2=root_hash,
            proof_nodes=[]
        )
        assert is_valid

    def test_verify_consistency_proof_invalid_size_order(self):
        """Test that tree_size_1 > tree_size_2 raises error"""
        root_hash = b'0' * 32

        with pytest.raises(InvalidTreeError):
            RFC6962Verifier.verify_consistency_proof(
                tree_size_1=10,
                tree_size_2=5,  # Smaller than tree_size_1
                root_hash_1=root_hash,
                root_hash_2=root_hash,
                proof_nodes=[]
            )

    def test_verify_consistency_proof_invalid_tree_size(self):
        """Test that invalid tree sizes raise errors"""
        root_hash = b'0' * 32

        with pytest.raises(InvalidTreeError):
            RFC6962Verifier.verify_consistency_proof(
                tree_size_1=-1,
                tree_size_2=5,
                root_hash_1=root_hash,
                root_hash_2=root_hash,
                proof_nodes=[]
            )

    def test_verify_consistency_proof_invalid_hash_length(self):
        """Test that invalid hash lengths raise errors"""
        with pytest.raises(InvalidProofError):
            RFC6962Verifier.verify_consistency_proof(
                tree_size_1=1,
                tree_size_2=5,
                root_hash_1=b'short',  # Too short
                root_hash_2=b'1' * 32,
                proof_nodes=[]
            )


class TestTransparencyLogVerifier:
    """Test high-level transparency log verifier"""

    def test_verify_transparency_entry_valid(self):
        """Test verification of a valid transparency entry (with truncated example)"""
        verifier = TransparencyLogVerifier(verify_proofs=True)

        # Create transparency entry with truncated proof (example data)
        entry = {
            'log_id': 'did:log:test-log',
            'entry_id': '0x0',
            'tree_size': 1,
            'inclusion_proof': 'base64:example...',  # Truncated example
        }

        is_valid, errors = verifier.verify_transparency_entry(
            entry, b"operation_data", context="test"
        )
        assert is_valid  # Truncated examples are accepted
        assert len(errors) == 0

    def test_verify_transparency_entry_missing_log_id(self):
        """Test that missing log_id is detected"""
        verifier = TransparencyLogVerifier(verify_proofs=True)

        entry = {
            # 'log_id' missing
            'entry_id': '0x0',
            'tree_size': 1,
            'inclusion_proof': 'base64data'
        }

        is_valid, errors = verifier.verify_transparency_entry(
            entry, b"data", context="test"
        )
        assert not is_valid
        assert any('log_id' in err for err in errors)

    def test_verify_transparency_entry_missing_entry_id(self):
        """Test that missing entry_id is detected"""
        verifier = TransparencyLogVerifier(verify_proofs=True)

        entry = {
            'log_id': 'did:log:test',
            # 'entry_id' missing
            'tree_size': 1,
            'inclusion_proof': 'base64data'
        }

        is_valid, errors = verifier.verify_transparency_entry(
            entry, b"data", context="test"
        )
        assert not is_valid
        assert any('entry_id' in err for err in errors)

    def test_verify_transparency_entry_invalid_tree_size(self):
        """Test that invalid tree_size is detected"""
        verifier = TransparencyLogVerifier(verify_proofs=True)

        entry = {
            'log_id': 'did:log:test',
            'entry_id': '0x0',
            'tree_size': 0,  # Invalid
            'inclusion_proof': 'base64data'
        }

        is_valid, errors = verifier.verify_transparency_entry(
            entry, b"data", context="test"
        )
        assert not is_valid
        assert any('tree_size' in err for err in errors)

    def test_verify_transparency_entry_missing_proof(self):
        """Test that missing inclusion_proof is detected"""
        verifier = TransparencyLogVerifier(verify_proofs=True)

        entry = {
            'log_id': 'did:log:test',
            'entry_id': '0x0',
            'tree_size': 1,
            # 'inclusion_proof' missing
        }

        is_valid, errors = verifier.verify_transparency_entry(
            entry, b"data", context="test"
        )
        assert not is_valid
        assert any('inclusion_proof' in err for err in errors)

    def test_verify_transparency_entry_truncated_example(self):
        """Test that truncated example proofs (ending with ...) are accepted"""
        verifier = TransparencyLogVerifier(verify_proofs=True)

        entry = {
            'log_id': 'did:log:test',
            'entry_id': '0x0',
            'tree_size': 1,
            'inclusion_proof': 'base64:MIICDzCCAbWgAwIBAgIUFmNj2fDq6vN6P5...'  # Truncated
        }

        is_valid, errors = verifier.verify_transparency_entry(
            entry, b"data", context="test"
        )
        assert is_valid  # Should accept truncated example data
        assert len(errors) == 0

    def test_verify_transparency_entry_log_id_too_long(self):
        """Test that excessively long log_id is rejected"""
        verifier = TransparencyLogVerifier(verify_proofs=True)

        entry = {
            'log_id': 'x' * 1000,  # Too long
            'entry_id': '0x0',
            'tree_size': 1,
            'inclusion_proof': 'base64data'
        }

        is_valid, errors = verifier.verify_transparency_entry(
            entry, b"data", context="test"
        )
        assert not is_valid
        assert any('too long' in err for err in errors)

    def test_verify_multi_witness_all_valid(self):
        """Test multi-witness with all valid entries"""
        verifier = TransparencyLogVerifier(verify_proofs=False)  # Skip crypto for simplicity

        entries = [
            {
                'log_id': 'did:log:witness-1',
                'entry_id': '0x1',
                'tree_size': 10,
                'inclusion_proof': 'base64:abc...'  # Truncated example
            },
            {
                'log_id': 'did:log:witness-2',
                'entry_id': '0x2',
                'tree_size': 20,
                'inclusion_proof': 'base64:def...'  # Truncated example
            }
        ]

        is_valid, messages = verifier.verify_multi_witness(
            entries, b"test_data", context="test", require_all=True
        )
        assert is_valid

    def test_verify_multi_witness_some_valid(self):
        """Test multi-witness with some valid entries (require_all=False)"""
        verifier = TransparencyLogVerifier(verify_proofs=False)

        entries = [
            {
                'log_id': 'did:log:witness-1',
                'entry_id': '0x1',
                'tree_size': 10,
                'inclusion_proof': 'base64:abc...'
            },
            {
                'log_id': 'did:log:witness-2',
                # Missing entry_id - will fail
                'tree_size': 20,
                'inclusion_proof': 'base64:def...'
            }
        ]

        is_valid, messages = verifier.verify_multi_witness(
            entries, b"test_data", context="test", require_all=False
        )
        assert is_valid  # At least one is valid

    def test_verify_multi_witness_require_all_fails(self):
        """Test multi-witness with require_all=True fails if any invalid"""
        verifier = TransparencyLogVerifier(verify_proofs=False)

        entries = [
            {
                'log_id': 'did:log:witness-1',
                'entry_id': '0x1',
                'tree_size': 10,
                'inclusion_proof': 'base64:abc...'
            },
            {
                'log_id': 'did:log:witness-2',
                # Missing tree_size - will fail
                'entry_id': '0x2',
                'inclusion_proof': 'base64:def...'
            }
        ]

        is_valid, messages = verifier.verify_multi_witness(
            entries, b"test_data", context="test", require_all=True
        )
        assert not is_valid  # Not all valid

    def test_verify_multi_witness_empty_list(self):
        """Test multi-witness with empty entry list"""
        verifier = TransparencyLogVerifier(verify_proofs=False)

        is_valid, messages = verifier.verify_multi_witness(
            [], b"test_data", context="test"
        )
        assert is_valid  # Empty list is valid


class TestTransparencyLogIntegration:
    """Integration tests with GenesisGraph validator"""

    def test_validator_with_transparency_disabled(self):
        """Test that validator works with transparency disabled"""
        from genesisgraph.validator import GenesisGraphValidator

        data = {
            'spec_version': '0.1',
            'entities': [
                {'id': 'e1', 'type': 'data', 'version': '1.0', 'uri': 'file:///tmp/test.txt'}
            ],
            'operations': [
                {
                    'id': 'op1',
                    'type': 'process',
                    'inputs': [{'entity_id': 'e1'}],
                    'outputs': [{'entity_id': 'e1'}],
                    'attestation': {
                        'mode': 'basic'
                    }
                }
            ]
        }

        validator = GenesisGraphValidator(verify_transparency=False)
        result = validator.validate(data)
        assert result.is_valid

    def test_validator_with_transparency_no_entries(self):
        """Test validator with transparency enabled but no transparency entries"""
        from genesisgraph.validator import GenesisGraphValidator

        data = {
            'spec_version': '0.1',
            'entities': [
                {'id': 'e1', 'type': 'data', 'version': '1.0', 'uri': 'file:///tmp/test.txt'}
            ],
            'operations': [
                {
                    'id': 'op1',
                    'type': 'process',
                    'inputs': [{'entity_id': 'e1'}],
                    'outputs': [{'entity_id': 'e1'}],
                    'attestation': {
                        'mode': 'basic'
                    }
                }
            ]
        }

        validator = GenesisGraphValidator(verify_transparency=True)
        result = validator.validate(data)
        assert result.is_valid  # No transparency entries is OK

    def test_validator_with_transparency_entry(self):
        """Test validator with transparency entry (example data)"""
        from genesisgraph.validator import GenesisGraphValidator

        data = {
            'spec_version': '0.1',
            'entities': [
                {'id': 'e1', 'type': 'data', 'version': '1.0', 'uri': 'file:///tmp/test.txt'}
            ],
            'operations': [
                {
                    'id': 'op1',
                    'type': 'process',
                    'inputs': [{'entity_id': 'e1'}],
                    'outputs': [{'entity_id': 'e1'}],
                    'attestation': {
                        'mode': 'signed',
                        'signer': 'did:key:test',
                        'signature': 'ed25519:mock:test',
                        'transparency': [
                            {
                                'log_id': 'did:log:test-log',
                                'entry_id': '0x1',
                                'tree_size': 100,
                                'inclusion_proof': 'base64:example...'  # Truncated
                            }
                        ]
                    }
                }
            ]
        }

        validator = GenesisGraphValidator(verify_transparency=True)
        result = validator.validate(data)
        assert result.is_valid  # Truncated example proofs are accepted

    def test_validator_with_invalid_transparency_entry(self):
        """Test validator detects invalid transparency entry"""
        from genesisgraph.validator import GenesisGraphValidator

        data = {
            'spec_version': '0.1',
            'entities': [
                {'id': 'e1', 'type': 'data', 'version': '1.0', 'uri': 'file:///tmp/test.txt'}
            ],
            'operations': [
                {
                    'id': 'op1',
                    'type': 'process',
                    'inputs': [{'entity_id': 'e1'}],
                    'outputs': [{'entity_id': 'e1'}],
                    'attestation': {
                        'mode': 'basic',
                        'transparency': [
                            {
                                'log_id': 'did:log:test-log',
                                # Missing required fields: entry_id and inclusion_proof
                                'tree_size': 100
                            }
                        ]
                    }
                }
            ]
        }

        validator = GenesisGraphValidator(verify_transparency=True)
        result = validator.validate(data)
        assert not result.is_valid
        # Should have errors about verification failure
        errors_str = ' '.join(result.errors)
        assert 'Verification failed' in errors_str or 'No witnesses verified' in errors_str


class TestTransparencyLogEntry:
    """Test TransparencyLogEntry dataclass"""

    def test_transparency_log_entry_creation(self):
        """Test creating a transparency log entry"""
        entry = TransparencyLogEntry(
            log_id='did:log:test',
            entry_id='0x123',
            tree_size=1000,
            inclusion_proof='base64:proof_data'
        )

        assert entry.log_id == 'did:log:test'
        assert entry.entry_id == '0x123'
        assert entry.tree_size == 1000
        assert entry.inclusion_proof == 'base64:proof_data'
        assert entry.consistency_proof is None
        assert entry.timestamp is None

    def test_transparency_log_entry_with_optional_fields(self):
        """Test creating entry with optional fields"""
        entry = TransparencyLogEntry(
            log_id='did:log:test',
            entry_id='0x123',
            tree_size=1000,
            inclusion_proof='base64:proof',
            consistency_proof='base64:consistency',
            timestamp=1234567890,
            root_hash='abcd1234'
        )

        assert entry.consistency_proof == 'base64:consistency'
        assert entry.timestamp == 1234567890
        assert entry.root_hash == 'abcd1234'
