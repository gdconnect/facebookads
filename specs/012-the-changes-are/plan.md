# Implementation Plan: Enhanced Article Outline Generator with Interim Classification

**Branch**: `012-the-changes-are` | **Date**: 2025-09-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/var/www/html/facebookads/specs/012-the-changes-are/spec.md`

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
Primary requirement: Enhance existing article_outline_generator.py with improved article vs essay classification capabilities. The system must provide interim classification results during outline generation workflow, support optional LLM-enhanced classification when rule-based confidence is low, and allow up to two LLM calls per request for improved accuracy. All existing outline generation functionality must remain backward compatible. Key technical approach: Extend existing decision tables and add PydanticAI integration for LLM fallback while maintaining constitutional compliance.

## Technical Context
**Language/Version**: Python 3.11+ (existing agent follows constitutional requirements)
**Primary Dependencies**: pydantic>=2.0, pydantic-ai (for LLM enhancement), standard library (existing)
**Storage**: N/A (stateless agent, existing pattern)
**Testing**: pytest with contract, integration, and golden test patterns (existing)
**Target Platform**: Linux server / CLI agent following single-file constitutional pattern (existing)
**Project Type**: single (enhancement to existing agents/article_outline_generator pattern)
**Performance Goals**: <5s total runtime, <2 LLM calls max, <2000 tokens per call (existing budgets maintained)
**Constraints**: <200ms p95 for rule-based classification, backward compatibility, graceful degradation when LLM unavailable
**Scale/Scope**: Enhancement to existing content classification within single-file agent boundaries

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Article I - Single-File Agent**: ✅ PASS - Will enhance existing `agents/article_outline_generator/article_outline_generator.py`
**Article II - Contract-First**: ✅ PASS - Will extend existing Pydantic v2 models with new classification fields
**Article III - Decision Tables First**: ✅ PASS - Will enhance existing CONTENT_TYPE_RULES with improved patterns
**Article X - STRICT Default**: ✅ PASS - LLM disabled by default, only activated on low confidence (existing pattern)
**Article XI - PydanticAI Integration**: ✅ PASS - All new LLM calls through PydanticAI with typed responses
**Article XII - Performance Budgets**: ✅ PASS - Maintain existing <5s runtime, <2 LLM calls, <2000 tokens
**Article XVIII - Structured Logging**: ✅ PASS - Extend existing JSONL logging with new classification events
**Article XX - CLI Requirements**: ✅ PASS - Existing run, selfcheck, print-schemas, dry-run subcommands preserved

**Initial Assessment**: PASS - No constitutional violations detected. Enhancement preserves existing constitutional compliance while adding new classification capabilities.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 1 (Single project) - Enhancement to existing single-file agent pattern

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Extend existing InputModel/OutputModel for enhanced classification [P]
- Enhance existing CONTENT_TYPE_RULES decision tables [P]
- Add PydanticAI integration for LLM fallback [P]
- Create interim classification methods [P]
- Update confidence scoring logic [P]
- Enhance existing CLI commands with new features
- Extend existing tests with new classification scenarios
- Update quickstart scenarios for enhanced functionality

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models before logic before CLI
- Mark [P] for parallel execution (independent enhancement tasks)
- Backward compatibility throughout

**Specific Task Categories**:
1. **Model Enhancement**: Extend existing Pydantic models with classification fields [P]
2. **Decision Table Enhancement**: Improve existing CONTENT_TYPE_RULES patterns [P]
3. **LLM Integration**: Add PydanticAI for enhanced classification fallback [P]
4. **Interim Classification**: Add methods for real-time classification results
5. **Confidence Scoring**: Enhance existing classification confidence logic
6. **CLI Enhancement**: Extend existing commands with new classification options
7. **Test Enhancement**: Extend existing test suites with new scenarios
8. **Documentation**: Update existing docstrings and quickstart scenarios

**Estimated Output**: 15-20 numbered, ordered tasks in tasks.md focusing on enhancement rather than new creation

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

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
- [x] Complexity deviations documented (none required)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
