# Video pipeline — R2 credentials

**Where to find / how to use**

- **Template:** [../.env.example](../.env.example) — lists the four R2 variables.
- **Your values:** In `cloudflare_api.rtf` at repo root (R2 Account Token). Keep that file as your backup; it is gitignored (`*.rtf`) so it is never committed.
- **At runtime:** Copy `.env.example` to `.env`, fill in from `cloudflare_api.rtf`, then load before running the distribution writer:
  ```bash
  set -a; source .env; set +a
  python scripts/video/distribution_writer.py --date YYYY-MM-DD
  ```

**Variable names (must match)**

| In cloudflare_api.rtf | Use in .env |
|------------------------|-------------|
| R2_ACCOUNT_ID         | `R2_ACCOUNT_ID` |
| Token value            | `R2_ACCESS_KEY_ID` |
| Secret Access Key      | `R2_SECRET_ACCESS_KEY` |
| R2_BUCKET_NAM          | `R2_BUCKET_NAME` (note: correct spelling is NAME) |

**Authority:** [VIDEO_PIPELINE_SPEC.md](VIDEO_PIPELINE_SPEC.md) §10, [config/video/distribution_r2.yaml](../config/video/distribution_r2.yaml).
