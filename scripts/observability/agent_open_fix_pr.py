#!/usr/bin/env python3
"""
Background agent: read elevated_failures, apply safe fix recipes, open a PR.
Restricted to low-risk changes (e.g. add missing dependency to requirements-test.txt).
See docs/PRODUCTION_OBSERVABILITY_LEARNING_SPEC.md and plan: Autonomous Improvement Loop.
Usage:
  python scripts/observability/agent_open_fix_pr.py
  python scripts/observability/agent_open_fix_pr.py --dry-run
  GITHUB_TOKEN=... python scripts/observability/agent_open_fix_pr.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_elevated_failures(max_rows: int = 50) -> list[dict]:
    path = REPO_ROOT / "artifacts" / "observability" / "elevated_failures.jsonl"
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows[-max_rows:] if len(rows) > max_rows else rows


def extract_missing_module(text: str | None) -> str | None:
    if not text:
        return None
    m = re.search(r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)['\"]", text)
    return m.group(1) if m else None


def is_safe_dependency(module: str) -> bool:
    """Allowlist: only add known test/runtime deps to avoid supply-chain risk."""
    safe = {
        "yaml", "pyyaml", "pytest", "jsonschema", "feedparser",
        "requests", "urllib3", "certifi", "charset_normalizer", "idna",
    }
    base = module.split(".")[0].split("-")[0].lower()
    return base in safe or module.lower() in safe


def apply_dependency_fix(module: str, req_file: Path) -> bool:
    """Append module to requirements file if not present. Prefer requirements-test.txt."""
    if not req_file.exists():
        return False
    content = req_file.read_text()
    # Normalize to package name (e.g. pyyaml -> pyyaml)
    pkg = module.replace("_", "-").lower()
    if pkg == "yaml":
        pkg = "pyyaml"
    if any(line.strip().startswith(pkg) or line.strip().startswith(module) for line in content.splitlines() if line.strip() and not line.strip().startswith("#")):
        return False
    line = f"{pkg}\n"
    req_file.write_text(content.rstrip() + "\n" + line)
    return True


def append_operations_board_row(row: dict) -> None:
    path = REPO_ROOT / "artifacts" / "observability" / "operations_board.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Agent: apply safe fixes and open PR")
    ap.add_argument("--dry-run", action="store_true", help="Do not push or create PR")
    ap.add_argument("--max-failures", type=int, default=50, help="Max elevated failure rows to read")
    args = ap.parse_args()

    failures = load_elevated_failures(max_rows=args.max_failures)
    to_add: set[str] = set()
    for row in failures:
        if row.get("status") != "fail":
            continue
        msg = row.get("message") or ""
        stderr = row.get("stderr_tail") or ""
        module = extract_missing_module(msg) or extract_missing_module(stderr)
        if module and is_safe_dependency(module):
            to_add.add(module)

    if not to_add:
        print("No safe dependency fixes to apply.")
        return 0

    req_file = REPO_ROOT / "requirements-test.txt"
    if not req_file.exists():
        req_file = REPO_ROOT / "requirements.txt"
    applied: list[str] = []
    for mod in sorted(to_add):
        if apply_dependency_fix(mod, req_file):
            applied.append(mod)
            # Only add first so we can revert and retry; agent can run again for next
            break
    if not applied:
        print("No new dependencies applied (already present or file missing).")
        return 0

    if args.dry_run:
        print(f"Dry-run: would add {applied} to {req_file}")
        return 0

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    branch = f"fix/deps-{timestamp}"
    try:
        subprocess.run(
            ["git", "config", "user.email", "agent@phoenix.local"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Phoenix Observability Agent"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            check=True,
        )
        subprocess.run(["git", "checkout", "-b", branch], cwd=str(REPO_ROOT), capture_output=True, check=True)
        subprocess.run(["git", "add", str(req_file)], cwd=str(REPO_ROOT), capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"fix(deps): add {', '.join(applied)} for observability/systems test\n\nAuto-generated by agent_open_fix_pr.py"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            check=True,
        )
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=str(REPO_ROOT), capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}", file=sys.stderr)
        return 1

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set; PR not created. Branch pushed.")
        return 0

    try:
        env = {**os.environ, "GH_TOKEN": token}
        result = subprocess.run(
            [
                "gh", "pr", "create",
                "--title", f"fix(deps): add {', '.join(applied)}",
                "--body", f"Auto-generated by observability agent. Adds missing dependency for CI/systems test.\n\nTrigger: elevated_failures.jsonl",
                "--base", "main",
                "--head", branch,
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"gh pr create failed: {result.stderr}", file=sys.stderr)
            return 1
        out = result.stdout.strip()
        pr_url = out.split("\n")[0] if out else ""
        if pr_url:
            append_operations_board_row({
                "timestamp": timestamp,
                "signal_id": "agent_fix_pr",
                "category": "core",
                "status": "pr_opened",
                "suggested_fix": f"add {', '.join(applied)} to {req_file.name}",
                "pr_url": pr_url,
                "merged": False,
            })
            print(f"PR opened: {pr_url}")
    except Exception as e:
        print(f"PR create error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
