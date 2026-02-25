# Pre-Publish Checklist (Blocking)

Use one command only:

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
5. `update_similarity_index.py` (append only after all above pass)

Rationale: no state mutation until all blocking checks pass; index update is the only mutating step. All gates 1–4 are always run for full diagnostics (no short-circuit on first failure).

## Blocking rules
- Any non-zero exit from gates 1-4 blocks publish.
- Similarity index is not updated unless gates 1-4 pass.
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
- **Release automation must call** `scripts/ci/run_prepublish_gates.py` or `scripts/release/prepare_wave_for_export.py` before any export to storefronts.
- **Do not export** when the command exits non-zero. The only path to "approved for export" is through this prepublish pass.

