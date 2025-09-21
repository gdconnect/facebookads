"""Golden test for enhanced classification with LLM fallback.

This test validates the enhanced classification features including
LLM fallback when confidence is low.
"""

import pytest
import json
from pathlib import Path
import sys
import subprocess
import os

# Try importing from the agent
try:
    from article_outline_generator import main, process_content
except ImportError:
    main = None
    process_content = None


class TestEnhancedClassificationGolden:
    """Test enhanced classification features with LLM integration."""

    @pytest.fixture
    def ambiguous_content(self):
        """Content that should have low confidence and trigger LLM."""
        return {
            "content": """The Digital Revolution

Technology continues to reshape our world in unprecedented ways. From artificial
intelligence to quantum computing, the pace of innovation accelerates daily.
Consider the implications for society, business, and individual privacy.

Emerging Trends:
- Machine learning applications
- Blockchain beyond cryptocurrency
- Edge computing paradigms
- Sustainable tech solutions

The future remains uncertain yet full of potential.
""",
            "target_depth": 3,
            "classification_method": "auto"
        }

    @pytest.fixture
    def high_confidence_content(self):
        """Content that should have high confidence without LLM."""
        return {
            "content": """# How to Configure Git for Team Collaboration

This step-by-step tutorial will guide you through setting up Git for effective
team collaboration. Follow these instructions to configure your environment.

## Prerequisites
- Git installed on your system
- A GitHub or GitLab account
- Basic command line knowledge

## Step 1: Global Configuration
First, set your user identity:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 2: SSH Key Setup
Generate and configure SSH keys for secure authentication.

## Step 3: Repository Setup
Clone the team repository and configure remotes.
""",
            "target_depth": 3,
            "classification_method": "auto"
        }

    @pytest.mark.golden
    @pytest.mark.skipif(
        not os.environ.get("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for LLM testing"
    )
    def test_llm_enhancement_on_low_confidence(self, ambiguous_content):
        """Test that low confidence content triggers LLM enhancement."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        # Run without strict mode to allow LLM
        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(ambiguous_content),
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "LLM_ENABLED": "true"}
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Should have used LLM enhancement
        output_meta = response["output"]["meta"]

        # Check if LLM was used (when confidence was low)
        if output_meta["classification_confidence"] < 0.8:
            assert output_meta["llm_calls_used"] > 0
            assert output_meta["classification_method"] in ["llm_single", "llm_double"]

            # Cost should be tracked
            assert response["meta"]["cost"]["llm_calls"] > 0
            assert response["meta"]["cost"]["tokens_in"] > 0
            assert response["meta"]["cost"]["tokens_out"] > 0
            assert response["meta"]["cost"]["usd"] > 0.0

    @pytest.mark.golden
    def test_high_confidence_skips_llm(self, high_confidence_content):
        """Test that high confidence content doesn't use LLM."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        # Run with LLM enabled but high confidence content
        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(high_confidence_content),
            capture_output=True,
            text=True,
            timeout=5,
            env={**os.environ, "LLM_ENABLED": "true"}
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Should NOT have used LLM (high confidence)
        output_meta = response["output"]["meta"]
        assert output_meta["classification_confidence"] >= 0.8
        assert output_meta["classification_method"] == "rule_based"
        assert output_meta["llm_calls_used"] == 0

        # No LLM costs
        assert response["meta"]["cost"]["llm_calls"] == 0
        assert response["meta"]["cost"]["usd"] == 0.0

    @pytest.mark.golden
    def test_classification_method_override(self, ambiguous_content):
        """Test that classification_method parameter works correctly."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        # Test rules_only - should never use LLM
        result = process_content(
            content=ambiguous_content["content"],
            target_depth=ambiguous_content["target_depth"],
            classification_method="rules_only"
        )

        assert result["output"]["meta"]["classification_method"] == "rule_based"
        assert result["output"]["meta"]["llm_calls_used"] == 0

    @pytest.mark.golden
    def test_enhanced_metadata_fields(self, high_confidence_content):
        """Test that all enhanced metadata fields are populated."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        result = process_content(
            content=high_confidence_content["content"],
            target_depth=high_confidence_content["target_depth"]
        )

        meta = result["output"]["meta"]

        # All enhanced fields should be present
        assert "classification_confidence" in meta
        assert isinstance(meta["classification_confidence"], float)
        assert 0.0 <= meta["classification_confidence"] <= 1.0

        assert "classification_method" in meta
        assert meta["classification_method"] in ["rule_based", "llm_single", "llm_double"]

        assert "classification_reasoning" in meta
        assert isinstance(meta["classification_reasoning"], str)
        assert len(meta["classification_reasoning"]) > 0

        assert "key_indicators" in meta
        assert isinstance(meta["key_indicators"], list)

        assert "llm_calls_used" in meta
        assert isinstance(meta["llm_calls_used"], int)
        assert 0 <= meta["llm_calls_used"] <= 2  # Constitutional limit

        assert "processing_time_ms" in meta
        assert isinstance(meta["processing_time_ms"], int)
        assert meta["processing_time_ms"] >= 0

        assert "interim_available" in meta
        assert isinstance(meta["interim_available"], bool)

    @pytest.mark.golden
    @pytest.mark.skipif(
        not os.environ.get("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for LLM testing"
    )
    def test_llm_fallback_on_failure(self, ambiguous_content):
        """Test graceful fallback when LLM fails."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        # Run with invalid API key to force failure
        result = subprocess.run(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            input=json.dumps(ambiguous_content),
            capture_output=True,
            text=True,
            timeout=5,
            env={**os.environ, "OPENAI_API_KEY": "invalid-key", "LLM_ENABLED": "true"}
        )

        assert result.returncode == 0
        response = json.loads(result.stdout)

        # Should fall back to rule-based
        output_meta = response["output"]["meta"]
        assert output_meta["classification_method"] == "rule_based"

        # Should still generate an outline
        assert len(response["output"]["outline"]) > 0