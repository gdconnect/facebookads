# Data Model: Article Outline Generator

**Feature**: Article Outline Generator
**Date**: 2025-09-21
**Phase**: Phase 1 (Design)

## Entity Overview

The Article Outline Generator processes markdown content descriptions and produces structured JSON outlines. The core data flow involves input normalization, content analysis, and structured output generation.

## Core Entities

### 1. InputModel (Pydantic)
**Purpose**: Normalized input from markdown content
**Fields**:
- `content: str` - The markdown content description
- `target_depth: int = 3` - Desired outline depth (1-6)
- `content_type_hint: Optional[str] = None` - Optional type hint ("article" | "story")
- `language_hint: Optional[str] = None` - Optional language hint
- `include_word_counts: bool = True` - Whether to generate word count estimates

**Validation Rules**:
- content must not be empty or whitespace-only
- target_depth must be between 1 and 6
- content_type_hint must be "article" or "story" if provided
- language_hint must be valid ISO 639-1 code if provided

**Relationships**: Source for ContentClassifier and OutlineGenerator

### 2. OutlineMetadata (Pydantic)
**Purpose**: Metadata about the generated outline
**Fields**:
- `content_type: Literal["article", "story"]` - Detected/classified content type
- `detected_language: str` - Detected language code (ISO 639-1)
- `depth: int` - Actual outline depth (1-6)
- `sections_count: int` - Total number of sections
- `generated_at: datetime` - ISO 8601 timestamp
- `notes: Optional[str] = None` - Optional generation notes

**Validation Rules**:
- content_type must be exactly "article" or "story"
- detected_language must be valid ISO 639-1 code
- depth must match actual section depth
- sections_count must be >= 0
- generated_at must be valid ISO timestamp

**Relationships**: Part of OutputModel envelope

### 3. Section (Pydantic - Recursive)
**Purpose**: Individual outline section with hierarchical support
**Fields**:
- `title: str` - Section title (required)
- `id: Optional[str] = None` - Stable slug/identifier
- `level: int = 1` - Heading level (1=H1, 2=H2, etc.)
- `summary: Optional[str] = None` - 1-3 sentence section synopsis
- `key_points: List[str] = []` - Bullet points for the section
- `word_count_estimate: Optional[int] = None` - Estimated word count
- `subsections: List[Section] = []` - Nested subsections

**Validation Rules**:
- title must be non-empty string
- level must be between 1 and 6
- id must be valid slug format if provided
- summary must be 1-3 sentences if provided
- word_count_estimate must be >= 0 if provided
- subsections must have level = parent.level + 1

**Relationships**: Self-referential (subsections), contained in OutputModel.outline

### 4. OutputModel (Pydantic)
**Purpose**: Complete outline response structure
**Fields**:
- `outline: List[Section]` - Top-level sections array
- `meta: OutlineMetadata` - Generation metadata

**Validation Rules**:
- outline must not be empty
- meta must be valid OutlineMetadata
- section levels must be consistent with hierarchy

**Relationships**: Wrapped in Agent Envelope

### 5. Agent Envelope (Constitutional)
**Purpose**: Standard agent response wrapper
**Fields**:
- `meta: EnvelopeMeta` - Agent execution metadata
- `input: InputModel` - Normalized input data
- `output: Optional[OutputModel]` - Generated outline (success case)
- `error: Optional[ErrorModel]` - Error details (failure case)

## Decision Tables

### 1. Content Type Classification
**Rules** (first-match precedence):
| Pattern | Content Type | Confidence | Why |
|---------|-------------|------------|-----|
| Contains: character, plot, story, narrative | story | 0.9 | Strong narrative indicators |
| Contains: how to, guide, tutorial, steps | article | 0.9 | Instructional content |
| Contains: analysis, review, opinion | article | 0.8 | Analytical content |
| Past tense dominance (>60%) | story | 0.7 | Narrative structure |
| Imperative mood dominance | article | 0.7 | Instructional structure |
| Default | article | 0.5 | Safe default |

### 2. Language Detection
**Rules** (first-match precedence):
| Pattern | Language | Confidence | Why |
|---------|----------|------------|-----|
| Stopwords: the, and, of, to, a | en | 0.9 | English indicators |
| Stopwords: le, la, de, et, un | fr | 0.9 | French indicators |
| Stopwords: der, die, das, und, ist | de | 0.9 | German indicators |
| Stopwords: el, la, de, y, un | es | 0.9 | Spanish indicators |
| Non-Latin characters detected | zh/ja/ar | 0.8 | Script-based detection |
| Default | en | 0.5 | Safe default |

### 3. Outline Template Selection
**Rules** (content-type based):
| Content Type | Template | Sections |
|-------------|----------|----------|
| article | Informational | Introduction, Main Topics, Conclusion |
| story | Narrative | Setup, Development, Climax, Resolution |
| article + "how-to" | Tutorial | Overview, Steps, Tips, Summary |
| article + "analysis" | Analytical | Background, Analysis, Implications |

## State Transitions

### Processing Flow
1. **Input** → Markdown normalization → `InputModel`
2. **Classification** → Content analysis → Content type + Language
3. **Template Selection** → Based on classification → Outline structure
4. **Section Generation** → Template population → `Section` hierarchy
5. **Metadata Generation** → Process summary → `OutlineMetadata`
6. **Output** → Envelope wrapping → `Agent Envelope`

### Error States
- **Invalid Input**: Empty content, invalid parameters
- **Classification Failure**: Ambiguous content, multiple patterns
- **Generation Failure**: Template instantiation errors
- **Validation Failure**: Schema compliance errors

## Performance Considerations

### Memory Efficiency
- Streaming JSON output for large outlines
- Lazy section generation (process headers first)
- Minimal text buffering (process line-by-line)

### Processing Speed
- Early classification decisions
- Template-based generation (avoid complex NLP)
- Regex compilation caching
- LLM fallback only when needed (<10% cases)

## Integration Points

### Input Sources
- CLI file input: `--input file.md`
- CLI stdin: `cat content.md | agent`
- Programmatic: `InputModel` direct instantiation

### Output Targets
- CLI stdout: JSON envelope
- File output: `--output file.json`
- Programmatic: `OutputModel` object

### External Dependencies
- **PydanticAI**: LLM fallback integration
- **Standard Library**: regex, json, datetime, pathlib
- **No external APIs**: Fully offline capable
