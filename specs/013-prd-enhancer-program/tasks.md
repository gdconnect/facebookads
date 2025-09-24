# Tasks: PRD Enhancer Program

**Input**: Design documents from `/specs/013-prd-enhancer-program/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: Python 3.11+, pydantic>=2, pydantic-ai, single-file agent
2. Load design documents:
   → data-model.md: 7 entities (PRDDocument, EnhancedPRD, Ambiguity, Feature, DomainEvent, ComplexityScore, JSONSchema)
   → contracts/: input.json, output.json, envelope.json
   → research.md: PydanticAI decisions, constitutional compliance
   → quickstart.md: 7 test scenarios from manual tests
3. Generate tasks by category:
   → Setup: agent structure, dependencies, constitutional compliance
   → Tests: contract tests, integration tests from scenarios
   → Core: models, LLM passes, decision tables, business logic
   → Integration: CLI, PydanticAI setup, file I/O, logging
   → Polish: unit tests, performance validation, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Single agent file = sequential for core logic
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. ORDER: Setup → Contract Tests → Model Tests → Integration Tests → Models → Core Logic → CLI → Polish
7. SUCCESS: 34 tasks ready for execution
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Single-file agent structure following constitution:
- **Agent**: `agents/prd_enhancer/prd_enhancer.py` (main file)
- **Tests**: `agents/prd_enhancer/tests/contract/`, `agents/prd_enhancer/tests/integration/`, `agents/prd_enhancer/tests/unit/`
- **Schemas**: `agents/prd_enhancer/schemas/` (auto-generated)
- **Examples**: `agents/prd_enhancer/examples/`
- **Docs**: `agents/prd_enhancer/docs/`

## Phase 3.1: Setup & Structure

- [ ] T001 Create agent directory structure `agents/prd_enhancer/` with subdirs: tests/, schemas/, examples/, docs/
- [ ] T002 Create `agents/prd_enhancer/README.md` with agent description and usage
- [ ] T003 [P] Create `agents/prd_enhancer/requirements.txt` with pydantic>=2, pydantic-ai, markdown
- [ ] T004 [P] Create pytest configuration in `agents/prd_enhancer/pytest.ini`
- [ ] T005 [P] Create `.gitignore` for Python cache and test artifacts in agent directory

## Phase 3.2: Contract Tests (TDD) ⚠️ MUST COMPLETE BEFORE 3.4
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [ ] T006 [P] Contract test for input schema validation in `agents/prd_enhancer/tests/contract/test_input_schema.py`
- [ ] T007 [P] Contract test for output schema validation in `agents/prd_enhancer/tests/contract/test_output_schema.py`
- [ ] T008 [P] Contract test for envelope schema validation in `agents/prd_enhancer/tests/contract/test_envelope_schema.py`
- [ ] T009 [P] Contract test for error schema validation in `agents/prd_enhancer/tests/contract/test_error_schema.py`

## Phase 3.3: Integration Tests (TDD) ⚠️ MUST COMPLETE BEFORE 3.4

- [ ] T010 [P] Smoke test scenario in `agents/prd_enhancer/tests/integration/test_smoke.py` (1-paragraph PRD, <2s)
- [ ] T011 [P] Ambiguity detection test in `agents/prd_enhancer/tests/integration/test_ambiguity_detection.py`
- [ ] T012 [P] Feature reduction test in `agents/prd_enhancer/tests/integration/test_feature_reduction.py` (20→5 features)
- [ ] T013 [P] LLM fallback test in `agents/prd_enhancer/tests/integration/test_llm_fallback.py`
- [ ] T014 [P] Multi-pass test in `agents/prd_enhancer/tests/integration/test_multi_pass.py`
- [ ] T015 [P] Skip-pass test in `agents/prd_enhancer/tests/integration/test_skip_pass.py`
- [ ] T016 [P] Complexity reduction test in `agents/prd_enhancer/tests/integration/test_complexity_reduction.py`

## Phase 3.4: Core Models (ONLY after tests are failing)

- [ ] T017 [P] PRDDocument model with validation in `agents/prd_enhancer/tests/unit/test_prd_document_model.py`
- [ ] T018 [P] EnhancedPRD model with validation in `agents/prd_enhancer/tests/unit/test_enhanced_prd_model.py`
- [ ] T019 [P] Ambiguity model with validation in `agents/prd_enhancer/tests/unit/test_ambiguity_model.py`
- [ ] T020 [P] Feature model with validation in `agents/prd_enhancer/tests/unit/test_feature_model.py`
- [ ] T021 [P] DomainEvent model with validation in `agents/prd_enhancer/tests/unit/test_domain_event_model.py`
- [ ] T022 [P] ComplexityScore model with validation in `agents/prd_enhancer/tests/unit/test_complexity_score_model.py`
- [ ] T023 [P] JSONSchema model with validation in `agents/prd_enhancer/tests/unit/test_json_schema_model.py`

## Phase 3.5: Core Implementation (Sequential - Single File)

- [ ] T024 Initialize `agents/prd_enhancer/prd_enhancer.py` with constitutional header, imports, and basic structure
- [ ] T025 Implement Pydantic models (MetaModel, InputModel, OutputModel, ErrorModel, Envelope) in prd_enhancer.py
- [ ] T026 Implement ConfigModel with env binding for agent configuration in prd_enhancer.py
- [ ] T027 Implement markdown parser and word count logic in prd_enhancer.py
- [ ] T028 Implement regex fallback patterns for ambiguity detection in prd_enhancer.py
- [ ] T029 Implement keyword scoring for feature prioritization in prd_enhancer.py
- [ ] T030 Implement complexity scoring algorithm `(entities * 3) + (events * 2) + (integrations * 5)` in prd_enhancer.py

## Phase 3.6: LLM Integration (Sequential - Single File)

- [ ] T031 Implement PydanticAI agent setup with Claude-3-haiku configuration in prd_enhancer.py
- [ ] T032 Implement Pass 1: AmbiguityDetector agent with fallback to regex in prd_enhancer.py
- [ ] T033 Implement Pass 2: ScopeGuardian agent with fallback to keyword scoring in prd_enhancer.py
- [ ] T034 Implement Pass 3: ConsistencyChecker agent with conditional execution in prd_enhancer.py

## Phase 3.7: CLI & Integration (Sequential - Single File)

- [ ] T035 Implement CLI interface with argparse (run, selfcheck, print-schemas, dry-run) in prd_enhancer.py
- [ ] T036 Implement file I/O operations with error handling and validation in prd_enhancer.py
- [ ] T037 Implement budget enforcement (10s timeout, 1000 tokens, cost tracking) in prd_enhancer.py
- [ ] T038 Implement structured logging (JSONL to STDERR) per Article XVIII in prd_enhancer.py
- [ ] T039 Implement main orchestration logic with pass decision tree in prd_enhancer.py

## Phase 3.8: Polish & Validation

- [ ] T040 [P] Create golden test data in `agents/prd_enhancer/examples/` (sample PRDs with expected outputs)
- [ ] T041 [P] Run static analysis tools (ruff, black, mypy --strict, pylint) and fix issues
- [ ] T042 [P] Create `agents/prd_enhancer/docs/USAGE.md` with comprehensive usage examples
- [ ] T043 [P] Validate budget compliance (token count, timeout enforcement, cost tracking)
- [ ] T044 Run full test suite and validate >80% coverage requirement
- [ ] T045 [P] Create agent selfcheck functionality with environment validation
- [ ] T046 [P] Generate JSON schemas to `agents/prd_enhancer/schemas/` and validate against contracts
- [ ] T047 Performance validation: ensure <10s processing, <2s for simple PRDs
- [ ] T048 Final constitutional compliance check against all DoD requirements

## Dependencies

**Critical Path**:
- Setup (T001-T005) blocks everything
- Contract tests (T006-T009) must fail before models (T017-T023)
- Integration tests (T010-T016) must fail before implementation (T024-T039)
- Models (T017-T023) must pass before core implementation (T024-T030)
- Core implementation (T024-T030) before LLM integration (T031-T034)
- LLM integration (T031-T034) before CLI (T035-T039)
- All implementation before polish (T040-T048)

**Parallel Groups**:
- Setup tasks: T003, T004, T005 (different files)
- Contract tests: T006, T007, T008, T009 (different files)
- Integration tests: T010-T016 (different files)
- Model tests: T017-T023 (different files)
- Polish tasks: T040, T041, T042, T043, T045, T046 (different files/activities)

## Parallel Execution Examples

### Contract Tests (Launch Together)
```bash
# All contract tests can run in parallel
Task: "Contract test for input schema validation in agents/prd_enhancer/tests/contract/test_input_schema.py"
Task: "Contract test for output schema validation in agents/prd_enhancer/tests/contract/test_output_schema.py"
Task: "Contract test for envelope schema validation in agents/prd_enhancer/tests/contract/test_envelope_schema.py"
Task: "Contract test for error schema validation in agents/prd_enhancer/tests/contract/test_error_schema.py"
```

### Integration Tests (Launch Together)
```bash
# All integration tests can run in parallel
Task: "Smoke test scenario in agents/prd_enhancer/tests/integration/test_smoke.py"
Task: "Ambiguity detection test in agents/prd_enhancer/tests/integration/test_ambiguity_detection.py"
Task: "Feature reduction test in agents/prd_enhancer/tests/integration/test_feature_reduction.py"
Task: "LLM fallback test in agents/prd_enhancer/tests/integration/test_llm_fallback.py"
Task: "Multi-pass test in agents/prd_enhancer/tests/integration/test_multi_pass.py"
Task: "Skip-pass test in agents/prd_enhancer/tests/integration/test_skip_pass.py"
Task: "Complexity reduction test in agents/prd_enhancer/tests/integration/test_complexity_reduction.py"
```

### Model Tests (Launch Together)
```bash
# All model tests can run in parallel
Task: "PRDDocument model with validation in agents/prd_enhancer/tests/unit/test_prd_document_model.py"
Task: "EnhancedPRD model with validation in agents/prd_enhancer/tests/unit/test_enhanced_prd_model.py"
Task: "Ambiguity model with validation in agents/prd_enhancer/tests/unit/test_ambiguity_model.py"
Task: "Feature model with validation in agents/prd_enhancer/tests/unit/test_feature_model.py"
Task: "DomainEvent model with validation in agents/prd_enhancer/tests/unit/test_domain_event_model.py"
Task: "ComplexityScore model with validation in agents/prd_enhancer/tests/unit/test_complexity_score_model.py"
Task: "JSONSchema model with validation in agents/prd_enhancer/tests/unit/test_json_schema_model.py"
```

## Notes

- **Single-file constraint**: T024-T039 must be sequential (all modify prd_enhancer.py)
- **TDD Critical**: All tests (T006-T023) must fail before implementation starts
- **Constitutional compliance**: T048 validates against all DoD requirements
- **Performance gates**: T043, T047 ensure budget compliance
- **Parallel optimization**: 23 of 48 tasks can run in parallel groups

## Task Generation Rules Applied

1. **From Contracts**: 3 contract files → 4 contract test tasks (T006-T009) [P]
2. **From Data Model**: 7 entities → 7 model test tasks (T017-T023) [P]
3. **From Quickstart**: 7 test scenarios → 7 integration tests (T010-T016) [P]
4. **Constitutional**: Single-file agent → sequential core tasks (T024-T039)
5. **TDD Order**: All tests before implementation
6. **Dependencies**: Setup → Tests → Models → Implementation → Polish

## Validation Checklist

- [x] All contracts have corresponding tests (T006-T009)
- [x] All entities have model tasks (T017-T023)
- [x] All tests come before implementation (T006-T023 before T024-T039)
- [x] Parallel tasks truly independent (different files only)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Constitutional compliance validated (T048)
- [x] Performance requirements addressed (T043, T047)