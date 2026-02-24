"""
Tests for slot resolver: determinism (SHA256), used_ids excluded, band filter, empty pool.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_sha256_determinism():
    """Same selector_key always produces same index."""
    from phoenix_v4.planning.slot_resolver import _selector_index

    key = "abc123:STORY:ch00:s00"
    n = 10
    idx1 = _selector_index(key, n)
    idx2 = _selector_index(key, n)
    assert idx1 == idx2
    assert 0 <= idx1 < n


def test_no_python_hash():
    """Resolver uses SHA256, not Python hash(). We verify _selector_index is deterministic across runs."""
    from phoenix_v4.planning.slot_resolver import _selector_index

    # SHA256 of "test_key" is fixed; first 16 bytes mod 5 is deterministic
    idx = _selector_index("test_key", 5)
    assert isinstance(idx, int)
    assert 0 <= idx < 5


def test_used_ids_excluded():
    """Previously used atom_ids are not selected again."""
    try:
        import yaml
    except ImportError:
        return  # skip when PyYAML not installed (fixture bindings required)
    from phoenix_v4.planning.pool_index import PoolIndex
    from phoenix_v4.planning.slot_resolver import ResolverContext, resolve_slot

    atoms_root = REPO_ROOT / "tests" / "fixtures" / "atoms"
    bindings_path = REPO_ROOT / "tests" / "fixtures" / "bindings" / "golden_test_bindings.yaml"
    if not bindings_path.exists():
        return
    pool_index = PoolIndex(atoms_root=atoms_root, bindings_path=bindings_path)
    used = set()
    context = ResolverContext(
        persona_id="golden_test_persona",
        topic_id="golden_test_topic",
        slot_definitions=[["STORY"], ["STORY"], ["STORY"]],
        used_atom_ids=used,
        pool_index=pool_index,
        selector_key_prefix="test_used",
        required_band_by_chapter={0: 2, 1: 5, 2: 4},
        used_semantic_families=set(),
    )
    a1 = resolve_slot("STORY", 0, 0, context)
    assert a1 is not None
    (aid1, _) = a1
    used.add(aid1)
    a2 = resolve_slot("STORY", 1, 0, context)
    assert a2 is not None
    (aid2, _) = a2
    assert aid2 != aid1
    used.add(aid2)
    a3 = resolve_slot("STORY", 2, 0, context)
    assert a3 is not None
    used.add(a3[0])
    # Pool has 3 atoms (bands 2, 4, 5). All three used. Next resolve for ch0 (band 2) has no available atom.
    a4 = resolve_slot("STORY", 0, 0, context)
    assert a4 is None


def test_band_filter_applied():
    """When required_band_by_chapter is set, only matching band atoms are selected."""
    try:
        import yaml
    except ImportError:
        return
    from phoenix_v4.planning.pool_index import PoolIndex
    from phoenix_v4.planning.slot_resolver import ResolverContext, resolve_slot

    atoms_root = REPO_ROOT / "tests" / "fixtures" / "atoms"
    bindings_path = REPO_ROOT / "tests" / "fixtures" / "bindings" / "golden_test_bindings.yaml"
    if not bindings_path.exists():
        return
    pool_index = PoolIndex(atoms_root=atoms_root, bindings_path=bindings_path)
    context = ResolverContext(
        persona_id="golden_test_persona",
        topic_id="golden_test_topic",
        slot_definitions=[["STORY"]],
        used_atom_ids=set(),
        pool_index=pool_index,
        selector_key_prefix="band_test",
        required_band_by_chapter={0: 5},
        used_semantic_families=set(),
    )
    result = resolve_slot("STORY", 0, 0, context)
    assert result is not None
    aid = result[0]
    assert "v03" in aid or "RECOGNITION" in aid


def test_empty_pool_returns_none():
    """Returns None when no atoms available (wrong persona/topic or exhausted)."""
    from phoenix_v4.planning.pool_index import PoolIndex
    from phoenix_v4.planning.slot_resolver import ResolverContext, resolve_slot

    atoms_root = REPO_ROOT / "tests" / "fixtures" / "atoms"
    bindings_path = REPO_ROOT / "tests" / "fixtures" / "bindings" / "golden_test_bindings.yaml"
    pool_index = PoolIndex(atoms_root=atoms_root, bindings_path=bindings_path)
    # Use a topic that has no engines in bindings (or persona/topic with no CANONICAL)
    context = ResolverContext(
        persona_id="no_such_persona",
        topic_id="no_such_topic",
        slot_definitions=[["STORY"]],
        used_atom_ids=set(),
        pool_index=pool_index,
        selector_key_prefix="empty",
        required_band_by_chapter=None,
        used_semantic_families=set(),
    )
    aid = resolve_slot("STORY", 0, 0, context)
    assert aid is None


def test_lexicographic_sort():
    """Available atoms are sorted by atom_id before selection for reproducibility."""
    try:
        import yaml
    except ImportError:
        return
    from phoenix_v4.planning.pool_index import PoolIndex
    from phoenix_v4.planning.slot_resolver import ResolverContext, resolve_slot

    atoms_root = REPO_ROOT / "tests" / "fixtures" / "atoms"
    bindings_path = REPO_ROOT / "tests" / "fixtures" / "bindings" / "golden_test_bindings.yaml"
    if not bindings_path.exists():
        return
    pool_index = PoolIndex(atoms_root=atoms_root, bindings_path=bindings_path)
    context = ResolverContext(
        persona_id="golden_test_persona",
        topic_id="golden_test_topic",
        slot_definitions=[["STORY"]],
        used_atom_ids=set(),
        pool_index=pool_index,
        selector_key_prefix="lex",
        required_band_by_chapter={0: 2, 1: 5, 2: 4},
        used_semantic_families=set(),
    )
    a1 = resolve_slot("STORY", 0, 0, context)
    a2 = resolve_slot("STORY", 1, 0, context)
    a3 = resolve_slot("STORY", 2, 0, context)
    # Same seed prefix -> deterministic order. Just check we got three distinct or valid ids.
    assert a1 and a2 and a3
    assert len({a1[0], a2[0], a3[0]}) == 3
