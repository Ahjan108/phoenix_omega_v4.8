# Phoenix V4 — Hard entry gates

Run **before** Stage 1. No override.

## Tuple viability preflight

```bash
# From repo root (PYTHONPATH required when run as script)
PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py \
  --persona first_responders \
  --topic anxiety \
  --engine watcher \
  --format F006
```

- **Pass:** prints `TUPLE_VIABLE`, exit 0.
- **Fail:** prints error codes (e.g. `NO_BINDING`, `NO_ARC`, `POOL_TOO_SHALLOW`, `BAND_DEFICIT`), exit 1. Use `--json` for machine-readable output.

Config: `config/gates.yaml` → `tuple_viability.min_story_pool_size`, `min_teacher_exercise_pool`. Brand emotional range: `config/catalog_planning/brand_emotional_range.yaml` (Phase 5); use `--brand phoenix` to enforce arc bands within brand range.

Pipeline: `run_pipeline.py` calls this gate automatically before Stage 1 (with `brand_id`); on fail it aborts.
