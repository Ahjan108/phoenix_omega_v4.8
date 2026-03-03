"""
E2E Teacher Mode compile smoke tests: one topic/persona/arc per teacher.
Runs run_pipeline with --teacher <id> --teacher-mode; expects compile to complete
and plan to contain no placeholders and no missing-atom warnings when teacher has
full F006 slot coverage (HOOK, SCENE, STORY, REFLECTION, COMPRESSION, EXERCISE, INTEGRATION).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# One arc per (topic, persona) that matches most teachers' allowed_topics/engines
# gen_z_professionals__burnout__overwhelm__F006: 20 ch, persona gen_z_professionals, topic burnout
ARC_PATH = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "gen_z_professionals__burnout__overwhelm__F006.yaml"


def _teacher_ids():
    import yaml
    reg = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    return list((data.get("teachers") or {}).keys())


def _has_f006_coverage(teacher_id: str, min_per_slot: int = 20) -> bool:
    """True if teacher has at least min_per_slot of each F006 slot."""
    banks = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "approved_atoms"
    if not banks.exists():
        return False
    slots = ["HOOK", "SCENE", "STORY", "REFLECTION", "COMPRESSION", "EXERCISE", "INTEGRATION"]
    for slot in slots:
        d = banks / slot
        n = sum(1 for f in d.glob("*.yaml")) if d.exists() else 0
        if n < min_per_slot:
            return False
    return True


@pytest.mark.slow
@pytest.mark.parametrize("teacher_id", _teacher_ids())
def test_teacher_mode_compile_smoke(teacher_id: str, tmp_path: Path):
    """Run pipeline for one arc per teacher; expect success when teacher has F006 coverage."""
    if not ARC_PATH.exists():
        pytest.skip(f"Arc not found: {ARC_PATH}")
    out_plan = tmp_path / "plan.json"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_pipeline.py"),
        "--topic", "burnout",
        "--persona", "gen_z_professionals",
        "--arc", str(ARC_PATH),
        "--teacher", teacher_id,
        "--out", str(out_plan),
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
    if not _has_f006_coverage(teacher_id):
        # Expect coverage gate or compile failure when slots missing
        if result.returncode != 0:
            assert "coverage" in result.stderr.lower() or "TeacherCoverageError" in result.stderr or "insufficient" in result.stderr.lower()
        return
    assert result.returncode == 0, f"Pipeline failed for {teacher_id}: {result.stderr}"
    assert out_plan.exists()
    plan = json.loads(out_plan.read_text())
    assert plan.get("teacher_mode") is True
    assert plan.get("teacher_id") == teacher_id
    atom_ids = plan.get("atom_ids") or []
    placeholders = [a for a in atom_ids if "placeholder" in a or "silence:" in a]
    assert len(placeholders) == 0, f"Teacher {teacher_id} plan has placeholders: {placeholders[:5]}"
    # No missing-atom warnings in output
    assert "Missing:" not in result.stdout and "Missing:" not in result.stderr
