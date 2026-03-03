"""
Part 3.1 capability check: K-table load, pool sizes per slot type, achievable chapter count.
Strict mode: missing K-table = hard fail. Relaxed: warn + pass.
Achievable chapters = min(requested, min_S floor(pool_size[S] / slots_per_chapter[S])).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FORMAT_SELECTION = REPO_ROOT / "config" / "format_selection"
K_TABLES_DIR = CONFIG_FORMAT_SELECTION / "k_tables"


@dataclass
class CapabilityResult:
    ok: bool
    achievable_chapters: int
    diagnostics: list[str]
    errors: list[str]


def _load_ktable(format_structural_id: str) -> dict | None:
    """Load K-table YAML for format. Returns None if file missing."""
    path = K_TABLES_DIR / f"{format_structural_id}.yaml"
    if not path.exists():
        return None
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return None


def _slots_per_chapter_per_type(slot_definitions: list[list[str]]) -> dict[str, int]:
    """Count slots per chapter for each slot type (assume uniform across chapters)."""
    if not slot_definitions:
        return {}
    counts: dict[str, int] = {}
    for row in slot_definitions:
        for st in row:
            counts[st] = counts.get(st, 0) + 1
    # Normalize by number of chapters so we get "per chapter"
    nch = len(slot_definitions)
    return {k: v // nch if nch else 0 for k, v in counts.items()}


def capability_check(
    book_spec: dict,
    format_plan: dict,
    pool_index: "PoolIndex",  # phoenix_v4.planning.pool_index.PoolIndex
    mode: Literal["strict", "relaxed"] = "strict",
) -> CapabilityResult:
    """
    Part 3.1 steps 1-2: K-table presence, pool sizes, achievable chapter count.
    Strict: missing K-table = hard fail. Relaxed: warn + pass.
    Achievable = min(requested, min_S floor(pool_size[S] / slots_per_chapter[S])).
    """
    diagnostics: list[str] = []
    errors: list[str] = []

    format_structural_id = format_plan.get("format_structural_id") or format_plan.get("format_id") or ""
    chapter_count = int(format_plan.get("chapter_count") or format_plan.get("target_chapter_count") or 12)
    slot_definitions = format_plan.get("slot_definitions") or []
    if not slot_definitions and chapter_count > 0:
        slot_definitions = [["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]] * chapter_count
    if len(slot_definitions) != chapter_count and len(slot_definitions) == 1:
        slot_definitions = [list(slot_definitions[0]) for _ in range(chapter_count)]
    persona_id = book_spec.get("persona_id") or book_spec.get("persona") or ""
    topic_id = book_spec.get("topic_id") or book_spec.get("topic") or ""

    k_table = _load_ktable(format_structural_id) if format_structural_id else None

    if k_table is None and format_structural_id:
        if mode == "strict":
            errors.append(f"K-table required for format {format_structural_id} (missing: {K_TABLES_DIR / format_structural_id}.yaml)")
            return CapabilityResult(ok=False, achievable_chapters=0, diagnostics=diagnostics, errors=errors)
        diagnostics.append(f"K-table missing for format {format_structural_id}; passing (relaxed mode).")
        return CapabilityResult(ok=True, achievable_chapters=chapter_count, diagnostics=diagnostics, errors=[])

    pool_sizes = pool_index.get_pool_sizes(persona_id, topic_id, slot_definitions)
    slots_per_chapter = _slots_per_chapter_per_type(slot_definitions)

    achievable_per_slot: dict[str, int] = {}
    for st, count_per_ch in slots_per_chapter.items():
        if count_per_ch <= 0:
            achievable_per_slot[st] = chapter_count
            continue
        pool_size = pool_sizes.get(st, 0)
        achievable_per_slot[st] = pool_size // count_per_ch

    achievable_chapters = chapter_count
    if achievable_per_slot:
        achievable_chapters = min(chapter_count, min(achievable_per_slot.values()))

    if k_table:
        k_min_per_slot = k_table.get("k_min_per_slot") or k_table
        for st in slots_per_chapter:
            k_min = None
            if isinstance(k_min_per_slot, dict):
                entry = k_min_per_slot.get(st)
                if isinstance(entry, dict):
                    k_min = entry.get("k_min")
                elif isinstance(entry, int):
                    k_min = entry
            required = chapter_count * slots_per_chapter.get(st, 0)
            pool_size = pool_sizes.get(st, 0)
            if required > pool_size and mode == "strict":
                errors.append(f"Slot type {st}: required {required} unique atoms for {chapter_count} chapters, pool has {pool_size}.")
            if achievable_chapters < chapter_count:
                diagnostics.append(f"Achievable chapters limited by {st} to {achievable_per_slot.get(st, 0)}.")

    return CapabilityResult(
        ok=len(errors) == 0,
        achievable_chapters=achievable_chapters,
        diagnostics=diagnostics,
        errors=errors,
    )


