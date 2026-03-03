"""
Phase 2: Emotional waveform, arc continuity, cross-series drift.
Uses synthetic metadata (no real atoms). Validates shape and differentiation.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

# Import plan type from simulator
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulator import SimulatedPlan, FormatConfig


# --- Thresholds (tunable) ---
MIN_INTENSITY_VARIANCE = 0.2       # avoid flat emotional line
MIN_VOLATILE_CHAPTERS = 1          # at least one "hot" chapter (tier B+)
MIN_SILENCE_DENSITY = 0.012        # silence beats per slot (min fraction)
MAX_FLAT_RUN = 10                  # max consecutive chapters with same intensity band (S-tier deep books)
MIN_PRIMARY_CHAR_APPEARANCES = 3
DRIFT_METAPHOR_MAX_SHARE = 0.4    # no metaphor in >40% of stack
DRIFT_ENDING_MAX_SHARE = 0.5       # no ending_phrase in >50% of stack
STACK_SIZE = 10


@dataclass
class SyntheticBookMeta:
    """Synthetic metadata for one book (for Phase 2 checks)."""
    request_id: str
    format_id: str
    tier: str
    chapters: int
    total_slots: int
    intensity_per_chapter: list[float] = field(default_factory=list)
    register_per_chapter: list[str] = field(default_factory=list)  # e.g. cool, warm, hot
    interrupt_chapter: int | None = None
    silence_beat_count: int = 0
    volatile_chapter_count: int = 0
    punch_line_count: int = 0
    character_appearances: dict[str, int] = field(default_factory=dict)
    has_consequence: bool = False
    has_action: bool = False
    metaphor_id: str = ""
    ending_phrase_id: str = ""
    reflection_phrase_ids: list[str] = field(default_factory=list)


def generate_synthetic_metadata(
    plan: SimulatedPlan,
    fmt_cfg: FormatConfig,
    request_id: str,
    seed: int,
) -> SyntheticBookMeta:
    """Generate deterministic synthetic metadata for waveform/arc/drift."""
    rng = random.Random(seed)
    tier = plan.tier
    chapters = plan.chapters or 1
    total_slots = plan.total_slots or 1

    # Emotional intensity per chapter (1-5 scale); force some variance
    intensity = []
    for _ in range(chapters):
        base = rng.uniform(1.5, 4.0)
        intensity.append(round(base, 2))
    if chapters >= 2 and max(intensity) - min(intensity) < 0.5:
        intensity[rng.randint(0, chapters - 1)] = round(rng.uniform(1.0, 2.0), 2)
        intensity[rng.randint(0, chapters - 1)] = round(rng.uniform(3.5, 5.0), 2)

    # Register (temperature) per chapter
    registers = ["cool", "warm", "hot", "land"]
    register = [rng.choice(registers) for _ in range(chapters)]
    if chapters >= 2:
        register[-1] = "land"

    # Interrupt: one chapter in final third (for tiers that need it)
    interrupt_ch = None
    if tier in ("S", "A", "B", "C") and chapters >= 2:
        start = max(0, (chapters * 2) // 3)
        interrupt_ch = rng.randint(start, chapters - 1) if start < chapters else chapters - 1

    # Silence beats: ~2-5% of slots, min 1 if tier has narrative
    silence_count = max(1, int(total_slots * rng.uniform(0.02, 0.08))) if tier != "E" else 0

    # Volatile (hot) chapters; ensure at least 1 for narrative tiers with multiple chapters
    volatile = sum(1 for i, r in zip(intensity, register) if r == "hot" or (i and i >= 4.0))
    if tier in ("S", "A", "B") and chapters >= 2 and volatile == 0:
        volatile = 1
        if register:
            register[min(1, chapters - 1)] = "hot"

    # Punch-line proxy: ~1 per 3 chapters
    punch = max(0, chapters // 3 + rng.randint(-1, 1))

    # Character appearances: 2-4 chars, one primary with >= 3
    num_chars = min(6, max(2, chapters // 2 + rng.randint(0, 2)))
    appearances = {}
    for j in range(num_chars):
        count = rng.randint(1, max(1, total_slots // 4))
        appearances[f"char_{j}"] = count
    if appearances and max(appearances.values()) < MIN_PRIMARY_CHAR_APPEARANCES:
        primary = rng.choice(list(appearances.keys()))
        appearances[primary] = rng.randint(MIN_PRIMARY_CHAR_APPEARANCES, max(5, total_slots // 3))

    # Consequence and action: at least one each for narrative tiers (synthetic: always true when required)
    has_consequence = tier in ("S", "A", "B", "C")
    has_action = tier in ("S", "A", "B", "C")

    # Metaphor and ending ids for drift (deterministic from seed)
    metaphor_id = f"meta_{rng.randint(1000, 9999)}"
    ending_phrase_id = f"end_{rng.randint(100, 999)}"
    reflection_phrase_ids = [f"refl_{rng.randint(10, 99)}" for _ in range(min(5, chapters))]

    return SyntheticBookMeta(
        request_id=request_id,
        format_id=plan.format_id,
        tier=tier,
        chapters=chapters,
        total_slots=total_slots,
        intensity_per_chapter=intensity,
        register_per_chapter=register,
        interrupt_chapter=interrupt_ch,
        silence_beat_count=silence_count,
        volatile_chapter_count=volatile,
        punch_line_count=punch,
        character_appearances=appearances,
        has_consequence=has_consequence,
        has_action=has_action,
        metaphor_id=metaphor_id,
        ending_phrase_id=ending_phrase_id,
        reflection_phrase_ids=reflection_phrase_ids,
    )


def validate_waveform(meta: SyntheticBookMeta) -> tuple[bool, list[str]]:
    """Emotional waveform: variance, volatility, silence density, no long flat run."""
    errors: list[str] = []
    if meta.chapters == 0:
        return True, []

    intensities = meta.intensity_per_chapter
    variance = max(intensities) - min(intensities) if len(intensities) >= 2 else 0.0
    if len(intensities) >= 2 and variance < MIN_INTENSITY_VARIANCE:
        errors.append(f"intensity_variance {variance:.2f} < min {MIN_INTENSITY_VARIANCE}")

    if meta.tier in ("S", "A", "B") and meta.volatile_chapter_count < MIN_VOLATILE_CHAPTERS:
        errors.append(f"volatile_chapters {meta.volatile_chapter_count} < min {MIN_VOLATILE_CHAPTERS}")

    density = meta.silence_beat_count / meta.total_slots if meta.total_slots else 0
    if meta.tier != "E" and meta.total_slots >= 5 and density < MIN_SILENCE_DENSITY:
        errors.append(f"silence_density {density:.3f} < min {MIN_SILENCE_DENSITY}")

    # Flat run: consecutive chapters in same band (1-2, 2-3, 3-4, 4-5)
    if len(intensities) > MAX_FLAT_RUN:
        band = [int(x) for x in intensities]
        run = 1
        for i in range(1, len(band)):
            if band[i] == band[i - 1] or abs(band[i] - band[i - 1]) <= 0.5:
                run += 1
                if run > MAX_FLAT_RUN:
                    errors.append(f"flat_run {run} chapters > max {MAX_FLAT_RUN}")
                    break
            else:
                run = 1

    return len(errors) == 0, errors


def validate_arc(meta: SyntheticBookMeta) -> tuple[bool, list[str]]:
    """Arc continuity: primary character >= 3, consequence, action."""
    errors: list[str] = []
    if meta.tier == "E":
        return True, []

    max_app = max(meta.character_appearances.values()) if meta.character_appearances else 0
    if meta.chapters >= 2 and max_app < MIN_PRIMARY_CHAR_APPEARANCES:
        errors.append(f"no primary character with >={MIN_PRIMARY_CHAR_APPEARANCES} appearances (max={max_app})")

    if meta.tier in ("S", "A", "B") and not meta.has_consequence:
        errors.append("missing visible consequence in arc")
    if meta.tier in ("S", "A", "B") and not meta.has_action:
        errors.append("missing visible action in arc")

    if meta.tier in ("S", "A", "B", "C") and meta.interrupt_chapter is None and meta.chapters >= 2:
        errors.append("missing interrupt placement in final third")

    return len(errors) == 0, errors


def validate_drift(stack: list[SyntheticBookMeta], metaphor_max_share: float = DRIFT_METAPHOR_MAX_SHARE, ending_max_share: float = DRIFT_ENDING_MAX_SHARE) -> tuple[bool, list[str]]:
    """Cross-series drift: metaphor and ending overlap across a stack of books."""
    errors: list[str] = []
    if len(stack) < 2:
        return True, []

    metaphors = [m.metaphor_id for m in stack if m.metaphor_id]
    endings = [m.ending_phrase_id for m in stack if m.ending_phrase_id]
    n = len(stack)

    from collections import Counter
    for mid, count in Counter(metaphors).items():
        if count / n > metaphor_max_share:
            errors.append(f"metaphor {mid} in {count}/{n} books (>{metaphor_max_share:.0%})")
    for eid, count in Counter(endings).items():
        if count / n > ending_max_share:
            errors.append(f"ending_phrase {eid} in {count}/{n} books (>{ending_max_share:.0%})")

    return len(errors) == 0, errors


def run_phase2_on_results(results: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Run Phase 2 on Phase 1 results. Recomputes plan from request_id hash for determinism.
    Enriches each result with phase2_passed, phase2_errors, waveform/arc flags, metaphor/ending ids.
    """
    from simulator import compute_plan, get_formats
    formats = get_formats()
    rng = random.Random(42)
    enriched: list[dict[str, Any]] = []
    all_metas: list[SyntheticBookMeta] = []

    for i, r in enumerate(results):
        if not r.get("passed"):
            enriched.append({**r, "phase2_passed": False, "phase2_errors": ["phase1 failed"], "phase2_skipped": True})
            continue
        fmt_cfg = formats.get(r["format_id"]) if r.get("format_id") else None
        if not fmt_cfg:
            enriched.append({**r, "phase2_passed": False, "phase2_errors": ["unknown format"], "phase2_skipped": True})
            continue
        # Recompute plan with deterministic seed from request_id
        seed = hash(r.get("request_id", i)) % (2**31)
        plan = compute_plan(fmt_cfg, random.Random(seed))
        meta = generate_synthetic_metadata(plan, fmt_cfg, r.get("request_id", f"req_{i}"), seed)
        all_metas.append(meta)
        w_ok, w_err = validate_waveform(meta)
        a_ok, a_err = validate_arc(meta)
        phase2_errors = w_err + a_err
        enriched.append({
            **r,
            "phase2_passed": len(phase2_errors) == 0,
            "phase2_errors": phase2_errors,
            "phase2_waveform_passed": w_ok,
            "phase2_arc_passed": a_ok,
            "phase2_skipped": False,
            "intensity_variance": max(meta.intensity_per_chapter) - min(meta.intensity_per_chapter) if meta.intensity_per_chapter else 0,
            "volatile_chapters": meta.volatile_chapter_count,
            "metaphor_id": meta.metaphor_id,
            "ending_phrase_id": meta.ending_phrase_id,
        })

    # Drift: stacks of STACK_SIZE
    drift_failures = []
    for start in range(0, len(all_metas) - STACK_SIZE + 1, STACK_SIZE):
        stack = all_metas[start : start + STACK_SIZE]
        d_ok, d_err = validate_drift(stack)
        if not d_ok:
            drift_failures.append({"stack_start": start, "errors": d_err})

    summary_phase2 = {
        "phase2_passed": sum(1 for x in enriched if x.get("phase2_passed")),
        "phase2_failed": sum(1 for x in enriched if not x.get("phase2_skipped") and not x.get("phase2_passed")),
        "phase2_skipped": sum(1 for x in enriched if x.get("phase2_skipped")),
        "waveform_failed": sum(1 for x in enriched if x.get("phase2_waveform_passed") is False),
        "arc_failed": sum(1 for x in enriched if x.get("phase2_arc_passed") is False),
        "drift_stacks_checked": (len(all_metas) - STACK_SIZE + 1) // STACK_SIZE if len(all_metas) >= STACK_SIZE else 0,
        "drift_stacks_failed": len(drift_failures),
        "drift_failures": drift_failures[:5],
    }
    return enriched, summary_phase2
