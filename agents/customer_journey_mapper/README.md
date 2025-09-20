# Customer Journey Mapper Generator

A constitutional single-file Python agent that generates comprehensive customer journey maps for niche markets based on market specifications.

## Overview

The Customer Journey Mapper Generator takes natural language descriptions of niche markets and produces detailed customer journey maps that conform to the `customer_journey.json.schema`. This agent is designed to follow the Schema-First Empire Constitution principles with LLM integration for input normalization and decision tables for deterministic business logic.

## Features

- **Schema-First Design**: Input and output validation against JSON schemas
- **Agent Envelope Output**: Standard envelope format with metadata and cost tracking
- **LLM Integration**: Input normalization from markdown/text to JSON
- **Decision Tables**: Deterministic business logic for market classification and journey patterns
- **Multiple Input Formats**: Support for markdown, JSON, and plain text inputs
- **Performance Optimized**: <5s runtime, <2 LLM calls, <2000 tokens

## Constitutional Compliance

This agent implements all 16 articles of the Schema-First Empire Constitution:

- ✅ **Article I**: Single-file Python program with CLI entrypoint in dedicated folder
- ✅ **Article II**: JSON schemas for input/output validation and Agent Envelope format
- ✅ **Article III**: Decision tables for business logic before LLM fallback
- ✅ **Article IV**: Input versatility (markdown/JSON/text) with consistent JSON output
- ✅ **Article V**: Hierarchical configuration with CLI flags and environment variables
- ✅ **Article VI**: Documentation with numbered flow and usage examples
- ✅ **Article VII**: Type safety with mypy --strict compliance
- ✅ **Article VIII**: Comprehensive testing (golden, contract, integration)
- ✅ **Article IX**: JSONL observability logging to STDERR
- ✅ **Article X**: STRICT mode LLM policy with budgets
- ✅ **Article XI**: Provider abstraction for OpenAI/Anthropic/Gemini/Local
- ✅ **Article XII**: Declared performance budgets
- ✅ **Article XIII**: Brand token security and compliance
- ✅ **Article XIV**: SemVer versioning and governance
- ✅ **Article XV**: Error handling and recovery
- ✅ **Article XVI**: Prompt management and schema binding

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run quality checks
make type-check
make lint
make test-journey
```

## Usage

### Basic Usage

```bash
# Generate journey for e-commerce market
python agents/customer_journey_mapper/customer_journey_mapper.py \
  --market-description "Eco-conscious millennials interested in sustainable fashion" \
  --industry ecommerce

# Generate journey for SaaS market
python agents/customer_journey_mapper/customer_journey_mapper.py \
  --market-description "Small business owners looking for accounting software solutions" \
  --industry saas
```

### Input Formats

**Command Line (JSON-like)**:
```bash
python customer_journey_mapper.py \
  --market-description "Healthcare professionals seeking telemedicine platforms" \
  --industry healthcare \
  --target-demographics '{"age": "35-45", "location": "Urban areas"}' \
  --business-model B2B
```

**Markdown File Input**:
```bash
python customer_journey_mapper.py input.md --input-content-type text/markdown
```

**JSON File Input**:
```bash
python customer_journey_mapper.py input.json --input-content-type application/json
```

### Configuration Options

```bash
# Configuration file
--config config.json

# Brand compliance
--brand-token my-brand-config

# Strict mode (no LLM calls)
--strict

# Logging level
--log-level DEBUG
```

## Input Schema

The agent accepts inputs conforming to `schemas/input.json`:

```json
{
  "market_description": "string (required)",
  "industry": "enum [ecommerce, saas, healthcare, ...]",
  "target_demographics": {
    "age": "string",
    "location": "string",
    "occupation": "string",
    "income": "string"
  },
  "product_service": "string",
  "business_model": "enum [B2B, B2C, B2B2C, ...]",
  "input_content_type": "enum [text/markdown, application/json, text/plain]",
  "brand_token": "string"
}
```

## Output Schema

Outputs follow the Agent Envelope format defined in `schemas/output.json`:

```json
{
  "meta": {
    "agent": "customer_journey_mapper",
    "version": "1.0.0",
    "trace_id": "uuid",
    "ts": "ISO-8601",
    "brand_token": "string",
    "hash": "sha256",
    "cost": {"tokens_in": 0, "tokens_out": 0, "usd": 0}
  },
  "input": {},
  "output": {
    "customer_journey": {
      // Full customer journey map structure
    }
  },
  "error": null
}
```

## Decision Tables

The agent uses decision tables for deterministic business logic:

1. **Market Classification**: Maps industry + demographics to journey patterns
2. **Journey Templates**: Selects appropriate journey structure based on business model
3. **Touchpoint Generation**: Determines relevant touchpoints for each journey stage
4. **Content Personalization**: Adapts messaging based on target demographics

## Performance Budgets

- **P95 Latency**: <5 seconds end-to-end
- **Token Budget**: <2000 tokens total
- **LLM Calls**: ≤2 calls maximum
- **Cost Budget**: <$0.01 per generation
- **Memory Usage**: <100MB peak

## Testing

```bash
# Run all tests for this agent
make test-journey

# Run specific test types
pytest agents/customer_journey_mapper/tests/contract/ -v      # Contract tests
pytest agents/customer_journey_mapper/tests/integration/ -v  # Integration tests
pytest agents/customer_journey_mapper/tests/golden/ -v       # Golden tests
```

## Examples

See the `examples/` directory for sample inputs and outputs:

- E-commerce journey examples
- SaaS journey examples
- Healthcare journey examples
- Markdown input examples

## Development

```bash
# Format code
make format

# Type check
mypy agents/customer_journey_mapper/customer_journey_mapper.py

# Lint
ruff check agents/customer_journey_mapper/

# Run single test
pytest agents/customer_journey_mapper/tests/integration/test_ecommerce_journey.py -v
```

## License

Part of the Facebook Ads Management System.