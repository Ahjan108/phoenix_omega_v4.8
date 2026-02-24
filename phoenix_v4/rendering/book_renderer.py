"""
Stage 6 book renderer: CompiledBook + prose map → manuscript/ebook outputs.
Writers: TxtWriter (QA and pipeline). Optional DOCX/EPUB later.
Edge cases: placeholders → [Placeholder: TYPE], silence → [Silence: TYPE], missing → fail or [Missing: atom_id].
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

from phoenix_v4.rendering.prose_resolver import (
    RenderResult,
    resolve_prose_for_plan,
    _is_placeholder_or_silence,
    _slot_type_from_placeholder_or_silence,
)


@dataclass
class RenderOptions:
    """Options for Stage 6 rendering."""
    allow_placeholders: bool = False
    on_missing: str = "fail"  # "fail" | "placeholder"
    title_page: bool = True
    include_slot_labels_qa: bool = False  # If True, emit [STORY] atom_id before prose (QA style)


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
        if self.options.title_page:
            lines.extend(_build_title_page_lines(self.plan))

        idx = 0
        for ch, slots in enumerate(chapter_slot_sequence):
            lines.append("")
            lines.append(f"========== CHAPTER {ch + 1} ==========")
            lines.append("")
            for slot_type in slots:
                if idx >= len(atom_ids):
                    break
                aid = atom_ids[idx]
                idx += 1
                slot_label = str(slot_type).strip()
                prose = _get_prose(aid, slot_label, self.prose_map, self.render_result, self.options)
                if self.options.include_slot_labels_qa and slot_label == "STORY" and not _is_placeholder_or_silence(aid):
                    lines.append(f"[STORY] {aid}")
                    lines.append("")
                lines.append(prose)
                lines.append("")
            lines.append("")

        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        return out_path


def render_book(
    plan: dict[str, Any],
    output_dir: Path,
    *,
    formats: Optional[List[str]] = None,
    atoms_root: Optional[Path] = None,
    bindings_path: Optional[Path] = None,
    teacher_banks_root: Optional[Path] = None,
    allow_placeholders: bool = False,
    on_missing: str = "fail",
    title_page: bool = True,
    include_slot_labels_qa: bool = False,
) -> dict[str, Path]:
    """
    Stage 6: resolve prose for plan and write requested formats to output_dir.
    Returns dict format -> path (e.g. {"txt": Path("output_dir/book.txt")}).
    """
    formats = formats or ["txt"]
    output_dir = Path(output_dir)

    render_result = resolve_prose_for_plan(
        plan,
        atoms_root=atoms_root,
        bindings_path=bindings_path,
        teacher_banks_root=teacher_banks_root,
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

    options = RenderOptions(
        allow_placeholders=allow_placeholders,
        on_missing=on_missing,
        title_page=title_page,
        include_slot_labels_qa=include_slot_labels_qa,
    )
    written: dict[str, Path] = {}

    if "txt" in formats:
        writer = TxtWriter(plan, render_result.prose_map, render_result, options)
        out_path = output_dir / "book.txt"
        writer.write(out_path)
        written["txt"] = out_path

    return written
