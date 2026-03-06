"""
PhoenixControl Executive Dashboard — Streamlit entry point.
Authority: docs/EXECUTIVE_DASHBOARD_AND_PHOENIXCONTROL_SPEC.md

Launch:
  streamlit run dashboard.py
  streamlit run dashboard.py -- --repo /path/to/phoenix_omega

Or from PhoenixControl Mac app:
  streamlit run /path/to/dashboard.py --server.headless true

Reads REPO_PATH env var (set by Mac app) or falls back to cwd.
GITHUB_TOKEN env var required for GitHub tab (use: export GITHUB_TOKEN=$(gh auth token))
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

# ── Repo root ─────────────────────────────────────────────────────────────────
REPO_ROOT = Path(os.environ.get("REPO_PATH", ".")).resolve()
sys.path.insert(0, str(REPO_ROOT))

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="PhoenixControl",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Sidebar — repo path + token status ───────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔥 PhoenixControl")
    st.caption(f"Repo: `{REPO_ROOT}`")

    # GitHub token status
    gh_token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not gh_token:
        try:
            import subprocess
            result = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                gh_token = result.stdout.strip()
        except Exception:
            pass

    if gh_token:
        st.success("GitHub ✅")
    else:
        st.warning("GitHub ⚠️ — set GITHUB_TOKEN")
        st.code("export GITHUB_TOKEN=$(gh auth token)", language="bash")

    st.divider()
    st.caption("v4.8 · Pearl Prime")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_github, tab_pearl_news, tab_pipeline, tab_ei, tab_system = st.tabs([
    "🔗 GitHub",
    "📰 Pearl News",
    "⚙️ Pipeline",
    "🧠 EI v2 / Marketing",
    "📊 System",
])

# ── GitHub Tab ────────────────────────────────────────────────────────────────
with tab_github:
    try:
        from scripts.dashboard.github_tab import render_github_tab
        render_github_tab(token=gh_token or None)
    except ImportError as e:
        st.error(f"Import error: {e}")

# ── Pearl News Tab ────────────────────────────────────────────────────────────
with tab_pearl_news:
    st.header("📰 Pearl News")

    drafts_dir = REPO_ROOT / "Qwen-Agent" / "artifacts" / "pearl_news" / "drafts"
    review_queue = drafts_dir / "manual_review_queue.json"
    build_manifest = drafts_dir / "build_manifests.json"

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pipeline Output")
        if build_manifest.exists():
            import json
            with open(build_manifest) as f:
            manifest_data = json.load(f)
            records = manifest_data if isinstance(manifest_data, list) else [manifest_data]
            st.metric("Articles written", len(records))
            if records:
                latest = records[-1]
                st.metric("Build date", latest.get("built_at", "—")[:10])
                passed = latest.get("validation", {}).get("passed", None)
                gates = latest.get("validation", {}).get("passed_count", "?")
                total = latest.get("validation", {}).get("gate_count", "?")
                status = "✅" if passed else "⚠️"
                st.caption(f"Language: {latest.get('language', '—')} · Validation: {status} {gates}/{total} gates")
            # build_manifests.json is a list of article records
            records = manifest_data if isinstance(manifest_data, list) else [manifest_data]
            st.metric("Articles written", len(records))
            if records:
                latest = records[-1]
                built_at = latest.get("built_at", "—")[:10]
                st.metric("Build date", built_at)
                lang = latest.get("language", "—")
                passed = latest.get("validation", {}).get("passed", None)
                gates = latest.get("validation", {}).get("passed_count", "?")
                total = latest.get("validation", {}).get("gate_count", "?")
                status = "✅" if passed else "⚠️"
                st.caption(f"Language: {lang} · Validation: {status} {gates}/{total} gates")
        else:
            st.info("No build manifest yet — run the pipeline first.")

    with col2:
        st.subheader("Manual Review Queue")
        if review_queue.exists():
            import json
            with open(review_queue) as f:
                queue = json.load(f)
            if queue:
                st.warning(f"{len(queue)} article(s) need review")
                for item in queue:
                    with st.expander(
                        f"⚠️ {item.get('title', item.get('article_id', '?'))[:60]}"
                    ):
                        st.write("**Failed gates:**", item.get("failed_gates", []))
                        st.write("**Topic:**", item.get("topic", "—"))
                        st.write("**Queued:**", item.get("queued_at", "—")[:19])
                        content = item.get("expanded_content", "")
                        if content:
                            st.markdown("**Expanded content preview:**")
                            st.code(content[:1500], language="html")
            else:
                st.success("Review queue is empty")
        else:
            st.info("No review queue file yet.")

    st.divider()
    st.subheader("Run Pipeline")
    st.code(
        "cd ~/phoenix_omega/Qwen-Agent\n"
        "PYTHONPATH=. python3 -m pearl_news.pipeline.run_article_pipeline \\\n"
        "  --feeds pearl_news/config/feeds.yaml \\\n"
        "  --out-dir artifacts/pearl_news/drafts \\\n"
        "  --limit 1 --expand --validate --select-image",
        language="bash",
    )
    st.caption("Or trigger via GitHub tab → ▶ Run Pearl News Expand")

# ── Pipeline Tab ─────────────────────────────────────────────────────────────
with tab_pipeline:
    st.header("⚙️ Pipeline & Gates")

    import subprocess

    col_gates, col_scripts = st.columns([2, 1])

    with col_gates:
        st.subheader("Production Readiness Gates")
        gates_path = REPO_ROOT / "artifacts" / "observability" / "evidence_log.jsonl"
        if gates_path.exists():
            import json
            rows = []
            with open(gates_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            rows.append(json.loads(line))
                        except Exception:
                            pass
            if rows:
                import pandas as pd
                df = pd.DataFrame(rows[-50:])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Evidence log is empty.")
        else:
            st.info(f"No evidence log at `{gates_path.relative_to(REPO_ROOT)}`")

    with col_scripts:
        st.subheader("Quick Actions")
        if st.button("▶ Run Production Readiness Gates"):
            with st.spinner("Running gates…"):
                result = subprocess.run(
                    [sys.executable, "scripts/run_production_readiness_gates.py"],
                    cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120
                )
            if result.returncode == 0:
                st.success("Gates passed")
            else:
                st.error("Gates failed")
            st.code(result.stdout[-2000:] + result.stderr[-1000:])

        if st.button("▶ Validate Freebie Density"):
            with st.spinner("Running…"):
                result = subprocess.run(
                    [sys.executable, "phoenix_v4/qa/validate_freebie_density.py"],
                    cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60
                )
            st.code(result.stdout[-1500:] + result.stderr[-500:])

# ── EI v2 / Marketing Tab ─────────────────────────────────────────────────────
with tab_ei:
    st.header("🧠 EI v2 / Marketing")
    try:
        from scripts.ei_v2_marketing_dashboard_tab import render_marketing_tab
        render_marketing_tab(repo_root=REPO_ROOT)
    except ImportError:
        st.info("EI v2 marketing tab module not found — check scripts/ei_v2_marketing_dashboard_tab.py")
    except Exception as e:
        st.error(f"Error loading EI v2 tab: {e}")

    st.divider()
    try:
        from scripts.dashboard.ml_editorial_tab import render_ml_editorial_tab
        render_ml_editorial_tab(repo_root=REPO_ROOT)
    except ImportError:
        pass
    except Exception as e:
        st.error(f"ML editorial tab error: {e}")

# ── System Tab ────────────────────────────────────────────────────────────────
with tab_system:
    st.header("📊 System")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Repo Health")
        import subprocess
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            cwd=str(REPO_ROOT), capture_output=True, text=True
        )
        st.code(result.stdout, language="bash")

        result2 = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(REPO_ROOT), capture_output=True, text=True
        )
        st.caption("Working tree status")
        st.code(result2.stdout or "(clean)", language="bash")

    with col_b:
        st.subheader("Observability")
        obs_path = REPO_ROOT / "artifacts" / "observability"
        if obs_path.exists():
            for f in sorted(obs_path.glob("*.jsonl"))[:5]:
                import os
                size = os.path.getsize(f)
                st.caption(f"`{f.name}` — {size:,} bytes")
        else:
            st.info("No observability artifacts yet.")

        st.subheader("Open Evidence Files")
        ev_log = REPO_ROOT / "artifacts" / "observability" / "evidence_log.jsonl"
        if ev_log.exists():
            st.markdown(f"[evidence\_log.jsonl](file://{ev_log})")
        checklist = REPO_ROOT / "docs" / "GO_LIVE_FINAL_CHECKLIST.md"
        if checklist.exists():
            st.markdown(f"[GO\_LIVE\_FINAL\_CHECKLIST.md](file://{checklist})")
