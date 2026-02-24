"""
Stage 2 Format Selector tests.
Determinism: same input -> same FormatPlan.
Persona constraints and installment strategy from config/format_selection/.
"""
import json
import os
import sys
from pathlib import Path

# Run from repo root so config and phoenix_v4 are on path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

from phoenix_v4.planning.format_selector import FormatSelector, FormatPlan, inputs_digest


def test_determinism():
    sel = FormatSelector()
    plan1 = sel.select_format("relationship_anxiety", "nyc_exec", 1, None)
    plan2 = sel.select_format("relationship_anxiety", "nyc_exec", 1, None)
    assert plan1.format_structural_id == plan2.format_structural_id
    assert plan1.format_runtime_id == plan2.format_runtime_id
    assert plan1.chapter_count == plan2.chapter_count
    assert plan1.rationale["inputs_digest"] == plan2.rationale["inputs_digest"]


def test_persona_constraint_gen_z_forbidden_f003():
    sel = FormatSelector()
    # gen_z forbids F001, F003. High-complexity opener would be F003 -> must fallback to another A-tier
    plan = sel.select_format("relationship_anxiety", "gen_z", 1, None)
    assert plan.format_structural_id != "F003"
    assert plan.format_structural_id != "F001"
    assert plan.format_runtime_id == "short_book_30"  # gen_z preferred_runtime


def test_installment_opener_vs_deepening():
    sel = FormatSelector()
    opener = sel.select_format("relationship_anxiety", "nyc_exec", 1, None)
    deepening = sel.select_format("relationship_anxiety", "nyc_exec", 2, None)
    assert opener.format_structural_id == "F003"  # opener high_complexity
    assert deepening.format_structural_id == "F006"  # deepening high_complexity


def test_plan_contract_fields():
    sel = FormatSelector()
    plan = sel.select_format("false_alarm", "healthcare_worker", 1, None)
    assert plan.format_structural_id.startswith("F") and len(plan.format_structural_id) == 4
    assert plan.tier in ("A", "B", "C")
    assert plan.blueprint_variant in ("linear", "wave", "scaffold", "rupture")
    assert isinstance(plan.chapter_count, int) and plan.chapter_count >= 1
    assert len(plan.word_target_range) == 2 and plan.word_target_range[0] <= plan.word_target_range[1]
    assert plan.rationale is not None and "inputs_digest" in plan.rationale


def test_to_compiler_input():
    sel = FormatSelector()
    plan = sel.select_format("overwhelm", "nyc_exec", 1, None)
    out = plan.to_compiler_input()
    assert out["format_structural_id"] == plan.format_structural_id
    assert out["target_chapter_count"] == plan.chapter_count
    assert out["word_target_range"] == list(plan.word_target_range)


if __name__ == "__main__":
    test_determinism()
    test_persona_constraint_gen_z_forbidden_f003()
    test_installment_opener_vs_deepening()
    test_plan_contract_fields()
    test_to_compiler_input()
    print("All format_selector tests passed.")
