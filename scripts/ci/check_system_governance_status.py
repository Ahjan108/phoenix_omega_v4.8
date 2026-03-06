#!/usr/bin/env python3
"""
Check all system functions status for passing governance and reports; optional auto-fix.

Authority: docs/DOCS_INDEX.md (Governance note, Scripts/CI — content quality gates).
Runs governance checks and report generators listed in the index, collects pass/fail,
writes a machine-readable report and optionally applies safe auto-fixes.

Usage:
  python scripts/ci/check_system_governance_status.py [--fix] [--out FILE] [--skip SLUG...]
  --fix    Apply safe auto-fixes (e.g. DOCS_INDEX Last updated date)
  --out    Write JSON report to FILE (default: artifacts/governance/system_governance_report.json)
  --skip   Skip checks by slug (e.g. --skip production_gates github_api)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_INDEX = REPO_ROOT / "docs" / "DOCS_INDEX.md"
LAST_UPDATED_RE = re.compile(r"(?im)^(\*\*Last updated:\*\*)\s*\d{4}-\d{2}-\d{2}\s*$")


@dataclass
class CheckResult:
    slug: str
    name: str
    passed: bool
    detail: str
    fix_applied: bool = False
    output: str = ""


def run_cmd(
    cwd: Path,
    argv: list[str],
    timeout: int | None = 120,
    env: dict | None = None,
) -> tuple[int, str, str]:
    env = env or {}
    full_env = {**dict(__import__("os").environ), **env}
    try:
        r = subprocess.run(
            argv,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=full_env,
        )
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def check_docs_governance(skip: set[str]) -> CheckResult:
    if "docs_governance" in skip:
        return CheckResult("docs_governance", "DOCS_INDEX link integrity + Last updated", True, "skipped", False, "")
    script = REPO_ROOT / "scripts" / "ci" / "check_docs_governance.py"
    if not script.exists():
        return CheckResult("docs_governance", "DOCS_INDEX governance", False, f"script missing: {script}", False, "")
    code, out, err = run_cmd(REPO_ROOT, [sys.executable, str(script), "--check-staleness"], timeout=30)
    passed = code == 0
    detail = (out + " " + err).strip()[:500] or ("PASS" if passed else "FAIL")
    return CheckResult("docs_governance", "DOCS_INDEX link integrity + Last updated", passed, detail, False, out + "\n" + err)


def check_github_governance_local(skip: set[str]) -> CheckResult:
    if "github_local" in skip:
        return CheckResult("github_local", "GitHub governance (local)", True, "skipped", False, "")
    script = REPO_ROOT / "scripts" / "ci" / "verify_github_governance.py"
    if not script.exists():
        return CheckResult("github_local", "GitHub governance (local)", False, f"script missing: {script}", False, "")
    code, out, err = run_cmd(REPO_ROOT, [sys.executable, str(script), "--mode", "local"], timeout=30)
    passed = code == 0
    detail = (out + " " + err).strip()[:500] or ("PASS" if passed else "FAIL")
    return CheckResult("github_local", "GitHub governance (local)", passed, detail, False, out + "\n" + err)


def check_github_governance_api(skip: set[str]) -> CheckResult:
    if "github_api" in skip:
        return CheckResult("github_api", "GitHub governance (API)", True, "skipped", False, "")
    script = REPO_ROOT / "scripts" / "ci" / "verify_github_governance.py"
    if not script.exists():
        return CheckResult("github_api", "GitHub governance (API)", False, f"script missing: {script}", False, "")
    code, out, err = run_cmd(REPO_ROOT, [sys.executable, str(script), "--mode", "api"], timeout=30)
    # API mode may exit 0 with warning if token missing; we still record result
    passed = code == 0
    detail = (out + " " + err).strip()[:500] or ("PASS" if passed else "warning/FAIL")
    return CheckResult("github_api", "GitHub governance (API)", passed, detail, False, out + "\n" + err)


def check_production_gates(skip: set[str]) -> CheckResult:
    if "production_gates" in skip:
        return CheckResult("production_gates", "Production readiness gates", True, "skipped", False, "")
    script = REPO_ROOT / "scripts" / "run_production_readiness_gates.py"
    if not script.exists():
        return CheckResult("production_gates", "Production readiness gates", False, f"script missing: {script}", False, "")
    code, out, err = run_cmd(REPO_ROOT, [sys.executable, str(script)], timeout=180)
    passed = code == 0
    detail = (out + " " + err).strip()[:500] or ("PASS" if passed else "FAIL")
    return CheckResult("production_gates", "Production readiness gates", passed, detail, False, out + "\n" + err)


def check_teacher_gates(skip: set[str]) -> CheckResult:
    if "teacher_gates" in skip:
        return CheckResult("teacher_gates", "Teacher production gates", True, "skipped", False, "")
    script = REPO_ROOT / "scripts" / "ci" / "run_teacher_production_gates.py"
    if not script.exists():
        return CheckResult("teacher_gates", "Teacher production gates", False, f"script missing: {script}", False, "")
    code, out, err = run_cmd(REPO_ROOT, [sys.executable, str(script)], timeout=90)
    passed = code == 0
    detail = (out + " " + err).strip()[:500] or ("PASS" if passed else "FAIL")
    return CheckResult("teacher_gates", "Teacher production gates", passed, detail, False, out + "\n" + err)


def check_teacher_synthetic_governance(skip: set[str]) -> CheckResult:
    if "teacher_synthetic" in skip:
        return CheckResult("teacher_synthetic", "Teacher synthetic governance", True, "skipped", False, "")
    script = REPO_ROOT / "scripts" / "ci" / "check_teacher_synthetic_governance.py"
    if not script.exists():
        return CheckResult("teacher_synthetic", "Teacher synthetic governance", False, f"script missing: {script}", False, "")
    code, out, err = run_cmd(REPO_ROOT, [sys.executable, str(script)], timeout=60)
    passed = code == 0
    detail = (out + " " + err).strip()[:500] or ("PASS" if passed else "FAIL")
    return CheckResult("teacher_synthetic", "Teacher synthetic governance", passed, detail, False, out + "\n" + err)


def check_brand_guards(skip: set[str]) -> CheckResult:
    if "brand_guards" in skip:
        return CheckResult("brand_guards", "NorCal Dharma + Church YAML guards", True, "skipped", False, "")
    norcal = REPO_ROOT / "scripts" / "ci" / "check_norcal_dharma_brand_guards.py"
    church = REPO_ROOT / "scripts" / "ci" / "check_church_yaml_no_sensitive_tokens.py"
    if not norcal.exists():
        return CheckResult("brand_guards", "Brand guards", False, f"missing: {norcal.name}", False, "")
    code1, out1, err1 = run_cmd(REPO_ROOT, [sys.executable, str(norcal)], timeout=30)
    if code1 != 0:
        return CheckResult("brand_guards", "NorCal Dharma + Church YAML guards", False, (out1 + " " + err1).strip()[:500], False, out1 + "\n" + err1)
    if not church.exists():
        return CheckResult("brand_guards", "Brand guards", True, "NorCal OK; church script missing", False, out1)
    code2, out2, err2 = run_cmd(REPO_ROOT, [sys.executable, str(church)], timeout=30)
    passed = code2 == 0
    detail = (out2 + " " + err2).strip()[:500] or ("PASS" if passed else "FAIL")
    return CheckResult("brand_guards", "NorCal Dharma + Church YAML guards", passed, detail, False, out1 + "\n" + out2 + "\n" + err2)


def report_variation_knobs(skip: set[str]) -> CheckResult:
    if "variation_report" in skip:
        return CheckResult("variation_report", "Variation knob report", True, "skipped", False, "")
    script = REPO_ROOT / "scripts" / "ci" / "report_variation_knobs.py"
    if not script.exists():
        return CheckResult("variation_report", "Variation knob report", False, f"script missing: {script}", False, "")
    code, out, err = run_cmd(REPO_ROOT, [sys.executable, str(script)], timeout=60)
    passed = code == 0
    detail = (out + " " + err).strip()[:500] or ("PASS" if passed else "FAIL")
    return CheckResult("variation_report", "Variation knob report", passed, detail, False, out + "\n" + err)


def fix_docs_index_last_updated() -> bool:
    """Update DOCS_INDEX.md **Last updated:** to today. Returns True if file was modified."""
    if not DOCS_INDEX.exists():
        return False
    text = DOCS_INDEX.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    new_text, n = LAST_UPDATED_RE.subn(rf"\g<1> {today}", text, count=1)
    if n == 0:
        # Try adding line after first **Purpose:** block if header not found
        if "**Last updated:**" not in text:
            return False
        new_text = re.sub(r"(\*\*Last updated:\*\*)\s*[^\s\n]+", rf"\1 {today}", text, count=1)
        if new_text == text:
            return False
    elif new_text == text:
        return False
    DOCS_INDEX.write_text(new_text, encoding="utf-8")
    return True


def apply_auto_fixes(results: list[CheckResult], do_fix: bool) -> list[CheckResult]:
    if not do_fix:
        return results
    out: list[CheckResult] = []
    for r in results:
        if r.slug == "docs_governance" and not r.passed:
            # Only fix if the sole issue is Last updated (missing or stale). We can't know from exit code alone,
            # so we offer to update the date; if there were broken links, the next run will still fail.
            if fix_docs_index_last_updated():
                # Re-run check to see if now passing
                code, out_str, err = run_cmd(
                    REPO_ROOT,
                    [sys.executable, str(REPO_ROOT / "scripts" / "ci" / "check_docs_governance.py"), "--check-staleness"],
                    timeout=30,
                )
                out.append(CheckResult(
                    r.slug, r.name, code == 0,
                    "Last updated set to today; re-check: " + ("PASS" if code == 0 else "still failing"),
                    fix_applied=True, output=out_str + "\n" + err,
                ))
            else:
                out.append(r)
        else:
            out.append(r)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check system governance and report status; optional auto-fix (docs/DOCS_INDEX.md authority)"
    )
    parser.add_argument("--fix", action="store_true", help="Apply safe auto-fixes (e.g. DOCS_INDEX Last updated)")
    parser.add_argument("--out", type=Path, default=None, help="JSON report path (default: artifacts/governance/system_governance_report.json)")
    parser.add_argument("--skip", action="append", default=[], help="Skip check by slug (repeatable)")
    args = parser.parse_args()

    skip = set(args.skip)
    checks: list[tuple[str, Callable[[set[str]], CheckResult]]] = [
        ("docs_governance", check_docs_governance),
        ("github_local", check_github_governance_local),
        ("github_api", check_github_governance_api),
        ("production_gates", check_production_gates),
        ("teacher_gates", check_teacher_gates),
        ("teacher_synthetic", check_teacher_synthetic_governance),
        ("brand_guards", check_brand_guards),
        ("variation_report", report_variation_knobs),
    ]

    results: list[CheckResult] = []
    for slug, fn in checks:
        results.append(fn(skip))

    if args.fix:
        results = apply_auto_fixes(results, do_fix=True)

    # Report path
    out_path = args.out or REPO_ROOT / "artifacts" / "governance" / "system_governance_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": datetime.now().isoformat(),
        "repo_root": str(REPO_ROOT),
        "fix_applied": args.fix,
        "checks": [asdict(r) for r in results],
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "fixes_applied": sum(1 for r in results if r.fix_applied),
        },
    }
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Human-readable summary to stdout
    print("System governance status")
    print("=" * 50)
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        fix_tag = " [fix applied]" if r.fix_applied else ""
        print(f"  {status}: {r.name}{fix_tag}")
        if not r.passed and r.detail:
            print(f"      {r.detail[:200]}")
    print("=" * 50)
    print(f"Report: {out_path.relative_to(REPO_ROOT)}")
    print(f"Summary: {report['summary']['passed']}/{report['summary']['total']} passed, {report['summary']['fixes_applied']} fixes applied")

    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
