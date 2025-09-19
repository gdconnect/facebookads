"""
Contract tests for backward compatibility.
Tests that existing CLI usage patterns work unchanged with configuration system.
"""

import subprocess
import tempfile
import pytest
import json
import os
from pathlib import Path


class TestBackwardCompatibility:
    """Test backward compatibility scenarios."""

    def test_existing_cli_commands_work_unchanged(self):
        """Test that all existing CLI commands work exactly as before."""
        # Create temporary brand file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Brand Overview
Brand Name: TestBrand
Description: A test brand

# Visual Identity / Colors
Primary: professional blue
Secondary: energetic orange

# Brand Personality
Traits: professional, innovative
""")
            input_file = f.name

        try:
            # Test basic enhancement
            result = subprocess.run([
                'python', 'brand_identity_generator.py',
                input_file, '--enhance'
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"Basic enhancement failed: {result.stderr}"
            output = json.loads(result.stdout)
            assert 'enhancement_metadata' in output
            assert 'colorPalette' in output

            # Test gap analysis
            result = subprocess.run([
                'python', 'brand_identity_generator.py',
                input_file, '--analyze-gaps'
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"Gap analysis failed: {result.stderr}"
            output = json.loads(result.stdout)
            assert 'gap_analysis' in output

            # Test provider switching
            result = subprocess.run([
                'python', 'brand_identity_generator.py',
                input_file, '--enhance', '--llm-provider', 'anthropic'
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"Provider switching failed: {result.stderr}"
            output = json.loads(result.stdout)
            assert output['enhancement_metadata']['llm_provider'] == 'anthropic'

            # Test enhancement levels
            result = subprocess.run([
                'python', 'brand_identity_generator.py',
                input_file, '--enhance', '--enhancement-level', 'comprehensive'
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"Enhancement level failed: {result.stderr}"
            output = json.loads(result.stdout)
            assert output['enhancement_metadata']['enhancement_level'] == 'comprehensive'

        finally:
            os.unlink(input_file)

    def test_cli_argument_precedence_over_configuration(self):
        """Test that CLI arguments override configuration values."""
        # This test will initially pass (no config to override)
        # After configuration implementation, should test precedence
        if 'DeveloperConfig' not in open('brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - precedence testing needs config")

        # Test CLI argument precedence over configuration defaults
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Brand Overview
Brand Name: TestBrand
Description: A test brand

# Visual Identity / Colors
Primary: professional blue
""")
            input_file = f.name

        try:
            # Test that CLI --llm-provider overrides configuration default
            result = subprocess.run([
                'python', 'brand_identity_generator.py',
                input_file, '--enhance', '--llm-provider', 'anthropic'
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"CLI override test failed: {result.stderr}"
            output = json.loads(result.stdout)

            # Verify that CLI argument was used (anthropic) over default (openai)
            assert output['enhancement_metadata']['llm_provider'] == 'anthropic'

        finally:
            os.unlink(input_file)

    def test_environment_variable_integration(self):
        """Test that environment variables work with configuration system."""
        # Test that existing environment variable usage still works
        original_key = os.environ.get('OPENAI_API_KEY')
        test_key = 'test-key-12345'

        try:
            os.environ['OPENAI_API_KEY'] = test_key

            # Create temporary brand file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write("""# Brand Overview
Brand Name: TestBrand

# Visual Identity / Colors
Primary: blue
""")
                input_file = f.name

            try:
                result = subprocess.run([
                    'python', 'brand_identity_generator.py',
                    input_file, '--enhance'
                ], capture_output=True, text=True)

                # Should work regardless of configuration system status
                assert result.returncode == 0, f"Environment variable handling failed: {result.stderr}"

            finally:
                os.unlink(input_file)

        finally:
            if original_key:
                os.environ['OPENAI_API_KEY'] = original_key
            elif 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']

    def test_output_format_unchanged(self):
        """Test that output format remains exactly the same."""
        # Create temporary brand file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Brand Overview
Brand Name: TestBrand

# Visual Identity / Colors
Primary: professional blue
""")
            input_file = f.name

        try:
            result = subprocess.run([
                'python', 'brand_identity_generator.py',
                input_file, '--enhance'
            ], capture_output=True, text=True)

            assert result.returncode == 0
            output = json.loads(result.stdout)

            # Verify expected output structure hasn't changed
            assert 'brandName' in output
            assert 'colorPalette' in output
            assert 'enhancement_metadata' in output
            assert 'workflow_id' in output['enhancement_metadata']
            assert 'processing_time' in output['enhancement_metadata']

        finally:
            os.unlink(input_file)

    def test_help_text_shows_configuration_defaults(self):
        """Test that help text shows current configuration defaults."""
        result = subprocess.run([
            'python', 'brand_identity_generator.py', '--help'
        ], capture_output=True, text=True)

        assert result.returncode == 0
        help_text = result.stdout

        # Basic help text should be present
        assert 'brand_identity_generator.py' in help_text
        assert '--enhance' in help_text
        assert '--llm-provider' in help_text

        # After configuration implementation, should show config defaults
        if 'DeveloperConfig' not in open('brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - help text enhancement pending")

        # When implemented, should test config defaults in help
        pytest.fail("Test should verify help text shows configuration defaults")

    def test_session_save_load_unchanged(self):
        """Test that session save/load functionality works unchanged."""
        # Create temporary brand file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Brand Overview
Brand Name: TestBrand

# Visual Identity / Colors
Primary: professional blue
""")
            input_file = f.name

        session_file = 'test_session.json'

        try:
            # Test session save
            result = subprocess.run([
                'python', 'brand_identity_generator.py',
                input_file, '--enhance', '--save-session', session_file
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"Session save failed: {result.stderr}"
            assert os.path.exists(session_file), "Session file was not created"

            # Test session load
            result = subprocess.run([
                'python', 'brand_identity_generator.py',
                '--load-session', session_file
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"Session load failed: {result.stderr}"
            output = json.loads(result.stdout)
            assert 'enhancement_metadata' in output

        finally:
            os.unlink(input_file)
            if os.path.exists(session_file):
                os.unlink(session_file)

    def test_error_handling_unchanged(self):
        """Test that existing error handling behaviors are preserved."""
        # Test missing input file
        result = subprocess.run([
            'python', 'brand_identity_generator.py',
            'nonexistent.md', '--enhance'
        ], capture_output=True, text=True)

        assert result.returncode != 0, "Should fail with nonexistent input file"

        # Test invalid enhancement level
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Brand Overview\nBrand Name: Test")
            input_file = f.name

        try:
            result = subprocess.run([
                'python', 'brand_identity_generator.py',
                input_file, '--enhance', '--enhancement-level', 'invalid'
            ], capture_output=True, text=True)

            assert result.returncode != 0, "Should fail with invalid enhancement level"

        finally:
            os.unlink(input_file)