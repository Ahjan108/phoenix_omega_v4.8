# Partner video pickup runbook

**Purpose:** One-page runbook for the partner who picks up daily video batches from R2 and ingests them into Metricool (or another publishing tool).  
**Authority:** [docs/VIDEO_PIPELINE_SPEC.md](./VIDEO_PIPELINE_SPEC.md) §10–11, [docs/VIDEO_PIPELINE_STORAGE_LAYOUT.md](./VIDEO_PIPELINE_STORAGE_LAYOUT.md).

---

## 1. Download daily_batch.json

- **Where:** R2 bucket, key `<YYYY-MM-DD>/daily_batch.json` (e.g. `2026-03-08/daily_batch.json`).
- **How:** Use S3-compatible API (Cloudflare R2 endpoint), presigned URL, or the Metricool integration if it reads from R2.
- **Do not** list or scan the bucket; the batch file is the only entry point. All video paths are inside it.

---

## 2. Pull videos from R2

- For each entry in `daily_batch.long_form` and `daily_batch.shorts`, use the `r2_prefix` (e.g. `2026-03-08/long/video-001/`) to fetch:
  - `video.mp4`
  - `thumb.jpg` (optional; may be missing)
  - `distribution_manifest.json`
- Use the `distribution_manifest_key` from the batch entry if you need the exact object key for the manifest.

---

## 3. Upload to Metricool

- Ingest each video (and thumbnail, title, description from the distribution manifest) into your Metricool queue or calendar.
- Map `video_id`, `title`, `description`, `tags` from `distribution_manifest.json` as required by your publishing workflow.

---

## 4. Write batch_acknowledged.json

- **When:** After you have finished processing the batch (all ingest attempts done).
- **Where:** Same R2 bucket, key `<YYYY-MM-DD>/batch_acknowledged.json`.
- **Schema:** [schemas/video/batch_acknowledged_v1.schema.json](../schemas/video/batch_acknowledged_v1.schema.json).

**Required fields:**

- `batch_date`: same as the date in the batch (YYYY-MM-DD).
- `acknowledged_at`: ISO 8601 timestamp (e.g. `2026-03-08T14:30:00Z`).
- `failed_count`: number of videos that failed to ingest (0 = all succeeded).
- `failed_ids`: (optional) array of `video_id` values that failed, so the pipeline owner can retry or alert.

**Critical:** The pipeline **wipe script** deletes staging (and optionally R2 date prefix) only when this file exists and `failed_count == 0`. If you do not write the ack file, data is never wiped and the pipeline will not treat the batch as complete.

---

## 5. Error cases and retry

- **Partial ingest:** Set `failed_count` to the number of failures and list `failed_ids`. Do not set `failed_count == 0` until all videos are successfully ingested.
- **R2 unreachable:** Retry with backoff; document in your runbook. If the batch is never picked up, the pipeline keeps the data; no automatic wipe.
- **Metricool API errors:** Same as partial ingest: ack with `failed_count` and `failed_ids` so the pipeline owner can see what to retry.

---

## 6. Contact

- For pipeline or R2 issues: [document owner or support channel].
- For Metricool or publishing issues: [document Metricool support or internal owner].
