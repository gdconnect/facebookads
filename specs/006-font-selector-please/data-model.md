# Data Model: Google Font Selector Enhancement

## Core Entities

### GoogleFont
Represents a single Google Font with all its metadata and variants.

**Fields**:
- `family: str` - Font family name (e.g., "Open Sans")
- `category: str` - Font category (serif, sans-serif, display, handwriting, monospace)
- `variants: List[str]` - Available font weights and styles (e.g., ["regular", "700", "italic"])
- `subsets: List[str]` - Character set support (e.g., ["latin", "latin-ext", "cyrillic"])
- `version: str` - Font version for cache invalidation
- `last_modified: str` - Last modification date for freshness tracking
- `files: Dict[str, str]` - Direct download URLs for each variant

**Validation Rules**:
- `family` must be non-empty string
- `category` must be one of: serif, sans-serif, display, handwriting, monospace
- `variants` must contain at least "regular"
- `subsets` must contain at least "latin"

### FontSelectionCriteria
Represents the input criteria used for font selection based on brand characteristics.

**Fields**:
- `brand_personality: List[str]` - Personality traits (e.g., ["professional", "modern"])
- `target_audience: str` - Primary audience description
- `brand_voice: str` - Brand voice characteristics
- `existing_colors: List[str]` - Existing brand colors for harmony consideration
- `industry_context: Optional[str]` - Industry or domain context
- `enhancement_level: str` - Requested enhancement depth (minimal, moderate, comprehensive)

**Validation Rules**:
- `brand_personality` must be non-empty list
- `enhancement_level` must be one of: minimal, moderate, comprehensive
- `target_audience` must be non-empty string

### TypographyHierarchy
Represents the complete typography system for a brand including font usage guidelines.

**Fields**:
- `primary_font: FontRecommendation` - Main font for headings and titles
- `secondary_font: Optional[FontRecommendation]` - Body text and supporting content font
- `accent_font: Optional[FontRecommendation]` - Special emphasis and decorative text
- `heading_scale: Dict[str, FontStyle]` - H1-H6 styling specifications
- `body_styles: Dict[str, FontStyle]` - Body text, caption, and other text styles
- `usage_guidelines: List[str]` - Human-readable usage recommendations

**Validation Rules**:
- `primary_font` must always be present
- `heading_scale` must contain at least H1, H2, and body entries
- All FontRecommendation objects must be valid

### FontRecommendation
Represents a specific font recommendation with confidence scoring and rationale.

**Fields**:
- `google_font: GoogleFont` - The recommended Google Font
- `confidence_score: float` - Selection confidence (0.0-1.0)
- `rationale: str` - Human-readable explanation for the selection
- `use_cases: List[str]` - Specific use cases for this font
- `weights: List[str]` - Recommended font weights for the brand
- `alternatives: List[GoogleFont]` - Alternative font options

**Validation Rules**:
- `confidence_score` must be between 0.0 and 1.0
- `rationale` must be non-empty string
- `use_cases` must be non-empty list
- `weights` must be subset of `google_font.variants`

### FontStyle
Represents specific styling properties for typography elements.

**Fields**:
- `font_weight: str` - Font weight (e.g., "400", "700", "bold")
- `font_size: str` - Size specification (e.g., "2.5rem", "18px")
- `line_height: str` - Line height ratio or absolute value
- `letter_spacing: Optional[str]` - Letter spacing adjustment
- `margin_bottom: Optional[str]` - Spacing below element

**Validation Rules**:
- `font_weight` must be valid CSS font-weight value
- `font_size` must be valid CSS size value
- `line_height` must be valid CSS line-height value

### GoogleFontsCache
Represents cached Google Fonts API responses for performance optimization.

**Fields**:
- `fonts: List[GoogleFont]` - Cached font data
- `last_updated: datetime` - Cache timestamp
- `api_version: str` - Google Fonts API version
- `total_count: int` - Total number of fonts in cache

**Validation Rules**:
- `fonts` must not be empty
- `last_updated` must be valid datetime
- `total_count` must match length of `fonts` list

### FontSelectionRequest
Represents a complete font selection request including context and preferences.

**Fields**:
- `criteria: FontSelectionCriteria` - Selection criteria from brand analysis
- `existing_typography: Optional[TypographyHierarchy]` - Existing font specifications to preserve
- `request_id: str` - Unique identifier for request tracking
- `timestamp: datetime` - Request creation time

**Validation Rules**:
- `criteria` must be valid FontSelectionCriteria
- `request_id` must be non-empty string
- `timestamp` must be valid datetime

### FontSelectionResponse
Represents the complete output of font selection including recommendations and metadata.

**Fields**:
- `typography: TypographyHierarchy` - Complete typography system
- `selection_metadata: FontSelectionMetadata` - Processing metadata
- `request_id: str` - Matching request identifier
- `processing_time: float` - Selection duration in seconds

**Validation Rules**:
- `typography` must be valid TypographyHierarchy
- `processing_time` must be non-negative float
- `request_id` must match original request

### FontSelectionMetadata
Represents metadata about the font selection process and decisions.

**Fields**:
- `selection_method: str` - Method used (rule-based, llm-assisted, cached)
- `api_calls_made: int` - Number of Google Fonts API calls
- `cache_hits: int` - Number of cache hits during selection
- `fallback_used: bool` - Whether fallback fonts were used
- `personality_matches: Dict[str, float]` - Personality trait match scores
- `total_fonts_considered: int` - Number of fonts evaluated

**Validation Rules**:
- `selection_method` must be one of: rule-based, llm-assisted, cached, fallback
- `api_calls_made` must be non-negative integer
- `cache_hits` must be non-negative integer
- `personality_matches` values must be between 0.0 and 1.0

## Entity Relationships

### Primary Relationships
- `FontSelectionRequest` → `FontSelectionCriteria` (one-to-one)
- `FontSelectionResponse` → `TypographyHierarchy` (one-to-one)
- `TypographyHierarchy` → `FontRecommendation` (one-to-many)
- `FontRecommendation` → `GoogleFont` (many-to-one)
- `GoogleFontsCache` → `GoogleFont` (one-to-many)

### Data Flow
```
Brand Analysis → FontSelectionCriteria → FontSelectionRequest
                                              ↓
GoogleFontsCache → Font Matching Logic → FontRecommendation
                                              ↓
FontStyle Generation → TypographyHierarchy → FontSelectionResponse
```

## State Transitions

### Font Selection Workflow States
1. **Initial**: Brand data available, no font analysis started
2. **Analyzing**: Extracting personality and criteria from brand
3. **Searching**: Querying Google Fonts API and cache
4. **Matching**: Applying selection algorithms to font candidates
5. **Generating**: Creating typography hierarchy and styles
6. **Complete**: Font selection finished, ready for output
7. **Error**: Fallback to default fonts due to failures

### Cache Management States
1. **Empty**: No cached font data available
2. **Loading**: Fetching fonts from Google Fonts API
3. **Fresh**: Cache contains current font data
4. **Stale**: Cache data older than TTL, needs refresh
5. **Invalid**: Cache corrupted or incompatible, needs rebuild

## Integration Points

### Existing Brand Identity Generator
- Extends `BrandData` to include `typography: Optional[TypographyHierarchy]`
- Integrates with `LLMEnhancementEngine` for personality analysis
- Adds font selection to enhancement workflow
- Maintains compatibility with existing session management

### Configuration Integration
- Add font-related settings to `DeveloperConfig`
- Environment variable support for Google Fonts API key
- Cache configuration options
- Font selection preferences and defaults