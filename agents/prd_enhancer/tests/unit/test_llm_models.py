"""Unit tests for LLM model classes and integration.

Tests PydanticAI agent creation, cost tracking, and budget enforcement
without making actual API calls.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List

# Import the agent module
try:
    from prd_enhancer import (
        LLMAgentFactory, CostTracker, PRDProcessor, AgentConfig,
        ModelConfig, ProcessingConfig, AmbiguityModel, FeatureModel
    )
except ImportError:
    pytest.skip("Agent not implemented yet - TDD phase", allow_module_level=True)


class TestCostTracker:
    """Test cost tracking and budget enforcement."""

    def test_cost_tracker_initialization(self):
        """Test CostTracker initializes with correct defaults."""
        tracker = CostTracker()

        assert tracker.max_tokens == 1000
        assert tracker.max_cost_usd == 0.05
        assert tracker.tokens_used == 0
        assert tracker.cost_usd == 0.0

    def test_cost_tracker_custom_limits(self):
        """Test CostTracker with custom limits."""
        tracker = CostTracker(max_tokens=500, max_cost_usd=0.03)

        assert tracker.max_tokens == 500
        assert tracker.max_cost_usd == 0.03

    def test_token_budget_enforcement(self):
        """Test that token usage is properly tracked and enforced."""
        tracker = CostTracker(max_tokens=100, max_cost_usd=1.0)

        # Within budget
        assert tracker.track_usage(30, 20) is True
        assert tracker.tokens_used == 50

        # Exceeds token budget
        assert tracker.track_usage(40, 20) is False
        assert tracker.tokens_used == 50  # Should not update on failure

    def test_cost_budget_enforcement(self):
        """Test that cost is properly tracked and enforced."""
        tracker = CostTracker(max_tokens=10000, max_cost_usd=0.001)

        # Within budget
        assert tracker.track_usage(100, 50) is True

        # Exceeds cost budget (large token usage)
        assert tracker.track_usage(5000, 2000) is False

    def test_cost_calculation(self):
        """Test that cost calculation is accurate."""
        tracker = CostTracker(max_tokens=2000, max_cost_usd=1.0)  # High limits to ensure success

        # Test with known values
        input_tokens = 1000
        output_tokens = 500

        expected_input_cost = input_tokens * 0.00000025
        expected_output_cost = output_tokens * 0.00000125
        expected_total = expected_input_cost + expected_output_cost

        success = tracker.track_usage(input_tokens, output_tokens)
        assert success is True

        assert abs(tracker.cost_usd - expected_total) < 0.0001

    def test_get_stats(self):
        """Test that statistics are correctly reported."""
        tracker = CostTracker(max_tokens=1000, max_cost_usd=0.05)
        tracker.track_usage(200, 100)

        stats = tracker.get_stats()

        assert stats["tokens_used"] == 300
        assert "cost_usd" in stats
        assert stats["tokens_remaining"] == 700
        assert "budget_remaining" in stats


class TestLLMAgentFactory:
    """Test LLM agent factory functionality."""

    def test_agent_creation_without_pydantic_ai(self):
        """Test graceful handling when PydanticAI is unavailable."""
        config = AgentConfig(model=ModelConfig(enabled=True))

        with patch('prd_enhancer.PYDANTIC_AI_AVAILABLE', False):
            agent = LLMAgentFactory.create_ambiguity_detector(config)
            assert agent is None

    def test_agent_creation_with_disabled_model(self):
        """Test that agents are not created when model is disabled."""
        config = AgentConfig(model=ModelConfig(enabled=False))

        agent = LLMAgentFactory.create_ambiguity_detector(config)
        assert agent is None

    @patch('prd_enhancer.PYDANTIC_AI_AVAILABLE', True)
    @patch('prd_enhancer._runtime_anthropic_model')
    @patch('prd_enhancer._runtime_agent')
    def test_ambiguity_detector_creation(self, mock_agent, mock_model):
        """Test AmbiguityDetector agent creation."""
        config = AgentConfig(model=ModelConfig(enabled=True))

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            agent = LLMAgentFactory.create_ambiguity_detector(config)

            mock_model.assert_called_once()
            mock_agent.assert_called_once()

    @patch('prd_enhancer.PYDANTIC_AI_AVAILABLE', True)
    @patch('prd_enhancer._runtime_anthropic_model')
    @patch('prd_enhancer._runtime_agent')
    def test_scope_guardian_creation(self, mock_agent, mock_model):
        """Test ScopeGuardian agent creation."""
        config = AgentConfig(model=ModelConfig(enabled=True))

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            agent = LLMAgentFactory.create_scope_guardian(config)

            mock_model.assert_called_once()
            mock_agent.assert_called_once()

    @patch('prd_enhancer.PYDANTIC_AI_AVAILABLE', True)
    @patch('prd_enhancer._runtime_anthropic_model')
    @patch('prd_enhancer._runtime_agent')
    def test_consistency_checker_creation(self, mock_agent, mock_model):
        """Test ConsistencyChecker agent creation."""
        config = AgentConfig(model=ModelConfig(enabled=True))

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            agent = LLMAgentFactory.create_consistency_checker(config)

            mock_model.assert_called_once()
            mock_agent.assert_called_once()


class TestPRDProcessorLLMIntegration:
    """Test PRDProcessor LLM method integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = AgentConfig(
            model=ModelConfig(enabled=True, max_tokens=1000),
            processing=ProcessingConfig()
        )
        self.processor = PRDProcessor(self.config)

    def test_cost_tracker_initialization(self):
        """Test that PRDProcessor initializes cost tracker."""
        assert hasattr(self.processor, 'cost_tracker')
        assert self.processor.cost_tracker.max_tokens == 1000
        assert self.processor.cost_tracker.max_cost_usd == 0.05

    @patch.object(LLMAgentFactory, 'create_ambiguity_detector')
    def test_detect_ambiguities_llm_fallback_on_no_agent(self, mock_factory):
        """Test fallback to regex when LLM agent unavailable."""
        mock_factory.return_value = None

        content = "System should be fast and user-friendly."
        result = self.processor.detect_ambiguities_llm(content)

        assert isinstance(result, list)
        assert "regex_ambiguity_detection" in self.processor.fallbacks_used

    @patch.object(LLMAgentFactory, 'create_ambiguity_detector')
    def test_detect_ambiguities_llm_budget_exceeded(self, mock_factory):
        """Test fallback when budget exceeded."""
        # Set very low budget
        self.processor.cost_tracker.max_tokens = 10

        mock_agent = Mock()
        mock_factory.return_value = mock_agent

        content = "This is a very long PRD document that should exceed the token budget for testing purposes."
        result = self.processor.detect_ambiguities_llm(content)

        # Should fall back to regex
        assert isinstance(result, list)
        assert "regex_ambiguity_detection" in self.processor.fallbacks_used

    @patch.object(LLMAgentFactory, 'create_ambiguity_detector')
    def test_detect_ambiguities_llm_success(self, mock_factory):
        """Test successful LLM ambiguity detection."""
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = """- Term: fast
- Problem: Vague performance requirement
- Fix: <200ms response time

- Term: user-friendly
- Problem: Subjective usability term
- Fix: task completed in 3 clicks"""

        mock_agent.run_sync.return_value = mock_result
        mock_factory.return_value = mock_agent

        content = "System should be fast and user-friendly."
        result = self.processor.detect_ambiguities_llm(content)

        assert len(result) == 2
        assert all(isinstance(amb, AmbiguityModel) for amb in result)
        assert result[0].term == "fast"
        assert result[1].term == "user-friendly"

    @patch.object(LLMAgentFactory, 'create_scope_guardian')
    def test_reduce_features_llm_success(self, mock_factory):
        """Test successful LLM feature reduction."""
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = """Feature: User Authentication
Value: 9
Effort: 3
Score: 3.0

Feature: Advanced Analytics
Value: 4
Effort: 8
Score: 0.5"""

        mock_agent.run_sync.return_value = mock_result
        mock_factory.return_value = mock_agent

        features = ["User Authentication", "Advanced Analytics", "Social Integration"]
        result = self.processor.reduce_features_llm(features)

        # Only features with score > 2.0 should be included
        assert len(result) == 1
        assert result[0].name == "User Authentication"
        assert result[0].priority_score == 3.0

    @patch.object(LLMAgentFactory, 'create_consistency_checker')
    def test_check_consistency_llm_no_conflicts(self, mock_factory):
        """Test consistency check with no conflicts."""
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = "NONE"

        mock_agent.run_sync.return_value = mock_result
        mock_factory.return_value = mock_agent

        features = [
            FeatureModel(name="User Auth", priority_score=3.0, value_score=9, effort_score=3),
            FeatureModel(name="Data Storage", priority_score=2.5, value_score=8, effort_score=3)
        ]
        result = self.processor.check_consistency_llm(features)

        assert result == []

    @patch.object(LLMAgentFactory, 'create_consistency_checker')
    def test_check_consistency_llm_with_conflicts(self, mock_factory):
        """Test consistency check with conflicts found."""
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = """Conflict: Real-time sync conflicts with Offline mode because they require opposite connectivity assumptions

Conflict: High security conflicts with Social sharing because security requires data isolation"""

        mock_agent.run_sync.return_value = mock_result
        mock_factory.return_value = mock_agent

        features = [
            FeatureModel(name="Real-time sync", priority_score=3.0, value_score=8, effort_score=3),
            FeatureModel(name="Offline mode", priority_score=2.5, value_score=7, effort_score=3)
        ]
        result = self.processor.check_consistency_llm(features)

        assert len(result) == 2
        assert "Real-time sync conflicts with Offline mode" in result[0]
        assert "High security conflicts with Social sharing" in result[1]


class TestBudgetEnforcement:
    """Test budget enforcement across multiple passes."""

    def test_sequential_pass_budget_enforcement(self):
        """Test that budget is enforced across sequential passes."""
        config = AgentConfig(
            model=ModelConfig(enabled=True, max_tokens=100),  # Very low budget
            processing=ProcessingConfig()
        )
        processor = PRDProcessor(config)

        # First pass should consume budget
        content = "This is a test PRD with fast, scalable, and user-friendly requirements."

        with patch.object(LLMAgentFactory, 'create_ambiguity_detector') as mock_factory:
            mock_agent = Mock()
            mock_result = Mock()
            mock_result.data = "- Term: fast\n- Problem: vague\n- Fix: <200ms"
            mock_agent.run_sync.return_value = mock_result
            mock_factory.return_value = mock_agent

            # First call should work
            result1 = processor.detect_ambiguities_llm(content)
            assert len(result1) > 0

            # Second call should fall back due to budget
            features = ["Feature 1", "Feature 2"]
            result2 = processor.reduce_features_llm(features)
            assert "keyword_feature_scoring" in processor.fallbacks_used

    def test_cost_tracking_persistence(self):
        """Test that cost tracking persists across method calls."""
        config = AgentConfig(
            model=ModelConfig(enabled=True, max_tokens=1000),
            processing=ProcessingConfig()
        )
        processor = PRDProcessor(config)

        initial_tokens = processor.cost_tracker.tokens_used
        assert initial_tokens == 0

        # Simulate token usage
        processor.cost_tracker.track_usage(100, 50)
        assert processor.cost_tracker.tokens_used == 150

        # Check that stats reflect usage
        stats = processor.cost_tracker.get_stats()
        assert stats["tokens_used"] == 150
        assert stats["tokens_remaining"] == 850