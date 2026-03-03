"""
Phase 9 — Catalog Emotional Distribution Index (standalone ops governance).

90-day rolling macro telemetry: detects catalog-level emotional flattening and
brand/persona drift. Cheap, incremental, deterministic.

Outputs:
  artifacts/ops/catalog_emotional_distribution_{report_date}.json
  (optional) ..._{report_date}.md

Inputs:
  --history-index artifacts/catalog_similarity/index.jsonl (rows with publish_date, band_sig or band_seq)
  and/or --plans-dir artifacts/plans/ (plan JSONs; file mtime or plan_timestamp as date proxy)

Daily cache (minimal compute):
  artifacts/ops/cache/catalog_emotional_daily_{YYYY-MM-DD}.jsonl

Exit: 0 PASS, 2 WARN (warn alerts), 1 FAIL (hard_fail_codes).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None

# Temperature label → band 1-5 (for band_seq from index)
_TEMP_TO_BAND = {"cool": 2, "warm": 3, "hot": 4, "cold": 1, "neutral": 3}


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def bands_from_sig(sig: str) -> list[int]:
    """Parse band_sig (e.g. '2-3-4-4') or band_seq (e.g. 'cool-warm-hot') to list of ints 1-5."""
    if not sig or not isinstance(sig, str):
        return []
    out: list[int] = []
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
    """
    Per-book volatility: 0.7 * transition_energy + 0.3 * range_util.
    T = sum |b_i - b_{i-1}|, T_max = (n-1)*4, transition_energy = T/T_max.
    range_util = (max(b)-min(b)) / 4.
    """
    if len(bands) < 2:
        return 0.0
    n = len(bands)
    t = sum(abs(bands[i] - bands[i - 1]) for i in range(1, n))
    t_max = (n - 1) * 4
    transition_energy = t / t_max if t_max > 0 else 0.0
    mn, mx = min(bands), max(bands)
    range_util = (mx - mn) / 4.0 if mn < mx else 0.0
    return round(0.7 * transition_energy + 0.3 * range_util, 4)


def band_entropy_norm(counts: dict[str, int]) -> float:
    """H_norm = H / log(5). 0 = single band, 1 = uniform over 5 bands."""
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log(p)
    return round(h / math.log(5), 4)


def _date_from_plan_path(plan_path: Path) -> str:
    """Use file mtime as date proxy (YYYY-MM-DD)."""
    try:
        m = plan_path.stat().st_mtime
        return datetime.fromtimestamp(m, tz=timezone.utc).strftime("%Y-%m-%d")
    except OSError:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _band_sig_from_plan(plan: dict) -> str:
    for key in ("dominant_band_sequence", "emotional_temperature_sequence"):
        v = plan.get(key)
        if isinstance(v, list) and v:
            return "-".join(str(x) if x is not None else "3" for x in v)
    return ""


def build_daily_cache_from_plans(
    date_str: str,
    plans_dir: Path,
    cache_path: Path,
) -> bool:
    """Build cache for date_str by scanning plans_dir (mtime = date). Returns True if cache was written."""
    if not plans_dir.is_dir():
        return False
    rows: list[dict[str, Any]] = []
    for path in plans_dir.rglob("*.json"):
        if not path.is_file():
            continue
        if _date_from_plan_path(path) != date_str:
            continue
        try:
            plan = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        band_sig = _band_sig_from_plan(plan)
        bands = bands_from_sig(band_sig)
        if not bands:
            continue
        book_id = str(plan.get("plan_id") or plan.get("book_id") or path.stem)
        brand_id = str(plan.get("brand_id") or "phoenix")
        persona_id = str(plan.get("persona_id") or plan.get("persona") or "")
        topic_id = str(plan.get("topic_id") or plan.get("topic") or "")
        vol = volatility_from_bands(bands)
        rows.append({
            "date": date_str,
            "book_id": book_id,
            "brand_id": brand_id,
            "persona_id": persona_id,
            "topic_id": topic_id,
            "band_sig": band_sig,
            "max_band": max(bands),
            "min_band": min(bands),
            "volatility": vol,
        })
    if not rows:
        return False
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=True) + "\n")
    return True


def build_daily_cache_from_index(
    date_str: str,
    history_index_path: Path,
    cache_path: Path,
) -> bool:
    """Build cache for date_str from history index (rows with publish_date or release_week == date)."""
    if not history_index_path.exists():
        return False
    rows: list[dict[str, Any]] = []
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
            if not pub:
                continue
            # Normalize to YYYY-MM-DD for comparison
            if isinstance(pub, str) and len(pub) >= 10:
                row_date = pub[:10]
            else:
                continue
            if row_date != date_str:
                continue
            band_raw = h.get("band_sig") or h.get("band_seq") or h.get("dominant_band_sequence")
            if isinstance(band_raw, list):
                band_sig = "-".join(str(x) for x in band_raw)
            else:
                band_sig = str(band_raw or "")
            bands = bands_from_sig(band_sig)
            if not bands:
                continue
            book_id = str(h.get("book_id") or "")
            if not book_id:
                continue
            rows.append({
                "date": row_date,
                "book_id": book_id,
                "brand_id": str(h.get("brand_id") or "phoenix"),
                "persona_id": str(h.get("persona_id") or ""),
                "topic_id": str(h.get("topic_id") or ""),
                "band_sig": band_sig,
                "max_band": max(bands),
                "min_band": min(bands),
                "volatility": volatility_from_bands(bands),
            })
    if not rows:
        return False
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=True) + "\n")
    return True


def load_window(
    cache_dir: Path,
    start_date: str,
    end_date: str,
    history_index_path: Optional[Path],
    plans_dir: Optional[Path],
) -> list[dict[str, Any]]:
    """Load all daily cache lines in [start_date, end_date]; build missing from index or plans."""
    out: list[dict[str, Any]] = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    d = start
    while d <= end:
        date_str = d.strftime("%Y-%m-%d")
        cache_path = cache_dir / f"catalog_emotional_daily_{date_str}.jsonl"
        if cache_path.exists():
            with open(cache_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            out.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        else:
            built = False
            if history_index_path and history_index_path.exists():
                built = build_daily_cache_from_index(date_str, history_index_path, cache_path)
            if not built and plans_dir and plans_dir.is_dir():
                built = build_daily_cache_from_plans(date_str, plans_dir, cache_path)
        d += timedelta(days=1)
    return out


def aggregate(reports: list[dict[str, Any]]) -> tuple[dict, dict, dict]:
    """Compute global, by_brand, by_persona metrics (chapter band distribution, entropy, avg volatility, band_5_share)."""
    global_band_counts: dict[str, int] = defaultdict(int)
    global_vol_sum = 0.0
    global_vol_count = 0
    global_band5_count = 0
    global_chapter_count = 0

    by_brand: dict[str, dict[str, Any]] = defaultdict(lambda: {"band_counts": defaultdict(int), "vol_sum": 0.0, "vol_count": 0, "band5_count": 0, "chapter_count": 0, "book_count": 0})
    by_persona: dict[str, dict[str, Any]] = defaultdict(lambda: {"band_counts": defaultdict(int), "vol_sum": 0.0, "vol_count": 0, "band5_count": 0, "chapter_count": 0, "book_count": 0})
    seen_books_global: set[str] = set()
    seen_books_brand: dict[str, set[str]] = defaultdict(set)
    seen_books_persona: dict[str, set[str]] = defaultdict(set)

    for r in reports:
        band_sig = r.get("band_sig") or ""
        bands = bands_from_sig(band_sig)
        if not bands:
            continue
        book_id = r.get("book_id") or ""
        brand_id = r.get("brand_id") or "phoenix"
        persona_id = r.get("persona_id") or ""
        vol = float(r.get("volatility") or 0)

        for b in bands:
            k = str(b)
            global_band_counts[k] += 1
            by_brand[brand_id]["band_counts"][k] += 1
            by_persona[persona_id]["band_counts"][k] += 1
        global_chapter_count += len(bands)
        by_brand[brand_id]["chapter_count"] += len(bands)
        by_persona[persona_id]["chapter_count"] += len(bands)
        global_vol_sum += vol
        global_vol_count += 1
        by_brand[brand_id]["vol_sum"] += vol
        by_brand[brand_id]["vol_count"] += 1
        by_persona[persona_id]["vol_sum"] += vol
        by_persona[persona_id]["vol_count"] += 1
        if 5 in bands:
            global_band5_count += sum(1 for x in bands if x == 5)
            by_brand[brand_id]["band5_count"] += sum(1 for x in bands if x == 5)
            by_persona[persona_id]["band5_count"] += sum(1 for x in bands if x == 5)
        seen_books_global.add(book_id)
        seen_books_brand[brand_id].add(book_id)
        seen_books_persona[persona_id].add(book_id)

    for bid, data in by_brand.items():
        data["book_count"] = len(seen_books_brand[bid])
    for pid, data in by_persona.items():
        data["book_count"] = len(seen_books_persona[pid])

    def to_global_style(band_counts: dict, vol_sum: float, vol_count: int, band5_count: int, chapter_count: int) -> dict:
        total = sum(band_counts.values())
        if total <= 0:
            dist = {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0}
            return {"chapter_band_distribution": dist, "band_entropy_norm": 0.0, "avg_volatility": 0.0, "band_5_share": 0.0}
        dist = {b: round(band_counts.get(b, 0) / total, 4) for b in ["1", "2", "3", "4", "5"]}
        return {
            "chapter_band_distribution": dist,
            "band_entropy_norm": band_entropy_norm(dict(band_counts)),
            "avg_volatility": round(vol_sum / vol_count, 4) if vol_count else 0.0,
            "band_5_share": round(band5_count / total, 4) if total else 0.0,
        }

    global_total = sum(global_band_counts.values())
    global_result = {
        "book_count": len(seen_books_global),
        **to_global_style(
            dict(global_band_counts),
            global_vol_sum,
            global_vol_count,
            global_band5_count,
            global_chapter_count,
        ),
    }

    by_brand_out: dict[str, dict] = {}
    for bid, data in by_brand.items():
        bc = dict(data["band_counts"])
        by_brand_out[bid] = {
            "book_count": data["book_count"],
            **to_global_style(
                bc,
                data["vol_sum"],
                data["vol_count"],
                data["band5_count"],
                data["chapter_count"],
            ),
        }

    by_persona_out: dict[str, dict] = {}
    for pid, data in by_persona.items():
        bc = dict(data["band_counts"])
        by_persona_out[pid] = {
            "book_count": data["book_count"],
            **to_global_style(
                bc,
                data["vol_sum"],
                data["vol_count"],
                data["band5_count"],
                data["chapter_count"],
            ),
        }

    return global_result, by_brand_out, by_persona_out


def build_alerts(
    global_metrics: dict,
    by_brand: dict,
    by_persona: dict,
    drift: Optional[dict],
    config: dict,
) -> list[dict[str, Any]]:
    """Build alert list with severity and recommendation. Recommendations come from config only (Phase 9 contract)."""
    alerts: list[dict[str, Any]] = []
    ced = config.get("catalog_emotional_distribution") or {}
    th = ced.get("thresholds") or {}
    ent = th.get("entropy") or {}
    vol = th.get("volatility") or {}
    band5 = th.get("band5_share") or {}
    drift_cfg = ced.get("drift") or {}
    policy = ced.get("alert_policy") or {}
    default_severity = policy.get("default_severity", "WARN")
    hard_fail = set(policy.get("hard_fail_codes") or [])
    minimums = ced.get("minimums") or {}
    brand_min_books = int(minimums.get("brand_min_books", 25))
    persona_min_books = int(minimums.get("persona_min_books", 25))
    recommendations = ced.get("recommendations") or {}
    _FALLBACK_REC = "Execute remediation per ops playbook."

    def rec(code: str) -> str:
        return (recommendations.get(code) or _FALLBACK_REC).strip()

    def add(code: str, metric: str, value: float, threshold: float, detail: str = ""):
        severity = "FAIL" if code in hard_fail else default_severity
        alerts.append({
            "severity": severity,
            "code": code,
            "metric": metric,
            "value": round(value, 4),
            "threshold": threshold,
            "recommendation": rec(code),
            "detail": detail,
        })

    g_ent_min = float(ent.get("global_min", 0.86))
    if global_metrics.get("band_entropy_norm", 0) < g_ent_min:
        add(
            "GLOBAL_ENTROPY_LOW",
            "band_entropy_norm",
            global_metrics.get("band_entropy_norm", 0),
            g_ent_min,
        )
    g_vol_min = float(vol.get("global_min", 0.42))
    if global_metrics.get("avg_volatility", 0) < g_vol_min:
        add(
            "GLOBAL_VOLATILITY_LOW",
            "avg_volatility",
            global_metrics.get("avg_volatility", 0),
            g_vol_min,
        )
    g_b5_min = float(band5.get("global_min", 0.06))
    if global_metrics.get("band_5_share", 0) < g_b5_min:
        add(
            "GLOBAL_BAND5_SHARE_LOW",
            "band_5_share",
            global_metrics.get("band_5_share", 0),
            g_b5_min,
        )

    for brand_id, data in by_brand.items():
        if data.get("book_count", 0) < brand_min_books:
            continue
        if data.get("band_entropy_norm", 0) < float(ent.get("brand_min", 0.78)):
            add("BRAND_ENTROPY_LOW", "band_entropy_norm", data["band_entropy_norm"], float(ent.get("brand_min", 0.78)), brand_id)
        if data.get("avg_volatility", 0) < float(vol.get("brand_min", 0.38)):
            add("BRAND_VOLATILITY_LOW", "avg_volatility", data["avg_volatility"], float(vol.get("brand_min", 0.38)), brand_id)
        if data.get("band_5_share", 0) < float(band5.get("brand_min", 0.03)):
            add("BRAND_BAND5_SHARE_LOW", "band_5_share", data["band_5_share"], float(band5.get("brand_min", 0.03)), brand_id)

    for persona_id, data in by_persona.items():
        if not persona_id or data.get("book_count", 0) < persona_min_books:
            continue
        if data.get("band_entropy_norm", 0) < float(ent.get("persona_min", 0.78)):
            add("PERSONA_ENTROPY_LOW", "band_entropy_norm", data["band_entropy_norm"], float(ent.get("persona_min", 0.78)), persona_id)
        if data.get("avg_volatility", 0) < float(vol.get("persona_min", 0.36)):
            add("PERSONA_VOLATILITY_LOW", "avg_volatility", data["avg_volatility"], float(vol.get("persona_min", 0.36)), persona_id)

    if drift:
        if drift.get("entropy_delta") is not None and drift["entropy_delta"] <= -float(drift_cfg.get("entropy_drop", 0.05)):
            add("DRIFT_ENTROPY_DROP", "entropy_delta", drift["entropy_delta"], -float(drift_cfg.get("entropy_drop", 0.05)), "")
        if drift.get("volatility_delta") is not None and drift["volatility_delta"] <= -float(drift_cfg.get("volatility_drop", 0.05)):
            add("DRIFT_VOLATILITY_DROP", "volatility_delta", drift["volatility_delta"], -float(drift_cfg.get("volatility_drop", 0.05)), "")
        if drift.get("band_5_share_delta") is not None and drift["band_5_share_delta"] <= -float(drift_cfg.get("band5_drop", 0.03)):
            add("DRIFT_BAND5_DROP", "band_5_share_delta", drift["band_5_share_delta"], -float(drift_cfg.get("band5_drop", 0.03)), "")

    return alerts


def run(
    report_date: str,
    window_days: int,
    history_index_path: Optional[Path],
    plans_dir: Optional[Path],
    cache_dir: Path,
    config: dict,
) -> dict[str, Any]:
    """Compute catalog emotional distribution for report_date. Returns full output dict."""
    end_dt = datetime.strptime(report_date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=window_days - 1)
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = report_date

    reports = load_window(cache_dir, start_date, end_date, history_index_path, plans_dir)
    global_metrics, by_brand, by_persona = aggregate(reports)

    # Previous window for drift
    prev_end_dt = start_dt - timedelta(days=1)
    prev_start_dt = prev_end_dt - timedelta(days=window_days - 1)
    prev_start_date = prev_start_dt.strftime("%Y-%m-%d")
    prev_end_date = prev_end_dt.strftime("%Y-%m-%d")
    prev_reports = load_window(cache_dir, prev_start_date, prev_end_date, history_index_path, plans_dir)
    drift: Optional[dict] = None
    if prev_reports:
        p_global, _, _ = aggregate(prev_reports)
        drift = {
            "previous_window": {"start": prev_start_date, "end": prev_end_date},
            "entropy_delta": round(global_metrics.get("band_entropy_norm", 0) - p_global.get("band_entropy_norm", 0), 4),
            "volatility_delta": round(global_metrics.get("avg_volatility", 0) - p_global.get("avg_volatility", 0), 4),
            "band_5_share_delta": round(global_metrics.get("band_5_share", 0) - p_global.get("band_5_share", 0), 4),
        }

    alerts = build_alerts(global_metrics, by_brand, by_persona, drift, config)

    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_date": report_date,
        "window_days": window_days,
        "source": {
            "history_index": str(history_index_path) if history_index_path else None,
            "plans_dir": str(plans_dir) if plans_dir else None,
            "cache_dir": str(cache_dir),
        },
        "global": global_metrics,
        "by_brand": by_brand,
        "by_persona": by_persona,
        "drift": drift,
        "alerts": alerts,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 9: Catalog Emotional Distribution (90-day rolling)")
    ap.add_argument("--report-date", default=None, help="Report date YYYY-MM-DD; default today UTC")
    ap.add_argument("--window-days", type=int, default=90, help="Rolling window days")
    ap.add_argument("--history-index", type=Path, default=None, help="JSONL index with publish_date, band_sig/band_seq")
    ap.add_argument("--plans-dir", type=Path, default=None, help="Plans directory (mtime = date proxy)")
    ap.add_argument("--cache-dir", type=Path, default=None, help="Daily cache dir (default artifacts/ops/cache)")
    ap.add_argument("--out-dir", type=Path, default=None, help="Output dir (default artifacts/ops)")
    ap.add_argument("--md", action="store_true", help="Also write catalog_emotional_distribution_{date}.md")
    ap.add_argument("--config", type=Path, default=None, help="Config YAML (default config/catalog_emotional_distribution.yaml)")
    args = ap.parse_args()

    repo_root = REPO_ROOT
    report_date = args.report_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cache_dir = args.cache_dir or repo_root / "artifacts" / "ops" / "cache"
    out_dir = args.out_dir or repo_root / "artifacts" / "ops"
    config_path = args.config or repo_root / "config" / "catalog_emotional_distribution.yaml"
    config = _load_yaml(config_path)
    if not config:
        config = {"catalog_emotional_distribution": {"window_days": args.window_days}}

    ced = config.get("catalog_emotional_distribution") or {}
    window_days = int(ced.get("window_days", args.window_days))

    result = run(
        report_date=report_date,
        window_days=window_days,
        history_index_path=args.history_index,
        plans_dir=args.plans_dir,
        cache_dir=cache_dir,
        config=config,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"catalog_emotional_distribution_{report_date}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if getattr(args, "md", False):
        md_path = out_dir / f"catalog_emotional_distribution_{report_date}.md"
        g = result.get("global") or {}
        lines = [
            f"# Catalog Emotional Distribution — {report_date}",
            "",
            f"Window: {result.get('window_days')} days.",
            f"Global: book_count={g.get('book_count')}  band_entropy_norm={g.get('band_entropy_norm')}  avg_volatility={g.get('avg_volatility')}  band_5_share={g.get('band_5_share')}",
            "",
        ]
        alerts = result.get("alerts") or []
        if alerts:
            lines.append("## Alerts")
            lines.append("")
            for a in alerts:
                lines.append(f"- **{a.get('code')}** ({a.get('severity')}): {a.get('recommendation')}")
            lines.append("")
        lines.append("See JSON artifact for by_brand, by_persona, drift.")
        md_path.write_text("\n".join(lines))
        print(f"Written: {md_path}")

    hard_fail = set((ced.get("alert_policy") or {}).get("hard_fail_codes") or [])
    has_fail = any(a.get("severity") == "FAIL" for a in result.get("alerts") or [])
    has_warn = any(a.get("severity") == "WARN" for a in result.get("alerts") or [])

    print(f"Written: {json_path}")
    print(f"Global entropy: {result['global'].get('band_entropy_norm')}  avg_volatility: {result['global'].get('avg_volatility')}  alerts: {len(result.get('alerts') or [])}")
    if has_fail:
        return 1
    if has_warn:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
