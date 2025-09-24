
# Implementation Plan: PRD Enhancer Program

**Branch**: `013-prd-enhancer-program` | **Date**: 2025-09-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-prd-enhancer-program/spec.md`

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
Single-file Python program that enhances PRD documents by detecting ambiguities, reducing scope to core features, and providing clear specifications. Uses PydanticAI with Claude-3-haiku for intelligent analysis with regex fallbacks. Processes markdown PRDs locally to reduce implementation time by 50%.

## Technical Context
**Language/Version**: Python 3.11+ (required for PydanticAI compatibility)
**Primary Dependencies**: pydantic>=2, pydantic-ai, markdown parser only
**Storage**: Local filesystem only (markdown input/output files, no database)
**Testing**: pytest with contract/integration/golden tests
**Target Platform**: Local development environments (Linux, macOS, Windows)
**Project Type**: single (single Python file agent following constitution)
**Performance Goals**: <10 seconds total processing time, <2 seconds for simple PRDs
**Constraints**: Single file <1000 lines, 3 LLM passes max, 1000 tokens total budget, offline fallbacks
**Scale/Scope**: Process single PRD files up to 1MB, complexity score 0-100, max 5 features output

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Single-File Agent Requirements (Article I)**:
- ✅ Single Python file with CLI entrypoint
- ✅ Agent in `agents/prd_enhancer/prd_enhancer.py`
- ✅ Folder structure: schemas/, tests/, examples/, docs/, README.md
- ✅ Dependencies: pydantic>=2, pydantic-ai, markdown parser (approved)

**Contract-First Requirements (Article II)**:
- ✅ MetaModel, InputModel, OutputModel, ErrorModel, Envelope required
- ✅ JSON schemas auto-generated to schemas/ directory
- ✅ Input: markdown PRD file paths
- ✅ Output: Enhanced PRD with metadata envelope

**Decision Tables & Rules (Article III)**:
- ✅ Regex fallback patterns for ambiguity detection
- ✅ Keyword scoring for feature prioritization
- ✅ Clear triggers for LLM pass activation

**Model Policy (Article X)**:
- ✅ Model disabled by default, used as fallback
- ✅ PydanticAI with typed responses only
- ✅ Budget enforcement: 1000 tokens, 10 seconds, max 1 retry
- ✅ Claude-3-haiku provider specified

**Performance Budgets (Article XII)**:
- ✅ P95 latency: <10 seconds total
- ✅ Token budget: 1000 tokens maximum
- ✅ Cost budget: minimal (haiku tier)
- ✅ Max retries: 1

**Security & Compliance (Article XIII)**:
- ✅ No secrets in code, env-only API keys
- ✅ Local processing only
- ✅ No external dependencies beyond LLM

**Result**: ✅ PASS - All constitutional requirements satisfied

**Post-Design Re-evaluation**:
- ✅ Data model maintains single-file agent structure
- ✅ Contracts follow Pydantic v2 typed model requirements
- ✅ No additional dependencies introduced beyond approved list
- ✅ Testing strategy aligns with constitutional requirements
- ✅ All budgets and constraints maintained in design
- ✅ No violations introduced during Phase 1 design

**Final Result**: ✅ PASS - Constitutional compliance maintained through design

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

**Structure Decision**: Option 1 (Single project) - Confirmed single-file agent structure per constitution

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
- Contract validation tasks from contracts/ directory [P]
- Pydantic model creation tasks for 7 core entities [P]
- Integration test tasks from user scenarios in spec
- Implementation tasks following constitutional single-file structure

**Specific Task Categories**:
1. **Contract Tests** (Parallel execution):
   - Validate input.json schema compliance
   - Validate output.json schema compliance
   - Validate envelope.json structure
   - Test error schema validation

2. **Model Creation** (Parallel execution):
   - PRDDocument, EnhancedPRD, Ambiguity, Feature models
   - DomainEvent, ComplexityScore, JSONSchema models
   - ConfigModel for agent configuration
   - MetaModel, InputModel, OutputModel, ErrorModel, Envelope

3. **Core Logic Tasks** (Sequential):
   - Markdown parser implementation
   - LLM pass orchestration (3 passes)
   - Regex fallback patterns
   - Decision table logic
   - Complexity scoring algorithm

4. **Integration Tasks**:
   - PydanticAI agent setup and configuration
   - CLI interface with argparse
   - File I/O operations with error handling
   - Budget enforcement and timeout management
   - Structured logging implementation

5. **Testing Tasks**:
   - Golden test scenarios from PRD manual tests
   - Smoke test (1-paragraph PRD)
   - Ambiguity detection test
   - Feature reduction test
   - LLM fallback test
   - Multi-pass and skip-pass tests

**Ordering Strategy**:
- TDD order: Contract tests → Model tests → Integration tests → Implementation
- Dependency order: Models → Decision tables → LLM integration → CLI
- Constitutional order: Pydantic models → Business logic → PydanticAI → CLI wrapper
- Mark [P] for parallel execution (independent model/test files)

**Constitutional Compliance Tasks**:
- Single-file agent structure validation
- Schema generation to agents/prd_enhancer/schemas/
- Structured logging implementation (Article XVIII)
- Budget enforcement and cost tracking
- Defensive programming patterns
- Static analysis compliance preparation

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**Task Complexity Distribution**:
- Simple tasks (models, basic tests): 15 tasks
- Medium tasks (business logic, integration): 12 tasks
- Complex tasks (LLM integration, CLI): 8 tasks

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
