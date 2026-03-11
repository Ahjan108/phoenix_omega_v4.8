#!/usr/bin/env python3
"""
Drift audit: validate phoenix_omega has all consolidated runtime paths.

Primary source of required paths is config/audit/qwen_migration_allowlist.yaml.
If the allowlist is missing/invalid, fall back to a minimal safety set.

Writes artifacts/drift_report.json. Exits 1 if any required path is missing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ALLOWLIST_PATH = REPO_ROOT / "config" / "audit" / "qwen_migration_allowlist.yaml"

FALLBACK_REQUIRED_PATHS = [
    ".github/workflows/audiobook_manual.yml",
    ".github/workflows/audiobook_regression.yml",
    ".github/workflows/audiobook_scheduled.yml",
    ".github/workflows/locale_max_agents.yml",
    ".github/workflows/pearl_news_scheduled.yml",
    ".github/workflows/pearl_news_manual_expand.yml",
    ".github/workflows/runner_artifacts_cleanup.yml",
    "scripts/lm_studio_lock.py",
]


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def required_paths_from_allowlist() -> tuple[list[str], str]:
    cfg = _load_yaml(ALLOWLIST_PATH)
    keys = ("workflows", "scripts", "config", "docs", "pearl_news_assets")
    if not cfg:
        return list(FALLBACK_REQUIRED_PATHS), "fallback_missing_or_invalid_allowlist"
    paths: list[str] = []
    for k in keys:
        v = cfg.get(k, [])
        if isinstance(v, list):
            paths.extend(str(x).strip() for x in v if str(x).strip())
    dedup = sorted(set(paths))
    if not dedup:
        return list(FALLBACK_REQUIRED_PATHS), "fallback_empty_allowlist"
    return dedup, "allowlist"


def main() -> int:
    required_paths, required_source = required_paths_from_allowlist()
    report = {
        "repo": "phoenix_omega",
        "required_paths": required_paths,
        "required_source": required_source,
        "allowlist_path": str(ALLOWLIST_PATH.relative_to(REPO_ROOT)),
        "missing": [],
        "present": [],
        "pass": True,
    }
    for rel in required_paths:
        p = REPO_ROOT / rel
        if p.exists():
            report["present"].append(rel)
        else:
            report["missing"].append(rel)
            report["pass"] = False

    out_dir = REPO_ROOT / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "drift_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Drift report: {out_path}")
    print(f"  Source: {required_source}")
    print(f"  Present: {len(report['present'])}")
    print(f"  Missing: {len(report['missing'])}")
    if report["missing"]:
        for m in report["missing"]:
            print(f"    - {m}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
