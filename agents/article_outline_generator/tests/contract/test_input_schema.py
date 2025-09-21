"""Contract tests for input schema validation.

These tests validate the InputModel Pydantic class against the JSON schema.
Tests MUST FAIL until T015 (InputModel implementation) is complete.
"""

import json
import pytest
from pathlib import Path
from pydantic import ValidationError

# These imports will fail until implementation
try:
    from article_outline_generator import InputModel
except ImportError:
    InputModel = None


class TestInputSchemaContract:
    """Test InputModel compliance with schema.input.json"""

    @pytest.fixture
    def input_schema(self):
        """Load input schema for validation."""
        schema_path = Path(__file__).parent.parent.parent / "schemas" / "schema.input.json"
        with open(schema_path, "r") as f:
            return json.load(f)

    @pytest.mark.contract
    def test_input_model_exists(self):
        """Test that InputModel class exists."""
        assert InputModel is not None, "InputModel not implemented yet"

    @pytest.mark.contract
    def test_valid_minimal_input(self):
        """Test InputModel accepts minimal valid input."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        data = {
            "content": "# Test Article\n\nSample content description."
        }

        # This should pass once implemented
        model = InputModel(**data)
        assert model.content == data["content"]
        assert model.target_depth == 3  # default value
        assert model.include_word_counts is True  # default value

    @pytest.mark.contract
    def test_valid_full_input(self):
        """Test InputModel accepts all optional fields."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        data = {
            "content": "# Test Story\n\nA fictional narrative about adventure.",
            "target_depth": 4,
            "content_type_hint": "story",
            "language_hint": "en",
            "include_word_counts": False
        }

        model = InputModel(**data)
        assert model.content == data["content"]
        assert model.target_depth == 4
        assert model.content_type_hint == "story"
        assert model.language_hint == "en"
        assert model.include_word_counts is False

    @pytest.mark.contract
    def test_enhanced_input_fields(self):
        """Test InputModel accepts enhanced classification fields."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        data = {
            "content": "# Test Content\n\nSample content for testing.",
            "interim": True,
            "timeout_ms": 2000,
            "classification_method": "llm_preferred"
        }

        model = InputModel(**data)
        assert model.content == data["content"]
        assert model.interim is True
        assert model.timeout_ms == 2000
        assert model.classification_method == "llm_preferred"

    @pytest.mark.contract
    def test_empty_content_rejected(self):
        """Test that empty content is rejected."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        with pytest.raises(ValidationError, match="String should have at least 1 character"):
            InputModel(content="")

    @pytest.mark.contract
    def test_whitespace_content_rejected(self):
        """Test that whitespace-only content is rejected."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        with pytest.raises(ValueError):
            InputModel(content="   \n\t  ")

    @pytest.mark.contract
    def test_invalid_target_depth_rejected(self):
        """Test that invalid target_depth values are rejected."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        valid_content = "# Test\n\nContent"

        # Below minimum
        with pytest.raises(ValueError):
            InputModel(content=valid_content, target_depth=0)

        # Above maximum
        with pytest.raises(ValueError):
            InputModel(content=valid_content, target_depth=7)

    @pytest.mark.contract
    def test_invalid_content_type_hint_rejected(self):
        """Test that invalid content_type_hint values are rejected."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        valid_content = "# Test\n\nContent"

        with pytest.raises(ValueError):
            InputModel(content=valid_content, content_type_hint="invalid")

    @pytest.mark.contract
    def test_invalid_language_hint_rejected(self):
        """Test that invalid language_hint values are rejected."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        valid_content = "# Test\n\nContent"

        # Invalid format (not ISO 639-1)
        with pytest.raises(ValueError):
            InputModel(content=valid_content, language_hint="eng")  # should be "en"

        with pytest.raises(ValueError):
            InputModel(content=valid_content, language_hint="english")

    @pytest.mark.contract
    def test_invalid_timeout_rejected(self):
        """Test that invalid timeout_ms values are rejected."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        valid_content = "# Test\n\nContent"

        # Below minimum
        with pytest.raises(ValueError):
            InputModel(content=valid_content, timeout_ms=50)

        # Above maximum
        with pytest.raises(ValueError):
            InputModel(content=valid_content, timeout_ms=35000)

    @pytest.mark.contract
    def test_invalid_classification_method_rejected(self):
        """Test that invalid classification_method values are rejected."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        valid_content = "# Test\n\nContent"

        with pytest.raises(ValueError):
            InputModel(content=valid_content, classification_method="invalid_method")

    @pytest.mark.contract
    def test_schema_compliance(self, input_schema):
        """Test that InputModel generates schema matching schema.input.json."""
        if InputModel is None:
            pytest.skip("InputModel not implemented")

        # This will test schema generation once Pydantic models are implemented
        generated_schema = InputModel.model_json_schema()

        # Key schema properties should match
        assert "content" in generated_schema["properties"]
        assert "target_depth" in generated_schema["properties"]
        assert generated_schema["properties"]["content"]["type"] == "string"
        assert generated_schema["properties"]["target_depth"]["type"] == "integer"

        # Required fields should match
        expected_required = input_schema.get("required", [])
        actual_required = generated_schema.get("required", [])
        assert set(expected_required) == set(actual_required)