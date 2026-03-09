#!/usr/bin/env python3
"""
Validate that required check names in config/governance/required_checks.yaml
match real workflow/job check names emitted by GitHub Actions.
"""
from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / "config" / "governance" / "required_checks.yaml"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _yaml_load(path: Path):
    import yaml  # type: ignore
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_required() -> list[str]:
    data = _yaml_load(CONFIG)
    out = []
    for name in data.get("always_required", []) or []:
        if isinstance(name, str) and name.strip():
            out.append(name.strip())
    return out


def collect_available_checks() -> set[str]:
    checks: set[str] = set()
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        data = _yaml_load(wf)
        wf_name = data.get("name")
        if isinstance(wf_name, str) and wf_name.strip():
            checks.add(wf_name.strip())
        jobs = data.get("jobs") or {}
        if isinstance(jobs, dict):
            for job_id, job_cfg in jobs.items():
                if not isinstance(job_cfg, dict):
                    continue
                nm = job_cfg.get("name")
                if isinstance(nm, str) and nm.strip():
                    checks.add(nm.strip())
                else:
                    checks.add(str(job_id))
    return checks


def main() -> int:
    try:
        required = load_required()
        available = collect_available_checks()
    except Exception as e:
        print(f"FAIL: unable to parse governance/workflow files: {e}")
        return 1

    missing = [c for c in required if c not in available]
    if missing:
        print("FAIL: required checks do not match any workflow/job names:")
        for m in missing:
            print(f"  - {m}")
        print("INFO: sample available names:")
        for n in sorted(list(available))[:40]:
            print(f"  * {n}")
        return 1

    print(f"PASS: {len(required)} required checks matched workflow/job names")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
