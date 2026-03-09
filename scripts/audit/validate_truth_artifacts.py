#!/usr/bin/env python3
"""
Validate that the four required truth-audit artifacts exist and are parseable.
With --check-sha: fail if artifacts lack last_verified_sha or it mismatches current main SHA.
Exit 0 if all valid; exit 1 if any missing or invalid.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_DIR = REPO_ROOT / "artifacts" / "audit"

REQUIRED = [
    "SYSTEM_TRUTH_REPORT.md",
    "DRIFT_MATRIX.csv",
    "MISSING_REFERENCED_FILES.md",
    "IMPLEMENTATION_STATUS_LEDGER.csv",
]


def _git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git"] + list(args),
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return (out.stdout or "").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def get_current_main_sha() -> str:
    """SHA of origin/main, or HEAD if origin/main not available."""
    sha = _git("rev-parse", "origin/main")
    if sha:
        return sha
    return _git("rev-parse", "HEAD") or ""


def check_sha_freshness(expected_sha: str) -> list[str]:
    """Fail if report or ledger lack expected_sha. Returns list of errors."""
    errors = []
    if not expected_sha:
        errors.append("check-sha: could not determine current main SHA")
        return errors
    report_path = AUDIT_DIR / "SYSTEM_TRUTH_REPORT.md"
    if report_path.exists():
        text = report_path.read_text(encoding="utf-8")
        if expected_sha not in text:
            errors.append(
                f"SYSTEM_TRUTH_REPORT.md: missing or mismatched last_verified_sha (expected {expected_sha[:12]}...)"
            )
    else:
        errors.append("SYSTEM_TRUTH_REPORT.md: missing (cannot check SHA)")
    ledger_path = AUDIT_DIR / "IMPLEMENTATION_STATUS_LEDGER.csv"
    if ledger_path.exists():
        with open(ledger_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "last_verified_sha" not in (reader.fieldnames or []):
                errors.append("IMPLEMENTATION_STATUS_LEDGER.csv: missing column last_verified_sha")
            else:
                rows = list(reader)
                if not any((r.get("last_verified_sha") or "").strip() == expected_sha for r in rows):
                    errors.append(
                        f"IMPLEMENTATION_STATUS_LEDGER.csv: no row with last_verified_sha={expected_sha[:12]}... (artifacts stale?)"
                    )
    else:
        errors.append("IMPLEMENTATION_STATUS_LEDGER.csv: missing (cannot check SHA)")
    return errors


def validate_report(p: Path) -> tuple[bool, str]:
    if not p.exists():
        return False, "missing"
    text = p.read_text(encoding="utf-8")
    if not text.strip():
        return False, "empty"
    if "Repo-wide summary" not in text and "Full-System Truth" not in text:
        return False, "invalid format (expected report sections)"
    return True, "ok"


def validate_csv(p: Path, min_cols: int = 2) -> tuple[bool, str]:
    if not p.exists():
        return False, "missing"
    try:
        with open(p, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as e:
        return False, f"parse error: {e}"
    if not rows:
        return False, "empty"
    if len(rows[0]) < min_cols:
        return False, f"header has <{min_cols} columns"
    return True, "ok"


def validate_missing_md(p: Path) -> tuple[bool, str]:
    if not p.exists():
        return False, "missing"
    text = p.read_text(encoding="utf-8")
    if not text.strip():
        return False, "empty"
    return True, "ok"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate truth-audit artifacts; optional SHA freshness vs main.")
    parser.add_argument(
        "--check-sha",
        action="store_true",
        help="Fail if artifacts lack last_verified_sha or it mismatches current main SHA",
    )
    args = parser.parse_args()

    errors = []
    if args.check_sha:
        expected = get_current_main_sha()
        errors.extend(check_sha_freshness(expected))

    # REPORT
    ok, msg = validate_report(AUDIT_DIR / "SYSTEM_TRUTH_REPORT.md")
    if not ok:
        errors.append(f"SYSTEM_TRUTH_REPORT.md: {msg}")

    # DRIFT_MATRIX
    ok, msg = validate_csv(AUDIT_DIR / "DRIFT_MATRIX.csv", min_cols=4)
    if not ok:
        errors.append(f"DRIFT_MATRIX.csv: {msg}")
    else:
        with open(AUDIT_DIR / "DRIFT_MATRIX.csv", newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            if "path_omega" not in (r.fieldnames or []):
                errors.append("DRIFT_MATRIX.csv: missing column path_omega")

    # MISSING_REFERENCED_FILES
    ok, msg = validate_missing_md(AUDIT_DIR / "MISSING_REFERENCED_FILES.md")
    if not ok:
        errors.append(f"MISSING_REFERENCED_FILES.md: {msg}")

    # LEDGER
    ok, msg = validate_csv(AUDIT_DIR / "IMPLEMENTATION_STATUS_LEDGER.csv", min_cols=6)
    if not ok:
        errors.append(f"IMPLEMENTATION_STATUS_LEDGER.csv: {msg}")
    else:
        with open(AUDIT_DIR / "IMPLEMENTATION_STATUS_LEDGER.csv", newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            if "system" not in (r.fieldnames or []):
                errors.append("IMPLEMENTATION_STATUS_LEDGER.csv: missing column system")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("All four required artifacts exist and are parseable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
