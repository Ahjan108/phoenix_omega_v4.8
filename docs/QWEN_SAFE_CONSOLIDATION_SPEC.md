# Safe Qwen-Agent Consolidation Into phoenix_omega (No Immediate Delete)

**Objective:** Promote useful runtime assets from Qwen-Agent to phoenix_omega, freeze Qwen-Agent as backup-only, verify parity, then archive Qwen-Agent safely.

---

## 1. Scope

**In scope:**

1. Workflow files used in production/manual ops.
2. Runtime scripts used by localization, audiobook, Pearl News, runner reliability.
3. Required config/docs supporting those runtimes.
4. Verification and cutover evidence.

**Out of scope:**

1. Full-tree copy.
2. Deleting Qwen-Agent immediately.
3. Changing canonical non-related systems.

---

## 2. Preconditions

1. `phoenix_omega` branch for migration exists (`codex/runtime-consolidation` or equivalent).
2. Qwen-Agent is dispatch-only for previously scheduled jobs.
3. `DRIFT_MATRIX.csv` and ownership policy exist.
4. Secrets for equivalent workflows already present in phoenix_omega.

---

## 3. Allowlist (authoritative)

Create and maintain:

**`config/audit/qwen_migration_allowlist.yaml`**

Schema: `workflows`, `scripts`, `config`, `docs`, `pearl_news_assets`. Populate only approved paths.

**Rule:** No path outside allowlist may be copied.

**Sync from canonical:** Any shared runtime file may only be edited in the canonical location (phoenix_omega). Edits in Qwen-Agent to allowlisted or shared paths do not count as source of truth. See [CANONICAL_EDIT_RULE.md](./CANONICAL_EDIT_RULE.md) and [GITHUB_OPERATIONS_FRAMEWORK.md](./GITHUB_OPERATIONS_FRAMEWORK.md).

See [config/audit/qwen_migration_allowlist.yaml](../config/audit/qwen_migration_allowlist.yaml) for the authoritative list (e.g. audiobook_manual, audiobook_regression, audiobook_scheduled, locale_max_agents, pearl_news_scheduled, pearl_news_manual_expand, runner_artifacts_cleanup, lm_studio_lock, localization scripts, pearl_news_article_judge, runner/*, and required supporting config/docs).

---

## 4. Freeze Qwen-Agent (enforced)

Backup repos are **frozen**: no schedule triggers, no production writes, manual dispatch only.

1. Keep `workflow_dispatch`.
2. Ensure no `schedule:` remains in designated production workflows in Qwen-Agent.
3. Add repo note in Qwen-Agent: backup/manual only; no production cron; no production writes.

---

## 5. Migration Procedure

1. **Baseline:** Record SHA of both repos; export pre-migration drift snapshot (`DRIFT_MATRIX.csv`).
2. Copy allowlisted paths from Qwen-Agent to phoenix_omega.
3. **Normalize path references:** Replace Qwen-Agent-root assumptions with phoenix_omega-root.
4. Resolve imports and script entrypoints.
5. **Update docs and registry:** DOCS_INDEX, operations framework, repo registry.

---

## 6. Parity Validation Gates (must pass)

For each migrated path:

1. **Existence gate:** Target file exists in phoenix_omega.
2. **Import gate:** Python compile/import succeeds (where applicable).
3. **Workflow gate:** YAML parses; workflow dispatch runs in phoenix_omega (dry/smoke mode).
4. **Smoke gate:** Localization smoke; Pearl News mode smoke; audiobook/manual smoke; runner utility smoke.
5. **Drift gate:** Ownership enforcement passes or only known approved exceptions.

**Required evidence artifacts:**

- `artifacts/audit/migration_parity_report.json`
- `artifacts/audit/migration_parity_report.md`
- Workflow run IDs/screenshots/links

---

## 7. Go/No-Go

**Go to archive only if:**

1. All parity gates pass.
2. No critical ownership violations remain.
3. Production schedules run only from phoenix_omega.
4. Rollback instructions documented.

**No-Go if:**

1. Any migrated workflow fails.
2. Any required script missing/broken.
3. Unresolved canonical conflict in ownership policy.

---

## 8. Archive (not delete)

After Go:

- **Option A (local rename):** `Qwen-Agent` → `Qwen-Agent_archive_YYYYMMDD`
- **Option B (move to backup disk):** Move entire folder and keep checksum manifest.

Retain archive for 2–6 weeks minimum.

Create **`artifacts/audit/qwen_archive_receipt.json`** with:

- `archive_path`
- `archive_date`
- `source_sha`
- `retention_until`
- `rollback_steps`

---

## 9. Rollback Plan

If post-cutover issue appears:

1. Restore specific file(s) from archive, not whole repo.
2. Re-run affected parity gates.
3. Log incident and fix ownership policy/remediation registry.

---

## 10. Acceptance Criteria

1. phoenix_omega contains all allowlisted runtime assets needed in production.
2. Qwen-Agent remains dispatch-only backup.
3. Parity report shows pass on all required gates.
4. Qwen-Agent archived (not deleted) with receipt + retention window.
5. Drift/ownership CI remains green after cutover.

---

## Handoff Addendum — Ownership Exemption Rules

These rules keep the audit-as-enforceable-system safe after handoff. Apply to **config/audit/ownership_policy.yaml** and any exemption list.

1. **Exemptions are temporary.** Each exemption must have an **owner** (GitHub handle or team) and a **removal date** (YYYY-MM-DD). No open-ended exemptions.

2. **No new exemptions without written justification.** Adding an exemption requires a short justification (e.g. “Pearl News cron cutover planned 2026-04-15”) in the policy or linked issue/PR.

3. **Any new shadow path must fail CI by default.** If a path appears in DRIFT_MATRIX as forbidden type and is not in the exemption list, the run must fail. Do not add exemptions preemptively for “expected” drift.

4. **Removing a shadow requires removing its exemption in the same PR.** When a shadow path is deleted or canonical ownership is resolved, remove that path from `exempt_shadow_paths` (or the exemption registry) in the same change. This keeps the exemption list and repo state in sync.

**Reference:** Truth Audit Governance Loop ([DOCS_INDEX § Truth Audit Governance Loop](DOCS_INDEX.md#truth-audit-governance-loop)), [config/audit/ownership_policy.yaml](../config/audit/ownership_policy.yaml).
