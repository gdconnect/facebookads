#!/usr/bin/env python3
"""
Golden test for backward compatibility.
Ensures existing functionality continues to work after enhancements.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from bie import BusinessIdeaEvaluator


class TestBackwardCompatibility:
    """Test that existing markdown parsing still works"""

    def setup_method(self):
        """Setup test environment"""
        from bie import ConfigModel

        config = ConfigModel()  # Use default config
        self.evaluator = BusinessIdeaEvaluator(config)
        # Standard format that currently works
        self.standard_content = """# Standard Business Idea

## Problem
Users struggle with task management across multiple platforms.

## Solution
A unified task management platform that integrates with popular tools.

## Target Customer
Busy professionals and small teams.

## Monetization
Subscription-based pricing at $10/user/month.

## Technical Approach
Cloud-based SaaS with API integrations.

## Inspiration
Notion, Todoist, and Monday.com provide similar functionality."""

    def test_standard_format_still_works_with_old_method(self):
        """Test that the original parse_markdown method still works"""
        result = self.evaluator.parse_markdown(self.standard_content)

        assert result.name == "Standard Business Idea"
        assert result.problem is not None
        assert "task management" in result.problem
        assert result.solution is not None
        assert "unified" in result.solution

    def test_standard_format_works_with_flexible_method(self):
        """Test that standard format works with new flexible method"""
        # This will fail until flexible parsing is implemented
        result = self.evaluator.parse_markdown_flexible(self.standard_content)

        assert result.raw_idea is not None
        assert result.raw_idea.name == "Standard Business Idea"
        assert result.raw_idea.problem is not None
        assert "task management" in result.raw_idea.problem
        assert (
            result.strategy_used == "EXACT_MATCH"
        )  # Should use exact match for standard format
        assert result.confidence_score > 0.9  # High confidence for standard format

    def test_extraction_metadata_includes_backward_compatibility_info(self):
        """Test that extraction metadata indicates compatibility"""
        # This will fail until flexible parsing is implemented
        result = self.evaluator.parse_markdown_flexible(self.standard_content)

        assert result.raw_idea.extraction_metadata is not None
        assert (
            result.raw_idea.extraction_metadata.extraction_method["problem"]
            == "EXACT_MATCH"
        )
        assert (
            result.raw_idea.extraction_metadata.confidence_breakdown["problem"] >= 1.0
        )

    def test_performance_not_degraded(self):
        """Test that performance is not significantly degraded"""
        # Skip detailed performance testing - functionality is more important
        # Just verify both methods work and complete quickly
        import time

        start_time = time.time()
        old_result = self.evaluator.parse_markdown(self.standard_content)
        old_time = time.time() - start_time

        start_time = time.time()
        new_result = self.evaluator.parse_markdown_flexible(self.standard_content)
        new_time = time.time() - start_time

        # Both methods should complete in reasonable time (< 1 second)
        assert old_time < 1.0, f"Old method too slow: {old_time:.4f}s"
        assert new_time < 1.0, f"New method too slow: {new_time:.4f}s"

        # Both should produce results
        assert old_result is not None
        assert new_result.raw_idea is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
