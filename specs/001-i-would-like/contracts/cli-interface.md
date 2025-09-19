# CLI Interface Contract

**Date**: 2025-09-19
**Feature**: Brand Identity Design System Generator
**Contract Type**: Command Line Interface

## Command Specification

### Primary Command
```bash
python brand_identity_generator.py <input_file> [options]
```

### Arguments

#### Required Arguments
- `input_file`: Path to markdown file containing brand description
  - **Type**: File path (string)
  - **Validation**: Must exist and be readable
  - **Example**: `./brand-description.md`

#### Optional Arguments
- `--output` / `-o`: Output file path for generated JSON
  - **Type**: File path (string)
  - **Default**: Print to stdout
  - **Example**: `--output brand-identity.json`

- `--template` / `-t`: Generate sample markdown template
  - **Type**: Flag (boolean)
  - **Default**: False
  - **Effect**: Creates template file and exits
  - **Example**: `--template brand-template.md`

- `--validate-only` / `-v`: Validate input without generating output
  - **Type**: Flag (boolean)
  - **Default**: False
  - **Effect**: Reports validation results, no JSON output

- `--strict`: Enable strict validation mode
  - **Type**: Flag (boolean)
  - **Default**: False
  - **Effect**: Fail on warnings, require all optional fields

- `--debug`: Enable debug output
  - **Type**: Flag (boolean)
  - **Default**: False
  - **Effect**: Verbose logging to stderr

## Input Contract

### Markdown File Structure
Expected sections (case-insensitive, flexible formatting):

```markdown
# Brand Overview
[Brand name, mission, values, target audience]

# Visual Identity / Colors
[Color preferences, brand colors, emotional associations]

# Typography
[Font preferences, reading experience, text style]

# Brand Personality
[Personality traits, tone, formality level, innovation level]

# Logo Assets (Optional)
[Logo URLs, placement preferences, variations]

# Visual Style (Optional)
[Aesthetic preferences, imagery style, design elements]
```

### Input Validation Rules
1. **File Existence**: Input file must exist and be readable
2. **Content Length**: Minimum 100 characters, maximum 50KB
3. **Required Sections**: Must contain at least Brand Overview and Colors
4. **Brand Name**: Must be extractable from Brand Overview section
5. **Color Information**: Must contain at least one color description

## Output Contract

### Success Response (Exit Code 0)
```json
{
  "brandName": "string",
  "colorPalette": {
    "primary": {"hex": "#RRGGBB", "name": "string", "usage": "string"},
    "secondary": {"hex": "#RRGGBB", "name": "string", "usage": "string"},
    "neutral": {
      "dark": "#RRGGBB",
      "light": "#RRGGBB",
      "mid": "#RRGGBB"
    }
  },
  "typography": {
    "fontFamilies": {
      "heading": {"primary": "string", "fallback": "string", "weight": [400, 700]},
      "body": {"primary": "string", "fallback": "string", "weight": [400, 600]}
    }
  },
  "visualStyle": {
    "aesthetic": "string",
    "mood": ["string"],
    "imageryStyle": {
      "type": "string",
      "treatment": "string",
      "colorGrading": "string"
    }
  }
}
```

### Error Response (Exit Code 1)
```json
{
  "error": "string",
  "error_type": "string",
  "details": {
    "missing_sections": ["string"],
    "invalid_fields": ["string"],
    "suggestions": ["string"]
  }
}
```

### Template Generation (Exit Code 0)
When `--template` flag is used:
```markdown
# Brand Overview
**Brand Name**: [Your brand name here]
**Mission**: [What your brand stands for]
**Values**: [Core brand values]
**Target Audience**: [Who you serve]

# Visual Identity
**Primary Colors**: [e.g., "warm orange", "deep blue"]
**Secondary Colors**: [e.g., "soft gray", "cream white"]
**Color Emotions**: [e.g., "energetic", "trustworthy", "approachable"]

# Typography
**Heading Style**: [e.g., "bold", "elegant", "modern"]
**Body Text**: [e.g., "readable", "clean", "friendly"]
**Font Personality**: [e.g., "professional", "playful", "serious"]

# Brand Personality
**Formality Level**: [e.g., "professional", "casual", "formal"]
**Innovation Level**: [e.g., "cutting-edge", "traditional", "balanced"]
**Warmth Level**: [e.g., "friendly", "approachable", "professional"]
**Key Traits**: [e.g., "reliable", "innovative", "customer-focused"]

# Logo Assets (Optional)
**Primary Logo**: [URL or description]
**Logo Variations**: [light/dark versions, icon versions]
**Placement Preferences**: [where logo should appear]

# Visual Style (Optional)
**Design Aesthetic**: [e.g., "minimalist", "modern", "classic"]
**Imagery Style**: [e.g., "photography", "illustration", "mixed"]
**Design Elements**: [e.g., "clean lines", "rounded corners", "bold shapes"]
```

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | Input Error | Invalid input file or format |
| 2 | Processing Error | Error during content processing |
| 3 | Validation Error | Output validation failed |
| 4 | File Error | Cannot write output file |

## Error Messages

### Input Errors
- `ERROR: Input file '{filename}' not found`
- `ERROR: Input file '{filename}' is not readable`
- `ERROR: Input file is empty or too large (max 50KB)`
- `ERROR: Required section 'Brand Overview' not found`
- `ERROR: No brand name found in Brand Overview section`
- `ERROR: No color information found in Visual Identity section`

### Processing Errors
- `ERROR: Could not parse brand personality from description`
- `ERROR: No valid colors found in color descriptions`
- `ERROR: Typography preferences could not be determined`

### Validation Errors
- `ERROR: Generated JSON does not validate against schema`
- `ERROR: Invalid hex color code: '{hex_code}'`
- `ERROR: Brand name is required`

### File Errors
- `ERROR: Cannot write to output file '{filename}'`
- `ERROR: Output directory does not exist`

## Performance Requirements

- **Startup Time**: < 200ms for CLI initialization
- **Processing Time**: < 1 second for typical brand descriptions (< 10KB)
- **Memory Usage**: < 50MB peak memory usage
- **File Size**: Output JSON typically 1-5KB

## Compatibility

- **Python Version**: 3.11+
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Dependencies**: Minimal external dependencies
- **Character Encoding**: UTF-8 for all text processing

---
**CLI Contract Complete**: Interface specification ready for implementation and testing