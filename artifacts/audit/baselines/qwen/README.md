# Qwen-Agent baseline for truth-audit delta

This directory holds the **intentional baseline** snapshot for `build_qwen_delta_addendum.py`.

- **`snapshot.json`** — Committed baseline. The workflow compares the current Qwen-Agent tree (after clone) to this file and writes `QWEN_DELTA_ADDENDUM.md` and `qwen_delta.json`.
- **Stable run-to-run:** With this file committed, every run has a known reference; no bootstrap drift.
- **Updating the baseline:** To reset “what changed” to a new reference, run the audit with Qwen-Agent present, then copy the generated snapshot into `snapshot.json` and commit (or run a one-off that writes the current snapshot here and commit).
