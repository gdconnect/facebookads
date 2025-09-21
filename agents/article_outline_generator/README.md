# Article Outline Generator

Constitutional single-file Python agent for generating structured outlines from markdown content descriptions.

## Features

- **Content Type Detection**: Automatically classifies content as "article" or "story"
- **Language Detection**: Identifies input language using heuristic patterns
- **Hierarchical Outlines**: Generates nested sections with configurable depth (1-6 levels)
- **Rich Metadata**: Includes section summaries, key points, and word count estimates
- **Constitutional Compliance**: Single-file agent following schema-first principles
- **Performance Optimized**: <5s runtime, <2 LLM calls, <2000 tokens per execution

## Enhanced Features (Feature 012)

- **Interim Classification**: Get early classification results before full outline generation
- **LLM Fallback**: PydanticAI integration for ambiguous content when confidence < 0.8
- **Enhanced Metadata**: Classification confidence, method, reasoning, and key indicators
- **Cost Tracking**: Token usage and USD cost monitoring for LLM calls
- **Flexible Classification**: Multiple methods (auto, rules_only, llm_preferred)

## Quick Start

```bash
# Install dependencies
pip install pydantic>=2 pydantic-ai

# Basic usage - article outline
echo "# Sustainable Gardening Practices

This article covers practical approaches to sustainable gardening including composting techniques, water conservation methods, native plant selection, and organic pest control strategies." | python article_outline_generator.py run

# Story outline with custom depth
python article_outline_generator.py run --target-depth 4 << 'EOF'
{
  "content": "# The Mars Expedition\n\nA science fiction story about the first human mission to Mars...",
  "target_depth": 4,
  "include_word_counts": true
}
EOF

# Validate agent installation
python article_outline_generator.py selfcheck

# Enhanced features - interim classification
echo "# Quick Article\n\nContent that needs fast classification." | python article_outline_generator.py run --interim

# Enhanced features - JSON with classification options
python article_outline_generator.py run --input-type json << 'EOF'
{
  "content": "# Ambiguous Content\n\nContent that might benefit from LLM analysis...",
  "interim": true,
  "classification_method": "auto",
  "timeout_ms": 2000
}
EOF
```

## Usage

### Command Line Interface

```bash
# Run with markdown input
python article_outline_generator.py run [OPTIONS]

# Available commands
python article_outline_generator.py {run|selfcheck|print-schemas|dry-run}

# Options
--input-type {markdown|json}     # Input format (default: markdown)
--target-depth N                 # Outline depth 1-6 (default: 3)
--output FILE                    # Output file (default: stdout)
--config FILE                    # Configuration file
--strict                         # Disable LLM fallback

# Enhanced options (Feature 012)
--interim                        # Return interim classification only
--classification-method {auto|rules_only|llm_preferred}  # Classification strategy
--timeout-ms N                   # Timeout for interim responses (100-30000ms)
--log-level {DEBUG|INFO|WARN|ERROR}
```

### Input Formats

**Markdown Input (default):**
```bash
echo "# Article Title\n\nContent description..." | python article_outline_generator.py run
```

**JSON Input:**
```bash
python article_outline_generator.py run --input-type json << 'EOF'
{
  "content": "# Article Title\n\nContent description...",
  "target_depth": 3,
  "content_type_hint": "article",
  "language_hint": "en",
  "include_word_counts": true
}
EOF
```

**Enhanced JSON Input (Feature 012):**
```bash
python article_outline_generator.py run --input-type json << 'EOF'
{
  "content": "# Ambiguous Content\n\nContent that benefits from LLM analysis...",
  "target_depth": 3,
  "interim": true,
  "classification_method": "auto",
  "timeout_ms": 2000
}
EOF
```

### Output Format

The agent returns a structured JSON envelope:

```json
{
  "meta": {
    "agent": "article_outline_generator",
    "version": "1.0.0",
    "trace_id": "...",
    "ts": "2025-09-21T10:30:00Z",
    "brand_token": "default",
    "hash": "...",
    "cost": {"tokens_in": 150, "tokens_out": 800, "usd": 0.002}
  },
  "input": {
    "content": "# Article Title...",
    "target_depth": 3,
    "include_word_counts": true
  },
  "output": {
    "meta": {
      "content_type": "article",
      "detected_language": "en",
      "depth": 3,
      "sections_count": 5,
      "generated_at": "2025-09-21T10:30:00Z",
      "classification_confidence": 0.85,
      "classification_method": "rule_based",
      "classification_reasoning": "Instructional content",
      "llm_calls_used": 0,
      "processing_time_ms": 150,
      "interim_available": false
    },
    "outline": [
      {
        "id": "introduction",
        "level": 1,
        "title": "Introduction",
        "summary": "Overview of sustainable gardening practices...",
        "key_points": ["Define sustainable gardening", "Benefits overview"],
        "word_count_estimate": 200,
        "subsections": []
      }
    ]
  },
  "error": null
}
```

### Enhanced Usage Examples (Feature 012)

**Interim Classification** (fast response, classification only):
```bash
echo "# Quick Analysis\nContent for rapid classification." | python article_outline_generator.py run --interim
# Returns: {"output": {"meta": {...}, "outline": []}, ...}
```

**LLM-Enhanced Classification** (for ambiguous content):
```bash
# Set up LLM (optional - only for low confidence content)
export OPENAI_API_KEY="your-key"
export LLM_ENABLED=true

echo "# Ambiguous Content\nCould be article or story..." | python article_outline_generator.py run --classification-method auto
# May use LLM if confidence < 0.8
```

**Cost Tracking**:
```bash
# Monitor LLM usage
python article_outline_generator.py run --input-type json << 'EOF'
{"content": "# Content", "classification_method": "auto"}
EOF
# Check output.meta.cost for tokens/USD usage
```

## Architecture

### Constitutional Compliance

This agent follows the [Constitutional Framework](../../.specify/memory/constitution.md):

- **Single-file**: All logic in `article_outline_generator.py`
- **Schema-first**: Pydantic models with JSON schema generation
- **Rules-first**: Decision tables before LLM fallback
- **Typed**: Full mypy --strict compliance
- **Tested**: Contract, integration, and golden tests
- **Observable**: JSONL logging to STDERR

### Decision Tables

**Content Type Classification:**
- Narrative keywords (character, plot, story) → "story"
- Instructional keywords (how-to, guide, steps) → "article"
- Past tense dominance → "story"
- Imperative mood → "article"

**Language Detection:**
- English stopwords (the, and, of) → "en"
- French stopwords (le, la, de) → "fr"
- Non-Latin characters → script-based detection

### Performance Budget

- **Runtime**: <5 seconds per execution
- **LLM Calls**: <2 calls (fallback only)
- **Token Usage**: <2000 tokens total
- **Memory**: <100MB working set

## Development

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m contract        # Schema validation tests
pytest -m integration     # End-to-end scenarios
pytest -m golden          # Real-world examples
pytest -m unit           # Component tests

# Run with coverage
pytest --cov=article_outline_generator --cov-report=html
```

### Code Quality

```bash
# Format code
black article_outline_generator.py

# Lint code
ruff check article_outline_generator.py

# Type check
mypy --strict article_outline_generator.py

# Quality score
pylint article_outline_generator.py

# Security scan
bandit article_outline_generator.py
```

### Project Structure

```
agents/article_outline_generator/
├── article_outline_generator.py    # Single-file agent (main implementation)
├── tests/
│   ├── contract/                   # Schema validation tests
│   ├── integration/               # End-to-end scenarios
│   ├── golden/                    # Real-world examples
│   ├── unit/                      # Component tests
│   └── performance/               # Performance validation
├── schemas/                       # JSON schemas (CI generated)
├── docs/                         # Additional documentation
├── examples/                     # Sample input files
├── pyproject.toml               # Project configuration
├── README.md                    # This file
└── __init__.py                  # Package initialization
```

## Configuration

### Environment Variables

```bash
# Model configuration (Feature 012 - LLM fallback)
LLM_ENABLED=false                   # Enable LLM fallback for low confidence content
AGENT_MODEL_ENABLED=false           # Legacy alias for LLM_ENABLED
AGENT_MODEL_PROVIDER=openai         # LLM provider (openai, anthropic, gemini)
AGENT_MODEL_NAME=gpt-4o-mini        # Model name
AGENT_MODEL_API_KEY_ENV=OPENAI_API_KEY  # API key environment variable
AGENT_MODEL_TIMEOUT_S=30            # Request timeout
AGENT_MODEL_MAX_TOKENS=2000         # Token limit per request

# Agent configuration
AGENT_BRAND_TOKEN=default           # Brand/compliance token
AGENT_LOG_LEVEL=INFO               # Logging level
```

### Configuration File

```json
{
  "model": {
    "enabled": false,
    "provider": "openai",
    "name": "gpt-4",
    "api_key_env": "OPENAI_API_KEY",
    "timeout_s": 30,
    "max_tokens": 2000,
    "temperature": 0.1
  },
  "agent": {
    "brand_token": "default",
    "log_level": "INFO"
  }
}
```

## Contributing

1. Follow constitutional requirements (single-file, schema-first, rules-first)
2. Maintain mypy --strict compliance
3. Add tests for new functionality
4. Update schemas if models change
5. Verify performance budgets
6. Update documentation

## License

MIT License - see LICENSE file for details.