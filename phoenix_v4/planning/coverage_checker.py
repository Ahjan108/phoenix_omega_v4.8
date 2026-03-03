"""
Coverage checker for CI: K-table and persona×topic×role coverage.
Runs capability_check over in-scope (persona, topic) × format and fails when under thresholds.
Authority: PLANNING_STATUS.md, SYSTEMS_V4.md — wire a single coverage check in CI.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"
CONFIG_FORMAT = REPO_ROOT / "config" / "format_selection"


def _discover_persona_topic_pairs(atoms_root: Path) -> list[tuple[str, str]]:
    """Discover (persona_id, topic_id) from atoms layout. Persona = dir under atoms/; topic = dir under persona/ with content."""
    pairs: list[tuple[str, str]] = []
    if not atoms_root.exists():
        return pairs
    for persona_dir in sorted(atoms_root.iterdir()):
        if not persona_dir.is_dir() or persona_dir.name.startswith("."):
            continue
        persona_id = persona_dir.name
        for topic_dir in sorted(persona_dir.iterdir()):
            if not topic_dir.is_dir() or topic_dir.name.startswith("."):
                continue
            topic_id = topic_dir.name
            if not list(topic_dir.rglob("CANONICAL.txt")):
                continue
            if True:
                pairs.append((persona_id, topic_id))
    return sorted(set(pairs))


def _default_format_plan(format_structural_id: str = "F006", chapter_count: int = 12) -> dict:
    """Build minimal format_plan for capability_check."""
    try:
        import yaml
        reg_path = CONFIG_FORMAT / "format_registry.yaml"
        if reg_path.exists():
            reg = yaml.safe_load(reg_path.read_text()) or {}
            struct = (reg.get("structural_formats") or {}).get(format_structural_id, {})
            ch_range = struct.get("chapter_range") or [8, 12]
            chapter_count = min(max(chapter_count, ch_range[0]), ch_range[1])
    except Exception:
        pass
    slot_def = [["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]] * chapter_count
    return {
        "format_structural_id": format_structural_id,
        "format_id": format_structural_id,
        "chapter_count": chapter_count,
        "slot_definitions": slot_def,
    }


def run_coverage_check(
    atoms_root: Path | None = None,
    format_structural_id: str = "F006",
    mode: str = "strict",
) -> tuple[bool, list[str]]:
    """
    Run capability_check over all discovered (persona, topic). Returns (all_passed, list of error messages).
    """
    atoms_root = atoms_root or ATOMS_ROOT
    from phoenix_v4.planning.pool_index import PoolIndex
    from phoenix_v4.planning.capability_check import capability_check

    pairs = _discover_persona_topic_pairs(atoms_root)
    if not pairs:
        return True, []  # No atoms layout: nothing to check

    pool_index = PoolIndex()
    format_plan = _default_format_plan(format_structural_id)
    errors: list[str] = []
    for persona_id, topic_id in pairs:
        book_spec = {"persona_id": persona_id, "topic_id": topic_id}
        result = capability_check(book_spec, format_plan, pool_index, mode=mode)
        if not result.ok:
            for e in result.errors:
                errors.append(f"[{persona_id}/{topic_id}] {e}")
    return len(errors) == 0, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Coverage check: K-table and persona×topic×role (CI)")
    ap.add_argument("--atoms", default=None, help="Atoms root (default: repo/atoms)")
    ap.add_argument("--format", default="F006", help="Structural format id for K-table")
    ap.add_argument("--relaxed", action="store_true", help="Relaxed mode: warn, do not fail on missing K-table")
    args = ap.parse_args()
    atoms_root = Path(args.atoms) if args.atoms else ATOMS_ROOT
    mode = "relaxed" if args.relaxed else "strict"
    passed, errors = run_coverage_check(atoms_root=atoms_root, format_structural_id=args.format, mode=mode)
    if not passed:
        for e in errors:
            print(e, file=sys.stderr)
        print("COVERAGE CHECK: FAIL", file=sys.stderr)
        return 1
    print("COVERAGE CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
