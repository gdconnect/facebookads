# Tasks: Business Idea Evaluator (BIE)

**Input**: Design documents from `/specs/014-business-idea-evaluator/`
**Prerequisites**: plan.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

## Execution Flow (main)
```
1. Loaded plan.md from feature directory ✓
   → Extracted: Python 3.10+, pydantic-ai, single-file CLI tool
2. Loaded design documents ✓:
   → data-model.md: 7 entities identified
   → contracts/: CLI interface with 3 main operations
   → quickstart.md: 8 test scenarios identified
3. Generated tasks by category:
   → Setup: project structure, dependencies, linting
   → Tests: contract tests, integration tests (TDD)
   → Core: models, services, CLI commands
   → Integration: LLM integration, scoring, I/O
   → Polish: unit tests, performance, documentation
4. Applied task rules:
   → Different modules/schemas = marked [P]
   → Single file implementation = sequential
   → Tests before implementation (TDD)
5. Numbered tasks T001-T035
6. Generated dependency graph
7. Created parallel execution examples
8. Validated task completeness ✓
9. SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files/modules, no dependencies)
- All file paths relative to repository root

## Path Conventions
- **Agent Structure**: `agents/bie/` (constitutional requirement)
- **Single File**: `agents/bie/bie.py` (main implementation)
- **Supporting Files**: `agents/bie/schemas/`, `agents/bie/tests/`, `agents/bie/examples/`

## Phase 3.1: Project Setup & Infrastructure

- [ ] **T001** Create agent directory structure at `agents/bie/` with subdirectories: `schemas/`, `tests/`, `examples/`, `docs/`
- [ ] **T002** Create `agents/bie/requirements.txt` with dependencies: pydantic>=2, pydantic-ai, pytest, hypothesis
- [ ] **T003** [P] Configure linting and formatting: create `agents/bie/.ruff.toml` and `agents/bie/pyproject.toml` for mypy
- [ ] **T004** [P] Create `agents/bie/README.md` with basic usage and setup instructions
- [ ] **T005** [P] Create `agents/bie/.env.example` with required environment variables

## Phase 3.2: Schema Generation (TDD Foundation) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: Schema definitions and contract tests MUST be written FIRST**

- [ ] **T006** [P] Define RawIdea Pydantic model in `agents/bie/schemas/raw_idea.py`
- [ ] **T007** [P] Define BusinessModel Pydantic model in `agents/bie/schemas/business_model.py`
- [ ] **T008** [P] Define ScalabilityFactors Pydantic model in `agents/bie/schemas/scalability.py`
- [ ] **T009** [P] Define RiskAssessment Pydantic model in `agents/bie/schemas/risk.py`
- [ ] **T010** [P] Define ComputedScores and ActionableInsights models in `agents/bie/schemas/results.py`
- [ ] **T011** [P] Define EvaluatedIdea and Envelope models in `agents/bie/schemas/evaluation.py`
- [ ] **T012** [P] Define MetaModel, ErrorModel, and Config models in `agents/bie/schemas/meta.py`

## Phase 3.3: Contract Tests (TDD) ⚠️ MUST FAIL BEFORE IMPLEMENTATION

- [ ] **T013** [P] Contract test for evaluate command in `agents/bie/tests/contract/test_evaluate_contract.py`
- [ ] **T014** [P] Contract test for compare command in `agents/bie/tests/contract/test_compare_contract.py`
- [ ] **T015** [P] Contract test for validate command in `agents/bie/tests/contract/test_validate_contract.py`
- [ ] **T016** [P] Contract test for schema generation in `agents/bie/tests/contract/test_schema_export.py`
- [ ] **T017** [P] Envelope validation test in `agents/bie/tests/contract/test_envelope_structure.py`

## Phase 3.4: Integration Tests (User Scenarios) ⚠️ MUST FAIL BEFORE IMPLEMENTATION

- [ ] **T018** [P] Integration test: Basic idea evaluation in `agents/bie/tests/integration/test_basic_evaluation.py`
- [ ] **T019** [P] Integration test: High-score platform idea in `agents/bie/tests/integration/test_high_score_idea.py`
- [ ] **T020** [P] Integration test: Low-score restaurant idea in `agents/bie/tests/integration/test_low_score_idea.py`
- [ ] **T021** [P] Integration test: Multiple idea comparison in `agents/bie/tests/integration/test_idea_comparison.py`
- [ ] **T022** [P] Integration test: Markdown input parsing in `agents/bie/tests/integration/test_markdown_parsing.py`
- [ ] **T023** [P] Integration test: JSON and markdown output formats in `agents/bie/tests/integration/test_output_formats.py`
- [ ] **T024** [P] Integration test: Error handling and recovery in `agents/bie/tests/integration/test_error_handling.py`
- [ ] **T025** [P] Integration test: Configuration and environment setup in `agents/bie/tests/integration/test_configuration.py`

## Phase 3.5: Golden Test Data

- [ ] **T026** [P] Create golden test case: high-score example in `agents/bie/examples/high_score_platform.md`
- [ ] **T027** [P] Create golden test case: low-score example in `agents/bie/examples/low_score_restaurant.md`
- [ ] **T028** [P] Create golden test case: medium-score example in `agents/bie/examples/medium_score_saas.md`
- [ ] **T029** [P] Create expected JSON outputs in `agents/bie/tests/golden/`

## Phase 3.6: Core Implementation (ONLY after tests are failing)

- [ ] **T030** Implement main CLI entry point and argument parsing in `agents/bie/bie.py` (lines 1-100)
- [ ] **T031** Implement configuration loading and validation in `agents/bie/bie.py` (lines 101-200)
- [ ] **T032** Implement markdown parsing and RawIdea extraction in `agents/bie/bie.py` (lines 201-300)
- [ ] **T033** Implement LLM integration with PydanticAI in `agents/bie/bie.py` (lines 301-400)
- [ ] **T034** Implement multi-pass evaluation pipeline in `agents/bie/bie.py` (lines 401-500)
- [ ] **T035** Implement scoring algorithms and grade calculation in `agents/bie/bie.py` (lines 501-600)
- [ ] **T036** Implement blindspot detection rules in `agents/bie/bie.py` (lines 601-700)
- [ ] **T037** Implement JSON and markdown output generation in `agents/bie/bie.py` (lines 701-800)
- [ ] **T038** Implement compare and validate commands in `agents/bie/bie.py` (lines 801-900)
- [ ] **T039** Implement error handling, logging, and recovery in `agents/bie/bie.py` (lines 901-1000)

## Phase 3.7: Integration & Polish

- [ ] **T040** [P] Implement selfcheck, print-schemas, and dry-run subcommands
- [ ] **T041** [P] Add structured JSONL logging to STDERR per constitutional requirements
- [ ] **T042** [P] Implement cost tracking and budget enforcement
- [ ] **T043** [P] Add retry logic and circuit breaker for LLM API calls
- [ ] **T044** [P] Performance optimization: caching and token management

## Phase 3.8: Quality & Documentation

- [ ] **T045** [P] Unit tests for scoring algorithms in `agents/bie/tests/unit/test_scoring.py`
- [ ] **T046** [P] Unit tests for markdown parsing in `agents/bie/tests/unit/test_parsing.py`
- [ ] **T047** [P] Unit tests for configuration validation in `agents/bie/tests/unit/test_config.py`
- [ ] **T048** [P] Property-based tests for scoring edge cases using Hypothesis
- [ ] **T049** [P] Performance benchmark tests: <2 minute evaluation, <10K token usage
- [ ] **T050** [P] Update `agents/bie/README.md` with complete usage documentation
- [ ] **T051** [P] Generate JSON schemas to `agents/bie/schemas/*.json` via CI automation
- [ ] **T052** Run linting and formatting: ruff, black, mypy --strict, pylint ≥9.5
- [ ] **T053** Verify test coverage ≥80% branches and <5s runtime for full suite

## Dependencies

### Critical Path Dependencies
- **Setup** (T001-T005) → **Schemas** (T006-T012) → **Contract Tests** (T013-T017)
- **Contract Tests** (T013-T017) + **Integration Tests** (T018-T025) → **Core Implementation** (T030-T039)
- **Core Implementation** (T030-T039) → **Integration** (T040-T044) → **Quality** (T045-T053)

### Sequential Dependencies (Single File)
- T030 → T031 → T032 → T033 → T034 → T035 → T036 → T037 → T038 → T039 (bie.py implementation)

### Parallel Groups
- **Schemas**: T006-T012 can run in parallel (different files)
- **Contract Tests**: T013-T017 can run in parallel (different test files)
- **Integration Tests**: T018-T025 can run in parallel (different scenarios)
- **Golden Data**: T026-T029 can run in parallel (different example files)
- **Quality Tasks**: T045-T051 can run in parallel (different test files)

## Parallel Execution Examples

### Phase 3.2: Schema Creation (7 parallel agents)
```bash
# Launch all schema tasks simultaneously
Task: "Define RawIdea Pydantic model in agents/bie/schemas/raw_idea.py"
Task: "Define BusinessModel Pydantic model in agents/bie/schemas/business_model.py"
Task: "Define ScalabilityFactors Pydantic model in agents/bie/schemas/scalability.py"
Task: "Define RiskAssessment Pydantic model in agents/bie/schemas/risk.py"
Task: "Define ComputedScores and ActionableInsights models in agents/bie/schemas/results.py"
Task: "Define EvaluatedIdea and Envelope models in agents/bie/schemas/evaluation.py"
Task: "Define MetaModel, ErrorModel, and Config models in agents/bie/schemas/meta.py"
```

### Phase 3.3: Contract Tests (5 parallel agents)
```bash
# Launch all contract tests simultaneously
Task: "Contract test for evaluate command in agents/bie/tests/contract/test_evaluate_contract.py"
Task: "Contract test for compare command in agents/bie/tests/contract/test_compare_contract.py"
Task: "Contract test for validate command in agents/bie/tests/contract/test_validate_contract.py"
Task: "Contract test for schema generation in agents/bie/tests/contract/test_schema_export.py"
Task: "Envelope validation test in agents/bie/tests/contract/test_envelope_structure.py"
```

### Phase 3.4: Integration Tests (8 parallel agents)
```bash
# Launch all integration tests simultaneously
Task: "Integration test: Basic idea evaluation in agents/bie/tests/integration/test_basic_evaluation.py"
Task: "Integration test: High-score platform idea in agents/bie/tests/integration/test_high_score_idea.py"
Task: "Integration test: Low-score restaurant idea in agents/bie/tests/integration/test_low_score_idea.py"
Task: "Integration test: Multiple idea comparison in agents/bie/tests/integration/test_idea_comparison.py"
Task: "Integration test: Markdown input parsing in agents/bie/tests/integration/test_markdown_parsing.py"
Task: "Integration test: JSON and markdown output formats in agents/bie/tests/integration/test_output_formats.py"
Task: "Integration test: Error handling and recovery in agents/bie/tests/integration/test_error_handling.py"
Task: "Integration test: Configuration and environment setup in agents/bie/tests/integration/test_configuration.py"
```

## Constitutional Compliance Requirements

### Code Quality Gates (enforced in T052)
- `ruff check agents/bie/` (style/fast lint)
- `black agents/bie/` (format)
- `mypy --strict agents/bie/bie.py` (zero type errors)
- `pylint agents/bie/bie.py` (score ≥9.5/10)
- `bandit agents/bie/bie.py` (no high/medium security issues)

### Testing Requirements
- Contract tests validate Envelope structure and JSON Schema compliance
- Integration tests cover all CLI commands and error scenarios
- Unit tests achieve ≥80% branch coverage
- Golden tests with known good/bad examples
- Property-based tests for scoring edge cases
- Runtime <5 seconds for full test suite

### Single-File Architecture
- All business logic in `agents/bie/bie.py` (<1000 lines)
- Pydantic models define schemas
- PydanticAI handles LLM integration
- Constitutional compliance with Articles I-XVIII

## Notes
- [P] tasks operate on different files and can run in parallel
- Schema tasks (T006-T012) create foundation for all other work
- ALL tests (T013-T025) must be written and FAIL before implementation (T030-T039)
- Single-file implementation (T030-T039) must be sequential due to shared file
- Commit after completing each phase
- Use `git branch 014-business-idea-evaluator` throughout development

## Validation Checklist
*GATE: All items must be checked before marking complete*

- [x] All CLI operations have corresponding contract tests
- [x] All data model entities have schema definitions
- [x] All tests come before implementation (TDD)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Constitutional requirements integrated throughout
- [x] Dependencies properly documented
- [x] Critical path identified