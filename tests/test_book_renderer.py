"""Tests for Stage 6 prose resolution and book renderer."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.rendering.prose_resolver import (
    PlanContext,
    RenderResult,
    _parse_block_file_with_prose,
    resolve_prose_for_plan,
    _is_placeholder_or_silence,
    _slot_type_from_placeholder_or_silence,
)
from phoenix_v4.rendering.book_renderer import (
    ChapterFlowGateError,
    RenderOptions,
    TxtWriter,
    render_book,
)


def test_placeholder_silence_helpers() -> None:
    assert _is_placeholder_or_silence("placeholder:STORY:ch0:slot2") is True
    assert _is_placeholder_or_silence("silence:REFLECTION:ch1:slot3") is True
    assert _is_placeholder_or_silence("nyc_executives_self_worth_shame_EMBODIMENT_v04") is False
    assert _slot_type_from_placeholder_or_silence("placeholder:HOOK:ch0:slot0") == "HOOK"
    assert _slot_type_from_placeholder_or_silence("silence:REFLECTION:ch1:slot3") == "REFLECTION"


def test_plan_context_from_plan_with_top_level_ids() -> None:
    plan = {"topic_id": "self_worth", "persona_id": "nyc_executives", "atom_ids": []}
    ctx = PlanContext.from_plan(plan)
    assert ctx.persona_id == "nyc_executives"
    assert ctx.topic_id == "self_worth"
    assert "shame" in ctx.engines or "comparison" in ctx.engines


def test_plan_context_infer_from_story_atom_id() -> None:
    plan = {
        "atom_ids": [
            "placeholder:HOOK:ch0:slot0",
            "nyc_executives_self_worth_shame_EMBODIMENT_v04",
        ],
    }
    ctx = PlanContext.from_plan(plan)
    assert ctx.persona_id == "nyc_executives"
    assert ctx.topic_id == "self_worth"
    assert "shame" in ctx.engines


def test_resolve_prose_returns_result_with_placeholder_tracking() -> None:
    plan = {
        "atom_ids": ["placeholder:HOOK:ch0:slot0", "nyc_executives_self_worth_shame_EMBODIMENT_v04"],
        "chapter_slot_sequence": [["HOOK", "STORY"]],
    }
    repo = Path(__file__).resolve().parent.parent
    result = resolve_prose_for_plan(plan, atoms_root=repo / "atoms")
    assert isinstance(result, RenderResult)
    assert len(result.placeholder_or_silence_ids) >= 1
    # STORY prose should be resolved if atoms exist
    if result.prose_map:
        assert "nyc_executives_self_worth_shame_EMBODIMENT_v04" in result.prose_map or "nyc_executives_self_worth_shame_EMBODIMENT_v04" in result.missing_ids


def test_render_book_txt_with_placeholders_allowed(tmp_path: Path) -> None:
    plan = {
        "plan_hash": "test_hash",
        "atom_ids": ["placeholder:HOOK:ch0:slot0", "placeholder:STORY:ch0:slot1"],
        "chapter_slot_sequence": [["HOOK", "STORY"]],
    }
    written = render_book(
        plan,
        tmp_path,
        formats=["txt"],
        allow_placeholders=True,
        on_missing="placeholder",
        title_page=False,
    )
    assert "txt" in written
    assert (tmp_path / "book.txt").exists()
    text = (tmp_path / "book.txt").read_text()
    assert "Chapter 1" in text
    assert "[Placeholder:" in text


def test_txt_writer_emits_missing_when_on_missing_placeholder() -> None:
    plan = {
        "atom_ids": ["unknown_atom_id_xyz"],
        "chapter_slot_sequence": [["STORY"]],
    }
    result = resolve_prose_for_plan(plan)
    result.missing_ids.append("unknown_atom_id_xyz")
    options = RenderOptions(allow_placeholders=True, on_missing="placeholder")
    writer = TxtWriter(plan, result.prose_map, result, options)
    out = Path(__file__).resolve().parent.parent / "artifacts" / "books_qa" / "test_missing.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    writer.write(out)
    assert "[Missing:" in out.read_text()
    out.unlink(missing_ok=True)


def test_render_book_writes_chapter_flow_report(tmp_path: Path) -> None:
    plan = {
        "plan_hash": "flow_report_hash",
        "atom_ids": ["placeholder:HOOK:ch0:slot0", "placeholder:STORY:ch0:slot1"],
        "chapter_slot_sequence": [["HOOK", "STORY"]],
    }
    written = render_book(
        plan,
        tmp_path,
        formats=["txt"],
        allow_placeholders=True,
        on_missing="placeholder",
        title_page=False,
        enforce_word_count=False,
    )
    assert "chapter_flow_report" in written
    report = json.loads((tmp_path / "chapter_flow_report.json").read_text(encoding="utf-8"))
    assert report["chapter_count"] >= 1
    assert report["status"] in {"PASS", "FAIL"}


def test_render_book_enforce_chapter_flow_raises(tmp_path: Path) -> None:
    plan = {
        "plan_hash": "flow_gate_fail_hash",
        "atom_ids": ["placeholder:HOOK:ch0:slot0", "placeholder:STORY:ch0:slot1"],
        "chapter_slot_sequence": [["HOOK", "STORY"]],
    }
    with pytest.raises(ChapterFlowGateError):
        render_book(
            plan,
            tmp_path,
            formats=["txt"],
            allow_placeholders=True,
            on_missing="placeholder",
            title_page=False,
            enforce_word_count=False,
            enforce_chapter_flow=True,
        )


def test_rewrite_overlay_does_not_mutate_source_atom_files(tmp_path: Path) -> None:
    """Overlay-only safety: resolve with rewrite_overrides must not modify any source atom file."""
    persona, topic, slot = "test_persona", "test_topic", "REFLECTION"
    atoms_root = tmp_path / "atoms"
    canonical = atoms_root / persona / topic / slot / "CANONICAL.txt"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    original_content = "Original prose from atom file.\n"
    canonical.write_text(
        "## REFLECTION v01\n---\n---\n" + original_content + "\n---\n",
        encoding="utf-8",
    )
    atom_id = f"{persona}_{topic}_{slot}_v01"
    plan = {
        "topic_id": topic,
        "persona_id": persona,
        "atom_ids": [atom_id],
        "chapter_slot_sequence": [["REFLECTION"]],
    }
    mtime_before = canonical.stat().st_mtime_ns
    content_before = canonical.read_text()
    overlay_text = "Overridden by rewrite overlay; source must stay unchanged."
    result = resolve_prose_for_plan(plan, atoms_root=atoms_root, rewrite_overrides={atom_id: overlay_text})
    mtime_after = canonical.stat().st_mtime_ns
    content_after = canonical.read_text()
    assert result.prose_map.get(atom_id) == overlay_text
    assert content_after == content_before, "Source atom file content must be unchanged after overlay"
    assert mtime_after == mtime_before, "Source atom file mtime must be unchanged after overlay"


def test_parse_block_file_with_metadata_then_prose(tmp_path: Path) -> None:
    canonical = tmp_path / "CANONICAL.txt"
    canonical.write_text(
        """## INTEGRATION v01
---
mode: BODY_LANDED
reframe_type: BODY_FACT
weight: light
carry_line: "line"
---
This is real prose, not metadata.
---
""",
        encoding="utf-8",
    )
    parsed = _parse_block_file_with_prose(canonical, "p", "t", "INTEGRATION")
    assert parsed["p_t_INTEGRATION_v01"].startswith("This is real prose")
