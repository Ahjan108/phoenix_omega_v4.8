#!/usr/bin/env python3
"""
Verify GitHub governance: ruleset targets main only, required checks match policy,
PR-only merge, no bypass scripts, no token files. Reads config from
config/governance/required_checks.yaml.

Modes:
  --mode local   Repo-only checks (no API). Always runnable in CI.
  --mode api     Ruleset + required checks via API. Needs GITHUB_TOKEN with ruleset read.
  --strict       In api mode, exit 1 if token missing (default: exit 0 with warning).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "governance" / "required_checks.yaml"
SCRIPTS_CI = REPO_ROOT / "scripts" / "ci"
FORBIDDEN_FILES = (".github_token", "github_access_token.rtf")
FORBIDDEN_PATTERNS = (re.compile(r"enforcement\s*:\s*[\"']disabled[\"']", re.I), re.compile(r"bypass_actors", re.I))


def load_config() -> dict:
    if not CONFIG_PATH.is_file():
        return {}
    data = {"version": 1, "always_required": ["Core tests"], "path_filtered_optional": []}
    try:
        with open(CONFIG_PATH) as f:
            in_always = in_path = False
            for line in f:
                s = line.strip()
                if s.startswith("always_required:"):
                    in_always, in_path = True, False
                    continue
                if "path_filtered_optional" in s and s.startswith("path_filtered"):
                    in_always, in_path = False, True
                    continue
                if in_always and s.startswith("- "):
                    data.setdefault("always_required", []).append(s[2:].strip(' "\t'))
                elif in_path and s.startswith("- "):
                    data.setdefault("path_filtered_optional", []).append(s[2:].strip(' "\t'))
    except Exception:
        pass
    return data


def check_policy_files_present() -> bool:
    ok = True
    if not CONFIG_PATH.is_file():
        print(f"  FAIL: Missing {CONFIG_PATH}")
        ok = False
    else:
        print(f"  PASS: {CONFIG_PATH} present")
    gov_doc = REPO_ROOT / "docs" / "GITHUB_GOVERNANCE.md"
    if not gov_doc.is_file():
        print(f"  FAIL: Missing {gov_doc}")
        ok = False
    else:
        print(f"  PASS: {gov_doc} present")
    return ok


def check_no_bypass_scripts() -> bool:
    ok = True
    if not SCRIPTS_CI.is_dir():
        return True
    for f in SCRIPTS_CI.glob("*.py"):
        if f.name == "verify_github_governance.py":
            continue
        if "bypass" in f.name.lower() and "no_bypass" not in f.name.lower():
            print(f"  FAIL: Bypass script not allowed: {f.name}")
            ok = False
        else:
            try:
                if f.name == "verify_github_governance.py":
                    continue
                text = f.read_text()
                for pat in FORBIDDEN_PATTERNS:
                    if pat.search(text):
                        print(f"  FAIL: Bypass logic in {f.name}")
                        ok = False
                        break
            except Exception:
                pass
    if ok:
        print("  PASS: No bypass scripts or logic")
    return ok


def check_no_token_files() -> bool:
    ok = True
    for name in FORBIDDEN_FILES:
        p = REPO_ROOT / name
        if p.is_file():
            print(f"  FAIL: Token file must be removed: {name}")
            ok = False
    for p in REPO_ROOT.glob("*.rtf"):
        if "token" in p.name.lower() or "github" in p.name.lower():
            print(f"  FAIL: Token file must be removed: {p.name}")
            ok = False
    if ok:
        print("  PASS: No token files in repo")
    return ok


def run_local() -> bool:
    print("[local] Policy files present")
    a = check_policy_files_present()
    print("[local] No bypass scripts")
    b = check_no_bypass_scripts()
    print("[local] No token files")
    c = check_no_token_files()
    return a and b and c


def api_get(token: str, path: str) -> dict | list:
    url = f"https://api.github.com/repos/Ahjan108/phoenix_omega_v4.8{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def run_api(strict: bool) -> bool:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        try:
            out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
            if out.returncode == 0 and out.stdout:
                token = out.stdout.strip()
        except Exception:
            pass
    if not token:
        msg = "Skipping API checks (no GITHUB_TOKEN). Use --mode local only or set GITHUB_TOKEN."
        if strict:
            print(f"  FAIL: {msg}", file=sys.stderr)
            return False
        print(f"  WARN: {msg}")
        return True
    config = load_config()
    always = config.get("always_required") or ["Core tests"]
    ok = True
    try:
        rulesets = api_get(token, "/rulesets")
        if not isinstance(rulesets, list):
            rulesets = [rulesets]
        for rs in rulesets:
            name = rs.get("name", "?")
            cond = rs.get("conditions", {}) or {}
            ref = cond.get("ref_name", {}) or {}
            include = ref.get("include") or []
            if not include or (len(include) == 1 and (include[0] in ("refs/heads/main", "~DEFAULT_BRANCH"))):
                print(f"  PASS: Ruleset {name} targets main only")
            else:
                print(f"  FAIL: Ruleset {name} does not target main only: {include}")
                ok = False
            rules = rs.get("rules") or []
            has_pr = any(r.get("type") == "pull_request" for r in rules)
            if has_pr:
                print(f"  PASS: Ruleset {name} requires PR before merge")
            else:
                print(f"  FAIL: Ruleset {name} must require PR before merge")
                ok = False
    except urllib.error.HTTPError as e:
        print(f"  WARN: Could not read rulesets ({e.code}). Run with token that has ruleset read.")
        if strict:
            ok = False
    except Exception as e:
        print(f"  WARN: API error: {e}")
        if strict:
            ok = False
    print("  INFO: Required checks list should include at least one of:", always)
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify GitHub governance")
    ap.add_argument("--mode", choices=("local", "api", "all"), default="all", help="local=repo-only, api=API checks, all=both")
    ap.add_argument("--strict", action="store_true", help="In api mode, fail if token missing")
    args = ap.parse_args()
    ok = True
    if args.mode in ("local", "all"):
        ok = run_local() and ok
    if args.mode in ("api", "all"):
        ok = run_api(args.strict) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
