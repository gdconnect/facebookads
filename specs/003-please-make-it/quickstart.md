# Quickstart Guide: Developer Configuration Management

**Date**: 2025-09-19
**Feature**: Developer Configuration Management
**Purpose**: Complete setup and usage guide for developers

## Quick Start (5 minutes)

### Step 1: Locate Configuration Section
Open `brand_identity_generator.py` and find the configuration section at the top:

```python
# ============================================================================
# DEVELOPER CONFIGURATION - Edit settings below for your environment
# ============================================================================

class DeveloperConfig(BaseModel):
    """Configuration settings for developers to customize the tool."""

    # LLM Provider Settings
    llm_provider: str = "openai"  # openai, anthropic, local
    llm_base_url: Optional[str] = None  # Custom API endpoint
    llm_model: str = "gpt-3.5-turbo"  # Model name
    llm_api_key: Optional[str] = None  # Uses env var if not set

    # Output Management
    default_output_dir: str = "./output"
    session_storage_dir: str = "./sessions"
    cache_dir: str = "./cache"

    # Performance Settings
    request_timeout: float = 30.0
    enable_caching: bool = True
    max_retries: int = 3

    # Enhancement Defaults
    default_enhancement_level: str = "moderate"
    debug_mode: bool = False
```

### Step 2: Customize Your Settings
Edit the configuration values for your environment:

```python
# Example: Switch to Anthropic with custom settings
llm_provider: str = "anthropic"
llm_model: str = "claude-3-sonnet-20240229"
default_output_dir: str = "/home/user/brand-outputs"
request_timeout: float = 45.0
debug_mode: bool = True
```

### Step 3: Set Environment Variables (Optional)
For sensitive settings like API keys:

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
```

### Step 4: Test Your Configuration
Run the tool to verify your settings work:

```bash
python brand_identity_generator.py examples/basic-brand.md --enhance
```

**Expected Output**: Enhanced brand identity saved to your configured output directory

## Configuration Scenarios

### Scenario 1: Development Environment Setup
**Use Case**: Developer setting up tool for local development with debugging

```python
# Development Configuration
llm_provider: str = "openai"
llm_model: str = "gpt-3.5-turbo"
default_output_dir: str = "./dev-output"
cache_dir: str = "./dev-cache"
request_timeout: float = 60.0  # Longer timeout for debugging
enable_caching: bool = False   # Fresh responses for testing
debug_mode: bool = True        # Verbose logging
```

Environment setup:
```bash
export OPENAI_API_KEY="sk-your-dev-key"
```

Usage:
```bash
# All outputs go to ./dev-output automatically
python brand_identity_generator.py test-brand.md --enhance
python brand_identity_generator.py test-brand.md --analyze-gaps
```

### Scenario 2: Production Deployment
**Use Case**: Production server with performance optimization

```python
# Production Configuration
llm_provider: str = "openai"
llm_model: str = "gpt-3.5-turbo"
default_output_dir: str = "/var/data/brand-tool/output"
session_storage_dir: str = "/var/data/brand-tool/sessions"
cache_dir: str = "/var/cache/brand-tool"
request_timeout: float = 20.0  # Shorter timeout for responsiveness
enable_caching: bool = True    # Performance optimization
max_retries: int = 5           # Reliability for network issues
debug_mode: bool = False       # Clean production logs
```

Environment setup:
```bash
export OPENAI_API_KEY="sk-prod-key"
```

### Scenario 3: Enterprise Custom Endpoint
**Use Case**: Company using Azure OpenAI or custom LLM endpoint

```python
# Enterprise Configuration
llm_provider: str = "openai"
llm_base_url: str = "https://your-company.openai.azure.com/openai/deployments/gpt-35-turbo"
llm_model: str = "gpt-35-turbo"  # Azure deployment name
default_output_dir: str = "/enterprise/brand-outputs"
request_timeout: float = 30.0
enable_caching: bool = True
```

Environment setup:
```bash
export OPENAI_API_KEY="your-azure-api-key"
```

### Scenario 4: Anthropic Claude Setup
**Use Case**: Developer preferring Claude for enhanced reasoning

```python
# Anthropic Configuration
llm_provider: str = "anthropic"
llm_model: str = "claude-3-sonnet-20240229"
default_output_dir: str = "./claude-output"
request_timeout: float = 45.0  # Claude can be slower but higher quality
enable_caching: bool = True
default_enhancement_level: str = "comprehensive"  # Take advantage of Claude's capabilities
```

Environment setup:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key"
```

### Scenario 5: Multiple Developer Team
**Use Case**: Team with shared settings but individual customizations

**Shared base configuration:**
```python
# Base team configuration
llm_provider: str = "openai"
llm_model: str = "gpt-3.5-turbo"
default_output_dir: str = "./team-output"
enable_caching: bool = True
max_retries: int = 3
```

**Individual developer overrides via environment:**
```bash
# Developer A - prefers different output location
export BRAND_TOOL_OUTPUT_DIR="/home/alice/my-brand-work"

# Developer B - debugging specific issues
export BRAND_TOOL_DEBUG_MODE="true"
export BRAND_TOOL_CACHE_ENABLED="false"

# Developer C - testing with Claude
export ANTHROPIC_API_KEY="sk-ant-..."
export BRAND_TOOL_LLM_PROVIDER="anthropic"
```

## Configuration Options Reference

### LLM Provider Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `llm_provider` | str | "openai" | LLM service: openai, anthropic, local |
| `llm_base_url` | str? | None | Custom API endpoint URL |
| `llm_model` | str | "gpt-3.5-turbo" | Model name for requests |
| `llm_api_key` | str? | None | API key (uses env var if not set) |

### Output Management

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `default_output_dir` | str | "./output" | Default directory for JSON files |
| `session_storage_dir` | str | "./sessions" | Directory for session files |
| `cache_dir` | str | "./cache" | Directory for LLM response cache |

### Performance Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `request_timeout` | float | 30.0 | Timeout for LLM API calls (seconds) |
| `enable_caching` | bool | True | Whether to cache LLM responses |
| `max_retries` | int | 3 | Maximum retry attempts for failed requests |
| `retry_backoff_factor` | float | 2.0 | Exponential backoff multiplier |

### Enhancement Defaults

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `default_enhancement_level` | str | "moderate" | Default level: minimal, moderate, comprehensive |
| `debug_mode` | bool | False | Enable debug logging and verbose output |
| `log_level` | str | "INFO" | Logging level: DEBUG, INFO, WARNING, ERROR |

## Environment Variable Overrides

Any configuration setting can be overridden with environment variables using the pattern:
`BRAND_TOOL_{SETTING_NAME}` (uppercase with underscores)

**LLM Provider Variables:**
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_BASE_URL` - Custom OpenAI endpoint
- `ANTHROPIC_API_KEY` - Anthropic API key
- `ANTHROPIC_BASE_URL` - Custom Anthropic endpoint

**Configuration Overrides:**
- `BRAND_TOOL_OUTPUT_DIR` - Override default_output_dir
- `BRAND_TOOL_DEBUG_MODE` - Override debug_mode ("true"/"false")
- `BRAND_TOOL_CACHE_ENABLED` - Override enable_caching ("true"/"false")
- `BRAND_TOOL_LLM_PROVIDER` - Override llm_provider

## Command-Line Override Examples

Configuration provides defaults, but CLI arguments always take precedence:

```bash
# Use configured defaults
python brand_identity_generator.py brand.md --enhance

# Override output location for this run
python brand_identity_generator.py brand.md --enhance -o /tmp/test-output.json

# Override LLM provider for this run
python brand_identity_generator.py brand.md --enhance --llm-provider anthropic

# Override enhancement level for this run
python brand_identity_generator.py brand.md --enhance --enhancement-level comprehensive
```

## Troubleshooting Configuration

### Common Issues

**Issue**: "Configuration Error in 'llm_provider': Invalid LLM provider"
**Solution**: Check that llm_provider is one of: openai, anthropic, local
```python
llm_provider: str = "openai"  # ✅ Correct
llm_provider: str = "gpt"     # ❌ Invalid
```

**Issue**: "Cannot create directory /path/to/output: Permission denied"
**Solution**: Ensure write permissions or choose different directory
```python
default_output_dir: str = "./output"           # ✅ Relative path
default_output_dir: str = "/home/user/output"  # ✅ With permissions
default_output_dir: str = "/root/output"       # ❌ No permissions
```

**Issue**: "Request timeout too low, may cause failures"
**Solution**: Increase timeout for slower networks or complex requests
```python
request_timeout: float = 5.0   # ❌ Too low
request_timeout: float = 30.0  # ✅ Reasonable
```

**Issue**: "API key not found for provider 'openai'"
**Solution**: Set API key in configuration or environment variable
```bash
export OPENAI_API_KEY="sk-your-key"
```
or
```python
llm_api_key: str = "sk-your-key"  # Not recommended for security
```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```python
debug_mode: bool = True
log_level: str = "DEBUG"
```

This provides:
- Configuration loading details
- Directory creation and validation steps
- LLM request and response information
- Performance timing information
- Cache hit/miss statistics

### Validation on Startup

The tool validates your configuration when it starts. If you see errors:

1. **Read the error message carefully** - it tells you exactly what's wrong
2. **Check the suggested fix** - most errors include specific solutions
3. **Verify file permissions** - ensure directories are writable
4. **Test with minimal config** - start with defaults and customize gradually

---
**Configuration Quickstart Complete**: Ready for developer customization and deployment