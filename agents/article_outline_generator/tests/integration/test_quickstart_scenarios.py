"""End-to-end validation of quickstart scenarios.

These tests validate the exact scenarios from quickstart.md to ensure
the enhanced agent works as documented.
"""

import pytest
import json
import sys
import subprocess
from pathlib import Path

# Try importing from the agent
try:
    from article_outline_generator import main, process_content
except ImportError:
    main = None
    process_content = None


class TestQuickstartScenarios:
    """Test all quickstart scenarios end-to-end."""

    @pytest.fixture
    def agent_path(self):
        """Path to the article outline generator agent."""
        return Path(__file__).parent.parent.parent / "article_outline_generator.py"

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_scenario_1_backward_compatibility(self, agent_path):
        """Scenario 1: Backward Compatibility - Existing Behavior Preserved."""
        input_data = {
            "content": "# How to Build a Personal Website\n\nThis comprehensive guide covers domain registration, hosting setup, and launch strategies for beginners.",
            "target_depth": 3,
            "include_word_counts": True
        }

        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Verify envelope structure
        assert response["error"] is None
        assert response["output"] is not None

        # Verify metadata
        meta = response["output"]["meta"]
        assert meta["content_type"] == "article"
        assert meta["classification_confidence"] >= 0.9
        assert meta["classification_method"] == "rule_based"
        assert meta["classification_reasoning"] == "Instructional content"
        assert meta["llm_calls_used"] == 0
        assert meta["processing_time_ms"] < 200

        # Verify cost tracking
        assert response["meta"]["cost"]["llm_calls"] == 0
        assert response["meta"]["cost"]["usd"] == 0.0

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_scenario_2_enhanced_classification(self, agent_path):
        """Scenario 2: Enhanced Classification - Low Confidence Content."""
        input_data = {
            "content": "The Future of Remote Work. Remote work has transformed modern employment. Companies adapt to distributed teams while employees navigate new challenges and opportunities in this evolving landscape.",
            "target_depth": 2
        }

        # Run with LLM enabled (non-strict mode)
        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=10,
            env={**dict(subprocess.os.environ), "LLM_ENABLED": "true"}
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Verify successful processing
        assert response["error"] is None
        assert response["output"] is not None

        meta = response["output"]["meta"]
        assert meta["content_type"] in ["article", "story"]
        assert meta["processing_time_ms"] < 5000

        # If confidence was low enough to trigger LLM
        if meta["llm_calls_used"] > 0:
            assert meta["classification_confidence"] > 0.8
            assert meta["classification_method"] in ["llm_single", "llm_double"]
            assert response["meta"]["cost"]["llm_calls"] > 0
            assert response["meta"]["cost"]["usd"] > 0

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_scenario_3_interim_classification(self, agent_path):
        """Scenario 3: Interim Classification Request."""
        input_data = {
            "content": "Marketing automation tools help businesses streamline their processes and improve efficiency. These tools integrate with existing systems to provide seamless workflow management.",
            "interim": True,
            "timeout_ms": 2000,
            "classification_method": "auto"
        }

        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Verify interim response
        assert response["error"] is None
        assert response["output"] is not None

        meta = response["output"]["meta"]
        assert meta["interim_available"] is True
        assert meta["processing_time_ms"] < 2000
        assert meta["content_type"] in ["article", "story"]
        assert meta["classification_confidence"] >= 0.0

        # Outline should be empty for interim
        assert response["output"]["outline"] == []

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_scenario_4_story_classification(self, agent_path):
        """Scenario 4: Story Classification Enhancement."""
        input_data = {
            "content": "In a kingdom far away, a young mage discovered an ancient pendant with mysterious powers. As she learned to harness its magic, she faced challenges that would test her courage and determination.",
            "target_depth": 4
        }

        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Verify story classification
        assert response["error"] is None
        meta = response["output"]["meta"]
        assert meta["content_type"] == "story"
        assert meta["classification_confidence"] >= 0.8
        assert meta["processing_time_ms"] < 1000

        # Should have story-specific indicators
        key_indicators = meta["key_indicators"]
        story_words = ["kingdom", "mage", "pendant", "magic", "powers"]
        assert any(word in " ".join(key_indicators).lower() for word in story_words)

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_scenario_5_graceful_degradation(self, agent_path):
        """Scenario 5: Graceful Degradation without LLM."""
        input_data = {
            "content": "Ambiguous content that might need LLM classification but LLM is not available.",
            "classification_method": "auto"
        }

        # Run in strict mode to force degradation
        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json", "--strict"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Should still work with rule-based classification
        assert response["error"] is None
        meta = response["output"]["meta"]
        assert meta["classification_method"] == "rule_based"
        assert meta["llm_calls_used"] == 0

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_scenario_6_error_handling(self, agent_path):
        """Scenario 6: Error Handling."""
        # Empty content should fail validation
        input_data = {"content": ""}

        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Should return error in envelope
        assert response["output"] is None
        assert response["error"] is not None
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert "empty" in response["error"]["message"].lower()

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_scenario_7_performance_budget(self, agent_path):
        """Scenario 7: Performance Budget Compliance."""
        # Large content to test performance
        large_content = "# Performance Test\n\n" + ("Content section. " * 100)
        input_data = {
            "content": large_content,
            "target_depth": 3
        }

        import time
        start_time = time.time()

        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        end_time = time.time()
        execution_time = end_time - start_time

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Performance budget compliance
        assert execution_time < 5.0
        assert response["error"] is None
        assert response["output"]["meta"]["processing_time_ms"] < 5000

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_scenario_8_schema_validation(self, agent_path):
        """Scenario 8: Schema Validation."""
        # Test that print-schemas command works
        result = subprocess.run(
            [sys.executable, str(agent_path), "print-schemas"],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        schemas = json.loads(result.stdout)

        # Verify all schemas present
        assert "input_schema" in schemas
        assert "output_schema" in schemas
        assert "interim_output_schema" in schemas
        assert "envelope_schema" in schemas
        assert "error_schema" in schemas
        assert "_metadata" in schemas

        # Verify metadata
        metadata = schemas["_metadata"]
        assert metadata["agent"] == "article_outline_generator"
        assert metadata["version"] == "1.0.0"
        assert metadata["feature"] == "012-enhanced-classification"
        assert metadata["compatibility"] == "backward-compatible"

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_cli_flag_overrides(self, agent_path):
        """Test CLI flags override JSON input."""
        input_data = {
            "content": "# Test Article\n\nContent for testing CLI overrides.",
            "interim": False,
            "classification_method": "rules_only"
        }

        # CLI flags should override JSON values
        result = subprocess.run(
            [sys.executable, str(agent_path), "run",
             "--input-type", "json",
             "--interim",
             "--classification-method", "auto"],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Should be interim (CLI override)
        assert response["output"]["meta"]["interim_available"] is True
        assert response["output"]["outline"] == []

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_selfcheck_validation(self, agent_path):
        """Test that selfcheck passes with enhanced features."""
        result = subprocess.run(
            [sys.executable, str(agent_path), "selfcheck"],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0

        # Should mention enhanced models
        output = result.stdout
        assert "Enhanced models validate correctly" in output
        assert "Schema generation works" in output
        assert "Configuration loaded successfully" in output