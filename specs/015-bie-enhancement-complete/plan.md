
# Implementation Plan: BIE Enhancement - Complete Implementation

**Branch**: `015-bie-enhancement-complete` | **Date**: 2025-09-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/var/www/html/facebookads/specs/015-bie-enhancement-complete/spec.md`

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
Complete the BIE (Business Idea Evaluator) implementation by adding enhanced markdown output with emoji sections, completing blindspot detection patterns, and implementing the compare command functionality. The enhancement maintains single-file architecture and constitutional compliance while adding user-friendly formatting and multi-idea comparison capabilities.

## Technical Context
**Language/Version**: Python 3.10+ (existing BIE implementation)
**Primary Dependencies**: Pydantic v2, argparse, pathlib, json, hashlib, uuid (constitutional compliance)
**Storage**: File-based (markdown input, JSON/markdown output)
**Testing**: pytest (existing test framework in agents/bie/tests/)
**Target Platform**: Linux CLI environment (existing deployment)
**Project Type**: single (single-file Python agent per constitution)
**Performance Goals**: <2 minutes end-to-end evaluation, <50MB memory footprint
**Constraints**: Single-file architecture, constitutional compliance, backwards compatibility
**Scale/Scope**: Individual developer tool, ~1000 lines of code, CLI interface

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Article I - Single-File Architecture**: ✅ PASS
- Enhancement maintains existing agents/bie/bie.py single-file structure
- No new files required, only modifications to existing implementation

**Article II - Contract-First (Pydantic v2)**: ✅ PASS
- Uses existing Pydantic v2 models (EvaluatedIdea, Envelope, etc.)
- New ComparisonResult model follows same Pydantic v2 patterns
- Schema extraction already established

**Article V - Configuration**: ✅ PASS
- Enhancement uses existing ConfigModel with env bindings
- CLI flags already established (--output, --model, --verbose)
- No new configuration needed

**Article X - Model Policy**: ✅ PASS
- Enhancement is deterministic (markdown formatting, comparison logic)
- No new LLM calls required beyond existing blindspot detection
- Model disabled by default maintained

**Article VII - Type Safety**: ✅ PASS
- All new methods will include full type hints
- Defensive programming patterns maintained
- mypy --strict compliance preserved

**Article VIII - Testing**: ✅ PASS
- Existing test structure in agents/bie/tests/ maintained
- Contract tests for new functionality will be added
- Coverage ≥80% requirement maintained

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

**Structure Decision**: Single-file agent structure per Article I of Constitution - agents/bie/bie.py contains all implementation

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
- Generate tasks from Phase 1 design docs (CLI contracts, data model, quickstart scenarios)
- Each CLI command enhancement → contract test task [P]
- Each new entity (ComparisonResult, enhanced BlindspotRule) → model creation task [P]
- Each quickstart scenario → integration test task [P]
- Implementation tasks to make tests pass within single-file architecture

**BIE-Specific Task Categories**:
1. **Setup & Validation**: Verify existing implementation, identify gaps
2. **Test-First Development**: Contract tests for CLI commands, integration tests for scenarios
3. **Core Enhancement Implementation**:
   - Enhanced markdown output (emoji sections, visual indicators, checkboxes)
   - Blindspot detection completion (monetization, perfectionism patterns)
   - Compare command implementation (ranking, analysis, recommendation)
4. **CLI Integration**: Output format handling, argument parsing, error handling
5. **Polish & Validation**: Performance testing, backwards compatibility verification

**Ordering Strategy**:
- TDD order: Tests before implementation (constitutional requirement)
- Single-file constraints: All tasks modify agents/bie/bie.py sequentially
- Logical grouping: Markdown → Blindspot → Compare → CLI integration
- Validation tasks run in parallel [P] where they test different functionality

**Constitutional Considerations**:
- All implementation tasks target single file (agents/bie/bie.py)
- No parallel [P] implementation tasks (same file modification conflict)
- Test tasks can be parallel [P] (different test files)
- Setup and validation tasks can be parallel [P] (read-only operations)

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
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✅
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved ✅
- [x] Complexity deviations documented (N/A - no violations) ✅

**Artifacts Generated**:
- [x] `/var/www/html/facebookads/specs/015-bie-enhancement-complete/research.md` ✅
- [x] `/var/www/html/facebookads/specs/015-bie-enhancement-complete/data-model.md` ✅
- [x] `/var/www/html/facebookads/specs/015-bie-enhancement-complete/contracts/cli-commands.yaml` ✅
- [x] `/var/www/html/facebookads/specs/015-bie-enhancement-complete/quickstart.md` ✅
- [x] Agent context updated in `/var/www/html/facebookads/CLAUDE.md` ✅

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
