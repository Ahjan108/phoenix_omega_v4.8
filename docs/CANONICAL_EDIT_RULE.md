# Sync from canonical — edit rule

**Purpose:** Single source of truth for shared runtime files. Prevents drift between phoenix_omega and backup repos (e.g. Qwen-Agent).

**Rule:** Any shared runtime file may only be edited in the **canonical location** (phoenix_omega). Edits in Qwen-Agent (or other backup repos) to allowlisted or shared paths do **not** count as source of truth.

**Implications:**

- When you need to change a script, config, or doc that exists in both repos, edit it in **phoenix_omega** only.
- Do not treat Qwen-Agent as the place to make changes to shared code; phoenix_omega is always the authority.
- Copy/sync direction is: phoenix_omega → backup (for backup copies), never the reverse for authority.
- The migration allowlist ([config/audit/qwen_migration_allowlist.yaml](../config/audit/qwen_migration_allowlist.yaml)) defines which paths are shared; no path outside the allowlist may be copied from Qwen-Agent into phoenix_omega without first adding it to the allowlist.

**See also:** [GITHUB_OPERATIONS_FRAMEWORK.md](./GITHUB_OPERATIONS_FRAMEWORK.md) (Sync from canonical), [QWEN_SAFE_CONSOLIDATION_SPEC.md](./QWEN_SAFE_CONSOLIDATION_SPEC.md) §3.
