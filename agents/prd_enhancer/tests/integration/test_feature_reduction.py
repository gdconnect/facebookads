"""Integration tests for feature reduction functionality.

Tests the core feature reduction capability that reduces 20+ features down to 5 core features
based on ROI scoring and business value analysis.
"""

import pytest
import tempfile
from pathlib import Path

# Import the agent module - will fail initially (TDD)
try:
    from prd_enhancer import enhance_prd
except ImportError:
    pytest.skip("Agent not implemented yet - TDD phase", allow_module_level=True)


class TestFeatureReduction:
    """Integration tests for feature reduction functionality."""

    def test_many_features_reduced_to_five(self):
        """Test that PRD with 20+ features is reduced to maximum 5."""
        prd_content = """# Large Feature Set PRD

## Features

1. User Registration - Allow users to create accounts
2. User Login - Authenticate existing users
3. User Profile Management - Edit personal information
4. Password Reset - Reset forgotten passwords
5. Email Verification - Verify email addresses
6. Dashboard - Main user interface
7. Real-time Notifications - Push notifications
8. File Upload - Upload documents and images
9. File Download - Download user files
10. Search Functionality - Search across content
11. Advanced Filtering - Filter search results
12. Data Export - Export data to CSV/PDF
13. API Access - REST API for integrations
14. Mobile App - iOS and Android apps
15. Admin Panel - Administrative interface
16. User Analytics - Track user behavior
17. Reporting Dashboard - Generate reports
18. Third-party Integrations - Connect external services
19. Backup System - Automated data backups
20. Multi-language Support - Internationalization
21. Custom Themes - UI customization
22. Audit Logging - Track all system changes
23. Rate Limiting - API rate controls
24. Social Media Login - OAuth integration
25. Two-Factor Authentication - Enhanced security
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Core requirement: maximum 5 features
            assert len(result.core_features) <= 5, f"Expected ≤5 features, got {len(result.core_features)}"

            # Should have some features (not empty)
            assert len(result.core_features) > 0, "Should select at least some core features"

            # Each feature should have proper structure
            for feature in result.core_features:
                assert hasattr(feature, 'name') and feature.name
                assert hasattr(feature, 'priority_score') and feature.priority_score > 0
                assert hasattr(feature, 'value_score') and 1 <= feature.value_score <= 10
                assert hasattr(feature, 'effort_score') and 1 <= feature.effort_score <= 10

            # Priority score should be value/effort ratio
            for feature in result.core_features:
                expected_score = feature.value_score / feature.effort_score
                assert abs(feature.priority_score - expected_score) < 0.01, \
                    f"Priority score mismatch for {feature.name}"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_not_doing_list_twice_as_long(self):
        """Test that 'not doing' list has at least 2x more items than core features."""
        prd_content = """# Feature Reduction Test PRD

## Required Features

1. User Authentication - Critical for security
2. Data Storage - Must have persistent storage
3. Search Interface - Users need to find content
4. File Management - Upload and organize files
5. Basic Reporting - Essential analytics
6. User Permissions - Role-based access
7. Email Notifications - Communication system
8. Data Export - Compliance requirement
9. API Integration - External system access
10. Mobile Support - Multi-platform access
11. Backup System - Data protection
12. Admin Dashboard - Management interface
13. Audit Trail - Security compliance
14. Performance Monitoring - System health
15. Help Documentation - User support
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            core_count = len(result.core_features)
            not_doing_count = len(result.not_doing)

            # Critical requirement: not_doing ≥ 2x core_features
            assert not_doing_count >= (core_count * 2), \
                f"'Not doing' list ({not_doing_count}) should be ≥ 2x core features ({core_count})"

            # Minimum absolute requirement
            assert not_doing_count >= 10, "Must have at least 10 items in 'not doing' list"

            # Not doing items should be meaningful
            for item in result.not_doing:
                assert isinstance(item, str) and len(item) > 0
                assert len(item) > 3, f"'Not doing' item too short: {item}"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_roi_based_prioritization(self):
        """Test that features are prioritized based on ROI (value/effort)."""
        prd_content = """# ROI Prioritization Test PRD

## Features with Different Value/Effort Ratios

1. High Value, Low Effort Feature - Critical user login (high ROI)
2. High Value, High Effort Feature - Complex AI recommendation engine
3. Low Value, Low Effort Feature - Change button colors
4. Low Value, High Effort Feature - Custom reporting with 50 chart types
5. Medium Value, Medium Effort Feature - Basic search functionality
6. Essential Security Feature - Data encryption (must have)
7. Nice to Have Feature - Social media sharing
8. Compliance Feature - GDPR data handling (required)
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Should prioritize high-ROI features
            selected_names = [feature.name for feature in result.core_features]

            # High ROI features should be more likely to be selected
            high_roi_indicators = ["login", "security", "encryption", "essential", "critical", "required"]
            low_roi_indicators = ["colors", "50 chart types", "nice to have", "social media"]

            high_roi_count = sum(1 for name in selected_names
                               if any(indicator in name.lower() for indicator in high_roi_indicators))

            low_roi_count = sum(1 for name in selected_names
                              if any(indicator in name.lower() for indicator in low_roi_indicators))

            # Should favor high ROI over low ROI
            assert high_roi_count >= low_roi_count, \
                f"Should prioritize high ROI features. High: {high_roi_count}, Low: {low_roi_count}"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_keyword_based_scoring_fallback(self):
        """Test keyword-based scoring when LLM is unavailable."""
        prd_content = """# Keyword Scoring Test PRD

## Features with Priority Keywords

1. MUST HAVE: User authentication system
2. CRITICAL: Data backup and recovery
3. CORE: Basic search functionality
4. SHOULD: Advanced analytics dashboard
5. NICE TO HAVE: Custom themes
6. COULD: Social media integration
7. FUTURE: AI-powered recommendations
8. MAYBE: Multi-language support
9. CONSIDER: Third-party plugins
10. ESSENTIAL: Security monitoring
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Force fallback mode
            result = enhance_prd(input_file, model_enabled=False)

            selected_names = [feature.name.lower() for feature in result.core_features]

            # Should prioritize high-priority keywords
            high_priority_features = []
            low_priority_features = []

            for feature in result.core_features:
                name_lower = feature.name.lower()
                if any(keyword in name_lower for keyword in ["must", "critical", "core", "essential"]):
                    high_priority_features.append(feature)
                elif any(keyword in name_lower for keyword in ["nice", "could", "future", "maybe", "consider"]):
                    low_priority_features.append(feature)

            # Should have more high-priority than low-priority features
            assert len(high_priority_features) >= len(low_priority_features), \
                "Should prioritize high-priority keyword features"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_feature_sorting_by_priority_score(self):
        """Test that selected features are sorted by priority score."""
        prd_content = """# Priority Sorting Test PRD

## Features for Priority Testing

1. Low Priority Feature - Complex reporting dashboard
2. High Priority Feature - User login system
3. Medium Priority Feature - Basic file upload
4. Critical Feature - Data security measures
5. Optional Feature - Custom color schemes
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            if len(result.core_features) > 1:
                # Features should be sorted by priority score (descending)
                priority_scores = [feature.priority_score for feature in result.core_features]

                for i in range(len(priority_scores) - 1):
                    assert priority_scores[i] >= priority_scores[i + 1], \
                        f"Features should be sorted by priority score: {priority_scores}"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_minimum_priority_threshold(self):
        """Test that only features above priority threshold (>2.0) are selected."""
        prd_content = """# Priority Threshold Test PRD

Features designed to test priority scoring:

1. High Value, Low Effort - User registration (Value: 9, Effort: 2)
2. Medium Value, Low Effort - Email notifications (Value: 6, Effort: 2)
3. Low Value, Low Effort - UI color customization (Value: 3, Effort: 1)
4. High Value, High Effort - AI recommendation engine (Value: 8, Effort: 8)
5. Low Value, High Effort - Complex reporting suite (Value: 4, Effort: 9)
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # All selected features should have priority score > 2.0
            for feature in result.core_features:
                assert feature.priority_score > 2.0, \
                    f"Feature '{feature.name}' has priority score {feature.priority_score} ≤ 2.0"

            # High ROI features should be selected
            # User registration: 9/2 = 4.5 (should be selected)
            # Email notifications: 6/2 = 3.0 (should be selected)
            # UI customization: 3/1 = 3.0 (should be selected)
            # AI engine: 8/8 = 1.0 (should NOT be selected)
            # Reporting: 4/9 = 0.44 (should NOT be selected)

            selected_names = [feature.name.lower() for feature in result.core_features]

            # Should include high-ROI features
            assert any("registration" in name for name in selected_names), \
                "Should select high-ROI user registration feature"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_empty_or_minimal_features_handling(self):
        """Test handling of PRDs with few or no explicit features."""
        prd_content = """# Minimal Features PRD

## Basic System Description

We need a simple system for users to manage their data.

The system should allow basic operations and be secure.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file)

            # Should handle gracefully - either extract implicit features or return empty
            assert len(result.core_features) <= 5
            assert len(result.not_doing) >= 10  # Still need not-doing list

            # If features are extracted, they should be valid
            for feature in result.core_features:
                assert feature.name and len(feature.name) > 0
                assert feature.priority_score > 0

        finally:
            Path(input_file).unlink(missing_ok=True)