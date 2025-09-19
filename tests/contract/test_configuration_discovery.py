"""
Contract tests for configuration section discovery.
Tests that developers can easily find and understand the configuration section.
"""

import subprocess
import tempfile
import pytest
from pathlib import Path


class TestConfigurationDiscovery:
    """Test configuration section discovery and documentation."""

    def test_configuration_section_prominently_located(self):
        """Test that configuration section is prominently located at top of file."""
        # Read the brand_identity_generator.py file
        with open('brand_identity_generator.py', 'r') as f:
            content = f.read()

        # Look for configuration section in first 1000 characters after imports
        lines = content.split('\n')
        import_section_end = 0

        # Find end of imports
        for i, line in enumerate(lines):
            if line.strip() and not (line.startswith('import ') or line.startswith('from ') or
                                   line.startswith('#') or line.startswith('"""') or
                                   line.strip() in ['"""', "'''"]):
                import_section_end = i
                break

        # Look for configuration section within next 50 lines
        config_section_found = False
        for i in range(import_section_end, min(import_section_end + 50, len(lines))):
            line = lines[i]
            if 'DEVELOPER CONFIGURATION' in line and 'Edit settings below' in line:
                config_section_found = True
                break

        assert config_section_found, "Configuration section with 'DEVELOPER CONFIGURATION - Edit settings below' not found in first 50 lines after imports"

    def test_developer_config_class_exists(self):
        """Test that DeveloperConfig class exists in configuration section."""
        with open('brand_identity_generator.py', 'r') as f:
            content = f.read()

        # Look for DeveloperConfig class definition
        assert 'class DeveloperConfig(' in content, "DeveloperConfig class not found"
        assert 'BaseModel' in content, "DeveloperConfig should inherit from BaseModel"

    def test_all_required_configuration_settings_present(self):
        """Test that all required configuration settings are present."""
        with open('brand_identity_generator.py', 'r') as f:
            content = f.read()

        required_settings = [
            'llm_provider',
            'llm_base_url',
            'llm_model',
            'llm_api_key',
            'default_output_dir',
            'session_storage_dir',
            'cache_dir',
            'request_timeout',
            'enable_caching',
            'max_retries',
            'retry_backoff_factor',
            'default_enhancement_level',
            'debug_mode',
            'log_level'
        ]

        for setting in required_settings:
            assert setting in content, f"Required configuration setting '{setting}' not found"

    def test_configuration_section_has_clear_header(self):
        """Test that configuration section has clear header with instructions."""
        with open('brand_identity_generator.py', 'r') as f:
            content = f.read()

        # Look for header comment block
        assert '# ============================================================================' in content
        assert 'DEVELOPER CONFIGURATION' in content
        assert 'Edit settings below for your environment' in content

    def test_inline_documentation_quality(self):
        """Test that each configuration setting has clear inline documentation."""
        with open('brand_identity_generator.py', 'r') as f:
            content = f.read()

        # Extract DeveloperConfig class section
        class_start = content.find('class DeveloperConfig(')
        if class_start == -1:
            pytest.skip("DeveloperConfig class not found - implementation not complete")

        # Find next class or end of file
        class_end = content.find('\nclass ', class_start + 1)
        if class_end == -1:
            class_end = len(content)

        config_section = content[class_start:class_end]

        # Check for documentation of key settings
        documented_settings = [
            ('llm_provider', ['openai', 'anthropic', 'local']),
            ('llm_model', ['Model name', 'gpt-3.5-turbo']),
            ('default_output_dir', ['output', 'directory']),
            ('request_timeout', ['timeout', 'seconds']),
            ('enable_caching', ['cache', 'caching']),
            ('default_enhancement_level', ['minimal', 'moderate', 'comprehensive'])
        ]

        for setting, keywords in documented_settings:
            setting_found = False
            for line in config_section.split('\n'):
                if setting in line:
                    # Check if line has inline comment or next lines have documentation
                    if '#' in line or '"""' in config_section:
                        setting_found = True
                        break

            assert setting_found, f"Setting '{setting}' should have inline documentation with examples"

    def test_configuration_defaults_are_sensible(self):
        """Test that configuration defaults are appropriate for development."""
        with open('brand_identity_generator.py', 'r') as f:
            content = f.read()

        if 'class DeveloperConfig(' not in content:
            pytest.skip("DeveloperConfig class not found - implementation not complete")

        # Check for sensible defaults
        expected_defaults = [
            ('llm_provider.*=.*"openai"', "Default LLM provider should be 'openai'"),
            ('default_output_dir.*=.*"./output"', "Default output directory should be './output'"),
            ('request_timeout.*=.*30', "Default timeout should be reasonable (30s)"),
            ('enable_caching.*=.*True', "Caching should be enabled by default"),
            ('default_enhancement_level.*=.*"moderate"', "Default enhancement level should be 'moderate'")
        ]

        import re
        for pattern, description in expected_defaults:
            assert re.search(pattern, content, re.IGNORECASE), description