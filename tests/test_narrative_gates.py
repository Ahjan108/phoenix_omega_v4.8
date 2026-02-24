"""
Narrative intelligence gates unit tests. Dev Spec §5.2.5.
Tests: mechanism escalation, cost gradient, callback integrity, identity shift, macro-cadence.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _plan_8ch_story_only(atom_ids: list[str]) -> dict:
    """Build plan with 8 chapters, 1 STORY slot per chapter (so 8 STORY atoms)."""
    ch_slots = [["STORY"] for _ in range(8)]
    return {
        "atom_ids": atom_ids,
        "chapter_slot_sequence": ch_slots,
        "dominant_band_sequence": [2, 3, 4, 4, 5, 4, 3, 2],
        "exercise_chapters": [],
        "emotional_curve": [2, 3, 4, 4, 5, 4, 3, 2],
        "persona_id": "test_persona",
        "topic_id": "test_topic",
    }


def test_mechanism_escalation_pass():
    """Properly escalating book passes gate."""
    from phoenix_v4.qa.mechanism_escalation_gate import validate_mechanism_escalation

    atom_ids = [f"test_persona_test_topic_eng_RECOGNITION_v{i:02d}" for i in range(1, 9)]
    plan = _plan_8ch_story_only(atom_ids)
    # Early ch 1-2 depth 1; mid 3-5 depth 2-3; late 6-8 depth 3,4,4 (one depth=4 in final third, no regression)
    metadata = {}
    for i, aid in enumerate(atom_ids):
        if i < 2:
            d = 1
        elif i < 5:
            d = 2 if i < 4 else 3
        else:
            d = 4 if i >= 6 else 3  # ch7 and ch8 both 4 so no late-stage decrease
        metadata[aid] = {"mechanism_depth": d, "band": plan["dominant_band_sequence"][i]}
    result = validate_mechanism_escalation(plan, metadata)
    assert result.valid, result.errors


def test_mechanism_escalation_flat_fail():
    """Flat-depth book fails with specific error."""
    from phoenix_v4.qa.mechanism_escalation_gate import validate_mechanism_escalation

    atom_ids = [f"test_persona_test_topic_eng_RECOGNITION_v{i:02d}" for i in range(1, 9)]
    plan = _plan_8ch_story_only(atom_ids)
    metadata = {aid: {"mechanism_depth": 1, "band": 2} for aid in atom_ids}
    result = validate_mechanism_escalation(plan, metadata)
    assert not result.valid
    assert any("mechanism_depth" in e for e in result.errors)


def test_cost_gradient_pass():
    """Escalating cost passes gate."""
    from phoenix_v4.qa.cost_gradient_gate import validate_cost_gradient

    atom_ids = [f"test_persona_test_topic_eng_RECOGNITION_v{i:02d}" for i in range(1, 9)]
    plan = _plan_8ch_story_only(atom_ids)
    # Cost rises to second half: ch 1-2 ~2, mid ~3, ch 5-6 ~4-5, then 3
    costs = [2, 2, 3, 3, 4, 5, 3, 3]
    metadata = {aid: {"cost_intensity": costs[i], "band": 2} for i, aid in enumerate(atom_ids)}
    result = validate_cost_gradient(plan, metadata)
    assert result.valid, result.errors


def test_cost_premature_peak_fail():
    """Peak cost before midpoint fails."""
    from phoenix_v4.qa.cost_gradient_gate import validate_cost_gradient

    atom_ids = [f"test_persona_test_topic_eng_RECOGNITION_v{i:02d}" for i in range(1, 9)]
    plan = _plan_8ch_story_only(atom_ids)
    # Highest cost at ch 1
    costs = [5, 2, 2, 2, 2, 2, 2, 2]
    metadata = {aid: {"cost_intensity": costs[i], "band": 2} for i, aid in enumerate(atom_ids)}
    result = validate_cost_gradient(plan, metadata)
    assert not result.valid
    assert any("midpoint" in e or "Peak" in e for e in result.errors)


def test_callback_integrity_pass():
    """All setups have returns."""
    from phoenix_v4.qa.callback_integrity_gate import validate_callback_integrity

    atom_ids = [f"test_persona_test_topic_eng_RECOGNITION_v{i:02d}" for i in range(1, 9)]
    plan = _plan_8ch_story_only(atom_ids)
    metadata = {}
    for i, aid in enumerate(atom_ids):
        m = {"callback_id": None, "callback_phase": None}
        if i == 1:
            m["callback_id"] = "thread_a"
            m["callback_phase"] = "setup"
        elif i == 5:
            m["callback_id"] = "thread_a"
            m["callback_phase"] = "return"
        metadata[aid] = m
    result = validate_callback_integrity(plan, metadata)
    assert result.valid, result.errors


def test_callback_orphaned_setup_fail():
    """Setup without return fails."""
    from phoenix_v4.qa.callback_integrity_gate import validate_callback_integrity

    atom_ids = [f"test_persona_test_topic_eng_RECOGNITION_v{i:02d}" for i in range(1, 9)]
    plan = _plan_8ch_story_only(atom_ids)
    metadata = {}
    for i, aid in enumerate(atom_ids):
        m = {"callback_id": None, "callback_phase": None}
        if i == 1:
            m["callback_id"] = "orphan"
            m["callback_phase"] = "setup"
        metadata[aid] = m
    result = validate_callback_integrity(plan, metadata)
    assert not result.valid
    assert any("orphan" in e or "setup" in e or "return" in e for e in result.errors)


def test_identity_monotonic_pass():
    """Non-decreasing identity stages pass."""
    from phoenix_v4.qa.identity_shift_gate import validate_identity_shift

    atom_ids = [f"test_persona_test_topic_eng_RECOGNITION_v{i:02d}" for i in range(1, 9)]
    plan = _plan_8ch_story_only(atom_ids)
    stages = ["pre_awareness", "pre_awareness", "destabilization", "destabilization", "experimentation", "experimentation", "self_claim", "self_claim"]
    metadata = {aid: {"identity_stage": stages[i]} for i, aid in enumerate(atom_ids)}
    result = validate_identity_shift(plan, metadata)
    assert result.valid, result.errors


def test_identity_regression_fail():
    """Regression (self_claim then pre_awareness) fails."""
    from phoenix_v4.qa.identity_shift_gate import validate_identity_shift

    atom_ids = [f"test_persona_test_topic_eng_RECOGNITION_v{i:02d}" for i in range(1, 9)]
    plan = _plan_8ch_story_only(atom_ids)
    stages = ["pre_awareness", "self_claim", "pre_awareness", "destabilization", "experimentation", "experimentation", "self_claim", "self_claim"]
    metadata = {aid: {"identity_stage": stages[i]} for i, aid in enumerate(atom_ids)}
    result = validate_identity_shift(plan, metadata)
    assert not result.valid
    assert any("regression" in e.lower() or "stage" in e for e in result.errors)


def test_macro_cadence_pass():
    """Varied intensity with regulation passes."""
    from phoenix_v4.qa.macro_cadence_gate import validate_macro_cadence

    plan = _plan_8ch_story_only([f"a_{i}" for i in range(8)])
    # Regulation (EXERCISE) at ch 2, 4, 6, 8 so every intensity 4/5 is within 2 ch of regulation
    plan["exercise_chapters"] = [1, 3, 5, 7]
    plan["dominant_band_sequence"] = [2, 3, 2, 4, 3, 4, 3, 2]  # no 3 consecutive 5s
    result = validate_macro_cadence(plan)
    assert result.valid, result.errors


def test_macro_cadence_burnout_fail():
    """3+ consecutive intensity=5 fails."""
    from phoenix_v4.qa.macro_cadence_gate import validate_macro_cadence

    plan = _plan_8ch_story_only([f"a_{i}" for i in range(8)])
    plan["emotional_curve"] = [5, 5, 5, 4, 3, 2, 2, 2]
    plan["dominant_band_sequence"] = [5, 5, 5, 4, 3, 2, 2, 2]
    result = validate_macro_cadence(plan)
    assert not result.valid
    assert any("consecutive" in e or "5" in e for e in result.errors)
