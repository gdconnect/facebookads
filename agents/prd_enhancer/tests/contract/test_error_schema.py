"""Contract tests for error schema validation.

Tests validate that the agent produces error outputs conforming to the error schema contract.
These tests MUST FAIL before implementation.
"""

import json
import pytest
from pathlib import Path

# Import the agent module - will fail initially (TDD)
try:
    from prd_enhancer import ErrorModel
except ImportError:
    pytest.skip("Agent not implemented yet - TDD phase", allow_module_level=True)


class TestErrorSchemaContract:
    """Contract tests for error schema validation."""

    def test_valid_error_with_required_fields(self):
        """Test that valid error with required fields is accepted."""
        valid_error = {
            "code": "FILE_NOT_FOUND",
            "message": "The specified PRD file could not be found"
        }

        error = ErrorModel(**valid_error)
        assert error.code == "FILE_NOT_FOUND"
        assert error.message == "The specified PRD file could not be found"

    def test_valid_error_with_details(self):
        """Test that valid error with optional details is accepted."""
        valid_error = {
            "code": "VALIDATION_ERROR",
            "message": "Input validation failed",
            "details": {
                "field": "file_path",
                "constraint": "must_be_markdown",
                "provided_value": "document.txt"
            }
        }

        error = ErrorModel(**valid_error)
        assert error.code == "VALIDATION_ERROR"
        assert error.details is not None
        assert error.details["field"] == "file_path"

    def test_all_valid_error_codes(self):
        """Test that all defined error codes are accepted."""
        valid_codes = [
            "INVALID_INPUT",
            "FILE_NOT_FOUND",
            "PARSE_ERROR",
            "PROCESSING_TIMEOUT",
            "LLM_ERROR",
            "BUDGET_EXCEEDED",
            "VALIDATION_ERROR"
        ]

        for code in valid_codes:
            valid_error = {
                "code": code,
                "message": f"Test message for {code}"
            }
            error = ErrorModel(**valid_error)
            assert error.code == code

    def test_invalid_error_code(self):
        """Test that invalid error codes are rejected."""
        invalid_error = {
            "code": "UNKNOWN_ERROR",  # Not in enum
            "message": "Some error occurred"
        }

        with pytest.raises(ValueError, match="code"):
            ErrorModel(**invalid_error)

    def test_missing_required_code(self):
        """Test that error without code is rejected."""
        invalid_error = {
            "message": "Error message without code"
            # Missing required code field
        }

        with pytest.raises(ValueError, match="code"):
            ErrorModel(**invalid_error)

    def test_missing_required_message(self):
        """Test that error without message is rejected."""
        invalid_error = {
            "code": "FILE_NOT_FOUND"
            # Missing required message field
        }

        with pytest.raises(ValueError, match="message"):
            ErrorModel(**invalid_error)

    def test_empty_message_rejected(self):
        """Test that empty message is rejected."""
        invalid_error = {
            "code": "PARSE_ERROR",
            "message": ""  # Empty string should be rejected
        }

        with pytest.raises(ValueError, match="message"):
            ErrorModel(**invalid_error)

    def test_specific_error_scenarios(self):
        """Test specific error scenarios with appropriate details."""
        # File not found error
        file_error = {
            "code": "FILE_NOT_FOUND",
            "message": "PRD file not found at specified path",
            "details": {
                "file_path": "/path/to/missing.md",
                "attempted_at": "2025-09-23T10:30:00Z"
            }
        }
        ErrorModel(**file_error)

        # Validation error
        validation_error = {
            "code": "VALIDATION_ERROR",
            "message": "Input validation failed",
            "details": {
                "field": "config.model.timeout_s",
                "constraint": "maximum 10 seconds",
                "provided_value": 15
            }
        }
        ErrorModel(**validation_error)

        # LLM error
        llm_error = {
            "code": "LLM_ERROR",
            "message": "LLM API call failed",
            "details": {
                "provider": "anthropic",
                "status_code": 429,
                "retry_after": 60
            }
        }
        ErrorModel(**llm_error)

        # Budget exceeded error
        budget_error = {
            "code": "BUDGET_EXCEEDED",
            "message": "Processing budget exceeded",
            "details": {
                "budget_type": "tokens",
                "limit": 1000,
                "used": 1200
            }
        }
        ErrorModel(**budget_error)

        # Processing timeout error
        timeout_error = {
            "code": "PROCESSING_TIMEOUT",
            "message": "Processing timed out after 10 seconds",
            "details": {
                "timeout_limit": 10,
                "elapsed_time": 12.5,
                "last_operation": "llm_pass_2"
            }
        }
        ErrorModel(**timeout_error)

    def test_details_can_be_complex_object(self):
        """Test that details field can contain complex nested objects."""
        complex_error = {
            "code": "PARSE_ERROR",
            "message": "Failed to parse markdown structure",
            "details": {
                "parser_info": {
                    "library": "markdown",
                    "version": "3.5.0"
                },
                "errors": [
                    {
                        "line": 15,
                        "column": 3,
                        "issue": "Invalid header syntax"
                    },
                    {
                        "line": 42,
                        "column": 1,
                        "issue": "Unclosed code block"
                    }
                ],
                "suggested_fixes": [
                    "Fix header on line 15",
                    "Close code block before line 42"
                ]
            }
        }

        error = ErrorModel(**complex_error)
        assert error.details is not None
        assert "parser_info" in error.details
        assert len(error.details["errors"]) == 2

    def test_schema_matches_contract_expectations(self):
        """Test that generated schema matches expected contract structure."""
        generated_schema = ErrorModel.model_json_schema()

        # Key requirements
        assert generated_schema["type"] == "object"
        assert "code" in generated_schema["required"]
        assert "message" in generated_schema["required"]

        # Code should be enum with valid values
        code_property = generated_schema["properties"]["code"]
        expected_codes = [
            "INVALID_INPUT", "FILE_NOT_FOUND", "PARSE_ERROR",
            "PROCESSING_TIMEOUT", "LLM_ERROR", "BUDGET_EXCEEDED", "VALIDATION_ERROR"
        ]
        assert "enum" in code_property
        for code in expected_codes:
            assert code in code_property["enum"]

        # Message should have minimum length
        message_property = generated_schema["properties"]["message"]
        assert message_property["type"] == "string"
        assert "minLength" in message_property
        assert message_property["minLength"] >= 1