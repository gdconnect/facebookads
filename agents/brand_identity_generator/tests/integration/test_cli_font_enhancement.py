#!/usr/bin/env python3
"""
Integration Tests for CLI Font Enhancement Workflow

These tests verify end-to-end font selection integration with the existing CLI.
They will initially fail since the implementation doesn't exist yet (TDD approach).
"""

import pytest
import sys
import json
import subprocess
import tempfile
import os
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCLIFontEnhancement:
    """Integration tests for font selection in CLI enhancement workflow."""

    @pytest.fixture
    def sample_brand_file(self):
        """Create a temporary brand file for testing."""
        content = """# Test Brand

**Primary Color**: #2563eb
**Brand Voice**: professional, modern, trustworthy
**Target Audience**: enterprise decision makers
**Industry**: Technology

## About
A technology company focused on providing reliable software solutions for businesses.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            yield f.name
        os.unlink(f.name)

    @pytest.fixture
    def sample_brand_with_existing_font(self):
        """Create a brand file that already has typography specified."""
        content = """# Brand with Existing Typography

**Primary Color**: #2563eb
**Font Family**: "Custom Corporate Font"
**Typography**: Existing font specification
**Brand Voice**: professional
**Target Audience**: corporate clients

## Typography Guidelines
We use our custom corporate font for all communications.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            yield f.name
        os.unlink(f.name)

    def test_cli_enhancement_includes_typography_automatically(self, sample_brand_file):
        """Test that font selection is automatically included in enhancement workflow."""
        pytest.fail("Test should fail initially - implement after CLI integration")

        # Run enhancement command
        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance",
            "--enhancement-level", "moderate"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0, f"CLI command failed: {result.stderr}"

        # Parse output JSON
        output_data = json.loads(result.stdout)

        # Contract: should include typography section
        assert "typography" in output_data, "Enhancement output should include typography section"
        typography = output_data["typography"]

        assert "primary_font" in typography, "Typography should include primary font"
        primary_font = typography["primary_font"]

        # Verify font structure
        assert "google_font" in primary_font, "Primary font should include Google Font data"
        assert "confidence_score" in primary_font, "Primary font should include confidence score"
        assert "rationale" in primary_font, "Primary font should include rationale"

        # Verify Google Font structure
        google_font = primary_font["google_font"]
        assert "family" in google_font, "Google Font should include family name"
        assert "category" in google_font, "Google Font should include category"

    def test_cli_enhancement_preserves_existing_functionality(self, sample_brand_file):
        """Test that font enhancement doesn't break existing color enhancement."""
        pytest.fail("Test should fail initially - implement after backward compatibility")

        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0
        output_data = json.loads(result.stdout)

        # Contract: existing functionality should still work
        assert "colorPalette" in output_data, "Color enhancement should still work"
        assert "enhancement_metadata" in output_data, "Enhancement metadata should be present"

        # New typography functionality should be added
        assert "typography" in output_data, "Typography enhancement should be added"

    def test_cli_enhancement_respects_existing_typography(self, sample_brand_with_existing_font):
        """Test that existing typography specifications are preserved."""
        pytest.fail("Test should fail initially - implement after typography preservation")

        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_with_existing_font,
            "--enhance"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0
        output_data = json.loads(result.stdout)

        # Contract: should preserve existing typography
        if "typography" in output_data:
            # Should not override existing font specifications
            # or should note that existing typography was preserved
            enhancement_metadata = output_data.get("enhancement_metadata", {})
            assert "typography_preserved" in enhancement_metadata or \
                   "Custom Corporate Font" in str(output_data), \
                   "Existing typography should be preserved"

    def test_cli_enhancement_different_levels_affect_typography(self, sample_brand_file):
        """Test that different enhancement levels produce different typography complexity."""
        pytest.fail("Test should fail initially - implement after enhancement level integration")

        # Test minimal enhancement
        result_minimal = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance",
            "--enhancement-level", "minimal"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result_minimal.returncode == 0
        minimal_data = json.loads(result_minimal.stdout)

        # Test comprehensive enhancement
        result_comprehensive = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance",
            "--enhancement-level", "comprehensive"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result_comprehensive.returncode == 0
        comprehensive_data = json.loads(result_comprehensive.stdout)

        # Contract: comprehensive should have more detailed typography
        minimal_typography = minimal_data.get("typography", {})
        comprehensive_typography = comprehensive_data.get("typography", {})

        # Count typography elements
        minimal_elements = len([k for k, v in minimal_typography.items() if v is not None])
        comprehensive_elements = len([k for k, v in comprehensive_typography.items() if v is not None])

        assert comprehensive_elements >= minimal_elements, \
            "Comprehensive enhancement should have more typography elements"

    def test_cli_enhancement_with_debug_shows_font_selection_process(self, sample_brand_file):
        """Test that debug mode shows font selection process details."""
        pytest.fail("Test should fail initially - implement after debug integration")

        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance",
            "--debug"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0

        # Contract: debug output should show font selection process
        debug_output = result.stderr
        font_related_keywords = [
            "font", "typography", "Google Fonts", "personality", "selection"
        ]

        found_keywords = [keyword for keyword in font_related_keywords
                         if keyword.lower() in debug_output.lower()]

        assert len(found_keywords) >= 2, \
            f"Debug output should mention font selection process. Found: {found_keywords}"

    def test_cli_enhancement_with_different_llm_providers(self, sample_brand_file):
        """Test that font selection works with different LLM providers."""
        pytest.fail("Test should fail initially - implement after LLM provider integration")

        providers = ["openai", "anthropic", "local"]

        for provider in providers:
            result = subprocess.run([
                "python", "brand_identity_generator.py",
                sample_brand_file,
                "--enhance",
                "--llm-provider", provider
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            assert result.returncode == 0, f"Enhancement failed with provider {provider}: {result.stderr}"

            output_data = json.loads(result.stdout)

            # Contract: typography should be included regardless of LLM provider
            assert "typography" in output_data, f"Typography missing with provider {provider}"

            # Enhancement metadata should record the provider used
            metadata = output_data.get("enhancement_metadata", {})
            assert metadata.get("llm_provider") == provider

    def test_cli_enhancement_session_management_includes_typography(self, sample_brand_file):
        """Test that session save/load includes typography state."""
        pytest.fail("Test should fail initially - implement after session integration")

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as session_file:
            session_path = session_file.name

        try:
            # Run enhancement with session save
            result = subprocess.run([
                "python", "brand_identity_generator.py",
                sample_brand_file,
                "--enhance",
                "--save-session", session_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            assert result.returncode == 0

            # Verify session file was created and contains typography
            assert os.path.exists(session_path), "Session file should be created"

            with open(session_path, 'r') as f:
                session_data = json.load(f)

            # Contract: session should include typography data
            assert "result" in session_data
            result_data = session_data["result"]
            assert "typography" in result_data, "Session should preserve typography data"

            # Test session loading
            load_result = subprocess.run([
                "python", "brand_identity_generator.py",
                "--load-session", session_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            assert load_result.returncode == 0
            loaded_data = json.loads(load_result.stdout)

            # Contract: loaded session should include typography
            assert "typography" in loaded_data, "Loaded session should include typography"

        finally:
            if os.path.exists(session_path):
                os.unlink(session_path)

    def test_cli_enhancement_error_handling_for_font_failures(self, sample_brand_file):
        """Test CLI behavior when font selection fails."""
        pytest.fail("Test should fail initially - implement after error handling integration")

        # Mock Google Fonts API failure by setting invalid API key
        env = os.environ.copy()
        env['GOOGLE_FONTS_API_KEY'] = 'invalid_key'

        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance"
        ], capture_output=True, text=True, env=env, cwd=Path(__file__).parent.parent.parent)

        # Contract: should not crash, should continue with fallbacks
        assert result.returncode == 0, "CLI should not crash on font API failure"

        output_data = json.loads(result.stdout)

        # Should still include color enhancement
        assert "colorPalette" in output_data, "Color enhancement should continue working"

        # Typography might be minimal or include fallback fonts
        if "typography" in output_data:
            metadata = output_data.get("enhancement_metadata", {})
            # Should indicate that font selection had issues
            assert "typography_fallback" in metadata or \
                   "font_selection_error" in metadata, \
                   "Should indicate font selection issues"

    def test_cli_enhancement_output_format_consistency(self, sample_brand_file):
        """Test that typography enhancement maintains output format consistency."""
        pytest.fail("Test should fail initially - implement after output format integration")

        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0
        output_data = json.loads(result.stdout)

        # Contract: should maintain existing top-level structure
        expected_top_level_keys = ["brandName", "colorPalette", "enhancement_metadata"]
        for key in expected_top_level_keys:
            assert key in output_data, f"Expected top-level key '{key}' missing"

        # Typography should be a new top-level section
        assert "typography" in output_data, "Typography should be top-level section"

        # Typography section should follow consistent structure
        typography = output_data["typography"]
        if "primary_font" in typography:
            primary_font = typography["primary_font"]
            expected_font_keys = ["google_font", "confidence_score", "rationale"]
            for key in expected_font_keys:
                assert key in primary_font, f"Expected font key '{key}' missing"

    def test_cli_enhancement_performance_with_typography(self, sample_brand_file):
        """Test that typography enhancement completes within reasonable time."""
        pytest.fail("Test should fail initially - implement after performance optimization")

        import time

        start_time = time.time()
        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        end_time = time.time()

        assert result.returncode == 0
        execution_time = end_time - start_time

        # Contract: should complete within reasonable time (15 seconds including startup)
        assert execution_time < 15.0, f"Enhancement took {execution_time:.2f}s, should be <15s"

        output_data = json.loads(result.stdout)
        if "enhancement_metadata" in output_data:
            metadata = output_data["enhancement_metadata"]
            if "processing_time" in metadata:
                processing_time = metadata["processing_time"]
                # Core processing should be much faster
                assert processing_time < 10.0, f"Core processing took {processing_time:.2f}s, should be <10s"