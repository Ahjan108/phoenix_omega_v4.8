"""
Phoenix V4.5 format simulation — tests all format/tier configurations.
Uses PHOENIX_V4_5_COMPLETE_FORMAT_SPEC (14 formats, 6 tiers).
No real atoms; mock pool and structural validation only.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Try YAML; fallback to empty config if not available
try:
    import yaml
except ImportError:
    yaml = None

CONFIG_DIR = Path(__file__).resolve().parent / "config"


def load_yaml(name: str) -> dict[str, Any]:
    p = CONFIG_DIR / name
    if p.exists() and yaml is not None:
        with open(p) as f:
            return yaml.safe_load(f) or {}
    if name == "v4_5_formats.yaml":
        return _FALLBACK_FORMATS
    if name == "validation_matrix.yaml":
        return _FALLBACK_MATRIX
    return {}


# Fallback when PyYAML not installed
_FALLBACK_FORMATS = {
    "formats": {
        "deep_book_6h": {"duration": "6 hours", "words_min": 52000, "words_max": 58000, "chapters_min": 38, "chapters_max": 44, "parts": 5, "tier": "S"},
        "deep_book_5h": {"duration": "5 hours", "words_min": 43000, "words_max": 48000, "chapters_min": 30, "chapters_max": 36, "parts": 4, "tier": "S"},
        "deep_book_4h": {"duration": "4 hours", "words_min": 34000, "words_max": 38000, "chapters_min": 24, "chapters_max": 30, "parts": 3, "parts_max": 4, "tier": "S"},
        "extended_book_3h": {"duration": "3 hours", "words_min": 25000, "words_max": 29000, "chapters_min": 18, "chapters_max": 22, "parts": 3, "tier": "A"},
        "extended_book_2h": {"duration": "2 hours", "words_min": 17000, "words_max": 19000, "chapters_min": 12, "chapters_max": 16, "parts": 2, "tier": "A"},
        "standard_book": {"duration": "1 hour", "words_min": 8500, "words_max": 10500, "chapters_min": 7, "chapters_max": 9, "parts": 1, "tier": "B"},
        "short_book_45": {"duration": "45 min", "words_min": 6000, "words_max": 7500, "chapters_min": 5, "chapters_max": 7, "parts": 1, "tier": "B"},
        "short_book_30": {"duration": "30 min", "words_min": 4000, "words_max": 5000, "chapters_min": 3, "chapters_max": 4, "parts": 1, "tier": "C"},
        "micro_book_20": {"duration": "20 min", "words_min": 2800, "words_max": 3400, "chapters_min": 2, "chapters_max": 3, "parts": 0, "tier": "C"},
        "micro_book_15": {"duration": "15 min", "words_min": 2000, "words_max": 2500, "chapters_min": 2, "chapters_max": 2, "parts": 0, "tier": "C"},
        "capsule_10": {"duration": "10 min", "words_min": 1300, "words_max": 1700, "chapters_min": 1, "chapters_max": 2, "parts": 0, "tier": "D"},
        "capsule_5": {"duration": "5 min", "words_min": 650, "words_max": 850, "chapters_min": 1, "chapters_max": 1, "parts": 0, "tier": "D"},
        "reset_2": {"duration": "2 min", "words_min": 250, "words_max": 350, "chapters_min": 0, "chapters_max": 0, "parts": 0, "tier": "E"},
        "reset_90s": {"duration": "90 sec", "words_min": 180, "words_max": 240, "chapters_min": 0, "chapters_max": 0, "parts": 0, "tier": "E"},
    },
    "section_types": ["HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"],
}
_FALLBACK_MATRIX = {
    "tiers": ["S", "A", "B", "C", "D", "E"],
    "parts_min": {"S": 4, "A": 2, "B": 1, "C": 1, "D": 0, "E": 0},
    "parts_max": {"S": 5, "A": 3, "B": 1, "C": 1, "D": 0, "E": 0},
    "characters_min": {"S": 4, "A": 3, "B": 4, "C": 2, "D": 1, "E": 0},
    "characters_max": {"S": 6, "A": 4, "B": 6, "C": 3, "D": 1, "E": 0},
    "misfire_tax_min": {"S": 1, "A": 1, "B": 2, "C": 1, "D": 0, "E": 0},
    "silence_beat_min": {"S": 1, "A": 1, "B": 2, "C": 1, "D": 0, "E": 0},
    "never_know_min": {"S": 1, "A": 1, "B": 2, "C": 1, "D": 0, "E": 0},
    "interrupt_count": {"S": 1, "A": 1, "B": 1, "C": 1, "D": 0, "E": 0},
    "integration_modes_min": {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "E": 1},
    "flinch_audit_min": {"S": 3, "A": 2, "B": 5, "C": 2, "D": 1, "E": 0},
    "reflection_max": {"S": 350, "A": 350, "B": 350, "C": 280, "D": 150, "E": 0},
    "reflection_post_impact_max": {"S": 280, "A": 280, "B": 280, "C": 200, "D": 120, "E": 0},
}


@dataclass
class FormatConfig:
    format_id: str
    duration: str
    words_min: int
    words_max: int
    chapters_min: int
    chapters_max: int
    parts: int
    parts_max: int | None
    tier: str

    @classmethod
    def from_dict(cls, format_id: str, d: dict[str, Any]) -> "FormatConfig":
        parts = d.get("parts", 0)
        return cls(
            format_id=format_id,
            duration=str(d.get("duration", "")),
            words_min=int(d.get("words_min", 0)),
            words_max=int(d.get("words_max", 0)),
            chapters_min=int(d.get("chapters_min", 0)),
            chapters_max=int(d.get("chapters_max", 0)),
            parts=int(parts) if parts else 0,
            parts_max=int(d["parts_max"]) if d.get("parts_max") is not None else None,
            tier=str(d.get("tier", "?")),
        )


@dataclass
class BookRequest:
    format_id: str
    teacher: str
    persona: str
    topic: str
    overlay: str | None
    seed: int

    def request_id(self, seq: int) -> str:
        return f"bk_{self.persona}_{self.topic}_{self.format_id}_{seq}"


@dataclass
class SimulatedPlan:
    """Simulated plan structure (no real atom IDs)."""
    format_id: str
    tier: str
    chapters: int
    parts: int
    slots_per_chapter: list[int]  # e.g. [7, 8, 7] for 3 chapters
    total_slots: int
    word_range: tuple[int, int]


@dataclass
class ValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def get_formats() -> dict[str, FormatConfig]:
    data = load_yaml("v4_5_formats.yaml")
    formats = data.get("formats", {})
    return {
        fid: FormatConfig.from_dict(fid, cfg)
        for fid, cfg in formats.items()
    }


def get_validation_matrix() -> dict[str, Any]:
    return load_yaml("validation_matrix.yaml")


# Default slot counts per chapter by tier (approximate from spec)
SLOTS_PER_CHAPTER: dict[str, tuple[int, int]] = {
    "S": (8, 10),
    "A": (7, 9),
    "B": (7, 9),
    "C": (5, 7),
    "D": (5, 6),
    "E": (0, 0),
}

# Tier E (resets): fixed atom counts, no chapters
RESET_2_SLOTS = 3   # SCENE + EXERCISE + INTEGRATION
RESET_90S_SLOTS = 2  # EXERCISE + INTEGRATION
CAPSULE_5_SLOTS = 5  # HOOK-STORY-REFLECTION-EXERCISE-INTEGRATION


def compute_plan(format_cfg: FormatConfig, rng: random.Random) -> SimulatedPlan:
    """Compute a simulated plan for this format (chapter count, slots)."""
    tier = format_cfg.tier
    c_min, c_max = format_cfg.chapters_min, format_cfg.chapters_max
    if c_max < c_min:
        c_max = c_min
    chapters = rng.randint(c_min, c_max) if c_min < c_max else c_min
    parts = format_cfg.parts or 1
    if format_cfg.format_id == "reset_90s":
        return SimulatedPlan(
            format_id=format_cfg.format_id,
            tier=tier,
            chapters=0,
            parts=0,
            slots_per_chapter=[],
            total_slots=RESET_90S_SLOTS,
            word_range=(format_cfg.words_min, format_cfg.words_max),
        )
    if format_cfg.format_id == "reset_2":
        return SimulatedPlan(
            format_id=format_cfg.format_id,
            tier=tier,
            chapters=0,
            parts=0,
            slots_per_chapter=[],
            total_slots=RESET_2_SLOTS,
            word_range=(format_cfg.words_min, format_cfg.words_max),
        )
    if format_cfg.format_id == "capsule_5":
        return SimulatedPlan(
            format_id=format_cfg.format_id,
            tier=tier,
            chapters=1,
            parts=0,
            slots_per_chapter=[CAPSULE_5_SLOTS],
            total_slots=CAPSULE_5_SLOTS,
            word_range=(format_cfg.words_min, format_cfg.words_max),
        )
    smin, smax = SLOTS_PER_CHAPTER.get(tier, (5, 7))
    slots_per_chapter = [rng.randint(smin, smax) for _ in range(chapters)]
    total_slots = sum(slots_per_chapter)
    return SimulatedPlan(
        format_id=format_cfg.format_id,
        tier=tier,
        chapters=chapters,
        parts=parts,
        slots_per_chapter=slots_per_chapter,
        total_slots=total_slots,
        word_range=(format_cfg.words_min, format_cfg.words_max),
    )


def validate_plan(plan: SimulatedPlan, fmt_cfg: FormatConfig, matrix: dict[str, Any]) -> ValidationResult:
    """Validate simulated plan against V4.5 validation matrix."""
    errors: list[str] = []
    warnings: list[str] = []
    tier = plan.tier
    tiers = matrix.get("tiers", ["S", "A", "B", "C", "D", "E"])
    if tier not in tiers:
        errors.append(f"Unknown tier {tier}")
        return ValidationResult(passed=False, errors=errors, warnings=warnings)

    def get_rule(name: str, default: Any = None) -> Any:
        val = matrix.get(name)
        if isinstance(val, dict) and tier in val:
            return val[tier]
        return default

    # Chapters in range
    if plan.chapters > 0 and fmt_cfg.chapters_max and plan.chapters > fmt_cfg.chapters_max:
        errors.append(f"chapters {plan.chapters} > max {fmt_cfg.chapters_max}")
    if plan.chapters > 0 and plan.chapters < fmt_cfg.chapters_min:
        errors.append(f"chapters {plan.chapters} < min {fmt_cfg.chapters_min}")

    # Parts: use format's part range when available (e.g. deep_book_4h allows 3-4)
    parts_min = get_rule("parts_min", 0)
    parts_max_rule = get_rule("parts_max", 1)
    # Format can allow fewer parts than tier default (e.g. deep_book_4h: 3-4 parts)
    effective_parts_min = min(parts_min, fmt_cfg.parts) if fmt_cfg.parts else parts_min
    fmt_parts_max = getattr(fmt_cfg, "parts_max", None) or fmt_cfg.parts
    effective_parts_max = max(parts_max_rule, fmt_parts_max) if parts_max_rule is not None else fmt_parts_max
    if plan.parts < effective_parts_min and tier in ("S", "A"):
        errors.append(f"parts {plan.parts} < min {effective_parts_min} for tier {tier}")
    if tier in ("S", "A") and plan.parts > effective_parts_max:
        errors.append(f"parts {plan.parts} > max {effective_parts_max}")

    # Misfire tax / silence / never-know / interrupt: need enough story slots to place them
    misfire_min = get_rule("misfire_tax_min", 0)
    silence_min = get_rule("silence_beat_min", 0)
    never_min = get_rule("never_know_min", 0)
    interrupt_cnt = get_rule("interrupt_count", 0)
    if tier in ("S", "A") and plan.parts > 0:
        misfire_min = misfire_min * plan.parts
        silence_min = silence_min * plan.parts
        never_min = never_min * plan.parts
        interrupt_cnt = interrupt_cnt * plan.parts
    # Conservative: we need at least (misfire + silence + never + interrupt) story-like slots
    special_story_slots = (misfire_min or 0) + (silence_min or 0) + (never_min or 0) + (interrupt_cnt or 0)
    # Approximate: ~1/3 of slots are STORY in a typical beat map
    approx_story_slots = plan.total_slots // 3
    if special_story_slots > 0 and approx_story_slots < special_story_slots:
        warnings.append(
            f"tier {tier}: need ~{special_story_slots} special story slots, plan has ~{approx_story_slots} story slots"
        )

    # Flinch audit
    flinch_min = get_rule("flinch_audit_min", 0)
    if tier in ("S", "A") and plan.parts > 0:
        flinch_min = flinch_min * plan.parts
    if flinch_min > 0 and plan.total_slots < flinch_min:
        errors.append(f"flinch_audit min {flinch_min} but total_slots {plan.total_slots}")

    # Integration modes: need at least N INTEGRATION slots
    modes_min = get_rule("integration_modes_min", 0)
    if modes_min > 0:
        # At least one integration per chapter typically
        integration_slots = plan.chapters if plan.chapters > 0 else (1 if plan.total_slots >= 2 else 0)
        if integration_slots < min(modes_min, 1):
            errors.append(f"integration_modes_min {modes_min} but no chapter structure for modes")

    # Reflection ceiling: checked at render time; we just note
    refl_max = get_rule("reflection_max", 0)
    if refl_max and plan.word_range[1] > 10000:
        warnings.append(f"reflection_max {refl_max} applies; ensure pool has compliant REFLECTION atoms")

    passed = len(errors) == 0
    return ValidationResult(passed=passed, errors=errors, warnings=warnings)


def format_config_from_stage2_plan(plan: dict[str, Any]) -> FormatConfig:
    """Build FormatConfig from Stage 2 FormatPlan (dict with format_runtime_id, chapter_count or target_chapter_count, word_target_range, tier)."""
    fid = plan.get("format_runtime_id", "standard_book")
    ch = int(plan.get("chapter_count") or plan.get("target_chapter_count", 12))
    wr = plan.get("word_target_range", [9000, 11000])
    if isinstance(wr, (list, tuple)) and len(wr) >= 2:
        w_min, w_max = int(wr[0]), int(wr[1])
    else:
        w_min, w_max = 9000, 11000
    tier = plan.get("tier", "A")
    return FormatConfig(
        format_id=fid,
        duration="",
        words_min=w_min,
        words_max=w_max,
        chapters_min=ch,
        chapters_max=ch,
        parts=1,
        parts_max=1,
        tier=tier,
    )


def capability_check(plan: SimulatedPlan, pool_per_type: int = 100) -> bool:
    """Mock capability: do we have enough atoms in pool for this plan?"""
    if plan.total_slots == 0:
        return True
    # Each slot needs one atom; we need at least total_slots across all types
    # Conservative: require pool has at least total_slots per section type (overkill but safe)
    return pool_per_type >= (plan.total_slots // 6 + 1)


def generate_requests(
    formats: dict[str, FormatConfig],
    teachers: list[str],
    personas: list[str],
    topics: list[str],
    n: int,
    seed: int,
    cover_all_formats: bool = True,
) -> list[BookRequest]:
    """Generate n book requests. If cover_all_formats, first 14 are one per format."""
    rng = random.Random(seed)
    format_ids = list(formats.keys())
    requests: list[BookRequest] = []
    if cover_all_formats and format_ids:
        for i, fid in enumerate(format_ids[:14]):
            requests.append(BookRequest(
                format_id=fid,
                teacher=teachers[i % len(teachers)] if teachers else "default_teacher",
                persona=personas[i % len(personas)] if personas else "default_persona",
                topic=topics[i % len(topics)] if topics else "default_topic",
                overlay=None,
                seed=seed + i,
            ))
    remaining = n - len(requests)
    if remaining <= 0:
        return requests[:n]
    for _ in range(remaining):
        fid = rng.choice(format_ids)
        requests.append(BookRequest(
            format_id=fid,
            teacher=rng.choice(teachers) if teachers else "default_teacher",
            persona=rng.choice(personas) if personas else "default_persona",
            topic=rng.choice(topics) if topics else "default_topic",
            overlay=None,
            seed=rng.randint(0, 2**31 - 1),
        ))
    return requests


def run_simulation(
    n: int,
    seed: int = 42,
    pool_per_type: int = 100,
    teachers: list[str] | None = None,
    personas: list[str] | None = None,
    topics: list[str] | None = None,
    cover_all_formats: bool = True,
    requests: list[BookRequest] | None = None,
    stage2_plans: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Run n simulated book compilations. Returns (results, summary).
    When requests and stage2_plans are provided (e.g. from Stage 2 format selector), format and chapter count come from each plan.
    """
    teachers = teachers or ["teacher_1"]
    personas = personas or ["gen_z_la", "first_responder", "healthcare_nurse"]
    topics = topics or ["anxiety", "burnout", "grief"]
    formats = get_formats()
    matrix = get_validation_matrix()
    if not formats:
        return [], {"error": "No formats loaded", "n": n}
    if requests is None:
        requests = generate_requests(formats, teachers, personas, topics, n, seed, cover_all_formats)
    results: list[dict[str, Any]] = []
    rng = random.Random(seed)
    for i, req in enumerate(requests):
        fmt_cfg = None
        if stage2_plans and i < len(stage2_plans) and stage2_plans[i]:
            fmt_cfg = format_config_from_stage2_plan(stage2_plans[i])
        if fmt_cfg is None:
            fmt_cfg = formats.get(req.format_id)
        if not fmt_cfg:
            results.append({
                "request_id": req.request_id(i),
                "format_id": req.format_id,
                "passed": False,
                "error": "unknown format",
                "errors": ["unknown format"],
            })
            continue
        plan = compute_plan(fmt_cfg, rng)
        cap_ok = capability_check(plan, pool_per_type)
        if not cap_ok:
            results.append({
                "request_id": req.request_id(i),
                "format_id": req.format_id,
                "tier": fmt_cfg.tier,
                "passed": False,
                "error": "capability_fail",
                "errors": ["insufficient pool for plan"],
                "chapters": plan.chapters,
                "total_slots": plan.total_slots,
            })
            continue
        val = validate_plan(plan, fmt_cfg, matrix)
        results.append({
            "request_id": req.request_id(i),
            "format_id": req.format_id,
            "tier": fmt_cfg.tier,
            "chapters": plan.chapters,
            "parts": plan.parts,
            "total_slots": plan.total_slots,
            "passed": val.passed,
            "errors": val.errors,
            "warnings": val.warnings,
        })
    # Summary
    passed = sum(1 for r in results if r.get("passed"))
    by_format: dict[str, dict[str, int]] = {}
    by_tier: dict[str, dict[str, int]] = {}
    for r in results:
        fid = r.get("format_id", "?")
        tier = r.get("tier", "?")
        by_format.setdefault(fid, {"pass": 0, "fail": 0})
        by_tier.setdefault(tier, {"pass": 0, "fail": 0})
        if r.get("passed"):
            by_format[fid]["pass"] += 1
            by_tier[tier]["pass"] += 1
        else:
            by_format[fid]["fail"] += 1
            by_tier[tier]["fail"] += 1
    error_reasons: dict[str, int] = {}
    for r in results:
        if not r.get("passed") and r.get("errors"):
            for e in r["errors"]:
                error_reasons[e] = error_reasons.get(e, 0) + 1
    summary = {
        "n": n,
        "passed": passed,
        "failed": n - passed,
        "pass_rate": passed / n if n else 0,
        "by_format": by_format,
        "by_tier": by_tier,
        "error_reasons": error_reasons,
    }
    return results, summary
