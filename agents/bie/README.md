# Business Idea Evaluator (BIE)

Transform unstructured business ideas written in Markdown into structured, evaluated, and actionable insights.

## Quick Start

```bash
# Basic evaluation (JSON output)
python bie.py evaluate my_idea.md

# Enhanced markdown output with emojis and checkboxes
python bie.py evaluate my_idea.md --output markdown

# Both JSON and markdown output
python bie.py evaluate my_idea.md --output both

# Compare multiple ideas (2-10 files)
python bie.py compare idea1.md idea2.md idea3.md

# Compare with markdown table output
python bie.py compare idea1.md idea2.md --output markdown

# Validate system
python bie.py selfcheck
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Optional: OpenAI API key for enhanced LLM-powered analysis

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# OPENAI_API_KEY=your-key-here  # Optional
```

## Usage

### Input Format

Create a markdown file with your business idea:

```markdown
# My Business Idea

## Problem
Describe the problem you're solving...

## Solution
Describe your proposed solution...

## Target Customer
Who will use your solution?

## Revenue Model
How will you make money?

## Technical Approach
How will you build it?

## Similar Companies
What companies are similar to your idea?
```

### Output

The tool provides:
- **Scalability Score (0-100)**: Growth potential and scaling efficiency
- **Complexity Score (0-100)**: Implementation difficulty (lower is better)
- **Risk Score (0-100)**: Business risk level (lower is better)
- **Overall Grade (A-F)**: Combined assessment
- **Actionable Insights**: Critical questions, quick wins, red flags, next steps
- **Blindspot Detection**: Catches common startup pitfalls like "monetization later" and "perfect before launch" traps
- **Enhanced Markdown**: Grade in title, emoji sections, checkbox action items, visual score indicators

### Output Formats

**JSON (default)**: Structured data with complete evaluation details
**Markdown**: Human-readable format with:
- Grade in title: `# [Idea Name] - Grade: B (72/100)`
- Emoji sections: 📊 Summary, 💡 Original, 🎯 Refined, 🚨 Red Flags, ✅ Quick Wins
- Checkbox action items: `- [ ] Research competitors`
- Visual indicators: ✅ good, ⚠️ warning, ❌ poor

### Grade Thresholds
- **A**: Scalability > 80, Complexity < 30, Risk < 30
- **B**: Scalability > 60, Complexity < 50, Risk < 50
- **C**: Scalability > 40, Complexity < 70, Risk < 70
- **D**: Scalability > 20, Complexity < 90, Risk < 90
- **F**: Everything else

### Comparison Features

Compare 2-10 business ideas with:
- **Ranked comparison table** showing relative performance
- **Strengths/weaknesses analysis** for each idea
- **Clear recommendation** on which idea to pursue
- **Grade distribution summary**

## Constitutional Compliance

This tool follows the Schema-First Empire Python Single-File Constitution:
- ✅ Single-file implementation in `bie.py`
- ✅ Contract-first with Pydantic v2 models
- ✅ Decision tables before LLM calls
- ✅ Structured JSONL logging to STDERR
- ✅ Model disabled by default with fallback logic
- ✅ Comprehensive testing framework

## Development

### Run Tests
```bash
pytest tests/
```

### Code Quality
```bash
ruff check .
black .
mypy --strict bie.py
```

### Generate Schemas
```bash
python bie.py print-schemas > schemas.json
```

## Configuration

Environment variables (optional):
- `BIE_MODEL_ENABLED=false` - Enable/disable LLM calls
- `BIE_MODEL_NAME=gpt-4-turbo` - LLM model to use
- `BIE_TEMPERATURE=0.3` - Model temperature
- `BIE_MAX_TOKENS=2000` - Maximum tokens per call
- `BIE_TIMEOUT=120` - Timeout in seconds

## Performance

- **Runtime**: <2 minutes end-to-end evaluation
- **Memory**: <50MB process footprint
- **Tokens**: ~10K tokens per evaluation (when LLM enabled)
- **Cost**: <$0.15 per evaluation (GPT-4 pricing)
