from __future__ import annotations

from phoenix_v4.quality.chapter_flow_gate import evaluate_chapter_flow
from scripts.build_proof_chapter import build_chapter


def test_chapter_flow_gate_fails_on_artifacts_and_repetition() -> None:
    bad = """
I have noticed that this keeps happening.
I have noticed that this keeps happening.
---
[family: F4 voice_mode: guide mechanism_emphasis: automatic]
The room is quiet. {street_name} is below.
"""
    result = evaluate_chapter_flow(bad)
    assert result.status == "FAIL"
    assert "DELIVERY_ARTIFACT_PRESENT" in result.errors
    assert any(e.startswith("REPETITIVE_STEM:") for e in result.errors)


def test_proof_chapter_passes_flow_gate() -> None:
    chapter = build_chapter("test-seed-01")
    result = evaluate_chapter_flow(chapter)
    assert result.status == "PASS", result.errors
    assert result.score >= 80
    assert result.metrics["transition_hits"] >= 3
    assert result.metrics["thesis_hits"] >= 1
