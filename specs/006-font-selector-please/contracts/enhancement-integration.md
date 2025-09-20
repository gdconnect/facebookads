# Enhancement Integration Contract

## LLM Enhancement Workflow Integration

### Font Selection Prompt Templates

```python
FONT_SELECTION_PROMPTS = {
    "personality_analysis": """
    Analyze this brand description for typography personality traits:
    Brand: {brand_content}

    Extract personality traits that influence font selection:
    - Professional level (1-10)
    - Creativity level (1-10)
    - Formality level (1-10)
    - Modern vs Classic preference
    - Target audience characteristics

    Return: JSON with personality scores and typography recommendations
    """,

    "font_refinement": """
    Refine this font selection based on brand context:
    Suggested Font: {font_name}
    Brand Personality: {personality_traits}
    Target Audience: {target_audience}
    Brand Voice: {brand_voice}

    Evaluate font appropriateness and suggest improvements:
    - Alignment with brand personality
    - Audience appeal and readability
    - Professional presentation
    - Alternative font suggestions if needed

    Return: JSON with refined recommendation and rationale
    """
}
```

### Enhancement Level Integration

```python
def integrate_font_selection_with_enhancement_levels():
    """
    Define how font selection integrates with existing enhancement levels.

    MINIMAL LEVEL:
    - Single primary font recommendation
    - Basic weight selection (Regular, Bold)
    - Simple usage guidelines
    - Fast rule-based selection only

    MODERATE LEVEL (default):
    - Primary + secondary font recommendations
    - Multiple weight options
    - Detailed usage guidelines for different elements
    - Rule-based + LLM validation
    - Typography hierarchy (H1-H3, body)

    COMPREHENSIVE LEVEL:
    - Complete typography system
    - Font pairing recommendations
    - Detailed spacing and sizing guidelines
    - LLM-enhanced selection and refinement
    - Full hierarchy (H1-H6, body, caption, etc.)
    - Brand application examples
    """
```

### Session Management Integration

```python
def extend_session_with_typography():
    """
    Extend existing session management to include font selection state.

    Session Structure Extension:
    {
        "session_id": "sess_...",
        "typography_state": {
            "selection_criteria": FontSelectionCriteria,
            "candidate_fonts": List[GoogleFont],
            "user_feedback": List[InteractionRecord],
            "final_selection": Optional[TypographyHierarchy],
            "selection_metadata": FontSelectionMetadata
        },
        "font_selection_history": [
            {
                "timestamp": "2025-09-20T...",
                "action": "personality_analysis",
                "input": {...},
                "output": {...}
            }
        ]
    }
    """
```

### Interactive Mode Integration

```python
def font_selection_interactive_workflow():
    """
    Define interactive review process for font selections.

    Interactive Steps:
    1. Show personality analysis results
    2. Present font recommendations with rationale
    3. Allow user to approve, modify, or reject each font
    4. Show typography hierarchy preview
    5. Confirm final selection
    6. Save preferences for future sessions

    User Options per Font:
    [A] Accept - Use this font as recommended
    [M] Modify - Adjust weights, usage, or find similar fonts
    [R] Reject - Remove from selection, find alternatives
    [P] Preview - Show examples of font in use
    [S] Similar - Show fonts with similar characteristics
    """
```

## Brand Analysis Enhancement

### Typography Context Extraction

```python
def extract_typography_context_from_brand(brand_content: str) -> dict:
    """
    Extract typography-relevant information from brand markdown.

    Extraction Rules:
    - Existing font specifications → preserve_typography = True
    - Brand personality keywords → personality_traits extraction
    - Target audience mentions → audience_analysis
    - Industry context → industry_typography_preferences
    - Brand voice descriptors → voice_to_font_mapping

    Returns:
    {
        "has_existing_typography": bool,
        "existing_fonts": List[str],
        "personality_indicators": List[str],
        "audience_descriptors": List[str],
        "industry_context": Optional[str],
        "voice_characteristics": List[str]
    }
    """
```

### Brand Harmony Validation

```python
def validate_font_brand_harmony(
    selected_fonts: List[FontRecommendation],
    existing_brand_elements: dict
) -> dict:
    """
    Validate that selected fonts harmonize with existing brand elements.

    Harmony Checks:
    - Color palette compatibility
    - Personality alignment consistency
    - Target audience appropriateness
    - Industry standards compliance
    - Visual weight balance

    Returns:
    {
        "harmony_score": float,  # 0.0-1.0
        "compatibility_analysis": {
            "color_harmony": float,
            "personality_alignment": float,
            "audience_fit": float,
            "industry_appropriate": float
        },
        "recommendations": List[str],
        "warnings": List[str]
    }
    """
```

## Error Recovery Integration

### Font Selection Failure Handling

```python
def handle_font_selection_failures():
    """
    Define error recovery for font selection failures.

    Failure Scenarios:
    1. Google Fonts API unavailable
       → Use cached fonts or default to safe fonts
    2. No personality match found
       → Use industry defaults or versatile fonts
    3. LLM enhancement fails
       → Fall back to rule-based selection only
    4. Cache corruption
       → Rebuild cache, use defaults temporarily
    5. Network timeout
       → Use cached data, warn user about staleness

    Recovery Actions:
    - Log detailed error information
    - Provide user-friendly error messages
    - Suggest manual font specification
    - Continue brand enhancement without typography
    - Save partial progress for later completion
    """
```

### Graceful Degradation Strategy

```python
def implement_graceful_degradation():
    """
    Define fallback behavior when font selection components fail.

    Degradation Levels:
    Level 1: Full functionality (API + LLM + Cache)
    Level 2: Cached + Rule-based (API unavailable)
    Level 3: Rule-based only (Cache + API unavailable)
    Level 4: Default fonts only (All systems unavailable)
    Level 5: No typography enhancement (Skip entirely)

    User Communication:
    - Clear status indicators for each degradation level
    - Explanation of limitations at current level
    - Suggestions for improving functionality
    - Option to retry with manual intervention
    """
```

## Configuration Integration

### Font-Specific Configuration Extension

```python
def extend_developer_config_for_fonts():
    """
    Add font-related configuration to existing DeveloperConfig.

    New Configuration Fields:
    # Google Fonts Integration
    google_fonts_api_key: Optional[str] = None
    google_fonts_cache_ttl: int = 24  # hours
    enable_font_selection: bool = True

    # Font Selection Behavior
    font_selection_timeout: float = 10.0  # seconds
    fallback_to_defaults: bool = True
    personality_matching_strict: bool = False

    # Cache Settings
    font_cache_directory: str = "./cache/fonts"
    font_cache_max_size: int = 50  # MB

    # Typography Preferences
    default_font_category: str = "sans-serif"
    prefer_web_safe_fonts: bool = True
    include_experimental_fonts: bool = False
    """
```

### Environment Variable Integration

```python
def font_environment_variables():
    """
    Define environment variables for font selection configuration.

    Environment Variables:
    BRAND_TOOL_GOOGLE_FONTS_API_KEY - Google Fonts API key
    BRAND_TOOL_FONT_CACHE_DIR - Font cache directory override
    BRAND_TOOL_FONT_SELECTION_ENABLED - Enable/disable font selection
    BRAND_TOOL_FONT_TIMEOUT - Font selection timeout in seconds
    BRAND_TOOL_FALLBACK_FONTS - Comma-separated list of fallback fonts

    Precedence Order:
    1. CLI arguments (--font-selection-timeout 15)
    2. Environment variables (BRAND_TOOL_FONT_TIMEOUT=15)
    3. Configuration file (font_selection_timeout: 15.0)
    4. Default values
    """
```

## Output Schema Integration

### Extended Brand Output Schema

```json
{
  "brandName": "Example Brand",
  "colorPalette": { /* existing color data */ },
  "typography": {
    "primary_font": {
      "google_font": {
        "family": "Inter",
        "category": "sans-serif",
        "css_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700",
        "font_files": {
          "400": "https://fonts.gstatic.com/s/inter/v12/...",
          "600": "https://fonts.gstatic.com/s/inter/v12/...",
          "700": "https://fonts.gstatic.com/s/inter/v12/..."
        }
      },
      "confidence_score": 0.92,
      "rationale": "Inter provides excellent readability for professional brands...",
      "use_cases": ["headings", "navigation", "CTAs"],
      "recommended_weights": ["400", "600", "700"]
    },
    "secondary_font": {
      /* similar structure for body text font */
    },
    "typography_system": {
      "heading_styles": {
        "h1": {
          "font_family": "Inter",
          "font_weight": "700",
          "font_size": "3rem",
          "line_height": "1.2",
          "margin_bottom": "1.5rem"
        },
        /* h2-h6 styles */
      },
      "text_styles": {
        "body": {
          "font_family": "Inter",
          "font_weight": "400",
          "font_size": "1rem",
          "line_height": "1.6"
        },
        /* caption, emphasis, etc. */
      }
    },
    "css_snippet": "/* Ready-to-use CSS */\n@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700');\n\nh1 { font-family: 'Inter', sans-serif; font-weight: 700; }"
  },
  "enhancement_metadata": {
    /* existing metadata */
    "typography_enhancement": {
      "method": "rule-based",
      "fonts_considered": 45,
      "selection_time": 1.23,
      "cache_hit": true,
      "api_calls": 0
    }
  }
}
```

### CLI Output Integration

```python
def integrate_typography_with_cli_output():
    """
    Integrate typography information into existing CLI output formats.

    Standard Output: Include typography in JSON result
    Debug Output: Show font selection process details
    Interactive Output: Typography-specific prompts and confirmations
    Session Output: Include typography state in session files

    Format Consistency:
    - Use existing enhancement metadata structure
    - Follow existing confidence scoring patterns
    - Maintain backward compatibility with typography-free outputs
    - Add typography data only when enhancement includes font selection
    """
```