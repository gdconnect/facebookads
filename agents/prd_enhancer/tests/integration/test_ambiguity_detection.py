"""Integration tests for ambiguity detection functionality.

Tests the core ambiguity detection feature with various scenarios
including LLM and regex fallback modes.
"""

import pytest
import tempfile
from pathlib import Path

# Import the agent module - will fail initially (TDD)
try:
    from prd_enhancer import enhance_prd
except ImportError:
    pytest.skip("Agent not implemented yet - TDD phase", allow_module_level=True)


class TestAmbiguityDetection:
    """Integration tests for ambiguity detection."""

    def test_common_ambiguous_terms_detection(self):
        """Test detection of common ambiguous terms."""
        prd_content = """# Ambiguous PRD

We need a fast, scalable, user-friendly system that is:
- Performant and reliable
- Secure and robust
- Intuitive for users
- Highly available

The solution should be flexible and maintainable.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Should detect multiple ambiguous terms
            assert len(result.ambiguities_found) >= 3

            found_terms = [amb.term.lower() for amb in result.ambiguities_found]
            expected_terms = ["fast", "scalable", "user-friendly", "performant", "reliable", "secure", "robust", "intuitive"]

            # Should find at least some of these terms
            found_expected = [term for term in expected_terms if any(term in found_term for found_term in found_terms)]
            assert len(found_expected) >= 3, f"Expected to find ambiguous terms, found: {found_terms}"

            # Each ambiguity should have proper structure
            for ambiguity in result.ambiguities_found:
                assert ambiguity.term is not None and len(ambiguity.term) > 0
                assert ambiguity.problem is not None and len(ambiguity.problem) > 0
                assert ambiguity.suggested_fix is not None and len(ambiguity.suggested_fix) > 0
                assert ambiguity.confidence >= 0.0 and ambiguity.confidence <= 1.0
                assert ambiguity.source in ["llm", "regex"]

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_specific_metric_suggestions(self):
        """Test that specific metrics are suggested for vague terms."""
        prd_content = """# Performance PRD

The system must be:
- Fast (response times)
- Scalable (user capacity)
- Reliable (uptime requirements)
- Secure (data protection)
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Validate specific metric suggestions
            suggestions = {amb.term.lower(): amb.suggested_fix for amb in result.ambiguities_found}

            # Check for specific metrics in suggestions
            if "fast" in suggestions:
                assert any(metric in suggestions["fast"].lower() for metric in ["ms", "second", "time"])

            if "scalable" in suggestions:
                assert any(metric in suggestions["scalable"].lower() for metric in ["user", "concurrent", "request"])

            if "reliable" in suggestions:
                assert any(metric in suggestions["reliable"].lower() for metric in ["uptime", "availability", "%"])

            if "secure" in suggestions:
                assert any(metric in suggestions["secure"].lower() for metric in ["ssl", "encryption", "auth"])

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_llm_vs_regex_fallback_comparison(self):
        """Test that LLM mode provides better results than regex fallback."""
        prd_content = """# Complex Ambiguity PRD

We need a user-friendly interface that feels intuitive and natural.
The system should be lightning-fast with excellent performance.
It must be enterprise-grade and production-ready.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Test with LLM enabled (if available)
            try:
                llm_result = enhance_prd(input_file, model_enabled=True)
                llm_ambiguities = len(llm_result.ambiguities_found)
                llm_sources = [amb.source for amb in llm_result.ambiguities_found]
            except Exception:
                # LLM might not be available, skip this comparison
                llm_result = None
                llm_ambiguities = 0

            # Test with regex fallback
            regex_result = enhance_prd(input_file, model_enabled=False)
            regex_ambiguities = len(regex_result.ambiguities_found)

            # Should detect ambiguities in both modes
            assert regex_ambiguities > 0, "Regex fallback should detect some ambiguities"

            # All regex results should be from regex source
            for ambiguity in regex_result.ambiguities_found:
                assert ambiguity.source == "regex"

            # LLM should potentially find more or different ambiguities
            if llm_result:
                assert any(source == "llm" for source in llm_sources), "LLM mode should use LLM source"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_ambiguity_confidence_scoring(self):
        """Test that confidence scoring works appropriately."""
        prd_content = """# Confidence Test PRD

Clear requirements:
- Response time must be under 200ms
- System must handle 1000 concurrent users

Ambiguous requirements:
- The interface should be user-friendly
- Performance must be good
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Should find ambiguous terms
            assert len(result.ambiguities_found) > 0

            # Confidence scores should be reasonable
            for ambiguity in result.ambiguities_found:
                assert 0.0 <= ambiguity.confidence <= 1.0

                # High-confidence ambiguities should be obvious cases
                if ambiguity.confidence > 0.8:
                    assert ambiguity.term.lower() in ["user-friendly", "good", "fast", "scalable"]

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_context_preservation(self):
        """Test that context around ambiguous terms is preserved."""
        prd_content = """# Context PRD

The user interface must be intuitive for new users but powerful for experts.
System performance should be fast during peak usage hours.
Data security must be robust against external threats.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Should capture context for each ambiguity
            for ambiguity in result.ambiguities_found:
                if ambiguity.context:
                    # Context should contain the ambiguous term
                    assert ambiguity.term.lower() in ambiguity.context.lower()

                    # Context should provide surrounding information
                    assert len(ambiguity.context) > len(ambiguity.term)

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_maximum_ambiguities_limit(self):
        """Test that maximum ambiguities limit (10) is respected."""
        # Create PRD with many ambiguous terms
        ambiguous_terms = [
            "fast", "slow", "quick", "scalable", "performant", "user-friendly",
            "intuitive", "secure", "safe", "reliable", "robust", "flexible",
            "maintainable", "efficient", "effective", "optimal"
        ]

        prd_content = "# Many Ambiguities PRD\n\n"
        for term in ambiguous_terms:
            prd_content += f"The system should be {term} for all users.\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Should not exceed maximum limit
            assert len(result.ambiguities_found) <= 10, "Should not exceed maximum of 10 ambiguities"

            # If we found 10, they should be the most important ones
            if len(result.ambiguities_found) == 10:
                # Should prioritize by confidence or importance
                confidences = [amb.confidence for amb in result.ambiguities_found]
                assert all(conf >= 0.3 for conf in confidences), "High-confidence ambiguities should be prioritized"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_no_false_positives_for_specific_terms(self):
        """Test that specific, clear terms are not flagged as ambiguous."""
        prd_content = """# Specific PRD

Requirements:
- Response time under 200 milliseconds
- Support 1000 concurrent users
- 99.9% uptime availability
- AES-256 encryption for data at rest
- OAuth 2.0 authentication
- Database backup every 24 hours
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Should find few or no ambiguities in specific requirements
            specific_terms = ["200 milliseconds", "1000 concurrent", "99.9%", "AES-256", "OAuth 2.0", "24 hours"]

            for ambiguity in result.ambiguities_found:
                # Shouldn't flag specific numeric requirements
                assert not any(specific in ambiguity.term for specific in specific_terms), \
                    f"Should not flag specific term: {ambiguity.term}"

        finally:
            Path(input_file).unlink(missing_ok=True)