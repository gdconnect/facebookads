# Schema-First Empire — Python Single-File Constitution (PydanticAI Edition)

**Version:** 1.4.0
**Ratified:** 2025-09-21
**Scope:** All **Python programs** in this repository MUST be implemented as **single-file agents** (`.py`).
Applies to storytelling, Satori visual spec emitters, email writers, backup utilities, niche research tools, PPC helpers, and any other agent class.

> North Star: **Schema-First, Rules-First, Single-File, KISS.**
> **Models are typed, budgeted fallbacks** orchestrated via **PydanticAI**. Every program ships with contracts, tests, observability, budgets, and versioning.

---

## Article I — Single-File Python Programs & Agent Organization
- Programs are single `.py` files with a clear CLI entrypoint (`if __name__ == "__main__":`).
- Each agent resides in its own folder: `agents/{agent_name}/{agent_name}.py`
- Agent folders contain: `schemas/`, `tests/`, `examples/`, `docs/`, and `README.md`.
- External dependencies minimized; prefer stdlib: `argparse`, `pathlib`, `json`, `uuid`, `hashlib`, `datetime`, `functools`, `itertools`, `textwrap`, `re`, `shutil`, `subprocess`, `typing`, `logging`, `time`.
- Allowed third-party (must be justified in header docstring): **pydantic>=2**, **pydantic-ai** (PydanticAI), `hypothesis` (if property tests), `httpx` (if HTTP), `tenacity` (if circuit breaker), `pyyaml` (if YAML I/O).

---

## Article II — Contract-First (Typed Models → JSON Schemas)
- **Each agent defines Pydantic v2 models in-file**:
  - `MetaModel`, `InputModel`, `OutputModel`, `ErrorModel`, and `Envelope` (`meta`, `input`, `output|None`, `error|None`).
- CI extracts **canonical JSON Schemas** from these models and writes:
  - `schemas/input.json`, `schemas/output.json`, `schemas/envelope.json` (overwrite on build; PR includes diffs).
- Inputs may be `application/json` or `text/markdown`. Markdown is normalized to `InputModel` **before** any rules/model calls.
- **Agent Envelope (typed)** (canonical shape):

  ```json
  {
    "meta": {
      "agent": "string",
      "version": "x.y.z",
      "trace_id": "string",
      "ts": "ISO-8601",
      "brand_token": "string",
      "hash": "sha256",
      "cost": {"tokens_in":0,"tokens_out":0,"usd":0},
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

## Article III — Decision Tables & Rules (Before Any Model Call)
- Business logic is implemented with **decision tables** (JSON/CSV or inline literal), parsed into a typed `DecisionRule` model.
- Supported operators: `eq`, `in`, `contains`, `gte_lte`; precedence = **first-match** unless `mode:"score_best"`.
- Each rule includes human-readable `why`.
- **No match → deterministic clarifying response** (typed `ErrorModel`), not a blind model call.

---

## Article IV — Input Versatility, Output Consistency
- If `input_content_type == "text/markdown"`, normalize to `InputModel` deterministically (documented in header).
- Output is always `OutputModel` inside the **Envelope** unless the PRD explicitly overrides (e.g., return a PNG path).

---

## Article V — Hierarchical Configuration (Typed)
- Precedence: sensible defaults → config file → env vars → CLI flags.
- Required CLI flags (where applicable): `--config`, `--rules`, `--brand-token`, `--strict`, `--log-level`.
- A clearly marked **CONFIG** section appears near the top (lines ~20–120) with ASCII headers and numbered notes.
- Config is parsed via a Pydantic `ConfigModel` with env binding (e.g., `model_config = SettingsConfigDict(env_prefix="AGENT_")`).

---

## Article VI — Documentation & Numbered Flow
- Header docstring includes: purpose, usage examples, accepted `input_content_types`, example Envelope output, **declared budgets**, and dependency pins.
- Major code blocks have **1., 2., 3.** numbered comments describing flow.

---

## Article VII — Type Safety & Defensive Programming
- Full type hints on all functions/classes; `mypy --strict` passes with zero errors.
- No Pydantic v1 APIs; use `@field_validator` and `ConfigDict`.
- **Defensive requirements**:
  - All variables initialized before conditionals or have exhaustive else clauses.
  - Every `if/elif` chain ends with `else` (even if raising).
  - Guard clauses & early returns to reduce nesting.
  - All `Optional` params have explicit `None` checks.
  - Use `typing.assert_never()` for exhaustiveness in `match`.
  - IDE strict modes (Pyright/Pylance) show zero diagnostics.

---

## Article VIII — Testing & Agent Test Organization
- Per-agent `tests/` with `contract/`, `integration/`, `golden/`.
- At least one **golden JSON→JSON** and one **Markdown→JSON** (if applicable).
- At least one **failure/edge** test (invalid inputs).
- Snapshot tests for large structured outputs.
- Contract tests validate generated **schemas** and **Envelope**.
- Coverage ≥ **80%** with branches; runtime of full suite < **5s**.
- Property-based tests (Hypothesis) for complex rules, **if justified**.

---

## Article IX — Observability & Events
- **Structured JSONL logs to STDERR** (see Article XVIII). One `agent_run` per execution + per-stage events.
- Agents may publish **AsyncAPI events** where relevant (StoryGenerated, VisualRendered, EmailDrafted, BackupCreated, ResearchSummaryProduced).
- KPI trees roll up daily metrics: runtime, model tokens, $, leads, conversions.

---

## Article X — **Model Policy via PydanticAI (STRICT Default Off)**
- `model.enabled = false` by default. Deterministic rules first; **typed model calls only as fallback** when confidence < 0.8.
- **Invocation is strictly typed**:
  - PydanticAI parses model response into `OutputModel` (or a dedicated intermediate) – invalid JSON raises and is caught.
  - On validation error: **one retry max** with stricter system instruction; else deterministic fallback (`ErrorModel`).
- **Budgets enforced**: `MAX_TOKENS`, `TIMEOUT_S`, `MAX_RETRIES` (≤1), `MAX_USD` per run.
- **Telemetry**: tokens/cost recorded in `meta.cost`; `model_call` event logged (Article XVIII).
- Prompts must be **schema-bound** and compact; “JSON-only, no backticks, null if unknown” constraints are required.

---

## Article XI — Provider & Transport Abstraction (via PydanticAI)
- All model calls **go through PydanticAI** agent/runner creation **inside the single file**.
- Config keys (typed in `ConfigModel`):
  - `model.enabled: bool`
  - `model.provider: Literal["openai","anthropic","azure","gemini","local"]`
  - `model.base_url: str|None` (supports self-hosted/local)
  - `model.path: str|None` (optional route override)
  - `model.name: str` (e.g., `gpt-4.1`, `claude-3.5`…)
  - `model.api_key_env: str` (env var name storing the key)
  - `model.timeout_s: int`
  - `model.max_tokens: int`
  - `model.temperature: float`
  - `model.top_p: float|None`
  - `model.extra_headers: dict[str,str]|None`
- Switching providers/endpoints is **config-only**; no code edits.

---

## Article XII — Cost & Performance Budgets
- Each program declares budgets in the header docstring: P95 latency, token/word budget, max retries, and max $/task.
- CI enforces budgets (fail PR if breached).
- Prefer deterministic templates and rules over model paths.

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
- Tools:
  - `ruff` (style/fast lint)
  - `black` (format)
  - `mypy --strict` (types; zero errors)
  - `pylint` score ≥ **9.5/10**
  - `pyright`/Pylance strict (zero errors/warnings)
  - `bandit` (no high/medium)
  - `vulture` (no dead code)
  - `radon` (cyclomatic ≤ 10/function; max nesting ≤ 4; functions ≤ 50 lines excl. docstrings)
- Error handling:
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
- `selfcheck` validates: env vars present, config parseable, ports reachable in `--healthcheck` mode, budgets sane, schema export works.
- `print-schemas` dumps current JSON Schemas for `InputModel`, `OutputModel`, `Envelope`.

---

## Definition of Done (DoD)
A PR is Done only if:
1. Single `.py` file with header docstring and numbered flow.
2. Pydantic models defined; JSON Schemas generated to `schemas/` in CI.
3. Decision table covers ≥80% cases with rationale.
4. Tests: golden + failure + (if needed) snapshot; runtime < 5s; coverage ≥ 80% (branches).
5. `ruff`, `black`, `mypy --strict`, `pylint≥9.5`, `pyright` strict, `bandit`, `vulture`, `radon` all pass.
6. STDERR JSONL emitted (Article XVIII); KPI events wired where relevant.
7. **Model path** via PydanticAI is **disabled by default**, guarded by budgets, and only invoked on low-confidence.
8. Budgets declared and enforced; CI green.
9. For resource access: port/adapter + fail-fast + breaker tests.
10. For model use: prompts swappable via config; `prompt_id`/`prompt_hash` logged; golden render & I/O tests pass.
11. Brand/compliance checks pass.
12. CHANGELOG updated if schema or prompt contract changed.
13. Control flow complete (exhaustive conditionals; initialized variables).
14. Defensive programming tests pass (None/empty/invalid inputs handled).

---

## Amendment History
- **v1.4.0 (2025-09-21)**: **Migrated to Pydantic + PydanticAI**; removed custom LLM adapter; added typed `Envelope`/`ErrorModel`; added Provider Abstraction via PydanticAI; introduced **Article XVIII** structured logging spec; clarified budgets, privacy redaction, and Markdown normalization; tightened DoD.
- v1.3.5 (2025-09-21): Defensive programming tightening; static analysis gates.
- v1.3.4 (2025-09-21): Prompt management policy.
- v1.3.3 (2025-09-21): Single-file mandate; normalization; strict model fallback; budgets & CI gates; brand/compliance; numbered flow; stdlib-first.
