# GHL Email Copy — Social Anxiety Hub

Pre-written email content for GHL automation (Mode B: GHL sends emails).

Each file is one email in the Proof Loop sequence. Copy the subject line and body
into GHL's email builder. All links and content are production-ready.

## Files

| File | Email | Timing | Subject |
|------|-------|--------|---------|
| e1_immediate.md | Email 1 | Immediate on contact created | Your Bee Breath tool is here |
| e2_24h.md | Email 2 | +24 hours | One more reset — Body Scan with Breath |
| e3_72h.md | Email 3 | +72 hours | Why this actually works |
| e4_48h_after_e3.md | Email 4 | +48h after E3 | Recommended for you: Anxiety Reset |

## GHL Automation Setup

1. Go to Automations → Create Workflow
2. Trigger: Contact Created → Filter: Tag = `funnel_social_anxiety_reset`
3. Add emails with wait steps between them (see timing above)
4. Paste subject + body from each file into GHL email builder
5. In each email body, use GHL merge fields where noted:
   - `{{contact.first_name}}` — lead's first name
6. Add unsubscribe link and CAN-SPAM footer in GHL email settings

## Links (production)

- Tool link (Bee Breath): https://phoenixprotocolbooks.com/breathwork/tools/bee-breath.html
- Second tool link (Body Scan with Breath): https://phoenixprotocolbooks.com/breathwork/tools/body-scan.html?utm_content=email2_practice
- Book link: https://phoenixprotocolbooks.com/books/anxiety-reset
- Unsubscribe: handled by GHL's built-in unsubscribe

## Critical Rule

48-hour MINIMUM gap between Email 3 (story) and Email 4 (book offer). Non-negotiable.
