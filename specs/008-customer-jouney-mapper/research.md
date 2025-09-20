# Research: Customer Journey Mapper Generator

**Date**: 2025-09-20
**Phase**: 0 (Research & Analysis)

## Research Objectives

Address clarifications from feature specification and establish technical foundation for customer journey map generation following constitutional requirements.

## Input Format Standardization

### Decision: Multi-format Input with LLM Normalization
**Research Question**: What input format for niche market specification?

**Findings**:
- **Markdown**: Most user-friendly for business analysts, allows natural language descriptions
- **JSON**: Structured but complex for non-technical users
- **Text**: Simple but lacks structure

**Decision**: Support all three formats with normalization pipeline:
1. Accept input as markdown/JSON/text via `--input-format` flag
2. Use LLM call to normalize to standardized JSON schema
3. Apply decision tables to structured data

**Rationale**:
- Maximizes usability (markdown for humans)
- Maintains constitutional compliance (structured processing)
- Enables deterministic business logic after normalization

**Alternatives Considered**:
- JSON-only: Rejected due to poor UX for business users
- Markdown-only: Rejected due to lack of validation structure
- Form-based input: Rejected as out of scope for CLI tool

## Persona Generation Strategy

### Decision: LLM-Inferred Personas with Decision Table Validation
**Research Question**: Should personas be generated or user-provided?

**Findings**:
- User-provided: Requires extensive input, may be incomplete
- Fully generated: Risk of generic/unrealistic personas
- Hybrid approach: Best of both worlds

**Decision**:
1. Extract persona hints from niche market description via LLM
2. Apply decision tables for persona demographics based on market type
3. Generate realistic details using industry-specific templates
4. Allow persona overrides via `--persona-file` flag

**Rationale**:
- Constitutional compliance: Decision tables for business logic
- User experience: Minimal input required
- Quality: Industry-validated persona patterns

**Alternatives Considered**:
- Manual persona input: Rejected due to complexity
- Pure template-based: Rejected due to lack of customization

## Journey Detail Automation Level

### Decision: Complete Automation with Pareto Principle
**Research Question**: What level of journey detail automation is expected?

**Findings**:
- Full automation needed for usability
- 80/20 rule: Focus on most common journey patterns
- KISS principle: Avoid over-engineering edge cases

**Decision**: Generate complete journey maps using:
1. Industry-standard journey stages (Awareness → Advocacy)
2. Decision tables for touchpoint selection by market type
3. Emotion/pain point templates based on stage + persona
4. Metrics templates with industry benchmarks

**Rationale**:
- Pareto principle: Cover 80% of use cases comprehensively
- KISS: Simple, predictable patterns
- Constitutional: Deterministic business logic

**Alternatives Considered**:
- Partial automation: Rejected due to poor UX
- Highly customizable: Rejected due to complexity

## Technical Architecture Decisions

### Decision Table Design
**Research**: Best practices for decision table implementation in Python

**Findings**:
- JSON format for rule storage
- First-match-wins semantics for performance
- Score-based matching for nuanced decisions

**Decision**: Implement decision tables for:
- Niche market classification (B2B/B2C/industry type)
- Journey stage templates by market type
- Touchpoint selection by industry/persona
- Emotion patterns by stage/touchpoint combination

### LLM Integration Pattern
**Research**: Constitutional LLM usage patterns

**Findings**:
- STRICT mode by default (llm.enabled=false)
- Use only for input normalization and content generation
- Provider-agnostic adapter pattern
- Fail-fast with deterministic fallbacks

**Decision**: Two LLM calls maximum:
1. Input normalization (markdown/text → structured JSON)
2. Content enrichment (persona details, touchpoint descriptions)

### Schema Validation Strategy
**Research**: customer_journey.json.schema compliance

**Findings**:
- Complex nested structure with 300+ lines
- Required fields: journeyId, persona, stages, metadata
- Enum values for channels, emotions, stage names

**Decision**:
- Pydantic v2 models generated from JSON schema
- Validation at output generation time
- Template-based field population for required fields

## Performance Optimization

### Decision: Template-Based Generation with Caching
**Research**: Meeting <5s runtime requirement

**Findings**:
- Decision table lookups: <100ms
- LLM calls: 1-3s each (major bottleneck)
- JSON schema validation: <50ms

**Decision**:
- Pre-built journey templates for common market types
- Cache normalized inputs for repeat processing
- Minimize LLM calls through smart templating
- Fail-fast validation before expensive operations

## Export and Modification Capabilities

### Decision: File-Based Export with Validation
**Research Question**: Users need export, save, modify capabilities

**Findings**:
- JSON export: Required for schema compliance
- Human-readable formats: Useful for review
- Modification workflow: Edit-validate-regenerate

**Decision**:
- Primary output: JSON conforming to schema
- Optional outputs: Markdown summary, CSV touchpoint export
- Validation tool: Separate `--validate` flag for modified files
- Re-import capability: `--input-file` for pre-structured JSON

## Industry-Specific Patterns

### Research: Common Journey Patterns by Market Type

**B2C E-commerce**:
- Stages: Awareness → Consideration → Purchase → Retention
- Key touchpoints: Social media, website, email, mobile app
- Typical duration: Days to weeks
- Pain points: Choice paralysis, trust, payment security

**B2B SaaS**:
- Stages: Awareness → Evaluation → Trial → Purchase → Onboarding → Expansion
- Key touchpoints: Content marketing, demos, trials, sales calls
- Typical duration: Weeks to months
- Pain points: Complex evaluation, stakeholder alignment, integration

**Service-Based**:
- Stages: Awareness → Consultation → Decision → Service → Follow-up
- Key touchpoints: Website, phone, in-person, email
- Typical duration: Hours to weeks
- Pain points: Trust building, scheduling, communication

**Decision**: Implement pattern templates for major market categories with decision table routing.

## Final Architecture

### Component Structure
```
customer_journey_mapper.py
├── CONFIG (lines 20-120)
├── Decision Tables (inline JSON)
├── LLM Adapter (provider abstraction)
├── Input Normalization (markdown/text → JSON)
├── Journey Generation (templates + decision logic)
├── Schema Validation (Pydantic models)
├── Output Generation (JSON + optional formats)
└── CLI Interface (argparse)
```

### Data Flow
```
Input (markdown/JSON/text)
→ Normalization (LLM if needed)
→ Market Classification (decision tables)
→ Template Selection (decision tables)
→ Content Generation (templates + LLM enrichment)
→ Validation (Pydantic models)
→ Output (JSON + optional formats)
```

## Research Completion

✅ All NEEDS CLARIFICATION items from specification resolved
✅ Technical approach validated against constitutional requirements
✅ Performance requirements achievable with proposed architecture
✅ Implementation complexity appropriate for single-file design

**Ready for Phase 1**: Design & Contracts