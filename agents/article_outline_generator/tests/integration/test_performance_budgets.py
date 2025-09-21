"""Performance tests for constitutional budget compliance.

Tests verify that the agent meets all performance requirements:
- Runtime: <5 seconds per execution
- LLM calls: <2 calls (fallback only)
- Tokens: <2000 tokens total
- Memory: <100MB working set
"""

import pytest
import json
import time
import sys
import subprocess
import psutil
import os
from pathlib import Path

# Try importing from the agent
try:
    from article_outline_generator import main, process_content
except ImportError:
    main = None
    process_content = None


class TestPerformanceBudgets:
    """Test constitutional performance budget compliance."""

    @pytest.fixture
    def large_content(self):
        """Large content to test performance limits."""
        sections = []
        for i in range(20):
            sections.append(f"""
## Section {i+1}: Topic Area {i+1}

This is a detailed section about topic area {i+1}. It contains multiple paragraphs
of content that need to be analyzed and processed. The content includes various
technical details, examples, and explanations that make it suitable for testing
the performance characteristics of the outline generator.

Key points for this section:
- First important point with detailed explanation
- Second critical concept that needs coverage
- Third essential element for completeness
- Fourth supporting detail for context
- Fifth concluding thought for the section
""")

        content = f"""# Comprehensive Technical Guide

This is an extensive technical guide covering multiple topics in great detail.
The content is designed to test the performance limits of the article outline
generator while staying within constitutional budgets.

{''.join(sections)}

## Conclusion

This comprehensive guide has covered all the essential topics. The outline
generator should process this efficiently within the performance budgets.
"""
        return content

    @pytest.mark.integration
    @pytest.mark.performance
    def test_runtime_budget(self, large_content):
        """Test that runtime stays under 5 seconds."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        start_time = time.time()

        result = process_content(
            content=large_content,
            target_depth=3,
            include_word_counts=True
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Verify successful completion
        assert result["error"] is None
        assert result["output"] is not None

        # Check runtime budget
        assert execution_time < 5.0, f"Execution took {execution_time:.2f}s, exceeds 5s budget"

        # Check reported processing time
        processing_time_ms = result["output"]["meta"]["processing_time_ms"]
        assert processing_time_ms < 5000, f"Processing time {processing_time_ms}ms exceeds 5000ms"

    @pytest.mark.integration
    @pytest.mark.performance
    def test_llm_call_budget(self):
        """Test that LLM calls stay under 2 calls limit."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        # Content designed to trigger LLM (ambiguous)
        ambiguous_content = """Abstract Concepts

Exploring the nature of reality through philosophical discourse and empirical
observation. The intersection of thought and matter presents intriguing
questions about consciousness and existence.
"""

        result = process_content(
            content=ambiguous_content,
            classification_method="auto"
        )

        # Check LLM call budget
        llm_calls = result["output"]["meta"]["llm_calls_used"]
        assert llm_calls <= 2, f"Used {llm_calls} LLM calls, exceeds 2 call limit"

        # Verify in envelope metadata
        assert result["meta"]["cost"]["llm_calls"] <= 2

    @pytest.mark.integration
    @pytest.mark.performance
    def test_token_budget(self):
        """Test that token usage stays under 2000 tokens."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        # Moderate content that might use LLM
        content = """# Technical Documentation Standards

This guide outlines the standards and best practices for technical documentation.
Following these guidelines ensures consistency and clarity across all materials.

## Documentation Types
- API references
- User guides
- Developer tutorials
- System architecture docs
"""

        result = process_content(
            content=content,
            classification_method="auto"
        )

        # Check token budget
        total_tokens = (result["meta"]["cost"]["tokens_in"] +
                       result["meta"]["cost"]["tokens_out"])
        assert total_tokens < 2000, f"Used {total_tokens} tokens, exceeds 2000 token limit"

    @pytest.mark.integration
    @pytest.mark.performance
    def test_memory_budget(self):
        """Test that memory usage stays under 100MB."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        # Create large input
        large_input = {
            "content": "# Test Article\n" + ("Content " * 1000),
            "target_depth": 3,
            "include_word_counts": True
        }

        # Run in subprocess to measure memory
        process = subprocess.Popen(
            [sys.executable, str(agent_path), "run", "--input-type", "json"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Monitor memory usage
        try:
            proc = psutil.Process(process.pid)
            max_memory = 0

            # Send input and get output
            stdout, stderr = process.communicate(
                input=json.dumps(large_input),
                timeout=5
            )

            # Get peak memory usage (if available)
            try:
                memory_info = proc.memory_info()
                max_memory = memory_info.rss / (1024 * 1024)  # Convert to MB
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process already finished
                pass

            # Verify successful completion
            result = json.loads(stdout)
            assert result["error"] is None

            # Check memory budget (if we got a measurement)
            if max_memory > 0:
                assert max_memory < 100, f"Used {max_memory:.1f}MB, exceeds 100MB limit"

        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("Process exceeded 5s timeout")

    @pytest.mark.integration
    @pytest.mark.performance
    def test_interim_response_performance(self):
        """Test that interim responses are fast."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        content = """# Quick Classification Test

This content should be classified quickly for interim response.
The classification should happen in milliseconds, not seconds.
"""

        start_time = time.time()

        result = process_content(
            content=content,
            interim=True,
            timeout_ms=500
        )

        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to ms

        # Should be very fast for interim
        assert execution_time < 500, f"Interim took {execution_time:.0f}ms, exceeds 500ms"
        assert result["output"]["meta"]["processing_time_ms"] < 500

    @pytest.mark.integration
    @pytest.mark.performance
    def test_concurrent_requests(self):
        """Test performance under concurrent load."""
        if main is None:
            pytest.skip("Agent not yet implemented")

        agent_path = Path(__file__).parent.parent.parent / "article_outline_generator.py"

        from concurrent.futures import ThreadPoolExecutor, as_completed

        def run_request(content):
            """Run a single request."""
            result = subprocess.run(
                [sys.executable, str(agent_path), "run"],
                input=content,
                capture_output=True,
                text=True,
                timeout=5
            )
            return json.loads(result.stdout)

        # Create multiple test inputs
        inputs = [
            "# Article 1\n\nFirst test article content.",
            "# Article 2\n\nSecond test article content.",
            "# Article 3\n\nThird test article content.",
        ]

        # Run concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_request, content) for content in inputs]

            start_time = time.time()
            results = [future.result() for future in as_completed(futures)]
            end_time = time.time()

        # All should complete within budget
        total_time = end_time - start_time
        assert total_time < 15, f"Concurrent requests took {total_time:.1f}s"

        # All should succeed
        for result in results:
            assert result["error"] is None
            assert result["output"] is not None

    @pytest.mark.integration
    @pytest.mark.performance
    def test_performance_degradation_with_depth(self):
        """Test that performance scales reasonably with depth."""
        if process_content is None:
            pytest.skip("Agent not yet implemented")

        content = """# Scalability Test

Testing how performance scales with different depth settings.
This content will be processed at various depths to measure impact.

## Section 1
Content for section 1.

## Section 2
Content for section 2.
"""

        times = []
        for depth in [1, 3, 6]:
            start_time = time.time()

            result = process_content(
                content=content,
                target_depth=depth
            )

            end_time = time.time()
            execution_time = end_time - start_time
            times.append(execution_time)

            # Each should stay within budget
            assert execution_time < 5.0
            assert result["error"] is None

        # Performance shouldn't degrade too much
        # Depth 6 shouldn't take more than 2x depth 1
        assert times[2] < times[0] * 2, "Performance degrades too much with depth"