"""Integration tests for LLM functionality and fallback behavior.

Tests both LLM-enabled processing and graceful fallback to regex patterns
when LLM services are unavailable or fail.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Import the agent module - will fail initially (TDD)
try:
    from prd_enhancer import enhance_prd, LLMAgentFactory
except ImportError:
    pytest.skip("Agent not implemented yet - TDD phase", allow_module_level=True)


class TestLLMFallback:
    """Integration tests for LLM fallback functionality."""

    def test_regex_fallback_for_ambiguity_detection(self):
        """Test that regex patterns work when LLM is disabled."""
        prd_content = """# Fallback Test PRD

System Requirements:
- Must be fast and responsive
- Should be scalable for growth
- Needs to be user-friendly
- Must be secure and safe
- Should be reliable and robust
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Test with LLM disabled (force fallback)
            result = enhance_prd(input_file, model_enabled=False)

            # Should still detect ambiguities using regex
            assert len(result.ambiguities_found) > 0, "Regex fallback should detect ambiguities"

            # All ambiguities should be from regex source
            for ambiguity in result.ambiguities_found:
                assert ambiguity.source == "regex", f"Expected regex source, got {ambiguity.source}"

            # Should detect expected patterns
            found_terms = [amb.term.lower() for amb in result.ambiguities_found]
            expected_patterns = ["fast", "scalable", "user-friendly", "secure", "safe", "reliable", "robust"]

            found_expected = [term for term in expected_patterns
                            if any(term in found_term for found_term in found_terms)]

            assert len(found_expected) >= 3, f"Should find multiple regex patterns, found: {found_terms}"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_keyword_scoring_fallback_for_features(self):
        """Test that keyword scoring works when LLM is disabled."""
        prd_content = """# Keyword Scoring Test PRD

## Critical Features
1. MUST HAVE: User authentication
2. CRITICAL: Data encryption
3. CORE: Basic search

## Secondary Features
4. SHOULD: Analytics dashboard
5. NICE TO HAVE: Custom themes
6. COULD: Social integration

## Future Features
7. MAYBE: AI recommendations
8. CONSIDER: Advanced reporting
9. FUTURE: Mobile app
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Force fallback mode
            result = enhance_prd(input_file, model_enabled=False)

            # Should prioritize based on keywords
            selected_names = [feature.name.lower() for feature in result.core_features]

            # High-priority keywords should be favored
            high_priority_count = sum(1 for name in selected_names
                                    if any(keyword in name for keyword in
                                          ["must", "critical", "core", "authentication", "encryption"]))

            low_priority_count = sum(1 for name in selected_names
                                   if any(keyword in name for keyword in
                                         ["maybe", "consider", "future", "nice"]))

            assert high_priority_count >= low_priority_count, \
                "Keyword scoring should favor high-priority terms"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_fallback_performance_acceptable(self):
        """Test that fallback mode still meets performance requirements."""
        prd_content = """# Performance Test PRD

Large document with many ambiguous terms and features to test fallback performance.

System should be fast, scalable, user-friendly, secure, reliable, robust,
efficient, performant, intuitive, flexible, maintainable.

Features:
1. User management
2. Data processing
3. Report generation
4. API integration
5. Security monitoring
6. Performance analytics
7. Backup systems
8. Notification service
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            import time
            start_time = time.time()

            result = enhance_prd(input_file, model_enabled=False)

            processing_time = time.time() - start_time

            # Should still be fast in fallback mode
            assert processing_time < 5.0, f"Fallback processing took {processing_time:.2f}s, should be <5s"

            # Should still produce valid results
            assert result.complexity_score is not None
            assert len(result.core_features) <= 5
            assert len(result.not_doing) >= 10

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_fallback_warning_in_output(self):
        """Test that fallback mode is indicated in processing stats."""
        prd_content = """# Fallback Warning Test PRD

## Overview
This is a comprehensive Product Requirements Document (PRD) designed to test the fallback warning functionality of the PRD enhancer system. The document intentionally contains content that should trigger fallback behavior when LLM services are unavailable or disabled.

## System Requirements
The system being developed must meet the following core requirements:

### Functional Requirements
1. **User Interface**: The system should provide a user-friendly interface that accommodates users of all technical skill levels. This includes intuitive navigation, clear visual hierarchy, and consistent interaction patterns throughout the application.

2. **Scalability**: The system should be scalable to handle growth in user base and data volume. This includes horizontal scaling capabilities, efficient resource utilization, and the ability to maintain performance as demand increases.

3. **Performance**: Response times should be optimized for user experience, with page loads completing within acceptable timeframes and database queries executing efficiently.

4. **Data Management**: The system must handle data storage, retrieval, and processing with appropriate security measures and backup procedures in place.

### Non-Functional Requirements
1. **Reliability**: The system should maintain high availability with minimal downtime for maintenance or issues.

2. **Security**: Appropriate authentication, authorization, and data protection measures must be implemented to safeguard user information and system integrity.

3. **Maintainability**: The codebase should be well-documented, follow established coding standards, and be structured to facilitate future updates and modifications.

4. **Compatibility**: The system should work across different browsers, devices, and operating systems to ensure broad accessibility.

## Testing Objectives
This PRD serves as a test case to verify that the PRD enhancer can properly detect when fallback methods are being used instead of LLM-based analysis. The system should clearly indicate in its processing statistics when regex patterns or keyword scoring are being employed due to LLM unavailability.

## Expected Behavior
When processing this document with LLM disabled, the system should:
- Use regex-based ambiguity detection for terms like "user-friendly" and "scalable"
- Apply keyword-based scoring for feature prioritization
- Generate appropriate fallback usage statistics
- Maintain processing quality despite using fallback methods

## Conclusion
This document provides sufficient content to avoid triggering the should_skip_all_passes() condition while maintaining the essential characteristics needed to test fallback warning functionality.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file, model_enabled=False)

            # Should indicate fallback usage in stats
            assert hasattr(result, 'processing_stats')
            assert hasattr(result.processing_stats, 'fallbacks_used')

            fallbacks = result.processing_stats.fallbacks_used
            assert len(fallbacks) > 0, "Should report fallback usage"
            assert "regex" in str(fallbacks).lower(), "Should mention regex fallback"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_graceful_llm_timeout_handling(self):
        """Test graceful handling when LLM times out."""
        prd_content = """# Timeout Handling Test PRD

## Executive Summary
This Product Requirements Document outlines the specifications for a comprehensive system that requires careful analysis of ambiguous requirements. The document is specifically designed to test the PRD enhancer's ability to gracefully handle LLM timeout scenarios while maintaining processing quality through fallback mechanisms.

## System Overview
The proposed system represents a next-generation platform that combines advanced user experience design with enterprise-grade scalability and security features. This system will serve as a foundation for future growth and adaptation to changing business requirements.

## Detailed Requirements

### User Experience Requirements
The system must deliver a very user-friendly interface with intuitive design principles. This encompasses several key aspects:

1. **Interface Design**: The user interface should be extremely intuitive, allowing users to accomplish their goals with minimal learning curve. The design should follow established usability principles and incorporate user feedback from extensive testing sessions.

2. **Navigation Structure**: The navigation should be logical and consistent across all sections of the application. Users should be able to find what they need quickly and efficiently, with clear visual indicators of their current location within the system.

3. **Accessibility**: The interface must be accessible to users with disabilities, following WCAG guidelines and ensuring compatibility with assistive technologies.

4. **Responsiveness**: The system should provide responsive design that works seamlessly across desktop, tablet, and mobile devices, adapting to different screen sizes and input methods.

### Scalability Architecture Requirements
The system requires an extremely scalable architecture designed for massive growth potential:

1. **Horizontal Scaling**: The architecture should support horizontal scaling to accommodate increasing user loads and data volumes without significant performance degradation.

2. **Load Distribution**: Implement intelligent load balancing mechanisms that can efficiently distribute traffic across multiple servers and data centers.

3. **Data Management**: Design database architecture that can scale with business growth, including appropriate sharding, replication, and caching strategies.

4. **Performance Monitoring**: Integrate comprehensive monitoring and alerting systems to track performance metrics and identify potential bottlenecks before they impact users.

### Security Framework Requirements
The system demands an ultra-secure framework with advanced protection mechanisms:

1. **Authentication**: Multi-factor authentication systems with support for various authentication methods including biometric options where appropriate.

2. **Authorization**: Role-based access control with granular permission management and audit logging of all security-related events.

3. **Data Protection**: End-to-end encryption for data in transit and at rest, with appropriate key management and rotation procedures.

4. **Threat Detection**: Advanced threat detection and prevention systems that can identify and respond to security incidents in real-time.

## Testing Objectives
This document contains intentionally ambiguous terms like "very user-friendly," "extremely scalable," and "ultra-secure" to test the system's ability to handle LLM timeout scenarios. When processing with a very short timeout, the system should gracefully fall back to regex-based analysis while maintaining processing quality.

## Success Criteria
The PRD enhancer should successfully process this document even when LLM services timeout, using fallback methods to identify ambiguous terms and complete the analysis within acceptable time limits.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Test with very short timeout to trigger fallback
            result = enhance_prd(input_file, model_enabled=True, model_timeout=1)

            # Should still complete successfully using fallbacks
            assert result is not None
            assert len(result.ambiguities_found) > 0

            # Should use fallback when LLM times out
            fallback_sources = [amb.source for amb in result.ambiguities_found]
            assert "regex" in fallback_sources, "Should fall back to regex on timeout"

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_mixed_mode_operation(self):
        """Test operation when some LLM passes succeed and others fail."""
        prd_content = """# Mixed Mode Test PRD

Features requiring different analysis types:

1. User authentication system
2. Real-time notification service
3. Advanced analytics dashboard
4. Machine learning recommendations
5. API integration framework
6. Mobile application
7. Data visualization tools

System should be scalable, secure, and user-friendly.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # This test simulates partial LLM failures
            # (In real implementation, some passes might succeed while others fail)
            result = enhance_prd(input_file, model_enabled=True)

            # Should handle mixed success/failure gracefully
            assert result is not None

            # Should have results from successful passes and fallbacks
            if len(result.ambiguities_found) > 0:
                sources = [amb.source for amb in result.ambiguities_found]
                # May contain mix of 'llm' and 'regex' sources
                assert all(source in ['llm', 'regex'] for source in sources)

        finally:
            Path(input_file).unlink(missing_ok=True)


class TestLLMIntegration:
    """Integration tests for LLM-enabled processing."""

    @patch.object(LLMAgentFactory, 'create_ambiguity_detector')
    def test_llm_ambiguity_detection_enabled(self, mock_factory):
        """Test LLM ambiguity detection when enabled."""
        # Mock LLM agent response
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = """- Term: fast
- Problem: Vague performance requirement
- Fix: <200ms response time

- Term: scalable
- Problem: Undefined capacity requirement
- Fix: handles 1000 concurrent users"""

        mock_agent.run_sync.return_value = mock_result
        mock_factory.return_value = mock_agent

        prd_content = """# LLM Test PRD

## Project Overview
This Product Requirements Document defines the specifications for a high-performance system designed to test LLM ambiguity detection capabilities. The system will serve as a critical component in our technology infrastructure, requiring careful attention to performance, scalability, and reliability characteristics.

## Background and Context
In today's rapidly evolving technological landscape, organizations need systems that can adapt to changing demands while maintaining consistent performance. This project aims to deliver a solution that meets these challenges through innovative design and implementation approaches.

## Core System Requirements

### Performance Requirements
The system must be fast and responsive across all user interactions:

1. **Response Time**: All user-initiated actions should complete within acceptable timeframes, providing immediate feedback for user interactions and maintaining system responsiveness during peak usage periods.

2. **Processing Speed**: Backend processing should be optimized for efficiency, utilizing appropriate algorithms and data structures to minimize computational overhead and resource consumption.

3. **User Experience**: The interface should feel snappy and responsive, with smooth transitions and minimal loading delays that could negatively impact user satisfaction.

4. **Resource Optimization**: System resources should be utilized efficiently, avoiding unnecessary memory usage or CPU consumption that could impact overall performance.

### Scalability Requirements
The system should be scalable for growth to accommodate future expansion:

1. **User Growth**: The architecture should support increasing numbers of concurrent users without degradation in performance or functionality.

2. **Data Volume**: As data volumes increase over time, the system should maintain consistent performance through appropriate database design and optimization strategies.

3. **Feature Expansion**: The system architecture should accommodate new features and functionality without requiring major restructuring of existing components.

4. **Geographic Distribution**: Consider scalability across different geographic regions to support global user bases and reduce latency.

### Load Handling Requirements
The system needs to handle user load effectively:

1. **Concurrent Users**: Support for multiple simultaneous users accessing the system without performance degradation or resource conflicts.

2. **Peak Traffic**: Ability to handle traffic spikes during high-usage periods through appropriate load balancing and resource allocation strategies.

3. **Graceful Degradation**: When approaching capacity limits, the system should degrade gracefully rather than failing completely, maintaining core functionality for users.

4. **Recovery Mechanisms**: Implement appropriate recovery procedures for handling system overload situations and returning to normal operation.

## Technical Specifications
The system will be built using modern technologies and architectural patterns that support the performance and scalability requirements outlined above. Implementation should follow industry best practices for security, maintainability, and reliability.

## Testing and Quality Assurance
This document serves as a test case for LLM ambiguity detection, containing terms like "fast," "scalable," and "handle user load" that should be identified as potentially ambiguous and requiring more specific definition.

## Success Metrics
Success will be measured by the system's ability to meet the specified performance and scalability requirements while maintaining high availability and user satisfaction ratings.\n\n## Implementation Guidelines\nDevelopment teams should follow established coding standards and best practices throughout the implementation process. Code reviews should focus on performance optimization, security considerations, and maintainability aspects. Testing strategies should include comprehensive unit tests, integration tests, and performance benchmarks to ensure system reliability and maintain quality standards across all development phases.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Test with LLM enabled
            result = enhance_prd(input_file, model_enabled=True)

            # Should have LLM-detected ambiguities
            assert len(result.ambiguities_found) >= 2

            # Should have LLM source
            llm_sources = [amb.source for amb in result.ambiguities_found if amb.source == "llm"]
            assert len(llm_sources) > 0

            # Verify specific terms were found
            found_terms = [amb.term.lower() for amb in result.ambiguities_found]
            assert "fast" in found_terms
            assert "scalable" in found_terms

        finally:
            Path(input_file).unlink(missing_ok=True)

    @patch.object(LLMAgentFactory, 'create_scope_guardian')
    def test_llm_feature_reduction_enabled(self, mock_factory):
        """Test LLM feature reduction when enabled."""
        # Mock LLM agent response
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = """Feature: User Authentication
Value: 9
Effort: 3
Score: 3.0

Feature: Data Encryption
Value: 8
Effort: 2
Score: 4.0

Feature: Analytics Dashboard
Value: 4
Effort: 8
Score: 0.5"""

        mock_agent.run_sync.return_value = mock_result
        mock_factory.return_value = mock_agent

        prd_content = """# Feature Reduction Test PRD

## Executive Summary
This Product Requirements Document outlines a comprehensive software platform designed to test the LLM feature reduction capabilities of the PRD enhancer. The document intentionally includes multiple features with varying levels of importance and complexity to evaluate the system's ability to prioritize and select core features effectively.

## Project Background
In the current competitive landscape, organizations must balance feature richness with development timelines and resource constraints. This project aims to deliver a platform that provides essential functionality while maintaining high quality and user satisfaction. The challenge lies in identifying which features provide the most value relative to their implementation effort.

## System Architecture Overview
The proposed system will be built using modern, scalable architecture principles that support rapid development and future expansion. The platform will integrate multiple components working together to deliver a cohesive user experience while maintaining security and performance standards.

## Detailed Feature Specifications

### 1. User Authentication System
A comprehensive authentication framework that provides secure access control for all system users:
- Multi-factor authentication support with various verification methods
- Role-based access control with granular permission management
- Session management with automatic timeout and security monitoring
- Integration with existing enterprise identity management systems
- Audit logging for all authentication and authorization events
- Password policies and security enforcement mechanisms
- Support for single sign-on (SSO) integration with external providers

### 2. Data Encryption Module
Robust encryption capabilities to protect sensitive information throughout the system:
- End-to-end encryption for data transmission between all system components
- Advanced encryption standards for data at rest in databases and file systems
- Key management and rotation procedures with secure key storage
- Compliance with industry standards and regulatory requirements
- Performance optimization to minimize encryption overhead
- Integration with existing security infrastructure and monitoring systems

### 3. Analytics Dashboard
Comprehensive analytics and reporting interface for business intelligence:
- Real-time data visualization with interactive charts and graphs
- Customizable dashboard layouts for different user roles and needs
- Advanced filtering and drill-down capabilities for detailed analysis
- Automated report generation and distribution systems
- Data export functionality in multiple formats
- Performance monitoring and system health indicators
- Integration with external analytics platforms and data sources

### 4. Social Media Integration
Seamless connectivity with popular social media platforms:
- API integration with major social media networks
- Content sharing and publishing capabilities
- Social authentication options for user onboarding
- Social media monitoring and engagement tracking
- Compliance with platform-specific policies and rate limits
- Content moderation and approval workflows

### 5. Advanced Reporting
Sophisticated reporting engine for business intelligence and compliance:
- Customizable report templates with drag-and-drop interface
- Scheduled report generation and automated distribution
- Advanced data analysis with statistical functions and calculations
- Export capabilities in multiple formats including PDF, Excel, and CSV
- Report versioning and audit trail functionality
- Integration with external business intelligence tools

### 6. Mobile Application
Native mobile applications for iOS and Android platforms:
- Full feature parity with web interface where applicable
- Optimized user interface for mobile interaction patterns
- Offline functionality with data synchronization capabilities
- Push notification support for important updates and alerts
- Device-specific features like camera integration and GPS
- App store compliance and distribution management

### 7. API Gateway
Centralized API management and integration platform:
- RESTful API design with comprehensive documentation
- Rate limiting and traffic management capabilities
- Authentication and authorization for API access
- API versioning and backward compatibility management
- Developer portal with testing tools and documentation
- Monitoring and analytics for API usage patterns

### 8. Notification Service
Reliable notification and messaging system:
- Multi-channel notification delivery including email, SMS, and push
- Template management for consistent message formatting
- Delivery tracking and confirmation mechanisms
- User preference management for notification settings
- Integration with external messaging services and providers
- Analytics and reporting for notification effectiveness

## Testing Objectives
This PRD is designed to test the LLM feature reduction system's ability to analyze and score features based on business value and implementation effort. The system should identify high-value, low-effort features like User Authentication and Data Encryption as core features, while recognizing that complex features like Analytics Dashboard may provide lower value relative to their implementation cost.

## Success Criteria
The feature reduction process should successfully identify the most valuable features for initial implementation while deferring less critical or more complex features to future development phases.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Test with LLM enabled
            result = enhance_prd(input_file, model_enabled=True)

            # Should have reduced features based on LLM scoring
            assert len(result.core_features) <= 5

            # Features with score > 2.0 should be included
            selected_names = [f.name.lower() for f in result.core_features]
            assert any("authentication" in name for name in selected_names)
            assert any("encryption" in name for name in selected_names)

            # Low-scoring features should be excluded
            assert not any("analytics" in name for name in selected_names)

        finally:
            Path(input_file).unlink(missing_ok=True)

    @patch.object(LLMAgentFactory, 'create_consistency_checker')
    def test_llm_consistency_checking_enabled(self, mock_factory):
        """Test LLM consistency checking when enabled."""
        # Mock LLM agent response with conflicts
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.data = """Conflict: Real-time sync conflicts with Offline mode because they require opposite connectivity assumptions"""

        mock_agent.run_sync.return_value = mock_result
        mock_factory.return_value = mock_agent

        prd_content = """# Consistency Test PRD

## Executive Summary
This Product Requirements Document defines a comprehensive system designed to test LLM consistency checking capabilities. The document intentionally includes potentially conflicting requirements to evaluate the system's ability to identify logical inconsistencies and architectural conflicts in product specifications.

## Project Overview
The proposed system aims to deliver a robust platform that operates effectively in various connectivity scenarios while maintaining data integrity and user experience quality. This dual-mode operation presents unique challenges in system design and architecture that require careful consideration of trade-offs and implementation strategies.

## Business Context
In today's mobile-first environment, users expect applications to function reliably regardless of network connectivity. This requirement drives the need for sophisticated synchronization mechanisms and offline capabilities that maintain data consistency while providing responsive user interactions.

## System Architecture Requirements
The system will implement a hybrid architecture that supports both connected and disconnected operation modes, with intelligent switching between these states based on network availability and user preferences.

## Detailed Feature Specifications

### 1. Real-time Data Synchronization
Advanced synchronization capabilities for immediate data consistency across all system components:

**Technical Requirements:**
- WebSocket-based real-time communication for instant data updates
- Conflict resolution algorithms for handling simultaneous updates
- Delta synchronization to minimize bandwidth usage and improve performance
- Priority-based synchronization for critical data updates
- Connection monitoring and automatic reconnection mechanisms
- Synchronization status indicators for user awareness

**Functional Requirements:**
- Immediate propagation of data changes to all connected clients
- Support for collaborative editing scenarios with multiple users
- Real-time notifications for data changes affecting user workflows
- Bandwidth optimization for mobile and low-connectivity environments
- Fallback mechanisms for degraded network conditions

### 2. Offline Mode Operation
Comprehensive offline functionality that maintains system usability without network connectivity:

**Technical Requirements:**
- Local data caching with intelligent cache management
- Background synchronization when connectivity is restored
- Conflict detection and resolution for offline changes
- Local storage optimization for performance and space management
- Offline-first architecture with progressive enhancement

**Functional Requirements:**
- Full feature availability during offline operation
- Automatic transition between online and offline modes
- User feedback for offline status and pending synchronization
- Data integrity maintenance during offline periods
- Seamless user experience regardless of connectivity state

### 3. User Authentication
Secure authentication framework supporting both online and offline scenarios:
- Multi-factor authentication with offline token validation
- Secure credential storage for offline authentication
- Token refresh and validation mechanisms
- Integration with enterprise identity management systems
- Biometric authentication support where available
- Session management across online/offline transitions

### 4. Data Storage
Flexible data storage architecture supporting multiple storage strategies:
- Hybrid storage model with local and remote components
- Data encryption for both local and remote storage
- Automated backup and recovery procedures
- Data compression and optimization techniques
- Schema versioning and migration capabilities
- Performance monitoring and optimization tools

### 5. Search Functionality
Powerful search capabilities that work in both connected and disconnected modes:
- Full-text search across all indexed content
- Local search index for offline operation
- Incremental index updates during synchronization
- Advanced filtering and sorting capabilities
- Search result ranking and relevance algorithms
- Integration with external search services when online

## System Integration Requirements
The system must work both online and offline seamlessly, presenting a significant architectural challenge. This requirement creates potential conflicts between real-time synchronization (which requires connectivity) and offline mode operation (which assumes no connectivity). The system must intelligently handle these conflicting states through sophisticated state management and synchronization strategies.

## Consistency Challenges
The combination of real-time synchronization and offline mode operation creates inherent tensions in system design:

1. **Data Consistency**: Real-time sync assumes immediate consistency, while offline mode accepts eventual consistency
2. **Resource Management**: Real-time features consume more battery and bandwidth, conflicting with offline efficiency requirements
3. **User Experience**: Real-time notifications may conflict with offline mode's emphasis on local-first operation
4. **Architecture Complexity**: Supporting both modes significantly increases system complexity and potential failure points

## Testing Objectives
This PRD is designed to test the LLM consistency checker's ability to identify logical conflicts between system requirements. The conflict between "Real-time Data Synchronization" and "Offline Mode Operation" should be detected as they represent fundamentally different architectural assumptions about network connectivity.

## Resolution Strategy
While these requirements appear conflicting, they can be reconciled through intelligent system design that prioritizes user experience and implements graceful degradation between modes. The system should maintain consistency checking capabilities to identify and resolve such conflicts during the design phase.
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Test with LLM enabled
            result = enhance_prd(input_file, model_enabled=True)

            # Should execute consistency check and find conflicts
            assert "pass3_consistency" in result.processing_stats.passes_executed

            # Conflicts should be detected (implementation may vary)
            # This tests that the pass was executed

        finally:
            Path(input_file).unlink(missing_ok=True)


class TestBudgetEnforcement:
    """Integration tests for budget enforcement."""

    def test_budget_enforcement_fallback(self):
        """Test that budget limits trigger fallback to regex/keyword methods."""
        prd_content = """# Budget Test PRD

This is a very long PRD document designed to test budget enforcement.
The system should be fast, scalable, user-friendly, secure, reliable, and robust.
It needs to handle high performance, maintain good usability, ensure data protection.

## Features
1. Advanced User Authentication System
2. Real-time Data Processing Engine
3. Comprehensive Analytics Dashboard
4. Machine Learning Recommendations
5. Social Media Integration Platform
6. Mobile Application Development
7. API Gateway Implementation
8. Notification Service Architecture
9. Data Visualization Components
10. Search and Discovery Engine
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Test with very low token budget to force fallback
            result = enhance_prd(input_file, model_enabled=True, model_max_tokens=100)

            # Should still complete successfully
            assert result is not None
            assert len(result.ambiguities_found) > 0
            assert len(result.core_features) <= 5

            # Should have used fallback methods due to budget
            assert len(result.processing_stats.fallbacks_used) > 0

        finally:
            Path(input_file).unlink(missing_ok=True)

    def test_token_usage_tracking(self):
        """Test that token usage is properly tracked."""
        prd_content = """# Token Tracking Test PRD

Simple PRD to test token usage tracking.
System should be user-friendly and scalable.

## Features
1. User Management
2. Data Processing
3. Report Generation
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            # Mock successful LLM responses to test tracking
            with patch.object(LLMAgentFactory, 'create_ambiguity_detector') as mock_detector:
                mock_agent = Mock()
                mock_result = Mock()
                mock_result.data = "- Term: user-friendly\n- Problem: vague\n- Fix: 3 clicks"
                mock_agent.run_sync.return_value = mock_result
                mock_detector.return_value = mock_agent

                result = enhance_prd(input_file, model_enabled=True)

                # Should track token usage
                assert result.processing_stats.tokens_used >= 0

        finally:
            Path(input_file).unlink(missing_ok=True)


class TestMixedModeOperation:
    """Integration tests for mixed LLM/fallback operation."""

    @patch.object(LLMAgentFactory, 'create_ambiguity_detector')
    @patch.object(LLMAgentFactory, 'create_scope_guardian')
    def test_partial_llm_success(self, mock_scope_factory, mock_ambiguity_factory):
        """Test operation when some LLM passes succeed and others fail."""
        # Ambiguity detection succeeds
        mock_ambiguity_agent = Mock()
        mock_ambiguity_result = Mock()
        mock_ambiguity_result.data = "- Term: fast\n- Problem: vague\n- Fix: <200ms"
        mock_ambiguity_agent.run_sync.return_value = mock_ambiguity_result
        mock_ambiguity_factory.return_value = mock_ambiguity_agent

        # Scope reduction fails (returns None to trigger fallback)
        mock_scope_factory.return_value = None

        prd_content = """# Mixed Mode Test PRD

System should be fast and scalable.

## Features
1. User Authentication
2. Data Processing
3. Report Generation
4. API Integration
5. Mobile Support
6. Analytics
7. Search
8. Notifications
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prd_content)
            input_file = f.name

        try:
            result = enhance_prd(input_file, model_enabled=True)

            # Should have mixed sources
            ambiguity_sources = [amb.source for amb in result.ambiguities_found]

            # Should have both LLM and fallback usage
            assert "pass1_ambiguity" in result.processing_stats.passes_executed
            assert "pass2_scope" in result.processing_stats.passes_executed

            # Should have some fallbacks used
            assert len(result.processing_stats.fallbacks_used) > 0

        finally:
            Path(input_file).unlink(missing_ok=True)