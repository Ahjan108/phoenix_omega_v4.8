from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "fixtures" / "video_pipeline_15_segment_demo" / "render_manifest.json"
OUT_DIR = REPO_ROOT / "artifacts" / "video" / "overthinking-genz-nyc-15seg-planning"


def test_fixture_has_15_plus_segments() -> None:
    assert FIXTURE.exists(), f"Missing fixture: {FIXTURE}"
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert len(data.get("segments", [])) >= 15


def test_15_segment_planning_hook_and_rhythm() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    script_segments = OUT_DIR / "script_segments.json"
    shot_plan = OUT_DIR / "shot_plan.json"

    r1 = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "video" / "prepare_script_segments.py"),
            str(FIXTURE),
            "-o",
            str(script_segments),
            "--content-type",
            "long_form",
            "--force",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r1.returncode == 0, r1.stderr

    r2 = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "video" / "run_shot_planner.py"),
            str(script_segments),
            "-o",
            str(shot_plan),
            "--content-type",
            "long_form",
            "--force",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r2.returncode == 0, r2.stderr

    segs = json.loads(script_segments.read_text(encoding="utf-8")).get("segments", [])
    shots = json.loads(shot_plan.read_text(encoding="utf-8")).get("shots", [])
    assert len(segs) >= 15
    assert len(shots) == len(segs)

    # Hook assignment check: first shot should be hook visual intent.
    assert shots[0].get("visual_intent") == "HOOK_VISUAL"

    # Visual rhythm check: max 3 consecutive same visual_intent.
    max_run = 1
    run = 1
    prev = shots[0].get("visual_intent")
    for s in shots[1:]:
        cur = s.get("visual_intent")
        if cur == prev:
            run += 1
            max_run = max(max_run, run)
        else:
            prev = cur
            run = 1
    assert max_run <= 3, f"visual rhythm violation: max consecutive same intent = {max_run}"
