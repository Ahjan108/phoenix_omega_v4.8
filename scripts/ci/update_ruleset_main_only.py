#!/usr/bin/env python3
"""
Update the Protect main ruleset to target only refs/heads/main (not all branches).

Token (pick one):
  • GITHUB_TOKEN=ghp_xxx python scripts/ci/update_ruleset_main_only.py
  • echo ghp_xxx > .github_token (repo root, gitignored)
  • gh auth login  then run script (uses gh auth token)

Requires: repo admin PAT with repo scope.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPO = "Ahjan108/phoenix_omega_v4.8"
RULESET_ID = 13451138
API = "https://api.github.com"


def _get_token() -> str:
    # 1. Environment
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    # 2. Repo-root file (script is in scripts/ci/)
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    token_file = os.path.join(repo_root, ".github_token")
    if os.path.isfile(token_file):
        with open(token_file) as f:
            return f.read().strip()
    # 3. GitHub CLI (gh auth login)
    try:
        out = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0 and out.stdout:
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    print(
        "No token found. Use one of:\n"
        "  • GITHUB_TOKEN=ghp_xxx python ...\n"
        "  • echo ghp_xxx > .github_token (repo root)\n"
        "  • gh auth login",
        file=sys.stderr,
    )
    sys.exit(1)


def api(method: str, path: str, data: dict | None = None) -> dict:
    token = _get_token()
    url = f"{API}/repos/{REPO}{path}"
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if data:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {body}", file=sys.stderr)
        raise SystemExit(1)


def main() -> None:
    # 1. Get current ruleset
    print(f"Fetching ruleset {RULESET_ID}...")
    rs = api("GET", f"/rulesets/{RULESET_ID}")
    print(f"  Name: {rs.get('name')}, Target: {rs.get('target')}, Enforcement: {rs.get('enforcement')}")

    # 2. Build PUT body: same rules, but conditions = main only
    payload = {
        "name": rs.get("name", "Protect main"),
        "target": rs.get("target", "branch"),
        "enforcement": rs.get("enforcement", "active"),
        "conditions": {
            "ref_name": {
                "include": ["refs/heads/main"],
                "exclude": [],
            }
        },
        "rules": rs.get("rules", []),
    }
    if rs.get("bypass_actors") is not None:
        payload["bypass_actors"] = rs["bypass_actors"]

    # 3. Update
    print("Updating ruleset to target only refs/heads/main...")
    updated = api("PUT", f"/rulesets/{RULESET_ID}", payload)
    print(f"  Done. Target branches: {updated.get('conditions', {}).get('ref_name', {}).get('include', [])}")
    print("\nYou can now push: git push -u origin codex/ei-v2-hybrid-only-clean")


if __name__ == "__main__":
    main()
