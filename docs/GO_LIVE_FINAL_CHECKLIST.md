# GO_LIVE_FINAL_CHECKLIST.md
## Qwen-Only Audiobook Pipeline — Production Go-Live

**Authority:** This document is the single paste-ready go-live gate for the Qwen-Only Audiobook Comparator Loop pipeline. All 10 items must be green before promotion to production. Sign-off fields are required.

**Scope:** Qwen draft → Comparator/Judge → repair loop → pass or manual_review. No Claude at runtime. No human in the repair loop.

**Key design decisions locked in this doc:**
- max_loops: config-driven (default 3, schema max 5) — see `comparator_config.yaml > loop_control`
- Aggregate pass: all hard gates pass **AND** scored_total/max_scored_total ≥ 0.75 (locale-overridable)
- TTS readability: **hard gate** (unshippable audiobook content = hard fail)
- Judge model: Qwen-max, temperature 0.1, rotated seed, separate system prompt — committed, not open
- Patch injection: **fully automated** via `PatchApplier`; hard gate patches first; never reviewed by human
- Parallel sections: `asyncio.Semaphore(max_parallel_sections=6)`; config-driven
- Manual review: best-scoring draft + full defect history written to packet; `manual_review_queue.json` for UI visibility
- Schema binding: `comparator_result_v2.schema.json` `schema_version=2.0` must match checklist `schema_version=2.0`

---

## ITEM 1 — Go-Live Freeze + Rollback

**Requirement:** Tag the release commit. One-command rollback tested and documented.

**Actions:**
- [ ] Tag commit: `git tag audiobook-pipeline-v2.0.0 <sha>`
- [ ] Push tag: `git push origin audiobook-pipeline-v2.0.0`
- [ ] Rollback script exists and is tested: `scripts/release/audiobook_rollback.sh`
  - Rollback reverts: `scripts/audiobook_script/`, `config/audiobook_script/`, `schemas/comparator_result_v2.schema.json`
  - Rollback re-enables previous pipeline variant if applicable
- [ ] One-page rollback runbook in `docs/audiobook_rollback_runbook.md`
- [ ] Rollback tested in staging environment (not just written)

**Artifact:** `scripts/release/audiobook_rollback.sh` + `docs/audiobook_rollback_runbook.md`
**Sign-off:** _____________________ Date: _____________

---

## ITEM 2 — Required CI Checks Enforced

**Requirement:** Ruleset enforces all required checks on `main` branch before merge. No bypass paths.

**Checks that must be required (not optional):**
- [ ] Core tests pass (pytest)
- [ ] EI V2 gates pass
- [ ] Change impact check passes (`.github/workflows/change-impact.yml`)
- [ ] DOCS_INDEX governance passes (`check_docs_governance.py --check-inventory`)
- [ ] Audiobook schema validation: `python scripts/audiobook_script/run_comparator_loop.py --dry-run`

**Verify:** GitHub branch protection → `main` → Required status checks includes all of the above.

**Artifact:** GitHub Settings → Branches → `main` ruleset screenshot or export.
**Sign-off:** _____________________ Date: _____________

---

## ITEM 3 — Comparator Loop Safety Caps

**Requirement:** Loop count is config-driven (not hardcoded). Schema enforces range. Hard-gate failure after max_loops → manual_review only; auto-pass is architecturally impossible.

**Verification steps:**
- [ ] `comparator_config.yaml > loop_control > max_loops` is set (default 3)
- [ ] `run_comparator_loop.py` validates `max_loops in [1, 5]` on startup and raises `ValueError` if violated
- [ ] Code review confirms: no `auto_pass` path exists anywhere in `run_comparator_loop.py`
- [ ] Test: run a section that fails all loops → verify it writes `manual_review` decision to `manual_review_queue.json` and does NOT write a passed draft
- [ ] Test: set `max_loops=6` in config → verify startup raises `ValueError` before any API call

**Artifact:** Test run output + code review confirmation.
**Sign-off:** _____________________ Date: _____________

---

## ITEM 4 — Judge Quality Controls

**Requirement:** Judge output is JSON-schema validated on every loop pass. Schema version binding enforced. Schema fail → manual_review; never silent pass. Judge independence is committed.

**Judge independence (committed, not open):**
- Model: `qwen-max` (same family as draft; independence via config)
- System prompt: `judge_audiobook_v2.txt` (separate from `draft_audiobook_v2.txt`)
- Temperature: `0.1` (near-deterministic; reproducible verdicts)
- Seed: rotated per loop — `hash(section_id + loop_index + "JUDGE_SALT_V2")`
- API endpoint: separate API key from draft model (see secrets config)

**Verification steps:**
- [ ] `schemas/comparator_result_v2.schema.json` exists and schema_version=2.0 binds to checklist schema_version=2.0
- [ ] `checklist_schema_version` field is validated on every gate result in `_validate_judge_output()`
- [ ] Test: inject malformed JSON from judge → verify section routes to `manual_review`, no exception leaks
- [ ] Test: inject valid JSON but with `checklist_schema_version: "1.0"` → verify schema mismatch routes to `manual_review`
- [ ] Test: inject valid JSON with wrong `gate_id` → verify schema validation fails cleanly
- [ ] Judge config in `comparator_config.yaml > judge_model` is committed (temperature, seed_strategy, system_prompt_id)
- [ ] Separate API key for judge model is in GitHub Secrets / local env (not in any repo file)

**Artifact:** Test output for all three failure injection tests.
**Sign-off:** _____________________ Date: _____________

---

## ITEM 5 — Golden Regression Gate

**Requirement:** Fixed multilingual golden set. Block promotion if fidelity/compliance hard-gate pass rate drops below 100% or scored pass rate drops below 90% on golden set.

**Golden set requirements:**
- [ ] `config/audiobook_script/golden_regression_set/` exists and contains sections for: zh-TW, zh-HK, zh-SG, zh-CN (minimum); ja-JP and ko-KR (optional)
- [ ] Each golden section has: English source, expected decision (pass), expected hard-gate verdicts
- [ ] Regression test script exists: `scripts/audiobook_script/run_regression.py --golden-set config/audiobook_script/golden_regression_set/`
- [ ] CI runs regression on every PR that touches: `scripts/audiobook_script/`, `config/audiobook_script/`, `schemas/`, `prompts/`
- [ ] CI blocks merge if hard-gate pass rate < 100% or scored pass rate < 90% on golden set

**Config reference:** `comparator_config.yaml > regression`

**Artifact:** Golden set directory + CI workflow entry + first baseline run output.
**Sign-off:** _____________________ Date: _____________

---

## ITEM 6 — Observability + Incident Hooks

**Requirement:** JSONL decision log per loop. Alert when manual_review rate or hard-gate fail rate exceeds threshold.

**Implementation:**
- [ ] `artifacts/audiobook/loop_decisions.jsonl` written on every loop pass (appended, never overwritten)
- [ ] Each JSONL record contains: `ts`, `run_id`, `section_id`, `locale`, `loop_index`, `decision`, `aggregate_score`, `hard_gates_passed`
- [ ] Alert fires when `manual_review_rate > 0.10` (configurable in `comparator_config.yaml > observability`)
- [ ] Alert fires when `hard_gate_fail_rate > 0.05` (configurable)
- [ ] Alert channel configured: `ops_webhook` or equivalent (see `comparator_config.yaml > observability > alert_channel`)
- [ ] `artifacts/audiobook/manual_review_queue.json` is the high-visibility UI feed — PhoenixControl "Manual Review" tab reads this file sorted by `hard_gate_failures` descending

**PhoenixControl UI requirement:**
- [ ] "Manual Review Queue" tab exists in PhoenixControl and reads `manual_review_queue.json`
- [ ] Queue is sorted: most hard gate failures first (highest severity at top)
- [ ] Each queue entry shows: section_id, locale, book_id, hard_gate_failures, best_aggregate_score, loops_attempted, packet_path link

**Artifact:** Screenshot of PhoenixControl Manual Review tab with at least one test entry.
**Sign-off:** _____________________ Date: _____________

---

## ITEM 7 — Cost / Rate Protection

**Requirement:** Per-section and per-batch token caps. Automatic stop when budget exceeded. No silent overrun.

**Token budget (from `comparator_config.yaml > token_budget`):**
- [ ] `max_tokens_per_section_per_loop: 6000` (draft + judge combined)
- [ ] `max_tokens_per_section_total: 20000` (across all loops)
- [ ] `max_tokens_per_batch: 2000000` (full catalog batch safety cap)
- [ ] Budget exceeded → section routes to `manual_review` (never silent overrun)

**Rate protection:**
- [ ] `max_parallel_sections` set based on verified API rate limits for the Qwen Cloud tier in use
- [ ] `max_parallel_books` set conservatively (default 2) to prevent cross-book rate spikes
- [ ] `section_timeout_seconds` and `batch_timeout_seconds` set and tested

**Estimated costs documented:**
- ~2,000 tokens/section (source) + ~1,500 (draft) + ~500 (judge) ≈ 4,000 tokens/loop
- 3 loops × 4,000 ≈ 12,000 tokens/section
- Full audiobook (20 sections) ≈ 240,000 tokens
- Full catalog batch (N books × 20 sections) estimated: _____ tokens (fill in before go-live)

**Artifact:** Token budget config verified + cost estimate for target batch size.
**Sign-off:** _____________________ Date: _____________

---

## ITEM 8 — Secrets Hygiene

**Requirement:** All API keys and credentials out of repo files. GitHub Secrets or local env only. Verified clean.

**Checklist:**
- [ ] Qwen Cloud API key (draft model): in GitHub Secret `QWEN_DRAFT_API_KEY` / local env only
- [ ] Qwen Cloud API key (judge model): in GitHub Secret `QWEN_JUDGE_API_KEY` / local env only (separate from draft)
- [ ] No API keys in any `.yaml`, `.rtf`, `.py`, `.json`, or `.md` file in the repo
- [ ] Run `git grep -i "api_key\|sk-\|dashscope"` and verify no secrets found in tracked files
- [ ] `config/audiobook_script/comparator_config.yaml` references `secrets config` for API endpoints — does NOT contain keys
- [ ] `.gitignore` includes any local env files that might contain keys

**Artifact:** `git grep` output showing clean. GitHub Secrets screenshot showing both keys present.
**Sign-off:** _____________________ Date: _____________

---

## ITEM 9 — Evidence Pack Complete

**Requirement:** One document with run URLs, artifact paths, timestamps, and go/no-go sign-offs for the staging validation run.

**Required evidence:**
- [ ] Staging run ID: _____________________
- [ ] Staging run timestamp (UTC): _____________________
- [ ] Staging batch summary path: `artifacts/audiobook/<batch_id>/batch_summary.json`
- [ ] Staging pass rate: _____ / _____ sections passed
- [ ] Staging manual_review count: _____
- [ ] Golden regression run output (all locales): pass rate _____ / _____
- [ ] CI run URL (all checks green): _____________________
- [ ] Any open issues discovered in staging and their disposition: _____________________

**Format:** Paste this evidence pack into a single `docs/audiobook_go_live_evidence_<date>.md` file and link it here.

**Evidence pack link:** _____________________
**Sign-off:** _____________________ Date: _____________

---

## ITEM 10 — Operator Runbook ("What to Do When Red")

**Requirement:** One-page runbook for each gate type that can turn red. On-call operator must be able to act without finding the author.

**Runbook entries required:**

| Gate / Scenario | Symptom | First action | Escalation |
|-----------------|---------|--------------|------------|
| Hard gate fail rate > 5% | Alert fires; `loop_decisions.jsonl` shows hard_gates_passed=false cluster | Check `manual_review_queue.json` → identify failing gate_id → inspect `defect_history.json` → check if prompt patch is being applied correctly | Review `judge_audiobook_v2.txt` prompt; check judge model config |
| Manual review rate > 10% | Alert fires; queue growing | Check if failure is locale-specific (look at locale in queue) → check if recent checklist or prompt change caused regression | Run golden regression set to confirm scope |
| Judge schema validation fails | Section routes to manual_review with `schema_error` in trace | Check judge model output format; verify checklist_schema_version matches `2.0` | Check if judge model was updated and changed output format |
| Section timeout | Section routes to manual_review; `loop_decisions.jsonl` shows no gate_results | Check Qwen Cloud API status; check `section_timeout_seconds` config | Increase timeout or reduce `max_parallel_sections` |
| Budget exceeded | Section routes to manual_review with budget error | Check `max_tokens_per_section_total` config; investigate if a section is unusually long | Split long sections before running; adjust budget cap |
| Golden regression fails | CI blocks promotion | Do NOT override; run `scripts/audiobook_script/run_regression.py --golden-set` locally to confirm | Root-cause which gate regressed; check recent changes to checklist, rubric, or prompts |
| manual_review_queue.json not visible in UI | PhoenixControl Manual Review tab empty | Check file exists at `artifacts/audiobook/manual_review_queue.json`; check UI reads correct path | Check PhoenixControl config for Manual Review tab data source |

**Runbook location:** `docs/audiobook_operator_runbook.md` (full version; above table is summary)
- [ ] Full runbook written at `docs/audiobook_operator_runbook.md`
- [ ] On-call engineer has read the runbook (sign-off below)

**Sign-off:** _____________________ Date: _____________

---

## SUMMARY TABLE

| # | Item | Status | Sign-off |
|---|------|--------|----------|
| 1 | Go-live freeze + rollback | ☐ | |
| 2 | Required CI checks enforced | ☐ | |
| 3 | Comparator loop safety caps (config-driven max_loops, no auto-pass) | ☐ | |
| 4 | Judge quality controls (schema validation every loop, committed model, independence) | ☐ | |
| 5 | Golden regression gate (TW/HK/SG/CN min; block on regression) | ☐ | |
| 6 | Observability + incident hooks (JSONL log, alerts, PhoenixControl Manual Review tab) | ☐ | |
| 7 | Cost/rate protection (per-section token cap, budget exceeded → manual_review) | ☐ | |
| 8 | Secrets hygiene (no keys in repo; GitHub Secrets / env only) | ☐ | |
| 9 | Evidence pack complete (staging run + golden run + CI green) | ☐ | |
| 10 | Operator runbook (what to do when red, per gate) | ☐ | |

**Overall go/no-go:** ☐ GO &nbsp;&nbsp; ☐ NO-GO

**Final approval:** _____________________ Date: _____________

---

## REFERENCE — Key Files

| File | Purpose |
|------|---------|
| `config/audiobook_script/static_polish_rubric.yaml` | Step 0: offline-authored polish + TTS rules; feeds checklist rubric_ref |
| `config/audiobook_script/comparator_config.yaml` | Master runtime config: max_loops, parallel, judge model, patch injection, scoring, token budget |
| `config/audiobook_script/comparison_checklist_v2.yaml` | 9 gates (7 scored, 4 hard — incl. TTS); rubric_ref; locale overrides; aggregate threshold |
| `schemas/comparator_result_v2.schema.json` | JSON schema for judge output; version-bound to checklist schema_version=2.0 |
| `scripts/audiobook_script/run_comparator_loop.py` | Full pipeline: async parallel sections, automated patch injection, artifact trace, manual review packet |
| `artifacts/audiobook/manual_review_queue.json` | High-visibility queue; PhoenixControl Manual Review tab; sorted by severity |
| `artifacts/audiobook/loop_decisions.jsonl` | Per-loop observability log; used for alerting and audit |
| `prompts/draft_audiobook_v2.txt` | Qwen draft system prompt (implement before go-live) |
| `prompts/judge_audiobook_v2.txt` | Qwen judge system prompt; references checklist gates and rubric (implement before go-live) |
| `config/audiobook_script/golden_regression_set/` | Fixed multilingual sections for regression gating |
