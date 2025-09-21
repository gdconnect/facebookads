"""Contract tests for envelope schema validation.

These tests validate the Agent Envelope structure against the JSON schema.
Tests MUST FAIL until T020 (Agent Envelope implementation) is complete.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

# These imports will fail until implementation
try:
    from article_outline_generator import (
        AgentEnvelope,
        EnvelopeMeta,
        ErrorModel,
        InputModel,
        OutputModel
    )
except ImportError:
    AgentEnvelope = None
    EnvelopeMeta = None
    ErrorModel = None
    InputModel = None
    OutputModel = None


class TestEnvelopeSchemaContract:
    """Test Agent Envelope compliance with schema.envelope.json"""

    @pytest.fixture
    def envelope_schema(self):
        """Load envelope schema for validation."""
        schema_path = Path(__file__).parent.parent.parent / "schemas" / "schema.envelope.json"
        with open(schema_path, "r") as f:
            return json.load(f)

    @pytest.mark.contract
    def test_envelope_models_exist(self):
        """Test that envelope model classes exist."""
        assert AgentEnvelope is not None, "AgentEnvelope not implemented yet"
        assert EnvelopeMeta is not None, "EnvelopeMeta not implemented yet"
        assert ErrorModel is not None, "ErrorModel not implemented yet"

    @pytest.mark.contract
    def test_envelope_meta_valid(self):
        """Test EnvelopeMeta accepts valid metadata."""
        if EnvelopeMeta is None:
            pytest.skip("EnvelopeMeta not implemented")

        data = {
            "agent": "article_outline_generator",
            "version": "1.0.0",
            "trace_id": "test-trace-123",
            "ts": datetime.now(),
            "brand_token": "default",
            "hash": "a" * 64,  # 64-character hex string
            "cost": {
                "tokens_in": 150,
                "tokens_out": 800,
                "usd": 0.002,
                "llm_calls": 1
            },
            "classification_enhanced": True,
            "fallback_used": False,
            "prompt_id": "test-prompt",
            "prompt_hash": "b" * 64
        }

        meta = EnvelopeMeta(**data)
        assert meta.agent == "article_outline_generator"
        assert meta.version == "1.0.0"
        assert meta.cost.tokens_in == 150

    @pytest.mark.contract
    def test_envelope_meta_agent_validation(self):
        """Test EnvelopeMeta validates agent name."""
        if EnvelopeMeta is None:
            pytest.skip("EnvelopeMeta not implemented")

        base_data = {
            "agent": "article_outline_generator",
            "version": "1.0.0",
            "trace_id": "test-trace-123",
            "ts": datetime.now(),
            "brand_token": "default",
            "hash": "a" * 64,
            "cost": {"tokens_in": 0, "tokens_out": 0, "usd": 0.0, "llm_calls": 0}
        }

        # Valid agent name
        meta = EnvelopeMeta(**base_data)
        assert meta.agent == "article_outline_generator"

        # Invalid agent name (should be enforced by const constraint)
        invalid_data = base_data.copy()
        invalid_data["agent"] = "wrong_agent"
        with pytest.raises(ValueError):
            EnvelopeMeta(**invalid_data)

    @pytest.mark.contract
    def test_envelope_meta_version_format(self):
        """Test EnvelopeMeta validates version format."""
        if EnvelopeMeta is None:
            pytest.skip("EnvelopeMeta not implemented")

        base_data = {
            "agent": "article_outline_generator",
            "version": "1.0.0",
            "trace_id": "test-trace-123",
            "ts": datetime.now(),
            "brand_token": "default",
            "hash": "a" * 64,
            "cost": {"tokens_in": 0, "tokens_out": 0, "usd": 0.0, "llm_calls": 0}
        }

        # Valid semver versions
        for version in ["1.0.0", "2.1.3", "0.0.1", "10.20.30"]:
            data = base_data.copy()
            data["version"] = version
            meta = EnvelopeMeta(**data)
            assert meta.version == version

        # Invalid version formats
        for invalid_version in ["1.0", "v1.0.0", "1.0.0-alpha", "1.0.0.0"]:
            data = base_data.copy()
            data["version"] = invalid_version
            with pytest.raises(ValueError):
                EnvelopeMeta(**data)

    @pytest.mark.contract
    def test_envelope_meta_hash_format(self):
        """Test EnvelopeMeta validates hash format."""
        if EnvelopeMeta is None:
            pytest.skip("EnvelopeMeta not implemented")

        base_data = {
            "agent": "article_outline_generator",
            "version": "1.0.0",
            "trace_id": "test-trace-123",
            "ts": datetime.now(),
            "brand_token": "default",
            "hash": "a" * 64,
            "cost": {"tokens_in": 0, "tokens_out": 0, "usd": 0.0, "llm_calls": 0}
        }

        # Valid 64-character hex hash
        valid_hash = "abcdef0123456789" * 4  # 64 chars
        data = base_data.copy()
        data["hash"] = valid_hash
        meta = EnvelopeMeta(**data)
        assert meta.hash == valid_hash

        # Invalid hash formats
        invalid_hashes = [
            "short",  # too short
            "g" * 64,  # invalid hex character
            "a" * 63,  # wrong length
            "a" * 65   # wrong length
        ]

        for invalid_hash in invalid_hashes:
            data = base_data.copy()
            data["hash"] = invalid_hash
            with pytest.raises(ValueError):
                EnvelopeMeta(**data)

    @pytest.mark.contract
    def test_envelope_meta_enhanced_cost_tracking(self):
        """Test EnvelopeMeta validates enhanced cost structure."""
        if EnvelopeMeta is None:
            pytest.skip("EnvelopeMeta not implemented")

        base_data = {
            "agent": "article_outline_generator",
            "version": "1.0.0",
            "trace_id": "test-trace-123",
            "ts": datetime.now(),
            "brand_token": "default",
            "hash": "a" * 64,
            "cost": {"tokens_in": 100, "tokens_out": 200, "usd": 0.005, "llm_calls": 1}
        }

        # Valid enhanced cost structure
        meta = EnvelopeMeta(**base_data)
        assert meta.cost.llm_calls == 1
        assert meta.cost.tokens_in == 100
        assert meta.cost.usd == 0.005

        # Test LLM calls limit validation (max 2)
        for invalid_calls in [-1, 3, 10]:
            data = base_data.copy()
            data["cost"]["llm_calls"] = invalid_calls
            with pytest.raises(ValueError):
                EnvelopeMeta(**data)

        # Test classification metadata with valid cost
        enhanced_data = {
            "agent": "article_outline_generator",
            "version": "1.0.0",
            "trace_id": "test-trace-123",
            "ts": datetime.now(),
            "brand_token": "default",
            "hash": "a" * 64,
            "cost": {"tokens_in": 100, "tokens_out": 200, "usd": 0.005, "llm_calls": 1},
            "classification_enhanced": True,
            "fallback_used": False
        }
        meta = EnvelopeMeta(**enhanced_data)
        assert meta.classification_enhanced is True
        assert meta.fallback_used is False

    @pytest.mark.contract
    def test_error_model_valid(self):
        """Test ErrorModel accepts valid error data."""
        if ErrorModel is None:
            pytest.skip("ErrorModel not implemented")

        data = {
            "code": "VALIDATION_ERROR",
            "message": "Input validation failed",
            "details": {
                "field": "content",
                "reason": "Content cannot be empty"
            }
        }

        error = ErrorModel(**data)
        assert error.code == "VALIDATION_ERROR"
        assert error.message == "Input validation failed"
        assert error.details["field"] == "content"

    @pytest.mark.contract
    def test_error_model_minimal(self):
        """Test ErrorModel works with minimal required fields."""
        if ErrorModel is None:
            pytest.skip("ErrorModel not implemented")

        data = {
            "code": "GENERIC_ERROR",
            "message": "Something went wrong"
        }

        error = ErrorModel(**data)
        assert error.code == "GENERIC_ERROR"
        assert error.message == "Something went wrong"
        assert error.details is None  # optional field

    @pytest.mark.contract
    def test_agent_envelope_success_case(self):
        """Test AgentEnvelope for successful execution."""
        if (AgentEnvelope is None or EnvelopeMeta is None or
            InputModel is None or OutputModel is None):
            pytest.skip("Envelope models not implemented")

        # This is a complex test that will fail until all models are implemented
        meta_data = {
            "agent": "article_outline_generator",
            "version": "1.0.0",
            "trace_id": "test-trace-123",
            "ts": datetime.now(),
            "brand_token": "default",
            "hash": "a" * 64,
            "cost": {"tokens_in": 150, "tokens_out": 800, "usd": 0.002, "llm_calls": 1}
        }

        input_data = {
            "content": "# Test Article\n\nContent description."
        }

        output_data = {
            "meta": {
                "content_type": "article",
                "detected_language": "en",
                "depth": 3,
                "sections_count": 1,
                "generated_at": datetime.now()
            },
            "outline": [
                {"title": "Introduction", "level": 1}
            ]
        }

        envelope_data = {
            "meta": meta_data,
            "input": input_data,
            "output": output_data,
            "error": None
        }

        envelope = AgentEnvelope(**envelope_data)
        assert envelope.meta.agent == "article_outline_generator"
        assert envelope.input.content.startswith("# Test Article")
        assert len(envelope.output.outline) == 1
        assert envelope.error is None

    @pytest.mark.contract
    def test_agent_envelope_error_case(self):
        """Test AgentEnvelope for error case."""
        if (AgentEnvelope is None or EnvelopeMeta is None or
            InputModel is None or ErrorModel is None):
            pytest.skip("Envelope models not implemented")

        meta_data = {
            "agent": "article_outline_generator",
            "version": "1.0.0",
            "trace_id": "test-trace-123",
            "ts": datetime.now(),
            "brand_token": "default",
            "hash": "a" * 64,
            "cost": {"tokens_in": 50, "tokens_out": 0, "usd": 0.001, "llm_calls": 0}
        }

        input_data = {
            "content": ""  # Invalid empty content
        }

        error_data = {
            "code": "VALIDATION_ERROR",
            "message": "Content cannot be empty"
        }

        envelope_data = {
            "meta": meta_data,
            "input": input_data,
            "output": None,
            "error": error_data
        }

        envelope = AgentEnvelope(**envelope_data)
        assert envelope.meta.agent == "article_outline_generator"
        assert envelope.output is None
        assert envelope.error.code == "VALIDATION_ERROR"

    @pytest.mark.contract
    def test_schema_compliance(self, envelope_schema):
        """Test that AgentEnvelope generates schema matching schema.envelope.json."""
        if AgentEnvelope is None:
            pytest.skip("AgentEnvelope not implemented")

        generated_schema = AgentEnvelope.model_json_schema()

        # Key schema properties should match
        assert "meta" in generated_schema["properties"]
        assert "input" in generated_schema["properties"]
        assert "output" in generated_schema["properties"]
        assert "error" in generated_schema["properties"]

        # Required fields should match
        expected_required = envelope_schema.get("required", [])
        actual_required = generated_schema.get("required", [])
        assert set(expected_required) == set(actual_required)