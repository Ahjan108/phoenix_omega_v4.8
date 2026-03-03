"""
Phase 12 — Unified Platform Health Scorecard (UPHS).

Read-only aggregation: does not recompute. Loads outputs from:
- Coverage Health (v1.1)
- Catalog Emotional Distribution (Phase 9 standalone)
- Cross-Brand Divergence (Phase 10)
- Brand Identity Stability (Phase 11)

Produces single composite score 0–1 and tier (STABLE / WATCH / RISK / CRITICAL).

Output: artifacts/ops/platform_health_scorecard_{date}.json (+ optional .md)

Exit: 0 STABLE/WATCH, 2 RISK, 1 CRITICAL.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def compute_coverage_health_score(
    data: Optional[dict],
    config: dict,
) -> tuple[float, bool]:
    """
    CHS = 0.40*GREEN_ratio + 0.20*(1-BLOCKER_ratio) + 0.20*(1-RED_ratio) + 0.20*velocity_score.
    Returns (score, loaded).
    """
    if not data:
        return 0.5, False
    summary = data.get("summary") or {}
    risk = summary.get("risk_counts") or {}
    total = int(summary.get("total_tuples") or 0)
    if total <= 0:
        return 0.5, True
    green_r = (int(risk.get("GREEN") or 0)) / total
    blocker_r = (int(risk.get("BLOCKER") or 0)) / total
    red_r = (int(risk.get("RED") or 0)) / total
    vel = summary.get("velocity") or {}
    delta = vel.get("week_over_week_story_delta_total")
    threshold = config.get("platform_health_scorecard") or {}
    vel_thresh = int(threshold.get("velocity_delta_threshold", 10))
    if delta is not None and vel_thresh > 0:
        velocity_score = 1.0 if delta >= vel_thresh else _clamp01((delta + vel_thresh) / (2 * vel_thresh))
    else:
        velocity_score = 0.5
    stagnation = (data.get("alerts") or {}).get("stagnation") or {}
    if (stagnation.get("by_persona") or stagnation.get("by_topic")):
        velocity_score *= 0.85
    chs = 0.40 * green_r + 0.20 * (1.0 - blocker_r) + 0.20 * (1.0 - red_r) + 0.20 * velocity_score
    return _clamp01(chs), True


def compute_emotional_distribution_score(
    data: Optional[dict],
    config: dict,
) -> tuple[float, bool]:
    """
    EDS = 0.40*entropy + 0.30*volatility + 0.30*band_5_share_normalized.
    Penalties: entropy alert *0.85, drift alert *0.90.
    """
    if not data:
        return 0.5, False
    global_ = data.get("global") or {}
    entropy = float(global_.get("band_entropy_norm", 0))
    volatility = float(global_.get("avg_volatility", 0))
    band5 = float(global_.get("band_5_share", 0))
    cfg = config.get("platform_health_scorecard") or {}
    target = float(cfg.get("band_5_share_target", 0.06))
    band5_norm = _clamp01(band5 / target) if target > 0 else 0.0
    eds = 0.40 * entropy + 0.30 * _clamp01(volatility) + 0.30 * band5_norm
    penalties = cfg.get("penalties") or {}
    alerts = data.get("alerts") or []
    for a in alerts:
        code = (a.get("code") or "").upper()
        if "ENTROPY" in code:
            eds *= float(penalties.get("entropy_alert", 0.85))
            break
    for a in alerts:
        code = (a.get("code") or "").upper()
        if "DRIFT" in code:
            eds *= float(penalties.get("drift_alert_emotional", 0.90))
            break
    return _clamp01(eds), True


def compute_cross_brand_divergence_score(
    data: Optional[dict],
    config: dict,
) -> tuple[float, bool]:
    """
    CBD_score = min(pairwise CBDI scores). Penalty 0.9 if below warn, 0.7 if below fail.
    """
    if not data:
        return 0.5, False
    pairs = data.get("pairwise_scores") or []
    if not pairs:
        return 0.5, True
    min_score = min((p.get("score", 0) for p in pairs), default=0)
    min_score = float(min_score)
    cfg = config.get("cross_brand_divergence") or {}
    th = cfg.get("thresholds") or {}
    warn_below = float(th.get("warn_below", 0.18))
    fail_below = float(th.get("fail_below", 0.12))
    penalties = (config.get("platform_health_scorecard") or {}).get("penalties") or {}
    if min_score < fail_below:
        min_score *= float(penalties.get("divergence_fail", 0.70))
    elif min_score < warn_below:
        min_score *= float(penalties.get("divergence_warn", 0.90))
    return _clamp01(min_score), True


def compute_brand_identity_stability_score(
    data: Optional[dict],
    config: dict,
) -> tuple[float, bool]:
    """
    BISI_score = min(1 - drift_score) across brands. Penalty 0.7 if any critical.
    """
    if not data:
        return 0.5, False
    results = data.get("results") or []
    if not results:
        return 0.5, True
    stabilities = [1.0 - float(r.get("drift_score", 0)) for r in results]
    score = min(stabilities) if stabilities else 0.5
    score = _clamp01(score)
    alerts = data.get("alerts") or []
    penalties = (config.get("platform_health_scorecard") or {}).get("penalties") or {}
    for a in alerts:
        if (a.get("code") or "").upper() == "BRAND_IDENTITY_DRIFT_CRITICAL":
            score *= float(penalties.get("identity_critical", 0.70))
            break
    return _clamp01(score), True


def run(
    report_date: str,
    ops_dir: Path,
    config: dict,
) -> dict[str, Any]:
    """Load four artifacts, compute component scores and composite. Returns scorecard dict."""
    cfg = config.get("platform_health_scorecard") or {}
    weights = cfg.get("weights") or {}
    w_ch = float(weights.get("coverage_health", 0.35))
    w_ed = float(weights.get("emotional_distribution", 0.25))
    w_cbd = float(weights.get("cross_brand_divergence", 0.20))
    w_bis = float(weights.get("brand_identity_stability", 0.20))
    tiers_cfg = cfg.get("tiers") or {}
    t_stable = float(tiers_cfg.get("stable", 0.85))
    t_watch = float(tiers_cfg.get("watch", 0.70))
    t_risk = float(tiers_cfg.get("risk", 0.55))

    ch_path = ops_dir / f"coverage_health_weekly_{report_date}.json"
    ed_path = ops_dir / f"catalog_emotional_distribution_{report_date}.json"
    cbd_path = ops_dir / f"cross_brand_divergence_{report_date}.json"
    bis_path = ops_dir / f"brand_identity_stability_{report_date}.json"

    ch_data = _load_json(ch_path)
    ed_data = _load_json(ed_path)
    cbd_data = _load_json(cbd_path)
    bis_data = _load_json(bis_path)

    chs, ch_ok = compute_coverage_health_score(ch_data, config)
    eds, ed_ok = compute_emotional_distribution_score(ed_data, config)
    cbd_s, cbd_ok = compute_cross_brand_divergence_score(cbd_data, config)
    bis_s, bis_ok = compute_brand_identity_stability_score(bis_data, config)

    # If a component is missing, use 0.5 for it and renormalize weights to present components only
    comp_weights = []
    if ch_ok:
        comp_weights.append(("coverage_health_score", chs, w_ch))
    else:
        comp_weights.append(("coverage_health_score", 0.5, w_ch))
    if ed_ok:
        comp_weights.append(("emotional_distribution_score", eds, w_ed))
    else:
        comp_weights.append(("emotional_distribution_score", 0.5, w_ed))
    if cbd_ok:
        comp_weights.append(("cross_brand_divergence_score", cbd_s, w_cbd))
    else:
        comp_weights.append(("cross_brand_divergence_score", 0.5, w_cbd))
    if bis_ok:
        comp_weights.append(("brand_identity_stability_score", bis_s, w_bis))
    else:
        comp_weights.append(("brand_identity_stability_score", 0.5, w_bis))

    total_w = sum(w for _, _, w in comp_weights)
    composite = sum(s * w for _, s, w in comp_weights) / total_w if total_w > 0 else 0.5
    composite = round(_clamp01(composite), 4)

    if composite >= t_stable:
        tier = "STABLE"
    elif composite >= t_watch:
        tier = "WATCH"
    elif composite >= t_risk:
        tier = "RISK"
    else:
        tier = "CRITICAL"

    components = {
        "coverage_health_score": round(chs, 4),
        "emotional_distribution_score": round(eds, 4),
        "cross_brand_divergence_score": round(cbd_s, 4),
        "brand_identity_stability_score": round(bis_s, 4),
    }

    coverage_alerts = 0
    if ch_data:
        a = ch_data.get("alerts") or {}
        coverage_alerts = len((a.get("stagnation") or {}).get("by_persona") or []) + len((a.get("stagnation") or {}).get("by_topic") or []) + len((a.get("decay") or {}).get("global") or [])
    entropy_alerts = len([x for x in (ed_data or {}).get("alerts") or [] if "ENTROPY" in (x.get("code") or "").upper() or "VOLATILITY" in (x.get("code") or "").upper() or "BAND5" in (x.get("code") or "").upper()])
    divergence_alerts = len((cbd_data or {}).get("alerts") or [])
    identity_alerts = len((bis_data or {}).get("alerts") or [])

    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_date": report_date,
        "components": components,
        "composite_score": composite,
        "tier": tier,
        "sources_loaded": {
            "coverage_health": ch_ok,
            "catalog_emotional_distribution": ed_ok,
            "cross_brand_divergence": cbd_ok,
            "brand_identity_stability": bis_ok,
        },
        "alerts_summary": {
            "coverage_alerts": coverage_alerts,
            "entropy_alerts": entropy_alerts,
            "divergence_alerts": divergence_alerts,
            "identity_alerts": identity_alerts,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 12: Unified Platform Health Scorecard")
    ap.add_argument("--report-date", default=None, help="Report date YYYY-MM-DD; default today UTC")
    ap.add_argument("--ops-dir", type=Path, default=None, help="Directory containing the 4 ops JSON artifacts (default artifacts/ops)")
    ap.add_argument("--config", type=Path, default=None, help="Config YAML (default config/platform_health_scorecard.yaml)")
    ap.add_argument("--md", action="store_true", help="Also write platform_health_scorecard_{date}.md")
    args = ap.parse_args()

    repo_root = REPO_ROOT
    report_date = args.report_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ops_dir = args.ops_dir or repo_root / "artifacts" / "ops"
    config_path = args.config or repo_root / "config" / "platform_health_scorecard.yaml"
    config = _load_yaml(config_path)
    # Merge in Phase 10/11 config for thresholds (warn_below, fail_below, etc.)
    cbd_cfg = _load_yaml(repo_root / "config" / "cross_brand_divergence.yaml")
    if cbd_cfg:
        config.setdefault("cross_brand_divergence", cbd_cfg.get("cross_brand_divergence") or {})

    result = run(report_date, ops_dir, config)

    ops_dir.mkdir(parents=True, exist_ok=True)
    json_path = ops_dir / f"platform_health_scorecard_{report_date}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if getattr(args, "md", False):
        md_path = ops_dir / f"platform_health_scorecard_{report_date}.md"
        lines = [
            f"# Platform Health Scorecard — {report_date}",
            "",
            f"**Composite score:** {result['composite_score']}  **Tier:** {result['tier']}",
            "",
            "## Components",
            f"- Coverage Health: {result['components']['coverage_health_score']}",
            f"- Emotional Distribution: {result['components']['emotional_distribution_score']}",
            f"- Cross-Brand Divergence: {result['components']['cross_brand_divergence_score']}",
            f"- Brand Identity Stability: {result['components']['brand_identity_stability_score']}",
            "",
            "## Alerts summary",
            f"- Coverage: {result['alerts_summary']['coverage_alerts']}",
            f"- Entropy/emotional: {result['alerts_summary']['entropy_alerts']}",
            f"- Divergence: {result['alerts_summary']['divergence_alerts']}",
            f"- Identity: {result['alerts_summary']['identity_alerts']}",
            "",
            "See JSON artifact for sources_loaded and full detail.",
        ]
        md_path.write_text("\n".join(lines))
        print(f"Written: {md_path}")

    tier = result.get("tier", "")
    print(f"Written: {json_path}")
    print(f"Composite: {result['composite_score']}  Tier: {tier}")
    if tier == "CRITICAL":
        return 1
    if tier == "RISK":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
