"""
T012: Constitutional compliance test (JSONL logging, cost tracking)

This test MUST FAIL until the customer_journey_mapper.py implements
all constitutional requirements for observability and compliance.

Constitutional requirements: Articles I-XVI compliance validation.
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# This import will fail until the main module is implemented
try:
    from ...constitutional_compliance_validator import main
except ImportError:
    main = None


class TestConstitutionalCompliance:
    """Constitutional compliance tests for all articles"""

    @pytest.mark.integration
    def test_article_i_single_file_compliance(self):
        """Article I: Single-file Python program with CLI entrypoint"""
        # This test validates file structure exists

        main_file = Path("customer_journey_mapper.py")
        assert main_file.exists(), "Single-file agent not found"

        # Check for CLI entrypoint
        with open(main_file) as f:
            content = f.read()

        assert 'if __name__ == "__main__":' in content, "Missing CLI entrypoint"
        assert "def main()" in content, "Missing main function"

    @pytest.mark.integration
    def test_article_ii_agent_envelope_output(self):
        """Article II: Agent Envelope output format"""
        # This test MUST FAIL until Agent Envelope is implemented

        result = subprocess.run([
            "python", "customer_journey_mapper.py",
            "--input", "Constitutional compliance test market",
            "--output", "envelope_test.json"
        ], capture_output=True, text=True)

        # This will fail until implementation exists
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        output_file = Path("envelope_test.json")
        assert output_file.exists(), "Output file not created"

        with open(output_file) as f:
            data = json.load(f)

        # Clean up
        output_file.unlink()

        # Validate Agent Envelope structure
        assert "meta" in data
        assert "input" in data
        assert "output" in data
        assert "error" in data

        meta = data["meta"]
        assert meta["agent"] == "customer_journey_mapper"
        assert "version" in meta
        assert "trace_id" in meta
        assert "ts" in meta
        assert "brand_token" in meta
        assert "hash" in meta
        assert "cost" in meta

    @pytest.mark.integration
    def test_article_ix_jsonl_observability(self):
        """Article IX: JSONL logging to STDERR"""
        # This test MUST FAIL until JSONL logging is implemented

        result = subprocess.run([
            "python", "customer_journey_mapper.py",
            "--input", "Observability test market",
            "--output", "jsonl_test.json",
            "--log-level", "INFO"
        ], capture_output=True, text=True)

        # Clean up
        Path("jsonl_test.json").unlink(missing_ok=True)

        # This will fail until JSONL logging is implemented
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Check for JSONL in stderr
        stderr_lines = result.stderr.strip().split('\n')
        jsonl_found = False

        for line in stderr_lines:
            if line.strip() and line.startswith('{'):
                try:
                    log_entry = json.loads(line)
                    if log_entry.get("event") == "agent_run":
                        jsonl_found = True
                        # Validate required JSONL fields
                        assert "agent" in log_entry
                        assert "version" in log_entry
                        assert "trace_id" in log_entry
                        assert "ms" in log_entry
                        assert "strict" in log_entry
                        assert "input_content_type" in log_entry
                        break
                except json.JSONDecodeError:
                    continue

        assert jsonl_found, "JSONL observability log not found in stderr"

    @pytest.mark.integration
    def test_article_x_llm_strict_default(self):
        """Article X: LLM disabled by default (STRICT mode)"""
        # This test MUST FAIL until LLM policy is implemented

        # Test without enabling LLM
        result = subprocess.run([
            "python", "customer_journey_mapper.py",
            "--input", "LLM strict mode test",
            "--output", "strict_test.json",
            "--log-level", "DEBUG"
        ], capture_output=True, text=True)

        # Clean up
        Path("strict_test.json").unlink(missing_ok=True)

        # This will fail until STRICT mode is implemented
        # Should either succeed without LLM or fail with appropriate message
        if result.returncode == 0:
            # If it succeeds, should not have used LLM
            debug_output = result.stderr.lower()
            assert "llm disabled" in debug_output or "strict mode" in debug_output
        else:
            # If it fails, should explain LLM is disabled
            assert "llm" in result.stderr.lower() and "disabled" in result.stderr.lower()

    @pytest.mark.integration
    def test_article_xii_budget_enforcement(self):
        """Article XII: Performance budgets declared and enforced"""
        # This test MUST FAIL until budget enforcement is implemented

        result = subprocess.run([
            "python", "customer_journey_mapper.py",
            "--input", "Budget enforcement test market",
            "--output", "budget_test.json"
        ], capture_output=True, text=True)

        # This will fail until implementation exists
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        output_file = Path("budget_test.json")
        assert output_file.exists(), "Output file not created"

        with open(output_file) as f:
            data = json.load(f)

        # Clean up
        output_file.unlink()

        # Validate budget compliance
        cost = data["meta"]["cost"]
        assert cost["tokens_in"] + cost["tokens_out"] <= 2000, "Token budget exceeded"
        assert cost["usd"] <= 0.10, "Cost budget exceeded"

    @pytest.mark.integration
    def test_article_xiii_brand_token_support(self):
        """Article XIII: Brand token configuration"""
        # This test MUST FAIL until brand token support is implemented

        result = subprocess.run([
            "python", "customer_journey_mapper.py",
            "--input", "Brand token test market",
            "--brand-token", "test_brand",
            "--output", "brand_test.json"
        ], capture_output=True, text=True)

        # This will fail until implementation exists
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        output_file = Path("brand_test.json")
        assert output_file.exists(), "Output file not created"

        with open(output_file) as f:
            data = json.load(f)

        # Clean up
        output_file.unlink()

        # Validate brand token is preserved
        assert data["meta"]["brand_token"] == "test_brand"

    @pytest.mark.integration
    def test_article_v_hierarchical_config(self):
        """Article V: Hierarchical configuration with required CLI flags"""
        # This test validates CLI flag support

        # Test all required constitutional flags
        result = subprocess.run([
            "python", "customer_journey_mapper.py", "--help"
        ], capture_output=True, text=True)

        assert result.returncode == 0, "Help command failed"

        help_text = result.stdout.lower()
        required_flags = ["--config", "--rules", "--brand-token", "--strict", "--log-level"]

        for flag in required_flags:
            assert flag in help_text, f"Required constitutional flag {flag} not found"

    @pytest.mark.integration
    def test_article_vii_type_safety(self):
        """Article VII: Type safety with mypy --strict"""
        # This test validates type safety compliance

        result = subprocess.run([
            "python", "-m", "mypy", "--strict", "customer_journey_mapper.py"
        ], capture_output=True, text=True)

        # This will fail until type hints are complete
        assert result.returncode == 0, f"mypy --strict failed:\n{result.stdout}\n{result.stderr}"

    @pytest.mark.integration
    def test_header_docstring_compliance(self):
        """Article VI: Header docstring with purpose, usage, budgets"""
        # This test validates docstring compliance

        main_file = Path("customer_journey_mapper.py")
        with open(main_file) as f:
            content = f.read()

        # Check for constitutional docstring elements
        assert '"""' in content, "Missing module docstring"

        docstring_start = content.find('"""')
        docstring_end = content.find('"""', docstring_start + 3)
        docstring = content[docstring_start:docstring_end + 3].lower()

        required_sections = [
            "description",
            "usage examples",
            "accepted input content types",
            "example output",
            "declared budgets"
        ]

        for section in required_sections:
            assert section in docstring, f"Missing docstring section: {section}"

    @pytest.mark.integration
    def test_numbered_flow_comments(self):
        """Article VI: Numbered flow comments in implementation"""
        # This test MUST FAIL until numbered flow is implemented

        main_file = Path("customer_journey_mapper.py")
        with open(main_file) as f:
            content = f.read()

        # Look for numbered comments in main function
        main_function_start = content.find("def main()")
        assert main_function_start != -1, "main() function not found"

        main_function = content[main_function_start:]

        # Should have numbered flow comments (1, 2, 3...)
        numbered_comments = []
        for i in range(1, 10):  # Check for numbers 1-9
            if f"# {i}." in main_function or f"#{i}." in main_function:
                numbered_comments.append(i)

        # This will fail until numbered flow is implemented
        assert len(numbered_comments) >= 3, f"Insufficient numbered flow comments: {numbered_comments}"

    @pytest.mark.integration
    def test_trace_id_consistency(self):
        """Test that trace_id is consistent across all outputs"""
        # This test MUST FAIL until trace_id consistency is implemented

        result = subprocess.run([
            "python", "customer_journey_mapper.py",
            "--input", "Trace ID consistency test",
            "--output", "trace_test.json",
            "--log-level", "DEBUG"
        ], capture_output=True, text=True)

        # This will fail until implementation exists
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Extract trace_id from output file
        output_file = Path("trace_test.json")
        with open(output_file) as f:
            data = json.load(f)

        # Clean up
        output_file.unlink()

        output_trace_id = data["meta"]["trace_id"]

        # Extract trace_id from JSONL log
        stderr_lines = result.stderr.strip().split('\n')
        log_trace_id = None

        for line in stderr_lines:
            if line.strip() and line.startswith('{'):
                try:
                    log_entry = json.loads(line)
                    if "trace_id" in log_entry:
                        log_trace_id = log_entry["trace_id"]
                        break
                except json.JSONDecodeError:
                    continue

        # Trace IDs should match
        assert log_trace_id is not None, "trace_id not found in JSONL log"
        assert output_trace_id == log_trace_id, "trace_id mismatch between output and log"

    @pytest.mark.integration
    def test_iso8601_timestamp_format(self):
        """Test that timestamps are in ISO-8601 format"""
        # This test MUST FAIL until timestamp formatting is implemented

        result = subprocess.run([
            "python", "customer_journey_mapper.py",
            "--input", "Timestamp format test",
            "--output", "timestamp_test.json"
        ], capture_output=True, text=True)

        # This will fail until implementation exists
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        output_file = Path("timestamp_test.json")
        with open(output_file) as f:
            data = json.load(f)

        # Clean up
        output_file.unlink()

        # Validate ISO-8601 timestamp format
        timestamp = data["meta"]["ts"]
        try:
            # Should be parseable as ISO-8601
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Timestamp {timestamp} is not valid ISO-8601 format")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])