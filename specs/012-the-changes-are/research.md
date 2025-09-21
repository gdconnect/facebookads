# Research: Enhanced Article Outline Generator with Interim Classification

**Feature**: 012-the-changes-are
**Date**: 2025-09-21
**Research Scope**: PydanticAI integration patterns for existing single-file agent enhancement

## Research Findings

### Decision: PydanticAI Integration Pattern
**Chosen**: Enhance existing agent with PydanticAI fallback integration using provider abstraction and typed responses

**Rationale**:
- Constitutional compliance: Article XI requires all LLM calls through PydanticAI
- Backward compatibility: Agent works identically when `model.enabled = false` (STRICT mode)
- Minimal code changes: Integration requires only 5 strategic enhancements to existing code
- Provider flexibility: Configuration-based provider switching (OpenAI, Anthropic, Gemini, local)
- Cost tracking: Built-in observability with token counting and USD cost calculation

**Alternatives considered**:
- Custom LLM integration: Rejected - violates constitutional Article XI requirement
- Separate classification service: Rejected - user explicitly requested enhancement to existing agent
- External API calls: Rejected - constitutional preference for single-file agents

### Decision: Enhanced Classification Confidence Strategy
**Chosen**: Dual-threshold approach with interim classification support

**Technical Approach**:
- Rule-based classification first with existing `CONTENT_TYPE_RULES`
- LLM fallback when `confidence < 0.8` (configurable threshold)
- Maximum 2 LLM calls per request (constitutional budget compliance)
- Interim classification available during processing workflow
- Graceful degradation when LLM unavailable

**Rationale**:
- Maintains existing deterministic behavior for high-confidence cases
- Provides enhanced accuracy for ambiguous content (user requirement)
- Supports interim classification for real-time processing workflows
- Preserves performance budgets (<5s runtime, <2000 tokens)

**Alternatives considered**:
- LLM-first approach: Rejected - violates constitutional Article III (decision tables first)
- Single threshold: Rejected - doesn't support interim classification use case
- External classification service: Rejected - increases complexity and latency

### Decision: Backward Compatibility Strategy
**Chosen**: Zero-breaking-change enhancement with feature flags

**Implementation**:
- Default `model.enabled = false` preserves existing behavior
- All new features behind configuration flags
- Existing Agent Envelope schema unchanged
- CLI interface unchanged (run, selfcheck, print-schemas, dry-run)
- Enhanced fields added to output metadata only when LLM used

**Rationale**:
- User requirement: "existing outline generation capabilities continue to work without regression"
- Constitutional requirement: maintain single-file agent patterns
- Operational safety: production systems can upgrade without behavior changes

**Alternatives considered**:
- New agent version: Rejected - user explicitly wants enhancement to existing agent
- Breaking schema changes: Rejected - violates backward compatibility requirement
- Separate endpoints: Rejected - adds complexity to single-file pattern

### Decision: Cost Tracking and Observability Implementation
**Chosen**: Constitutional Article XVIII structured logging with token/cost tracking

**Technical Implementation**:
- JSONL logging to STDERR with required event types
- Token counting approximation for immediate cost estimates
- Provider-specific cost calculation (OpenAI, Anthropic, Gemini rates)
- Envelope metadata cost tracking (`tokens_in`, `tokens_out`, `usd`)
- Model call events with duration, success, retry status

**Rationale**:
- Constitutional requirement: Article XVIII structured logging spec
- Business requirement: cost control and budget enforcement
- Operational requirement: observability for production monitoring
- Debug requirement: detailed event tracing for troubleshooting

**Alternatives considered**:
- Simple text logging: Rejected - violates constitutional structured logging requirement
- No cost tracking: Rejected - violates constitutional budget enforcement requirement
- External logging service: Rejected - adds dependencies to single-file pattern

### Decision: Provider Abstraction Strategy
**Chosen**: Configuration-based provider switching with environment variable precedence

**Configuration Hierarchy** (Constitutional Article V):
1. Sensible defaults (OpenAI GPT-4, disabled by default)
2. Configuration file settings
3. Environment variables (`AGENT_MODEL_*`)
4. CLI flags (`--config`, `--strict`)

**Provider Support**:
- OpenAI: Standard API integration
- Anthropic: Claude models via API
- Gemini: Google AI Studio/Vertex AI
- Azure: Azure OpenAI Service
- Local: Self-hosted/local model endpoints

**Rationale**:
- Constitutional requirement: provider abstraction via PydanticAI
- Operational flexibility: easy provider switching without code changes
- Security compliance: API keys from environment variables only
- Testing support: local/mock providers for CI/CD

**Alternatives considered**:
- Hardcoded provider: Rejected - violates constitutional abstraction requirement
- Runtime provider discovery: Rejected - adds complexity and failure modes
- Multiple provider support per request: Rejected - exceeds scope and budget

### Decision: Enhanced Model Validation Strategy
**Chosen**: Pydantic v2 typed responses with constitutional retry logic

**Validation Pipeline**:
1. PydanticAI agent creation with `result_type=LLMClassificationResult`
2. Automatic JSON parsing and Pydantic validation
3. Business logic validation (confidence bounds, required fields)
4. Single retry with enhanced prompt on validation failure
5. Deterministic fallback to rule-based classification on persistent failure

**Rationale**:
- Constitutional requirement: typed model responses via Pydantic v2
- Reliability requirement: handle LLM response variability gracefully
- Budget requirement: maximum 1 retry per constitutional Article X
- User experience: never fail due to LLM issues when rules available

**Alternatives considered**:
- Untyped JSON parsing: Rejected - violates constitutional type safety requirement
- Multiple retry attempts: Rejected - violates constitutional budget and retry limits
- Fail-fast on LLM errors: Rejected - doesn't support graceful degradation requirement

## Implementation Strategy

### Code Integration Points

1. **Enhanced Configuration** (Lines 79-93):
   - Extend existing `ModelConfig` dataclass with PydanticAI fields
   - Add confidence threshold, retry limits, fallback options

2. **PydanticAI Agent Creation** (New function):
   - Create typed agent with `LLMClassificationResult` response model
   - Provider-agnostic configuration mapping

3. **Enhanced LLM Fallback** (Lines 479-494):
   - Replace existing stub with full PydanticAI implementation
   - Integrate cost tracking and structured logging

4. **Envelope Cost Tracking** (Lines 600-608):
   - Add LLM cost metadata to Agent Envelope
   - Track tokens and USD cost per request

5. **Configuration Loading** (Lines 200-250):
   - Environment variable precedence for model settings
   - Provider validation and API key checks

### Performance Budget Compliance

- **Runtime**: <5s maintained (LLM calls have 30s timeout, typically <2s response)
- **Token Budget**: <2000 tokens enforced via PydanticAI configuration
- **LLM Calls**: <2 calls maximum (1 primary + 1 retry if needed)
- **Memory**: <100MB working set maintained (no large model loading)

### Risk Mitigation

- **API Key Security**: Environment variables only, no hardcoded secrets
- **Network Failures**: Graceful fallback to rule-based classification
- **Cost Control**: Per-request budget enforcement and tracking
- **Response Validation**: Multiple validation layers with typed responses
- **Backward Compatibility**: Feature flags and default disabled mode

## Constitutional Compliance Verification

✅ **Article I** - Single-File Agent: Enhancement maintains single-file pattern
✅ **Article II** - Contract-First: Extends existing Pydantic v2 models
✅ **Article III** - Decision Tables First: Rules before LLM fallback
✅ **Article X** - STRICT Default**: LLM disabled by default, fallback only
✅ **Article XI** - PydanticAI Integration: All LLM calls via PydanticAI
✅ **Article XII** - Performance Budgets: Maintains declared budget limits
✅ **Article XVIII** - Structured Logging: JSONL events for model calls
✅ **Article XX** - CLI Requirements: Preserves existing command interface

---
*Research complete. Ready for Phase 1: Design & Contracts*
