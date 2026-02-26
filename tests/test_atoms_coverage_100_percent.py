"""
Sim test: assert 100% atom coverage for all books (all personas × all topics × allowed engines).

For every (persona, topic, engine) in the catalog universe we require:
  atoms/{persona}/{topic}/{engine}/CANONICAL.txt exists and is non-empty (STORY pool).

Authority: docs/TUPLE_VIABILITY_AND_COVERAGE_HEALTH_SPEC.md, docs/UNIFIED_PERSONAS_BOOK_READINESS_ANALYSIS.md.
Run: pytest tests/test_atoms_coverage_100_percent.py -v
"""
from __future__ import annotations

import os
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
ATOMS_ROOT = REPO_ROOT / "atoms"


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
    Run the sim test programmatically. Returns (passed, message).
    Use from pytest or from CLI: python3 tests/test_atoms_coverage_100_percent.py
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
        lines = [f"Atom coverage {pct:.1f}% ({covered}/{total}). Missing STORY pool for {len(missing)} tuples:"]
        for p, t, e in missing[:50]:
            lines.append(f"  atoms/{p}/{t}/{e}/CANONICAL.txt")
        if len(missing) > 50:
            lines.append(f"  ... and {len(missing) - 50} more")
        return False, "\n".join(lines)

    msg = f"100% atoms coverage: {total} tuples (personas × topics × engines) have non-empty STORY pool."
    if shallow:
        msg += f" {len(shallow)} pools below min_story_pool_size={min_depth} (RED in coverage report)."
    return True, msg


if __name__ == "__main__":
    passed, message = run_sim_test()
    print(message)
    sys.exit(0 if passed else 1)
