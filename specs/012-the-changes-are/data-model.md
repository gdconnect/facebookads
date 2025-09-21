# Data Model: Enhanced Article Outline Generator with Interim Classification

**Feature**: 012-the-changes-are
**Date**: 2025-09-21
**Purpose**: Define enhanced data entities for interim classification capabilities

## Enhanced Data Entities

### 1. Enhanced InputModel (Extension)
**Purpose**: Extend existing input model with interim classification options

**New Fields**:
```python
class InputModel(BaseModel):
    """Enhanced input model with interim classification support."""
    # Existing fields preserved
    content: str = Field(..., min_length=1, description="Markdown content description")
    target_depth: int = Field(default=3, ge=1, le=6, description="Desired outline depth (1-6)")
    content_type_hint: Literal["article", "story"] | None = Field(
        default=None, description="Optional content type hint"
    )
    language_hint: str | None = Field(
        default=None, pattern=r"^[a-z]{2}$", description="Optional ISO 639-1 language code"
    )
    include_word_counts: bool = Field(
        default=True, description="Whether to generate word count estimates"
    )

    # New fields for interim classification
    interim: bool = Field(
        default=False, description="Request interim classification during processing"
    )
    timeout_ms: int | None = Field(
        default=None, ge=100, le=30000, description="Timeout for interim responses (100-30000ms)"
    )
    classification_method: Literal["auto", "rules_only", "llm_preferred"] = Field(
        default="auto", description="Classification method preference"
    )
```

**Validation Rules**:
- Content cannot be empty or whitespace-only (existing)
- Timeout must be reasonable for interim requests (100ms-30s)
- Classification method affects LLM fallback behavior

### 2. Enhanced OutlineMetadata (Extension)
**Purpose**: Extend existing metadata with classification information

**New Fields**:
```python
class OutlineMetadata(BaseModel):
    """Enhanced metadata with classification details."""
    # Existing fields preserved
    content_type: Literal["article", "story"]
    detected_language: str = Field(..., pattern=r"^[a-z]{2}$")
    depth: int = Field(..., ge=1, le=6)
    sections_count: int = Field(..., ge=0)
    generated_at: datetime
    notes: str | None = None

    # New classification fields
    classification_confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    classification_method: Literal["rule_based", "llm_single", "llm_double"] = Field(
        ..., description="Method used for classification"
    )
    classification_reasoning: str = Field(..., min_length=1, description="Why this classification was chosen")
    key_indicators: list[str] = Field(default_factory=list, description="Key content indicators found")
    llm_calls_used: int = Field(default=0, ge=0, le=2, description="Number of LLM calls made")
    processing_time_ms: int = Field(..., ge=0, description="Total processing time in milliseconds")
    interim_available: bool = Field(default=False, description="Whether interim classification was requested")
```

**Business Rules**:
- Confidence must be between 0.0 and 1.0
- LLM calls cannot exceed 2 per constitutional requirement
- Processing time tracked for performance monitoring

### 3. New LLMClassificationResult (Internal Entity)
**Purpose**: Typed responses from PydanticAI for classification enhancement

```python
class LLMClassificationResult(BaseModel):
    """Typed LLM response for content classification."""
    content_type: Literal["article", "story"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=1)
    key_indicators: list[str] = Field(default_factory=list)
    processing_notes: str | None = Field(default=None, description="Additional processing insights")
```

**Validation Rules**:
- Content type must be one of the supported types
- Confidence must be valid probability (0.0-1.0)
- Reasoning must be provided for transparency
- Key indicators help explain classification decisions

### 4. New ClassificationPrompt (Internal Entity)
**Purpose**: Structured input for LLM classification requests

```python
class ClassificationPrompt(BaseModel):
    """Input structure for LLM classification requests."""
    content: str = Field(..., min_length=1, max_length=2000)
    existing_confidence: float = Field(..., ge=0.0, le=1.0)
    rule_classification: str
    rule_reasoning: str
    context_hints: dict[str, Any] = Field(default_factory=dict)
```

**Business Rules**:
- Content truncated to 2000 chars for token budget compliance
- Include rule-based results for LLM context
- Context hints can include language, depth preferences

### 5. Enhanced EnvelopeMeta (Extension)
**Purpose**: Extend existing envelope metadata with LLM cost tracking

**Enhanced Fields**:
```python
class EnvelopeMeta(BaseModel):
    """Enhanced agent execution metadata."""
    # Existing fields preserved
    agent: Literal["article_outline_generator"]
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    trace_id: str
    ts: datetime
    brand_token: str
    hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")

    # Enhanced cost tracking
    cost: dict[str, int | float] = Field(
        ..., description="Enhanced: tokens_in, tokens_out, usd, llm_calls"
    )
    prompt_id: str | None = None
    prompt_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$|^$")

    # New classification metadata
    classification_enhanced: bool = Field(default=False, description="Whether LLM enhancement was used")
    fallback_used: bool = Field(default=False, description="Whether fallback to rules was needed")
```

**State Transitions**:
- classification_enhanced = True when LLM called successfully
- fallback_used = True when LLM fails and rules used instead

## Entity Relationships

### Core Processing Flow
```
InputModel → Content Classification → Enhanced Metadata → OutputModel
                       ↓
           Decision Tables → LLM Fallback (if confidence < threshold)
                       ↓
              LLMClassificationResult → Classification Enhancement
```

### Data Dependencies
1. **InputModel** → validates user input and preferences
2. **ClassificationPrompt** → structures LLM requests with context
3. **LLMClassificationResult** → provides typed LLM responses
4. **Enhanced OutlineMetadata** → aggregates classification results
5. **Enhanced EnvelopeMeta** → tracks costs and processing metadata

### State Management
- **Rule-based path**: Content → Rules → Metadata (no LLM cost)
- **Enhanced path**: Content → Rules → LLM → Enhanced Results → Metadata
- **Fallback path**: Content → Rules → LLM Error → Rules → Metadata

## Validation Constraints

### Input Validation
- Content length: 1 char minimum, practical maximum ~50KB
- Timeout bounds: 100ms to 30s for interim requests
- Classification method: must be supported enum value

### Processing Validation
- Confidence scores: 0.0 to 1.0 range strictly enforced
- LLM call limits: Maximum 2 calls per constitutional requirement
- Token budgets: Maximum 2000 tokens per call
- Response timeouts: 30s maximum per LLM call

### Output Validation
- Required metadata fields: All new fields must be populated
- Classification reasoning: Must be meaningful and actionable
- Cost tracking: Must be accurate for monitoring and billing

## Schema Evolution Strategy

### Backward Compatibility
- All existing fields preserved with identical validation
- New fields are optional or have sensible defaults
- Agent Envelope structure unchanged for external consumers
- CLI interface remains compatible

### Forward Compatibility
- Extension points for additional classification types
- Flexible context hints for future LLM enhancements
- Versioned schemas for contract validation
- Graceful handling of unknown fields in metadata

## Performance Characteristics

### Rule-based Classification
- Target: <200ms for 95th percentile
- Memory: <10MB additional working set
- CPU: Minimal regex processing overhead

### LLM-enhanced Classification
- Target: <5s total including LLM calls
- Network: Up to 2 API calls with 30s timeout each
- Memory: <50MB for prompt processing and response validation
- Cost: Tracked per token with provider-specific rates

---
*Entity design complete. Ready for contract generation.*
