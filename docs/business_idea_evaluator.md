# Product Requirements Document: Business Idea Evaluator (BIE)

## Executive Summary

A single-file Python command-line tool that transforms unstructured business ideas written in Markdown into structured, evaluated, and actionable insights. Designed specifically for a web development agency to evaluate and refine digital asset opportunities before committing development resources.

## Core Purpose

**Problem**: Agency developers often pursue digital asset ideas based on technical interest rather than business viability, leading to wasted resources and abandoned projects.

**Solution**: A systematic evaluation pipeline that forces critical thinking, identifies blindspots, and scores ideas on scalability potential - all before writing production code.

## Key Design Principles

1. **Single File Simplicity**: Entire tool in one `.py` file - no complex project structure
2. **Progressive Enhancement**: Each LLM pass adds specific value, building on previous insights
3. **80/20 Focus**: Evaluate the 20% of factors that determine 80% of success
4. **Fast Iteration**: Process should take <2 minutes end-to-end
5. **Human-in-the-Loop**: Tool suggests and questions, human decides

## Technical Architecture

### Dependencies
- `pydantic`: Data validation and schema definition
- `pydantic_ai`: LLM integration and structured extraction
- Python 3.10+ (for modern type hints)
- OpenAI API (or compatible LLM endpoint)

### Core Flow
```
Markdown → Parse → Enrich (Multi-Pass) → Score → Output (JSON/Enhanced MD)
```

## Schema Progression

### Input Schema: Raw Idea Extraction
```python
class RawIdea(BaseModel):
    """First pass: Extract what the human actually wrote"""
    name: str
    problem: str
    solution: str
    target_customer: Optional[str]
    monetization: Optional[str]
    technical_approach: Optional[str]
    inspiration: Optional[str]  # "It's like X for Y"
```

### Enrichment Pass 1: Business Model Decomposition
```python
class BusinessModel(BaseModel):
    """Understand the fundamental business mechanics"""
    value_creation: str  # What value is created?
    value_capture: str   # How is money made?
    unit_economics: str  # Revenue per user - costs
    growth_mechanism: str  # How does it grow?
    competitive_moat: str  # Why won't others copy?
    minimum_viable_scope: str  # Smallest valuable version
```

### Enrichment Pass 2: Scalability Analysis
```python
class ScalabilityFactors(BaseModel):
    """Evaluate growth potential and constraints"""
    marginal_cost_per_customer: str  # Cost to serve N+1
    geographic_constraints: str  # Local/national/global
    automation_potential: int  # 0-100% automatable
    network_effects: str  # How users create value for other users
    platform_potential: bool  # Can others build on top?
    data_compound_value: str  # Does data accumulate advantage?
```

### Enrichment Pass 3: Risk and Reality Check
```python
class RiskAssessment(BaseModel):
    """Identify what could go wrong"""
    startup_costs: Dict[str, float]  # Infrastructure, marketing, legal
    time_to_revenue: str  # Realistic timeline
    key_dependencies: List[str]  # External services, APIs, partners
    biggest_risk: str  # Single greatest threat
    boring_version: str  # Stripped down but profitable version
    why_not_already_dominated: str  # Market inefficiency explanation
```

### Final Output Schema
```python
class EvaluatedIdea(BaseModel):
    """Complete evaluated business idea"""
    raw_idea: RawIdea
    business_model: BusinessModel
    scalability: ScalabilityFactors
    risks: RiskAssessment
    
    # Computed Scores
    scalability_score: int  # 0-100
    complexity_score: int  # 0-100 (lower is better)
    risk_score: int  # 0-100 (lower is better)
    overall_grade: str  # A-F
    
    # Actionable Insights
    critical_questions: List[str]  # Must answer before proceeding
    quick_wins: List[str]  # Easy improvements
    red_flags: List[str]  # Serious concerns
    next_steps: List[str]  # Concrete actions
    similar_successes: List[str]  # Companies that proved model
    recommended_mvp: str  # 30-day buildable version
```

## LLM Decision Table

| Pass | Purpose | Input | Key Instructions | Output |
|------|---------|-------|------------------|--------|
| 1 | Extract | Markdown | "Extract explicit statements only, don't infer" | RawIdea |
| 2 | Decompose | RawIdea | "Think like a business strategist. Identify unit economics." | BusinessModel |
| 3 | Analyze Scale | RawIdea + BusinessModel | "Evaluate like a VC. What prevents infinite scale?" | ScalabilityFactors |
| 4 | Reality Check | All Previous | "Be pessimistic. What will actually break?" | RiskAssessment |
| 5 | Synthesize | All Previous | "Give actionable verdict. Be brutal but constructive." | Final scores + recommendations |

## Scoring Algorithm

### Scalability Score (0-100)
```python
score = weighted_sum(
    marginal_cost: 30%,      # 0 = high cost, 100 = zero cost
    automation: 25%,          # Direct percentage
    network_effects: 20%,     # 0 = none, 100 = viral
    geographic_reach: 15%,    # local=20, national=60, global=100
    platform_potential: 10%   # binary 0 or 100
)
```

### Complexity Score (0-100, lower better)
```python
score = weighted_sum(
    technical_dependencies: 30%,  # Count of external services
    time_to_market: 30%,          # Days / 30
    required_features: 20%,        # Feature count * 10
    regulatory_burden: 20%         # none=0, light=30, heavy=100
)
```

### Risk Score (0-100, lower better)
```python
score = weighted_sum(
    market_risk: 25%,          # Competition and demand uncertainty
    technical_risk: 25%,       # Complexity and dependencies
    financial_risk: 25%,       # Startup costs and runway needed
    execution_risk: 25%        # Team capability and time commitment
)
```

### Overall Grade
- **A**: Scalability > 80, Complexity < 30, Risk < 30
- **B**: Scalability > 60, Complexity < 50, Risk < 50
- **C**: Scalability > 40, Complexity < 70, Risk < 70
- **D**: Scalability > 20, Complexity < 90, Risk < 90
- **F**: Anything else

## Command Line Interface

```bash
# Basic evaluation
python bie.py evaluate idea.md

# Output to JSON
python bie.py evaluate idea.md --output json > evaluated.json

# Enhanced markdown for iteration
python bie.py evaluate idea.md --output markdown > idea_v2.md

# Compare multiple ideas
python bie.py compare idea1.md idea2.md idea3.md

# Quick validation only (fewer LLM calls)
python bie.py validate idea.md

# Specify custom LLM model
python bie.py evaluate idea.md --model gpt-4-turbo

# Verbose mode for debugging
python bie.py evaluate idea.md --verbose
```

## Enhanced Markdown Output Format

```markdown
# [Original Idea Name] - Grade: B (72/100)

## 📊 Summary Scores
- Scalability: 75/100 ✅
- Complexity: 45/100 ⚠️
- Risk: 38/100 ✅

## 💡 Your Original Idea
[Original content preserved]

## 🎯 Refined Business Model
**Value Creation**: [Enhanced description]
**Unit Economics**: [Specific breakdown]
**Growth Engine**: [Clear mechanism]

## ❗ Critical Questions (Answer Before Proceeding)
1. [Specific question about market]
2. [Specific question about competition]
3. [Specific question about technical feasibility]

## 🚨 Red Flags
- ⚠️ [Specific concern]
- ⚠️ [Another concern]

## ✅ Quick Wins
- [ ] [Actionable improvement]
- [ ] [Another improvement]

## 🚀 Recommended MVP (30 days)
[Specific, buildable scope]

## 📈 Similar Success: [Company]
They proved this model by [specific strategy]

## 🔄 Next Iteration Prompts
- Consider: [Alternative approach]
- Research: [Specific unknown]
- Simplify: [Complexity to remove]
```

## JSON Output Format

```json
{
  "name": "Business Idea Name",
  "grade": "B",
  "scores": {
    "scalability": 75,
    "complexity": 45,
    "risk": 38,
    "overall": 72
  },
  "raw_idea": { ... },
  "business_model": { ... },
  "scalability_factors": { ... },
  "risk_assessment": { ... },
  "insights": {
    "critical_questions": [...],
    "quick_wins": [...],
    "red_flags": [...],
    "next_steps": [...],
    "recommended_mvp": "..."
  },
  "metadata": {
    "evaluation_date": "2024-01-15T10:30:00Z",
    "model_used": "gpt-4-turbo",
    "processing_time": 45.2
  }
}
```

## Agency-Specific Blindspot Detection

The tool specifically checks for these common agency pitfalls:

1. **"We'll build it better" syndrome**
   - Flag: Competing on quality alone
   - Reality check: Distribution beats product

2. **"Features equal value" fallacy**
   - Flag: Feature list > 5 for MVP
   - Reality check: One feature done perfectly

3. **"We're different from clients" delusion**
   - Flag: No clear distribution strategy
   - Reality check: You need marketing too

4. **"Code is the hard part" bias**
   - Flag: 80% of plan is technical
   - Reality check: Getting customers is the hard part

5. **"We'll figure out monetization later"**
   - Flag: Vague pricing strategy
   - Reality check: Charge from day one

6. **"Perfect before launch" trap**
   - Flag: MVP timeline > 60 days
   - Reality check: Ship in 30 days or scope down

## Success Criteria

1. **Speed**: Full evaluation in <2 minutes
2. **Clarity**: Output immediately actionable
3. **Accuracy**: Correctly ranks Expedia > Restaurant
4. **Prevention**: Catches 80% of common agency blindspots
5. **Iteration**: Each cycle produces measurably refined idea
6. **Simplicity**: Single file < 1000 lines of code

## Anti-Requirements (What This Tool Is NOT)

- ❌ Not a business plan generator
- ❌ Not a market research tool
- ❌ Not a technical architecture designer
- ❌ Not a guarantee of success
- ❌ Not a replacement for customer validation
- ❌ Not a project management tool
- ❌ Not a financial modeling system

## Error Handling

- Invalid markdown structure → Graceful extraction of available content
- LLM API failures → Retry with exponential backoff (max 3 attempts)
- Incomplete extraction → Flag missing fields, continue with available data
- Scoring edge cases → Default to conservative (lower) scores

## Configuration

Tool reads from environment variables:
- `OPENAI_API_KEY`: Required for LLM access
- `BIE_MODEL`: Override default model (default: gpt-4-turbo)
- `BIE_MAX_TOKENS`: Maximum tokens per request (default: 2000)
- `BIE_TEMPERATURE`: LLM temperature (default: 0.3 for consistency)

## Example Ideas for Testing

### High Score Example (Expedia-like)
- Zero marginal cost per transaction
- Global reach from day one
- Network effects (reviews, inventory)
- Platform potential (hotels can manage listings)
- High automation (95%+)

### Low Score Example (Restaurant)
- High marginal cost (food, labor)
- Hyperlocal geography
- No network effects
- No platform potential
- Low automation (20%)

### Medium Score Example (Niche SaaS)
- Low marginal cost
- Global reach possible
- Limited network effects
- Some automation (70%)
- Moderate complexity

## Implementation Milestones

### MVP (Week 1)
- [ ] Basic schema definitions
- [ ] Single LLM pass extraction
- [ ] Simple scoring algorithm
- [ ] JSON output

### Enhanced (Week 2)
- [ ] Multi-pass enrichment
- [ ] Sophisticated scoring
- [ ] Enhanced markdown output
- [ ] Error handling

### Refined (Week 3)
- [ ] Comparison mode
- [ ] Blindspot detection
- [ ] Iteration tracking
- [ ] Performance optimization

### Polish (Week 4)
- [ ] Documentation
- [ ] Test suite
- [ ] Example library
- [ ] Configuration options

## Maintenance and Evolution

- Log all evaluations for future analysis
- Track which predictions prove accurate
- Refine scoring weights based on real outcomes
- Add new blindspot patterns as discovered
- Update prompts based on LLM improvements

## Success Metrics

- **Usage**: Tool run on every new idea before coding
- **Time Saved**: 80% reduction in abandoned projects
- **Quality**: Ideas pursued have 3x higher success rate
- **Iteration**: Average idea refined 3+ times before build
- **Portfolio**: 5+ profitable assets within 12 months

## Conclusion

This tool transforms the agency's approach from "build first, think later" to "think rigorously, build confidently." By forcing systematic evaluation before code, it ensures development resources focus on ideas with genuine scalability potential.