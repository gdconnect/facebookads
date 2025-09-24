# PRD Enhancer Agent - Usage Guide

## Overview

The PRD Enhancer Agent is a single-file Python application that enhances Product Requirements Documents (PRDs) by detecting ambiguities, reducing scope to core features, and providing clear specifications.

## Installation

```bash
# Navigate to agent directory
cd agents/prd_enhancer

# Install dependencies
pip install -r requirements.txt

# Set environment variable (optional - works offline with fallbacks)
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Basic Usage

### Process a PRD File

```bash
# Basic usage
python prd_enhancer.py sample_prd.md

# With custom output file
python prd_enhancer.py input.md --output enhanced_input.md

# Enable LLM processing (disabled by default for cost control)
python prd_enhancer.py input.md --model-enabled

# JSON output format
python prd_enhancer.py input.md --json

# Verbose output with details
python prd_enhancer.py input.md --verbose

# Dry run (show what would be done)
python prd_enhancer.py input.md --dry-run
```

### Utility Commands

```bash
# Check environment and dependencies
python prd_enhancer.py selfcheck

# Display JSON schemas
python prd_enhancer.py print-schemas

# Help
python prd_enhancer.py --help
```

## Output

The agent produces several types of output:

### 1. Enhanced PRD File
- Original PRD with ambiguous terms replaced by specific metrics
- Feature list reduced to maximum 5 core features (if input has >7 features)
- "Not doing" list with 2x more items than "doing" list
- Processing metadata

### 2. Console Output
```
🔍 Found 7 ambiguities
✂️  Selected 5 core features
📊 Complexity score: 42
⏱️  Processing time: 1.23s
✅ Enhanced PRD saved to input_enhanced.md
```

### 3. JSON Output (with --json flag)
```json
{
  "complexity_score": 42,
  "core_features": [
    {
      "name": "User Authentication",
      "priority_score": 4.5,
      "value_score": 9,
      "effort_score": 2
    }
  ],
  "not_doing": [
    "Real-time notifications",
    "Advanced analytics"
  ],
  "ambiguities_found": [
    {
      "term": "fast",
      "problem": "Vague performance requirement",
      "suggested_fix": "Response time <200ms",
      "confidence": 0.9,
      "source": "regex"
    }
  ],
  "enhanced_prd": "# Enhanced PRD Content...",
  "processing_stats": {
    "processing_time": 1.23,
    "passes_executed": ["pass1_ambiguity"],
    "tokens_used": 0,
    "fallbacks_used": ["regex_ambiguity_detection"]
  }
}
```

## Features

### Ambiguity Detection
Identifies vague terms and suggests specific metrics:
- "fast" → "Response time <200ms"
- "scalable" → "Handles 1000 concurrent users"
- "user-friendly" → "Task completed in 3 clicks"
- "secure" → "AES-256 encryption, OAuth 2.0"
- "reliable" → "99.9% availability"

### Feature Reduction
- Reduces 20+ features down to 5 core features
- Uses ROI-based prioritization (value/effort ratio)
- Only features with priority score >2.0 are selected
- Keyword-based scoring for fallback mode

### Scope Clarification
- Generates "not doing" list with 2x items of core features
- Minimum 10 items in not-doing list
- Includes cut features and common exclusions

### Performance Goals
- Simple PRDs (<500 words): <2 seconds
- Complex PRDs: <10 seconds
- Complexity reduction: >30% for complex PRDs
- Enhanced PRD fits within 3 pages

## Configuration

### Environment Variables
```bash
# Optional - enables LLM features
export ANTHROPIC_API_KEY="your-key"

# Optional overrides
export AGENT_MODEL_TIMEOUT_S=5          # Default: 10
export AGENT_MODEL_MAX_TOKENS=500       # Default: 1000
export AGENT_LOG_LEVEL=DEBUG           # Default: INFO
export AGENT_BRAND_TOKEN=custom        # Default: default
```

### Command Line Options
```bash
--output PATH               # Custom output file path
--model-enabled            # Enable LLM processing (disabled by default)
--model-timeout SECONDS    # LLM timeout (default: 10)
--dry-run                  # Show what would be done
--json                     # Output in JSON format
--verbose                  # Detailed logging
--log-level LEVEL          # DEBUG, INFO, WARN, ERROR
```

## Operating Modes

### 1. Fallback Mode (Default)
- Uses regex patterns for ambiguity detection
- Keyword scoring for feature prioritization
- Works completely offline
- Fast processing (<2 seconds for most PRDs)

### 2. LLM Mode (--model-enabled)
- Uses Claude-3-haiku via PydanticAI
- More intelligent ambiguity detection
- Better feature analysis
- Requires API key and internet connection
- Budget-controlled (1000 tokens max, $0.05 per PRD)

## Test Scenarios

### Smoke Test
```bash
echo "# Test PRD\nWe need a fast user-friendly system." > test.md
python prd_enhancer.py test.md
# Should complete in <2 seconds
```

### Ambiguity Detection Test
```bash
cat > ambiguous.md << EOF
# Feature Request
We need a scalable, user-friendly, and fast system that is reliable.
EOF
python prd_enhancer.py ambiguous.md --verbose
# Should detect 4 ambiguous terms
```

### Feature Reduction Test
```bash
# Create PRD with 20+ features
python prd_enhancer.py examples/sample_complex_prd.md --verbose
# Should reduce to 5 core features
```

## Troubleshooting

### Common Issues

**"Model timeout" error**
```bash
# Increase timeout or disable LLM
python prd_enhancer.py input.md --model-timeout 15
python prd_enhancer.py input.md  # Uses fallback mode
```

**"File not found" error**
```bash
# Check file path and extension
ls -la *.md
python prd_enhancer.py document.md  # Must be .md or .markdown
```

**No ambiguities found**
```bash
# Check that PRD contains vague terms
python prd_enhancer.py input.md --verbose --log-level DEBUG
```

### Debug Mode
```bash
# Enable detailed logging
python prd_enhancer.py input.md --log-level DEBUG --verbose

# Check self-diagnostic
python prd_enhancer.py selfcheck
```

## Integration

### CI/CD Pipeline
```yaml
# .github/workflows/prd-validation.yml
- name: Enhance PRD
  run: |
    python agents/prd_enhancer/prd_enhancer.py docs/prd.md
    git diff --exit-code || echo "PRD needs enhancement"
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
for file in $(git diff --cached --name-only | grep '\.md$'); do
  python agents/prd_enhancer/prd_enhancer.py "$file" --dry-run
done
```

## Performance Expectations

| Input Size | Processing Time | Memory Usage | Features Detected |
|------------|----------------|--------------|------------------|
| < 500 words | < 2 seconds | < 50 MB | Regex patterns only |
| 500-2000 words | 2-5 seconds | < 100 MB | Full analysis |
| 2000+ words | 5-10 seconds | < 200 MB | Complex PRDs |

## Success Criteria

After running the enhancer, verify:
- ✅ Enhanced PRD is shorter than original
- ✅ Complexity score decreased by >30% (for complex PRDs)
- ✅ Maximum 5 features in output
- ✅ "Not doing" list has 2x "doing" items
- ✅ All vague terms replaced with specific metrics
- ✅ Output fits on 3 pages or less

## Architecture

### Single-File Design
- Constitutional compliance: single Python file
- All dependencies in requirements.txt
- Self-contained with fallback modes
- Structured logging to STDERR
- JSON schema validation

### Constitutional Features
- Contract-first design with Pydantic models
- Budget enforcement and cost tracking
- Defensive programming patterns
- Comprehensive error handling
- Structured logging per Article XVIII

## License

Proprietary - Internal use only