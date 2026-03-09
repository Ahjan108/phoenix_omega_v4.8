# Brand Admin Portal (minimal v1)

Login-required packet downloads. No permanent public links; backend mints a 15-minute R2 signed URL when the admin clicks "Get download."

## Auth

- **Production:** Put the app behind [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/policies/access/) (Google/Microsoft + MFA). Access sets `Cf-Access-Authenticated-User-Email` and optional JWT.
- **Local dev:** Set `OVERRIDE_EMAIL=you@example.com` to bypass CF and act as that user.

## Data

- **SQLite:** `data/portal.db` (create with `schema.sql` on first run; `models.init_db()` is called automatically).
- **Users and grants:** `brand_admin_users`, `brand_admin_grants`. Bootstrap from config (see below) or insert manually.
- **Packet metadata:** `weekly_packets` is filled by `scripts/release/sync_packets_to_portal_index.py` after the pipeline uploads zips to R2.

## Env

- `PORTAL_DB_PATH` — optional path to SQLite DB (default: `services/admin_portal/data/portal.db`).
- `OVERRIDE_EMAIL` — dev only; treat as authenticated user.
- `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME` — for minting signed URLs.

## Run

```bash
cd /path/to/phoenix_omega
pip install -r services/admin_portal/requirements.txt
OVERRIDE_EMAIL=admin@example.com uvicorn services.admin_portal.app:app --reload --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000/admin/packets` and `http://localhost:8000/docs` for API.

## Bootstrap users from config

Map `admin_user -> allowed_brand_ids` from `config/release/brand_admin_contacts.yaml` (email per brand). Run once:

```bash
python scripts/release/bootstrap_portal_users.py
```

(Optional script: reads brand_admin_contacts.yaml and ensures each email has a user and grants for that brand.)

## Weekly automation

1. Pipeline exports zips and uploads to R2 (`weekly/YYYY-WW/<brand_id>/packet.zip`).
2. Run sync to update portal DB and optionally write `download_index.json`:
   `python scripts/release/sync_packets_to_portal_index.py --week-start 2026-03-10 --write-index`
3. Notify admins: "Packet ready; log in to the portal to download" (no direct signed URLs in email).

## Security

- Signed URLs expire in 15 minutes.
- No public bucket ACL; R2 only via backend-minted URLs.
- Rate limit: 10 mint requests per user per 15 minutes.
- Every list/mint is logged in `packet_access_audit`.
- Disable a user by setting `status = 'disabled'` in `brand_admin_users`.
