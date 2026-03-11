#!/usr/bin/env python3
"""
Remote-only commit review: list commits on main that were not made via a merged PR.
Produces a report for weekly triage (triage within 24h).
Outputs: artifacts/audit/remote_commit_review_YYYYMMDD.json and .md summary.
Uses GITHUB_TOKEN to fetch commits and PR merge info.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_DIR = REPO_ROOT / "artifacts" / "audit"


def get_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("  WARN: GITHUB_TOKEN not set; cannot fetch PR info.", file=sys.stderr)
    return token


def api_get(token: str, url: str) -> dict | list:
    import urllib.request

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


def list_commits_on_main(token: str, repo: str, since_iso: str) -> list[dict]:
    # repo e.g. "Ahjan108/phoenix_omega_v4.8" or "Ahjan108/phoenix_omega"
    url = (
        f"https://api.github.com/repos/{repo}/commits"
        f"?sha=main&since={since_iso}&per_page=100"
    )
    data = api_get(token, url)
    return data if isinstance(data, list) else []


def get_pull_for_commit(token: str, repo: str, sha: str) -> dict | None:
    url = f"https://api.github.com/repos/{repo}/commits/{sha}/pulls"
    try:
        data = api_get(token, url)
        if isinstance(data, list) and data:
            return data[0]
        return None
    except Exception:
        return None


def is_merge_commit_message(msg: str) -> bool:
    return bool(re.match(r"^Merge pull request #\d+", msg.strip()))


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "Ahjan108/phoenix_omega_v4.8").strip()
    token = get_token()

    since = datetime.now(UTC) - timedelta(days=7)
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    today = datetime.now(UTC).strftime("%Y%m%d")

    commits = list_commits_on_main(token, repo, since_iso) if token else []
    remote_only: list[dict] = []
    from_pr: list[dict] = []

    for c in commits:
        sha = c.get("sha", "")[:7]
        msg = (c.get("commit", {}) or {}).get("message", "")
        author = (c.get("commit", {}) or {}).get("author", {}) or {}
        author_name = author.get("name", "")
        date = (c.get("commit", {}) or {}).get("author", {}).get("date", "")

        if is_merge_commit_message(msg):
            from_pr.append({"sha": sha, "message_first_line": msg.split("\n")[0], "date": date})
            continue

        if token:
            pr = get_pull_for_commit(token, repo, c.get("sha", ""))
            if pr and pr.get("merged_at"):
                from_pr.append({"sha": sha, "message_first_line": msg.split("\n")[0][:80], "date": date})
                continue

        remote_only.append({
            "sha": sha,
            "message_first_line": msg.split("\n")[0][:80],
            "date": date,
            "author": author_name,
        })

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "repo": repo,
        "since": since_iso,
        "commits_total": len(commits),
        "from_pr_or_merge": len(from_pr),
        "remote_only": remote_only,
        "remote_only_count": len(remote_only),
    }

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = AUDIT_DIR / f"remote_commit_review_{today}.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_lines = [
        "# Remote-only commit review",
        "",
        f"**Generated:** {report['generated_at']}",
        f"**Repo:** {repo}",
        f"**Since:** {since_iso}",
        "",
        f"**Total commits on main (7d):** {report['commits_total']}",
        f"**From PR / merge commit:** {report['from_pr_or_merge']}",
        f"**Remote-only (no linked PR):** {report['remote_only_count']}",
        "",
        "## Triage within 24h",
        "",
    ]
    if remote_only:
        md_lines.append("| SHA | Date | Author | Message |")
        md_lines.append("|-----|------|--------|---------|")
        for r in remote_only:
            md_lines.append(f"| {r['sha']} | {r['date'][:10]} | {r.get('author', '')} | {r['message_first_line'][:60]} |")
        md_lines.append("")
    else:
        md_lines.append("No remote-only commits in the last 7 days.")
        md_lines.append("")

    md_path = AUDIT_DIR / f"remote_commit_review_{today}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Report: {json_path}")
    print(f"Summary: {md_path}")
    print(f"  Remote-only commits: {report['remote_only_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
