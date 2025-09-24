# Tasks: Flexible Business Idea Generator

**Input**: Design documents from `/specs/016-flexible-business-idea/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack (Python 3.10+, pydantic, pydantic-ai), structure (single-file agent)
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: enhanced-parser.json → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: agent enhancement, dependencies, linting
   → Tests: contract tests, integration tests (5 quickstart scenarios)
   → Core: enhanced models, flexible parser, section mapping
   → Integration: LLM fallback, configuration, validation
   → Polish: unit tests, performance, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → Contract has test? ✓
   → All entities have models? ✓
   → All scenarios tested? ✓
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single-file agent**: Enhancement to existing `agents/bie/bie.py`
- **Tests**: `agents/bie/tests/` (contract/, integration/, golden/, unit/)
- **Schemas**: `agents/bie/schemas/` (generated JSON schemas)
- **Examples**: `agents/bie/examples/` (test documents)

## Phase 3.1: Setup

- [ ] T001 Create enhanced test structure in agents/bie/tests/ with contract/, integration/, golden/, unit/ folders
- [ ] T002 [P] Create test document examples in agents/bie/examples/ from quickstart scenarios
- [ ] T003 [P] Configure pytest with hypothesis for property testing
- [ ] T004 [P] Update agents/bie/requirements.txt with enhanced dependencies (if not using stdlib fuzzy matching)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [ ] T005 [P] Contract test for parse_markdown_flexible method in agents/bie/tests/contract/test_enhanced_parser_contract.py
- [ ] T006 [P] Schema validation test for ExtractionResult in agents/bie/tests/contract/test_extraction_result_schema.py
- [ ] T007 [P] Configuration schema test for FlexibleExtractionConfig in agents/bie/tests/contract/test_config_schema.py

### Integration Tests (from Quickstart Scenarios)
- [ ] T008 [P] Alternative section names test in agents/bie/tests/integration/test_alt_sections.py
- [ ] T009 [P] Nested structure extraction test in agents/bie/tests/integration/test_nested_structure.py
- [ ] T010 [P] Missing optional fields test in agents/bie/tests/integration/test_missing_fields.py
- [ ] T011 [P] Ambiguous content LLM fallback test in agents/bie/tests/integration/test_llm_fallback.py
- [ ] T012 [P] Error handling and validation test in agents/bie/tests/integration/test_error_handling.py

### Golden Tests (Backward Compatibility)
- [ ] T013 [P] Existing markdown format golden test in agents/bie/tests/golden/test_legacy_format.py
- [ ] T014 [P] Performance regression test in agents/bie/tests/golden/test_performance_benchmark.py

## Phase 3.3: Enhanced Models (ONLY after tests are failing)

- [ ] T015 [P] FlexibleExtractionConfig model with validation in agents/bie/bie.py (lines ~80-120)
- [ ] T016 [P] SectionMapping model with field validation in agents/bie/bie.py (lines ~121-140)
- [ ] T017 [P] ExtractionStrategy enum definition in agents/bie/bie.py (lines ~141-150)
- [ ] T018 [P] ExtractionResult model with metadata in agents/bie/bie.py (lines ~151-190)
- [ ] T019 [P] ExtractionWarning and ExtractionError models in agents/bie/bie.py (lines ~191-220)
- [ ] T020 [P] ExtractionMetadata and DocumentStats models in agents/bie/bie.py (lines ~221-260)
- [ ] T021 Enhance existing RawIdea model with extraction_metadata field in agents/bie/bie.py (lines ~126-136)

## Phase 3.4: Core Parser Implementation

- [ ] T022 Section mapping decision table with similarity scoring in agents/bie/bie.py (lines ~300-350)
- [ ] T023 Fuzzy string matching function with Levenshtein distance in agents/bie/bie.py (lines ~351-380)
- [ ] T024 Confidence scoring algorithm implementation in agents/bie/bie.py (lines ~381-420)
- [ ] T025 Enhanced parse_markdown method with multi-strategy extraction in agents/bie/bie.py (lines ~539-650)
- [ ] T026 Hierarchical content analysis for nested sections in agents/bie/bie.py (lines ~651-700)
- [ ] T027 Document statistics calculation and complexity assessment in agents/bie/bie.py (lines ~701-730)

## Phase 3.5: LLM Integration & Fallback

- [ ] T028 LLM fallback extraction using PydanticAI when confidence < 0.8 in agents/bie/bie.py (lines ~731-800)
- [ ] T029 Structured prompt for flexible content extraction in agents/bie/bie.py (lines ~801-850)
- [ ] T030 Token usage tracking and budget enforcement in agents/bie/bie.py (lines ~851-880)

## Phase 3.6: Configuration & CLI Enhancement

- [ ] T031 Add flexible extraction CLI flags (--fuzzy-threshold, --confidence-threshold, --enhanced) in agents/bie/bie.py (lines ~600-650)
- [ ] T032 Configuration loading with environment variable support in agents/bie/bie.py (lines ~100-150)
- [ ] T033 Enhanced error reporting with actionable suggestions in agents/bie/bie.py (lines ~881-920)

## Phase 3.7: Validation & Error Handling

- [ ] T034 Field length validation with graceful truncation in agents/bie/bie.py (lines ~921-950)
- [ ] T035 Document size limits and timeout handling in agents/bie/bie.py (lines ~951-980)
- [ ] T036 Comprehensive logging for extraction strategies and confidence in agents/bie/bie.py (lines ~981-1020)

## Phase 3.8: Performance Optimization

- [ ] T037 [P] Regex pattern caching and compilation optimization in agents/bie/bie.py (lines ~280-299)
- [ ] T038 [P] Early termination for high-confidence extractions in agents/bie/bie.py (lines ~420-450)
- [ ] T039 Memory usage optimization for large documents in agents/bie/bie.py (lines ~450-480)

## Phase 3.9: Polish & Documentation

- [ ] T040 [P] Unit tests for fuzzy matching algorithm in agents/bie/tests/unit/test_fuzzy_matching.py
- [ ] T041 [P] Unit tests for confidence scoring in agents/bie/tests/unit/test_confidence_scoring.py
- [ ] T042 [P] Property tests for section mapping with Hypothesis in agents/bie/tests/unit/test_section_mapping_properties.py
- [ ] T043 [P] Performance benchmarks for 2000-line documents in agents/bie/tests/unit/test_performance_limits.py
- [ ] T044 [P] Update agents/bie/README.md with flexible parsing examples
- [ ] T045 [P] Generate updated JSON schemas to agents/bie/schemas/ folder
- [ ] T046 Run complete test suite and validate all scenarios pass

## Dependencies

### Critical Dependencies
- Tests (T005-T014) must complete before any implementation (T015-T039)
- Models (T015-T021) before core parser (T022-T027)
- Core parser (T022-T027) before LLM integration (T028-T030)
- Configuration (T031-T033) can run parallel with core parser
- Performance optimization (T037-T039) after core implementation

### Specific Blocks
- T021 (enhance RawIdea) blocks T025 (enhanced parser)
- T022 (section mapping) blocks T023 (fuzzy matching) blocks T024 (confidence scoring)
- T025 (enhanced parser) blocks T028 (LLM fallback)
- T028-T030 (LLM integration) blocks T040-T043 (unit tests)

## Parallel Execution Examples

### Setup Phase (can run together)
```bash
# Launch T002-T004 together:
Task: "Create test document examples in agents/bie/examples/ from quickstart scenarios"
Task: "Configure pytest with hypothesis for property testing"
Task: "Update agents/bie/requirements.txt with enhanced dependencies"
```

### Test Creation Phase (can run together)
```bash
# Launch T005-T007 (contract tests) together:
Task: "Contract test for parse_markdown_flexible method in agents/bie/tests/contract/test_enhanced_parser_contract.py"
Task: "Schema validation test for ExtractionResult in agents/bie/tests/contract/test_extraction_result_schema.py"
Task: "Configuration schema test for FlexibleExtractionConfig in agents/bie/tests/contract/test_config_schema.py"

# Launch T008-T012 (integration tests) together:
Task: "Alternative section names test in agents/bie/tests/integration/test_alt_sections.py"
Task: "Nested structure extraction test in agents/bie/tests/integration/test_nested_structure.py"
Task: "Missing optional fields test in agents/bie/tests/integration/test_missing_fields.py"
Task: "Ambiguous content LLM fallback test in agents/bie/tests/integration/test_llm_fallback.py"
Task: "Error handling and validation test in agents/bie/tests/integration/test_error_handling.py"
```

### Model Creation Phase (can run together)
```bash
# Launch T015-T020 (new models) together:
Task: "FlexibleExtractionConfig model with validation in agents/bie/bie.py (lines ~80-120)"
Task: "SectionMapping model with field validation in agents/bie/bie.py (lines ~121-140)"
Task: "ExtractionStrategy enum definition in agents/bie/bie.py (lines ~141-150)"
Task: "ExtractionResult model with metadata in agents/bie/bie.py (lines ~151-190)"
Task: "ExtractionWarning and ExtractionError models in agents/bie/bie.py (lines ~191-220)"
Task: "ExtractionMetadata and DocumentStats models in agents/bie/bie.py (lines ~221-260)"
```

### Polish Phase (can run together)
```bash
# Launch T040-T045 (documentation and final tests) together:
Task: "Unit tests for fuzzy matching algorithm in agents/bie/tests/unit/test_fuzzy_matching.py"
Task: "Unit tests for confidence scoring in agents/bie/tests/unit/test_confidence_scoring.py"
Task: "Property tests for section mapping with Hypothesis in agents/bie/tests/unit/test_section_mapping_properties.py"
Task: "Performance benchmarks for 2000-line documents in agents/bie/tests/unit/test_performance_limits.py"
Task: "Update agents/bie/README.md with flexible parsing examples"
Task: "Generate updated JSON schemas to agents/bie/schemas/ folder"
```

## Task Success Criteria

### Each Task Must:
1. **Be Specific**: Include exact file paths and line number ranges where applicable
2. **Be Testable**: Clear definition of done with measurable outcomes
3. **Follow TDD**: Tests written first and must fail before implementation
4. **Maintain Constitution**: Single-file agent, schema-first, decision tables before LLM
5. **Preserve Backward Compatibility**: All existing functionality must continue to work

### Performance Targets:
- Parsing time: <200ms for typical documents
- Memory usage: <50MB per extraction
- Document size: Handle up to 2000 lines
- LLM token usage: <10K tokens per evaluation

### Quality Gates:
- All tests pass (contract, integration, golden, unit)
- No regressions in existing functionality
- Constitution compliance maintained
- Performance benchmarks met
- Schema validation passes

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing (TDD requirement)
- Single-file agent means some tasks cannot be truly parallel
- Line number ranges are estimates - adjust during implementation
- Constitution requires decision tables before LLM fallback
- All changes must maintain backward compatibility

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (T005-T007)
- [x] All entities have model tasks (T015-T021)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks truly independent (different files or line ranges)
- [x] Each task specifies exact file path (agents/bie/bie.py or specific test files)
- [x] No task modifies same lines as another [P] task (line ranges specified)
- [x] Quickstart scenarios covered (T008-T012)
- [x] Performance requirements addressed (T037-T039, T043)
- [x] Constitution compliance maintained (decision tables, schema-first, single-file)
