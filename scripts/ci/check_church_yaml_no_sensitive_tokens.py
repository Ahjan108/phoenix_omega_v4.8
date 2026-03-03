#!/usr/bin/env python3
"""
CI grep guard: church YAMLs must not contain sensitive tokens (ssn, account_number, etc.).
Authority: Cooperative Church Compliance YAML Schema — no SSNs, bank account numbers, secrets in repo.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS = REPO_ROOT / "docs"

# Case-insensitive patterns that indicate sensitive data (must not appear in church YAMLs)
SENSITIVE_PATTERNS = [
    r"\bssn\b",
    r"\bsocial_security\b",
    r"\baccount_number\b",
    r"\bbank_account\b",
    r"\brouting_number\b",
    r"\bapi_key\b",
    r"\bsecret\b",
    r"\bpassword\b",
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN format XXX-XX-XXXX
]

# Allowed: placeholder/empty values, comments explaining no SSN
ALLOWED_CONTEXTS = [
    "populated after",
    "placeholder",
    "FILL",
    "no ssn",
    "no SSN",
    "ein: \"\"",
    "ein: ''",
]


def _check_file(path: Path) -> list[str]:
    """Return list of errors for this file."""
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"{path}: read failed: {e}"]
    for i, line in enumerate(text.splitlines(), 1):
        line_lower = line.lower()
        if any(ctx in line for ctx in ALLOWED_CONTEXTS):
            continue
        if "ein" in line_lower and ('""' in line or "''" in line):
            continue
        for pat in SENSITIVE_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                errors.append(f"{path}:{i}: potential sensitive token: {pat!r} in {line.strip()[:60]!r}")
                break
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Assert church YAMLs contain no sensitive tokens")
    ap.add_argument("--docs-dir", type=Path, default=DOCS, help="Docs directory to scan")
    ap.add_argument("--files", nargs="*", help="Specific files to check")
    args = ap.parse_args()

    if args.files:
        paths = [Path(p) for p in args.files if Path(p).exists()]
    else:
        paths = list(args.docs_dir.glob("*.yaml"))
        church_docs = args.docs_dir / "church_docs"
        if church_docs.exists():
            paths.extend(church_docs.rglob("*.yaml"))
    church_paths = [p for p in paths if "norcal_dharma" in p.name or "church" in str(p)]
    if not church_paths:
        church_paths = [p for p in paths if p.name.endswith(".yaml")]

    errors: list[str] = []
    for path in sorted(church_paths):
        errors.extend(_check_file(path))

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
