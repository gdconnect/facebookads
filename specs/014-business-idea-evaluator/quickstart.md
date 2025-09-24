# Business Idea Evaluator - Quickstart Guide

## Overview
The Business Idea Evaluator (BIE) transforms unstructured business ideas written in Markdown into structured, evaluated, and actionable insights. This guide demonstrates the complete workflow from idea to evaluation.

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- OpenAI API key (or other supported LLM provider)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd <repository-root>

# Install dependencies
pip install -r requirements.txt

# Set up environment
export OPENAI_API_KEY="your-api-key-here"
export BIE_MODEL="gpt-4-turbo"  # optional
export BIE_TEMPERATURE="0.3"   # optional
```

### Verify Installation
```bash
python agents/bie/bie.py selfcheck
```

## Quick Start: Evaluate Your First Idea

### Step 1: Create Business Idea File
Create a markdown file with your business idea:

```markdown
# My Awesome SaaS Idea

## Problem
Small businesses struggle to manage their social media presence across multiple platforms. They don't have time to create content, schedule posts, or track engagement.

## Solution
An AI-powered social media management platform that automatically generates content, schedules posts at optimal times, and provides engagement analytics.

## Target Customer
Small business owners (1-50 employees) in retail, restaurants, and professional services.

## Revenue Model
Monthly subscription tiers: Basic ($29), Pro ($79), Enterprise ($199).

## Technical Approach
Web application with social media API integrations, AI content generation, and analytics dashboard.

## Similar Companies
Like Buffer, but with AI-generated content and automated optimization.
```

Save this as `my_idea.md`.

### Step 2: Run Basic Evaluation
```bash
python agents/bie/bie.py evaluate my_idea.md
```

Expected output: JSON evaluation with scores, insights, and recommendations.

### Step 3: Get Human-Readable Output
```bash
python agents/bie/bie.py evaluate my_idea.md --output markdown > my_idea_evaluated.md
```

This creates an enhanced markdown file with:
- Original idea preserved
- Refined business model analysis
- Critical questions to answer
- Red flags and quick wins
- Recommended 30-day MVP
- Similar successful companies

## Testing Different Scenarios

### High-Score Example (Expected Grade: A-B)
Create `platform_idea.md`:
```markdown
# Developer Tool Marketplace

## Problem
Developers waste time building common utilities instead of focusing on core business logic.

## Solution
A marketplace for pre-built, well-tested code components with easy integration and licensing.

## Target Customer
Professional developers and engineering teams at tech companies.

## Revenue Model
Transaction fees (10%) + premium subscriptions for advanced features.

## Technical Approach
Web platform with package registry, automated testing, and integration tools.
```

### Low-Score Example (Expected Grade: D-F)
Create `restaurant_idea.md`:
```markdown
# Gourmet Burger Restaurant

## Problem
People want high-quality burgers but can't find good options nearby.

## Solution
Open a restaurant serving gourmet burgers with locally-sourced ingredients.

## Target Customer
Food enthusiasts in our local neighborhood.

## Revenue Model
Direct sales of food and beverages.
```

### Compare Multiple Ideas
```bash
python agents/bie/bie.py compare platform_idea.md restaurant_idea.md my_idea.md
```

## Understanding the Output

### Scoring System
- **Scalability Score (0-100)**: Growth potential and scaling efficiency
- **Complexity Score (0-100)**: Implementation difficulty (lower is better)
- **Risk Score (0-100)**: Business risk level (lower is better)
- **Overall Grade (A-F)**: Combined assessment

### Grade Thresholds
- **A**: Scalability > 80, Complexity < 30, Risk < 30
- **B**: Scalability > 60, Complexity < 50, Risk < 50
- **C**: Scalability > 40, Complexity < 70, Risk < 70
- **D**: Scalability > 20, Complexity < 90, Risk < 90
- **F**: Anything else

### Key Insights Sections
- **Critical Questions**: Must be answered before proceeding
- **Red Flags**: Serious concerns requiring attention
- **Quick Wins**: Easy improvements to implement
- **Next Steps**: Concrete actions to take
- **Recommended MVP**: 30-day buildable version

## Advanced Usage

### Custom Model Configuration
```bash
python agents/bie/bie.py evaluate my_idea.md --model claude-3-sonnet --temperature 0.1
```

### Validation Only (No LLM Calls)
```bash
python agents/bie/bie.py validate my_idea.md
```

### Verbose Debugging
```bash
python agents/bie/bie.py evaluate my_idea.md --verbose
```

### Custom Configuration File
Create `bie_config.yaml`:
```yaml
model:
  enabled: true
  provider: "openai"
  name: "gpt-4-turbo"
  temperature: 0.2
  max_tokens: 2000

scoring:
  scalability_weights:
    marginal_cost: 0.35
    automation: 0.25
    network_effects: 0.20
    geographic_reach: 0.15
    platform_potential: 0.05

output:
  default_format: "markdown"
  include_reasoning: true
```

```bash
python agents/bie/bie.py evaluate my_idea.md --config bie_config.yaml
```

## Common Issues & Solutions

### Issue: "No API key found"
**Solution**: Set environment variable
```bash
export OPENAI_API_KEY="your-key-here"
```

### Issue: "Cannot parse business idea"
**Solution**: Ensure your markdown has clear Problem and Solution sections
```markdown
## Problem
[Clear problem statement]

## Solution
[Clear solution description]
```

### Issue: "Evaluation timeout"
**Solution**: Use faster model or increase timeout
```bash
python agents/bie/bie.py evaluate my_idea.md --model gpt-3.5-turbo --timeout 180
```

### Issue: "Low confidence scores"
**Solution**: Provide more detailed business idea with specific examples

## Best Practices

### Writing Effective Business Ideas
1. **Be Specific**: Avoid vague descriptions like "help people" or "make things better"
2. **Include Numbers**: Mention market size, pricing, customer segments
3. **Show Understanding**: Demonstrate knowledge of the problem and market
4. **Be Honest**: Include challenges and limitations you're aware of

### Iterating on Ideas
1. **Start Broad**: Initial evaluation to identify major issues
2. **Address Red Flags**: Fix the most serious concerns first
3. **Answer Critical Questions**: Research and answer key unknowns
4. **Implement Quick Wins**: Easy improvements for better scores
5. **Re-evaluate**: Run the tool again to measure improvement

### Example Iteration Workflow
```bash
# Initial evaluation
python agents/bie/bie.py evaluate idea_v1.md --output markdown > idea_v1_evaluated.md

# Review red flags and critical questions
# Update idea based on insights

# Second evaluation
python agents/bie/bie.py evaluate idea_v2.md --output markdown > idea_v2_evaluated.md

# Compare versions
python agents/bie/bie.py compare idea_v1.md idea_v2.md
```

## Integration Examples

### CI/CD Pipeline Integration
```yaml
# .github/workflows/idea-evaluation.yml
name: Evaluate Business Ideas
on:
  pull_request:
    paths: ['ideas/*.md']

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Evaluate Ideas
      run: |
        for file in ideas/*.md; do
          python agents/bie/bie.py validate "$file"
        done
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Bulk Processing Script
```bash
#!/bin/bash
# evaluate_all.sh
for file in ideas/*.md; do
  echo "Evaluating $file..."
  python agents/bie/bie.py evaluate "$file" --output both
done
```

## Troubleshooting

### Check System Status
```bash
python agents/bie/bie.py selfcheck --healthcheck
```

### View Generated Schemas
```bash
python agents/bie/bie.py print-schemas
```

### Dry Run Mode
```bash
python agents/bie/bie.py dry-run my_idea.md
```

### Log Analysis
```bash
python agents/bie/bie.py evaluate my_idea.md --verbose 2>evaluation.log
grep "ERROR" evaluation.log
```

## Next Steps

1. **Evaluate Your Ideas**: Start with your current business ideas
2. **Compare Alternatives**: Evaluate multiple approaches to the same problem
3. **Iterate and Improve**: Use insights to refine your ideas
4. **Build MVPs**: Focus on recommended 30-day buildable versions
5. **Track Results**: Monitor which predictions prove accurate over time

## Support & Feedback

- **Issues**: Report bugs via GitHub issues
- **Feature Requests**: Suggest improvements via GitHub discussions
- **Documentation**: Contribute to documentation improvements

Remember: This tool provides structured analysis to inform your decisions, but success ultimately depends on execution, market conditions, and factors beyond the scope of this evaluation.