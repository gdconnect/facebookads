#!/usr/bin/env python3
"""
LLM-Enhanced Brand Identity Processing Tool

A comprehensive brand identity generator with AI-powered enhancement capabilities.
Supports gap analysis, semantic color generation, and unified design strategies.
"""

import argparse
import json
import sys
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, validator
import re
import os


# ============================================================================
# DEVELOPER CONFIGURATION - Edit settings below for your environment
# ============================================================================

class DeveloperConfig(BaseModel):
    """Configuration settings for developers to customize the tool."""

    # LLM Provider Settings
    llm_provider: str = "openai"  # openai, anthropic, local
    llm_base_url: Optional[str] = None  # Custom API endpoint URL
    llm_model: str = "gpt-3.5-turbo"  # Model name (e.g., gpt-3.5-turbo, claude-3-sonnet)
    llm_api_key: Optional[str] = None  # API key (uses environment variable if not set)

    # Output Management
    default_output_dir: str = "./output"  # Default directory for generated JSON files
    session_storage_dir: str = "./sessions"  # Directory for session persistence files
    cache_dir: str = "./cache"  # Directory for LLM response cache

    # Performance Settings
    request_timeout: float = 30.0  # Timeout for LLM API calls in seconds (>= 1.0)
    enable_caching: bool = True  # Whether to cache LLM responses for performance
    max_retries: int = 3  # Maximum retry attempts for failed requests (0-10)
    retry_backoff_factor: float = 2.0  # Exponential backoff multiplier (1.0-5.0)

    # Enhancement Defaults
    default_enhancement_level: str = "moderate"  # minimal, moderate, comprehensive
    debug_mode: bool = False  # Enable debug logging and verbose output
    log_level: str = "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR

    class Config:
        extra = "forbid"  # Prevent unknown fields

    @validator('llm_provider')
    def validate_llm_provider(cls, v):
        valid_providers = ["openai", "anthropic", "local"]
        if v not in valid_providers:
            raise ValueError(f"Invalid LLM provider '{v}'. Valid options: {', '.join(valid_providers)}")
        return v

    @validator('llm_base_url')
    def validate_base_url(cls, v):
        if v is not None and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError(f"Invalid base URL format '{v}'. Must start with http:// or https://")
        return v

    @validator('request_timeout')
    def validate_timeout(cls, v):
        if v < 1.0:
            raise ValueError(f"Request timeout must be >= 1.0 seconds, got {v}")
        return v

    @validator('max_retries')
    def validate_max_retries(cls, v):
        if not (0 <= v <= 10):
            raise ValueError(f"Max retries must be between 0 and 10, got {v}")
        return v

    @validator('retry_backoff_factor')
    def validate_backoff_factor(cls, v):
        if not (1.0 <= v <= 5.0):
            raise ValueError(f"Retry backoff factor must be between 1.0 and 5.0, got {v}")
        return v

    @validator('default_enhancement_level')
    def validate_enhancement_level(cls, v):
        valid_levels = ["minimal", "moderate", "comprehensive"]
        if v not in valid_levels:
            raise ValueError(f"Invalid enhancement level '{v}'. Valid options: {', '.join(valid_levels)}")
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if v not in valid_levels:
            raise ValueError(f"Invalid log level '{v}'. Valid options: {', '.join(valid_levels)}")
        return v

    def __init__(self, **data):
        # Apply environment variable fallbacks before validation
        if not data.get('llm_api_key'):
            provider = data.get('llm_provider', 'openai').upper()
            data['llm_api_key'] = os.getenv(f"{provider}_API_KEY")

        if not data.get('llm_base_url'):
            provider = data.get('llm_provider', 'openai').upper()
            data['llm_base_url'] = os.getenv(f"{provider}_BASE_URL")

        # Apply configuration overrides from environment variables
        env_overrides = {
            'llm_provider': os.getenv('BRAND_TOOL_LLM_PROVIDER'),
            'default_output_dir': os.getenv('BRAND_TOOL_OUTPUT_DIR'),
            'cache_dir': os.getenv('BRAND_TOOL_CACHE_DIR'),
            'session_storage_dir': os.getenv('BRAND_TOOL_SESSION_DIR'),
            'debug_mode': os.getenv('BRAND_TOOL_DEBUG_MODE'),
            'log_level': os.getenv('BRAND_TOOL_LOG_LEVEL'),
            'enable_caching': os.getenv('BRAND_TOOL_CACHE_ENABLED'),
        }

        for key, env_value in env_overrides.items():
            if env_value is not None and key not in data:
                if key in ['debug_mode', 'enable_caching']:
                    data[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                else:
                    data[key] = env_value

        super().__init__(**data)


class ResolvedConfig(BaseModel):
    """Final configuration after merging developer config with CLI arguments."""

    # All fields from DeveloperConfig
    llm_provider: str
    llm_base_url: Optional[str]
    llm_model: str
    llm_api_key: Optional[str]
    default_output_dir: str
    session_storage_dir: str
    cache_dir: str
    request_timeout: float
    enable_caching: bool
    max_retries: int
    retry_backoff_factor: float
    default_enhancement_level: str
    debug_mode: bool
    log_level: str

    # Source tracking and validation
    config_source: Dict[str, str] = Field(default_factory=dict)
    validation_warnings: List[str] = Field(default_factory=list)
    validation_errors: List[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""

    def __init__(self, message: str, setting_name: Optional[str] = None,
                 setting_value: Optional[Any] = None, suggestion: Optional[str] = None):
        self.message = message
        self.setting_name = setting_name
        self.setting_value = setting_value
        self.suggestion = suggestion

        # Format error message
        error_parts = [message]
        if setting_name and setting_value is not None:
            error_parts.append(f"  Setting: '{setting_name}'")
            error_parts.append(f"  Value: '{setting_value}'")
        if suggestion:
            error_parts.append(f"  Suggestion: {suggestion}")

        super().__init__("\n".join(error_parts))


class DirectoryManager:
    """Manages creation and validation of configured directories."""

    def __init__(self, directories: Optional[List[str]] = None):
        self.directories = [Path(d) for d in (directories or [])]
        self.validation_cache: Dict[str, bool] = {}
        self.created_directories: set = set()

    def ensure_directory_exists(self, directory: str) -> None:
        """Ensure a single directory exists and is writable."""
        path = Path(directory)
        cache_key = str(path)

        if cache_key in self.validation_cache:
            return

        try:
            # Create directory if it doesn't exist
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                self.created_directories.add(path)

            # Test write permission
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()

            self.validation_cache[cache_key] = True

        except PermissionError:
            raise ConfigurationError(
                f"No write permission for directory: {path}",
                setting_name="directory_permission",
                setting_value=str(path),
                suggestion="Check directory permissions or choose a different location"
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to create directory: {path}",
                setting_name="directory_creation",
                setting_value=str(path),
                suggestion=f"Error: {e}"
            )

    def ensure_exists(self) -> None:
        """Create directories if they don't exist and validate permissions."""
        for directory in self.directories:
            cache_key = str(directory)

            if cache_key in self.validation_cache:
                continue

            try:
                # Create directory if it doesn't exist
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    self.created_directories.add(directory)

                # Test write permission
                test_file = directory / ".write_test"
                test_file.touch()
                test_file.unlink()

                self.validation_cache[cache_key] = True

            except PermissionError:
                raise ConfigurationError(
                    f"No write permission for directory: {directory}",
                    suggestion="Check directory permissions or choose a different location"
                )
            except Exception as e:
                raise ConfigurationError(
                    f"Cannot create or access directory {directory}: {e}",
                    suggestion="Ensure parent directory exists and you have write permissions"
                )

    def validate_permissions(self) -> None:
        """Check read/write permissions for all directories."""
        self.ensure_exists()

    def cleanup_created(self) -> None:
        """Remove directories created during this session (for testing)."""
        for directory in self.created_directories:
            if directory.exists() and not any(directory.iterdir()):
                try:
                    directory.rmdir()
                except Exception:
                    pass  # Ignore cleanup errors


class EnvironmentResolver:
    """Resolves environment variables with fallback logic."""

    def __init__(self):
        self.provider_env_map = {
            "openai": "OPENAI",
            "anthropic": "ANTHROPIC",
            "local": "LOCAL"
        }
        self.env_cache: Dict[str, Optional[str]] = {}

    def resolve_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider from environment."""
        cache_key = f"{provider}_api_key"
        if cache_key not in self.env_cache:
            env_prefix = self.provider_env_map.get(provider, provider.upper())
            self.env_cache[cache_key] = os.getenv(f"{env_prefix}_API_KEY")
        return self.env_cache[cache_key]

    def resolve_base_url(self, provider: str) -> Optional[str]:
        """Get base URL for provider from environment."""
        cache_key = f"{provider}_base_url"
        if cache_key not in self.env_cache:
            env_prefix = self.provider_env_map.get(provider, provider.upper())
            self.env_cache[cache_key] = os.getenv(f"{env_prefix}_BASE_URL")
        return self.env_cache[cache_key]

    def get_all_env_overrides(self) -> Dict[str, Optional[str]]:
        """Get all environment variable overrides."""
        return {
            'llm_provider': os.getenv('BRAND_TOOL_LLM_PROVIDER'),
            'llm_base_url': os.getenv('BRAND_TOOL_LLM_BASE_URL'),
            'llm_model': os.getenv('BRAND_TOOL_LLM_MODEL'),
            'default_output_dir': os.getenv('BRAND_TOOL_OUTPUT_DIR'),
            'session_storage_dir': os.getenv('BRAND_TOOL_SESSION_DIR'),
            'cache_dir': os.getenv('BRAND_TOOL_CACHE_DIR'),
            'request_timeout': os.getenv('BRAND_TOOL_REQUEST_TIMEOUT'),
            'enable_caching': os.getenv('BRAND_TOOL_ENABLE_CACHING'),
            'debug_mode': os.getenv('BRAND_TOOL_DEBUG_MODE'),
        }


# Global configuration instances
DEV_CONFIG = DeveloperConfig()
RESOLVED_CONFIG: Optional[ResolvedConfig] = None

# ============================================================================
# LLM Integration Models
# ============================================================================

class LLMRequest(BaseModel):
    """Structured request to LLM for brand enhancement."""

    prompt_type: str = Field(..., description="Type of enhancement: gap_analysis, color_generation, design_strategy")
    context: Dict[str, Any] = Field(..., description="Brand context and existing elements")
    enhancement_level: str = Field("moderate", pattern="^(minimal|moderate|comprehensive)$")
    user_preferences: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "prompt_type": "color_generation",
                "context": {
                    "brand_name": "TechFlow",
                    "personality": "professional, innovative",
                    "color_descriptions": ["professional blue", "energetic orange"]
                },
                "enhancement_level": "moderate"
            }
        }


class LLMResponse(BaseModel):
    """Response from LLM with enhancement suggestions."""

    response_type: str
    content: Dict[str, Any]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., description="Explanation of enhancement decisions")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time: float

    @validator('confidence_score')
    def validate_confidence(cls, v):
        return max(0.0, min(1.0, v))

    class Config:
        schema_extra = {
            "example": {
                "response_type": "color_enhancement",
                "content": {
                    "primary": {"hex": "#2563EB", "name": "Professional Blue", "usage": "CTAs, headers"},
                    "secondary": {"hex": "#F97316", "name": "Energetic Orange", "usage": "Accents, highlights"}
                },
                "confidence_score": 0.87,
                "rationale": "Blue conveys trust and professionalism while orange adds energy and innovation",
                "processing_time": 1.2
            }
        }


class LLMEnhancementEngine:
    """Role-based LLM enhancement with structured prompts."""

    PROMPTS = {
        "gap_analysis": """Analyze this brand description and identify missing elements:
        Brand: {brand_content}
        Required elements: colors, typography, personality, visual style
        Return: JSON with missing elements and recommendations""",

        "color_generation": """Generate hex codes for these color descriptions:
        Colors: {color_descriptions}
        Brand personality: {personality}
        Return: JSON with hex codes, names, usage guidelines, accessibility scores""",

        "design_strategy": """Create unified design strategy:
        Brand: {brand_summary}
        Elements: {existing_elements}
        Return: JSON with spacing, hierarchy, consistency guidelines"""
    }

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None,
                 model: str = "gpt-3.5-turbo", enable_caching: bool = True,
                 timeout: float = 30.0, base_url: Optional[str] = None):
        """Initialize LLM enhancement engine."""
        if provider not in ["openai", "anthropic", "local"]:
            raise ValueError(f"Invalid provider: {provider}")

        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.model = model
        self.enable_caching = enable_caching
        self.base_url = base_url
        self.timeout = timeout
        self._cache: Dict[str, LLMResponse] = {}

    def process_request(self, request: LLMRequest) -> LLMResponse:
        """Process an LLM request and return response."""
        start_time = time.time()

        try:
            # Generate cache key if caching is enabled
            cache_key = None
            if self.enable_caching:
                cache_key = self._get_cache_key(request)
                if cache_key in self._cache:
                    cached_response = self._cache[cache_key]
                    cached_response.processing_time = time.time() - start_time
                    return cached_response

            # For now, return mock responses since we don't have real LLM integration
            response = self._generate_mock_response(request)
            response.processing_time = time.time() - start_time

            # Cache the response
            if self.enable_caching and cache_key is not None:
                self._cache[cache_key] = response

            return response

        except Exception as e:
            # Error handling - return low confidence response
            return LLMResponse(
                response_type=f"{request.prompt_type}_error",
                content={"error": str(e)},
                confidence_score=0.0,
                rationale=f"Error processing request: {str(e)}",
                processing_time=time.time() - start_time
            )

    def _generate_mock_response(self, request: LLMRequest) -> LLMResponse:
        """Generate mock responses for testing purposes."""
        if request.prompt_type == "gap_analysis":
            # Determine completeness based on content richness
            content = request.context
            completeness_score = 0.6  # Default

            # Calculate based on available fields
            available_fields = 0
            total_fields = 6  # brand_name, colors, personality, typography, visual_style, logo

            if content.get("brand_name"):
                available_fields += 1
            if content.get("colors"):
                available_fields += 1
            if content.get("personality"):
                available_fields += 1
            if "typography" in content.get("raw_content", "").lower():
                available_fields += 1
            if "visual" in content.get("raw_content", "").lower():
                available_fields += 1
            if "logo" in content.get("raw_content", "").lower():
                available_fields += 1

            completeness_score = available_fields / total_fields

            # Determine missing elements based on content
            missing_elements = []
            raw_content_lower = content.get("raw_content", "").lower()

            # Check for typography section/keywords
            if not any(keyword in raw_content_lower for keyword in ["typography", "font", "typeface"]):
                missing_elements.append("typography")

            # Check for visual style section/keywords
            if not any(keyword in raw_content_lower for keyword in ["visual style", "style:", "design style", "aesthetic"]):
                missing_elements.append("visual_style")

            return LLMResponse(
                response_type="gap_analysis",
                content={
                    "missing_elements": missing_elements,
                    "incomplete_elements": ["color_palette"] if len(content.get("colors", [])) < 3 else [],
                    "completeness_score": completeness_score,
                    "priority_gaps": [
                        {
                            "element": elem,
                            "impact": "high",
                            "description": f"No {elem.replace('_', ' ')} specified"
                        } for elem in missing_elements[:3]  # Top 3 gaps
                    ],
                    "enhancement_opportunities": [
                        "Generate specific hex codes for color descriptions",
                        "Create unified design strategy",
                        "Establish visual hierarchy guidelines"
                    ]
                },
                confidence_score=0.85,
                rationale="Analysis based on standard brand requirements",
                processing_time=0.0
            )

        elif request.prompt_type == "color_generation":
            return LLMResponse(
                response_type="color_enhancement",
                content={
                    "primary": {
                        "hex": "#2563EB",
                        "name": "Professional Blue",
                        "usage": "Primary brand color for headers and CTAs"
                    },
                    "secondary": {
                        "hex": "#F97316",
                        "name": "Energetic Orange",
                        "usage": "Accents and highlights"
                    }
                },
                confidence_score=0.92,
                rationale="Colors selected based on brand personality and accessibility",
                alternatives=[
                    {"hex": "#1E40AF", "name": "Deep Blue"},
                    {"hex": "#3B82F6", "name": "Bright Blue"}
                ],
                processing_time=0.0
            )

        elif request.prompt_type == "design_strategy":
            return LLMResponse(
                response_type="design_strategy",
                content={
                    "consistency_principles": [
                        "Maintain 4.5:1 contrast ratio",
                        "Use consistent spacing scale",
                        "Apply hierarchical typography"
                    ],
                    "coherence_score": 0.88
                },
                confidence_score=0.89,
                rationale="Strategy ensures brand consistency and accessibility",
                processing_time=0.0
            )

        else:
            return LLMResponse(
                response_type="unknown",
                content={},
                confidence_score=0.0,
                rationale=f"Unknown prompt type: {request.prompt_type}",
                processing_time=0.0
            )

    def _get_cache_key(self, request: LLMRequest) -> str:
        """Generate cache key for request."""
        request_str = f"{request.prompt_type}_{request.enhancement_level}_{json.dumps(request.context, sort_keys=True)}"
        return hashlib.md5(request_str.encode()).hexdigest()


# ============================================================================
# Gap Analysis Models
# ============================================================================

class GapItem(BaseModel):
    """Individual gap requiring enhancement."""

    element: str = Field(..., description="Brand element with gap")
    impact: str = Field(..., pattern="^(low|medium|high|critical)$")
    description: str = Field(..., description="Detailed gap description")
    enhancement_suggestion: Optional[str] = None
    estimated_improvement: float = Field(..., ge=0.0, le=1.0)

    @validator('impact')
    def validate_impact(cls, v):
        valid_impacts = ["low", "medium", "high", "critical"]
        if v not in valid_impacts:
            raise ValueError(f"Impact must be one of {valid_impacts}")
        return v


class BrandGapAnalysis(BaseModel):
    """Analysis of missing or incomplete brand elements."""

    missing_elements: List[str] = Field(..., description="List of missing brand components")
    incomplete_elements: List[str] = Field(..., description="List of elements needing enhancement")
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="Overall completeness percentage")
    priority_gaps: List[GapItem] = Field(..., description="Prioritized list of gaps to address")
    enhancement_opportunities: List[str] = Field(..., description="Areas for quality improvement")

    class Config:
        schema_extra = {
            "example": {
                "missing_elements": ["typography", "visual_style"],
                "incomplete_elements": ["color_palette"],
                "completeness_score": 0.6,
                "priority_gaps": [
                    {
                        "element": "typography",
                        "impact": "high",
                        "description": "No font preferences specified"
                    }
                ]
            }
        }


# ============================================================================
# Enhancement Models
# ============================================================================

class EnhancementSuggestion(BaseModel):
    """LLM-generated enhancement recommendation."""

    element_type: str = Field(..., description="Type of brand element being enhanced")
    original_value: Optional[str] = None
    suggested_value: Dict[str, Any] = Field(..., description="Enhanced element specification")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., description="Explanation for the enhancement")
    accessibility_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        schema_extra = {
            "example": {
                "element_type": "color",
                "original_value": "blue",
                "suggested_value": {
                    "hex": "#1E40AF",
                    "name": "Trust Blue",
                    "usage": "Primary brand color for headers and CTAs"
                },
                "confidence_score": 0.92,
                "rationale": "This shade balances professionalism with approachability",
                "accessibility_score": 0.85
            }
        }


# ============================================================================
# CLI Argument Parser
# ============================================================================

def create_argument_parser(config: DeveloperConfig) -> argparse.ArgumentParser:
    """Create and configure the argument parser with LLM enhancement options."""
    parser = argparse.ArgumentParser(
        description="LLM-Enhanced Brand Identity Processing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Standard processing
  python brand_identity_generator.py brand.md -o output.json

  # LLM enhancement
  python brand_identity_generator.py brand.md --enhance -o enhanced.json

  # Gap analysis only
  python brand_identity_generator.py brand.md --analyze-gaps

  # Interactive enhancement
  python brand_identity_generator.py brand.md --enhance --interactive

Configuration:
  Current defaults from configuration:
    LLM Provider: {config.llm_provider}
    Enhancement Level: {config.default_enhancement_level}
    Output Directory: {config.default_output_dir}
    Debug Mode: {config.debug_mode}

  Override with environment variables:
    OPENAI_API_KEY, ANTHROPIC_API_KEY (API keys)
    BRAND_TOOL_LLM_PROVIDER, BRAND_TOOL_OUTPUT_DIR (settings)
        """
    )

    # Core arguments
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Input markdown file with brand description"
    )
    parser.add_argument(
        "-o", "--output",
        help=f"Output JSON file path (default: uses {config.default_output_dir})"
    )

    # LLM Enhancement Control
    parser.add_argument(
        "--enhance", "-e",
        action="store_true",
        help="Enable LLM enhancement processing"
    )
    parser.add_argument(
        "--enhancement-level",
        choices=["minimal", "moderate", "comprehensive"],
        default=config.default_enhancement_level,
        help=f"Set enhancement intensity (default: {config.default_enhancement_level})"
    )
    parser.add_argument(
        "--llm-provider",
        choices=["openai", "anthropic", "local"],
        default=config.llm_provider,
        help=f"Choose LLM service provider (default: {config.llm_provider})"
    )

    # Gap Analysis and Strategy
    parser.add_argument(
        "--analyze-gaps",
        action="store_true",
        help="Perform gap analysis without enhancement"
    )
    parser.add_argument(
        "--design-strategy",
        action="store_true",
        help="Generate unified design strategy"
    )

    # User Interaction
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive enhancement review"
    )
    parser.add_argument(
        "--save-session",
        help="Save enhancement session to file"
    )
    parser.add_argument(
        "--load-session",
        help="Load previous enhancement session"
    )

    # Debug and configuration
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )

    return parser


def create_resolved_config(dev_config: DeveloperConfig, args: argparse.Namespace) -> ResolvedConfig:
    """Create final configuration by merging developer config with CLI arguments."""
    # Start with developer config values
    config_data = {
        'llm_provider': args.llm_provider,
        'llm_base_url': dev_config.llm_base_url,
        'llm_model': dev_config.llm_model,
        'llm_api_key': dev_config.llm_api_key,
        'default_output_dir': dev_config.default_output_dir,
        'session_storage_dir': dev_config.session_storage_dir,
        'cache_dir': dev_config.cache_dir,
        'request_timeout': dev_config.request_timeout,
        'enable_caching': dev_config.enable_caching,
        'max_retries': dev_config.max_retries,
        'retry_backoff_factor': dev_config.retry_backoff_factor,
        'default_enhancement_level': args.enhancement_level,
        'debug_mode': getattr(args, 'debug', False) or dev_config.debug_mode,
        'log_level': dev_config.log_level,
    }

    # Track sources for each setting
    sources = {
        'llm_provider': 'cli' if args.llm_provider != dev_config.llm_provider else 'config',
        'llm_base_url': 'config',
        'llm_model': 'config',
        'llm_api_key': 'env' if dev_config.llm_api_key else 'default',
        'default_output_dir': 'config',
        'session_storage_dir': 'config',
        'cache_dir': 'config',
        'request_timeout': 'config',
        'enable_caching': 'config',
        'max_retries': 'config',
        'retry_backoff_factor': 'config',
        'default_enhancement_level': 'cli' if args.enhancement_level != dev_config.default_enhancement_level else 'config',
        'debug_mode': 'cli' if getattr(args, 'debug', False) else 'config',
        'log_level': 'config',
    }

    # Create resolved configuration
    resolved = ResolvedConfig(
        **config_data,
        config_source=sources,
        validation_warnings=[],
        validation_errors=[]
    )

    return resolved


def validate_configuration(config: ResolvedConfig) -> None:
    """Validate the final configuration and handle errors."""
    try:
        # Validate directories
        dir_manager = DirectoryManager([
            config.default_output_dir,
            config.session_storage_dir,
            config.cache_dir
        ])
        dir_manager.ensure_exists()

        # Add any validation warnings to config
        if config.request_timeout < 5.0:
            config.validation_warnings.append(f"Low timeout ({config.request_timeout}s) may cause failures")

        if not config.llm_api_key:
            config.validation_warnings.append(f"No API key found for provider '{config.llm_provider}' - using mock responses")

    except ConfigurationError as e:
        config.validation_errors.append(str(e))
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Display warnings if debug mode is enabled
    if config.debug_mode and config.validation_warnings:
        for warning in config.validation_warnings:
            print(f"WARNING: {warning}", file=sys.stderr)


# ============================================================================
# Processing Functions
# ============================================================================

def analyze_gaps_only(input_file: str) -> Dict[str, Any]:
    """Perform gap analysis without enhancement."""
    if not input_file or not Path(input_file).exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Read and parse input file
    content = read_brand_markdown(input_file)

    # Create LLM engine for gap analysis
    engine = LLMEnhancementEngine()

    # Perform gap analysis
    request = LLMRequest(
        prompt_type="gap_analysis",
        context=content,
        enhancement_level="moderate"
    )

    response = engine.process_request(request)

    return {
        "gap_analysis": response.content
    }


def process_with_enhancement(args, config: ResolvedConfig) -> Dict[str, Any]:
    """Process brand identity with LLM enhancement."""
    if not args.input_file or not Path(args.input_file).exists():
        raise FileNotFoundError(f"Input file not found: {args.input_file}")

    content = read_brand_markdown(args.input_file)

    # Initialize LLM engine with configuration
    engine = LLMEnhancementEngine(
        provider=config.llm_provider,
        api_key=config.llm_api_key,
        model=config.llm_model,
        enable_caching=config.enable_caching,
        timeout=config.request_timeout,
        base_url=config.llm_base_url
    )

    # Perform enhancement
    workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    start_time = time.time()

    # Color enhancement
    color_request = LLMRequest(
        prompt_type="color_generation",
        context=content,
        enhancement_level=args.enhancement_level
    )
    color_response = engine.process_request(color_request)

    # Design strategy (if requested)
    design_strategy = None
    if args.design_strategy:
        strategy_request = LLMRequest(
            prompt_type="design_strategy",
            context=content,
            enhancement_level=args.enhancement_level
        )
        strategy_response = engine.process_request(strategy_request)
        design_strategy = strategy_response.content

    total_time = time.time() - start_time
    user_feedback_count = 0

    # Interactive mode - handle feedback for each color element
    if args.interactive:
        user_feedback_count = 0
        # Provide feedback opportunity for each color
        if "primary" in color_response.content:
            primary_response = LLMResponse(
                response_type="primary_color_enhancement",
                content={"primary": color_response.content["primary"]},
                confidence_score=color_response.confidence_score,
                rationale="Primary color enhancement",
                alternatives=color_response.alternatives[:2] if color_response.alternatives else [],
                processing_time=color_response.processing_time
            )
            user_feedback_count += handle_interactive_enhancement(primary_response)

        if "secondary" in color_response.content:
            secondary_response = LLMResponse(
                response_type="secondary_color_enhancement",
                content={"secondary": color_response.content["secondary"]},
                confidence_score=color_response.confidence_score,
                rationale="Secondary color enhancement",
                alternatives=color_response.alternatives[2:] if len(color_response.alternatives) > 2 else [],
                processing_time=color_response.processing_time
            )
            user_feedback_count += handle_interactive_enhancement(secondary_response)

    # Build enhanced output with per-element metadata
    enhanced_color_palette = {}
    if "primary" in color_response.content:
        enhanced_color_palette["primary"] = {
            **color_response.content["primary"],
            "enhancement_metadata": {
                "original_description": content.get("colors", ["blue"])[0] if content.get("colors") else "blue",
                "confidence_score": color_response.confidence_score,
                "rationale": color_response.rationale,
                "accessibility_score": 0.85  # Mock accessibility score
            }
        }

    if "secondary" in color_response.content:
        enhanced_color_palette["secondary"] = {
            **color_response.content["secondary"],
            "enhancement_metadata": {
                "original_description": content.get("colors", ["orange"])[1] if len(content.get("colors", [])) > 1 else "orange",
                "confidence_score": color_response.confidence_score,
                "rationale": color_response.rationale,
                "accessibility_score": 0.85  # Mock accessibility score
            }
        }

    result = {
        "brandName": content.get("brand_name", "Unknown Brand"),
        "colorPalette": enhanced_color_palette,
        "enhancement_metadata": {
            "workflow_id": workflow_id,
            "enhancement_level": args.enhancement_level,
            "gaps_filled": ["color_palette"],
            "processing_time": total_time,
            "llm_provider": args.llm_provider,
            "user_feedback_count": user_feedback_count
        }
    }

    if design_strategy:
        result["designStrategy"] = design_strategy

    # Save session if requested using configured directory
    if args.save_session:
        session_path = args.save_session
        if not Path(session_path).is_absolute():
            session_path = Path(config.session_storage_dir) / session_path
        save_enhancement_session(str(session_path), result, content)

    return result


def process_standard(input_file: str) -> Dict[str, Any]:
    """Standard processing without LLM enhancement."""
    if not input_file or not Path(input_file).exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    content = read_brand_markdown(input_file)

    return {
        "brandName": content.get("brand_name", "Unknown Brand"),
        "colorPalette": {
            "primary": {"hex": "#0066CC", "name": "Blue"}
        },
        "typography": {
            "fontFamilies": {
                "heading": {"primary": "Arial", "fallback": "sans-serif"}
            }
        }
    }


def read_brand_markdown(file_path: str) -> Dict[str, Any]:
    """Read and parse brand markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Basic parsing - extract brand name and content sections
        brand_data: Dict[str, Any] = {"raw_content": content}

        # Extract brand name
        name_match = re.search(r'Brand Name:\s*(.+)', content, re.IGNORECASE)
        if name_match:
            brand_data["brand_name"] = name_match.group(1).strip()

        # Extract colors - store as list of color descriptions
        colors: List[str] = re.findall(r'(?:Primary|Secondary):\s*(.+)', content, re.IGNORECASE)
        if colors:
            brand_data["colors"] = colors

        # Extract personality traits
        traits_match = re.search(r'Traits:\s*(.+)', content, re.IGNORECASE)
        if traits_match:
            brand_data["personality"] = traits_match.group(1).strip()

        return brand_data

    except Exception as e:
        raise ValueError(f"Error reading brand file: {str(e)}")


def handle_interactive_enhancement(response: LLMResponse) -> int:
    """Handle interactive enhancement review."""
    feedback_count = 0

    print(f"\nEnhancement Review for: {response.response_type}", file=sys.stderr)
    print(f"AI Suggestion: {json.dumps(response.content, indent=2)}", file=sys.stderr)
    print(f"Rationale: {response.rationale}", file=sys.stderr)
    print(f"Confidence Score: {response.confidence_score:.2f}", file=sys.stderr)
    print("\nOptions:", file=sys.stderr)
    print("[A] Accept  [M] Modify  [R] Reject  [S] See alternatives", file=sys.stderr)

    try:
        print("Choice: ", file=sys.stderr, end="")
        choice = input().upper().strip()
        feedback_count += 1

        if choice == 'A':
            print("Suggestion accepted.", file=sys.stderr)
        elif choice == 'M':
            print("What would you like to modify? ", file=sys.stderr, end="")
            modification = input()
            print(f"Noted: {modification}", file=sys.stderr)
            feedback_count += 1
        elif choice == 'R':
            print("Suggestion rejected.", file=sys.stderr)
        elif choice == 'S':
            if response.alternatives:
                print("Alternatives:", file=sys.stderr)
                for i, alt in enumerate(response.alternatives):
                    print(f"{i+1}. {json.dumps(alt, indent=2)}", file=sys.stderr)
            else:
                print("No alternatives available.", file=sys.stderr)
        else:
            print("Invalid choice, accepting suggestion.", file=sys.stderr)

    except KeyboardInterrupt:
        print("\nInteractive mode cancelled.", file=sys.stderr)
    except EOFError:
        print("\nNo input provided, accepting suggestion.", file=sys.stderr)

    return feedback_count


def save_enhancement_session(file_path: str, result: Dict[str, Any],
                           original_input: Dict[str, Any]) -> None:
    """Save enhancement session for later review."""
    session_data = {
        "session_id": f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now().isoformat(),
        "original_input": original_input,
        "current_state": "completed",
        "result": result,
        "session_metadata": {
            "enhancement_level": result["enhancement_metadata"]["enhancement_level"],
            "llm_provider": result["enhancement_metadata"]["llm_provider"],
            "steps_completed": ["gap_analysis", "color_enhancement"]
        }
    }

    try:
        # Use configured directory if relative path provided
        output_path = Path(file_path)
        if not output_path.is_absolute() and 'RESOLVED_CONFIG' in globals() and RESOLVED_CONFIG is not None:
            output_path = Path(RESOLVED_CONFIG.session_storage_dir) / file_path

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        print(f"Session saved to {output_path}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Could not save session: {e}", file=sys.stderr)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the brand identity generator."""
    try:
        # Load and validate configuration
        start_time = time.time()
        dev_config = DEV_CONFIG
        config_load_time = time.time() - start_time

        # Create argument parser with configuration defaults
        parser = create_argument_parser(dev_config)
        args = parser.parse_args()

        # Create resolved configuration
        resolved_config = create_resolved_config(dev_config, args)

        # Validate configuration
        validate_configuration(resolved_config)

        # Performance check
        if config_load_time > 0.01:  # 10ms threshold
            if resolved_config.debug_mode:
                print(f"WARNING: Configuration loading took {config_load_time*1000:.1f}ms", file=sys.stderr)

        # Store resolved config globally for use by other functions
        global RESOLVED_CONFIG
        RESOLVED_CONFIG = resolved_config

        # Ensure all configured directories exist and are writable
        dir_manager = DirectoryManager()
        try:
            dir_manager.ensure_directory_exists(resolved_config.default_output_dir)
            dir_manager.ensure_directory_exists(resolved_config.session_storage_dir)
            if resolved_config.enable_caching:
                dir_manager.ensure_directory_exists(resolved_config.cache_dir)
        except Exception as e:
            raise ConfigurationError(f"Directory validation failed: {e}")

        if args.load_session:
            # Load and process session
            session_file = args.load_session
            if not Path(session_file).is_absolute():
                session_file = Path(resolved_config.session_storage_dir) / session_file
            print(f"Loading session from {session_file}", file=sys.stderr)
            # TODO: Implement session loading with configured directory
            return

        if args.analyze_gaps:
            result = analyze_gaps_only(args.input_file)
        elif args.enhance:
            result = process_with_enhancement(args, resolved_config)
        else:
            result = process_standard(args.input_file)

        # Output results using configured directory
        if args.output:
            output_path = Path(args.output)
            if not output_path.is_absolute():
                output_path = Path(resolved_config.default_output_dir) / args.output

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))

    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()