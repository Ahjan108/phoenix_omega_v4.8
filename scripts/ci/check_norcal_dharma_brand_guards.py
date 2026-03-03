#!/usr/bin/env python3
"""
CI guards for NorCal Dharma brand (brand-only, not teacher).
- Guard 1: norcal_dharma must NEVER appear in any brand_teacher_matrix_*.yaml.
- Guard 2: In brand_teacher_assignments.yaml, every row with brand_id norcal_dharma must have teacher_id default_teacher.
Exit 0 if both pass, 1 otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_CATALOG = REPO_ROOT / "config" / "catalog_planning"
ASSIGNMENTS_PATH = CONFIG_CATALOG / "brand_teacher_assignments.yaml"
BRAND_ONLY_ID = "norcal_dharma"
REQUIRED_TEACHER_ID = "default_teacher"


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def _collect_brand_ids_from_matrix(data: dict) -> set[str]:
    """Collect all brand IDs from a matrix file (brands: or matrix: top-level)."""
    ids = set()
    brands = data.get("brands") or data.get("matrix")
    if isinstance(brands, dict):
        ids.update(brands.keys())
    return ids


def check_not_in_matrices() -> tuple[bool, str]:
    """Guard 1: norcal_dharma must not appear in any brand_teacher_matrix_*.yaml."""
    matrix_files = list(CONFIG_CATALOG.glob("brand_teacher_matrix_*.yaml"))
    # Also check the default matrix (no suffix) if it exists
    default_matrix = CONFIG_CATALOG / "brand_teacher_matrix.yaml"
    if default_matrix.exists() and default_matrix not in matrix_files:
        matrix_files.append(default_matrix)
    for path in sorted(matrix_files):
        data = _load_yaml(path)
        brand_ids = _collect_brand_ids_from_matrix(data)
        if BRAND_ONLY_ID in brand_ids:
            return False, f"norcal_dharma must not appear in any brand_teacher_matrix. Found in: {path}"
    return True, "norcal_dharma not in any brand_teacher_matrix (OK)"


def check_assignments_default_teacher_only() -> tuple[bool, str]:
    """Guard 2: Every assignment with brand_id norcal_dharma must have teacher_id default_teacher."""
    data = _load_yaml(ASSIGNMENTS_PATH)
    assignments = data.get("assignments") or []
    for i, row in enumerate(assignments):
        if (row.get("brand_id") or "").strip() != BRAND_ONLY_ID:
            continue
        teacher_id = (row.get("teacher_id") or "").strip()
        if teacher_id != REQUIRED_TEACHER_ID:
            return False, (
                f"brand_teacher_assignments: norcal_dharma must map only to default_teacher. "
                f"Row index {i} has teacher_id={teacher_id!r}."
            )
    return True, "norcal_dharma assignments map only to default_teacher (OK)"


def main() -> int:
    ok1, msg1 = check_not_in_matrices()
    print(msg1)
    if not ok1:
        return 1
    ok2, msg2 = check_assignments_default_teacher_only()
    print(msg2)
    if not ok2:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
