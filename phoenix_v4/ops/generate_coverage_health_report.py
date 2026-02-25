"""
Weekly coverage health report. Ops-owned; run on schedule (cron or CI).

Outputs:
  artifacts/ops/coverage_health_weekly_{date}.md
  artifacts/ops/coverage_health_weekly_{date}.csv
  artifacts/ops/coverage_health_weekly_{date}.json

Per-tuple metrics: binding exists, arc exists, story count, band counts, required bands missing,
min depth satisfied, last story update, risk score (BLOCKER | RED | YELLOW | GREEN).

Summary: total viable, total blocked, top 10 risk tuples, story growth rate (vs last week if available).
Content team may only act when risk in {BLOCKER, RED}; backlog CSV updated by ops only.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_ROOT = REPO_ROOT / "config"
ATOMS_ROOT = REPO_ROOT / "atoms"
ARCS_ROOT = CONFIG_ROOT / "source_of_truth" / "master_arcs"
ARTIFACTS_OPS = REPO_ROOT / "artifacts" / "ops"

try:
    import yaml
except ImportError:
    yaml = None

# Arc filename: persona__topic__engine__format.yaml
ARC_FILE_PATTERN = re.compile(r"^([a-z0-9_]+)__([a-z0-9_]+)__([a-z0-9_]+)__(F[0-9]+)\.yaml$", re.I)


@dataclass
class TupleRow:
    persona: str
    topic: str
    engine: str
    format_id: str
    binding_exists: bool
    arc_exists: bool
    arc_path_rel: str  # relative path for report
    arc_id: str
    story_count: int
    band_counts: dict[int, int]  # band -> count
    required_bands: list[int]
    required_bands_missing: list[int]
    min_depth_satisfied: bool
    last_story_update: Optional[float]  # mtime or None
    story_pool_path_rel: str
    risk: str  # BLOCKER | RED | YELLOW | GREEN
    deficit_codes: list[str]  # NO_BINDING, NO_ARC, NO_STORY_POOL, POOL_TOO_SHALLOW, BAND_DEFICIT


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _bindings_topic_key(topic_slug: str) -> str:
    if topic_slug == "grief_topic":
        return "grief"
    return topic_slug


def _get_gate_config() -> dict[str, Any]:
    path = CONFIG_ROOT / "gates.yaml"
    data = _load_yaml(path)
    tvc = data.get("tuple_viability") or {}
    ch = data.get("coverage_health") or {}
    return {
        "min_story_pool_size": int(tvc.get("min_story_pool_size", 12)),
        "band_distribution_skew_threshold": float(ch.get("band_distribution_skew_threshold", 0.6)),
    }


def _load_story_atoms_and_mtime(
    atoms_root: Path,
    persona: str,
    topic: str,
    engine: str,
) -> tuple[list[dict[str, Any]], Optional[float]]:
    """Return (atoms, last_mtime of CANONICAL.txt)."""
    from phoenix_v4.planning.assembly_compiler import _parse_canonical_txt
    path = atoms_root / persona / topic / engine / "CANONICAL.txt"
    if not path.exists():
        return [], None
    try:
        atoms = _parse_canonical_txt(path)
        mtime = path.stat().st_mtime
        return atoms, mtime
    except (ValueError, OSError):
        return [], path.stat().st_mtime if path.exists() else None


def _required_bands_from_arc_data(arc_data: dict) -> list[int]:
    curve = arc_data.get("emotional_curve") or []
    out: list[int] = []
    for b in curve:
        try:
            v = int(b)
            if 1 <= v <= 5 and v not in out:
                out.append(v)
        except (TypeError, ValueError):
            continue
    return sorted(out)


def _band_distribution_skew(band_counts: dict[int, int]) -> float:
    """Max share minus fair share. 0 = even; high = one band dominates."""
    if not band_counts:
        return 0.0
    total = sum(band_counts.values())
    if total == 0:
        return 0.0
    n = len(band_counts)
    fair = 1.0 / n
    max_share = max(c / total for c in band_counts.values())
    return max(0.0, max_share - fair)


def _compute_risk(
    binding_exists: bool,
    arc_exists: bool,
    story_count: int,
    min_depth: int,
    required_bands_missing: list,
    band_skew: float,
    skew_threshold: float,
) -> str:
    if not binding_exists or not arc_exists:
        return "BLOCKER"
    if story_count < min_depth or required_bands_missing:
        return "RED"
    if band_skew > skew_threshold:
        return "YELLOW"
    return "GREEN"


def _discover_tuples(arcs_root: Path) -> list[tuple[str, str, str, str]]:
    """List (persona, topic, engine, format_id) from master_arcs filenames."""
    out: list[tuple[str, str, str, str]] = []
    if not arcs_root.is_dir():
        return out
    for path in arcs_root.glob("*.yaml"):
        m = ARC_FILE_PATTERN.match(path.name)
        if m:
            out.append((m.group(1), m.group(2), m.group(3), m.group(4)))
    return sorted(out, key=lambda t: (t[0], t[1], t[2], t[3]))


def generate_report(repo_root: Optional[Path] = None) -> tuple[list[TupleRow], dict[str, Any]]:
    """Compute per-tuple metrics and summary. Returns (rows, summary_dict)."""
    root = repo_root or REPO_ROOT
    config_root = root / "config"
    atoms_root = root / "atoms"
    arcs_root = config_root / "source_of_truth" / "master_arcs"
    bindings_path = config_root / "topic_engine_bindings.yaml"
    bindings = _load_yaml(bindings_path)
    cfg = _get_gate_config()
    min_depth = cfg["min_story_pool_size"]
    skew_threshold = cfg["band_distribution_skew_threshold"]

    tuples = _discover_tuples(arcs_root)
    rows: list[TupleRow] = []

    for persona, topic, engine, format_id in tuples:
        bkey = _bindings_topic_key(topic)
        topic_config = bindings.get(bkey)
        allowed = (topic_config or {}).get("allowed_engines") or []
        binding_exists = topic_config is not None and engine in allowed

        arc_path = arcs_root / f"{persona}__{topic}__{engine}__{format_id}.yaml"
        arc_exists = arc_path.exists()
        arc_data = _load_yaml(arc_path) if arc_exists else {}
        required_bands = _required_bands_from_arc_data(arc_data)

        story_atoms, last_story_mtime = _load_story_atoms_and_mtime(atoms_root, persona, topic, engine)
        story_count = len(story_atoms)
        band_counts: dict[int, int] = defaultdict(int)
        for a in story_atoms:
            band_counts[a.get("band", 3)] += 1
        bands_in_pool = set(band_counts.keys())
        required_bands_missing = [b for b in required_bands if b not in bands_in_pool]
        min_depth_satisfied = story_count >= min_depth
        band_skew = _band_distribution_skew(dict(band_counts))

        risk = _compute_risk(
            binding_exists,
            arc_exists,
            story_count,
            min_depth,
            required_bands_missing,
            band_skew,
            skew_threshold,
        )

        deficit_codes: list[str] = []
        if not binding_exists:
            deficit_codes.append("NO_BINDING")
        if not arc_exists:
            deficit_codes.append("NO_ARC")
        if story_count == 0:
            deficit_codes.append("NO_STORY_POOL")
        elif not min_depth_satisfied:
            deficit_codes.append("POOL_TOO_SHALLOW")
        if required_bands_missing:
            deficit_codes.append("BAND_DEFICIT")

        arc_path_rel = f"config/source_of_truth/master_arcs/{persona}__{topic}__{engine}__{format_id}.yaml"
        story_pool_path_rel = f"atoms/{persona}/{topic}/{engine}/CANONICAL.txt"
        arc_id_val = str(arc_data.get("arc_id", ""))

        rows.append(
            TupleRow(
                persona=persona,
                topic=topic,
                engine=engine,
                format_id=format_id,
                binding_exists=binding_exists,
                arc_exists=arc_exists,
                arc_path_rel=arc_path_rel,
                arc_id=arc_id_val,
                story_count=story_count,
                band_counts=dict(band_counts),
                required_bands=required_bands,
                required_bands_missing=required_bands_missing,
                min_depth_satisfied=min_depth_satisfied,
                last_story_update=last_story_mtime,
                story_pool_path_rel=story_pool_path_rel,
                risk=risk,
                deficit_codes=deficit_codes,
            )
        )

    # Summary
    viable = sum(1 for r in rows if r.risk == "GREEN")
    blocked = sum(1 for r in rows if r.risk == "BLOCKER")
    red = sum(1 for r in rows if r.risk == "RED")
    yellow = sum(1 for r in rows if r.risk == "YELLOW")
    total_story = sum(r.story_count for r in rows)
    top_risk = sorted(rows, key=lambda r: ("BLOCKER" != r.risk, "RED" != r.risk, "YELLOW" != r.risk, -r.story_count))[:10]

    now_ts = datetime.now(timezone.utc).timestamp()
    stale_14 = sum(1 for r in rows if r.last_story_update is not None and (now_ts - r.last_story_update) / 86400 > 14)
    stale_30 = sum(1 for r in rows if r.last_story_update is not None and (now_ts - r.last_story_update) / 86400 > 30)
    stale_60 = sum(1 for r in rows if r.last_story_update is not None and (now_ts - r.last_story_update) / 86400 > 60)

    deficit_counter: dict[str, int] = defaultdict(int)
    for r in rows:
        for c in r.deficit_codes:
            deficit_counter[c] += 1
    top_deficit_codes = [{"code": k, "count": v} for k, v in sorted(deficit_counter.items(), key=lambda x: -x[1])]

    summary = {
        "total_tuples": len(rows),
        "risk_counts": {"BLOCKER": blocked, "RED": red, "YELLOW": yellow, "GREEN": viable},
        "viable_tuples": viable,
        "blocked_tuples": blocked,
        "red_tuples": red,
        "viable_green": viable,
        "blocked": blocked,
        "red": red,
        "yellow": yellow,
        "total_story_atoms": total_story,
        "top_10_risk_tuples": [
            f"{r.persona},{r.topic},{r.engine},{r.format_id} ({r.risk})"
            for r in top_risk
        ],
        "top_deficit_codes": top_deficit_codes,
        "aging": {"stale_over_days_14": stale_14, "stale_over_days_30": stale_30, "stale_over_days_60": stale_60},
        "velocity": {"week_over_week_story_delta_total": None, "week_over_week_story_delta_median": None},
        "delta_vs_last_week": None,
        "story_growth_rate": None,
    }
    return rows, summary


def _git_commit(repo_root: Path) -> Optional[str]:
    try:
        import subprocess
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if r.returncode == 0 and r.stdout:
            return r.stdout.strip()
    except Exception:
        pass
    return None


def _load_previous_week_summary(out_dir: Path, report_date: str) -> Optional[dict]:
    """Try to parse previous week's report date (report_date - 7 days) and load its summary."""
    try:
        from datetime import datetime, timedelta
        dt = datetime.strptime(report_date, "%Y-%m-%d")
        prev = (dt - timedelta(days=7)).strftime("%Y-%m-%d")
        base = f"coverage_health_weekly_{prev}"
        path = out_dir / f"{base}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("summary") or data
    except Exception:
        return None


def _write_artifacts(
    rows: list[TupleRow],
    summary: dict[str, Any],
    date_str: str,
    out_dir: Path,
    repo_root: Path,
    config_snapshot: dict[str, Any],
    min_depth: int,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"coverage_health_weekly_{date_str}"
    now = datetime.now(timezone.utc)
    now_ts = now.timestamp()

    # Velocity: compare to previous week if available
    prev_summary = _load_previous_week_summary(out_dir, date_str)
    if prev_summary is not None and summary.get("total_story_atoms") is not None:
        prev_total = prev_summary.get("total_story_atoms")
        if prev_total is not None:
            delta_total = summary["total_story_atoms"] - int(prev_total)
            summary["velocity"]["week_over_week_story_delta_total"] = delta_total
            summary["velocity"]["week_over_week_story_delta_median"] = None  # would need per-tuple prev

    # JSON (dashboard schema 1.0)
    json_path = out_dir / f"{base}.json"
    tuple_id_sep = "|"
    tuples_payload = []
    for r in rows:
        tuple_id = f"{r.persona}{tuple_id_sep}{r.topic}{tuple_id_sep}{r.engine}{tuple_id_sep}{r.format_id}"
        last_utc: Optional[str] = None
        age_days: Optional[int] = None
        if r.last_story_update is not None:
            last_utc = datetime.fromtimestamp(r.last_story_update, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            age_days = int((now_ts - r.last_story_update) / 86400)
        tuples_payload.append({
            "tuple_id": tuple_id,
            "persona_id": r.persona,
            "topic_id": r.topic,
            "engine_id": r.engine,
            "format_id": r.format_id,
            "binding": {"exists": r.binding_exists},
            "arc": {"exists": r.arc_exists, "path": r.arc_path_rel, "arc_id": r.arc_id},
            "story_pool": {
                "exists": r.story_count > 0,
                "path": r.story_pool_path_rel,
                "story_count": r.story_count,
                "min_required": min_depth,
                "last_modified_utc": last_utc,
                "age_days": age_days,
            },
            "bands": {
                "required_bands": r.required_bands,
                "band_counts": r.band_counts,
                "missing_bands": r.required_bands_missing,
            },
            "deficit_codes": r.deficit_codes,
            "risk": r.risk,
        })
    by_risk: dict[str, list[str]] = defaultdict(list)
    by_persona: dict[str, list[str]] = defaultdict(list)
    by_topic: dict[str, list[str]] = defaultdict(list)
    for t in tuples_payload:
        tid = t["tuple_id"]
        by_risk[t["risk"]].append(tid)
        by_persona[t["persona_id"]].append(tid)
        by_topic[t["topic_id"]].append(tid)

    payload = {
        "schema_version": "1.0",
        "generated_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_date": date_str,
        "repo": {
            "root": str(repo_root),
            "git": {"commit": _git_commit(repo_root)},
        },
        "config_snapshot": config_snapshot,
        "summary": summary,
        "tuples": tuples_payload,
        "indices": {
            "by_risk": dict(by_risk),
            "by_persona": dict(by_persona),
            "by_topic": dict(by_topic),
        },
        "date": date_str,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # CSV (full table; backward compatible columns)
    csv_path = out_dir / f"{base}.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "persona", "topic", "engine", "format_id",
            "binding_exists", "arc_exists", "story_count",
            "band_counts", "required_bands_missing", "min_depth_satisfied",
            "last_story_update", "risk", "deficit_codes",
        ])
        for r in rows:
            w.writerow([
                r.persona, r.topic, r.engine, r.format_id,
                r.binding_exists, r.arc_exists, r.story_count,
                json.dumps(r.band_counts), json.dumps(r.required_bands_missing),
                r.min_depth_satisfied,
                r.last_story_update,
                r.risk,
                json.dumps(r.deficit_codes),
            ])

    # Markdown summary
    md_path = out_dir / f"{base}.md"
    lines = [
        f"# Coverage Health Weekly Report — {date_str}",
        "",
        "## Summary",
        f"- **Total tuples:** {summary['total_tuples']}",
        f"- **Viable (GREEN):** {summary['viable_green']}",
        f"- **Blocked (BLOCKER):** {summary['blocked']}",
        f"- **RED:** {summary['red']}",
        f"- **YELLOW:** {summary['yellow']}",
        f"- **Total STORY atoms:** {summary['total_story_atoms']}",
        "",
        "## Top 10 risk tuples",
        ""
    ]
    for t in summary["top_10_risk_tuples"]:
        lines.append(f"- {t}")
    lines.extend([
        "",
        "## Reopen content rule",
        "Content team may only act when risk in {BLOCKER, RED}. Backlog CSV updated by ops only.",
        "",
        "## Full table",
        "See CSV and JSON artifacts for per-tuple metrics.",
        "",
    ])
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate weekly coverage health report")
    ap.add_argument("--repo", type=Path, default=None, help="Repo root")
    ap.add_argument("--date", default=None, help="Report date (YYYY-MM-DD); default today UTC")
    ap.add_argument("--out-dir", type=Path, default=None, help="Output dir (default: artifacts/ops)")
    args = ap.parse_args()

    repo_root = args.repo or REPO_ROOT
    date_str = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = args.out_dir or repo_root / "artifacts" / "ops"

    gate_cfg = _get_gate_config()
    config_snapshot = {
        "min_story_pool_size": gate_cfg.get("min_story_pool_size", 12),
        "band_distribution_skew_threshold": gate_cfg.get("band_distribution_skew_threshold", 0.6),
    }
    path_gates = repo_root / "config" / "gates.yaml"
    if path_gates.exists() and yaml:
        g = _load_yaml(path_gates)
        tvc = g.get("tuple_viability") or {}
        config_snapshot["min_teacher_exercise_pool"] = int(tvc.get("min_teacher_exercise_pool", 5))

    rows, summary = generate_report(repo_root=repo_root)
    _write_artifacts(
        rows, summary, date_str, out_dir,
        repo_root=repo_root,
        config_snapshot=config_snapshot,
        min_depth=config_snapshot["min_story_pool_size"],
    )

    print(f"Report written: {out_dir}/coverage_health_weekly_{date_str}.{{md,csv,json}}")
    print(f"Viable: {summary['viable_green']}  Blocked: {summary['blocked']}  RED: {summary['red']}  YELLOW: {summary['yellow']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
