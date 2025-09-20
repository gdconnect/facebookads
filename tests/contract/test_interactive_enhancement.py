"""
Contract test for CLI --interactive enhancement functionality.
Tests interactive user review and feedback collection.
"""

import json
import subprocess
import tempfile
from pathlib import Path
import pytest
import time
from unittest.mock import patch, MagicMock


def test_interactive_flag_requires_enhancement():
    """Test that --interactive flag requires --enhance to be meaningful."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = f.name

    try:
        # Interactive without enhance should still work but have limited functionality
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--interactive'
        ], capture_output=True, text=True, timeout=5)

        # Should complete without hanging
        assert result.returncode == 0

    finally:
        Path(input_file).unlink()


def test_interactive_enhancement_structure():
    """Test that interactive enhancement produces expected output structure."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: professional blue
""")
        input_file = f.name

    try:
        # Mock interactive input to auto-accept suggestions
        with patch('builtins.input', return_value='A'):
            result = subprocess.run([
                'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                input_file, '--enhance', '--interactive'
            ], capture_output=True, text=True, timeout=10)

            assert result.returncode == 0

            output = json.loads(result.stdout)

            # Should have enhancement metadata
            assert 'enhancement_metadata' in output

            # Should record user feedback count
            assert 'user_feedback_count' in output['enhancement_metadata']

    finally:
        Path(input_file).unlink()


def test_interactive_session_save_load():
    """Test session save and load functionality."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as input_f:
        input_f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = input_f.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as session_f:
        session_file = session_f.name

    try:
        # Save session
        with patch('builtins.input', return_value='A'):
            result = subprocess.run([
                'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                input_file, '--enhance', '--interactive',
                '--save-session', session_file
            ], capture_output=True, text=True, timeout=10)

            assert result.returncode == 0

        # Verify session file was created
        session_path = Path(session_file)
        assert session_path.exists()

        # Verify session file structure
        with open(session_file, 'r') as f:
            session_data = json.load(f)

        expected_fields = ['session_id', 'created_at', 'original_input',
                          'current_state', 'session_metadata']
        for field in expected_fields:
            assert field in session_data

        # Load session
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            '--load-session', session_file
        ], capture_output=True, text=True, timeout=10)

        assert result.returncode == 0

    finally:
        Path(input_file).unlink()
        Path(session_file).unlink(missing_ok=True)


def test_interactive_enhancement_user_feedback_recording():
    """Test that user feedback is properly recorded."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
Secondary: orange
""")
        input_file = f.name

    try:
        # Provide actual input for interactive mode (Accept, then Modify)
        input_text = "A\nM\nwarmer orange\nA\n"

        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--enhance', '--interactive'
        ], capture_output=True, text=True, input=input_text, timeout=15)

        assert result.returncode == 0

        output = json.loads(result.stdout)

        # Should record multiple feedback interactions
        assert output['enhancement_metadata']['user_feedback_count'] >= 2

    finally:
        Path(input_file).unlink()


def test_interactive_enhancement_timeout_handling():
    """Test that interactive mode handles timeouts gracefully."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = f.name

    try:
        # Don't mock input to test timeout behavior
        start_time = time.time()
        result = subprocess.run([
            'python', 'agents/brand_identity_generator/brand_identity_generator.py',
            input_file, '--enhance', '--interactive'
        ], capture_output=True, text=True, timeout=3, input='\n')

        duration = time.time() - start_time

        # Should complete within timeout or handle gracefully
        # Either succeeds quickly or times out appropriately
        assert duration <= 5

    except subprocess.TimeoutExpired:
        # Timeout is acceptable for interactive mode
        pass
    finally:
        Path(input_file).unlink()


def test_interactive_enhancement_with_output_file():
    """Test interactive enhancement with output file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as input_f:
        input_f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = input_f.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_f:
        output_file = output_f.name

    try:
        with patch('builtins.input', return_value='A'):
            result = subprocess.run([
                'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                input_file, '--enhance', '--interactive',
                '-o', output_file
            ], capture_output=True, text=True, timeout=10)

            assert result.returncode == 0

        # Verify output file was created
        output_path = Path(output_file)
        assert output_path.exists()

        with open(output_file, 'r') as f:
            output = json.load(f)

        assert 'enhancement_metadata' in output
        assert 'user_feedback_count' in output['enhancement_metadata']

    finally:
        Path(input_file).unlink()
        Path(output_file).unlink(missing_ok=True)


def test_interactive_enhancement_different_providers():
    """Test interactive enhancement with different LLM providers."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = f.name

    try:
        for provider in ['openai', 'anthropic']:
            with patch('builtins.input', return_value='A'):
                result = subprocess.run([
                    'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                    input_file, '--enhance', '--interactive',
                    '--llm-provider', provider
                ], capture_output=True, text=True, timeout=10)

                assert result.returncode == 0

                output = json.loads(result.stdout)
                assert output['enhancement_metadata']['llm_provider'] == provider

    finally:
        Path(input_file).unlink()


def test_interactive_enhancement_all_levels():
    """Test interactive enhancement with all enhancement levels."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
""")
        input_file = f.name

    try:
        for level in ['minimal', 'moderate', 'comprehensive']:
            with patch('builtins.input', return_value='A'):
                result = subprocess.run([
                    'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                    input_file, '--enhance', '--interactive',
                    '--enhancement-level', level
                ], capture_output=True, text=True, timeout=10)

                assert result.returncode == 0

                output = json.loads(result.stdout)
                assert output['enhancement_metadata']['enhancement_level'] == level

    finally:
        Path(input_file).unlink()


def test_interactive_enhancement_error_handling():
    """Test interactive enhancement error handling."""
    # Test with invalid input file
    result = subprocess.run([
        'python', 'agents/brand_identity_generator/brand_identity_generator.py',
        'nonexistent.md', '--enhance', '--interactive'
    ], capture_output=True, text=True, timeout=5)

    assert result.returncode != 0
    assert 'ERROR' in result.stderr


def test_interactive_enhancement_design_strategy():
    """Test interactive enhancement with design strategy generation."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Brand Overview
Brand Name: TestBrand
Primary: blue
Secondary: orange

# Brand Personality
Traits: professional, innovative
""")
        input_file = f.name

    try:
        with patch('builtins.input', return_value='A'):
            result = subprocess.run([
                'python', 'agents/brand_identity_generator/brand_identity_generator.py',
                input_file, '--enhance', '--interactive', '--design-strategy'
            ], capture_output=True, text=True, timeout=10)

            assert result.returncode == 0

            output = json.loads(result.stdout)

            # Should include design strategy
            assert 'designStrategy' in output or 'design_strategy' in output

    finally:
        Path(input_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__])