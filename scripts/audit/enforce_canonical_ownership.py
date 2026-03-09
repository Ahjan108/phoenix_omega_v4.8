#!/usr/bin/env python3
"""
Enforce canonical ownership from DRIFT_MATRIX.csv.
For rows where canonical_repo=phoenix_omega and duplicate_type is in forbidden types,
fail if the non-canonical (shadow) path exists under Qwen-Agent.
Writes artifacts/audit/ownership_violations.json and exits non-zero on violations
(unless config/audit/ownership_policy.yaml has warn_only: true).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_DIR = REPO_ROOT / "artifacts" / "audit"
CONFIG_AUDIT = REPO_ROOT / "config" / "audit"
QWEN_AGENT = REPO_ROOT / "Qwen-Agent"


def _normalize_dup_type(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_")


def load_policy() -> dict:
    policy_path = CONFIG_AUDIT / "ownership_policy.yaml"
    if not policy_path.exists():
        return {"forbidden_types": ["stale_shadow_copy", "semantic_duplicate"], "warn_only": False}
    try:
        import yaml
        return yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {"forbidden_types": ["stale_shadow_copy", "semantic_duplicate"], "warn_only": False}


def load_drift_matrix() -> list[dict]:
    p = AUDIT_DIR / "DRIFT_MATRIX.csv"
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    policy = load_policy()
    forbidden_raw = policy.get("forbidden_types") or ["stale_shadow_copy", "semantic_duplicate"]
    forbidden = set()
    for t in forbidden_raw:
        forbidden.add(_normalize_dup_type(t))
        forbidden.add((t or "").strip().lower())
    warn_only = bool(policy.get("warn_only"))
    exempt_raw = policy.get("exempt_shadow_paths") or []
    # Support both string entries and { path, owner?, removal_date? } for handoff rules.
    exempt_patterns = []
    for p in exempt_raw:
        if isinstance(p, dict):
            path_val = (p.get("path") or "").strip()
            if path_val:
                exempt_patterns.append(path_val)
        elif isinstance(p, str) and p.strip():
            exempt_patterns.append(p.strip())

    def is_exempt(path: str) -> bool:
        for pat in exempt_patterns:
            if path == pat or path.startswith(pat.rstrip("/") + "/") or (pat.endswith("/") and path.startswith(pat)):
                return True
        return False

    rows = load_drift_matrix()
    violations = []

    for row in rows:
        canonical = (row.get("canonical_repo") or "").strip().lower()
        if canonical != "phoenix_omega":
            continue
        dup_type = (row.get("duplicate_type") or "").strip()
        if _normalize_dup_type(dup_type) not in forbidden and dup_type.lower() not in forbidden:
            continue
        path_qwen = (row.get("path_qwen") or "").strip()
        if not path_qwen or path_qwen.startswith("N/A"):
            continue
        if is_exempt(path_qwen):
            continue
        # path_qwen is the shadow path (e.g. Qwen-Agent/pearl_news/ or Qwen-Agent/scripts/audiobook_script/run_comparator_loop.py)
        rel = path_qwen.replace("Qwen-Agent/", "", 1).strip("/")
        if not rel:
            continue
        check_path = QWEN_AGENT / rel
        if check_path.exists():
            violations.append({"path_qwen": path_qwen, "duplicate_type": dup_type, "canonical_repo": "phoenix_omega"})

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    out = AUDIT_DIR / "ownership_violations.json"
    out.write_text(json.dumps({"violations": violations, "warn_only": warn_only}, indent=2), encoding="utf-8")

    if violations:
        for v in violations:
            print(f"Ownership violation: {v['path_qwen']} (canonical=phoenix_omega, type={v['duplicate_type']})", file=sys.stderr)
        if warn_only:
            print("warn_only=true: not failing CI.", file=sys.stderr)
            return 0
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
