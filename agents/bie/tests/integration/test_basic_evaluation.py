"""Basic integration test for business idea evaluation"""

import json
import tempfile
from pathlib import Path

import pytest

from bie import BusinessIdeaEvaluator, ConfigModel


def test_basic_evaluation():
    """Test basic idea evaluation workflow"""
    # Create test config
    config = ConfigModel(
        model_enabled=False,  # Use deterministic evaluation
        verbose_logging=False
    )

    evaluator = BusinessIdeaEvaluator(config)

    # Create temporary markdown file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Test Business Idea

## Problem
Small businesses struggle with social media management.

## Solution
Automated social media posting and analytics platform.

## Target Customer
Small business owners with 1-50 employees.

## Revenue Model
Monthly SaaS subscription at $29, $79, and $199 tiers.
""")
        temp_file = Path(f.name)

    try:
        # Evaluate the idea
        envelope = evaluator.evaluate_idea(temp_file)

        # Verify envelope structure
        assert envelope.meta is not None
        assert envelope.input is not None
        assert envelope.output is not None
        assert envelope.error is None

        # Verify input parsing
        assert envelope.input.name == "Test Business Idea"
        assert "social media" in envelope.input.problem.lower()
        assert "automated" in envelope.input.solution.lower()

        # Verify evaluation results
        evaluated = envelope.output
        assert evaluated.raw_idea == envelope.input
        assert evaluated.business_model is not None
        assert evaluated.scalability is not None
        assert evaluated.risks is not None
        assert evaluated.scores is not None
        assert evaluated.insights is not None

        # Verify scores are in valid range
        assert 0 <= evaluated.scores.scalability_score <= 100
        assert 0 <= evaluated.scores.complexity_score <= 100
        assert 0 <= evaluated.scores.risk_score <= 100
        assert evaluated.scores.overall_grade in ['A', 'B', 'C', 'D', 'F']

        # Verify insights have required items
        assert len(evaluated.insights.critical_questions) >= 3
        assert len(evaluated.insights.quick_wins) >= 3
        assert len(evaluated.insights.red_flags) >= 3
        assert len(evaluated.insights.next_steps) >= 3

        print(f"✅ Evaluation completed successfully with grade: {evaluated.scores.overall_grade}")

    finally:
        # Clean up
        temp_file.unlink()


if __name__ == "__main__":
    test_basic_evaluation()