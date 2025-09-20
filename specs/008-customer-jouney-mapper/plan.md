
# Implementation Plan: Customer Journey Mapper Generator

**Branch**: `008-customer-jouney-mapper` | **Date**: 2025-09-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-customer-jouney-mapper/spec.md`

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
Generate comprehensive customer journey maps for niche markets based on market specifications. The system accepts various input formats (markdown, JSON, text), normalizes them via LLM calls, infers customer personas, and generates complete journey maps conforming to the customer_journey.json.schema. Core approach follows constitutional requirements: single-file Python agent with decision tables, schema-first design, and structured JSON output in Agent Envelope format.

## Technical Context
**Language/Version**: Python 3.11+ (Constitutional requirement for single-file agents)
**Primary Dependencies**: Standard library preferred (json, argparse, pathlib, typing), Pydantic v2 for schema validation
**Storage**: File-based output (JSON), no persistent storage required
**Testing**: pytest with golden tests (JSON→JSON, Markdown→JSON, edge cases)
**Target Platform**: Cross-platform CLI tool (Linux/macOS/Windows)
**Project Type**: single (CLI agent following constitutional Article I)
**Performance Goals**: <5s total runtime, <1s for decision table resolution, <2 LLM calls per execution
**Constraints**: Single-file implementation, schema-first design, LLM as fallback only, STRICT mode default
**Scale/Scope**: Individual niche market processing (1 market → 1 journey map), support for batch processing

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Article I (Single-File Python)**: ✅ PASS - Single .py file with CLI entrypoint
**Article II (Contract-First)**: ✅ PASS - Will include schema.input.json and schema.output.json with Agent Envelope
**Article III (Decision Tables)**: ✅ PASS - Business logic via decision tables for niche market classification and journey patterns
**Article IV (Input Versatility)**: ✅ PASS - Supports text/markdown normalization to JSON before processing
**Article V (Hierarchical Config)**: ✅ PASS - CLI flags for config, rules, brand-token, strict, log-level
**Article VI (Documentation)**: ✅ PASS - Header docstring with numbered flow, usage examples
**Article VII (Type Safety)**: ✅ PASS - Full type hints, mypy --strict compliance
**Article VIII (Testing)**: ✅ PASS - Golden JSON→JSON, Markdown→JSON, failure tests
**Article IX (Observability)**: ✅ PASS - JSONL log to STDERR with trace_id, metrics
**Article X (LLM Policy)**: ✅ PASS - LLM disabled by default, only used for input normalization with <0.8 confidence
**Article XI (Provider Abstraction)**: ✅ PASS - Single call_llm adapter for multiple providers
**Article XII (Budgets)**: ✅ PASS - Declared P95 latency <5s, token budget, max retries ≤1
**Article XIII (Security/Brand)**: ✅ PASS - brand_token support, no hardcoded secrets
**Article XV (External Resources)**: ✅ PASS - LLM access via port/adapter pattern with fail-fast
**Article XVI (Prompt Management)**: ✅ PASS - Swappable prompts via config, prompt_id tracking

**Overall**: ✅ CONSTITUTIONAL COMPLIANCE - No violations detected

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

**Structure Decision**: Option 1 (Single project) - CLI agent follows constitutional single-file structure

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
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

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
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented (N/A - no violations)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
