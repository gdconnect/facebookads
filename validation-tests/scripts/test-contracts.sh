#!/bin/bash
# Contract Validation Tests Script
# Tasks: T010-T014 Contract Testing

set -e

echo "🚀 Starting Contract Validation Tests (T010-T014)..."

REPO_ROOT="/var/www/html/facebookads"
cd "$REPO_ROOT"

VALIDATION_LOG="$REPO_ROOT/validation-tests/logs/contract-validation.log"
> "$VALIDATION_LOG"

echo "📋 T010: Font Selection Documentation Completeness (DOC-FS-002)..." | tee -a "$VALIDATION_LOG"

# T010: Font selection documentation validation
DOCS_FILE="agents/brand_identity_generator/README.md"

# Check required font selection sections
REQUIRED_FONT_SECTIONS=("Google Fonts API Setup" "Font Selection & Typography" "Enhancement Levels")
for section in "${REQUIRED_FONT_SECTIONS[@]}"; do
    if grep -q "$section" "$DOCS_FILE"; then
        echo "✅ PASS: Font section '$section' documented" | tee -a "$VALIDATION_LOG"
    else
        echo "❌ FAIL: Font section '$section' missing" | tee -a "$VALIDATION_LOG"
        exit 1
    fi
done

# Check for API key setup instructions
if grep -q "GOOGLE_FONTS_API_KEY" "$DOCS_FILE"; then
    echo "✅ PASS: Google Fonts API key setup documented" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Google Fonts API key setup missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check for enhancement level explanations
ENHANCEMENT_LEVELS=("minimal" "moderate" "comprehensive")
for level in "${ENHANCEMENT_LEVELS[@]}"; do
    if grep -q "enhancement-level $level" "$DOCS_FILE"; then
        echo "✅ PASS: Enhancement level '$level' documented" | tee -a "$VALIDATION_LOG"
    else
        echo "❌ FAIL: Enhancement level '$level' not documented" | tee -a "$VALIDATION_LOG"
        exit 1
    fi
done

echo "📋 T011: KISS Principle Compliance (DOC-KISS-003)..." | tee -a "$VALIDATION_LOG"

# T011: KISS compliance testing
README_WORDS=$(wc -w < README.md)
DOCS_WORDS=$(wc -w < "$DOCS_FILE")

echo "📊 README words: $README_WORDS (limit: 1000)" | tee -a "$VALIDATION_LOG"
echo "📊 Main docs words: $DOCS_WORDS (limit: 5000)" | tee -a "$VALIDATION_LOG"

if [ $README_WORDS -le 1000 ] && [ $DOCS_WORDS -le 5000 ]; then
    echo "✅ PASS: Word count limits met" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Word count limits exceeded" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check deployment content removal
if ! grep -q -i "deploy\|ci/cd\|pipeline\|staging\|production" "$DOCS_FILE" 2>/dev/null; then
    echo "✅ PASS: No deployment content found" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Deployment content still present" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check actionable content ratio
CODE_BLOCKS=$(grep -c '```' "$DOCS_FILE")
TOTAL_LINES=$(wc -l < "$DOCS_FILE")
if [ $TOTAL_LINES -gt 0 ]; then
    ACTIONABLE_RATIO=$((CODE_BLOCKS * 100 / TOTAL_LINES))
    echo "📊 Actionable content ratio: ${ACTIONABLE_RATIO}%" | tee -a "$VALIDATION_LOG"
    if [ $ACTIONABLE_RATIO -ge 5 ]; then  # At least 5% actionable content
        echo "✅ PASS: Sufficient actionable content" | tee -a "$VALIDATION_LOG"
    else
        echo "❌ FAIL: Low actionable content ratio" | tee -a "$VALIDATION_LOG"
        exit 1
    fi
fi

echo "📋 T012: Program State Accuracy (DOC-STATE-004)..." | tee -a "$VALIDATION_LOG"

# T012: Current program state validation
# Check that documented CLI options match actual options
python agents/brand_identity_generator/brand_identity_generator.py --help > /tmp/actual_help.txt 2>/dev/null

DOCUMENTED_OPTIONS=$(grep -c "\-\-" "$DOCS_FILE")
ACTUAL_OPTIONS=$(grep -c "\-\-" /tmp/actual_help.txt)

echo "📊 Documented options: $DOCUMENTED_OPTIONS" | tee -a "$VALIDATION_LOG"
echo "📊 Actual options: $ACTUAL_OPTIONS" | tee -a "$VALIDATION_LOG"

if [ $DOCUMENTED_OPTIONS -ge $((ACTUAL_OPTIONS * 70 / 100)) ]; then
    echo "✅ PASS: Most CLI options documented (≥70% coverage)" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Insufficient CLI option coverage" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check enhancement levels are documented
for level in minimal moderate comprehensive; do
    if grep -q "enhancement-level $level" "$DOCS_FILE"; then
        echo "✅ PASS: Enhancement level '$level' documented" | tee -a "$VALIDATION_LOG"
    else
        echo "❌ FAIL: Enhancement level '$level' missing" | tee -a "$VALIDATION_LOG"
        exit 1
    fi
done

echo "📋 T013: Local Developer Focus (DOC-LOCAL-005)..." | tee -a "$VALIDATION_LOG"

# T013: Local developer focus verification
# Check no server deployment content
SERVER_TERMS="nginx\|apache\|docker\|kubernetes\|heroku\|aws\|azure\|gcp"
if ! grep -i "$SERVER_TERMS" "$DOCS_FILE" > /dev/null 2>&1; then
    echo "✅ PASS: No server deployment content" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Server deployment content found" | tee -a "$VALIDATION_LOG"
    grep -i "$SERVER_TERMS" "$DOCS_FILE" | head -n 3 | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check environment variable documentation
if grep -q "export.*=" "$DOCS_FILE"; then
    echo "✅ PASS: Environment variable setup documented" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Environment variable setup missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check local troubleshooting
if grep -q -i "troubleshoot" "$DOCS_FILE"; then
    echo "✅ PASS: Troubleshooting section present" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Troubleshooting section missing" | tee -a "$VALIDATION_LOG"
    exit 1
fi

echo "📋 T014: Cross-platform validation..." | tee -a "$VALIDATION_LOG"

# T014: Cross-platform documentation validation
# Check for platform-agnostic instructions
if grep -q "Windows\|macOS\|Linux" "$DOCS_FILE"; then
    echo "✅ PASS: Cross-platform considerations mentioned" | tee -a "$VALIDATION_LOG"
else
    echo "⚠️  INFO: No explicit cross-platform mentions (may be acceptable)" | tee -a "$VALIDATION_LOG"
fi

# Check for universal commands (Python-based, platform agnostic)
if grep -q "python agents/brand_identity_generator/brand_identity_generator.py" "$DOCS_FILE"; then
    echo "✅ PASS: Platform-agnostic Python commands used" | tee -a "$VALIDATION_LOG"
else
    echo "❌ FAIL: Python commands not documented" | tee -a "$VALIDATION_LOG"
    exit 1
fi

# Check environment variable syntax (should be cross-platform compatible)
if grep -q "export " "$DOCS_FILE"; then
    echo "✅ PASS: Environment variable syntax documented" | tee -a "$VALIDATION_LOG"
    # Could add Windows syntax check here if needed
fi

rm -f /tmp/actual_help.txt

echo "🎉 Contract Validation Tests Complete - All contracts passed!" | tee -a "$VALIDATION_LOG"
echo "📄 Full validation log saved to: $VALIDATION_LOG"