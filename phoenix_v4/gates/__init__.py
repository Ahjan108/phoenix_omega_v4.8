# Phoenix V4 — Hard entry gates (run before Stage 1) and post-compile quality gate.
# Tuple viability preflight: fail early, fail deterministically.
# Creative Quality v1: post-compile, read-only, deterministic heuristics.

from phoenix_v4.gates.check_tuple_viability import check_tuple_viability
from phoenix_v4.gates.check_creative_quality_v1 import (
    evaluate_book,
    load_book,
    BookQualitySummary,
)

__all__ = [
    "check_tuple_viability",
    "evaluate_book",
    "load_book",
    "BookQualitySummary",
]
