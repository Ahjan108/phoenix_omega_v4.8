# Video pipeline: test, review, and fix plan

**Purpose:** Regression (golden fixture), real-content integration (15+ segments), and teacher-mode alignment. When 100%, run manual review and then implement renderer.

---

## 1. Regression test (golden fixture)

**Goal:** Any change to pipeline or config must not break the golden path.

**Steps:**

1. Run full pipeline against fixtures:
   ```bash
   python3 scripts/video/run_pipeline.py --plan-id plan-therapeutic-001 --force
   ```
2. Assert all stages succeed and outputs exist under `artifacts/video/plan-therapeutic-001/`.
3. (Optional) Snapshot key fields of `shot_plan.json`, `timeline.json`, `distribution_manifest.json` and assert in CI (e.g. pytest) so regressions are caught.

**Pass criteria:** Pipeline completes; script_segments, shot_plan, resolved_assets, timeline, captions, qc_summary, provenance, distribution_manifest all present and valid.

---

## 2. Real-content integration test (15+ segments)

**Goal:** Prove the pipeline on a real rendered book chapter, not the 2-segment fixture.

**Steps:**

1. **Produce a render manifest** for a real chapter from the content engine (15+ segments). If Stage 6 does not yet emit render_manifest, build it once by hand or via a one-off script from an existing plan + book.txt (segment boundaries + atom_id from plan).
2. Run pipeline with that manifest:
   ```bash
   python3 scripts/video/prepare_script_segments.py <path_to_render_manifest.json> -o artifacts/video/<plan_id>/script_segments.json
   python3 scripts/video/run_shot_planner.py artifacts/video/<plan_id>/script_segments.json -o artifacts/video/<plan_id>/shot_plan.json
   # ... through to metadata
   ```
   Or point `run_pipeline.py` at a directory that contains the real render_manifest (e.g. `--fixtures-dir` or a plan-specific manifest path when supported).
3. **Manual review** of `shot_plan.json`:
   - Do visual intents match the content (hook vs body vs closing)?
   - Is the hook assigned correctly for the first segment?
   - Are there **3+ consecutive shots with the same visual_intent**? (visual rhythm violation; fix in shot planner or config.)
   - Are durations and pacing sane given `pacing_by_content_type`?
4. Fix any bugs in shot planner, config, or fixtures; re-run until review passes.

**Pass criteria:** Pipeline runs on 15+ segment input; manual review finds no hook or rhythm violations; durations and intents look sensible.

---

## 3. Teacher mode alignment

**Goal:** Ensure video pipeline artifacts and terminology align with teacher mode / authoring where they share concepts (e.g. arc_role, segments, personas).

**Steps:**

1. List shared concepts: arc_role, segment boundaries, persona/topic/location, emotional_band.
2. Confirm script_segments and shot_plan use the same vocabulary as teacher mode specs (e.g. [TEACHER_MODE_AUTHORING_PLAYBOOK.md](../specs/TEACHER_MODE_AUTHORING_PLAYBOOK.md)).
3. If render manifest or plan format is produced by the same content engine that feeds teacher mode, ensure segment_id / slot_id / atom_id are consistent so one source of truth applies.
4. Document any assumptions (e.g. “hook” = first segment, arc_role from metadata) in VIDEO_PIPELINE_SPEC or this doc.

**Pass criteria:** No conflicting definitions; pipeline and teacher mode docs reference the same concepts where relevant.

---

## 4. Fix plan (when issues are found)

| Finding | Where to fix |
|--------|----------------|
| Hook wrong for first segment | hook_selection_rules.yaml or run_shot_planner.py (arc_role / topic mapping) |
| 3+ consecutive same visual_intent | run_shot_planner.py: add rhythm rule (max N same intent in a row); or motion_policy / visual_intent_defaults |
| Duration out of range | pacing_by_content_type.yaml or script preparer WPM/timing |
| Consecutive same asset_id | run_asset_resolver.py or image bank diversity; QC already flags |
| Config hash mismatch after config change | Expected: stages rebuild when config changes (should_skip_output compares config_hash) |

---

## 5. After 100%: next steps

- **Implement renderer** (FFmpeg) against the same real plan; output to `staging/<date>/<video_id>/`.
- **Throughput check:** Render 10 shorts, measure average render time; measure upload time if applicable (see VIDEO_PIPELINE_SPEC / architecture notes).
- **Cleanup pass (after first real video):** pipeline_version in artifacts, input artifact refs in outputs, placeholder asset naming (e.g. placeholder_env_forest_001), pipeline_log.json timing, QC expansion (caption overflow, max same visual_intent in a row). See `docs/VIDEO_PIPELINE_POST_FIRST_VIDEO_BACKLOG.md`.
