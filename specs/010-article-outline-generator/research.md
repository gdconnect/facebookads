# Research: Article Outline Generator

**Feature**: Article Outline Generator
**Date**: 2025-09-21
**Phase**: Phase 0 (Research)

## Markdown Parser Patterns

### Decision: Use regex patterns with fallback structure recognition
**Rationale**: Lightweight parsing without external dependencies, suitable for outline generation context
**Alternatives considered**:
- markdown-it-py: Full-featured but adds dependency
- commonmark: Adds dependency, over-engineered for our use case
- mistune: Fast but still external dependency

**Implementation approach**:
- Header detection: `^#{1,6}\s+(.+)$`
- List item detection: `^[\s]*[-*+]\s+(.+)$`
- Paragraph segmentation for content analysis
- Fallback to sentence-based section splitting

## Content Type Classification

### Decision: Rule-based classification with keyword analysis
**Rationale**: Deterministic, fast, constitutional compliance (rules before LLM)
**Alternatives considered**:
- ML-based classification: Too complex, requires training data
- Pure LLM classification: Violates constitutional rule-first principle

**Classification rules**:
- Story indicators: narrative keywords (character, plot, setting, conflict, resolution)
- Article indicators: informational keywords (how-to, guide, analysis, review, tips)
- Structure patterns: chronological vs. topical organization
- Verb tense analysis: past tense narrative vs. present/imperative instructional

## Language Detection

### Decision: Simple heuristics with common language patterns
**Rationale**: Lightweight, covers common use cases, no external dependencies
**Alternatives considered**:
- langdetect library: Adds dependency, overkill for outline generation
- polyglot: Complex dependency chain
- Google Translate API: External service dependency

**Detection approach**:
- Common stopwords frequency analysis
- Character set detection (ASCII, accented characters, non-Latin scripts)
- Language-specific patterns (articles, conjunctions)
- Default to 'en' for ambiguous cases

## Outline Structure Templates

### Decision: Template-based generation with content type variations
**Rationale**: Predictable structure, easy to maintain, supports both articles and stories
**Alternatives considered**:
- Dynamic structure generation: Too complex, unpredictable outputs
- Fixed single template: Inflexible for different content types

**Template patterns**:
- Article template: Introduction → Main sections → Conclusion
- Story template: Setup → Rising action → Climax → Resolution
- How-to template: Overview → Steps → Tips → Summary
- Analysis template: Background → Analysis → Implications → Conclusion

## Word Count Estimation

### Decision: Section-based estimation with content complexity factors
**Rationale**: Provides useful guidance for writers, simple algorithm
**Alternatives considered**:
- Fixed word counts: Too rigid, doesn't account for content complexity
- ML-based estimation: Over-engineered for the use case

**Estimation factors**:
- Base word count by section type (intro: 150-300, main: 300-800, conclusion: 100-200)
- Complexity multipliers based on key points count
- Content type adjustments (stories typically longer sections)
- Depth level adjustments (deeper sections are typically shorter)

## Section ID Generation

### Decision: Slug-based IDs with collision detection
**Rationale**: Human-readable, stable references, suitable for content management
**Alternatives considered**:
- UUID: Not human-readable, unnecessary complexity
- Sequential numbers: Not semantic, fragile to reordering

**Generation approach**:
- Title-to-slug conversion (lowercase, spaces to hyphens, special char removal)
- Collision detection with numeric suffixes
- Reserved keywords handling (introduction, conclusion, etc.)
- Maximum length limiting for practical use

## PydanticAI Integration

### Decision: Fallback-only model usage for ambiguous content
**Rationale**: Constitutional compliance, cost control, performance
**Alternatives considered**:
- Primary LLM-based processing: Violates constitutional rules-first principle
- No LLM integration: Misses opportunity for quality enhancement

**Integration strategy**:
- Rules handle 90%+ of cases deterministically
- LLM fallback for ambiguous content type classification
- LLM enhancement for section summary generation when content is sparse
- Strict budget enforcement (<2 calls, <2000 tokens)
- PydanticAI typed responses ensure schema compliance

## Performance Optimization

### Decision: Lazy processing with early returns
**Rationale**: Meet <5s performance target, efficient resource usage
**Alternatives considered**:
- Full text analysis: Too slow for simple cases
- Caching: Adds complexity, not needed for single-use tool

**Optimization strategies**:
- Process headers first, content analysis only if needed
- Early classification decisions based on clear indicators
- Minimal regex compilation overhead
- Streaming JSON output for large outlines
- Memory-efficient text processing (no full document loading)
