# Brand Identity Generator Documentation

AI-powered brand identity enhancement tool with automatic font selection and color palette generation.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation & Setup](#installation--setup)
- [Core Features](#core-features)
- [Font Selection & Google Fonts API](#font-selection--google-fonts-api)
- [CLI Reference](#cli-reference)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Quick Start

Get running in under 5 minutes:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create a Brand File
```bash
cat > my-brand.md << EOF
# My Brand

**Primary Color**: #2563eb
**Brand Voice**: professional, modern, trustworthy
**Target Audience**: enterprise decision makers
**Industry**: Technology

## About
A technology company focused on reliable software solutions.
EOF
```

### 3. Basic Enhancement
```bash
python brand_identity_generator.py my-brand.md --enhance
```

### 4. With Font Selection (Recommended)
```bash
# Set up Google Fonts API (optional but recommended)
export GOOGLE_FONTS_API_KEY=your_api_key_here

# Enhanced typography with font selection
python brand_identity_generator.py my-brand.md --enhance --enhancement-level comprehensive
```

## Installation & Setup

### Requirements
- Python 3.11+
- Dependencies: `pydantic`, `openai`, `anthropic`, `requests`

### Basic Installation
```bash
# Clone or download the tool
curl -O https://raw.githubusercontent.com/your-repo/brand_identity_generator.py

# Install dependencies
pip install pydantic openai anthropic requests
```

### Environment Variables (Optional)
```bash
# LLM API Keys (for enhanced features)
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_anthropic_key

# Google Fonts API Key (for font selection)
export GOOGLE_FONTS_API_KEY=your_google_fonts_key

# Custom directories
export BRAND_TOOL_OUTPUT_DIR=./output
export BRAND_TOOL_SESSION_DIR=./sessions
export BRAND_TOOL_CACHE_DIR=./cache
```

## Core Features

### 1. Color Enhancement
Converts color descriptions into specific hex codes with usage guidelines:

```bash
# Input: "Primary Color: blue"
# Output: Specific palette with hex codes, tints, shades
python brand_identity_generator.py brand.md --enhance
```

### 2. Font Selection & Typography
**NEW**: AI-powered Google Font recommendations based on brand personality:

- **Automatic Font Matching**: Analyzes brand voice and selects appropriate Google Fonts
- **Typography Hierarchy**: Complete H1-H6 and text style system
- **CSS Generation**: Ready-to-use CSS with Google Fonts imports
- **Confidence Scoring**: Quality indicators for font recommendations

```bash
# Basic typography
python brand_identity_generator.py brand.md --enhance --enhancement-level moderate

# Comprehensive typography with multiple fonts
python brand_identity_generator.py brand.md --enhance --enhancement-level comprehensive
```

### 3. Gap Analysis
Identifies missing brand elements:

```bash
python brand_identity_generator.py brand.md --analyze-gaps
```

### 4. Interactive Enhancement
Step-by-step guided enhancement:

```bash
python brand_identity_generator.py brand.md --enhance --interactive
```

### 5. Session Management
Save and resume enhancement workflows:

```bash
# Save session
python brand_identity_generator.py brand.md --enhance --save-session session.json

# Resume session
python brand_identity_generator.py --load-session session.json
```

## Font Selection & Google Fonts API

### Google Fonts API Setup

1. **Get API Key** (Free):
   - Visit [Google Fonts Developer API](https://developers.google.com/fonts/docs/developer_api)
   - Create a project in Google Cloud Console
   - Enable Google Fonts Developer API
   - Create credentials (API Key)

2. **Set Environment Variable**:
   ```bash
   export GOOGLE_FONTS_API_KEY=your_api_key_here
   ```

3. **Verify Setup**:
   ```bash
   python brand_identity_generator.py test-brand.md --enhance --debug
   # Look for "Google Fonts API: Connected" in output
   ```

### How Font Selection Works

The tool analyzes your brand characteristics and selects appropriate fonts:

**Brand Voice → Font Categories:**
- `professional, corporate` → Sans-serif fonts (Inter, Roboto, Open Sans)
- `elegant, sophisticated` → Serif fonts (Playfair Display, Lora, Crimson Text)
- `creative, artistic` → Display fonts (Montserrat, Poppins, Nunito)
- `friendly, approachable` → Rounded fonts (Source Sans Pro, Lato, Ubuntu)

**Enhancement Levels:**
- **Minimal**: Primary font only
- **Moderate**: Primary + secondary fonts with basic hierarchy
- **Comprehensive**: Complete typography system with heading styles, text styles, and CSS

### Font Selection Output

```json
{
  "typography": {
    "primary_font": {
      "google_font": {
        "family": "Inter",
        "category": "sans-serif",
        "variants": ["300", "400", "500", "600", "700"]
      },
      "confidence_score": 0.95,
      "rationale": "Inter's professional and modern characteristics align with your brand voice...",
      "use_cases": ["headings", "body text"],
      "recommended_weights": ["400", "600"]
    },
    "typography_system": {
      "heading_styles": {
        "h1": {
          "font_family": "Inter",
          "font_weight": "600",
          "font_size": "2.5rem",
          "line_height": "1.2"
        }
      }
    },
    "css_snippet": "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');\n\nh1 { font-family: 'Inter', sans-serif; font-weight: 600; }"
  }
}
```

### Offline Mode
Font selection works without Google Fonts API using built-in fallbacks:
- Inter (professional)
- Open Sans (friendly)
- Roboto (neutral)
- Arial (universal fallback)

## CLI Reference

### Basic Commands

```bash
# Gap analysis only
python brand_identity_generator.py BRAND_FILE --analyze-gaps

# Basic enhancement (colors only)
python brand_identity_generator.py BRAND_FILE --enhance

# Enhanced typography
python brand_identity_generator.py BRAND_FILE --enhance --enhancement-level comprehensive

# Interactive mode
python brand_identity_generator.py BRAND_FILE --enhance --interactive
```

### Enhancement Levels

- `--enhancement-level minimal`: Basic color enhancement only
- `--enhancement-level moderate`: Colors + basic typography
- `--enhancement-level comprehensive`: Complete brand system with fonts

### LLM Providers

```bash
# OpenAI (default)
python brand_identity_generator.py brand.md --enhance --llm-provider openai

# Anthropic
python brand_identity_generator.py brand.md --enhance --llm-provider anthropic

# Local LLM
python brand_identity_generator.py brand.md --enhance --llm-provider local --custom-endpoint http://localhost:8000/v1
```

### Session Management

```bash
# Save session
python brand_identity_generator.py brand.md --enhance --save-session session.json

# Load session
python brand_identity_generator.py --load-session session.json

# Resume with modifications
python brand_identity_generator.py --load-session session.json --enhancement-level comprehensive
```

### Debug Mode

```bash
python brand_identity_generator.py brand.md --enhance --debug
```

## Configuration

### Configuration File
Create `brand_config.json` for persistent settings:

```json
{
  "llm_provider": "openai",
  "enhancement_level": "moderate",
  "output_directory": "./output",
  "session_directory": "./sessions",
  "cache_directory": "./cache",
  "request_timeout": 30.0,
  "max_retries": 3,
  "enable_caching": true,
  "font_cache_ttl_hours": 24,
  "font_cache_max_size_mb": 50
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | None | OpenAI API key for GPT models |
| `ANTHROPIC_API_KEY` | None | Anthropic API key for Claude models |
| `GOOGLE_FONTS_API_KEY` | None | Google Fonts API key for font selection |
| `BRAND_TOOL_LLM_PROVIDER` | "openai" | Default LLM provider |
| `BRAND_TOOL_OUTPUT_DIR` | "./output" | Output directory for enhanced files |
| `BRAND_TOOL_SESSION_DIR` | "./sessions" | Session save directory |
| `BRAND_TOOL_CACHE_DIR` | "./cache" | Cache directory for fonts and API responses |

## Examples

### Basic Brand Enhancement

**Input** (`tech-startup.md`):
```markdown
# TechFlow

**Primary Color**: blue
**Secondary Color**: gray
**Brand Voice**: innovative, reliable, user-focused
**Target Audience**: software developers
**Industry**: Developer Tools
```

**Command**:
```bash
python brand_identity_generator.py tech-startup.md --enhance --enhancement-level comprehensive
```

**Output** (key sections):
```json
{
  "brandName": "TechFlow",
  "colorPalette": {
    "primary": "#2563eb",
    "secondary": "#6b7280",
    "accent": "#3b82f6"
  },
  "typography": {
    "primary_font": {
      "google_font": {
        "family": "Inter",
        "category": "sans-serif"
      },
      "confidence_score": 0.92,
      "rationale": "Inter's technical precision and readability make it ideal for developer tools..."
    }
  }
}
```

### E-commerce Brand

**Input** (`fashion-brand.md`):
```markdown
# Elegance Co

**Primary Color**: dusty rose
**Brand Voice**: sophisticated, elegant, timeless
**Target Audience**: fashion-conscious women 25-45
**Industry**: Fashion & Retail
```

**Command**:
```bash
python brand_identity_generator.py fashion-brand.md --enhance
```

**Font Selection** (automatic):
- Primary: Playfair Display (serif, elegant)
- Secondary: Source Sans Pro (clean, readable)

### Creative Agency

**Input**:
```markdown
# Creative Spark

**Brand Voice**: bold, creative, energetic, inspiring
**Target Audience**: creative professionals and startups
**Industry**: Creative Services
```

**Font Selection** (automatic):
- Primary: Montserrat (modern, geometric)
- Accent: Nunito (friendly, rounded)

## Troubleshooting

### Common Issues

**1. Google Fonts API Not Working**
```bash
# Check API key
echo $GOOGLE_FONTS_API_KEY

# Test API access
curl "https://www.googleapis.com/webfonts/v1/webfonts?key=$GOOGLE_FONTS_API_KEY" | head

# Verify in debug mode
python brand_identity_generator.py brand.md --enhance --debug
```

**2. No Font Recommendations**
- Ensure `--enhancement-level moderate` or `comprehensive`
- Check brand voice is specified in markdown file
- Verify tool is using recent version with font selection

**3. LLM API Errors**
```bash
# Check API keys
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Try different provider
python brand_identity_generator.py brand.md --enhance --llm-provider anthropic
```

**4. Permission Errors**
```bash
# Create output directories
mkdir -p output sessions cache

# Check permissions
ls -la output/ sessions/ cache/
```

### Performance Tips

1. **Enable Caching**: Speeds up repeated operations
   ```bash
   export BRAND_TOOL_CACHE_DIR=./cache
   ```

2. **Use Moderate Enhancement**: Faster than comprehensive
   ```bash
   python brand_identity_generator.py brand.md --enhance --enhancement-level moderate
   ```

3. **Google Fonts API**: Improves font selection quality
   ```bash
   export GOOGLE_FONTS_API_KEY=your_key
   ```

### Getting Help

1. **Debug Mode**: Shows detailed processing steps
   ```bash
   python brand_identity_generator.py brand.md --enhance --debug
   ```

2. **Validate Input**: Check your brand file format
   ```bash
   python brand_identity_generator.py brand.md --analyze-gaps
   ```

3. **Test Setup**: Verify configuration
   ```bash
   python brand_identity_generator.py --help
   ```

For complex issues, run with `--debug` and check the detailed output for specific error messages and processing steps.