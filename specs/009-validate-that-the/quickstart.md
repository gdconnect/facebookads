# Quickstart: Constitutional Compliance Validator

## Overview
The Constitutional Compliance Validator ensures that Python files comply with all 17 articles of the Schema-First Empire Constitution v1.3.5. This tool validates the customer_journey_mapper.py implementation and generates comprehensive compliance reports.

## Prerequisites

### Required Tools
- Python 3.10+ with pip
- mypy (`pip install mypy`)
- pylint (`pip install pylint`)
- bandit (`pip install bandit`)
- vulture (`pip install vulture`)
- radon (`pip install radon`)
- pytest (`pip install pytest`)

### File Requirements
- Target Python file to validate (customer_journey_mapper.py)
- Constitution document (.specify/memory/constitution.md)
- Valid Python environment with required dependencies

## Quick Start

### 1. Basic Validation
```bash
# Validate customer_journey_mapper.py against constitution v1.3.5
python constitutional_compliance_validator.py \
  --target-file /path/to/customer_journey_mapper.py \
  --output validation_report.json
```

### 2. Validation with Custom Configuration
```bash
# Validate with strict mode and specific timeout
python constitutional_compliance_validator.py \
  --target-file /path/to/customer_journey_mapper.py \
  --strict-mode \
  --timeout 60 \
  --output validation_report.json
```

### 3. Validate Specific Articles Only
```bash
# Validate only type safety and quality gates articles
python constitutional_compliance_validator.py \
  --target-file /path/to/customer_journey_mapper.py \
  --articles VII,XVII \
  --output validation_report.json
```

## Input Examples

### Minimal Input (JSON)
```json
{
  "target_file": "/var/www/html/facebookads/customer_journey_mapper.py"
}
```

### Complete Configuration (JSON)
```json
{
  "target_file": "/var/www/html/facebookads/customer_journey_mapper.py",
  "constitution_version": "1.3.5",
  "validation_config": {
    "strict_mode": true,
    "timeout_seconds": 60,
    "parallel_execution": true,
    "article_filter": ["VII", "XVII"],
    "tool_overrides": {
      "mypy_path": "/usr/local/bin/mypy",
      "pylint_path": "/usr/local/bin/pylint"
    }
  },
  "output_options": {
    "format": "json",
    "include_evidence": true,
    "include_remediation": true
  },
  "brand_token": "validation"
}
```

## Expected Outputs

### Successful Validation Report
```json
{
  "meta": {
    "agent": "constitutional_compliance_validator",
    "version": "1.0.0",
    "trace_id": "12345678-1234-1234-1234-123456789012",
    "ts": "2025-09-20T10:30:00Z",
    "brand_token": "validation",
    "hash": "abc123...",
    "cost": {"tokens_in": 0, "tokens_out": 0, "usd": 0.0}
  },
  "input": {
    "target_file": "/var/www/html/facebookads/customer_journey_mapper.py"
  },
  "output": {
    "validation_id": "val_20250920_103000",
    "target_file": "/var/www/html/facebookads/customer_journey_mapper.py",
    "constitution_version": "1.3.5",
    "overall_status": "PASS",
    "summary": {
      "total_articles": 17,
      "passed_articles": 17,
      "failed_articles": 0,
      "warning_articles": 0,
      "overall_score": 1.0,
      "execution_time_ms": 2500,
      "tools_used": ["mypy", "pylint", "bandit", "vulture", "radon"]
    },
    "article_results": [
      {
        "article_number": "I",
        "article_title": "Single-File Python Programs",
        "status": "PASS",
        "score": 1.0,
        "execution_time_ms": 100,
        "checks_performed": [
          {
            "check_name": "single_file_architecture",
            "tool_used": "internal",
            "status": "PASS",
            "details": "File is single Python file with CLI entrypoint",
            "execution_time_ms": 50
          }
        ],
        "violations": []
      }
    ]
  },
  "error": null
}
```

### Validation with Violations
```json
{
  "overall_status": "FAIL",
  "summary": {
    "total_articles": 17,
    "passed_articles": 15,
    "failed_articles": 2,
    "warning_articles": 0,
    "overall_score": 0.82
  },
  "article_results": [
    {
      "article_number": "VII",
      "article_title": "Type Safety, Modern Python & Defensive Programming",
      "status": "FAIL",
      "score": 0.3,
      "violations": [
        "Missing type hints on function: load_input",
        "Unbound variable: input_content (line 320)"
      ]
    }
  ],
  "remediation_guidance": [
    {
      "article": "VII",
      "violation": "Missing type hints on function: load_input",
      "recommendation": "Add complete type hints to function signature and return type",
      "priority": "HIGH",
      "effort_estimate": "15 minutes"
    }
  ]
}
```

## Validation Scenarios

### Scenario 1: Full Constitutional Compliance
**Given**: customer_journey_mapper.py fully compliant with constitution v1.3.5
**When**: Run basic validation command
**Then**:
- Overall status = PASS
- All 17 articles pass validation
- Overall score = 1.0
- No violations reported
- Execution time < 5 seconds

### Scenario 2: Type Safety Violations
**Given**: customer_journey_mapper.py with missing type hints
**When**: Run validation with strict mode
**Then**:
- Overall status = FAIL
- Article VII fails validation
- Specific type safety violations listed
- Remediation guidance provided
- Tool outputs included as evidence

### Scenario 3: Quality Gate Failures
**Given**: customer_journey_mapper.py with high complexity functions
**When**: Run validation targeting Article XVII
**Then**:
- Article XVII fails validation
- Radon complexity metrics show violations
- Specific functions flagged for refactoring
- Priority and effort estimates provided

### Scenario 4: Missing Dependencies
**Given**: Static analysis tools not installed
**When**: Run validation
**Then**:
- Tool availability checks fail
- Clear error messages about missing tools
- Guidance on installing required dependencies
- Graceful degradation where possible

## Performance Expectations

### Timing Benchmarks
- **Full validation**: < 5 seconds
- **Type checking**: < 2 seconds
- **Quality analysis**: < 1 second
- **Security scan**: < 1 second
- **Report generation**: < 500ms

### Resource Usage
- **Memory**: < 100MB peak usage
- **CPU**: Utilizes available cores for parallel execution
- **Disk**: Minimal temporary file usage
- **Network**: No external dependencies

## Troubleshooting

### Common Issues

#### Tool Not Found Errors
```bash
Error: mypy not found in PATH
```
**Solution**: Install missing tools with pip or specify custom paths in configuration

#### Permission Denied
```bash
Error: Permission denied reading target file
```
**Solution**: Ensure file is readable and path is absolute

#### Timeout Exceeded
```bash
Error: Validation exceeded 30 second timeout
```
**Solution**: Increase timeout or disable parallel execution for large files

#### Invalid Constitution Version
```bash
Error: Constitution version 1.2.0 not supported
```
**Solution**: Update to constitution v1.3.5 or specify correct version

### Debug Mode
Enable verbose logging for troubleshooting:
```bash
python constitutional_compliance_validator.py \
  --target-file /path/to/file.py \
  --log-level DEBUG \
  --output report.json
```

## Next Steps

1. **Review Results**: Examine validation report for any violations
2. **Fix Issues**: Address high-priority violations first
3. **Re-validate**: Run validation again after fixes
4. **Integrate**: Add validation to CI/CD pipeline
5. **Monitor**: Track compliance scores over time

## Integration Examples

### CI/CD Pipeline
```yaml
- name: Constitutional Compliance Check
  run: |
    python constitutional_compliance_validator.py \
      --target-file src/my_agent.py \
      --strict-mode \
      --output compliance_report.json

    # Fail build if validation fails
    if [ "$(jq -r '.output.overall_status' compliance_report.json)" != "PASS" ]; then
      echo "Constitutional compliance check failed"
      exit 1
    fi
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
python constitutional_compliance_validator.py \
  --target-file $(git diff --name-only --cached | grep '\.py$') \
  --strict-mode \
  || exit 1
```

This quickstart provides everything needed to begin validating Python files against the constitutional requirements.