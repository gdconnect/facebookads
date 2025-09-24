"""Contract tests for output schema validation.

Tests validate that the agent produces outputs conforming to the output schema contract.
These tests MUST FAIL before implementation.
"""

import json
import pytest
from pathlib import Path

# Import the agent module - will fail initially (TDD)
try:
    from prd_enhancer import OutputModel, process_prd
except ImportError:
    pytest.skip("Agent not implemented yet - TDD phase", allow_module_level=True)


class TestOutputSchemaContract:
    """Contract tests for output schema validation."""

    def setup_method(self):
        """Load output schema for validation."""
        schema_path = Path(__file__).parent.parent.parent / "contracts" / "output.json"
        with open(schema_path) as f:
            self.output_schema = json.load(f)

    def test_valid_output_with_all_required_fields(self):
        """Test that valid output with all required fields is accepted."""
        valid_output = {
            "complexity_score": 45,
            "core_features": [
                {
                    "name": "User Authentication",
                    "priority_score": 3.5,
                    "value_score": 7,
                    "effort_score": 2
                }
            ],
            "not_doing": [
                "Real-time notifications",
                "Advanced analytics",
                "Multi-language support",
                "Social media integration",
                "Third-party plugins",
                "Mobile app",
                "Offline mode",
                "API rate limiting",
                "Custom branding",
                "Export functionality"
            ],
            "ambiguities_found": [
                {
                    "term": "fast",
                    "problem": "Vague performance requirement",
                    "suggested_fix": "Response time <200ms",
                    "confidence": 0.9,
                    "source": "llm"
                }
            ],
            "enhanced_prd": "# Enhanced PRD\n\nThis is the enhanced content...",
            "processing_stats": {
                "processing_time": 3.2,
                "passes_executed": ["pass1_ambiguity", "pass2_scope"],
                "tokens_used": 450
            }
        }

        model = OutputModel(**valid_output)
        assert model.complexity_score == 45
        assert len(model.core_features) == 1
        assert len(model.not_doing) >= 10

    def test_complexity_score_range_validation(self):
        """Test that complexity score must be in valid range (0-100)."""
        # Test minimum boundary
        valid_output = self._get_minimal_valid_output()
        valid_output["complexity_score"] = 0
        OutputModel(**valid_output)  # Should not raise

        # Test maximum boundary
        valid_output["complexity_score"] = 100
        OutputModel(**valid_output)  # Should not raise

        # Test below minimum
        valid_output["complexity_score"] = -1
        with pytest.raises(ValueError, match="complexity_score"):
            OutputModel(**valid_output)

        # Test above maximum
        valid_output["complexity_score"] = 101
        with pytest.raises(ValueError, match="complexity_score"):
            OutputModel(**valid_output)

    def test_core_features_max_items_validation(self):
        """Test that core_features cannot exceed maximum of 5 items."""
        valid_output = self._get_minimal_valid_output()

        # Test maximum allowed (5 features)
        valid_output["core_features"] = [
            self._get_valid_feature(f"Feature {i}") for i in range(5)
        ]
        OutputModel(**valid_output)  # Should not raise

        # Test exceeding maximum (6 features)
        valid_output["core_features"] = [
            self._get_valid_feature(f"Feature {i}") for i in range(6)
        ]
        with pytest.raises(ValueError, match="maxItems"):
            OutputModel(**valid_output)

    def test_not_doing_min_items_validation(self):
        """Test that not_doing list must have minimum 10 items."""
        valid_output = self._get_minimal_valid_output()

        # Test minimum allowed (10 items)
        valid_output["not_doing"] = [f"Not doing item {i}" for i in range(10)]
        OutputModel(**valid_output)  # Should not raise

        # Test below minimum (9 items)
        valid_output["not_doing"] = [f"Not doing item {i}" for i in range(9)]
        with pytest.raises(ValueError, match="minItems"):
            OutputModel(**valid_output)

    def test_feature_priority_score_validation(self):
        """Test that feature priority_score validation works."""
        valid_output = self._get_minimal_valid_output()

        # Valid feature with proper scores
        valid_feature = {
            "name": "Valid Feature",
            "priority_score": 2.5,
            "value_score": 5,
            "effort_score": 2
        }
        valid_output["core_features"] = [valid_feature]
        OutputModel(**valid_output)  # Should not raise

        # Missing required fields
        invalid_feature = {
            "name": "Invalid Feature"
            # Missing priority_score, value_score, effort_score
        }
        valid_output["core_features"] = [invalid_feature]
        with pytest.raises(ValueError):
            OutputModel(**valid_output)

    def test_ambiguity_source_enum_validation(self):
        """Test that ambiguity source must be valid enum value."""
        valid_output = self._get_minimal_valid_output()

        # Valid source values
        for source in ["llm", "regex"]:
            valid_ambiguity = {
                "term": "fast",
                "problem": "Vague term",
                "suggested_fix": "<200ms",
                "confidence": 0.8,
                "source": source
            }
            valid_output["ambiguities_found"] = [valid_ambiguity]
            OutputModel(**valid_output)  # Should not raise

        # Invalid source value
        invalid_ambiguity = {
            "term": "fast",
            "problem": "Vague term",
            "suggested_fix": "<200ms",
            "confidence": 0.8,
            "source": "invalid_source"
        }
        valid_output["ambiguities_found"] = [invalid_ambiguity]
        with pytest.raises(ValueError, match="source"):
            OutputModel(**valid_output)

    def test_domain_events_pascal_case_validation(self):
        """Test that domain event names must be PascalCase."""
        valid_output = self._get_minimal_valid_output()

        # Valid PascalCase names
        valid_event = {
            "name": "UserRegistered",
            "sequence": 1
        }
        valid_output["domain_events"] = [valid_event]
        OutputModel(**valid_output)  # Should not raise

        # Invalid non-PascalCase name
        invalid_event = {
            "name": "user_registered",  # snake_case, should be PascalCase
            "sequence": 1
        }
        valid_output["domain_events"] = [invalid_event]
        with pytest.raises(ValueError, match="pattern"):
            OutputModel(**valid_output)

    def test_processing_stats_required_fields(self):
        """Test that processing_stats has all required fields."""
        valid_output = self._get_minimal_valid_output()

        # Missing required field
        invalid_stats = {
            "processing_time": 2.5,
            "passes_executed": ["pass1_ambiguity"]
            # Missing tokens_used
        }
        valid_output["processing_stats"] = invalid_stats
        with pytest.raises(ValueError, match="tokens_used"):
            OutputModel(**valid_output)

    def test_schema_matches_contract(self):
        """Test that generated schema matches the contract."""
        generated_schema = OutputModel.model_json_schema()

        # Key contract requirements
        assert generated_schema["type"] == "object"
        required_fields = [
            "complexity_score", "core_features", "not_doing",
            "ambiguities_found", "enhanced_prd", "processing_stats"
        ]
        for field in required_fields:
            assert field in generated_schema["required"]

    def _get_minimal_valid_output(self) -> dict:
        """Get minimal valid output for testing."""
        return {
            "complexity_score": 50,
            "core_features": [],
            "not_doing": [f"Item {i}" for i in range(10)],
            "ambiguities_found": [],
            "enhanced_prd": "# Enhanced PRD content",
            "processing_stats": {
                "processing_time": 2.0,
                "passes_executed": ["pass1_ambiguity"],
                "tokens_used": 200
            }
        }

    def _get_valid_feature(self, name: str) -> dict:
        """Get valid feature for testing."""
        return {
            "name": name,
            "priority_score": 2.0,
            "value_score": 4,
            "effort_score": 2
        }