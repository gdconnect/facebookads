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
from pydantic import BaseModel, Field, field_validator
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

    # Font Selection Settings
    google_fonts_api_key: Optional[str] = None  # Google Fonts API key (uses environment variable if not set)
    font_cache_dir: str = "./cache/fonts"  # Directory for Google Fonts cache
    font_cache_ttl_hours: int = 24  # Cache time-to-live in hours (1-168)
    font_cache_max_size_mb: int = 50  # Maximum cache size in MB (1-500)
    enable_font_selection: bool = True  # Whether to enable automatic font selection

    class Config:
        extra = "forbid"  # Prevent unknown fields

    @field_validator('llm_provider')
    @classmethod
    def validate_llm_provider(cls, v):
        valid_providers = ["openai", "anthropic", "local"]
        if v not in valid_providers:
            raise ValueError(f"Invalid LLM provider '{v}'. Valid options: {', '.join(valid_providers)}")
        return v

    @field_validator('llm_base_url')
    @classmethod
    def validate_base_url(cls, v):
        if v is not None and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError(f"Invalid base URL format '{v}'. Must start with http:// or https://")
        return v

    @field_validator('request_timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v < 1.0:
            raise ValueError(f"Request timeout must be >= 1.0 seconds, got {v}")
        return v

    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v):
        if not (0 <= v <= 10):
            raise ValueError(f"Max retries must be between 0 and 10, got {v}")
        return v

    @field_validator('retry_backoff_factor')
    @classmethod
    def validate_backoff_factor(cls, v):
        if not (1.0 <= v <= 5.0):
            raise ValueError(f"Retry backoff factor must be between 1.0 and 5.0, got {v}")
        return v

    @field_validator('default_enhancement_level')
    @classmethod
    def validate_enhancement_level(cls, v):
        valid_levels = ["minimal", "moderate", "comprehensive"]
        if v not in valid_levels:
            raise ValueError(f"Invalid enhancement level '{v}'. Valid options: {', '.join(valid_levels)}")
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if v not in valid_levels:
            raise ValueError(f"Invalid log level '{v}'. Valid options: {', '.join(valid_levels)}")
        return v

    @field_validator('font_cache_ttl_hours')
    @classmethod
    def validate_font_cache_ttl(cls, v):
        if not 1 <= v <= 168:  # 1 hour to 1 week
            raise ValueError(f"Font cache TTL '{v}' must be between 1 and 168 hours")
        return v

    @field_validator('font_cache_max_size_mb')
    @classmethod
    def validate_font_cache_max_size(cls, v):
        if not 1 <= v <= 500:  # 1MB to 500MB
            raise ValueError(f"Font cache max size '{v}' must be between 1 and 500 MB")
        return v

    def __init__(self, **data):
        # Apply environment variable fallbacks before validation
        if not data.get('llm_api_key'):
            provider = data.get('llm_provider', 'openai').upper()
            data['llm_api_key'] = os.getenv(f"{provider}_API_KEY")

        if not data.get('llm_base_url'):
            provider = data.get('llm_provider', 'openai').upper()
            data['llm_base_url'] = os.getenv(f"{provider}_BASE_URL")

        # Apply Google Fonts API key from environment if not provided
        if not data.get('google_fonts_api_key'):
            data['google_fonts_api_key'] = os.getenv('GOOGLE_FONTS_API_KEY')

        # Apply configuration overrides from environment variables
        env_overrides = {
            'llm_provider': os.getenv('BRAND_TOOL_LLM_PROVIDER'),
            'default_output_dir': os.getenv('BRAND_TOOL_OUTPUT_DIR'),
            'cache_dir': os.getenv('BRAND_TOOL_CACHE_DIR'),
            'session_storage_dir': os.getenv('BRAND_TOOL_SESSION_DIR'),
            'debug_mode': os.getenv('BRAND_TOOL_DEBUG_MODE'),
            'log_level': os.getenv('BRAND_TOOL_LOG_LEVEL'),
            'enable_caching': os.getenv('BRAND_TOOL_CACHE_ENABLED'),
            'font_cache_dir': os.getenv('BRAND_TOOL_FONT_CACHE_DIR'),
            'font_cache_ttl_hours': os.getenv('BRAND_TOOL_FONT_CACHE_TTL'),
            'font_cache_max_size_mb': os.getenv('BRAND_TOOL_FONT_CACHE_SIZE'),
            'enable_font_selection': os.getenv('BRAND_TOOL_FONT_ENABLED'),
        }

        for key, env_value in env_overrides.items():
            if env_value is not None and key not in data:
                if key in ['debug_mode', 'enable_caching', 'enable_font_selection']:
                    data[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                elif key in ['font_cache_ttl_hours', 'font_cache_max_size_mb']:
                    try:
                        data[key] = int(env_value)
                    except ValueError:
                        pass  # Let the validator handle the error
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

    @field_validator('confidence_score')
    @classmethod
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

    @field_validator('impact')
    @classmethod
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
# Font Selection Models
# ============================================================================

class GoogleFont(BaseModel):
    """Google Font data structure with validation."""

    family: str = Field(..., description="Font family name", min_length=1)
    category: str = Field(..., description="Font category")
    variants: List[str] = Field(..., description="Available font weights and styles")
    subsets: List[str] = Field(default_factory=list, description="Supported character subsets")
    version: Optional[str] = Field(None, description="Font version from Google Fonts")
    last_modified: Optional[str] = Field(None, description="Last modification date")
    font_files: Optional[Dict[str, str]] = Field(None, description="Direct URLs to font files")

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = ["serif", "sans-serif", "display", "handwriting", "monospace"]
        if v not in valid_categories:
            raise ValueError(f"Invalid font category '{v}'. Valid options: {', '.join(valid_categories)}")
        return v

    @field_validator('variants')
    @classmethod
    def validate_variants(cls, v):
        if not v:
            raise ValueError("Font must have at least one variant")

        valid_weights = ['100', '200', '300', '400', '500', '600', '700', '800', '900']
        valid_styles = ['regular', 'italic']
        valid_variants = valid_weights + valid_styles + [w + 'italic' for w in valid_weights]

        for variant in v:
            if variant not in valid_variants:
                # Allow some flexibility for Google Fonts variants
                if not (variant.endswith('italic') and variant[:-6] in valid_weights):
                    # Log warning but don't fail for unknown variants
                    pass
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "family": "Inter",
                "category": "sans-serif",
                "variants": ["300", "400", "600", "700"],
                "subsets": ["latin", "latin-ext"],
                "version": "v12",
                "last_modified": "2023-05-02",
                "font_files": {
                    "400": "https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiA.woff2"
                }
            }
        }


class FontSelectionCriteria(BaseModel):
    """Criteria for selecting appropriate fonts based on brand characteristics."""

    brand_personality: List[str] = Field(..., description="Brand personality traits", min_length=1)
    target_audience: str = Field(..., description="Primary target audience", min_length=1)
    brand_voice: str = Field(..., description="Brand voice characteristics", min_length=1)
    enhancement_level: str = Field("moderate", description="Level of typography enhancement")
    existing_colors: List[str] = Field(default_factory=list, description="Existing brand colors for harmony")
    industry_context: Optional[str] = Field(None, description="Industry or domain context")

    @field_validator('enhancement_level')
    @classmethod
    def validate_enhancement_level(cls, v):
        valid_levels = ["minimal", "moderate", "comprehensive"]
        if v not in valid_levels:
            raise ValueError(f"Invalid enhancement level '{v}'. Valid options: {', '.join(valid_levels)}")
        return v

    @field_validator('brand_personality')
    @classmethod
    def validate_personality_traits(cls, v):
        if not v:
            raise ValueError("At least one brand personality trait is required")

        # Clean and normalize traits
        cleaned = [trait.strip().lower() for trait in v if trait.strip()]
        if not cleaned:
            raise ValueError("Brand personality traits cannot be empty")
        return cleaned

    class Config:
        json_schema_extra = {
            "example": {
                "brand_personality": ["professional", "modern", "trustworthy"],
                "target_audience": "enterprise decision makers",
                "brand_voice": "authoritative yet approachable",
                "enhancement_level": "moderate",
                "existing_colors": ["#2563eb", "#10b981"],
                "industry_context": "technology"
            }
        }


class FontStyle(BaseModel):
    """CSS-compatible font style specification."""

    font_family: str = Field(..., description="Font family name")
    font_weight: str = Field(..., description="Font weight (CSS-compatible)")
    font_size: str = Field(..., description="Font size with CSS unit")
    line_height: Union[str, float] = Field(..., description="Line height value")
    margin_bottom: Optional[str] = Field(None, description="Bottom margin with CSS unit")

    @field_validator('font_weight')
    @classmethod
    def validate_font_weight(cls, v):
        valid_weights = ['100', '200', '300', '400', '500', '600', '700', '800', '900', 'normal', 'bold']
        if v not in valid_weights:
            raise ValueError(f"Invalid font weight '{v}'. Valid options: {', '.join(valid_weights)}")
        return v

    @field_validator('font_size')
    @classmethod
    def validate_font_size(cls, v):
        if not any(v.endswith(unit) for unit in ['px', 'rem', 'em', '%']):
            raise ValueError(f"Font size '{v}' must include a valid CSS unit (px, rem, em, %)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "font_family": "Inter",
                "font_weight": "700",
                "font_size": "3rem",
                "line_height": "1.2",
                "margin_bottom": "1.5rem"
            }
        }


class FontRecommendation(BaseModel):
    """Font recommendation with confidence scoring and rationale."""

    google_font: GoogleFont = Field(..., description="Selected Google Font")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    rationale: str = Field(..., description="Explanation for font selection", min_length=10)
    use_cases: List[str] = Field(..., description="Recommended use cases for this font")
    recommended_weights: List[str] = Field(..., description="Recommended font weights to use")
    alternatives: List[GoogleFont] = Field(default_factory=list, description="Alternative font suggestions")

    @field_validator('confidence_score')
    @classmethod
    def validate_confidence_score(cls, v):
        if v < 0.7:
            raise ValueError(f"Confidence score {v} is below minimum threshold of 0.7")
        return v

    @field_validator('use_cases')
    @classmethod
    def validate_use_cases(cls, v):
        valid_use_cases = [
            "headings", "body", "navigation", "CTAs", "captions",
            "emphasis", "quotes", "labels", "buttons", "forms"
        ]

        for use_case in v:
            if use_case not in valid_use_cases:
                # Allow but don't validate unknown use cases for flexibility
                pass

        if not v:
            raise ValueError("At least one use case must be specified")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "google_font": {
                    "family": "Inter",
                    "category": "sans-serif",
                    "variants": ["400", "600", "700"]
                },
                "confidence_score": 0.92,
                "rationale": "Inter provides excellent readability for professional brands while maintaining modern appeal",
                "use_cases": ["headings", "navigation", "CTAs"],
                "recommended_weights": ["400", "600", "700"]
            }
        }


class TypographyHierarchy(BaseModel):
    """Complete typography system with font hierarchy and styles."""

    primary_font: Optional[FontRecommendation] = Field(None, description="Primary font for headings and emphasis")
    secondary_font: Optional[FontRecommendation] = Field(None, description="Secondary font for body text")
    accent_font: Optional[FontRecommendation] = Field(None, description="Accent font for special elements")

    heading_styles: Dict[str, FontStyle] = Field(default_factory=dict, description="H1-H6 heading styles")
    text_styles: Dict[str, FontStyle] = Field(default_factory=dict, description="Body, caption, emphasis styles")

    css_snippet: Optional[str] = Field(None, description="Ready-to-use CSS code")
    font_urls: Optional[Dict[str, str]] = Field(None, description="Font loading URLs")

    @field_validator('heading_styles')
    @classmethod
    def validate_heading_styles(cls, v):
        # Ensure required heading levels are present
        required_headings = ["h1", "h2", "h3"]
        missing_headings = [h for h in required_headings if h not in v]

        if missing_headings and v:  # Only validate if styles are provided
            raise ValueError(f"Missing required heading styles: {', '.join(missing_headings)}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "primary_font": {
                    "google_font": {"family": "Inter", "category": "sans-serif"},
                    "confidence_score": 0.9,
                    "rationale": "Modern, highly readable font"
                },
                "heading_styles": {
                    "h1": {
                        "font_family": "Inter",
                        "font_weight": "700",
                        "font_size": "3rem",
                        "line_height": "1.2"
                    }
                },
                "text_styles": {
                    "body": {
                        "font_family": "Inter",
                        "font_weight": "400",
                        "font_size": "1rem",
                        "line_height": "1.6"
                    }
                }
            }
        }


class FontSelectionMetadata(BaseModel):
    """Metadata about the font selection process."""

    selection_method: str = Field(..., description="Method used for selection")
    processing_time: float = Field(..., description="Time taken for selection in seconds")
    fonts_considered: int = Field(..., description="Number of fonts evaluated")
    api_calls_made: int = Field(default=0, description="Number of API calls made")
    cache_hit: bool = Field(default=False, description="Whether cache was used")
    fallback_used: bool = Field(default=False, description="Whether fallback fonts were used")

    class Config:
        json_schema_extra = {
            "example": {
                "selection_method": "rule-based",
                "processing_time": 1.23,
                "fonts_considered": 45,
                "api_calls_made": 1,
                "cache_hit": True,
                "fallback_used": False
            }
        }


class FontSelectionResponse(BaseModel):
    """Complete response from font selection process."""

    typography: TypographyHierarchy = Field(..., description="Selected typography system")
    selection_metadata: FontSelectionMetadata = Field(..., description="Selection process metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "typography": {
                    "primary_font": {
                        "google_font": {"family": "Inter", "category": "sans-serif"},
                        "confidence_score": 0.9
                    }
                },
                "selection_metadata": {
                    "selection_method": "rule-based",
                    "processing_time": 1.23,
                    "fonts_considered": 45
                }
            }
        }


# Font Selection Exceptions
class FontSelectionError(Exception):
    """Base exception for font selection failures."""
    pass


class GoogleFontsAPIError(FontSelectionError):
    """Google Fonts API access failures."""
    pass


class CacheError(FontSelectionError):
    """Font cache operation failures."""
    pass


class MatchingError(FontSelectionError):
    """Font matching algorithm failures."""
    pass


# ============================================================================
# Google Fonts API Client
# ============================================================================

def fetch_google_fonts(api_key: Optional[str] = None, force_refresh: bool = False) -> List[GoogleFont]:
    """
    Fetch Google Fonts catalog from API with caching.

    Args:
        api_key: Google Fonts API key (uses environment variable if not provided)
        force_refresh: Force API call even if cache is fresh

    Returns:
        List of all available Google Fonts with metadata

    Raises:
        GoogleFontsAPIError: When API request fails
        CacheError: When cache operations fail
    """
    import requests

    # Get API key from parameter or environment
    if api_key is None:
        api_key = os.getenv('GOOGLE_FONTS_API_KEY')

    if not api_key:
        raise GoogleFontsAPIError("Google Fonts API key is required. Set GOOGLE_FONTS_API_KEY environment variable or provide api_key parameter.")

    # Try cache first (unless force refresh)
    if not force_refresh:
        cached_fonts = get_cached_fonts()
        if cached_fonts is not None:
            return cached_fonts

    # Make API request
    try:
        url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code == 403:
            raise GoogleFontsAPIError("Invalid Google Fonts API key or quota exceeded.")
        elif response.status_code == 429:
            raise GoogleFontsAPIError("Google Fonts API rate limit exceeded. Please try again later.")
        elif response.status_code != 200:
            raise GoogleFontsAPIError(f"Google Fonts API request failed with status {response.status_code}: {response.text}")

        data = response.json()
        items = data.get('items', [])

        if len(items) < 800:  # Sanity check
            raise GoogleFontsAPIError(f"Received only {len(items)} fonts, expected at least 800. API may be incomplete.")

        # Convert to GoogleFont models
        fonts = []
        for item in items:
            try:
                font = GoogleFont(
                    family=item.get('family', ''),
                    category=item.get('category', 'sans-serif'),
                    variants=item.get('variants', ['400']),
                    subsets=item.get('subsets', ['latin']),
                    version=item.get('version'),
                    last_modified=item.get('lastModified'),
                    font_files=item.get('files', {})
                )
                fonts.append(font)
            except Exception as e:
                # Log font parsing error but continue
                print(f"Warning: Failed to parse font {item.get('family', 'unknown')}: {e}", file=sys.stderr)
                continue

        # Update cache with fresh data
        update_font_cache(fonts)

        return fonts

    except requests.exceptions.Timeout:
        raise GoogleFontsAPIError("Google Fonts API request timed out. Please check your internet connection.")
    except requests.exceptions.ConnectionError:
        raise GoogleFontsAPIError("Failed to connect to Google Fonts API. Please check your internet connection.")
    except requests.exceptions.RequestException as e:
        raise GoogleFontsAPIError(f"Google Fonts API request failed: {e}")
    except Exception as e:
        raise GoogleFontsAPIError(f"Unexpected error fetching Google Fonts: {e}")


def get_cached_fonts(max_age_hours: int = 24) -> Optional[List[GoogleFont]]:
    """
    Retrieve fonts from local cache if fresh.

    Args:
        max_age_hours: Maximum cache age before considering stale

    Returns:
        Cached fonts list or None if cache miss/stale
    """
    try:
        cache_dir = Path("./cache/fonts")
        cache_file = cache_dir / "google_fonts_cache.json"

        if not cache_file.exists():
            return None

        # Check cache age
        cache_mtime = cache_file.stat().st_mtime
        cache_age_seconds = time.time() - cache_mtime
        max_age_seconds = max_age_hours * 3600

        if cache_age_seconds > max_age_seconds:
            return None  # Cache is stale

        # Load and parse cache
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert to GoogleFont models
        fonts = []
        for item in data:
            try:
                font = GoogleFont(**item)
                fonts.append(font)
            except Exception as e:
                # Cache corruption - return None to trigger fresh fetch
                print(f"Warning: Cache corruption detected: {e}", file=sys.stderr)
                return None

        return fonts

    except Exception as e:
        # Cache read error - return None to trigger fresh fetch
        print(f"Warning: Cache read error: {e}", file=sys.stderr)
        return None


def update_font_cache(fonts: List[GoogleFont]) -> bool:
    """
    Update local font cache with fresh data.

    Args:
        fonts: Fresh font data from Google Fonts API

    Returns:
        True if cache update succeeded, False otherwise
    """
    try:
        cache_dir = Path("./cache/fonts")
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / "google_fonts_cache.json"

        # Convert fonts to JSON-serializable format
        font_data = []
        for font in fonts:
            try:
                font_dict = font.model_dump()
                font_data.append(font_dict)
            except Exception as e:
                print(f"Warning: Failed to serialize font {font.family}: {e}", file=sys.stderr)
                continue

        # Write to temporary file first, then move (atomic operation)
        temp_file = cache_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(font_data, f, indent=2, ensure_ascii=False)

        # Atomic move
        temp_file.replace(cache_file)

        print(f"✅ Updated font cache with {len(font_data)} fonts", file=sys.stderr)
        return True

    except Exception as e:
        print(f"Warning: Failed to update font cache: {e}", file=sys.stderr)
        return False


# ============================================================================
# Font Matching and Selection Engine
# ============================================================================

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
    if not available_fonts:
        raise MatchingError("No fonts available for matching")

    if not personality_traits:
        personality_traits = ["neutral"]

    # Normalize personality traits
    normalized_traits = [trait.lower().strip() for trait in personality_traits]

    # Define personality to category mapping
    category_weights = _calculate_category_weights(normalized_traits)

    # Filter and score fonts
    font_scores = []
    for font in available_fonts:
        score = _score_font_for_personality(font, normalized_traits, category_weights)
        if score > 0.5:  # Only consider decent matches
            font_scores.append((font, score))

    if not font_scores:
        # Fallback to safe fonts
        safe_fonts = [f for f in available_fonts if f.category == "sans-serif"]
        if safe_fonts:
            font_scores = [(safe_fonts[0], 0.7)]  # Minimum viable confidence
        else:
            raise MatchingError("No suitable fonts found and no safe fallbacks available")

    # Sort by score (highest first)
    font_scores.sort(key=lambda x: x[1], reverse=True)

    # Determine number of recommendations based on enhancement level
    max_recommendations = {
        "minimal": 1,
        "moderate": 3,
        "comprehensive": 5
    }.get(enhancement_level, 3)

    # Create recommendations
    recommendations = []
    for font, score in font_scores[:max_recommendations]:
        try:
            # Generate rationale
            rationale = _generate_font_rationale(font, normalized_traits, score)

            # Determine use cases
            use_cases = _determine_use_cases(font, normalized_traits)

            # Select recommended weights
            recommended_weights = _select_font_weights(font, normalized_traits)

            recommendation = FontRecommendation(
                google_font=font,
                confidence_score=max(0.7, min(1.0, score)),  # Ensure within bounds
                rationale=rationale,
                use_cases=use_cases,
                recommended_weights=recommended_weights,
                alternatives=[]  # Could be populated later
            )
            recommendations.append(recommendation)

        except Exception as e:
            # Skip this font if recommendation creation fails
            print(f"Warning: Failed to create recommendation for {font.family}: {e}", file=sys.stderr)
            continue

    if not recommendations:
        raise MatchingError("Failed to create any font recommendations")

    return recommendations


def _calculate_category_weights(traits: List[str]) -> Dict[str, float]:
    """Calculate font category weights based on personality traits."""

    # Base weights (neutral)
    weights = {
        "sans-serif": 0.4,
        "serif": 0.3,
        "display": 0.15,
        "handwriting": 0.1,
        "monospace": 0.05
    }

    # Trait-based adjustments
    trait_mappings = {
        # Professional traits favor sans-serif and serif
        "professional": {"sans-serif": +0.3, "serif": +0.2, "display": -0.1},
        "corporate": {"sans-serif": +0.3, "serif": +0.2, "display": -0.2, "handwriting": -0.1},
        "business": {"sans-serif": +0.2, "serif": +0.2, "display": -0.1},
        "formal": {"serif": +0.3, "sans-serif": +0.1, "display": -0.1, "handwriting": -0.2},
        "trustworthy": {"serif": +0.2, "sans-serif": +0.2, "display": -0.1},

        # Modern traits favor sans-serif
        "modern": {"sans-serif": +0.3, "display": +0.1, "serif": -0.1},
        "contemporary": {"sans-serif": +0.2, "display": +0.1, "serif": -0.1},
        "clean": {"sans-serif": +0.3, "serif": -0.1, "display": -0.1},
        "minimal": {"sans-serif": +0.3, "serif": -0.2, "display": -0.2},
        "simple": {"sans-serif": +0.2, "serif": -0.1, "display": -0.1},

        # Creative traits favor display and handwriting
        "creative": {"display": +0.3, "handwriting": +0.2, "sans-serif": -0.1},
        "artistic": {"display": +0.3, "handwriting": +0.3, "serif": -0.1},
        "expressive": {"display": +0.2, "handwriting": +0.2},
        "playful": {"display": +0.2, "handwriting": +0.1, "serif": -0.2},
        "fun": {"display": +0.2, "handwriting": +0.1, "serif": -0.1},

        # Traditional traits favor serif
        "traditional": {"serif": +0.4, "sans-serif": -0.1, "display": -0.2},
        "classic": {"serif": +0.3, "sans-serif": -0.1, "display": -0.1},
        "elegant": {"serif": +0.3, "display": +0.1, "handwriting": -0.1},
        "sophisticated": {"serif": +0.2, "sans-serif": +0.1, "display": -0.1},
        "luxury": {"serif": +0.2, "display": +0.1, "handwriting": -0.2},

        # Technical traits favor monospace and sans-serif
        "technical": {"monospace": +0.3, "sans-serif": +0.2, "serif": -0.1, "handwriting": -0.2},
        "code": {"monospace": +0.4, "sans-serif": +0.1, "serif": -0.2, "handwriting": -0.2},
        "digital": {"sans-serif": +0.2, "monospace": +0.1, "serif": -0.1},
        "tech": {"sans-serif": +0.2, "monospace": +0.1, "serif": -0.1},

        # Personal traits favor handwriting
        "personal": {"handwriting": +0.3, "serif": +0.1, "sans-serif": -0.1},
        "handwritten": {"handwriting": +0.4, "display": -0.2, "sans-serif": -0.2},
        "informal": {"handwriting": +0.2, "display": +0.1, "serif": -0.2},

        # Bold traits favor display
        "bold": {"display": +0.2, "sans-serif": +0.1, "serif": -0.1},
        "strong": {"sans-serif": +0.2, "display": +0.1, "serif": -0.1},
        "impactful": {"display": +0.2, "sans-serif": +0.1},

        # Readable traits favor sans-serif
        "readable": {"sans-serif": +0.2, "serif": +0.1, "display": -0.1, "handwriting": -0.2},
        "clear": {"sans-serif": +0.2, "serif": +0.1, "display": -0.1, "handwriting": -0.1},
        "legible": {"sans-serif": +0.2, "serif": +0.1, "display": -0.1, "handwriting": -0.2},
    }

    # Apply trait adjustments
    for trait in traits:
        if trait in trait_mappings:
            for category, adjustment in trait_mappings[trait].items():
                weights[category] = max(0.0, weights[category] + adjustment)

    # Normalize weights to sum to 1.0
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}

    return weights


def _score_font_for_personality(font: GoogleFont, traits: List[str], category_weights: Dict[str, float]) -> float:
    """Score a font based on how well it matches the personality traits."""

    # Base score from category match
    base_score = category_weights.get(font.category, 0.1)

    # Family name bonus for certain traits
    family_lower = font.family.lower()
    family_bonus = 0.0

    # Professional family names
    if any(trait in ["professional", "corporate", "business"] for trait in traits):
        if any(word in family_lower for word in ["inter", "roboto", "open", "source", "system", "work"]):
            family_bonus += 0.1

    # Modern family names
    if any(trait in ["modern", "contemporary", "clean"] for trait in traits):
        if any(word in family_lower for word in ["inter", "montserrat", "lato", "nunito", "poppins"]):
            family_bonus += 0.1

    # Creative family names
    if any(trait in ["creative", "artistic", "playful"] for trait in traits):
        if any(word in family_lower for word in ["pacifico", "dancing", "lobster", "comfortaa", "quicksand"]):
            family_bonus += 0.1

    # Traditional family names
    if any(trait in ["traditional", "classic", "elegant"] for trait in traits):
        if any(word in family_lower for word in ["times", "georgia", "playfair", "libre", "crimson"]):
            family_bonus += 0.1

    # Variant richness bonus (more weights = more versatile)
    variant_bonus = min(0.1, len(font.variants) * 0.01)

    # Popularity bonus for well-known fonts
    popular_fonts = ["inter", "roboto", "open sans", "lato", "montserrat", "source sans pro"]
    popularity_bonus = 0.05 if any(popular in family_lower for popular in popular_fonts) else 0.0

    final_score = base_score + family_bonus + variant_bonus + popularity_bonus

    return min(1.0, final_score)


def _generate_font_rationale(font: GoogleFont, traits: List[str], score: float) -> str:
    """Generate human-readable rationale for font selection."""

    # Base rationale based on category
    category_rationales = {
        "sans-serif": f"{font.family} is a clean, modern sans-serif font that provides excellent readability",
        "serif": f"{font.family} is an elegant serif font that conveys tradition and sophistication",
        "display": f"{font.family} is a distinctive display font that makes a strong visual impact",
        "handwriting": f"{font.family} offers a personal, handwritten feel that adds warmth",
        "monospace": f"{font.family} is a technical monospace font ideal for code and data"
    }

    base_rationale = category_rationales.get(font.category, f"{font.family} is a versatile font")

    # Add personality-specific reasoning
    trait_reasons = []
    if any(trait in ["professional", "corporate", "business"] for trait in traits):
        trait_reasons.append("perfect for professional and corporate communications")

    if any(trait in ["modern", "contemporary", "clean"] for trait in traits):
        trait_reasons.append("aligns with modern design principles")

    if any(trait in ["creative", "artistic", "playful"] for trait in traits):
        trait_reasons.append("supports creative expression and artistic branding")

    if any(trait in ["readable", "clear", "legible"] for trait in traits):
        trait_reasons.append("ensures optimal readability across all applications")

    if any(trait in ["trustworthy", "reliable", "stable"] for trait in traits):
        trait_reasons.append("builds trust and conveys reliability")

    # Combine rationale parts
    full_rationale = base_rationale

    if trait_reasons:
        full_rationale += f", making it {trait_reasons[0]}"
        if len(trait_reasons) > 1:
            full_rationale += f" and {trait_reasons[1]}"

    # Add confidence context
    if score > 0.9:
        full_rationale += ". This is an excellent match for your brand characteristics."
    elif score > 0.8:
        full_rationale += ". This is a strong match for your brand personality."
    else:
        full_rationale += ". This provides a good foundation for your brand typography."

    return full_rationale


def _determine_use_cases(font: GoogleFont, traits: List[str]) -> List[str]:
    """Determine appropriate use cases for a font based on its characteristics."""

    use_cases = []

    # Category-based use cases
    if font.category == "sans-serif":
        use_cases.extend(["headings", "body", "navigation", "CTAs"])
    elif font.category == "serif":
        use_cases.extend(["headings", "body", "emphasis"])
    elif font.category == "display":
        use_cases.extend(["headings", "quotes", "emphasis"])
    elif font.category == "handwriting":
        use_cases.extend(["quotes", "emphasis", "captions"])
    elif font.category == "monospace":
        use_cases.extend(["labels", "captions", "forms"])

    # Trait-based refinements
    if any(trait in ["professional", "corporate"] for trait in traits):
        use_cases = [case for case in use_cases if case not in ["quotes"]]
        if "forms" not in use_cases:
            use_cases.append("forms")

    if any(trait in ["creative", "artistic"] for trait in traits):
        if "quotes" not in use_cases:
            use_cases.append("quotes")

    # Ensure we have at least one use case
    if not use_cases:
        use_cases = ["headings"]

    return list(set(use_cases))  # Remove duplicates


def _select_font_weights(font: GoogleFont, traits: List[str]) -> List[str]:
    """Select appropriate font weights based on available variants and traits."""

    available_weights = [v for v in font.variants if v.isdigit()]

    if not available_weights:
        # Handle non-numeric variants
        if "regular" in font.variants:
            available_weights.append("400")
        if "bold" in font.variants:
            available_weights.append("700")

    if not available_weights:
        return ["400"]  # Fallback

    # Convert to integers for sorting
    weight_numbers = []
    for weight in available_weights:
        try:
            weight_numbers.append(int(weight))
        except ValueError:
            continue

    weight_numbers.sort()

    # Select weights based on traits
    selected = []

    # Always include regular weight if available
    if 400 in weight_numbers:
        selected.append("400")
    elif weight_numbers:
        # Find closest to 400
        closest = min(weight_numbers, key=lambda x: abs(x - 400))
        selected.append(str(closest))

    # Add bold for headings
    if any(weight >= 600 for weight in weight_numbers):
        bold_weights = [w for w in weight_numbers if w >= 600]
        selected.append(str(min(bold_weights)))

    # Add light weight for creative/elegant brands
    if any(trait in ["elegant", "light", "minimal"] for trait in traits):
        if any(weight <= 300 for weight in weight_numbers):
            light_weights = [w for w in weight_numbers if w <= 300]
            selected.append(str(max(light_weights)))

    # Add extra bold for impactful brands
    if any(trait in ["bold", "strong", "impactful"] for trait in traits):
        if any(weight >= 800 for weight in weight_numbers):
            heavy_weights = [w for w in weight_numbers if w >= 800]
            selected.append(str(min(heavy_weights)))

    # Remove duplicates and ensure we have at least one weight
    selected = list(set(selected))
    if not selected:
        selected = ["400"]

    return selected


# ============================================================================
# Typography System Generator
# ============================================================================

def generate_typography_hierarchy(
    primary_font: FontRecommendation,
    secondary_font: Optional[FontRecommendation] = None,
    enhancement_level: str = "moderate"
) -> TypographyHierarchy:
    """
    Generate complete typography hierarchy from font recommendations.

    Args:
        primary_font: Main font for headings and emphasis
        secondary_font: Supporting font for body text (optional)
        enhancement_level: System complexity level

    Returns:
        Complete typography hierarchy with styles and guidelines
    """
    # Generate heading styles
    heading_styles = _generate_heading_styles(primary_font, enhancement_level)

    # Generate text styles
    text_styles = _generate_text_styles(secondary_font or primary_font, enhancement_level)

    # Generate CSS snippet
    css_snippet = _generate_css_snippet(primary_font, secondary_font, heading_styles, text_styles)

    # Generate font URLs
    font_urls = _generate_font_urls(primary_font, secondary_font)

    return TypographyHierarchy(
        primary_font=primary_font,
        secondary_font=secondary_font,
        accent_font=None,  # Could be added in future
        heading_styles=heading_styles,
        text_styles=text_styles,
        css_snippet=css_snippet,
        font_urls=font_urls
    )


def _generate_heading_styles(font_rec: FontRecommendation, enhancement_level: str) -> Dict[str, FontStyle]:
    """Generate H1-H6 heading styles with appropriate sizing."""

    font_family = font_rec.google_font.family

    # Determine which weights to use
    weights = font_rec.recommended_weights
    bold_weight = next((w for w in weights if int(w) >= 600), weights[-1] if weights else "700")
    regular_weight = next((w for w in weights if int(w) <= 500), weights[0] if weights else "400")

    # Base font sizes (rem) with scaling ratios
    base_sizes = {
        "h1": 3.0,
        "h2": 2.25,
        "h3": 1.875,
        "h4": 1.5,
        "h5": 1.25,
        "h6": 1.125
    }

    # Line height ratios for readability
    line_heights = {
        "h1": 1.2,
        "h2": 1.25,
        "h3": 1.3,
        "h4": 1.35,
        "h5": 1.4,
        "h6": 1.45
    }

    # Margin bottom spacing
    margin_bottoms = {
        "h1": "1.5rem",
        "h2": "1.25rem",
        "h3": "1rem",
        "h4": "0.75rem",
        "h5": "0.5rem",
        "h6": "0.5rem"
    }

    # Determine heading levels based on enhancement level
    if enhancement_level == "minimal":
        headings_to_generate = ["h1", "h2", "h3"]
    elif enhancement_level == "moderate":
        headings_to_generate = ["h1", "h2", "h3", "h4"]
    else:  # comprehensive
        headings_to_generate = ["h1", "h2", "h3", "h4", "h5", "h6"]

    styles = {}
    for heading in headings_to_generate:
        # Use bold weight for main headings, regular for smaller ones
        weight = bold_weight if heading in ["h1", "h2", "h3"] else regular_weight

        styles[heading] = FontStyle(
            font_family=font_family,
            font_weight=weight,
            font_size=f"{base_sizes[heading]}rem",
            line_height=line_heights[heading],
            margin_bottom=margin_bottoms[heading]
        )

    return styles


def _generate_text_styles(font_rec: FontRecommendation, enhancement_level: str) -> Dict[str, FontStyle]:
    """Generate body and text styles."""

    font_family = font_rec.google_font.family

    # Determine weights
    weights = font_rec.recommended_weights
    regular_weight = next((w for w in weights if int(w) <= 500), weights[0] if weights else "400")
    medium_weight = next((w for w in weights if 500 <= int(w) <= 600), regular_weight)
    bold_weight = next((w for w in weights if int(w) >= 600), weights[-1] if weights else "700")

    # Base text styles
    base_styles = {
        "body": FontStyle(
            font_family=font_family,
            font_weight=regular_weight,
            font_size="1rem",
            line_height=1.6,
            margin_bottom="1rem"
        ),
        "caption": FontStyle(
            font_family=font_family,
            font_weight=regular_weight,
            font_size="0.875rem",
            line_height=1.5,
            margin_bottom="0.5rem"
        ),
        "emphasis": FontStyle(
            font_family=font_family,
            font_weight=medium_weight,
            font_size="1rem",
            line_height=1.6,
            margin_bottom=None
        )
    }

    # Add more styles for comprehensive level
    if enhancement_level == "comprehensive":
        base_styles.update({
            "lead": FontStyle(
                font_family=font_family,
                font_weight=regular_weight,
                font_size="1.25rem",
                line_height=1.7,
                margin_bottom="1.5rem"
            ),
            "small": FontStyle(
                font_family=font_family,
                font_weight=regular_weight,
                font_size="0.75rem",
                line_height=1.4,
                margin_bottom="0.5rem"
            ),
            "blockquote": FontStyle(
                font_family=font_family,
                font_weight=medium_weight,
                font_size="1.125rem",
                line_height=1.65,
                margin_bottom="1rem"
            )
        })

    return base_styles


def _generate_css_snippet(
    primary_font: FontRecommendation,
    secondary_font: Optional[FontRecommendation],
    heading_styles: Dict[str, FontStyle],
    text_styles: Dict[str, FontStyle]
) -> str:
    """Generate ready-to-use CSS snippet."""

    css_lines = []

    # Google Fonts import
    fonts_to_import = [primary_font]
    if secondary_font and secondary_font.google_font.family != primary_font.google_font.family:
        fonts_to_import.append(secondary_font)

    import_urls = []
    for font_rec in fonts_to_import:
        family = font_rec.google_font.family.replace(" ", "+")
        weights = ":wght@" + ";".join(font_rec.recommended_weights)
        import_urls.append(f"family={family}{weights}")

    if import_urls:
        google_fonts_url = "https://fonts.googleapis.com/css2?" + "&".join(import_urls) + "&display=swap"
        css_lines.append(f"@import url('{google_fonts_url}');")
        css_lines.append("")

    # CSS custom properties for easier customization
    css_lines.append(":root {")
    css_lines.append(f"  --font-primary: '{primary_font.google_font.family}', sans-serif;")
    if secondary_font:
        css_lines.append(f"  --font-secondary: '{secondary_font.google_font.family}', sans-serif;")
    css_lines.append("}")
    css_lines.append("")

    # Heading styles
    for heading, style in heading_styles.items():
        css_lines.append(f"{heading} {{")
        css_lines.append(f"  font-family: '{style.font_family}', sans-serif;")
        css_lines.append(f"  font-weight: {style.font_weight};")
        css_lines.append(f"  font-size: {style.font_size};")
        css_lines.append(f"  line-height: {style.line_height};")
        if style.margin_bottom:
            css_lines.append(f"  margin-bottom: {style.margin_bottom};")
        css_lines.append("}")
        css_lines.append("")

    # Text styles
    for style_name, style in text_styles.items():
        class_name = f".text-{style_name}" if style_name != "body" else "body, p"
        css_lines.append(f"{class_name} {{")
        css_lines.append(f"  font-family: '{style.font_family}', sans-serif;")
        css_lines.append(f"  font-weight: {style.font_weight};")
        css_lines.append(f"  font-size: {style.font_size};")
        css_lines.append(f"  line-height: {style.line_height};")
        if style.margin_bottom:
            css_lines.append(f"  margin-bottom: {style.margin_bottom};")
        css_lines.append("}")
        css_lines.append("")

    return "\n".join(css_lines)


def _generate_font_urls(
    primary_font: FontRecommendation,
    secondary_font: Optional[FontRecommendation]
) -> Dict[str, str]:
    """Generate font loading URLs for web usage."""

    urls = {}

    # Primary font CSS URL
    family = primary_font.google_font.family.replace(" ", "+")
    weights = ":wght@" + ";".join(primary_font.recommended_weights)
    urls["primary_css"] = f"https://fonts.googleapis.com/css2?family={family}{weights}&display=swap"

    # Secondary font CSS URL
    if secondary_font and secondary_font.google_font.family != primary_font.google_font.family:
        family = secondary_font.google_font.family.replace(" ", "+")
        weights = ":wght@" + ";".join(secondary_font.recommended_weights)
        urls["secondary_css"] = f"https://fonts.googleapis.com/css2?family={family}{weights}&display=swap"

    # Combined URL for both fonts
    fonts_to_combine = [primary_font]
    if secondary_font and secondary_font.google_font.family != primary_font.google_font.family:
        fonts_to_combine.append(secondary_font)

    combined_families = []
    for font_rec in fonts_to_combine:
        family = font_rec.google_font.family.replace(" ", "+")
        weights = ":wght@" + ";".join(font_rec.recommended_weights)
        combined_families.append(f"family={family}{weights}")

    if combined_families:
        urls["combined_css"] = f"https://fonts.googleapis.com/css2?{' &'.join(combined_families)}&display=swap"

    return urls


# ============================================================================
# Main Font Selection Function
# ============================================================================

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
    start_time = time.time()

    try:
        # If existing typography is provided, preserve it
        if existing_typography and existing_typography.primary_font:
            processing_time = time.time() - start_time
            metadata = FontSelectionMetadata(
                selection_method="preserved",
                processing_time=processing_time,
                fonts_considered=0,
                api_calls_made=0,
                cache_hit=True,
                fallback_used=False
            )
            return FontSelectionResponse(
                typography=existing_typography,
                selection_metadata=metadata
            )

        # Get available fonts
        try:
            available_fonts = fetch_google_fonts()
            api_calls_made = 1
            cache_hit = False
        except GoogleFontsAPIError:
            # Try cache as fallback
            cached_fonts = get_cached_fonts()
            if cached_fonts:
                available_fonts = cached_fonts
                api_calls_made = 0
                cache_hit = True
            else:
                raise GoogleFontsAPIError("Both API and cache unavailable")

        # Match fonts to personality
        font_recommendations = match_fonts_to_personality(
            criteria.brand_personality,
            available_fonts,
            criteria.enhancement_level
        )

        # Select primary and secondary fonts
        primary_font = font_recommendations[0]
        secondary_font = font_recommendations[1] if len(font_recommendations) > 1 else None

        # Generate typography hierarchy
        typography = generate_typography_hierarchy(
            primary_font,
            secondary_font,
            criteria.enhancement_level
        )

        processing_time = time.time() - start_time

        # Create selection metadata
        metadata = FontSelectionMetadata(
            selection_method="rule-based",
            processing_time=processing_time,
            fonts_considered=len(available_fonts),
            api_calls_made=api_calls_made,
            cache_hit=cache_hit,
            fallback_used=False
        )

        return FontSelectionResponse(
            typography=typography,
            selection_metadata=metadata
        )

    except Exception as e:
        # Comprehensive fallback system with multiple options
        fallback_fonts = [
            {
                "family": "Inter",
                "category": "sans-serif",
                "variants": ["300", "400", "600", "700"],
                "rationale": "Inter is a modern, highly readable font designed for user interfaces and digital displays."
            },
            {
                "family": "Open Sans",
                "category": "sans-serif",
                "variants": ["400", "600", "700"],
                "rationale": "Open Sans is a reliable, widely-supported font that ensures readability across all platforms."
            },
            {
                "family": "Roboto",
                "category": "sans-serif",
                "variants": ["300", "400", "500", "700"],
                "rationale": "Roboto provides excellent readability and is optimized for both web and mobile interfaces."
            },
            {
                "family": "Arial",
                "category": "sans-serif",
                "variants": ["400", "700"],
                "rationale": "Arial is a universal system font that provides maximum compatibility across all devices."
            }
        ]

        for fallback_data in fallback_fonts:
            try:
                fallback_font = GoogleFont(
                    family=fallback_data["family"],
                    category=fallback_data["category"],
                    variants=fallback_data["variants"]
                )

                fallback_recommendation = FontRecommendation(
                    google_font=fallback_font,
                    confidence_score=0.7,
                    rationale=fallback_data["rationale"],
                    use_cases=["headings", "body"],
                    recommended_weights=fallback_data["variants"]
                )

                typography = generate_typography_hierarchy(
                    fallback_recommendation,
                    None,
                    criteria.enhancement_level
                )

                processing_time = time.time() - start_time
                metadata = FontSelectionMetadata(
                    selection_method="fallback",
                    processing_time=processing_time,
                    fonts_considered=len(fallback_fonts),
                    api_calls_made=0,
                    cache_hit=False,
                    fallback_used=True
                )

                return FontSelectionResponse(
                    typography=typography,
                    selection_metadata=metadata
                )

            except Exception as fallback_error:
                # Try next fallback font
                continue

        # If all fallbacks failed
        raise FontSelectionError(f"Font selection failed and all fallbacks failed: {e}")


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

    # Font selection enhancement (new feature)
    typography_response = None
    if not content.get("has_existing_typography", False):
        try:
            # Create font selection criteria from brand context
            criteria = FontSelectionCriteria(
                brand_personality=content.get("personality_indicators", ["professional"]),
                target_audience=content.get("audience_descriptors", ["users"])[0] if content.get("audience_descriptors") else "users",
                brand_voice=", ".join(content.get("personality_indicators", ["professional"])[:3]),
                enhancement_level=args.enhancement_level,
                existing_colors=content.get("colors", []),
                industry_context=content.get("industry_context")
            )

            # Select fonts
            font_selection = select_fonts(criteria)
            typography_response = font_selection  # Keep the full FontSelectionResponse

            if args.debug:
                print(f"Font selection completed in {font_selection.selection_metadata.processing_time:.2f}s", file=sys.stderr)
                print(f"Selected font: {font_selection.typography.primary_font.google_font.family} (confidence: {font_selection.typography.primary_font.confidence_score:.2f})", file=sys.stderr)

        except Exception as e:
            if args.debug:
                print(f"Font selection failed: {e}", file=sys.stderr)
            # Continue without typography - don't fail the entire enhancement
            typography_response = None

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

    # Track which gaps were filled
    gaps_filled = ["color_palette"]

    result = {
        "brandName": content.get("brand_name", "Unknown Brand"),
        "colorPalette": enhanced_color_palette,
        "enhancement_metadata": {
            "workflow_id": workflow_id,
            "enhancement_level": args.enhancement_level,
            "gaps_filled": gaps_filled,
            "processing_time": total_time,
            "llm_provider": args.llm_provider,
            "user_feedback_count": user_feedback_count
        }
    }

    # Add typography if font selection was successful
    if typography_response:
        result["typography"] = {
            "primary_font": typography_response.typography.primary_font.model_dump() if typography_response.typography.primary_font else None,
            "secondary_font": typography_response.typography.secondary_font.model_dump() if typography_response.typography.secondary_font else None,
            "accent_font": typography_response.typography.accent_font.model_dump() if typography_response.typography.accent_font else None,
            "heading_styles": {k: v.model_dump() for k, v in typography_response.typography.heading_styles.items()},
            "text_styles": {k: v.model_dump() for k, v in typography_response.typography.text_styles.items()},
            "css_snippet": typography_response.typography.css_snippet,
            "font_urls": typography_response.typography.font_urls
        }
        gaps_filled.append("typography")

        # Add typography metadata to enhancement metadata
        result["enhancement_metadata"]["typography_enhancement"] = True
        result["enhancement_metadata"]["typography_method"] = typography_response.selection_metadata.selection_method
        result["enhancement_metadata"]["font_selection_time"] = typography_response.selection_metadata.processing_time

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

        # Extract typography context for font selection
        typography_context = extract_typography_context_from_brand(content)
        brand_data.update(typography_context)

        return brand_data

    except Exception as e:
        raise ValueError(f"Error reading brand file: {str(e)}")


def extract_typography_context_from_brand(brand_content: str) -> dict:
    """
    Extract typography-relevant information from brand markdown.

    Args:
        brand_content: Raw brand markdown content

    Returns:
        Dictionary with typography context including existing fonts and personality indicators
    """
    content_lower = brand_content.lower()

    # Check for existing typography specifications
    has_existing_typography = any(keyword in content_lower for keyword in [
        "font family", "typography", "typeface", "font:", "fonts:"
    ])

    existing_fonts = []
    if has_existing_typography:
        # Extract font family names
        font_patterns = [
            r'font[- ]family:\s*["\']?([^"\'\n]+)["\']?',
            r'font:\s*["\']?([^"\'\n]+)["\']?',
            r'typography:\s*["\']?([^"\'\n]+)["\']?',
            r'typeface:\s*["\']?([^"\'\n]+)["\']?'
        ]

        for pattern in font_patterns:
            matches = re.findall(pattern, brand_content, re.IGNORECASE)
            existing_fonts.extend([match.strip() for match in matches])

    # Extract personality indicators
    personality_indicators = []

    # Brand voice extraction
    voice_match = re.search(r'(?:brand\s+voice|voice):\s*(.+)', brand_content, re.IGNORECASE)
    if voice_match:
        voice_text = voice_match.group(1).strip()
        # Split on common separators
        voice_traits = re.split(r'[,;]\s*', voice_text)
        personality_indicators.extend([trait.strip() for trait in voice_traits if trait.strip()])

    # Brand personality extraction
    personality_match = re.search(r'(?:brand\s+personality|personality):\s*(.+)', brand_content, re.IGNORECASE)
    if personality_match:
        personality_text = personality_match.group(1).strip()
        personality_traits = re.split(r'[,;]\s*', personality_text)
        personality_indicators.extend([trait.strip() for trait in personality_traits if trait.strip()])

    # Extract from general descriptive text
    descriptive_keywords = [
        "professional", "modern", "clean", "elegant", "sophisticated", "friendly",
        "creative", "artistic", "bold", "minimalist", "traditional", "classic",
        "innovative", "trustworthy", "reliable", "technical", "casual", "formal"
    ]

    for keyword in descriptive_keywords:
        if keyword in content_lower:
            personality_indicators.append(keyword)

    # Extract audience descriptors
    audience_descriptors = []
    audience_match = re.search(r'(?:target\s+audience|audience):\s*(.+)', brand_content, re.IGNORECASE)
    if audience_match:
        audience_text = audience_match.group(1).strip()
        audience_descriptors.append(audience_text)

    # Extract industry context
    industry_context = None
    industry_match = re.search(r'industry:\s*(.+)', brand_content, re.IGNORECASE)
    if industry_match:
        industry_context = industry_match.group(1).strip()

    return {
        "has_existing_typography": has_existing_typography,
        "existing_fonts": list(set(existing_fonts)),  # Remove duplicates
        "personality_indicators": list(set(personality_indicators)),
        "audience_descriptors": audience_descriptors,
        "industry_context": industry_context
    }


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