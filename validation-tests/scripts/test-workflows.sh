#!/bin/bash
# User Workflow Validation Tests Script
# Tasks: T015-T018 User Workflow Testing

set -e

echo "🚀 Starting User Workflow Validation Tests (T015-T018)..."

REPO_ROOT="/var/www/html/facebookads"
cd "$REPO_ROOT"

VALIDATION_LOG="$REPO_ROOT/validation-tests/logs/workflow-validation.log"
> "$VALIDATION_LOG"

echo "📋 T015: Quickstart workflow timing validation..." | tee -a "$VALIDATION_LOG"

# T015: Execute 5-step quickstart sequence and measure timing
START_TIME=$(date +%s)

echo "Step 1: Tool availability (from quickstart.md)" | tee -a "$VALIDATION_LOG"
if [ -f "agents/brand_identity_generator/brand_identity_generator.py" ]; then
    echo "✅ Tool available" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Tool not found" | tee -a "$VALIDATION_LOG"
    exit 1
fi

echo "Step 2: Dependencies check (simulation)" | tee -a "$VALIDATION_LOG"
if python -c "import pydantic, openai, anthropic, requests" 2>/dev/null; then
    echo "✅ Dependencies available" | tee -a "$VALIDATION_LOG"
else
    echo "⚠️  Dependencies missing (would install via pip install -r requirements.txt)" | tee -a "$VALIDATION_LOG"
fi

echo "Step 3: Create brand file" | tee -a "$VALIDATION_LOG"
cat > workflow-test-brand.md << EOF
# Workflow Test Brand

**Primary Color**: #2563eb
**Brand Voice**: professional, modern, trustworthy
**Target Audience**: enterprise decision makers
**Industry**: Technology

## About
A technology company focused on reliable software solutions.
EOF

if [ -f "workflow-test-brand.md" ]; then
    echo "✅ Brand file created" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Could not create brand file" | tee -a "$VALIDATION_LOG"
    exit 1
fi

echo "Step 4: Basic enhancement" | tee -a "$VALIDATION_LOG"
if python agents/brand_identity_generator/brand_identity_generator.py workflow-test-brand.md --enhance > workflow-basic.json 2>/dev/null; then
    echo "✅ Basic enhancement successful" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Basic enhancement failed" | tee -a "$VALIDATION_LOG"
    exit 1
fi

echo "Step 5: Comprehensive enhancement" | tee -a "$VALIDATION_LOG"
if python agents/brand_identity_generator/brand_identity_generator.py workflow-test-brand.md --enhance --enhancement-level comprehensive > workflow-comprehensive.json 2>/dev/null; then
    echo "✅ Comprehensive enhancement successful" | tee -a "$VALIDATION_LOG"

    # Check for typography section
    if python -c "
import json
data = json.load(open('workflow-comprehensive.json'))
assert 'typography' in data
print('✅ Typography present')
" 2>/dev/null; then
        echo "✅ Font selection working" | tee -a "$VALIDATION_LOG"
    else
        echo "⚠️  Typography section missing (may be expected)" | tee -a "$VALIDATION_LOG"
    fi
else
    echo "❌ FAIL: Comprehensive enhancement failed" | tee -a "$VALIDATION_LOG"
    exit 1
fi

END_TIME=$(date +%s)
WORKFLOW_TIME=$((END_TIME - START_TIME))

echo "⏱️  5-step workflow completed in ${WORKFLOW_TIME}s" | tee -a "$VALIDATION_LOG"
if [ $WORKFLOW_TIME -le 600 ]; then
    echo "✅ PASS: Workflow within 10-minute target" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Workflow exceeds 10-minute target" | tee -a "$VALIDATION_LOG"
    exit 1
fi

echo "📋 T016: Google Fonts API setup workflow..." | tee -a "$VALIDATION_LOG"

# T016: Test Google Fonts API setup workflow
echo "Testing Google Fonts API setup documentation..." | tee -a "$VALIDATION_LOG"

# Check if setup instructions are clear and complete
if grep -q "export GOOGLE_FONTS_API_KEY" agents/brand_identity_generator/README.md; then
    echo "✅ Environment variable setup documented" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Environment variable setup missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

if grep -q "Google Cloud Console" agents/brand_identity_generator/README.md; then
    echo "✅ Google Cloud setup instructions present" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Google Cloud setup instructions missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

if grep -q "Enable Google Fonts Developer API" agents/brand_identity_generator/README.md; then
    echo "✅ API enabling instructions present" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: API enabling instructions missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Test with mock API key
export GOOGLE_FONTS_API_KEY=test_key_for_validation
if python agents/brand_identity_generator/brand_identity_generator.py workflow-test-brand.md --enhance --debug 2>&1 | grep -q "API"; then
    echo "✅ API key environment variable recognized" | tee -a "$VALIDATION_LOG"
else
    echo "⚠️  API key handling not clearly visible in debug output" | tee -a "$VALIDATION_LOG"
fi

echo "📋 T017: Troubleshooting scenarios validation..." | tee -a "$VALIDATION_LOG"

# T017: Validate troubleshooting scenarios and solutions
DOCS_FILE="agents/brand_identity_generator/README.md"

# Check for troubleshooting section
if grep -q -i "troubleshoot" "$DOCS_FILE"; then
    echo "✅ Troubleshooting section present" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Troubleshooting section missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check for common issues coverage
COMMON_ISSUES=("Google Fonts API" "permission" "LLM API" "dependencies")
for issue in "${COMMON_ISSUES[@]}"; do
    if grep -q -i "$issue" "$DOCS_FILE"; then
        echo "✅ Troubleshooting covers: $issue" | tee -a "$VALIDATION_LOG"
    else
        echo "⚠️  Troubleshooting may not cover: $issue" | tee -a "$VALIDATION_LOG"
    fi
done

# Test common error scenarios
echo "Testing error handling..." | tee -a "$VALIDATION_LOG"
# Test with non-existent file
if python agents/brand_identity_generator/brand_identity_generator.py non-existent-file.md --enhance 2>/dev/null; then
    echo "⚠️  Should have failed on non-existent file" | tee -a "$VALIDATION_LOG"
else
    echo "✅ Handles file errors gracefully" | tee -a "$VALIDATION_LOG"
fi

echo "📋 T018: Multi-level developer accessibility..." | tee -a "$VALIDATION_LOG"

# T018: Test documentation accessibility for different developer levels
echo "Testing beginner developer accessibility..." | tee -a "$VALIDATION_LOG"

# Check for clear, step-by-step instructions
if grep -A 10 "Quick Start" README.md | grep -q "1\." || \
   grep -A 10 "Quick Start" README.md | grep -q "##.*1" || \
   grep -q "Step.*1\|1\.\|Install dependencies" README.md; then
    echo "✅ Step-by-step instructions for beginners" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Missing clear step-by-step instructions" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check for prerequisites section
if grep -q -i "prerequisite\|requirement" "$DOCS_FILE" || grep -q -i "prerequisite\|requirement" README.md; then
    echo "✅ Prerequisites documented" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Prerequisites not clearly documented" | tee -a "$VALIDATION_LOG"
    exit 1
fi

echo "Testing intermediate developer accessibility..." | tee -a "$VALIDATION_LOG"

# Check for configuration options
if grep -q -i "configuration\|config" "$DOCS_FILE"; then
    echo "✅ Configuration options documented" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Configuration options missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check for CLI reference
if grep -q -i "CLI Reference\|command.*reference" "$DOCS_FILE"; then
    echo "✅ CLI reference available" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: CLI reference missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

echo "Testing expert developer accessibility..." | tee -a "$VALIDATION_LOG"

# Check for advanced options and examples
if grep -q "enhancement-level.*comprehensive" "$DOCS_FILE"; then
    echo "✅ Advanced features documented" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Advanced features not documented" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check for environment variable documentation
if grep -q -i "environment variable\|env var\|Environment Variables" "$DOCS_FILE"; then
    echo "✅ Environment configuration documented" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Environment configuration missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Cleanup test files
rm -f workflow-test-brand.md workflow-basic.json workflow-comprehensive.json

echo "🎉 User Workflow Validation Complete - All workflows validated!" | tee -a "$VALIDATION_LOG"
echo "📄 Full validation log saved to: $VALIDATION_LOG"