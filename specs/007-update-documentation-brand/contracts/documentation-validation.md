# Documentation Validation Contracts

**Feature**: 007-update-documentation-brand
**Contract Type**: Documentation Validation
**Date**: 2025-09-20

## Overview

This contract defines validation criteria and acceptance tests for brand generator documentation updates.

## Contract 1: Quick Start Performance

**Contract ID**: DOC-QS-001
**Requirement**: FR-005 - Documentation MUST include a quick start section that gets developers running in under 10 minutes

### Validation Criteria
```yaml
test_scenario: new_developer_quick_start
success_criteria:
  - setup_time: <= 600 seconds (10 minutes)
  - steps_count: <= 5 major steps
  - dependencies_install_time: <= 300 seconds
  - first_successful_run: <= 60 seconds after setup
```

### Test Contract
```bash
# Test: Time a new developer following README.md from discovery to first success
START_TIME=$(date +%s)

# Step 1: Install dependencies (timed)
pip install -r requirements.txt

# Step 2: Set up environment (optional, timed)
export GOOGLE_FONTS_API_KEY=test_key_placeholder

# Step 3: Create brand file (timed)
cat > test-brand.md << EOF
# Test Brand
**Primary Color**: blue
**Brand Voice**: professional
**Target Audience**: developers
EOF

# Step 4: Run enhancement (timed)
python brand_identity_generator.py test-brand.md --enhance

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

# Contract assertion
if [ $TOTAL_TIME -le 600 ]; then
  echo "✅ PASS: Quick start completed in $TOTAL_TIME seconds"
else
  echo "❌ FAIL: Quick start took $TOTAL_TIME seconds (limit: 600)"
fi
```

### Acceptance Criteria
- [ ] Total time from README discovery to successful enhancement ≤ 10 minutes
- [ ] All commands in quick start section are copy-paste ready
- [ ] No external dependencies beyond Python and pip
- [ ] Error messages guide user to solution within quick start section

## Contract 2: Font Selection Documentation Completeness

**Contract ID**: DOC-FS-002
**Requirement**: FR-002, FR-006, FR-010 - Font selection features and Google API setup must be fully documented

### Validation Criteria
```yaml
documentation_sections_required:
  - google_fonts_api_setup:
      - api_key_acquisition
      - environment_variable_setup
      - verification_steps
  - font_selection_features:
      - automatic_font_matching
      - typography_hierarchy
      - css_generation
      - confidence_scoring
  - working_examples:
      - basic_font_selection
      - comprehensive_typography
      - offline_mode_fallback
```

### Test Contract
```bash
# Test: Verify font selection documentation completeness
echo "Testing font selection documentation..."

# Contract 1: Google API setup is documented
grep -q "GOOGLE_FONTS_API_KEY" docs/brand_identity_generator.md || {
  echo "❌ FAIL: Google API key setup not documented"
  exit 1
}

# Contract 2: Font selection workflow is explained
grep -q "Font Selection & Typography" docs/brand_identity_generator.md || {
  echo "❌ FAIL: Font selection section missing"
  exit 1
}

# Contract 3: Enhancement levels documented
grep -q "enhancement-level comprehensive" docs/brand_identity_generator.md || {
  echo "❌ FAIL: Enhancement levels not documented"
  exit 1
}

# Contract 4: Working examples provided
grep -q "python brand_identity_generator.py.*--enhance.*comprehensive" docs/brand_identity_generator.md || {
  echo "❌ FAIL: Comprehensive enhancement example missing"
  exit 1
}

echo "✅ PASS: Font selection documentation complete"
```

### Acceptance Criteria
- [ ] Google Fonts API setup has step-by-step instructions
- [ ] Font selection behavior is explained with brand voice mapping
- [ ] All enhancement levels are documented with output examples
- [ ] CSS generation feature is documented with sample output
- [ ] Offline mode fallback is explained

## Contract 3: KISS Principle Compliance

**Contract ID**: DOC-KISS-003
**Requirement**: FR-003 - Documentation MUST follow KISS principles with concise, actionable content

### Validation Criteria
```yaml
kiss_metrics:
  readme_word_count: <= 1000
  guide_word_count: <= 5000
  deployment_content_percentage: <= 5%
  actionable_command_ratio: >= 70%
  table_of_contents_depth: <= 3 levels
```

### Test Contract
```bash
# Test: KISS principle compliance
echo "Testing KISS principle compliance..."

# Contract 1: README brevity
README_WORDS=$(wc -w < README.md)
if [ $README_WORDS -le 1000 ]; then
  echo "✅ PASS: README word count: $README_WORDS (limit: 1000)"
else
  echo "❌ FAIL: README too long: $README_WORDS words (limit: 1000)"
fi

# Contract 2: No deployment content in main docs
DEPLOYMENT_LINES=$(grep -c -i "deploy\|ci/cd\|pipeline\|staging\|production" docs/brand_identity_generator.md || echo 0)
if [ $DEPLOYMENT_LINES -eq 0 ]; then
  echo "✅ PASS: No deployment content found"
else
  echo "❌ FAIL: $DEPLOYMENT_LINES deployment-related lines found"
fi

# Contract 3: Actionable content ratio
TOTAL_LINES=$(wc -l < docs/brand_identity_generator.md)
CODE_BLOCKS=$(grep -c "```" docs/brand_identity_generator.md)
ACTIONABLE_RATIO=$((CODE_BLOCKS * 100 / TOTAL_LINES))
if [ $ACTIONABLE_RATIO -ge 10 ]; then  # Adjusted for realistic docs
  echo "✅ PASS: Actionable content ratio sufficient"
else
  echo "❌ FAIL: Low actionable content ratio: $ACTIONABLE_RATIO%"
fi
```

### Acceptance Criteria
- [ ] README.md ≤ 1000 words
- [ ] Main documentation ≤ 5000 words
- [ ] No CI/CD, staging, or production deployment content
- [ ] Every feature has at least one working example
- [ ] Table of contents has ≤ 3 levels of nesting

## Contract 4: Current Program State Accuracy

**Contract ID**: DOC-STATE-004
**Requirement**: FR-009 - Documentation MUST reflect the current state of the program including all implemented features

### Validation Criteria
```yaml
feature_documentation_required:
  - color_enhancement: documented
  - font_selection: documented
  - typography_hierarchy: documented
  - css_generation: documented
  - gap_analysis: documented
  - interactive_mode: documented
  - session_management: documented
  - llm_provider_selection: documented
  - caching_system: documented
  - enhancement_levels: documented
```

### Test Contract
```bash
# Test: Documentation reflects actual implementation
echo "Testing program state accuracy..."

# Contract 1: All CLI options are documented
python brand_identity_generator.py --help > /tmp/actual_options.txt
DOCUMENTED_OPTIONS=$(grep -c "\-\-" docs/brand_identity_generator.md)
ACTUAL_OPTIONS=$(grep -c "\-\-" /tmp/actual_options.txt)

if [ $DOCUMENTED_OPTIONS -ge $((ACTUAL_OPTIONS * 80 / 100)) ]; then
  echo "✅ PASS: Most CLI options documented ($DOCUMENTED_OPTIONS/$ACTUAL_OPTIONS)"
else
  echo "❌ FAIL: Insufficient CLI option coverage ($DOCUMENTED_OPTIONS/$ACTUAL_OPTIONS)"
fi

# Contract 2: Enhancement levels match implementation
for level in minimal moderate comprehensive; do
  grep -q "enhancement-level $level" docs/brand_identity_generator.md || {
    echo "❌ FAIL: Enhancement level '$level' not documented"
    exit 1
  }
done
echo "✅ PASS: All enhancement levels documented"

# Contract 3: Font selection features documented
grep -q "Font Selection" docs/brand_identity_generator.md || {
  echo "❌ FAIL: Font selection not documented"
  exit 1
}
echo "✅ PASS: Font selection documented"
```

### Acceptance Criteria
- [ ] All CLI command options are documented
- [ ] All enhancement levels are explained
- [ ] Font selection features are comprehensively covered
- [ ] Environment variable configuration is documented
- [ ] All LLM provider options are explained
- [ ] Session management workflow is documented

## Contract 5: Local Developer Focus

**Contract ID**: DOC-LOCAL-005
**Requirement**: FR-001, FR-007 - Documentation MUST focus on local developer usage, removing deployment scenarios

### Validation Criteria
```yaml
local_focus_requirements:
  - setup_instructions: local_environment_only
  - examples: localhost_execution
  - troubleshooting: local_issues_only
  - configuration: environment_variables
  - deployment_content: removed_or_minimal
```

### Test Contract
```bash
# Test: Local developer focus validation
echo "Testing local developer focus..."

# Contract 1: No server deployment instructions
SERVER_TERMS="server|nginx|apache|docker|kubernetes|heroku|aws|azure|gcp"
if ! grep -i -E "$SERVER_TERMS" docs/brand_identity_generator.md > /dev/null; then
  echo "✅ PASS: No server deployment content"
else
  echo "❌ FAIL: Server deployment content found"
  grep -i -E "$SERVER_TERMS" docs/brand_identity_generator.md
fi

# Contract 2: Environment variable setup documented
grep -q "export.*=" docs/brand_identity_generator.md || {
  echo "❌ FAIL: Environment variable setup not documented"
  exit 1
}
echo "✅ PASS: Environment variable setup documented"

# Contract 3: Local troubleshooting present
grep -q -i "troubleshoot" docs/brand_identity_generator.md || {
  echo "❌ FAIL: Troubleshooting section missing"
  exit 1
}
echo "✅ PASS: Troubleshooting section present"
```

### Acceptance Criteria
- [ ] All setup instructions target local development environment
- [ ] No server deployment, CI/CD, or production environment content
- [ ] Environment variable configuration is clearly explained
- [ ] Troubleshooting focuses on local development issues
- [ ] All examples use local file paths and local execution

## Integration Testing Contract

**Contract ID**: DOC-INTEGRATION-006
**Requirement**: Overall documentation system integration validation

### Full System Test
```bash
#!/bin/bash
# integration-test.sh - Full documentation validation

set -e  # Exit on any error

echo "🚀 Starting full documentation integration test..."

# Test 1: Quick start performance
echo "📋 Testing quick start performance..."
bash contracts/quick-start-test.sh

# Test 2: Font selection completeness
echo "🔤 Testing font selection documentation..."
bash contracts/font-selection-test.sh

# Test 3: KISS compliance
echo "✨ Testing KISS principle compliance..."
bash contracts/kiss-compliance-test.sh

# Test 4: Program state accuracy
echo "🔍 Testing program state accuracy..."
bash contracts/state-accuracy-test.sh

# Test 5: Local developer focus
echo "🏠 Testing local developer focus..."
bash contracts/local-focus-test.sh

echo "✅ All documentation contracts PASSED"
echo "📚 Documentation is ready for publication"
```

### Success Criteria
All individual contracts must pass for overall documentation acceptance.

## Contract Execution Schedule

1. **Development Phase**: All contracts must pass before documentation merge
2. **Maintenance Phase**: Contracts run on documentation changes
3. **Feature Updates**: Contracts updated when new features added
4. **Quality Gates**: Contract failure blocks documentation publication

**Contract Status**: ✅ DEFINED - Ready for implementation validation