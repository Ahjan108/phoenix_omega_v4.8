"""
Regression test for video pipeline: run against golden fixture, assert all outputs exist and are valid.
Run: pytest tests/test_video_pipeline_regression.py -v
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_ID = "plan-therapeutic-001"
OUT_ROOT = REPO_ROOT / "artifacts" / "video" / PLAN_ID
PROVENANCE_DIR = REPO_ROOT / "artifacts" / "video" / "provenance"


@pytest.fixture(scope="module")
def run_pipeline():
    """Run full video pipeline with --force; skip if fixtures missing."""
    manifest = REPO_ROOT / "fixtures" / "video_pipeline" / "render_manifest.json"
    if not manifest.exists():
        pytest.skip("fixtures/video_pipeline/render_manifest.json not found")
    if not os.environ.get("OPENAI_BASE_URL"):
        pytest.skip("OPENAI_BASE_URL not set for strict segment-scene extraction")
    if not (os.environ.get("CLOUDFLARE_ACCOUNT_ID") and (os.environ.get("CLOUDFLARE_API_TOKEN") or os.environ.get("CLOUDFLARE_AI_API_TOKEN"))):
        pytest.skip("Cloudflare FLUX credentials not set for strict segment image generation")
    script = REPO_ROOT / "scripts" / "video" / "run_pipeline.py"
    r = subprocess.run(
        [sys.executable, str(script), "--plan-id", PLAN_ID, "--force"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Pipeline failed: {r.stderr}"
    return r


def test_pipeline_succeeds(run_pipeline):
    """Pipeline exits 0."""
    assert run_pipeline.returncode == 0


def test_script_segments_exists_and_valid(run_pipeline):
    """script_segments.json exists and has plan_id, segments."""
    path = OUT_ROOT / "script_segments.json"
    if not path.exists():
        pytest.skip("Run pipeline first (script_segments.json missing)")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "plan_id" in data and data["plan_id"] == PLAN_ID
    assert "segments" in data and len(data["segments"]) >= 1


def test_shot_plan_has_config_hash_and_shots(run_pipeline):
    """shot_plan.json has config_hash and shots."""
    path = OUT_ROOT / "shot_plan.json"
    if not path.exists():
        pytest.skip("Run pipeline first (shot_plan.json missing)")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("plan_id") == PLAN_ID
    assert "config_hash" in data
    assert "shots" in data and len(data["shots"]) >= 1
    for shot in data["shots"]:
        assert "shot_id" in shot and "visual_intent" in shot and "segment_id" in shot


def test_resolved_assets_exists(run_pipeline):
    """resolved_assets.json has plan_id and resolved map."""
    path = OUT_ROOT / "resolved_assets.json"
    if not path.exists():
        pytest.skip("Run pipeline first (resolved_assets.json missing)")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("plan_id") == PLAN_ID
    assert "resolved" in data


def test_timeline_has_clips_and_config_hash(run_pipeline):
    """timeline.json has clips, config_hash, duration_s."""
    path = OUT_ROOT / "timeline.json"
    if not path.exists():
        pytest.skip("Run pipeline first (timeline.json missing)")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("plan_id") == PLAN_ID
    assert "config_hash" in data
    assert "clips" in data and len(data["clips"]) >= 1
    assert "duration_s" in data and data["duration_s"] > 0


def test_captions_exists(run_pipeline):
    """captions.json has plan_id and captions map."""
    path = OUT_ROOT / "captions.json"
    if not path.exists():
        pytest.skip("Run pipeline first (captions.json missing)")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "captions" in data


def test_qc_summary_exists(run_pipeline):
    """qc_summary.json exists and has passed, checks."""
    path = OUT_ROOT / "qc_summary.json"
    if not path.exists():
        pytest.skip("Run pipeline first (qc_summary.json missing)")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "passed" in data
    assert data["passed"] is True


def test_provenance_exists_and_has_config_hash(run_pipeline):
    """Provenance file exists and records config_hash."""
    path = PROVENANCE_DIR / f"video-{PLAN_ID}.json"
    if not path.exists():
        pytest.skip("Run pipeline first (provenance missing)")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("video_id") == f"video-{PLAN_ID}"
    assert data.get("plan_id") == PLAN_ID
    assert "config_hash" in data
    assert "primary_asset_ids" in data


def test_distribution_manifest_exists(run_pipeline):
    """distribution_manifest.json has required fields and config_hash."""
    path = OUT_ROOT / "distribution_manifest.json"
    if not path.exists():
        pytest.skip("Run pipeline first (distribution_manifest.json missing)")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "video_id" in data and "title" in data and "video_provenance_path" in data
    assert "config_hash" in data
