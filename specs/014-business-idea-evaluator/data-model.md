# Data Model: Business Idea Evaluator

## Entity Definitions

### Core Business Entities

#### RawIdea
**Purpose**: Initial business idea extraction from markdown input
**Lifecycle**: Input processing → Validation → Enhancement

```python
class RawIdea(BaseModel):
    """First pass: Extract what the human actually wrote"""
    name: str = Field(..., description="Business idea name/title")
    problem: str = Field(..., description="Problem being solved")
    solution: str = Field(..., description="Proposed solution approach")
    target_customer: Optional[str] = Field(None, description="Target customer segment")
    monetization: Optional[str] = Field(None, description="Revenue model")
    technical_approach: Optional[str] = Field(None, description="Implementation approach")
    inspiration: Optional[str] = Field(None, description="Similar companies or 'X for Y' analogy")
```

**Validation Rules**:
- `name`: 1-100 characters, non-empty
- `problem`: 10-1000 characters, non-empty
- `solution`: 10-1000 characters, non-empty
- Optional fields: 0-500 characters if provided

#### BusinessModel
**Purpose**: Refined business mechanics analysis
**Lifecycle**: RawIdea → LLM Enhancement → Scoring Input

```python
class BusinessModel(BaseModel):
    """Understand the fundamental business mechanics"""
    value_creation: str = Field(..., description="What value is created?")
    value_capture: str = Field(..., description="How is money made?")
    unit_economics: str = Field(..., description="Revenue per user minus costs")
    growth_mechanism: str = Field(..., description="How does it grow?")
    competitive_moat: str = Field(..., description="Why won't others copy?")
    minimum_viable_scope: str = Field(..., description="Smallest valuable version")
```

**Validation Rules**:
- All fields: 20-500 characters, actionable descriptions
- `unit_economics`: Must reference specific numbers or ratios
- `growth_mechanism`: Must be specific, measurable

#### ScalabilityFactors
**Purpose**: Growth potential and constraint analysis
**Lifecycle**: BusinessModel → LLM Analysis → Scalability Scoring

```python
class ScalabilityFactors(BaseModel):
    """Evaluate growth potential and constraints"""
    marginal_cost_per_customer: str = Field(..., description="Cost to serve N+1 customer")
    geographic_constraints: str = Field(..., description="Local/regional/national/global reach")
    automation_potential: int = Field(..., ge=0, le=100, description="Percentage automatable (0-100)")
    network_effects: str = Field(..., description="How users create value for other users")
    platform_potential: bool = Field(..., description="Can others build on top?")
    data_compound_value: str = Field(..., description="Does data accumulate advantage?")
```

**Validation Rules**:
- `automation_potential`: Integer 0-100
- `platform_potential`: Boolean (True/False)
- String fields: 20-300 characters with specific examples

#### RiskAssessment
**Purpose**: Reality check and risk identification
**Lifecycle**: All Previous → LLM Analysis → Risk Scoring

```python
class RiskAssessment(BaseModel):
    """Identify what could go wrong"""
    startup_costs: Dict[str, float] = Field(..., description="Infrastructure, marketing, legal costs")
    time_to_revenue: str = Field(..., description="Realistic timeline to first revenue")
    key_dependencies: List[str] = Field(..., description="External services, APIs, partners")
    biggest_risk: str = Field(..., description="Single greatest threat to success")
    boring_version: str = Field(..., description="Stripped down but profitable version")
    why_not_already_dominated: str = Field(..., description="Market inefficiency explanation")
```

**Validation Rules**:
- `startup_costs`: Valid float values, at least one category
- `key_dependencies`: 1-10 items, each 5-100 characters
- String fields: 20-500 characters

### Evaluation Results

#### ComputedScores
**Purpose**: Quantitative evaluation metrics
**Lifecycle**: Analysis Results → Scoring Algorithm → Grade Calculation

```python
class ComputedScores(BaseModel):
    """Calculated evaluation metrics"""
    scalability_score: int = Field(..., ge=0, le=100, description="Growth potential (0-100)")
    complexity_score: int = Field(..., ge=0, le=100, description="Implementation difficulty (0-100, lower better)")
    risk_score: int = Field(..., ge=0, le=100, description="Risk level (0-100, lower better)")
    overall_grade: str = Field(..., pattern="^[A-F]$", description="Letter grade A-F")
```

**Calculation Rules**:
- All scores: Integer 0-100
- `overall_grade`: Single letter A, B, C, D, or F
- Validation: Grade must match score thresholds

#### ActionableInsights
**Purpose**: Specific recommendations and next steps
**Lifecycle**: Analysis Results → LLM Synthesis → User Output

```python
class ActionableInsights(BaseModel):
    """Specific recommendations and actions"""
    critical_questions: List[str] = Field(..., description="Must answer before proceeding")
    quick_wins: List[str] = Field(..., description="Easy improvements to implement")
    red_flags: List[str] = Field(..., description="Serious concerns requiring attention")
    next_steps: List[str] = Field(..., description="Concrete actions to take")
    similar_successes: List[str] = Field(..., description="Companies that proved the model")
    recommended_mvp: str = Field(..., description="30-day buildable version")
```

**Validation Rules**:
- List fields: 3-7 items each, 20-200 characters per item
- `recommended_mvp`: 50-300 characters, specific and actionable
- All items must be actionable, not abstract

#### EvaluationMetadata
**Purpose**: Execution context and audit trail
**Lifecycle**: Evaluation Start → Continuous Updates → Final Output

```python
class EvaluationMetadata(BaseModel):
    """Evaluation execution context"""
    evaluation_date: datetime = Field(..., description="When evaluation was performed")
    model_used: str = Field(..., description="LLM model identifier")
    processing_time: float = Field(..., description="Total evaluation time in seconds")
    token_usage: Dict[str, int] = Field(..., description="Input/output tokens by phase")
    confidence_scores: Dict[str, float] = Field(..., description="LLM confidence per phase")
```

### Complete Evaluation Result

#### EvaluatedIdea
**Purpose**: Complete evaluation result combining all analyses
**Lifecycle**: All Components → Assembly → Output Generation

```python
class EvaluatedIdea(BaseModel):
    """Complete evaluated business idea"""
    # Input
    raw_idea: RawIdea

    # Analysis Components
    business_model: BusinessModel
    scalability: ScalabilityFactors
    risks: RiskAssessment

    # Computed Results
    scores: ComputedScores
    insights: ActionableInsights
    metadata: EvaluationMetadata

    # Output Configuration
    output_format: Literal["json", "markdown", "both"] = "json"
    include_reasoning: bool = True
```

## Entity Relationships

```
RawIdea (1) → (1) BusinessModel
       ↓
    ScalabilityFactors (1) → (1) ComputedScores
       ↓                          ↑
   RiskAssessment (1) ----→ (1) ---
       ↓
   ActionableInsights
       ↓
   EvaluatedIdea (aggregates all)
```

## State Transitions

### Evaluation Pipeline States
1. **INPUT**: Markdown file → RawIdea extraction
2. **ENHANCE_1**: RawIdea → BusinessModel analysis
3. **ENHANCE_2**: BusinessModel → ScalabilityFactors analysis
4. **ENHANCE_3**: ScalabilityFactors → RiskAssessment analysis
5. **SYNTHESIZE**: All components → ComputedScores + ActionableInsights
6. **OUTPUT**: EvaluatedIdea → JSON/Markdown generation

### Error States
- **PARSE_ERROR**: Invalid markdown structure
- **EXTRACT_ERROR**: Cannot identify business idea components
- **LLM_ERROR**: API failures or validation errors
- **SCORE_ERROR**: Invalid scoring calculations
- **OUTPUT_ERROR**: Cannot generate requested format

## Configuration Schema

#### EvaluatorConfig
**Purpose**: Tool configuration and behavior settings

```python
class EvaluatorConfig(BaseModel):
    """Tool configuration settings"""

    # Model Settings
    model_enabled: bool = False  # Constitutional default
    model_provider: Literal["openai", "anthropic", "azure", "gemini"] = "openai"
    model_name: str = "gpt-4-turbo"
    model_temperature: float = Field(0.3, ge=0.0, le=2.0)
    model_max_tokens: int = Field(2000, ge=100, le=4000)
    model_timeout_seconds: int = Field(120, ge=30, le=300)

    # Performance Budgets
    max_evaluation_time_seconds: int = Field(120, ge=60, le=300)
    max_cost_usd: float = Field(1.0, ge=0.1, le=5.0)
    max_retries: int = Field(1, ge=0, le=3)

    # Scoring Weights
    scalability_weights: Dict[str, float] = {
        "marginal_cost": 0.30,
        "automation": 0.25,
        "network_effects": 0.20,
        "geographic_reach": 0.15,
        "platform_potential": 0.10
    }

    # Output Settings
    default_output_format: Literal["json", "markdown", "both"] = "json"
    include_reasoning: bool = True
    verbose_logging: bool = False
```

## Validation Strategy

### Input Validation
- **Markdown Structure**: Required sections present
- **Content Length**: Within specified bounds
- **Character Encoding**: UTF-8 compliance
- **Business Relevance**: Keywords and structure validation

### Business Logic Validation
- **Score Consistency**: Grades match score ranges
- **Dependency Logic**: Risk factors align with complexity
- **Recommendation Coherence**: Insights match analysis
- **Time/Cost Realism**: Numbers within reasonable bounds

### Output Validation
- **Schema Compliance**: All required fields present
- **Format Consistency**: JSON/Markdown structure valid
- **Content Quality**: Non-empty, meaningful responses
- **Token Budget**: Within configured limits

## Testing Data Requirements

### Golden Test Cases
1. **High-Score Example**: Expedia-like platform business
2. **Low-Score Example**: Traditional restaurant business
3. **Medium-Score Example**: Niche SaaS tool
4. **Edge Case**: Minimal valid input
5. **Error Case**: Invalid/incomplete markdown

### Property-Based Testing
- **Score Boundaries**: All combinations of min/max scores
- **Text Length Variations**: Edge cases for field limits
- **Configuration Permutations**: Valid config combinations
- **Unicode Handling**: International characters and symbols