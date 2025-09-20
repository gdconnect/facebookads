#!/usr/bin/env python3
"""
Constitutional Compliance Validator v1.0.0

PURPOSE: Validates Python single-file programs against Schema-First Empire Constitution v1.3.5
USAGE: python constitutional_compliance_validator.py --target-file /path/to/file.py [--output report.json]
INPUT: target_file (required), optional validation_config, output_options, brand_token
OUTPUT: Agent Envelope JSON with comprehensive compliance report and remediation guidance

BUDGETS:
- Execution time: < 5 seconds for typical single-file validation
- Memory usage: < 100MB peak
- Network calls: 0 (fully offline operation)

DEPENDENCIES: Uses only stdlib + external static analysis tools (mypy, pylint, bandit, vulture, radon)
Tools must be installed separately: pip install mypy pylint bandit vulture radon

EXAMPLES:
    python constitutional_compliance_validator.py --target-file customer_journey_mapper.py
    python constitutional_compliance_validator.py --target-file app.py --strict-mode --output report.json
    echo '{"target_file": "/path/to/file.py"}' | python constitutional_compliance_validator.py
"""

import argparse
import json
import hashlib
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, NamedTuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import ast


# ═══════════════════════════════════════════════════════════════════════════
# CONFIG SECTION (Lines 30-120)
# ═══════════════════════════════════════════════════════════════════════════

class ValidationConfig(NamedTuple):
    """1. Configuration for validation execution"""
    strict_mode: bool = False
    timeout_seconds: int = 30
    parallel_execution: bool = True
    article_filter: Optional[List[str]] = None
    tool_overrides: Optional[Dict[str, str]] = None

class OutputOptions(NamedTuple):
    """2. Output formatting configuration"""
    format: str = "json"  # json, yaml, text
    include_evidence: bool = True
    include_remediation: bool = True

class ToolConfig(NamedTuple):
    """3. Static analysis tool configuration"""
    mypy_path: str = "mypy"
    pylint_path: str = "pylint"
    bandit_path: str = "bandit"
    vulture_path: str = "vulture"
    radon_path: str = "radon"

# 4. Constitutional article definitions with validation criteria
CONSTITUTIONAL_ARTICLES = {
    "I": {
        "title": "Single-File Python Programs",
        "description": "Programs are single .py files with clear CLI entrypoint",
        "weight": 0.8,
        "pass_criteria": ["single_file", "cli_entrypoint", "minimal_dependencies"]
    },
    "II": {
        "title": "Contract-First (JSON Envelopes)",
        "description": "Agent Envelope output format compliance",
        "weight": 0.9,
        "pass_criteria": ["agent_envelope_format", "json_output", "schema_present"]
    },
    "III": {
        "title": "Decision Tables & Rules",
        "description": "Business logic implemented with decision tables",
        "weight": 0.7,
        "pass_criteria": ["decision_tables", "rule_precedence", "fallback_handling"]
    },
    "IV": {
        "title": "Input Versatility, Output Consistency",
        "description": "Flexible input handling with consistent JSON output",
        "weight": 0.6,
        "pass_criteria": ["input_handling", "output_consistency"]
    },
    "V": {
        "title": "Hierarchical Configuration",
        "description": "Config precedence and CLI flag requirements",
        "weight": 0.7,
        "pass_criteria": ["config_hierarchy", "required_cli_flags", "config_section"]
    },
    "VI": {
        "title": "Documentation & Numbered Flow",
        "description": "Header docstring and numbered code annotations",
        "weight": 0.6,
        "pass_criteria": ["header_docstring", "numbered_flow", "usage_examples"]
    },
    "VII": {
        "title": "Type Safety, Modern Python & Defensive Programming",
        "description": "Full type hints, mypy compliance, defensive patterns",
        "weight": 1.0,
        "pass_criteria": ["type_hints", "mypy_strict", "defensive_programming"]
    },
    "VIII": {
        "title": "Testing",
        "description": "Comprehensive test coverage and types",
        "weight": 0.9,
        "pass_criteria": ["golden_tests", "edge_case_tests", "contract_tests", "defensive_tests"]
    },
    "IX": {
        "title": "Observability",
        "description": "JSONL logging and monitoring compliance",
        "weight": 0.5,
        "pass_criteria": ["jsonl_logging", "structured_output"]
    },
    "X": {
        "title": "Idempotency",
        "description": "Deterministic operations and state management",
        "weight": 0.6,
        "pass_criteria": ["deterministic_operations", "state_management"]
    },
    "XI": {
        "title": "Brand Systems",
        "description": "Brand token support and configuration",
        "weight": 0.4,
        "pass_criteria": ["brand_token_support"]
    },
    "XII": {
        "title": "Performance Budget",
        "description": "Performance constraints and resource limits",
        "weight": 0.8,
        "pass_criteria": ["execution_time", "memory_usage", "resource_constraints"]
    },
    "XIII": {
        "title": "Agent Envelope Meta",
        "description": "Complete meta field implementation",
        "weight": 0.7,
        "pass_criteria": ["meta_fields", "trace_id", "cost_tracking"]
    },
    "XIV": {
        "title": "Error Handling",
        "description": "Graceful error handling and recovery",
        "weight": 0.8,
        "pass_criteria": ["error_handling", "graceful_failure", "error_messages"]
    },
    "XV": {
        "title": "Versioning",
        "description": "Semantic versioning and compatibility",
        "weight": 0.5,
        "pass_criteria": ["semantic_versioning", "compatibility"]
    },
    "XVI": {
        "title": "CLI Standards",
        "description": "Standard CLI patterns and help text",
        "weight": 0.6,
        "pass_criteria": ["cli_patterns", "help_text", "argument_parsing"]
    },
    "XVII": {
        "title": "Quality Gates",
        "description": "Static analysis and code quality requirements",
        "weight": 1.0,
        "pass_criteria": ["pylint_score", "security_scan", "complexity_metrics", "dead_code"]
    }
}

# 5. Quality gate thresholds
QUALITY_THRESHOLDS = {
    "pylint_min_score": 9.5,
    "max_complexity": 10,
    "max_function_length": 50,
    "min_test_coverage": 80
}


# ═══════════════════════════════════════════════════════════════════════════
# CORE VALIDATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class CheckResult(NamedTuple):
    """6. Result of a specific validation check"""
    check_name: str
    tool_used: str
    status: str  # PASS, FAIL, WARNING, ERROR
    details: str
    evidence: Dict[str, Any]
    execution_time_ms: int

class ArticleAssessment(NamedTuple):
    """7. Assessment result for a constitutional article"""
    article_number: str
    article_title: str
    status: str  # PASS, FAIL, WARNING, SKIP, ERROR
    score: float
    execution_time_ms: int
    checks_performed: List[CheckResult]
    violations: List[str]

class ValidationSummary(NamedTuple):
    """8. High-level validation statistics"""
    total_articles: int
    passed_articles: int
    failed_articles: int
    warning_articles: int
    overall_score: float
    execution_time_ms: int
    tools_used: List[str]

class ConstitutionalComplianceValidator:
    """9. Main validation engine for constitutional compliance"""

    def __init__(self, config: ValidationConfig, tool_config: ToolConfig) -> None:
        """10. Initialize validator with configuration"""
        self.config = config
        self.tool_config = tool_config
        self.start_time = time.time()

    def validate_file(self, target_file: Path) -> Dict[str, Any]:
        """11. Main validation entry point - orchestrates all article validations"""
        validation_id = f"val_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 12. Validate file exists and is readable
        if not target_file.exists():
            raise FileNotFoundError(f"Target file not found: {target_file}")
        if not target_file.is_file():
            raise ValueError(f"Target is not a file: {target_file}")
        if target_file.suffix != '.py':
            raise ValueError(f"Target must be a Python file: {target_file}")

        # 13. Read file content for analysis
        try:
            content = target_file.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            raise ValueError(f"Cannot read file as UTF-8: {e}")

        # 14. Determine which articles to validate
        articles_to_validate = self.config.article_filter or list(CONSTITUTIONAL_ARTICLES.keys())

        # 15. Run validation for each article
        article_results: List[ArticleAssessment] = []
        tools_used = set()

        for article_num in articles_to_validate:
            if article_num not in CONSTITUTIONAL_ARTICLES:
                continue

            assessment = self._validate_article(
                article_num,
                target_file,
                content
            )
            article_results.append(assessment)

            # 16. Track tools used across all assessments
            for check in assessment.checks_performed:
                tools_used.add(check.tool_used)

        # 17. Calculate overall summary
        summary = self._calculate_summary(article_results, list(tools_used))

        # 18. Generate remediation guidance
        remediation = self._generate_remediation(article_results)

        # 19. Construct validation report
        return {
            "validation_id": validation_id,
            "target_file": str(target_file.absolute()),
            "constitution_version": "1.3.5",
            "overall_status": "PASS" if summary.failed_articles == 0 else "FAIL",
            "summary": summary._asdict(),
            "article_results": [result._asdict() for result in article_results],
            "remediation_guidance": remediation
        }

    def _validate_article(self, article_num: str, target_file: Path, content: str) -> ArticleAssessment:
        """20. Validate a single constitutional article"""
        article_info = CONSTITUTIONAL_ARTICLES[article_num]
        start_time = time.time()
        checks: List[CheckResult] = []
        violations: List[str] = []

        # 21. Dispatch to article-specific validation methods
        try:
            if article_num == "I":
                checks.extend(self._validate_article_i(target_file, content))
            elif article_num == "II":
                checks.extend(self._validate_article_ii(content))
            elif article_num == "III":
                checks.extend(self._validate_article_iii(content))
            elif article_num == "VII":
                checks.extend(self._validate_article_vii(target_file, content))
            elif article_num == "VIII":
                checks.extend(self._validate_article_viii(target_file))
            elif article_num == "XVII":
                checks.extend(self._validate_article_xvii(target_file, content))
            else:
                # 22. For other articles, perform basic structural checks
                checks.extend(self._validate_article_generic(article_num, content))

        except Exception as e:
            # 23. Handle validation errors gracefully
            error_check = CheckResult(
                check_name=f"article_{article_num}_validation",
                tool_used="internal",
                status="ERROR",
                details=f"Validation error: {str(e)}",
                evidence={"error": str(e)},
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            checks.append(error_check)

        # 24. Analyze check results
        failed_checks = [c for c in checks if c.status == "FAIL"]
        warning_checks = [c for c in checks if c.status == "WARNING"]

        # 25. Determine article status and score
        if any(c.status == "ERROR" for c in checks):
            status = "ERROR"
            score = 0.0
        elif failed_checks:
            status = "FAIL"
            score = max(0.0, 1.0 - (len(failed_checks) / len(checks)))
        elif warning_checks and self.config.strict_mode:
            status = "FAIL"
            score = max(0.0, 1.0 - (len(warning_checks) / len(checks)) * 0.5)
        elif warning_checks:
            status = "WARNING"
            score = max(0.5, 1.0 - (len(warning_checks) / len(checks)) * 0.3)
        else:
            status = "PASS"
            score = 1.0

        # 26. Collect violation messages
        for check in failed_checks:
            violations.append(f"{check.check_name}: {check.details}")

        execution_time = int((time.time() - start_time) * 1000)

        return ArticleAssessment(
            article_number=article_num,
            article_title=article_info["title"],
            status=status,
            score=score,
            execution_time_ms=execution_time,
            checks_performed=checks,
            violations=violations
        )

    def _validate_article_i(self, target_file: Path, content: str) -> List[CheckResult]:
        """27. Validate Article I: Single-File Python Programs"""
        checks = []
        start_time = time.time()

        # 28. Check if it's a single file (not a package)
        parent_dir = target_file.parent
        has_init = (parent_dir / "__init__.py").exists()

        single_file_check = CheckResult(
            check_name="single_file_architecture",
            tool_used="internal",
            status="PASS" if not has_init else "WARNING",
            details="File is single Python file" if not has_init else "File is part of a package structure",
            evidence={"is_package": has_init, "file_path": str(target_file)},
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        checks.append(single_file_check)

        # 29. Check for CLI entrypoint
        has_main = 'if __name__ == "__main__":' in content

        cli_check = CheckResult(
            check_name="cli_entrypoint",
            tool_used="internal",
            status="PASS" if has_main else "FAIL",
            details="Has CLI entrypoint" if has_main else "Missing CLI entrypoint",
            evidence={"has_main_guard": has_main},
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        checks.append(cli_check)

        # 30. Check import dependencies (prefer stdlib)
        imports = self._extract_imports(content)
        stdlib_imports = {'pathlib', 'json', 'argparse', 'uuid', 'hashlib', 'datetime',
                         'functools', 'itertools', 'textwrap', 're', 'shutil', 'subprocess', 'typing'}
        external_imports = [imp for imp in imports if imp not in stdlib_imports and not imp.startswith('typing')]

        deps_check = CheckResult(
            check_name="minimal_dependencies",
            tool_used="internal",
            status="PASS" if len(external_imports) <= 3 else "WARNING",
            details=f"External dependencies: {len(external_imports)}" if external_imports else "Uses only stdlib",
            evidence={"external_imports": external_imports, "total_imports": len(imports)},
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        checks.append(deps_check)

        return checks

    def _validate_article_ii(self, content: str) -> List[CheckResult]:
        """31. Validate Article II: Contract-First (JSON Envelopes)"""
        checks = []
        start_time = time.time()

        # 32. Check for Agent Envelope structure in code
        has_envelope = any(term in content for term in ['"meta":', '"input":', '"output":', '"error":'])

        envelope_check = CheckResult(
            check_name="agent_envelope_format",
            tool_used="internal",
            status="PASS" if has_envelope else "FAIL",
            details="Agent Envelope structure found" if has_envelope else "No Agent Envelope structure detected",
            evidence={"envelope_fields_present": has_envelope},
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        checks.append(envelope_check)

        # 33. Check for JSON output handling
        has_json_output = 'json.dumps' in content or 'json.dump' in content

        json_check = CheckResult(
            check_name="json_output",
            tool_used="internal",
            status="PASS" if has_json_output else "WARNING",
            details="JSON output handling found" if has_json_output else "No explicit JSON output handling",
            evidence={"has_json_output": has_json_output},
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        checks.append(json_check)

        return checks

    def _validate_article_iii(self, content: str) -> List[CheckResult]:
        """34. Validate Article III: Decision Tables & Rules"""
        checks = []
        start_time = time.time()

        # 35. Look for decision table patterns
        decision_patterns = ['decision', 'rules', 'table', 'lookup', 'mapping']
        has_decision_logic = any(pattern in content.lower() for pattern in decision_patterns)

        decision_check = CheckResult(
            check_name="decision_tables",
            tool_used="internal",
            status="PASS" if has_decision_logic else "WARNING",
            details="Decision logic patterns found" if has_decision_logic else "No clear decision table patterns",
            evidence={"has_decision_patterns": has_decision_logic},
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        checks.append(decision_check)

        return checks

    def _validate_article_vii(self, target_file: Path, content: str) -> List[CheckResult]:
        """36. Validate Article VII: Type Safety & Defensive Programming"""
        checks = []

        # 37. Run mypy strict validation
        mypy_check = self._run_mypy_validation(target_file)
        checks.append(mypy_check)

        # 38. Check for defensive programming patterns
        defensive_checks = self._check_defensive_programming(content)
        checks.extend(defensive_checks)

        return checks

    def _validate_article_viii(self, target_file: Path) -> List[CheckResult]:
        """39. Validate Article VIII: Testing"""
        checks = []
        start_time = time.time()

        # 40. Look for test files in common locations
        test_dirs = [target_file.parent / "tests", target_file.parent / "test"]
        test_files = []

        for test_dir in test_dirs:
            if test_dir.exists():
                test_files.extend(list(test_dir.glob("test_*.py")))
                test_files.extend(list(test_dir.glob("*_test.py")))

        # 41. Also check for test files next to the target file
        test_pattern = target_file.parent / f"test_{target_file.stem}.py"
        if test_pattern.exists():
            test_files.append(test_pattern)

        test_check = CheckResult(
            check_name="test_presence",
            tool_used="internal",
            status="PASS" if test_files else "FAIL",
            details=f"Found {len(test_files)} test files" if test_files else "No test files found",
            evidence={"test_files": [str(f) for f in test_files]},
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        checks.append(test_check)

        return checks

    def _validate_article_xvii(self, target_file: Path, content: str) -> List[CheckResult]:
        """42. Validate Article XVII: Quality Gates"""
        checks = []

        # 43. Run static analysis tools
        if self.config.parallel_execution:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                futures.append(executor.submit(self._run_pylint_validation, target_file))
                futures.append(executor.submit(self._run_bandit_validation, target_file))
                futures.append(executor.submit(self._run_vulture_validation, target_file))
                futures.append(executor.submit(self._run_radon_validation, target_file))

                for future in as_completed(futures):
                    try:
                        check_result = future.result(timeout=10)
                        checks.append(check_result)
                    except Exception as e:
                        # 44. Handle tool execution errors
                        error_check = CheckResult(
                            check_name="static_analysis_error",
                            tool_used="unknown",
                            status="ERROR",
                            details=f"Tool execution failed: {e}",
                            evidence={"error": str(e)},
                            execution_time_ms=0
                        )
                        checks.append(error_check)
        else:
            # 45. Sequential execution fallback
            checks.append(self._run_pylint_validation(target_file))
            checks.append(self._run_bandit_validation(target_file))
            checks.append(self._run_vulture_validation(target_file))
            checks.append(self._run_radon_validation(target_file))

        return checks

    def _validate_article_generic(self, article_num: str, content: str) -> List[CheckResult]:
        """46. Generic validation for articles without specific implementation"""
        start_time = time.time()

        # 47. Basic structural validation
        basic_check = CheckResult(
            check_name=f"article_{article_num}_basic",
            tool_used="internal",
            status="WARNING",
            details=f"Article {article_num} validation not fully implemented",
            evidence={"article_number": article_num, "content_length": len(content)},
            execution_time_ms=int((time.time() - start_time) * 1000)
        )

        return [basic_check]

    def _run_mypy_validation(self, target_file: Path) -> CheckResult:
        """48. Run mypy strict type checking"""
        start_time = time.time()

        try:
            cmd = [self.tool_config.mypy_path, "--strict", str(target_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            return CheckResult(
                check_name="mypy_strict_compliance",
                tool_used="mypy",
                status="PASS" if success else "FAIL",
                details="mypy --strict passes" if success else f"mypy errors: {output[:200]}",
                evidence={
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                },
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except subprocess.TimeoutExpired:
            return CheckResult(
                check_name="mypy_strict_compliance",
                tool_used="mypy",
                status="ERROR",
                details="mypy execution timed out",
                evidence={"error": "timeout"},
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        except FileNotFoundError:
            return CheckResult(
                check_name="mypy_strict_compliance",
                tool_used="mypy",
                status="ERROR",
                details="mypy not found - install with: pip install mypy",
                evidence={"error": "tool_not_found"},
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _run_pylint_validation(self, target_file: Path) -> CheckResult:
        """49. Run pylint code quality analysis"""
        start_time = time.time()

        try:
            cmd = [self.tool_config.pylint_path, "--score=yes", str(target_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # 50. Extract pylint score
            score_match = re.search(r'Your code has been rated at ([\d.]+)/10', result.stdout)
            score = float(score_match.group(1)) if score_match else 0.0

            passes_threshold = score >= QUALITY_THRESHOLDS["pylint_min_score"]

            return CheckResult(
                check_name="pylint_quality_score",
                tool_used="pylint",
                status="PASS" if passes_threshold else "FAIL",
                details=f"pylint score: {score}/10 (min: {QUALITY_THRESHOLDS['pylint_min_score']})",
                evidence={
                    "score": score,
                    "threshold": QUALITY_THRESHOLDS["pylint_min_score"],
                    "output": result.stdout
                },
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return CheckResult(
                check_name="pylint_quality_score",
                tool_used="pylint",
                status="ERROR",
                details=f"pylint execution failed: {e}",
                evidence={"error": str(e)},
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _run_bandit_validation(self, target_file: Path) -> CheckResult:
        """51. Run bandit security analysis"""
        start_time = time.time()

        try:
            cmd = [self.tool_config.bandit_path, "-f", "json", str(target_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # 52. Parse bandit JSON output
            try:
                bandit_data = json.loads(result.stdout) if result.stdout else {}
                issues = bandit_data.get("results", [])
                high_severity = [i for i in issues if i.get("issue_severity") == "HIGH"]

                has_critical_issues = len(high_severity) > 0

                return CheckResult(
                    check_name="security_vulnerability_scan",
                    tool_used="bandit",
                    status="FAIL" if has_critical_issues else "PASS",
                    details=f"Found {len(high_severity)} high-severity security issues",
                    evidence={
                        "total_issues": len(issues),
                        "high_severity_issues": len(high_severity),
                        "issues": issues[:5]  # Limit evidence size
                    },
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )
            except json.JSONDecodeError:
                # 53. Fallback for non-JSON output
                return CheckResult(
                    check_name="security_vulnerability_scan",
                    tool_used="bandit",
                    status="WARNING",
                    details="Could not parse bandit output",
                    evidence={"output": result.stdout[:500]},
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return CheckResult(
                check_name="security_vulnerability_scan",
                tool_used="bandit",
                status="ERROR",
                details=f"bandit execution failed: {e}",
                evidence={"error": str(e)},
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _run_vulture_validation(self, target_file: Path) -> CheckResult:
        """54. Run vulture dead code detection"""
        start_time = time.time()

        try:
            cmd = [self.tool_config.vulture_path, str(target_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # 55. Vulture returns 0 if no dead code found
            dead_code_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            has_dead_code = len(dead_code_lines) > 0 and dead_code_lines[0]

            return CheckResult(
                check_name="dead_code_detection",
                tool_used="vulture",
                status="WARNING" if has_dead_code else "PASS",
                details=f"Found {len(dead_code_lines)} potential dead code issues" if has_dead_code else "No dead code detected",
                evidence={
                    "dead_code_count": len(dead_code_lines),
                    "issues": dead_code_lines[:10]  # Limit evidence size
                },
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return CheckResult(
                check_name="dead_code_detection",
                tool_used="vulture",
                status="ERROR",
                details=f"vulture execution failed: {e}",
                evidence={"error": str(e)},
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _run_radon_validation(self, target_file: Path) -> CheckResult:
        """56. Run radon complexity analysis"""
        start_time = time.time()

        try:
            cmd = [self.tool_config.radon_path, "cc", "-j", str(target_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # 57. Parse radon JSON output
            try:
                radon_data = json.loads(result.stdout) if result.stdout else {}
                file_data = radon_data.get(str(target_file), [])

                high_complexity = []
                for func_data in file_data:
                    if func_data.get("complexity", 0) > QUALITY_THRESHOLDS["max_complexity"]:
                        high_complexity.append(func_data)

                has_high_complexity = len(high_complexity) > 0

                return CheckResult(
                    check_name="cyclomatic_complexity",
                    tool_used="radon",
                    status="FAIL" if has_high_complexity else "PASS",
                    details=f"Found {len(high_complexity)} functions with complexity > {QUALITY_THRESHOLDS['max_complexity']}",
                    evidence={
                        "total_functions": len(file_data),
                        "high_complexity_count": len(high_complexity),
                        "threshold": QUALITY_THRESHOLDS["max_complexity"],
                        "high_complexity_functions": high_complexity
                    },
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

            except json.JSONDecodeError:
                return CheckResult(
                    check_name="cyclomatic_complexity",
                    tool_used="radon",
                    status="WARNING",
                    details="Could not parse radon output",
                    evidence={"output": result.stdout[:500]},
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return CheckResult(
                check_name="cyclomatic_complexity",
                tool_used="radon",
                status="ERROR",
                details=f"radon execution failed: {e}",
                evidence={"error": str(e)},
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _check_defensive_programming(self, content: str) -> List[CheckResult]:
        """58. Check defensive programming patterns"""
        checks = []
        start_time = time.time()

        # 59. Parse AST to analyze code structure
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            error_check = CheckResult(
                check_name="defensive_programming_syntax",
                tool_used="ast",
                status="ERROR",
                details=f"Syntax error prevents analysis: {e}",
                evidence={"syntax_error": str(e)},
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            return [error_check]

        # 60. Check for if-elif chains without else
        if_elif_issues = []

        class DefensiveChecker(ast.NodeVisitor):
            def visit_If(self, node: ast.If) -> None:
                # 61. Check if this is an if-elif chain without final else
                current = node
                has_elif = False

                while current and hasattr(current, 'orelse') and current.orelse:
                    if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                        # This is an elif
                        has_elif = True
                        current = current.orelse[0]
                    else:
                        # This is an else clause
                        break
                else:
                    # No else clause found
                    if has_elif:
                        if_elif_issues.append(f"Line {node.lineno}: if-elif chain without else clause")

                self.generic_visit(node)

        checker = DefensiveChecker()
        checker.visit(tree)

        # 62. Create check result for defensive programming
        defensive_check = CheckResult(
            check_name="defensive_programming_patterns",
            tool_used="ast",
            status="FAIL" if if_elif_issues else "PASS",
            details=f"Found {len(if_elif_issues)} defensive programming violations" if if_elif_issues else "Defensive programming patterns followed",
            evidence={
                "if_elif_violations": if_elif_issues,
                "violation_count": len(if_elif_issues)
            },
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        checks.append(defensive_check)

        return checks

    def _extract_imports(self, content: str) -> List[str]:
        """63. Extract import statements from Python code"""
        try:
            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split('.')[0])
                else:
                    # Other node types are ignored for import extraction
                    pass

            return list(set(imports))
        except SyntaxError:
            # 64. Fallback to regex if AST parsing fails
            import_pattern = r'^\s*(?:from\s+(\w+)|import\s+(\w+))'
            imports = []
            for line in content.split('\n'):
                match = re.match(import_pattern, line)
                if match:
                    imports.append(match.group(1) or match.group(2))
            return list(set(imports))

    def _calculate_summary(self, article_results: List[ArticleAssessment], tools_used: List[str]) -> ValidationSummary:
        """65. Calculate overall validation summary statistics"""
        total_articles = len(article_results)
        passed_articles = len([r for r in article_results if r.status == "PASS"])
        failed_articles = len([r for r in article_results if r.status == "FAIL"])
        warning_articles = len([r for r in article_results if r.status == "WARNING"])

        # 66. Calculate weighted overall score
        total_weight = sum(CONSTITUTIONAL_ARTICLES[r.article_number]["weight"] for r in article_results)
        weighted_score = sum(
            r.score * CONSTITUTIONAL_ARTICLES[r.article_number]["weight"]
            for r in article_results
        )
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0

        execution_time = int((time.time() - self.start_time) * 1000)

        return ValidationSummary(
            total_articles=total_articles,
            passed_articles=passed_articles,
            failed_articles=failed_articles,
            warning_articles=warning_articles,
            overall_score=overall_score,
            execution_time_ms=execution_time,
            tools_used=tools_used
        )

    def _generate_remediation(self, article_results: List[ArticleAssessment]) -> List[Dict[str, str]]:
        """67. Generate remediation guidance for violations"""
        remediation = []

        for result in article_results:
            if result.status in ["FAIL", "WARNING"]:
                for violation in result.violations:
                    # 68. Create remediation based on violation type
                    priority = "HIGH" if result.status == "FAIL" else "MEDIUM"

                    # 69. Generate specific recommendations
                    recommendation = self._get_remediation_recommendation(
                        result.article_number,
                        violation
                    )

                    remediation.append({
                        "article": result.article_number,
                        "violation": violation,
                        "recommendation": recommendation,
                        "priority": priority,
                        "effort_estimate": self._estimate_effort(violation)
                    })

        return remediation

    def _get_remediation_recommendation(self, article_num: str, violation: str) -> str:
        """70. Get specific remediation recommendation for violation"""
        # 71. Article-specific remediation guidance
        remediation_map = {
            "I": "Ensure single-file architecture with clear CLI entrypoint and minimal dependencies",
            "II": "Implement Agent Envelope output format with meta, input, output, error fields",
            "III": "Add decision tables and structured rule processing before LLM fallback",
            "VII": "Add complete type hints and fix mypy --strict compliance issues",
            "VIII": "Create comprehensive test suite with golden, edge case, and contract tests",
            "XVII": "Address static analysis issues: improve code quality, fix security issues, reduce complexity"
        }

        return remediation_map.get(article_num, "Review constitutional requirements and implement necessary changes")

    def _estimate_effort(self, violation: str) -> str:
        """72. Estimate effort required to fix violation"""
        # 73. Simple effort estimation based on violation type
        if "mypy" in violation.lower():
            return "30-60 minutes"
        elif "test" in violation.lower():
            return "2-4 hours"
        elif "complexity" in violation.lower():
            return "1-2 hours"
        elif "security" in violation.lower():
            return "1-3 hours"
        else:
            return "15-30 minutes"


# ═══════════════════════════════════════════════════════════════════════════
# CLI INTERFACE AND MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

def create_agent_envelope(
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    error: Optional[str] = None,
    brand_token: str = "neutral"
) -> Dict[str, Any]:
    """74. Create Agent Envelope format output"""
    # 75. Generate trace ID and hash
    trace_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat() + "Z"

    # 76. Calculate content hash
    content = json.dumps({
        "input": input_data,
        "output": output_data,
        "error": error
    }, sort_keys=True)
    content_hash = hashlib.sha256(content.encode()).hexdigest()

    # 77. Construct envelope
    return {
        "meta": {
            "agent": "constitutional_compliance_validator",
            "version": "1.0.0",
            "trace_id": trace_id,
            "ts": timestamp,
            "brand_token": brand_token,
            "hash": content_hash,
            "cost": {
                "tokens_in": 0,
                "tokens_out": 0,
                "usd": 0.0
            }
        },
        "input": input_data,
        "output": output_data,
        "error": error
    }

def load_input() -> Tuple[str, Dict[str, Any]]:
    """78. Load and validate input from CLI args or stdin"""
    parser = argparse.ArgumentParser(
        description="Constitutional Compliance Validator v1.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --target-file customer_journey_mapper.py
  %(prog)s --target-file app.py --strict-mode --output report.json
  echo '{"target_file": "/path/file.py"}' | %(prog)s
        """
    )

    # 79. CLI argument definitions
    parser.add_argument(
        "--target-file",
        type=str,
        help="Path to Python file to validate (required)"
    )
    parser.add_argument(
        "--constitution-version",
        type=str,
        default="1.3.5",
        help="Constitution version to validate against (default: 1.3.5)"
    )
    parser.add_argument(
        "--strict-mode",
        action="store_true",
        help="Fail validation on warnings"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Maximum validation time in seconds (default: 30)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--articles",
        type=str,
        help="Comma-separated list of articles to validate (e.g., VII,XVII)"
    )
    parser.add_argument(
        "--brand-token",
        type=str,
        default="neutral",
        help="Brand configuration token (default: neutral)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # 80. Handle JSON input from stdin
    input_content = None
    if not sys.stdin.isatty():
        try:
            stdin_data = sys.stdin.read().strip()
            if stdin_data:
                input_content = json.loads(stdin_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON input from stdin: {e}")

    # 81. Build input data structure
    if input_content:
        # From JSON input
        target_file = input_content.get("target_file")
        if not target_file:
            raise ValueError("target_file is required in JSON input")

        brand_token = input_content.get("brand_token", "neutral")
        validation_config = input_content.get("validation_config", {})
        output_options = input_content.get("output_options", {})

    else:
        # From CLI arguments
        target_file = args.target_file
        if not target_file:
            raise ValueError("--target-file is required")

        brand_token = args.brand_token
        validation_config = {
            "strict_mode": args.strict_mode,
            "timeout_seconds": args.timeout,
            "parallel_execution": True
        }

        if args.articles:
            validation_config["article_filter"] = [
                article.strip()
                for article in args.articles.split(",")
            ]

        output_options = {
            "format": "json",
            "include_evidence": True,
            "include_remediation": True
        }

    # 82. Construct complete input structure
    input_data = {
        "target_file": target_file,
        "constitution_version": args.constitution_version if not input_content else input_content.get("constitution_version", "1.3.5"),
        "validation_config": validation_config,
        "output_options": output_options,
        "brand_token": brand_token
    }

    return args.output if hasattr(args, 'output') else None, input_data

def main() -> None:
    """83. Main execution function with proper error handling"""
    try:
        # 84. Load input and configuration
        output_file, input_data = load_input()

        # 85. Extract configuration
        target_file_str = input_data["target_file"]
        target_file = Path(target_file_str).resolve()

        validation_config_data = input_data.get("validation_config", {})
        validation_config = ValidationConfig(
            strict_mode=validation_config_data.get("strict_mode", False),
            timeout_seconds=validation_config_data.get("timeout_seconds", 30),
            parallel_execution=validation_config_data.get("parallel_execution", True),
            article_filter=validation_config_data.get("article_filter"),
            tool_overrides=validation_config_data.get("tool_overrides")
        )

        tool_overrides = validation_config.tool_overrides or {}
        tool_config = ToolConfig(
            mypy_path=tool_overrides.get("mypy_path", "mypy"),
            pylint_path=tool_overrides.get("pylint_path", "pylint"),
            bandit_path=tool_overrides.get("bandit_path", "bandit"),
            vulture_path=tool_overrides.get("vulture_path", "vulture"),
            radon_path=tool_overrides.get("radon_path", "radon")
        )

        # 86. Initialize validator and run validation
        validator = ConstitutionalComplianceValidator(validation_config, tool_config)
        validation_result = validator.validate_file(target_file)

        # 87. Create Agent Envelope output
        envelope = create_agent_envelope(
            input_data=input_data,
            output_data=validation_result,
            error=None,
            brand_token=input_data.get("brand_token", "neutral")
        )

        # 88. Output results
        output_json = json.dumps(envelope, indent=2, ensure_ascii=False)

        if output_file:
            Path(output_file).write_text(output_json, encoding='utf-8')
            print(f"Validation report written to: {output_file}")
        else:
            print(output_json)

        # 89. Exit with appropriate code
        overall_status = validation_result.get("overall_status", "FAIL")
        sys.exit(0 if overall_status == "PASS" else 1)

    except Exception as e:
        # 90. Handle all errors gracefully
        error_envelope = create_agent_envelope(
            input_data={"error": "Failed to load input"},
            output_data={},
            error=str(e),
            brand_token="neutral"
        )

        print(json.dumps(error_envelope, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()