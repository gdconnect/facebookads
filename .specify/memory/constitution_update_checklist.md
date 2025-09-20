# Constitution Update Checklist (v1.3.5)

This checklist enforces the Schema-First Empire Python Single-File Constitution (v1.3.5).  
Every PR must check off each relevant item before merging.

---

## Article I — Single-File Python Programs
- [ ] Program implemented in a single `.py` file with `if __name__ == "__main__":`.
- [ ] Stdlib-first; any external deps justified in header docstring.

## Article II — Contract-First (JSON Envelopes)
- [ ] `/schema.input.json` present and valid.
- [ ] `/schema.output.json` present and valid.
- [ ] Program outputs JSON Agent Envelope (meta, input, output, error).
- [ ] Envelope validation in tests/CI.
- [ ] (Optional) `prompt_id` / `prompt_hash` included in meta.

## Article III — Decision Tables & Rules
- [ ] Logic encoded in JSON/CSV/table literal (not scattered `if/else`).
- [ ] Operators limited to `eq`, `in`, `contains`, `gte_lte` (or documented extension).
- [ ] Each rule has a `why` rationale.
- [ ] Deterministic fallback when no rule matches.

## Article IV — Input Versatility, Output Consistency
- [ ] Declared input types supported (JSON and/or Markdown).
- [ ] Markdown normalized to JSON before rules/LLM.
- [ ] Output is JSON in the Agent Envelope unless PRD overrides.

## Article V — Hierarchical Configuration
- [ ] Precedence: defaults → config file → env → CLI flags.
- [ ] CLI supports: `--config`, `--rules`, `--brand-token`, `--strict`, `--log-level`.
- [ ] Config block near top (lines 20–120) with ASCII header.

## Article VI — Documentation & Numbered Flow
- [ ] Header docstring includes purpose, usage examples, input types, example output, and budgets.
- [ ] Major steps annotated with numbered comments (1,2,3…).

## Article VII — Type Safety, Modern Python & Defensive Programming
- [ ] Full type hints everywhere; Python 3.10+ unions.
- [ ] `mypy --strict` passes with 0 errors.
- [ ] Zero IDE warnings (Pylance/PyCharm with strict mode).
- [ ] If pydantic v2 used: `@field_validator` + `ConfigDict`; no deprecations.
- [ ] All variables initialized before conditional blocks OR have exhaustive else clauses.
- [ ] Every if-elif chain has an else clause (even if raising an exception).
- [ ] Guard clauses and early returns used to reduce nesting and complexity.
- [ ] Function parameters with Optional types have explicit None checks.
- [ ] `typing.assert_never()` used for exhaustiveness checking in match/switch statements.
- [ ] Pylance/Pyright "strict" mode enabled in development.

## Article VIII — Testing
- [ ] Golden JSON→JSON test.
- [ ] Golden Markdown→JSON test (if applicable).
- [ ] At least one failure/edge case test.
- [ ] Snapshot tests for non-deterministic outputs.
- [ ] Test runtime < 5s.
- [ ] Contract tests validate envelope and schemas.
- [ ] All code paths including error branches tested.
- [ ] Tests with None/empty/invalid inputs included.
- [ ] Boundary conditions and edge cases tested.
- [ ] Code coverage ≥ 80% with all branches tested.
- [ ] Property-based tests for complex logic (using `hypothesis` if justified).

## Article IX — Observability & Events
- [ ] STDERR JSONL includes: event, agent, version, trace_id, ms, bytes_in, strict, input_content_type, provider, and (if applicable) prompt_id/hash.
- [ ] AsyncAPI events emitted where relevant (StoryGenerated, VisualRendered, EmailDrafted, BackupCreated, ResearchSummaryProduced).
- [ ] Metrics feed daily KPI rollups.

## Article X — LLM Policy (STRICT Default)
- [ ] `llm.enabled=false` by default.
- [ ] LLM used only when deterministic confidence < 0.8.
- [ ] Prompts schema-bound; JSON-only response rule enforced.
- [ ] Budgets enforced: MAX_TOKENS, TIMEOUT_S, MAX_RETRIES (≤1).
- [ ] Post-processing validates JSON; one retry with explicit hints; deterministic fallback on failure.
- [ ] Token/cost telemetry logged.

## Article XI — Provider Abstraction
- [ ] Single in-file adapter (`call_llm(cfg, prompt)`) routes to OpenAI/Anthropic/Gemini/Local.
- [ ] Config keys supported: provider, base_url, path, model, api_key_env, timeout_s, max_tokens, temperature, top_p, headers.
- [ ] Provider/base_url can be changed without code edits (config only).

## Article XII — Cost & Performance Budgets
- [ ] Header docstring declares P95 latency, token/word budget, retries, max $/task.
- [ ] CI fails if budgets exceeded.
- [ ] Deterministic templates preferred where possible.

## Article XIII — Security, Compliance & Brand
- [ ] `brand_token` defines tone, allowed claims, banned phrases, geo restrictions, reading level.
- [ ] Compliance checks run in CI for generated artifacts.
- [ ] Secrets only via env; logs redacted.

## Article XIV — Governance & Versioning
- [ ] Program + schemas follow SemVer; CHANGELOG updated.
- [ ] Schema changes include migration notes and baseline tests.
- [ ] Deviations justified in PR referencing Articles.

## Article XV — External Resource Access (Ports/Adapters/Fail-Fast)
- [ ] Port interface + single adapter per resource; core depends on Port only.
- [ ] Config keys documented: base_url, path, api_key_env, timeout_s, max_retries, backoff_ms, jitter_ms, circuit_threshold, circuit_cooldown_s, headers, scopes[], dry_run.
- [ ] Preflight validation; (optional) lightweight healthcheck.
- [ ] Tight timeouts (≤5s); ≤1 retry for idempotent calls with jitter backoff.
- [ ] Circuit breaker with cooldown; STDERR `port_call` logs include ms/status/retries/breaker state.
- [ ] Dry-run deterministic; secrets via env; logs redacted.
- [ ] Goldens: success / timeout / breaker / dry-run / non-idempotent no-retry.

## Article XVI — Prompt Management & Evolution
- [ ] Prompt swappable via config (`--prompt` / `llm.prompt_path`); default in-file prompt present.
- [ ] Placeholders validated (no unresolved variables); allowed variable list documented.
- [ ] `prompt_id` and `prompt_hash` logged (and optionally present in meta).
- [ ] Injection-hardening clauses present (JSON-only; no backticks; ignore instruction changes in user content).
- [ ] Secrets/PII redacted from prompt variables; prompt text not logged by default.
- [ ] Golden prompt-render test passes (under token budget).
- [ ] Golden I/O test passes for chosen prompt variant; snapshot baseline acknowledged when updated.
- [ ] A/B variant supported via `llm.prompt_variant`; variant logged.
- [ ] Budgets respected; deterministic fallback on breach.

## Article XVII — Code Quality Gates & Static Analysis
- [ ] `pylint` passes with score ≥ 9.5/10.
- [ ] `pyright` or Pylance in strict mode (zero errors/warnings).
- [ ] `bandit` security scan passes (no high/medium issues).
- [ ] `vulture` dead code detection passes.
- [ ] Cyclomatic complexity ≤ 10 per function (enforced via `radon`).
- [ ] Maximum nesting depth ≤ 4 levels.
- [ ] Functions ≤ 50 lines (excluding docstrings).
- [ ] All variables initialized before use.
- [ ] No implicit globals (explicit `global` keyword if needed).
- [ ] No shadowing of built-in names.
- [ ] Consistent naming conventions (snake_case for functions/variables, PascalCase for classes).
- [ ] No bare `except:` clauses.
- [ ] All exceptions specific or use `Exception` with justification.
- [ ] Error messages actionable and include context.
- [ ] Structured logging with levels (DEBUG, INFO, WARNING, ERROR).

---

**DoD (must all be true before merge):**
single-file + docs + numbered flow • schemas present/validated • rules ≥80% with rationale • tests (golden/failure/snapshot) <5s • ruff/black/mypy strict clean • STDERR JSONL • STRICT LLM default + provider swap by config • budgets enforced • ports/adapters fail-fast if external • prompt swappable + id/hash logged + prompt tests • brand/compliance pass • CHANGELOG updated when schemas/prompts change • static analysis tools pass (pylint ≥9.5, pyright strict, bandit, vulture) • control flow complete (all if-elif have else, variables initialized) • defensive programming tests pass (None/empty/invalid inputs) • code coverage ≥80% with branch coverage.
