# Progressive Reveal CLI

A powerful command-line tool for exploring files at different levels of detail. Progressive Reveal CLI allows you to understand file contents incrementally, from high-level metadata to detailed content, with smart type-aware analysis for YAML, JSON, Markdown, and Python files.

## Features

- **4 Progressive Levels**: Metadata → Structure → Preview → Full Content
- **Smart File Type Detection**: Automatic detection and specialized handling for YAML, JSON, Markdown, Python
- **Grep Filtering**: Regex-based filtering with context support across all levels
- **Type-Aware Analysis**:
  - YAML: Top-level keys, nesting depth, anchors/aliases
  - JSON: Object/array counts, max depth, value types
  - Markdown: Headings, paragraphs, code blocks
  - Python: Imports, classes, functions, docstrings
- **Paged Output**: Configurable page size for large files
- **Binary Detection**: Safe handling of binary files
- **UTF-8 Support**: Proper Unicode handling throughout

## Installation

```bash
# Install from the tools directory
cd tools/progressive-reveal-cli
pip install -e .
```

## Quick Start

```bash
# View metadata
reveal myfile.yaml

# View structure
reveal myfile.json --level 1

# View preview with filtering
reveal myfile.py --level 2 --grep "class"

# View full content with paging
reveal myfile.md --level 3 --page-size 50
```

## Usage with Claude Code

This tool is particularly useful when working with Claude Code to explore large codebases or configuration files incrementally:

```bash
# Start with metadata to understand file size and type
reveal config.yaml

# Then view structure to see top-level keys
reveal config.yaml --level 1

# Preview specific sections with grep
reveal config.yaml --level 2 --grep "database"

# Finally view full content when needed
reveal config.yaml --level 3
```

## Command Line Options

```
reveal <file> [options]

Options:
  --level <0-3>           Revelation level (default: 0)
                          0 = metadata
                          1 = structural synopsis
                          2 = content preview
                          3 = full content (paged)

  --grep, -m <pattern>    Filter pattern (regex)
  --context, -C <n>       Context lines around matches (default: 0)
  --grep-case-sensitive   Use case-sensitive grep matching
  --page-size <n>         Page size for level 3 (default: 120)
  --force                 Force read of large or binary files
```

## Examples

```bash
# View file metadata
reveal config.yaml

# View YAML structure
reveal config.yaml --level 1

# Preview Python file
reveal app.py --level 2

# View full content with grep
reveal app.py --level 3 --grep "class" --context 2

# Force read large file
reveal large.log --level 3 --force
```

## License

MIT License
