# Video pipeline scripts

Sequential stages per [docs/VIDEO_PIPELINE_SPEC.md](../../docs/VIDEO_PIPELINE_SPEC.md). Run against golden fixtures first.

## Order (implementation order)

1. **prepare_script_segments.py** — Render manifest → script_segments (timing via WPM; optional metadata).
2. **run_shot_planner.py** — Script segments → ShotPlan (visual_intent, duration_s, thumbnail_candidate, prompt_bundle).
3. **run_asset_resolver.py** — ShotPlan + optional Image Bank → resolved asset_id per shot.
4. **run_timeline_builder.py** — ShotPlan + resolved_assets → Timeline JSON (per aspect).
5. **run_caption_adapter.py** — Timeline + script_segments → captions (reflow/truncate per caption_policies).
6. **run_qc.py** — Validates shot_plan, resolved_assets, timeline (no consecutive same asset; duration/resolution).
7. **write_provenance.py** — Writes video_provenance.json (telemetry: hook_type, environment, etc.).
8. **write_metadata.py** — Writes distribution_manifest.json with telemetry and primary_asset_ids.
9. **run_render.py** — Stub: timeline → placeholder video path (FFmpeg/Remotion later).

## Run full pipeline

```bash
python3 scripts/video/run_pipeline.py --plan-id plan-therapeutic-001
```

Outputs under `artifacts/video/<plan_id>/` and `artifacts/video/provenance/`.

## Run single stage

```bash
python3 scripts/video/prepare_script_segments.py fixtures/video_pipeline/render_manifest.json -o artifacts/video/plan-therapeutic-001/script_segments.json
python3 scripts/video/run_shot_planner.py artifacts/video/plan-therapeutic-001/script_segments.json -o artifacts/video/plan-therapeutic-001/shot_plan.json
# ... etc
```

Config is loaded from `config/video/*.yaml` (pacing, caption_policies, asset_selection_priority, aspect_ratio_presets, etc.).
