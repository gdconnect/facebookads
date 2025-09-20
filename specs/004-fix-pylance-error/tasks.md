# Tasks: Pydantic V1 to V2 Validator Migration

**Input**: Design documents from `/specs/004-fix-pylance-error/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/validation-interface.md, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.10+, Pydantic V2, single-file architecture
   → Scope: ~10-15 validator functions in brand_identity_generator.py
2. Load design documents:
   → research.md: Migration approach (syntax-only changes)
   → contracts/validation-interface.md: Validation behavior requirements
   → quickstart.md: Verification scenarios and test procedures
3. Generate tasks by category:
   → Setup: Baseline testing and environment verification
   → Tests: Validation behavior verification before/after migration
   → Core: Systematic validator syntax migration
   → Integration: End-to-end testing and verification
   → Polish: Warning cleanup and performance validation
4. Apply task rules:
   → Different validation categories = mark [P] for parallel baseline tests
   → Same file (brand_identity_generator.py) = sequential migration
   → Tests before changes, verification after changes
5. Number tasks sequentially (T001-T012)
6. Validate: All validators covered, behavior preserved, warnings eliminated
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different test categories, no dependencies)
- Single-file architecture: All changes in `brand_identity_generator.py`

## Phase 3.1: Setup & Baseline Testing

### T001 Establish baseline validation behavior
**File**: `tests/contract/test_pydantic_migration_baseline.py`
**Description**: Create comprehensive baseline tests capturing current V1 validator behavior for all DeveloperConfig validators (provider, URL, timeout, retries, backoff, enhancement level, log level)
**Success Criteria**:
- Test passes with current V1 validators
- Captures exact error messages for invalid inputs
- Records validation success for valid inputs
- Covers all edge cases from contracts

### T002 [P] Document current Pylance warnings
**File**: `docs/migration-baseline.md`
**Description**: Capture screenshot/output of current Pylance deprecation warnings in IDE, document exact warning messages and line numbers
**Success Criteria**:
- Complete list of all @validator deprecation warnings
- Line numbers and warning text documented
- Baseline for measuring warning elimination

### T003 [P] Verify existing test suite baseline
**File**: Current test files
**Description**: Run complete existing test suite and document results as baseline for regression detection
**Success Criteria**:
- All existing tests pass
- Test execution time recorded
- Output captured for comparison

## Phase 3.2: Migration Preparation ⚠️ MUST COMPLETE BEFORE 3.3

### T004 Update Pydantic imports for V2 syntax
**File**: `brand_identity_generator.py`
**Description**: Add `field_validator` to the Pydantic imports while keeping existing `validator` import temporarily for compatibility verification
**Success Criteria**:
- Import line includes both `validator` and `field_validator`
- Code still compiles without errors
- No functional changes yet

### T005 [P] Create validator migration verification test
**File**: `tests/contract/test_validation_behavior_preservation.py`
**Description**: Create test that compares V1 vs V2 validator behavior side-by-side for identical inputs/outputs
**Success Criteria**:
- Test framework can run same validation with both syntaxes
- Captures and compares error messages
- Will be used to verify migration preserves behavior

## Phase 3.3: Core Validator Migration (ONLY after preparation complete)

### T006 Migrate DeveloperConfig validators to V2 syntax
**File**: `brand_identity_generator.py`
**Description**: Replace all `@validator` decorators in DeveloperConfig class with `@field_validator` and add `@classmethod` decorators (llm_provider, llm_base_url, request_timeout, max_retries, retry_backoff_factor, default_enhancement_level, log_level)
**Success Criteria**:
- All 7 DeveloperConfig validators use V2 syntax
- No changes to validation logic
- All tests from T001 still pass
- Error messages remain identical

### T007 Migrate LLMRequest validators to V2 syntax
**File**: `brand_identity_generator.py`
**Description**: Replace `@validator` decorators in LLMRequest class with `@field_validator` and add `@classmethod` (confidence_score validator)
**Success Criteria**:
- LLMRequest validators use V2 syntax
- Confidence score validation works identically
- No functional changes

### T008 Migrate remaining model validators to V2 syntax
**File**: `brand_identity_generator.py`
**Description**: Find and migrate any remaining `@validator` decorators in other Pydantic models (impact validator, etc.)
**Success Criteria**:
- All `@validator` usage eliminated from file
- All validators use `@field_validator` + `@classmethod`
- Complete syntax migration

## Phase 3.4: Verification & Cleanup

### T009 Verify Pylance warnings eliminated
**File**: `brand_identity_generator.py`
**Description**: Open file in IDE with Pylance and verify no deprecation warnings about validators remain
**Success Criteria**:
- No Pylance warnings about deprecated `@validator`
- IDE shows no deprecation indicators
- Compare with T002 baseline to confirm elimination

### T010 Run comprehensive validation regression test
**File**: All test files
**Description**: Execute all validation tests from T001, T005 and existing test suite to verify identical behavior after migration
**Success Criteria**:
- All baseline tests from T001 pass with identical results
- T005 behavior comparison shows no differences
- Existing test suite results identical to T003 baseline

### T011 Remove unused validator import
**File**: `brand_identity_generator.py`
**Description**: Remove the `validator` import since all validators now use `field_validator`
**Success Criteria**:
- Only `field_validator` in imports
- No unused imports
- Code compiles and runs correctly

## Phase 3.5: Final Validation & Polish

### T012 Execute quickstart verification procedures
**File**: Follow `quickstart.md` procedures
**Description**: Run all verification steps from quickstart.md including configuration loading, CLI testing, environment variables, and performance checks
**Success Criteria**:
- All quickstart verification steps pass
- Performance baseline maintained
- Configuration system works identically
- CLI behavior unchanged
- Environment variable processing unchanged

## Dependencies
- T001-T003 (baseline) before T004-T005 (preparation)
- T004-T005 (preparation) before T006-T008 (migration)
- T006-T008 (migration) before T009-T010 (verification)
- T010 (regression test) before T011 (cleanup)
- T011 (cleanup) before T012 (final validation)

## Parallel Execution Opportunities

### Phase 3.1 Baseline (Can run in parallel):
```bash
# Launch T001-T003 together:
Task: "Establish baseline validation behavior in tests/contract/test_pydantic_migration_baseline.py"
Task: "Document current Pylance warnings in docs/migration-baseline.md"
Task: "Verify existing test suite baseline"
```

### Phase 3.3 Migration (Must be sequential - same file):
- T006 → T007 → T008 (sequential, all modify brand_identity_generator.py)

### Phase 3.4 Verification (Can partially parallel):
```bash
# T009 and T010 can run together:
Task: "Verify Pylance warnings eliminated in brand_identity_generator.py"
Task: "Run comprehensive validation regression test"
```

## Success Criteria Summary
1. **Zero Functional Changes**: All validation logic works identically
2. **Zero Pylance Warnings**: No deprecation warnings in IDE
3. **Performance Maintained**: No measurable performance regression
4. **Test Coverage**: All validators tested before/after migration
5. **Backward Compatibility**: Existing functionality unchanged

## Validation Checklist
*GATE: Checked before completion*

- [x] All @validator decorators have migration tasks
- [x] All validation contracts have verification tasks
- [x] All tests come before implementation changes
- [x] Parallel tasks are truly independent (different files/categories)
- [x] Each task specifies exact file path or procedure
- [x] Migration preserves single-file architecture
- [x] No task conflicts with constitutional requirements

## Notes
- Single-file architecture means most core tasks are sequential
- Focus on behavior preservation over implementation changes
- Comprehensive testing before and after each migration step
- Rollback plan available via git if any verification fails