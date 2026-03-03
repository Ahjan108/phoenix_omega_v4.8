"""
Tests for Controlled Intro/Conclusion Variation (plan §9).
- Determinism: same inputs -> same resolved pre-intro, signatures, style IDs.
- No-leak: resolved pre-intro and carry text must not contain {}, ---, id:, path:.
- Cap/duplicate gate: over-cap or duplicate triggers reselect; after max_retries, fail with explicit error and candidates.
- YAML vs runtime title conflict: fixed book_title_line + different runtime title -> ValueError.
- Missing-bank fallback: missing bank -> use YAML; both missing for required block -> validation fails.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_determinism_pre_intro_and_signature():
    """Same inputs (seed, topic, persona, brand, author_assets) produce same resolved blocks and pre_intro_signature."""
    try:
        import yaml
    except ImportError:
        return
    from phoenix_v4.planning.pre_intro_resolver import (
        resolve_pre_intro_blocks,
        compute_pre_intro_signature,
        PRE_INTRO_BLOCK_ORDER,
    )
    from phoenix_v4.planning.author_asset_loader import render_audiobook_pre_intro

    author_assets = {
        "pen_name": "Test Author",
        "audiobook_pre_intro": {
            "narrator_intro": "I am the narrator.",
            "book_title_line": "You are listening to Test Book.",
            "author_intro": "This book was written by Test Author.",
            "author_background": "Test Author is a writer.",
            "why_this_book": "This book exists because.",
            "transition_line": "Chapter One.",
        },
    }
    brand_id = "stillness_press"
    selector_key = "grief|burnout|default_seed"
    config_sot = REPO_ROOT / "config" / "source_of_truth"

    blocks1 = resolve_pre_intro_blocks(
        author_assets,
        brand_id,
        selector_key,
        book_title="",
        series_name="",
        include_series_line=False,
        pattern_bank_overrides_yaml=True,
        config_root=config_sot,
    )
    blocks2 = resolve_pre_intro_blocks(
        author_assets,
        brand_id,
        selector_key,
        book_title="",
        series_name="",
        include_series_line=False,
        pattern_bank_overrides_yaml=True,
        config_root=config_sot,
    )
    assert blocks1 == blocks2
    full1 = render_audiobook_pre_intro(
        author_assets, book_title="", series_name="", include_series_line=False, resolved_blocks=blocks1
    )
    full2 = render_audiobook_pre_intro(
        author_assets, book_title="", series_name="", include_series_line=False, resolved_blocks=blocks2
    )
    assert full1 == full2
    sig1 = compute_pre_intro_signature(full1)
    sig2 = compute_pre_intro_signature(full2)
    assert sig1 == sig2
    assert len(sig1) == 16


def test_no_leak_pre_intro():
    """Resolved pre-intro text must not contain {}, ---, id:, path: or placeholder/markdown artifacts."""
    from phoenix_v4.qa.validate_pre_intro import validate_pre_intro

    # Clean blocks -> valid
    clean = {
        "narrator_intro": "I am the narrator.",
        "book_title_line": "You are listening to Test Book.",
        "author_intro": "This book was written by Test Author.",
        "author_background": "Test Author is a writer.",
        "why_this_book": "This book exists.",
        "transition_line": "Chapter One.",
    }
    r = validate_pre_intro(clean, author_id="test_author")
    assert r.valid, r.errors

    # Leak patterns -> invalid
    for bad in ["{}", "---", "id: x", "path: /foo"]:
        blocks_bad = {**clean, "transition_line": clean["transition_line"] + " " + bad}
        r = validate_pre_intro(blocks_bad, author_id="test_author")
        assert not r.valid
        assert any("leak" in e.lower() or "internal" in e.lower() for e in r.errors)

    # Placeholder -> invalid
    blocks_ph = {**clean, "why_this_book": "Hello {{name}}."}
    r = validate_pre_intro(blocks_ph, author_id="test_author")
    assert not r.valid


def test_cap_duplicate_gate_intro():
    """When same pre_intro_signature would exceed 15% or is duplicate, check returns ok=False with candidates."""
    from phoenix_v4.planning.intro_ending_caps import (
        check_intro_cap_and_duplicate,
        check_ending_cap_and_duplicate,
        CapCheckResult,
    )

    brand_id = "test_brand"
    quarter = "2025-Q1"
    sig = "abc123def4567890"
    # 7 rows with same sig, 1 other -> 7/8 = 87.5% > 15%; adding one -> 8/9 still high
    index = [{"brand_id": brand_id, "quarter": quarter, "pre_intro_signature": sig}] * 7
    index += [{"brand_id": brand_id, "quarter": quarter, "pre_intro_signature": "other_sig"}]
    result = check_intro_cap_and_duplicate(brand_id, quarter, sig, index, cap_share=0.15)
    assert not result.ok
    assert result.error
    assert result.candidate_alternatives

    # Duplicate: same sig already in quarter
    result_dup = check_intro_cap_and_duplicate(brand_id, quarter, sig, index[:1], cap_share=0.15)
    assert not result_dup.ok
    assert "duplicate" in result_dup.error.lower() or result_dup.error

    # Ending: 20% cap
    end_sig = "ending1234567890"
    end_index = [{"brand_id": brand_id, "quarter": quarter, "ending_signature": end_sig}] * 5
    end_index += [{"brand_id": brand_id, "quarter": quarter, "ending_signature": "x"}] * 15
    result_end = check_ending_cap_and_duplicate(brand_id, quarter, end_sig, end_index, cap_share=0.20)
    assert not result_end.ok
    assert result_end.candidate_alternatives


def test_yaml_vs_runtime_title_conflict():
    """When YAML has fixed book_title_line and runtime supplies a different book_title, resolver raises ValueError."""
    from phoenix_v4.planning.pre_intro_resolver import resolve_pre_intro_blocks

    author_assets = {
        "pen_name": "Luna Hart",
        "audiobook_pre_intro": {
            "narrator_intro": "I am the narrator.",
            "book_title_line": "You are listening to The Old Title, written by Luna Hart.",
            "author_intro": "This book was written by Luna Hart.",
            "author_background": "Luna is a writer.",
            "why_this_book": "This book exists.",
            "transition_line": "Chapter One.",
        },
    }
    config_sot = REPO_ROOT / "config" / "source_of_truth"
    try:
        resolve_pre_intro_blocks(
            author_assets,
            "stillness_press",
            "topic|persona|seed",
            book_title="The New Title",
            pattern_bank_overrides_yaml=False,
            config_root=config_sot,
        )
        assert False, "Expected ValueError for title conflict"
    except ValueError as e:
        assert "conflict" in str(e).lower() or "differ" in str(e).lower()


def test_missing_bank_fallback_and_required_block_fail():
    """When pattern bank missing for block, use YAML. When both missing for required block, validation fails."""
    try:
        import yaml
    except ImportError:
        return
    from phoenix_v4.planning.pre_intro_resolver import resolve_pre_intro_blocks
    from phoenix_v4.qa.validate_pre_intro import validate_pre_intro

    # Brand with no bank (e.g. nonexistent) -> should fall back to YAML for all
    author_assets = {
        "pen_name": "Author",
        "audiobook_pre_intro": {
            "narrator_intro": "Narrator here.",
            "book_title_line": "Title.",
            "author_intro": "Written by Author.",
            "author_background": "Background.",
            "why_this_book": "Why.",
            "transition_line": "Chapter One.",
        },
    }
    config_sot = REPO_ROOT / "config" / "source_of_truth"
    blocks = resolve_pre_intro_blocks(
        author_assets,
        "nonexistent_brand_xyz",
        "seed1",
        pattern_bank_overrides_yaml=True,
        config_root=config_sot,
    )
    # Should have used YAML values (bank missing for brand)
    assert blocks.get("author_intro") == "Written by Author."
    assert blocks.get("transition_line") == "Chapter One."

    # Required block missing -> validation fails
    incomplete = {
        "book_title_line": "Title.",
        "author_intro": "Written by Author.",
        "author_background": "Background.",
        "why_this_book": "Why.",
        "transition_line": "Chapter One.",
    }
    r = validate_pre_intro(incomplete, author_id="test")
    assert not r.valid
    assert any("narrator_intro" in e for e in r.errors)
