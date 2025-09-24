# Quickstart: PRD Enhancer Program

**Date**: 2025-09-23
**Feature**: 013-prd-enhancer-program

## Quick Start Guide

### Prerequisites
- Python 3.11+ installed
- API key for Claude (Anthropic) set in environment

### Installation
```bash
# Navigate to agent directory
cd agents/prd_enhancer

# Install dependencies
pip install pydantic>=2 pydantic-ai markdown

# Set environment variable
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Basic Usage

#### 1. Enhance a PRD file
```bash
# Basic usage
python prd_enhancer.py sample_prd.md

# With custom output file
python prd_enhancer.py input.md --output enhanced_input.md

# Enable LLM processing (disabled by default)
python prd_enhancer.py input.md --model-enabled

# Dry run mode (show what would be done)
python prd_enhancer.py input.md --dry-run
```

#### 2. Self-check and validation
```bash
# Validate configuration and environment
python prd_enhancer.py selfcheck

# Print JSON schemas
python prd_enhancer.py print-schemas

# Health check mode
python prd_enhancer.py selfcheck --healthcheck
```

### Expected Outputs

#### Console Output
```
🔍 Pass 1: Found 8 ambiguities via LLM
✂️ Pass 2: Cut 15 of 20 features (keeping only essential 5)
✅ Pass 3: Skipped (complexity already <30)
📊 Complexity score reduced from 85 to 28
✅ Enhanced PRD saved to sample_prd_enhanced.md
```

#### Enhanced PRD File
- Original PRD with ambiguities replaced by specific metrics
- Feature list reduced to maximum 5 core features
- "Not doing" list with 2x more items than "doing" list
- Complexity score reduced by >30%
- Fits within 3 pages

#### JSON Output (if --json flag used)
```json
{
  "meta": {
    "agent": "prd_enhancer",
    "version": "1.0.0",
    "trace_id": "uuid-here",
    "ts": "2025-09-23T10:30:00Z",
    "cost": {"tokens_in": 450, "tokens_out": 120, "usd": 0.02}
  },
  "output": {
    "complexity_score": 28,
    "core_features": [...],
    "not_doing": [...],
    "ambiguities_found": [...],
    "enhanced_prd": "# Enhanced PRD Content..."
  }
}
```

### Test Scenarios

#### 1. Smoke Test
```bash
# Create minimal test PRD
echo "# Test PRD\nWe need a fast user-friendly system." > test.md

# Should complete in <2 seconds
time python prd_enhancer.py test.md
```

#### 2. Ambiguity Detection Test
```bash
# Create PRD with vague terms
cat > ambiguous.md << EOF
# Feature Request
We need a scalable, user-friendly, and fast system that is reliable.
EOF

# Should detect 4 ambiguous terms
python prd_enhancer.py ambiguous.md --verbose
```

#### 3. Feature Reduction Test
```bash
# Create PRD with many features
cat > many_features.md << EOF
# Big PRD
Features needed:
1. User registration
2. Login system
3. Dashboard
4. Analytics
5. Reporting
6. Admin panel
7. API endpoints
8. Mobile app
9. Email notifications
10. Search functionality
[...continue to 20 features...]
EOF

# Should reduce to 5 core features
python prd_enhancer.py many_features.md
```

#### 4. LLM Fallback Test
```bash
# Disable network/API access
unset ANTHROPIC_API_KEY

# Should use regex fallbacks
python prd_enhancer.py test.md
# Expected: "⚠️ Fallback mode: Results may be less precise"
```

### Configuration

#### Environment Variables
```bash
# Required for LLM features
export ANTHROPIC_API_KEY="your-key"

# Optional overrides
export AGENT_MODEL_TIMEOUT_S=5          # Default: 10
export AGENT_MODEL_MAX_TOKENS=500       # Default: 1000
export AGENT_LOG_LEVEL=DEBUG           # Default: INFO
```

#### Config File (optional)
```yaml
# config.yaml
model:
  enabled: false
  provider: "anthropic"
  name: "claude-3-haiku"
  timeout_s: 10
  max_tokens: 1000

processing:
  max_features: 5
  max_events: 5
  max_ambiguities: 10
```

### Troubleshooting

#### Common Issues

**"Model timeout" error**
```bash
# Increase timeout
python prd_enhancer.py input.md --model-timeout 15
```

**"Budget exceeded" error**
```bash
# Use smaller input or disable LLM
python prd_enhancer.py input.md --model-disabled
```

**"Invalid markdown" error**
```bash
# Validate markdown syntax first
python prd_enhancer.py input.md --validate-only
```

#### Debug Mode
```bash
# Enable detailed logging
python prd_enhancer.py input.md --log-level DEBUG

# Show processing steps
python prd_enhancer.py input.md --verbose --dry-run
```

### Integration Examples

#### CI/CD Pipeline
```yaml
# .github/workflows/prd-validation.yml
- name: Enhance PRD
  run: |
    python agents/prd_enhancer/prd_enhancer.py docs/prd.md
    git diff --exit-code || echo "PRD needs enhancement"
```

#### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
for file in $(git diff --cached --name-only | grep '\.md$'); do
  python agents/prd_enhancer/prd_enhancer.py "$file" --validate-only
done
```

### Performance Expectations

| Input Size | Processing Time | Memory Usage |
|------------|----------------|--------------|
| < 500 words | < 2 seconds | < 50 MB |
| 500-2000 words | 2-5 seconds | < 100 MB |
| 2000+ words | 5-10 seconds | < 200 MB |

### Success Criteria Validation

After running the enhancer, verify:
- ✅ Enhanced PRD is shorter than original
- ✅ Complexity score decreased by >30% (for complex PRDs)
- ✅ Maximum 5 features in output
- ✅ "Not doing" list has 2x "doing" items
- ✅ All vague terms replaced with specific metrics
- ✅ Output fits on 3 pages or less