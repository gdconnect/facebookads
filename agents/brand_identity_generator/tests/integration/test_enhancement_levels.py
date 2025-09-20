#!/usr/bin/env python3
"""
Integration Tests for Enhancement Level Variations

These tests verify that different enhancement levels produce appropriate typography complexity.
They will initially fail since the implementation doesn't exist yet (TDD approach).
"""

import pytest
import sys
import json
import subprocess
import tempfile
import os
import time
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestEnhancementLevels:
    """Integration tests for enhancement level variations with typography."""

    @pytest.fixture
    def sample_brand_file(self):
        """Create a temporary brand file for testing enhancement levels."""
        content = """# Multi-Level Test Brand

**Primary Color**: #2563eb
**Brand Voice**: professional, modern, innovative, trustworthy
**Target Audience**: enterprise decision makers and technical teams
**Industry**: Technology Software
**Brand Personality**: sophisticated, reliable, cutting-edge

## About
A comprehensive technology company that provides enterprise software solutions
with a focus on innovation, reliability, and user experience. We serve both
technical teams and business decision makers.

## Values
- Innovation through technology
- Reliability in delivery
- User-centered design
- Professional excellence
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            yield f.name
        os.unlink(f.name)

    def test_minimal_enhancement_level_typography(self, sample_brand_file):
        """Test minimal enhancement level produces basic typography."""
        pytest.fail("Test should fail initially - implement after minimal level typography")

        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance",
            "--enhancement-level", "minimal"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0, f"Minimal enhancement failed: {result.stderr}"
        output_data = json.loads(result.stdout)

        # Contract: minimal should have basic typography
        assert "typography" in output_data, "Minimal enhancement should include typography"
        typography = output_data["typography"]

        # Should have at least primary font
        assert "primary_font" in typography, "Minimal should include primary font"
        assert typography["primary_font"] is not None

        # Should have basic font recommendation
        primary_font = typography["primary_font"]
        assert "google_font" in primary_font
        assert "confidence_score" in primary_font
        assert primary_font["confidence_score"] >= 0.7

        # Minimal complexity expectations
        font_count = sum(1 for key in ["primary_font", "secondary_font", "accent_font"]
                        if typography.get(key) is not None)
        assert font_count >= 1, "Minimal should have at least 1 font"
        assert font_count <= 2, "Minimal should not exceed 2 fonts"

    def test_moderate_enhancement_level_typography(self, sample_brand_file):
        """Test moderate enhancement level produces balanced typography."""
        pytest.fail("Test should fail initially - implement after moderate level typography")

        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance",
            "--enhancement-level", "moderate"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0, f"Moderate enhancement failed: {result.stderr}"
        output_data = json.loads(result.stdout)

        typography = output_data["typography"]

        # Contract: moderate should have primary + secondary fonts
        assert "primary_font" in typography
        assert typography["primary_font"] is not None

        # Should likely have secondary font for moderate level
        font_count = sum(1 for key in ["primary_font", "secondary_font", "accent_font"]
                        if typography.get(key) is not None)
        assert font_count >= 1, "Moderate should have at least 1 font"
        assert font_count <= 3, "Moderate should not exceed 3 fonts"

        # Should have typography hierarchy
        if "typography_system" in typography:
            system = typography["typography_system"]
            assert "heading_styles" in system, "Moderate should include heading styles"

            # Should have H1-H3 at minimum
            heading_styles = system["heading_styles"]
            required_headings = ["h1", "h2", "h3"]
            for heading in required_headings:
                assert heading in heading_styles, f"Moderate should include {heading} style"

    def test_comprehensive_enhancement_level_typography(self, sample_brand_file):
        """Test comprehensive enhancement level produces complete typography system."""
        pytest.fail("Test should fail initially - implement after comprehensive level typography")

        result = subprocess.run([
            "python", "brand_identity_generator.py",
            sample_brand_file,
            "--enhance",
            "--enhancement-level", "comprehensive"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0, f"Comprehensive enhancement failed: {result.stderr}"
        output_data = json.loads(result.stdout)

        typography = output_data["typography"]

        # Contract: comprehensive should have complete typography system
        assert "primary_font" in typography
        assert typography["primary_font"] is not None

        # Should have multiple fonts for comprehensive level
        font_count = sum(1 for key in ["primary_font", "secondary_font", "accent_font"]
                        if typography.get(key) is not None)
        assert font_count >= 2, "Comprehensive should have at least 2 fonts"

        # Should have complete typography hierarchy
        assert "typography_system" in typography, "Comprehensive should include complete typography system"
        system = typography["typography_system"]

        # Should have all heading levels
        assert "heading_styles" in system
        heading_styles = system["heading_styles"]
        all_headings = ["h1", "h2", "h3", "h4", "h5", "h6"]
        present_headings = [h for h in all_headings if h in heading_styles]
        assert len(present_headings) >= 4, "Comprehensive should include at least H1-H4"

        # Should have text styles
        assert "text_styles" in system
        text_styles = system["text_styles"]
        required_text_styles = ["body", "caption"]
        for style in required_text_styles:
            assert style in text_styles, f"Comprehensive should include {style} text style"

        # Should include CSS snippet
        if "css_snippet" in typography:
            css = typography["css_snippet"]
            assert len(css) > 100, "Comprehensive should have substantial CSS snippet"
            assert "@import" in css or "font-family" in css, "CSS should include font imports"

    def test_enhancement_levels_progression_typography_complexity(self, sample_brand_file):
        """Test that enhancement levels show progressive complexity increase."""
        pytest.fail("Test should fail initially - implement after level progression")

        levels = ["minimal", "moderate", "comprehensive"]
        results = {}

        # Run all enhancement levels
        for level in levels:
            result = subprocess.run([
                "python", "brand_identity_generator.py",
                sample_brand_file,
                "--enhance",
                "--enhancement-level", level
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            assert result.returncode == 0, f"Enhancement level {level} failed: {result.stderr}"
            results[level] = json.loads(result.stdout)

        # Analyze complexity progression
        complexity_metrics = {}

        for level in levels:
            typography = results[level]["typography"]
            metrics = {
                "font_count": sum(1 for key in ["primary_font", "secondary_font", "accent_font"]
                                if typography.get(key) is not None),
                "heading_count": 0,
                "text_style_count": 0,
                "css_length": 0
            }

            # Count typography system elements
            if "typography_system" in typography:
                system = typography["typography_system"]
                if "heading_styles" in system:
                    metrics["heading_count"] = len(system["heading_styles"])
                if "text_styles" in system:
                    metrics["text_style_count"] = len(system["text_styles"])

            if "css_snippet" in typography:
                metrics["css_length"] = len(typography["css_snippet"])

            complexity_metrics[level] = metrics

        # Contract: complexity should generally increase across levels
        minimal = complexity_metrics["minimal"]
        moderate = complexity_metrics["moderate"]
        comprehensive = complexity_metrics["comprehensive"]

        # Font count progression
        assert moderate["font_count"] >= minimal["font_count"]
        assert comprehensive["font_count"] >= moderate["font_count"]

        # Heading count progression
        assert comprehensive["heading_count"] >= moderate["heading_count"]
        assert moderate["heading_count"] >= minimal["heading_count"]

        # Overall complexity should increase
        def complexity_score(metrics):
            return (metrics["font_count"] * 2 +
                   metrics["heading_count"] +
                   metrics["text_style_count"] +
                   min(metrics["css_length"] / 100, 5))  # Cap CSS contribution

        minimal_score = complexity_score(minimal)
        moderate_score = complexity_score(moderate)
        comprehensive_score = complexity_score(comprehensive)

        assert moderate_score >= minimal_score, \
            f"Moderate complexity ({moderate_score}) should be >= minimal ({minimal_score})"
        assert comprehensive_score >= moderate_score, \
            f"Comprehensive complexity ({comprehensive_score}) should be >= moderate ({moderate_score})"

    def test_enhancement_levels_performance_scaling(self, sample_brand_file):
        """Test that performance scales appropriately with enhancement levels."""
        pytest.fail("Test should fail initially - implement after performance optimization")

        levels = ["minimal", "moderate", "comprehensive"]
        performance_data = {}

        for level in levels:
            start_time = time.time()
            result = subprocess.run([
                "python", "brand_identity_generator.py",
                sample_brand_file,
                "--enhance",
                "--enhancement-level", level
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            end_time = time.time()

            assert result.returncode == 0
            execution_time = end_time - start_time
            performance_data[level] = execution_time

            # Each level should complete within reasonable time
            max_times = {"minimal": 5.0, "moderate": 10.0, "comprehensive": 15.0}
            assert execution_time < max_times[level], \
                f"{level.title()} level took {execution_time:.2f}s, should be <{max_times[level]}s"

        # Contract: performance should scale reasonably
        # Comprehensive can take longer but not excessively so
        assert performance_data["comprehensive"] <= performance_data["minimal"] * 3, \
            "Comprehensive should not take more than 3x minimal time"

    def test_enhancement_levels_quality_consistency(self, sample_brand_file):
        """Test that all enhancement levels maintain quality standards."""
        pytest.fail("Test should fail initially - implement after quality standards")

        levels = ["minimal", "moderate", "comprehensive"]

        for level in levels:
            result = subprocess.run([
                "python", "brand_identity_generator.py",
                sample_brand_file,
                "--enhance",
                "--enhancement-level", level
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            assert result.returncode == 0
            output_data = json.loads(result.stdout)

            typography = output_data["typography"]

            # Contract: all levels should meet minimum quality standards
            if "primary_font" in typography and typography["primary_font"]:
                primary_font = typography["primary_font"]

                # Confidence score should meet threshold
                assert primary_font["confidence_score"] >= 0.7, \
                    f"{level} level confidence {primary_font['confidence_score']} below threshold"

                # Rationale should be meaningful
                rationale = primary_font["rationale"]
                assert len(rationale) >= 20, f"{level} level rationale too short: '{rationale}'"

                # Google Font data should be complete
                google_font = primary_font["google_font"]
                assert google_font["family"], f"{level} level missing font family"
                assert google_font["category"] in ["serif", "sans-serif", "display", "handwriting", "monospace"], \
                    f"{level} level invalid font category: {google_font['category']}"

    def test_enhancement_levels_with_different_brand_personalities(self, sample_brand_file):
        """Test enhancement levels with different brand personality combinations."""
        pytest.fail("Test should fail initially - implement after personality handling")

        # Test different personality combinations
        personality_variations = [
            {"voice": "professional, corporate, trustworthy", "expected_category": "sans-serif"},
            {"voice": "creative, artistic, expressive", "expected_category": "display"},
            {"voice": "elegant, sophisticated, luxury", "expected_category": "serif"},
            {"voice": "friendly, approachable, casual", "expected_category": "sans-serif"}
        ]

        for variation in personality_variations:
            # Create brand file with specific personality
            brand_content = f"""# Personality Test Brand
**Primary Color**: #2563eb
**Brand Voice**: {variation["voice"]}
**Target Audience**: test audience
**Industry**: Test Industry
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(brand_content)
                temp_file = f.name

            try:
                # Test moderate level with this personality
                result = subprocess.run([
                    "python", "brand_identity_generator.py",
                    temp_file,
                    "--enhance",
                    "--enhancement-level", "moderate"
                ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

                assert result.returncode == 0
                output_data = json.loads(result.stdout)

                typography = output_data["typography"]
                if "primary_font" in typography and typography["primary_font"]:
                    primary_font = typography["primary_font"]
                    google_font = primary_font["google_font"]

                    # Personality should influence font category selection
                    actual_category = google_font["category"]
                    expected_category = variation["expected_category"]

                    # Not strict requirement, but should show personality influence
                    # At minimum, rationale should reference personality traits
                    rationale = primary_font["rationale"].lower()
                    voice_words = variation["voice"].split(", ")
                    personality_referenced = any(word.lower() in rationale for word in voice_words)

                    assert personality_referenced, \
                        f"Rationale should reference personality traits for voice: {variation['voice']}"

            finally:
                os.unlink(temp_file)

    def test_enhancement_levels_backward_compatibility(self, sample_brand_file):
        """Test that all enhancement levels maintain backward compatibility."""
        pytest.fail("Test should fail initially - implement after backward compatibility")

        levels = ["minimal", "moderate", "comprehensive"]

        for level in levels:
            result = subprocess.run([
                "python", "brand_identity_generator.py",
                sample_brand_file,
                "--enhance",
                "--enhancement-level", level
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            assert result.returncode == 0
            output_data = json.loads(result.stdout)

            # Contract: all levels should maintain existing output structure
            required_keys = ["brandName", "colorPalette", "enhancement_metadata"]
            for key in required_keys:
                assert key in output_data, f"{level} level missing required key: {key}"

            # Typography should be additive, not replacing existing functionality
            assert "colorPalette" in output_data, f"{level} level should preserve color enhancement"
            assert "enhancement_metadata" in output_data, f"{level} level should preserve metadata"

            # New typography should be properly integrated
            assert "typography" in output_data, f"{level} level should include typography"

    def test_enhancement_levels_metadata_completeness(self, sample_brand_file):
        """Test that enhancement metadata includes typography information for all levels."""
        pytest.fail("Test should fail initially - implement after metadata integration")

        levels = ["minimal", "moderate", "comprehensive"]

        for level in levels:
            result = subprocess.run([
                "python", "brand_identity_generator.py",
                sample_brand_file,
                "--enhance",
                "--enhancement-level", level
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            assert result.returncode == 0
            output_data = json.loads(result.stdout)

            metadata = output_data["enhancement_metadata"]

            # Contract: metadata should include typography enhancement information
            typography_keys = [
                "typography_enhancement", "typography_method", "font_selection_time"
            ]

            typography_metadata_present = any(key in metadata for key in typography_keys)
            assert typography_metadata_present, \
                f"{level} level should include typography metadata"

            # Should record enhancement level used
            assert metadata.get("enhancement_level") == level, \
                f"Metadata should record enhancement level as {level}"