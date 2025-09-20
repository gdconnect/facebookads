"""
Contract test for CLI --analyze-gaps functionality.
Tests gap analysis without enhancement processing.
"""

import json
import subprocess
import tempfile
from pathlib import Path
import pytest


def test_analyze_gaps_flag_basic_functionality():
    """Test that --analyze-gaps flag performs gap analysis without enhancement."""
    # Create input with missing elements
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: IncompleteB

# Visual Identity / Colors
Primary: blue

# Brand Personality
Traits: professional
""")
        input_file = f.name

    try:
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--analyze-gaps'
        ], capture_output=True, text=True)

        assert result.returncode == 0, f"Gap analysis failed: {result.stderr}"

        # Parse output
        output = json.loads(result.stdout)

        # Verify gap analysis structure
        assert 'gap_analysis' in output
        gap_analysis = output['gap_analysis']

        # Required fields
        assert 'missing_elements' in gap_analysis
        assert 'incomplete_elements' in gap_analysis
        assert 'completeness_score' in gap_analysis
        assert 'priority_gaps' in gap_analysis
        assert 'enhancement_opportunities' in gap_analysis

        # Verify completeness score is between 0 and 1
        assert 0.0 <= gap_analysis['completeness_score'] <= 1.0

        # Verify missing elements is a list
        assert isinstance(gap_analysis['missing_elements'], list)
        assert isinstance(gap_analysis['incomplete_elements'], list)
        assert isinstance(gap_analysis['priority_gaps'], list)
        assert isinstance(gap_analysis['enhancement_opportunities'], list)

    finally:
        Path(input_file).unlink()


def test_analyze_gaps_identifies_missing_typography():
    """Test that gap analysis identifies missing typography elements."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand

# Visual Identity / Colors
Primary: blue
Secondary: orange

# Brand Personality
Traits: professional, innovative
""")
        input_file = f.name

    try:
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--analyze-gaps'
        ], capture_output=True, text=True)

        assert result.returncode == 0
        output = json.loads(result.stdout)

        gap_analysis = output['gap_analysis']

        # Should identify missing typography
        assert 'typography' in gap_analysis['missing_elements']

    finally:
        Path(input_file).unlink()


def test_analyze_gaps_identifies_missing_visual_style():
    """Test that gap analysis identifies missing visual style elements."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand

# Visual Identity / Colors
Primary: #0066CC

# Brand Personality
Traits: modern, clean
""")
        input_file = f.name

    try:
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--analyze-gaps'
        ], capture_output=True, text=True)

        assert result.returncode == 0
        output = json.loads(result.stdout)

        gap_analysis = output['gap_analysis']

        # Should identify missing visual style
        assert 'visual_style' in gap_analysis['missing_elements']

    finally:
        Path(input_file).unlink()


def test_analyze_gaps_priority_gaps_structure():
    """Test that priority gaps have correct structure."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = f.name

    try:
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--analyze-gaps'
        ], capture_output=True, text=True)

        assert result.returncode == 0
        output = json.loads(result.stdout)

        gap_analysis = output['gap_analysis']
        priority_gaps = gap_analysis['priority_gaps']

        # Each priority gap should have required fields
        for gap in priority_gaps:
            assert 'element' in gap
            assert 'impact' in gap
            assert 'description' in gap
            assert gap['impact'] in ['low', 'medium', 'high', 'critical']

    finally:
        Path(input_file).unlink()


def test_analyze_gaps_enhancement_opportunities():
    """Test that enhancement opportunities are provided."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand

# Visual Identity / Colors
Primary: professional blue
""")
        input_file = f.name

    try:
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--analyze-gaps'
        ], capture_output=True, text=True)

        assert result.returncode == 0
        output = json.loads(result.stdout)

        gap_analysis = output['gap_analysis']
        opportunities = gap_analysis['enhancement_opportunities']

        # Should have some enhancement opportunities
        assert len(opportunities) > 0
        assert all(isinstance(opp, str) for opp in opportunities)

        # Should suggest hex code generation for color descriptions
        hex_suggestions = [opp for opp in opportunities if 'hex' in opp.lower()]
        assert len(hex_suggestions) > 0

    finally:
        Path(input_file).unlink()


def test_analyze_gaps_does_not_include_enhancement_metadata():
    """Test that gap analysis doesn't include enhancement metadata."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = f.name

    try:
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--analyze-gaps'
        ], capture_output=True, text=True)

        assert result.returncode == 0
        output = json.loads(result.stdout)

        # Should NOT include enhancement metadata
        assert 'enhancement_metadata' not in output

        # Should NOT include enhanced brand identity
        assert 'colorPalette' not in output or 'enhancement_metadata' not in output.get('colorPalette', {}).get('primary', {})

    finally:
        Path(input_file).unlink()


def test_analyze_gaps_with_complete_brand():
    """Test gap analysis with a complete brand description."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: CompleteBrand
Description: A comprehensive brand with all elements

# Visual Identity / Colors
Primary: #2563EB "Trust Blue"
Secondary: #F97316 "Energy Orange"
Neutral: #6B7280 "Professional Gray"

# Typography
Heading Font: Roboto Bold
Body Font: Open Sans Regular
Font Weights: 400, 600, 700

# Brand Personality
Traits: professional, innovative, trustworthy, approachable
Values: quality, integrity, customer-first

# Logo Assets
Logo Type: wordmark
Colors: primary and neutral
Formats: SVG, PNG

# Visual Style
Style: modern, clean, minimal
Spacing: consistent 8px grid
Corners: 4px border radius
""")
        input_file = f.name

    try:
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--analyze-gaps'
        ], capture_output=True, text=True)

        assert result.returncode == 0
        output = json.loads(result.stdout)

        gap_analysis = output['gap_analysis']

        # Should have high completeness score
        assert gap_analysis['completeness_score'] >= 0.8

        # Should have fewer missing elements
        assert len(gap_analysis['missing_elements']) <= 2

    finally:
        Path(input_file).unlink()


def test_analyze_gaps_output_to_file():
    """Test gap analysis with file output."""
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
            input_file, '--analyze-gaps', '-o', output_file
        ], capture_output=True, text=True)

        assert result.returncode == 0

        # Verify file was created
        output_path = Path(output_file)
        assert output_path.exists()

        with open(output_file, 'r') as f:
            output = json.load(f)

        assert 'gap_analysis' in output

    finally:
        Path(input_file).unlink()
        Path(output_file).unlink(missing_ok=True)


def test_analyze_gaps_with_invalid_input():
    """Test gap analysis with invalid input."""
    result = subprocess.run([
        'python', 'agents/brand_identity_generator/brand_identity_generator.py',
        'nonexistent.md', '--analyze-gaps'
    ], capture_output=True, text=True)

    assert result.returncode != 0
    assert 'ERROR' in result.stderr


if __name__ == "__main__":
    pytest.main([__file__])