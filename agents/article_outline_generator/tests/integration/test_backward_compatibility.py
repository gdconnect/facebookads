"""Integration tests for backward compatibility validation.

These tests ensure existing functionality works identically with enhancements.
Tests MUST FAIL until implementation is complete.
"""

import json
import pytest
from pathlib import Path
import subprocess
import sys


class TestBackwardCompatibility:
    """Test that enhanced agent maintains backward compatibility."""

    @pytest.fixture
    def agent_path(self):
        """Path to the article outline generator agent."""
        return Path(__file__).parent.parent.parent / "article_outline_generator.py"

    @pytest.mark.integration
    def test_existing_input_format_unchanged(self, agent_path):
        """Test that existing input format still works without new fields."""
        input_data = {
            "content": "# How to Build a Personal Website\n\nThis comprehensive guide covers domain registration, hosting setup, and launch strategies for beginners.",
            "target_depth": 3,
            "include_word_counts": True
        }

        # This should work exactly as before
        result = subprocess.run(
            [sys.executable, str(agent_path), "run"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should complete successfully
        assert result.returncode == 0, f"Agent failed: {result.stderr}"

        response = json.loads(result.stdout)

        # Verify envelope structure unchanged
        assert "meta" in response
        assert "input" in response
        assert "output" in response
        assert "error" in response
        assert response["error"] is None

        # Verify output structure unchanged
        assert "meta" in response["output"]
        assert "outline" in response["output"]

        # Verify classification happens (enhanced) but structure preserved
        assert response["output"]["meta"]["content_type"] == "article"
        assert response["output"]["meta"]["classification_confidence"] >= 0.7
        assert len(response["output"]["outline"]) >= 1

    @pytest.mark.integration
    def test_no_llm_calls_by_default(self, agent_path):
        """Test that STRICT mode is preserved (no LLM calls by default)."""
        input_data = {
            "content": "# Test Article\n\nSample content description."
        }

        result = subprocess.run(
            [sys.executable, str(agent_path), "run"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Should not use LLM by default (STRICT mode)
        assert response["output"]["meta"]["llm_calls_used"] == 0
        assert response["output"]["meta"]["classification_method"] == "rule_based"
        assert response["meta"]["cost"]["llm_calls"] == 0
        assert response["meta"]["cost"]["usd"] == 0.0

    @pytest.mark.integration
    def test_cli_commands_unchanged(self, agent_path):
        """Test that all CLI commands still work as expected."""

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
        input_data = {"content": "# Test\n\nContent"}
        result = subprocess.run(
            [sys.executable, str(agent_path), "dry-run"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0

    @pytest.mark.integration
    def test_performance_unchanged(self, agent_path):
        """Test that performance characteristics are preserved."""
        input_data = {
            "content": "# Test Article\n\nThis is a test article with sufficient content to generate a proper outline structure."
        }

        import time
        start_time = time.time()

        result = subprocess.run(
            [sys.executable, str(agent_path), "run"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        end_time = time.time()
        execution_time = end_time - start_time

        assert result.returncode == 0
        # Should complete in reasonable time (<5s constitutional requirement)
        assert execution_time < 5.0

        response = json.loads(result.stdout)
        # Processing time should be reasonable for rule-based classification
        assert response["output"]["meta"]["processing_time_ms"] < 1000

    @pytest.mark.integration
    def test_error_handling_unchanged(self, agent_path):
        """Test that error handling behavior is preserved."""
        # Test empty content (should fail validation)
        input_data = {"content": ""}

        result = subprocess.run(
            [sys.executable, str(agent_path), "run"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0  # Agent handles errors gracefully
        response = json.loads(result.stdout)

        # Should return error in envelope
        assert response["output"] is None
        assert response["error"] is not None
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert "empty" in response["error"]["message"].lower()