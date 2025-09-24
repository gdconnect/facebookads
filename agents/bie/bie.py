#!/usr/bin/env python3
"""
Business Idea Evaluator (BIE) - Single-file Python CLI tool

PURPOSE: Transform unstructured business ideas written in Markdown into structured,
evaluated, and actionable insights using multi-pass LLM evaluation.

USAGE:
    python bie.py evaluate idea.md                    # Basic evaluation
    python bie.py evaluate idea.md --output json     # JSON output
    python bie.py evaluate idea.md --output markdown # Enhanced markdown
    python bie.py compare idea1.md idea2.md idea3.md # Compare multiple ideas
    python bie.py validate idea.md                   # Quick validation only
    python bie.py selfcheck                          # System validation
    python bie.py print-schemas                      # Export JSON schemas

ACCEPTED INPUT CONTENT TYPES:
- text/markdown: Business idea descriptions in markdown format

EXAMPLE ENVELOPE OUTPUT:
{
  "meta": {
    "agent": "business_idea_evaluator",
    "version": "1.0.0",
    "trace_id": "uuid-string",
    "ts": "2024-01-15T10:30:00Z",
    "brand_token": "agency",
    "hash": "sha256-hash",
    "cost": {"tokens_in": 2500, "tokens_out": 1500, "usd": 0.12}
  },
  "input": {...},
  "output": {...},
  "error": null
}

DECLARED BUDGETS:
- Runtime: <4 minutes end-to-end evaluation
- Tokens: ~30K tokens per evaluation (input + output)
- Cost: <$3.00 per evaluation at GPT-5 pricing assumptions
- Memory: <50MB process footprint
- Timeout: 180 seconds per LLM call, up to 3 attempts per evaluation

DEPENDENCY PINS:
- pydantic>=2.0.0 (schema validation and JSON generation)
- pydantic-ai>=0.0.1 (LLM integration with structured extraction)
- python>=3.10 (modern type hints)
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from pydantic_ai import Agent
from pydantic_ai.models import Model

# =============================================================================
# CONFIG SECTION (Lines 20-120)
# =============================================================================


class ConfigModel(BaseModel):
    """Configuration settings with environment binding"""

    model_config = ConfigDict()

    # Model Settings (Constitutional Article X - enabled by default for enhanced parsing)
    model_enabled: bool = Field(default=True, description="Enable LLM model calls")
    model_provider: Literal["openai", "anthropic", "azure", "gemini"] = "openai"
    model_name: str = Field(default="gpt-5", description="LLM model identifier")
    model_temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    model_max_tokens: int = Field(default=32000, ge=100, le=40000)
    model_timeout_seconds: int = Field(default=180, ge=30, le=600)

    # Performance Budgets (Constitutional Article XII)
    max_evaluation_time_seconds: int = Field(default=240, ge=60, le=600)
    max_cost_usd: float = Field(default=3.0, ge=0.1, le=10.0)
    max_retries: int = Field(default=2, ge=0, le=5)

    # Scoring Weights
    scalability_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "marginal_cost": 0.30,
            "automation": 0.25,
            "network_effects": 0.20,
            "geographic_reach": 0.15,
            "platform_potential": 0.10,
        }
    )

    # Output Settings
    default_output_format: Literal["json", "markdown", "both"] = "json"
    include_reasoning: bool = True
    verbose_logging: bool = False


# =============================================================================
# PYDANTIC MODELS (Constitutional Article II)
# =============================================================================


class MetaModel(BaseModel):
    """Metadata for all agent responses"""

    agent: str = "business_idea_evaluator"
    version: str = "1.0.0"
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    brand_token: str = "agency"
    hash: str = Field(default="", description="SHA256 hash of input content")
    cost: dict[str, int | float] = Field(
        default_factory=lambda: {"tokens_in": 0, "tokens_out": 0, "usd": 0.0}
    )
    prompt_id: str | None = None
    prompt_hash: str | None = None


class RawIdea(BaseModel):
    """Initial business idea extraction from markdown"""

    name: str = Field(..., min_length=1, max_length=100)
    problem: str = Field(..., min_length=10, max_length=1000)
    solution: str = Field(..., min_length=10, max_length=1000)
    target_customer: str | None = Field(None, max_length=500)
    monetization: str | None = Field(None, max_length=500)
    technical_approach: str | None = Field(None, max_length=500)
    inspiration: str | None = Field(None, max_length=500)
    extraction_metadata: Optional["ExtractionMetadata"] = Field(
        None, description="Metadata about extraction process"
    )


# ================================================================================================
# FLEXIBLE EXTRACTION MODELS
# ================================================================================================


class FlexibleExtractionConfig(BaseModel):
    """Configuration for flexible markdown parsing behavior"""

    fuzzy_threshold: float = Field(
        0.8, ge=0.0, le=1.0, description="Similarity threshold for fuzzy matching"
    )
    confidence_threshold: float = Field(
        0.6, ge=0.0, le=1.0, description="Minimum confidence to avoid LLM fallback"
    )
    max_section_depth: int = Field(
        3, ge=1, le=6, description="Maximum heading depth to consider"
    )
    max_document_lines: int = Field(8000, ge=1, description="Maximum lines to process")
    fallback_enabled: bool = Field(
        False, description="Whether to use LLM fallback for low confidence"
    )
    section_mappings: dict[str, list[str]] = Field(
        default_factory=lambda: {
            "problem": [
                "problem",
                "challenge",
                "pain point",
                "issue",
                "identifying the problem",
                "problem statement",
                "the challenge we face",
            ],
            "solution": [
                "solution",
                "approach",
                "proposed solution",
                "our solution",
                "how we solve it",
                "our approach",
                "the solution",
            ],
            "target_customer": [
                "target",
                "customer",
                "audience",
                "users",
                "who we serve",
                "target market",
                "target customer",
                "target users",
            ],
            "monetization": [
                "revenue",
                "monetization",
                "business model",
                "how we make money",
                "pricing",
                "revenue strategy",
                "revenue model",
            ],
            "technical_approach": [
                "technical",
                "implementation",
                "technology",
                "how it works",
                "architecture",
                "technical approach",
            ],
            "inspiration": [
                "similar",
                "competitors",
                "inspiration",
                "alternatives",
                "market examples",
                "similar companies",
            ],
        },
        description="Maps field names to possible section headers",
    )


class ExtractionStrategy(str, Enum):
    """Strategy used for content extraction"""

    EXACT_MATCH = "EXACT_MATCH"
    FUZZY_MATCH = "FUZZY_MATCH"
    HIERARCHICAL = "HIERARCHICAL"
    LLM_FALLBACK = "LLM_FALLBACK"
    HYBRID = "HYBRID"


class ExtractionWarning(BaseModel):
    """Non-fatal issues during extraction"""

    field: str = Field(..., description="Field name related to warning")
    issue: str = Field(..., min_length=1, description="Description of the issue")
    suggestion: str = Field(..., min_length=1, description="Actionable recommendation")
    section_found: str | None = Field(
        None, description="Section that caused the warning"
    )


class ExtractionError(BaseModel):
    """Fatal errors preventing successful extraction"""

    field: str = Field(..., description="Field name related to error")
    issue: str = Field(..., min_length=1, description="Description of the error")
    suggestion: str = Field(..., min_length=1, description="How to fix the issue")
    severity: Literal["error", "critical"] = Field(
        ..., description="Error severity level"
    )


class DocumentStats(BaseModel):
    """Statistics about the processed markdown document"""

    total_lines: int = Field(..., ge=0, description="Total lines in document")
    section_count: int = Field(..., ge=0, description="Number of sections found")
    heading_levels: list[int] = Field(..., description="Heading levels present (1-6)")
    content_length: int = Field(..., ge=0, description="Total character count")
    language_detected: str | None = Field(None, description="Detected language code")
    structure_complexity: Literal["simple", "moderate", "complex"] = Field(
        ..., description="Document complexity"
    )


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process"""

    source_sections: dict[str, str] = Field(
        ..., description="Original section headers that provided each field"
    )
    extraction_method: dict[str, ExtractionStrategy] = Field(
        ..., description="Method used for each field"
    )
    confidence_breakdown: dict[str, float] = Field(
        ..., description="Detailed confidence scoring"
    )
    processing_notes: list[str] = Field(
        default_factory=list, description="Internal processing notes"
    )
    document_stats: DocumentStats = Field(
        ..., description="Statistics about the source document"
    )


class ExtractionResult(BaseModel):
    """Detailed result of markdown parsing attempt"""

    raw_idea: RawIdea | None = Field(
        None, description="Successfully extracted business idea"
    )
    strategy_used: ExtractionStrategy = Field(
        ..., description="Primary strategy that succeeded"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Overall confidence in extraction"
    )
    field_confidences: dict[str, float] = Field(
        ..., description="Per-field confidence scores"
    )
    section_matches: dict[str, str] = Field(
        ..., description="Mapping of found sections to fields"
    )
    warnings: list[ExtractionWarning] = Field(
        default_factory=list, description="Non-fatal issues found"
    )
    errors: list[ExtractionError] = Field(
        default_factory=list, description="Fatal errors preventing extraction"
    )
    processing_time_ms: int = Field(..., ge=0, description="Time taken for extraction")
    llm_tokens_used: int = Field(
        default=0, ge=0, description="Tokens consumed by LLM calls"
    )


# ================================================================================================


class BusinessModel(BaseModel):
    """Refined business mechanics analysis"""

    value_creation: str = Field(..., min_length=20, max_length=500)
    value_capture: str = Field(..., min_length=20, max_length=500)
    unit_economics: str = Field(..., min_length=20, max_length=500)
    growth_mechanism: str = Field(..., min_length=20, max_length=500)
    competitive_moat: str = Field(..., min_length=20, max_length=500)
    minimum_viable_scope: str = Field(..., min_length=20, max_length=500)


class ScalabilityFactors(BaseModel):
    """Growth potential and constraints analysis"""

    marginal_cost_per_customer: str = Field(..., min_length=20, max_length=300)
    geographic_constraints: str = Field(..., min_length=20, max_length=300)
    automation_potential: int = Field(..., ge=0, le=100)
    network_effects: str = Field(..., min_length=20, max_length=300)
    platform_potential: bool
    data_compound_value: str = Field(..., min_length=20, max_length=300)


class RiskAssessment(BaseModel):
    """Reality check and risk identification"""

    startup_costs: dict[str, float] = Field(..., min_length=1)
    time_to_revenue: str = Field(..., min_length=20, max_length=500)
    key_dependencies: list[str] = Field(..., min_length=1, max_length=10)
    biggest_risk: str = Field(..., min_length=20, max_length=500)
    boring_version: str = Field(..., min_length=20, max_length=500)
    why_not_already_dominated: str = Field(..., min_length=20, max_length=500)

    @field_validator("key_dependencies")
    def validate_dependencies(cls, v: list[str]) -> list[str]:
        for dep in v:
            if not (5 <= len(dep) <= 100):
                raise ValueError(f"Dependency must be 5-100 chars: {dep}")
        return v


class ComputedScores(BaseModel):
    """Calculated evaluation metrics"""

    scalability_score: int = Field(..., ge=0, le=100)
    complexity_score: int = Field(..., ge=0, le=100)
    risk_score: int = Field(..., ge=0, le=100)
    overall_grade: str = Field(..., pattern="^[A-F]$")


class ActionableInsights(BaseModel):
    """Specific recommendations and actions"""

    critical_questions: list[str] = Field(..., min_length=3, max_length=7)
    quick_wins: list[str] = Field(..., min_length=3, max_length=7)
    red_flags: list[str] = Field(..., min_length=3, max_length=7)
    next_steps: list[str] = Field(..., min_length=3, max_length=7)
    similar_successes: list[str] = Field(..., min_length=3, max_length=7)
    recommended_mvp: str = Field(..., min_length=50, max_length=300)


class EvaluationMetadata(BaseModel):
    """Evaluation execution context"""

    evaluation_date: datetime = Field(default_factory=datetime.utcnow)
    model_used: str
    processing_time: float
    token_usage: dict[str, int] = Field(default_factory=dict)
    confidence_scores: dict[str, float] = Field(default_factory=dict)


class EvaluatedIdea(BaseModel):
    """Complete evaluated business idea"""

    raw_idea: RawIdea
    business_model: BusinessModel
    scalability: ScalabilityFactors
    risks: RiskAssessment
    scores: ComputedScores
    insights: ActionableInsights
    metadata: EvaluationMetadata


class LLMAnalysisResponse(BaseModel):
    """Structured payload expected from LLM analysis"""

    business_model: BusinessModel
    scalability: ScalabilityFactors
    risks: RiskAssessment
    scores: ComputedScores
    insights: ActionableInsights
    confidence_scores: dict[str, float] = Field(default_factory=dict)


class ComparisonResult(BaseModel):
    """Result of comparing multiple business ideas"""

    ideas: list[EvaluatedIdea]
    ranking: list[dict[str, Any]] = Field(default_factory=list)
    recommendation: str = ""
    comparison_summary: str = ""


class ErrorModel(BaseModel):
    """Error response model"""

    type: Literal[
        "validation_error", "llm_error", "file_error", "config_error", "timeout_error"
    ]
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    recoverable: bool = False


class Envelope(BaseModel):
    """Standard response envelope (Constitutional Article II)"""

    meta: MetaModel
    input: RawIdea | list[RawIdea] | None = None
    output: EvaluatedIdea | list[EvaluatedIdea] | dict[str, Any] | None = None
    error: ErrorModel | None = None


# =============================================================================
# BUSINESS LOGIC & DECISION TABLES (Constitutional Article III)
# =============================================================================


class ScoringRules:
    """Decision tables for scoring calculations"""

    @staticmethod
    def calculate_scalability_score(
        factors: ScalabilityFactors, weights: dict[str, float]
    ) -> int:
        """Calculate scalability score using weighted factors"""
        # 1. Marginal cost scoring (0 = high cost, 100 = zero cost)
        marginal_score = (
            100
            if "zero" in factors.marginal_cost_per_customer.lower()
            else 80
            if "low" in factors.marginal_cost_per_customer.lower()
            else 60
            if "medium" in factors.marginal_cost_per_customer.lower()
            else 30
        )

        # 2. Automation potential (direct percentage)
        automation_score = factors.automation_potential

        # 3. Network effects (0 = none, 100 = viral)
        network_score = (
            100
            if "viral" in factors.network_effects.lower()
            else 80
            if "strong" in factors.network_effects.lower()
            else 50
            if "moderate" in factors.network_effects.lower()
            else 20
        )

        # 4. Geographic reach (local=20, national=60, global=100)
        geo_score = (
            100
            if "global" in factors.geographic_constraints.lower()
            else 80
            if "international" in factors.geographic_constraints.lower()
            else 60
            if "national" in factors.geographic_constraints.lower()
            else 20
        )

        # 5. Platform potential (binary 0 or 100)
        platform_score = 100 if factors.platform_potential else 0

        # Calculate weighted sum
        score = (
            marginal_score * weights.get("marginal_cost", 0.30)
            + automation_score * weights.get("automation", 0.25)
            + network_score * weights.get("network_effects", 0.20)
            + geo_score * weights.get("geographic_reach", 0.15)
            + platform_score * weights.get("platform_potential", 0.10)
        )

        return int(min(100, max(0, score)))

    @staticmethod
    def calculate_complexity_score(raw_idea: RawIdea, risks: RiskAssessment) -> int:
        """Calculate complexity score (lower is better)"""
        # Count dependencies
        dep_count = len(risks.key_dependencies)
        dep_score = min(100, dep_count * 10)

        # Estimate time to market
        time_score = (
            100
            if "year" in risks.time_to_revenue.lower()
            else 70
            if "month" in risks.time_to_revenue.lower()
            else 30
        )

        # Count required features (estimate from solution length)
        feature_score = min(100, len(raw_idea.solution.split()) // 10 * 20)

        # Regulatory burden (simple heuristic)
        reg_score = (
            100
            if any(
                word in raw_idea.solution.lower()
                for word in ["financial", "healthcare", "legal"]
            )
            else 30
            if any(
                word in raw_idea.solution.lower()
                for word in ["data", "privacy", "security"]
            )
            else 0
        )

        # Weighted average (higher = more complex)
        score = (
            dep_score * 0.30
            + time_score * 0.30
            + feature_score * 0.20
            + reg_score * 0.20
        )

        return int(min(100, max(0, score)))

    @staticmethod
    def calculate_risk_score(risks: RiskAssessment) -> int:
        """Calculate risk score (lower is better)"""
        # Market risk (competition and demand)
        market_score = (
            80
            if "competitive" in risks.biggest_risk.lower()
            else 50
            if "market" in risks.biggest_risk.lower()
            else 30
        )

        # Technical risk (complexity and dependencies)
        tech_score = min(100, len(risks.key_dependencies) * 15)

        # Financial risk (startup costs)
        total_costs = sum(risks.startup_costs.values())
        financial_score = (
            100
            if total_costs > 100000
            else 70
            if total_costs > 50000
            else 40
            if total_costs > 10000
            else 20
        )

        # Execution risk (time and commitment)
        exec_score = (
            80
            if "team" in risks.biggest_risk.lower()
            else 60
            if "time" in risks.biggest_risk.lower()
            else 40
        )

        # Equal weighting
        score = (market_score + tech_score + financial_score + exec_score) / 4
        return int(min(100, max(0, score)))

    @staticmethod
    def calculate_overall_grade(scores: ComputedScores) -> str:
        """Calculate overall grade based on score thresholds"""
        if (
            scores.scalability_score > 80
            and scores.complexity_score < 30
            and scores.risk_score < 30
        ):
            return "A"
        elif (
            scores.scalability_score > 60
            and scores.complexity_score < 50
            and scores.risk_score < 50
        ):
            return "B"
        elif (
            scores.scalability_score > 40
            and scores.complexity_score < 70
            and scores.risk_score < 70
        ):
            return "C"
        elif (
            scores.scalability_score > 20
            and scores.complexity_score < 90
            and scores.risk_score < 90
        ):
            return "D"
        else:
            return "F"


class BlindspotDetector:
    """Detect common agency development blindspots"""

    BLINDSPOT_RULES = [
        {
            "pattern": r"build.*better",
            "flag": '"We\'ll build it better" syndrome',
            "advice": "Focus on distribution and customer acquisition, not just quality",
        },
        {
            "pattern": r"feature.*feature.*feature",
            "flag": '"Features equal value" fallacy',
            "advice": "One feature done perfectly beats many mediocre ones",
        },
        {
            "pattern": r"we.*different",
            "flag": '"We\'re different from clients" delusion',
            "advice": "You need marketing and sales strategy too",
        },
        {
            "pattern": r"technical.*complex",
            "flag": '"Code is the hard part" bias',
            "advice": "Getting customers is harder than writing code",
        },
        {
            "pattern": r"monetization.*later|figure.*out.*pricing",
            "flag": '"We\'ll figure out monetization later"',
            "advice": "Charge from day one with clear pricing strategy",
        },
        {
            "pattern": r"perfect|polish|ready",
            "flag": '"Perfect before launch" trap',
            "advice": "Ship in 30 days or scope down",
        },
    ]

    @classmethod
    def detect_blindspots(cls, raw_idea: RawIdea) -> list[str]:
        """Detect blindspots in business idea"""
        blindspots = []
        combined_text = f"{raw_idea.problem} {raw_idea.solution} {raw_idea.technical_approach or ''}"

        for rule in cls.BLINDSPOT_RULES:
            if re.search(rule["pattern"], combined_text, re.IGNORECASE):
                blindspots.append(f"{rule['flag']}: {rule['advice']}")

        # Check for vague monetization
        if not raw_idea.monetization or len(raw_idea.monetization) < 20:
            blindspots.append(
                '"We\'ll figure out monetization later": Charge from day one with clear pricing strategy'
            )

        # Check for unrealistic timeline
        if raw_idea.technical_approach and len(raw_idea.technical_approach) > 200:
            blindspots.append(
                '"Perfect before launch" trap: Ship in 30 days or scope down'
            )

        # Check for timeline mentions
        timeline_text = f"{raw_idea.technical_approach or ''} {raw_idea.solution}"
        if any(
            phrase in timeline_text.lower()
            for phrase in ["6 months", "year", "years", "months"]
        ):
            blindspots.append(
                '"Perfect before launch" trap: Ship in 30 days or scope down'
            )

        return blindspots


# =============================================================================
# MAIN BUSINESS LOGIC
# =============================================================================


class BusinessIdeaEvaluator:
    """Main evaluator class"""

    def __init__(self, config: ConfigModel):
        self.config = config
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup structured JSONL logging to STDERR (Constitutional Article XVIII)"""
        logger = logging.getLogger("bie")
        logger.setLevel(logging.DEBUG if self.config.verbose_logging else logging.INFO)

        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Add STDERR handler with JSON formatting
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

        return logger

    def _log_event(self, event: str, **kwargs: Any) -> None:
        """Log structured JSONL event"""
        log_entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "lvl": "INFO",
            "event": event,
            "agent": "business_idea_evaluator",
            "version": "1.0.0",
            "trace_id": kwargs.pop("trace_id", str(uuid.uuid4())),
            **kwargs,
        }
        self.logger.info(json.dumps(log_entry))

    # ================================================================================================
    # FLEXIBLE EXTRACTION METHODS
    # ================================================================================================

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _fuzzy_match_section(
        self, header: str, targets: list[str], threshold: float = 0.8
    ) -> tuple[str | None, float]:
        """Match section header to known patterns using similarity scoring"""
        header_lower = header.lower().strip()
        best_match = None
        best_score = 0.0

        for target in targets:
            target_lower = target.lower().strip()
            max_len = max(len(header_lower), len(target_lower))
            if max_len == 0:
                continue

            distance = self._levenshtein_distance(header_lower, target_lower)
            similarity = 1.0 - (distance / max_len)

            if similarity >= threshold and similarity > best_score:
                best_match = target
                best_score = similarity

        return best_match, best_score

    def _extract_sections(self, content: str, max_depth: int = 3) -> dict[str, str]:
        """Extract sections from markdown content with hierarchical support"""
        sections = {}
        lines = content.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            # Check for headers (# to ###)
            header_match = re.match(r"^(#{1," + str(max_depth) + r"})\s+(.+)$", line)
            if header_match:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = header_match.group(2).strip()
                current_content = []
            elif current_section:
                # Add content to current section
                current_content.append(line)

        # Don't forget the last section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _calculate_confidence(
        self, field_matches: dict[str, tuple[str, float]], required_fields: set[str]
    ) -> float:
        """Calculate overall confidence score based on field matches"""
        if not field_matches:
            return 0.0

        total_score = 0.0
        total_weight = 0.0

        for field_name, (_, score) in field_matches.items():
            weight = 1.0 if field_name in required_fields else 0.5
            total_score += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        base_confidence = total_score / total_weight

        # Bonus for having all required fields
        required_found = sum(1 for field in required_fields if field in field_matches)
        completeness_bonus = (required_found / len(required_fields)) * 0.2

        return min(1.0, base_confidence + completeness_bonus)

    def _analyze_document_stats(
        self, content: str, sections: dict[str, str]
    ) -> DocumentStats:
        """Analyze document statistics and complexity"""
        lines = content.split("\n")
        heading_levels = []

        for line in lines:
            header_match = re.match(r"^(#{1,6})\s+", line)
            if header_match:
                heading_levels.append(len(header_match.group(1)))

        complexity = "simple"
        if len(sections) > 10 or len(heading_levels) > 15:
            complexity = "complex"
        elif len(sections) > 5 or len(heading_levels) > 8:
            complexity = "moderate"

        return DocumentStats(
            total_lines=len(lines),
            section_count=len(sections),
            heading_levels=sorted(set(heading_levels)),
            content_length=len(content),
            language_detected=None,  # Could add language detection later
            structure_complexity=complexity,
        )

    def parse_markdown_flexible(
        self, content: str, config: FlexibleExtractionConfig | None = None
    ) -> ExtractionResult:
        """Enhanced markdown parsing with flexible section matching and LLM fallback"""
        start_time = time.time()

        if config is None:
            config = FlexibleExtractionConfig()

        # 1. Extract title/name
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        name = title_match.group(1).strip() if title_match else "Untitled Idea"

        # 2. Extract sections
        sections = self._extract_sections(content, config.max_section_depth)

        # 3. Map sections to fields using flexible matching
        field_matches = {}
        section_matches = {}
        extraction_methods = {}

        required_fields = {"problem", "solution"}

        for field_name, possible_headers in config.section_mappings.items():
            best_match = None
            best_score = 0.0
            matched_section = None
            strategy = ExtractionStrategy.EXACT_MATCH

            # Try exact matches first
            for section_header, section_content in sections.items():
                if section_header.lower() in [h.lower() for h in possible_headers]:
                    if len(section_content.strip()) >= (
                        10 if field_name in required_fields else 1
                    ):
                        best_match = section_content.strip()
                        best_score = 1.0
                        matched_section = section_header
                        strategy = ExtractionStrategy.EXACT_MATCH
                        break

            # If no exact match, try fuzzy matching
            if not best_match:
                for section_header, section_content in sections.items():
                    match, score = self._fuzzy_match_section(
                        section_header, possible_headers, config.fuzzy_threshold
                    )
                    if match and score > best_score:
                        if len(section_content.strip()) >= (
                            10 if field_name in required_fields else 1
                        ):
                            best_match = section_content.strip()
                            best_score = score
                            matched_section = section_header
                            strategy = ExtractionStrategy.FUZZY_MATCH

            if best_match:
                # Enforce field length limits
                max_length = 1000 if field_name in required_fields else 500
                if len(best_match) > max_length:
                    best_match = best_match[:max_length]

                field_matches[field_name] = (best_match, best_score)
                section_matches[matched_section] = field_name
                extraction_methods[field_name] = strategy

        # 4. Calculate confidence and determine strategy
        confidence = self._calculate_confidence(field_matches, required_fields)
        overall_strategy = (
            ExtractionStrategy.HYBRID
            if len(set(extraction_methods.values())) > 1
            else list(extraction_methods.values())[0]
            if extraction_methods
            else ExtractionStrategy.EXACT_MATCH
        )

        # 5. Check for errors and warnings
        errors = []
        warnings = []

        for required_field in required_fields:
            if required_field not in field_matches:
                errors.append(
                    ExtractionError(
                        field=required_field,
                        issue=f"Required field '{required_field}' not found",
                        suggestion=f"Add a section titled '{config.section_mappings[required_field][0].title()}' describing the {required_field}",
                        severity="error",
                    )
                )

        # 6. Create RawIdea if we have required fields
        raw_idea = None
        if len(errors) == 0:  # No critical errors
            extraction_metadata = ExtractionMetadata(
                source_sections=section_matches,
                extraction_method=extraction_methods,
                confidence_breakdown={
                    field: score for field, (_, score) in field_matches.items()
                },
                processing_notes=[
                    f"Processed {len(sections)} sections using {overall_strategy.value}"
                ],
                document_stats=self._analyze_document_stats(content, sections),
            )

            raw_idea = RawIdea(
                name=name[:100],
                problem=field_matches.get("problem", ("", 0.0))[0] or "",
                solution=field_matches.get("solution", ("", 0.0))[0] or "",
                target_customer=field_matches.get("target_customer", (None, 0.0))[0],
                monetization=field_matches.get("monetization", (None, 0.0))[0],
                technical_approach=field_matches.get("technical_approach", (None, 0.0))[
                    0
                ],
                inspiration=field_matches.get("inspiration", (None, 0.0))[0],
                extraction_metadata=extraction_metadata,
            )

        processing_time = int((time.time() - start_time) * 1000)

        return ExtractionResult(
            raw_idea=raw_idea,
            strategy_used=overall_strategy,
            confidence_score=confidence,
            field_confidences={
                field: score for field, (_, score) in field_matches.items()
            },
            section_matches=section_matches,
            warnings=warnings,
            errors=errors,
            processing_time_ms=processing_time,
            llm_tokens_used=0,  # No LLM used yet
        )

    # ================================================================================================

    def parse_markdown(self, content: str) -> RawIdea:
        """Parse markdown content into RawIdea model"""
        # 1. Extract title/name
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        name = title_match.group(1).strip() if title_match else "Untitled Idea"

        # 2. Extract sections
        sections = {}
        current_section = None
        current_content: list[str] = []

        for line in content.split("\n"):
            if line.startswith("##"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line.replace("#", "").strip().lower()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Don't forget the last section
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        # 3. Map sections to RawIdea fields
        return RawIdea(
            name=name[:100],  # Enforce length limit
            problem=sections.get("problem", sections.get("problem statement", ""))[
                :1000
            ],
            solution=sections.get("solution", sections.get("proposed solution", ""))[
                :1000
            ],
            target_customer=sections.get(
                "target customer", sections.get("customer", "")
            )[:500]
            or None,
            monetization=sections.get(
                "revenue model", sections.get("monetization", "")
            )[:500]
            or None,
            technical_approach=sections.get(
                "technical approach", sections.get("implementation", "")
            )[:500]
            or None,
            inspiration=sections.get(
                "similar companies", sections.get("inspiration", "")
            )[:500]
            or None,
        )

    def evaluate_idea(
        self,
        file_path: Path,
        output_format: str = "json",
        use_enhanced: bool = True,
        fuzzy_threshold: float = 0.8,
        confidence_threshold: float = 0.6,
        max_document_lines: int | None = None,
    ) -> Envelope:
        """Main evaluation pipeline"""
        trace_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Log start of evaluation
            self._log_event("agent_run", trace_id=trace_id, input_file=str(file_path))

            # 1. Read and parse input
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            content = file_path.read_text(encoding="utf-8")
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # 2. Parse markdown to RawIdea (using enhanced parsing if requested)
            if use_enhanced:
                config_kwargs: dict[str, Any] = {
                    "fuzzy_threshold": fuzzy_threshold,
                    "confidence_threshold": confidence_threshold,
                    "fallback_enabled": self.config.model_enabled,
                }
                if max_document_lines is not None:
                    config_kwargs["max_document_lines"] = max_document_lines

                config = FlexibleExtractionConfig(**config_kwargs)
                extraction_result = self.parse_markdown_flexible(content, config)

                if extraction_result.raw_idea is None:
                    # If enhanced parsing fails, return error envelope
                    error_msg = "; ".join(
                        [error.issue for error in extraction_result.errors]
                    )
                    raise ValueError(f"Enhanced parsing failed: {error_msg}")

                raw_idea = extraction_result.raw_idea
                self._log_event(
                    "extraction_result",
                    strategy=extraction_result.strategy_used.value,
                    confidence=extraction_result.confidence_score,
                    processing_time_ms=extraction_result.processing_time_ms,
                )
            else:
                raw_idea = self.parse_markdown(content)

            # 3. Create deterministic analysis (no LLM by default per constitution)
            if not self.config.model_enabled:
                evaluated, usage_stats, usd_cost = self._deterministic_evaluation(
                    raw_idea
                )
            else:
                evaluated, usage_stats, usd_cost = self._llm_evaluation(
                    raw_idea, trace_id
                )

            # 4. Calculate processing metrics
            processing_time = time.time() - start_time

            # 5. Create response envelope
            meta = MetaModel(
                trace_id=trace_id,
                hash=content_hash,
                cost={
                    "tokens_in": usage_stats.get("prompt_tokens", 0),
                    "tokens_out": usage_stats.get("completion_tokens", 0),
                    "usd": usd_cost,
                },
            )

            envelope = Envelope(meta=meta, input=raw_idea, output=evaluated)

            self._log_event(
                "agent_run_complete",
                trace_id=trace_id,
                processing_time=processing_time,
                outcome="ok",
                tokens_in=usage_stats.get("prompt_tokens", 0),
                tokens_out=usage_stats.get("completion_tokens", 0),
                usd=usd_cost,
            )

            return envelope

        except Exception as e:
            error = ErrorModel(
                type="validation_error" if isinstance(e, ValueError) else "file_error",
                message=str(e),
                details={"trace_id": trace_id},
                recoverable=True,
            )

            return Envelope(meta=MetaModel(trace_id=trace_id), error=error)

    def _deterministic_evaluation(
        self, raw_idea: RawIdea
    ) -> tuple[EvaluatedIdea, dict[str, int], float]:
        """Fallback deterministic evaluation without LLM calls"""

        # Create deterministic business model analysis
        business_model = BusinessModel(
            value_creation=f"Creates value by solving: {raw_idea.problem[:100]}...",
            value_capture=raw_idea.monetization
            or "Revenue model not specified - needs clarification",
            unit_economics="Unit economics analysis requires more detailed financial information",
            growth_mechanism=f"Growth through {raw_idea.target_customer or 'target market'} adoption",
            competitive_moat="Competitive advantages require market analysis to determine",
            minimum_viable_scope=f"MVP focusing on core {raw_idea.solution[:100]}... functionality",
        )

        # Create scalability analysis
        scalability = ScalabilityFactors(
            marginal_cost_per_customer="Marginal cost analysis requires technical architecture details",
            geographic_constraints="Geographic reach depends on solution implementation approach",
            automation_potential=50,  # Conservative estimate
            network_effects="Network effects potential requires user interaction analysis",
            platform_potential=False,  # Conservative default
            data_compound_value="Data accumulation benefits require more detailed analysis",
        )

        # Create risk assessment
        risks = RiskAssessment(
            startup_costs={
                "development": 10000.0,
                "marketing": 5000.0,
            },  # Conservative estimates
            time_to_revenue="6-12 months estimated based on typical development cycles",
            key_dependencies=[
                "market validation",
                "technical implementation",
                "customer acquisition",
            ],
            biggest_risk="Market acceptance and customer acquisition challenges",
            boring_version=f"Simple version: {raw_idea.solution[:100]}... with basic features",
            why_not_already_dominated="Market gap analysis requires competitive research",
        )

        # Calculate scores
        scalability_score = ScoringRules.calculate_scalability_score(
            scalability, self.config.scalability_weights
        )
        complexity_score = ScoringRules.calculate_complexity_score(raw_idea, risks)
        risk_score = ScoringRules.calculate_risk_score(risks)

        scores = ComputedScores(
            scalability_score=scalability_score,
            complexity_score=complexity_score,
            risk_score=risk_score,
            overall_grade="C",  # Temporary value
        )

        # Calculate and update overall grade
        scores.overall_grade = ScoringRules.calculate_overall_grade(scores)

        # Generate insights
        blindspots = BlindspotDetector.detect_blindspots(raw_idea)
        insights = ActionableInsights(
            critical_questions=[
                "Who exactly is your target customer and how will you reach them?",
                "What is your specific competitive advantage over existing solutions?",
                "How will you validate market demand before building?",
            ],
            quick_wins=[
                "Conduct customer interviews to validate problem-solution fit",
                "Research direct competitors and their pricing strategies",
                "Create a simple landing page to test market interest",
            ],
            red_flags=self._ensure_min_red_flags(blindspots),
            next_steps=[
                "Define specific customer personas and their pain points",
                "Research and analyze direct and indirect competitors",
                "Create detailed financial projections and unit economics",
            ],
            similar_successes=[
                "Buffer (social media management - proven SaaS model)",
                "Canva (design tools - freemium to premium conversion)",
                "Slack (communication tools - viral growth through teams)",
            ],
            recommended_mvp=f"Build a simple {raw_idea.solution[:50]}... tool that solves the core problem for a specific customer segment within 30 days",
        )

        # Create metadata
        usage_info = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

        metadata = EvaluationMetadata(
            model_used="deterministic_fallback",
            processing_time=0.1,
            token_usage=usage_info,
            confidence_scores={"overall": 0.6},  # Lower confidence for deterministic
        )

        evaluated = EvaluatedIdea(
            raw_idea=raw_idea,
            business_model=business_model,
            scalability=scalability,
            risks=risks,
            scores=scores,
            insights=insights,
            metadata=metadata,
        )

        return evaluated, usage_info, 0.0

    def _resolve_model(self) -> Model:
        """Instantiate provider-specific PydanticAI model"""
        provider = self.config.model_provider

        if provider == "openai":
            from pydantic_ai.models.openai import OpenAIModel

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY environment variable must be set for OpenAI models"
                )
            return OpenAIModel(self.config.model_name, api_key=api_key)

        if provider == "anthropic":
            from pydantic_ai.models.anthropic import AnthropicModel

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY environment variable must be set for Anthropic models"
                )
            return AnthropicModel(self.config.model_name, api_key=api_key)

        if provider == "gemini":
            from pydantic_ai.models.gemini import GeminiModel

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY environment variable must be set for Gemini models"
                )
            return GeminiModel(self.config.model_name, api_key=api_key)

        raise RuntimeError(f"Model provider '{provider}' is not supported yet")

    def _create_llm_agent(self) -> Agent:
        """Create configured PydanticAI agent for idea evaluation"""
        model_settings = {
            "max_completion_tokens": self.config.model_max_tokens,
            "timeout": self.config.model_timeout_seconds,
        }

        temperature = self.config.model_temperature
        if temperature is not None:
            # GPT-5 currently ignores non-default temperatures; omit to avoid API errors.
            if not (
                self.config.model_provider == "openai"
                and self.config.model_name.startswith("gpt-5")
            ):
                model_settings["temperature"] = temperature
            else:
                logging.debug(
                    "Omitting temperature override for %s:%s because the model only supports the default",
                    self.config.model_provider,
                    self.config.model_name,
                )

        return Agent(
            model=self._resolve_model(),
            result_type=str,
            system_prompt=(
                "You are a senior startup analyst evaluating business ideas for venture studios. "
                "Respond with rigorous, actionable analysis. ALWAYS return strictly valid JSON without backticks."
            ),
            model_settings=model_settings,
            retries=self.config.max_retries,
        )

    def _build_llm_prompt(self, raw_idea: RawIdea) -> str:
        """Compose rich prompt for LLM evaluation"""
        idea_payload = raw_idea.model_dump(
            exclude_none=True,
            exclude={"extraction_metadata": {"processing_notes"}},
        )

        extraction_summary = {}
        if raw_idea.extraction_metadata:
            extraction_summary = {
                "source_sections": raw_idea.extraction_metadata.source_sections,
                "confidence_breakdown": raw_idea.extraction_metadata.confidence_breakdown,
                "document_stats": raw_idea.extraction_metadata.document_stats.model_dump(),
            }

        schema_outline = {
            "business_model": {
                "value_creation": "string (20-500 chars)",
                "value_capture": "string (20-500 chars)",
                "unit_economics": "string (20-500 chars)",
                "growth_mechanism": "string (20-500 chars)",
                "competitive_moat": "string (20-500 chars)",
                "minimum_viable_scope": "string (20-500 chars)",
            },
            "scalability": {
                "marginal_cost_per_customer": "string (20-300 chars)",
                "geographic_constraints": "string (20-300 chars)",
                "automation_potential": "int (0-100)",
                "network_effects": "string (20-300 chars)",
                "platform_potential": "boolean",
                "data_compound_value": "string (20-300 chars)",
            },
            "risks": {
                "startup_costs": "object with >=2 entries, numeric USD values",
                "time_to_revenue": "string (20-500 chars)",
                "key_dependencies": "list of 3-7 concise dependencies (5-100 chars each)",
                "biggest_risk": "string (20-500 chars)",
                "boring_version": "string (20-500 chars)",
                "why_not_already_dominated": "string (20-500 chars)",
            },
            "scores": {
                "scalability_score": "int 0-100",
                "complexity_score": "int 0-100",
                "risk_score": "int 0-100",
                "overall_grade": "A-F aligned with other scores",
            },
            "insights": {
                "critical_questions": "3-7 items, each 20-200 chars",
                "quick_wins": "3-7 items, each actionable",
                "red_flags": "3-7 items, hard truths and risks",
                "next_steps": "3-7 items, sequenced actions",
                "similar_successes": "3-7 signals citing comparable companies",
                "recommended_mvp": "string (50-300 chars) defining 30-day build",
            },
            "confidence_scores": "optional map of section->0.0-1.0 confidence",
        }

        guidance = (
            "Rules:\n"
            "- Ground every statement in the supplied idea details.\n"
            "- Use concrete numbers, channels, and examples where possible.\n"
            "- Respect min/max lengths; elaborate instead of being vague.\n"
            "- red_flags must include uncomfortable truths, not platitudes.\n"
            "- key_dependencies must be explicit assets, partners, or skills.\n"
            "- Scores must be integers; compute overall_grade consistent with the provided scores.\n"
            "- Output strictly valid JSON matching the schema outline with double quotes only."
        )

        prompt = (
            "Evaluate the following business idea and produce structured analysis.\n\n"
            f"Idea fields (JSON):\n{json.dumps(idea_payload, indent=2)}\n\n"
            f"Extraction summary:\n{json.dumps(extraction_summary, indent=2)}\n\n"
            f"Target JSON schema summary:\n{json.dumps(schema_outline, indent=2)}\n\n"
            f"{guidance}\n"
            "Return ONLY the JSON object, no commentary or markdown."
        )

        return prompt

    def _estimate_cost(self, usage_stats: dict[str, int]) -> float:
        """Best-effort USD cost estimate based on provider pricing (placeholder)"""
        # Pricing for GPT-5 is not yet finalized; return 0 and delegate cost tracking to upstream billing.
        if not usage_stats:
            return 0.0
        return 0.0

    def _llm_evaluation(
        self, raw_idea: RawIdea, trace_id: str
    ) -> tuple[EvaluatedIdea, dict[str, int], float]:
        """LLM-powered evaluation using configured model"""
        agent = self._create_llm_agent()
        base_prompt = self._build_llm_prompt(raw_idea)
        prompt_to_send = base_prompt
        usage_stats = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        attempts = max(1, self.config.max_retries + 1)
        last_error: Exception | None = None

        for attempt in range(attempts):
            prompt_hash = hashlib.sha256(prompt_to_send.encode()).hexdigest()

            try:
                self._log_event(
                    "model_call_start",
                    trace_id=trace_id,
                    attempt=attempt + 1,
                    model=f"{self.config.model_provider}:{self.config.model_name}",
                    prompt_hash=prompt_hash,
                )

                start = time.time()
                result = agent.run_sync(prompt_to_send)
                duration = time.time() - start

                usage = result.usage()
                usage_stats = {
                    "prompt_tokens": usage.request_tokens or 0,
                    "completion_tokens": usage.response_tokens or 0,
                    "total_tokens": usage.total_tokens
                    or ((usage.request_tokens or 0) + (usage.response_tokens or 0)),
                }

                self._log_event(
                    "model_call_complete",
                    trace_id=trace_id,
                    attempt=attempt + 1,
                    model=f"{self.config.model_provider}:{self.config.model_name}",
                    prompt_hash=prompt_hash,
                    tokens_in=usage_stats["prompt_tokens"],
                    tokens_out=usage_stats["completion_tokens"],
                    duration_ms=int(duration * 1000),
                )

                raw_payload = (
                    result.data
                    if isinstance(result.data, str)
                    else json.dumps(result.data)
                )
                parsed = json.loads(raw_payload)
                response = LLMAnalysisResponse.model_validate(parsed)

                scores = response.scores
                scores.overall_grade = ScoringRules.calculate_overall_grade(scores)

                blindspots = BlindspotDetector.detect_blindspots(raw_idea)
                combined_flags = response.insights.red_flags + [
                    flag
                    for flag in blindspots
                    if flag not in response.insights.red_flags
                ]

                insights = response.insights.model_copy(
                    update={
                        "critical_questions": self._trim_list(
                            response.insights.critical_questions
                        ),
                        "quick_wins": self._trim_list(response.insights.quick_wins),
                        "red_flags": self._ensure_min_red_flags(combined_flags),
                        "next_steps": self._trim_list(response.insights.next_steps),
                        "similar_successes": self._trim_list(
                            response.insights.similar_successes
                        ),
                    }
                )

                metadata = EvaluationMetadata(
                    model_used=f"{self.config.model_provider}:{self.config.model_name}",
                    processing_time=duration,
                    token_usage=usage_stats,
                    confidence_scores=response.confidence_scores or {},
                )

                evaluated = EvaluatedIdea(
                    raw_idea=raw_idea,
                    business_model=response.business_model,
                    scalability=response.scalability,
                    risks=response.risks,
                    scores=scores,
                    insights=insights,
                    metadata=metadata,
                )

                usd_cost = self._estimate_cost(usage_stats)

                return evaluated, usage_stats, usd_cost

            except (json.JSONDecodeError, ValidationError) as err:
                last_error = err
                self._log_event(
                    "model_call_retry",
                    trace_id=trace_id,
                    attempt=attempt + 1,
                    error=str(err),
                    reason="validation_error",
                )
                if attempt < attempts - 1:
                    prompt_to_send = (
                        base_prompt
                        + "\n\nREMINDER: Output STRICT JSON only with double quotes and no trailing text."
                    )
                    continue
                raise ValueError(
                    "LLM evaluation failed: response did not match expected schema"
                ) from err

            except Exception as err:
                last_error = err
                self._log_event(
                    "model_call_retry",
                    trace_id=trace_id,
                    attempt=attempt + 1,
                    error=str(err),
                    reason="llm_exception",
                )
                if attempt < attempts - 1:
                    time.sleep(1)
                    continue
                raise

        if last_error:
            raise last_error

        raise RuntimeError("LLM evaluation failed for unknown reasons")

    def generate_enhanced_markdown(self, evaluated: EvaluatedIdea) -> str:
        """Generate enhanced markdown output with emojis and formatting"""
        # Calculate overall score for title
        overall_score = int(
            (evaluated.scores.scalability_score * 0.4)
            + ((100 - evaluated.scores.complexity_score) * 0.3)
            + ((100 - evaluated.scores.risk_score) * 0.3)
        )

        # Visual indicators based on scores
        def get_indicator(score: int) -> str:
            if score >= 70:
                return "✅"
            elif score >= 40:
                return "⚠️"
            else:
                return "❌"

        markdown = f"""# {evaluated.raw_idea.name} - Grade: {evaluated.scores.overall_grade} ({overall_score}/100)

## 📊 Summary Scores
- **Scalability**: {evaluated.scores.scalability_score}/100 {get_indicator(evaluated.scores.scalability_score)}
- **Complexity**: {evaluated.scores.complexity_score}/100 {get_indicator(100 - evaluated.scores.complexity_score)} (lower is better)
- **Risk**: {evaluated.scores.risk_score}/100 {get_indicator(100 - evaluated.scores.risk_score)} (lower is better)

## 💡 Your Original Idea

### Problem
{evaluated.raw_idea.problem}

### Solution
{evaluated.raw_idea.solution}

### Target Customer
{evaluated.raw_idea.target_customer or "Not specified"}

### Revenue Model
{evaluated.raw_idea.monetization or "Not specified"}

### Technical Approach
{evaluated.raw_idea.technical_approach or "Not specified"}

### Inspiration
{evaluated.raw_idea.inspiration or "Not specified"}

## 🎯 Refined Business Model

**Value Creation**: {evaluated.business_model.value_creation}

**Value Capture**: {evaluated.business_model.value_capture}

**Unit Economics**: {evaluated.business_model.unit_economics}

**Growth Mechanism**: {evaluated.business_model.growth_mechanism}

**Competitive Moat**: {evaluated.business_model.competitive_moat}

**Minimum Viable Scope**: {evaluated.business_model.minimum_viable_scope}

## ❗ Critical Questions (Answer Before Proceeding)
"""
        for i, question in enumerate(evaluated.insights.critical_questions, 1):
            markdown += f"{i}. {question}\n"

        markdown += "\n## 🚨 Red Flags\n"
        for flag in evaluated.insights.red_flags:
            markdown += f"- ⚠️ {flag}\n"

        markdown += "\n## ✅ Quick Wins\n"
        for win in evaluated.insights.quick_wins:
            markdown += f"- [ ] {win}\n"

        markdown += (
            f"\n## 🚀 Recommended MVP (30 days)\n{evaluated.insights.recommended_mvp}\n"
        )

        # Find the first similar success
        similar_company = (
            evaluated.insights.similar_successes[0]
            if evaluated.insights.similar_successes
            else "No similar examples found"
        )
        markdown += f"\n## 📈 Similar Success: {similar_company.split('(')[0].strip()}\n"
        if "(" in similar_company:
            strategy = similar_company.split("(")[1].replace(")", "").strip()
            markdown += f"They proved this model by {strategy}\n"
        else:
            markdown += "Research similar companies to validate your model\n"

        markdown += "\n## 🔄 Next Iteration Prompts\n"
        for i, step in enumerate(evaluated.insights.next_steps[:3], 1):
            if "research" in step.lower():
                markdown += f"- **Research**: {step}\n"
            elif "simplify" in step.lower():
                markdown += f"- **Simplify**: {step}\n"
            else:
                markdown += f"- **Consider**: {step}\n"

        return markdown

    def _ensure_min_red_flags(self, blindspots: list[str]) -> list[str]:
        """Ensure at least 3 red flags are present, padding with defaults if needed"""
        default_flags = [
            "Vague target customer definition may lead to unfocused development",
            "Unclear revenue model creates uncertainty for business viability",
            "Limited competitive analysis increases market risk",
        ]

        # Use blindspots first, then pad with defaults
        red_flags = blindspots[:] if blindspots else []

        # Add defaults that aren't already present
        for flag in default_flags:
            if len(red_flags) >= 3:
                break
            if flag not in red_flags:
                red_flags.append(flag)

        return red_flags[:3]  # Ensure exactly 3 items

    def _trim_list(
        self, values: list[str], max_items: int = 7, min_items: int = 3
    ) -> list[str]:
        """Deduplicate while preserving order and enforce list length bounds"""
        trimmed: list[str] = []
        for value in values:
            if value and value not in trimmed:
                trimmed.append(value)

        if len(trimmed) < min_items:
            trimmed = [v for v in values if v][: max(min_items, len(values))]

        return trimmed[:max_items]

    def compare_ideas(self, idea_files: list[Path]) -> ComparisonResult:
        """Compare multiple business ideas and provide ranking with analysis"""
        if len(idea_files) < 2 or len(idea_files) > 10:
            raise ValueError("Can only compare 2-10 business ideas")

        evaluated_ideas: list[EvaluatedIdea] = []

        # Evaluate each idea independently
        for idea_file in idea_files:
            try:
                envelope = self.evaluate_idea(idea_file)
                if envelope.error or not envelope.output:
                    self.logger.error(
                        f"Failed to evaluate {idea_file.name}: {envelope.error}"
                    )
                    continue
                if isinstance(envelope.output, EvaluatedIdea):
                    evaluated_ideas.append(envelope.output)
            except Exception as e:
                self.logger.error(f"Error evaluating {idea_file.name}: {str(e)}")
                continue

        if len(evaluated_ideas) < 2:
            raise ValueError(
                "Need at least 2 successfully evaluated ideas for comparison"
            )

        # Sort by overall score (descending)
        sorted_ideas = sorted(
            evaluated_ideas,
            key=lambda x: x.scores.scalability_score
            - x.scores.complexity_score
            - x.scores.risk_score,
            reverse=True,
        )

        # Create ranking with relative analysis
        ranking = []
        for i, idea in enumerate(sorted_ideas):
            rank_entry = {
                "rank": i + 1,
                "name": idea.raw_idea.name,
                "grade": idea.scores.overall_grade,
                "total_score": idea.scores.scalability_score
                - idea.scores.complexity_score
                - idea.scores.risk_score,
                "scalability": idea.scores.scalability_score,
                "complexity": idea.scores.complexity_score,
                "risk": idea.scores.risk_score,
                "strengths": self._identify_relative_strengths(idea, sorted_ideas),
                "weaknesses": self._identify_relative_weaknesses(idea, sorted_ideas),
            }
            ranking.append(rank_entry)

        # Generate recommendation
        top_idea = sorted_ideas[0]
        recommendation = self._generate_comparison_recommendation(
            top_idea, sorted_ideas
        )

        # Generate comparison summary
        comparison_summary = self._generate_comparison_summary(sorted_ideas, ranking)

        return ComparisonResult(
            ideas=evaluated_ideas,
            ranking=ranking,
            recommendation=recommendation,
            comparison_summary=comparison_summary,
        )

    def _identify_relative_strengths(
        self, idea: EvaluatedIdea, all_ideas: list[EvaluatedIdea]
    ) -> list[str]:
        """Identify this idea's strengths relative to others"""
        strengths = []

        # Calculate averages
        avg_scalability = sum(i.scores.scalability_score for i in all_ideas) / len(
            all_ideas
        )
        avg_complexity = sum(i.scores.complexity_score for i in all_ideas) / len(
            all_ideas
        )
        avg_risk = sum(i.scores.risk_score for i in all_ideas) / len(all_ideas)

        # Compare against averages
        if idea.scores.scalability_score > avg_scalability + 10:
            strengths.append("High scalability potential")
        if idea.scores.complexity_score < avg_complexity - 10:
            strengths.append("Lower implementation complexity")
        if idea.scores.risk_score < avg_risk - 10:
            strengths.append("Lower business risk")

        # Domain-specific strengths
        if idea.raw_idea.monetization and (
            "SaaS" in idea.raw_idea.monetization
            or "subscription" in idea.raw_idea.monetization.lower()
        ):
            strengths.append("Recurring revenue model")
        if "automation" in idea.raw_idea.solution.lower():
            strengths.append("Automation-driven efficiency")
        if (
            "API" in idea.raw_idea.solution
            or "platform" in idea.raw_idea.solution.lower()
        ):
            strengths.append("Platform scalability")

        return strengths[:3]  # Limit to top 3 strengths

    def _identify_relative_weaknesses(
        self, idea: EvaluatedIdea, all_ideas: list[EvaluatedIdea]
    ) -> list[str]:
        """Identify this idea's weaknesses relative to others"""
        weaknesses = []

        # Calculate averages
        avg_scalability = sum(i.scores.scalability_score for i in all_ideas) / len(
            all_ideas
        )
        avg_complexity = sum(i.scores.complexity_score for i in all_ideas) / len(
            all_ideas
        )
        avg_risk = sum(i.scores.risk_score for i in all_ideas) / len(all_ideas)

        # Compare against averages
        if idea.scores.scalability_score < avg_scalability - 10:
            weaknesses.append("Limited scalability potential")
        if idea.scores.complexity_score > avg_complexity + 10:
            weaknesses.append("Higher implementation complexity")
        if idea.scores.risk_score > avg_risk + 10:
            weaknesses.append("Higher business risk")

        # Check for red flags
        if len(idea.insights.red_flags) > 2:
            weaknesses.append("Multiple risk factors identified")
        if "unclear" in idea.business_model.value_capture.lower():
            weaknesses.append("Unclear monetization strategy")
        if idea.scores.overall_grade in ["D", "F"]:
            weaknesses.append("Below-average overall score")

        return weaknesses[:3]  # Limit to top 3 weaknesses

    def _generate_comparison_recommendation(
        self, top_idea: EvaluatedIdea, all_ideas: list[EvaluatedIdea]
    ) -> str:
        """Generate recommendation for which idea to pursue"""
        grade_distribution: dict[str, int] = {}
        for idea in all_ideas:
            grade = idea.scores.overall_grade
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

        if top_idea.scores.overall_grade in ["A", "B"]:
            confidence = "strongly recommend"
        elif top_idea.scores.overall_grade == "C":
            confidence = "cautiously recommend"
        else:
            confidence = "suggest reconsidering"

        return (
            f"Based on the analysis, I {confidence} pursuing '{top_idea.raw_idea.name}' "
            f"(Grade: {top_idea.scores.overall_grade}). This idea scored highest on overall potential "
            f"with {top_idea.scores.scalability_score}% scalability, {100-top_idea.scores.complexity_score}% "
            f"ease of implementation, and {100-top_idea.scores.risk_score}% risk mitigation."
        )

    def _generate_comparison_summary(
        self, sorted_ideas: list[EvaluatedIdea], ranking: list[dict[str, Any]]
    ) -> str:
        """Generate overall comparison summary"""
        total_ideas = len(sorted_ideas)
        grades = [idea.scores.overall_grade for idea in sorted_ideas]
        grade_counts = {
            grade: grades.count(grade) for grade in ["A", "B", "C", "D", "F"]
        }

        summary = f"Compared {total_ideas} business ideas. "

        if grade_counts["A"] > 0:
            summary += f"{grade_counts['A']} received grade A (excellent). "
        if grade_counts["B"] > 0:
            summary += f"{grade_counts['B']} received grade B (good). "
        if grade_counts["C"] > 0:
            summary += f"{grade_counts['C']} received grade C (average). "
        if grade_counts["D"] + grade_counts["F"] > 0:
            summary += f"{grade_counts['D'] + grade_counts['F']} need significant improvement. "

        # Identify patterns
        avg_scalability = sum(i.scores.scalability_score for i in sorted_ideas) / len(
            sorted_ideas
        )
        avg_complexity = sum(i.scores.complexity_score for i in sorted_ideas) / len(
            sorted_ideas
        )

        if avg_scalability > 70:
            summary += "Overall high scalability potential across ideas. "
        if avg_complexity > 70:
            summary += "Most ideas show high implementation complexity. "

        return summary.strip()


def main() -> None:
    """Main CLI entry point"""

    def save_enhanced_markdown(markdown: str, source_file: Path) -> None:
        """Persist enhanced markdown next to the source idea file"""
        output_path = source_file.with_name(f"enhanced_{source_file.name}")
        try:
            output_path.write_text(markdown, encoding="utf-8")
            print(f"Enhanced markdown saved to {output_path}", file=sys.stderr)
        except OSError as exc:
            print(
                f"Warning: could not save enhanced markdown to {output_path}: {exc}",
                file=sys.stderr,
            )

    parser = argparse.ArgumentParser(
        description="Business Idea Evaluator - Transform business ideas into structured insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a business idea")
    eval_parser.add_argument(
        "file", type=Path, help="Markdown file containing business idea"
    )
    eval_parser.add_argument(
        "--output", choices=["json", "markdown", "both"], default="json"
    )
    eval_parser.add_argument("--model", help="Override default LLM model")
    eval_parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    # Parsing mode options (enhanced is now default)
    eval_parser.add_argument(
        "--legacy", action="store_true", help="Use legacy rigid markdown parsing"
    )
    eval_parser.add_argument(
        "--fuzzy-threshold",
        type=float,
        default=0.8,
        help="Similarity threshold for fuzzy matching (0.0-1.0)",
    )
    eval_parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.6,
        help="Minimum confidence to avoid LLM fallback (0.0-1.0)",
    )
    eval_parser.add_argument(
        "--max-lines",
        type=int,
        help="Override maximum document lines considered during parsing",
    )

    # Compare command
    compare_parser = subparsers.add_parser(
        "compare", help="Compare multiple business ideas"
    )
    compare_parser.add_argument(
        "files", nargs="+", type=Path, help="Markdown files to compare"
    )
    compare_parser.add_argument(
        "--output", choices=["json", "markdown"], default="json"
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Quick validation only")
    validate_parser.add_argument("file", type=Path, help="Markdown file to validate")

    # Selfcheck command
    subparsers.add_parser("selfcheck", help="Validate system configuration")

    # Print schemas command
    subparsers.add_parser("print-schemas", help="Export JSON schemas")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Load configuration
    config = ConfigModel()
    if hasattr(args, "verbose") and args.verbose:
        config.verbose_logging = True
    if hasattr(args, "model") and args.model:
        config.model_name = args.model

    # Initialize evaluator
    evaluator = BusinessIdeaEvaluator(config)

    # Execute command
    if args.command == "evaluate":
        envelope = evaluator.evaluate_idea(
            args.file,
            args.output,
            use_enhanced=not args.legacy,
            fuzzy_threshold=args.fuzzy_threshold,
            confidence_threshold=args.confidence_threshold,
            max_document_lines=args.max_lines,
        )

        if args.output == "json":
            print(envelope.model_dump_json(indent=2))
        elif args.output == "markdown":
            if envelope.output and isinstance(envelope.output, EvaluatedIdea):
                enhanced_markdown = evaluator.generate_enhanced_markdown(
                    envelope.output
                )
                print(enhanced_markdown)
                save_enhanced_markdown(enhanced_markdown, args.file)
            else:
                print("Error generating markdown output")
                print(envelope.model_dump_json(indent=2))
        elif args.output == "both":
            # Print JSON first
            print("=== JSON OUTPUT ===")
            print(envelope.model_dump_json(indent=2))
            print("\n=== MARKDOWN OUTPUT ===")
            if envelope.output and isinstance(envelope.output, EvaluatedIdea):
                enhanced_markdown = evaluator.generate_enhanced_markdown(
                    envelope.output
                )
                print(enhanced_markdown)
                save_enhanced_markdown(enhanced_markdown, args.file)
            else:
                print("Error generating markdown output")

    elif args.command == "compare":
        try:
            result = evaluator.compare_ideas(args.files)
            if args.output == "json":
                print(result.model_dump_json(indent=2))
            elif args.output == "markdown":
                # Generate markdown comparison table
                markdown = "# Business Idea Comparison\n\n"
                markdown += f"## Summary\n{result.comparison_summary}\n\n"
                markdown += "## Ranking\n\n| Rank | Idea | Grade | Total Score | Scalability | Complexity | Risk |\n"
                markdown += "|------|------|-------|-------------|-------------|------------|------|\n"
                for item in result.ranking:
                    markdown += f"| {item['rank']} | {item['name']} | {item['grade']} | {item['total_score']:.1f} | {item['scalability']}% | {item['complexity']}% | {item['risk']}% |\n"
                markdown += f"\n## Recommendation\n{result.recommendation}\n"
                print(markdown)
        except Exception as e:
            print(f"Error comparing ideas: {str(e)}")
            return

    elif args.command == "validate":
        # Quick validation without full evaluation
        try:
            content = args.file.read_text(encoding="utf-8")
            raw_idea = evaluator.parse_markdown(content)
            print(json.dumps({"status": "valid", "idea_name": raw_idea.name}, indent=2))
        except Exception as e:
            print(json.dumps({"status": "invalid", "error": str(e)}, indent=2))

    elif args.command == "selfcheck":
        print(json.dumps({"status": "ok", "version": "1.0.0"}, indent=2))

    elif args.command == "print-schemas":
        schemas = {
            "RawIdea": RawIdea.model_json_schema(),
            "EvaluatedIdea": EvaluatedIdea.model_json_schema(),
            "ComparisonResult": ComparisonResult.model_json_schema(),
            "Envelope": Envelope.model_json_schema(),
        }
        print(json.dumps(schemas, indent=2))

    else:
        print(f"Command '{args.command}' not yet implemented")


if __name__ == "__main__":
    main()
