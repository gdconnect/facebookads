# Constitutional Compliance Validator

A constitutional single-file Python agent that validates other Python agents for compliance with the Schema-First Empire Constitution (v1.3.5).

## Overview

The Constitutional Compliance Validator analyzes Python files to ensure they meet all 16 articles of the Schema-First Empire Constitution. It provides detailed compliance reports, violation detection, and actionable recommendations for achieving full constitutional compliance.

## Features

- **Complete Article Coverage**: Validates all 16 constitutional articles
- **Detailed Reporting**: Comprehensive compliance reports with severity levels
- **Schema-First Design**: Input and output validation against JSON schemas
- **Agent Envelope Output**: Standard envelope format with metadata and cost tracking
- **Automated Analysis**: Static code analysis and runtime behavior validation
- **Actionable Recommendations**: Specific guidance for fixing violations

## Constitutional Compliance

This agent implements all 16 articles of the Schema-First Empire Constitution and serves as the reference implementation for constitutional compliance validation.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run quality checks
make type-check
make lint
make test-constitutional
```

## Usage

### Basic Usage

```bash
# Validate a specific agent
python agents/constitutional_compliance_validator/constitutional_compliance_validator.py \
  --file-path agents/brand_identity_generator/brand_identity_generator.py

# Validate with strict mode
python constitutional_compliance_validator.py \
  --file-path agents/customer_journey_mapper/customer_journey_mapper.py \
  --strict-mode true

# Validate against specific constitution version
python constitutional_compliance_validator.py \
  --file-path my_agent.py \
  --constitution-version 1.3.5
```

### Configuration Options

```bash
# Configuration file
--config config.json

# Brand compliance
--brand-token my-brand-config

# Strict validation mode
--strict-mode true

# Constitution version
--constitution-version 1.3.5

# Logging level
--log-level DEBUG
```

## Input Schema

The agent accepts inputs conforming to `schemas/input.json`:

```json
{
  "file_path": "string (required, must end with .py)",
  "strict_mode": "boolean (default: true)",
  "constitution_version": "string (default: 1.3.5)",
  "input_content_type": "enum [application/json, text/plain]",
  "brand_token": "string"
}
```

## Output Schema

Outputs follow the Agent Envelope format defined in `schemas/output.json`:

```json
{
  "meta": {
    "agent": "constitutional_compliance_validator",
    "version": "1.0.0",
    "trace_id": "uuid",
    "ts": "ISO-8601",
    "brand_token": "string",
    "hash": "sha256",
    "cost": {"tokens_in": 0, "tokens_out": 0, "usd": 0}
  },
  "input": {},
  "output": {
    "compliant": "boolean",
    "score": "number (0-100)",
    "violations": [
      {
        "article": "string",
        "rule": "string",
        "severity": "enum [critical, major, minor, warning]",
        "description": "string",
        "line_number": "integer (optional)"
      }
    ],
    "recommendations": ["string"]
  },
  "error": null
}
```

## Validation Coverage

### Article I - Single-File Python Programs & Agent Organization
- ✅ Single file with CLI entrypoint (`if __name__ == "__main__":`)
- ✅ Proper agent folder structure
- ✅ Minimal external dependencies
- ✅ Justified third-party libraries in docstring

### Article II - Contract-First (JSON Envelopes)
- ✅ Presence of `schemas/input.json` and `schemas/output.json`
- ✅ Agent Envelope output format compliance
- ✅ Schema validation implementation

### Article III - Decision Tables & Rules
- ✅ Decision table implementation before LLM
- ✅ Supported operators (`eq`, `in`, `contains`, `gte_lte`)
- ✅ Rule precedence and human-readable `why` fields
- ✅ Deterministic fallback handling

### Article IV - Input Versatility, Output Consistency
- ✅ Multiple input content type support
- ✅ Markdown to JSON normalization
- ✅ Consistent JSON output format

### Article V - Hierarchical Configuration
- ✅ Configuration precedence order
- ✅ Required CLI flags implementation
- ✅ CONFIG section with ASCII headers

### Article VI - Documentation & Numbered Flow
- ✅ Header docstring completeness
- ✅ Numbered comment flow annotations
- ✅ Usage examples and budget declarations

### Article VII - Type Safety, Modern Python & Defensive Programming
- ✅ Full type hints coverage
- ✅ `mypy --strict` compliance
- ✅ Zero IDE warnings
- ✅ Pydantic v2 best practices
- ✅ Defensive programming patterns

### Article VIII - Testing & Agent Test Organization
- ✅ Golden JSON→JSON tests
- ✅ Golden Markdown→JSON tests (if applicable)
- ✅ Failure/edge-case tests
- ✅ Contract and integration test organization
- ✅ Test performance (<5s runtime)
- ✅ Coverage requirements (≥80%)

### Article IX - Observability & Events
- ✅ JSONL logging to STDERR
- ✅ Required metadata fields
- ✅ Event publishing where applicable

### Article X - LLM Policy (STRICT Default)
- ✅ `llm.enabled=false` by default
- ✅ Confidence threshold validation
- ✅ Budget enforcement
- ✅ Token/cost telemetry

### Article XI - Provider Abstraction
- ✅ Single LLM adapter implementation
- ✅ Supported configuration keys
- ✅ Provider switching capability

### Article XII - Cost & Performance Budgets
- ✅ Budget declarations in docstring
- ✅ Budget enforcement implementation
- ✅ Performance measurement

### Article XIII - Security, Compliance & Brand
- ✅ Brand token implementation
- ✅ Environment variable usage for secrets
- ✅ Compliance gate integration

### Article XIV - Governance & Versioning
- ✅ SemVer compliance
- ✅ Schema versioning
- ✅ Migration strategy

### Article XV - Error Handling and Recovery
- ✅ Comprehensive error handling
- ✅ Graceful degradation
- ✅ Recovery mechanisms

### Article XVI - Prompt Management and Schema Binding
- ✅ Prompt template management
- ✅ Schema-bound responses
- ✅ Version control for prompts

## Severity Levels

- **Critical**: Prevents agent from functioning or violates core constitutional principles
- **Major**: Significant deviation from constitutional requirements
- **Minor**: Style or best practice violations that don't affect functionality
- **Warning**: Recommendations for improvement or potential issues

## Performance Budgets

- **P95 Latency**: <10 seconds for full validation
- **Token Budget**: <1000 tokens (minimal LLM usage)
- **Memory Usage**: <200MB peak
- **File Size Limit**: Up to 10MB Python files

## Testing

```bash
# Run all tests for this agent
make test-constitutional

# Run specific test types
pytest agents/constitutional_compliance_validator/tests/contract/ -v      # Contract tests
pytest agents/constitutional_compliance_validator/tests/integration/ -v  # Integration tests
```

## Examples

```bash
# Validate brand identity generator
make example-validate-brand

# Validate customer journey mapper
make example-validate-journey

# Validate with custom configuration
python constitutional_compliance_validator.py \
  --file-path agents/my_agent/my_agent.py \
  --config custom-validation.json \
  --brand-token enterprise-brand
```

## Development

```bash
# Format code
make format

# Type check
mypy agents/constitutional_compliance_validator/constitutional_compliance_validator.py

# Lint
ruff check agents/constitutional_compliance_validator/

# Run single test
pytest agents/constitutional_compliance_validator/tests/integration/test_constitutional.py -v
```

## Architecture

The validator uses a multi-phase approach:

1. **Static Analysis**: AST parsing for structure and syntax validation
2. **Schema Validation**: JSON schema compliance checking
3. **Runtime Analysis**: Execution behavior validation (when safe)
4. **Documentation Analysis**: Docstring and comment validation
5. **Test Coverage Analysis**: Test suite validation
6. **Performance Analysis**: Budget and performance validation

## License

Part of the Facebook Ads Management System.