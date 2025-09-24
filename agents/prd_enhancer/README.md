# PRD Enhancer Agent

Transforms vague Product Requirements Documents into specific, actionable specifications.

## Quick Start

```bash
# Setup
git clone <repo>
cd prd_enhancer
pip install -r requirements.txt

# Basic usage (works offline)
python prd_enhancer.py examples/sample_complex_prd.md

# With LLM (needs API key)
export ANTHROPIC_API_KEY="sk-..."
python prd_enhancer.py input.md --model-enabled
```

## What It Does

**Before:** "System should be fast and user-friendly"
**After:** "System should respond in <200ms and complete tasks in 3 clicks"

**Features:**
- **Ambiguity Detection**: Finds vague terms, suggests specific metrics
- **Scope Reduction**: Reduces 20+ features → 5 core features
- **Complexity Scoring**: 0-100 implementation difficulty score
- **LLM + Fallbacks**: Works offline with regex patterns

## Common Commands

```bash
# Process PRD with LLM intelligence
python prd_enhancer.py input.md --model-enabled

# Offline mode (no API needed)
python prd_enhancer.py input.md

# Check setup and environment
python prd_enhancer.py selfcheck

# Run tests
pytest

# See all options
python prd_enhancer.py --help
```

## Testing

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit/           # Component tests
pytest tests/integration/    # End-to-end tests
pytest -m smoke             # Quick tests only
```

## Project Structure

```
prd_enhancer.py          # Main agent (single file, all logic)
tests/
  ├── unit/              # Component tests
  ├── integration/       # End-to-end tests
  └── contract/          # Schema validation
examples/                # Sample PRDs to try
requirements.txt         # Dependencies
```

## Output

The agent produces:
- Enhanced PRD with specific metrics replacing vague terms
- Core features list (max 5 features)
- "Not doing" list with excluded features
- Complexity score and processing stats

## Troubleshooting

**"No API key found"** → Works offline! Use `--model-enabled` only when you have a key
**"Tests failing"** → Check Python 3.10+, run `pip install -r requirements.txt`
**"Slow processing"** → Normal for >2000 words. Use offline mode for speed

## Performance

- **Simple PRDs** (<500 words): <2 seconds
- **Complex PRDs** (>2000 words): <10 seconds
- **Architecture**: Single-file agent, 3-pass processing with fallbacks

## License

Proprietary - Internal use only