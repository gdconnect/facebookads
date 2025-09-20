"""
Contract test for CLI --enhance flag functionality.
Tests the basic enhancement flag behavior and integration.
"""

import json
import subprocess
import tempfile
from pathlib import Path
import pytest


def test_enhance_flag_activates_llm_processing():
    """Test that --enhance flag activates LLM enhancement processing."""
    # Create temporary input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Description: A professional technology company

# Visual Identity / Colors
Primary: professional blue
Secondary: energetic orange

# Brand Personality
Traits: professional, innovative, trustworthy
""")
        input_file = f.name

    try:
        # Run with enhancement flag
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--enhance'
        ], capture_output=True, text=True)

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Parse output
        output = json.loads(result.stdout)

        # Verify enhancement metadata is present
        assert 'enhancement_metadata' in output
        assert output['enhancement_metadata']['enhancement_level'] == 'moderate'
        assert 'workflow_id' in output['enhancement_metadata']
        assert 'processing_time' in output['enhancement_metadata']
        assert 'llm_provider' in output['enhancement_metadata']

        # Verify enhanced color format
        if 'colorPalette' in output and 'primary' in output['colorPalette']:
            primary_color = output['colorPalette']['primary']
            assert 'enhancement_metadata' in primary_color
            assert 'confidence_score' in primary_color['enhancement_metadata']
            assert 'rationale' in primary_color['enhancement_metadata']

    finally:
        Path(input_file).unlink()


def test_enhance_flag_with_enhancement_levels():
    """Test --enhance flag with different enhancement levels."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = f.name

    try:
        for level in ['minimal', 'moderate', 'comprehensive']:
            result = subprocess.run([
                'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                input_file, '--enhance', '--enhancement-level', level
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"Enhancement level {level} failed: {result.stderr}"

            output = json.loads(result.stdout)
            assert output['enhancement_metadata']['enhancement_level'] == level

    finally:
        Path(input_file).unlink()


def test_enhance_flag_with_llm_providers():
    """Test --enhance flag with different LLM providers."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = f.name

    try:
        for provider in ['openai', 'anthropic', 'local']:
            result = subprocess.run([
                'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                input_file, '--enhance', '--llm-provider', provider
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"LLM provider {provider} failed: {result.stderr}"

            output = json.loads(result.stdout)
            assert output['enhancement_metadata']['llm_provider'] == provider

    finally:
        Path(input_file).unlink()


def test_enhance_flag_without_input_fails():
    """Test that --enhance flag requires input file."""
    result = subprocess.run([
        'python', 'agents/brand_identity_generator/brand_identity_generator.py', '--enhance'
    ], capture_output=True, text=True)

    # Should fail gracefully
    assert result.returncode != 0


def test_enhance_flag_with_invalid_file_fails():
    """Test that --enhance flag fails gracefully with invalid input."""
    result = subprocess.run([
        'python', 'agents/brand_identity_generator/brand_identity_generator.py',
        'nonexistent.md', '--enhance'
    ], capture_output=True, text=True)

    assert result.returncode != 0
    assert 'ERROR' in result.stderr


def test_enhance_flag_backward_compatibility():
    """Test that enhancement doesn't break existing functionality."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = f.name

    try:
        # Run without enhancement (standard mode)
        standard_result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py', input_file
        ], capture_output=True, text=True)

        assert standard_result.returncode == 0
        standard_output = json.loads(standard_result.stdout)

        # Run with enhancement
        enhanced_result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--enhance'
        ], capture_output=True, text=True)

        assert enhanced_result.returncode == 0
        enhanced_output = json.loads(enhanced_result.stdout)

        # Verify core structure is preserved
        assert 'brandName' in standard_output
        assert 'brandName' in enhanced_output
        assert standard_output['brandName'] == enhanced_output['brandName']

        # Enhanced output should have additional metadata
        assert 'enhancement_metadata' not in standard_output
        assert 'enhancement_metadata' in enhanced_output

    finally:
        Path(input_file).unlink()


def test_enhance_flag_output_to_file():
    """Test --enhance flag with file output."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as input_f:
        input_f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = input_f.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_f:
        output_file = output_f.name

    try:
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--enhance', '-o', output_file
        ], capture_output=True, text=True)

        assert result.returncode == 0

        # Verify file was created and contains valid JSON
        output_path = Path(output_file)
        assert output_path.exists()

        with open(output_file, 'r') as f:
            output = json.load(f)

        assert 'enhancement_metadata' in output
        assert output['enhancement_metadata']['enhancement_level'] == 'moderate'

    finally:
        Path(input_file).unlink()
        Path(output_file).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])