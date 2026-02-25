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
import math
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


def _get_alerts_config() -> dict[str, Any]:
    path = CONFIG_ROOT / "gates.yaml"
    data = _load_yaml(path)
    return data.get("coverage_health_alerts") or {}


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


def _discover_tuples_from_catalog(config_root: Path, bindings: dict, formats: list[str]) -> list[tuple[str, str, str, str]]:
    """
    List (persona, topic, engine, format_id) from catalog universe:
    personas × (topics with bindings) × allowed_engines × formats.
    Ensures NO_ARC can appear for tuples that have no arc file yet.
    """
    out: list[tuple[str, str, str, str]] = []
    # Personas from canonical config
    personas_path = config_root / "catalog_planning" / "canonical_personas.yaml"
    personas_data = _load_yaml(personas_path)
    personas_list = personas_data.get("personas") or []
    if not isinstance(personas_list, list):
        personas_list = []
    personas = [str(p) for p in personas_list if p]

    # Topics = bindings keys that have allowed_engines
    topics: list[str] = []
    for k, v in bindings.items():
        if k in ("---", "notes") or not isinstance(v, dict):
            continue
        allowed = v.get("allowed_engines") or v.get("engines")
        if allowed:
            topics.append(k)

    for persona in personas:
        for topic in topics:
            bkey = _bindings_topic_key(topic)
            topic_config = bindings.get(bkey)
            if not topic_config or not isinstance(topic_config, dict):
                continue
            allowed_engines = topic_config.get("allowed_engines") or topic_config.get("engines") or []
            for engine in allowed_engines:
                for format_id in formats:
                    out.append((persona, topic, str(engine), str(format_id)))
    return sorted(out, key=lambda t: (t[0], t[1], t[2], t[3]))


def _discover_tuples_arc_only(arcs_root: Path) -> list[tuple[str, str, str, str]]:
    """Legacy: list (persona, topic, engine, format_id) from master_arcs filenames only."""
    out: list[tuple[str, str, str, str]] = []
    if not arcs_root.is_dir():
        return out
    for path in arcs_root.glob("*.yaml"):
        m = ARC_FILE_PATTERN.match(path.name)
        if m:
            out.append((m.group(1), m.group(2), m.group(3), m.group(4)))
    return sorted(out, key=lambda t: (t[0], t[1], t[2], t[3]))


def _get_coverage_formats(repo_root: Path) -> list[str]:
    """Formats for coverage tuple universe (personas × topics × engines × formats)."""
    path = repo_root / "config" / "gates.yaml"
    data = _load_yaml(path)
    ch = data.get("coverage_health") or {}
    formats = ch.get("formats")
    if isinstance(formats, list) and formats:
        return [str(f) for f in formats]
    return ["F006"]


def generate_report(repo_root: Optional[Path] = None) -> tuple[list[TupleRow], dict[str, Any]]:
    """Compute per-tuple metrics and summary. Returns (rows, summary_dict).
    Tuple universe = catalog (personas × topics × allowed_engines × formats) so NO_ARC appears for missing arcs.
    """
    root = repo_root or REPO_ROOT
    config_root = root / "config"
    atoms_root = root / "atoms"
    arcs_root = config_root / "source_of_truth" / "master_arcs"
    bindings_path = config_root / "topic_engine_bindings.yaml"
    bindings = _load_yaml(bindings_path)
    cfg = _get_gate_config()
    min_depth = cfg["min_story_pool_size"]
    skew_threshold = cfg["band_distribution_skew_threshold"]
    formats = _get_coverage_formats(root)

    tuples = _discover_tuples_from_catalog(config_root, bindings, formats)
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
        from datetime import timedelta
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


def _load_report_for_date(out_dir: Path, report_date: str) -> tuple[Optional[dict], Optional[Path]]:
    """Load report JSON for given date. Returns (data, path) or (None, path)."""
    try:
        base = f"coverage_health_weekly_{report_date}"
        path = out_dir / f"{base}.json"
        if not path.exists():
            return None, path
        return json.loads(path.read_text(encoding="utf-8")), path
    except Exception:
        return None, out_dir / f"coverage_health_weekly_{report_date}.json"


def _load_previous_week_report(out_dir: Path, report_date: str) -> Optional[dict]:
    """Load full previous week report (tuples + summary) for v1.1 delta tracking."""
    from datetime import timedelta
    dt = datetime.strptime(report_date, "%Y-%m-%d")
    prev = (dt - timedelta(days=7)).strftime("%Y-%m-%d")
    data, _ = _load_report_for_date(out_dir, prev)
    return data


def _previous_report_meta(out_dir: Path, report_date: str) -> dict[str, Any]:
    """Build previous_report block: expected_report_date, loaded, path, git_commit."""
    from datetime import timedelta
    dt = datetime.strptime(report_date, "%Y-%m-%d")
    expected = (dt - timedelta(days=7)).strftime("%Y-%m-%d")
    data, path = _load_report_for_date(out_dir, expected)
    rel_path = f"artifacts/ops/coverage_health_weekly_{expected}.json"
    return {
        "expected_report_date": expected,
        "loaded": data is not None,
        "path": rel_path,
        "git_commit": (data or {}).get("repo", {}).get("git", {}).get("commit") if data else None,
    }


def _stale_counts_from_summary(summary: dict) -> dict[str, int]:
    """Derive over_14/over_30/over_60 from summary.aging."""
    aging = summary.get("aging") or {}
    return {
        "over_14": int(aging.get("stale_over_days_14", 0)),
        "over_30": int(aging.get("stale_over_days_30", 0)),
        "over_60": int(aging.get("stale_over_days_60", 0)),
    }


def _build_deltas(
    tuples_payload: list[dict],
    summary: dict[str, Any],
    prev_report: Optional[dict],
) -> dict[str, Any]:
    """Build v1.1 deltas: global, by_persona, by_topic, by_tuple (only if prev_report loaded)."""
    if not prev_report:
        return {}
    prev_tuples = prev_report.get("tuples") or []
    prev_sum = prev_report.get("summary") or {}
    prev_by_id = {t.get("tuple_id"): t for t in prev_tuples if t.get("tuple_id")}

    # Global
    risk_names = ["BLOCKER", "RED", "YELLOW", "GREEN"]
    current_risk = {k: len([t for t in tuples_payload if t.get("risk") == k]) for k in risk_names}
    prev_risk = {k: len([t for t in prev_tuples if t.get("risk") == k]) for k in risk_names}
    delta_risk = {k: current_risk[k] - prev_risk[k] for k in risk_names}
    current_stale = _stale_counts_from_summary(summary)
    prev_stale = _stale_counts_from_summary(prev_sum)
    delta_stale = {k: current_stale[k] - prev_stale[k] for k in current_stale}
    total_story = sum(_story_count_from_tuple(t) for t in tuples_payload)
    prev_total_story = sum(_story_count_from_tuple(t) for t in prev_tuples)
    deltas: dict[str, Any] = {
        "global": {
            "story_count_total": {"current": total_story, "previous": prev_total_story, "delta": total_story - prev_total_story},
            "risk_counts": {"current": current_risk, "previous": prev_risk, "delta": delta_risk},
            "stale_counts": {"current": current_stale, "previous": prev_stale, "delta": delta_stale},
        },
        "by_persona": {},
        "by_topic": {},
        "by_tuple": {},
    }

    # By persona
    for persona_id in {t.get("persona_id") for t in tuples_payload if t.get("persona_id")}:
        cur_p = [t for t in tuples_payload if t.get("persona_id") == persona_id]
        prev_p = [t for t in prev_tuples if t.get("persona_id") == persona_id]
        cur_story = sum(_story_count_from_tuple(t) for t in cur_p)
        prev_story = sum(_story_count_from_tuple(t) for t in prev_p)
        cur_risk = {k: sum(1 for t in cur_p if t.get("risk") == k) for k in risk_names}
        prev_risk_p = {k: sum(1 for t in prev_p if t.get("risk") == k) for k in risk_names}
        cur_stale_30 = sum(1 for t in cur_p if (t.get("story_pool") or {}).get("age_days") is not None and (t.get("story_pool") or {}).get("age_days", 0) > 30)
        prev_stale_30 = sum(1 for t in prev_p if (t.get("story_pool") or {}).get("age_days") is not None and (t.get("story_pool") or {}).get("age_days", 0) > 30)
        deltas["by_persona"][persona_id] = {
            "story_count_total": {"current": cur_story, "previous": prev_story, "delta": cur_story - prev_story},
            "risk_counts_delta": {k: cur_risk[k] - prev_risk_p[k] for k in risk_names},
            "stale_over_30_delta": cur_stale_30 - prev_stale_30,
        }
    # By topic
    for topic_id in {t.get("topic_id") for t in tuples_payload if t.get("topic_id")}:
        cur_t = [t for t in tuples_payload if t.get("topic_id") == topic_id]
        prev_t = [t for t in prev_tuples if t.get("topic_id") == topic_id]
        cur_story = sum(_story_count_from_tuple(t) for t in cur_t)
        prev_story = sum(_story_count_from_tuple(t) for t in prev_t)
        cur_risk = {k: sum(1 for t in cur_t if t.get("risk") == k) for k in risk_names}
        prev_risk_t = {k: sum(1 for t in prev_t if t.get("risk") == k) for k in risk_names}
        cur_stale_30 = sum(1 for t in cur_t if (t.get("story_pool") or {}).get("age_days") is not None and (t.get("story_pool") or {}).get("age_days", 0) > 30)
        prev_stale_30 = sum(1 for t in prev_t if (t.get("story_pool") or {}).get("age_days") is not None and (t.get("story_pool") or {}).get("age_days", 0) > 30)
        deltas["by_topic"][topic_id] = {
            "story_count_total": {"current": cur_story, "previous": prev_story, "delta": cur_story - prev_story},
            "risk_counts_delta": {k: cur_risk[k] - prev_risk_t[k] for k in risk_names},
            "stale_over_30_delta": cur_stale_30 - prev_stale_30,
        }
    # By tuple
    for t in tuples_payload:
        tid = t.get("tuple_id")
        if not tid:
            continue
        prev_t = prev_by_id.get(tid)
        cur_story = _story_count_from_tuple(t)
        cur_risk = t.get("risk")
        cur_missing = list((t.get("bands") or {}).get("missing_bands") or [])
        cur_codes = set(t.get("deficit_codes") or [])
        if prev_t:
            prev_story = _story_count_from_tuple(prev_t)
            prev_risk = prev_t.get("risk")
            prev_missing = list((prev_t.get("bands") or {}).get("missing_bands") or [])
            prev_codes = set(prev_t.get("deficit_codes") or [])
            deltas["by_tuple"][tid] = {
                "risk": {"current": cur_risk, "previous": prev_risk},
                "story_count": {"current": cur_story, "previous": prev_story, "delta": cur_story - prev_story},
                "missing_bands": {"current": cur_missing, "previous": prev_missing},
                "deficit_codes": {"added": list(cur_codes - prev_codes), "removed": list(prev_codes - cur_codes)},
            }
        else:
            deltas["by_tuple"][tid] = {
                "risk": {"current": cur_risk, "previous": None},
                "story_count": {"current": cur_story, "previous": None, "delta": cur_story},
                "missing_bands": {"current": cur_missing, "previous": []},
                "deficit_codes": {"added": list(cur_codes), "removed": []},
            }
    return deltas


def _build_alerts(
    tuples_payload: list[dict],
    summary: dict[str, Any],
    prev_report: Optional[dict],
    out_dir: Path,
    report_date: str,
    alerts_config: dict[str, Any],
) -> dict[str, Any]:
    """Build v1.1 alerts: stagnation (by_persona, by_topic) and decay (global)."""
    alerts: dict[str, Any] = {"stagnation": {"by_persona": [], "by_topic": []}, "decay": {"global": []}}
    stag_cfg = alerts_config.get("stagnation") or {}
    decay_cfg = alerts_config.get("decay") or {}
    if not stag_cfg.get("enabled") and not decay_cfg.get("enabled"):
        return alerts

    # Stagnation: 4-week story delta
    if stag_cfg.get("enabled"):
        window_weeks = int(stag_cfg.get("window_weeks", 4))
        min_delta = int(stag_cfg.get("min_story_delta_total", 5))
        require_not_green = stag_cfg.get("require_risk_not_green", True)
        from datetime import timedelta
        dt = datetime.strptime(report_date, "%Y-%m-%d")
        old_date = (dt - timedelta(days=7 * window_weeks)).strftime("%Y-%m-%d")
        old_report, _ = _load_report_for_date(out_dir, old_date)
        weeks_loaded = 1 if prev_report else 0
        if old_report:
            weeks_loaded = min(window_weeks, 1 + (dt - datetime.strptime(old_date, "%Y-%m-%d")).days // 7)
        old_tuples = (old_report or {}).get("tuples") or []
        old_story_by_persona: dict[str, int] = defaultdict(int)
        old_story_by_topic: dict[str, int] = defaultdict(int)
        for t in old_tuples:
            old_story_by_persona[t.get("persona_id", "")] += _story_count_from_tuple(t)
            old_story_by_topic[t.get("topic_id", "")] += _story_count_from_tuple(t)
        cur_story_by_persona: dict[str, int] = defaultdict(int)
        cur_story_by_topic: dict[str, int] = defaultdict(int)
        for t in tuples_payload:
            cur_story_by_persona[t.get("persona_id", "")] += _story_count_from_tuple(t)
            cur_story_by_topic[t.get("topic_id", "")] += _story_count_from_tuple(t)
        # By persona
        for persona_id in set(cur_story_by_persona) | set(old_story_by_persona):
            story_delta_total = cur_story_by_persona.get(persona_id, 0) - old_story_by_persona.get(persona_id, 0)
            if story_delta_total >= min_delta:
                continue
            persona_tuples = [t for t in tuples_payload if t.get("persona_id") == persona_id]
            red_blocker = [t for t in persona_tuples if t.get("risk") in ("RED", "BLOCKER")]
            if require_not_green and not red_blocker:
                continue
            code_counts: dict[str, int] = defaultdict(int)
            for t in red_blocker:
                for c in t.get("deficit_codes") or []:
                    code_counts[c] += 1
            top_codes = [{"code": c, "count": n} for c, n in sorted(code_counts.items(), key=lambda x: -x[1])[:5]]
            alerts["stagnation"]["by_persona"].append({
                "persona_id": persona_id,
                "window_weeks": window_weeks,
                "weeks_loaded": weeks_loaded,
                "story_delta_total": story_delta_total,
                "red_or_blocker_tuples": len(red_blocker),
                "top_deficit_codes": top_codes,
                "recommendation": "Freeze releases for this persona until deficits resolve via backlog.",
            })
        # By topic
        for topic_id in set(cur_story_by_topic) | set(old_story_by_topic):
            story_delta_total = cur_story_by_topic.get(topic_id, 0) - old_story_by_topic.get(topic_id, 0)
            if story_delta_total >= min_delta:
                continue
            topic_tuples = [t for t in tuples_payload if t.get("topic_id") == topic_id]
            red_blocker = [t for t in topic_tuples if t.get("risk") in ("RED", "BLOCKER")]
            if require_not_green and not red_blocker:
                continue
            code_counts = defaultdict(int)
            for t in red_blocker:
                for c in t.get("deficit_codes") or []:
                    code_counts[c] += 1
            top_codes = [{"code": c, "count": n} for c, n in sorted(code_counts.items(), key=lambda x: -x[1])[:5]]
            alerts["stagnation"]["by_topic"].append({
                "topic_id": topic_id,
                "window_weeks": window_weeks,
                "weeks_loaded": weeks_loaded,
                "story_delta_total": story_delta_total,
                "red_or_blocker_tuples": len(red_blocker),
                "top_deficit_codes": top_codes,
                "recommendation": "Reopen content ONLY for tuples flagged with deficit codes per backlog CSV.",
            })

    # Decay: week-over-week thresholds
    if decay_cfg.get("enabled") and prev_report:
        prev_sum = prev_report.get("summary") or {}
        cur_stale = _stale_counts_from_summary(summary)
        prev_stale = _stale_counts_from_summary(prev_sum)
        thresh_30 = int(decay_cfg.get("stale_over_30_wow_increase_threshold", 10))
        thresh_60_abs = int(decay_cfg.get("stale_over_60_absolute_threshold", 20))
        thresh_rb = int(decay_cfg.get("red_blocker_wow_increase_threshold", 5))
        thresh_green = int(decay_cfg.get("green_wow_decrease_threshold", 5))
        delta_30 = cur_stale["over_30"] - prev_stale["over_30"]
        if delta_30 > thresh_30:
            alerts["decay"]["global"].append({
                "code": "STALE_OVER_30_SPIKE",
                "current": cur_stale["over_30"],
                "previous": prev_stale["over_30"],
                "delta": delta_30,
                "threshold": thresh_30,
                "recommendation": "Pause new tuple expansion. Address stale pools flagged >30d via backlog CSV.",
            })
        if cur_stale["over_60"] > thresh_60_abs:
            alerts["decay"]["global"].append({
                "code": "STALE_OVER_60_CAP",
                "current": cur_stale["over_60"],
                "threshold": thresh_60_abs,
                "recommendation": "Address stale pools >60d via backlog CSV before adding new content.",
            })
        by_risk = summary.get("risk_counts") or {}
        prev_risk = prev_sum.get("risk_counts") or {}
        cur_rb = int(by_risk.get("RED", 0)) + int(by_risk.get("BLOCKER", 0))
        prev_rb = int(prev_risk.get("RED", 0)) + int(prev_risk.get("BLOCKER", 0))
        if cur_rb - prev_rb > thresh_rb:
            alerts["decay"]["global"].append({
                "code": "RISK_REGRESSION",
                "current_red_blocker": cur_rb,
                "previous_red_blocker": prev_rb,
                "delta": cur_rb - prev_rb,
                "threshold": thresh_rb,
                "recommendation": "Pause releases. Resolve RED/BLOCKER deficits via backlog.",
            })
        cur_green = int(by_risk.get("GREEN", 0))
        prev_green = int(prev_risk.get("GREEN", 0))
        if prev_green - cur_green > thresh_green:
            alerts["decay"]["global"].append({
                "code": "GREEN_DECREASE",
                "current_green": cur_green,
                "previous_green": prev_green,
                "delta": prev_green - cur_green,
                "threshold": thresh_green,
                "recommendation": "Review tuples that regressed from GREEN; address via backlog.",
            })

    return alerts


def _band_entropy(proportions: dict[str, float]) -> float:
    """Shannon entropy of band distribution, normalized to [0, 1] (max = log2(5))."""
    total = sum(proportions.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for p in proportions.values():
        if p > 0:
            p_norm = p / total
            entropy -= p_norm * math.log2(p_norm)
    max_entropy = math.log2(5)
    return round(entropy / max_entropy, 4) if max_entropy > 0 else 0.0


def _compute_catalog_emotional_distribution(
    rows: list[TupleRow],
    prev_report: Optional[dict],
    report_date: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Phase 9: Catalog emotional distribution index (macro drift detection).
    Uses current catalog snapshot; drift is vs previous report (minimal compute path).
    """
    window_days = int(config.get("window_days", 90))
    band_names = ["1", "2", "3", "4", "5"]
    global_counts: dict[str, int] = defaultdict(int)
    for r in rows:
        for b, c in (r.band_counts or {}).items():
            k = str(int(b)) if b in (1, 2, 3, 4, 5) else None
            if k:
                global_counts[k] += c
    total = sum(global_counts.values())
    if total == 0:
        global_dist = {b: 0.0 for b in band_names}
        global_entropy = 0.0
    else:
        global_dist = {b: round(global_counts.get(b, 0) / total, 4) for b in band_names}
        global_entropy = _band_entropy(global_dist)

    # Brand-level entropy (placeholder: single brand = global until we have brand_id per tuple)
    brand_entropy: dict[str, float] = {}
    brand_range_path = CONFIG_ROOT / "catalog_planning" / "brand_emotional_range.yaml"
    if brand_range_path.exists() and yaml:
        br = _load_yaml(brand_range_path)
        brands_cfg = br.get("brands") or {}
        if brands_cfg:
            for brand_id in brands_cfg:
                brand_entropy[brand_id] = round(global_entropy, 4)
        if not brand_entropy:
            brand_entropy["phoenix"] = round(global_entropy, 4)
    else:
        brand_entropy["phoenix"] = round(global_entropy, 4)

    # Persona volatility index = normalized entropy of that persona's band distribution
    persona_volatility: dict[str, float] = {}
    by_persona: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in rows:
        for b, c in (r.band_counts or {}).items():
            if b in (1, 2, 3, 4, 5):
                by_persona[r.persona][str(b)] += c
    for persona_id, counts in by_persona.items():
        tot = sum(counts.values())
        if tot > 0:
            props = {b: float(counts.get(b, 0)) for b in band_names}
            persona_volatility[persona_id] = round(_band_entropy(props), 4)
        else:
            persona_volatility[persona_id] = 0.0

    # Drift vs previous window (previous report's global distribution)
    drift: dict[str, Any] = {}
    prev_ced = (prev_report or {}).get("catalog_emotional_distribution") or {}
    prev_global = prev_ced.get("global_band_distribution") or {}
    if prev_global and global_dist:
        for b in band_names:
            cur = global_dist.get(b, 0.0)
            prev = float(prev_global.get(b, 0.0))
            drift[f"band_{b}_share_delta"] = round(cur - prev, 4)
        drift["band_5_share_delta"] = drift.get("band_5_share_delta", 0.0)

    out: dict[str, Any] = {
        "window_days": window_days,
        "global_band_distribution": global_dist,
        "global_band_entropy": round(global_entropy, 4),
        "brand_band_entropy": brand_entropy,
        "persona_volatility_index": persona_volatility,
    }
    if drift:
        out["drift_vs_previous_window"] = drift
    return out


def _build_catalog_emotional_alerts(
    catalog_emotional: dict[str, Any],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Phase 9: Alerts for emotional flattening / band_5 drop / low persona volatility."""
    alerts_list: list[dict[str, Any]] = []
    ac = (config.get("catalog_emotional_distribution") or {}).get("alerts") or {}
    if not ac.get("enabled"):
        return alerts_list
    entropy_thresh = float(ac.get("entropy_below_threshold", 0.85))
    band5_drop_thresh = float(ac.get("band_5_share_drop_above", 0.03))
    volatility_thresh = float(ac.get("persona_volatility_below_threshold", 0.40))

    global_entropy = catalog_emotional.get("global_band_entropy") or 0.0
    if global_entropy < entropy_thresh:
        alerts_list.append({
            "code": "ENTROPY_BELOW_THRESHOLD",
            "current_entropy": global_entropy,
            "threshold": entropy_thresh,
            "recommendation": "Catalog emotional diversity is low. Review arc curves and story band mix to avoid mid-intensity flattening.",
        })

    drift = catalog_emotional.get("drift_vs_previous_window") or {}
    band5_delta = drift.get("band_5_share_delta")
    if band5_delta is not None and band5_delta < -band5_drop_thresh:
        alerts_list.append({
            "code": "BAND_5_SHARE_DROP",
            "band_5_share_delta": band5_delta,
            "threshold": band5_drop_thresh,
            "recommendation": "High-intensity (band 5) share dropped. Preserve emotional range; avoid convergence to mid-bands.",
        })

    persona_vol = catalog_emotional.get("persona_volatility_index") or {}
    low_volatility = [pid for pid, v in persona_vol.items() if v < volatility_thresh and v >= 0]
    if low_volatility:
        alerts_list.append({
            "code": "PERSONA_VOLATILITY_LOW",
            "persona_ids": sorted(low_volatility)[:20],
            "count": len(low_volatility),
            "threshold": volatility_thresh,
            "recommendation": "Personas with low emotional spread may flatten catalog. Consider diversifying band mix for these personas.",
        })

    return alerts_list


def _story_count_from_tuple(t: dict) -> int:
    """Extract story count from tuple (schema 1.0 or 1.1)."""
    sp = t.get("story_pool")
    if isinstance(sp, dict) and "story_count" in sp:
        return int(sp.get("story_count", 0))
    return int(t.get("story_count", 0))


def _compute_v11_deltas(
    tuples_payload: list[dict],
    summary: dict,
    prev_report: Optional[dict],
) -> tuple[dict, dict, list[dict], dict[str, Any], dict[str, list[str]]]:
    """
    Compute v1.1 fields: velocity_by_persona, velocity_by_topic, deficit_trend_delta,
    tuple_risk_trend, risk_transitions (for indices).
    Returns (velocity_by_persona, velocity_by_topic, deficit_trend_delta, tuple_risk_trend, risk_transitions).
    """
    velocity_by_persona: dict[str, dict[str, Any]] = {}
    velocity_by_topic: dict[str, dict[str, Any]] = {}
    deficit_trend_delta: list[dict[str, Any]] = []
    tuple_risk_trend: dict[str, Any] = {"transition_counts": {}, "improved_count": 0, "worsened_count": 0}
    risk_transitions: dict[str, list[str]] = defaultdict(list)

    this_persona_stories: dict[str, int] = defaultdict(int)
    this_topic_stories: dict[str, int] = defaultdict(int)
    for t in tuples_payload:
        sc = _story_count_from_tuple(t)
        this_persona_stories[t["persona_id"]] += sc
        this_topic_stories[t["topic_id"]] += sc

    prev_tuples = (prev_report or {}).get("tuples") or []
    prev_risk_by_id: dict[str, str] = {}
    prev_persona_stories: dict[str, int] = defaultdict(int)
    prev_topic_stories: dict[str, int] = defaultdict(int)
    for t in prev_tuples:
        tid = t.get("tuple_id") or ""
        if tid:
            prev_risk_by_id[tid] = t.get("risk") or ""
        sc = _story_count_from_tuple(t)
        pid = t.get("persona_id") or ""
        tid_topic = t.get("topic_id") or ""
        if pid:
            prev_persona_stories[pid] += sc
        if tid_topic:
            prev_topic_stories[tid_topic] += sc

    for persona_id in sorted(set(this_persona_stories) | set(prev_persona_stories)):
        this_c = this_persona_stories.get(persona_id, 0)
        prev_c = prev_persona_stories.get(persona_id, 0)
        velocity_by_persona[persona_id] = {
            "story_count_this_week": this_c,
            "story_count_last_week": prev_c,
            "delta": this_c - prev_c,
        }
    for topic_id in sorted(set(this_topic_stories) | set(prev_topic_stories)):
        this_c = this_topic_stories.get(topic_id, 0)
        prev_c = prev_topic_stories.get(topic_id, 0)
        velocity_by_topic[topic_id] = {
            "story_count_this_week": this_c,
            "story_count_last_week": prev_c,
            "delta": this_c - prev_c,
        }

    prev_summary = (prev_report or {}).get("summary") or {}
    prev_deficit = {x["code"]: x["count"] for x in (prev_summary.get("top_deficit_codes") or [])}
    this_deficit = {x["code"]: x["count"] for x in (summary.get("top_deficit_codes") or [])}
    all_codes = sorted(set(this_deficit) | set(prev_deficit))
    for code in all_codes:
        c_this = this_deficit.get(code, 0)
        c_prev = prev_deficit.get(code, 0)
        deficit_trend_delta.append({"code": code, "count_this_week": c_this, "count_last_week": c_prev, "delta": c_this - c_prev})
    deficit_trend_delta.sort(key=lambda x: -abs(x["delta"]))

    risk_order = ("BLOCKER", "RED", "YELLOW", "GREEN")
    def risk_rank(r: str) -> int:
        return risk_order.index(r) if r in risk_order else 4
    improved = 0
    worsened = 0
    for t in tuples_payload:
        tid = t.get("tuple_id") or ""
        this_risk = t.get("risk") or ""
        prev_risk = prev_risk_by_id.get(tid)
        if prev_risk is None or prev_risk == this_risk:
            continue
        key = f"{prev_risk}_to_{this_risk}"
        tuple_risk_trend["transition_counts"][key] = tuple_risk_trend["transition_counts"].get(key, 0) + 1
        risk_transitions[key].append(tid)
        if risk_rank(this_risk) < risk_rank(prev_risk):
            improved += 1
        else:
            worsened += 1
    tuple_risk_trend["improved_count"] = improved
    tuple_risk_trend["worsened_count"] = worsened

    return velocity_by_persona, velocity_by_topic, deficit_trend_delta, tuple_risk_trend, dict(risk_transitions)


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

    # Velocity and v1.1 deltas: load previous week report
    prev_summary = _load_previous_week_summary(out_dir, date_str)
    prev_report = _load_previous_week_report(out_dir, date_str)
    if prev_summary is not None and summary.get("total_story_atoms") is not None:
        prev_total = prev_summary.get("total_story_atoms")
        if prev_total is not None:
            delta_total = summary["total_story_atoms"] - int(prev_total)
            summary["velocity"]["week_over_week_story_delta_total"] = delta_total

    # JSON (dashboard schema 1.0 → 1.1)
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
    by_persona_risk: dict[str, dict[str, list[str]]] = defaultdict(lambda: {"BLOCKER": [], "RED": [], "YELLOW": [], "GREEN": []})
    by_topic_risk: dict[str, dict[str, list[str]]] = defaultdict(lambda: {"BLOCKER": [], "RED": [], "YELLOW": [], "GREEN": []})
    for t in tuples_payload:
        tid = t["tuple_id"]
        risk = t["risk"]
        by_risk[risk].append(tid)
        by_persona[t["persona_id"]].append(tid)
        by_topic[t["topic_id"]].append(tid)
        by_persona_risk[t["persona_id"]][risk].append(tid)
        by_topic_risk[t["topic_id"]][risk].append(tid)

    # Schema v1.1: velocity by persona/topic, deficit trend, risk trend, median delta
    velocity_by_persona: dict[str, dict] = {}
    velocity_by_topic: dict[str, dict] = {}
    deficit_trend_delta: list[dict] = []
    tuple_risk_trend: dict[str, Any] = {}
    risk_transitions: dict[str, list[str]] = {}
    if prev_report:
        velocity_by_persona, velocity_by_topic, deficit_trend_delta, tuple_risk_trend, risk_transitions = _compute_v11_deltas(
            tuples_payload, summary, prev_report
        )
        summary["velocity_by_persona"] = velocity_by_persona
        summary["velocity_by_topic"] = velocity_by_topic
        summary["deficit_trend_delta"] = deficit_trend_delta
        summary["tuple_risk_trend"] = tuple_risk_trend
        # Per-tuple story delta for median
        prev_tuples = prev_report.get("tuples") or []
        prev_story_by_id = {t.get("tuple_id", ""): _story_count_from_tuple(t) for t in prev_tuples if t.get("tuple_id")}
        deltas = []
        for t in tuples_payload:
            tid = t.get("tuple_id") or ""
            this_c = _story_count_from_tuple(t)
            prev_c = prev_story_by_id.get(tid, 0)
            deltas.append(this_c - prev_c)
        if deltas:
            deltas.sort()
            mid = len(deltas) // 2
            summary["velocity"]["week_over_week_story_delta_median"] = deltas[mid] if len(deltas) % 2 else (deltas[mid - 1] + deltas[mid]) / 2

    indices: dict[str, Any] = {
        "by_risk": dict(by_risk),
        "by_persona": dict(by_persona),
        "by_topic": dict(by_topic),
        "by_persona_risk": {k: dict(v) for k, v in by_persona_risk.items()},
        "by_topic_risk": {k: dict(v) for k, v in by_topic_risk.items()},
    }
    if velocity_by_persona:
        indices["velocity_by_persona"] = velocity_by_persona
    if velocity_by_topic:
        indices["velocity_by_topic"] = velocity_by_topic
    if risk_transitions:
        indices["risk_transitions"] = risk_transitions

    previous_report = _previous_report_meta(out_dir, date_str)
    deltas = _build_deltas(tuples_payload, summary, prev_report) if prev_report else {}
    path_gates = repo_root / "config" / "gates.yaml"
    gates_data = _load_yaml(path_gates) if path_gates.exists() and yaml else {}
    alerts_config = gates_data.get("coverage_health_alerts") or _get_alerts_config()
    alerts = _build_alerts(tuples_payload, summary, prev_report, out_dir, date_str, alerts_config)
    catalog_emotional_config = gates_data.get("catalog_emotional_distribution") or {}
    catalog_emotional_distribution = _compute_catalog_emotional_distribution(
        rows, prev_report, date_str, catalog_emotional_config
    )
    alerts["catalog_emotional"] = _build_catalog_emotional_alerts(catalog_emotional_distribution, gates_data)

    payload = {
        "schema_version": "1.1",
        "generated_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_date": date_str,
        "repo": {
            "root": str(repo_root),
            "git": {"commit": _git_commit(repo_root)},
        },
        "config_snapshot": config_snapshot,
        "previous_report": previous_report,
        "summary": summary,
        "deltas": deltas,
        "alerts": alerts,
        "catalog_emotional_distribution": catalog_emotional_distribution,
        "tuples": tuples_payload,
        "indices": indices,
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
    ])
    # Alerts section (v1.1) + Phase 9 catalog emotional
    stag = (alerts.get("stagnation") or {})
    decay_list = (alerts.get("decay") or {}).get("global") or []
    catalog_emotional_list = alerts.get("catalog_emotional") or []
    if stag.get("by_persona") or stag.get("by_topic") or decay_list or catalog_emotional_list:
        lines.append("## Alerts")
        lines.append("")
        if stag.get("by_persona"):
            lines.append("### Stagnation (by persona)")
            for a in stag["by_persona"]:
                lines.append(f"- **{a.get('persona_id', '')}**: story_delta_total={a.get('story_delta_total')} over {a.get('window_weeks')}w, red_or_blocker_tuples={a.get('red_or_blocker_tuples')}. {a.get('recommendation', '')}")
            lines.append("")
        if stag.get("by_topic"):
            lines.append("### Stagnation (by topic)")
            for a in stag["by_topic"]:
                lines.append(f"- **{a.get('topic_id', '')}**: story_delta_total={a.get('story_delta_total')} over {a.get('window_weeks')}w, red_or_blocker_tuples={a.get('red_or_blocker_tuples')}. {a.get('recommendation', '')}")
            lines.append("")
        if decay_list:
            lines.append("### Decay (global)")
            for a in decay_list:
                code = a.get("code", "")
                rec = a.get("recommendation", "")
                lines.append(f"- **{code}**: {rec}")
            lines.append("")
        if catalog_emotional_list:
            lines.append("### Catalog emotional (Phase 9)")
            for a in catalog_emotional_list:
                code = a.get("code", "")
                rec = a.get("recommendation", "")
                lines.append(f"- **{code}**: {rec}")
            lines.append("")
    lines.extend([
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
