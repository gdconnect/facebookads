# Font Selection API Contract

## Font Selection Service Interface

### Core Font Selection Method

```python
def select_fonts(
    criteria: FontSelectionCriteria,
    existing_typography: Optional[TypographyHierarchy] = None
) -> FontSelectionResponse:
    """
    Select appropriate Google Fonts based on brand criteria.

    Args:
        criteria: Brand characteristics and selection preferences
        existing_typography: Existing font specs to preserve (optional)

    Returns:
        Complete typography system with metadata

    Raises:
        FontSelectionError: When selection fails and no fallbacks available
        GoogleFontsAPIError: When API is unavailable and cache is empty
    """
```

**Contract Requirements**:
- MUST return valid TypographyHierarchy with at least primary_font
- MUST preserve existing_typography if provided
- MUST include confidence scores ≥ 0.7 for primary recommendations
- MUST complete within 2 seconds for cached requests
- MUST complete within 10 seconds for API requests
- MUST provide fallback fonts when API fails

### Google Fonts API Integration

```python
def fetch_google_fonts(
    api_key: Optional[str] = None,
    force_refresh: bool = False
) -> List[GoogleFont]:
    """
    Fetch current Google Fonts catalog from API.

    Args:
        api_key: Google Fonts API key (optional, uses env var if not provided)
        force_refresh: Force API call even if cache is fresh

    Returns:
        List of all available Google Fonts with metadata

    Raises:
        GoogleFontsAPIError: When API request fails
        CacheError: When cache operations fail
    """
```

**Contract Requirements**:
- MUST cache results for 24 hours minimum
- MUST handle API rate limiting gracefully
- MUST validate font metadata completeness
- MUST return at least 800 fonts (current Google Fonts count)
- MUST include font files URLs for web usage

### Font Caching Service

```python
def get_cached_fonts(max_age_hours: int = 24) -> Optional[List[GoogleFont]]:
    """
    Retrieve fonts from local cache if fresh.

    Args:
        max_age_hours: Maximum cache age before considering stale

    Returns:
        Cached fonts list or None if cache miss/stale
    """

def update_font_cache(fonts: List[GoogleFont]) -> bool:
    """
    Update local font cache with fresh data.

    Args:
        fonts: Fresh font data from Google Fonts API

    Returns:
        True if cache update succeeded, False otherwise
    """
```

**Contract Requirements**:
- MUST handle cache corruption gracefully
- MUST support concurrent access safely
- MUST respect configured cache directory
- MUST provide cache statistics for monitoring

### Font Matching Algorithm

```python
def match_fonts_to_personality(
    personality_traits: List[str],
    available_fonts: List[GoogleFont],
    enhancement_level: str = "moderate"
) -> List[FontRecommendation]:
    """
    Match fonts to brand personality using rule-based + LLM approach.

    Args:
        personality_traits: Brand personality descriptors
        available_fonts: Google Fonts to consider
        enhancement_level: Selection complexity (minimal/moderate/comprehensive)

    Returns:
        Ranked list of font recommendations with confidence scores

    Raises:
        MatchingError: When no suitable fonts found
    """
```

**Contract Requirements**:
- MUST return at least 1 font recommendation
- MUST rank recommendations by confidence score
- MUST include rationale for each recommendation
- MUST respect enhancement_level complexity
- MUST handle unknown personality traits gracefully

### Typography System Generator

```python
def generate_typography_hierarchy(
    primary_font: FontRecommendation,
    secondary_font: Optional[FontRecommendation] = None,
    enhancement_level: str = "moderate"
) -> TypographyHierarchy:
    """
    Generate complete typography system from font recommendations.

    Args:
        primary_font: Main font for headings and emphasis
        secondary_font: Supporting font for body text (optional)
        enhancement_level: System complexity level

    Returns:
        Complete typography hierarchy with styles and guidelines
    """
```

**Contract Requirements**:
- MUST include H1-H6 heading styles
- MUST include body, caption, and emphasis styles
- MUST provide CSS-compatible values
- MUST ensure readability compliance
- MUST scale appropriately across devices

## Integration Contracts

### CLI Integration Contract

```python
# Brand markdown processing
def analyze_brand_for_typography(brand_content: str) -> FontSelectionCriteria:
    """Extract typography criteria from brand markdown."""

# Enhancement workflow integration
def enhance_brand_with_typography(
    brand_data: dict,
    enhancement_level: str,
    llm_provider: str
) -> dict:
    """Add typography to existing brand enhancement workflow."""

# Interactive mode integration
def review_font_selection_interactively(
    recommendations: List[FontRecommendation]
) -> FontRecommendation:
    """Allow user to review and approve font selections."""
```

### Configuration Contract

```python
# Configuration extension
class FontSelectionConfig(BaseModel):
    google_fonts_api_key: Optional[str] = None
    font_cache_ttl_hours: int = 24
    font_cache_max_size_mb: int = 50
    default_fallback_fonts: List[str] = ["Open Sans", "Roboto", "Inter"]
    enable_font_selection: bool = True
    font_selection_timeout: float = 10.0
```

### Error Handling Contract

```python
class FontSelectionError(Exception):
    """Base exception for font selection failures."""

class GoogleFontsAPIError(FontSelectionError):
    """Google Fonts API access failures."""

class CacheError(FontSelectionError):
    """Font cache operation failures."""

class MatchingError(FontSelectionError):
    """Font matching algorithm failures."""
```

**Error Contract Requirements**:
- MUST provide specific error messages
- MUST include recovery suggestions
- MUST log errors for debugging
- MUST never crash the main application
- MUST trigger fallback mechanisms

## Performance Contracts

### Response Time Requirements
- Font selection (cached): ≤ 2 seconds
- Font selection (API call): ≤ 10 seconds
- Cache operations: ≤ 500ms
- Personality matching: ≤ 1 second

### Resource Usage Limits
- Memory usage: ≤ 100MB for font cache
- Disk usage: ≤ 50MB for cache files
- API calls: ≤ 10 per brand enhancement
- Concurrent requests: Support 5 simultaneous operations

### Reliability Requirements
- Cache hit rate: ≥ 80% for repeated brands
- API success rate: ≥ 95% under normal conditions
- Fallback success rate: 100% (must never fail completely)
- Recovery time: ≤ 30 seconds after API restoration

## Testing Contracts

### Unit Test Requirements
- Font matching logic with mock data
- Cache operations with temporary directories
- Error handling with simulated failures
- Configuration validation with invalid inputs

### Integration Test Requirements
- Google Fonts API real requests (with test key)
- End-to-end font selection workflow
- Cache persistence across application restarts
- CLI integration with actual brand files

### Contract Test Requirements
- API response schema validation
- Font metadata completeness verification
- Typography hierarchy structure validation
- Performance benchmark compliance

## Data Format Contracts

### Input Data Contract
```json
{
  "brand_personality": ["professional", "modern", "trustworthy"],
  "target_audience": "enterprise decision makers",
  "brand_voice": "authoritative yet approachable",
  "existing_colors": ["#2563eb", "#10b981"],
  "enhancement_level": "moderate"
}
```

### Output Data Contract
```json
{
  "typography": {
    "primary_font": {
      "google_font": {
        "family": "Inter",
        "category": "sans-serif",
        "variants": ["300", "400", "500", "600", "700"]
      },
      "confidence_score": 0.92,
      "rationale": "Inter provides excellent readability...",
      "use_cases": ["headings", "navigation", "CTAs"],
      "weights": ["400", "600", "700"]
    },
    "heading_scale": {
      "h1": {
        "font_weight": "700",
        "font_size": "3rem",
        "line_height": "1.2"
      }
    }
  },
  "selection_metadata": {
    "selection_method": "rule-based",
    "processing_time": 1.23,
    "total_fonts_considered": 45
  }
}
```