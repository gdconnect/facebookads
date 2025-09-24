# Tasks: BIE Enhancement - Complete Implementation

**Input**: Design documents from `/var/www/html/facebookads/specs/015-bie-enhancement-complete/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory ✅
   → Extracted: Python 3.10+, Pydantic v2, single-file architecture
   → Structure: agents/bie/bie.py (constitutional single-file agent)
2. Load design documents ✅
   → data-model.md: ComparisonResult, Enhanced BlindspotRule, MarkdownFormatter
   → contracts/: CLI command contracts for evaluate, compare, validate commands
   → research.md: Deterministic approach, backwards compatibility decisions
   → quickstart.md: 5 test scenarios, performance benchmarks
3. Generate tasks by category:
   → Setup: verification, gap analysis, planning
   → Tests: CLI contract tests, integration scenario tests
   → Core: markdown formatter, blindspot detection, comparison logic
   → Integration: CLI argument parsing, output format handling
   → Polish: performance testing, backwards compatibility validation
4. Apply constitutional constraints:
   → All implementation tasks target single file: agents/bie/bie.py
   → No parallel [P] for implementation (same file conflicts)
   → Tests can be parallel [P] (different test files)
5. Number tasks sequentially (T001-T035)
6. TDD approach: Tests before implementation
7. Validate: All 16 functional requirements covered
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **Constitutional constraint**: All implementation tasks modify agents/bie/bie.py sequentially

## Path Conventions
- **Single-file agent**: `agents/bie/bie.py` (constitutional requirement)
- **Tests**: `agents/bie/tests/` (existing structure)
- **Absolute paths**: All paths from repository root `/var/www/html/facebookads/`

## Phase 3.1: Setup & Verification
- [ ] T001 Verify existing BIE implementation against functional requirements FR-001 to FR-016
- [ ] T002 [P] Analyze current markdown output gaps in agents/bie/bie.py
- [ ] T003 [P] Identify missing blindspot detection patterns in BlindspotDetector class
- [ ] T004 [P] Validate current CLI argument parsing structure for extension points

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### CLI Contract Tests [P]
- [ ] T005 [P] Contract test enhanced evaluate command with --output markdown in agents/bie/tests/contract/test_evaluate_markdown.py
- [ ] T006 [P] Contract test enhanced evaluate command with --output both in agents/bie/tests/contract/test_evaluate_both.py
- [ ] T007 [P] Contract test compare command with 2-10 files in agents/bie/tests/contract/test_compare_command.py
- [ ] T008 [P] Contract test compare command markdown output in agents/bie/tests/contract/test_compare_markdown.py

### Quickstart Integration Tests [P]
- [ ] T009 [P] Integration test enhanced markdown output scenario in agents/bie/tests/integration/test_enhanced_markdown_scenario.py
- [ ] T010 [P] Integration test blindspot detection scenario in agents/bie/tests/integration/test_blindspot_detection_scenario.py
- [ ] T011 [P] Integration test multi-idea comparison scenario in agents/bie/tests/integration/test_comparison_scenario.py
- [ ] T012 [P] Integration test output format consistency scenario in agents/bie/tests/integration/test_output_format_scenario.py
- [ ] T013 [P] Integration test edge cases and error handling in agents/bie/tests/integration/test_edge_cases_scenario.py

### Entity Model Tests [P]
- [ ] T014 [P] Unit test ComparisonResult model validation in agents/bie/tests/unit/test_comparison_result_model.py
- [ ] T015 [P] Unit test enhanced BlindspotRule patterns in agents/bie/tests/unit/test_enhanced_blindspot_rules.py
- [ ] T016 [P] Unit test markdown formatter methods in agents/bie/tests/unit/test_markdown_formatter.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Enhanced Markdown Output (FR-001 to FR-005)
- [ ] T017 Add ComparisonResult Pydantic v2 model to agents/bie/bie.py
- [ ] T018 Implement generate_enhanced_markdown() method in agents/bie/bie.py
- [ ] T019 Add grade-in-title formatting logic to generate_enhanced_markdown()
- [ ] T020 Add emoji-prefixed sections (📊, 💡, 🎯, ❗, 🚨, ✅, 🚀, 📈, 🔄) to markdown output
- [ ] T021 Implement checkbox formatting for quick wins (- [ ] format) in agents/bie/bie.py
- [ ] T022 Add visual score indicators (✅, ⚠️, ❌) based on score thresholds
- [ ] T023 Add original idea content preservation in dedicated markdown section

### Blindspot Detection Enhancement (FR-006 to FR-008)
- [ ] T024 Add "monetization later" blindspot detection pattern to BlindspotDetector in agents/bie/bie.py
- [ ] T025 Add "perfect before launch" blindspot detection pattern to BlindspotDetector in agents/bie/bie.py
- [ ] T026 Add specific advice generation for each blindspot pattern
- [ ] T027 Implement _ensure_min_red_flags() helper method for proper validation

### Multi-Idea Comparison (FR-009 to FR-013)
- [ ] T028 Implement compare_ideas() method in BusinessIdeaEvaluator class
- [ ] T029 Add _identify_relative_strengths() helper method for comparison analysis
- [ ] T030 Add _identify_relative_weaknesses() helper method for comparison analysis
- [ ] T031 Implement ranking algorithm by overall score with tie-breaking logic
- [ ] T032 Add _generate_comparison_recommendation() method with confidence levels
- [ ] T033 Add _generate_comparison_summary() method with pattern analysis

## Phase 3.4: CLI Integration & Output Handling (FR-014 to FR-016)
- [ ] T034 Update main() function argument parsing to handle --output markdown flag
- [ ] T035 Add --output both flag implementation with dual output formatting
- [ ] T036 Implement compare command CLI argument parsing and validation
- [ ] T037 Add markdown table generation for comparison output format
- [ ] T038 Update error handling for compare command (2-10 file validation)
- [ ] T039 Add ComparisonResult to print-schemas command output
- [ ] T040 Update validate command to handle enhanced parsing capabilities

## Phase 3.5: Polish & Validation
- [ ] T041 [P] Run existing integration tests to verify backwards compatibility
- [ ] T042 [P] Performance test: Single idea markdown generation (<1 second)
- [ ] T043 [P] Performance test: 10-idea comparison (<5 minutes total)
- [ ] T044 [P] Stress test: Large business ideas (5KB each) with memory monitoring
- [ ] T045 [P] Validate all 16 functional requirements (FR-001 to FR-016) implementation
- [ ] T046 [P] Run constitutional compliance checks (mypy --strict, type safety)
- [ ] T047 [P] Execute complete quickstart.md validation workflow
- [ ] T048 [P] Performance benchmark against targets (<2min evaluation, <50MB memory)

## Dependencies
**Critical Dependencies**:
- Tests (T005-T016) MUST complete and FAIL before implementation (T017-T040)
- T017 (ComparisonResult model) blocks T028-T033 (comparison implementation)
- T018-T023 (markdown formatter) can run after T017 completes
- T024-T027 (blindspot detection) can run after T017 completes
- T034-T040 (CLI integration) depends on T017-T033 completion
- Polish tasks (T041-T048) depend on all implementation tasks completion

**Sequential Constraints** (Constitutional single-file requirement):
- All T017-T040 tasks modify agents/bie/bie.py and must run sequentially
- No parallel execution for implementation tasks due to file conflicts

**Parallel Opportunities**:
- Test tasks T005-T016 can run in parallel [P] (different test files)
- Setup tasks T001-T004 can run in parallel [P] (read-only analysis)
- Polish tasks T041-T048 can run in parallel [P] (different validation aspects)

## Parallel Execution Examples

### Launch Test Suite (After Setup Complete)
```bash
# Launch T005-T016 together (all test files independent):
Task: "Contract test enhanced evaluate command with --output markdown in agents/bie/tests/contract/test_evaluate_markdown.py"
Task: "Contract test enhanced evaluate command with --output both in agents/bie/tests/contract/test_evaluate_both.py"
Task: "Contract test compare command with 2-10 files in agents/bie/tests/contract/test_compare_command.py"
Task: "Integration test enhanced markdown output scenario in agents/bie/tests/integration/test_enhanced_markdown_scenario.py"
Task: "Integration test blindspot detection scenario in agents/bie/tests/integration/test_blindspot_detection_scenario.py"
Task: "Unit test ComparisonResult model validation in agents/bie/tests/unit/test_comparison_result_model.py"
```

### Launch Polish & Validation (After Implementation Complete)
```bash
# Launch T041-T048 together (different validation aspects):
Task: "Run existing integration tests to verify backwards compatibility"
Task: "Performance test: Single idea markdown generation (<1 second)"
Task: "Performance test: 10-idea comparison (<5 minutes total)"
Task: "Validate all 16 functional requirements (FR-001 to FR-016) implementation"
Task: "Run constitutional compliance checks (mypy --strict, type safety)"
Task: "Execute complete quickstart.md validation workflow"
```

## Constitutional Compliance Notes
- ✅ Single-file architecture: All implementation in agents/bie/bie.py
- ✅ Pydantic v2 models: ComparisonResult follows existing patterns
- ✅ Type safety: Full type hints required on all new methods
- ✅ Testing coverage: ≥80% coverage maintained with new functionality
- ✅ No new dependencies: Uses existing stdlib + Pydantic v2
- ✅ Backwards compatibility: Existing JSON output format unchanged
- ✅ Structured logging: JSONL format preserved for new functionality

## Functional Requirements Coverage
Each task maps to specific functional requirements:

**Enhanced Markdown Output**: T017-T023 → FR-001 to FR-005
- T019: Grade in title format → FR-001
- T020: Emoji-prefixed sections → FR-002
- T021: Checkbox quick wins → FR-003
- T022: Visual score indicators → FR-004
- T023: Original idea preservation → FR-005

**Blindspot Detection**: T024-T027 → FR-006 to FR-008
- T024: Monetization blindspot → FR-006
- T025: Perfect launch blindspot → FR-007
- T026: Specific blindspot advice → FR-008

**Compare Command**: T028-T033 → FR-009 to FR-013
- T028: 2-10 file comparison → FR-009
- T031: Independent evaluation → FR-010
- T031: Ranking by score → FR-011
- T029-T030: Strengths/weaknesses → FR-012
- T032: Summary recommendation → FR-013

**Output Format**: T034-T040 → FR-014 to FR-016
- T034: --output markdown → FR-014
- T035: --output both → FR-015
- T041: Backwards compatibility → FR-016

## Validation Checklist
*GATE: All items must pass before marking feature complete*

- [ ] All 48 tasks completed successfully
- [ ] All contract tests passing (validate CLI behavior)
- [ ] All integration tests passing (validate user scenarios)
- [ ] All unit tests passing (validate model behavior)
- [ ] Constitutional compliance verified (single-file, type safety, coverage)
- [ ] Performance benchmarks met (<2min evaluation, <50MB memory, <5min comparison)
- [ ] All 16 functional requirements implemented and tested
- [ ] Backwards compatibility maintained (existing tests still pass)
- [ ] Quickstart scenarios executable and passing