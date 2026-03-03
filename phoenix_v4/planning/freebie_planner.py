"""
Freebie Planning & Attachment — Phase 1 + V4 Immersion Ecosystem.
Authority: specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md.

Input: BookSpec (or dict), FormatPlan (dict), CompiledBook (or dict), Arc (engine + peak).
Optional: wave_index, series_context (series_id, installment_number, total_in_series, previous_primary_freebies).
Output: freebie_bundle (list[str]), cta_template_id (str), freebie_slug (str).
Also: freebie_bundle_with_formats (list of {freebie_id, formats}) for asset manifest.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FREEBIES = REPO_ROOT / "config" / "freebies"

FREEBIE_TYPES = [
    "companion_workbook_pdf",
    "somatic_html_tool",
    "assessment_html",
    "mini_audio",
    "checklist_pdf",
    "journal_pdf",
    "identity_sheet_pdf",
    "thirty_day_tracker_pdf",
    "environment_guide_pdf",
    "emergency_kit_html",
    "guided_audio",
    "affirmations_audio",
    "audio_journal_prompts",
    "conversation_scripts_pdf",
    "resistance_mapping_html",
    "accountability_partner_pdf",
]


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _book_duration_minutes(format_plan: dict[str, Any], default_min_per_chapter: int = 5) -> int:
    ch = format_plan.get("chapter_count") or 0
    return ch * default_min_per_chapter


def _duration_class(minutes: int) -> str:
    if minutes >= 120:
        return "CORE"
    if minutes >= 60:
        return "SHORT"
    return "MIN"


def _has_exercise_slot(compiled: Any) -> bool:
    seq = _get(compiled, "chapter_slot_sequence") or []
    for ch in seq:
        if isinstance(ch, list):
            for s in ch:
                if str(s).upper() == "EXERCISE":
                    return True
        elif str(ch).upper() == "EXERCISE":
            return True
    return False


def _arc_peak(arc: Any) -> int:
    if arc is None:
        return 4
    curve = _get(arc, "emotional_curve") or _get(arc, "emotional_temperature_sequence")
    if isinstance(curve, list) and curve:
        try:
            return max(int(x) for x in curve if x is not None)
        except (ValueError, TypeError):
            pass
    return 4


def _slug_part(s: str) -> str:
    return (s or "").lower().replace("_", "-").strip() or "default"


def _persona_prefers_structured(persona_id: str, rules: dict) -> Optional[bool]:
    """True = prefer structured, False = prefer interactive, None = no preference."""
    priorities = rules.get("persona_priorities") or {}
    structured = priorities.get("structured") or []
    interactive = priorities.get("interactive") or []
    pid = (persona_id or "").lower()
    for p in structured:
        if p.lower() in pid or pid in p.lower():
            return True
    for p in interactive:
        if p.lower() in pid or pid in p.lower():
            return False
    return None


def _pick_diverse_by_persona(
    candidates: list[tuple[str, dict]],
    persona_id: str,
    rules: dict,
    wave_rows: list[dict[str, Any]],
) -> Optional[str]:
    """
    Deterministic picker that applies persona style preference first, then picks
    the least-used freebie id across current wave rows.
    """
    if not candidates:
        return None
    prefer = _persona_prefers_structured(persona_id, rules)
    if prefer is None:
        pool = candidates
    else:
        want_style = "structured" if prefer else "interactive"
        preferred = [(fid, fb) for fid, fb in candidates if fb.get("tool_style") == want_style]
        pool = preferred or candidates
    if not wave_rows:
        return pool[0][0]

    def _usage(fid: str) -> int:
        return sum(1 for r in wave_rows if fid in (r.get("freebie_bundle") or []))

    return min(pool, key=lambda item: (_usage(item[0]), item[0]))[0]


def _normalize_wave_rows(wave_index: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Keep only plan rows and collapse duplicates by book_id (last row wins).
    This keeps wave density logic scoped to unique books rather than artifact/file rows.
    """
    plan_rows = [r for r in wave_index if isinstance(r, dict) and "freebie_bundle" in r]
    if not plan_rows:
        return []
    dedup: dict[str, dict[str, Any]] = {}
    ordered_keys: list[str] = []
    for i, row in enumerate(plan_rows):
        key = str(row.get("book_id") or row.get("plan_id") or row.get("plan_hash") or f"row:{i}")
        if key not in dedup:
            ordered_keys.append(key)
        dedup[key] = row
    return [dedup[k] for k in ordered_keys]


def get_freebie_bundle_with_formats(
    bundle: list[str],
    freebies_map: dict[str, Any],
    book_spec: Any,
    format_plan: dict[str, Any],
    compiled: Any,
) -> list[dict[str, Any]]:
    """
    Return list of {freebie_id, formats} for each freebie in bundle.
    Formats come from registry output_formats; filtered by book context (e.g. no epub for somatic/assessment).
    """
    result: list[dict[str, Any]] = []
    for freebie_id in bundle:
        fb = freebies_map.get(freebie_id) or {}
        formats = list(fb.get("output_formats") or [])
        if not formats:
            freebie_type = (fb.get("type") or "").lower()
            if "audio" in freebie_type or freebie_type == "mini_audio":
                formats = ["mp3"]
            else:
                formats = ["html"]
        freebie_type = (fb.get("type") or "").lower()
        if "somatic" in freebie_type or "assessment" in freebie_type:
            formats = [f for f in formats if f != "epub"]
        result.append({"freebie_id": freebie_id, "formats": formats})
    return result


def plan_freebies(
    book_spec: Any,
    format_plan: dict[str, Any],
    compiled: Any,
    arc: Any,
    wave_index: Optional[list[dict[str, Any]]] = None,
    series_context: Optional[dict[str, Any]] = None,
    registry_path: Optional[Path] = None,
    rules_path: Optional[Path] = None,
) -> tuple[list[str], str, str]:
    """
    Deterministic freebie assignment. Phase 1: no wave_index. Phase 3: pass wave_index
    (rows from artifacts/freebies/index.jsonl) to reseed slug when density exceeds thresholds.
    series_context (optional): series_id, installment_number, total_in_series, previous_primary_freebies
    for series-aware selection (future use).
    Returns (freebie_bundle, cta_template_id, freebie_slug).
    Slug formula: {topic}-{persona}-{primary_freebie}.
    """
    registry_path = registry_path or (CONFIG_FREEBIES / "freebie_registry.yaml")
    rules_path = rules_path or (CONFIG_FREEBIES / "freebie_selection_rules.yaml")

    reg = _load_yaml(registry_path)
    rules = _load_yaml(rules_path)
    freebies_map = reg.get("freebies") or {}
    normalized_wave = _normalize_wave_rows(wave_index or [])

    # series_context (optional): used for series-aware selection rules (e.g. max_per_series, required_installments)
    _ = series_context  # reserved for future use

    topic_id = _get(book_spec, "topic_id") or ""
    persona_id = _get(book_spec, "persona_id") or ""
    engine = _get(arc, "engine") or ""

    duration_min = _book_duration_minutes(format_plan)
    duration_class = _duration_class(duration_min)
    has_exercise = _has_exercise_slot(compiled)
    arc_peak_val = _arc_peak(arc)

    def compatible(fb: dict) -> bool:
        topics = fb.get("topics") or []
        personas = fb.get("personas") or []
        engines = fb.get("engines") or []
        book_types = fb.get("book_types") or []
        max_int = fb.get("arc_intensity_max", 0)
        if topic_id and topics and topic_id not in topics:
            return False
        if persona_id and personas and persona_id not in personas:
            return False
        if engine and engines and engine not in engines:
            return False
        if duration_class and book_types and duration_class not in book_types:
            return False
        if max_int < arc_peak_val:
            return False
        return True

    bundle: list[str] = []

    # Rule 1 — Companion (duration >= 60)
    companion_rule = rules.get("companion_rule") or {}
    min_dur = companion_rule.get("min_duration_minutes", 60)
    if duration_min >= min_dur:
        ft = companion_rule.get("freebie_type", "companion_workbook_pdf")
        for fid, fb in freebies_map.items():
            if fb.get("type") != ft or not compatible(fb):
                continue
            bundle.append(fid)
            break

    # Rule 2 — Somatic (one somatic_html_tool if EXERCISE present); Rule 4/5 persona prioritization
    if has_exercise:
        somatic_rule = rules.get("somatic_rule") or {}
        ft = somatic_rule.get("freebie_type", "somatic_html_tool")
        candidates = [(fid, fb) for fid, fb in freebies_map.items() if fb.get("type") == ft and compatible(fb)]
        chosen = _pick_diverse_by_persona(candidates, persona_id, rules, normalized_wave)
        if chosen and chosen not in bundle:
            bundle.append(chosen)

    # Rule 3 — Assessment (engine in shame/anxiety/burnout); Rule 4/5 persona prioritization
    assessment_rule = rules.get("assessment_rule") or {}
    assessment_engines = assessment_rule.get("engines") or ["shame", "anxiety", "burnout"]
    if engine in assessment_engines:
        ft = assessment_rule.get("freebie_type", "assessment_html")
        candidates = [(fid, fb) for fid, fb in freebies_map.items() if fb.get("type") == ft and compatible(fb)]
        chosen = _pick_diverse_by_persona(candidates, persona_id, rules, normalized_wave)
        if chosen and chosen not in bundle:
            bundle.append(chosen)

    # Fallback: ensure at least one compatible freebie is attached.
    if not bundle:
        generic_candidates: list[tuple[str, dict]] = []
        for fid, fb in freebies_map.items():
            if not compatible(fb):
                continue
            formats = [str(f).lower() for f in (fb.get("output_formats") or [])]
            if formats and all(f == "mp3" for f in formats):
                continue
            generic_candidates.append((fid, fb))
        if not generic_candidates:
            # Last-resort catalog fallback: pick from any registry freebie to avoid empty-bundle waves.
            for fid, fb in freebies_map.items():
                formats = [str(f).lower() for f in (fb.get("output_formats") or [])]
                if formats and all(f == "mp3" for f in formats):
                    continue
                generic_candidates.append((fid, fb))
        fallback = _pick_diverse_by_persona(generic_candidates, persona_id, rules, normalized_wave)
        if fallback:
            bundle.append(fallback)

    anti = rules.get("anti_cluster") or {}
    max_bundle = anti.get("identical_bundle_ratio_max", 0.40)
    max_cta = anti.get("identical_cta_ratio_max", 0.50)
    max_slug = anti.get("identical_slug_pattern_ratio_max", 0.60)

    if normalized_wave and bundle:
        n = len(normalized_wave)
        same_bundle = sum(1 for r in normalized_wave if sorted(r.get("freebie_bundle") or []) == sorted(bundle))
        if (same_bundle / n) >= max_bundle:
            extra_candidates: list[tuple[str, dict]] = []
            for fid, fb in freebies_map.items():
                if fid in bundle or not compatible(fb):
                    continue
                formats = [str(f).lower() for f in (fb.get("output_formats") or [])]
                # Prefer extras that have at least one non-audio format.
                if formats and all(f == "mp3" for f in formats):
                    continue
                extra_candidates.append((fid, fb))
            if extra_candidates:
                def _usage(fid: str) -> int:
                    return sum(1 for r in normalized_wave if fid in (r.get("freebie_bundle") or []))
                extra_id = min(extra_candidates, key=lambda item: (_usage(item[0]), item[0]))[0]
                bundle.append(extra_id)

    bundle = sorted(bundle)

    primary_id = bundle[0] if bundle else None
    cta_style = "tool_forward"
    if primary_id and primary_id in freebies_map:
        cta_style = freebies_map[primary_id].get("cta_style") or cta_style
    cta_template_id = cta_style

    topic_slug = _slug_part(topic_id)
    persona_slug = _slug_part(persona_id)
    freebie_part = _slug_part(primary_id) if primary_id else "default"
    freebie_slug = f"{topic_slug}-{persona_slug}-{freebie_part}"

    # Phase 3: reseed slug when wave density would exceed thresholds (deterministic)
    if normalized_wave:
        import hashlib
        seed_hex = hashlib.sha256(
            f"freebie:{topic_id}:{persona_id}:{_get(book_spec, 'seed', '')}".encode()
        ).hexdigest()[:8]
        cta_seed_int = int(seed_hex, 16)
        n = len(normalized_wave)

        same_cta = sum(1 for r in normalized_wave if (r.get("cta_template_id") or "") == cta_template_id)
        if (same_cta / n) >= max_cta:
            cta_templates = _load_yaml(CONFIG_FREEBIES / "cta_templates.yaml")
            alt_templates = sorted(k for k in cta_templates.keys() if isinstance(k, str) and k != cta_template_id)
            if alt_templates:
                cta_template_id = alt_templates[cta_seed_int % len(alt_templates)]

        same_bundle = sum(1 for r in normalized_wave if (r.get("freebie_bundle") or []) == bundle)
        same_cta = sum(1 for r in normalized_wave if (r.get("cta_template_id") or "") == cta_template_id)
        same_slug = sum(1 for r in normalized_wave if (r.get("slug") or "").startswith(f"{topic_slug}-{persona_slug}-"))
        if (same_bundle / n) >= max_bundle or (same_cta / n) >= max_cta or (same_slug / n) >= max_slug:
            freebie_slug = f"{topic_slug}-{persona_slug}-{freebie_part}-{seed_hex}"

    return (bundle, cta_template_id, freebie_slug)
