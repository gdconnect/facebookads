# Tasks: Article Outline Generator

**Input**: Design documents from `/specs/010-article-outline-generator/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single-file agent**: `agents/article_outline_generator/` (Constitutional requirement)
- **Tests**: `agents/article_outline_generator/tests/`
- **Schemas**: `agents/article_outline_generator/schemas/`
- **Docs**: `agents/article_outline_generator/docs/`

## Phase 3.1: Setup
- [ ] T001 Create agent directory structure at `agents/article_outline_generator/`
- [ ] T002 Initialize Python project with pydantic>=2, pydantic-ai dependencies in `agents/article_outline_generator/`
- [ ] T003 [P] Configure linting tools (ruff, black, mypy, pylint) in `agents/article_outline_generator/pyproject.toml`
- [ ] T004 [P] Create README.md with usage examples in `agents/article_outline_generator/README.md`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T005 [P] Contract test for input schema validation in `agents/article_outline_generator/tests/contract/test_input_schema.py`
- [ ] T006 [P] Contract test for output schema validation in `agents/article_outline_generator/tests/contract/test_output_schema.py`
- [ ] T007 [P] Contract test for envelope schema validation in `agents/article_outline_generator/tests/contract/test_envelope_schema.py`
- [ ] T008 [P] Integration test for article outline generation in `agents/article_outline_generator/tests/integration/test_article_generation.py`
- [ ] T009 [P] Integration test for story outline generation in `agents/article_outline_generator/tests/integration/test_story_generation.py`
- [ ] T010 [P] Integration test for content type classification in `agents/article_outline_generator/tests/integration/test_content_classification.py`
- [ ] T011 [P] Integration test for language detection in `agents/article_outline_generator/tests/integration/test_language_detection.py`
- [ ] T012 [P] Golden test with sample article input in `agents/article_outline_generator/tests/golden/test_article_sample.py`
- [ ] T013 [P] Golden test with sample story input in `agents/article_outline_generator/tests/golden/test_story_sample.py`
- [ ] T014 [P] Edge case test for empty/invalid input in `agents/article_outline_generator/tests/integration/test_error_handling.py`

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T015 [P] InputModel Pydantic class with validation in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T016 [P] OutlineMetadata Pydantic class in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T017 [P] Section Pydantic class (recursive) in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T018 [P] OutputModel Pydantic class in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T019 [P] ErrorModel Pydantic class in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T020 [P] Agent Envelope wrapper class in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T021 Content type classification decision table in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T022 Language detection decision table in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T023 Markdown parser for content analysis in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T024 Outline template generator (article/story patterns) in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T025 Section ID generation (slug creation) in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T026 Word count estimation algorithm in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T027 PydanticAI integration for LLM fallback in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T028 CLI argument parsing with argparse in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T029 Main execution flow coordination in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T030 JSONL logging to STDERR in `agents/article_outline_generator/article_outline_generator.py`

## Phase 3.4: Integration
- [ ] T031 Configuration management (env vars, config file) in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T032 Cost tracking and budget enforcement in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T033 Error handling and recovery mechanisms in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T034 Input validation and sanitization in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T035 Performance monitoring and optimization in `agents/article_outline_generator/article_outline_generator.py`

## Phase 3.5: Polish
- [ ] T036 [P] Unit tests for content classification logic in `agents/article_outline_generator/tests/unit/test_classification.py`
- [ ] T037 [P] Unit tests for language detection in `agents/article_outline_generator/tests/unit/test_language_detection.py`
- [ ] T038 [P] Unit tests for markdown parsing in `agents/article_outline_generator/tests/unit/test_markdown_parser.py`
- [ ] T039 [P] Unit tests for outline generation in `agents/article_outline_generator/tests/unit/test_outline_generation.py`
- [ ] T040 [P] Unit tests for section ID generation in `agents/article_outline_generator/tests/unit/test_section_ids.py`
- [ ] T041 [P] Performance tests (verify <5s execution) in `agents/article_outline_generator/tests/performance/test_execution_time.py`
- [ ] T042 [P] Update docs with usage examples in `agents/article_outline_generator/docs/usage.md`
- [ ] T043 [P] Create example input files in `agents/article_outline_generator/examples/`
- [ ] T044 Code quality cleanup (remove duplication, optimize) in `agents/article_outline_generator/article_outline_generator.py`
- [ ] T045 Run quickstart.md validation scenarios manually

## Dependencies
**Critical Dependencies:**
- Setup (T001-T004) before everything else
- Tests (T005-T014) MUST be written and failing before implementation (T015-T030)
- Pydantic models (T015-T020) before business logic (T021-T030)
- Core implementation (T015-T030) before integration (T031-T035)
- Integration (T031-T035) before polish (T036-T045)

**Sequential Constraints (same file, cannot be parallel):**
- T015-T020: All models in same file (sequential order matters for dependencies)
- T021-T030: All business logic in same file (must follow model definitions)
- T031-T035: All integration features in same file

## Parallel Execution Examples

### Setup Phase (all parallel except T001):
```bash
# T002, T003, T004 can run together after T001:
Task: "Initialize Python project with pydantic>=2, pydantic-ai dependencies in agents/article_outline_generator/"
Task: "Configure linting tools (ruff, black, mypy, pylint) in agents/article_outline_generator/pyproject.toml"
Task: "Create README.md with usage examples in agents/article_outline_generator/README.md"
```

### Test Phase (all parallel):
```bash
# T005-T014 can all run together:
Task: "Contract test for input schema validation in agents/article_outline_generator/tests/contract/test_input_schema.py"
Task: "Contract test for output schema validation in agents/article_outline_generator/tests/contract/test_output_schema.py"
Task: "Contract test for envelope schema validation in agents/article_outline_generator/tests/contract/test_envelope_schema.py"
Task: "Integration test for article outline generation in agents/article_outline_generator/tests/integration/test_article_generation.py"
Task: "Integration test for story outline generation in agents/article_outline_generator/tests/integration/test_story_generation.py"
# ... (all test tasks can run in parallel)
```

### Model Phase (sequential in same file):
```bash
# T015-T020 must run sequentially (same file, dependencies):
# Run T015, then T016, then T017, etc.
```

### Polish Phase (all parallel):
```bash
# T036-T043 can all run together:
Task: "Unit tests for content classification logic in agents/article_outline_generator/tests/unit/test_classification.py"
Task: "Unit tests for language detection in agents/article_outline_generator/tests/unit/test_language_detection.py"
Task: "Performance tests (verify <5s execution) in agents/article_outline_generator/tests/performance/test_execution_time.py"
Task: "Update docs with usage examples in agents/article_outline_generator/docs/usage.md"
# ... (all different files, fully parallel)
```

## Notes
- **Constitutional Compliance**: Single-file agent in `article_outline_generator.py`
- **Schema Generation**: CI will extract JSON schemas from Pydantic models
- **Performance Budget**: <5s runtime, <2 LLM calls, <2000 tokens
- **Testing Strategy**: Golden tests for real scenarios, contract tests for schema validation
- **TDD Required**: All tests must fail before implementation begins
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task or logical group
- Run `mypy --strict` after each implementation task

## Task Generation Rules Applied

1. **From Contracts**: 3 schema files → 3 contract test tasks (T005-T007)
2. **From Data Model**: 5 entities → 6 model creation tasks (T015-T020)
3. **From Quickstart**: 5 scenarios → 5 integration tests + 3 golden tests (T008-T014)
4. **From Research**: Technical decisions → setup and implementation tasks
5. **Constitutional**: Single-file requirement → all core implementation in one file

## Validation Checklist
*GATE: Checked before task execution*

- [x] All contracts have corresponding tests (T005-T007)
- [x] All entities have model tasks (T015-T020)
- [x] All tests come before implementation (T005-T014 → T015+)
- [x] Parallel tasks truly independent (different files or no dependencies)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Constitutional compliance (single-file agent structure)
- [x] Performance requirements included (T041, budgets in T027, T032)
- [x] Quickstart scenarios covered (T008-T014, T045)
