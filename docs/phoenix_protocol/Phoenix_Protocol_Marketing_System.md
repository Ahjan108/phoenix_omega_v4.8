
PHOENIX PROTOCOL BOOKS
Complete Marketing System
Freebie Funnel · Email Automation · Content Strategy · Upsell Architecture

SpiritualTech Systems · PhoenixProtocolBooks.com

VERSION 1.0 — IMPLEMENTATION READY

Executive Overview
This document is your complete, ready-to-execute marketing operating system for Phoenix Protocol Books. It covers every gap identified in the dev audit — freebie marketing intelligence, email automation using free platforms, persona-specific content, upsell funnels, and a 90-day launch plan.

🎯 Core Mission
Transform 1,200+ therapeutic audiobooks into a self-sustaining spiritual content empire by connecting each book to the right person at the right moment — using freebies as the entry point, email as the relationship engine, and series upsells as the growth flywheel.

System Gaps → Solutions
Marketing Component
Status
Priority
Freebie ↔ Marketing Intelligence
⚠️ Indirect only
🔴 HIGH — Fix First
Email Automation
❌ Not implemented
🔴 HIGH — Core Revenue
Freebie Marketing Plan
❌ No dedicated doc
🔴 HIGH — This Document
Upsell / Series Funnel
❌ Not implemented
🟡 MEDIUM — Phase 2
Multi-locale Pipeline
⚠️ Metadata only
🟢 LOW — Phase 3
Topic × Persona Grid
✅ Canonical grid possible
🟢 In Progress

Free Email Platform Stack
Using 100% free tools, here is the complete email infrastructure stack for Phoenix Protocol Books:

Recommended Stack: Brevo (Formerly Sendinblue)
Why Brevo #1 Choice
300 emails/day FREE (9,000/month). Unlimited contacts. Automation workflows on free plan. Transactional + marketing in one platform. Built-in landing pages. GDPR compliant.

Free Platform Comparison
Platform
Free Emails/Mo
Automation
Contacts
Best For
Brevo
9,000
✅ Yes
Unlimited
Phoenix Protocol ✅
Mailchimp
1,000
Basic only
500
Too limited
MailerLite
12,000
✅ Yes
1,000
Backup option
EmailOctopus
10,000
Limited
2,500
Simple lists
HubSpot Free
2,000
✅ Basic
1M CRM
CRM tracking

Formspree → Brevo Automation Bridge
Replace the Zapier-only suggestion with this free, working setup:

	•	Create Brevo account at brevo.com (free)
	•	In Brevo, create a List per freebie topic (e.g. 'Breathwork - NYC Exec', 'Grief Healing - Healthcare')
	•	In Formspree, add webhook: POST to Brevo API /contacts endpoint
	•	Include 'exercise_tag' field → maps to Brevo List ID
	•	Trigger: form submit → contact added to tagged list → automation fires

🔧 No-Code Alternative
Use Make.com (free tier: 1,000 ops/month): Formspree → Make → Brevo. Trigger on form submit, filter by exercise_tag, add to correct Brevo list, start the matching automation sequence.

Freebie Marketing Intelligence Integration
The dev audit shows freebies are assigned by rules only — not marketing intelligence. Here is how to connect them without changing code architecture.

The Marketing Intelligence Bridge
For each canonical topic × persona combination, the following metadata should be attached to freebie selection rules. This does not require code changes — it is a config layer addition to freebie_selection_rules.yaml:

Persona-Specific Freebie CTA Language
Persona
Pain Language
CTA Copy
NYC Executive
'I'm drowning in decisions and can't slow down'
Get your 5-min reset — free executive breathwork audio
Healthcare Worker
'I give all day and have nothing left'
Free compassion fatigue relief — 7-min somatic audio
Trauma Survivor
'I don't feel safe in my own body'
Begin gently — free body-safety audio exercise
Spiritual Seeker
'I want depth, not just stress tips'
Free ancient healing practice — your first sacred breath
Caregiver
'I'm last on my own list'
3 minutes just for you — free caregiver restoration audio
New Mom
'I've lost myself in motherhood'
Reclaim you — free 5-min postpartum grounding audio
Burned Out Pro
'High performance is costing me everything'
Free sustainable energy reset — no hustle required
Grief Holder
'I don't know how to carry this loss'
Free grief breathing practice — meet your pain gently

Topic-Specific Freebie Positioning
High-Urgency Topics
	•	Anxiety: 'Finally breathe again' angle
	•	Grief: Gentleness + permission to feel
	•	Burnout: Recovery without quitting
	•	Trauma: Safety first, healing second
	•	Depression: Small steps, real hope
Transformational Topics
	•	Sleep: Wake up transformed, not just rested
	•	Chronic Pain: Mind-body bridge language
	•	Relationships: Inner work = outer harmony
	•	Purpose: Ancient wisdom + modern clarity
	•	Addiction Recovery: Replace with breath, not willpower

Complete Email Automation Sequences
These are production-ready email sequences. Load these directly into Brevo as automation workflows. Each sequence triggers from a specific freebie download tag.

Sequence 1: The Welcome & Depth Sequence (All Personas)
Trigger: Any freebie download. Duration: 7 days, 5 emails. Goal: Build relationship, deliver value, soft pitch book.

📧 EMAIL TEMPLATE
Subject: Your free [EXERCISE_NAME] is inside 🌬️
Preview: Plus: the one thing most people miss when they start breathwork...
Hi [First Name],

Your free [EXERCISE_NAME] is attached. I created this specifically for [PERSONA_PAIN_POINT] — people who [INVISIBLE_SCRIPT_PHRASE].

Before you press play, one thing:
Most people try to do breathwork perfectly. The practice doesn't need your perfection. It just needs your presence.

Take 5 minutes today. That's it.

→ [DOWNLOAD LINK]

Tomorrow I'll share what happens in your nervous system during the first 90 seconds of conscious breath — it's why this works even when everything else has failed.

With you,
[AUTHOR_NAME]
PhoenixProtocolBooks.com

📧 EMAIL TEMPLATE
Subject: What happens in your body after 90 seconds (science + spirit)
Preview: This is why the practice works even when you've tried everything else...
Hi [First Name],

Yesterday you downloaded [EXERCISE_NAME]. Whether you've tried it yet or not — this email is for you.

Here's what happens neurologically in the first 90 seconds of conscious breathwork:
• Your vagus nerve activates — shifting from threat to safety mode
• Cortisol drops measurably within 2 minutes
• Your prefrontal cortex (decision-making, compassion) comes back online

This isn't just stress relief. It's a rewiring.

Ancient traditions knew this. Modern neuroscience has now confirmed it.
That's exactly what my book [BOOK_TITLE] is built on — the bridge between.

I'd love you to experience the full practice. But for now, try your free audio one more time — knowing what you know now.

[REPLAY DOWNLOAD LINK]

Tomorrow: the three mistakes that make breathwork feel useless (and how to avoid them).

📧 EMAIL TEMPLATE
Subject: 3 mistakes that make breathwork feel like a waste of time
Preview: Most people make mistake #2 and don't even know it...
Hi [First Name],

I hear this a lot: 'I tried it and nothing happened.'
Here's why — and the three mistakes almost everyone makes:

MISTAKE 1: Breathing FOR relaxation instead of FOR presence.
The goal isn't calm. The goal is contact — with yourself.

MISTAKE 2: Stopping when it gets uncomfortable.
Discomfort in breathwork is often the sensation of something releasing.
The practice begins at the edge, not before it.

MISTAKE 3: Treating it like a one-time fix.
Your nervous system learned its patterns over years.
3 minutes a day for 21 days rewires more than 3 hours once.

In [BOOK_TITLE], I give you a full 21-day protocol — one practice per day, building on the last.

You can start with just the free audio. And when you're ready for the full journey:
→ [BOOK_LINK] (Available on Amazon / [platform])

More tomorrow.

📧 EMAIL TEMPLATE
Subject: A story about [PERSONA_ARCHETYPE] who couldn't stop crying in a parking lot
Preview: This is why the work we're doing together matters...
Hi [First Name],

[STORY: 150-word true or composite story of a persona-matched person hitting rock bottom and finding relief through the practice. Specific, sensory, emotionally honest. No toxic positivity.]

I tell this story because [PERSONA CONNECTING LINE — why this speaks to their specific journey].

The free exercise you downloaded is a doorway.
[BOOK_TITLE] is the full passage.

If you've been carrying [SPECIFIC BURDEN FOR PERSONA] — you don't have to anymore.

→ Get [BOOK_TITLE] on [Platform]: [LINK]

Whether you get the book or not — keep breathing.

[AUTHOR_NAME]

📧 EMAIL TEMPLATE
Subject: Last email (+ something I've been saving for you)
Preview: This is the practice that changed everything for me personally...
Hi [First Name],

This is the last email in this series — but not the last I hope to send you.

I've saved one thing: the practice that changed my own life.
Not the most complex one. The simplest.

[AUTHOR'S PERSONAL 3-SENTENCE PRACTICE STORY]

I've included this practice in [BOOK_TITLE] as Chapter [X]: [CHAPTER_NAME].
I wanted you to know it exists, and that it's yours if you want it.

→ [BOOK_LINK]

And if you want to stay on this list, you'll occasionally hear from me about:
• New free exercises
• Upcoming audiobook releases
• Live practice sessions (free)

Just reply 'YES KEEP ME' and I'll make sure you get everything.

With gratitude for your practice,
[AUTHOR_NAME]

Sequence 2: The Series Upsell Sequence
Trigger: Book purchase confirmed OR 14 days after freebie download with no purchase. Duration: 4 emails over 10 days.

📧 EMAIL TEMPLATE
Subject: You've started something. Here's what comes next.
Preview: The journey doesn't end at Book 1 — here's the full map...
Hi [First Name],

You're working with [BOOK_TITLE]. I want to show you where this can take you.

The Phoenix Protocol is a series. Here's the full path:

BOOK 1: [BOOK_1_TITLE] — Foundation (You are here ✓)
BOOK 2: [BOOK_2_TITLE] — Integration
BOOK 3: [BOOK_3_TITLE] — Embodiment

Each book builds on the last. Each one has its own free audio companion.

You don't need all three right now. You just need to know the path exists.

When you're ready for Book 2: [SERIES_BOOK_2_LINK]

Keep practicing,
[AUTHOR_NAME]

Sequence 3: Re-engagement (90 Days No Open)
Trigger: Contact hasn't opened any email in 90 days. 3-email win-back sequence.

📧 EMAIL TEMPLATE
Subject: Did we lose you? (honest question)
Preview: I want to make sure this is still useful for you...
Hi [First Name],

I noticed you haven't opened anything in a while.
That's completely okay — life gets loud.

I have one question: Is breathwork still something you want in your life?

Reply with:
YES — keep sending me practices
PAUSE — I'll check back in 3 months
STOP — I'll remove you completely (no hard feelings)

No click required. Just a reply.

Either way, I'm grateful you downloaded that first audio.

[AUTHOR_NAME]

Content Strategy: 90-Day Plan
Content serves one purpose: send warm, pre-educated leads into the freebie funnel. Every piece of content ends with a freebie CTA.

Content Pillars by Platform
Four Content Pillars
	•	PILLAR 1: The Science (neuroscience explainers)
	•	PILLAR 2: The Story (transformation narratives)
	•	PILLAR 3: The Practice (micro-exercises in post)
	•	PILLAR 4: The Why (spiritual philosophy accessible)
Platform Matching
	•	Instagram/TikTok: Pillar 3 + 2 (visual, emotional)
	•	YouTube: Pillar 1 + 4 (depth content)
	•	LinkedIn: Pillar 1 + 2 (for healthcare/exec personas)
	•	Email: All 4 pillars rotating weekly

30-Day Content Calendar (Month 1: Foundation)
Week
Theme
Content Pieces
Freebie CTA
Week 1
Your Nervous System Is Not Broken
3 IG posts, 1 LinkedIn article, 1 email
Anxiety breathwork freebie
Week 2
The Body Keeps the Score (And Can Heal)
3 IG posts, 1 YouTube short, 1 email
Trauma somatic freebie
Week 3
What Ancient Monks Knew That We Forgot
3 IG posts, 1 LinkedIn, 1 TikTok, 1 email
Spiritual seeker freebie
Week 4
5 Minutes That Change Everything
4 IG posts, 1 YouTube long-form, 1 email
General breathwork freebie

Month 2: Persona Deep Dives
Week
Persona Focus
Content Angle
Freebie
Week 5
NYC Exec / Burned Out Pro
'Performance without sacrifice' positioning
Executive reset audio
Week 6
Healthcare Workers
'You can't pour from an empty cup' + compassion fatigue angle
Compassion fatigue relief
Week 7
Trauma + Grief
Permission-based, safety-first language
Gentle somatic entry
Week 8
Spiritual Seekers
Ancient wisdom meets neuroscience hook
Sacred breath practice

Month 3: Series Launch & Upsell
	•	Announce Book 2 with existing list (warm launch)
	•	Send 'You started with Book 1 — here's what it unlocks' to all purchasers
	•	Launch freebie for Book 2 to existing subscribers as VIP early access
	•	Add 'complete the series' CTA to all Book 1 automated emails

Landing Page Strategy
Each freebie needs its own high-converting landing page at PhoenixProtocolBooks.com/free/{slug}. Here is the proven structure:

Landing Page Template Structure
	•	HEADLINE: '[Persona Pain] ends here.' OR 'Finally: [outcome] in [timeframe]'
	•	SUB-HEADLINE: What they get + how long it takes + what it does
	•	AUDIO PREVIEW: 30-second sample of the freebie audio
	•	3 BULLETS: What they'll experience (sensory, specific, honest)
	•	FORM: First name + email only (Formspree with exercise_tag hidden field)
	•	SOCIAL PROOF: 1 quote from someone like them (same persona)
	•	BELOW FOLD: Brief author bio + mission statement

🔑 Conversion Secret for Spiritual Audiences
Don't sell the technique. Sell the PERMISSION. Your audience has been told their emotions are wrong, their bodies are broken, their spirituality is impractical. The headline that converts is: 'You're not broken. You're ready.' Then give them the practice as proof.

Slug Strategy by Persona
	•	/free/executive-reset — NYC Exec, Burned Out Pro
	•	/free/compassion-restore — Healthcare Workers, Caregivers
	•	/free/gentle-start — Trauma Survivors, Grief Holders
	•	/free/sacred-breath — Spiritual Seekers
	•	/free/mother-restore — New Moms
	•	/free/sleep-ritual — General wellness, insomnia
	•	/free/anxiety-anchor — Anxiety, panic, overwhelm
	•	/free/grief-practice — Grief, loss, transition

90-Day Launch Plan

Phase 1: Foundation (Days 1–30)
Week 1-2: Infrastructure Setup
	•	Create Brevo account + import any existing emails
	•	Build 8 Brevo automation lists (one per freebie slug)
	•	Set up Formspree webhooks to Brevo API for each of the 27 breathwork pages
	•	Load Welcome Sequence (5 emails) into Brevo automations
	•	Test full flow: form submit → email received → sequence triggers

Week 3-4: Content & Landing Pages
	•	Audit existing 27 breathwork landing pages — add persona-matched CTA copy
	•	Create 8 persona-specific landing pages using template structure above
	•	Write Month 1 content calendar (12 pieces) — use Pillar 1 + 2 content
	•	Schedule via Buffer (free) or Meta Business Suite (free for IG/FB)

Phase 2: Activation (Days 31–60)
	•	Begin persona deep-dive content month (Week 5-8 calendar)
	•	Add Series Upsell Sequence to Brevo (Sequence 2 above)
	•	A/B test subject lines on Welcome Email 1 (Brevo has free A/B)
	•	Add UTM parameters to all freebie links for tracking in Google Analytics (free)
	•	Launch LinkedIn content for healthcare + executive personas

Phase 3: Scale (Days 61–90)
	•	Add Re-engagement sequence for 90-day non-openers
	•	Build Book 2 launch sequence for existing list
	•	Create 'Complete the Series' upsell campaign
	•	Set up Google Analytics funnel tracking: social → landing page → email → book purchase
	•	Document what's working for replication across all 1,200 books

📊 Free Analytics Stack
Google Analytics 4 (traffic + funnels) + Brevo Analytics (email opens, clicks, revenue) + Formspree submissions dashboard = complete funnel visibility at zero cost.

Gen Z Optimization Strategy
With 51.88% of Claude's audience aged 18-24, and Gen Z being the fastest-growing mental wellness market, here's how to position Phoenix Protocol Books for this demographic:

Gen Z Language & Positioning
Language That Lands
	•	'Deregulate your nervous system' (not 'relax')
	•	'Somatic healing' is already in their vocab
	•	'This is neurodivergent-friendly'
	•	'No toxic positivity — real practices'
	•	'Trauma-informed, not trauma-bypassing'
Format That Works
	•	TikTok-first: 15-second 'try this right now' clips
	•	Raw, unfiltered audio > polished production
	•	Community angle: 'we're all figuring this out'
	•	Acknowledge systemic stress (not just personal)
	•	Anti-hustle, pro-sustainable performance

Gen Z Freebie Hook Variations
	•	'Your body knows things your brain hasn't processed yet. Here's how to listen.' (Anxiety)
	•	'5-minute nervous system reset for when you're absolutely done.' (Burnout)
	•	'Grieving something you can't explain? This practice doesn't need words.' (Grief)
	•	'Ancient monks figured out what therapists now call 'regulation.' You can learn it in a day.' (Spiritual)
	•	'This isn't mindfulness. This is something older and it actually works.' (General)

Metrics, KPIs & Optimization
Key Performance Indicators
Metric
Month 1 Target
Month 3 Target
Track In
Freebie downloads
50/month
500/month
Formspree + Brevo
Email open rate
35%+
40%+
Brevo Analytics
Click-through rate
5%+
8%+
Brevo Analytics
Book page clicks
10% of opens
15% of opens
GA4 + UTMs
Email list growth
+50/month
+500/month
Brevo
Social → landing pg conversion
2%
4%
GA4

Monthly Optimization Ritual
	•	Pull Brevo report: open rates, click rates, unsubscribes by sequence
	•	Check GA4: which freebie slugs are getting traffic, which converting
	•	A/B test: one subject line variation per week
	•	Content audit: which pillar content drives most freebie downloads
	•	List hygiene: remove 90-day non-openers after re-engagement sequence

Implementation Checklist
Use this as your weekly operations checklist.
Check off as you build. This is your single source of truth for the marketing system launch.

Infrastructure (Week 1)
	•	☐  Create Brevo account (brevo.com)
	•	☐  Create 8 segmented lists in Brevo (one per persona/freebie type)
	•	☐  Connect Formspree forms to Brevo via webhook or Make.com
	•	☐  Upload Welcome Sequence (5 emails) from this document into Brevo
	•	☐  Upload Series Upsell Sequence (4 emails)
	•	☐  Upload Re-engagement Sequence (3 emails)
	•	☐  Test all automation triggers with test email addresses

Content & Landing Pages (Week 2-3)
	•	☐  Audit all 27 existing breathwork landing pages — add persona CTA copy
	•	☐  Build 8 persona landing pages using template structure
	•	☐  Write 12 content pieces for Month 1 calendar
	•	☐  Set up Buffer or Meta Business Suite for scheduling
	•	☐  Add UTM parameters to all landing page links

Analytics (Week 3)
	•	☐  Install GA4 on PhoenixProtocolBooks.com
	•	☐  Set up GA4 conversion events (form submit, book page view, book link click)
	•	☐  Create GA4 funnel report: social → landing → email → book
	•	☐  Connect Brevo analytics dashboard

Launch (Week 4)
	•	☐  Soft launch: share freebies to existing personal networks first
	•	☐  Post first content calendar week
	•	☐  Monitor first 100 form submissions for any automation errors
	•	☐  Adjust subject lines based on first open rate data



Phoenix Protocol Books Marketing System v1.0
SpiritualTech Systems · PhoenixProtocolBooks.com · Built with intention.
