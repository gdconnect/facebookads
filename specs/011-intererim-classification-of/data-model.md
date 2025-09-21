# Data Model: Content Classification System

**Feature**: 011-intererim-classification-of
**Date**: 2025-09-21
**Source**: Derived from spec.md functional requirements

## Core Entities

### Content
**Purpose**: Represents text content requiring classification
**Attributes**:
- `text`: Raw content text (required, min_length=1)
- `metadata`: Optional content metadata (author, source, date)
- `content_type_hint`: Optional user-provided hint ("article" | "essay")
- `language_hint`: Optional language code (default: auto-detect)

**Validation Rules**:
- Content text cannot be empty or whitespace-only
- Metadata must be valid JSON if provided
- Content type hint must be "article" or "essay" if specified

### Classification Request
**Purpose**: Represents a classification task with execution parameters
**Attributes**:
- `content`: Content entity to classify (required)
- `interim`: Boolean flag for interim processing (default: false)
- `max_llm_calls`: Maximum LLM calls allowed (default: 2, max: 2)
- `confidence_threshold`: Threshold for LLM fallback (default: 0.7)
- `timeout_ms`: Maximum processing time (default: 5000)

**Validation Rules**:
- max_llm_calls must be 0-2
- confidence_threshold must be 0.0-1.0
- timeout_ms must be positive integer

### Classification Result
**Purpose**: Contains classification outcome with metadata
**Attributes**:
- `content_type`: Classified type ("article" | "essay")
- `confidence`: Confidence score (0.0-1.0)
- `method`: Classification method used ("rule_based" | "llm_single" | "llm_double")
- `reasoning`: Optional explanation for classification (present for LLM results)
- `processing_time_ms`: Actual processing time
- `llm_calls_used`: Number of LLM calls made (0-2)

**State Transitions**:
1. Initial → Rule-based classification
2. If confidence < threshold → LLM classification (first call)
3. If still uncertain → LLM refinement (second call)
4. Final → Return best available result

### Batch Classification Request
**Purpose**: Handles multiple content pieces in single request
**Attributes**:
- `items`: List of ClassificationRequest objects
- `fail_fast`: Stop on first error (default: false)
- `max_parallel`: Maximum concurrent processing (default: 1)

**Validation Rules**:
- items list cannot be empty
- max_parallel must be positive integer ≤ 10

### Error Model
**Purpose**: Structured error responses with actionable information
**Attributes**:
- `code`: Error code ("VALIDATION_ERROR" | "TIMEOUT_ERROR" | "LLM_ERROR" | "UNKNOWN_ERROR")
- `message`: Human-readable error description
- `details`: Optional additional error context
- `retry_possible`: Boolean indicating if retry might succeed

## Agent Envelope Structure

Following Constitutional Article II requirements:

```json
{
  "meta": {
    "agent": "content_classifier",
    "version": "1.0.0",
    "trace_id": "uuid4",
    "ts": "ISO-8601",
    "brand_token": "default",
    "hash": "sha256",
    "cost": {
      "tokens_in": 0,
      "tokens_out": 0,
      "usd": 0.0
    },
    "prompt_id": "string|null",
    "prompt_hash": "sha256|null"
  },
  "input": {
    // ClassificationRequest or BatchClassificationRequest
  },
  "output": {
    // ClassificationResult or BatchClassificationResult
  },
  "error": null // ErrorModel if failed
}
```

## Decision Table Entities

### Classification Rule
**Purpose**: Represents a single classification rule in decision tables
**Attributes**:
- `pattern`: Regex pattern to match content
- `content_type`: Target classification ("article" | "essay")
- `confidence`: Rule confidence score (0.0-1.0)
- `reasoning`: Human-readable explanation
- `priority`: Rule evaluation order (lower = higher priority)

### Rule Evaluation Result
**Purpose**: Result of applying a single classification rule
**Attributes**:
- `rule_id`: Identifier of the applied rule
- `matched`: Whether the rule pattern matched
- `confidence`: Confidence if matched
- `reasoning`: Why this rule applied
- `elapsed_ms`: Time to evaluate this rule

## LLM Integration Entities

### LLM Classification Request
**Purpose**: Structured request for LLM-based classification
**Attributes**:
- `content_text`: Text to classify
- `previous_result`: Optional previous classification result
- `classification_type`: "initial" | "refinement"
- `max_tokens`: Token budget for this call

### LLM Classification Response
**Purpose**: Structured response from LLM classification
**Attributes**:
- `content_type`: LLM's classification ("article" | "essay")
- `confidence`: LLM's confidence score (0.0-1.0)
- `reasoning`: LLM's explanation
- `alternative_type`: Alternative classification considered
- `key_indicators`: List of content features that influenced decision

## Relationships

1. **ClassificationRequest** contains **Content**
2. **ClassificationResult** references **ClassificationRequest**
3. **BatchClassificationRequest** contains multiple **ClassificationRequest**
4. **Rule Evaluation** produces **Classification Result**
5. **LLM Request** produces **LLM Response** which becomes **Classification Result**

## Validation Constraints

### Performance Constraints
- Total processing time ≤ 5000ms
- Rule-based classification ≤ 200ms
- Individual LLM call ≤ 2000ms
- Total LLM tokens ≤ 2000 per request

### Business Constraints
- Classification must be deterministic for identical input
- Confidence scores must be consistently scaled across methods
- LLM reasoning must be actionable and specific
- Batch processing must handle partial failures gracefully

### Data Integrity
- All timestamps in UTC with millisecond precision
- All monetary amounts in USD with 4 decimal places
- All confidence scores normalized to 0.0-1.0 range
- All text fields sanitized to prevent injection attacks
