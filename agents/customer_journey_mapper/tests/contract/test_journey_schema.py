"""
T006: Contract test for customer journey schema compliance

This test MUST FAIL until the customer_journey_mapper.py generates output
that validates against the customer_journey.json.schema.

Constitutional requirement: Schema-first design with validation (Article II).
"""

import json
import pytest
import jsonschema
from pathlib import Path

# This import will fail until the main module is implemented
try:
    from ...customer_journey_mapper import generate_journey_map
except ImportError:
    generate_journey_map = None


class TestJourneySchemaContract:
    """Contract tests for customer journey schema compliance"""

    @pytest.fixture
    def customer_journey_schema(self):
        """Load the customer journey JSON schema"""
        schema_path = Path("schemas/customer_journey.json.schema")
        assert schema_path.exists(), f"Customer journey schema not found at {schema_path}"

        with open(schema_path) as f:
            return json.load(f)

    @pytest.mark.contract
    def test_schema_file_exists(self, customer_journey_schema):
        """Customer journey schema must exist and be valid"""
        assert customer_journey_schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert customer_journey_schema["title"] == "Customer Journey Map"
        assert customer_journey_schema["type"] == "object"

        # Required fields validation
        required_fields = customer_journey_schema["required"]
        assert "journeyId" in required_fields
        assert "persona" in required_fields
        assert "stages" in required_fields
        assert "metadata" in required_fields

    @pytest.mark.contract
    def test_generated_journey_validates_schema(self, customer_journey_schema):
        """Generated journey map must validate against schema"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "Eco-conscious millennials buying sustainable fashion",
            "industry": "ecommerce",
            "business_model": "B2C"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)
        journey_map = result["output"]

        # Validate against customer journey schema
        try:
            jsonschema.validate(journey_map, customer_journey_schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"Generated journey map does not validate against schema: {e}")

    @pytest.mark.contract
    def test_required_fields_present(self, customer_journey_schema):
        """All required fields must be present in generated output"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "B2B SaaS for small business accounting"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)
        journey_map = result["output"]

        # Check required top-level fields
        assert "journeyId" in journey_map
        assert "persona" in journey_map
        assert "stages" in journey_map
        assert "metadata" in journey_map

        # Check persona required fields
        persona = journey_map["persona"]
        assert "id" in persona
        assert "name" in persona

        # Check stages structure
        stages = journey_map["stages"]
        assert isinstance(stages, list)
        if stages:  # If stages exist, validate structure
            for stage in stages:
                assert "stageId" in stage
                assert "stageName" in stage
                assert "touchpoints" in stage

        # Check metadata required fields
        metadata = journey_map["metadata"]
        assert "createdDate" in metadata
        assert "version" in metadata

    @pytest.mark.contract
    def test_enum_values_compliance(self, customer_journey_schema):
        """Generated values must comply with schema enum constraints"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "Healthcare telemedicine platform users"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)
        journey_map = result["output"]

        # Extract enum values from schema
        stage_name_enum = customer_journey_schema["properties"]["stages"]["items"]["properties"]["stageName"]["enum"]
        channel_enum = customer_journey_schema["properties"]["stages"]["items"]["properties"]["touchpoints"]["items"]["properties"]["channel"]["enum"]

        # Validate stage names are from enum
        for stage in journey_map["stages"]:
            stage_name = stage["stageName"]
            if stage_name != "Custom":  # Custom allows customStageName
                assert stage_name in stage_name_enum, f"Invalid stage name: {stage_name}"

            # Validate touchpoint channels are from enum
            for touchpoint in stage["touchpoints"]:
                channel = touchpoint["channel"]
                assert channel in channel_enum, f"Invalid channel: {channel}"

    @pytest.mark.contract
    def test_data_types_compliance(self, customer_journey_schema):
        """Generated data types must match schema specifications"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "Digital marketing agencies needing analytics tools"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)
        journey_map = result["output"]

        # Validate data types
        assert isinstance(journey_map["journeyId"], str)
        assert isinstance(journey_map["persona"], dict)
        assert isinstance(journey_map["stages"], list)
        assert isinstance(journey_map["metadata"], dict)

        # Validate persona structure
        persona = journey_map["persona"]
        assert isinstance(persona["id"], str)
        assert isinstance(persona["name"], str)
        if "goals" in persona:
            assert isinstance(persona["goals"], list)
        if "painPoints" in persona:
            assert isinstance(persona["painPoints"], list)

    @pytest.mark.contract
    def test_nested_validation(self, customer_journey_schema):
        """Nested objects must validate against schema constraints"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_input = {
            "market_description": "E-learning platform for professional development"
        }

        # This will fail until implementation exists
        result = generate_journey_map(test_input)
        journey_map = result["output"]

        # Deep validation of nested structures
        for stage in journey_map["stages"]:
            # Each stage must have required fields
            assert isinstance(stage["stageId"], str)
            assert isinstance(stage["touchpoints"], list)

            for touchpoint in stage["touchpoints"]:
                # Each touchpoint must have required fields
                assert isinstance(touchpoint["touchpointId"], str)
                assert isinstance(touchpoint["channel"], str)
                assert isinstance(touchpoint["action"], str)

                # Optional emotion validation
                if "emotions" in touchpoint:
                    for emotion in touchpoint["emotions"]:
                        assert isinstance(emotion, dict)
                        if "intensity" in emotion:
                            intensity = emotion["intensity"]
                            assert isinstance(intensity, int)
                            assert 1 <= intensity <= 5

    @pytest.mark.contract
    def test_multiple_market_types_schema_compliance(self, customer_journey_schema):
        """Different market types should all produce schema-compliant output"""
        # This test MUST FAIL until generate_journey_map is implemented
        assert generate_journey_map is not None, "generate_journey_map function not implemented"

        test_cases = [
            {"market_description": "B2C e-commerce for sustainable products", "industry": "ecommerce"},
            {"market_description": "B2B SaaS for project management", "industry": "saas"},
            {"market_description": "Healthcare telemedicine consultations", "industry": "healthcare"},
            {"market_description": "Financial planning for millennials", "industry": "finance"},
        ]

        for test_input in test_cases:
            # This will fail until implementation exists
            result = generate_journey_map(test_input)
            journey_map = result["output"]

            # Each should validate against schema
            try:
                jsonschema.validate(journey_map, customer_journey_schema)
            except jsonschema.ValidationError as e:
                pytest.fail(f"Market type {test_input} failed schema validation: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])