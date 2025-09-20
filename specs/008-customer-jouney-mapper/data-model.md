# Data Model: Customer Journey Mapper Generator

**Date**: 2025-09-20
**Phase**: 1 (Design & Contracts)

## Overview

Data model design for customer journey mapper generator following constitutional schema-first principles. All entities conform to customer_journey.json.schema and support Agent Envelope output format.

## Core Entities

### 1. Niche Market Input

**Purpose**: Represents user input specification for target market

**Schema**: `/contracts/schema.input.json`

```python
class NicheMarketInput:
    market_description: str  # Natural language or structured description
    industry: Optional[str]  # e.g., "e-commerce", "saas", "healthcare"
    target_demographics: Optional[Dict[str, str]]  # age, location, income
    product_service: Optional[str]  # What is being sold/offered
    business_model: Optional[str]  # B2B, B2C, B2B2C
    input_content_type: str  # "text/markdown", "application/json", "text/plain"
```

**Validation Rules**:
- `market_description` is required and non-empty
- At least one optional field should be provided for context
- `input_content_type` must match MIME type standards

**State Transitions**:
1. Raw Input → Normalized Input (via LLM if needed)
2. Normalized Input → Market Classification (via decision tables)

### 2. Customer Journey Map

**Purpose**: Complete journey representation conforming to schema

**Schema**: `/contracts/schema.output.json` (based on customer_journey.json.schema)

```python
class CustomerJourneyMap:
    journey_id: str  # UUID generated
    journey_name: Optional[str]  # Descriptive name
    persona: CustomerPersona  # Target customer profile
    stages: List[JourneyStage]  # Sequential journey stages
    cross_channel_experience: Optional[CrossChannelExperience]
    metadata: JourneyMetadata  # Required metadata
    overall_metrics: Optional[OverallMetrics]
    improvements: Optional[List[Improvement]]
```

**Validation Rules**:
- Must contain all required schema fields
- Stages must follow logical sequence
- All enum values must match schema definitions
- Metadata must include createdDate and version

### 3. Customer Persona

**Purpose**: Target customer profile specific to niche market

```python
class CustomerPersona:
    id: str  # Generated identifier
    name: str  # Persona name (e.g., "Eco-conscious Millennial")
    demographics: Demographics  # Age, location, occupation, income
    goals: List[str]  # Customer objectives
    pain_points: List[str]  # Key frustrations
    motivations: List[str]  # What drives decisions
```

**Generation Rules**:
- Demographics inferred from market type via decision tables
- Goals/pain points templated by industry + persona type
- Name generated using persona naming conventions

### 4. Journey Stage

**Purpose**: Distinct phase of customer experience

```python
class JourneyStage:
    stage_id: str  # Generated identifier
    stage_name: StageNameEnum  # Awareness, Consideration, Decision, etc.
    custom_stage_name: Optional[str]  # When stage_name is "Custom"
    description: str  # Stage description
    duration: Optional[Duration]  # Time spent in stage
    touchpoints: List[Touchpoint]  # Customer interactions
    goals: List[str]  # Customer goals for this stage
    success_criteria: List[str]  # Success definitions
    barriers: List[str]  # Common obstacles
```

**Business Rules**:
- Standard stages: Awareness → Consideration → Decision → Purchase → Onboarding → Retention → Advocacy
- B2B variations may include: Evaluation, Trial, Expansion stages
- Duration varies by market type (hours for impulse, months for enterprise)

### 5. Touchpoint

**Purpose**: Individual customer interaction point

```python
class Touchpoint:
    touchpoint_id: str  # Generated identifier
    channel: ChannelEnum  # website, mobile_app, email, etc.
    channel_details: Optional[str]  # Specific channel information
    action: str  # What customer does
    trigger: Optional[str]  # What initiates this touchpoint
    customer_thoughts: List[str]  # Internal dialogue
    emotions: List[Emotion]  # Emotional states with intensity
    pain_points: List[str]  # Specific frustrations
    opportunities: List[str]  # Improvement possibilities
    content: Optional[List[Content]]  # Delivered content
    metrics: Optional[Metrics]  # Performance indicators
    systems_involved: List[str]  # Backend systems
    data_collected: List[str]  # Information gathered
```

**Generation Strategy**:
- Channel selection via decision tables based on industry/persona
- Emotions templated by stage + touchpoint type
- Pain points and opportunities from industry best practices

## Decision Table Schemas

### Market Classification Rules

```python
class MarketClassificationRule:
    rule_id: str
    conditions: Dict[str, Any]  # Field conditions for matching
    market_type: str  # B2B, B2C, B2B2C
    industry_category: str  # ecommerce, saas, healthcare, etc.
    persona_template: str  # Which persona template to use
    journey_template: str  # Which journey template to use
    confidence: float  # Rule confidence score
    why: str  # Human-readable explanation
```

### Journey Template Rules

```python
class JourneyTemplateRule:
    template_id: str
    market_type: str  # Applies to which market type
    industry: str  # Specific industry
    stages: List[str]  # Stage sequence for this template
    typical_duration: Dict[str, str]  # Duration by stage
    key_channels: List[str]  # Primary channels for this journey
    success_metrics: List[str]  # Key performance indicators
```

## Template Schemas

### Persona Templates

```python
class PersonaTemplate:
    template_id: str
    market_type: str  # B2B, B2C, etc.
    industry: str  # Target industry
    demographics_defaults: Demographics  # Default demographic values
    goals_templates: List[str]  # Common goals for this persona type
    pain_points_templates: List[str]  # Common pain points
    motivations_templates: List[str]  # Common motivations
    behavioral_patterns: Dict[str, Any]  # Channel preferences, timing, etc.
```

### Touchpoint Templates

```python
class TouchpointTemplate:
    template_id: str
    stage: str  # Which journey stage
    channel: str  # Communication channel
    market_type: str  # B2B, B2C applicability
    action_templates: List[str]  # Common actions
    thought_templates: List[str]  # Common thoughts
    emotion_patterns: List[Emotion]  # Typical emotions
    pain_point_patterns: List[str]  # Common issues
    opportunity_patterns: List[str]  # Improvement areas
```

## Agent Envelope Schema

### Output Wrapper

```python
class AgentEnvelope:
    meta: AgentMeta  # Agent metadata
    input: NicheMarketInput  # Original input
    output: CustomerJourneyMap  # Generated journey map
    error: Optional[str]  # Error message if failed

class AgentMeta:
    agent: str  # "customer_journey_mapper"
    version: str  # SemVer version
    trace_id: str  # Unique execution identifier
    ts: str  # ISO-8601 timestamp
    brand_token: str  # Brand configuration token
    hash: str  # SHA256 of output
    cost: CostMetrics  # Token and USD costs
    prompt_id: Optional[str]  # Prompt identifier if LLM used
    prompt_hash: Optional[str]  # Prompt hash if LLM used
```

## Relationships

### Entity Relationships
```
NicheMarketInput
    ↓ (normalized via LLM)
MarketClassification
    ↓ (via decision tables)
PersonaTemplate + JourneyTemplate
    ↓ (content generation)
CustomerJourneyMap
    ├── CustomerPersona
    └── JourneyStage[]
        └── Touchpoint[]
```

### Data Flow Dependencies
1. Input validation depends on schema.input.json
2. Market classification depends on decision table rules
3. Template selection depends on classification results
4. Content generation depends on selected templates
5. Output validation depends on customer_journey.json.schema

## Validation Strategy

### Input Validation
- JSON Schema validation for structured inputs
- Content validation for markdown/text inputs
- Business rule validation via decision tables

### Output Validation
- Pydantic model validation against customer_journey.json.schema
- Business rule validation (stage sequence, enum values)
- Completeness validation (all required fields populated)

### Test Data Requirements
- Golden input examples for each input format
- Template test data for each market type
- Edge case examples (minimal input, complex scenarios)
- Invalid input examples for negative testing

## Performance Considerations

### Memory Efficiency
- Lazy loading of templates based on classification
- Streaming JSON output for large journey maps
- Template caching for repeated market types

### Computation Efficiency
- Decision table indexing for O(1) rule lookup
- Template pre-compilation for faster generation
- Minimal LLM calls (≤2 per execution)

## Data Model Completion

✅ All entities from feature specification modeled
✅ Relationships and dependencies defined
✅ Validation rules specified
✅ Template structures designed
✅ Agent Envelope compliance ensured
✅ Performance considerations addressed

**Ready for**: Contract generation and API design