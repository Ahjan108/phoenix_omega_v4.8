"""
ML Editorial & Market Intelligence — dashboard tab contract.
Exposes section scores, variant rankings, reader fit, rewrite recs, market actions for a UI tab.
See docs/ML_EDITORIAL_MARKET_LOOP_SPEC.md §9 and §11.
Usage:
  from scripts.dashboard.ml_editorial_tab import render_ml_editorial_tab, get_ml_editorial_summary
  # In Streamlit: render_ml_editorial_tab(repo_root=Path("."))
  # Or: summary = get_ml_editorial_summary(repo_root) for headless.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_jsonl(path: Path, limit: int = 500) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
                if len(out) >= limit:
                    break
            except json.JSONDecodeError:
                continue
    return out


def get_ml_editorial_summary(repo_root: Path | None = None) -> dict[str, Any]:
    """Return summary and recent rows for dashboard. No UI dependency."""
    repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
    base = repo_root / "artifacts" / "ml_editorial"
    section_scores = _load_jsonl(base / "section_scores.jsonl", 200)
    variant_rankings = _load_jsonl(base / "variant_rankings.jsonl", 200)
    reader_fit = _load_jsonl(base / "reader_fit_scores.jsonl", 200)
    rewrite_recs = _load_jsonl(base / "rewrite_recs.jsonl", 200)
    market_actions = _load_jsonl(base / "market_actions.jsonl", 200)
    weak_count = sum(1 for r in section_scores if (r.get("weak_flags") or []))
    return {
        "section_scores_count": len(section_scores),
        "variant_rankings_count": len(variant_rankings),
        "reader_fit_count": len(reader_fit),
        "rewrite_recs_count": len(rewrite_recs),
        "market_actions_count": len(market_actions),
        "weak_sections_count": weak_count,
        "recent_section_scores": section_scores[-20:],
        "recent_rewrite_recs": rewrite_recs[-20:],
        "recent_market_actions": market_actions[-20:],
        "artifacts_dir": str(base),
    }


def render_ml_editorial_tab(repo_root: Path | None = None) -> None:
    """Render Streamlit tab 'ML Editorial & Market Intelligence'. Call from app."""
    try:
        import streamlit as st
    except ImportError:
        return
    repo_root = repo_root or Path(__file__).resolve().parent.parent.parent
    summary = get_ml_editorial_summary(repo_root)
    st.subheader("ML Editorial & Market Intelligence")
    st.caption("Section scores, variant rankings, reader-fit, rewrite recommendations, market actions.")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Section scores", summary["section_scores_count"])
    col2.metric("Variant rankings", summary["variant_rankings_count"])
    col3.metric("Reader fit", summary["reader_fit_count"])
    col4.metric("Rewrite recs", summary["rewrite_recs_count"])
    col5.metric("Market actions", summary["market_actions_count"])
    st.metric("Weak sections (flagged)", summary["weak_sections_count"])
    with st.expander("Recent market actions"):
        for r in summary["recent_market_actions"]:
            st.json(r)
    with st.expander("Recent rewrite recommendations"):
        for r in summary["recent_rewrite_recs"]:
            st.json(r)
    st.caption(f"Artifacts: {summary['artifacts_dir']}")
