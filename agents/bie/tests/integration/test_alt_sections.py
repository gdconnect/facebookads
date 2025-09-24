#!/usr/bin/env python3
"""
Integration test for alternative section names.
This test MUST FAIL initially before implementation.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from bie import BusinessIdeaEvaluator


class TestAlternativeSectionNames:
    """Test handling of varied section naming conventions"""

    def setup_method(self):
        """Setup test environment"""
        from bie import ConfigModel

        config = ConfigModel()  # Use default config
        self.evaluator = BusinessIdeaEvaluator(config)
        self.test_content = """# FoodTech Revolution

## The Challenge We Face
Restaurants struggle with food waste, losing 30% of ingredients daily.

## Our Approach
An AI-powered inventory management system that predicts demand.

## Who We Serve
Independent restaurants with 20-150 seats.

## Revenue Strategy
SaaS model with $99/month per location.

## How It Works
IoT sensors track ingredient usage, ML models predict demand."""

    def test_alternative_problem_section_mapping(self):
        """Test that 'The Challenge We Face' maps to problem field"""
        # This will fail until flexible parsing is implemented
        result = self.evaluator.parse_markdown_flexible(self.test_content)

        assert result.raw_idea is not None
        assert result.raw_idea.problem is not None
        assert "food waste" in result.raw_idea.problem
        assert result.confidence_score > 0.7

    def test_alternative_solution_section_mapping(self):
        """Test that 'Our Approach' maps to solution field"""
        # This will fail until flexible parsing is implemented
        result = self.evaluator.parse_markdown_flexible(self.test_content)

        assert result.raw_idea is not None
        assert result.raw_idea.solution is not None
        assert "AI-powered" in result.raw_idea.solution

    def test_alternative_customer_section_mapping(self):
        """Test that 'Who We Serve' maps to target_customer field"""
        # This will fail until flexible parsing is implemented
        result = self.evaluator.parse_markdown_flexible(self.test_content)

        assert result.raw_idea is not None
        assert result.raw_idea.target_customer is not None
        assert "restaurants" in result.raw_idea.target_customer

    def test_alternative_monetization_section_mapping(self):
        """Test that 'Revenue Strategy' maps to monetization field"""
        # This will fail until flexible parsing is implemented
        result = self.evaluator.parse_markdown_flexible(self.test_content)

        assert result.raw_idea is not None
        assert result.raw_idea.monetization is not None
        assert "$99/month" in result.raw_idea.monetization

    def test_alternative_technical_section_mapping(self):
        """Test that 'How It Works' maps to technical_approach field"""
        # This will fail until flexible parsing is implemented
        result = self.evaluator.parse_markdown_flexible(self.test_content)

        assert result.raw_idea is not None
        assert result.raw_idea.technical_approach is not None
        assert "IoT sensors" in result.raw_idea.technical_approach

    def test_extraction_strategy_used(self):
        """Test that appropriate extraction strategy is recorded"""
        # This will fail until flexible parsing is implemented
        result = self.evaluator.parse_markdown_flexible(self.test_content)

        # Should use EXACT_MATCH or FUZZY_MATCH depending on section mapping
        # (EXACT_MATCH if sections are in default mappings, FUZZY_MATCH otherwise)
        assert result.strategy_used in ["EXACT_MATCH", "FUZZY_MATCH", "HYBRID"]

    def test_section_matches_recorded(self):
        """Test that section matches are properly recorded"""
        # This will fail until flexible parsing is implemented
        result = self.evaluator.parse_markdown_flexible(self.test_content)

        assert "The Challenge We Face" in result.section_matches
        assert "Our Approach" in result.section_matches
        assert result.section_matches["The Challenge We Face"] == "problem"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
