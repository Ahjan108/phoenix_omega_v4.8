"""
Stage 6 book renderer: CompiledBook + prose map → manuscript/ebook outputs.
Writers: TxtWriter (QA and pipeline). Optional DOCX/EPUB later.
Edge cases: placeholders → [Placeholder: TYPE], silence → [Silence: TYPE], missing → fail or [Missing: atom_id].
Teacher Mode: when atom_source == practice_fallback for EXERCISE, wrap with teacher intro/close templates (deterministic).
Delivery: clean_for_delivery() strips scaffolding + resolves loc-var fallbacks.
          delivery_contract_gate() hard-fails build if forbidden artifacts survive into output.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow, evaluate_chapter_flow_with_slots

# ---------------------------------------------------------------------------
# Delivery contract: forbidden patterns that must never reach output
# ---------------------------------------------------------------------------

# Universal sensory fallbacks for location variables that may not be hydrated.
# Written to work anywhere — no city, no transit system, no weather specifics.
_LOC_VAR_FALLBACKS: dict[str, str] = {
    "weather_detail":   "gray light through the window",
    "street_name":      "the street below",
    "transit_line":     "the train",
    "transit_stop":     "the platform",
    "city_name":        "the city",
    "neighborhood":     "the neighborhood",
    "building_type":    "the building",
    "local_landmark":   "a landmark nearby",
    "park_name":        "the park",
    "coffee_shop":      "a coffee shop",
    "restaurant":       "a nearby restaurant",
    "store_name":       "a nearby store",
    "office_building":  "the office building",
    "commute_mode":     "the commute",
}

# Metadata keys that belong to the pipeline, not the reader.
_METADATA_LINE_RE = re.compile(
    r"^\s*"
    r"(family|voice_mode|mode|reframe_type|mechanism_emphasis|"
    r"weight|carry_line|atom_id|BAND|MECHANISM_DEPTH|"
    r"COST_TYPE|COST_INTENSITY|IDENTITY_STAGE)"
    r"\s*:",
    re.IGNORECASE,
)

# Inline block headers like [family: F4 voice_mode: guide mechanism_emphasis: automatic]
_METADATA_BLOCK_RE = re.compile(r"^\[.*?(family|voice_mode|mode|reframe_type).*?\]", re.IGNORECASE)

# Title-page lines like "Topic: anxiety" or "Persona: gen_z_professionals"
_TITLE_META_RE = re.compile(r"^(Topic|Persona)\s*:", re.IGNORECASE)

# Scaffold markers
_DIVIDER_RE    = re.compile(r"^---\s*$")
_CHAPTER_RE    = re.compile(r"^={5,}.*CHAPTER", re.IGNORECASE)


class DeliveryContractError(ValueError):
    """Raised by delivery_contract_gate() when forbidden artifacts survive into prose output."""


def _resolve_loc_var_fallbacks(text: str) -> str:
    """Replace known location variables with universal sensory fallbacks.
    Any {var} that remains after this is caught and hard-failed by delivery_contract_gate().
    """
    for var_name, fallback in _LOC_VAR_FALLBACKS.items():
        text = text.replace("{" + var_name + "}", fallback)
    return text


def _strip_scaffolding_lines(text: str) -> str:
    """Remove lines that are pipeline control data or markdown scaffolding, not prose."""
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if (
            _METADATA_LINE_RE.match(stripped)
            or _METADATA_BLOCK_RE.match(stripped)
            or _TITLE_META_RE.match(stripped)
            or _DIVIDER_RE.match(stripped)
            or _CHAPTER_RE.match(stripped)
        ):
            continue
        out.append(line)
    return "\n".join(out)


def clean_for_delivery(text: str) -> str:
    """Post-assembly cleanup pass.

    Order of operations:
      1. Resolve known loc-var placeholders with universal fallbacks.
      2. Strip pipeline metadata lines and markdown scaffolding.
      3. Collapse 3+ consecutive blank lines to 2 (paragraph breathing room only).

    Always call this before delivery_contract_gate().
    """
    text = _resolve_loc_var_fallbacks(text)
    text = _strip_scaffolding_lines(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def delivery_contract_gate(text: str, source_hint: str = "output") -> None:
    """Hard-fail the build if any forbidden artifact survives into delivered prose.

    Call after clean_for_delivery(). Raises DeliveryContractError with line numbers
    and descriptions so the upstream author or atom can be fixed.

    Checks (per line):
      - Unresolved {variable} placeholders
      - Pipeline metadata keys: family:, voice_mode:, mode:, reframe_type:
      - Markdown dividers: ---
      - Chapter scaffold markers: ===...=== CHAPTER
    """
    violations: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        m = re.search(r"\{[^}]+\}", line)
        if m:
            violations.append(f"  line {lineno}: unresolved variable {m.group()!r}")
        if _METADATA_LINE_RE.match(stripped):
            violations.append(f"  line {lineno}: pipeline metadata key in prose {stripped[:40]!r}")
        if _METADATA_BLOCK_RE.match(stripped):
            violations.append(f"  line {lineno}: metadata block in prose {stripped[:60]!r}")
        if _DIVIDER_RE.match(stripped):
            violations.append(f"  line {lineno}: markdown divider '---'")
        if _CHAPTER_RE.match(stripped):
            violations.append(f"  line {lineno}: chapter scaffold marker {stripped[:40]!r}")

    if violations:
        extra = (
            f" ... and {len(violations) - 5} more" if len(violations) > 5 else ""
        )
        raise DeliveryContractError(
            f"Delivery contract violated in {source_hint}: "
            f"{len(violations)} artifact(s) found.\n"
            + "\n".join(violations[:5])
            + extra
            + "\n\nFix the upstream atom, or add the variable to _LOC_VAR_FALLBACKS."
        )

import json

import yaml

# ---------------------------------------------------------------------------
# Mechanism alias system
# ---------------------------------------------------------------------------

_MECHANISM_ALIASES_DIR = Path(__file__).parent.parent.parent / "config" / "source_of_truth" / "mechanism_aliases"
_MECHANISM_ALIAS_CACHE: dict[str, dict] = {}


def _load_mechanism_alias(persona_id: str, topic_id: str) -> Optional[dict]:
    """Load the mechanism alias for this persona × topic, or None if not found.

    Returns the parsed YAML dict with at minimum:
      short_form, descriptor, naming_moment, forms
    """
    if not persona_id or not topic_id:
        return None
    cache_key = f"{persona_id}/{topic_id}"
    if cache_key in _MECHANISM_ALIAS_CACHE:
        return _MECHANISM_ALIAS_CACHE[cache_key]
    path = _MECHANISM_ALIASES_DIR / persona_id / f"{topic_id}.yaml"
    if not path.exists():
        _MECHANISM_ALIAS_CACHE[cache_key] = None  # type: ignore[assignment]
        return None
    try:
        alias = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        _MECHANISM_ALIAS_CACHE[cache_key] = alias
        return alias
    except Exception:
        _MECHANISM_ALIAS_CACHE[cache_key] = None  # type: ignore[assignment]
        return None


def _resolve_mechanism_alias_tokens(text: str, alias: Optional[dict]) -> str:
    """Replace {{MA}}, {{MA_DEF}}, {{MA_FULL}} tokens with alias values.

    Also substitutes literal "the mechanism" / "The mechanism" / "this mechanism"
    with the persona-specific alias short_form, so existing atoms that use the
    generic phrase are automatically upgraded without requiring atom edits.

    If no alias is provided, replaces tokens with a neutral fallback so the
    delivery_contract_gate doesn't fire on unresolved {variable} patterns.
    """
    if alias:
        short_form    = alias.get("short_form") or "this pattern"
        descriptor    = alias.get("descriptor") or "the pattern that shapes this experience"
        naming_moment = alias.get("naming_moment") or ""
    else:
        short_form    = "this pattern"
        descriptor    = "the pattern that shapes this experience"
        naming_moment = ""

    # Explicit tokens (new atoms / future-facing)
    text = text.replace("{{MA}}", short_form)
    text = text.replace("{{MA_DEF}}", descriptor)
    text = text.replace("{{MA_FULL}}", naming_moment)

    # Backward-compatible: replace generic "the mechanism" in existing atoms
    if alias:
        # Sentence-start capitalised form first (order matters)
        sf_cap = short_form[0].upper() + short_form[1:] if short_form else short_form
        text = text.replace("The mechanism", sf_cap)
        text = text.replace("the mechanism", short_form)
        text = text.replace("this mechanism", short_form)
        text = text.replace("that mechanism", short_form)

    return text


def _build_naming_moment_block(alias: dict) -> str:
    """Compose the full naming-moment paragraph injected once into Chapter 1.

    Structure:
      [naming_moment text]

      That's [short_form]. It will come up throughout this book — not because
      it's the only thing happening, but because it tends to be underneath
      most of what we're going to look at.
    """
    short_form    = alias.get("short_form") or "this pattern"
    naming_moment = (alias.get("naming_moment") or "").strip()
    if not naming_moment:
        return ""
    bridge = (
        f"That's {short_form}. It will come up throughout this book — not because "
        f"it's the only thing happening, but because it tends to be underneath "
        f"most of what we're going to look at."
    )
    return f"{naming_moment}\n\n{bridge}"


from phoenix_v4.rendering.prose_resolver import (
    RenderResult,
    resolve_prose_for_plan,
    _is_placeholder_or_silence,
    _slot_type_from_placeholder_or_silence,
)

# ---------------------------------------------------------------------------
# Word-count build gate + slot-level deficit report
# ---------------------------------------------------------------------------

_FORMAT_REGISTRY_PATH = Path(__file__).parent.parent.parent / "config" / "format_selection" / "format_registry.yaml"
_FORMAT_REGISTRY_CACHE: Optional[dict] = None


def _load_format_registry() -> dict:
    global _FORMAT_REGISTRY_CACHE
    if _FORMAT_REGISTRY_CACHE is None:
        try:
            _FORMAT_REGISTRY_CACHE = yaml.safe_load(_FORMAT_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
        except Exception:
            _FORMAT_REGISTRY_CACHE = {}
    return _FORMAT_REGISTRY_CACHE


def _runtime_word_range(runtime_format_id: str) -> Optional[tuple[int, int]]:
    """Return (min, max) word range for a runtime format, or None if not found."""
    if not runtime_format_id:
        return None
    registry = _load_format_registry()
    runtime_formats = registry.get("runtime_formats") or {}
    entry = runtime_formats.get(runtime_format_id) or {}
    word_range = entry.get("word_range")
    if word_range and len(word_range) == 2:
        return (int(word_range[0]), int(word_range[1]))
    return None


class WordCountGateError(ValueError):
    """Raised when rendered word count falls below the runtime format's minimum target."""


def word_count_gate(text: str, runtime_format_id: str, source_hint: str = "output") -> dict:
    """Fail build if word count is below the runtime format's word_range minimum.

    Returns a metrics dict on success:
      {"word_count": N, "word_range": (min, max), "runtime_format_id": id, "status": "pass"}

    Raises WordCountGateError with a clear deficit message on failure.
    """
    word_count = len(text.split())
    word_range = _runtime_word_range(runtime_format_id)

    metrics = {
        "word_count": word_count,
        "runtime_format_id": runtime_format_id,
        "word_range": list(word_range) if word_range else None,
        "status": "pass",
    }

    if word_range is None:
        metrics["status"] = "skip"
        metrics["note"] = f"runtime_format_id {runtime_format_id!r} not found in format_registry — gate skipped"
        return metrics

    lo, hi = word_range
    if word_count < lo:
        deficit = lo - word_count
        pct = word_count / lo * 100
        raise WordCountGateError(
            f"Word count gate FAILED for {source_hint}.\n"
            f"  Runtime target : {runtime_format_id} → {lo:,}–{hi:,} words\n"
            f"  Actual output  : {word_count:,} words ({pct:.0f}% of minimum)\n"
            f"  Deficit        : {deficit:,} words\n\n"
            f"Fix options (see docs/LONGFORM_STRATEGY.md):\n"
            f"  1. Increase per-atom prose length (target 400–800 words for 6h builds).\n"
            f"  2. Add a second STORY slot per chapter (doubles narrative content).\n"
            f"  3. Enable multi-atom REFLECTION composition in format k-table."
        )

    if word_count > hi:
        metrics["status"] = "warn_over"
        metrics["note"] = f"Word count {word_count:,} exceeds max {hi:,} — review pacing"

    return metrics


class ChapterFlowGateError(ValueError):
    """Raised when chapter flow gate is enforced and one or more chapters fail."""


def _extract_rendered_chapters(rendered_text: str) -> list[tuple[int, str]]:
    """
    Split rendered manuscript by clean chapter headings ("Chapter N").
    Returns list of (chapter_number, chapter_text_without_heading).
    """
    lines = rendered_text.splitlines()
    chapters: list[tuple[int, str]] = []
    current_num: Optional[int] = None
    current_lines: list[str] = []
    for line in lines:
        m = re.match(r"^\s*Chapter\s+(\d+)\s*$", line.strip())
        if m:
            if current_num is not None:
                chapters.append((current_num, "\n".join(current_lines).strip()))
            current_num = int(m.group(1))
            current_lines = []
            continue
        if current_num is not None:
            current_lines.append(line)
    if current_num is not None:
        chapters.append((current_num, "\n".join(current_lines).strip()))
    return chapters


def chapter_flow_gate_report(
    rendered_text: str,
    plan: Optional[dict[str, Any]] = None,
    prose_map: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """
    Evaluate each rendered chapter with chapter_flow_gate and return summary report.
    When plan and prose_map are provided, uses slot-level checks so TAKEAWAY and THREAD
    are required to be non-empty when present.
    """
    chapter_slot_sequence = (plan or {}).get("chapter_slot_sequence") or []
    atom_ids = (plan or {}).get("atom_ids") or []
    if plan and prose_map and chapter_slot_sequence and atom_ids:
        # Slot-level: require TAKEAWAY and THREAD content when present
        chapter_reports = []
        failed = 0
        idx = 0
        for ch, slots in enumerate(chapter_slot_sequence):
            segment_proses = []
            for _ in slots:
                if idx < len(atom_ids):
                    aid = atom_ids[idx]
                    segment_proses.append(prose_map.get(aid, ""))
                else:
                    segment_proses.append("")
                idx += 1
            res = evaluate_chapter_flow_with_slots(slots, segment_proses)
            if res.status != "PASS":
                failed += 1
            chapter_reports.append({
                "chapter": ch + 1,
                "status": res.status,
                "score": res.score,
                "errors": res.errors,
                "warnings": res.warnings,
                "metrics": res.metrics,
            })
        return {
            "chapter_count": len(chapter_reports),
            "failed_chapters": failed,
            "status": "PASS" if failed == 0 else "FAIL",
            "chapters": chapter_reports,
        }
    # Fallback: text-only (no TAKEAWAY/THREAD slot enforcement)
    chapters = _extract_rendered_chapters(rendered_text)
    chapter_reports = []
    failed = 0
    for chapter_number, chapter_text in chapters:
        res = evaluate_chapter_flow(chapter_text)
        if res.status != "PASS":
            failed += 1
        chapter_reports.append({
            "chapter": chapter_number,
            "status": res.status,
            "score": res.score,
            "errors": res.errors,
            "warnings": res.warnings,
            "metrics": res.metrics,
        })
    return {
        "chapter_count": len(chapters),
        "failed_chapters": failed,
        "status": "PASS" if failed == 0 else "FAIL",
        "chapters": chapter_reports,
    }


def _build_deficit_report(
    plan: dict,
    prose_map: dict[str, str],
    runtime_format_id: str,
) -> dict:
    """Build a per-chapter, per-slot word-budget breakdown.

    Returns a dict suitable for writing as budget.json alongside the rendered book.
    """
    chapter_slot_sequence = plan.get("chapter_slot_sequence") or []
    atom_ids = plan.get("atom_ids") or []
    word_range = _runtime_word_range(runtime_format_id)
    target_total = word_range[0] if word_range else None
    target_per_chapter = (target_total // len(chapter_slot_sequence)) if (target_total and chapter_slot_sequence) else None

    chapters = []
    slot_totals: dict[str, int] = {}
    grand_total = 0
    idx = 0

    for ch_idx, slots in enumerate(chapter_slot_sequence):
        ch_data: dict = {"chapter": ch_idx + 1, "slots": [], "chapter_word_count": 0}
        for slot_type in slots:
            if idx >= len(atom_ids):
                break
            aid = atom_ids[idx]
            prose = prose_map.get(aid, "")
            wc = len(prose.split()) if prose else 0
            ch_data["slots"].append({"slot": slot_type, "atom_id": aid, "word_count": wc})
            ch_data["chapter_word_count"] += wc
            slot_totals[slot_type] = slot_totals.get(slot_type, 0) + wc
            grand_total += wc
            idx += 1

        deficit = ((target_per_chapter - ch_data["chapter_word_count"]) if target_per_chapter else None)
        ch_data["target_per_chapter"] = target_per_chapter
        ch_data["chapter_deficit"] = deficit
        chapters.append(ch_data)

    return {
        "runtime_format_id": runtime_format_id,
        "word_range_target": list(word_range) if word_range else None,
        "grand_total_words": grand_total,
        "deficit_to_minimum": ((word_range[0] - grand_total) if word_range else None),
        "slot_totals": slot_totals,
        "chapters": chapters,
    }


@dataclass
class RenderOptions:
    """Options for Stage 6 rendering."""
    allow_placeholders: bool = False
    on_missing: str = "fail"          # "fail" | "placeholder"
    title_page: bool = True
    include_slot_labels_qa: bool = False  # If True, emit [STORY] atom_id before prose (QA style)
    clean_output: bool = True         # Strip scaffolding + run delivery_contract_gate before write
    mechanism_alias: Optional[dict] = None  # Loaded alias dict for {{MA}} token resolution


def _get_prose(
    atom_id: str,
    slot_type: str,
    prose_map: dict[str, str],
    render_result: RenderResult,
    options: RenderOptions,
) -> str:
    """Return prose for this slot. Normalizes placeholders, silence, missing."""
    if _is_placeholder_or_silence(atom_id):
        if not options.allow_placeholders:
            return f"[Placeholder: {slot_type}]"  # caller may have chosen to fail earlier
        if atom_id.startswith("silence:"):
            return f"[Silence: {slot_type}]"
        return f"[Placeholder: {slot_type}]"

    prose = prose_map.get(atom_id)
    if prose is not None and prose != "":
        return prose
    if atom_id in render_result.missing_ids:
        if options.on_missing == "fail":
            raise ValueError(f"Missing prose for atom_id: {atom_id}")
        return f"[Missing: {atom_id}]"
    if options.on_missing == "fail":
        raise ValueError(f"Missing prose for atom_id: {atom_id}")
    return f"[Missing: {atom_id}]"


def _wrap_practice_fallback_exercise(prose: str, plan: dict[str, Any], chapter_index: int, slot_index: int) -> str:
    """When EXERCISE has atom_source=practice_fallback, wrap with teacher intro/close. Deterministic by (book_id, ch, si)."""
    teacher_id = (plan.get("teacher_id") or (plan.get("book_spec") or {}).get("teacher_id") or "").strip()
    if not teacher_id:
        return prose
    try:
        from phoenix_v4.teacher.teacher_config import load_teacher_config
        cfg = load_teacher_config(teacher_id)
        wrapper = cfg.get("exercise_wrapper") or {}
        intro_templates = list(wrapper.get("intro_templates") or [])
        close_templates = list(wrapper.get("close_templates") or [])
        if not intro_templates and not close_templates:
            return prose
        book_id = plan.get("plan_id") or plan.get("plan_hash") or "book"
        h = hashlib.sha256(f"{book_id}:{chapter_index}:{slot_index}".encode("utf-8")).hexdigest()
        intro = (intro_templates[int(int(h[:8], 16) % len(intro_templates))] + "\n\n") if intro_templates else ""
        close = ("\n\n" + close_templates[int(int(h[8:16], 16) % len(close_templates))]) if close_templates else ""
        return f"{intro}{prose}{close}"
    except Exception:
        return prose


def _build_title_page_lines(plan: dict[str, Any]) -> list[str]:
    """Optional title/credits from plan (author_assets, topic_id, persona_id)."""
    lines: list[str] = []
    topic_id = plan.get("topic_id") or (plan.get("book_spec") or {}).get("topic_id") or ""
    persona_id = plan.get("persona_id") or (plan.get("book_spec") or {}).get("persona_id") or ""
    author_assets = plan.get("author_assets") or {}
    pen_name = author_assets.get("pen_name") or author_assets.get("author_pen_name") or plan.get("author_id") or ""
    if topic_id or persona_id or pen_name:
        lines.append("")
        if pen_name:
            lines.append(str(pen_name))
        if topic_id:
            lines.append(f"Topic: {topic_id}")
        if persona_id:
            lines.append(f"Persona: {persona_id}")
        lines.append("")
    return lines


class TxtWriter:
    """Write plan + prose to a single .txt file (manuscript/QA)."""

    def __init__(self, plan: dict[str, Any], prose_map: dict[str, str], render_result: RenderResult, options: RenderOptions):
        self.plan = plan
        self.prose_map = prose_map
        self.render_result = render_result
        self.options = options

    def write(self, out_path: Path) -> Path:
        chapter_slot_sequence = self.plan.get("chapter_slot_sequence") or []
        atom_ids = self.plan.get("atom_ids") or []
        if not chapter_slot_sequence or not atom_ids:
            raise ValueError("Plan missing chapter_slot_sequence or atom_ids")

        lines: list[str] = []
        if self.options.title_page and not self.options.clean_output:
            # Title page only in QA mode; clean_output strips persona/topic metadata
            lines.extend(_build_title_page_lines(self.plan))

        atom_sources = self.plan.get("atom_sources") or []
        alias = self.options.mechanism_alias  # may be None
        naming_moment_injected = False

        idx = 0
        for ch, slots in enumerate(chapter_slot_sequence):
            lines.append("")
            if self.options.clean_output:
                # Clean delivery: simple heading, no scaffold decoration
                lines.append(f"Chapter {ch + 1}")
            else:
                # QA mode: scaffold markers kept for diff/debugging
                lines.append(f"========== CHAPTER {ch + 1} ==========")
            lines.append("")
            for si, slot_type in enumerate(slots):
                if idx >= len(atom_ids):
                    break
                aid = atom_ids[idx]
                slot_label = str(slot_type).strip()
                prose = _get_prose(aid, slot_label, self.prose_map, self.render_result, self.options)
                if atom_sources and idx < len(atom_sources) and atom_sources[idx] == "practice_fallback" and slot_label == "EXERCISE":
                    prose = _wrap_practice_fallback_exercise(prose, self.plan, ch, si)
                idx += 1
                if self.options.include_slot_labels_qa and slot_label == "STORY" and not _is_placeholder_or_silence(aid):
                    lines.append(f"[STORY] {aid}")
                    lines.append("")
                lines.append(prose)
                lines.append("")

                # Inject mechanism alias naming_moment once, after the first HOOK in Chapter 1
                if (
                    not naming_moment_injected
                    and ch == 0
                    and slot_label == "HOOK"
                    and alias
                    and self.options.clean_output
                ):
                    naming_block = _build_naming_moment_block(alias)
                    if naming_block:
                        lines.append(naming_block)
                        lines.append("")
                        naming_moment_injected = True

            lines.append("")

        full_text = "\n".join(lines).strip()

        # Resolve {{MA}}, {{MA_DEF}}, {{MA_FULL}} tokens before delivery gate
        full_text = _resolve_mechanism_alias_tokens(full_text, alias)

        if self.options.clean_output:
            full_text = clean_for_delivery(full_text)
            delivery_contract_gate(full_text, source_hint=str(out_path))

        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(full_text + "\n", encoding="utf-8")
        return out_path


def render_book(
    plan: dict[str, Any],
    output_dir: Path,
    *,
    formats: Optional[List[str]] = None,
    atoms_root: Optional[Path] = None,
    bindings_path: Optional[Path] = None,
    teacher_banks_root: Optional[Path] = None,
    rewrite_overrides: Optional[dict[str, str]] = None,
    rewrite_audit_path: Optional[Path] = None,
    allow_placeholders: bool = False,
    on_missing: str = "fail",
    title_page: bool = True,
    include_slot_labels_qa: bool = False,
    clean_output: bool = True,
    enforce_word_count: bool = True,
    enforce_chapter_flow: bool = False,
) -> dict[str, Path]:
    """
    Stage 6: resolve prose for plan and write requested formats to output_dir.
    Returns dict format -> path (e.g. {"txt": Path("output_dir/book.txt")}).

    clean_output=True (default):
      - Strips pipeline metadata, markdown dividers, and chapter scaffold markers.
      - Resolves unhydrated loc-vars ({weather_detail} etc.) with universal fallbacks.
      - Runs delivery_contract_gate() before write — hard-fails if any artifact survives.
      Use for production epub/TTS output.

    clean_output=False:
      - Passes raw assembled text through (scaffold markers preserved).
      - No gate. Use for QA diffs and debugging.

    enforce_word_count=True (default):
      - Reads runtime_format_id from plan and compares rendered word count to word_range min.
      - Writes a budget.json deficit report alongside every rendered book.
      - Raises WordCountGateError if word count is below minimum.
      - Set to False to skip gate (e.g. for short QA builds or atom-pool builds).

    enforce_chapter_flow=False (default):
      - Computes chapter flow report at output_dir/chapter_flow_report.json.
      - If True and any chapter fails flow gate, raises ChapterFlowGateError.
    """
    formats = formats or ["txt"]
    output_dir = Path(output_dir)

    render_result = resolve_prose_for_plan(
        plan,
        atoms_root=atoms_root,
        bindings_path=bindings_path,
        teacher_banks_root=teacher_banks_root,
        rewrite_overrides=rewrite_overrides,
        rewrite_audit_path=rewrite_audit_path,
    )

    # Normalize edge cases: fail on placeholders or missing when not allowed
    if not allow_placeholders and render_result.placeholder_or_silence_ids:
        raise ValueError(
            "Plan contains placeholders or silence slots. Resolve upstream or use allow_placeholders=True. "
            f"First: {render_result.placeholder_or_silence_ids[0]}"
        )
    if on_missing == "fail" and render_result.missing_ids:
        raise ValueError(
            "Missing prose for atom_ids (not found in atoms/ or teacher_banks or compression_atoms): "
            + ", ".join(render_result.missing_ids[:5])
            + (f" ... and {len(render_result.missing_ids) - 5} more" if len(render_result.missing_ids) > 5 else "")
        )

    # Load mechanism alias for this persona × topic (gracefully no-ops if not found)
    persona_id = (plan.get("persona_id") or (plan.get("book_spec") or {}).get("persona_id") or "").strip()
    topic_id   = (plan.get("topic_id")   or (plan.get("book_spec") or {}).get("topic_id")   or "").strip()
    alias = _load_mechanism_alias(persona_id, topic_id)

    options = RenderOptions(
        allow_placeholders=allow_placeholders,
        on_missing=on_missing,
        title_page=title_page,
        include_slot_labels_qa=include_slot_labels_qa,
        clean_output=clean_output,
        mechanism_alias=alias,
    )
    written: dict[str, Path] = {}
    runtime_format_id = (plan.get("runtime_format_id") or "").strip()

    if "txt" in formats:
        writer = TxtWriter(plan, render_result.prose_map, render_result, options)
        out_path = output_dir / "book.txt"
        writer.write(out_path)
        written["txt"] = out_path

        # Word-count gate + slot-level deficit report (always written, gate optional)
        rendered_text = out_path.read_text(encoding="utf-8")
        flow_report = chapter_flow_gate_report(rendered_text, plan=plan, prose_map=render_result.prose_map)
        flow_path = output_dir / "chapter_flow_report.json"
        flow_path.write_text(json.dumps(flow_report, indent=2), encoding="utf-8")
        written["chapter_flow_report"] = flow_path

        if enforce_chapter_flow and flow_report.get("status") != "PASS":
            first_fail = next((c for c in flow_report.get("chapters", []) if c.get("status") != "PASS"), None)
            if first_fail:
                raise ChapterFlowGateError(
                    f"Chapter flow gate FAILED at chapter {first_fail.get('chapter')}: "
                    + ", ".join(first_fail.get("errors") or ["UNKNOWN"])
                )
            raise ChapterFlowGateError("Chapter flow gate FAILED.")

        deficit_report = _build_deficit_report(plan, render_result.prose_map, runtime_format_id)
        budget_path = output_dir / "budget.json"
        budget_path.write_text(json.dumps(deficit_report, indent=2), encoding="utf-8")
        written["budget"] = budget_path

        if enforce_word_count and runtime_format_id:
            wc_metrics = word_count_gate(rendered_text, runtime_format_id, source_hint=str(out_path))
            deficit_report["gate_result"] = wc_metrics
            budget_path.write_text(json.dumps(deficit_report, indent=2), encoding="utf-8")

    return written
