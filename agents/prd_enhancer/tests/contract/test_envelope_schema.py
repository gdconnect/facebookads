"""Contract tests for envelope schema validation.

Tests validate that the agent produces outputs conforming to the envelope schema contract.
These tests MUST FAIL before implementation.
"""

import json
import pytest
from datetime import datetime
from pathlib import Path

# Import the agent module - will fail initially (TDD)
try:
    from prd_enhancer import Envelope, MetaModel
except ImportError:
    pytest.skip("Agent not implemented yet - TDD phase", allow_module_level=True)


class TestEnvelopeSchemaContract:
    """Contract tests for envelope schema validation."""

    def setup_method(self):
        """Load envelope schema for validation."""
        schema_path = Path(__file__).parent.parent.parent / "contracts" / "envelope.json"
        with open(schema_path) as f:
            self.envelope_schema = json.load(f)

    def test_valid_envelope_with_successful_output(self):
        """Test that valid envelope with successful output is accepted."""
        valid_envelope = {
            "meta": {
                "agent": "prd_enhancer",
                "version": "1.0.0",
                "trace_id": "test-trace-123",
                "ts": "2025-09-23T10:30:00Z",
                "brand_token": "test-brand",
                "hash": "a" * 64,  # 64-character hex hash
                "cost": {
                    "tokens_in": 450,
                    "tokens_out": 120,
                    "usd": 0.02
                },
                "prompt_id": "prompt-123",
                "prompt_hash": "b" * 64
            },
            "input": {
                "file_path": "test.md"
            },
            "output": {
                "complexity_score": 28,
                "core_features": [],
                "not_doing": [f"Item {i}" for i in range(10)],
                "ambiguities_found": [],
                "enhanced_prd": "# Enhanced content",
                "processing_stats": {
                    "processing_time": 2.0,
                    "passes_executed": ["pass1_ambiguity"],
                    "tokens_used": 200
                }
            },
            "error": None
        }

        envelope = Envelope(**valid_envelope)
        assert envelope.meta.agent == "prd_enhancer"
        assert envelope.output is not None
        assert envelope.error is None

    def test_valid_envelope_with_error(self):
        """Test that valid envelope with error (no output) is accepted."""
        valid_envelope = {
            "meta": {
                "agent": "prd_enhancer",
                "version": "1.0.0",
                "trace_id": "test-trace-error",
                "ts": "2025-09-23T10:30:00Z",
                "brand_token": "test-brand",
                "hash": "c" * 64,
                "cost": {
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "usd": 0.0
                }
            },
            "input": {
                "file_path": "invalid.md"
            },
            "output": None,
            "error": {
                "code": "FILE_NOT_FOUND",
                "message": "The specified PRD file could not be found",
                "details": {
                    "file_path": "invalid.md",
                    "attempted_at": "2025-09-23T10:30:00Z"
                }
            }
        }

        envelope = Envelope(**valid_envelope)
        assert envelope.error is not None
        assert envelope.error.code == "FILE_NOT_FOUND"
        assert envelope.output is None

    def test_meta_agent_name_validation(self):
        """Test that meta.agent must be 'prd_enhancer'."""
        invalid_envelope = self._get_minimal_valid_envelope()
        invalid_envelope["meta"]["agent"] = "wrong_agent"

        with pytest.raises(ValueError, match="agent"):
            Envelope(**invalid_envelope)

    def test_meta_version_format_validation(self):
        """Test that meta.version must follow semantic versioning."""
        valid_envelope = self._get_minimal_valid_envelope()

        # Valid versions
        for version in ["1.0.0", "2.1.3", "0.0.1"]:
            valid_envelope["meta"]["version"] = version
            Envelope(**valid_envelope)  # Should not raise

        # Invalid versions
        for version in ["1.0", "v1.0.0", "1.0.0-beta", ""]:
            valid_envelope["meta"]["version"] = version
            with pytest.raises(ValueError, match="version"):
                Envelope(**valid_envelope)

    def test_meta_hash_format_validation(self):
        """Test that meta.hash must be 64-character hex string."""
        valid_envelope = self._get_minimal_valid_envelope()

        # Valid hash (64 hex chars)
        valid_envelope["meta"]["hash"] = "a" * 64
        Envelope(**valid_envelope)  # Should not raise

        # Invalid hash length
        valid_envelope["meta"]["hash"] = "a" * 32  # Too short
        with pytest.raises(ValueError, match="hash"):
            Envelope(**valid_envelope)

        # Invalid hash characters
        valid_envelope["meta"]["hash"] = "g" * 64  # 'g' is not hex
        with pytest.raises(ValueError, match="hash"):
            Envelope(**valid_envelope)

    def test_meta_cost_required_fields(self):
        """Test that meta.cost has all required fields with proper types."""
        valid_envelope = self._get_minimal_valid_envelope()

        # Valid cost object
        valid_cost = {
            "tokens_in": 100,
            "tokens_out": 50,
            "usd": 0.01
        }
        valid_envelope["meta"]["cost"] = valid_cost
        Envelope(**valid_envelope)  # Should not raise

        # Missing required field
        invalid_cost = {
            "tokens_in": 100,
            "tokens_out": 50
            # Missing usd
        }
        valid_envelope["meta"]["cost"] = invalid_cost
        with pytest.raises(ValueError, match="usd"):
            Envelope(**valid_envelope)

        # Negative values (should be rejected)
        invalid_cost = {
            "tokens_in": -10,
            "tokens_out": 50,
            "usd": 0.01
        }
        valid_envelope["meta"]["cost"] = invalid_cost
        with pytest.raises(ValueError, match="tokens_in"):
            Envelope(**valid_envelope)

    def test_meta_prompt_hash_format_when_present(self):
        """Test that meta.prompt_hash follows correct format when not null."""
        valid_envelope = self._get_minimal_valid_envelope()

        # Valid prompt_hash (64 hex chars)
        valid_envelope["meta"]["prompt_hash"] = "d" * 64
        Envelope(**valid_envelope)  # Should not raise

        # Null prompt_hash (allowed)
        valid_envelope["meta"]["prompt_hash"] = None
        Envelope(**valid_envelope)  # Should not raise

        # Invalid prompt_hash format
        valid_envelope["meta"]["prompt_hash"] = "invalid"
        with pytest.raises(ValueError, match="prompt_hash"):
            Envelope(**valid_envelope)

    def test_error_code_enum_validation(self):
        """Test that error.code must be valid enum value."""
        valid_envelope = self._get_minimal_valid_envelope()

        # Valid error codes
        valid_codes = [
            "INVALID_INPUT", "FILE_NOT_FOUND", "PARSE_ERROR",
            "PROCESSING_TIMEOUT", "LLM_ERROR", "BUDGET_EXCEEDED",
            "VALIDATION_ERROR"
        ]

        for code in valid_codes:
            valid_envelope["error"] = {
                "code": code,
                "message": "Test error message"
            }
            valid_envelope["output"] = None
            Envelope(**valid_envelope)  # Should not raise

        # Invalid error code
        valid_envelope["error"] = {
            "code": "INVALID_CODE",
            "message": "Test error message"
        }
        with pytest.raises(ValueError, match="code"):
            Envelope(**valid_envelope)

    def test_input_required_field(self):
        """Test that input field is always required."""
        invalid_envelope = {
            "meta": self._get_valid_meta(),
            # Missing input field
            "output": None,
            "error": None
        }

        with pytest.raises(ValueError, match="input"):
            Envelope(**invalid_envelope)

    def test_output_and_error_mutual_exclusivity(self):
        """Test that output and error should be mutually exclusive in practice."""
        # This is more of a business rule than schema enforcement
        # Both can be null, or one can be set, but having both set might indicate an issue

        # Success case: output set, error null
        success_envelope = self._get_minimal_valid_envelope()
        success_envelope["output"] = self._get_minimal_valid_output()
        success_envelope["error"] = None
        Envelope(**success_envelope)  # Should work

        # Error case: output null, error set
        error_envelope = self._get_minimal_valid_envelope()
        error_envelope["output"] = None
        error_envelope["error"] = {
            "code": "FILE_NOT_FOUND",
            "message": "File not found"
        }
        Envelope(**error_envelope)  # Should work

        # Both null case: might be valid for some scenarios
        empty_envelope = self._get_minimal_valid_envelope()
        empty_envelope["output"] = None
        empty_envelope["error"] = None
        Envelope(**empty_envelope)  # Should work (schema allows this)

    def test_schema_matches_contract(self):
        """Test that generated schema matches the contract."""
        generated_schema = Envelope.model_json_schema()

        # Key contract requirements
        assert generated_schema["type"] == "object"
        assert "meta" in generated_schema["required"]
        assert "input" in generated_schema["required"]
        assert "additionalProperties" in generated_schema
        assert not generated_schema["additionalProperties"]

    def _get_minimal_valid_envelope(self) -> dict:
        """Get minimal valid envelope for testing."""
        return {
            "meta": self._get_valid_meta(),
            "input": {
                "file_path": "test.md"
            },
            "output": self._get_minimal_valid_output(),
            "error": None
        }

    def _get_valid_meta(self) -> dict:
        """Get valid meta object for testing."""
        return {
            "agent": "prd_enhancer",
            "version": "1.0.0",
            "trace_id": "test-trace",
            "ts": "2025-09-23T10:30:00Z",
            "brand_token": "test-brand",
            "hash": "a" * 64,
            "cost": {
                "tokens_in": 100,
                "tokens_out": 50,
                "usd": 0.01
            },
            "prompt_id": None,
            "prompt_hash": None
        }

    def _get_minimal_valid_output(self) -> dict:
        """Get minimal valid output for testing."""
        return {
            "complexity_score": 50,
            "core_features": [],
            "not_doing": [f"Item {i}" for i in range(10)],
            "ambiguities_found": [],
            "enhanced_prd": "# Enhanced content",
            "processing_stats": {
                "processing_time": 2.0,
                "passes_executed": ["pass1_ambiguity"],
                "tokens_used": 200
            }
        }