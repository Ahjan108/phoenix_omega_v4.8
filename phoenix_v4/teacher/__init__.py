"""
Teacher Mode: strict resolution, coverage gate, TDEL, and governance.
Authority: specs/TEACHER_MODE_MASTER_SPEC.md, plan teacher_mode_strict_and_fallback.
"""
from phoenix_v4.teacher.coverage_gate import (
    TeacherCoverageError,
    compute_required_slots,
    compute_available_teacher_atoms,
    compute_story_band_inventory,
    make_gap_report,
    run_coverage_gate,
)

__all__ = [
    "TeacherCoverageError",
    "compute_required_slots",
    "compute_available_teacher_atoms",
    "compute_story_band_inventory",
    "make_gap_report",
    "run_coverage_gate",
]
