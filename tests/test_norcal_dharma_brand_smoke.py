"""
Runtime smoke tests for NorCal Dharma brand (brand-only, not teacher).
- Wave allocation must never include norcal_dharma.
- Explicit --brand norcal_dharma must resolve to default_teacher and not enter Teacher Mode.
"""
from __future__ import annotations

import pytest

BRAND_ONLY_ID = "norcal_dharma"
REQUIRED_TEACHER_ID = "default_teacher"


def test_wave_allocation_does_not_allocate_norcal_dharma():
    """generate_full_catalog wave mode must not allocate norcal_dharma (not in brand_teacher_matrix)."""
    from pathlib import Path
    from phoenix_v4.planning.teacher_portfolio_planner import allocate_wave, load_brand_matrix

    repo_root = Path(__file__).resolve().parent.parent
    matrix_path = repo_root / "config" / "catalog_planning" / "brand_teacher_matrix.yaml"
    matrix = load_brand_matrix(matrix_path)
    brands = matrix.get("brands") or {}
    teachers = []
    for b in brands.values():
        teachers.extend(b.get("teachers") or [])
    teachers = list(dict.fromkeys(teachers))

    assert teachers, "Matrix must define at least one teacher for allocation"
    allocations = allocate_wave(
        wave_id="smoke",
        teachers=teachers,
        total_books=30,
        brand_matrix_path=matrix_path,
    )
    norcal_allocations = [a for a in allocations if a.brand_id == BRAND_ONLY_ID]
    assert not norcal_allocations, (
        f"norcal_dharma must not be allocated in wave (brand-only, not in matrix). "
        f"Got {len(norcal_allocations)} allocations."
    )


def test_brand_norcal_dharma_resolves_to_default_teacher():
    """Explicit brand_id norcal_dharma must resolve to teacher_id default_teacher."""
    from phoenix_v4.planning.teacher_brand_resolver import resolve_teacher_brand

    teacher_id, brand_id = resolve_teacher_brand(brand_id=BRAND_ONLY_ID)
    assert teacher_id == REQUIRED_TEACHER_ID, (
        f"norcal_dharma must map to default_teacher, got teacher_id={teacher_id!r}"
    )
    assert brand_id == BRAND_ONLY_ID


def test_brand_norcal_dharma_implies_non_teacher_mode():
    """When brand is norcal_dharma, teacher_mode is False (default_teacher)."""
    from phoenix_v4.planning.teacher_brand_resolver import resolve_teacher_brand

    teacher_id, _ = resolve_teacher_brand(brand_id=BRAND_ONLY_ID)
    teacher_mode = teacher_id and teacher_id != "default_teacher"
    assert not teacher_mode, "norcal_dharma must not enter Teacher Mode (teacher_id is default_teacher)"
