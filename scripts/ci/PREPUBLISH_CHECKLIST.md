# Pre-Publish Checklist (Blocking)

## Wave path contract (deterministic)

Any script that produces a wave for export **must** write to this layout so `prepare_wave_for_export` can resolve paths by `--wave-id`:

- **Plans:** `artifacts/waves/<wave_id>/plans/` (compiled plan `.json` files)
- **Rendered prose:** `artifacts/waves/<wave_id>/rendered/` (rendered `.txt` for the same wave)

Then `prepare_wave_for_export --wave-id <wave_id>` resolves plans-dir and wave-rendered-dir from these paths. Do not add alternate wave layouts for export.

---

Use one command only (prefer release layer):

```bash
python scripts/ci/run_prepublish_gates.py \
  --plans-dir artifacts/waves/<wave_id>/plans \
  --index artifacts/catalog_similarity/index.jsonl \
  --wave-rendered-dir artifacts/waves/<wave_id>/rendered \
  --catalog-rendered-dir artifacts/catalog_rendered \
  --report artifacts/ops/prepublish_<wave_id>.json
```

## Gate Order (fixed)
1. `check_structural_entropy.py` (per plan)
2. `check_platform_similarity.py` (per plan, against existing index)
3. `check_prose_duplication.py` (wave rendered vs catalog rendered)
4. `check_wave_density.py` (wave-wide)
4b. **Series diversity** (P0): `validate_series_diversity` — hard fail on adjacent same (primary_mechanism_id + journey_shape_id) or same band_curve_id; soft warn on combo density. Fail on hard violations; pass with warnings on soft only.
5. `update_similarity_index.py` (append only after all above pass)

Rationale: no state mutation until all blocking checks pass; index update is the only mutating step. All gates 1–4 and 4b are always run for full diagnostics (no short-circuit on first failure).

## Blocking rules
- Any non-zero exit from gates 1–4 or 4b (series diversity hard violations) blocks publish.
- Similarity index is not updated unless gates 1–4 and 4b pass.
- If `--fail-on-similarity-warn` is used, CTSS review warnings are blocking.

## Required inputs
- `artifacts/waves/<wave_id>/plans/*.json` (compiled plans)
- `artifacts/waves/<wave_id>/rendered/*.txt` (rendered prose for the same wave)
- `artifacts/catalog_similarity/index.jsonl` (can be empty/missing for first run)
- `artifacts/catalog_rendered/*.txt` (recommended for prose dup check vs full catalog)

## Optional controls
- `--book-spec-dir <dir>`: pass matching `BookSpec` JSON to structural entropy checks.
- `--dry-run-index-update`: run all gates without mutating similarity index.
- `--fail-ngram-jaccard` / `--warn-ngram-jaccard`: tune prose overlap thresholds.

## Release decision
- Publish only when command exits `0`.
- Archive the JSON report in release artifacts for auditability.

## Release automation
- **The only path to export is via `scripts/release/` entrypoints.** Call `scripts/release/prepare_wave_for_export.py` (or the single export script that calls it) before any export to storefronts. Do not add alternate upload paths that skip gates. Automation must call release-layer scripts only, not `scripts/ci/run_prepublish_gates.py` directly for export.
- **Do not export** when the command exits non-zero. The only path to "approved for export" is through this prepublish pass.

