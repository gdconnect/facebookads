"""Golden test for backward compatibility with existing functionality.

This test ensures that the enhanced agent maintains complete backward
compatibility with the original functionality.
"""

import pytest
import json
from pathlib import Path
import sys
import subprocess

# Try importing from the agent
try:
    from article_outline_generator import main, process_content
except ImportError:
    main = None
    process_content = None


class TestBackwardCompatibilityGolden:
    """Test backward compatibility with pre-enhancement behavior."""

    @pytest.fixture
    def legacy_input(self):
        """Original input format without enhanced fields."""
        return {
            "content": """# How to Build a Personal Website

This comprehensive guide will walk you through the process of creating your own
personal website from scratch. We'll cover everything from domain registration
to hosting setup and design considerations.

## Topics to Cover
- Choosing a domain name and registering it
- Selecting the right hosting provider
- Setting up your development environment
- Building your first HTML pages
- Adding CSS for styling
- Making your site responsive
- Deploying and maintaining your website
""",
            "target_depth": 3,
            "include_word_counts": True
        }

    @pytest.mark.golden
    def test_legacy_input_format_works(self, legacy_input):
        """Test that old input format still works without new fields."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        result = process_content(
            content=legacy_input["content"],
            target_depth=legacy_input["target_depth"],
            include_word_counts=legacy_input["include_word_counts"]
        )

        # Verify envelope structure
        assert "meta" in result
        assert "input" in result
        assert "output" in result
        assert "error" in result

        # Should succeed
        assert result["error"] is None
        assert result["output"] is not None

        # Verify output structure unchanged
        output = result["output"]
        assert "meta" in output
        assert "outline" in output

        # Verify metadata has sensible defaults for new fields
        meta = output["meta"]
        assert meta["content_type"] in ["article", "story"]
        assert meta["detected_language"] == "en"
        assert meta["depth"] == 3
        assert meta["sections_count"] > 0

        # New fields should have defaults
        assert meta["classification_confidence"] >= 0.0
        assert meta["classification_method"] == "rule_based"
        assert meta["llm_calls_used"] == 0  # No LLM in STRICT mode by default
        assert meta["interim_available"] == False

        # Outline should be populated
        assert len(output["outline"]) > 0
        for section in output["outline"]:
            assert "title" in section
            assert "level" in section
            assert section["word_count_estimate"] is not None  # Since include_word_counts=True

    @pytest.mark.golden
    def test_no_llm_calls_in_strict_mode(self, legacy_input):
        """Test that STRICT mode (default) makes no LLM calls."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        # Run via CLI to test complete flow
        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json", "--strict"],
            input=json.dumps(legacy_input),
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Verify no LLM usage
        assert response["meta"]["cost"]["llm_calls"] == 0
        assert response["meta"]["cost"]["tokens_in"] == 0
        assert response["meta"]["cost"]["tokens_out"] == 0
        assert response["meta"]["cost"]["usd"] == 0.0

        # Verify classification was rule-based
        assert response["output"]["meta"]["classification_method"] == "rule_based"
        assert response["output"]["meta"]["llm_calls_used"] == 0

    @pytest.mark.golden
    def test_performance_unchanged(self, legacy_input):
        """Test that performance characteristics are preserved."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        import time

        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(legacy_input),
            capture_output=True,
            text=True,
            timeout=5
        )
        end_time = time.time()

        assert result.returncode == 0
        execution_time = end_time - start_time

        # Should complete within constitutional budget
        assert execution_time < 5.0, f"Execution took {execution_time:.2f}s, exceeds 5s budget"

        response = json.loads(result.stdout)

        # Processing time should be reasonable for rule-based
        assert response["output"]["meta"]["processing_time_ms"] < 1000

    @pytest.mark.golden
    def test_existing_cli_commands_work(self):
        """Test that all existing CLI commands still function."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        # Test selfcheck
        result = subprocess.run(
            [sys.executable, str(agent_path), "selfcheck"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0

        # Test print-schemas
        result = subprocess.run(
            [sys.executable, str(agent_path), "print-schemas"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
        schemas = json.loads(result.stdout)
        assert "input_schema" in schemas
        assert "output_schema" in schemas
        assert "envelope_schema" in schemas

        # Test dry-run
        test_input = {"content": "# Test Article\n\nTest content."}
        result = subprocess.run(
            [sys.executable, str(agent_path), "dry-run", "--input-type", "json"],
            input=json.dumps(test_input),
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
        response = json.loads(result.stdout)
        assert response["status"] == "valid"