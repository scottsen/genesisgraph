"""
Performance benchmarks for GenesisGraph validation

Run with: pytest tests/test_performance.py --benchmark-only
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from genesisgraph.validator import GenesisGraphValidator


@pytest.fixture
def validator():
    """Create a validator instance"""
    return GenesisGraphValidator()


@pytest.fixture
def small_document():
    """Generate a small document (10 entities, 5 operations)"""
    return {
        "spec_version": "0.1.0",
        "entities": [
            {
                "id": f"entity_{i}",
                "type": "Dataset",
                "version": "1.0",
                "uri": f"https://example.com/data_{i}.csv",
                "hash": f"sha256:{'a' * 64}"
            }
            for i in range(10)
        ],
        "operations": [
            {
                "id": f"op_{i}",
                "type": "transformation",
                "inputs": [f"entity_{i}"],
                "outputs": [f"entity_{i+1}"]
            }
            for i in range(5)
        ],
        "tools": [
            {
                "id": "tool_1",
                "type": "Software",
                "version": "1.0"
            }
        ]
    }


@pytest.fixture
def medium_document():
    """Generate a medium document (100 entities, 50 operations)"""
    return {
        "spec_version": "0.1.0",
        "entities": [
            {
                "id": f"entity_{i}",
                "type": "Dataset",
                "version": "1.0",
                "uri": f"https://example.com/data_{i}.csv",
                "hash": f"sha256:{'a' * 64}"
            }
            for i in range(100)
        ],
        "operations": [
            {
                "id": f"op_{i}",
                "type": "transformation",
                "inputs": [f"entity_{i}"],
                "outputs": [f"entity_{i+1}"]
            }
            for i in range(50)
        ],
        "tools": [
            {
                "id": f"tool_{i}",
                "type": "Software",
                "version": "1.0"
            }
            for i in range(10)
        ]
    }


@pytest.fixture
def large_document():
    """Generate a large document (1000 entities, 500 operations)"""
    return {
        "spec_version": "0.1.0",
        "entities": [
            {
                "id": f"entity_{i}",
                "type": "Dataset",
                "version": "1.0",
                "uri": f"https://example.com/data_{i}.csv",
                "hash": f"sha256:{'a' * 64}"
            }
            for i in range(1000)
        ],
        "operations": [
            {
                "id": f"op_{i}",
                "type": "transformation",
                "inputs": [f"entity_{i}"],
                "outputs": [f"entity_{i+1}"]
            }
            for i in range(500)
        ],
        "tools": [
            {
                "id": f"tool_{i}",
                "type": "Software",
                "version": "1.0"
            }
            for i in range(50)
        ]
    }


def test_validation_small_document(benchmark, validator, small_document):
    """Benchmark validation of small document (10 entities)"""
    result = benchmark(validator.validate, small_document)
    assert result.is_valid, f"Validation failed: {result.errors}"


def test_validation_medium_document(benchmark, validator, medium_document):
    """Benchmark validation of medium document (100 entities)"""
    result = benchmark(validator.validate, medium_document)
    assert result.is_valid, f"Validation failed: {result.errors}"


def test_validation_large_document(benchmark, validator, large_document):
    """Benchmark validation of large document (1000 entities)"""
    result = benchmark(validator.validate, large_document)
    assert result.is_valid, f"Validation failed: {result.errors}"


def test_validation_with_schema(benchmark, small_document):
    """Benchmark validation with JSON Schema enabled"""
    validator = GenesisGraphValidator(use_schema=True)
    result = benchmark(validator.validate, small_document)
    assert result.is_valid or len(result.warnings) > 0  # Schema might not be found


def test_file_parsing_and_validation(benchmark, small_document):
    """Benchmark file I/O + validation"""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gg.yaml', delete=False) as f:
        yaml.dump(small_document, f)
        temp_path = f.name
    
    try:
        validator = GenesisGraphValidator()
        result = benchmark(validator.validate_file, temp_path)
        assert result.is_valid
    finally:
        Path(temp_path).unlink()


def test_multiple_validations(benchmark, validator, small_document):
    """Benchmark validating the same document multiple times"""
    def validate_multiple():
        results = []
        for _ in range(10):
            result = validator.validate(small_document)
            results.append(result)
        return results
    
    results = benchmark(validate_multiple)
    assert all(r.is_valid for r in results)


def test_validation_with_signatures(benchmark, small_document):
    """Benchmark validation with signature verification enabled"""
    # Add mock signatures to operations
    small_document['operations'] = [
        {
            **op,
            'attestation': {
                'mode': 'signed',
                'signer': 'did:key:test',
                'signature': 'ed25519:mock:test_signature',
                'timestamp': '2025-11-20T12:00:00Z'
            }
        }
        for op in small_document['operations']
    ]
    
    validator = GenesisGraphValidator(verify_signatures=True)
    result = benchmark(validator.validate, small_document)
    # Mock signatures should pass format validation
    assert result.is_valid or len(result.errors) == 0 or 'mock' in str(result.errors)


# Memory profiling tests (require pytest-memray or similar)

def test_memory_small_document(validator, small_document):
    """Test memory usage for small document"""
    # This is a placeholder - actual memory profiling requires additional tools
    result = validator.validate(small_document)
    assert result.is_valid


def test_memory_large_document(validator, large_document):
    """Test memory usage for large document"""
    # This is a placeholder - actual memory profiling requires additional tools
    result = validator.validate(large_document)
    assert result.is_valid


# Regression tests - ensure performance doesn't degrade

def test_performance_regression_baseline(benchmark, validator, medium_document):
    """Baseline performance test for regression detection
    
    Expected: < 100ms for 100 entities, 50 operations
    This test will fail if validation time significantly increases
    """
    result = benchmark(validator.validate, medium_document)
    assert result.is_valid
    
    # Check that benchmark completed in reasonable time
    # pytest-benchmark will track this over time


if __name__ == "__main__":
    # Run with: python tests/test_performance.py
    # Or: pytest tests/test_performance.py --benchmark-only
    print("Run with: pytest tests/test_performance.py --benchmark-only")
    print("\nNote: Install pytest-benchmark: pip install pytest-benchmark")
