# Video documentation completeness
_Exported on 3/8/2026 at 12:26:31 HST from Cursor (2.5.25)_

---

**User**

read @docs/DOCS_INDEX.md @docs/VIDEO_PIPELINE_SPEC.md are we 100% with video in https://github.com/Ahjan108/Qwen-Agent 

---

**Cursor**


Searching DOCS_INDEX for video sections and checking how this repo relates to Qwen-Agent.



Checking whether the video pipeline lives in phoenix_omega or Qwen-Agent:



Here’s the concise answer.

---

## Are we 100% with video in Ahjan108/Qwen-Agent?

**No.** The video pipeline is **not** in [Ahjan108/Qwen-Agent](https://github.com/Ahjan108/Qwen-Agent). It lives entirely in **phoenix_omega** (this repo).

### Where video actually is

| What | Location |
|------|----------|
| **Video pipeline** | **phoenix_omega only** — `scripts/video/`, `config/video/`, `schemas/video/`, `artifacts/video/`, `docs/VIDEO_*.md` |
| **Qwen-Agent** | **No video** — grep for "video"/"Video" under `Qwen-Agent/` returns no matches |

So per your docs:

- **VIDEO_PIPELINE_SPEC.md** and **DOCS_INDEX.md** § Video pipeline describe a pipeline that is implemented and specified in **phoenix_omega** (schemas, config, scripts, storage layout, FFmpeg, FLUX, etc.).
- **Ahjan108/Qwen-Agent** is used for **Pearl News** (scheduled + manual expand), **audiobook**, **localization**, and **LM Studio lock** — not for video.

### Summary

- **Video:** 100% in **phoenix_omega** (and thus in **Ahjan108/phoenix_omega_v4.8** if that’s the same codebase).
- **Qwen-Agent:** 0% video; it’s the Pearl News/audiobook/localization/runner repo.

If the goal is “100% with video in Qwen-Agent,” you’d need to either add the video pipeline (or a runner that calls back to phoenix_omega) inside Qwen-Agent, or explicitly keep video in phoenix_omega and treat Qwen-Agent as the non-video app repo.

---

**User**

what's the plan to hand to videos to off to partner who puts them in metricle? 

---

**Cursor**


Checking for a distribution writer or upload step that pushes to R2/staging:



Here’s the **plan to hand videos off to the partner who puts them in Metricool** (your “metricle”):

---

## Handoff plan (partner → Metricool)

Defined in [VIDEO_PIPELINE_SPEC.md](docs/VIDEO_PIPELINE_SPEC.md) §10 and [VIDEO_PIPELINE_STORAGE_LAYOUT.md](docs/VIDEO_PIPELINE_STORAGE_LAYOUT.md). Partner uses **Metricool**; handoff is **R2 + manifests + ack-before-wipe**.

### 1. **Where handoff lives**

- **Target:** Cloudflare R2 (or equivalent).
- **Layout:** One prefix per day, e.g. `/{date}/long/{video_id}/` and `/{date}/shorts/{video_id}/`.
- Per video: `video.mp4`, `thumb.jpg`, `distribution_manifest.json` in that video’s folder.
- At date root: `daily_batch.json` (index of all videos for that day).

### 2. **Artifacts you produce**

| Artifact | Purpose |
|----------|--------|
| **distribution_manifest.json** (per video) | title, description, tags, `video_provenance_path`, `batch_id`, telemetry (hook_type, environment, motion_type, music_mood, etc.), `primary_asset_ids` — so partner/Metricool can schedule and categorize. |
| **daily_batch.json** | Single entry point for the day: `batch_date`, `long_form` / `shorts` arrays (paths or refs), **machine-verifiable counts** (e.g. `long_form_count`, `short_count`) so partner can confirm nothing was dropped. |

Pipeline already writes `distribution_manifest.json` ([write_metadata.py](scripts/video/write_metadata.py)); `daily_batch.json` and the R2 layout are for the **Distribution Writer** stage.

### 3. **Ack-before-wipe (required)**

- **Do not** wipe staging/R2 on a schedule (e.g. midnight).
- Partner’s system (or automation) writes **batch_acknowledged.json** (e.g. in the same bucket/folder) after ingest into Metricool.
- Your wipe step runs only when that file exists (and optionally when `failed_count == 0`).
- Ack should include `failed_count` and optionally `failed_ids[]` so you know what didn’t land.

So: **hand off to partner → partner ingests into Metricool → partner writes ack → then you wipe.**

### 4. **Pipeline stage (spec)**

- Stage **11. Distribution Writer** in the spec: “pack and upload (e.g. R2)”.
- In practice that means: take rendered output from `staging/<date>/` (or equivalent), upload to R2 in the layout above, write `daily_batch.json` **after** all uploads succeed (with retry/`upload_progress.json` so batch never points at missing files).

### 5. **Partner side (Metricool)**

- Partner (or her tooling): **only** reads `daily_batch.json` and follows the paths; no scanning/listening to the bucket.
- For each video: pull `video.mp4`, `thumb.jpg`, `distribution_manifest.json` and use manifest fields for scheduling/categorization in Metricool.
- After ingest: write `batch_acknowledged.json` (with `failed_count` / `failed_ids` if applicable).

### 6. **What’s in the repo today**

- **Done:** Per-video `distribution_manifest.json` (write_metadata.py), storage layout doc (staging under `staging/<date>/long|shorts/<video_id>/`), wipe rule “only after batch_acknowledged”.
- **Still to implement (per spec and chat):**
  - **Distribution Writer** script: upload to R2 (retry + `upload_progress.json`), then write `daily_batch.json` with verifiable counts.
  - Actual R2 bucket creation and credentials.
  - **daily_batch.json** schema and generation.
  - **batch_acknowledged.json** schema and wipe script that checks it (and optional `failed_count == 0`).

---

**One-line summary:** Hand off to partner for Metricool by uploading to R2 in a daily layout with per-video `distribution_manifest.json` and a single `daily_batch.json`, and only wipe after the partner writes `batch_acknowledged.json` (and optionally when there are no failures). The plan is specified; the R2 upload and batch/ack wiring are the remaining implementation work.

