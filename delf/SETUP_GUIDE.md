# Phoenix Protocol — Email Funnel Setup Guide
## MailerLite + GitHub Pages · Deploy in Under 1 Hour

---

## PHOENIX V4 SINGLE DEPLOY PATH (27 exercises)

If you're using the full Phoenix V4 freebie system:

1. **Landing pages (27)** — Generated into `public/breathwork/`:
   - **Email capture without MailerLite:** Set `formspree_form_id` in `config/freebies/exercises_landing.json` (one free form at [formspree.io](https://formspree.io)); then run `python3 scripts/generate_landing_pages.py`. You get submissions by email + CSV; optional Zapier → MailerLite later. See [docs/email_sequences/FORMSPREE_SETUP.md](../docs/email_sequences/FORMSPREE_SETUP.md).
   - Source of truth: `config/freebies/exercises_landing.json`
   - Output: `public/breathwork/lp-cyclic-sighing.html` … `lp-moon-breath.html`
   - **Optional MailerLite:** Leave `formspree_form_id` empty and add `ML_API_KEY` / `ML_GROUP_ID` in the generated pages (or in a shared script).

2. **Book CTAs** — Pipeline writes `public/free/{slug}/index.html`; when the freebie maps in `config/freebies/freebie_to_landing.yaml`, that page redirects to the correct `public/breathwork/lp-{exercise}.html` for email capture.

3. **Email sequences** — Copy from `docs/email_sequences/`:
   - [5-email-welcome-sequence.md](../docs/email_sequences/5-email-welcome-sequence.md) — replace `{{exercise_name}}`, `{{exercise_benefit}}`, `{{tool_link}}` per exercise.
   - [persona-variants.md](../docs/email_sequences/persona-variants.md) — Executive / Gen Z / Healthcare.
   - [exercise-one-liners.md](../docs/email_sequences/exercise-one-liners.md) — all 27 exercises for building one automation per exercise.

4. **Deploy** — Upload the contents of `public/` (e.g. `public/breathwork/` and `public/free/`) to your host or GitHub Pages. Your base URL is then `https://yoursite.com/` and `/breathwork/lp-cyclic-sighing.html` etc. work as landing pages; `/free/{slug}/` redirects to the right one.

---

## STEP 1 — MAILERLITE SETUP (20 min)

### 1.1 Create your free account
- Go to: mailerlite.com
- Sign up with your SpiritualTech email
- Verify domain ownership (they'll walk you through it)
- Free tier: up to 1,000 subscribers, 12,000 emails/month

### 1.2 Create your Groups (audiences)
In MailerLite → Subscribers → Groups, create these 5:

| Group Name | Tag |
|---|---|
| Phoenix — Spiritual Seekers | spiritual |
| Phoenix — Executives | executive |
| Phoenix — Gen Z | genz |
| Phoenix — Healthcare | healthcare |
| Phoenix — All Subscribers | all |

### 1.3 Get your API key
- MailerLite → Integrations → Developer API
- Copy your API key
- Add it to index.html (see comment block in the code)

### 1.4 Get your Group ID
- Click on any Group → the ID is in the URL bar
- Note each one down for the persona routing

---

## STEP 2 — GITHUB PAGES HOSTING (15 min)

### 2.1 Create a GitHub account (if needed)
- github.com → Sign up (free)

### 2.2 Create a new repository
- Click "+" → New repository
- Name it: `phoenix-tools` (or any name)
- Set to Public
- Click "Create repository"

### 2.3 Upload your files
Upload all 5 HTML files:
- index.html
- breath-reset.html
- emotional-audit.html
- nervous-system-reset.html
- courage-spinner.html

### 2.4 Enable GitHub Pages
- Repository → Settings → Pages
- Source: "Deploy from a branch"
- Branch: main / (root)
- Click Save

Your site will be live at:
`https://[yourusername].github.io/phoenix-tools/`

Takes 2–5 minutes to go live.

### 2.5 Optional: Custom domain
- Buy domain (e.g. phoenixprotocoltools.com) ~$12/year at Namecheap
- Add CNAME file to repo with your domain
- Point domain DNS to GitHub Pages

---

## STEP 3 — CONNECT MAILERLITE TO YOUR LANDING PAGE (10 min)

In index.html, find the comment block that starts with:
`// MAILERLITE INTEGRATION`

Uncomment it and replace:
- `YOUR_MAILERLITE_API_KEY` → your actual key
- `YOUR_GROUP_ID` → the "all" group ID

For persona routing (advanced), use this logic:
```javascript
const groupMap = {
  spiritual: 'GROUP_ID_SPIRITUAL',
  executive: 'GROUP_ID_EXECUTIVE',
  genz: 'GROUP_ID_GENZ',
  healthcare: 'GROUP_ID_HEALTHCARE'
};

const groupId = groupMap[persona] || 'GROUP_ID_ALL';
```

---

## STEP 4 — WELCOME EMAIL SEQUENCE

Set these up in MailerLite → Automations → Create workflow
Trigger: "Subscriber joins group"

---

### EMAIL 1 — Instant Delivery (Send immediately)

**Subject:** Your 4 Phoenix tools are here, [first_name]

---

[first_name],

You asked for tools that actually work.

Here they are.

**Your four Phoenix Protocol tools:**

→ [Breath Reset Timer](LINK) — Stop a stress spiral in 3 minutes
→ [Emotional Audit](LINK) — Name what's hijacking your focus
→ [Nervous System Reset](LINK) — Move tension out of your body
→ [Courage Action Spinner](LINK) — Break the freeze. Take one brave step.

Start with whichever one calls you.

If you're completely overwhelmed: Breath Reset.
If you want to understand yourself first: Emotional Audit.
If your body feels tight or stuck: Nervous System Reset.
If you know what to do but can't start: Courage Spinner.

These tools were built from 25 years of Buddhist practice, neuroscience, and somatic healing. They are not affirmations. They are not productivity hacks.

They are invitations to come back to yourself.

Use them.

— Phoenix Protocol

---

### EMAIL 2 — Day 2 (Send 24 hours later)

**Subject:** The one thing most people skip (don't skip this)

---

[first_name],

Most people who download wellness tools use them once, feel better for a day, then forget about them.

The tools then sit in a folder. The folder sits unopened.

Nothing changes.

Here's what actually creates change: **repetition before the crisis hits.**

The Breath Reset Timer takes 3 minutes.
If you do it today — not because you're spiraling, but because you're choosing to — you train your nervous system to access calm as a baseline, not just as an escape.

That's the difference between a practice and a fix.

Open the [Breath Reset Timer](LINK) right now. Before anything else.

Three minutes. That's the whole ask.

— Phoenix Protocol

P.S. Tomorrow I'll share the neuroscience behind why your body holds tension the way it does — and why the body scan works when "trying to relax" doesn't.

---

### EMAIL 3 — Day 4 (Send 3 days after Email 2)

**Subject:** Why "just relax" is neurologically impossible (and what to do instead)

---

[first_name],

Someone tells you to relax.

You try.

It doesn't work. You feel worse — now you're stressed AND failing at relaxing.

Here's why: the command to relax is processed by the same nervous system that's already dysregulated. You can't think your way out of a state that lives below thought.

This is why meditation doesn't work for everyone in acute stress. And why "breathe deeply" sometimes makes anxiety worse — if you're not doing it correctly, slow breathing without a proper exhale ratio can actually increase CO2 and amplify the panic signal.

The 4-7-8 pattern in your [Breath Reset Timer](LINK) is different. The extended exhale (8 counts) activates the vagus nerve directly — the parasympathetic pathway that signals: *threat is over. You are safe.*

This is why it works when "trying to relax" doesn't.

Your body doesn't respond to instructions. It responds to signals.

The tools I've built are all signal-based. Not affirmation-based.

That's the difference.

— Phoenix Protocol

P.S. I'm working on something bigger — a full therapeutic audio journey built for exactly the pattern you're in. I'll share it with you first, before anyone else sees it.

---

### EMAIL 4 — Day 7 (Send 3 days after Email 3)

**Subject:** [first_name], what's actually in the way?

---

[first_name],

A week ago, you asked for these tools.

I want to ask you something honest:

Have you used them?

If yes — which one has surprised you most? Just reply to this email and tell me. I read every response.

If no — what's in the way? 

Not asking to make you feel guilty. Genuinely curious. Because whatever is stopping you from a 3-minute breath exercise is probably the same thing that's stopping other things in your life that matter to you.

That's worth knowing.

The tools are still here, waiting:

→ [Breath Reset Timer](LINK)
→ [Emotional Audit](LINK)
→ [Nervous System Reset](LINK)
→ [Courage Action Spinner](LINK)

Start with one. Whichever one you keep skipping.

That's the one that needs you most.

— Phoenix Protocol

---

### EMAIL 5 — Day 14 (Send 7 days after Email 4)

**Subject:** Something I've been building for you

---

[first_name],

The four tools you have are a beginning.

What I've been building — for two years now — goes much deeper.

Therapeutic audiobooks. Each one engineered around a specific emotional pattern: shame loops, fear scanning, chronic depletion, cognitive overwhelm. Each one built from Buddhist doctrine, somatic science, and the kind of neurological precision that most self-help content never gets close to.

They're not motivational.
They're not aspirational.
They're structural — designed to shift the pattern at the root, not just soothe the symptom.

The first titles are almost ready.

As someone who found these tools, you'll hear about them before anyone else. And you'll get the subscriber rate — significantly less than what they'll sell for publicly.

I'll share more next week.

Until then — keep using the tools. Especially the one you find hardest.

— Phoenix Protocol

---

## SEGMENT-SPECIFIC VARIATIONS

For the **Executive** segment, replace the opening of Email 3 with:

> You've probably been told to "just take a break." Maybe by your therapist, your partner, your doctor.
> You've nodded. You've scheduled the vacation. You've come back and nothing has changed.
> Here's what they're not telling you about high-achieving nervous systems...

For the **Gen Z** segment, replace Email 2 subject with:
**Subject:** No, you're not broken. Here's what's actually happening.

For the **Healthcare** segment, replace Email 4 subject with:
**Subject:** The thing nobody tells healthcare workers about burnout

---

## FREEBIE_REGISTRY CONFIG (for V4 integration later)

```yaml
# config/freebies/freebie_registry.yaml

freebie_hub:
  url: https://[yourusername].github.io/phoenix-tools/
  tools:
    - id: breath_reset
      url: breath-reset.html
      engine_tags: [overwhelm, fear]
      persona_tags: [all]
    - id: emotional_audit
      url: emotional-audit.html
      engine_tags: [all]
      persona_tags: [all]
    - id: nervous_system_reset
      url: nervous-system-reset.html
      engine_tags: [depletion, fear, shame]
      persona_tags: [all]
    - id: courage_spinner
      url: courage-spinner.html
      engine_tags: [overwhelm, shame]
      persona_tags: [genz, executive]

email_platform: mailerlite
email_groups:
  all: YOUR_GROUP_ID_ALL
  spiritual: YOUR_GROUP_ID_SPIRITUAL
  executive: YOUR_GROUP_ID_EXECUTIVE
  genz: YOUR_GROUP_ID_GENZ
  healthcare: YOUR_GROUP_ID_HEALTHCARE
```

---

## TOTAL DEPLOYMENT TIME

| Task | Time |
|---|---|
| Sign up for MailerLite | 5 min |
| Create groups + get API key | 10 min |
| Create GitHub account + repo | 5 min |
| Upload 5 HTML files | 5 min |
| Enable GitHub Pages | 2 min |
| Connect MailerLite to form | 10 min |
| Set up 5 email automations | 20 min |
| **Total** | **~1 hour** |

After that: every visitor who enters their email is automatically tagged by persona and enrolled in the 5-email sequence.

You're building an owned audience. Not renting one from Instagram.

That is the foundation of everything that comes next.
