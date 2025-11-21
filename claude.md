# Claude Code Guide for GenesisGraph

This document provides guidance for working with the GenesisGraph codebase using Claude Code.

## Available Tools

### Progressive Reveal CLI

Located in `tools/progressive-reveal-cli/`, this is a powerful command-line tool for exploring files at different levels of detail. It's particularly useful when analyzing large configuration files, data files, or complex code files in the GenesisGraph repository.

#### Installation

```bash
cd tools/progressive-reveal-cli
pip install -e .
```

#### Usage

The tool provides 4 progressive levels of file exploration:

**Level 0: Metadata** - Quick overview of file characteristics
```bash
reveal path/to/file.yaml
```
Shows: filename, type, size, modification date, line count, SHA256 hash

**Level 1: Structure** - Structural synopsis without content
```bash
reveal path/to/file.yaml --level 1
```
For different file types, shows:
- YAML/JSON: Top-level keys, nesting depth, object/array counts
- Python: Imports, classes, functions, top-level assignments
- Markdown: Headings hierarchy, paragraph/code block/list counts
- Text: Line count, word count, estimated type

**Level 2: Preview** - Content preview with key sections
```bash
reveal path/to/file.py --level 2
```
Shows a condensed view of important content (e.g., class/function signatures, docstrings)

**Level 3: Full Content** - Complete file content with pagination
```bash
reveal path/to/file.md --level 3 --page-size 50
```
Full file content with configurable page size

#### Filtering with Grep

All levels support regex-based filtering:

```bash
# Find specific patterns in structure
reveal config.yaml --level 1 --grep "database"

# Preview with context around matches
reveal app.py --level 2 --grep "class" --context 2

# Full content filtered by pattern
reveal README.md --level 3 --grep "installation" --context 5
```

#### Common Workflows

**Exploring configuration files:**
```bash
# Start with metadata to understand size/type
reveal pyproject.toml

# Check structure to see all configuration sections
reveal pyproject.toml --level 1

# Preview specific sections
reveal pyproject.toml --level 2 --grep "dependencies"

# View full content when needed
reveal pyproject.toml --level 3
```

**Understanding Python modules:**
```bash
# See module structure (imports, classes, functions)
reveal genesisgraph/core.py --level 1

# Preview class/function signatures with docstrings
reveal genesisgraph/core.py --level 2

# Find specific implementations
reveal genesisgraph/core.py --level 3 --grep "def process" --context 10
```

**Analyzing documentation:**
```bash
# See document structure (headings, sections)
reveal README.md --level 1

# Preview introduction and key sections
reveal README.md --level 2

# Find specific topics
reveal README.md --level 3 --grep "API" --context 3
```

## Tips for Working with GenesisGraph

1. **Start Small**: Use `reveal` with level 0 or 1 to understand file structure before diving into full content
2. **Use Grep**: Filter large files with `--grep` to focus on relevant sections
3. **Progressive Exploration**: Follow the natural progression (metadata → structure → preview → full content)
4. **Context Lines**: Use `--context` to see code around matches for better understanding

## Repository Structure

```
genesisgraph/
├── genesisgraph/      # Main package source code
├── tests/            # Test suite
├── docs/             # Documentation
├── tools/            # Development tools (including progressive-reveal-cli)
├── examples/         # Usage examples
├── scripts/          # Build and utility scripts
└── pyproject.toml    # Project configuration
```

## Working with Claude Code

When Claude Code is exploring the GenesisGraph codebase, it can use the Progressive Reveal CLI to:
- Quickly understand file structure without reading entire files
- Filter large configuration or data files for specific sections
- Get file metadata to make informed decisions about what to analyze
- Preview code structure before making modifications

This is especially useful for large files where full content might be overwhelming or unnecessary for the task at hand.
