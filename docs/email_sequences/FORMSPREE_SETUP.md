# Formspree setup (no MailerLite required)

All 27 landing pages can capture email with **one Formspree form**. No API keys, no MailerLite account.

## Steps

1. **Sign up**  
   Go to [formspree.io](https://formspree.io) → Sign up (free).

2. **Create a form**  
   Dashboard → **New form** → Name it e.g. "Phoenix breathwork signups" → Create.

3. **Copy the form ID**  
   Formspree shows an endpoint like `https://formspree.io/f/xyzabcde`.  
   Copy only the ID part: **`xyzabcde`**.

4. **Put it in config**  
   Open `config/freebies/exercises_landing.json`.  
   Set `"formspree_form_id": "xyzabcde"` (replace with your ID).  
   Save.

5. **Regenerate the 27 pages**  
   From repo root:
   ```bash
   python3 scripts/generate_landing_pages.py
   ```
   All 27 HTML files in `public/breathwork/` will now submit to Formspree.

6. **Deploy**  
   Upload `public/breathwork/` (and the rest of `public/`) to your host or GitHub Pages.

## What you get

- **Email on every signup** — Formspree sends you an email per submission (you can turn this off and use the dashboard only).
- **Dashboard** — All submissions at formspree.io with columns: email, exercise (which of the 27 pages they used).
- **Export** — CSV export anytime.
- **Integrations** — Formspree can send to Google Sheets, Airtable, Slack, or **Mailchimp/MailerLite via Zapier** when you’re ready.

## Optional: MailerLite later

When you want automations (welcome series, segments), use Zapier: Formspree → MailerLite. Or switch the generator back to MailerLite by clearing `formspree_form_id` and adding your API key/group ID to the generated pages (see SETUP_GUIDE).
