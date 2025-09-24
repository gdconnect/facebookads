# Data Model: BIE Enhancement - Complete Implementation

**Phase 1 Output**: Entity definitions and data model for BIE enhancements

## Enhanced Data Entities

### ComparisonResult
**Purpose**: Represents the output of comparing multiple business ideas with ranking and analysis.

**Fields**:
- `ideas: List[EvaluatedIdea]` - List of all evaluated ideas in original order
- `ranking: List[Dict[str, Any]]` - Ranked comparison data with scores and analysis
- `recommendation: str` - Summary recommendation indicating which idea to pursue
- `comparison_summary: str` - Overall comparison summary with patterns and insights

**Validation Rules**:
- `ideas` must contain 2-10 evaluated ideas
- `ranking` must be sorted by overall score (descending)
- `recommendation` must be non-empty string
- `comparison_summary` must be non-empty string

**Relationships**:
- Contains multiple `EvaluatedIdea` entities (composition)
- Each ranking entry references an `EvaluatedIdea` by name
- No external entity relationships

### Enhanced BlindspotRule (Extension)
**Purpose**: Expanded blindspot detection patterns including new agency-specific patterns.

**New Patterns**:
```python
{
    "pattern": r"monetization.*later|figure.*out.*pricing",
    "flag": '"We\'ll figure out monetization later"',
    "advice": "Charge from day one with clear pricing strategy"
},
{
    "pattern": r"perfect|polish|ready",
    "flag": '"Perfect before launch" trap',
    "advice": "Ship in 30 days or scope down"
}
```

**Validation Rules**:
- Pattern must be valid regex
- Flag must be non-empty descriptive string
- Advice must provide actionable guidance
- All patterns case-insensitive by default

**State Transitions**:
- Pattern detected → Flag generated → Advice provided → Red flag added to insights

### MarkdownFormatter (Conceptual Entity)
**Purpose**: Handles conversion of evaluation results to enhanced markdown format with emojis and structure.

**Key Methods** (implemented as functions in single file):
- `generate_enhanced_markdown(evaluated: EvaluatedIdea) -> str`
- `_get_visual_indicator(score: int) -> str` (✅, ⚠️, ❌)
- `_format_checkbox_items(items: List[str]) -> str`
- `_ensure_min_red_flags(blindspots: List[str]) -> List[str]`

**Formatting Rules**:
- Title format: `# [Idea Name] - Grade: [Grade] ([Score]/100)`
- Emoji prefixes for all sections (📊, 💡, 🎯, ❗, 🚨, ✅, 🚀, 📈, 🔄)
- Visual indicators based on score thresholds (70+: ✅, 40-69: ⚠️, <40: ❌)
- Checkbox format for quick wins: `- [ ] actionable item`
- Minimum 3 red flags with default padding if needed

### Ranking Entry Structure
**Purpose**: Individual ranking data for each idea in comparison results.

**Fields**:
- `rank: int` - Position in ranking (1-based)
- `name: str` - Business idea name
- `grade: str` - Overall grade (A-F)
- `total_score: float` - Calculated overall score
- `scalability: int` - Scalability score (0-100)
- `complexity: int` - Complexity score (0-100, lower is better)
- `risk: int` - Risk score (0-100, lower is better)
- `strengths: List[str]` - Relative strengths (max 3)
- `weaknesses: List[str]` - Relative weaknesses (max 3)

**Validation Rules**:
- `rank` must be positive integer
- `grade` must be one of A, B, C, D, F
- `total_score` calculated as: scalability - complexity - risk
- Score fields must be 0-100 range
- Strengths/weaknesses lists limited to 3 items each

## Existing Entity Enhancements

### EvaluatedIdea (No Changes)
**Status**: No modifications required to existing model
**Rationale**: Enhanced markdown output uses existing fields without schema changes

### Envelope (No Changes)
**Status**: No modifications required to existing model
**Rationale**: ComparisonResult will be wrapped in same Envelope pattern

### ActionableInsights (Minor Enhancement)
**Change**: Enhanced red_flags validation to ensure minimum 3 items
**Implementation**: Helper method `_ensure_min_red_flags()` provides default padding
**Backwards Compatibility**: ✅ Maintained, only enhancement to validation logic

## Data Flow Diagrams

### Enhanced Markdown Generation Flow
```
EvaluatedIdea → MarkdownFormatter → Enhanced Markdown Output
              ↓
         Visual Indicators (✅⚠️❌)
              ↓
         Emoji Section Headers
              ↓
         Checkbox Action Items
```

### Multi-Idea Comparison Flow
```
List[Path] → Multiple EvaluatedIdea → ComparisonResult
                    ↓                      ↓
              Individual Scores      Ranking Analysis
                    ↓                      ↓
              Strengths/Weaknesses   Summary Recommendation
```

### Blindspot Detection Flow
```
RawIdea → Enhanced BlindspotRules → Detected Patterns
            ↓                           ↓
    Pattern Matching                Red Flags
            ↓                           ↓
    Specific Advice              ActionableInsights
```

## Schema Validation

### ComparisonResult JSON Schema
```json
{
  "type": "object",
  "required": ["ideas", "ranking", "recommendation", "comparison_summary"],
  "properties": {
    "ideas": {
      "type": "array",
      "minItems": 2,
      "maxItems": 10,
      "items": {"$ref": "#/definitions/EvaluatedIdea"}
    },
    "ranking": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["rank", "name", "grade", "total_score"],
        "properties": {
          "rank": {"type": "integer", "minimum": 1},
          "grade": {"type": "string", "enum": ["A", "B", "C", "D", "F"]},
          "total_score": {"type": "number"},
          "strengths": {"type": "array", "maxItems": 3},
          "weaknesses": {"type": "array", "maxItems": 3}
        }
      }
    },
    "recommendation": {"type": "string", "minLength": 1},
    "comparison_summary": {"type": "string", "minLength": 1}
  }
}
```

## Constitutional Compliance

### Article II - Contract-First ✅
- All new entities follow Pydantic v2 model patterns
- JSON schemas will be auto-generated from models
- Type safety maintained throughout

### Article VII - Type Safety ✅
- Full type hints on all new methods and classes
- Defensive programming with proper None checks
- Exhaustive conditionals with proper else clauses

### Article VIII - Testing ✅
- Each new entity will have corresponding test coverage
- Golden test files for markdown output formatting
- Contract tests for ComparisonResult schema validation
- Integration tests for multi-file comparison workflow

## Implementation Notes

### Single-File Integration
- All new models added to existing `agents/bie/bie.py`
- No new files created, maintaining constitutional compliance
- Existing imports and structure preserved

### Backwards Compatibility
- No changes to existing model schemas
- Additive changes only (new ComparisonResult model)
- Existing JSON output format unchanged
- New functionality available via CLI flags only

### Performance Considerations
- Markdown generation is O(1) per idea (deterministic formatting)
- Comparison is O(n log n) for sorting, O(n²) for relative analysis
- Memory usage linear with number of ideas compared
- File I/O minimized through efficient Path handling
