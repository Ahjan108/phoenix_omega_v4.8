"""
Phase 10 — Cross-Brand Divergence Index (CBDI).

Measures structural identity separation across brands over a rolling window.
Guards against brands drifting toward identical arc/slot/band/engine usage.

Uses Jensen-Shannon Divergence (JSD) per dimension; weighted combination = CBDI.
Input: history index (JSONL with publish_date/release_week, brand_id, arc_id, slot_sig, band_sig, engine_id)
   or plans-dir (plan JSONs; file mtime as date).

Output: artifacts/ops/cross_brand_divergence_{report_date}.json

Exit: 0 PASS, 2 WARN (convergence low), 1 FAIL (convergence critical).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None

try:
    from phoenix_v4.ops.catalog_emotional_distribution import bands_from_sig, volatility_from_bands
except ImportError:
    # Fallback if run standalone
    _TEMP_TO_BAND = {"cool": 2, "warm": 3, "hot": 4, "cold": 1, "neutral": 3}

    def bands_from_sig(sig: str) -> list[int]:
        if not sig or not isinstance(sig, str):
            return []
        out = []
        for part in sig.replace(" ", "").split("-"):
            part = part.strip().lower()
            if part in _TEMP_TO_BAND:
                out.append(_TEMP_TO_BAND[part])
            else:
                try:
                    b = int(part)
                    if 1 <= b <= 5:
                        out.append(b)
                except ValueError:
                    pass
        return out

    def volatility_from_bands(bands: list[int]) -> float:
        if len(bands) < 2:
            return 0.0
        n = len(bands)
        t = sum(abs(bands[i] - bands[i - 1]) for i in range(1, n))
        t_max = (n - 1) * 4
        transition_energy = t / t_max if t_max > 0 else 0.0
        mn, mx = min(bands), max(bands)
        range_util = (mx - mn) / 4.0 if mn < mx else 0.0
        return round(0.7 * transition_energy + 0.3 * range_util, 4)


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _counts_to_probs(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    if total <= 0:
        return {}
    return {k: c / total for k, c in counts.items()}


def jsd(P: dict[str, float], Q: dict[str, float]) -> float:
    """
    Jensen-Shannon Divergence. Normalized to [0, 1]. 0 = identical, 1 = maximally different.
    JSD(P,Q) = 0.5*KL(P||M) + 0.5*KL(Q||M), M = (P+Q)/2. Raw JSD in [0, ln(2)]; divide by ln(2).
    """
    keys = set(P) | set(Q)
    if not keys:
        return 0.0
    M: dict[str, float] = {}
    for k in keys:
        p = P.get(k, 0.0)
        q = Q.get(k, 0.0)
        M[k] = (p + q) / 2.0
    def kl(a: dict[str, float], m: dict[str, float]) -> float:
        d = 0.0
        for k in keys:
            a_k = a.get(k, 0.0)
            m_k = m.get(k, 0.0)
            if a_k > 0 and m_k > 0:
                d += a_k * math.log(a_k / m_k)
        return d
    raw = 0.5 * kl(P, M) + 0.5 * kl(Q, M)
    return round(raw / math.log(2), 4) if raw > 0 else 0.0


def volatility_bucket(vol: float) -> str:
    """Low / med / high for distribution."""
    if vol < 0.35:
        return "low"
    if vol <= 0.55:
        return "med"
    return "high"


def load_releases_in_window(
    start_date: str,
    end_date: str,
    history_index_path: Optional[Path],
    plans_dir: Optional[Path],
) -> list[dict[str, Any]]:
    """Load release rows (date, brand_id, arc_id, slot_sig, band_sig, engine_id, volatility) in [start_date, end_date]."""
    out: list[dict[str, Any]] = []
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    if history_index_path and history_index_path.exists():
        with open(history_index_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    h = json.loads(line)
                except json.JSONDecodeError:
                    continue
                pub = h.get("publish_date") or h.get("release_week") or ""
                if not pub or not isinstance(pub, str):
                    continue
                row_date = pub[:10] if len(pub) >= 10 else pub
                try:
                    dt = datetime.strptime(row_date, "%Y-%m-%d")
                except ValueError:
                    continue
                if not (start_dt <= dt <= end_dt):
                    continue
                brand_id = str(h.get("brand_id") or "phoenix")
                arc_id = str(h.get("arc_id") or "")
                slot_raw = h.get("slot_sig") or h.get("slot_sig")
                slot_sig = str(slot_raw) if slot_raw else ""
                band_raw = h.get("band_sig") or h.get("band_seq") or h.get("dominant_band_sequence")
                if isinstance(band_raw, list):
                    band_sig = "-".join(str(x) for x in band_raw)
                else:
                    band_sig = str(band_raw or "")
                engine_id = str(h.get("engine_id") or "")
                bands = bands_from_sig(band_sig)
                vol = volatility_from_bands(bands) if bands else 0.0
                out.append({
                    "date": row_date,
                    "brand_id": brand_id,
                    "arc_id": arc_id or "_none",
                    "slot_sig": slot_sig or "_none",
                    "band_sig": band_sig or "_none",
                    "engine_id": engine_id or "_none",
                    "volatility": vol,
                })

    if plans_dir and plans_dir.is_dir():
        for path in plans_dir.rglob("*.json"):
            if not path.is_file():
                continue
            try:
                mtime = path.stat().st_mtime
                dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
                row_date = dt.strftime("%Y-%m-%d")
            except OSError:
                continue
            if not (start_dt <= datetime.strptime(row_date, "%Y-%m-%d") <= end_dt):
                continue
            try:
                plan = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            brand_id = str(plan.get("brand_id") or "phoenix")
            arc_id = str(plan.get("arc_id") or "_none")
            slot_sig = str(plan.get("slot_sig") or "_none")
            seq = plan.get("dominant_band_sequence") or plan.get("emotional_temperature_sequence") or []
            band_sig = "-".join(str(x) for x in seq) if isinstance(seq, list) and seq else "_none"
            engine_id = str(plan.get("engine_id") or "_none")
            bands = bands_from_sig(band_sig)
            vol = volatility_from_bands(bands) if bands else 0.0
            out.append({
                "date": row_date,
                "brand_id": brand_id,
                "arc_id": arc_id,
                "slot_sig": slot_sig,
                "band_sig": band_sig,
                "engine_id": engine_id,
                "volatility": vol,
            })

    return out


def build_brand_distributions(
    releases: list[dict[str, Any]],
    min_books: int,
) -> dict[str, dict[str, dict[str, int]]]:
    """
    Group releases by brand_id; for each brand with >= min_books, build count dicts for
    arc_id, slot_sig, band_sig, engine_id, volatility_bucket.
    Returns { brand_id: { "arc": {...}, "slot": {...}, "band": {...}, "engine": {...}, "volatility": {... } } }
    """
    by_brand: dict[str, list[dict]] = defaultdict(list)
    for r in releases:
        by_brand[r["brand_id"]].append(r)

    out: dict[str, dict[str, dict[str, int]]] = {}
    for brand_id, rows in by_brand.items():
        if len(rows) < min_books:
            continue
        arc_c: dict[str, int] = defaultdict(int)
        slot_c: dict[str, int] = defaultdict(int)
        band_c: dict[str, int] = defaultdict(int)
        engine_c: dict[str, int] = defaultdict(int)
        vol_c: dict[str, int] = defaultdict(int)
        for r in rows:
            arc_c[r["arc_id"]] += 1
            slot_c[r["slot_sig"]] += 1
            band_c[r["band_sig"]] += 1
            engine_c[r["engine_id"]] += 1
            vol_c[volatility_bucket(r["volatility"])] += 1
        out[brand_id] = {
            "arc": dict(arc_c),
            "slot": dict(slot_c),
            "band": dict(band_c),
            "engine": dict(engine_c),
            "volatility": dict(vol_c),
        }
    return out


def cbdi_pair(
    dist_a: dict[str, dict[str, int]],
    dist_b: dict[str, dict[str, int]],
    weights: dict[str, float],
) -> tuple[float, dict[str, float]]:
    """
    CBDI(A,B) = weighted sum of JSDs. Returns (score, components).
    """
    components: dict[str, float] = {}
    total = 0.0
    for dim in ("arc", "slot", "band", "engine", "volatility"):
        P = _counts_to_probs(dist_a.get(dim) or {})
        Q = _counts_to_probs(dist_b.get(dim) or {})
        d = jsd(P, Q)
        components[dim] = round(d, 4)
        w = weights.get(dim, 0.0)
        total += w * d
    return round(total, 4), components


def run(
    report_date: str,
    window_days: int,
    history_index_path: Optional[Path],
    plans_dir: Optional[Path],
    config: dict,
) -> dict[str, Any]:
    """Compute cross-brand divergence. Returns full output dict."""
    cfg = config.get("cross_brand_divergence") or {}
    min_books = int(cfg.get("minimum_books_per_brand", 20))
    th = cfg.get("thresholds") or {}
    warn_below = float(th.get("warn_below", 0.18))
    fail_below = float(th.get("fail_below", 0.12))
    weights = cfg.get("weights") or {
        "arc": 0.30, "slot": 0.20, "band": 0.20, "engine": 0.15, "volatility": 0.15,
    }
    recommendations = cfg.get("recommendations") or {}
    _fallback = "Execute remediation per ops playbook."

    end_dt = datetime.strptime(report_date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=window_days - 1)
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = report_date

    releases = load_releases_in_window(start_date, end_date, history_index_path, plans_dir)
    brand_dists = build_brand_distributions(releases, min_books)
    brands = sorted(brand_dists.keys())

    pairwise_scores: list[dict[str, Any]] = []
    alerts: list[dict[str, Any]] = []

    for i in range(len(brands)):
        for j in range(i + 1, len(brands)):
            a, b = brands[i], brands[j]
            score, components = cbdi_pair(brand_dists[a], brand_dists[b], weights)
            pairwise_scores.append({
                "brand_a": a,
                "brand_b": b,
                "score": score,
                "components": components,
            })
            rec_low = (recommendations.get("BRAND_CONVERGENCE_LOW") or _fallback).strip()
            rec_crit = (recommendations.get("BRAND_CONVERGENCE_CRITICAL") or _fallback).strip()
            if score < fail_below:
                alerts.append({
                    "severity": "FAIL",
                    "code": "BRAND_CONVERGENCE_CRITICAL",
                    "brand_a": a,
                    "brand_b": b,
                    "score": score,
                    "threshold": fail_below,
                    "recommendation": rec_crit,
                })
            elif score < warn_below:
                alerts.append({
                    "severity": "WARN",
                    "code": "BRAND_CONVERGENCE_LOW",
                    "brand_a": a,
                    "brand_b": b,
                    "score": score,
                    "threshold": warn_below,
                    "recommendation": rec_low,
                })

    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_date": report_date,
        "window_days": window_days,
        "brands_evaluated": brands,
        "pairwise_scores": pairwise_scores,
        "alerts": alerts,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 10: Cross-Brand Divergence Index (CBDI)")
    ap.add_argument("--report-date", default=None, help="Report date YYYY-MM-DD; default today UTC")
    ap.add_argument("--window-days", type=int, default=90, help="Rolling window days")
    ap.add_argument("--history-index", type=Path, default=None, help="JSONL with publish_date, brand_id, arc_id, slot_sig, band_sig, engine_id")
    ap.add_argument("--plans-dir", type=Path, default=None, help="Plans directory (file mtime = date)")
    ap.add_argument("--out-dir", type=Path, default=None, help="Output dir (default artifacts/ops)")
    ap.add_argument("--config", type=Path, default=None, help="Config YAML (default config/cross_brand_divergence.yaml)")
    args = ap.parse_args()

    repo_root = REPO_ROOT
    report_date = args.report_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = args.out_dir or repo_root / "artifacts" / "ops"
    config_path = args.config or repo_root / "config" / "cross_brand_divergence.yaml"
    config = _load_yaml(config_path)
    if not config:
        config = {"cross_brand_divergence": {"window_days": args.window_days}}

    ced = config.get("cross_brand_divergence") or {}
    window_days = int(ced.get("window_days", args.window_days))

    result = run(
        report_date=report_date,
        window_days=window_days,
        history_index_path=args.history_index,
        plans_dir=args.plans_dir,
        config=config,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"cross_brand_divergence_{report_date}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    has_fail = any(a.get("severity") == "FAIL" for a in result.get("alerts") or [])
    has_warn = any(a.get("severity") == "WARN" for a in result.get("alerts") or [])

    print(f"Written: {json_path}")
    print(f"Brands evaluated: {len(result.get('brands_evaluated') or [])}  Pairs: {len(result.get('pairwise_scores') or [])}  Alerts: {len(result.get('alerts') or [])}")
    if has_fail:
        return 1
    if has_warn:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
