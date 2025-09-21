#!/usr/bin/env python3
"""
Article Outline Generator - Enhanced Constitutional Single-File Python Agent (Feature 012)

PURPOSE:
Generate structured outlines for articles and stories from markdown descriptions.
Automatically detects content type, language, and creates hierarchical sections
with summaries, key points, and word count estimates. Enhanced with interim
classification support and LLM fallback for ambiguous content.

USAGE:
    # Basic usage with markdown input
    echo "# Article Title\nContent..." | python article_outline_generator.py run

    # JSON input with enhanced options
    python article_outline_generator.py run --input-type json << 'EOF'
    {
      "content": "# Story Title\nNarrative...",
      "target_depth": 4,
      "interim": true,
      "classification_method": "auto",
      "timeout_ms": 2000
    }
    EOF

    # Enhanced CLI flags
    python article_outline_generator.py run --interim --classification-method auto --timeout-ms 1000

    # Available commands
    python article_outline_generator.py {run|selfcheck|print-schemas|dry-run}

ENHANCED FEATURES (Feature 012):
- Interim classification: Early classification results before full outline generation
- LLM fallback: PydanticAI integration for low-confidence content (<0.8)
- Enhanced metadata: Classification confidence, method, reasoning, key indicators
- Cost tracking: Token usage and USD cost for LLM calls
- Multiple classification methods: auto, rules_only, llm_preferred

INPUT CONTENT TYPES:
- text/markdown: Direct markdown content (default)
- application/json: Structured input with enhanced options

CLI FLAGS:
- --interim: Request interim classification response
- --classification-method: auto (default) | rules_only | llm_preferred
- --timeout-ms: Timeout for interim responses (100-30000ms)
- --strict: Disable LLM fallback (STRICT mode, default)

EXAMPLE ENHANCED ENVELOPE OUTPUT:
{
  "meta": {
    "agent": "article_outline_generator",
    "version": "1.0.0",
    "cost": {"tokens_in": 25, "tokens_out": 50, "usd": 0.002, "llm_calls": 1},
    "classification_enhanced": true,
    "fallback_used": false
  },
  "input": {
    "content": "# Title\nContent...",
    "target_depth": 3,
    "interim": false,
    "classification_method": "auto"
  },
  "output": {
    "meta": {
      "content_type": "article",
      "detected_language": "en",
      "classification_confidence": 0.85,
      "classification_method": "llm_single",
      "classification_reasoning": "LLM enhanced: Instructional content detected",
      "key_indicators": ["how to", "guide", "tutorial"],
      "llm_calls_used": 1,
      "processing_time_ms": 150,
      "interim_available": false
    },
    "outline": [{"title": "Introduction", "level": 1, ...}]
  },
  "error": null
}

INTERIM RESPONSE EXAMPLE:
{
  "output": {
    "meta": {
      "content_type": "article",
      "classification_confidence": 0.9,
      "classification_method": "rule_based",
      "interim_available": true,
      "processing_time_ms": 50
    },
    "outline": []  // Empty for interim
  }
}

DECLARED BUDGETS:
- Runtime: <5 seconds per execution
- LLM calls: <2 calls (fallback only for ambiguous classification)
- Tokens: <2000 tokens total
- Memory: <100MB working set

DEPENDENCY PINS:
- pydantic>=2.0.0 (required for models)
- pydantic-ai>=0.0.1 (required for LLM integration)
- Standard library: argparse, pathlib, json, typing, datetime, re, logging, hashlib

ENHANCED NUMBERED FLOW:
1. Parse CLI arguments and load configuration
2. Normalize input (markdown -> enhanced InputModel)
3. Classify content type using decision tables
4. Check classification confidence and method preference
5. Enhance with LLM if confidence < 0.8 and enabled (PydanticAI)
6. Return interim response if requested and within timeout
7. Detect language using pattern matching
8. Generate outline using template-based approach
9. Package in Agent Envelope with enhanced metadata and cost tracking
10. Return JSON response with comprehensive observability data

CONSTITUTIONAL COMPLIANCE:
- Article II: Agent Envelope format with enhanced metadata
- Article X: STRICT mode default, LLM as fallback only
- Article XI: All LLM calls through PydanticAI with proper typing
- Article XVIII: Structured JSONL logging for observability
- Article XX: CLI compliance with enhanced flags
"""

import argparse
import hashlib
import json
import logging
import re
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

# Constitutional requirement: pydantic>=2
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Constitutional requirement: pydantic-ai for LLM integration (Feature 012)
try:
    from pydantic_ai import Agent, RunContext

    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    from typing import Any
    Agent = Any  # type: ignore
    RunContext = Any  # type: ignore
    PYDANTIC_AI_AVAILABLE = False

# ============================================================================
# CONFIGURATION SECTION (Lines 67-120)
# Constitutional Article V: Hierarchical Configuration
# ============================================================================


@dataclass
class ModelConfig:
    """LLM model configuration with provider abstraction."""

    enabled: bool = False  # STRICT mode by default (Constitutional Article X)
    provider: Literal["openai", "anthropic", "azure", "gemini", "local"] = "openai"
    base_url: str | None = None
    path: str | None = None
    name: str = "gpt-4"
    api_key_env: str = "OPENAI_API_KEY"
    timeout_s: int = 30
    max_tokens: int = 2000
    temperature: float = 0.1
    top_p: float | None = None
    extra_headers: dict[str, str] | None = None
    # Enhanced for PydanticAI integration (Feature 012)
    confidence_threshold: float = 0.8
    max_retries: int = 1


@dataclass
class AgentConfig:
    """Agent-specific configuration."""

    brand_token: str = "default"
    log_level: str = "INFO"
    strict: bool = True  # Disable LLM by default


@dataclass
class Config:
    """Main configuration with hierarchical precedence."""

    model: ModelConfig
    agent: AgentConfig


# Configuration defaults
DEFAULT_CONFIG = Config(model=ModelConfig(), agent=AgentConfig())

# ============================================================================
# PYDANTIC MODELS (Constitutional Article II: Contract-First)
# ============================================================================


# T015: InputModel Pydantic class
class InputModel(BaseModel):
    """Normalized input from markdown content."""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(..., min_length=1, description="Markdown content description")
    target_depth: int = Field(
        default=3, ge=1, le=6, description="Desired outline depth (1-6)"
    )
    content_type_hint: Literal["article", "story"] | None = Field(
        default=None, description="Optional content type hint"
    )
    language_hint: str | None = Field(
        default=None,
        pattern=r"^[a-z]{2}$",
        description="Optional ISO 639-1 language code",
    )
    include_word_counts: bool = Field(
        default=True, description="Whether to generate word count estimates"
    )

    # Enhanced fields for interim classification (Feature 012)
    interim: bool = Field(
        default=False, description="Request interim classification during processing"
    )
    timeout_ms: int | None = Field(
        default=None,
        ge=100,
        le=30000,
        description="Timeout for interim responses (100-30000ms)",
    )
    classification_method: Literal["auto", "rules_only", "llm_preferred"] = Field(
        default="auto", description="Classification method preference"
    )

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        """Validate content is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty or whitespace-only")
        return v


# T016: OutlineMetadata Pydantic class
class OutlineMetadata(BaseModel):
    """Metadata about the generated outline."""

    content_type: Literal["article", "story"]
    detected_language: str = Field(..., pattern=r"^[a-z]{2}$")
    depth: int = Field(..., ge=1, le=6)
    sections_count: int = Field(..., ge=0)
    generated_at: datetime
    notes: str | None = None

    # Enhanced classification fields (Feature 012) - with defaults for backward compatibility
    classification_confidence: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Classification confidence score"
    )
    classification_method: Literal["rule_based", "llm_single", "llm_double"] = Field(
        default="rule_based", description="Method used for classification"
    )
    classification_reasoning: str = Field(
        default="Rule-based classification",
        min_length=1,
        description="Why this classification was chosen",
    )
    key_indicators: list[str] = Field(
        default_factory=list, description="Key content indicators found"
    )
    llm_calls_used: int = Field(
        default=0, ge=0, le=2, description="Number of LLM calls made"
    )
    processing_time_ms: int = Field(
        default=0, ge=0, description="Total processing time in milliseconds"
    )
    interim_available: bool = Field(
        default=False, description="Whether interim classification was requested"
    )


# T017: Section Pydantic class (recursive)
class Section(BaseModel):
    """Individual outline section with hierarchical support."""

    title: str = Field(..., min_length=1)
    id: str | None = Field(default=None, description="Stable slug/identifier")
    level: int = Field(
        default=1, ge=1, le=6, description="Heading level (1=H1, 2=H2, ...)"
    )
    summary: str | None = Field(
        default=None, description="1-3 sentence section synopsis"
    )
    key_points: list[str] = Field(
        default_factory=list, description="Bullet points for section"
    )
    word_count_estimate: int | None = Field(
        default=None, ge=0, description="Estimated word count"
    )
    subsections: list["Section"] = Field(
        default_factory=list, description="Nested subsections"
    )


# T018: OutputModel Pydantic class
class OutputModel(BaseModel):
    """Complete outline response structure."""

    meta: OutlineMetadata
    outline: list[Section] = Field(..., min_length=1, description="Top-level sections")

    @field_validator("outline")
    @classmethod
    def validate_outline_not_empty(cls, v: list[Section]) -> list[Section]:
        """Validate outline is not empty."""
        if not v:
            raise ValueError("Outline cannot be empty")
        return v


# Special case for interim responses (Feature 012)
class InterimOutputModel(BaseModel):
    """Interim response with classification only."""

    meta: OutlineMetadata
    outline: list[Section] = Field(
        default_factory=list, description="Empty for interim responses"
    )


# T019: ErrorModel Pydantic class
class ErrorModel(BaseModel):
    """Error response structure."""

    code: str
    message: str
    details: dict[str, Any] | None = None


# Enhanced models for LLM integration (Feature 012)
# T021: LLMClassificationResult model
class LLMClassificationResult(BaseModel):
    """Typed LLM response for content classification."""

    content_type: Literal["article", "story"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=1)
    key_indicators: list[str] = Field(default_factory=list)
    processing_notes: str | None = Field(
        default=None, description="Additional processing insights"
    )


# T022: ClassificationPrompt model
class ClassificationPrompt(BaseModel):
    """Input structure for LLM classification requests."""

    content: str = Field(..., min_length=1, max_length=2000)
    existing_confidence: float = Field(..., ge=0.0, le=1.0)
    rule_classification: str
    rule_reasoning: str
    context_hints: dict[str, Any] = Field(default_factory=dict)


# T023: Enhanced cost tracking model
class CostModel(BaseModel):
    """Enhanced cost tracking with LLM call limits."""

    tokens_in: int = Field(..., ge=0)
    tokens_out: int = Field(..., ge=0)
    usd: float = Field(..., ge=0.0)
    llm_calls: int = Field(
        ..., ge=0, le=2, description="Max 2 LLM calls per constitutional requirement"
    )


# T020: Agent Envelope classes
class EnvelopeMeta(BaseModel):
    """Agent execution metadata (Constitutional Article II)."""

    agent: Literal["article_outline_generator"]
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    trace_id: str
    ts: datetime
    brand_token: str
    hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    cost: CostModel = Field(
        ..., description="Enhanced cost tracking with LLM call limits"
    )
    prompt_id: str | None = None
    prompt_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$|^$")

    # Enhanced classification metadata (Feature 012)
    classification_enhanced: bool = Field(
        default=False, description="Whether LLM enhancement was used"
    )
    fallback_used: bool = Field(
        default=False, description="Whether fallback to rules was needed"
    )


class AgentEnvelope(BaseModel):
    """Agent response envelope (Constitutional Article II)."""

    meta: EnvelopeMeta
    input: InputModel | dict[str, Any]  # Allow raw input for error cases
    output: OutputModel | InterimOutputModel | None = None
    error: ErrorModel | None = None


# ============================================================================
# PYDANTIC AI INTEGRATION (Feature 012)
# Constitutional Article XI: All LLM calls through PydanticAI
# ============================================================================


def create_classification_agent(config: "Config") -> Any:
    """Create PydanticAI agent for content classification."""
    if not PYDANTIC_AI_AVAILABLE:
        raise RuntimeError(
            "PydanticAI not available - cannot create classification agent"
        )

    if not config.model.enabled:
        raise ValueError("Model must be enabled to create classification agent")

    # Provider string mapping for PydanticAI
    provider_map = {
        "openai": f"openai:{config.model.name}",
        "anthropic": f"anthropic:{config.model.name}",
        "gemini": f"gemini:{config.model.name}",
        "azure": f"azure:{config.model.name}",
        "local": config.model.base_url or "local",
    }

    model_str: str = provider_map.get(config.model.provider, f"openai:{config.model.name}")

    agent = Agent(
        model_str,  # type: ignore[arg-type]
        result_type=LLMClassificationResult,
        system_prompt="""You are a content classification specialist. Analyze the provided content and classify it as either "article" or "story" based on these criteria:

ARTICLE indicators:
- Informational, instructional, factual content
- How-to guides, tutorials, analysis, news
- Third-person perspective, objective tone
- Structured with clear sections/steps

STORY indicators:
- Narrative, creative, personal content
- Fiction, memoir, personal experiences
- Character development, plot elements
- Emotional engagement, subjective perspective

Respond ONLY with valid JSON matching the schema. No additional text, formatting, or backticks.""",
    )

    return agent


def calculate_cost(provider: str, model: str, tokens_in: int, tokens_out: int) -> float:
    """Calculate USD cost based on provider and model."""
    # Pricing as of 2025-09-21 (update as needed)
    pricing = {
        "openai": {
            "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
            "gpt-3.5-turbo": {"input": 0.001 / 1000, "output": 0.002 / 1000},
        },
        "anthropic": {
            "claude-3.5": {"input": 0.015 / 1000, "output": 0.075 / 1000},
            "claude-3": {"input": 0.01 / 1000, "output": 0.05 / 1000},
        },
        "gemini": {
            "gemini-1.5-flash": {"input": 0.001 / 1000, "output": 0.002 / 1000},
        },
    }

    rates = pricing.get(provider, {}).get(
        model, {"input": 0.01 / 1000, "output": 0.02 / 1000}
    )
    return (tokens_in * rates["input"]) + (tokens_out * rates["output"])


def enhance_classification_with_llm(
    content: str,
    classification: dict[str, Any],
    config: "Config",
    logger: logging.Logger,
    trace_id: str,
) -> dict[str, Any]:
    """
    Enhance classification with LLM if confidence is below threshold.

    Constitutional Article X: Typed model calls only as fallback when confidence < 0.8
    """
    if not config.model.enabled:
        log_event(
            logger,
            "model_call",
            provider=config.model.provider,
            enabled=False,
            reason="strict_mode",
            trace_id=trace_id,
        )
        return classification

    if classification["confidence"] >= config.model.confidence_threshold:
        log_event(
            logger,
            "model_call",
            provider=config.model.provider,
            enabled=True,
            reason="confidence_sufficient",
            trace_id=trace_id,
        )
        return classification

    if not PYDANTIC_AI_AVAILABLE:
        log_event(
            logger,
            "fallback_used",
            reason="pydantic_ai_unavailable",
            path="model",
            trace_id=trace_id,
        )
        return {
            **classification,
            "enhancement_used": False,
            "enhancement_error": "PydanticAI not available",
        }

    start_time = datetime.now(timezone.utc)

    try:
        # Create PydanticAI agent
        agent = create_classification_agent(config)

        # Prepare prompt with context
        prompt_text = f"""Content: {content[:1000]}

Rule-based classification: {classification['content_type']} (confidence: {classification['confidence']:.2f})
Reasoning: {classification['why']}

Please provide enhanced classification with reasoning."""

        # Calculate prompt hash for observability
        prompt_hash = generate_hash(prompt_text)

        log_event(
            logger,
            "model_call",
            provider=config.model.provider,
            name=config.model.name,
            prompt_hash=prompt_hash,
            reason="low_confidence",
            trace_id=trace_id,
        )

        # Make LLM call with timeout
        result = agent.run_sync(prompt_text)

        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        # Extract cost information (approximate)
        tokens_in = len(prompt_text.split())
        tokens_out = len(str(result.data).split())
        usd_cost = calculate_cost(
            config.model.provider, config.model.name, tokens_in, tokens_out
        )

        # Log successful call
        log_event(
            logger,
            "model_call",
            provider=config.model.provider,
            name=config.model.name,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            usd=usd_cost,
            duration_ms=duration_ms,
            retry=False,
            prompt_hash=prompt_hash,
            ok=True,
            validation_ok=True,
            trace_id=trace_id,
        )

        # Return enhanced classification
        return {
            "content_type": result.data.content_type,
            "confidence": result.data.confidence,
            "why": f"LLM enhanced: {result.data.reasoning}",
            "key_indicators": result.data.key_indicators,
            "enhancement_used": True,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "usd_cost": usd_cost,
        }

    except Exception as e:
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        # Log failed call
        log_event(
            logger,
            "model_call",
            provider=config.model.provider,
            name=config.model.name,
            duration_ms=duration_ms,
            retry=False,
            prompt_hash=prompt_hash,
            ok=False,
            validation_ok=False,
            error=str(e),
            trace_id=trace_id,
        )

        # Constitutional requirement: deterministic fallback
        log_event(
            logger,
            "fallback_used",
            reason="model_error",
            path="model",
            trace_id=trace_id,
        )

        # Return original classification with error info
        return {
            **classification,
            "enhancement_used": False,
            "enhancement_error": str(e),
        }


# ============================================================================
# DECISION TABLES (Constitutional Article III: Rules Before Models)
# ============================================================================

# T021: Content type classification decision table
CONTENT_TYPE_RULES = [
    # Rule format: (pattern, content_type, confidence, why)
    (
        r"\b(character|plot|story|narrative|once upon|protagonist|dialogue)\b",
        "story",
        0.9,
        "Strong narrative indicators",
    ),
    (
        r"\b(how to|guide|tutorial|step|instruction|method)\b",
        "article",
        0.9,
        "Instructional content",
    ),
    (
        r"\b(analysis|review|opinion|examination|study|research)\b",
        "article",
        0.8,
        "Analytical content",
    ),
    (r"\b(news|breaking|announcement|report|update)\b", "article", 0.8, "News content"),
    (
        r"\b(fiction|novel|tale|adventure|mystery|romance)\b",
        "story",
        0.8,
        "Fiction indicators",
    ),
    (
        r"\b(kingdom|mage|dragon|magic|power|pendant|inheritance|inherited)\b",
        "story",
        0.8,
        "Fantasy story elements",
    ),
    (
        r"\b(discovered|woke up|faced|journey|quest|adventure)\b.*\b(he|she|they|him|her|them)\b",
        "story",
        0.7,
        "Narrative action with characters",
    ),
    (
        r"\b(tips|advice|best practices|strategies|techniques)\b",
        "article",
        0.7,
        "Advisory content",
    ),
    (
        r"\b(memoir|autobiography|personal experience|growing up)\b",
        "story",
        0.7,
        "Personal narrative",
    ),
    (
        r"\b(impossible choice|decision|dilemma|struggle)\b",
        "story",
        0.6,
        "Character conflict",
    ),
]

# T022: Language detection decision table
LANGUAGE_RULES = [
    # Rule format: (pattern, language, confidence, why)
    (
        r"\b(the|and|of|to|a|in|is|it|you|that|he|was|for|on|are|as|with|his|they|i|at|be|this|have|from|or|one|had|by|word|but|not|what|all|were|we|when|your|can|said|there|each|which|do|how|their|if|will|up|other|about|out|many|then|them|these|so|some|her|would|make|like|into|time|has|two|more|go|no|way|could|my|than|first|been|call|who|oil|sit|now|find|long|down|day|did|get|come|made|may|part)\b",
        "en",
        0.9,
        "English stopwords",
    ),
    (
        r"\b(le|la|les|de|des|du|et|un|une|je|tu|il|elle|nous|vous|ils|elles|ce|qui|que|ne|pas|pour|avec|sur|par|dans|sans|sous|entre|chez|depuis|pendant|avant|après|contre|vers|jusqu|selon|malgré|parmi|envers|hormis|outre|moyennant)\b",
        "fr",
        0.9,
        "French stopwords",
    ),
    (
        r"\b(der|die|das|und|ist|in|den|von|zu|mit|auf|für|an|als|nach|bei|aus|um|über|durch|gegen|ohne|unter|zwischen|während|wegen|trotz|statt|außer|seit|bis)\b",
        "de",
        0.9,
        "German stopwords",
    ),
    (
        r"\b(el|la|los|las|de|del|y|un|una|es|en|que|no|se|por|con|para|su|al|lo|le|da|su|pero|más|como|ya|muy|sin|sobre|me|te|le|nos|os|les)\b",
        "es",
        0.9,
        "Spanish stopwords",
    ),
    (r"[一-龯]", "zh", 0.8, "Chinese characters"),
    (r"[ひらがなカタカナ]", "ja", 0.8, "Japanese characters"),
    (r"[א-ת]", "he", 0.8, "Hebrew characters"),
    (r"[ا-ي]", "ar", 0.8, "Arabic characters"),
]

# T023: Outline template patterns
OUTLINE_TEMPLATES = {
    ("article", "how-to"): [
        {
            "title": "Overview",
            "level": 1,
            "summary": "Introduction to the process and objectives.",
        },
        {
            "title": "Preparation",
            "level": 1,
            "summary": "Required materials, tools, and preliminary steps.",
        },
        {
            "title": "Step-by-Step Instructions",
            "level": 1,
            "summary": "Detailed implementation steps.",
        },
        {
            "title": "Tips and Best Practices",
            "level": 1,
            "summary": "Expert advice and common pitfalls to avoid.",
        },
        {"title": "Conclusion", "level": 1, "summary": "Summary and next steps."},
    ],
    ("article", "analysis"): [
        {
            "title": "Background",
            "level": 1,
            "summary": "Context and foundation for the analysis.",
        },
        {
            "title": "Methodology",
            "level": 1,
            "summary": "Approach and analytical framework used.",
        },
        {
            "title": "Findings",
            "level": 1,
            "summary": "Key discoveries and data analysis.",
        },
        {
            "title": "Implications",
            "level": 1,
            "summary": "Significance and broader impact.",
        },
        {
            "title": "Conclusion",
            "level": 1,
            "summary": "Summary of insights and recommendations.",
        },
    ],
    ("article", "default"): [
        {
            "title": "Introduction",
            "level": 1,
            "summary": "Overview and context setting.",
        },
        {
            "title": "Main Content",
            "level": 1,
            "summary": "Core information and details.",
        },
        {"title": "Conclusion", "level": 1, "summary": "Summary and final thoughts."},
    ],
    ("story", "default"): [
        {
            "title": "Setup",
            "level": 1,
            "summary": "Character introduction and world building.",
        },
        {
            "title": "Rising Action",
            "level": 1,
            "summary": "Conflict development and tension building.",
        },
        {
            "title": "Climax",
            "level": 1,
            "summary": "Peak tension and crucial turning point.",
        },
        {
            "title": "Resolution",
            "level": 1,
            "summary": "Conflict resolution and character development conclusion.",
        },
    ],
}

# ============================================================================
# CORE BUSINESS LOGIC
# ============================================================================


def setup_logging(log_level: str) -> logging.Logger:
    """Configure structured JSONL logging to STDERR (Constitutional Article XVIII)."""
    logger = logging.getLogger("article_outline_generator")
    logger.setLevel(getattr(logging, log_level.upper()))

    # STDERR handler for machine logs
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    return logger


def log_event(logger: logging.Logger, event: str, **kwargs: Any) -> None:
    """Log structured JSONL event (Constitutional Article XVIII)."""
    log_data = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "agent": "article_outline_generator",
        "version": "1.0.0",
        **kwargs,
    }
    logger.info(json.dumps(log_data))


def generate_trace_id() -> str:
    """Generate unique trace ID for request tracking."""
    return str(uuid.uuid4())


def generate_hash(content: str) -> str:
    """Generate SHA256 hash for content."""
    return hashlib.sha256(content.encode()).hexdigest()


def classify_content_type(content: str, hint: str | None = None) -> dict[str, Any]:
    """
    Classify content type using decision tables (Constitutional Article III).

    2. Apply decision rules in first-match precedence order
    3. Return classification with confidence score
    """
    if hint and hint in ["article", "story"]:
        return {"content_type": hint, "confidence": 1.0, "why": "User-provided hint"}

    content_lower = content.lower()

    # Apply rules in order (first match wins unless mode is score_best)
    for pattern, content_type, confidence, why in CONTENT_TYPE_RULES:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return {"content_type": content_type, "confidence": confidence, "why": why}

    # Default fallback (Constitutional requirement: deterministic response)
    return {
        "content_type": "article",
        "confidence": 0.5,
        "why": "Default classification",
    }


def detect_language(content: str, hint: str | None = None) -> dict[str, Any]:
    """
    Detect content language using pattern matching.

    4. Apply language detection rules
    5. Return language code with confidence
    """
    if hint:
        return {"language": hint, "confidence": 1.0, "why": "User-provided hint"}

    content_lower = content.lower()

    # Apply language rules
    for pattern, language, confidence, why in LANGUAGE_RULES:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return {"language": language, "confidence": confidence, "why": why}

    # Default to English
    return {"language": "en", "confidence": 0.5, "why": "Default language"}


def generate_section_id(title: str, used_ids: set[str]) -> str:
    """
    Generate stable section ID/slug from title.

    6. Convert title to slug format
    7. Handle collision detection with numeric suffixes
    """
    # Basic slug conversion
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", title.lower())
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")

    # Handle collisions
    original_slug = slug
    counter = 1
    while slug in used_ids:
        slug = f"{original_slug}-{counter}"
        counter += 1

    used_ids.add(slug)
    return slug


def estimate_word_count(
    section_level: int, content_type: str, key_points_count: int
) -> int:
    """
    Estimate word count for section based on various factors.

    8. Apply base word count by section type
    9. Adjust for complexity and depth
    """
    # Base word counts by level and type
    base_counts = {
        ("article", 1): 400,  # Top-level article sections
        ("article", 2): 250,
        ("article", 3): 150,
        ("story", 1): 600,  # Story sections typically longer
        ("story", 2): 350,
        ("story", 3): 200,
    }

    base = base_counts.get((content_type, section_level), 200)

    # Adjust for key points (more points = more content)
    if key_points_count > 0:
        base += key_points_count * 30

    # Ensure reasonable bounds
    return max(50, min(base, 1500))


def extract_key_topics(content: str) -> list[str]:
    """
    Extract key topics from content for outline generation.

    10. Parse content for major topics and themes
    11. Return prioritized list of topics
    """
    # Simple keyword extraction (could be enhanced)
    # Remove common words and extract meaningful terms
    words = re.findall(r"\b\w{4,}\b", content.lower())

    # Common stop words to exclude
    stop_words = {
        "this",
        "that",
        "with",
        "have",
        "will",
        "from",
        "they",
        "been",
        "were",
        "said",
        "each",
        "which",
        "their",
        "time",
        "about",
        "would",
        "there",
        "could",
        "other",
        "more",
        "very",
        "what",
        "know",
        "just",
        "first",
        "into",
        "over",
        "think",
        "also",
        "your",
        "work",
        "life",
    }

    # Filter and count
    word_freq: dict[str, int] = {}
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Return top topics
    sorted_topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, freq in sorted_topics[:10] if freq > 1]


def generate_outline_template(
    content_type: str, content: str, target_depth: int
) -> list[dict[str, Any]]:
    """
    Generate outline template based on content type and analysis.

    12. Select appropriate template pattern
    13. Customize based on content analysis
    """
    content_lower = content.lower()

    # Determine subtype for articles
    subtype = "default"
    if content_type == "article":
        if re.search(r"\b(how to|guide|tutorial|step)\b", content_lower):
            subtype = "how-to"
        elif re.search(r"\b(analysis|review|study|research)\b", content_lower):
            subtype = "analysis"

    # Get base template
    template_key = (content_type, subtype)
    template = OUTLINE_TEMPLATES.get(
        template_key, OUTLINE_TEMPLATES[(content_type, "default")]
    )

    # Extract key topics for customization
    topics = extract_key_topics(content)

    # Customize template with content-specific sections
    customized_template = []
    used_ids: set[str] = set()

    for i, section_template in enumerate(template):
        section = section_template.copy()

        # Generate section ID
        section["id"] = generate_section_id(str(section["title"]), used_ids)

        # Add key points based on topics (for middle sections)
        if i > 0 and i < len(template) - 1 and topics:
            # Add relevant topics as key points
            relevant_topics = topics[:3] if len(topics) >= 3 else topics
            section["key_points"] = [f"Explore {topic}" for topic in relevant_topics]

        customized_template.append(section)

    # Add depth by creating subsections if target_depth > 1
    if target_depth > 1 and len(customized_template) > 1:
        # Add subsections to main content sections (skip intro/conclusion)
        for section in customized_template[1:-1]:
            if len(topics) > 3:
                # Create subsections from remaining topics
                subsection_topics = topics[3:6]
                section["subsections"] = [
                    {
                        "title": topic.title(),
                        "level": 2,
                        "id": generate_section_id(topic, used_ids),
                        "summary": f"Detailed exploration of {topic}.",
                    }
                    for topic in subsection_topics
                ]

    return customized_template


def enhance_with_llm(
    content: str, outline: list[dict[str, Any]], config: Config
) -> list[dict[str, Any]]:
    """
    Enhance outline with LLM if enabled and needed (Constitutional Article X).

    14. Check if LLM enhancement is needed (low confidence cases)
    15. Make typed LLM call with strict budget enforcement
    """
    if not config.model.enabled:
        return outline  # STRICT mode - no LLM calls

    # Only use LLM for enhancement in very limited cases
    # This is a fallback mechanism, not primary generation

    # For now, return outline as-is (constitutional compliance)
    # Real LLM integration would go here with PydanticAI
    return outline


def process_content(
    content: str,
    target_depth: int = 3,
    content_type_hint: str | None = None,
    language_hint: str | None = None,
    include_word_counts: bool = True,
    interim: bool = False,
    timeout_ms: int | None = None,
    classification_method: str = "auto",
    config: Config | None = None,
) -> dict[str, Any]:
    """
    Main content processing function.

    16. Orchestrate the complete outline generation process
    17. Return Agent Envelope with results or errors
    """
    if config is None:
        config = DEFAULT_CONFIG

    logger = setup_logging(config.agent.log_level)
    trace_id = generate_trace_id()
    start_time = datetime.now(timezone.utc)

    log_event(logger, "agent_run", trace_id=trace_id, strict=config.agent.strict)

    try:
        # 1. Create and validate input model
        input_model = InputModel(
            content=content,
            target_depth=target_depth,
            content_type_hint=content_type_hint,  # type: ignore[arg-type]
            language_hint=language_hint,
            include_word_counts=include_word_counts,
            interim=interim,
            timeout_ms=timeout_ms,
            classification_method=classification_method,  # type: ignore[arg-type]
        )

        # 2. Classify content type with enhanced logic
        classification = classify_content_type(content, content_type_hint)
        log_event(
            logger,
            "decision_eval",
            rule_id="content_type",
            matched=True,
            why=classification["why"],
        )

        # Track LLM usage for cost calculation
        total_llm_calls = 0
        total_tokens_in = 0
        total_tokens_out = 0

        # 2a. Enhance classification with LLM if needed
        if (
            classification_method != "rules_only"
            and classification["confidence"] < 0.8
            and config.model.enabled
        ):

            log_event(
                logger,
                "model_call",
                provider=config.model.provider,
                enabled=config.model.enabled,
                reason="low_confidence_classification",
            )

            # Use LLM to enhance classification
            enhanced = enhance_classification_with_llm(
                content, classification, config, logger, trace_id
            )

            # Update classification with enhanced results
            classification.update(enhanced)
            total_llm_calls += enhanced.get("llm_calls_used", 0)
            total_tokens_in += enhanced.get("tokens_in", 0)
            total_tokens_out += enhanced.get("tokens_out", 0)

        # 3. Detect language
        language_detection = detect_language(content, language_hint)
        log_event(
            logger,
            "decision_eval",
            rule_id="language",
            matched=True,
            why=language_detection["why"],
        )

        # 4. Generate outline template
        outline_template = generate_outline_template(
            classification["content_type"], content, target_depth
        )

        # 5. Convert to Section objects
        sections = []

        for section_data in outline_template:
            # Estimate word count if requested
            word_count = None
            if include_word_counts:
                word_count = estimate_word_count(
                    section_data.get("level", 1),
                    classification["content_type"],
                    len(section_data.get("key_points", [])),
                )

            # Create section
            section = Section(
                title=section_data["title"],
                id=section_data.get("id"),
                level=section_data.get("level", 1),
                summary=section_data.get("summary"),
                key_points=section_data.get("key_points", []),
                word_count_estimate=word_count,
                subsections=[
                    Section(
                        title=sub["title"],
                        id=sub.get("id"),
                        level=sub.get("level", 2),
                        summary=sub.get("summary"),
                        word_count_estimate=(
                            estimate_word_count(2, classification["content_type"], 0)
                            if include_word_counts
                            else None
                        ),
                    )
                    for sub in section_data.get("subsections", [])
                ],
            )
            sections.append(section)

        # 6. Handle interim classification response if requested
        current_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        if interim and current_time_ms < (timeout_ms or 5000):
            # For interim responses, provide classification results early
            interim_metadata = OutlineMetadata(
                content_type=classification["content_type"],
                detected_language=language_detection["language"],
                depth=target_depth,
                sections_count=0,  # Not yet calculated
                generated_at=start_time,
                notes=f"Interim classification: {classification['confidence']:.2f}",
                classification_confidence=classification["confidence"],
                classification_method=classification.get(
                    "classification_method", "rule_based"
                ),
                classification_reasoning=classification.get(
                    "why", "Rule-based classification"
                ),
                key_indicators=classification.get("key_indicators", []),
                llm_calls_used=total_llm_calls,
                processing_time_ms=current_time_ms,
                interim_available=True,
            )

            # Return interim response with classification only
            interim_output = InterimOutputModel(meta=interim_metadata, outline=[])

            cost_model = CostModel(
                tokens_in=total_tokens_in,
                tokens_out=total_tokens_out,
                usd=(
                    calculate_cost(
                        config.model.provider,
                        config.model.name,
                        total_tokens_in,
                        total_tokens_out,
                    )
                    if total_llm_calls > 0
                    else 0.0
                ),
                llm_calls=total_llm_calls,
            )

            interim_envelope_meta = EnvelopeMeta(
                agent="article_outline_generator",
                version="1.0.0",
                trace_id=trace_id,
                ts=start_time,
                brand_token=config.agent.brand_token,
                hash=generate_hash(content),
                cost=cost_model,
            )

            interim_envelope = AgentEnvelope(
                meta=interim_envelope_meta,
                input=input_model,
                output=interim_output,
                error=None,
            )

            log_event(
                logger,
                "agent_run",
                trace_id=trace_id,
                ms=current_time_ms,
                outcome="interim",
                classification_confidence=classification["confidence"],
            )

            return interim_envelope.model_dump()

        # 6a. Calculate processing time
        processing_time_ms = int(
            (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        )

        # 7. Create enhanced metadata with classification details
        metadata = OutlineMetadata(
            content_type=classification["content_type"],
            detected_language=language_detection["language"],
            depth=target_depth,
            sections_count=len(sections),
            generated_at=start_time,
            notes=f"Generated with confidence: {classification['confidence']:.2f}",
            classification_confidence=classification["confidence"],
            classification_method=classification.get(
                "classification_method", "rule_based"
            ),
            classification_reasoning=classification.get(
                "why", "Rule-based classification"
            ),
            key_indicators=classification.get("key_indicators", []),
            llm_calls_used=total_llm_calls,
            processing_time_ms=processing_time_ms,
            interim_available=interim,
        )

        # 8. Create output model
        output = OutputModel(meta=metadata, outline=sections)

        # 9. Create envelope with proper cost tracking
        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

        # Calculate USD cost for LLM usage
        usd_cost = 0.0
        if total_llm_calls > 0:
            usd_cost = calculate_cost(
                config.model.provider,
                config.model.name,
                total_tokens_in,
                total_tokens_out,
            )

        cost_model = CostModel(
            tokens_in=total_tokens_in,
            tokens_out=total_tokens_out,
            usd=usd_cost,
            llm_calls=total_llm_calls,
        )

        envelope_meta = EnvelopeMeta(
            agent="article_outline_generator",
            version="1.0.0",
            trace_id=trace_id,
            ts=start_time,
            brand_token=config.agent.brand_token,
            hash=generate_hash(content),
            cost=cost_model,
        )

        envelope = AgentEnvelope(
            meta=envelope_meta, input=input_model, output=output, error=None
        )

        log_event(
            logger,
            "agent_run",
            trace_id=trace_id,
            ms=int(execution_time * 1000),
            outcome="ok",
            sections_count=len(sections),
        )

        return envelope.model_dump()

    except Exception as e:
        # Error handling with structured response
        error = ErrorModel(
            code="PROCESSING_ERROR", message=str(e), details={"trace_id": trace_id}
        )

        cost_model = CostModel(tokens_in=0, tokens_out=0, usd=0.0, llm_calls=0)

        envelope_meta = EnvelopeMeta(
            agent="article_outline_generator",
            version="1.0.0",
            trace_id=trace_id,
            ts=start_time,
            brand_token=config.agent.brand_token,
            hash=generate_hash(content) if content else "error",
            cost=cost_model,
        )

        envelope = AgentEnvelope(
            meta=envelope_meta,
            input=InputModel(content=content or "error"),
            output=None,
            error=error,
        )

        log_event(logger, "agent_run", trace_id=trace_id, outcome="error", error=str(e))

        return envelope.model_dump()


# ============================================================================
# CLI INTERFACE (Constitutional Article XX)
# ============================================================================


def normalize_markdown_input(content: str) -> InputModel:
    """
    Normalize markdown input to InputModel (Constitutional Article XIX).

    18. Parse markdown content deterministically
    19. Extract any embedded configuration
    """
    # Simple markdown normalization
    # In a full implementation, this would parse headers, extract metadata, etc.

    return InputModel(content=content.strip())


def load_config(config_path: str | None = None) -> Config:
    """Load configuration with hierarchical precedence."""
    config = DEFAULT_CONFIG

    # TODO: Load from config file if provided
    # TODO: Override with environment variables
    # TODO: Apply CLI flag overrides

    return config


def selfcheck(config: Config) -> bool:
    """
    Validate agent configuration and dependencies.

    20. Check environment variables, dependencies, schemas
    21. Return health status
    """
    import os

    success = True

    try:
        # Check Pydantic models can be instantiated
        InputModel(content="Test content")
        Section(title="Test")
        print("✅ All models validate correctly")

        # Check enhanced models (Feature 012)
        InterimOutputModel(
            meta=OutlineMetadata(
                content_type="article",
                detected_language="en",
                depth=3,
                sections_count=0,
                generated_at=datetime.now(timezone.utc),
            )
        )
        print("✅ Enhanced models validate correctly")

        # Check schema generation works
        InputModel.model_json_schema()
        OutputModel.model_json_schema()
        InterimOutputModel.model_json_schema()
        AgentEnvelope.model_json_schema()
        print("✅ Schema generation works")

        # Check configuration
        print("✅ Configuration loaded successfully")
        print(f"   - Agent: article_outline_generator v1.0.0")
        print(f"   - Strict mode: {config.agent.strict}")
        print(f"   - Log level: {config.agent.log_level}")

        # Check LLM configuration (Feature 012)
        if config.model.enabled:
            print("⚠️ LLM mode enabled:")
            print(f"   - Provider: {config.model.provider}")
            print(f"   - Model: {config.model.name}")

            # Check for API keys
            api_key_var = f"{config.model.provider.upper()}_API_KEY"
            if os.environ.get(api_key_var):
                print(f"   ✅ {api_key_var} environment variable set")
            else:
                print(f"   ⚠️ {api_key_var} environment variable not set")
                if config.agent.strict:
                    print("   ✅ STRICT mode enabled - LLM will not be used")
                else:
                    print("   ❌ LLM calls will fail without API key")
                    success = False

            # Try PydanticAI import
            try:
                import pydantic_ai  # noqa: F401

                print("   ✅ PydanticAI library available")
            except ImportError:
                print("   ⚠️ PydanticAI not installed - LLM features unavailable")
                if not config.agent.strict:
                    success = False
        else:
            print("✅ STRICT mode - no LLM dependencies required")

        return success

    except Exception as e:
        print(f"❌ Selfcheck failed: {e}")
        return False


def print_schemas() -> None:
    """Print current JSON schemas with validation examples."""
    schemas = {
        "input_schema": InputModel.model_json_schema(),
        "output_schema": OutputModel.model_json_schema(),
        "interim_output_schema": InterimOutputModel.model_json_schema(),
        "envelope_schema": AgentEnvelope.model_json_schema(),
        "error_schema": ErrorModel.model_json_schema(),
    }

    # Add metadata
    schemas["_metadata"] = {
        "agent": "article_outline_generator",
        "version": "1.0.0",
        "feature": "012-enhanced-classification",
        "compatibility": "backward-compatible",
        "schemas_generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Print formatted JSON
    print(json.dumps(schemas, indent=2, default=str))


def main(input_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Main entry point for the agent.

    22. Handle CLI parsing and input normalization
    23. Delegate to process_content and return results
    """
    parser = argparse.ArgumentParser(description="Article Outline Generator")
    parser.add_argument(
        "command",
        choices=["run", "selfcheck", "print-schemas", "dry-run"],
        default="run",
        nargs="?",
    )
    parser.add_argument(
        "--input-type", choices=["markdown", "json"], default="markdown"
    )
    parser.add_argument("--target-depth", type=int, default=3, choices=range(1, 7))
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--strict", action="store_true", help="Disable LLM fallback")
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARN", "ERROR"], default="INFO"
    )
    # Enhanced CLI flags (Feature 012)
    parser.add_argument(
        "--interim", action="store_true", help="Request interim classification response"
    )
    parser.add_argument(
        "--classification-method",
        choices=["auto", "rules_only", "llm_preferred"],
        default="auto",
        help="Classification method preference",
    )
    parser.add_argument(
        "--timeout-ms", type=int, help="Timeout for interim responses (100-30000ms)"
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    if args.strict:
        config.agent.strict = True
        config.model.enabled = False
    config.agent.log_level = args.log_level

    # Handle special commands
    if args.command == "selfcheck":
        success = selfcheck(config)
        sys.exit(0 if success else 1)

    if args.command == "print-schemas":
        print_schemas()
        sys.exit(0)

    # Handle input
    if input_data:
        # Called programmatically
        content = input_data.get("content", "")
        target_depth = input_data.get("target_depth", 3)
        content_type_hint = input_data.get("content_type_hint")
        language_hint = input_data.get("language_hint")
        include_word_counts = input_data.get("include_word_counts", True)
        interim = input_data.get("interim", False)
        timeout_ms = input_data.get("timeout_ms")
        classification_method = input_data.get("classification_method", "auto")
    else:
        # Read from stdin
        input_text = sys.stdin.read().strip()

        if args.input_type == "json":
            try:
                input_json = json.loads(input_text)
                content = input_json.get("content", "")
                target_depth = input_json.get("target_depth", args.target_depth)
                content_type_hint = input_json.get("content_type_hint")
                language_hint = input_json.get("language_hint")
                include_word_counts = input_json.get("include_word_counts", True)
                # CLI flags override JSON values
                interim = args.interim or input_json.get("interim", False)
                timeout_ms = args.timeout_ms or input_json.get("timeout_ms")
                classification_method = (
                    args.classification_method
                    if args.classification_method != "auto"
                    else input_json.get("classification_method", "auto")
                )
            except json.JSONDecodeError as e:
                error_result = {
                    "error": {
                        "code": "INVALID_JSON",
                        "message": f"Invalid JSON input: {e}",
                    }
                }
                print(json.dumps(error_result))
                sys.exit(1)
        else:
            # Markdown input
            content = input_text
            target_depth = args.target_depth
            content_type_hint = None
            language_hint = None
            include_word_counts = True
            interim = args.interim
            timeout_ms = args.timeout_ms
            classification_method = args.classification_method

    # Process content
    if args.command == "dry-run":
        # Just validate input without processing
        try:
            input_model = InputModel(
                content=content,
                target_depth=target_depth,
                content_type_hint=content_type_hint,
                language_hint=language_hint,
                include_word_counts=include_word_counts,
                interim=interim,
                timeout_ms=timeout_ms,
                classification_method=classification_method,
            )
            result = {"status": "valid", "input": input_model.model_dump()}
        except Exception as e:
            result = {"status": "invalid", "error": str(e)}
    else:
        # Full processing
        result = process_content(
            content=content,
            target_depth=target_depth,
            content_type_hint=content_type_hint,
            language_hint=language_hint,
            include_word_counts=include_word_counts,
            interim=interim,
            timeout_ms=timeout_ms,
            classification_method=classification_method,
            config=config,
        )

    # Output results
    output_json = json.dumps(result, indent=2, default=str)

    if args.output:
        Path(args.output).write_text(output_json)
    else:
        print(output_json)

    return result


if __name__ == "__main__":
    main()
