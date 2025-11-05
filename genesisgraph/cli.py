#!/usr/bin/env python3
"""
GenesisGraph CLI

Command-line interface for GenesisGraph validation and verification.
"""

import sys
from pathlib import Path
from typing import Optional

try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False

from .validator import GenesisGraphValidator
from . import __version__


if CLICK_AVAILABLE:
    @click.group()
    @click.version_option(version=__version__)
    def cli():
        """GenesisGraph: Universal Verifiable Process Provenance"""
        pass

    @cli.command()
    @click.argument('file_path', type=click.Path(exists=True))
    @click.option('--schema', '-s', type=click.Path(exists=True),
                  help='Path to JSON Schema file')
    @click.option('--verbose', '-v', is_flag=True,
                  help='Verbose output')
    def validate(file_path: str, schema: Optional[str], verbose: bool):
        """Validate a GenesisGraph document"""

        validator = GenesisGraphValidator(schema_path=schema)
        result = validator.validate_file(file_path)

        if verbose or not result.is_valid:
            click.echo(result.format_report())
        elif result.is_valid:
            click.echo("✓ Validation PASSED")

        if result.warnings and verbose:
            for warning in result.warnings:
                click.echo(f"⚠ {warning}", err=True)

        sys.exit(0 if result.is_valid else 1)

    @cli.command()
    @click.argument('file_path', type=click.Path(exists=True))
    def info(file_path: str):
        """Display information about a GenesisGraph document"""
        import yaml

        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            click.echo(f"❌ Error loading file: {e}", err=True)
            sys.exit(1)

        click.echo(f"GenesisGraph Document: {file_path}")
        click.echo(f"Spec version: {data.get('spec_version', 'UNKNOWN')}")
        click.echo(f"Profile: {data.get('profile', 'NONE')}")

        entities = data.get('entities', [])
        operations = data.get('operations', [])
        tools = data.get('tools', [])

        click.echo(f"\nContent:")
        click.echo(f"  Entities: {len(entities)}")
        click.echo(f"  Operations: {len(operations)}")
        click.echo(f"  Tools: {len(tools)}")

        # Count operation types
        if operations:
            op_types = {}
            for op in operations:
                op_type = op.get('type', 'unknown')
                op_types[op_type] = op_types.get(op_type, 0) + 1

            click.echo(f"\nOperation types:")
            for op_type, count in sorted(op_types.items()):
                click.echo(f"  {op_type}: {count}")

    @cli.command()
    def version():
        """Show version information"""
        click.echo(f"GenesisGraph v{__version__}")
        click.echo("https://github.com/genesisgraph/genesisgraph")

else:
    # Fallback CLI without click
    def main():
        """Simple CLI without click"""
        if len(sys.argv) < 2:
            print("GenesisGraph CLI")
            print(f"Version: {__version__}")
            print("\nUsage:")
            print("  python -m genesisgraph.cli validate <file.gg.yaml>")
            print("  python -m genesisgraph.cli info <file.gg.yaml>")
            print("\nInstall 'click' for better CLI experience:")
            print("  pip install click")
            sys.exit(1)

        command = sys.argv[1]

        if command == 'validate':
            if len(sys.argv) < 3:
                print("Error: Missing file path")
                sys.exit(1)

            file_path = sys.argv[2]
            validator = GenesisGraphValidator()
            result = validator.validate_file(file_path)

            print(result.format_report())
            sys.exit(0 if result.is_valid else 1)

        elif command == 'info':
            if len(sys.argv) < 3:
                print("Error: Missing file path")
                sys.exit(1)

            import yaml
            file_path = sys.argv[2]

            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
            except Exception as e:
                print(f"❌ Error loading file: {e}")
                sys.exit(1)

            print(f"GenesisGraph Document: {file_path}")
            print(f"Spec version: {data.get('spec_version', 'UNKNOWN')}")
            print(f"Profile: {data.get('profile', 'NONE')}")
            print(f"\nEntities: {len(data.get('entities', []))}")
            print(f"Operations: {len(data.get('operations', []))}")
            print(f"Tools: {len(data.get('tools', []))}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)


def main():
    """Entry point for CLI"""
    if CLICK_AVAILABLE:
        cli()
    else:
        # Use fallback
        if len(sys.argv) < 2:
            print("GenesisGraph CLI")
            print(f"Version: {__version__}")
            print("\nUsage:")
            print("  gg validate <file.gg.yaml>")
            print("  gg info <file.gg.yaml>")
            print("\nInstall 'click' and 'rich' for better experience:")
            print("  pip install click rich")
            sys.exit(1)

        command = sys.argv[1]

        if command == 'validate':
            if len(sys.argv) < 3:
                print("Error: Missing file path")
                sys.exit(1)

            file_path = sys.argv[2]
            validator = GenesisGraphValidator()
            result = validator.validate_file(file_path)

            print(result.format_report())
            sys.exit(0 if result.is_valid else 1)

        elif command == 'info':
            if len(sys.argv) < 3:
                print("Error: Missing file path")
                sys.exit(1)

            import yaml
            file_path = sys.argv[2]

            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
            except Exception as e:
                print(f"❌ Error loading file: {e}")
                sys.exit(1)

            print(f"GenesisGraph Document: {file_path}")
            print(f"Spec version: {data.get('spec_version', 'UNKNOWN')}")
            print(f"Profile: {data.get('profile', 'NONE')}")
            print(f"\nEntities: {len(data.get('entities', []))}")
            print(f"Operations: {len(data.get('operations', []))}")
            print(f"Tools: {len(data.get('tools', []))}")

        elif command == 'version':
            print(f"GenesisGraph v{__version__}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)


if __name__ == '__main__':
    main()
