# Research: Flexible Business Idea Generator

**Feature**: 016-flexible-business-idea
**Date**: 2025-09-24

## Research Objectives

1. Flexible markdown parsing strategies for Python
2. LLM-based content extraction with PydanticAI
3. Section name normalization patterns
4. Fuzzy string matching for section headers

## Findings

### 1. Flexible Markdown Parsing Strategies

**Decision**: Multi-strategy approach with progressive enhancement
- Primary: Regex-based section detection with fuzzy matching
- Secondary: Hierarchical content analysis
- Tertiary: LLM-based extraction for ambiguous cases

**Rationale**:
- Regex provides fast, deterministic parsing for well-formed documents
- Hierarchical analysis handles nested structures
- LLM fallback ensures robustness for edge cases

**Alternatives Considered**:
- Pure regex parsing (rejected: too rigid for varied formats)
- Markdown AST parsing (rejected: doesn't help with semantic section mapping)
- Pure LLM extraction (rejected: too expensive for simple cases)

### 2. Section Name Mapping Rules

**Decision**: Decision table with similarity scoring
```python
SECTION_MAPPINGS = {
    "problem": ["problem", "challenge", "pain point", "issue", "identifying the problem", "problem statement"],
    "solution": ["solution", "approach", "proposed solution", "our solution", "how we solve it"],
    "target_customer": ["target", "customer", "audience", "users", "who we serve", "target market"],
    "monetization": ["revenue", "monetization", "business model", "how we make money", "pricing"],
    "technical_approach": ["technical", "implementation", "technology", "how it works", "architecture"],
    "inspiration": ["similar", "competitors", "inspiration", "alternatives", "market examples"]
}
```

**Rationale**:
- Decision tables align with constitution requirements
- Similarity scoring handles variations
- Deterministic and testable

**Alternatives Considered**:
- Hardcoded exact matches (rejected: too inflexible)
- Full NLP similarity (rejected: overkill, non-deterministic)
- LLM classification (rejected: expensive for simple mappings)

### 3. LLM Fallback Strategy

**Decision**: Structured extraction with PydanticAI when confidence < 0.8
```python
# Confidence scoring based on:
# - Section header matches (0.4 weight)
# - Content structure (0.3 weight)
# - Required field presence (0.3 weight)

if confidence < 0.8 and config.model.enabled:
    result = await agent.extract_flexible(
        markdown_content,
        output_model=RawIdea
    )
```

**Rationale**:
- Constitution requires model disabled by default
- Confidence threshold prevents unnecessary LLM calls
- PydanticAI ensures structured output

**Alternatives Considered**:
- Always use LLM (rejected: violates constitution)
- Never use LLM (rejected: can't handle edge cases)
- Multiple LLM passes (rejected: too expensive)

### 4. Fuzzy Matching Implementation

**Decision**: Levenshtein distance with threshold
```python
def fuzzy_match_section(header: str, targets: list[str], threshold: float = 0.8) -> str | None:
    """Match section header to known patterns using similarity scoring"""
    header_lower = header.lower().strip()
    for target in targets:
        similarity = 1 - (levenshtein_distance(header_lower, target) / max(len(header_lower), len(target)))
        if similarity >= threshold:
            return target
    return None
```

**Rationale**:
- Simple, well-understood algorithm
- Configurable threshold for precision/recall trade-off
- Fast enough for real-time parsing

**Alternatives Considered**:
- Exact substring matching (rejected: misses valid variations)
- Advanced NLP similarity (rejected: overkill for headers)
- Phonetic matching (rejected: not applicable to technical terms)

### 5. Error Handling Strategy

**Decision**: Detailed validation with actionable messages
```python
class ExtractionError(BaseModel):
    field: str
    issue: str
    suggestion: str
    severity: Literal["error", "warning"]

# Example errors:
errors = [
    ExtractionError(
        field="problem",
        issue="No problem statement found",
        suggestion="Add a section titled 'Problem' or 'Challenge' describing the issue your idea solves",
        severity="error"
    )
]
```

**Rationale**:
- Actionable errors help users fix issues
- Severity levels allow graceful degradation
- Structured errors enable programmatic handling

**Alternatives Considered**:
- Simple string errors (rejected: not actionable)
- Exception-based (rejected: doesn't allow partial success)
- Silent failures (rejected: poor user experience)

### 6. Performance Optimizations

**Decision**: Caching and early termination
```python
# Cache compiled regexes
SECTION_PATTERN = re.compile(r"^#{1,3}\s+(.+)$", re.MULTILINE)

# Early termination for required fields
if found_required_fields():
    return early_success()
```

**Rationale**:
- Regex compilation is expensive
- Most documents have required fields early
- Meets <200ms parsing goal

**Alternatives Considered**:
- No optimization (rejected: too slow for large docs)
- Parallel processing (rejected: overkill for single doc)
- Memory mapping (rejected: unnecessary complexity)

## Implementation Recommendations

1. **Phase Implementation**:
   - First: Rule-based extraction with fuzzy matching
   - Second: Confidence scoring system
   - Third: LLM fallback for low-confidence cases

2. **Testing Strategy**:
   - Golden tests for each section mapping variation
   - Property tests for fuzzy matching thresholds
   - Performance tests for 2000-line documents

3. **Configuration**:
   ```python
   class FlexibleExtractionConfig(BaseModel):
       fuzzy_threshold: float = 0.8
       confidence_threshold: float = 0.8
       max_section_depth: int = 3
       section_mappings: dict[str, list[str]] = Field(default_factory=get_default_mappings)
   ```

4. **Observability**:
   - Log extraction strategy used (rule/fuzzy/llm)
   - Track confidence scores
   - Monitor section mapping hits/misses

## Conclusion

The flexible extraction approach balances robustness with performance, following constitutional requirements for deterministic rules before LLM fallback. The multi-strategy approach ensures both common and edge cases are handled efficiently.
