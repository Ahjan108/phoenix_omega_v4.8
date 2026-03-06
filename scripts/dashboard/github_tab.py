"""
GitHub Status Tab — PhoenixControl Executive Dashboard.
Authority: docs/EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md §6 (Agent change feed)

Shows live workflow run status, open PRs, and workflow dispatch triggers
for both repos: phoenix_omega_v4.8 and Qwen-Agent (Pearl News).

Requires: GITHUB_TOKEN env var (set via `gh auth token` or ~/.env)
Usage (standalone test): streamlit run scripts/dashboard/github_tab.py
Usage (in dashboard.py): from scripts.dashboard.github_tab import render_github_tab
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

import requests

# ── Config ────────────────────────────────────────────────────────────────────

REPOS = {
    "phoenix_omega": "Ahjan108/phoenix_omega_v4.8",
    "qwen_agent":    "Ahjan108/Qwen-Agent",
}

# Key workflows to surface in the dashboard (workflow filename → display name)
WATCHED_WORKFLOWS = {
    "Ahjan108/phoenix_omega_v4.8": {
        "core-tests.yml":               "Core Tests",
        "release-gates.yml":            "Release Gates",
        "audiobook-regression.yml":     "Audiobook Regression",
        "ei-v2-gates.yml":              "EI V2 Gates",
        "github-governance-check.yml":  "GitHub Governance",
        "production-observability.yml": "Production Observability",
        "docs-ci.yml":                  "Docs CI",
    },
    "Ahjan108/Qwen-Agent": {
        "pearl_news_scheduled.yml":     "Pearl News (Scheduled)",
        "pearl_news_manual_expand.yml": "Pearl News (Manual Expand)",
    },
}

# Workflows that can be triggered via workflow_dispatch from the dashboard
DISPATCHABLE = {
    "Ahjan108/phoenix_omega_v4.8": [
        ("release-gates.yml",        "Run Release Gates"),
        ("audiobook-regression.yml", "Run Audiobook Regression"),
    ],
    "Ahjan108/Qwen-Agent": [
        ("pearl_news_manual_expand.yml", "Run Pearl News Expand"),
    ],
}

GH_API = "https://api.github.com"


# ── GitHub API helpers ────────────────────────────────────────────────────────

def _token() -> str | None:
    """Read GITHUB_TOKEN from env, then try gh CLI."""
    t = os.environ.get("GITHUB_TOKEN", "").strip()
    if t:
        return t
    try:
        import subprocess
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get(path: str, token: str, params: dict | None = None) -> dict | list | None:
    url = f"{GH_API}{path}"
    try:
        r = requests.get(url, headers=_headers(token), params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        return {"_error": r.status_code, "_msg": r.text[:200]}
    except Exception as e:
        return {"_error": "request_failed", "_msg": str(e)}


def _post(path: str, token: str, body: dict) -> tuple[bool, str]:
    url = f"{GH_API}{path}"
    try:
        r = requests.post(url, headers=_headers(token), json=body, timeout=10)
        if r.status_code in (204, 200, 201):
            return True, "Triggered successfully"
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def _age(ts: str | None) -> str:
    """Convert ISO timestamp to human-readable age."""
    if not ts:
        return "—"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        s = int(delta.total_seconds())
        if s < 60:
            return f"{s}s ago"
        if s < 3600:
            return f"{s // 60}m ago"
        if s < 86400:
            return f"{s // 3600}h ago"
        return f"{s // 86400}d ago"
    except Exception:
        return ts[:10]


def _status_emoji(conclusion: str | None, status: str | None) -> str:
    if status in ("in_progress", "queued", "waiting"):
        return "⏳"
    c = (conclusion or "").lower()
    return {
        "success": "✅",
        "failure": "❌",
        "cancelled": "🚫",
        "skipped": "⏭️",
        "timed_out": "⏱️",
        "action_required": "⚠️",
    }.get(c, "❓")


# ── Data fetchers ─────────────────────────────────────────────────────────────

def fetch_workflow_runs(repo: str, token: str) -> list[dict]:
    """Fetch the latest run for each watched workflow in this repo."""
    watched = WATCHED_WORKFLOWS.get(repo, {})
    results = []
    for filename, display_name in watched.items():
        data = _get(
            f"/repos/{repo}/actions/workflows/{filename}/runs",
            token,
            params={"per_page": 1},
        )
        if isinstance(data, dict) and "workflow_runs" in data:
            runs = data["workflow_runs"]
            if runs:
                r = runs[0]
                results.append({
                    "workflow": display_name,
                    "filename": filename,
                    "status": r.get("status", "—"),
                    "conclusion": r.get("conclusion"),
                    "branch": r.get("head_branch", "—"),
                    "started": _age(r.get("created_at")),
                    "url": r.get("html_url", ""),
                    "run_id": r.get("id"),
                })
            else:
                results.append({
                    "workflow": display_name,
                    "filename": filename,
                    "status": "never_run",
                    "conclusion": None,
                    "branch": "—",
                    "started": "—",
                    "url": "",
                    "run_id": None,
                })
        else:
            results.append({
                "workflow": display_name,
                "filename": filename,
                "status": "error",
                "conclusion": None,
                "branch": "—",
                "started": "—",
                "url": "",
                "run_id": None,
            })
    return results


def fetch_open_prs(repo: str, token: str) -> list[dict]:
    data = _get(f"/repos/{repo}/pulls", token, params={"state": "open", "per_page": 10})
    if not isinstance(data, list):
        return []
    return [
        {
            "number": pr.get("number"),
            "title": pr.get("title", "—")[:70],
            "author": pr.get("user", {}).get("login", "—"),
            "branch": pr.get("head", {}).get("ref", "—"),
            "created": _age(pr.get("created_at")),
            "url": pr.get("html_url", ""),
            "draft": pr.get("draft", False),
        }
        for pr in data
    ]


def trigger_workflow(repo: str, workflow_file: str, token: str, branch: str = "main") -> tuple[bool, str]:
    ok, msg = _post(
        f"/repos/{repo}/actions/workflows/{workflow_file}/dispatches",
        token,
        {"ref": branch},
    )
    return ok, msg


# ── Streamlit render ──────────────────────────────────────────────────────────

def render_github_tab(token: str | None = None) -> None:
    """Render the full GitHub tab. Call from dashboard.py inside a tab."""
    try:
        import streamlit as st
    except ImportError:
        print("streamlit not installed — run: pip install streamlit")
        return

    token = token or _token()

    st.header("🔗 GitHub — Live Status")

    if not token:
        st.error(
            "**GITHUB_TOKEN not found.** Set it in your environment:\n\n"
            "```bash\nexport GITHUB_TOKEN=$(gh auth token)\n```\n\n"
            "Then restart the dashboard."
        )
        return

    # Auto-refresh control
    col_refresh, col_age = st.columns([1, 3])
    with col_refresh:
        refresh = st.button("🔄 Refresh now")
    with col_age:
        st.caption(f"Last loaded: {datetime.now().strftime('%H:%M:%S')}")

    # ── Per-repo sections ──────────────────────────────────────────────────
    for repo_key, repo_full in REPOS.items():
        repo_label = {
            "phoenix_omega": "phoenix\_omega\_v4.8",
            "qwen_agent":    "Qwen-Agent (Pearl News)",
        }.get(repo_key, repo_full)

        st.subheader(f"📦 {repo_label}")
        st.caption(f"[github.com/{repo_full}](https://github.com/{repo_full})")

        runs_col, prs_col = st.columns([3, 2])

        # ── Workflow runs ───────────────────────────────────────────────
        with runs_col:
            st.markdown("**Workflow Runs**")
            with st.spinner("Fetching runs…"):
                runs = fetch_workflow_runs(repo_full, token)

            for run in runs:
                emoji = _status_emoji(run["conclusion"], run["status"])
                label = f"{emoji} **{run['workflow']}**"
                detail = f"`{run['branch']}` · {run['started']}"
                if run["url"]:
                    st.markdown(f"{label} — [{detail}]({run['url']})")
                else:
                    st.markdown(f"{label} — {detail} _(never run)_")

        # ── Open PRs ────────────────────────────────────────────────────
        with prs_col:
            st.markdown("**Open Pull Requests**")
            with st.spinner("Fetching PRs…"):
                prs = fetch_open_prs(repo_full, token)

            if not prs:
                st.caption("No open PRs")
            for pr in prs:
                draft_tag = " `draft`" if pr["draft"] else ""
                st.markdown(
                    f"[#{pr['number']} {pr['title']}]({pr['url']}){draft_tag}  \n"
                    f"<small>{pr['branch']} · {pr['author']} · {pr['created']}</small>",
                    unsafe_allow_html=True,
                )

        # ── Dispatch triggers ───────────────────────────────────────────
        dispatchable = DISPATCHABLE.get(repo_full, [])
        if dispatchable:
            st.markdown("**Trigger Workflows**")
            branch_input = st.text_input(
                "Branch", value="main", key=f"branch_{repo_key}",
                help="Branch to dispatch on"
            )
            btn_cols = st.columns(len(dispatchable))
            for i, (wf_file, btn_label) in enumerate(dispatchable):
                with btn_cols[i]:
                    if st.button(f"▶ {btn_label}", key=f"dispatch_{repo_key}_{i}"):
                        with st.spinner(f"Triggering {wf_file}…"):
                            ok, msg = trigger_workflow(
                                repo_full, wf_file, token, branch=branch_input
                            )
                        if ok:
                            st.success(f"✅ {msg} — check Workflow Runs above in ~10s")
                        else:
                            st.error(f"❌ {msg}")

        st.divider()

    # ── Recent runs across both repos (flat list) ─────────────────────────
    with st.expander("📋 All recent workflow runs (both repos)", expanded=False):
        for repo_full in REPOS.values():
            runs = fetch_workflow_runs(repo_full, token)
            for run in runs:
                if run["url"]:
                    emoji = _status_emoji(run["conclusion"], run["status"])
                    st.markdown(
                        f"{emoji} [{run['workflow']}]({run['url']}) — "
                        f"`{repo_full.split('/')[1]}` · `{run['branch']}` · {run['started']}"
                    )


# ── Standalone entry (streamlit run scripts/dashboard/github_tab.py) ─────────
if __name__ == "__main__":
    try:
        import streamlit as st
        st.set_page_config(page_title="GitHub Status", layout="wide")
        render_github_tab()
    except ImportError:
        # Headless test: print token status
        t = _token()
        print(f"Token found: {'yes (' + t[:8] + '...)' if t else 'NO — set GITHUB_TOKEN'}")
        for repo in REPOS.values():
            if t:
                runs = fetch_workflow_runs(repo, t)
                print(f"\n{repo}:")
                for r in runs:
                    print(f"  {_status_emoji(r['conclusion'], r['status'])} {r['workflow']} — {r['started']}")
