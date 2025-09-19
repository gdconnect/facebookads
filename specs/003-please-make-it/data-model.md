# Data Model: Developer Configuration Management

**Date**: 2025-09-19
**Feature**: Developer Configuration Management
**Phase**: 1 - Data Model Design

## Core Models

### DeveloperConfig
**Purpose**: Central configuration model for all developer-customizable settings

**Fields**:
- `llm_provider: str` - LLM service provider ("openai", "anthropic", "local")
- `llm_base_url: Optional[str]` - Custom API endpoint URL
- `llm_model: str` - Model name (e.g., "gpt-3.5-turbo", "claude-3-sonnet")
- `llm_api_key: Optional[str]` - API authentication key
- `default_output_dir: str` - Default directory for generated JSON files
- `session_storage_dir: str` - Directory for session persistence files
- `cache_dir: str` - Directory for LLM response cache
- `request_timeout: float` - Timeout for LLM API calls in seconds
- `enable_caching: bool` - Whether to cache LLM responses
- `max_retries: int` - Maximum retry attempts for failed requests
- `retry_backoff_factor: float` - Exponential backoff multiplier
- `default_enhancement_level: str` - Default enhancement level ("minimal", "moderate", "comprehensive")
- `debug_mode: bool` - Enable debug logging and verbose output
- `log_level: str` - Logging level ("DEBUG", "INFO", "WARNING", "ERROR")

**Validation Rules**:
- `llm_provider` must be in ["openai", "anthropic", "local"]
- `llm_base_url` must be valid URL format if provided
- `request_timeout` must be >= 1.0 seconds
- `max_retries` must be >= 0 and <= 10
- `retry_backoff_factor` must be >= 1.0 and <= 5.0
- `default_enhancement_level` must be in ["minimal", "moderate", "comprehensive"]
- `log_level` must be valid logging level
- Directory paths must be writable locations

**Relationships**:
- Provides settings for `LLMEnhancementEngine` initialization
- Controls `FileManager` output directory behavior
- Configures `RetryManager` backoff and attempt settings

### ResolvedConfig
**Purpose**: Final configuration after merging developer config with CLI arguments

**Fields**:
- All fields from `DeveloperConfig`
- `config_source: Dict[str, str]` - Source of each setting (config/cli/env/default)
- `validation_warnings: List[str]` - Non-critical configuration warnings
- `validation_errors: List[str]` - Critical configuration errors

**Validation Rules**:
- Inherits all validation from `DeveloperConfig`
- Must have no critical validation errors
- Warnings are logged but don't prevent operation

**State Transitions**:
- Created from `DeveloperConfig` + CLI arguments
- Validated before use in application
- Immutable after creation and validation

### ConfigurationError
**Purpose**: Custom exception for configuration-related errors

**Fields**:
- `message: str` - Human-readable error description
- `setting_name: Optional[str]` - Name of problematic setting
- `setting_value: Optional[Any]` - Invalid value that caused error
- `suggestion: Optional[str]` - Suggested fix for the error

**Validation Rules**:
- Message must be descriptive and actionable
- Suggestion should provide specific remediation steps

### DirectoryManager
**Purpose**: Manages creation and validation of configured directories

**Fields**:
- `directories: List[Path]` - List of directories to manage
- `validation_cache: Dict[str, bool]` - Cache of validation results
- `created_directories: Set[Path]` - Directories created by this instance

**Methods**:
- `ensure_exists()` - Create directories if they don't exist
- `validate_permissions()` - Check read/write permissions
- `cleanup_created()` - Remove directories created during this session

**Validation Rules**:
- All directories must be creatable with current permissions
- Parent directories must exist or be creatable
- Paths must not contain security-sensitive characters

### EnvironmentResolver
**Purpose**: Resolves environment variables with fallback logic

**Fields**:
- `provider_env_map: Dict[str, str]` - Mapping of providers to env var prefixes
- `env_cache: Dict[str, Optional[str]]` - Cache of environment variable values

**Methods**:
- `resolve_api_key(provider: str)` - Get API key for provider
- `resolve_base_url(provider: str)` - Get base URL for provider
- `get_all_env_overrides()` - Get all environment variable overrides

**Validation Rules**:
- Environment variable names must follow {PROVIDER}_{SETTING} pattern
- Cached values are refreshed only on explicit request

## Entity Relationships

```
DeveloperConfig
    ├── validates_into → ResolvedConfig
    ├── provides_settings_for → LLMEnhancementEngine
    ├── configures → DirectoryManager
    └── uses → EnvironmentResolver

ResolvedConfig
    ├── used_by → Application (main execution)
    ├── validates_against → ConfigurationError (on invalid state)
    └── provides_settings_to → All subsystems

DirectoryManager
    ├── manages → FileSystem directories
    ├── validates → Write permissions
    └── reports_errors_via → ConfigurationError

EnvironmentResolver
    ├── reads_from → OS environment variables
    ├── caches → Environment values
    └── provides_overrides_to → DeveloperConfig
```

## Validation Schema

### Configuration File Structure
```python
{
    "llm_provider": "openai",  # Required: string enum
    "llm_base_url": null,      # Optional: URL string or null
    "llm_model": "gpt-3.5-turbo",  # Required: string
    "llm_api_key": null,       # Optional: string or null (uses env var)
    "default_output_dir": "./output",  # Required: directory path
    "session_storage_dir": "./sessions",  # Required: directory path
    "cache_dir": "./cache",    # Required: directory path
    "request_timeout": 30.0,   # Required: float >= 1.0
    "enable_caching": true,    # Required: boolean
    "max_retries": 3,          # Required: int 0-10
    "retry_backoff_factor": 2.0,  # Required: float 1.0-5.0
    "default_enhancement_level": "moderate",  # Required: string enum
    "debug_mode": false,       # Required: boolean
    "log_level": "INFO"        # Required: string enum
}
```

### Environment Variable Schema
```bash
# LLM Provider Settings
OPENAI_API_KEY="sk-..."
OPENAI_BASE_URL="https://api.openai.com/v1"
ANTHROPIC_API_KEY="sk-ant-..."
ANTHROPIC_BASE_URL="https://api.anthropic.com"

# Override any config setting
BRAND_TOOL_OUTPUT_DIR="/custom/output"
BRAND_TOOL_CACHE_DIR="/tmp/cache"
BRAND_TOOL_DEBUG_MODE="true"
BRAND_TOOL_LOG_LEVEL="DEBUG"
```

### CLI Argument Precedence
1. **Explicit CLI arguments** (highest priority)
2. **Environment variables**
3. **Developer configuration**
4. **Built-in defaults** (lowest priority)

## Data Flow

### Configuration Loading Flow
```
1. Load DeveloperConfig from top of file
2. Apply environment variable overrides via EnvironmentResolver
3. Parse CLI arguments
4. Create ResolvedConfig with precedence rules
5. Validate ResolvedConfig and collect errors/warnings
6. Initialize DirectoryManager and ensure directories exist
7. Return validated configuration for application use
```

### Error Handling Flow
```
1. Validation error occurs during config loading
2. ConfigurationError created with descriptive message
3. Error includes setting name, invalid value, and suggestion
4. Application displays error and exits with helpful message
5. Developer fixes configuration and retries
```

### Directory Management Flow
```
1. ResolvedConfig provides directory paths
2. DirectoryManager validates each path
3. Directories created if they don't exist
4. Permissions validated with test file write
5. Validation results cached for performance
6. Any failures reported via ConfigurationError
```

## Integration Points

### With Existing LLMEnhancementEngine
- Provider selection from `llm_provider`
- API key from `llm_api_key` or environment variable
- Timeout from `request_timeout`
- Caching behavior from `enable_caching`
- Retry logic from `max_retries` and `retry_backoff_factor`

### With File Operations
- JSON output to `default_output_dir`
- Session files to `session_storage_dir`
- Cache files to `cache_dir`
- All file operations validate write permissions

### With CLI Argument Processing
- Configuration values as defaults for argparse
- CLI arguments override configuration settings
- Help text shows current configuration values
- Validation errors include both CLI and config context

---
**Data Model Complete**: All entities defined with validation rules and relationships