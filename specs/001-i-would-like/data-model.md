# Data Model: Brand Identity Design System Generator

**Date**: 2025-09-19
**Feature**: Brand Identity Design System Generator
**Phase**: 1 - Data Model Design

## Core Data Models

### Input Models (Markdown Processing)

#### BrandMarkdownInput
```python
class BrandMarkdownInput(BaseModel):
    """Parsed markdown content organized by sections."""

    brand_overview: Optional[str] = None
    colors: Optional[str] = None
    typography: Optional[str] = None
    personality: Optional[str] = None
    logo_assets: Optional[str] = None
    visual_style: Optional[str] = None
    raw_content: str

    @validator('raw_content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Markdown content cannot be empty")
        return v
```

#### ParsedColorInfo
```python
class ParsedColorInfo(BaseModel):
    """Extracted color information from natural language."""

    description: str
    hex_code: str = Field(..., regex=r"^#[0-9A-Fa-f]{6}$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    usage_hint: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "description": "warm orange",
                "hex_code": "#FF6B35",
                "confidence": 0.9,
                "usage_hint": "primary brand color"
            }
        }
```

#### PersonalityScores
```python
class PersonalityScores(BaseModel):
    """Brand personality analysis results."""

    formality: int = Field(..., ge=1, le=10)
    innovation: int = Field(..., ge=1, le=10)
    warmth: int = Field(..., ge=1, le=10)
    confidence: float = Field(..., ge=0.0, le=1.0)
    keywords_found: List[str] = []

    @validator('formality', 'innovation', 'warmth')
    def valid_score_range(cls, v):
        if not 1 <= v <= 10:
            raise ValueError("Personality scores must be between 1 and 10")
        return v
```

### Output Models (JSON Schema Compliant)

#### ColorInfo (Output)
```python
class ColorInfo(BaseModel):
    """Color specification matching schema requirements."""

    hex: str = Field(..., regex=r"^#[0-9A-Fa-f]{6}$")
    name: Optional[str] = None
    usage: Optional[str] = None
```

#### ColorPalette
```python
class ColorPalette(BaseModel):
    """Complete color system for brand identity."""

    primary: ColorInfo
    secondary: ColorInfo
    neutral: NeutralColors
    accent: Optional[List[ColorInfo]] = Field(None, max_items=3)
    gradients: Optional[List[GradientInfo]] = Field(None, max_items=2)

    @validator('accent')
    def validate_accent_colors(cls, v):
        if v and len(v) > 3:
            raise ValueError("Maximum 3 accent colors allowed")
        return v
```

#### NeutralColors
```python
class NeutralColors(BaseModel):
    """Neutral color specifications."""

    dark: str = Field("#1A1A1A", regex=r"^#[0-9A-Fa-f]{6}$")
    light: str = Field("#FFFFFF", regex=r"^#[0-9A-Fa-f]{6}$")
    mid: Optional[str] = Field("#6B7280", regex=r"^#[0-9A-Fa-f]{6}$")
```

#### FontFamily
```python
class FontFamily(BaseModel):
    """Font family specification with fallbacks."""

    primary: str
    fallback: str = "Arial, sans-serif"
    weight: List[int] = Field([400, 700], min_items=1)

    @validator('weight')
    def validate_weights(cls, v):
        valid_weights = [100, 200, 300, 400, 500, 600, 700, 800, 900]
        for weight in v:
            if weight not in valid_weights:
                raise ValueError(f"Invalid font weight: {weight}")
        return v
```

#### Typography
```python
class Typography(BaseModel):
    """Complete typography system."""

    fontFamilies: FontFamilies
    scale: Optional[TypographyScale] = None
    styles: Optional[TypographyStyles] = None

class FontFamilies(BaseModel):
    heading: FontFamily
    body: FontFamily

class TypographyScale(BaseModel):
    baseSize: int = Field(16, ge=14, le=18)
    scaleRatio: float = Field(1.25, description="Typography scaling ratio")

class TypographyStyles(BaseModel):
    headingCase: str = Field("normal", regex="^(normal|uppercase|lowercase|title)$")
    letterSpacing: str = Field("normal", regex="^(tight|normal|loose)$")
    lineHeight: str = Field("normal", regex="^(tight|normal|relaxed)$")
```

#### VisualStyle
```python
class VisualStyle(BaseModel):
    """Visual design language specifications."""

    aesthetic: str = Field(..., description="Primary design aesthetic")
    mood: List[str] = Field(..., min_items=1, max_items=3)
    imageryStyle: ImageryStyle

    @validator('aesthetic')
    def validate_aesthetic(cls, v):
        valid_aesthetics = [
            "minimalist", "modern", "classic", "playful", "bold",
            "elegant", "tech", "organic", "retro", "luxury",
            "hand-crafted", "corporate"
        ]
        if v not in valid_aesthetics:
            raise ValueError(f"Invalid aesthetic: {v}")
        return v

class ImageryStyle(BaseModel):
    type: str = Field(..., regex="^(photography|illustration|mixed|3d-renders|abstract)$")
    treatment: str = Field("realistic", regex="^(realistic|stylized|filtered|duotone|black-white)$")
    colorGrading: str = Field("vibrant", regex="^(vibrant|muted|warm|cool|high-contrast|soft)$")
```

#### BrandIdentity (Root Model)
```python
class BrandIdentity(BaseModel):
    """Complete brand identity design system."""

    brandName: str
    colorPalette: ColorPalette
    typography: Typography
    visualStyle: VisualStyle
    logoAssets: Optional[LogoAssets] = None
    layoutPrinciples: Optional[LayoutPrinciples] = None
    designElements: Optional[DesignElements] = None
    animations: Optional[Animations] = None
    brandPersonality: Optional[BrandPersonality] = None
    accessibilityPreferences: Optional[AccessibilityPreferences] = None

    @validator('brandName')
    def brand_name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Brand name is required")
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "brandName": "TechStart Solutions",
                "colorPalette": {
                    "primary": {
                        "hex": "#5B21B6",
                        "name": "Tech Purple",
                        "usage": "CTAs, headlines"
                    }
                }
            }
        }
```

### Processing Models

#### ColorMappingResult
```python
class ColorMappingResult(BaseModel):
    """Result of color name to hex conversion."""

    original_description: str
    mapped_colors: List[ParsedColorInfo]
    unmapped_descriptions: List[str] = []
    confidence_score: float

    @validator('confidence_score')
    def valid_confidence(cls, v):
        return max(0.0, min(1.0, v))
```

#### ValidationResult
```python
class ValidationResult(BaseModel):
    """Schema validation results."""

    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    missing_required_fields: List[str] = []

    def add_error(self, message: str):
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        self.warnings.append(message)
```

#### ProcessingContext
```python
class ProcessingContext(BaseModel):
    """Context information for processing pipeline."""

    input_file_path: str
    output_file_path: Optional[str] = None
    template_mode: bool = False
    strict_validation: bool = True
    debug_mode: bool = False

    class Config:
        arbitrary_types_allowed = True
```

## Data Relationships

### Processing Flow
```
MarkdownFile → BrandMarkdownInput → ColorMappingResult + PersonalityScores
                                 ↓
                              BrandIdentity → ValidationResult → JSON Output
```

### Validation Chain
1. **Input Validation**: Markdown structure and content
2. **Parsing Validation**: Section extraction and content analysis
3. **Mapping Validation**: Color and typography mapping results
4. **Schema Validation**: Final JSON schema compliance
5. **Output Validation**: File writing and format verification

## Error Handling Models

#### ProcessingError
```python
class ProcessingError(BaseModel):
    """Structured error information."""

    error_type: str
    message: str
    field: Optional[str] = None
    line_number: Optional[int] = None
    suggestions: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "error_type": "MissingSection",
                "message": "Brand Overview section not found",
                "field": "brand_overview",
                "suggestions": ["Add a '# Brand Overview' section to your markdown"]
            }
        }
```

## State Transitions

### Color Processing States
- `raw_text` → `parsed_descriptions` → `mapped_colors` → `validated_palette`

### Typography Processing States
- `brand_personality` → `font_categories` → `font_families` → `typography_system`

### Validation States
- `input_received` → `parsed` → `processed` → `validated` → `output_generated`

---
**Data Model Complete**: All entities defined with Pydantic validation, ready for contract generation