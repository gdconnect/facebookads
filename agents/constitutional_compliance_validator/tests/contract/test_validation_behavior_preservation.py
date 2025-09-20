"""
Validation behavior preservation test for Pydantic V1 to V2 migration.

This test will be used during migration to verify that V2 validators
produce identical behavior to V1 validators.
"""

import pytest
from pydantic import ValidationError
from brand_identity_generator import DeveloperConfig, LLMResponse, GapItem


class TestValidationBehaviorPreservation:
    """Test that V2 migration preserves exact validation behavior."""

    def test_developer_config_behavior_preservation(self):
        """Test that DeveloperConfig validation behavior is preserved."""
        # Test all validators with the same test cases as baseline

        # Valid configurations should work identically
        valid_config = DeveloperConfig(
            llm_provider="anthropic",
            llm_base_url="https://api.anthropic.com",
            request_timeout=45.0,
            max_retries=5,
            retry_backoff_factor=2.5,
            default_enhancement_level="comprehensive",
            log_level="INFO"
        )

        assert valid_config.llm_provider == "anthropic"
        assert valid_config.llm_base_url == "https://api.anthropic.com"
        assert valid_config.request_timeout == 45.0
        assert valid_config.max_retries == 5
        assert valid_config.retry_backoff_factor == 2.5
        assert valid_config.default_enhancement_level == "comprehensive"
        assert valid_config.log_level == "INFO"

        # Invalid configurations should produce identical error messages
        validation_test_cases = [
            # (field_data, expected_error_fragment)
            ({"llm_provider": "invalid"}, "Invalid LLM provider 'invalid'"),
            ({"llm_base_url": "invalid-url"}, "Invalid base URL format 'invalid-url'"),
            ({"request_timeout": 0.5}, "Request timeout must be >= 1.0 seconds, got 0.5"),
            ({"max_retries": 15}, "Max retries must be between 0 and 10, got 15"),
            ({"retry_backoff_factor": 0.5}, "Retry backoff factor must be between 1.0 and 5.0, got 0.5"),
            ({"default_enhancement_level": "invalid"}, "Invalid enhancement level 'invalid'"),
            ({"log_level": "INVALID"}, "Invalid log level 'INVALID'"),
        ]

        for field_data, expected_error in validation_test_cases:
            with pytest.raises(ValidationError) as exc_info:
                DeveloperConfig(**field_data)

            error_msg = str(exc_info.value)
            assert expected_error in error_msg, f"Expected '{expected_error}' in error message: {error_msg}"

    def test_llm_response_behavior_preservation(self):
        """Test that LLMResponse validation behavior is preserved."""
        base_data = {
            "response_type": "test",
            "content": {"test": "data"},
            "confidence_score": 0.5,
            "rationale": "test rationale",
            "processing_time": 1.0
        }

        # Valid scores should work identically
        for score in [0.0, 0.5, 1.0]:
            data = base_data.copy()
            data["confidence_score"] = score
            response = LLMResponse(**data)
            assert response.confidence_score == score

        # Invalid scores should produce identical Field constraint errors
        for invalid_score in [-0.1, 1.1]:
            with pytest.raises(ValidationError) as exc_info:
                data = base_data.copy()
                data["confidence_score"] = invalid_score
                LLMResponse(**data)

            error_msg = str(exc_info.value)
            if invalid_score < 0:
                assert "Input should be greater than or equal to 0" in error_msg
            else:
                assert "Input should be less than or equal to 1" in error_msg

    def test_gap_item_behavior_preservation(self):
        """Test that GapItem validation behavior is preserved."""
        base_data = {
            "element": "test element",
            "impact": "medium",
            "description": "test description",
            "estimated_improvement": 0.5
        }

        # Valid impacts should work identically
        for impact in ["low", "medium", "high", "critical"]:
            data = base_data.copy()
            data["impact"] = impact
            gap_item = GapItem(**data)
            assert gap_item.impact == impact

        # Invalid impact should produce identical Field pattern error
        with pytest.raises(ValidationError) as exc_info:
            data = base_data.copy()
            data["impact"] = "invalid"
            GapItem(**data)

        error_msg = str(exc_info.value)
        assert "String should match pattern" in error_msg
        assert "string_pattern_mismatch" in error_msg

    def test_default_values_preservation(self):
        """Test that default values work identically after migration."""
        config = DeveloperConfig()

        # Check all defaults are preserved exactly
        assert config.llm_provider == "openai"
        assert config.llm_base_url is None
        assert config.request_timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_backoff_factor == 2.0
        assert config.default_enhancement_level == "moderate"
        assert config.log_level == "INFO"

    def test_multiple_errors_preservation(self):
        """Test that multiple validation errors produce identical messages."""
        with pytest.raises(ValidationError) as exc_info:
            DeveloperConfig(
                llm_provider="invalid",
                request_timeout=0.5,
                max_retries=15
            )

        error_msg = str(exc_info.value)
        # Should contain all three error messages
        assert "Invalid LLM provider" in error_msg
        assert "Request timeout must be >= 1.0" in error_msg
        assert "Max retries must be between 0 and 10" in error_msg

    def test_edge_case_preservation(self):
        """Test edge cases work identically after migration."""
        # Test boundary values
        config = DeveloperConfig(
            request_timeout=1.0,  # Minimum valid timeout
            max_retries=0,        # Minimum valid retries
            retry_backoff_factor=1.0  # Minimum valid backoff
        )

        assert config.request_timeout == 1.0
        assert config.max_retries == 0
        assert config.retry_backoff_factor == 1.0

        # Test maximum boundary values
        config = DeveloperConfig(
            max_retries=10,       # Maximum valid retries
            retry_backoff_factor=5.0  # Maximum valid backoff
        )

        assert config.max_retries == 10
        assert config.retry_backoff_factor == 5.0