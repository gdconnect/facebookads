
# Implementation Plan: Interim Content Classification with LLM Fallback

**Branch**: `011-intererim-classification-of` | **Date**: 2025-09-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/var/www/html/facebookads/specs/011-intererim-classification-of/spec.md`

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
Primary requirement: Implement enhanced content classification system that reliably distinguishes between "article" and "essay" content types with LLM fallback capabilities. The system must support interim classification during content processing workflows, automatically invoke LLM when rule-based confidence is low, and allow up to two LLM calls per request for improved accuracy. Key technical approach: Build single-file Python agent extending existing article-outline-generator with dual-classification decision tables and PydanticAI integration for LLM fallback.

## Technical Context
**Language/Version**: Python 3.11+ (constitutional requirement for single-file agents)
**Primary Dependencies**: pydantic>=2.0, pydantic-ai (LLM abstraction), standard library (argparse, json, re, typing)
**Storage**: N/A (stateless classification agent)
**Testing**: pytest with contract, integration, and golden test patterns (constitutional requirement)
**Target Platform**: Linux server / CLI agent following single-file constitutional pattern
**Project Type**: single (extends existing agents/article_outline_generator pattern)
**Performance Goals**: <5s total runtime, <2 LLM calls max, <2000 tokens per call
**Constraints**: <200ms p95 for rule-based classification, graceful degradation when LLM unavailable
**Scale/Scope**: Interim classification for content processing pipelines, batch requests supported

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Article I - Single-File Agent**: ✅ PASS - Will implement as `agents/content_classifier/content_classifier.py`
**Article II - Contract-First**: ✅ PASS - Pydantic v2 models with JSON schema generation required
**Article III - Decision Tables First**: ✅ PASS - Rule-based classification before LLM fallback
**Article X - STRICT Default**: ✅ PASS - LLM disabled by default, only activated on low confidence
**Article XI - PydanticAI Integration**: ✅ PASS - All LLM calls through PydanticAI with typed responses
**Article XII - Performance Budgets**: ✅ PASS - <5s runtime, <2 LLM calls, <2000 tokens declared
**Article XVIII - Structured Logging**: ✅ PASS - JSONL to STDERR with agent_run, decision_eval, model_call events
**Article XX - CLI Requirements**: ✅ PASS - run, selfcheck, print-schemas, dry-run subcommands required

**Initial Assessment**: PASS - No constitutional violations detected. Feature aligns with single-file agent pattern and LLM fallback requirements.

**Post-Design Assessment**: PASS - Design maintains constitutional compliance:
- ✅ Single-file agent with clear CLI entrypoint
- ✅ Pydantic v2 models with JSON schema contracts
- ✅ Decision tables before LLM fallback (Article III)
- ✅ PydanticAI integration with typed responses
- ✅ Performance budgets declared and enforced
- ✅ Structured JSONL logging to STDERR
- ✅ Graceful degradation and error handling

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

**Structure Decision**: Option 1 (Single project) - Constitutional single-file agent pattern with agent-specific directory structure

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
- Contract schemas → contract test tasks [P]
- Pydantic models → model creation tasks [P]
- Decision tables → rule implementation tasks
- LLM integration → PydanticAI implementation tasks
- Quickstart scenarios → integration test tasks
- Constitutional requirements → compliance tasks

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models → Decision Tables → LLM Integration → CLI
- Mark [P] for parallel execution (independent files)
- Constitutional compliance throughout

**Specific Task Categories**:
1. **Setup Tasks**: Agent directory structure, pyproject.toml, README
2. **Contract Tests**: Schema validation, envelope compliance [P]
3. **Model Implementation**: Pydantic models for all entities [P]
4. **Decision Tables**: Article/essay classification rules
5. **LLM Integration**: PydanticAI setup with typed responses
6. **CLI Implementation**: run, batch, selfcheck, print-schemas commands
7. **Integration Tests**: End-to-end classification scenarios
8. **Golden Tests**: Real-world content samples
9. **Performance Tests**: Budget compliance validation
10. **Documentation**: Usage examples and edge cases

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

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
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


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
