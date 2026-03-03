"""
Sim test: assert 100% atom coverage for all books (all personas × all topics × allowed engines).

STORY: For every (persona, topic, engine) we require
  atoms/{persona}/{topic}/{engine}/CANONICAL.txt exists and is non-empty (STORY pool).

Non-STORY: For every (persona, topic) we require non-empty canonical pools for:
  HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION at atoms/{persona}/{topic}/{slot_type}/CANONICAL.txt.

Authority: docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md, docs/UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md.
Run: pytest tests/test_atoms_coverage_100_percent.py -v
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

REPO_ROOT = Path(__file__).resolve().parent.parent
# Ensure repo root on path so phoenix_v4 can be imported when run as script or from another cwd
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
CONFIG_ROOT = REPO_ROOT / "config"
_raw = os.environ.get("ATOMS_ROOT")
ATOMS_ROOT = Path(_raw) if _raw else (REPO_ROOT / "atoms")

# Non-STORY slot types required for every (persona, topic). Same rigor as STORY: file exists, ≥1 block.
NON_STORY_SLOT_TYPES = ("HOOK", "SCENE", "REFLECTION", "EXERCISE", "INTEGRATION")


def _load_yaml(p: Path) -> dict:
    try:
        import yaml
    except ImportError:
        return {}
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _catalog_personas(config_root: Path) -> list[str]:
    path = config_root / "catalog_planning" / "canonical_personas.yaml"
    data = _load_yaml(path)
    personas = data.get("personas") or []
    return [str(p) for p in personas if p]


def _catalog_topics_and_engines(config_root: Path) -> list[tuple[str, list[str]]]:
    """(topic_id, [engine_id, ...]) for each topic that has allowed_engines in bindings."""
    path = config_root / "topic_engine_bindings.yaml"
    bindings = _load_yaml(path)
    out: list[tuple[str, list[str]]] = []
    for k, v in bindings.items():
        if k in ("---", "notes") or not isinstance(v, dict):
            continue
        allowed = v.get("allowed_engines") or v.get("engines")
        if allowed:
            out.append((k, [str(e) for e in allowed]))
    return out


def _required_tuples(config_root: Path) -> list[tuple[str, str, str]]:
    """All (persona, topic, engine) required to make all books for all personas and topics."""
    personas = _catalog_personas(config_root)
    topic_engines = _catalog_topics_and_engines(config_root)
    out: list[tuple[str, str, str]] = []
    for persona in personas:
        for topic, engines in topic_engines:
            for engine in engines:
                out.append((persona, topic, engine))
    return sorted(out)


def _required_persona_topic_pairs(config_root: Path) -> list[tuple[str, str]]:
    """All (persona, topic) required for non-STORY coverage (same catalog as STORY)."""
    personas = _catalog_personas(config_root)
    topic_engines = _catalog_topics_and_engines(config_root)
    out: list[tuple[str, str]] = []
    for persona in personas:
        for topic, _ in topic_engines:
            out.append((persona, topic))
    return sorted(out)


# Block format for non-STORY CANONICAL.txt (must match pool_index._parse_block_file_canonical).
_NON_STORY_BLOCK_RE = re.compile(
    r"^##\s+(\S+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---",
    re.MULTILINE,
)


def _has_non_story_pool(
    atoms_root: Path, persona: str, topic: str, slot_type: str
) -> tuple[bool, int]:
    """True if atoms/{persona}/{topic}/{slot_type}/CANONICAL.txt exists and has ≥1 block. Returns (ok, count)."""
    path = atoms_root / persona / topic / slot_type / "CANONICAL.txt"
    if not path.exists():
        return False, 0
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False, 0
    count = len(_NON_STORY_BLOCK_RE.findall(text))
    return count > 0, count


def _has_story_pool(atoms_root: Path, persona: str, topic: str, engine: str) -> tuple[bool, int]:
    """True if atoms/{persona}/{topic}/{engine}/CANONICAL.txt exists and has at least one atom. Returns (ok, count)."""
    path = atoms_root / persona / topic / engine / "CANONICAL.txt"
    if not path.exists():
        return False, 0
    try:
        from phoenix_v4.planning.assembly_compiler import _parse_canonical_txt
        atoms = _parse_canonical_txt(path)
        return len(atoms) > 0, len(atoms)
    except Exception as e:
        # Validation or parse error; treat as missing for coverage
        return False, 0


@pytest.mark.slow
def test_100_percent_atoms_for_all_books():
    """
    Sim test: every (persona, topic, engine) in the catalog has a non-empty STORY pool
    so that all books for all personas + all topics can be built.
    """
    if not CONFIG_ROOT.exists():
        pytest.skip("config/ not found (not in repo root)")  # type: ignore[union-attr]
    if not ATOMS_ROOT.exists():
        pytest.skip("atoms/ not found")  # type: ignore[union-attr]

    required = _required_tuples(CONFIG_ROOT)
    assert required, "Catalog has no (persona, topic, engine) tuples"

    missing: list[tuple[str, str, str]] = []
    shallow: list[tuple[str, str, str, int]] = []  # (p, t, e, count) for count < min_depth
    min_depth = 12
    try:
        gates = _load_yaml(REPO_ROOT / "config" / "gates.yaml")
        min_depth = int((gates.get("tuple_viability") or {}).get("min_story_pool_size", 12))
    except Exception:
        pass

    for persona, topic, engine in required:
        ok, count = _has_story_pool(ATOMS_ROOT, persona, topic, engine)
        if not ok:
            missing.append((persona, topic, engine))
        elif count < min_depth:
            shallow.append((persona, topic, engine, count))

    total = len(required)
    covered = total - len(missing)
    pct = 100.0 * covered / total if total else 0.0

    # Fail if any tuple has no STORY pool
    assert not missing, (
        f"Atom coverage {pct:.1f}% ({covered}/{total}). Missing STORY pool for {len(missing)} tuples:\n"
        + "\n".join(f"  atoms/{p}/{t}/{e}/CANONICAL.txt" for p, t, e in missing[:50])
        + (f"\n  ... and {len(missing) - 50} more" if len(missing) > 50 else "")
    )

    # Optional: log shallow pools (POOL_TOO_SHALLOW = RED in coverage report, not BLOCKER)
    if shallow:
        shallow_msg = "; ".join(f"{p}/{t}/{e}(n={n})" for p, t, e, n in shallow[:10])
        if len(shallow) > 10:
            shallow_msg += f" ... and {len(shallow) - 10} more"
        print(f"\nShallow pools (below min_story_pool_size={min_depth}): {len(shallow)}. Examples: {shallow_msg}")


@pytest.mark.slow
def test_100_percent_non_story_atoms_for_all_books():
    """
    Every (persona, topic) has non-empty HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION pools
    so that all books can be built without relying on fallbacks. Same rigor as STORY: fail on any gap.
    """
    if not CONFIG_ROOT.exists():
        pytest.skip("config/ not found (not in repo root)")  # type: ignore[union-attr]
    if not ATOMS_ROOT.exists():
        pytest.skip("atoms/ not found")  # type: ignore[union-attr]

    pairs = _required_persona_topic_pairs(CONFIG_ROOT)
    assert pairs, "Catalog has no (persona, topic) pairs"

    # missing[slot_type] = list of (persona, topic)
    missing: dict[str, list[tuple[str, str]]] = {st: [] for st in NON_STORY_SLOT_TYPES}

    for persona, topic in pairs:
        for slot_type in NON_STORY_SLOT_TYPES:
            ok, _ = _has_non_story_pool(ATOMS_ROOT, persona, topic, slot_type)
            if not ok:
                missing[slot_type].append((persona, topic))

    total_pairs = len(pairs)
    required_per_slot = total_pairs * len(NON_STORY_SLOT_TYPES)
    missing_total = sum(len(m) for m in missing.values())

    if missing_total > 0:
        lines = []
        for st in NON_STORY_SLOT_TYPES:
            m = missing[st]
            if not m:
                continue
            examples = ", ".join(f"atoms/{p}/{t}/{st}/CANONICAL.txt" for p, t in m[:3])
            suffix = f" ... and {len(m) - 3} more" if len(m) > 3 else ""
            lines.append(f"  {st}: {len(m)} missing — {examples}{suffix}")
        raise AssertionError(
            "Non-STORY coverage not 100%: missing canonical pools for "
            f"{missing_total} (persona, topic, slot_type) combinations.\n" + "\n".join(lines)
        )


@pytest.mark.slow
def test_non_story_coverage_summary():
    """Print non-STORY coverage summary (always runs; does not fail). Useful for CI logs."""
    if not CONFIG_ROOT.exists() or not ATOMS_ROOT.exists():
        pytest.skip("config/ or atoms/ not found")  # type: ignore[union-attr]

    pairs = _required_persona_topic_pairs(CONFIG_ROOT)
    missing: dict[str, list[tuple[str, str]]] = {st: [] for st in NON_STORY_SLOT_TYPES}
    for persona, topic in pairs:
        for slot_type in NON_STORY_SLOT_TYPES:
            ok, _ = _has_non_story_pool(ATOMS_ROOT, persona, topic, slot_type)
            if not ok:
                missing[slot_type].append((persona, topic))

    total = len(pairs) * len(NON_STORY_SLOT_TYPES)
    covered = total - sum(len(m) for m in missing.values())
    pct = 100.0 * covered / total if total else 0.0
    print(f"\nNon-STORY coverage: {pct:.1f}% ({covered}/{total}) persona×topic×slot_type have canonical pool.")
    for st in NON_STORY_SLOT_TYPES:
        m = missing[st]
        if m:
            print(f"  {st}: {len(m)} missing (first 5): {[f'{p}/{t}' for p, t in m[:5]]}")


@pytest.mark.slow
def test_atoms_coverage_summary():
    """Print coverage summary (always runs; does not fail). Useful for CI logs."""
    if not CONFIG_ROOT.exists() or not ATOMS_ROOT.exists():
        pytest.skip("config/ or atoms/ not found")  # type: ignore[union-attr]

    required = _required_tuples(CONFIG_ROOT)
    missing = []
    for persona, topic, engine in required:
        ok, _ = _has_story_pool(ATOMS_ROOT, persona, topic, engine)
        if not ok:
            missing.append((persona, topic, engine))

    total = len(required)
    covered = total - len(missing)
    pct = 100.0 * covered / total if total else 0.0
    print(f"\nAtoms coverage: {pct:.1f}% ({covered}/{total}) personas×topics×engines have STORY pool.")
    if missing:
        print(f"Missing: {len(missing)} tuples (first 20):")
        for p, t, e in missing[:20]:
            print(f"  atoms/{p}/{t}/{e}/CANONICAL.txt")


def run_sim_test() -> tuple[bool, str]:
    """
    Run the STORY sim test programmatically. Returns (passed, message).
    """
    if not CONFIG_ROOT.exists():
        return False, "config/ not found (run from repo root)"
    if not ATOMS_ROOT.exists():
        return False, "atoms/ not found"

    required = _required_tuples(CONFIG_ROOT)
    if not required:
        return False, "Catalog has no (persona, topic, engine) tuples"

    missing: list[tuple[str, str, str]] = []
    shallow: list[tuple[str, str, str, int]] = []
    min_depth = 12
    try:
        gates = _load_yaml(REPO_ROOT / "config" / "gates.yaml")
        min_depth = int((gates.get("tuple_viability") or {}).get("min_story_pool_size", 12))
    except Exception:
        pass

    for persona, topic, engine in required:
        ok, count = _has_story_pool(ATOMS_ROOT, persona, topic, engine)
        if not ok:
            missing.append((persona, topic, engine))
        elif count < min_depth:
            shallow.append((persona, topic, engine, count))

    total = len(required)
    covered = total - len(missing)
    pct = 100.0 * covered / total if total else 0.0

    if missing:
        lines = [f"STORY coverage {pct:.1f}% ({covered}/{total}). Missing STORY pool for {len(missing)} tuples:"]
        for p, t, e in missing[:50]:
            lines.append(f"  atoms/{p}/{t}/{e}/CANONICAL.txt")
        if len(missing) > 50:
            lines.append(f"  ... and {len(missing) - 50} more")
        return False, "\n".join(lines)

    msg = f"100% STORY coverage: {total} tuples (personas × topics × engines) have non-empty STORY pool."
    if shallow:
        msg += f" {len(shallow)} pools below min_story_pool_size={min_depth} (RED in coverage report)."
    return True, msg


def run_non_story_sim_test() -> tuple[bool, str]:
    """
    Run the non-STORY coverage test programmatically. Returns (passed, message).
    Requires every (persona, topic) to have non-empty HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION.
    """
    if not CONFIG_ROOT.exists():
        return False, "config/ not found (run from repo root)"
    if not ATOMS_ROOT.exists():
        return False, "atoms/ not found"

    pairs = _required_persona_topic_pairs(CONFIG_ROOT)
    if not pairs:
        return False, "Catalog has no (persona, topic) pairs"

    missing: dict[str, list[tuple[str, str]]] = {st: [] for st in NON_STORY_SLOT_TYPES}
    for persona, topic in pairs:
        for slot_type in NON_STORY_SLOT_TYPES:
            ok, _ = _has_non_story_pool(ATOMS_ROOT, persona, topic, slot_type)
            if not ok:
                missing[slot_type].append((persona, topic))

    missing_total = sum(len(m) for m in missing.values())
    total = len(pairs) * len(NON_STORY_SLOT_TYPES)
    covered = total - missing_total
    pct = 100.0 * covered / total if total else 0.0

    if missing_total > 0:
        lines = [f"Non-STORY coverage {pct:.1f}% ({covered}/{total}). Missing canonical pools:"]
        for st in NON_STORY_SLOT_TYPES:
            m = missing[st]
            if m:
                examples = ", ".join(f"atoms/{p}/{t}/{st}/CANONICAL.txt" for p, t in m[:3])
                suffix = f" ... and {len(m) - 3} more" if len(m) > 3 else ""
                lines.append(f"  {st}: {len(m)} — {examples}{suffix}")
        return False, "\n".join(lines)

    return True, (
        f"100% non-STORY coverage: all {len(pairs)} (persona, topic) pairs have non-empty "
        f"HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION pools."
    )


if __name__ == "__main__":
    story_ok, story_msg = run_sim_test()
    non_story_ok, non_story_msg = run_non_story_sim_test()
    print(story_msg)
    print(non_story_msg)
    if not story_ok:
        sys.exit(1)
    if not non_story_ok:
        sys.exit(1)
    sys.exit(0)
