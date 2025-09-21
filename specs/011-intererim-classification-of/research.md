# Research: Interim Content Classification with LLM Fallback

**Feature**: 011-intererim-classification-of
**Date**: 2025-09-21
**Status**: Complete

## Research Questions

### Q1: Article vs Essay Classification Patterns
**Decision**: Implement dual decision table approach with linguistic and structural indicators
**Rationale**:
- Articles: Informational, instructional, factual content (how-to, news, tutorials, analysis)
- Essays: Personal, argumentative, reflective content (opinion, memoir, persuasive, narrative)
- Linguistic indicators: Tense patterns, pronoun usage, discourse markers
- Structural indicators: Section patterns, organizational flow, content purpose

**Alternatives considered**:
- Single binary classifier → Rejected: Too simplistic for nuanced content types
- Multi-class classification → Rejected: Scope limited to article/essay distinction

### Q2: LLM Fallback Integration Strategy
**Decision**: PydanticAI integration with typed classification responses and confidence thresholds
**Rationale**:
- Constitutional requirement for PydanticAI usage
- Typed model responses ensure structured classification output
- Confidence threshold (0.7) triggers LLM fallback automatically
- Two-stage LLM approach: initial classification + validation/refinement

**Alternatives considered**:
- Direct OpenAI API calls → Rejected: Violates constitutional PydanticAI requirement
- Always use LLM → Rejected: Performance and cost constraints, constitutional STRICT mode default

### Q3: Performance Budget Allocation
**Decision**:
- Rule-based classification: <200ms target
- LLM call 1 (initial): <2s timeout, <1000 tokens
- LLM call 2 (refinement): <1.5s timeout, <800 tokens
- Total budget: <5s runtime, <2000 tokens, <$0.01 per request

**Rationale**: Supports interim classification in real-time workflows while staying within constitutional budget requirements

**Alternatives considered**:
- Single long LLM call → Rejected: Risk of timeout in interim workflows
- No performance budgets → Rejected: Constitutional requirement for declared budgets

### Q4: Confidence Threshold Determination
**Decision**: 0.7 confidence threshold for LLM fallback trigger
**Rationale**:
- Balances accuracy vs performance
- Allows rule-based classification for clear cases (>0.7)
- Triggers LLM for ambiguous content (<0.7)
- Aligns with constitutional low-confidence fallback pattern

**Alternatives considered**:
- Fixed 0.5 threshold → Rejected: Too many false positives
- Dynamic threshold → Rejected: Added complexity without clear benefit

### Q5: Batch Processing Strategy
**Decision**: Sequential processing with per-item budgets and early termination
**Rationale**:
- Maintains per-item performance guarantees
- Supports graceful degradation on timeout
- Enables interim results for partial batches

**Alternatives considered**:
- Parallel LLM calls → Rejected: Cost and rate limit concerns
- All-or-nothing batch → Rejected: Poor UX for interim classification

## Technical Architecture Decisions

### Decision Table Design
**Structure**:
```python
ARTICLE_INDICATORS = [
    (r'\b(how to|guide|tutorial|step|instruction)\b', 0.9, "Instructional content"),
    (r'\b(analysis|review|study|research|findings)\b', 0.8, "Analytical content"),
    (r'\b(news|breaking|announcement|report)\b', 0.8, "News content"),
]

ESSAY_INDICATORS = [
    (r'\b(I believe|in my opinion|personally|my experience)\b', 0.9, "Personal opinion"),
    (r'\b(memoir|autobiography|growing up|childhood)\b', 0.8, "Personal narrative"),
    (r'\b(should|must|ought to|argue that|persuade)\b', 0.7, "Argumentative content"),
]
```

### PydanticAI Integration Pattern
**Models**:
- `ClassificationRequest`: Input validation
- `ClassificationResult`: Typed response with content_type, confidence, reasoning
- `BatchClassificationRequest`: Multiple content pieces
- LLM prompts with JSON-only constraints

### Error Handling Strategy
**Graceful Degradation**:
1. LLM timeout → Return rule-based result with lower confidence
2. LLM service unavailable → Rule-based fallback with warning
3. Invalid input → Structured error response
4. Batch partial failure → Return successful items with error details

## Implementation Approach

### Agent Structure
Following constitutional single-file pattern:
- `agents/content_classifier/content_classifier.py` (main implementation)
- `agents/content_classifier/schemas/` (generated JSON schemas)
- `agents/content_classifier/tests/` (contract, integration, golden tests)
- `agents/content_classifier/README.md` (usage documentation)

### Configuration Hierarchy
1. Defaults: STRICT mode (LLM disabled), 0.7 confidence threshold
2. Config file: Override thresholds and LLM settings
3. Environment variables: API keys and runtime settings
4. CLI flags: Per-execution overrides

### Testing Strategy
- Contract tests: Schema validation and envelope compliance
- Integration tests: End-to-end classification scenarios
- Golden tests: Real-world content samples with expected classifications
- Performance tests: Budget compliance validation

## Dependencies Analysis

### Core Dependencies (Justified)
- **pydantic>=2.0**: Constitutional requirement for typed models
- **pydantic-ai**: Constitutional requirement for LLM integration
- **Standard library**: argparse, json, re, typing, datetime, logging

### Optional Dependencies
- **pytest**: Testing framework (development only)
- **httpx**: HTTP client for PydanticAI (runtime dependency)

## Risk Assessment

### High Risk
- LLM service reliability → Mitigation: Robust fallback to rule-based classification
- Performance budget compliance → Mitigation: Aggressive timeouts and circuit breakers

### Medium Risk
- Classification accuracy for edge cases → Mitigation: Comprehensive test coverage
- Configuration complexity → Mitigation: Sensible defaults with minimal required config

### Low Risk
- Single-file maintenance → Mitigation: Clear code organization with numbered flow

## Next Steps

Phase 1 Design tasks:
1. Define Pydantic models for all input/output types
2. Create classification decision tables with test coverage
3. Design PydanticAI integration pattern
4. Generate contract schemas and failing tests
5. Create quickstart validation scenarios
