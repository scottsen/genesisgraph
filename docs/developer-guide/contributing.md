# Contributing to GenesisGraph

Thank you for your interest in contributing to GenesisGraph! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors. We expect:

- Be respectful and constructive in communication
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Familiarity with YAML and JSON Schema

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/genesisgraph/genesisgraph.git
   cd genesisgraph
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev,cli]"
   ```

4. **Run tests to verify setup**
   ```bash
   pytest tests/
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Reports** - Report issues you encounter
2. **Feature Requests** - Suggest new features or improvements
3. **Code Contributions** - Fix bugs or implement features
4. **Documentation** - Improve or add documentation
5. **Examples** - Create example files for different use cases
6. **Domain Profiles** - Develop profiles for specific domains (AI, manufacturing, etc.)

### Reporting Bugs

Before creating a bug report:
- Check existing issues to avoid duplicates
- Gather information about your environment

Create an issue with:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- GenesisGraph version and Python version
- Minimal example that reproduces the issue

### Suggesting Features

Feature requests should include:
- Clear use case and motivation
- Proposed implementation (if you have ideas)
- Examples of how it would be used
- Potential impact on existing functionality

## Coding Standards

### Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters
- **Formatting**: Use `black` for code formatting
- **Linting**: Use `ruff` for linting
- **Type hints**: Use type hints where appropriate

Run formatting and linting:
```bash
black genesisgraph/
ruff check genesisgraph/
```

### Code Structure

- **One feature per PR**: Keep pull requests focused
- **Modular design**: Write reusable, modular code
- **Documentation**: Add docstrings to all public functions and classes
- **Type hints**: Use type hints for function signatures

### Documentation Style

Docstrings should follow Google style:

```python
def validate_file(file_path: str) -> ValidationResult:
    """
    Validate a GenesisGraph file.

    Args:
        file_path: Path to .gg.yaml file

    Returns:
        ValidationResult with validation details

    Raises:
        FileNotFoundError: If file doesn't exist

    Example:
        >>> result = validate_file("workflow.gg.yaml")
        >>> print(result.format_report())
    """
```

## Testing

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=genesisgraph --cov-report=html
```

Run specific test:
```bash
pytest tests/test_validator.py::TestGenesisGraphValidator::test_validate_minimal_document
```

### Writing Tests

- Write tests for all new features
- Aim for >90% code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

Example:
```python
def test_entity_validation():
    """Test entity validation with required fields"""
    # Arrange
    data = {'spec_version': '0.1.0', 'entities': [...]}
    validator = GenesisGraphValidator()

    # Act
    result = validator.validate(data)

    # Assert
    assert result.is_valid
    assert len(result.errors) == 0
```

## Submitting Changes

### Pull Request Process

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation
   - Run tests locally

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new validation feature"
   ```

   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Adding or updating tests
   - `refactor:` - Code refactoring
   - `chore:` - Maintenance tasks

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to GitHub and create a PR
   - Fill in the PR template
   - Link any related issues
   - Request review from maintainers

### PR Requirements

Before submitting:
- [ ] All tests pass
- [ ] Code follows style guide
- [ ] Documentation is updated
- [ ] Changelog is updated (for significant changes)
- [ ] Examples are provided (if applicable)

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code contributions

### Getting Help

If you need help:
1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Reach out to maintainers

## Domain-Specific Contributions

### Creating Domain Profiles

Domain profiles extend GenesisGraph for specific use cases. To create a profile:

1. **Define the scope** - What domain does it cover?
2. **Specify requirements** - What fields are mandatory?
3. **Create examples** - Provide real-world examples
4. **Write documentation** - Explain use cases and integration

Example profile IDs:
- `gg-ai-basic-v1` - Basic AI workflows
- `gg-cam-v1` - CAM/manufacturing
- `gg-bio-v1` - Bioinformatics
- `gg-media-c2pa-v1` - Media with C2PA compatibility

### Contributing Examples

Examples are crucial for adoption. Good examples include:

- **Real-world use case** - Not toy examples
- **Complete workflow** - Show full provenance chain
- **Comments** - Explain design decisions
- **Validation** - Must pass `gg validate`

Place examples in `examples/` directory with descriptive names.

## Release Process

Releases are handled by maintainers. The process includes:

1. Version bump in `pyproject.toml`
2. Update CHANGELOG.md
3. Create GitHub release
4. Publish to PyPI

## Questions?

If you have questions not covered here:
- Open a GitHub Discussion
- Reach out to maintainers
- Check the FAQ.md

---

Thank you for contributing to GenesisGraph! Your efforts help build infrastructure for trust in an increasingly automated world. 🚀
