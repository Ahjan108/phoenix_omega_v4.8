"""
EI v2 Marketing Integration — Streamlit dashboard tab.

Drop into your Streamlit v1 app under a Marketing tab:
  from scripts.ei_v2_marketing_dashboard_tab import render_marketing_tab
  render_marketing_tab(log_path=None, repo_root=None)

Log format: artifacts/ei_v2/marketing_integration.log (JSONL).
Fields: ts, event, source, source_path, file_02_hash, file_03_hash, file_04_hash, fallback_reason.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

EXPECTED_LOG_PATH = "artifacts/ei_v2/marketing_integration.log"


def _parse_log_safe(log_path: Path) -> tuple[List[Dict[str, Any]], int]:
    """Parse JSONL; return (valid records, malformed_line_count). Skip bad lines, don't break."""
    records: List[Dict[str, Any]] = []
    malformed = 0
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    malformed += 1
                    continue
                records.append(obj)
            except (json.JSONDecodeError, TypeError):
                malformed += 1
                continue
    return records, malformed


def render_marketing_tab(
    log_path: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> None:
    """Render the EI v2 Marketing Integration section. Requires streamlit, pandas."""
    try:
        import streamlit as st
    except ImportError:
        print("streamlit not installed; run: pip install streamlit")
        return

    repo_root = repo_root or Path.cwd()
    log_path = log_path or repo_root / EXPECTED_LOG_PATH

    st.subheader("EI v2 Marketing Integration")
    st.caption("Lexicon source, file hashes, and fallback reasons from marketing_integration.log")

    if not log_path.exists():
        st.warning("Log file not found — integration inactive or first run.")
        st.write("**No events found.** To enable logging:")
        st.write("1. Set `marketing_sources.enabled: true` in `config/quality/ei_v2_config.yaml`")
        st.write("2. Run EI v2 (e.g. pipeline or rigorous eval) so the loader writes to the log.")
        st.write("**Expected path:**")
        st.code(str(log_path), language="text")
        return

    records, malformed = _parse_log_safe(log_path)
    if malformed > 0:
        st.warning(f"Schema/parse: {malformed} malformed or non-dict line(s) skipped. Rest of log rendered.")

    if not records:
        st.warning("No events found.")
        st.write("To get events: set `marketing_sources.enabled: true` in `config/quality/ei_v2_config.yaml` and run EI v2. Log path:")
        st.code(str(log_path), language="text")
        return

    try:
        import pandas as pd
    except ImportError:
        st.error("pandas required for this tab. pip install pandas")
        return

    log_df = pd.DataFrame(records)
    if "ts" not in log_df.columns:
        log_df["ts"] = ""
    log_df["ts"] = pd.to_datetime(log_df["ts"], errors="coerce")
    log_df = log_df.dropna(subset=["ts"]).sort_values("ts")
    if log_df.empty:
        st.warning("No events with valid `ts` in log. Check log format (expected: ts, event, source, ...).")
        return
    tail = log_df.tail(100)

    # Freshness: last event age
    last_ts = log_df["ts"].max()
    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)
        delta = now - last_ts
        if delta.days > 0:
            age_str = f"{delta.days} day(s) ago"
        elif delta.seconds >= 3600:
            age_str = f"{delta.seconds // 3600} hour(s) ago"
        elif delta.seconds >= 60:
            age_str = f"{delta.seconds // 60} min ago"
        else:
            age_str = "just now"
        st.metric("Last event age", age_str, last_ts.strftime("%Y-%m-%d %H:%M UTC"))
    except Exception:
        st.caption(f"Last event: {last_ts}")

    st.write("**Last 100 events**")
    display_cols = [c for c in ["ts", "event", "source", "source_path", "fallback_reason"] if c in tail.columns]
    if display_cols:
        st.dataframe(tail[display_cols].iloc[::-1], use_container_width=True, height=300)
    else:
        st.caption("No standard columns (ts, event, source, ...) in log records.")

    # File hash status: use .get so missing fields don't break
    st.write("**File hash status (most recent load)**")
    last = tail.iloc[-1]
    last_dict = last.to_dict() if hasattr(last, "to_dict") else dict(last) if hasattr(last, "keys") else {}
    hash_cols = ["file_02_hash", "file_03_hash", "file_04_hash"]
    if any(last_dict.get(c) for c in hash_cols):
        hash_df = pd.DataFrame({
            "file": ["02_emotional_vocabulary_patch.yaml", "03_consumer_language_by_topic.yaml", "04_invisible_scripts.yaml"],
            "hash": [str(last_dict.get(c, "")) for c in hash_cols],
        })
        st.dataframe(hash_df, use_container_width=True, hide_index=True)
    else:
        st.caption("Hash fields missing in most recent record.")

    source = last_dict.get("source", "")
    if source:
        st.metric("Lexicon source", source, "built-in → fallback" if source == "built-in" else "marketing active")

    if last_dict.get("fallback_reason"):
        st.warning("Fallback: " + str(last_dict["fallback_reason"]))

    # Optional: events by source over time (compact chart) if Plotly available
    try:
        import plotly.express as px
        if "source" in log_df.columns and "ts" in log_df.columns and len(log_df) > 0:
            by_date_source = log_df.assign(date=log_df["ts"].dt.date).groupby(["date", "source"]).size().reset_index(name="count")
            fig = px.bar(by_date_source, x="date", y="count", color="source", title="Events by source over time", barmode="stack")
            fig.update_layout(height=220, margin=dict(t=40, b=30, l=40, r=20))
            st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        pass

    st.write("**Calibration (locked thresholds)**")
    st.caption("domain_thesis_similarity Δ ≤ 0.12, safety Δ ≤ 0.10. From calibration test or future log events.")
    cal = log_df[log_df.get("event") == "calibration"] if "event" in log_df.columns else pd.DataFrame()
    if not cal.empty and "domain_thesis_delta" in cal.columns and "safety_delta" in cal.columns:
        deltas = cal.agg({"domain_thesis_delta": "max", "safety_delta": "max"}).iloc[0]
        st.metric("Max domain Δ", f"{deltas.get('domain_thesis_delta', 0):.3f}", "≤ 0.12 ✓" if deltas.get("domain_thesis_delta", 0) <= 0.12 else "> 0.12")
        st.metric("Max safety Δ", f"{deltas.get('safety_delta', 0):.3f}", "≤ 0.10 ✓" if deltas.get("safety_delta", 0) <= 0.10 else "> 0.10")
    else:
        st.info("No calibration events in log yet. Run tests/test_ei_v2_marketing_lexicons.py calibration test; optional: write calibration results to this log.")


if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(page_title="EI v2 Marketing", layout="wide")
    render_marketing_tab()
