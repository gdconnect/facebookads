# Implementation Plan: Flexible Business Idea Generator

**Branch**: `016-flexible-business-idea` | **Date**: 2025-09-24 | **Spec**: [/specs/016-flexible-business-idea/spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-flexible-business-idea/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Enhance the Business Idea Evaluator (BIE) agent to intelligently extract business components from markdown documents with varied structures and section names, using LLM-based content understanding when strict pattern matching fails. This allows users to submit business ideas in natural formats without conforming to rigid templates.

## Technical Context
**Language/Version**: Python 3.10+
**Primary Dependencies**: pydantic>=2.0.0, pydantic-ai>=0.0.1
**Storage**: File-based (markdown input, JSON/markdown output)
**Testing**: pytest, hypothesis for property tests
**Target Platform**: Linux/macOS/Windows CLI
**Project Type**: single (Python single-file agent per constitution)
**Performance Goals**: <2 minutes end-to-end evaluation, <10K tokens per evaluation
**Constraints**: <200ms parsing time, <50MB memory, must handle 2000-line documents
**Scale/Scope**: Single-file agent enhancement, ~1000 LOC

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the Python Single-File Constitution (v1.4.0):

- [x] **Single-file implementation**: Enhancement to existing `agents/bie/bie.py` - PASS
- [x] **Schema-first design**: Uses Pydantic models (RawIdea, BusinessModel, etc.) - PASS
- [x] **Contract-first approach**: JSON schemas generated from Pydantic models - PASS
- [x] **Decision tables before LLM**: Can implement mapping rules as decision table - PASS
- [x] **PydanticAI integration**: Already uses pydantic-ai for LLM calls - PASS
- [x] **Model disabled by default**: Currently has model.enabled config - PASS
- [x] **Structured logging**: Uses JSONL on STDERR - PASS
- [x] **Hierarchical config**: Config → env → CLI pattern present - PASS
- [x] **Testing requirements**: Has tests/ folder structure - PASS
- [x] **Defensive programming**: Type hints and validation present - PASS

No violations detected. Constitution alignment confirmed.

## Project Structure

### Documentation (this feature)
```
specs/016-flexible-business-idea/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Single-file agent structure (per constitution)
agents/bie/
├── bie.py               # Enhanced single-file agent
├── schemas/             # Generated JSON schemas
│   ├── input.json
│   ├── output.json
│   └── envelope.json
├── tests/
│   ├── contract/
│   ├── integration/
│   └── golden/
├── examples/
├── docs/
└── README.md
```

**Structure Decision**: Single-file agent per constitution requirements

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Best practices for flexible markdown parsing
   - LLM prompt patterns for content extraction
   - Section name mapping strategies
   - Fallback extraction patterns

2. **Generate and dispatch research agents**:
   ```
   Task: "Research flexible markdown parsing strategies for Python"
   Task: "Find best practices for LLM-based content extraction with PydanticAI"
   Task: "Research section name normalization patterns"
   Task: "Investigate fuzzy string matching for section headers"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Enhanced RawIdea model with flexible extraction
   - SectionMapping rules entity
   - ExtractionStrategy enumeration
   - ValidationResult with detailed errors

2. **Generate API contracts** from functional requirements:
   - Enhanced parse_markdown method signature
   - Flexible extraction pipeline contract
   - Section mapping configuration schema

3. **Generate contract tests** from contracts:
   - Test varied markdown structures
   - Test section name alternatives
   - Test missing required fields
   - Test field length enforcement

4. **Extract test scenarios** from user stories:
   - Alternative section names test
   - Nested structure test
   - Missing optional fields test
   - Content overflow test

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
   - Add flexible parsing approach to CLAUDE.md
   - Document new extraction strategies

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Enhance parse_markdown method with flexible extraction
- Add section mapping configuration
- Implement LLM fallback for ambiguous content
- Add comprehensive error reporting
- Create golden tests for various formats

**Ordering Strategy**:
- Tests first (TDD approach)
- Section mapping rules
- Enhanced parser implementation
- LLM fallback integration
- Error handling improvements

**Estimated Output**: 15-20 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No violations detected - section not needed*

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none)

**Artifacts Generated**:
- [x] plan.md (this file)
- [x] research.md (flexible parsing strategies)
- [x] data-model.md (enhanced entities and schemas)
- [x] contracts/enhanced-parser.json (API contract)
- [x] quickstart.md (comprehensive test scenarios)
- [x] CLAUDE.md updated (agent context)

---
*Based on Constitution v1.4.0 - See `.specify/memory/constitution.md`*
