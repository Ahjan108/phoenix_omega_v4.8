# Canonical Recovery Map
Generated from branch history audit.

## Recommended restore points
| Path | Capability | Recommended source ref/commit | Exists there | Restore command |
|---|---|---|---|---|
| `config/author_registry.yaml` | author 2-per-brand model | `53d89094` | yes | `git checkout 53d89094 -- config/author_registry.yaml` |
| `.github/workflows/system-truth-audit.yml` | truth audit governance loop | `origin/codex/runtime-consolidation` | yes | `git checkout origin/codex/runtime-consolidation -- .github/workflows/system-truth-audit.yml` |
| `scripts/audit/run_truth_audit.py` | audit artifact regeneration | `origin/codex/runtime-consolidation` | yes | `git checkout origin/codex/runtime-consolidation -- scripts/audit/run_truth_audit.py` |
| `scripts/audit/validate_truth_artifacts.py` | artifact validation + SHA freshness | `origin/codex/runtime-consolidation` | yes | `git checkout origin/codex/runtime-consolidation -- scripts/audit/validate_truth_artifacts.py` |
| `scripts/audit/enforce_canonical_ownership.py` | ownership enforcement | `origin/codex/runtime-consolidation` | yes | `git checkout origin/codex/runtime-consolidation -- scripts/audit/enforce_canonical_ownership.py` |
| `scripts/audit/sync_section_g_issues.py` | section G issue sync | `origin/codex/runtime-consolidation` | yes | `git checkout origin/codex/runtime-consolidation -- scripts/audit/sync_section_g_issues.py` |
| `scripts/audit/build_qwen_delta_addendum.py` | qwen delta addendum | `origin/codex/runtime-consolidation` | yes | `git checkout origin/codex/runtime-consolidation -- scripts/audit/build_qwen_delta_addendum.py` |
| `config/audit/ownership_policy.yaml` | ownership policy hard-fail/exemptions | `origin/codex/runtime-consolidation` | yes | `git checkout origin/codex/runtime-consolidation -- config/audit/ownership_policy.yaml` |
| `config/audit/remediation_registry.yaml` | section G registry | `origin/codex/runtime-consolidation` | yes | `git checkout origin/codex/runtime-consolidation -- config/audit/remediation_registry.yaml` |
| `docs/GITHUB_OPERATIONS_FRAMEWORK.md` | single-repo ops framework alignment | `origin/codex/runtime-consolidation` | yes | `git checkout origin/codex/runtime-consolidation -- docs/GITHUB_OPERATIONS_FRAMEWORK.md` |

## Notes
- Use only non-destructive source refs (main and vetted codex branches).
- Avoid restoring from known destructive branches (e.g., `origin/codex/pearl-news-pr`, `origin/codex/pearl-news-option-b`).
