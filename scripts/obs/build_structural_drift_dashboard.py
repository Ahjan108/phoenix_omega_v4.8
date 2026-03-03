#!/usr/bin/env python3
"""
Structural Drift Dashboard

Input:
- One wave folder of compiled plans OR a plan list
- Optional similarity index (for historical baseline)

Output:
- artifacts/drift/summary.json
- artifacts/drift/report.html
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from collections import Counter
from typing import Any, Dict, List, Tuple


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_plan_paths(plans_dir: str) -> List[str]:
    paths = []
    for fn in os.listdir(plans_dir):
        if fn.endswith(".json"):
            paths.append(os.path.join(plans_dir, fn))
    return sorted(paths)


def mode_share(values: List[str]) -> Tuple[float, str, int]:
    if not values:
        return 0.0, "", 0
    c = Counter(values)
    val, cnt = c.most_common(1)[0]
    return cnt / len(values), val, cnt


def normalize_band_seq(plan: Dict[str, Any]) -> str:
    seq = plan.get("emotional_temperature_sequence") or plan.get("dominant_band_sequence") or []
    return "-".join(str(x) for x in seq)


def normalize_ex_pattern(plan: Dict[str, Any]) -> str:
    xs = plan.get("exercise_chapters") or []
    return ",".join(str(int(x)) for x in xs)


def family_dominance_from_dist(dist: Dict[str, int]) -> float:
    if not dist:
        return 0.0
    total = sum(dist.values())
    if total == 0:
        return 0.0
    top = max(dist.values())
    return top / total


def family_dominance_from_vec(vec: List[int]) -> float:
    """When only a count vector is available (e.g. index row). Dominance = max/sum."""
    if not vec or sum(vec) == 0:
        return 0.0
    return max(vec) / sum(vec)


def compute_wave_metrics(plans: List[Dict[str, Any]]) -> Dict[str, Any]:
    arcs = [str(p.get("arc_id", "")) for p in plans]
    bands = [normalize_band_seq(p) for p in plans]
    slots = [str(p.get("slot_sig", "")) for p in plans]
    exps = [normalize_ex_pattern(p) for p in plans]

    arc_share, arc_mode, arc_cnt = mode_share(arcs)
    band_share, band_mode, band_cnt = mode_share(bands)
    slot_share, slot_mode, slot_cnt = mode_share(slots)
    exp_share, exp_mode, exp_cnt = mode_share(exps)

    distinct_band_shapes = len(set(bands))
    distinct_arcs = len(set(arcs))
    distinct_slot_sigs = len(set(slots))
    distinct_ex_patterns = len(set(exps))

    story_dom = []
    ex_dom = []
    tps_nonzero = []
    for p in plans:
        story_dist = p.get("story_family_distribution")
        if isinstance(story_dist, dict):
            story_dom.append(family_dominance_from_dist(story_dist))
        elif isinstance(p.get("story_fam_vec"), list):
            story_dom.append(family_dominance_from_vec(p["story_fam_vec"]))
        else:
            story_dom.append(0.0)

        ex_dist = p.get("exercise_family_distribution")
        if isinstance(ex_dist, dict):
            ex_dom.append(family_dominance_from_dist(ex_dist))
        elif isinstance(p.get("ex_fam_vec"), list):
            ex_dom.append(family_dominance_from_vec(p["ex_fam_vec"]))
        else:
            ex_dom.append(0.0)

        tps = p.get("teacher_presence_sequence") or []
        tps_nonzero.append(sum(1 for x in tps if int(x) > 0))

    # Per-author positioning (Writer Spec §24)
    positioning_profiles = [str(p.get("author_positioning_profile") or "") for p in plans]
    positioning_counts: Dict[str, int] = {}
    for pp in positioning_profiles:
        if pp:
            positioning_counts[pp] = positioning_counts.get(pp, 0) + 1
    author_ids = [str(p.get("author_id") or "") for p in plans]
    author_counts: Dict[str, int] = {}
    for a in author_ids:
        if a:
            author_counts[a] = author_counts.get(a, 0) + 1

    # DEV SPEC 3: Emotional role distribution and signatures
    role_sigs_list = [str(p.get("emotional_role_sig") or "") for p in plans]
    role_sig_counts: Dict[str, int] = {}
    for rs in role_sigs_list:
        if rs:
            role_sig_counts[rs] = role_sig_counts.get(rs, 0) + 1
    top_role_sigs = sorted(role_sig_counts.items(), key=lambda x: -x[1])[:10]
    role_dist: Dict[str, int] = {}
    for p in plans:
        seq = p.get("emotional_role_sequence") or []
        for r in seq:
            if r:
                role_dist[r] = role_dist.get(r, 0) + 1
    role_band_pairs: List[Tuple[str, str]] = []
    for p in plans:
        roles = p.get("emotional_role_sequence") or []
        bands = p.get("emotional_temperature_sequence") or p.get("dominant_band_sequence") or []
        for i in range(min(len(roles), len(bands))):
            if roles[i] and bands[i] is not None:
                role_band_pairs.append((str(roles[i]), str(bands[i])))
    role_band_counts: Dict[str, int] = {}
    for rb in role_band_pairs:
        role_band_counts[rb] = role_band_counts.get(rb, 0) + 1

    def safe_mean(xs: List[float]) -> float:
        return float(statistics.mean(xs)) if xs else 0.0

    return {
        "n_books": len(plans),
        "mode_shares": {
            "arc_id": {"share": arc_share, "mode": arc_mode, "count": arc_cnt},
            "band_seq": {"share": band_share, "mode": band_mode, "count": band_cnt},
            "slot_sig": {"share": slot_share, "mode": slot_mode, "count": slot_cnt},
            "exercise_pattern": {"share": exp_share, "mode": exp_mode, "count": exp_cnt},
        },
        "diversity": {
            "distinct_arcs": distinct_arcs,
            "distinct_band_shapes": distinct_band_shapes,
            "distinct_slot_sigs": distinct_slot_sigs,
            "distinct_exercise_patterns": distinct_ex_patterns,
        },
        "dominance": {
            "avg_story_family_dominance": safe_mean(story_dom),
            "avg_exercise_family_dominance": safe_mean(ex_dom),
        },
        "teacher_presence": {
            "avg_chapters_with_teacher_presence": float(statistics.mean(tps_nonzero)) if tps_nonzero else 0.0,
        },
        "author_positioning": {
            "profile_counts": positioning_counts,
            "author_counts": author_counts,
        },
        "emotional_roles": {
            "role_distribution": role_dist,
            "top_role_sigs": top_role_sigs,
            "role_band_counts": role_band_counts,
        },
    }


def load_index_jsonl(path: str) -> List[Dict[str, Any]]:
    if not path or not os.path.exists(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def compute_baseline_from_index(rows: List[Dict[str, Any]], max_rows: int = 2000) -> Dict[str, Any]:
    rows = rows[-max_rows:] if len(rows) > max_rows else rows
    pseudo_plans = []
    for r in rows:
        pseudo_plans.append({
            "arc_id": r.get("arc_id", ""),
            "slot_sig": r.get("slot_sig", ""),
            "exercise_chapters": r.get("exercise_chapters", []),
            "emotional_temperature_sequence": r.get("band_seq", []),
            "story_fam_vec": r.get("story_fam_vec", []),
            "ex_fam_vec": r.get("ex_fam_vec", []),
            "teacher_presence_sequence": r.get("tps", []),
        })
    return compute_wave_metrics(pseudo_plans)


def render_html(wave: Dict[str, Any], baseline: Dict[str, Any] | None) -> str:
    def pct(x: float) -> str:
        return f"{x * 100:.1f}%"

    pos = wave.get("author_positioning") or {}
    profile_counts = pos.get("profile_counts") or {}
    author_counts = pos.get("author_counts") or {}
    profile_rows = "".join(
        f'<tr><td>{k or "(none)"}</td><td>{v}</td></tr>' for k, v in sorted(profile_counts.items())
    ) or "<tr><td colspan=\"2\">—</td></tr>"
    author_rows = "".join(
        f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in sorted(author_counts.items())
    ) or "<tr><td colspan=\"2\">—</td></tr>"

    er = wave.get("emotional_roles") or {}
    role_dist = er.get("role_distribution") or {}
    top_role_sigs = er.get("top_role_sigs") or []
    role_band_counts = er.get("role_band_counts") or {}
    role_dist_rows = "".join(
        f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in sorted(role_dist.items())
    ) or "<tr><td colspan=\"2\">—</td></tr>"
    top_role_sigs_str = ", ".join(f"{sig}({c})" for sig, c in top_role_sigs[:10]) or "—"
    def _rb_key(k: Any) -> str:
        if isinstance(k, tuple):
            return f"{k[0]}:{k[1]}"
        return str(k)
    role_band_str = ", ".join(f"{_rb_key(rb)}({c})" for rb, c in sorted(role_band_counts.items(), key=lambda x: -x[1])[:15]) or "—"

    def row(label: str, w: Dict[str, Any], b: Dict[str, Any]) -> str:
        wm = (w.get("mode") or "")[:32]
        bm = (b.get("mode") or "")[:32]
        return f"""
        <tr>
          <td>{label}</td>
          <td>{pct(w['share'])} (mode: {wm})</td>
          <td>{pct(b['share'])} (mode: {bm})</td>
        </tr>
        """

    ws = wave["mode_shares"]
    bs = (
        baseline["mode_shares"]
        if baseline
        else {
            "arc_id": {"share": 0, "mode": ""},
            "band_seq": {"share": 0, "mode": ""},
            "slot_sig": {"share": 0, "mode": ""},
            "exercise_pattern": {"share": 0, "mode": ""},
        }
    )

    dom_baseline = baseline["dominance"] if baseline else {"avg_story_family_dominance": 0.0, "avg_exercise_family_dominance": 0.0}
    tps_baseline = baseline["teacher_presence"]["avg_chapters_with_teacher_presence"] if baseline else 0.0

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Structural Drift Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    h1 {{ margin-bottom: 6px; }}
    .sub {{ color: #444; margin-bottom: 18px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; }}
    th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    .kpi {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 12px; }}
    .big {{ font-size: 22px; font-weight: 700; }}
    .muted {{ color: #555; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>Structural Drift Dashboard</h1>
  <div class="sub">Wave size: <b>{wave['n_books']}</b> | Baseline: trailing index</div>

  <div class="kpi">
    <div class="card"><div class="big">{wave['diversity']['distinct_arcs']}</div><div class="muted">Distinct arcs</div></div>
    <div class="card"><div class="big">{wave['diversity']['distinct_band_shapes']}</div><div class="muted">Distinct band shapes</div></div>
    <div class="card"><div class="big">{wave['diversity']['distinct_slot_sigs']}</div><div class="muted">Distinct slot signatures</div></div>
    <div class="card"><div class="big">{wave['diversity']['distinct_exercise_patterns']}</div><div class="muted">Distinct exercise patterns</div></div>
  </div>

  <h2>Mode Share vs Baseline</h2>
  <table>
    <tr><th>Dimension</th><th>Wave</th><th>Baseline</th></tr>
    {row("arc_id", ws["arc_id"], bs["arc_id"])}
    {row("band_seq", ws["band_seq"], bs["band_seq"])}
    {row("slot_sig", ws["slot_sig"], bs["slot_sig"])}
    {row("exercise_pattern", ws["exercise_pattern"], bs["exercise_pattern"])}
  </table>

  <h2>Dominance</h2>
  <table>
    <tr><th>Metric</th><th>Wave</th><th>Baseline</th></tr>
    <tr><td>Avg story family dominance</td><td>{pct(wave['dominance']['avg_story_family_dominance'])}</td><td>{pct(dom_baseline['avg_story_family_dominance'])}</td></tr>
    <tr><td>Avg exercise family dominance</td><td>{pct(wave['dominance']['avg_exercise_family_dominance'])}</td><td>{pct(dom_baseline['avg_exercise_family_dominance'])}</td></tr>
    <tr><td>Avg chapters w/ teacher presence</td><td>{wave['teacher_presence']['avg_chapters_with_teacher_presence']:.2f}</td><td>{tps_baseline:.2f}</td></tr>
  </table>

  <h2>Author positioning (Writer Spec §24)</h2>
  <table>
    <tr><th>Profile</th><th>Count</th></tr>
    {profile_rows}
  </table>
  <table>
    <tr><th>Author</th><th>Count</th></tr>
    {author_rows}
  </table>

  <h2>Emotional roles (DEV SPEC 3)</h2>
  <table>
    <tr><th>Role</th><th>Count</th></tr>
    {role_dist_rows}
  </table>
  <p><b>Top 10 role signatures:</b> {top_role_sigs_str}</p>
  <p><b>Role × band (counts):</b> {role_band_str}</p>

</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Structural drift dashboard: wave metrics + HTML report")
    ap.add_argument("--plans-dir", help="Wave plans directory (compiled plan JSONs)")
    ap.add_argument("--plan-list", help="Text file with plan paths (one per line)")
    ap.add_argument("--index", default="artifacts/catalog_similarity/index.jsonl", help="Similarity index for baseline")
    ap.add_argument("--out-dir", default="artifacts/drift", help="Output directory")
    args = ap.parse_args()

    if not args.plans_dir and not args.plan_list:
        print("Provide --plans-dir or --plan-list", file=sys.stderr)
        return 1

    if args.plans_dir:
        paths = list_plan_paths(args.plans_dir)
    else:
        with open(args.plan_list, "r", encoding="utf-8") as f:
            paths = [ln.strip() for ln in f if ln.strip()]

    plans = [load_json(p) for p in paths]
    wave = compute_wave_metrics(plans)
    idx = load_index_jsonl(args.index)
    baseline = compute_baseline_from_index(idx) if idx else None

    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"wave": wave, "baseline": baseline}, f, ensure_ascii=False, indent=2)

    html = render_html(wave, baseline)
    with open(os.path.join(args.out_dir, "report.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print("DRIFT DASHBOARD: wrote")
    print(f"  - {os.path.join(args.out_dir, 'summary.json')}")
    print(f"  - {os.path.join(args.out_dir, 'report.html')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
