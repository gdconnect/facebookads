"""Integration tests for content type classification.

These tests validate the decision logic for classifying content as article vs story.
Tests MUST FAIL until classification logic is implemented.
"""

import pytest

# These imports will fail until implementation
try:
    from article_outline_generator import classify_content_type, process_content
except ImportError:
    classify_content_type = None
    process_content = None


class TestContentClassification:
    """Test content type classification logic"""

    @pytest.mark.integration
    def test_classification_function_exists(self):
        """Test that classification function exists."""
        assert classify_content_type is not None, "classify_content_type function not implemented yet"

    @pytest.mark.integration
    def test_clear_article_indicators(self):
        """Test content with clear article indicators."""
        if process_content is None:
            pytest.skip("process_content not implemented")

        # How-to content
        how_to_content = """# How to Build a Garden Shed

Step-by-step guide for constructing a basic garden shed including materials list, tools needed, foundation preparation, and assembly instructions."""

        result = process_content(how_to_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "article"

        # Tutorial content
        tutorial_content = """# Photography Tutorial: Manual Camera Settings

Learn to master manual camera settings including aperture, shutter speed, and ISO. This guide covers exposure triangle concepts and practical exercises."""

        result = process_content(tutorial_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "article"

        # Analysis content
        analysis_content = """# Market Analysis: Renewable Energy Sector

Comprehensive analysis of current trends in renewable energy investment, policy impacts, and growth projections for solar and wind technologies."""

        result = process_content(analysis_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "article"

    @pytest.mark.integration
    def test_clear_story_indicators(self):
        """Test content with clear story indicators."""
        if process_content is None:
            pytest.skip("process_content not implemented")

        # Character-driven narrative
        character_content = """# The Last Library

Sarah discovered the abandoned library on a rainy Tuesday. As the last librarian in the city, she faced an impossible choice between preserving the books and saving her own life."""

        result = process_content(character_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "story"

        # Plot-driven narrative
        plot_content = """# The Time Loop

Every morning, Jake woke up to the same day. The car crash, the conversation with his boss, even the coffee spill - everything repeated exactly. He had to find a way to break the cycle."""

        result = process_content(plot_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "story"

        # Fantasy narrative
        fantasy_content = """# The Dragon's Gift

In the kingdom of Eldoria, young mage Kira inherited her grandmother's mysterious pendant. When dragons returned to the land, she discovered the pendant's true power."""

        result = process_content(fantasy_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "story"

    @pytest.mark.integration
    def test_verb_tense_classification(self):
        """Test classification based on verb tense patterns."""
        if process_content is None:
            pytest.skip("process_content not implemented")

        # Past tense narrative (story)
        past_tense_content = """# The Discovery

Maria walked through the forest and found an ancient artifact. She picked it up and felt its power coursing through her hands. The artifact changed everything she thought she knew about her family's history."""

        result = process_content(past_tense_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "story"

        # Present/imperative instructional (article)
        imperative_content = """# Emergency Preparedness

Create an emergency kit with essential supplies. Store water, non-perishable food, and first aid materials. Keep important documents in waterproof containers. Review and update your plan regularly."""

        result = process_content(imperative_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "article"

    @pytest.mark.integration
    def test_content_type_hint_override(self):
        """Test that content_type_hint parameter works when provided."""
        if process_content is None:
            pytest.skip("process_content not implemented")

        # Ambiguous content that could be either
        ambiguous_content = """# The Future of Work

Remote work transforms how people approach their careers. Companies adapt to distributed teams while employees navigate new challenges and opportunities."""

        # Test with article hint
        result = process_content(ambiguous_content, content_type_hint="article")
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "article"

        # Test with story hint
        result = process_content(ambiguous_content, content_type_hint="story")
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "story"

    @pytest.mark.integration
    def test_edge_case_classification(self):
        """Test classification of edge cases and ambiguous content."""
        if process_content is None:
            pytest.skip("process_content not implemented")

        # Very short content
        short_content = """# Quick Note

Brief thoughts on productivity."""

        result = process_content(short_content)
        assert result["error"] is None
        # Should default to article for ambiguous short content
        assert result["output"]["meta"]["content_type"] == "article"

        # Mixed content (should choose dominant pattern)
        mixed_content = """# The Research Process

Dr. Johnson began her research in 2020. She discovered that effective research requires systematic planning, careful data collection, and thorough analysis. Follow these steps to improve your research methodology."""

        result = process_content(mixed_content)
        assert result["error"] is None
        # Should lean toward article due to instructional ending
        assert result["output"]["meta"]["content_type"] == "article"

    @pytest.mark.integration
    def test_specific_genre_classification(self):
        """Test classification of specific genres and formats."""
        if process_content is None:
            pytest.skip("process_content not implemented")

        # News article
        news_content = """# Tech Company Announces Breakthrough

StartupCorp announced today a major breakthrough in quantum computing technology. The company's new processor demonstrates unprecedented speed improvements over classical computers."""

        result = process_content(news_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "article"

        # Review article
        review_content = """# Restaurant Review: The Garden Bistro

The Garden Bistro offers an exceptional dining experience with fresh, locally-sourced ingredients. The service is attentive and the atmosphere is welcoming."""

        result = process_content(review_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "article"

        # Memoir/personal narrative (story)
        memoir_content = """# Growing Up in Small Town America

I remember the summer I turned twelve, when everything changed. My grandfather taught me to fish at the old creek, and I learned lessons that would shape the rest of my life."""

        result = process_content(memoir_content)
        assert result["error"] is None
        assert result["output"]["meta"]["content_type"] == "story"

    @pytest.mark.integration
    def test_classification_confidence_levels(self):
        """Test that classification works with varying confidence levels."""
        if classify_content_type is None:
            pytest.skip("classify_content_type not implemented")

        # High confidence article
        high_conf_article = "How to install solar panels. Step 1: Calculate your energy needs. Step 2: Choose equipment."
        result = classify_content_type(high_conf_article)
        assert result["content_type"] == "article"
        assert result["confidence"] > 0.8

        # High confidence story
        high_conf_story = "Once upon a time, Princess Elena lived in a castle. She met a dragon who needed her help."
        result = classify_content_type(high_conf_story)
        assert result["content_type"] == "story"
        assert result["confidence"] > 0.8

        # Lower confidence (ambiguous)
        ambiguous = "The future of technology will be interesting to observe and analyze."
        result = classify_content_type(ambiguous)
        assert result["content_type"] in ["article", "story"]
        # Should still make a decision but with lower confidence
        assert 0.5 <= result["confidence"] < 0.8