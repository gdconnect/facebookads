# Constitution Update Checklist (v1.4.0 — PydanticAI Edition)

This checklist enforces the Schema-First Empire Python Single-File Constitution (v1.4.0).
Every PR must check off each relevant item before merging.

---

## Article I — Single-File Python Programs
- [ ] Program implemented in a single `.py` file with `if __name__ == "__main__":`.
- [ ] Stdlib-first; any external deps justified in header docstring.
- [ ] Allowed 3rd-party libs limited to: `pydantic>=2`, `pydantic-ai`, `hypothesis` (if property tests), `httpx` (if HTTP), `tenacity` (if breaker), `pyyaml` (if YAML).

## Article II — Contract-First (Typed Models → JSON Schemas)
- [ ] Envelope defined via Pydantic models (`MetaModel`, `InputModel`, `OutputModel`, `ErrorModel`, `Envelope`).
- [ ] JSON Schemas auto-exported to `schemas/input.json`, `schemas/output.json`, `schemas/envelope.json`.
- [ ] Program outputs typed Envelope (`meta`, `input`, `output|null`, `error|null`).
- [ ] Envelope validation in tests/CI.
- [ ] `prompt_id` / `prompt_hash` optional but supported.

## Article III — Decision Tables & Rules
- [ ] Logic encoded in JSON/CSV/table literal parsed into `DecisionRule` model.
- [ ] Operators limited to `eq`, `in`, `contains`, `gte_lte`.
- [ ] Each rule includes `why` rationale.
- [ ] Deterministic fallback (`ErrorModel`) if no rule matches.

## Article IV — Input Versatility, Output Consistency
- [ ] Declared input types supported (JSON and/or Markdown).
- [ ] Markdown normalized deterministically to `InputModel`.
- [ ] Output is always `OutputModel` in Envelope unless PRD override.

## Article V — Hierarchical Configuration
- [ ] Precedence: defaults → config file → env → CLI flags.
- [ ] CLI supports: `--config`, `--rules`, `--brand-token`, `--strict`, `--log-level`.
- [ ] Config parsed via `ConfigModel` with env binding.
- [ ] Config section placed near top (lines ~20–120) with ASCII header.

## Article VI — Documentation & Numbered Flow
- [ ] Header docstring includes: purpose, usage examples, input types, example Envelope, budgets, deps.
- [ ] Major steps annotated with numbered comments (1,2,3…).

## Article VII — Type Safety & Defensive Programming
- [ ] Full type hints everywhere.
- [ ] `mypy --strict` passes with 0 errors.
- [ ] IDE strict mode (Pyright/Pylance) passes with 0 errors/warnings.
- [ ] Pydantic v2 only (`@field_validator`, `ConfigDict`).
- [ ] All vars initialized before conditionals OR exhaustive else clauses.
- [ ] Every `if/elif` chain ends with `else`.
- [ ] Guard clauses/early returns reduce nesting.
- [ ] Optional params explicitly checked for `None`.
- [ ] `typing.assert_never()` used for exhaustiveness in `match`.

## Article VIII — Testing
- [ ] Golden JSON→JSON test.
- [ ] Golden Markdown→JSON test (if applicable).
- [ ] At least one failure/edge test.
- [ ] Snapshot tests for large or non-deterministic outputs.
- [ ] Test runtime < 5s.
- [ ] Contract tests validate schemas and Envelope.
- [ ] All code paths (success + error) tested.
- [ ] Tests include None/empty/invalid inputs.
- [ ] Boundary/edge conditions covered.
- [ ] Code coverage ≥ 80% with branches.
- [ ] Property-based tests for complex logic (if justified).

## Article IX — Observability & Events
- [ ] STDERR JSONL logs include required fields per Article XVIII.
- [ ] `agent_run` + per-stage events emitted.
- [ ] AsyncAPI events published where relevant.
- [ ] Metrics feed daily KPI rollups.

## Article X — Model Policy via PydanticAI
- [ ] `model.enabled=false` by default.
- [ ] Models only used when deterministic confidence < 0.8.
- [ ] Responses parsed into `OutputModel` by PydanticAI.
- [ ] One retry max on validation failure; else deterministic fallback.
- [ ] Budgets enforced: MAX_TOKENS, TIMEOUT_S, MAX_RETRIES ≤1, MAX_USD.
- [ ] Telemetry logged to `meta.cost` and STDERR.

## Article XI — Provider Abstraction (via PydanticAI)
- [ ] Model invocation uses PydanticAI runner inside single file.
- [ ] Config keys supported: `enabled`, `provider`, `base_url`, `path`, `name`, `api_key_env`, `timeout_s`, `max_tokens`, `temperature`, `top_p`, `extra_headers`.
- [ ] Provider/endpoint switchable via config only.

## Article XII — Cost & Performance Budgets
- [ ] Header docstring declares budgets (P95 latency, token/word, retries, max $/task).
- [ ] CI fails if exceeded.
- [ ] Deterministic rules/templates preferred.

## Article XIII — Security, Compliance & Brand
- [ ] `brand_token` defines tone, claims, banned phrases, geo restrictions, reading level.
- [ ] Compliance checks in CI.
- [ ] Secrets only from env; logs redact secrets/PII.

## Article XIV — Governance & Versioning
- [ ] Program + schemas follow SemVer.
- [ ] CHANGELOG updated.
- [ ] Schema changes include migrations + tests.
- [ ] Deviations justified in PR referencing Articles.

## Article XV — External Resource Access
- [ ] External systems accessed via in-file Port + Adapter.
- [ ] Preflight validation + optional healthcheck.
- [ ] Tight timeouts (≤5s).
- [ ] ≤1 retry for idempotent ops with jitter.
- [ ] Circuit breaker with cooldown + structured fallback.
- [ ] STDERR `port_call` logs include ms/status/retries/breaker.
- [ ] Secrets from env only; logs redacted.
- [ ] Golden tests: success/timeout/breaker/dry_run; non-idempotent ops = no retry.

## Article XVI — Prompt Packs & Instructions
- [ ] Prompts/instructions swappable via config (`--prompt` or `model.prompt_path`).
- [ ] Default inline prompt present.
- [ ] Variables validated; unresolved placeholders fail-fast.
- [ ] `prompt_id` and `prompt_hash` logged and stored in meta.
- [ ] Injection hardening present (JSON-only, no backticks, ignore instruction-change).
- [ ] Secrets/PII redacted from variables.
- [ ] Golden render test passes under token budget.
- [ ] Golden I/O test passes for prompt variant.
- [ ] A/B supported via `model.prompt_variant`; variant logged.

## Article XVII — Code Quality Gates & Static Analysis
- [ ] `ruff` + `black` pass.
- [ ] `mypy --strict` passes.
- [ ] `pylint` score ≥ 9.5/10.
- [ ] `pyright`/Pylance strict mode passes.
- [ ] `bandit` passes (no high/medium issues).
- [ ] `vulture` shows no dead code.
- [ ] `radon`: cyclomatic ≤10, nesting ≤4, functions ≤50 lines.
- [ ] No bare `except:`.
- [ ] Exceptions are specific or justified.
- [ ] Error messages actionable/contextual.

## Article XVIII — Structured Logging Spec
- [ ] STDERR JSONL includes: ts, lvl, event, agent, version, trace_id, span_id.
- [ ] Event types covered: `agent_run`, `decision_eval`, `model_call`, `port_call`, `validation_error`, `fallback_used`.
- [ ] Privacy respected (secrets redacted; hashes/excerpts only).
- [ ] Human-readable logs (optional) go to STDOUT only.

## Article XIX — Markdown Normalization
- [ ] Deterministic Markdown parser maps sections → `InputModel`.
- [ ] Parser is pure and side-effect free.
- [ ] Golden tests include tricky formatting cases.

## Article XX — CLI UX & Self-Check
- [ ] CLI supports: `run`, `selfcheck`, `print-schemas`, `dry-run`.
- [ ] `selfcheck` validates env, config, ports (if `--healthcheck`), budgets, schema export.
- [ ] `print-schemas` dumps JSON Schemas for `InputModel`, `OutputModel`, `Envelope`.

---

**DoD (must all be true before merge):**
single-file + docs + numbered flow • Pydantic models + schemas exported • rules ≥80% with rationale • tests (golden/failure/snapshot) <5s • coverage ≥80% • ruff/black/mypy strict clean • pylint ≥9.5 • pyright strict • bandit/vulture/radon pass • STDERR JSONL (Article XVIII) • PydanticAI disabled by default + budget-guarded fallback • budgets enforced • ports/adapters fail-fast tested • prompts swappable + id/hash logged + prompt tests • brand/compliance pass • CHANGELOG updated when schemas/prompts change • control flow complete • defensive programming tests pass.
