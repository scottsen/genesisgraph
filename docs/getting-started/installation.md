# Installation Guide

## Requirements

- **Python**: 3.8 or higher
- **pip**: Latest version recommended

## Basic Installation

Install GenesisGraph from PyPI:

```bash
pip install genesisgraph
```

This installs the core library with:
- ✅ YAML parsing
- ✅ JSON Schema validation
- ✅ Cryptographic verification (Ed25519)
- ✅ DID resolution (did:key, did:web, did:ion, did:ethr)
- ✅ Transparency log verification (RFC 6962)

## Optional Features

### CLI with Rich Formatting

```bash
pip install genesisgraph[cli]
```

Adds:
- `gg` command-line tool
- Rich terminal output with colors
- Progress bars and formatting

### Selective Disclosure (SD-JWT, BBS+)

```bash
pip install genesisgraph[credentials]
```

Adds:
- SD-JWT (Selective Disclosure JWT)
- BBS+ signatures
- Zero-knowledge predicate proofs

### Development Tools

```bash
pip install genesisgraph[dev]
```

Adds:
- pytest (testing)
- black (code formatting)
- ruff (linting)
- mypy (type checking)

### All Features

```bash
pip install genesisgraph[cli,credentials,dev]
```

## Verify Installation

```bash
# Check version
python -c "import genesisgraph; print(genesisgraph.__version__)"

# Test CLI
gg --version

# Run validation test
gg validate examples/level-a-full-disclosure.gg.yaml
```

## Platform-Specific Instructions

=== "Linux (Ubuntu/Debian)"

    ```bash
    # Install system dependencies
    sudo apt-get update
    sudo apt-get install python3 python3-pip python3-dev build-essential libssl-dev
    
    # Install GenesisGraph
    pip3 install genesisgraph[cli]
    ```

=== "macOS"

    ```bash
    # Install Homebrew (if not installed)
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Install Python 3
    brew install python@3.11
    
    # Install OpenSSL (for cryptography)
    brew install openssl
    
    # Install GenesisGraph
    pip3 install genesisgraph[cli]
    ```

=== "Windows"

    ```powershell
    # Using Python from python.org or Microsoft Store
    python -m pip install --upgrade pip
    python -m pip install genesisgraph[cli]
    
    # Add Scripts directory to PATH if needed
    # C:\Users\<YourName>\AppData\Local\Programs\Python\Python311\Scripts
    ```

## Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install
pip install genesisgraph[cli]
```

## Troubleshooting

See [Troubleshooting Guide](../developer-guide/troubleshooting.md) for common issues.

## Next Steps

- [Quickstart Tutorial](quickstart.md)
- [Examples](examples.md)
- [User Guide](../user-guide/overview.md)
