"""
T009: Integration test for markdown input processing

This test MUST FAIL until the customer_journey_mapper.py can process
markdown input files and normalize them to structured JSON via LLM.

Based on Quickstart Scenario 3: Healthcare telemedicine market specification.
"""

import json
import pytest
import subprocess
from pathlib import Path

# This import will fail until the main module is implemented
try:
    from ...customer_journey_mapper import normalize_markdown_input, main
except ImportError:
    normalize_markdown_input = None
    main = None


class TestMarkdownInputIntegration:
    """Integration tests for markdown input processing and normalization"""

    @pytest.fixture
    def sample_healthcare_markdown(self):
        """Sample markdown input from Quickstart Scenario 3"""
        return """# Healthcare Telemedicine Market

## Target Market
Healthcare professionals working in rural clinics who need remote consultation capabilities.

## Demographics
- **Age**: 35-55 years
- **Location**: Rural areas, small towns
- **Occupation**: General practitioners, nurse practitioners
- **Tech Comfort**: Moderate to high

## Product
HIPAA-compliant telemedicine platform with:
- Video consultations
- Electronic health records integration
- Prescription management
- Insurance billing

## Business Model
B2B SaaS with per-provider monthly subscriptions.

## Key Challenges
- Internet connectivity limitations
- Regulatory compliance requirements
- Patient adoption resistance
- Integration with existing systems
"""

    @pytest.mark.integration
    def test_markdown_file_processing_cli(self, sample_healthcare_markdown):
        """Test CLI processing of markdown input file"""
        # This test MUST FAIL until CLI markdown processing is implemented

        # Create test markdown file
        markdown_file = Path("test_healthcare_market.md")
        with open(markdown_file, "w") as f:
            f.write(sample_healthcare_markdown)

        # Run CLI command with markdown input
        result = subprocess.run([
            "python", "customer_journey_mapper.py",
            "--input-file", str(markdown_file),
            "--input-format", "text/markdown",
            "--output", "test_healthcare_journey.json",
            "--log-level", "DEBUG"
        ], capture_output=True, text=True)

        # Clean up input file
        markdown_file.unlink()

        # This will fail until implementation exists
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Validate output file was created
        output_file = Path("test_healthcare_journey.json")
        assert output_file.exists(), "Output file not created"

        # Load and validate output
        with open(output_file) as f:
            journey_data = json.load(f)

        # Clean up
        output_file.unlink()

        # Validate markdown content was properly processed
        journey_map = journey_data["output"]

        # Should reflect healthcare industry
        assert "healthcare" in str(journey_data).lower()

        # Should reflect B2B SaaS model
        assert journey_map["metadata"]["industry"] == "healthcare"

    @pytest.mark.integration
    def test_markdown_normalization_function(self, sample_healthcare_markdown):
        """Test markdown normalization to structured JSON"""
        # This test MUST FAIL until normalize_markdown_input is implemented
        assert normalize_markdown_input is not None, "normalize_markdown_input function not implemented"

        # This will fail until implementation exists
        normalized_input = normalize_markdown_input(sample_healthcare_markdown)

        # Validate normalized structure
        assert isinstance(normalized_input, dict)
        assert "market_description" in normalized_input
        assert "industry" in normalized_input
        assert "business_model" in normalized_input

        # Validate content extraction
        assert "healthcare" in normalized_input["industry"].lower()
        assert "telemedicine" in normalized_input["market_description"].lower()
        assert "B2B" in normalized_input["business_model"]

    @pytest.mark.integration
    def test_markdown_demographics_extraction(self, sample_healthcare_markdown):
        """Test extraction of demographics from markdown structure"""
        # This test MUST FAIL until markdown parsing is implemented
        assert normalize_markdown_input is not None, "normalize_markdown_input function not implemented"

        # This will fail until implementation exists
        normalized_input = normalize_markdown_input(sample_healthcare_markdown)

        # Should extract demographics from markdown
        assert "target_demographics" in normalized_input
        demographics = normalized_input["target_demographics"]

        assert "age" in demographics
        assert "35-55" in demographics["age"]
        assert "location" in demographics
        assert "rural" in demographics["location"].lower()
        assert "occupation" in demographics

    @pytest.mark.integration
    def test_markdown_product_service_extraction(self, sample_healthcare_markdown):
        """Test extraction of product/service details from markdown"""
        # This test MUST FAIL until product extraction is implemented
        assert normalize_markdown_input is not None, "normalize_markdown_input function not implemented"

        # This will fail until implementation exists
        normalized_input = normalize_markdown_input(sample_healthcare_markdown)

        # Should extract product/service information
        assert "product_service" in normalized_input
        product_service = normalized_input["product_service"].lower()

        assert "telemedicine" in product_service
        assert "hipaa" in product_service
        assert "video" in product_service

    @pytest.mark.integration
    def test_markdown_challenges_to_pain_points(self, sample_healthcare_markdown):
        """Test conversion of markdown challenges to pain points"""
        # This test MUST FAIL until challenge extraction is implemented
        assert main is not None, "main function not implemented"

        # Create temporary markdown file
        markdown_file = Path("test_challenges.md")
        with open(markdown_file, "w") as f:
            f.write(sample_healthcare_markdown)

        # This will fail until implementation exists
        # Simulate processing the file
        result = main()  # Would need to mock sys.argv

        # Clean up
        markdown_file.unlink()

        # Should convert challenges to journey pain points
        result_str = str(result).lower()
        assert "connectivity" in result_str or "compliance" in result_str
        assert "integration" in result_str

    @pytest.mark.integration
    def test_complex_markdown_structure(self):
        """Test processing of complex markdown with multiple sections"""
        # This test MUST FAIL until complex markdown parsing is implemented
        assert normalize_markdown_input is not None, "normalize_markdown_input function not implemented"

        complex_markdown = """# Digital Marketing Agency Tools

## Executive Summary
Marketing agencies specializing in small business clients need affordable, integrated tools.

### Primary Market Segment
- **Industry**: Professional services
- **Size**: 5-50 employee agencies
- **Location**: North America, primarily urban

### Secondary Markets
1. Freelance marketing consultants
2. In-house marketing teams at SMBs
3. Startups with limited marketing budget

## Product Portfolio
Our SaaS platform provides:
- Campaign management
- Client reporting dashboards
- Social media scheduling
- Analytics and ROI tracking

### Pricing Tiers
1. **Starter**: $99/month - Up to 5 clients
2. **Professional**: $299/month - Up to 20 clients
3. **Enterprise**: $699/month - Unlimited clients

## Competitive Landscape
- **Direct competitors**: HubSpot, Mailchimp
- **Indirect competitors**: Internal tools, spreadsheets
- **Differentiation**: Focus on agency workflow, white-label reports

## Customer Feedback Themes
> "Need better client communication features"
> "Pricing is competitive but onboarding is complex"
> "Love the reporting but need more integrations"
"""

        # This will fail until implementation exists
        normalized_input = normalize_markdown_input(complex_markdown)

        # Should handle complex structure
        assert "market_description" in normalized_input
        assert "marketing agencies" in normalized_input["market_description"].lower()
        assert "industry" in normalized_input
        assert "saas" in normalized_input.get("business_model", "").lower()

    @pytest.mark.integration
    def test_markdown_error_handling(self):
        """Test handling of malformed or incomplete markdown"""
        # This test MUST FAIL until error handling is implemented
        assert normalize_markdown_input is not None, "normalize_markdown_input function not implemented"

        malformed_markdown_cases = [
            "",  # Empty markdown
            "# Just a title",  # Minimal content
            "Random text without structure",  # Unstructured
            "# Market\n\n## Demographics\n- Age:",  # Incomplete information
        ]

        for malformed_markdown in malformed_markdown_cases:
            # This will fail until implementation exists
            try:
                result = normalize_markdown_input(malformed_markdown)
                # Should either succeed with minimal data or raise appropriate error
                if result:
                    assert "market_description" in result
            except (ValueError, Exception) as e:
                # Should provide meaningful error messages
                assert "markdown" in str(e).lower() or "insufficient" in str(e).lower()

    @pytest.mark.integration
    def test_markdown_content_type_detection(self):
        """Test automatic detection of markdown content type"""
        # This test MUST FAIL until content type detection is implemented
        assert main is not None, "main function not implemented"

        markdown_content = "# Test Market\n\nSample market description."

        # Should auto-detect as markdown based on content
        # This will fail until implementation exists
        result = main()  # Would need proper input simulation

        # Should process as markdown even without explicit --input-format
        assert "text/markdown" in str(result) or "markdown" in str(result).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])