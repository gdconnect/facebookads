# System Validation Tests

Repository-wide validation tests that ensure quality, compliance, and functionality across all agents and documentation.

## Purpose

These validation tests serve as **system-wide quality gates** for the Facebook Ads repository, implementing comprehensive validation tasks (T001-T023) that verify:

- **Cross-Agent Integration**: End-to-end workflows across multiple agents
- **Documentation Quality**: Completeness, accuracy, and KISS compliance
- **Constitutional Compliance**: Schema-First Empire Constitution adherence
- **Repository Standards**: Consistent structure and organization
- **Quality Gates**: Feature acceptance criteria validation

## Directory Structure

```
validation-tests/
├── scripts/                    # Validation shell scripts
│   ├── test-contracts.sh       # Contract validation (T010-T014)
│   ├── test-quality-assurance.sh  # Quality validation (T019-T023)
│   ├── test-quick-start.sh     # Quick start validation (T015-T018)
│   ├── test-workflows.sh       # Workflow validation (T016-T018)
│   └── validate-content.sh     # Content validation (T004-T008)
├── fixtures/                   # Test input files
│   ├── test-brand-basic.md     # Basic brand test fixture
│   ├── test-brand-comprehensive.md  # Comprehensive test fixture
│   └── test-brand-font-focused.md   # Font-focused test fixture
├── logs/                       # Validation logs (gitignored)
│   ├── *.log                   # Individual test logs
└── VALIDATION_REPORT.md        # Latest validation report
```

## Validation Tasks (T001-T023)

### Phase 1: Setup & Environment (T001-T003)
- **T001**: Documentation validation environment setup
- **T002**: Tool functionality verification
- **T003**: Test brand file creation

### Phase 2: Content Validation (T004-T008)
- **T004**: README.md structure and KISS compliance
- **T005**: Main documentation completeness (word count ≤5000)
- **T006**: Code examples verification (all executable)
- **T007**: Cross-reference links validation
- **T008**: Font selection documentation completeness

### Phase 3: Contract Testing (T009-T014)
- **T009**: Quick start performance validation (≤10 minutes)
- **T010**: Font selection documentation completeness
- **T011**: KISS principle compliance verification
- **T012**: Program state accuracy validation (≥70% CLI coverage)
- **T013**: Local developer focus verification
- **T014**: Cross-platform validation

### Phase 4: Workflow Testing (T015-T018)
- **T015**: End-to-end workflow validation
- **T016**: Google Fonts API setup workflow
- **T017**: Troubleshooting scenarios validation
- **T018**: Integration workflow validation

### Phase 5: Quality Assurance (T019-T023)
- **T019**: Performance regression testing
- **T020**: Full system integration testing
- **T021**: KISS metrics validation
- **T022**: Documentation consistency validation
- **T023**: Final quality gate and publication readiness

## Running Validation Tests

### Run All Validation Tests
```bash
# Run all validation scripts
for script in validation-tests/scripts/*.sh; do
    echo "Running $(basename $script)..."
    bash "$script"
done
```

### Run Individual Test Categories
```bash
# Content validation
bash validation-tests/scripts/validate-content.sh

# Contract validation
bash validation-tests/scripts/test-contracts.sh

# Quality assurance
bash validation-tests/scripts/test-quality-assurance.sh

# Quick start validation
bash validation-tests/scripts/test-quick-start.sh

# Workflow validation
bash validation-tests/scripts/test-workflows.sh
```

### Run Specific Validation Tasks
```bash
# Check logs for specific task results
grep "T010" validation-tests/logs/contract-validation.log
grep "T021" validation-tests/logs/quality-assurance.log
```

## Validation Criteria

### Documentation Standards
- **README.md**: ≤1000 words, includes Quick Start
- **Agent README**: ≤5000 words, comprehensive coverage
- **Actionable Content**: ≥5% code blocks and examples
- **KISS Compliance**: No deployment/CI/CD content
- **Cross-References**: All internal links valid

### Performance Requirements
- **Quick Start**: Complete setup in ≤10 minutes
- **Tool Execution**: All examples work without errors
- **API Integration**: Google Fonts API setup documented
- **Troubleshooting**: Common issues and solutions provided

### Quality Gates
- **Word Count Limits**: Enforced per KISS principles
- **Link Validation**: All cross-references working
- **Code Examples**: All snippets executable
- **Terminology**: Consistent usage throughout
- **Formatting**: Consistent code block formatting

## Integration with CI/CD

These validation tests are designed to be integrated into CI/CD pipelines:

```bash
# Example CI/CD integration
#!/bin/bash
set -e

echo "Running system validation tests..."
for script in validation-tests/scripts/*.sh; do
    echo "Executing $(basename $script)..."
    if ! bash "$script"; then
        echo "❌ Validation failed: $(basename $script)"
        exit 1
    fi
done

echo "✅ All validation tests passed"
```

## Validation Report

The latest validation results are documented in `VALIDATION_REPORT.md`, which includes:
- Summary of all 23 validation tasks
- Pass/fail status for each task
- Performance metrics and word counts
- Quality gate compliance verification
- Publication readiness assessment

## Adding New Validation Tests

To add new validation tests:

1. **Create test script** in `validation-tests/scripts/`
2. **Add test fixtures** in `validation-tests/fixtures/` if needed
3. **Update this README** with new task descriptions
4. **Follow task naming** convention (T024, T025, etc.)
5. **Log results** to `validation-tests/logs/`

### Test Script Template
```bash
#!/bin/bash
# Your Validation Test Script
# Tasks: TXXX-TXXX Description

set -e

echo "🚀 Starting Your Validation Test..."

REPO_ROOT="/var/www/html/facebookads"
cd "$REPO_ROOT"

VALIDATION_LOG="$REPO_ROOT/validation-tests/logs/your-validation.log"
> "$VALIDATION_LOG"

echo "📋 TXXX: Your validation task..." | tee -a "$VALIDATION_LOG"

# Your validation logic here
if [ condition ]; then
    echo "✅ PASS: Your validation criteria" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Your validation criteria" | tee -a "$VALIDATION_LOG"
    exit 1
fi

echo "✅ Your Validation Test completed successfully!" | tee -a "$VALIDATION_LOG"
```

## Troubleshooting

### Common Issues
- **Path References**: Ensure all paths use the new `agents/*/` structure
- **Log Permissions**: Ensure `validation-tests/logs/` is writable
- **Test Fixtures**: Verify fixtures exist in `validation-tests/fixtures/`
- **Agent Paths**: All agent references should use full `agents/agent_name/agent_name.py` paths

### Debug Mode
Run scripts with debug output:
```bash
bash -x validation-tests/scripts/test-contracts.sh
```

### Check Recent Results
```bash
# View latest validation logs
ls -la validation-tests/logs/
tail -f validation-tests/logs/quality-assurance.log
```

---

**Note**: These validation tests are **system-level** tests that validate the entire repository structure and quality. For agent-specific tests, see the individual `agents/*/tests/` directories.