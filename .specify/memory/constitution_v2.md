# Schema-First Empire — Python Single-File Constitution v2.0 (PydanticAI Mandatory Edition)

**Version:** 2.0.0
**Ratified:** 2025-09-21
**Scope:** All **Python programs** in this repository MUST be implemented as **single-file agents** (`.py`).
Applies to storytelling, Satori visual spec emitters, email writers, backup utilities, niche research tools, PPC helpers, and any other agent class.

> North Star: **Schema-First, Rules-First, Single-File, KISS, Complexity-Appropriate.**
> **LLM via PydanticAI exclusively. Models are typed, budgeted fallbacks.** Every program ships with contracts, tests, observability, budgets, versioning, and DEVELOPER-FOCUSED README.

---

## Article 0 — Agent Complexity Tiers

Agents self-declare their complexity tier based on scope and requirements:

### Tier 1: Simple Agents
- **Scope**: <200 lines of code, no external API calls, single responsibility
- **Examples**: formatters, simple classifiers, validators
- **Requirements**: Minimal constitutional compliance
- **Testing**: Basic (1 success, 1 failure test)
- **Documentation**: Essential README sections only

### Tier 2: Standard Agents
- **Scope**: 200-500 lines OR external dependencies OR moderate complexity
- **Examples**: API integrators, multi-step processors, enhanced classifiers
- **Requirements**: Standard constitutional compliance
- **Testing**: Balanced (golden tests, edge cases)
- **Documentation**: Complete README with usage examples

### Tier 3: Critical Agents
- **Scope**: >500 lines OR production revenue impact OR complex business logic
- **Examples**: payment processors, core business logic, enterprise integrations
- **Requirements**: Full constitutional compliance
- **Testing**: Comprehensive (all test types, performance benchmarks)
- **Documentation**: Complete with troubleshooting and architecture notes

---

## Article I — Single-File Python Programs & Agent Organization
- Programs are single `.py` files with a clear CLI entrypoint (`if __name__ == "__main__":`).
- Each agent resides in its own folder: `agents/{agent_name}/{agent_name}.py`
- Agent folders contain: `schemas/`, `tests/`, `examples/`, `docs/`, and **`README.md`** (MANDATORY).
- External dependencies minimized; prefer stdlib: `argparse`, `pathlib`, `json`, `uuid`, `hashlib`, `datetime`, `functools`, `itertools`, `textwrap`, `re`, `shutil`, `subprocess`, `typing`, `logging`, `time`.
- **Required third-party**: **pydantic>=2**, **pydantic-ai** (for ANY LLM functionality).
- **Optional third-party** (must be justified in header docstring): `hypothesis` (if property tests), `httpx` (if HTTP), `tenacity` (if circuit breaker), `pyyaml` (if YAML I/O).

---

## Article II — Contract-First (Typed Models → JSON Schemas)

### All Tiers:
- **Each agent defines Pydantic v2 models in-file**:
  - `MetaModel`, `InputModel`, `OutputModel`, `ErrorModel`, and `Envelope` (`meta`, `input`, `output|None`, `error|None`).
- Inputs may be `application/json` or `text/markdown`. Markdown is normalized to `InputModel` **before** any rules/model calls.

### Tier 2 & 3 Only:
- CI extracts **canonical JSON Schemas** from these models and writes:
  - `schemas/input.json`, `schemas/output.json`, `schemas/envelope.json` (overwrite on build; PR includes diffs).

### **Agent Envelope (typed)** (canonical shape):

```json
{
  "meta": {
    "agent": "string",
    "version": "x.y.z",
    "trace_id": "string",
    "ts": "ISO-8601",
    "brand_token": "string",
    "hash": "sha256",
    "cost": {"tokens_in":0,"tokens_out":0,"usd":0,"llm_calls":0},
    "prompt_id": "string|null",
    "prompt_hash": "sha256|null"
  },
  "input": {},
  "output": {},
  "error": null
}
```

- `meta` fields are forward-compatible; agents MUST ignore unknown meta fields.

---

## Article III — Business Logic Implementation (Complexity-Appropriate)

### Tier 1 (Simple Logic):
- **Direct conditional logic** with clear comments allowed
- **Example**:
  ```python
  # Rule: Story indicators -> classify as story
  if any(word in text.lower() for word in ["plot", "character", "memoir"]):
      return "story"
  # Rule: Instructional indicators -> classify as article
  elif any(word in text.lower() for word in ["how to", "tutorial", "guide"]):
      return "article"
  # Rule: Default fallback
  else:
      return "article"  # Default classification
  ```

### Tier 2 (Moderate Logic):
- **Decision tables for >5 rules** OR multi-criteria decisions
- **Inline decision matrices** acceptable
- Simple conditional logic still allowed for <5 rules

### Tier 3 (Complex Logic):
- **Full decision table infrastructure** with JSON/CSV or inline literal
- **Versioned rules** with audit trail
- Supported operators: `eq`, `in`, `contains`, `gte_lte`; precedence = **first-match** unless `mode:"score_best"`
- Each rule includes human-readable `why`
- **No match → deterministic clarifying response** (typed `ErrorModel`), not a blind model call

---

## Article IV — Input Versatility, Output Consistency
- If `input_content_type == "text/markdown"`, normalize to `InputModel` deterministically (documented in header).
- Output is always `OutputModel` inside the **Envelope** unless the PRD explicitly overrides (e.g., return a PNG path).
- **Multi-output agents** (e.g., standard vs interim responses) use typed unions: `output: StandardOutput | InterimOutput`

---

## Article V — Configuration (Streamlined)

### Two-layer precedence:
1. **Defaults** (in code)
2. **Overrides** (CLI flags > environment variables > config file)

### Required CLI flags:
- `run` (default command)
- `selfcheck`, `print-schemas`, `dry-run`

### Optional CLI flags (based on agent needs):
- `--config FILE` (if configuration needed)
- `--strict` (for LLM-enabled agents)
- `--log-level` (if logging needed)

### **Standard LLM Configuration** (for LLM-enabled agents):
All LLM-enabled agents use these exact configuration keys:

```python
@dataclass
class ModelConfig:
    """Standard model configuration (Constitutional)."""
    enabled: bool = False  # LLM off by default (STRICT mode)
    provider: str = "openai"  # openai|anthropic|gemini|groq|local
    name: str = "gpt-4o-mini"  # Model identifier
    api_key_env: str = "OPENAI_API_KEY"  # Env var with key
    base_url: str | None = None  # For local/custom endpoints
    timeout_s: int = 30
    max_tokens: int = 2000
    temperature: float = 0.1  # Low for consistency
    system_prompt: str | None = None  # Override via config
```

### **Environment Variables** (Standard Pattern):
```bash
# Primary controls
LLM_ENABLED=true|false          # Master switch
AGENT_MODEL_PROVIDER=openai     # Provider selection
AGENT_MODEL_NAME=gpt-4o-mini    # Model selection

# Provider-specific keys (one required based on provider)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GROQ_API_KEY=gsk_...

# Optional overrides
AGENT_MODEL_TIMEOUT_S=30
AGENT_MODEL_MAX_TOKENS=2000
AGENT_MODEL_TEMPERATURE=0.1
```

A clearly marked **CONFIG** section appears near the top (lines ~20–120) with ASCII headers and numbered notes.

---

## Article VI — Documentation & Numbered Flow
- Header docstring includes: purpose, usage examples, accepted `input_content_types`, example Envelope output, **declared budgets**, and dependency pins.
- Major code blocks have **1., 2., 3.** numbered comments describing flow.

---

## Article VII — Type Safety & Defensive Programming (Tier-Appropriate)

### All Tiers:
- Type hints on public functions and classes
- Handle None/empty inputs gracefully
- **Defensive requirements**:
  - All variables initialized before conditionals or have exhaustive else clauses
  - Every `if/elif` chain ends with `else` (even if raising)
  - Guard clauses & early returns to reduce nesting
  - All `Optional` params have explicit `None` checks

### Tier 1:
- `mypy` basic mode acceptable
- Up to 10 `# type: ignore` comments with inline justification

### Tier 2:
- `mypy --strict` required
- Up to 5 `# type: ignore` comments with detailed justification
- **Conditional import patterns allowed**:
  ```python
  try:
      from optional_lib import Feature
      HAS_FEATURE = True
  except ImportError:
      HAS_FEATURE = False
      Feature = Any  # type: ignore[misc]
  ```

### Tier 3:
- `mypy --strict` with zero ignore comments
- Full type coverage including private methods
- Use `typing.assert_never()` for exhaustiveness in `match`
- IDE strict modes (Pyright/Pylance) show zero diagnostics

---

## Article VIII — Testing (Risk-Based, Tier-Appropriate)

### Tier 1 (Minimal Testing):
- **1 success path test** (basic functionality)
- **1 failure case test** (error handling)
- **Coverage ≥ 70%** with branches
- **Runtime < 3s**

### Tier 2 (Balanced Testing):
- **Golden test** (JSON→JSON and/or Markdown→JSON if applicable)
- **Edge cases and boundary conditions**
- **Coverage ≥ 80%** with branches
- **Runtime < 5s**
- **Optional**: Contract tests for schema validation

### Tier 3 (Comprehensive Testing):
- **Golden** tests, **contract** tests, **integration** tests
- **Property-based tests** for complex logic (Hypothesis)
- **Performance benchmarks** and budget compliance
- **Coverage ≥ 90%** with branches
- **Runtime < 10s**
- **Snapshot tests** for large structured outputs

### All Tiers:
- At least one **failure/edge** test (invalid inputs)
- Tests organized in `tests/` with appropriate subdirectories

---

## Article IX — Observability & Events
- **Structured JSONL logs to STDERR** (see Article XVIII). One `agent_run` per execution + per-stage events.
- Agents may publish **AsyncAPI events** where relevant (StoryGenerated, VisualRendered, EmailDrafted, BackupCreated, ResearchSummaryProduced).
- KPI trees roll up daily metrics: runtime, model tokens, $, leads, conversions.

---

## Article X — Model Policy via PydanticAI (STRICT Default)
- `model.enabled = false` by default. Deterministic rules first; **typed model calls only as fallback** when confidence < 0.8.
- **All LLM functionality MUST use PydanticAI exclusively** - no exceptions, no custom integrations.
- **Invocation is strictly typed** via PydanticAI patterns (see Article XXIII).
- **Budgets enforced**: `MAX_TOKENS` (≤2000), `TIMEOUT_S` (≤30), `MAX_RETRIES` (≤1), `MAX_LLM_CALLS` (≤2), `MAX_USD` (≤$0.01) per run.
- **Telemetry**: tokens/cost recorded in `meta.cost`; `model_call` event logged (Article XVIII).

---

## Article XI — LLM Integration via PydanticAI (Mandatory)

### Core Requirement
**ANY agent requiring LLM functionality MUST use PydanticAI exclusively.** No custom LLM integrations, wrappers, or direct API calls allowed.

### Rationale
- **Provider swapping** without code changes via configuration
- **Consistent typing** and validation across all agents
- **Built-in retry logic** and error handling
- **Automatic cost tracking** and budget enforcement
- **Structured output guarantees** with Pydantic validation

### Graceful Degradation Required
```python
# At module level - required pattern
try:
    from pydantic_ai import Agent
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False

# In main flow - required pattern
if config.model.enabled:
    if not PYDANTIC_AI_AVAILABLE:
        logger.warning("PydanticAI not available, falling back to rules")
        return rule_based_fallback(input)

    agent = create_llm_agent(config)
    return await call_llm_with_tracking(agent, input, logger, trace_id)
else:
    return rule_based_processing(input)
```

---

## Article XII — Cost & Performance Budgets

### All Tiers:
- Each program declares budgets in the header docstring: P95 latency and max runtime.

### LLM-Enabled Agents (Additional Requirements):
- **LLM-Specific Budgets** (enforced by PydanticAI and validation):
  ```python
  class CostModel(BaseModel):
      """Constitutional cost limits (enforced)."""
      tokens_in: int = Field(le=1000, description="Max input tokens per call")
      tokens_out: int = Field(le=1000, description="Max output tokens per call")
      usd: float = Field(le=0.01, description="Max USD per request")
      llm_calls: int = Field(le=2, description="Max LLM calls per request")

      @field_validator('llm_calls')
      @classmethod
      def validate_llm_calls(cls, v):
          if v > 2:
              raise ValueError("Constitutional limit: max 2 LLM calls per request")
          return v
  ```

### Tier 2 & 3:
- CI enforces budgets (fail PR if breached)
- Performance benchmarks in test suite

---

## Article XIII — Security, Compliance & Brand
- Programs accept a `brand_token` to shape tone, allowed claims, banned phrases, geo restrictions, reading level.
- Compliance gates run in CI for generated text/visuals.
- **Secrets only from env**; never hardcode or log secrets. Redact in logs.

---

## Article XIV — Governance & Versioning
- Program and schemas follow **SemVer**; schema changes require minor/major bump + CHANGELOG.
- Migrations include baseline tests and verification steps.
- Deviations require an explicit **NOTE** in PR referencing affected Articles.

---

## Article XV — External Resource Access (Ports, Adapters, Fail-Fast)
- Any external system (API, queue, storage) is accessed via an in-file **Port interface** and single **Adapter**; swap vendors via config only.
- **Isolation & resilience**:
  - Preflight config validation → optional healthcheck → tight timeouts (≤5s) → ≤1 retry for idempotent ops with jitter → circuit breaker with cooldown → deterministic fallback returning `ErrorModel`.
- **Security**: env-only secrets; redacted logs; scopes documented.
- **Observability**: per-call STDERR JSONL `port_call` with ms/status/retries/breaker state.
- **Tests**: fake adapter; golden tests for success/timeout/breaker/dry_run; non-idempotent ops = **no retry**.

---

## Article XVI — Prompt Packs & Instructions (for PydanticAI)
- Prompts/instructions must be **config-swappable**:
  - `--prompt` path or `model.prompt_path` (with optional inline `model.prompt_text` default).
  - Files are plain text with `${variable}` placeholders (`string.Template`).
- **Structure**: Header (role), Task, Constraints (**JSON-only schema**), Few-shot (≤2), Rubric.
- Allowed variables documented in header docstring; unresolved variables → fail-fast.
- **Versioning**: each prompt has `prompt_id` + `prompt_hash (sha256)`; both logged and may be stored in `meta`.
- **Testing**:
  - Render test: sample vars → no unresolved placeholders; token count under budget.
  - I/O golden: given prompt variant X, same input → `OutputModel` valid.

---

## Article XVII — Code Quality Gates & Static Analysis

### All Tiers:
- `ruff` (style/fast lint) - must pass
- `black` (format) - must pass

### Tier 1:
- `mypy` basic mode - must pass
- Up to 10 justified `# type: ignore` comments

### Tier 2:
- `mypy --strict` - must pass
- Up to 5 justified `# type: ignore` comments
- `pylint` score ≥ **8.0/10**

### Tier 3:
- `mypy --strict` - must pass with zero ignores
- `pylint` score ≥ **9.5/10**
- `pyright`/Pylance strict (zero errors/warnings)
- `bandit` (no high/medium security issues)
- `vulture` (no dead code)
- `radon` (cyclomatic ≤ 10/function; max nesting ≤ 4; functions ≤ 50 lines excl. docstrings)

### Error handling (All Tiers):
- No bare `except:`
- Raise specific exceptions or `Exception` with justification
- Error messages must be actionable and include context

---

## Article XVIII — Structured Logging Spec (JSONL on STDERR)
- **One `agent_run` per execution**, plus granular events. All logs are single-line JSON with:
  - `ts` (ISO-8601 with ms), `lvl` (`DEBUG|INFO|WARN|ERROR`), `event`, `agent`, `version`, `trace_id`, `span_id`.
- **Event types & required fields**:
  - `agent_run`: `ms`, `bytes_in`, `strict`, `input_content_type`, `rules_source`, `model.enabled`, `outcome: "ok|fallback|error"`.
  - `decision_eval`: `rule_id`, `matched: bool`, `why`, `elapsed_ms`.
  - `model_call`: `provider`, `name`, `tokens_in`, `tokens_out`, `usd`, `duration_ms`, `retry: bool`, `prompt_id`, `prompt_hash`, `ok: bool`, `validation_ok: bool`.
  - `port_call`: `port`, `op`, `status`, `duration_ms`, `retries`, `breaker_state`, `idempotent: bool`.
  - `validation_error`: `schema`, `field`, `message`, `input_excerpt_hash`.
  - `fallback_used`: `reason`, `path` (`rules|model|port`).
- **Privacy**: redact PII/secret-like values; log hashes/excerpts only.
- **Human logs** (optional) go to STDOUT; **machine logs** (these) go to STDERR.

---

## Article XIX — Deterministic Markdown Normalization
- For Markdown inputs, agents define a deterministic parser mapping sections → `InputModel` fields.
- Parser is pure and side-effect free; golden tests include tricky formatting.

---

## Article XX — CLI UX & Self-Check
- Required subcommands: `run` (default), `selfcheck`, `print-schemas`, `dry-run`.
- `selfcheck` validates: env vars present, config parseable, ports reachable in `--healthcheck` mode, budgets sane, schema export works, **PydanticAI availability** (if LLM enabled).
- `print-schemas` dumps current JSON Schemas for `InputModel`, `OutputModel`, `Envelope`.

---

## Article XXI — README.md Requirements (MANDATORY)

**Every agent MUST have a README.md** following the KISS principle and focused on developer experience.

### Structure (Required Sections):
1. **Title & One-line Description** (what the agent does)
2. **Quick Start** (copy-paste example that works)
3. **Usage** (common scenarios with examples)
4. **Configuration** (only if agent needs configuration)
5. **Development** (test/lint commands for contributors)

### Template Requirements:
- **Under 200 lines total**
- **Copy-paste friendly examples**
- **No implementation details** (focus on "how to use")
- **Working bash commands** (tested and verified)

### Basic Template:
```markdown
# Agent Name

One-line description of what this agent does.

## Quick Start

```bash
pip install -r requirements.txt
echo "input content" | python agent_name.py run
```

## Usage

### Basic Example
```bash
python agent_name.py run --input "your content here"
```

### JSON Input
```bash
python agent_name.py run --input-type json << 'EOF'
{"content": "input", "option": "value"}
EOF
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| API_KEY  | Service key | None    |

## Development

```bash
pytest                    # Run tests
mypy agent_name.py       # Type check
python agent_name.py selfcheck  # Validate installation
```
```

### LLM-Enabled Agents (Additional Required Section):
```markdown
## LLM Configuration

This agent supports multiple AI providers via PydanticAI.

### Quick Setup
```bash
# OpenAI (default)
export OPENAI_API_KEY=sk-...
export LLM_ENABLED=true

# Or Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
export AGENT_MODEL_PROVIDER=anthropic
export AGENT_MODEL_NAME=claude-3-haiku

# Or local model
export AGENT_MODEL_PROVIDER=local
export AGENT_MODEL_BASE_URL=http://localhost:8080
```

### Supported Providers
- OpenAI (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
- Anthropic (claude-3-opus, claude-3-sonnet, claude-3-haiku)
- Google (gemini-pro, gemini-flash)
- Groq (mixtral, llama3)
- Local (any OpenAI-compatible endpoint)

### Cost Limits
- Max 2 LLM calls per request
- Max 2000 tokens per call
- Max $0.01 per request
```

---

## Article XXII — Version Compatibility Patterns

Provide standard patterns for handling different Python versions and optional dependencies:

### Python Version Compatibility:
```python
import sys
from typing import Any

# Handle datetime differences
if sys.version_info >= (3, 11):
    from datetime import UTC
else:
    from datetime import timezone
    UTC = timezone.utc

# Handle typing differences
if sys.version_info >= (3, 10):
    from typing import Union
else:
    from typing_extensions import Union
```

### Optional Dependency Patterns:
```python
# Standard pattern for optional imports
try:
    from optional_lib import Feature
    HAS_FEATURE = True
except ImportError:
    HAS_FEATURE = False
    Feature = Any  # type: ignore[misc]

# Usage pattern
if HAS_FEATURE and config.feature_enabled:
    result = Feature().process(input)
else:
    result = fallback_process(input)
```

---

## Article XXIII — PydanticAI Standard Patterns (REQUIRED)

All LLM-enabled agents MUST follow these exact patterns:

### Pattern 1: Agent Factory (Required)
```python
def create_{purpose}_agent(config: Config) -> Agent:
    """Create PydanticAI agent for {purpose}."""
    # Provider string mapping - standardized
    provider_map = {
        "openai": f"openai:{config.model.name}",
        "anthropic": f"anthropic:{config.model.name}",
        "gemini": f"gemini:{config.model.name}",
        "groq": f"groq:{config.model.name}",
        "azure": f"azure:{config.model.name}",
        "local": config.model.base_url or "local",
    }

    model_str = provider_map.get(config.model.provider, f"openai:{config.model.name}")

    return Agent(
        model_str,
        result_type=YourResponseModel,  # Always use typed response
        system_prompt=YOUR_SYSTEM_PROMPT,
        max_retries=1,  # Constitutional limit
        timeout=config.model.timeout_s,
    )
```

### Pattern 2: Typed Response Models (Required)
```python
class LLMResult(BaseModel):
    """All LLM responses MUST be Pydantic models."""
    # Core result field(s)
    result: str | dict[str, Any]  # The actual classification/result

    # Required metadata
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")

    # Optional metadata (recommended)
    reasoning: str | None = Field(default=None, description="Why this result")
    alternatives: list[str] = Field(default_factory=list, description="Other options")
    key_indicators: list[str] = Field(default_factory=list, description="Evidence used")
```

### Pattern 3: Cost-Tracked LLM Calls (Required)
```python
async def call_llm_with_tracking(
    agent: Agent,
    input_text: str,
    logger: logging.Logger,
    trace_id: str,
    config: Config
) -> Any:
    """Standard pattern for tracked LLM calls."""
    start_time = time.time()

    try:
        # Make the call
        result = await agent.run(input_text)

        # Extract cost information (PydanticAI provides this)
        cost = result.cost() if hasattr(result, 'cost') else None
        duration_ms = int((time.time() - start_time) * 1000)

        # Log the call (Constitutional Article XVIII)
        log_event(logger, "model_call",
            trace_id=trace_id,
            provider=config.model.provider,
            name=config.model.name,
            tokens_in=cost.request_tokens if cost else 0,
            tokens_out=cost.response_tokens if cost else 0,
            usd=cost.total_cost if cost else 0.0,
            duration_ms=duration_ms,
            retry=False,
            ok=True,
            validation_ok=True
        )

        return result.data

    except ValidationError as e:
        # One retry with stricter instruction (Constitutional limit)
        logger.warning(f"LLM validation failed, retrying: {e}")

        retry_result = await agent.run(
            input_text,
            extra_prompt="Return ONLY valid JSON matching the exact schema. No additional text."
        )

        # Log retry
        log_event(logger, "model_call",
            trace_id=trace_id,
            provider=config.model.provider,
            retry=True,
            ok=True,
            validation_ok=True
        )

        return retry_result.data

    except Exception as e:
        # Log failure and fallback
        log_event(logger, "model_call",
            trace_id=trace_id,
            provider=config.model.provider,
            ok=False,
            error=str(e)
        )
        raise
```

### Pattern 4: Integration Template (Required)
```python
# Standard integration pattern for main processing function
async def process_with_llm_fallback(
    input_data: InputModel,
    config: Config,
    logger: logging.Logger,
    trace_id: str
) -> OutputModel:
    """Standard pattern: rules first, LLM fallback on low confidence."""

    # 1. Always try rule-based first
    rule_result = apply_rule_based_logic(input_data)

    # 2. Check if LLM fallback needed
    if (rule_result.confidence >= 0.8 or
        not config.model.enabled or
        not PYDANTIC_AI_AVAILABLE):

        # Use rule-based result
        log_event(logger, "decision_eval",
            rule_id="primary_rules",
            matched=True,
            why=f"Confidence {rule_result.confidence:.2f} >= 0.8"
        )
        return rule_result

    # 3. Use LLM fallback
    log_event(logger, "fallback_used",
        reason=f"Low confidence {rule_result.confidence:.2f}",
        path="model"
    )

    agent = create_classification_agent(config)
    llm_result = await call_llm_with_tracking(
        agent, input_data.content, logger, trace_id, config
    )

    # 4. Combine results (keep higher confidence)
    if llm_result.confidence > rule_result.confidence:
        return llm_result
    else:
        return rule_result
```

---

## Definition of Done (DoD) v2.0

A PR is Done only if:

### All Tiers:
1. **Single `.py` file** with header docstring and numbered flow
2. **Pydantic models** defined for input/output/error/envelope
3. **README.md** created following Article XXI template (MANDATORY)
4. **Appropriate testing** for complexity tier (Article VIII)
5. **Code quality** gates pass for tier (Article XVII)
6. **STDERR JSONL** emitted (Article XVIII)
7. **Budgets declared** in header docstring
8. **Control flow complete** (exhaustive conditionals; initialized variables)
9. **Defensive programming** (None/empty/invalid inputs handled)

### LLM-Enabled Agents (Additional):
10. **PydanticAI exclusively** - no custom LLM integrations (Article XI)
11. **Standard patterns** implemented (Article XXIII)
12. **Model disabled by default**, guarded by budgets, fallback on low-confidence
13. **Provider abstraction** via config - test multiple providers
14. **Cost tracking** and budget enforcement working
15. **Graceful degradation** when PydanticAI unavailable

### Tier 2 & 3 (Additional):
16. **JSON Schemas** generated to `schemas/` (Article II)
17. **Decision logic** appropriate for complexity (Article III)

### Tier 3 (Additional):
18. **Comprehensive testing** including property-based (Article VIII)
19. **Performance benchmarks** and CI enforcement
20. **Brand/compliance** checks pass
21. **CHANGELOG** updated if schema or prompt contract changed

---

## Amendment History

- **v2.0.0 (2025-09-21)**: **BREAKING** - Introduced complexity tiers; mandatory PydanticAI for LLM; mandatory README.md; streamlined patterns; conditional requirements based on complexity; improved developer experience.
- **v1.4.0 (2025-09-21)**: **Migrated to Pydantic + PydanticAI**; removed custom LLM adapter; added typed `Envelope`/`ErrorModel`; added Provider Abstraction via PydanticAI; introduced **Article XVIII** structured logging spec; clarified budgets, privacy redaction, and Markdown normalization; tightened DoD.
- v1.3.5 (2025-09-21): Defensive programming tightening; static analysis gates.
- v1.3.4 (2025-09-21): Prompt management policy.
- v1.3.3 (2025-09-21): Single-file mandate; normalization; strict model fallback; budgets & CI gates; brand/compliance; numbered flow; stdlib-first.