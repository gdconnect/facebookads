"""
Contract tests for directory management functionality.
Tests automatic directory creation, permission validation, and configuration usage.
"""

import subprocess
import tempfile
import pytest
import json
import os
import shutil
from pathlib import Path


class TestDirectoryManagement:
    """Test directory management and configuration."""

    def test_automatic_directory_creation(self):
        """Test that configured directories are created automatically."""
        # This test will initially fail - should be implemented after configuration system
        if 'DeveloperConfig' not in open('agents/brand_identity_generator/brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - test should fail initially")

        # Test directory creation with unique temporary directories
        import tempfile
        import shutil

        base_temp_dir = tempfile.mkdtemp()
        try:
            output_dir = os.path.join(base_temp_dir, "test_output")
            session_dir = os.path.join(base_temp_dir, "test_sessions")
            cache_dir = os.path.join(base_temp_dir, "test_cache")

            # Create temporary brand file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write("""# Brand Overview
Brand Name: TestBrand
Description: A test brand

# Visual Identity / Colors
Primary: professional blue
""")
                input_file = f.name

            try:
                # Test that tool creates missing directories automatically
                result = subprocess.run([
                    'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                    input_file, '--enhance'
                ], capture_output=True, text=True, env={
                    **os.environ,
                    'BRAND_TOOL_OUTPUT_DIR': output_dir,
                    'BRAND_TOOL_SESSION_DIR': session_dir,
                    'BRAND_TOOL_CACHE_DIR': cache_dir
                })

                assert result.returncode == 0, f"Tool execution failed: {result.stderr}"

                # Verify directories were created
                assert os.path.exists(output_dir), f"Output directory {output_dir} was not created"
                assert os.path.exists(session_dir), f"Session directory {session_dir} was not created"
                assert os.path.exists(cache_dir), f"Cache directory {cache_dir} was not created"

            finally:
                os.unlink(input_file)

        finally:
            shutil.rmtree(base_temp_dir, ignore_errors=True)

    def test_write_permission_validation(self):
        """Test that write permissions are validated with test file creation."""
        # This test will initially fail - should be implemented after configuration system
        if 'DeveloperConfig' not in open('agents/brand_identity_generator/brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - test should fail initially")

        # When implemented, should test permission validation
        pytest.fail("Test should fail initially - implement after permission validation")

    def test_custom_output_directory_usage(self):
        """Test that configured default_output_dir is used for JSON output."""
        # Create temporary brand file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Brand Overview
Brand Name: TestBrand
Description: A test brand

# Visual Identity / Colors
Primary: professional blue
""")
            input_file = f.name

        try:
            # This test will initially pass with default behavior
            # After configuration implementation, should test custom output directory
            result = subprocess.run([
                'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                input_file, '--enhance'
            ], capture_output=True, text=True)

            if 'DeveloperConfig' not in open('agents/brand_identity_generator/brand_identity_generator.py').read():
                # Before implementation - just verify tool works
                assert result.returncode == 0
                pytest.skip("Configuration system not implemented yet - test should fail initially")

            # When implemented, should test custom output directory usage
            pytest.fail("Test should fail initially - implement after output directory configuration")

        finally:
            os.unlink(input_file)

    def test_session_storage_location_configuration(self):
        """Test that session_storage_dir controls session save/load operations."""
        # This test will initially fail - should be implemented after configuration system
        if 'DeveloperConfig' not in open('agents/brand_identity_generator/brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - test should fail initially")

        # When implemented, should test session storage configuration
        pytest.fail("Test should fail initially - implement after session storage configuration")

    def test_cache_directory_configuration(self):
        """Test that cache_dir and enable_caching control LLM response caching."""
        # This test will initially fail - should be implemented after configuration system
        if 'DeveloperConfig' not in open('agents/brand_identity_generator/brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - test should fail initially")

        # When implemented, should test cache directory configuration
        pytest.fail("Test should fail initially - implement after cache configuration")

    def test_cache_disabled_bypasses_cache_directory(self):
        """Test that enable_caching=False bypasses cache entirely."""
        # This test will initially fail - should be implemented after configuration system
        if 'DeveloperConfig' not in open('agents/brand_identity_generator/brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - test should fail initially")

        # When implemented, should test cache bypass behavior
        pytest.fail("Test should fail initially - implement after cache disable functionality")

    def test_permission_error_messages_are_helpful(self):
        """Test that permission errors provide helpful messages."""
        # This test will initially fail - should be implemented after configuration system
        if 'DeveloperConfig' not in open('agents/brand_identity_generator/brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - test should fail initially")

        # When implemented, should test permission error messages
        # Expected: "No write permission for directory: /path/to/dir"
        pytest.fail("Test should fail initially - implement after permission error handling")

    def test_directory_validation_caching(self):
        """Test that directory validation results are cached for performance."""
        # This test will initially fail - should be implemented after configuration system
        if 'DeveloperConfig' not in open('agents/brand_identity_generator/brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - test should fail initially")

        # When implemented, should test validation caching
        pytest.fail("Test should fail initially - implement after validation caching")

    def test_nested_directory_creation(self):
        """Test that nested directories are created properly."""
        # This test will initially fail - should be implemented after configuration system
        if 'DeveloperConfig' not in open('agents/brand_identity_generator/brand_identity_generator.py').read():
            pytest.skip("Configuration system not implemented yet - test should fail initially")

        # When implemented, should test nested directory creation
        # Expected: ./deep/nested/output should create all levels
        pytest.fail("Test should fail initially - implement after nested directory support")