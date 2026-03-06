# GoHighLevel (GHL) handoff — Burnout Reset funnel

**Purpose:** This app pushes leads to GHL on form submit. No webhook for MVP. Operator adds API Key 2.0 and Location ID; GHL automations can run on "contact created" if desired.

## Setup

1. **GHL API Key 2.0** — Create in GHL (Settings → API → Create Key). Put in env: `GHL_API_KEY`.
2. **Location ID** — Your GHL location/sub-account ID. Put in env: `GHL_LOCATION_ID`.

## Payload (Contacts API)

| Field | Source | Notes |
|-------|--------|--------|
| `locationId` | `GHL_LOCATION_ID` | Required |
| `email` | Form `email` | Required |
| `firstName` | First word of form `name` | |
| `lastName` | Rest of `name` | |
| `phone` | — | Empty for MVP |
| `source` | `burnout_reset` (or hub slug) | |
| `customFields` | See below | |

**Custom fields:** GHL custom field **ids are UUIDs** assigned in GHL, not human-readable strings. In GHL go to **Settings → Custom Fields**, create or find the field, and copy its **ID (UUID)**. Put those UUIDs in your app config (e.g. `config.yaml` or env) and use them in the payload instead of `"id": "topic"`. Example: `{"id": "abc123-uuid-from-ghl", "value": "burnout"}`. Using string ids like `"topic"` or `"exercise"` will cause the push to fail or not map to the right field — this is the most common GHL integration failure.

## Recommended tags (add in GHL on contact created)

- `topic_burnout` (or per topic)
- `persona_*` if you add persona later
- `funnel_burnout_reset`
- `exercise_cyclic_sighing` (or chosen exercise)

## API reference

- **Endpoint:** `POST https://services.leadconnectorhq.com/contacts/`
- **Headers:** `Authorization: Bearer <GHL_API_KEY>`, `Content-Type: application/json`, `Version: 2021-07-28`
- **Body:** JSON as in table above. See [GHL Contacts API](https://highlevel.stoplight.io/docs/integrations/) for latest schema.

## Who sends email

Controlled by **email_mode** in `config.yaml` (or env `EMAIL_MODE`):

- **smtp:** This app sends E1–E5 via Brevo SMTP and APScheduler (persistent jobstore in same SQLite DB). Use for version-controlled, testable sequence.
- **ghl:** App only pushes contact + tags. GHL operator builds the sequence in GHL automation. No app sending; no scheduler.

Do not go live with smtp mode until E1–E5 are verified sending and unsubscribe is working.
