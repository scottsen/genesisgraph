"""Tests for GenesisGraph CLI"""

import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import yaml

# Import CLI module to test
from genesisgraph import cli
from genesisgraph.cli import CLICK_AVAILABLE


class TestClickCLI:
    """Test Click-based CLI commands"""

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_validate_command_success(self, valid_gg_file):
        """Test validate command with valid file"""
        from click.testing import CliRunner
        runner = CliRunner()

        result = runner.invoke(cli.cli, ['validate', valid_gg_file])

        assert result.exit_code == 0
        assert '✓' in result.output or 'PASSED' in result.output

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_validate_command_failure(self, invalid_gg_file):
        """Test validate command with invalid file"""
        from click.testing import CliRunner
        runner = CliRunner()

        result = runner.invoke(cli.cli, ['validate', invalid_gg_file])

        assert result.exit_code == 1
        assert 'spec_version' in result.output

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_validate_command_verbose(self, valid_gg_file):
        """Test validate command with verbose flag"""
        from click.testing import CliRunner
        runner = CliRunner()

        result = runner.invoke(cli.cli, ['validate', '--verbose', valid_gg_file])

        assert result.exit_code == 0
        assert 'Validation' in result.output or '✓' in result.output

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_validate_command_with_schema(self, valid_gg_file):
        """Test validate command with custom schema"""
        from click.testing import CliRunner
        runner = CliRunner()

        # Create a basic JSON schema
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["spec_version"],
            "properties": {
                "spec_version": {"type": "string"}
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema, f)
            schema_file = f.name

        try:
            result = runner.invoke(cli.cli, ['validate', '--schema', schema_file, valid_gg_file])
            assert result.exit_code == 0
        finally:
            os.unlink(schema_file)

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_validate_command_nonexistent_file(self):
        """Test validate command with nonexistent file"""
        from click.testing import CliRunner
        runner = CliRunner()

        result = runner.invoke(cli.cli, ['validate', 'nonexistent.gg.yaml'])

        # Click will fail before our code runs due to Path(exists=True)
        assert result.exit_code != 0

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_info_command_success(self, info_gg_file):
        """Test info command with valid file"""
        from click.testing import CliRunner
        runner = CliRunner()

        result = runner.invoke(cli.cli, ['info', info_gg_file])

        assert result.exit_code == 0
        assert '0.1.0' in result.output
        assert 'gg-ai-basic-v1' in result.output
        assert 'Entities: 1' in result.output
        assert 'Operations: 2' in result.output
        assert 'Tools: 2' in result.output

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_info_command_with_operation_types(self, info_gg_file):
        """Test info command displays operation types"""
        from click.testing import CliRunner
        runner = CliRunner()

        result = runner.invoke(cli.cli, ['info', info_gg_file])

        assert result.exit_code == 0
        assert 'Operation types:' in result.output
        assert 'transformation' in result.output
        assert 'inference' in result.output

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_info_command_nonexistent_file(self):
        """Test info command with nonexistent file"""
        from click.testing import CliRunner
        runner = CliRunner()

        result = runner.invoke(cli.cli, ['info', 'nonexistent.gg.yaml'])

        assert result.exit_code != 0

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_info_command_invalid_yaml(self):
        """Test info command with invalid YAML"""
        from click.testing import CliRunner
        runner = CliRunner()

        # Create an invalid YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [[[")
            invalid_file = f.name

        try:
            result = runner.invoke(cli.cli, ['info', invalid_file])
            assert result.exit_code == 1
            assert 'Error' in result.output or 'error' in result.output
        finally:
            os.unlink(invalid_file)

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_version_command(self):
        """Test version command"""
        from click.testing import CliRunner
        runner = CliRunner()

        result = runner.invoke(cli.cli, ['version'])

        assert result.exit_code == 0
        assert 'GenesisGraph' in result.output
        assert 'github.com/genesisgraph/genesisgraph' in result.output

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_cli_version_option(self):
        """Test --version option on main CLI"""
        from click.testing import CliRunner
        runner = CliRunner()

        result = runner.invoke(cli.cli, ['--version'])

        assert result.exit_code == 0
        # Should contain version number
        assert '0.1.0' in result.output or 'version' in result.output.lower()

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_validate_with_warnings_verbose(self, tmpdir):
        """Test validate command shows warnings in verbose mode"""
        from click.testing import CliRunner
        runner = CliRunner()

        # Create a file with invalid semver (triggers warning)
        data = {
            'spec_version': 'invalid-version',
            'tools': [],
            'entities': [],
            'operations': []
        }

        test_file = tmpdir.join('test.gg.yaml')
        with open(test_file, 'w') as f:
            yaml.dump(data, f)

        result = runner.invoke(cli.cli, ['validate', '--verbose', str(test_file)])

        # The file should pass validation but may have warnings
        assert 'semver' in result.output.lower() or 'warning' in result.output.lower()


class TestFallbackCLI:
    """Test fallback CLI without Click"""

    def test_fallback_validate_success(self, valid_gg_file, capsys):
        """Test fallback validate with valid file"""
        with patch.object(sys, 'argv', ['gg', 'validate', valid_gg_file]):
            with pytest.raises(SystemExit) as exc_info:
                # Temporarily disable click
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert 'PASSED' in captured.out or '✓' in captured.out

    def test_fallback_validate_failure(self, invalid_gg_file, capsys):
        """Test fallback validate with invalid file"""
        with patch.object(sys, 'argv', ['gg', 'validate', invalid_gg_file]):
            with pytest.raises(SystemExit) as exc_info:
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert 'spec_version' in captured.out

    def test_fallback_info_success(self, info_gg_file, capsys):
        """Test fallback info with valid file"""
        with patch.object(sys, 'argv', ['gg', 'info', info_gg_file]):
            with pytest.raises(SystemExit) as exc_info:
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert 'Spec version: 0.1.0' in captured.out  # Check spec version from document
            assert 'gg-ai-basic-v1' in captured.out

    def test_fallback_version(self, capsys):
        """Test fallback version command"""
        with patch.object(sys, 'argv', ['gg', 'version']):
            with pytest.raises(SystemExit) as exc_info:
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert 'GenesisGraph' in captured.out
            assert '0.3.0' in captured.out

    def test_fallback_no_args(self, capsys):
        """Test fallback CLI with no arguments"""
        with patch.object(sys, 'argv', ['gg']):
            with pytest.raises(SystemExit) as exc_info:
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert 'GenesisGraph CLI' in captured.out
            assert 'Usage:' in captured.out

    def test_fallback_unknown_command(self, capsys):
        """Test fallback CLI with unknown command"""
        with patch.object(sys, 'argv', ['gg', 'unknown']):
            with pytest.raises(SystemExit) as exc_info:
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert 'Unknown command' in captured.out

    def test_fallback_validate_missing_file_arg(self, capsys):
        """Test fallback validate without file argument"""
        with patch.object(sys, 'argv', ['gg', 'validate']):
            with pytest.raises(SystemExit) as exc_info:
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert 'Missing file path' in captured.out

    def test_fallback_info_missing_file_arg(self, capsys):
        """Test fallback info without file argument"""
        with patch.object(sys, 'argv', ['gg', 'info']):
            with pytest.raises(SystemExit) as exc_info:
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert 'Missing file path' in captured.out

    def test_fallback_info_invalid_yaml(self, capsys):
        """Test fallback info with invalid YAML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: [[[")
            invalid_file = f.name

        try:
            with patch.object(sys, 'argv', ['gg', 'info', invalid_file]):
                with pytest.raises(SystemExit) as exc_info:
                    with patch.object(cli, 'CLICK_AVAILABLE', False):
                        cli.main()

                assert exc_info.value.code == 1
                captured = capsys.readouterr()
                assert 'Error loading file' in captured.out
        finally:
            os.unlink(invalid_file)


class TestCLIIntegration:
    """Test CLI integration and entry points"""

    @pytest.fixture
    def valid_gg_file(self):
        """Create a temporary valid GenesisGraph file"""
        data = {
            'spec_version': '0.1.0',
            'tools': [],
            'entities': [],
            'operations': []
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gg.yaml', delete=False) as f:
            yaml.dump(data, f)
            yield f.name
        os.unlink(f.name)

    def test_main_with_click_available(self, valid_gg_file):
        """Test main() function when Click is available"""
        if not CLICK_AVAILABLE:
            pytest.skip("Click not available")

        with patch.object(sys, 'argv', ['gg', 'validate', valid_gg_file]):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()

            assert exc_info.value.code == 0

    def test_main_without_click_available(self, valid_gg_file, capsys):
        """Test main() function when Click is not available"""
        with patch.object(sys, 'argv', ['gg', 'validate', valid_gg_file]):
            with pytest.raises(SystemExit) as exc_info:
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            assert exc_info.value.code == 0

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_example_files_validate_via_cli(self):
        """Test validating example files via CLI"""
        from click.testing import CliRunner
        runner = CliRunner()

        example_files = [
            'examples/level-a-full-disclosure.gg.yaml',
            'examples/level-b-partial-envelope.gg.yaml',
            'examples/level-c-sealed-subgraph.gg.yaml'
        ]

        for example_file in example_files:
            if os.path.exists(example_file):
                result = runner.invoke(cli.cli, ['info', example_file])
                # Info should work even if validation might fail due to file refs
                assert 'spec_version' in result.output.lower() or 'Spec version' in result.output


class TestCLIEdgeCases:
    """Test CLI edge cases and error handling"""

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_validate_empty_file(self):
        """Test validate with empty file"""
        from click.testing import CliRunner
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Empty file
            empty_file = f.name

        try:
            result = runner.invoke(cli.cli, ['validate', empty_file])
            # Should fail validation
            assert result.exit_code == 1
        finally:
            os.unlink(empty_file)

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_info_minimal_document(self):
        """Test info with minimal document"""
        from click.testing import CliRunner
        runner = CliRunner()

        data = {'spec_version': '0.1.0'}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(data, f)
            test_file = f.name

        try:
            result = runner.invoke(cli.cli, ['info', test_file])
            assert result.exit_code == 0
            assert '0.1.0' in result.output
            assert 'Entities: 0' in result.output
            assert 'Operations: 0' in result.output
            assert 'Tools: 0' in result.output
        finally:
            os.unlink(test_file)

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_validate_short_flags(self):
        """Test validate with short option flags"""
        from click.testing import CliRunner
        runner = CliRunner()

        data = {'spec_version': '0.1.0', 'tools': [], 'entities': [], 'operations': []}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(data, f)
            test_file = f.name

        try:
            # Test -v for verbose
            result = runner.invoke(cli.cli, ['validate', '-v', test_file])
            assert result.exit_code == 0
        finally:
            os.unlink(test_file)

    def test_fallback_validate_nonexistent_file(self, capsys):
        """Test fallback validate with nonexistent file"""
        with patch.object(sys, 'argv', ['gg', 'validate', 'nonexistent.yaml']):
            with pytest.raises(SystemExit) as exc_info:
                with patch.object(cli, 'CLICK_AVAILABLE', False):
                    cli.main()

            # Should fail with non-zero exit code
            assert exc_info.value.code == 1


class TestCLIOutputFormats:
    """Test CLI output formatting and messages"""

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_validate_success_message_format(self):
        """Test validate success message format"""
        from click.testing import CliRunner
        runner = CliRunner()

        data = {'spec_version': '0.1.0', 'tools': [], 'entities': [], 'operations': []}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(data, f)
            test_file = f.name

        try:
            result = runner.invoke(cli.cli, ['validate', test_file])
            assert result.exit_code == 0
            # Check for success indicator
            assert '✓' in result.output or 'PASSED' in result.output
        finally:
            os.unlink(test_file)

    @pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
    def test_info_output_structure(self):
        """Test info command output structure"""
        from click.testing import CliRunner
        runner = CliRunner()

        data = {
            'spec_version': '0.1.0',
            'profile': 'test-profile',
            'tools': [{'id': 't1', 'type': 'Software'}],
            'entities': [{'id': 'e1', 'type': 'Dataset', 'version': '1.0', 'file': 'test.txt'}],
            'operations': [{'id': 'op1', 'type': 'transformation', 'inputs': [], 'outputs': []}]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(data, f)
            test_file = f.name

        try:
            result = runner.invoke(cli.cli, ['info', test_file])
            assert result.exit_code == 0

            # Check for expected structure
            assert 'Spec version: 0.1.0' in result.output
            assert 'Profile: test-profile' in result.output
            assert 'Entities: 1' in result.output
            assert 'Operations: 1' in result.output
            assert 'Tools: 1' in result.output
        finally:
            os.unlink(test_file)
