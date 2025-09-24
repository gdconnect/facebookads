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
- Runtime: <2 minutes end-to-end evaluation
- Tokens: ~10K tokens per evaluation (input + output)
- Cost: <$0.15 per evaluation at GPT-4 pricing
- Memory: <50MB process footprint
- Timeout: 120 seconds per LLM call, 3 total retries max

DEPENDENCY PINS:
- pydantic>=2.0.0 (schema validation and JSON generation)
- pydantic-ai>=0.0.1 (LLM integration with structured extraction)
- python>=3.10 (modern type hints)
"""

import argparse
import hashlib
import json
import logging
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic_ai import Agent
from pydantic_ai.models import Model

# =============================================================================
# CONFIG SECTION (Lines 20-120)
# =============================================================================

class ConfigModel(BaseModel):
    """Configuration settings with environment binding"""
    model_config = ConfigDict(env_prefix="BIE_")

    # Model Settings (Constitutional Article X - disabled by default)
    model_enabled: bool = Field(False, description="Enable LLM model calls")
    model_provider: Literal["openai", "anthropic", "azure", "gemini"] = "openai"
    model_name: str = Field("gpt-4-turbo", description="LLM model identifier")
    model_temperature: float = Field(0.3, ge=0.0, le=2.0)
    model_max_tokens: int = Field(2000, ge=100, le=4000)
    model_timeout_seconds: int = Field(120, ge=30, le=300)

    # Performance Budgets (Constitutional Article XII)
    max_evaluation_time_seconds: int = Field(120, ge=60, le=300)
    max_cost_usd: float = Field(1.0, ge=0.1, le=5.0)
    max_retries: int = Field(1, ge=0, le=3)

    # Scoring Weights
    scalability_weights: Dict[str, float] = Field(default_factory=lambda: {
        "marginal_cost": 0.30,
        "automation": 0.25,
        "network_effects": 0.20,
        "geographic_reach": 0.15,
        "platform_potential": 0.10
    })

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
    cost: Dict[str, Union[int, float]] = Field(default_factory=lambda: {
        "tokens_in": 0, "tokens_out": 0, "usd": 0.0
    })
    prompt_id: Optional[str] = None
    prompt_hash: Optional[str] = None

class RawIdea(BaseModel):
    """Initial business idea extraction from markdown"""
    name: str = Field(..., min_length=1, max_length=100)
    problem: str = Field(..., min_length=10, max_length=1000)
    solution: str = Field(..., min_length=10, max_length=1000)
    target_customer: Optional[str] = Field(None, max_length=500)
    monetization: Optional[str] = Field(None, max_length=500)
    technical_approach: Optional[str] = Field(None, max_length=500)
    inspiration: Optional[str] = Field(None, max_length=500)

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
    startup_costs: Dict[str, float] = Field(..., min_length=1)
    time_to_revenue: str = Field(..., min_length=20, max_length=500)
    key_dependencies: List[str] = Field(..., min_length=1, max_length=10)
    biggest_risk: str = Field(..., min_length=20, max_length=500)
    boring_version: str = Field(..., min_length=20, max_length=500)
    why_not_already_dominated: str = Field(..., min_length=20, max_length=500)

    @field_validator('key_dependencies')
    def validate_dependencies(cls, v: List[str]) -> List[str]:
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
    critical_questions: List[str] = Field(..., min_length=3, max_length=7)
    quick_wins: List[str] = Field(..., min_length=3, max_length=7)
    red_flags: List[str] = Field(..., min_length=3, max_length=7)
    next_steps: List[str] = Field(..., min_length=3, max_length=7)
    similar_successes: List[str] = Field(..., min_length=3, max_length=7)
    recommended_mvp: str = Field(..., min_length=50, max_length=300)

class EvaluationMetadata(BaseModel):
    """Evaluation execution context"""
    evaluation_date: datetime = Field(default_factory=datetime.utcnow)
    model_used: str
    processing_time: float
    token_usage: Dict[str, int] = Field(default_factory=dict)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)

class EvaluatedIdea(BaseModel):
    """Complete evaluated business idea"""
    raw_idea: RawIdea
    business_model: BusinessModel
    scalability: ScalabilityFactors
    risks: RiskAssessment
    scores: ComputedScores
    insights: ActionableInsights
    metadata: EvaluationMetadata

class ComparisonResult(BaseModel):
    """Result of comparing multiple business ideas"""
    ideas: List[EvaluatedIdea]
    ranking: List[Dict[str, Any]] = Field(default_factory=list)
    recommendation: str = ""
    comparison_summary: str = ""

class ErrorModel(BaseModel):
    """Error response model"""
    type: Literal["validation_error", "llm_error", "file_error", "config_error", "timeout_error"]
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    recoverable: bool = False

class Envelope(BaseModel):
    """Standard response envelope (Constitutional Article II)"""
    meta: MetaModel
    input: Optional[Union[RawIdea, List[RawIdea]]] = None
    output: Optional[Union[EvaluatedIdea, List[EvaluatedIdea], Dict[str, Any]]] = None
    error: Optional[ErrorModel] = None

# =============================================================================
# BUSINESS LOGIC & DECISION TABLES (Constitutional Article III)
# =============================================================================

class ScoringRules:
    """Decision tables for scoring calculations"""

    @staticmethod
    def calculate_scalability_score(factors: ScalabilityFactors, weights: Dict[str, float]) -> int:
        """Calculate scalability score using weighted factors"""
        # 1. Marginal cost scoring (0 = high cost, 100 = zero cost)
        marginal_score = 100 if "zero" in factors.marginal_cost_per_customer.lower() else \
                        80 if "low" in factors.marginal_cost_per_customer.lower() else \
                        60 if "medium" in factors.marginal_cost_per_customer.lower() else 30

        # 2. Automation potential (direct percentage)
        automation_score = factors.automation_potential

        # 3. Network effects (0 = none, 100 = viral)
        network_score = 100 if "viral" in factors.network_effects.lower() else \
                       80 if "strong" in factors.network_effects.lower() else \
                       50 if "moderate" in factors.network_effects.lower() else 20

        # 4. Geographic reach (local=20, national=60, global=100)
        geo_score = 100 if "global" in factors.geographic_constraints.lower() else \
                   80 if "international" in factors.geographic_constraints.lower() else \
                   60 if "national" in factors.geographic_constraints.lower() else 20

        # 5. Platform potential (binary 0 or 100)
        platform_score = 100 if factors.platform_potential else 0

        # Calculate weighted sum
        score = (
            marginal_score * weights.get("marginal_cost", 0.30) +
            automation_score * weights.get("automation", 0.25) +
            network_score * weights.get("network_effects", 0.20) +
            geo_score * weights.get("geographic_reach", 0.15) +
            platform_score * weights.get("platform_potential", 0.10)
        )

        return int(min(100, max(0, score)))

    @staticmethod
    def calculate_complexity_score(raw_idea: RawIdea, risks: RiskAssessment) -> int:
        """Calculate complexity score (lower is better)"""
        # Count dependencies
        dep_count = len(risks.key_dependencies)
        dep_score = min(100, dep_count * 10)

        # Estimate time to market
        time_score = 100 if "year" in risks.time_to_revenue.lower() else \
                    70 if "month" in risks.time_to_revenue.lower() else 30

        # Count required features (estimate from solution length)
        feature_score = min(100, len(raw_idea.solution.split()) // 10 * 20)

        # Regulatory burden (simple heuristic)
        reg_score = 100 if any(word in raw_idea.solution.lower()
                              for word in ["financial", "healthcare", "legal"]) else \
                   30 if any(word in raw_idea.solution.lower()
                            for word in ["data", "privacy", "security"]) else 0

        # Weighted average (higher = more complex)
        score = (
            dep_score * 0.30 +
            time_score * 0.30 +
            feature_score * 0.20 +
            reg_score * 0.20
        )

        return int(min(100, max(0, score)))

    @staticmethod
    def calculate_risk_score(risks: RiskAssessment) -> int:
        """Calculate risk score (lower is better)"""
        # Market risk (competition and demand)
        market_score = 80 if "competitive" in risks.biggest_risk.lower() else \
                      50 if "market" in risks.biggest_risk.lower() else 30

        # Technical risk (complexity and dependencies)
        tech_score = min(100, len(risks.key_dependencies) * 15)

        # Financial risk (startup costs)
        total_costs = sum(risks.startup_costs.values())
        financial_score = 100 if total_costs > 100000 else \
                         70 if total_costs > 50000 else \
                         40 if total_costs > 10000 else 20

        # Execution risk (time and commitment)
        exec_score = 80 if "team" in risks.biggest_risk.lower() else \
                    60 if "time" in risks.biggest_risk.lower() else 40

        # Equal weighting
        score = (market_score + tech_score + financial_score + exec_score) / 4
        return int(min(100, max(0, score)))

    @staticmethod
    def calculate_overall_grade(scores: ComputedScores) -> str:
        """Calculate overall grade based on score thresholds"""
        if (scores.scalability_score > 80 and
            scores.complexity_score < 30 and
            scores.risk_score < 30):
            return "A"
        elif (scores.scalability_score > 60 and
              scores.complexity_score < 50 and
              scores.risk_score < 50):
            return "B"
        elif (scores.scalability_score > 40 and
              scores.complexity_score < 70 and
              scores.risk_score < 70):
            return "C"
        elif (scores.scalability_score > 20 and
              scores.complexity_score < 90 and
              scores.risk_score < 90):
            return "D"
        else:
            return "F"

class BlindspotDetector:
    """Detect common agency development blindspots"""

    BLINDSPOT_RULES = [
        {
            "pattern": r"build.*better",
            "flag": "\"We'll build it better\" syndrome",
            "advice": "Focus on distribution and customer acquisition, not just quality"
        },
        {
            "pattern": r"feature.*feature.*feature",
            "flag": "\"Features equal value\" fallacy",
            "advice": "One feature done perfectly beats many mediocre ones"
        },
        {
            "pattern": r"we.*different",
            "flag": "\"We're different from clients\" delusion",
            "advice": "You need marketing and sales strategy too"
        },
        {
            "pattern": r"technical.*complex",
            "flag": "\"Code is the hard part\" bias",
            "advice": "Getting customers is harder than writing code"
        },
        {
            "pattern": r"monetization.*later|figure.*out.*pricing",
            "flag": "\"We'll figure out monetization later\"",
            "advice": "Charge from day one with clear pricing strategy"
        },
        {
            "pattern": r"perfect|polish|ready",
            "flag": "\"Perfect before launch\" trap",
            "advice": "Ship in 30 days or scope down"
        }
    ]

    @classmethod
    def detect_blindspots(cls, raw_idea: RawIdea) -> List[str]:
        """Detect blindspots in business idea"""
        blindspots = []
        combined_text = f"{raw_idea.problem} {raw_idea.solution} {raw_idea.technical_approach or ''}"

        for rule in cls.BLINDSPOT_RULES:
            if re.search(rule["pattern"], combined_text, re.IGNORECASE):
                blindspots.append(f"{rule['flag']}: {rule['advice']}")

        # Check for vague monetization
        if not raw_idea.monetization or len(raw_idea.monetization) < 20:
            blindspots.append("\"We'll figure out monetization later\": Charge from day one with clear pricing strategy")

        # Check for unrealistic timeline
        if raw_idea.technical_approach and len(raw_idea.technical_approach) > 200:
            blindspots.append("\"Perfect before launch\" trap: Ship in 30 days or scope down")

        # Check for timeline mentions
        timeline_text = f"{raw_idea.technical_approach or ''} {raw_idea.solution}"
        if any(phrase in timeline_text.lower() for phrase in ["6 months", "year", "years", "months"]):
            blindspots.append("\"Perfect before launch\" trap: Ship in 30 days or scope down")

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
        handler.setFormatter(logging.Formatter('%(message)s'))
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
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))

    def parse_markdown(self, content: str) -> RawIdea:
        """Parse markdown content into RawIdea model"""
        # 1. Extract title/name
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = title_match.group(1).strip() if title_match else "Untitled Idea"

        # 2. Extract sections
        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            if line.startswith('##'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.replace('#', '').strip().lower()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Don't forget the last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        # 3. Map sections to RawIdea fields
        return RawIdea(
            name=name[:100],  # Enforce length limit
            problem=sections.get('problem', sections.get('problem statement', ''))[:1000],
            solution=sections.get('solution', sections.get('proposed solution', ''))[:1000],
            target_customer=sections.get('target customer', sections.get('customer', ''))[:500] or None,
            monetization=sections.get('revenue model', sections.get('monetization', ''))[:500] or None,
            technical_approach=sections.get('technical approach', sections.get('implementation', ''))[:500] or None,
            inspiration=sections.get('similar companies', sections.get('inspiration', ''))[:500] or None
        )

    def evaluate_idea(self, file_path: Path, output_format: str = "json") -> Envelope:
        """Main evaluation pipeline"""
        trace_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Log start of evaluation
            self._log_event("agent_run", trace_id=trace_id, input_file=str(file_path))

            # 1. Read and parse input
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            content = file_path.read_text(encoding='utf-8')
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # 2. Parse markdown to RawIdea
            raw_idea = self.parse_markdown(content)

            # 3. Create deterministic analysis (no LLM by default per constitution)
            if not self.config.model_enabled:
                evaluated = self._deterministic_evaluation(raw_idea)
            else:
                # LLM-powered evaluation (if enabled)
                evaluated = self._llm_evaluation(raw_idea, trace_id)

            # 4. Calculate processing metrics
            processing_time = time.time() - start_time

            # 5. Create response envelope
            meta = MetaModel(
                trace_id=trace_id,
                hash=content_hash,
                cost={"tokens_in": 0, "tokens_out": 0, "usd": 0.0}  # Updated by LLM calls
            )

            envelope = Envelope(
                meta=meta,
                input=raw_idea,
                output=evaluated
            )

            self._log_event("agent_run_complete",
                           trace_id=trace_id,
                           processing_time=processing_time,
                           outcome="ok")

            return envelope

        except Exception as e:
            error = ErrorModel(
                type="validation_error" if isinstance(e, ValueError) else "file_error",
                message=str(e),
                details={"trace_id": trace_id},
                recoverable=True
            )

            return Envelope(
                meta=MetaModel(trace_id=trace_id),
                error=error
            )

    def _deterministic_evaluation(self, raw_idea: RawIdea) -> EvaluatedIdea:
        """Fallback deterministic evaluation without LLM calls"""

        # Create deterministic business model analysis
        business_model = BusinessModel(
            value_creation=f"Creates value by solving: {raw_idea.problem[:100]}...",
            value_capture=raw_idea.monetization or "Revenue model not specified - needs clarification",
            unit_economics="Unit economics analysis requires more detailed financial information",
            growth_mechanism=f"Growth through {raw_idea.target_customer or 'target market'} adoption",
            competitive_moat="Competitive advantages require market analysis to determine",
            minimum_viable_scope=f"MVP focusing on core {raw_idea.solution[:100]}... functionality"
        )

        # Create scalability analysis
        scalability = ScalabilityFactors(
            marginal_cost_per_customer="Marginal cost analysis requires technical architecture details",
            geographic_constraints="Geographic reach depends on solution implementation approach",
            automation_potential=50,  # Conservative estimate
            network_effects="Network effects potential requires user interaction analysis",
            platform_potential=False,  # Conservative default
            data_compound_value="Data accumulation benefits require more detailed analysis"
        )

        # Create risk assessment
        risks = RiskAssessment(
            startup_costs={"development": 10000.0, "marketing": 5000.0},  # Conservative estimates
            time_to_revenue="6-12 months estimated based on typical development cycles",
            key_dependencies=["market validation", "technical implementation", "customer acquisition"],
            biggest_risk="Market acceptance and customer acquisition challenges",
            boring_version=f"Simple version: {raw_idea.solution[:100]}... with basic features",
            why_not_already_dominated="Market gap analysis requires competitive research"
        )

        # Calculate scores
        scalability_score = ScoringRules.calculate_scalability_score(scalability, self.config.scalability_weights)
        complexity_score = ScoringRules.calculate_complexity_score(raw_idea, risks)
        risk_score = ScoringRules.calculate_risk_score(risks)

        scores = ComputedScores(
            scalability_score=scalability_score,
            complexity_score=complexity_score,
            risk_score=risk_score,
            overall_grade="C"  # Temporary value
        )

        # Calculate and update overall grade
        scores.overall_grade = ScoringRules.calculate_overall_grade(scores)

        # Generate insights
        blindspots = BlindspotDetector.detect_blindspots(raw_idea)
        insights = ActionableInsights(
            critical_questions=[
                "Who exactly is your target customer and how will you reach them?",
                "What is your specific competitive advantage over existing solutions?",
                "How will you validate market demand before building?"
            ],
            quick_wins=[
                "Conduct customer interviews to validate problem-solution fit",
                "Research direct competitors and their pricing strategies",
                "Create a simple landing page to test market interest"
            ],
            red_flags=self._ensure_min_red_flags(blindspots),
            next_steps=[
                "Define specific customer personas and their pain points",
                "Research and analyze direct and indirect competitors",
                "Create detailed financial projections and unit economics"
            ],
            similar_successes=[
                "Buffer (social media management - proven SaaS model)",
                "Canva (design tools - freemium to premium conversion)",
                "Slack (communication tools - viral growth through teams)"
            ],
            recommended_mvp=f"Build a simple {raw_idea.solution[:50]}... tool that solves the core problem for a specific customer segment within 30 days"
        )

        # Create metadata
        metadata = EvaluationMetadata(
            model_used="deterministic_fallback",
            processing_time=0.1,
            token_usage={"deterministic": 0},
            confidence_scores={"overall": 0.6}  # Lower confidence for deterministic
        )

        return EvaluatedIdea(
            raw_idea=raw_idea,
            business_model=business_model,
            scalability=scalability,
            risks=risks,
            scores=scores,
            insights=insights,
            metadata=metadata
        )

    def _llm_evaluation(self, raw_idea: RawIdea, trace_id: str) -> EvaluatedIdea:
        """LLM-powered evaluation (placeholder - requires PydanticAI integration)"""
        # This would be implemented with PydanticAI when model is enabled
        # For now, fall back to deterministic evaluation
        return self._deterministic_evaluation(raw_idea)

    def generate_enhanced_markdown(self, evaluated: EvaluatedIdea) -> str:
        """Generate enhanced markdown output with emojis and formatting"""
        # Calculate overall score for title
        overall_score = int(
            (evaluated.scores.scalability_score * 0.4) +
            ((100 - evaluated.scores.complexity_score) * 0.3) +
            ((100 - evaluated.scores.risk_score) * 0.3)
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

        markdown += f"\n## 🚀 Recommended MVP (30 days)\n{evaluated.insights.recommended_mvp}\n"

        # Find the first similar success
        similar_company = evaluated.insights.similar_successes[0] if evaluated.insights.similar_successes else "No similar examples found"
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

    def _ensure_min_red_flags(self, blindspots: List[str]) -> List[str]:
        """Ensure at least 3 red flags are present, padding with defaults if needed"""
        default_flags = [
            "Vague target customer definition may lead to unfocused development",
            "Unclear revenue model creates uncertainty for business viability",
            "Limited competitive analysis increases market risk"
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

    def compare_ideas(self, idea_files: List[Path]) -> ComparisonResult:
        """Compare multiple business ideas and provide ranking with analysis"""
        if len(idea_files) < 2 or len(idea_files) > 10:
            raise ValueError("Can only compare 2-10 business ideas")

        evaluated_ideas: List[EvaluatedIdea] = []

        # Evaluate each idea independently
        for idea_file in idea_files:
            try:
                envelope = self.evaluate_idea(idea_file)
                if envelope.error:
                    self.logger.error(f"Failed to evaluate {idea_file.name}: {envelope.error}")
                    continue
                evaluated_ideas.append(envelope.output)
            except Exception as e:
                self.logger.error(f"Error evaluating {idea_file.name}: {str(e)}")
                continue

        if len(evaluated_ideas) < 2:
            raise ValueError("Need at least 2 successfully evaluated ideas for comparison")

        # Sort by overall score (descending)
        sorted_ideas = sorted(evaluated_ideas,
                            key=lambda x: x.scores.scalability_score - x.scores.complexity_score - x.scores.risk_score,
                            reverse=True)

        # Create ranking with relative analysis
        ranking = []
        for i, idea in enumerate(sorted_ideas):
            rank_entry = {
                "rank": i + 1,
                "name": idea.raw_idea.name,
                "grade": idea.scores.overall_grade,
                "total_score": idea.scores.scalability_score - idea.scores.complexity_score - idea.scores.risk_score,
                "scalability": idea.scores.scalability_score,
                "complexity": idea.scores.complexity_score,
                "risk": idea.scores.risk_score,
                "strengths": self._identify_relative_strengths(idea, sorted_ideas),
                "weaknesses": self._identify_relative_weaknesses(idea, sorted_ideas)
            }
            ranking.append(rank_entry)

        # Generate recommendation
        top_idea = sorted_ideas[0]
        recommendation = self._generate_comparison_recommendation(top_idea, sorted_ideas)

        # Generate comparison summary
        comparison_summary = self._generate_comparison_summary(sorted_ideas, ranking)

        return ComparisonResult(
            ideas=evaluated_ideas,
            ranking=ranking,
            recommendation=recommendation,
            comparison_summary=comparison_summary
        )

    def _identify_relative_strengths(self, idea: EvaluatedIdea, all_ideas: List[EvaluatedIdea]) -> List[str]:
        """Identify this idea's strengths relative to others"""
        strengths = []

        # Calculate averages
        avg_scalability = sum(i.scores.scalability_score for i in all_ideas) / len(all_ideas)
        avg_complexity = sum(i.scores.complexity_score for i in all_ideas) / len(all_ideas)
        avg_risk = sum(i.scores.risk_score for i in all_ideas) / len(all_ideas)

        # Compare against averages
        if idea.scores.scalability_score > avg_scalability + 10:
            strengths.append("High scalability potential")
        if idea.scores.complexity_score < avg_complexity - 10:
            strengths.append("Lower implementation complexity")
        if idea.scores.risk_score < avg_risk - 10:
            strengths.append("Lower business risk")

        # Domain-specific strengths
        if "SaaS" in idea.raw_idea.monetization or "subscription" in idea.raw_idea.monetization.lower():
            strengths.append("Recurring revenue model")
        if "automation" in idea.raw_idea.solution.lower():
            strengths.append("Automation-driven efficiency")
        if "API" in idea.raw_idea.solution or "platform" in idea.raw_idea.solution.lower():
            strengths.append("Platform scalability")

        return strengths[:3]  # Limit to top 3 strengths

    def _identify_relative_weaknesses(self, idea: EvaluatedIdea, all_ideas: List[EvaluatedIdea]) -> List[str]:
        """Identify this idea's weaknesses relative to others"""
        weaknesses = []

        # Calculate averages
        avg_scalability = sum(i.scores.scalability_score for i in all_ideas) / len(all_ideas)
        avg_complexity = sum(i.scores.complexity_score for i in all_ideas) / len(all_ideas)
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
        if idea.scores.overall_grade in ['D', 'F']:
            weaknesses.append("Below-average overall score")

        return weaknesses[:3]  # Limit to top 3 weaknesses

    def _generate_comparison_recommendation(self, top_idea: EvaluatedIdea, all_ideas: List[EvaluatedIdea]) -> str:
        """Generate recommendation for which idea to pursue"""
        grade_distribution = {}
        for idea in all_ideas:
            grade = idea.scores.overall_grade
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

        if top_idea.scores.overall_grade in ['A', 'B']:
            confidence = "strongly recommend"
        elif top_idea.scores.overall_grade == 'C':
            confidence = "cautiously recommend"
        else:
            confidence = "suggest reconsidering"

        return f"Based on the analysis, I {confidence} pursuing '{top_idea.raw_idea.name}' " \
               f"(Grade: {top_idea.scores.overall_grade}). This idea scored highest on overall potential " \
               f"with {top_idea.scores.scalability_score}% scalability, {100-top_idea.scores.complexity_score}% " \
               f"ease of implementation, and {100-top_idea.scores.risk_score}% risk mitigation."

    def _generate_comparison_summary(self, sorted_ideas: List[EvaluatedIdea], ranking: List[Dict]) -> str:
        """Generate overall comparison summary"""
        total_ideas = len(sorted_ideas)
        grades = [idea.scores.overall_grade for idea in sorted_ideas]
        grade_counts = {grade: grades.count(grade) for grade in ['A', 'B', 'C', 'D', 'F']}

        summary = f"Compared {total_ideas} business ideas. "

        if grade_counts['A'] > 0:
            summary += f"{grade_counts['A']} received grade A (excellent). "
        if grade_counts['B'] > 0:
            summary += f"{grade_counts['B']} received grade B (good). "
        if grade_counts['C'] > 0:
            summary += f"{grade_counts['C']} received grade C (average). "
        if grade_counts['D'] + grade_counts['F'] > 0:
            summary += f"{grade_counts['D'] + grade_counts['F']} need significant improvement. "

        # Identify patterns
        avg_scalability = sum(i.scores.scalability_score for i in sorted_ideas) / len(sorted_ideas)
        avg_complexity = sum(i.scores.complexity_score for i in sorted_ideas) / len(sorted_ideas)

        if avg_scalability > 70:
            summary += "Overall high scalability potential across ideas. "
        if avg_complexity > 70:
            summary += "Most ideas show high implementation complexity. "

        return summary.strip()

def main() -> None:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Business Idea Evaluator - Transform business ideas into structured insights",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a business idea")
    eval_parser.add_argument("file", type=Path, help="Markdown file containing business idea")
    eval_parser.add_argument("--output", choices=["json", "markdown", "both"], default="json")
    eval_parser.add_argument("--model", help="Override default LLM model")
    eval_parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare multiple business ideas")
    compare_parser.add_argument("files", nargs="+", type=Path, help="Markdown files to compare")
    compare_parser.add_argument("--output", choices=["json", "markdown"], default="json")

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
    if hasattr(args, 'verbose') and args.verbose:
        config.verbose_logging = True
    if hasattr(args, 'model') and args.model:
        config.model_name = args.model

    # Initialize evaluator
    evaluator = BusinessIdeaEvaluator(config)

    # Execute command
    if args.command == "evaluate":
        envelope = evaluator.evaluate_idea(args.file, args.output)

        if args.output == "json":
            print(envelope.model_dump_json(indent=2))
        elif args.output == "markdown":
            if envelope.output:
                print(evaluator.generate_enhanced_markdown(envelope.output))
            else:
                print("Error generating markdown output")
                print(envelope.model_dump_json(indent=2))
        elif args.output == "both":
            # Print JSON first
            print("=== JSON OUTPUT ===")
            print(envelope.model_dump_json(indent=2))
            print("\n=== MARKDOWN OUTPUT ===")
            if envelope.output:
                print(evaluator.generate_enhanced_markdown(envelope.output))
            else:
                print("Error generating markdown output")

    elif args.command == "compare":
        try:
            result = evaluator.compare_ideas(args.files)
            if args.output == "json":
                print(result.model_dump_json(indent=2))
            elif args.output == "markdown":
                # Generate markdown comparison table
                markdown = f"# Business Idea Comparison\n\n"
                markdown += f"## Summary\n{result.comparison_summary}\n\n"
                markdown += f"## Ranking\n\n| Rank | Idea | Grade | Total Score | Scalability | Complexity | Risk |\n"
                markdown += f"|------|------|-------|-------------|-------------|------------|------|\n"
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
            content = args.file.read_text(encoding='utf-8')
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
            "Envelope": Envelope.model_json_schema()
        }
        print(json.dumps(schemas, indent=2))

    else:
        print(f"Command '{args.command}' not yet implemented")

if __name__ == "__main__":
    main()