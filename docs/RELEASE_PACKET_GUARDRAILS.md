# Release packet guardrails

**Authority:** Weekly brand packet flow; export, upload, notify, portal.

## 1. Schema split

- **JSON artifacts:** [schemas/release/brand_packet_manifest_v1.schema.json](../schemas/release/brand_packet_manifest_v1.schema.json) — advisory_report.json structure only.
- **CSV contract:** [schemas/release/upload_manifest_csv_v1.schema.json](../schemas/release/upload_manifest_csv_v1.schema.json) — required headers and row shape after CSV→JSON transform for `upload_manifest.csv`.

## 2. ISO week consistency

- **YYYY-WW** is derived from `week_start` **after normalizing to Monday** (scripts/release/week_utils.py) to avoid timezone/week-boundary drift.
- All scripts that use week_start (export, upload, notify, sync) use this helper.

## 3. Required rendered output

- **Strict feasibility:** Each scheduled plan must have **required rendered output** present.
- **Path rule:**  
  - Default: `artifacts/rendered/<plan_id>/book.txt`  
  - Wave: `artifacts/waves/<wave_id>/rendered/<plan_id>/book.txt` (or `.../rendered/<plan_stem>/book.txt`).
- Constant in export script: `REQUIRED_RENDERED_FILE = "book.txt"`. Missing file → strict mode fails whole week.

## 4. Partial brand handling

- **Strict mode (default):** Any missing plan file or required rendered file fails the **whole week**; no partial export.
- **Permissive (--no-strict):** Skip broken brand/plan and continue; use only when explicitly needed.

## 5. Notification and report idempotency

- **run_id** (UUID) and **week_key** (YYYY-WW) are written into:
  - `notify_failures.json` — top-level `run_id`, `week_key`, and `failures[]`.
  - `packet_delivery_report.json` — top-level `run_id`, `week`; notify section includes `run_id`, `week_key`.
- Reruns are traceable by run_id and week_key.

## 6. Workflow: schedule source validation

- **Pre-step:** Before export, the workflow **validates that the schedule was built with `--candidates-dir` or `--wave`** (generate_weekly_schedule.py writes `schedule_source` and `candidates_dir`/`wave` into release_schedule.json).
- If `schedule_source` is missing or not `candidates_dir`/`wave`, the workflow fails with an actionable error so the pipeline is not run without a proper upstream schedule.
