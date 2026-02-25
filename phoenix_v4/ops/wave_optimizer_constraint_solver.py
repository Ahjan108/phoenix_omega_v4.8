"""
Phase 13-C — Deterministic Constraint Solver Wave Optimizer (DWO-CS).

Produces a wave that satisfies hard constraints (weekly caps, cross-brand separation,
brand identity caps) and maximizes a deterministic objective. No randomness; no ML.

Inputs: candidates JSON, ops-dir (for CBDI/BISI signals), config.
Outputs: wave_optimizer_solution_{wave_id}.json (.md) or wave_optimizer_infeasible_{wave_id}.json

Exit: 0 SOLVED, 1 INFEASIBLE, 2 SOLVED_WITH_WARN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None

from phoenix_v4.ops.quality_objective import (
    normalize_quality,
    compute_wave_quality_stats,
)


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(p: Path) -> Optional[dict]:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _wave_fingerprint(c: dict) -> str:
    return "|".join([
        str(c.get("arc_id") or "none"),
        str(c.get("slot_sig") or "none"),
        str(c.get("band_sig") or "none"),
        str(c.get("variation_signature") or "none"),
    ])


def _sort_key(c: dict) -> str:
    return str(c.get("candidate_sort_key") or c.get("candidate_id") or "")


def _get_report_date_from_wave_id(wave_id: str) -> str:
    """Map 2026-W10 -> last day of that week approx 2026-03-08."""
    try:
        y, w = wave_id.split("-W")
        y, w = int(y), int(w)
        # ISO week: simple approx
        from datetime import datetime, timedelta
        jan1 = datetime(y, 1, 1)
        start = jan1 + timedelta(days=(w - 1) * 7 - jan1.weekday())
        return start.strftime("%Y-%m-%d")
    except Exception:
        return ""


def load_candidates(path: Path) -> list[dict]:
    data = _load_json(path)
    if not data:
        return []
    if isinstance(data, list):
        return data
    return data.get("candidates") or data.get("items") or []


def load_convergent_pairs(ops_dir: Path, report_date: str, config: dict) -> list[tuple[str, str]]:
    """From CBDI report, return [(brand_a, brand_b)] for pairs with convergence alert."""
    if not report_date:
        return []
    cfg = (config.get("wave_optimizer") or {}).get("hard_constraints") or {}
    cross = cfg.get("cross_brand") or {}
    if not cross.get("enforce_no_arc_overlap_when_convergent"):
        return []
    path = ops_dir / f"cross_brand_divergence_{report_date}.json"
    data = _load_json(path)
    if not data:
        return []
    pairs = []
    for a in data.get("alerts") or []:
        if (a.get("code") or "").upper() in ("BRAND_CONVERGENCE_LOW", "BRAND_CONVERGENCE_CRITICAL"):
            ba, bb = a.get("brand_a"), a.get("brand_b")
            if ba and bb:
                pairs.append((str(ba), str(bb)))
    return pairs


def load_drift_critical_brands(ops_dir: Path, report_date: str, config: dict) -> set[str]:
    """From BISI report, return brand_ids with BRAND_IDENTITY_DRIFT_CRITICAL."""
    if not report_date:
        return set()
    path = ops_dir / f"brand_identity_stability_{report_date}.json"
    data = _load_json(path)
    if not data:
        return set()
    out = set()
    for a in data.get("alerts") or []:
        if (a.get("code") or "").upper() == "BRAND_IDENTITY_DRIFT_CRITICAL":
            b = a.get("brand_id")
            if b:
                out.add(str(b))
    return out


def solve(
    candidates: list[dict],
    target_size: int,
    config: dict,
    convergent_pairs: list[tuple[str, str]],
    drift_critical_brands: set[str],
) -> tuple[list[dict], Optional[list[dict]], Optional[str]]:
    """
    Deterministic greedy solver. Returns (selected_list, blocking_reasons, status).
    status: "SOLVED" | "SOLVED_WITH_WARN" | "INFEASIBLE"
    """
    wo = config.get("wave_optimizer") or {}
    eligibility = wo.get("eligibility") or {}
    exclude_risks = set(eligibility.get("exclude_risks") or ["BLOCKER", "RED"])
    allow_yellow = eligibility.get("allow_yellow", True)
    caps_cfg = (wo.get("hard_constraints") or {}).get("weekly_caps") or {}
    obj_cfg = (wo.get("objective") or {}).get("weights") or {}
    vol_bins = (wo.get("objective") or {}).get("volatility_bins") or {}
    vol_low = float(vol_bins.get("low", 0.35))
    vol_high = float(vol_bins.get("high", 0.55))
    bi = ((wo.get("hard_constraints") or {}).get("brand_identity") or {})
    max_new_arcs = int(bi.get("max_new_arcs_per_brand_when_critical") or 2)

    # Eligibility filter
    eligible = []
    exclusion_breakdown = defaultdict(int)
    for c in candidates:
        risk = (c.get("risk") or "GREEN").upper()
        if risk in exclude_risks:
            exclusion_breakdown["risk_red_blocker"] += 1
            continue
        if risk == "YELLOW" and not allow_yellow:
            exclusion_breakdown["risk_yellow"] += 1
            continue
        cid = c.get("candidate_id")
        if not cid:
            continue
        eligible.append(c)

    # Quality constraints (from book_quality_bundle / wave_candidates_enricher)
    q_constraints = (wo.get("constraints") or {})
    if q_constraints.get("exclude_quality_fail") or q_constraints.get("min_ending_strength") is not None or q_constraints.get("min_csi_score") is not None or q_constraints.get("exclude_quality_missing"):
        quality_filtered = []
        for c in eligible:
            q = c.get("quality") or {}
            status = (q.get("status") or "missing").lower()
            if q_constraints.get("exclude_quality_fail") and status == "fail":
                exclusion_breakdown["filtered_fail"] += 1
                continue
            if q_constraints.get("exclude_quality_missing") and (status == "missing" or not q):
                exclusion_breakdown["filtered_missing"] += 1
                continue
            ending = q.get("ending_strength")
            if ending is not None and q_constraints.get("min_ending_strength") is not None:
                if float(ending) < float(q_constraints["min_ending_strength"]):
                    exclusion_breakdown["filtered_ending"] += 1
                    continue
            csi = q.get("csi_score")
            if csi is not None and q_constraints.get("min_csi_score") is not None:
                if float(csi) < float(q_constraints["min_csi_score"]):
                    exclusion_breakdown["filtered_csi"] += 1
                    continue
            quality_filtered.append(c)
        eligible = quality_filtered

    eligible.sort(key=_sort_key)

    if len(eligible) < target_size:
        return [], [{
            "code": "INSUFFICIENT_ELIGIBLE_CANDIDATES",
            "eligible_count": len(eligible),
            "needed": target_size,
            "exclusion_breakdown": dict(exclusion_breakdown),
        }], "INFEASIBLE"

    cap_keys = [
        ("topic_id", caps_cfg.get("max_same_topic")),
        ("persona_id", caps_cfg.get("max_same_persona")),
        ("arc_id", caps_cfg.get("max_same_arc_id")),
        ("engine_id", caps_cfg.get("max_same_engine_id")),
        ("band_sig", caps_cfg.get("max_same_band_sig")),
        ("slot_sig", caps_cfg.get("max_same_slot_sig")),
        ("variation_signature", caps_cfg.get("max_same_variation_signature")),
        ("wave_fingerprint", caps_cfg.get("max_same_wave_fingerprint")),
        ("teacher_id", caps_cfg.get("max_same_teacher_id")),
    ]
    topic_persona_cap = caps_cfg.get("max_same_topic_persona_pair")
    teacher_mode_cap = caps_cfg.get("max_teacher_mode_books")

    selected: list[dict] = []
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    topic_persona_counts: dict[str, int] = defaultdict(int)
    state: dict[str, Any] = {"teacher_mode_count": 0}
    convergent_arc_used: dict[tuple[str, str], set[str]] = defaultdict(set)
    brand_new_arc_count: dict[str, int] = defaultdict(int)

    def would_violate(c: dict) -> bool:
        for key, cap in cap_keys:
            if cap is None:
                continue
            val = c.get(key)
            if key == "wave_fingerprint":
                val = _wave_fingerprint(c)
            val = str(val or "")
            if counts[key][val] >= cap:
                return True
        if topic_persona_cap is not None:
            tp = f"{c.get('topic_id')}|{c.get('persona_id')}"
            if topic_persona_counts[tp] >= topic_persona_cap:
                return True
        if teacher_mode_cap is not None and c.get("teacher_mode"):
            if state["teacher_mode_count"] >= teacher_mode_cap:
                return True
        for (ba, bb) in convergent_pairs:
            brand = str(c.get("brand_id") or "")
            arc = str(c.get("arc_id") or "")
            if brand not in (ba, bb):
                continue
            if arc in convergent_arc_used[(ba, bb)]:
                return True
        brand = str(c.get("brand_id") or "")
        if brand in drift_critical_brands and c.get("is_new_arc"):
            if brand_new_arc_count[brand] >= max_new_arcs:
                return True
        return False

    def add_counts(c: dict) -> None:
        for key, _ in cap_keys:
            val = c.get(key)
            if key == "wave_fingerprint":
                val = _wave_fingerprint(c)
            val = str(val or "")
            counts[key][val] += 1
        tp = f"{c.get('topic_id')}|{c.get('persona_id')}"
        topic_persona_counts[tp] += 1
        if c.get("teacher_mode"):
            state["teacher_mode_count"] += 1
        for (ba, bb) in convergent_pairs:
            brand = str(c.get("brand_id") or "")
            if brand in (ba, bb):
                convergent_arc_used[(ba, bb)].add(str(c.get("arc_id") or ""))
        if str(c.get("brand_id")) in drift_critical_brands and c.get("is_new_arc"):
            brand_new_arc_count[str(c.get("brand_id"))] += 1

    def remove_counts(c: dict) -> None:
        for key, _ in cap_keys:
            val = c.get(key)
            if key == "wave_fingerprint":
                val = _wave_fingerprint(c)
            val = str(val or "")
            counts[key][val] -= 1
        tp = f"{c.get('topic_id')}|{c.get('persona_id')}"
        topic_persona_counts[tp] -= 1
        if c.get("teacher_mode"):
            state["teacher_mode_count"] -= 1
        for (ba, bb) in convergent_pairs:
            brand = str(c.get("brand_id") or "")
            if brand in (ba, bb):
                convergent_arc_used[(ba, bb)].discard(str(c.get("arc_id") or ""))
        if str(c.get("brand_id")) in drift_critical_brands and c.get("is_new_arc"):
            brand_new_arc_count[str(c.get("brand_id"))] -= 1

    def score(c: dict, selected_ids: set[str]) -> float:
        """Higher = better. Deterministic. Returns float to allow quality fractional terms."""
        s = 0
        vol = float(c.get("volatility") or 0)
        if vol >= vol_high:
            s += int(obj_cfg.get("volatility_preference", 10)) * 2
        elif vol >= vol_low:
            s += int(obj_cfg.get("volatility_preference", 10))
        age = c.get("age_days")
        if age is not None and age <= 14:
            s += int(obj_cfg.get("freshness_preference", 5))
        topic = str(c.get("topic_id") or "")
        persona = str(c.get("persona_id") or "")
        arc = str(c.get("arc_id") or "")
        band = str(c.get("band_sig") or "")
        if counts["topic_id"][topic] == 0:
            s += int(obj_cfg.get("topic_diversity", 25))
        if counts["persona_id"][persona] == 0:
            s += int(obj_cfg.get("persona_diversity", 20))
        if counts["arc_id"][arc] == 0:
            s += int(obj_cfg.get("arc_diversity", 20))
        if counts["band_sig"][band] == 0:
            s += int(obj_cfg.get("band_diversity", 15))
        if (c.get("risk") or "GREEN").upper() == "YELLOW":
            s -= int(obj_cfg.get("yellow_risk_penalty", 5))
        # Quality objective terms (scaled so they don't dominate integer diversity)
        w_csi = float(obj_cfg.get("quality_csi", 0))
        w_end = float(obj_cfg.get("quality_ending", 0))
        if w_csi > 0 or w_end > 0:
            qn = normalize_quality(c)
            s += w_csi * 100 * (qn["csi_score"] / 100.0)
            s += w_end * 100 * (qn["ending_strength"] / 100.0)
        return max(0.0, s)

    selected_ids = set()
    remaining = list(eligible)
    while len(selected) < target_size:
        best = None
        best_score = -1
        for c in remaining:
            if c.get("candidate_id") in selected_ids:
                continue
            if would_violate(c):
                continue
            sc = score(c, selected_ids)
            if sc > best_score:
                best_score = sc
                best = c
            elif sc == best_score and best is not None and _sort_key(c) < _sort_key(best):
                best = c
            elif sc == best_score and best is None:
                best = c
        if best is None:
            blocking = [{
                "code": "NO_VALID_CANDIDATE_AT_STEP",
                "selected_so_far": len(selected),
                "needed": target_size,
                "note": "No remaining candidate can be added without violating a cap or cross-brand/identity constraint.",
            }]
            return selected, blocking, "INFEASIBLE"
        selected.append(best)
        selected_ids.add(best.get("candidate_id"))
        remaining.remove(best)
        add_counts(best)

    return selected, None, "SOLVED"


def run(
    wave_id: str,
    target_size: int,
    candidates_path: Path,
    ops_dir: Path,
    config: dict,
) -> dict[str, Any]:
    """Load candidates and ops signals, solve, return result dict (solution or infeasible)."""
    candidates = load_candidates(candidates_path)
    report_date = _get_report_date_from_wave_id(wave_id)
    convergent_pairs = load_convergent_pairs(ops_dir, report_date, config)
    drift_critical_brands = load_drift_critical_brands(ops_dir, report_date, config)

    # Ensure each candidate has wave_fingerprint and sort_key for caps
    for c in candidates:
        if "wave_fingerprint" not in c:
            c["wave_fingerprint"] = _wave_fingerprint(c)
        if "candidate_sort_key" not in c:
            c["candidate_sort_key"] = _sort_key(c)

    selected, blocking_reasons, status = solve(
        candidates, target_size, config, convergent_pairs, drift_critical_brands,
    )

    if status == "INFEASIBLE" and blocking_reasons:
        return {
            "schema_version": "1.0",
            "status": "INFEASIBLE",
            "wave_id": wave_id,
            "target_size": target_size,
            "candidate_count": len(candidates),
            "blocking_reasons": blocking_reasons,
            "recommended_ops_actions": [
                "Increase candidate pool diversity for next wave (selection step), OR reduce target_size.",
                "Do not reopen content unless coverage deficits exist; this is a scheduling pool issue.",
            ],
        }
    selected_ids = [c.get("candidate_id") for c in selected]
    quality_summary = None
    if selected:
        stats = compute_wave_quality_stats(selected)
        quality_summary = {
            "mean_csi": round(stats["mean_csi"], 2),
            "mean_ending_strength": round(stats["mean_ending_strength"], 2),
            "bucket_coverage": round(stats["bucket_coverage"], 2),
            "low_ending_ratio": round(stats["low_ending_ratio"], 2),
        }
    result = {
        "schema_version": "1.0",
        "status": status,
        "wave_id": wave_id,
        "target_size": target_size,
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "selected": selected_ids,
        "selected_candidates": selected_ids,
        "selected_items": selected,
        "constraint_satisfaction": "all hard constraints satisfied",
        "determinism_note": "Same inputs + config yield identical selection.",
    }
    if quality_summary is not None:
        result["quality_summary"] = quality_summary
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 13-C: Deterministic Constraint Solver Wave Optimizer")
    ap.add_argument("--wave-id", required=True, help="Wave identifier (e.g. 2026-W10)")
    ap.add_argument("--target-size", type=int, default=None, help="Books to select (default from config)")
    ap.add_argument("--candidates-json", type=Path, required=True, help="Path to wave_candidates_*.json")
    ap.add_argument("--ops-dir", type=Path, default=None, help="Ops artifacts dir (default artifacts/ops)")
    ap.add_argument("--config", type=Path, default=None, help="Config YAML")
    ap.add_argument("--out-dir", type=Path, default=None, help="Output dir (default artifacts/ops/wave_optimizer)")
    args = ap.parse_args()

    repo_root = REPO_ROOT
    ops_dir = args.ops_dir or repo_root / "artifacts" / "ops"
    out_dir = args.out_dir or repo_root / "artifacts" / "ops" / "wave_optimizer"
    config_path = args.config or repo_root / "config" / "wave_optimizer_constraint_solver.yaml"
    config = _load_yaml(config_path)
    wo = config.get("wave_optimizer") or {}
    target_size = args.target_size if args.target_size is not None else int(wo.get("target_size_default", 90))

    result = run(
        args.wave_id,
        target_size,
        args.candidates_json,
        ops_dir,
        config,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    status = result.get("status", "UNKNOWN")

    if status == "INFEASIBLE":
        out_path = out_dir / f"wave_optimizer_infeasible_{args.wave_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Infeasible. Written: {out_path}")
        return 1

    out_path = out_dir / f"wave_optimizer_solution_{args.wave_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    md_path = out_dir / f"wave_optimizer_solution_{args.wave_id}.md"
    lines = [
        f"# Wave Optimizer Solution — {args.wave_id}",
        "",
        f"**Status:** {status}  **Selected:** {result.get('selected_count')} / {result.get('target_size')}",
        "",
        "## Selected candidate_ids",
        "",
    ]
    for cid in (result.get("selected") or [])[:50]:
        lines.append(f"- {cid}")
    if len(result.get("selected") or []) > 50:
        lines.append(f"- ... and {len(result['selected']) - 50} more")
    qs = result.get("quality_summary")
    if qs:
        lines.extend([
            "",
            "## Quality summary",
            "",
            f"- Mean CSI: {qs.get('mean_csi')}  Mean ending strength: {qs.get('mean_ending_strength')}",
            f"- Bucket coverage: {qs.get('bucket_coverage')}  Low ending ratio: {qs.get('low_ending_ratio')}",
        ])
        items = result.get("selected_items") or []
        by_csi = sorted([c for c in items if (c.get("quality") or {}).get("csi_score") is not None], key=lambda c: float((c.get("quality") or {}).get("csi_score", 0)), reverse=True)
        by_end = sorted([c for c in items if (c.get("quality") or {}).get("ending_strength") is not None], key=lambda c: float((c.get("quality") or {}).get("ending_strength", 0)))
        if by_csi:
            lines.extend(["", "### Top 5 by CSI", ""])
            for c in by_csi[:5]:
                lines.append(f"- {c.get('candidate_id')}: {c.get('quality', {}).get('csi_score')}")
        if by_end:
            lines.extend(["", "### Bottom 5 by ending strength", ""])
            for c in by_end[:5]:
                lines.append(f"- {c.get('candidate_id')}: {c.get('quality', {}).get('ending_strength')}")
    lines.append("")
    lines.append("See JSON for full selected_items and constraint_satisfaction.")
    md_path.write_text("\n".join(lines))
    print(f"Solved. Written: {out_path}  {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
