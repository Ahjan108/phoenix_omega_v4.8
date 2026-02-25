"""
Tuple viability preflight gate. Runs BEFORE Stage 1.
Hard entry gate: fail early, fail deterministically. No override.

Tuple = (persona, topic, engine, format). Atomic production unit.

Checks:
  1. Binding exists (topic + engine in config/topic_engine_bindings.yaml)
  2. Arc exists (master_arcs/{persona}__{topic}__{engine}__{format}.yaml)
  3. STORY pool exists (atoms/<persona>/<topic>/<engine>/CANONICAL.txt non-empty)
  4. Minimum STORY depth (len(pool) >= min_story_pool_size)
  5. Required emotional bands present (arc emotional_curve bands covered by pool)
  6. Optional: Teacher Mode exercise pool depth (when teacher_mode=true)

CLI:
  python3 phoenix_v4/gates/check_tuple_viability.py --persona gen_z --topic overthinking --engine E1 --format F006
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_ROOT = REPO_ROOT / "config"
ATOMS_ROOT = REPO_ROOT / "atoms"
ARCS_ROOT = CONFIG_ROOT / "source_of_truth" / "master_arcs"
TEACHER_BANKS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class TupleViabilityResult:
    """Result of tuple viability check."""
    tuple_str: str
    status: str  # "PASS" | "FAIL"
    errors: list[str]


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
    return {
        "min_story_pool_size": int(tvc.get("min_story_pool_size", 12)),
        "min_teacher_exercise_pool": int(tvc.get("min_teacher_exercise_pool", 5)),
    }


def _get_brand_emotional_range(repo_root: Path, brand_id: str) -> tuple[int, int]:
    """Return (min_band, max_band) for brand. Uses default if brand not in config."""
    path = repo_root / "config" / "catalog_planning" / "brand_emotional_range.yaml"
    data = _load_yaml(path)
    default = (data.get("default") or {})
    brands = (data.get("brands") or {})
    entry = brands.get(brand_id) if brand_id else None
    if not entry:
        return (
            int(default.get("min_band", 1)),
            int(default.get("max_band", 5)),
        )
    return (
        int(entry.get("min_band", 1)),
        int(entry.get("max_band", 5)),
    )


def _load_story_atoms_for_engine(
    atoms_root: Path,
    persona: str,
    topic: str,
    engine: str,
) -> list[dict[str, Any]]:
    """Load STORY atoms from atoms/<persona>/<topic>/<engine>/CANONICAL.txt. Returns [] if missing/invalid."""
    from phoenix_v4.planning.assembly_compiler import _parse_canonical_txt
    path = atoms_root / persona / topic / engine / "CANONICAL.txt"
    if not path.exists():
        return []
    try:
        return _parse_canonical_txt(path)
    except (ValueError, OSError):
        return []


def _required_bands_from_arc(arc: Any) -> list[int]:
    """Unique bands (1–5) from arc emotional_curve."""
    if arc is None:
        return []
    if isinstance(arc, dict):
        curve = arc.get("emotional_curve") or []
    else:
        curve = getattr(arc, "emotional_curve", [])
    out: list[int] = []
    for b in curve:
        try:
            v = int(b)
            if 1 <= v <= 5 and v not in out:
                out.append(v)
        except (TypeError, ValueError):
            continue
    return sorted(out)


def _count_teacher_exercises(teacher_id: str) -> int:
    """Count approved EXERCISE atoms for teacher."""
    ex_dir = TEACHER_BANKS_ROOT / teacher_id / "approved_atoms" / "EXERCISE"
    if not ex_dir.is_dir():
        return 0
    return sum(1 for _ in ex_dir.glob("*.yaml"))


def check_tuple_viability(
    persona: str,
    topic: str,
    engine: str,
    format_id: str,
    *,
    repo_root: Optional[Path] = None,
    teacher_mode: bool = False,
    teacher_id: Optional[str] = None,
    arc: Any = None,
    brand_id: Optional[str] = None,
) -> TupleViabilityResult:
    """
    Run all tuple viability checks. Returns result with status PASS or FAIL and list of errors.
    If arc is not provided, arc file is loaded to derive required_bands (and arc existence is still checked).
    """
    root = repo_root or REPO_ROOT
    config_root = root / "config"
    atoms_root = root / "atoms"
    arcs_root = config_root / "source_of_truth" / "master_arcs"
    bindings_path = config_root / "topic_engine_bindings.yaml"
    tuple_str = f"{persona},{topic},{engine},{format_id}"
    errors: list[str] = []

    # 1) Binding exists
    bindings = _load_yaml(bindings_path)
    bkey = _bindings_topic_key(topic)
    topic_config = bindings.get(bkey)
    if not topic_config:
        errors.append(f"NO_BINDING: persona={persona} topic={topic} engine={engine}")
    else:
        allowed = topic_config.get("allowed_engines") or []
        if engine not in allowed:
            errors.append(f"NO_BINDING: persona={persona} topic={topic} engine={engine}")

    # 2) Arc exists
    arc_path = arcs_root / f"{persona}__{topic}__{engine}__{format_id}.yaml"
    if not arc_path.exists():
        errors.append("NO_ARC: tuple has no arc file")
    elif arc is None and yaml:
        arc = _load_yaml(arc_path)

    # 3) STORY pool exists (and 4) min depth, 5) bands)
    story_atoms = _load_story_atoms_for_engine(atoms_root, persona, topic, engine)
    if not story_atoms:
        errors.append("NO_STORY_POOL")
    else:
        cfg = _get_gate_config()
        min_depth = cfg["min_story_pool_size"]
        if len(story_atoms) < min_depth:
            errors.append(f"POOL_TOO_SHALLOW: {len(story_atoms)} < {min_depth}")
        required_bands = _required_bands_from_arc(arc) if arc else []
        bands_in_pool = {a.get("band", 3) for a in story_atoms}
        for b in required_bands:
            if b not in bands_in_pool:
                errors.append(f"BAND_DEFICIT: missing band {b}")

    # 6) Teacher Mode: exercise pool depth
    if teacher_mode and teacher_id:
        cfg = _get_gate_config()
        min_ex = cfg["min_teacher_exercise_pool"]
        count = _count_teacher_exercises(teacher_id)
        if count < min_ex:
            errors.append(f"TEACHER_EXERCISE_DEFICIT: approved_exercises={count} < {min_ex}")

    # 7) Brand emotional range (Phase 5): arc required bands must be within brand [min_band, max_band]
    if brand_id and arc:
        required_bands = _required_bands_from_arc(arc)
        if required_bands:
            min_band, max_band = _get_brand_emotional_range(root, brand_id)
            out_of_range = [b for b in required_bands if b < min_band or b > max_band]
            if out_of_range:
                errors.append(
                    f"ARC_OUTSIDE_BRAND_EMOTIONAL_RANGE: brand={brand_id} range=[{min_band},{max_band}] "
                    f"arc requires bands {out_of_range}"
                )

    status = "PASS" if not errors else "FAIL"
    return TupleViabilityResult(tuple_str=tuple_str, status=status, errors=errors)


def main() -> int:
    ap = argparse.ArgumentParser(description="Tuple viability preflight gate")
    ap.add_argument("--persona", required=True, help="Persona ID (e.g. gen_z)")
    ap.add_argument("--topic", required=True, help="Topic ID (e.g. overthinking)")
    ap.add_argument("--engine", required=True, help="Engine ID (e.g. E1 or false_alarm)")
    ap.add_argument("--format", required=True, dest="format_id", help="Format ID (e.g. F006)")
    ap.add_argument("--teacher-mode", action="store_true", help="Enable teacher exercise pool check")
    ap.add_argument("--teacher", default=None, help="Teacher ID (required if --teacher-mode)")
    ap.add_argument("--brand", default=None, dest="brand_id", help="Brand ID for emotional range check (Phase 5)")
    ap.add_argument("--repo", type=Path, default=None, help="Repo root (default: auto)")
    ap.add_argument("--json", action="store_true", help="Output JSON on fail")
    args = ap.parse_args()

    teacher_id = (args.teacher or "").strip() or None
    if args.teacher_mode and not teacher_id:
        print("Error: --teacher required when --teacher-mode", file=sys.stderr)
        return 1

    brand_id = (args.brand_id or "").strip() or None

    result = check_tuple_viability(
        persona=args.persona,
        topic=args.topic,
        engine=args.engine,
        format_id=args.format_id,
        repo_root=args.repo,
        teacher_mode=args.teacher_mode,
        teacher_id=teacher_id,
        brand_id=brand_id,
    )

    if result.status == "PASS":
        print("TUPLE_VIABLE")
        return 0
    if args.json:
        out = {
            "tuple": result.tuple_str,
            "status": result.status,
            "errors": result.errors,
        }
        print(json.dumps(out, indent=2))
    else:
        for e in result.errors:
            print(e, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
