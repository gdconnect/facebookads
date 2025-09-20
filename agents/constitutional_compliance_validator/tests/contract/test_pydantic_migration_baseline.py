"""
Baseline validation behavior tests for Pydantic V1 to V2 migration.

This test suite captures the exact behavior of all validators before migration
to ensure identical behavior after migrating to V2 syntax.
"""

import pytest
from pydantic import ValidationError
from brand_identity_generator import DeveloperConfig, LLMResponse, GapItem


class TestDeveloperConfigValidationBaseline:
    """Baseline validation tests for DeveloperConfig model."""

    def test_llm_provider_validation_baseline(self):
        """Test llm_provider validator behavior before migration."""
        # Valid values
        valid_providers = ["openai", "anthropic", "local"]
        for provider in valid_providers:
            config = DeveloperConfig(llm_provider=provider)
            assert config.llm_provider == provider

        # Invalid value
        with pytest.raises(ValidationError) as exc_info:
            DeveloperConfig(llm_provider="invalid")

        error_msg = str(exc_info.value)
        assert "Invalid LLM provider 'invalid'" in error_msg
        assert "Valid options: openai, anthropic, local" in error_msg

    def test_llm_base_url_validation_baseline(self):
        """Test llm_base_url validator behavior before migration."""
        # Valid URLs
        valid_urls = [
            "https://api.openai.com",
            "http://localhost:8080",
            "https://my-custom-endpoint.com/v1",
            None  # None should be allowed
        ]
        for url in valid_urls:
            config = DeveloperConfig(llm_base_url=url)
            assert config.llm_base_url == url

        # Invalid URLs
        invalid_urls = [
            "invalid-url",
            "ftp://invalid.com",
            "not-a-url",
            "just-text"
        ]
        for url in invalid_urls:
            with pytest.raises(ValidationError) as exc_info:
                DeveloperConfig(llm_base_url=url)

            error_msg = str(exc_info.value)
            assert f"Invalid base URL format '{url}'" in error_msg
            assert "Must start with http:// or https://" in error_msg

    def test_request_timeout_validation_baseline(self):
        """Test request_timeout validator behavior before migration."""
        # Valid timeouts
        valid_timeouts = [1.0, 1.5, 30.0, 60.0, 120.0]
        for timeout in valid_timeouts:
            config = DeveloperConfig(request_timeout=timeout)
            assert config.request_timeout == timeout

        # Invalid timeouts
        invalid_timeouts = [0.0, 0.5, 0.9, -1.0]
        for timeout in invalid_timeouts:
            with pytest.raises(ValidationError) as exc_info:
                DeveloperConfig(request_timeout=timeout)

            error_msg = str(exc_info.value)
            assert f"Request timeout must be >= 1.0 seconds, got {timeout}" in error_msg

    def test_max_retries_validation_baseline(self):
        """Test max_retries validator behavior before migration."""
        # Valid retry counts
        valid_retries = [0, 1, 3, 5, 10]
        for retries in valid_retries:
            config = DeveloperConfig(max_retries=retries)
            assert config.max_retries == retries

        # Invalid retry counts
        invalid_retries = [-1, 11, 15, 100]
        for retries in invalid_retries:
            with pytest.raises(ValidationError) as exc_info:
                DeveloperConfig(max_retries=retries)

            error_msg = str(exc_info.value)
            assert f"Max retries must be between 0 and 10, got {retries}" in error_msg

    def test_retry_backoff_factor_validation_baseline(self):
        """Test retry_backoff_factor validator behavior before migration."""
        # Valid backoff factors
        valid_factors = [1.0, 1.5, 2.0, 3.0, 5.0]
        for factor in valid_factors:
            config = DeveloperConfig(retry_backoff_factor=factor)
            assert config.retry_backoff_factor == factor

        # Invalid backoff factors
        invalid_factors = [0.5, 0.9, 5.1, 10.0]
        for factor in invalid_factors:
            with pytest.raises(ValidationError) as exc_info:
                DeveloperConfig(retry_backoff_factor=factor)

            error_msg = str(exc_info.value)
            assert f"Retry backoff factor must be between 1.0 and 5.0, got {factor}" in error_msg

    def test_default_enhancement_level_validation_baseline(self):
        """Test default_enhancement_level validator behavior before migration."""
        # Valid enhancement levels
        valid_levels = ["minimal", "moderate", "comprehensive"]
        for level in valid_levels:
            config = DeveloperConfig(default_enhancement_level=level)
            assert config.default_enhancement_level == level

        # Invalid enhancement level
        with pytest.raises(ValidationError) as exc_info:
            DeveloperConfig(default_enhancement_level="invalid")

        error_msg = str(exc_info.value)
        assert "Invalid enhancement level 'invalid'" in error_msg
        assert "Valid options: minimal, moderate, comprehensive" in error_msg

    def test_log_level_validation_baseline(self):
        """Test log_level validator behavior before migration."""
        # Valid log levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        for level in valid_levels:
            config = DeveloperConfig(log_level=level)
            assert config.log_level == level

        # Invalid log level
        with pytest.raises(ValidationError) as exc_info:
            DeveloperConfig(log_level="INVALID")

        error_msg = str(exc_info.value)
        assert "Invalid log level 'INVALID'" in error_msg
        assert "Valid options: DEBUG, INFO, WARNING, ERROR" in error_msg


class TestLLMResponseValidationBaseline:
    """Baseline validation tests for LLMResponse model."""

    def test_confidence_score_validation_baseline(self):
        """Test confidence_score validator behavior before migration."""
        # Test data for LLMResponse
        base_data = {
            "response_type": "test",
            "content": {"test": "data"},
            "confidence_score": 0.5,
            "rationale": "test rationale",
            "processing_time": 1.0
        }

        # Valid confidence scores (within Field constraints)
        valid_cases = [
            (0.0, 0.0),
            (0.5, 0.5),
            (1.0, 1.0),
        ]

        for input_score, expected_score in valid_cases:
            data = base_data.copy()
            data["confidence_score"] = input_score
            response = LLMResponse(**data)
            assert response.confidence_score == expected_score

        # Invalid confidence scores (Field constraints checked first)
        invalid_cases = [-0.1, 1.1, -5.0, 10.0]
        for invalid_score in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                data = base_data.copy()
                data["confidence_score"] = invalid_score
                LLMResponse(**data)

            error_msg = str(exc_info.value)
            # Field constraints are checked before validator
            if invalid_score < 0:
                assert "Input should be greater than or equal to 0" in error_msg
            else:
                assert "Input should be less than or equal to 1" in error_msg


class TestGapItemValidationBaseline:
    """Baseline validation tests for GapItem model."""

    def test_impact_validation_baseline(self):
        """Test impact validator behavior before migration."""
        base_data = {
            "element": "test element",
            "impact": "medium",
            "description": "test description",
            "estimated_improvement": 0.5
        }

        # Valid impact values
        valid_impacts = ["low", "medium", "high", "critical"]
        for impact in valid_impacts:
            data = base_data.copy()
            data["impact"] = impact
            gap_item = GapItem(**data)
            assert gap_item.impact == impact

        # Invalid impact value (Field pattern is checked first)
        with pytest.raises(ValidationError) as exc_info:
            data = base_data.copy()
            data["impact"] = "invalid"
            GapItem(**data)

        error_msg = str(exc_info.value)
        # Field pattern constraint is checked before validator
        assert "String should match pattern" in error_msg
        assert "string_pattern_mismatch" in error_msg


class TestValidationEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are handled correctly."""
        with pytest.raises(ValidationError) as exc_info:
            DeveloperConfig(
                llm_provider="invalid",
                request_timeout=0.5,
                max_retries=15
            )

        error_msg = str(exc_info.value)
        # Should contain multiple error messages
        assert "Invalid LLM provider" in error_msg
        assert "Request timeout must be >= 1.0" in error_msg
        assert "Max retries must be between 0 and 10" in error_msg

    def test_valid_configuration_creation(self):
        """Test that a fully valid configuration can be created."""
        config = DeveloperConfig(
            llm_provider="anthropic",
            llm_base_url="https://api.anthropic.com",
            request_timeout=45.0,
            max_retries=5,
            retry_backoff_factor=2.5,
            default_enhancement_level="comprehensive",
            log_level="INFO"
        )

        assert config.llm_provider == "anthropic"
        assert config.llm_base_url == "https://api.anthropic.com"
        assert config.request_timeout == 45.0
        assert config.max_retries == 5
        assert config.retry_backoff_factor == 2.5
        assert config.default_enhancement_level == "comprehensive"
        assert config.log_level == "INFO"

    def test_default_values_work(self):
        """Test that default values work correctly."""
        config = DeveloperConfig()

        # Check all defaults are set correctly
        assert config.llm_provider == "openai"
        assert config.llm_base_url is None
        assert config.request_timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_backoff_factor == 2.0
        assert config.default_enhancement_level == "moderate"
        assert config.log_level == "INFO"