"""
K-table pool depth validation. Dev Spec §4.2.3.
Before compilation, check that the atom pool for the target persona×topic meets the K-table minimums for the selected format.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from phoenix_v4.qa.validate_compiled_plan import ValidationResult

if TYPE_CHECKING:
    from phoenix_v4.planning.pool_index import PoolIndex

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_K_TABLES_DIR = REPO_ROOT / "config" / "format_selection" / "k_tables"


def _load_k_table(format_id: str, k_tables_dir: Path) -> dict[str, Any] | None:
    path = k_tables_dir / f"{format_id}.yaml"
    if not path.exists():
        return None
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return None


def _get_k_min(k_table: dict[str, Any], slot_type: str) -> int | None:
    """Return required minimum pool size for slot_type from K-table."""
    k_min_per_slot = k_table.get("k_min_per_slot") or k_table
    if not isinstance(k_min_per_slot, dict):
        return None
    entry = k_min_per_slot.get(slot_type)
    if isinstance(entry, dict):
        return entry.get("k_min")
    if isinstance(entry, int):
        return entry
    return None


def validate_pool_depth(
    format_id: str,
    persona_id: str,
    topic_id: str,
    pool_index: "PoolIndex",
    k_tables_dir: Path | None = None,
    slot_definitions: list[list[str]] | None = None,
) -> ValidationResult:
    """
    Fail if any slot type pool size < K-table minimum for that slot.
    If slot_definitions provided, only check slot types that appear there; otherwise check all in K-table.
    """
    errors: list[str] = []
    warnings: list[str] = []
    k_tables_dir = k_tables_dir or DEFAULT_K_TABLES_DIR
    k_table = _load_k_table(format_id, k_tables_dir)
    if not k_table:
        warnings.append(f"K-table missing for format {format_id}; pool depth check skipped.")
        return ValidationResult(valid=True, errors=[], warnings=warnings)

    slot_types_to_check = set()
    if slot_definitions:
        for row in slot_definitions:
            slot_types_to_check.update(row)
    else:
        k_min_per_slot = k_table.get("k_min_per_slot") or k_table
        if isinstance(k_min_per_slot, dict):
            slot_types_to_check.update(k_min_per_slot.keys())
    if not slot_types_to_check:
        slot_types_to_check = {"STORY"}

    # Build slot_definitions so get_pool_sizes returns all relevant types
    fallback_slots = list(slot_types_to_check)
    slots_for_sizes = slot_definitions if slot_definitions else [fallback_slots]
    pool_sizes = pool_index.get_pool_sizes(persona_id, topic_id, slots_for_sizes)
    for st in slot_types_to_check:
        k_min = _get_k_min(k_table, st)
        if k_min is None:
            continue
        pool_size = pool_sizes.get(st, 0)
        if pool_size < k_min:
            errors.append(
                f"Pool depth for {st}: {pool_size} < K-table minimum {k_min} (format {format_id}, persona={persona_id}, topic={topic_id})."
            )
    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
