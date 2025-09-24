# Data Model: Flexible Business Idea Generator

**Feature**: 016-flexible-business-idea
**Date**: 2025-09-24

## Core Entities

### 1. FlexibleExtractionConfig
Configuration for flexible markdown parsing behavior.

**Fields**:
- `fuzzy_threshold: float` - Similarity threshold for fuzzy section matching (0.0-1.0)
- `confidence_threshold: float` - Minimum confidence to avoid LLM fallback (0.0-1.0)
- `max_section_depth: int` - Maximum heading depth to consider (1-6)
- `section_mappings: dict[str, list[str]]` - Maps field names to possible section headers
- `max_document_lines: int` - Maximum lines to process (default: 2000)
- `fallback_enabled: bool` - Whether to use LLM fallback for low confidence

**Validation Rules**:
- `fuzzy_threshold` must be between 0.0 and 1.0
- `confidence_threshold` must be between 0.0 and 1.0
- `max_section_depth` must be between 1 and 6
- `section_mappings` must contain all required fields (problem, solution)

### 2. SectionMapping
Rules for mapping various section names to standard fields.

**Fields**:
- `field_name: str` - Target field name (problem, solution, etc.)
- `aliases: list[str]` - Alternative section names that map to this field
- `required: bool` - Whether this field is required for valid extraction
- `weight: float` - Importance weight for confidence calculation

**Validation Rules**:
- `field_name` must be a valid RawIdea field
- `aliases` must contain at least one entry
- `weight` must be between 0.0 and 1.0

### 3. ExtractionStrategy (Enum)
Strategy used for content extraction.

**Values**:
- `EXACT_MATCH` - Exact section header matching
- `FUZZY_MATCH` - Similarity-based section matching
- `HIERARCHICAL` - Structure-based content detection
- `LLM_FALLBACK` - AI-based content extraction
- `HYBRID` - Combination of multiple strategies

### 4. ExtractionResult
Detailed result of markdown parsing attempt.

**Fields**:
- `raw_idea: RawIdea | None` - Successfully extracted business idea
- `strategy_used: ExtractionStrategy` - Primary strategy that succeeded
- `confidence_score: float` - Overall confidence in extraction (0.0-1.0)
- `field_confidences: dict[str, float]` - Per-field confidence scores
- `section_matches: dict[str, str]` - Mapping of found sections to fields
- `warnings: list[ExtractionWarning]` - Non-fatal issues found
- `errors: list[ExtractionError]` - Fatal errors preventing extraction
- `processing_time_ms: int` - Time taken for extraction
- `llm_tokens_used: int` - Tokens consumed by LLM calls (if any)

**State Transitions**:
1. INITIALIZED → ANALYZING (start extraction)
2. ANALYZING → SUCCESS (valid extraction)
3. ANALYZING → PARTIAL_SUCCESS (missing optional fields)
4. ANALYZING → FAILED (missing required fields)
5. Any state → TIMEOUT (processing exceeded limits)

### 5. ExtractionWarning
Non-fatal issues during extraction.

**Fields**:
- `field: str` - Field name related to warning
- `issue: str` - Description of the issue
- `suggestion: str` - Actionable recommendation
- `section_found: str | None` - Section that caused the warning

**Examples**:
- Field too long (truncated)
- Multiple sections mapping to same field
- Unusual section structure detected

### 6. ExtractionError
Fatal errors preventing successful extraction.

**Fields**:
- `field: str` - Field name related to error
- `issue: str` - Description of the error
- `suggestion: str` - How to fix the issue
- `severity: Literal["error", "critical"]` - Error severity level

**Examples**:
- Required field missing entirely
- Document structure unrecognizable
- Content exceeds maximum size limits

### 7. Enhanced RawIdea
Extended version of existing RawIdea with extraction metadata.

**New Fields** (added to existing):
- `extraction_metadata: ExtractionMetadata` - Information about how fields were extracted

**Validation Rules** (enhanced):
- All existing validation plus:
- Field length limits with graceful truncation
- Content quality scoring
- Language detection for non-English content

### 8. ExtractionMetadata
Metadata about the extraction process.

**Fields**:
- `source_sections: dict[str, str]` - Original section headers that provided each field
- `extraction_method: dict[str, ExtractionStrategy]` - Method used for each field
- `confidence_breakdown: dict[str, float]` - Detailed confidence scoring
- `processing_notes: list[str]` - Internal processing notes
- `document_stats: DocumentStats` - Statistics about the source document

### 9. DocumentStats
Statistics about the processed markdown document.

**Fields**:
- `total_lines: int` - Total lines in document
- `section_count: int` - Number of sections found
- `heading_levels: list[int]` - Heading levels present (1-6)
- `content_length: int` - Total character count
- `language_detected: str | None` - Detected language code
- `structure_complexity: Literal["simple", "moderate", "complex"]` - Document complexity

## Relationships

```
FlexibleExtractionConfig
    ├── contains → SectionMapping (1:many)
    └── controls → ExtractionResult (1:many)

ExtractionResult
    ├── produces → RawIdea (1:1 optional)
    ├── contains → ExtractionWarning (1:many)
    ├── contains → ExtractionError (1:many)
    └── includes → ExtractionMetadata (1:1)

ExtractionMetadata
    ├── references → DocumentStats (1:1)
    └── maps to → ExtractionStrategy (many:1)

RawIdea
    └── enhanced with → ExtractionMetadata (1:1)
```

## Decision Tables Integration

### Section Mapping Decision Table
```python
SECTION_MAPPING_RULES = [
    {
        "condition": {"header_exact": "problem"},
        "action": {"field": "problem", "confidence": 1.0}
    },
    {
        "condition": {"header_contains": ["problem", "challenge", "issue"]},
        "action": {"field": "problem", "confidence": 0.9}
    },
    {
        "condition": {"header_fuzzy_match": "problem", "threshold": 0.8},
        "action": {"field": "problem", "confidence": 0.8}
    }
    # ... more rules
]
```

### Extraction Strategy Decision Table
```python
STRATEGY_SELECTION_RULES = [
    {
        "condition": {"exact_matches": ">= 2", "required_fields": "all"},
        "action": {"strategy": "EXACT_MATCH", "confidence_bonus": 0.2}
    },
    {
        "condition": {"fuzzy_matches": ">= 2", "confidence": ">= 0.7"},
        "action": {"strategy": "FUZZY_MATCH", "confidence_bonus": 0.1}
    },
    {
        "condition": {"confidence": "< 0.5", "llm_enabled": True},
        "action": {"strategy": "LLM_FALLBACK", "confidence_override": True}
    }
]
```

## Performance Considerations

1. **Caching Strategy**:
   - Compile regex patterns once
   - Cache section mapping lookups
   - Memoize fuzzy match calculations

2. **Memory Management**:
   - Stream large documents instead of loading entirely
   - Limit section content size during extraction
   - Clean up intermediate parsing results

3. **Processing Limits**:
   - Maximum 2000 lines per document
   - 30-second timeout for complex documents
   - 50MB memory limit per extraction

## Backward Compatibility

- All existing RawIdea fields remain unchanged
- New fields are optional with sensible defaults
- Existing API contracts preserved
- Configuration changes are additive only

## Future Extensions

1. **Multi-language Support**:
   - Language-specific section name mappings
   - Character encoding detection
   - Localized error messages

2. **Advanced Extraction**:
   - Table extraction for financial data
   - Image/diagram analysis
   - Cross-reference resolution

3. **Learning System**:
   - Track successful extraction patterns
   - Adapt confidence thresholds based on success rates
   - User feedback incorporation
