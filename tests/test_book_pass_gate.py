from __future__ import annotations

from phoenix_v4.qa.book_pass_gate import validate_book_pass


def _build_plan_and_maps(repetitive_claims: bool) -> tuple[dict, dict, dict]:
    chapter_slot_sequence = [
        ["STORY", "REFLECTION", "INTEGRATION"],
        ["STORY", "REFLECTION", "EXERCISE", "INTEGRATION"],
        ["STORY", "REFLECTION", "INTEGRATION"],
        ["STORY", "REFLECTION", "INTEGRATION"],
        ["STORY", "REFLECTION", "EXERCISE", "INTEGRATION"],
        ["STORY", "REFLECTION", "EXERCISE", "INTEGRATION"],
    ]
    atom_ids: list[str] = []
    prose_map: dict[str, str] = {}
    atom_meta: dict[str, dict] = {}

    story_meta = [
        ("pre_awareness", 1, 2),
        ("destabilization", 2, 2),
        ("experimentation", 2, 3),
        ("experimentation", 3, 4),
        ("self_claim", 4, 4),
        ("self_claim", 4, 4),
    ]

    varied_claims = [
        "The point is your alarm is active before language catches up.",
        "Here is what is happening: prediction loops amplify uncertainty.",
        "What this means is the mechanism adds false urgency to uncertainty.",
        "This is not failure; it is pattern recognition under stress and cost prediction.",
        "Which means you can choose a smaller entry and keep moving.",
        "The point is not zero fear but steady forward agency.",
    ]

    for ch in range(6):
        s_id = f"s{ch+1}"
        r_id = f"r{ch+1}"
        i_id = f"i{ch+1}"
        atom_ids.append(s_id)
        atom_ids.append(r_id)
        if "EXERCISE" in chapter_slot_sequence[ch]:
            x_id = f"x{ch+1}"
            atom_ids.append(x_id)
            prose_map[x_id] = "Practice this now. Exhale once and choose one small next step."
        atom_ids.append(i_id)

        stage, depth, cost = story_meta[ch]
        atom_meta[s_id] = {
            "identity_stage": stage,
            "mechanism_depth": depth,
            "cost_intensity": cost,
        }
        prose_map[s_id] = f"Story chapter {ch+1}. Concrete scene with stakes."
        claim = "The point is anxiety predicts threat everywhere." if repetitive_claims else varied_claims[ch]
        prose_map[r_id] = claim + " This chapter gives one clear frame."

        if ch == 5:
            prose_map[i_id] = (
                "This is not about eliminating alarm but building choice under load. "
                "From now on, choose one next step and practice it daily."
            )
        else:
            prose_map[i_id] = "Integration line that lands the chapter and keeps continuity."

    plan = {
        "chapter_slot_sequence": chapter_slot_sequence,
        "atom_ids": atom_ids,
        "dominant_band_sequence": [2, 2, 3, 4, 4, 4],
        "emotional_curve": [2, 3, 4, 5, 4, 3],
        "exercise_chapters": [1, 4, 5],
    }
    return plan, atom_meta, prose_map


def test_book_pass_gate_fails_repetitive_claims() -> None:
    plan, atom_meta, prose_map = _build_plan_and_maps(repetitive_claims=True)
    res = validate_book_pass(plan, atom_meta, prose_map=prose_map)
    assert res.valid is False
    assert any("repetitive chapter claims" in e for e in res.errors)


def test_book_pass_gate_passes_varied_progressive_book() -> None:
    plan, atom_meta, prose_map = _build_plan_and_maps(repetitive_claims=False)
    res = validate_book_pass(plan, atom_meta, prose_map=prose_map)
    assert res.valid is True, res.errors
    assert res.metrics["claim_coverage"] >= 0.8
