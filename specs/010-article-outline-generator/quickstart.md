# Quickstart: Article Outline Generator

**Feature**: Article Outline Generator
**Date**: 2025-09-21
**Purpose**: Validation scenarios for testing the implemented agent

## Installation & Setup

```bash
# Navigate to the agent directory
cd agents/article_outline_generator

# Install dependencies (if any beyond stdlib)
pip install pydantic>=2 pydantic-ai

# Verify agent structure
python article_outline_generator.py selfcheck
```

## Basic Usage Examples

### 1. Simple Article Outline
```bash
# Input: Basic article description
echo "# Sustainable Gardening Practices

This article will cover practical approaches to sustainable gardening including composting techniques, water conservation methods, native plant selection, and organic pest control strategies." | python article_outline_generator.py run --input-type markdown

# Expected output: JSON envelope with article-type outline
# - Introduction section
# - Main topics: Composting, Water Conservation, Plant Selection, Pest Control
# - Conclusion section
# - Metadata: content_type="article", detected_language="en"
```

### 2. Story Outline Generation
```bash
# Input: Fictional story description
echo "# The Mars Expedition

A science fiction story about the first human mission to Mars. The crew faces unexpected challenges when their communication system fails, forcing them to make critical decisions independently. Character development focuses on the mission commander dealing with leadership under pressure and the team's growing bonds of trust." | python article_outline_generator.py run --input-type markdown

# Expected output: JSON envelope with story-type outline
# - Setup: Introduction of characters and mission
# - Rising Action: Communication failure and initial challenges
# - Climax: Critical decision point under pressure
# - Resolution: Team bonds and mission outcome
# - Metadata: content_type="story", detected_language="en"
```

### 3. How-To Article with Depth Control
```bash
# Input: Instructional content with custom depth
python article_outline_generator.py run --input-type json --target-depth 4 << 'EOF'
{
  "content": "# How to Build a Personal Website\n\nA comprehensive guide for beginners covering domain registration, hosting selection, website builders vs. custom coding, content planning, SEO basics, and ongoing maintenance.",
  "target_depth": 4,
  "include_word_counts": true
}
EOF

# Expected output: JSON envelope with 4-level deep outline
# - Depth 4 subsections for detailed how-to structure
# - Word count estimates for each section
# - How-to specific template applied
```

## Validation Scenarios

### Scenario 1: Content Type Classification
**Test**: Verify automatic detection of article vs. story content
```bash
# Article indicators
echo "# Market Analysis Report\nThis analysis examines current trends..." | python article_outline_generator.py run
# Should detect content_type="article"

# Story indicators
echo "# The Lost Key\nOnce upon a time, Sarah discovered..." | python article_outline_generator.py run
# Should detect content_type="story"
```

### Scenario 2: Language Detection
**Test**: Verify language detection capability
```bash
# English content
echo "# Cooking Tips\nLearn essential cooking techniques..." | python article_outline_generator.py run
# Should detect detected_language="en"

# Spanish content (if supported)
echo "# Consejos de Cocina\nAprende técnicas esenciales de cocina..." | python article_outline_generator.py run
# Should detect detected_language="es"
```

### Scenario 3: Depth Level Control
**Test**: Verify outline depth respects target_depth parameter
```bash
# Shallow outline (depth 2)
python article_outline_generator.py run --target-depth 2 << 'EOF'
# Complex Technology Guide
Comprehensive coverage of machine learning, data science, and AI development
EOF
# Should produce max 2-level hierarchy

# Deep outline (depth 5)
python article_outline_generator.py run --target-depth 5 << 'EOF'
# Detailed Academic Paper
In-depth analysis requiring extensive sub-categorization
EOF
# Should produce up to 5-level hierarchy
```

### Scenario 4: Error Handling
**Test**: Verify graceful error handling
```bash
# Empty input
echo "" | python article_outline_generator.py run
# Should return error in envelope.error field

# Invalid depth
python article_outline_generator.py run --target-depth 10 << 'EOF'
# Simple Article
Basic content description
EOF
# Should return validation error
```

### Scenario 5: Performance Validation
**Test**: Verify performance meets constitutional requirements
```bash
# Measure execution time (should be <5s)
time python article_outline_generator.py run << 'EOF'
# Large Content Description
[... extensive content description ...]
EOF

# Verify STRICT mode (no LLM calls by default)
python article_outline_generator.py run --strict << 'EOF'
# Clear Article Content
Simple, unambiguous article description
EOF
# Should complete without LLM calls
```

## Success Criteria

### ✅ Functional Validation
- [ ] Article content correctly classified as content_type="article"
- [ ] Story content correctly classified as content_type="story"
- [ ] English content detected as detected_language="en"
- [ ] Outline depth respects target_depth parameter (1-6)
- [ ] Generated sections include title, summary, key_points
- [ ] Section IDs are stable slug format
- [ ] Word count estimates provided when requested
- [ ] Nested subsections have correct level increments

### ✅ Constitutional Compliance
- [ ] Agent runs as single .py file
- [ ] Input/output conforms to JSON schemas
- [ ] Agent Envelope structure followed
- [ ] STRICT mode works (no LLM calls for clear input)
- [ ] Performance <5s for typical input
- [ ] Error handling returns structured ErrorModel
- [ ] JSONL logging to STDERR

### ✅ Quality Validation
- [ ] Generated outlines are logically structured
- [ ] Section titles are descriptive and relevant
- [ ] Key points are actionable and specific
- [ ] Word count estimates are reasonable
- [ ] No duplicate section IDs
- [ ] Consistent formatting and style

### ✅ Edge Case Handling
- [ ] Empty input returns appropriate error
- [ ] Invalid parameters return validation errors
- [ ] Ambiguous content handled gracefully (LLM fallback)
- [ ] Very short content produces minimal viable outline
- [ ] Very long content processes within time limits

## Acceptance Checklist

Before considering the feature complete:

1. **Schema Compliance**: All outputs validate against contracts/
2. **Performance**: Execution time <5s for all quickstart examples
3. **Constitutional**: Passes all constitutional requirements
4. **Error Handling**: All error scenarios return structured errors
5. **Documentation**: README.md covers usage and examples
6. **Testing**: Contract, integration, and golden tests pass
7. **Quality Gates**: ruff, black, mypy --strict, pylint all pass

## Test Data Files

Sample test files should be created in `tests/fixtures/`:
- `sample_article.md` - Clear article content
- `sample_story.md` - Clear story content
- `ambiguous_content.md` - Requires LLM classification
- `multilingual_content.md` - Non-English content
- `minimal_content.md` - Edge case: very short input
- `complex_content.md` - Edge case: very detailed input
