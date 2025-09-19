# Data Model: LLM-Enhanced Brand Identity Processing

**Date**: 2025-09-19
**Feature**: LLM-Enhanced Brand Identity Processing
**Phase**: 1 - Data Model Design

## Core Enhancement Models

### LLM Integration Models

#### LLMRequest
```python
class LLMRequest(BaseModel):
    """Structured request to LLM for brand enhancement."""

    prompt_type: str = Field(..., description="Type of enhancement: gap_analysis, color_generation, design_strategy")
    context: Dict[str, Any] = Field(..., description="Brand context and existing elements")
    enhancement_level: str = Field("moderate", regex="^(minimal|moderate|comprehensive)$")
    user_preferences: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "prompt_type": "color_generation",
                "context": {
                    "brand_name": "TechFlow",
                    "personality": "professional, innovative",
                    "color_descriptions": ["professional blue", "energetic orange"]
                },
                "enhancement_level": "moderate"
            }
        }
```

#### LLMResponse
```python
class LLMResponse(BaseModel):
    """Response from LLM with enhancement suggestions."""

    response_type: str
    content: Dict[str, Any]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., description="Explanation of enhancement decisions")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time: float

    @validator('confidence_score')
    def validate_confidence(cls, v):
        return max(0.0, min(1.0, v))

    class Config:
        schema_extra = {
            "example": {
                "response_type": "color_enhancement",
                "content": {
                    "primary": {"hex": "#2563EB", "name": "Professional Blue", "usage": "CTAs, headers"},
                    "secondary": {"hex": "#F97316", "name": "Energetic Orange", "usage": "Accents, highlights"}
                },
                "confidence_score": 0.87,
                "rationale": "Blue conveys trust and professionalism while orange adds energy and innovation",
                "processing_time": 1.2
            }
        }
```

### Gap Analysis Models

#### BrandGapAnalysis
```python
class BrandGapAnalysis(BaseModel):
    """Analysis of missing or incomplete brand elements."""

    missing_elements: List[str] = Field(..., description="List of missing brand components")
    incomplete_elements: List[str] = Field(..., description="List of elements needing enhancement")
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="Overall completeness percentage")
    priority_gaps: List[GapItem] = Field(..., description="Prioritized list of gaps to address")
    enhancement_opportunities: List[str] = Field(..., description="Areas for quality improvement")

    class Config:
        schema_extra = {
            "example": {
                "missing_elements": ["typography", "visual_style"],
                "incomplete_elements": ["color_palette"],
                "completeness_score": 0.6,
                "priority_gaps": [
                    {
                        "element": "typography",
                        "impact": "high",
                        "description": "No font preferences specified"
                    }
                ]
            }
        }
```

#### GapItem
```python
class GapItem(BaseModel):
    """Individual gap requiring enhancement."""

    element: str = Field(..., description="Brand element with gap")
    impact: str = Field(..., regex="^(low|medium|high|critical)$")
    description: str = Field(..., description="Detailed gap description")
    enhancement_suggestion: Optional[str] = None
    estimated_improvement: float = Field(..., ge=0.0, le=1.0)

    @validator('impact')
    def validate_impact(cls, v):
        valid_impacts = ["low", "medium", "high", "critical"]
        if v not in valid_impacts:
            raise ValueError(f"Impact must be one of {valid_impacts}")
        return v
```

### Enhancement Models

#### EnhancementSuggestion
```python
class EnhancementSuggestion(BaseModel):
    """LLM-generated enhancement recommendation."""

    element_type: str = Field(..., description="Type of brand element being enhanced")
    original_value: Optional[str] = None
    suggested_value: Dict[str, Any] = Field(..., description="Enhanced element specification")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., description="Explanation for the enhancement")
    accessibility_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        schema_extra = {
            "example": {
                "element_type": "color",
                "original_value": "blue",
                "suggested_value": {
                    "hex": "#1E40AF",
                    "name": "Trust Blue",
                    "usage": "Primary brand color for headers and CTAs"
                },
                "confidence_score": 0.92,
                "rationale": "This shade balances professionalism with approachability",
                "accessibility_score": 0.85
            }
        }
```

#### DesignStrategy
```python
class DesignStrategy(BaseModel):
    """Unified design strategy for brand consistency."""

    consistency_principles: List[str] = Field(..., description="Core design principles")
    color_strategy: ColorStrategyGuidelines
    typography_strategy: TypographyStrategyGuidelines
    spacing_strategy: SpacingGuidelines
    hierarchy_strategy: HierarchyGuidelines
    accessibility_strategy: AccessibilityGuidelines
    coherence_score: float = Field(..., ge=0.0, le=1.0)

    class Config:
        schema_extra = {
            "example": {
                "consistency_principles": [
                    "Maintain 4.5:1 contrast ratio",
                    "Use consistent spacing scale",
                    "Apply hierarchical typography"
                ],
                "coherence_score": 0.88
            }
        }
```

#### ColorStrategyGuidelines
```python
class ColorStrategyGuidelines(BaseModel):
    """Guidelines for consistent color usage."""

    primary_usage: str = Field(..., description="When to use primary colors")
    secondary_usage: str = Field(..., description="When to use secondary colors")
    neutral_usage: str = Field(..., description="When to use neutral colors")
    contrast_requirements: Dict[str, float] = Field(..., description="Minimum contrast ratios")
    accessibility_notes: List[str] = Field(..., description="Color accessibility guidelines")
```

#### TypographyStrategyGuidelines
```python
class TypographyStrategyGuidelines(BaseModel):
    """Guidelines for consistent typography usage."""

    heading_hierarchy: Dict[str, str] = Field(..., description="H1-H6 usage guidelines")
    body_text_guidelines: str = Field(..., description="Body text usage")
    emphasis_guidelines: str = Field(..., description="Bold, italic usage")
    spacing_guidelines: str = Field(..., description="Line height, letter spacing")
```

### Enhancement Workflow Models

#### EnhancementWorkflow
```python
class EnhancementWorkflow(BaseModel):
    """Complete LLM enhancement workflow state."""

    workflow_id: str = Field(..., description="Unique identifier for this enhancement session")
    original_input: BrandMarkdownInput
    gap_analysis: BrandGapAnalysis
    enhancement_suggestions: List[EnhancementSuggestion]
    design_strategy: DesignStrategy
    user_feedback: List[UserFeedback] = Field(default_factory=list)
    final_brand_identity: Optional[BrandIdentity] = None
    workflow_metadata: WorkflowMetadata

    class Config:
        schema_extra = {
            "example": {
                "workflow_id": "wf_20251219_techflow_001",
                "workflow_metadata": {
                    "started_at": "2025-12-19T10:00:00Z",
                    "enhancement_level": "moderate",
                    "total_processing_time": 4.2
                }
            }
        }
```

#### WorkflowMetadata
```python
class WorkflowMetadata(BaseModel):
    """Metadata about the enhancement workflow."""

    started_at: datetime
    completed_at: Optional[datetime] = None
    enhancement_level: str = Field(..., regex="^(minimal|moderate|comprehensive)$")
    llm_provider: str = Field(..., description="LLM service used")
    total_processing_time: Optional[float] = None
    steps_completed: List[str] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
```

### User Interaction Models

#### UserFeedback
```python
class UserFeedback(BaseModel):
    """User feedback on enhancement suggestions."""

    suggestion_id: str
    user_rating: int = Field(..., ge=1, le=5, description="1-5 star rating")
    feedback_type: str = Field(..., regex="^(accept|reject|modify|request_alternative)$")
    feedback_text: Optional[str] = None
    modification_request: Optional[Dict[str, Any]] = None
    timestamp: datetime

    @validator('user_rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

    class Config:
        schema_extra = {
            "example": {
                "suggestion_id": "color_enhancement_001",
                "user_rating": 4,
                "feedback_type": "modify",
                "feedback_text": "Like the blue but prefer a warmer orange",
                "modification_request": {
                    "secondary_color": "warm orange instead of energetic orange"
                }
            }
        }
```

#### UserPreferences
```python
class UserPreferences(BaseModel):
    """Learned user preferences for future enhancements."""

    user_id: Optional[str] = None
    color_preferences: Dict[str, Any] = Field(default_factory=dict)
    typography_preferences: Dict[str, Any] = Field(default_factory=dict)
    style_preferences: Dict[str, Any] = Field(default_factory=dict)
    enhancement_level_preference: str = Field("moderate", regex="^(minimal|moderate|comprehensive)$")
    feedback_history: List[Dict[str, Any]] = Field(default_factory=list)
    learning_metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        schema_extra = {
            "example": {
                "color_preferences": {
                    "preferred_blue_range": ["#1E40AF", "#2563EB"],
                    "avoid_colors": ["pure_red", "bright_yellow"],
                    "accessibility_priority": "high"
                },
                "enhancement_level_preference": "moderate"
            }
        }
```

### Validation and Quality Models

#### CoherenceReport
```python
class CoherenceReport(BaseModel):
    """Report on design coherence and consistency."""

    overall_coherence_score: float = Field(..., ge=0.0, le=1.0)
    dimension_scores: Dict[str, float] = Field(..., description="Scores for each coherence dimension")
    coherence_issues: List[CoherenceIssue] = Field(default_factory=list)
    improvement_recommendations: List[str] = Field(default_factory=list)
    accessibility_compliance: bool
    professional_standards_met: bool

    class Config:
        schema_extra = {
            "example": {
                "overall_coherence_score": 0.85,
                "dimension_scores": {
                    "color_harmony": 0.9,
                    "typography_alignment": 0.8,
                    "visual_consistency": 0.85
                },
                "accessibility_compliance": True,
                "professional_standards_met": True
            }
        }
```

#### CoherenceIssue
```python
class CoherenceIssue(BaseModel):
    """Individual coherence issue requiring attention."""

    issue_type: str = Field(..., description="Type of coherence issue")
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    description: str = Field(..., description="Detailed issue description")
    affected_elements: List[str] = Field(..., description="Brand elements affected")
    recommended_fix: str = Field(..., description="Suggested resolution")
    impact_on_coherence: float = Field(..., ge=0.0, le=1.0)
```

## Enhanced Processing Pipeline

### Processing Flow
```
Original Input → Gap Analysis → LLM Enhancement Suggestions → User Review → Design Strategy → Coherence Validation → Enhanced Brand Identity
```

### Enhancement Integration Points
1. **Pre-Processing**: Gap analysis identifies enhancement opportunities
2. **Color Enhancement**: LLM generates semantic colors with accessibility validation
3. **Typography Enhancement**: AI-powered font selection based on brand personality
4. **Strategy Generation**: Unified design principles for consistency
5. **Post-Processing**: Coherence validation and quality assurance
6. **Learning**: User feedback captured for continuous improvement

### State Management
- **Enhancement Session**: Tracks complete workflow from input to output
- **User Interaction**: Captures feedback and preferences for learning
- **Quality Assurance**: Validates coherence and professional standards
- **Performance Monitoring**: Tracks processing times and success rates

## Data Relationships

### Enhancement Flow
```
BrandMarkdownInput → BrandGapAnalysis → [LLMRequest → LLMResponse]* → EnhancementSuggestion[] → DesignStrategy → CoherenceReport → Enhanced BrandIdentity
```

### Learning Flow
```
EnhancementSuggestion → UserFeedback → UserPreferences → Future Enhancement Improvements
```

### Validation Flow
```
Enhanced BrandIdentity → CoherenceReport → Quality Validation → Final Output
```

---
**Data Model Complete**: All LLM enhancement entities defined with Pydantic validation, ready for contract generation