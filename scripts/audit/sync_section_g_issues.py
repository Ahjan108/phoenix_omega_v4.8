#!/usr/bin/env python3
"""
Sync Section G remediation items from config/audit/remediation_registry.yaml to GitHub issues.
Create issue if none exists for id; update body/labels/assignee if changed; close when status=done.
Writes artifacts/audit/remediation_issue_map.json.
Uses GITHUB_TOKEN for same-repo issue write.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_DIR = REPO_ROOT / "artifacts" / "audit"
CONFIG_AUDIT = REPO_ROOT / "config" / "audit"

# Label for audit-gap issues
LABELS = ["audit-gap", "truth-audit"]
PRIORITY_LABEL = {"P0": "priority:P0", "P1": "priority:P1", "P2": "priority:P2"}


def load_remediation_registry() -> list[dict]:
    path = CONFIG_AUDIT / "remediation_registry.yaml"
    if not path.exists():
        return []
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return data.get("remediation_items") or []
    except Exception as e:
        print(f"Failed to load remediation_registry.yaml: {e}", file=sys.stderr)
        return []


def load_existing_map() -> dict:
    path = AUDIT_DIR / "remediation_issue_map.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def gh_api(method: str, path: str, data: dict | None = None) -> dict | list:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return {}
    import urllib.request
    url = f"https://api.github.com/repos/{os.environ.get('GITHUB_REPOSITORY', 'Ahjan108/phoenix_omega_v4.8')}{path}"
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    if data:
        req.data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"GitHub API error: {e}", file=sys.stderr)
        return {}


def find_issue_by_title(title_prefix: str, label: str = "audit-gap") -> dict | None:
    repo = os.environ.get("GITHUB_REPOSITORY", "Ahjan108/phoenix_omega_v4.8")
    path = f"/issues?state=all&labels={label}&per_page=100"
    resp = gh_api("GET", path)
    if isinstance(resp, list):
        for i in resp:
            if (i.get("title") or "").startswith(title_prefix) or title_prefix in (i.get("title") or ""):
                return i
    return None


def create_issue(item: dict) -> dict | None:
    title = (item.get("title") or item.get("id", ""))[:256]
    body = f"**ID:** {item.get('id', '')}\n\n{item.get('description', '')}\n\n**Evidence refs:** {item.get('evidence_refs', [])}\n**Priority:** {item.get('priority', '')}\n**Owner:** {item.get('owner', '')}\n**Due date:** {item.get('due_date', '')}"
    labels = LABELS + [PRIORITY_LABEL.get(item.get("priority", ""), "priority:P2")]
    resp = gh_api("POST", "/issues", {"title": title, "body": body, "labels": labels})
    if isinstance(resp, dict) and resp.get("number"):
        return resp
    return None


def update_issue(number: int, item: dict, state: str | None = None) -> bool:
    body = f"**ID:** {item.get('id', '')}\n\n{item.get('description', '')}\n\n**Evidence refs:** {item.get('evidence_refs', [])}\n**Priority:** {item.get('priority', '')}\n**Owner:** {item.get('owner', '')}\n**Due date:** {item.get('due_date', '')}"
    data = {"body": body}
    if state:
        data["state"] = state
    resp = gh_api("PATCH", f"/issues/{number}", data)
    return isinstance(resp, dict) and resp.get("number") == number


def main() -> int:
    items = load_remediation_registry()
    if not items:
        print("No remediation items; nothing to sync.")
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        (AUDIT_DIR / "remediation_issue_map.json").write_text("{}", encoding="utf-8")
        return 0

    existing_map = load_existing_map()
    issue_map = dict(existing_map)
    errors = []

    for item in items:
        rid = item.get("id") or ""
        status = (item.get("status") or "open").strip().lower()
        if status == "done":
            if rid in issue_map and issue_map[rid]:
                num = issue_map[rid].get("number") if isinstance(issue_map[rid], dict) else issue_map[rid]
                if num:
                    update_issue(num, item, state="closed")
                issue_map[rid] = {"number": num, "state": "closed"}
            continue
        title = (item.get("title") or rid)[:80]
        if rid in issue_map and issue_map[rid]:
            num = issue_map[rid].get("number") if isinstance(issue_map[rid], dict) else issue_map[rid]
            if num:
                if not update_issue(num, item):
                    errors.append(f"Update failed for {rid} #{num}")
            continue
        created = find_issue_by_title(title) or create_issue(item)
        if created and created.get("number"):
            issue_map[rid] = {"number": created["number"], "url": created.get("html_url", ""), "state": created.get("state", "open")}
        elif not os.environ.get("GITHUB_TOKEN"):
            issue_map[rid] = {"number": None, "state": "open", "note": "no GITHUB_TOKEN"}
        else:
            errors.append(f"Could not create issue for {rid}")

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    (AUDIT_DIR / "remediation_issue_map.json").write_text(json.dumps(issue_map, indent=2), encoding="utf-8")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
