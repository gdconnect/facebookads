
# Implementation Plan: Google Font Selector Enhancement

**Branch**: `006-font-selector-please` | **Date**: 2025-09-20 | **Spec**: [spec.md](/var/www/html/facebookads/specs/006-font-selector-please/spec.md)
**Input**: Feature specification from `/specs/006-font-selector-please/spec.md`

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
Enhance the existing brand identity generator tool to automatically select appropriate Google Fonts and typography settings when no explicit font specification is provided in the brand markdown. The feature integrates with the existing LLM enhancement workflow to provide intelligent font recommendations based on brand personality, target audience, and visual characteristics.

## Technical Context
**Language/Version**: Python 3.11+ (constitutional requirement with type hints)
**Primary Dependencies**: Pydantic V2, Click CLI, requests (for Google Fonts API), existing LLM providers (OpenAI/Anthropic)
**Storage**: File-based (Google Fonts metadata cache, enhanced JSON outputs, session persistence files)
**Testing**: pytest with contract, integration, and unit test structure
**Target Platform**: Cross-platform CLI tool (Linux, macOS, Windows)
**Project Type**: single (extends existing single-file Python program)
**Performance Goals**: Font selection <2 seconds, Google Fonts API <1 second response time
**Constraints**: Single-file architecture, Google Fonts exclusive usage, maintain backward compatibility
**Scale/Scope**: Support 1000+ Google Fonts, handle 100+ brand personalities, serve all existing use cases

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitutional Compliance**:
✅ **Single File Programs**: Font selector feature extends existing single-file brand_identity_generator.py
✅ **Best Practice Adherence**: Will follow PEP 8, comprehensive type hints, proper error handling
✅ **Comprehensive Documentation**: Font selection logic and Google Fonts integration will be fully documented
✅ **Pydantic V2 Integration**: New font models use @field_validator with @classmethod, modern syntax
✅ **Self-Contained Design**: Minimal dependencies (only requests for Google Fonts API), justified benefit
✅ **Developer Productivity**: Configuration for font selection at top of file, environment variable support
✅ **Type Safety & IDE Compliance**: 100% type hints, zero warnings, modern Python 3.11+ syntax

**Result**: ✅ PASS - No constitutional violations identified

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

**Structure Decision**: Option 1 (Single project) - Font selector extends existing single-file brand identity generator

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
- Generate font-specific implementation tasks from Phase 1 design docs
- Google Fonts API integration and caching → independent implementation tasks [P]
- Font selection algorithms and personality matching → core logic tasks
- Typography system generation → formatting and style tasks [P]
- CLI integration and enhancement workflow → integration tasks
- Configuration extension → settings and environment tasks [P]
- Contract tests for each API contract → validation tasks

**Ordering Strategy**:
- TDD order: Contract tests → Models → Font API → Selection logic → Typography generation → CLI integration
- Dependency order: Base models → Google Fonts client → Font selection engine → Typography system → Enhancement integration
- Mark [P] for parallel execution: Independent models, separate API clients, test files
- Sequential for core workflow: Font selection must work before typography generation

**Font-Specific Task Categories**:
1. **Data Model Tasks [P]**: GoogleFont, FontSelectionCriteria, TypographyHierarchy, FontRecommendation models
2. **Google Fonts Integration**: API client, caching system, metadata parsing
3. **Font Selection Engine**: Personality matching, rule-based selection, LLM integration
4. **Typography System**: Hierarchy generation, CSS output, style specifications
5. **CLI Integration**: Enhancement workflow, interactive mode, configuration
6. **Testing & Validation**: Contract tests, integration tests, performance validation

**Estimated Output**: 20-25 numbered, ordered tasks in tasks.md focusing on font selection implementation

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
- [x] Complexity deviations documented (N/A - no deviations)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
