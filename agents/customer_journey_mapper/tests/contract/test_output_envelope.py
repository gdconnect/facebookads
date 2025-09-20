"""
T005: Contract test for output Agent Envelope

This test MUST FAIL until the customer_journey_mapper.py implements
Agent Envelope output format according to constitutional requirements.

Constitutional requirement: All outputs must use Agent Envelope format (Article II).
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

# This import will fail until the main module is implemented
try:
    from ...customer_journey_mapper import generate_journey_map, AgentEnvelope, AgentMeta
except ImportError:
    generate_journey_map = None
    AgentEnvelope = None
    AgentMeta = None


class TestOutputEnvelopeContract:
    """Contract tests for Agent Envelope output format"""

    @pytest.mark.contract
    def test_output_schema_exists(self):
        """Output schema file must exist and specify Agent Envelope"""
        schema_path = Path("specs/008-customer-jouney-mapper/contracts/schema.output.json")
        assert schema_path.exists(), f"Output schema not found at {schema_path}"

        with open(schema_path) as f:
            schema = json.load(f)

        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert schema["title"] == "Customer Journey Mapper Output (Agent Envelope)"
        assert "meta" in schema["required"]
        assert "input" in schema["required"]
        assert "output" in schema["required"]

    @pytest.mark.contract
    def test_agent_envelope_structure(self):
        """Generated output must conform to Agent Envelope structure"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "Small business owners seeking cloud accounting",
            "industry": "saas",
            "business_model": "B2B"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)

        # Validate Agent Envelope structure
        assert isinstance(result, dict)
        assert "meta" in result
        assert "input" in result
        assert "output" in result
        assert "error" in result

    @pytest.mark.contract
    def test_agent_meta_fields(self):
        """Agent meta must contain all required constitutional fields"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "Digital nomads looking for travel planning apps"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)
        meta = result["meta"]

        # Required meta fields (Article II)
        assert meta["agent"] == "customer_journey_mapper"
        assert "version" in meta
        assert "trace_id" in meta
        assert "ts" in meta
        assert "brand_token" in meta
        assert "hash" in meta
        assert "cost" in meta

        # Validate timestamp format (ISO-8601)
        datetime.fromisoformat(meta["ts"].replace("Z", "+00:00"))

        # Validate cost structure
        cost = meta["cost"]
        assert "tokens_in" in cost
        assert "tokens_out" in cost
        assert "usd" in cost
        assert isinstance(cost["tokens_in"], int)
        assert isinstance(cost["tokens_out"], int)
        assert isinstance(cost["usd"], (int, float))

    @pytest.mark.contract
    def test_input_preservation(self):
        """Original input must be preserved in envelope"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "Healthcare professionals seeking telemedicine",
            "industry": "healthcare",
            "target_demographics": {"age": "35-55"},
            "brand_token": "healthcare_pro"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)

        # Input should be preserved exactly
        assert result["input"] == test_input

    @pytest.mark.contract
    def test_customer_journey_output_reference(self):
        """Output must reference customer_journey.json.schema"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "Fitness enthusiasts buying home gym equipment"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)
        output = result["output"]

        # Must have required fields from customer_journey.json.schema
        assert "journeyId" in output
        assert "persona" in output
        assert "stages" in output
        assert "metadata" in output

    @pytest.mark.contract
    def test_error_handling_envelope(self):
        """Errors must be properly wrapped in Agent Envelope"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        invalid_input = {}  # Missing required fields

        # This will fail until implementation exists
        result = generate_journey_map(invalid_input)

        # Should still be a valid envelope even on error
        assert "meta" in result
        assert "input" in result
        assert "output" in result or result["output"] is None
        assert "error" in result
        assert result["error"] is not None  # Should contain error message

    @pytest.mark.contract
    def test_hash_validation(self):
        """Output hash must be SHA256 of output content"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "Students looking for note-taking apps"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)

        # Validate hash format and content
        hash_value = result["meta"]["hash"]
        assert len(hash_value) == 64  # SHA256 is 64 hex characters
        assert all(c in "0123456789abcdef" for c in hash_value)

    @pytest.mark.contract
    def test_pydantic_models(self):
        """Pydantic models must validate envelope structure"""
        # This test MUST FAIL until Pydantic models are implemented
        assert AgentEnvelope is not None, "AgentEnvelope model not implemented"
        assert AgentMeta is not None, "AgentMeta model not implemented"

        envelope_data = {
            "meta": {
                "agent": "customer_journey_mapper",
                "version": "1.0.0",
                "trace_id": "test-trace-123",
                "ts": "2025-09-20T14:30:00Z",
                "brand_token": "test",
                "hash": "a" * 64,
                "cost": {"tokens_in": 100, "tokens_out": 200, "usd": 0.05}
            },
            "input": {"market_description": "Test market"},
            "output": {
                "journeyId": "test-journey",
                "persona": {"id": "p1", "name": "Test Persona"},
                "stages": [],
                "metadata": {"createdDate": "2025-09-20T14:30:00Z", "version": "1.0.0"}
            },
            "error": None
        }

        # This will fail until models are implemented
        envelope = AgentEnvelope(**envelope_data)
        assert envelope.meta.agent == "customer_journey_mapper"
        assert envelope.input["market_description"] == "Test market"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])