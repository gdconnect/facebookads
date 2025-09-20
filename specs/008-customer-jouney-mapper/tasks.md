# Tasks: Customer Journey Mapper Generator

**Input**: Design documents from `/specs/008-customer-jouney-mapper/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.11+, Pydantic v2, single-file agent
   → Structure: Single project with constitutional compliance
2. Load optional design documents:
   → data-model.md: 5 core entities + Agent Envelope + decision tables
   → contracts/: schema.input.json, schema.output.json → contract tests
   → research.md: LLM integration, template-based generation decisions
3. Generate tasks by category:
   → Setup: single-file project, constitutional compliance
   → Tests: schema validation, integration scenarios from quickstart
   → Core: decision tables, LLM adapter, journey generation
   → Integration: CLI interface, error handling, observability
   → Polish: golden tests, performance validation, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Single-file implementation = sequential for core components
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. SUCCESS: 23 tasks ready for single-file constitutional agent
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single file agent**: `customer_journey_mapper.py` at repository root
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/unit/`
- **Schemas**: Reference existing `schemas/customer_journey.json.schema`

## Phase 3.1: Setup

### Project Structure & Dependencies
- [ ] **T001** Create single-file agent structure at `customer_journey_mapper.py` with constitutional header docstring
- [ ] **T002** Initialize Python project dependencies (Pydantic v2, pytest, mypy, ruff, black) in pyproject.toml
- [ ] **T003** [P] Configure linting tools (ruff.toml, mypy.ini) and pre-commit hooks for constitutional compliance

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (Schema Validation)
- [ ] **T004** [P] Contract test for input schema validation in `tests/contract/test_input_schema.py`
- [ ] **T005** [P] Contract test for output Agent Envelope in `tests/contract/test_output_envelope.py`
- [ ] **T006** [P] Contract test for customer journey schema compliance in `tests/contract/test_journey_schema.py`

### Integration Tests (Quickstart Scenarios)
- [ ] **T007** [P] Integration test for B2C e-commerce journey in `tests/integration/test_ecommerce_journey.py`
- [ ] **T008** [P] Integration test for B2B SaaS journey in `tests/integration/test_saas_journey.py`
- [ ] **T009** [P] Integration test for markdown input processing in `tests/integration/test_markdown_input.py`
- [ ] **T010** [P] Integration test for error handling edge cases in `tests/integration/test_error_handling.py`

### Performance & Constitutional Tests
- [ ] **T011** [P] Performance validation test (<5s runtime) in `tests/integration/test_performance.py`
- [ ] **T012** [P] Constitutional compliance test (JSONL logging, cost tracking) in `tests/integration/test_constitutional.py`

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Configuration & CLI Interface
- [ ] **T013** CONFIG section (lines 20-120) with hierarchical configuration in `customer_journey_mapper.py`
- [ ] **T014** CLI interface with argparse (--input, --input-file, --input-format, --output, --brand-token, --strict) in `customer_journey_mapper.py`
- [ ] **T015** Input validation and content type detection in `customer_journey_mapper.py`

### Decision Tables & Business Logic
- [ ] **T016** Market classification decision tables (inline JSON) in `customer_journey_mapper.py`
- [ ] **T017** Journey template decision tables for B2B/B2C patterns in `customer_journey_mapper.py`
- [ ] **T018** Persona generation templates and rules in `customer_journey_mapper.py`

### LLM Integration & Data Processing
- [ ] **T019** LLM provider abstraction (OpenAI/Anthropic/Gemini/Local) with fail-fast in `customer_journey_mapper.py`
- [ ] **T020** Input normalization (markdown/text → JSON) via LLM in `customer_journey_mapper.py`
- [ ] **T021** Journey generation engine using templates and decision tables in `customer_journey_mapper.py`

### Schema Validation & Output
- [ ] **T022** Pydantic models for all entities from data-model.md in `customer_journey_mapper.py`
- [ ] **T023** Agent Envelope output generation with metadata in `customer_journey_mapper.py`

## Phase 3.4: Integration & Observability

### Error Handling & Logging
- [ ] **T024** Error handling with constitutional fail-fast patterns in `customer_journey_mapper.py`
- [ ] **T025** JSONL observability logging to STDERR with trace_id in `customer_journey_mapper.py`
- [ ] **T026** Cost tracking and token usage monitoring in `customer_journey_mapper.py`

## Phase 3.5: Polish & Validation

### Golden Tests & Documentation
- [ ] **T027** [P] Golden test for B2C e-commerce (deterministic output) in `tests/unit/test_golden_ecommerce.py`
- [ ] **T028** [P] Golden test for B2B SaaS (deterministic output) in `tests/unit/test_golden_saas.py`
- [ ] **T029** [P] Golden test for markdown normalization in `tests/unit/test_golden_markdown.py`

### Final Validation
- [ ] **T030** [P] Performance benchmarking and optimization in `tests/performance/test_benchmarks.py`
- [ ] **T031** [P] Update documentation with usage examples and CLI help
- [ ] **T032** Execute quickstart.md validation scenarios end-to-end
- [ ] **T033** Constitutional DoD checklist verification (mypy --strict, ruff, black)

## Dependencies

### Critical Path Dependencies
```
Setup (T001-T003) → Tests (T004-T012) → Core Implementation (T013-T023) → Integration (T024-T026) → Polish (T027-T033)
```

### Specific Dependencies
- **T004-T012** (All tests) must complete and FAIL before **T013** (first implementation)
- **T013** (CONFIG) blocks **T014** (CLI) blocks **T015** (validation)
- **T016-T018** (Decision tables) can run parallel after **T015**
- **T019** (LLM adapter) blocks **T020** (normalization) blocks **T021** (generation)
- **T022** (Pydantic models) can run parallel with **T019-T021**
- **T023** (Agent Envelope) requires **T021** (generation) + **T022** (models)
- **T024-T026** (Integration) require all core implementation **T013-T023**
- **T027-T033** (Polish) require all previous phases complete

## Parallel Execution Examples

### Phase 3.2: Launch All Tests Together
```bash
# All test files can be created in parallel since they're independent files
Task: "Contract test for input schema validation in tests/contract/test_input_schema.py"
Task: "Contract test for output Agent Envelope in tests/contract/test_output_envelope.py"
Task: "Contract test for customer journey schema compliance in tests/contract/test_journey_schema.py"
Task: "Integration test for B2C e-commerce journey in tests/integration/test_ecommerce_journey.py"
Task: "Integration test for B2B SaaS journey in tests/integration/test_saas_journey.py"
Task: "Integration test for markdown input processing in tests/integration/test_markdown_input.py"
Task: "Integration test for error handling edge cases in tests/integration/test_error_handling.py"
Task: "Performance validation test (<5s runtime) in tests/integration/test_performance.py"
Task: "Constitutional compliance test (JSONL logging, cost tracking) in tests/integration/test_constitutional.py"
```

### Phase 3.3: Decision Tables Parallel Development
```bash
# After T015 completes, these can run in parallel (different logical components)
Task: "Market classification decision tables (inline JSON) in customer_journey_mapper.py"
Task: "Journey template decision tables for B2B/B2C patterns in customer_journey_mapper.py"
Task: "Persona generation templates and rules in customer_journey_mapper.py"
```

### Phase 3.5: Golden Tests Parallel Creation
```bash
# Different test files can be created simultaneously
Task: "Golden test for B2C e-commerce (deterministic output) in tests/unit/test_golden_ecommerce.py"
Task: "Golden test for B2B SaaS (deterministic output) in tests/unit/test_golden_saas.py"
Task: "Golden test for markdown normalization in tests/unit/test_golden_markdown.py"
Task: "Performance benchmarking and optimization in tests/performance/test_benchmarks.py"
Task: "Update documentation with usage examples and CLI help"
```

## Special Considerations for Single-File Agent

### Constitutional Requirements
- All implementation happens in ONE file: `customer_journey_mapper.py`
- Tasks T013-T026 modify the same file, so they CANNOT be parallel
- Each task should add a specific component to the file without breaking previous work
- Follow numbered flow comments (1, 2, 3...) as specified in constitutional Article VI

### Testing Strategy
- Tests are in separate files, so they CAN be parallel [P]
- All tests must be written first and MUST FAIL before implementation begins
- Golden tests provide deterministic validation for non-LLM components
- Integration tests validate full CLI workflows from quickstart scenarios

### Performance Targets
- **T011** validates <5s total runtime requirement
- **T030** provides detailed performance benchmarking
- LLM calls limited to ≤2 per execution (T020 normalization + T021 enrichment)

## Task Generation Rules Applied

1. **From Contracts**:
   - schema.input.json → T004 (input validation test)
   - schema.output.json → T005 (Agent Envelope test)
   - customer_journey.json.schema → T006 (journey compliance test)

2. **From Data Model**:
   - 5 core entities → T022 (Pydantic models)
   - Decision table schemas → T016-T018 (business logic)
   - Agent Envelope → T023 (output generation)

3. **From Quickstart Scenarios**:
   - B2C e-commerce scenario → T007 integration test + T027 golden test
   - B2B SaaS scenario → T008 integration test + T028 golden test
   - Markdown input → T009 integration test + T029 golden test
   - Error handling → T010 integration test
   - Performance validation → T011 integration test + T030 benchmarks

4. **From Research Decisions**:
   - Multi-format input → T015 (validation) + T020 (normalization)
   - LLM integration → T019 (adapter) + T020 (normalization)
   - Template-based generation → T017-T018 (templates) + T021 (generation)

## Validation Checklist
*GATE: Checked before task execution begins*

- [x] All contracts have corresponding tests (T004-T006)
- [x] All entities have model tasks (T022 covers all from data-model.md)
- [x] All tests come before implementation (T004-T012 before T013-T026)
- [x] Parallel tasks truly independent (separate files or logical components)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task (single-file constraints respected)
- [x] Constitutional requirements addressed (single-file, schema-first, Agent Envelope)
- [x] Performance targets included (T011, T030)
- [x] Quickstart scenarios covered (T007-T012, T027-T029, T032)

## Notes
- Single-file implementation means T013-T026 are sequential within the same file
- [P] tasks are independent files or separate logical components
- Verify ALL tests fail before beginning ANY implementation
- Follow constitutional DoD checklist in T033
- Each task should be atomic and immediately testable