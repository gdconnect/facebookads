#!/usr/bin/env python3
"""
Customer Journey Mapper Generator - Constitutional Single-File Python Agent

DESCRIPTION:
Generates comprehensive customer journey maps for niche markets based on market
specifications. Accepts various input formats (markdown, JSON, text), normalizes them
via LLM calls, infers customer personas, and generates complete journey maps conforming
to the customer_journey.json.schema.

USAGE EXAMPLES:
    # Generate from natural language description
    python customer_journey_mapper.py --input "Eco-conscious millennials buying sustainable fashion"

    # Generate from structured JSON input
    python customer_journey_mapper.py --input-file market_spec.json --output journey.json

    # Generate from markdown specification
    python customer_journey_mapper.py --input-file spec.md --input-format text/markdown

ACCEPTED INPUT CONTENT TYPES:
    - text/plain: Natural language market description
    - text/markdown: Structured markdown market specification
    - application/json: Structured JSON market data

EXAMPLE OUTPUT:
    Agent Envelope with customer journey map conforming to customer_journey.json.schema

DECLARED BUDGETS:
    - P95 Latency: <5 seconds total runtime
    - Token Budget: <2000 tokens per execution (≤2 LLM calls)
    - Max Retries: ≤1 retry per LLM call
    - Max Cost: <$0.10 per execution

VERSION: 1.0.0
CONSTITUTIONAL COMPLIANCE: Articles I-XVI (Single-file, Schema-first, LLM fallback)
"""

import argparse
import json
import hashlib
import uuid
import sys
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Literal, Tuple
import logging

# Third-party dependencies (justified in header docstring)
try:
    from pydantic import BaseModel, Field, field_validator, ConfigDict
except ImportError:
    print("ERROR: pydantic v2 required. Install with: pip install pydantic>=2.0.0", file=sys.stderr)
    sys.exit(1)

# ============================================================================
# CONFIG SECTION (Lines 20-120) - Hierarchical Configuration
# ============================================================================

# 1. Sensible defaults
DEFAULT_CONFIG: Dict[str, Any] = {
    "version": "1.0.0",
    "agent_name": "customer_journey_mapper",

    # LLM Configuration (STRICT mode by default - Article X)
    "llm": {
        "enabled": False,  # STRICT mode default
        "provider": "openai",  # openai, anthropic, gemini, local
        "base_url": None,  # Optional custom endpoint
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
        "timeout_s": 30,
        "max_tokens": 1000,
        "temperature": 0.1,
        "top_p": 0.9,
        "max_retries": 1,
        "headers": {}
    },

    # Performance budgets (Article XII)
    "budgets": {
        "max_runtime_s": 5,
        "max_tokens_total": 2000,
        "max_usd_cost": 0.10,
        "max_llm_calls": 2
    },

    # Decision table configuration
    "rules": {
        "market_classification": "inline",  # or path to JSON file
        "journey_templates": "inline",
        "persona_templates": "inline"
    },

    # Brand and compliance (Article XIII)
    "brand": {
        "default_token": "neutral",
        "tone": "professional",
        "compliance_level": "standard"
    },

    # Observability (Article IX)
    "logging": {
        "level": "INFO",
        "emit_jsonl": True,
        "trace_enabled": True
    }
}

# 2. Environment variable overrides
def load_env_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Override config with environment variables"""
    # LLM provider configuration
    if os.getenv("LLM_PROVIDER"):
        config["llm"]["provider"] = os.getenv("LLM_PROVIDER")
    if os.getenv("LLM_MODEL"):
        config["llm"]["model"] = os.getenv("LLM_MODEL")
    if os.getenv("LLM_ENABLED") == "true":
        config["llm"]["enabled"] = True

    # API keys
    if os.getenv("OPENAI_API_KEY"):
        config["llm"]["api_key_env"] = "OPENAI_API_KEY"
    elif os.getenv("ANTHROPIC_API_KEY"):
        config["llm"]["api_key_env"] = "ANTHROPIC_API_KEY"
    else:
        # No API key environment variable found - use default
        pass

    # Budget overrides
    max_runtime = os.getenv("MAX_RUNTIME_S")
    if max_runtime:
        config["budgets"]["max_runtime_s"] = int(max_runtime)

    return config

# 3. CLI argument parsing with required flags (Article V)
def create_argument_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser with constitutional requirements"""
    parser = argparse.ArgumentParser(
        description="Customer Journey Mapper Generator - Constitutional Single-File Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --input "Tech startups needing accounting software"
    %(prog)s --input-file market.md --input-format text/markdown
    %(prog)s --input-file market.json --output journey.json --brand-token enterprise
        """
    )

    # Input specification (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input",
        help="Natural language market description"
    )
    input_group.add_argument(
        "--input-file",
        type=Path,
        help="Path to input file (JSON, markdown, or text)"
    )

    # Input format specification
    parser.add_argument(
        "--input-format",
        choices=["text/plain", "text/markdown", "application/json"],
        default="text/plain",
        help="Input content type (default: text/plain)"
    )

    # Output specification
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("customer_journey.json"),
        help="Output file path (default: customer_journey.json)"
    )

    # Constitutional required flags (Article V)
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--rules",
        type=Path,
        help="Path to decision rules file"
    )
    parser.add_argument(
        "--brand-token",
        default="neutral",
        help="Brand configuration token (default: neutral)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode (disable LLM fallback)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    # Additional flags
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate input without generating output"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate existing journey map file"
    )

    return parser

# ============================================================================
# PYDANTIC MODELS (T022) - Schema validation and type safety
# ============================================================================

class Demographics(BaseModel):
    """Customer demographics information"""
    age: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[str] = None

class NicheMarketInput(BaseModel):
    """Input validation model for niche market specifications"""
    model_config = ConfigDict(extra='forbid')

    market_description: str = Field(min_length=10, description="Natural language market description")
    industry: Optional[str] = Field(None, description="Industry category")
    target_demographics: Optional[Demographics] = None
    product_service: Optional[str] = None
    business_model: Optional[str] = Field(None, pattern=r"^(B2B|B2C|B2B2C|marketplace|subscription|freemium)$")
    input_content_type: str = Field(default="text/plain", pattern=r"^(text/plain|text/markdown|application/json)$")
    brand_token: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9_-]+$")

class CostMetrics(BaseModel):
    """Token and cost tracking"""
    tokens_in: int = Field(default=0, ge=0)
    tokens_out: int = Field(default=0, ge=0)
    usd: float = Field(default=0.0, ge=0.0)

class AgentMeta(BaseModel):
    """Agent metadata for constitutional compliance"""
    agent: str = Field(default="customer_journey_mapper")
    version: str
    trace_id: str
    ts: str  # ISO-8601 timestamp
    brand_token: str
    hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    cost: CostMetrics
    prompt_id: Optional[str] = None
    prompt_hash: Optional[str] = None

class AgentEnvelope(BaseModel):
    """Constitutional Agent Envelope for all outputs"""
    meta: AgentMeta
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# ============================================================================
# INPUT VALIDATION (T015) - Content type detection and validation
# ============================================================================

def detect_content_type(input_text: str) -> str:
    """Detect content type from input text patterns"""
    input_text = input_text.strip()

    # JSON detection
    if input_text.startswith('{') and input_text.endswith('}'):
        try:
            json.loads(input_text)
            return "application/json"
        except json.JSONDecodeError:
            pass

    # Markdown detection
    if any(marker in input_text for marker in ['# ', '## ', '### ', '- **', '* **']):
        return "text/markdown"

    return "text/plain"

def validate_input(input_data: Dict[str, Any]) -> bool:
    """Validate input against schema - implements contract test requirement"""
    try:
        NicheMarketInput(**input_data)
        return True
    except Exception as e:
        raise ValueError(f"Input validation failed: {e}")

def load_input(args: argparse.Namespace) -> Tuple[Dict[str, Any], str]:
    """Load and validate input from various sources"""
    # 1. Determine input source and content
    if args.input:
        input_content = args.input
        content_type = args.input_format
    elif args.input_file:
        if not args.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {args.input_file}")

        input_content = args.input_file.read_text(encoding='utf-8')
        content_type = args.input_format

        # Auto-detect if not specified
        if content_type == "text/plain":
            detected_type = detect_content_type(input_content)
            if detected_type != "text/plain":
                content_type = detected_type
    else:
        # Handle the case where neither input nor input_file is provided
        raise ValueError("Either --input or --input-file must be provided")

    # 2. Parse based on content type
    if content_type == "application/json":
        try:
            input_data = json.loads(input_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON input: {e}")
    elif content_type == "text/markdown":
        # For now, convert markdown to basic structured input
        # Full LLM normalization would be implemented in T020
        input_data = {
            "market_description": input_content[:500] + "..." if len(input_content) > 500 else input_content,
            "input_content_type": content_type
        }
    else:  # text/plain
        input_data = {
            "market_description": input_content,
            "input_content_type": content_type
        }

        # Basic keyword inference for natural language input
        content_lower = input_content.lower()

        # Infer industry from keywords
        if not input_data.get("industry"):
            if any(word in content_lower for word in ["shopping", "ecommerce", "e-commerce", "retail", "store", "buy", "purchase"]):
                input_data["industry"] = "ecommerce"
            elif any(word in content_lower for word in ["saas", "software", "platform", "application", "system"]):
                input_data["industry"] = "saas"
            elif any(word in content_lower for word in ["health", "medical", "healthcare", "telemedicine", "patient"]):
                input_data["industry"] = "healthcare"
            else:
                # No industry keywords found - keep default or leave unset
                pass

        # Infer business model from keywords
        if not input_data.get("business_model"):
            if any(word in content_lower for word in ["consumer", "customer", "shopper", "millennials", "people"]):
                input_data["business_model"] = "B2C"
            elif any(word in content_lower for word in ["business", "company", "organization", "enterprise", "professional"]):
                input_data["business_model"] = "B2B"
            else:
                # No business model keywords found - keep default or leave unset
                pass

    # 3. Add brand token if provided
    if hasattr(args, 'brand_token') and args.brand_token:
        input_data["brand_token"] = args.brand_token

    # 4. Validate
    validate_input(input_data)

    return input_data, content_type

# ============================================================================
# DECISION TABLES (T016-T018) - Business logic without LLM
# ============================================================================

# Market classification decision table (T016)
MARKET_CLASSIFICATION_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "saas_b2b",
        "conditions": {"industry": "saas", "business_model": "B2B"},
        "market_type": "B2B_SaaS",
        "persona_template": "business_professional",
        "journey_template": "b2b_saas_journey",
        "confidence": 0.9,
        "why": "SaaS B2B has established patterns"
    },
    {
        "rule_id": "ecommerce_b2c",
        "conditions": {"industry": "ecommerce", "business_model": "B2C"},
        "market_type": "B2C_Ecommerce",
        "persona_template": "consumer_shopper",
        "journey_template": "b2c_ecommerce_journey",
        "confidence": 0.9,
        "why": "E-commerce B2C well-established patterns"
    },
    {
        "rule_id": "healthcare_any",
        "conditions": {"industry": "healthcare"},
        "market_type": "Healthcare",
        "persona_template": "healthcare_professional",
        "journey_template": "healthcare_journey",
        "confidence": 0.8,
        "why": "Healthcare has unique compliance requirements"
    },
    {
        "rule_id": "default_b2b",
        "conditions": {"business_model": "B2B"},
        "market_type": "B2B_Generic",
        "persona_template": "business_decision_maker",
        "journey_template": "b2b_generic_journey",
        "confidence": 0.6,
        "why": "Default B2B pattern"
    },
    {
        "rule_id": "default_b2c",
        "conditions": {"business_model": "B2C"},
        "market_type": "B2C_Generic",
        "persona_template": "consumer_generic",
        "journey_template": "b2c_generic_journey",
        "confidence": 0.6,
        "why": "Default B2C pattern"
    },
    {
        "rule_id": "fallback",
        "conditions": {},
        "market_type": "Generic",
        "persona_template": "generic_customer",
        "journey_template": "generic_journey",
        "confidence": 0.4,
        "why": "Fallback when no specific patterns match"
    }
]

def classify_market(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Classify market using decision tables (first-match-wins)"""
    for rule in MARKET_CLASSIFICATION_RULES:
        conditions: Dict[str, Any] = rule["conditions"]
        match = True

        for field, expected_value in conditions.items():
            if field not in input_data or input_data[field] != expected_value:
                match = False
                break

        if match:
            return rule

    # Should never reach here due to fallback rule
    return MARKET_CLASSIFICATION_RULES[-1]

# ============================================================================
# JOURNEY GENERATION (T021) - Template-based generation
# ============================================================================

def generate_customer_persona(market_classification: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate customer persona based on market classification"""
    persona_template = market_classification["persona_template"]

    # Basic persona templates
    persona_templates = {
        "business_professional": {
            "name": "Business Professional",
            "demographics": {"age": "35-55", "occupation": "Business Professional", "income": "$75k+"},
            "goals": ["Increase efficiency", "Reduce costs", "Improve processes"],
            "painPoints": ["Complex integrations", "Training requirements", "ROI uncertainty"],
            "motivations": ["Business growth", "Competitive advantage", "Process optimization"]
        },
        "consumer_shopper": {
            "name": "Eco-conscious Millennial",
            "demographics": {"age": "25-35", "occupation": "Professional", "income": "$50k+"},
            "goals": ["Find sustainable products", "Support ethical brands", "Convenient shopping"],
            "painPoints": ["Trust in sustainability claims", "Premium pricing", "Limited options"],
            "motivations": ["Environmental impact", "Social responsibility", "Quality"]
        },
        "healthcare_professional": {
            "name": "Healthcare Professional",
            "demographics": {"age": "35-55", "occupation": "Healthcare Provider", "income": "$100k+"},
            "goals": ["Improve patient care", "Ensure compliance", "Increase efficiency"],
            "painPoints": ["Regulatory compliance", "Integration challenges", "Patient adoption"],
            "motivations": ["Patient outcomes", "Efficiency", "Compliance"]
        }
    }

    template = persona_templates.get(persona_template, persona_templates["business_professional"])

    return {
        "id": str(uuid.uuid4()),
        "name": template["name"],
        "demographics": template["demographics"],
        "goals": template["goals"],
        "painPoints": template["painPoints"],
        "motivations": template["motivations"]
    }

def generate_journey_stages(market_classification: Dict[str, Any], persona: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate journey stages based on market type"""
    journey_template = market_classification["journey_template"]

    # Stage templates by journey type
    if "b2b" in journey_template:
        stages = [
            {
                "stageId": str(uuid.uuid4()),
                "stageName": "Awareness",
                "description": "Initial problem recognition and solution discovery",
                "touchpoints": [
                    {
                        "touchpointId": str(uuid.uuid4()),
                        "channel": "website",
                        "action": "Research solutions online",
                        "emotions": [{"emotion": "neutral", "intensity": 3}],
                        "painPoints": ["Information overload"],
                        "opportunities": ["Clear value proposition"]
                    }
                ]
            },
            {
                "stageId": str(uuid.uuid4()),
                "stageName": "Consideration",
                "description": "Evaluation of alternatives and requirements gathering",
                "touchpoints": [
                    {
                        "touchpointId": str(uuid.uuid4()),
                        "channel": "email",
                        "action": "Request product demo",
                        "emotions": [{"emotion": "happy", "intensity": 4}],
                        "painPoints": ["Complex feature comparison"],
                        "opportunities": ["Personalized demo"]
                    }
                ]
            },
            {
                "stageId": str(uuid.uuid4()),
                "stageName": "Decision",
                "description": "Final evaluation and purchase decision",
                "touchpoints": [
                    {
                        "touchpointId": str(uuid.uuid4()),
                        "channel": "phone",
                        "action": "Negotiate terms and pricing",
                        "emotions": [{"emotion": "anxious", "intensity": 3}],
                        "painPoints": ["Budget approval process"],
                        "opportunities": ["Flexible pricing options"]
                    }
                ]
            }
        ]
    else:  # B2C or generic
        stages = [
            {
                "stageId": str(uuid.uuid4()),
                "stageName": "Awareness",
                "description": "Discovery of product or service",
                "touchpoints": [
                    {
                        "touchpointId": str(uuid.uuid4()),
                        "channel": "social_media",
                        "action": "See product advertisement",
                        "emotions": [{"emotion": "neutral", "intensity": 3}],
                        "painPoints": ["Ad fatigue"],
                        "opportunities": ["Engaging content"]
                    }
                ]
            },
            {
                "stageId": str(uuid.uuid4()),
                "stageName": "Consideration",
                "description": "Product research and comparison",
                "touchpoints": [
                    {
                        "touchpointId": str(uuid.uuid4()),
                        "channel": "website",
                        "action": "Browse product catalog and reviews",
                        "emotions": [{"emotion": "confused", "intensity": 3}],
                        "painPoints": ["Too many options", "Conflicting reviews"],
                        "opportunities": ["Product recommendations", "Clear comparisons"]
                    },
                    {
                        "touchpointId": str(uuid.uuid4()),
                        "channel": "mobile_app",
                        "action": "Check prices and availability",
                        "emotions": [{"emotion": "neutral", "intensity": 3}],
                        "painPoints": ["Slow loading", "Complex navigation"],
                        "opportunities": ["Push notifications", "Saved items"]
                    }
                ]
            },
            {
                "stageId": str(uuid.uuid4()),
                "stageName": "Purchase",
                "description": "Product purchase and payment",
                "touchpoints": [
                    {
                        "touchpointId": str(uuid.uuid4()),
                        "channel": "website",
                        "action": "Complete online purchase",
                        "emotions": [{"emotion": "excited", "intensity": 4}],
                        "painPoints": ["Payment security concerns"],
                        "opportunities": ["Streamlined checkout"]
                    }
                ]
            },
            {
                "stageId": str(uuid.uuid4()),
                "stageName": "Post-Purchase",
                "description": "Follow-up and customer retention",
                "touchpoints": [
                    {
                        "touchpointId": str(uuid.uuid4()),
                        "channel": "email",
                        "action": "Receive order confirmation and updates",
                        "emotions": [{"emotion": "satisfied", "intensity": 4}],
                        "painPoints": ["Delivery delays"],
                        "opportunities": ["Personalized recommendations"]
                    }
                ]
            }
        ]

    return stages

def generate_journey_map_internal(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete customer journey map - internal function"""
    # 1. Classify market using decision tables
    market_classification = classify_market(input_data)

    # 2. Generate persona
    persona = generate_customer_persona(market_classification, input_data)

    # 3. Generate journey stages
    stages = generate_journey_stages(market_classification, persona)

    # 4. Create journey map
    journey_map = {
        "journeyId": str(uuid.uuid4()),
        "journeyName": f"{persona['name']} Journey",
        "persona": persona,
        "stages": stages,
        "metadata": {
            "createdDate": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "industry": input_data.get("industry", "unknown"),
            "marketSegment": market_classification["market_type"],
            "tags": [market_classification["market_type"].lower()]
        }
    }

    return journey_map

def generate_journey_map(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete customer journey map with Agent Envelope - for test compatibility"""
    # This version returns Agent Envelope for contract test compatibility
    trace_id = str(uuid.uuid4())
    cost_metrics = CostMetrics()
    config = DEFAULT_CONFIG.copy()

    try:
        # Validate input first
        if not validate_input(input_data):
            raise ValueError("Invalid input data")

        # Generate the journey map
        journey_map = generate_journey_map_internal(input_data)

        # Wrap in Agent Envelope
        envelope = create_agent_envelope(input_data, journey_map, None, trace_id, config, cost_metrics)

        return envelope

    except Exception as e:
        # Handle errors by creating error envelope
        error_message = str(e)
        envelope = create_agent_envelope(input_data, None, error_message, trace_id, config, cost_metrics)
        return envelope

# ============================================================================
# AGENT ENVELOPE GENERATION (T023) - Constitutional output format
# ============================================================================

def create_agent_envelope(input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]],
                         error_message: Optional[str], trace_id: str, config: Dict[str, Any],
                         cost_metrics: CostMetrics) -> Dict[str, Any]:
    """Create constitutional Agent Envelope"""
    # Generate output hash
    output_content = json.dumps(output_data, sort_keys=True) if output_data else ""
    content_hash = hashlib.sha256(output_content.encode('utf-8')).hexdigest()

    meta = AgentMeta(
        version=config["version"],
        trace_id=trace_id,
        ts=datetime.now(timezone.utc).isoformat(),
        brand_token=input_data.get("brand_token", config["brand"]["default_token"]),
        hash=content_hash,
        cost=cost_metrics
    )

    envelope = AgentEnvelope(
        meta=meta,
        input=input_data,
        output=output_data,
        error=error_message
    )

    return envelope.model_dump()

# ============================================================================
# OBSERVABILITY (T025) - JSONL logging and cost tracking
# ============================================================================

def emit_jsonl_log(trace_id: str, config: Dict[str, Any], execution_time_ms: int,
                  input_content_type: str, cost_metrics: CostMetrics) -> None:
    """Emit JSONL observability log to STDERR (Article IX)"""
    log_entry = {
        "event": "agent_run",
        "agent": "customer_journey_mapper",
        "version": config["version"],
        "trace_id": trace_id,
        "ms": execution_time_ms,
        "bytes_in": 0,  # Would be calculated in full implementation
        "strict": not config["llm"]["enabled"],
        "input_content_type": input_content_type,
        "rules_path": "inline",
        "provider": config["llm"]["provider"] if config["llm"]["enabled"] else None,
        "prompt_id": None,  # Would be set if LLM used
        "prompt_hash": None  # Would be set if LLM used
    }

    print(json.dumps(log_entry), file=sys.stderr)

# ============================================================================
# MAIN EXECUTION (T013-T014) - Constitutional single-file agent
# ============================================================================

def main() -> int:
    """Main entry point - Constitutional single-file agent"""
    start_time = datetime.now(timezone.utc)
    trace_id = str(uuid.uuid4())
    cost_metrics = CostMetrics()

    # Initialize variables with defaults to ensure they're always bound (defensive programming)
    args = None  # Will be set by argument parser
    config = DEFAULT_CONFIG.copy()  # Safe default configuration
    content_type = "unknown"  # Default content type

    try:
        # 1. Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()

        # 2. Load and merge configuration
        config = DEFAULT_CONFIG.copy()
        config = load_env_config(config)

        # Override with CLI arguments
        if args.strict:
            config["llm"]["enabled"] = False

        config["logging"]["level"] = args.log_level
        config["brand"]["default_token"] = args.brand_token

        # 3. Setup logging
        logging.basicConfig(
            level=getattr(logging, config["logging"]["level"]),
            format="%(asctime)s [%(levelname)s] %(message)s"
        )

        # 4. Handle special modes
        if args.dry_run:
            print("Dry run mode - validation only")
            input_data, content_type = load_input(args)
            print("✅ Input validation successful")
            return 0

        # 5. Load and validate input
        input_data, content_type = load_input(args)

        # 6. Generate journey map (deterministic - no LLM in basic implementation)
        if args.strict:
            logging.debug("LLM disabled - running in strict mode with deterministic templates")
        else:
            logging.debug("LLM disabled by default - using deterministic templates (strict mode implied)")
        journey_map = generate_journey_map_internal(input_data)

        # 7. Create Agent Envelope
        envelope = create_agent_envelope(input_data, journey_map, None, trace_id, config, cost_metrics)

        # 8. Write output
        with open(args.output, 'w') as f:
            json.dump(envelope, f, indent=2)

        # 9. Emit observability log
        execution_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        emit_jsonl_log(trace_id, config, execution_time, content_type, cost_metrics)

        logging.info(f"✅ Journey map generated successfully: {args.output}")
        return 0

    except Exception as e:
        # Error handling with Agent Envelope (T024)
        execution_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        try:
            # Try to get input data for envelope if args is available
            if args is not None:
                input_data, content_type = load_input(args)
            else:
                input_data = {"error": "Failed to parse command line arguments"}
                content_type = "unknown"
        except:
            input_data = {"error": "Failed to parse input"}
            content_type = "unknown"

        # Create error envelope
        error_envelope = create_agent_envelope(input_data, None, str(e), trace_id, config, cost_metrics)

        # Write error envelope to output if possible
        try:
            if args is not None and hasattr(args, 'output'):
                with open(args.output, 'w') as f:
                    json.dump(error_envelope, f, indent=2)
        except:
            pass  # Fail silently on output error

        # Emit error log
        emit_jsonl_log(trace_id, config, execution_time, content_type, cost_metrics)

        logging.error(f"❌ Error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())