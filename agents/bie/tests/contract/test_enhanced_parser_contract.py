#!/usr/bin/env python3
"""
Contract tests for enhanced markdown parser functionality.
These tests MUST FAIL initially before implementation.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from bie import BusinessIdeaEvaluator


class TestEnhancedParserContract:
    """Contract tests for flexible markdown parsing"""

    def setup_method(self):
        """Setup test environment"""
        from bie import ConfigModel

        config = ConfigModel()  # Use default config
        self.evaluator = BusinessIdeaEvaluator(config)

    def test_parse_markdown_flexible_method_exists(self):
        """Test that parse_markdown_flexible method exists"""
        # This will fail until we implement the method
        assert hasattr(self.evaluator, "parse_markdown_flexible")

    def test_flexible_extraction_config_model_exists(self):
        """Test that FlexibleExtractionConfig model exists"""
        # This will fail until we implement the model
        from bie import FlexibleExtractionConfig

        config = FlexibleExtractionConfig()
        assert hasattr(config, "fuzzy_threshold")
        assert hasattr(config, "confidence_threshold")
        assert hasattr(config, "section_mappings")

    def test_extraction_result_model_exists(self):
        """Test that ExtractionResult model exists"""
        # This will fail until we implement the model
        from bie import ExtractionResult

        result = ExtractionResult(
            strategy_used="EXACT_MATCH",
            confidence_score=0.9,
            field_confidences={},
            section_matches={},
            warnings=[],
            errors=[],
            processing_time_ms=100,
            llm_tokens_used=0,
        )
        assert result.strategy_used == "EXACT_MATCH"
        assert result.confidence_score == 0.9

    def test_parse_markdown_flexible_returns_extraction_result(self):
        """Test that parse_markdown_flexible returns ExtractionResult"""
        # This will fail until we implement the method
        content = "# Test\n## Problem\nSome problem\n## Solution\nSome solution"
        result = self.evaluator.parse_markdown_flexible(content)

        assert hasattr(result, "strategy_used")
        assert hasattr(result, "confidence_score")
        assert hasattr(result, "raw_idea")

    def test_enhanced_models_schema_compatibility(self):
        """Test that enhanced models are schema-compatible"""
        # This will fail until we implement the models
        from bie import ExtractionStrategy, FlexibleExtractionConfig

        # Test enum exists
        strategy = ExtractionStrategy.FUZZY_MATCH
        assert strategy is not None

        # Test config validation
        config = FlexibleExtractionConfig(fuzzy_threshold=0.8, confidence_threshold=0.7)
        assert 0.0 <= config.fuzzy_threshold <= 1.0
        assert 0.0 <= config.confidence_threshold <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
