"""Contract tests for output schema validation.

These tests validate the OutputModel and related Pydantic classes against the JSON schema.
Tests MUST FAIL until T016-T018 (OutlineMetadata, Section, OutputModel) are complete.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError

# These imports will fail until implementation
try:
    from article_outline_generator import (
        OutputModel,
        OutlineMetadata,
        Section
    )
except ImportError:
    OutputModel = None
    OutlineMetadata = None
    Section = None


class TestOutputSchemaContract:
    """Test OutputModel compliance with schema.output.json"""

    @pytest.fixture
    def output_schema(self):
        """Load output schema for validation."""
        schema_path = Path(__file__).parent.parent.parent / "schemas" / "schema.output.json"
        with open(schema_path, "r") as f:
            return json.load(f)

    @pytest.mark.contract
    def test_output_models_exist(self):
        """Test that output model classes exist."""
        assert OutputModel is not None, "OutputModel not implemented yet"
        assert OutlineMetadata is not None, "OutlineMetadata not implemented yet"
        assert Section is not None, "Section not implemented yet"

    @pytest.mark.contract
    def test_outline_metadata_valid(self):
        """Test OutlineMetadata accepts valid data."""
        if OutlineMetadata is None:
            pytest.skip("OutlineMetadata not implemented")

        data = {
            "content_type": "article",
            "detected_language": "en",
            "depth": 3,
            "sections_count": 5,
            "generated_at": datetime.now(),
            "notes": "Generated successfully",
            "classification_confidence": 0.9,
            "classification_method": "rule_based",
            "classification_reasoning": "Instructional content detected",
            "key_indicators": ["how to", "guide", "tutorial"],
            "llm_calls_used": 0,
            "processing_time_ms": 150,
            "interim_available": False
        }

        metadata = OutlineMetadata(**data)
        assert metadata.content_type == "article"
        assert metadata.detected_language == "en"
        assert metadata.depth == 3
        assert metadata.sections_count == 5
        assert metadata.classification_confidence == 0.9
        assert metadata.classification_method == "rule_based"
        assert metadata.llm_calls_used == 0
        assert metadata.processing_time_ms == 150

    @pytest.mark.contract
    def test_outline_metadata_content_type_validation(self):
        """Test OutlineMetadata validates content_type."""
        if OutlineMetadata is None:
            pytest.skip("OutlineMetadata not implemented")

        base_data = {
            "content_type": "article",
            "detected_language": "en",
            "depth": 3,
            "sections_count": 5,
            "generated_at": datetime.now(),
            "classification_confidence": 0.8,
            "classification_method": "rule_based",
            "classification_reasoning": "Test reasoning",
            "processing_time_ms": 100
        }

        # Valid values
        for content_type in ["article", "story"]:
            data = base_data.copy()
            data["content_type"] = content_type
            metadata = OutlineMetadata(**data)
            assert metadata.content_type == content_type

        # Invalid value
        invalid_data = base_data.copy()
        invalid_data["content_type"] = "invalid"
        with pytest.raises(ValueError):
            OutlineMetadata(**invalid_data)

    @pytest.mark.contract
    def test_outline_metadata_classification_validation(self):
        """Test OutlineMetadata validates classification fields."""
        if OutlineMetadata is None:
            pytest.skip("OutlineMetadata not implemented")

        base_data = {
            "content_type": "article",
            "detected_language": "en",
            "depth": 3,
            "sections_count": 5,
            "generated_at": datetime.now(),
            "classification_confidence": 0.8,
            "classification_method": "rule_based",
            "classification_reasoning": "Test reasoning",
            "processing_time_ms": 100
        }

        # Test confidence range validation
        for invalid_confidence in [-0.1, 1.1, 2.0, -1.0]:
            data = base_data.copy()
            data["classification_confidence"] = invalid_confidence
            with pytest.raises(ValueError):
                OutlineMetadata(**data)

        # Test classification method validation
        for method in ["rule_based", "llm_single", "llm_double"]:
            data = base_data.copy()
            data["classification_method"] = method
            metadata = OutlineMetadata(**data)
            assert metadata.classification_method == method

        # Invalid classification method
        data = base_data.copy()
        data["classification_method"] = "invalid_method"
        with pytest.raises(ValueError):
            OutlineMetadata(**data)

        # Test LLM calls validation
        for invalid_calls in [-1, 3, 10]:
            data = base_data.copy()
            data["llm_calls_used"] = invalid_calls
            with pytest.raises(ValueError):
                OutlineMetadata(**data)

    @pytest.mark.contract
    def test_section_minimal_valid(self):
        """Test Section accepts minimal valid data."""
        if Section is None:
            pytest.skip("Section not implemented")

        data = {
            "title": "Introduction"
        }

        section = Section(**data)
        assert section.title == "Introduction"
        assert section.level == 1  # default
        assert section.key_points == []  # default
        assert section.subsections == []  # default

    @pytest.mark.contract
    def test_section_full_valid(self):
        """Test Section accepts all fields."""
        if Section is None:
            pytest.skip("Section not implemented")

        subsection_data = {
            "title": "Subsection",
            "level": 2,
            "summary": "A subsection summary."
        }

        data = {
            "title": "Main Section",
            "id": "main-section",
            "level": 1,
            "summary": "This is a main section with all fields.",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "word_count_estimate": 500,
            "subsections": [subsection_data]
        }

        section = Section(**data)
        assert section.title == "Main Section"
        assert section.id == "main-section"
        assert section.level == 1
        assert len(section.key_points) == 3
        assert section.word_count_estimate == 500
        assert len(section.subsections) == 1
        assert section.subsections[0].title == "Subsection"
        assert section.subsections[0].level == 2

    @pytest.mark.contract
    def test_section_level_validation(self):
        """Test Section validates level range."""
        if Section is None:
            pytest.skip("Section not implemented")

        base_data = {"title": "Test Section"}

        # Valid levels
        for level in range(1, 7):  # 1-6
            data = base_data.copy()
            data["level"] = level
            section = Section(**data)
            assert section.level == level

        # Invalid levels
        for invalid_level in [0, 7, -1, 10]:
            data = base_data.copy()
            data["level"] = invalid_level
            with pytest.raises(ValueError):
                Section(**data)

    @pytest.mark.contract
    def test_section_recursive_structure(self):
        """Test Section supports recursive subsections."""
        if Section is None:
            pytest.skip("Section not implemented")

        # Create nested structure: Level 1 -> Level 2 -> Level 3
        level3_data = {
            "title": "Level 3 Section",
            "level": 3,
            "summary": "Deeply nested section."
        }

        level2_data = {
            "title": "Level 2 Section",
            "level": 2,
            "subsections": [level3_data]
        }

        level1_data = {
            "title": "Level 1 Section",
            "level": 1,
            "subsections": [level2_data]
        }

        section = Section(**level1_data)
        assert section.level == 1
        assert len(section.subsections) == 1
        assert section.subsections[0].level == 2
        assert len(section.subsections[0].subsections) == 1
        assert section.subsections[0].subsections[0].level == 3

    @pytest.mark.contract
    def test_output_model_valid(self):
        """Test OutputModel accepts valid outline and metadata."""
        if OutputModel is None or OutlineMetadata is None or Section is None:
            pytest.skip("Output models not implemented")

        metadata_data = {
            "content_type": "article",
            "detected_language": "en",
            "depth": 2,
            "sections_count": 3,
            "generated_at": datetime.now()
        }

        sections_data = [
            {"title": "Introduction", "level": 1},
            {"title": "Main Content", "level": 1},
            {"title": "Conclusion", "level": 1}
        ]

        data = {
            "meta": metadata_data,
            "outline": sections_data
        }

        output = OutputModel(**data)
        assert len(output.outline) == 3
        assert output.meta.content_type == "article"
        assert output.meta.sections_count == 3

    @pytest.mark.contract
    def test_output_model_empty_outline_rejected(self):
        """Test OutputModel rejects empty outline."""
        if OutputModel is None or OutlineMetadata is None:
            pytest.skip("Output models not implemented")

        metadata_data = {
            "content_type": "article",
            "detected_language": "en",
            "depth": 1,
            "sections_count": 0,
            "generated_at": datetime.now()
        }

        data = {
            "meta": metadata_data,
            "outline": []
        }

        with pytest.raises(ValidationError, match="List should have at least 1 item"):
            OutputModel(**data)

    @pytest.mark.contract
    def test_schema_compliance(self, output_schema):
        """Test that OutputModel generates schema matching schema.output.json."""
        if OutputModel is None:
            pytest.skip("OutputModel not implemented")

        generated_schema = OutputModel.model_json_schema()

        # Key schema properties should match
        assert "meta" in generated_schema["properties"]
        assert "outline" in generated_schema["properties"]
        assert generated_schema["properties"]["outline"]["type"] == "array"

        # Required fields should match
        expected_required = output_schema.get("required", [])
        actual_required = generated_schema.get("required", [])
        assert set(expected_required) == set(actual_required)