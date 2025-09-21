"""Golden test for interim classification feature.

This test validates the interim classification capability that provides
early classification results before full outline generation.
"""

import pytest
import json
from pathlib import Path
import sys
import subprocess
import time

# Try importing from the agent
try:
    from article_outline_generator import main, process_content
except ImportError:
    main = None
    process_content = None


class TestInterimClassificationGolden:
    """Test interim classification response feature."""

    @pytest.fixture
    def interim_request(self):
        """Input requesting interim classification."""
        return {
            "content": """# Building Scalable Web Applications

This guide explores modern techniques for building web applications that can
scale to millions of users. We'll examine architecture patterns, technology
choices, and operational best practices.

Key Topics:
- Microservices vs Monoliths
- Database scaling strategies
- Caching layers and CDNs
- Load balancing techniques
- Monitoring and observability
""",
            "target_depth": 3,
            "interim": True,
            "timeout_ms": 1000,
            "classification_method": "auto"
        }

    @pytest.mark.golden
    def test_interim_response_structure(self, interim_request):
        """Test that interim response has correct structure."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        result = process_content(
            content=interim_request["content"],
            target_depth=interim_request["target_depth"],
            interim=interim_request["interim"],
            timeout_ms=interim_request["timeout_ms"],
            classification_method=interim_request["classification_method"]
        )

        # Should return valid envelope
        assert "meta" in result
        assert "input" in result
        assert "output" in result
        assert "error" in result

        # Should succeed
        assert result["error"] is None
        assert result["output"] is not None

        # Output should have classification but empty outline
        output = result["output"]
        assert "meta" in output
        assert "outline" in output

        # Outline should be empty for interim
        assert output["outline"] == []

        # Metadata should indicate interim
        meta = output["meta"]
        assert meta["interim_available"] is True
        assert meta["sections_count"] == 0  # No sections yet

        # Classification should be complete
        assert meta["content_type"] in ["article", "story"]
        assert meta["classification_confidence"] >= 0.0
        assert meta["classification_method"] in ["rule_based", "llm_single", "llm_double"]
        assert meta["classification_reasoning"] != ""

        # Should have quick processing time
        assert meta["processing_time_ms"] < interim_request["timeout_ms"]

    @pytest.mark.golden
    def test_interim_cli_flag(self):
        """Test interim classification via CLI flag."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        content = "# Quick Classification Test\n\nThis content needs classification."

        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(agent_path), "run",
             "--interim", "--timeout-ms", "500"],
            input=content,
            capture_output=True,
            text=True,
            timeout=2
        )
        end_time = time.time()

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Should return quickly
        execution_time = (end_time - start_time) * 1000
        assert execution_time < 1000, f"Took {execution_time:.0f}ms, should be <1000ms"

        # Should have interim response
        assert response["output"]["meta"]["interim_available"] is True
        assert response["output"]["outline"] == []
        assert response["output"]["meta"]["processing_time_ms"] < 500

    @pytest.mark.golden
    def test_interim_with_timeout(self):
        """Test that interim respects timeout settings."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        # Very short timeout
        result = process_content(
            content="# Test Article\n\nQuick classification needed.",
            interim=True,
            timeout_ms=100  # 100ms timeout
        )

        # Should still return a valid response
        assert result["error"] is None
        assert result["output"] is not None

        # Should be marked as interim
        assert result["output"]["meta"]["interim_available"] is True

        # Processing should be fast
        assert result["output"]["meta"]["processing_time_ms"] <= 200  # Some buffer

    @pytest.mark.golden
    def test_interim_preserves_classification_quality(self, interim_request):
        """Test that interim classification is as accurate as full processing."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        # Get interim classification
        interim_result = process_content(
            content=interim_request["content"],
            interim=True,
            timeout_ms=1000
        )

        interim_meta = interim_result["output"]["meta"]

        # Get full classification (no interim)
        full_result = process_content(
            content=interim_request["content"],
            interim=False
        )

        full_meta = full_result["output"]["meta"]

        # Classification should match
        assert interim_meta["content_type"] == full_meta["content_type"]
        assert interim_meta["detected_language"] == full_meta["detected_language"]

        # Confidence should be similar (allowing small variance)
        assert abs(interim_meta["classification_confidence"] -
                  full_meta["classification_confidence"]) < 0.1

        # Method should match
        assert interim_meta["classification_method"] == full_meta["classification_method"]

    @pytest.mark.golden
    def test_interim_flag_overrides_json(self):
        """Test CLI flag overrides JSON input for interim."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        # JSON says no interim, but CLI flag says yes
        input_data = {
            "content": "# Test Content\n\nSome article content here.",
            "interim": False  # Explicitly false in JSON
        }

        result = subprocess.run(
            [sys.executable, str(agent_path), "run",
             "--input-type", "json",
             "--interim"],  # CLI flag overrides
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=2
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Should be interim (CLI flag wins)
        assert response["output"]["meta"]["interim_available"] is True
        assert response["output"]["outline"] == []

    @pytest.mark.golden
    def test_non_interim_has_full_outline(self):
        """Test that non-interim requests return full outline."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        result = process_content(
            content="# Complete Article\n\nThis needs a full outline.",
            interim=False  # Explicitly not interim
        )

        # Should have full outline
        assert result["output"]["outline"] != []
        assert len(result["output"]["outline"]) > 0
        assert result["output"]["meta"]["sections_count"] > 0
        assert result["output"]["meta"]["interim_available"] is False