"""Smoke test scenario for PRD enhancer.

Tests the basic functionality with a minimal PRD to ensure the agent
can process simple documents in under 2 seconds.
"""

import pytest
import tempfile
import time
from pathlib import Path

# Import the agent module - will fail initially (TDD)
try:
    from prd_enhancer import enhance_prd, main
except ImportError:
    pytest.skip("Agent not implemented yet - TDD phase", allow_module_level=True)


class TestSmokeScenario:
    """Smoke test for basic PRD enhancement functionality."""

    def test_minimal_prd_processing(self):
        """Test processing of minimal 1-paragraph PRD completes quickly."""
        # Create minimal test PRD
        minimal_prd_content = """# Test PRD

We need a fast user-friendly system that can handle customer requests efficiently.

The system should be scalable and reliable for our users.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(minimal_prd_content)
            input_file = f.name

        try:
            # Measure processing time
            start_time = time.time()
            result = enhance_prd(input_file)
            processing_time = time.time() - start_time

            # Critical requirements
            assert processing_time < 2.0, f"Processing took {processing_time:.2f}s, should be <2s"
            assert result is not None
            assert result.complexity_score is not None
            assert isinstance(result.enhanced_prd, str)
            assert len(result.enhanced_prd) > 0

            # Basic content validation
            assert "# Test PRD" in result.enhanced_prd or "# Enhanced" in result.enhanced_prd
            assert result.complexity_score >= 0 and result.complexity_score <= 100

        finally:
            # Cleanup
            Path(input_file).unlink(missing_ok=True)

    def test_ambiguity_detection_in_minimal_prd(self):
        """Test that ambiguous terms are detected even in minimal PRDs."""
        minimal_prd_content = """# Simple PRD

We need a fast user-friendly system.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(minimal_prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Should detect ambiguous terms
            assert len(result.ambiguities_found) > 0

            # Check for expected ambiguous terms
            found_terms = [amb.term for amb in result.ambiguities_found]
            assert "fast" in found_terms or "user-friendly" in found_terms

            # Each ambiguity should have a suggested fix
            for ambiguity in result.ambiguities_found:
                assert ambiguity.suggested_fix is not None
                assert len(ambiguity.suggested_fix) > 0

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_cli_basic_functionality(self):
        """Test that CLI interface works for basic operations."""
        minimal_prd_content = """# CLI Test PRD

Simple system for testing CLI functionality.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(minimal_prd_content)
            input_file = f.name

        try:
            # Test CLI processing
            import sys
            from io import StringIO

            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            try:
                # Simulate CLI call
                sys.argv = ['prd_enhancer.py', input_file]
                main()

                output = captured_output.getvalue()

                # Should have some processing output
                assert len(output) > 0

            finally:
                sys.stdout = old_stdout

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_fallback_mode_performance(self):
        """Test that fallback mode (without LLM) still performs adequately."""
        minimal_prd_content = """# Fallback Test PRD

We need a scalable, performant, user-friendly solution that is robust and reliable.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(minimal_prd_content)
            input_file = f.name

        try:
            # Force fallback mode by setting model disabled
            start_time = time.time()
            result = enhance_prd(input_file, model_enabled=False)
            processing_time = time.time() - start_time

            # Should still be fast
            assert processing_time < 2.0

            # Should still detect ambiguities using regex
            assert len(result.ambiguities_found) > 0

            # Check that fallback was used
            for ambiguity in result.ambiguities_found:
                assert ambiguity.source == "regex"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_invalid_input_handling(self):
        """Test that invalid inputs are handled gracefully."""
        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            enhance_prd("non_existent_file.md")

        # Test with different file extension (should still work as agent is flexible)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("System should be fast and user-friendly.")
            text_file = f.name

        try:
            # Agent should handle any text file, not just .md
            result = enhance_prd(text_file)
            assert result is not None
            assert len(result.ambiguities_found) > 0  # Should find ambiguities
        finally:
            Path(text_file).unlink(missing_ok=True)

    def test_empty_file_handling(self):
        """Test that empty files are handled appropriately."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")  # Empty file
            empty_file = f.name

        try:
            result = enhance_prd(empty_file)

            # Should handle gracefully
            assert result.complexity_score == 0
            assert len(result.ambiguities_found) == 0
            assert len(result.core_features) == 0

        finally:
            Path(empty_file).unlink(missing_ok=True)