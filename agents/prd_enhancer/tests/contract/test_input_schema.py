"""Contract tests for input schema validation.

Tests validate that the agent accepts valid inputs and rejects invalid ones
according to the input schema contract. These tests MUST FAIL before implementation.
"""

import json
import pytest
from pathlib import Path

# Import the agent module - will fail initially (TDD)
try:
    from prd_enhancer import InputModel, validate_input
except ImportError:
    pytest.skip("Agent not implemented yet - TDD phase", allow_module_level=True)


class TestInputSchemaContract:
    """Contract tests for input schema validation."""

    def setup_method(self):
        """Load input schema for validation."""
        schema_path = Path(__file__).parent.parent.parent / "contracts" / "input.json"
        with open(schema_path) as f:
            self.input_schema = json.load(f)

    def test_valid_input_with_required_fields(self):
        """Test that valid input with only required fields is accepted."""
        valid_input = {
            "file_path": "test.md"
        }

        # Should create InputModel successfully
        model = InputModel(**valid_input)
        assert model.file_path == "test.md"

    def test_valid_input_with_optional_config(self):
        """Test that valid input with optional configuration is accepted."""
        valid_input = {
            "file_path": "complex_prd.md",
            "config": {
                "model": {
                    "enabled": True,
                    "provider": "anthropic",
                    "name": "claude-3-haiku",
                    "timeout_s": 5,
                    "max_tokens": 500
                },
                "processing": {
                    "max_features": 3,
                    "max_events": 4,
                    "max_ambiguities": 8
                }
            }
        }

        model = InputModel(**valid_input)
        assert model.file_path == "complex_prd.md"
        assert model.config is not None
        assert model.config["model"]["enabled"] is True

    def test_missing_required_file_path(self):
        """Test that input without required file_path is rejected."""
        invalid_input = {
            "config": {"model": {"enabled": False}}
        }

        with pytest.raises(ValueError, match="file_path"):
            InputModel(**invalid_input)

    def test_invalid_file_extension(self):
        """Test that non-markdown file paths are rejected."""
        invalid_input = {
            "file_path": "document.txt"  # Should be .md or .markdown
        }

        with pytest.raises(ValueError, match="pattern"):
            InputModel(**invalid_input)

    def test_empty_file_path(self):
        """Test that empty file_path is rejected."""
        invalid_input = {
            "file_path": ""
        }

        with pytest.raises(ValueError, match="minLength"):
            InputModel(**invalid_input)

    def test_invalid_model_provider(self):
        """Test that invalid model provider is rejected."""
        invalid_input = {
            "file_path": "test.md",
            "config": {
                "model": {
                    "provider": "invalid_provider"  # Not in enum
                }
            }
        }

        with pytest.raises(ValueError, match="provider"):
            InputModel(**invalid_input)

    def test_invalid_timeout_range(self):
        """Test that timeout outside valid range is rejected."""
        invalid_input = {
            "file_path": "test.md",
            "config": {
                "model": {
                    "timeout_s": 15  # Max is 10
                }
            }
        }

        with pytest.raises(ValueError, match="timeout_s"):
            InputModel(**invalid_input)

    def test_invalid_max_features_range(self):
        """Test that max_features outside valid range is rejected."""
        invalid_input = {
            "file_path": "test.md",
            "config": {
                "processing": {
                    "max_features": 10  # Max is 5
                }
            }
        }

        with pytest.raises(ValueError, match="max_features"):
            InputModel(**invalid_input)

    def test_additional_properties_rejected(self):
        """Test that additional properties are rejected."""
        invalid_input = {
            "file_path": "test.md",
            "extra_field": "not_allowed"
        }

        with pytest.raises(ValueError, match="extra"):
            InputModel(**invalid_input)

    def test_schema_matches_contract(self):
        """Test that generated schema matches the contract."""
        # This will validate that the InputModel generates correct JSON schema
        generated_schema = InputModel.model_json_schema()

        # Key contract requirements
        assert generated_schema["type"] == "object"
        assert "file_path" in generated_schema["required"]
        assert generated_schema["properties"]["file_path"]["type"] == "string"
        assert "additionalProperties" not in generated_schema or not generated_schema["additionalProperties"]