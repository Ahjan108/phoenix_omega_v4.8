#!/usr/bin/env python3
"""
Drift audit: validate phoenix_omega has all consolidated runtime paths (allowlist).
Writes artifacts/drift_report.json. Exits 1 if any required path is missing.
See docs/RUNTIME_CONSOLIDATION_MIGRATION_MANIFEST.md and docs/OWNERSHIP_MATRIX.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Required paths after consolidation (allowlist from migration manifest)
REQUIRED_PATHS = [
    ".github/workflows/audiobook_manual.yml",
    ".github/workflows/audiobook_regression.yml",
    ".github/workflows/audiobook_scheduled.yml",
    ".github/workflows/locale_max_agents.yml",
    ".github/workflows/pearl_news_scheduled.yml",
    ".github/workflows/pearl_news_manual_expand.yml",
    ".github/workflows/runner_artifacts_cleanup.yml",
    "scripts/lm_studio_lock.py",
    "scripts/localization/run_locale_batches.py",
    "scripts/localization/translate_atoms_all_locales.py",
    "scripts/localization/validate_translations.py",
    "scripts/pearl_news_article_judge.py",
    "scripts/runner/runner_cleanup.sh",
    "scripts/runner/heavy_window_guard.py",
    "scripts/runner/runner_watchdog.sh",
    "scripts/runner/install_watchdog_launchd.sh",
    "config/content_type_registry.yaml",
    "config/runner/heavy_windows.yaml",
    "docs/RUNTIME_CONSOLIDATION_MIGRATION_MANIFEST.md",
    "docs/OWNERSHIP_MATRIX.md",
    "docs/LOCALIZATION_100_PERCENT_RUNBOOK.md",
    "prompts/article_judge/judge_pearl_news_v1.txt",
]


def main() -> int:
    report = {
        "repo": "phoenix_omega",
        "required_paths": REQUIRED_PATHS,
        "missing": [],
        "present": [],
        "pass": True,
    }
    for rel in REQUIRED_PATHS:
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
    print(f"  Present: {len(report['present'])}")
    print(f"  Missing: {len(report['missing'])}")
    if report["missing"]:
        for m in report["missing"]:
            print(f"    - {m}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
