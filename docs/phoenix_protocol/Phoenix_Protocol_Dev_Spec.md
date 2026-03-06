
PHOENIX PROTOCOL BOOKS
Marketing Funnel — Developer Implementation Spec
v1.0  ·  SpiritualTech Systems  ·  PhoenixProtocolBooks.com


Document Type
Audience
Status
Date
Technical + Marketing Spec
Developer + Marketing Lead
Ready for Implementation
2026

📋  How to use this document
Read Section 1 (System Overview) first. Section 2 is the MVP build — start here. Sections 3–7 are the scaling roadmap to implement after MVP validation. Sections 8–9 are constraints and decisions that must be locked before any build begins.
1. System Overview
Phoenix Protocol Books is a therapeutic audiobook catalog targeting 1,200+ titles organized by topic × persona. The marketing system's job is to connect each book to the right person through a freebie → email → book recommendation funnel.

1.1 What Already Exists (Do Not Rebuild)
	•	27 breathwork landing pages at public/breathwork/
	•	Formspree email capture on all 27 pages (exercise_tag field present)
	•	freebie_registry.yaml and freebie_selection_rules.yaml — freebie assignment logic
	•	15 canonical topics in canonical_topics.yaml
	•	10 canonical personas in canonical_personas.yaml
	•	Series metadata (series_id, installment_number) on all books
	•	Marketing intelligence in marketing_deep_research/ and config/marketing/ — feeds title engine only

1.2 What Does Not Exist Yet (The Build List)
Gap
Impact
Phase
Email automation (sequences)
No relationship after capture
MVP
Freebie → book mapping
No conversion path
MVP
Topic hub pages (SEO)
No organic traffic
Phase 2
Persona-specific landing pages
Low conversion on warm traffic
Phase 2
Series upsell funnel
No repeat purchase
Phase 2
Multi-locale pipeline
English only
Phase 3
Recommendation engine
Manual book suggestions
Phase 3

1.3 The Single Validation Question
🎯  MVP Question
Will a cold visitor trust this source enough to exchange their email for a free breathwork audio — and then follow a book recommendation in the email sequence? Everything in the MVP exists to answer this one question. Do not build beyond it until you have data.
2. MVP Build Spec
Build exactly this — nothing more. Estimated dev time: 3–5 hours with existing stack.

2.1 The MVP Funnel
Traffic (personal network + LinkedIn)
   ↓
Topic page: /burnout-reset
   ↓
Formspree form → Brevo API (structured tags)
   ↓
Thank-you page: /free/burnout-reset
   ↓
4-email sequence (Brevo automation)
   ↓
Book recommendation link (UTM-tracked → your site → Amazon redirect)

2.2 Page: /burnout-reset
URL
PhoenixProtocolBooks.com/burnout-reset

Page Section Order
	•	Identity headline (see copy below)
	•	Authority narrative — WRITTEN BY NIHALA, NOT GENERATED (see Section 2.3)
	•	Burnout explanation — 2 paragraphs, plain language, one research citation
	•	Practice preview — breathing rhythm, optional 30-sec audio preview
	•	Email capture form (see Section 2.4)
	•	Single book recommendation (see Section 2.5)

Headline Options to A/B Test
Variant
Headline
Sub-headline
A (Identity)
For People Who Give Too Much
A 3-minute nervous system reset — free guided audio
B (Outcome)
When You Care Too Much and Your Body Pays the Price
Try the 3-minute reset. No apps, no subscriptions.
C (Direct)
Burnout Isn't Weakness. It's Nervous System Overload.
Get the free guided audio that helps your body stand down.

📝  Recommendation
Test Variant A first — identity-based headlines self-select the right audience and reduce unsubscribes. Switch to B or C after 200+ visitors if conversion is below 5% from warm traffic.

2.3 The Authority Narrative — CRITICAL
⚠️  This section must be written by Nihala in her own voice. Do not generate or approximate it. The entire SEO and trust value of the page depends on authentic specificity.

The authority narrative is a single paragraph (100–150 words) placed immediately below the headline. It must contain:
	•	A specific moment or observation from lived experience
	•	A connection between that experience and the practice on this page
	•	No generic inspiration language

Nihala's actual authority elements to draw from:
	•	25 years of Buddhist monastic training
	•	MIT robotics background — systems that respond to feedback loops
	•	McKinsey strategy experience
	•	Work with therapeutic breathwork across professional burnout populations

✍️  Process
Nihala dictates or writes this paragraph. Developer or editor does one light pass for clarity. This text becomes the canonical authority block used across all hub pages — not rewritten per page.

2.4 Form Specification
Fields — Visible
first_name    type="text"   required=false
email         type="email"  required=true

Fields — Hidden
topic         value="burnout"
exercise      value="reset_breath"
source_page   value="burnout-reset"
utm_source    value=""   // populated by JS from URL params
utm_medium    value=""   // populated by JS from URL params
utm_campaign  value=""   // populated by JS from URL params
referrer      value=""   // populated by JS: document.referrer
landing_path  value=""   // populated by JS: window.location.pathname

⚠️  Do NOT hardcode persona in the form. The burnout page serves nurses, therapists, teachers, and caregivers. Persona is collected via a single optional dropdown (see below) or inferred from UTM source — never hardcoded.

Optional Persona Field
persona   type="select"   required=false   label="I work as a..."

Options:
  nurse_or_healthcare
  therapist_or_counselor
  teacher_or_educator
  caregiver
  entrepreneur_or_leader
  other

Default: blank (do not pre-select)

CTA Button Copy
Option
Copy
Notes
Recommended
Yes — I'm ready to reset my nervous system
Permission framing, high intent signal
Alternative
Start the 3-minute reset
Agency-based, shorter
Avoid
Send me the audio / Get the free reset
Transactional, lower resonance for this audience

Form Endpoint
Formspree: POST to https://formspree.io/f/YOUR_FORM_ID

On success: do NOT redirect immediately.
Show inline confirmation: 'Done — check your email.'
Fire GA4 event: freebie_signup (see Section 2.7)

Optional: redirect to /free/burnout-reset after 2 seconds
          (thank-you page with audio player + download link)

2.5 Book Recommendation Section
Exactly one book recommended on the page. Do not list multiple. The recommendation appears below the form, not before it.

Book title:   [INSERT: primary burnout book from catalog]
Sub-line:     [INSERT: one sentence — who it's for]
Link:         Your site URL → 301 redirect to Amazon
              (routing through your domain lets GA4 track the click)
Link text:    See the book →
Track as:     data-track='book_link' for GA4 event

⚠️  Do not link directly to Amazon from the page. Route all book links through a page on PhoenixProtocolBooks.com (e.g. /books/burnout-recovery-healthcare) that 301-redirects to Amazon. This is the only way to measure intent between email click and Amazon page view.

2.6 Email System: Brevo
Why Brevo
Feature
Brevo Free Tier
Requirement Met?
Monthly sends
9,000 emails/month
✅ Yes
Contacts
Unlimited
✅ Yes
Automation workflows
Yes, on free plan
✅ Yes
Attribute-based segmentation
Yes
✅ Yes
A/B subject line testing
Yes
✅ Yes
API access
Yes
✅ Yes

Formspree → Brevo Connection
Option A (No-code):  Make.com free tier
  Trigger:  Formspree webhook
  Action 1: Create/update contact in Brevo
  Action 2: Set contact attributes (topic, exercise, persona, source_page)
  Action 3: Add to list 'burnout_reset'
  Action 4: Trigger automation 'burnout_welcome_sequence'

Option B (Code):  Direct Brevo API call from Formspree webhook
  POST https://api.brevo.com/v3/contacts
  Header: api-key: YOUR_BREVO_API_KEY
  Body: { email, attributes: { TOPIC, EXERCISE, PERSONA, SOURCE_PAGE } }
  Then: POST https://api.brevo.com/v3/contacts/email/trigger-automation

Brevo Contact Attributes to Create
TOPIC          text     e.g. burnout
EXERCISE       text     e.g. reset_breath
PERSONA        text     e.g. nurse_or_healthcare
SOURCE_PAGE    text     e.g. burnout-reset
UTM_SOURCE     text
UTM_MEDIUM     text
UTM_CAMPAIGN   text
SIGNUP_DATE    date     auto

Brevo List Structure
Create one list per freebie slug. Do not use a single master list — segmentation breaks down at scale.
List: burnout_reset
List: anxiety_anchor
List: compassion_restore
List: gentle_start
List: grief_practice
List: sleep_ritual
List: sacred_breath
List: executive_reset

Add more lists as new freebie pages launch.
Naming convention: {slug_without_hyphens}

2.7 The 4-Email MVP Sequence
Load this sequence into Brevo as an automation triggered by list membership. All delays are from signup time.

#
Delay
Subject Line
Primary Goal
Key Content
1
Immediate
Your 3-minute burnout reset is inside
Deliver the audio
Audio link + one-sentence framing. No selling. End with: 'Tomorrow: why this works in your body.'
2
+1 day
What's happening in your body during burnout
Build trust via science
Vagus nerve + cortisol explanation (plain language). One research citation. Soft bridge: 'This is what [BOOK] is built on.'
3
+3 days
[PERSONA-MATCHED STORY — written by Nihala]
Emotional resonance
True or composite story: specific profession, specific moment, specific change. 120–150 words. No toxic positivity.
4
+5 days
If this has been building for a while...
Book recommendation
One sentence on who the book is for. Link via your domain (not direct Amazon). Track as: utm_campaign=burnout_reset&utm_content=email4_book

⚠️  Email 3 (the story) must be written by Nihala or sourced from real client experience with consent. A generated story will read as generic and undermine the trust built in emails 1–2. This is not optional.

Email 4 Book Link Format
https://phoenixprotocolbooks.com/books/{book-slug}
  ?utm_source=email
  &utm_medium=automation
  &utm_campaign=burnout_reset
  &utm_content=email4_book

The /books/{slug} page 301-redirects to Amazon.
GA4 tracks the click at /books/{slug} before redirect.

2.8 Analytics: GA4
Events to Track
Event Name
Trigger
Parameters
page_view
automatic
page_path, page_title
freebie_signup
Formspree success callback
exercise_tag, topic, persona, source
book_link_click
click on [data-track='book_link']
book_slug, source_page
audio_play
play event on audio element
exercise_tag
email_book_click
GA4 auto-tracks UTM arrivals
utm_campaign, utm_content

The Conversion Funnel to Monitor
Step 1: /burnout-reset page view
Step 2: freebie_signup event
Step 3: email opened (tracked in Brevo, not GA4)
Step 4: /books/{slug} page view with utm_medium=automation

GA4 Funnel Report: Exploration → Funnel exploration
Steps: page_view → freebie_signup → book page view (utm filtered)

2.9 MVP Success Criteria
⚠️  These benchmarks are traffic-source dependent. Track traffic source separately. Do not average warm and cold traffic together — they are different experiments.

Traffic Source
Email Conversion Target
Email Open Target
Book Click Target
Personal network / warm
15–25%
45–60%
10–15%
LinkedIn organic
3–8%
35–45%
5–10%
SEO organic (month 3+)
5–10%
35–45%
5–10%
Cold social
1–3%
25–35%
3–6%

The funnel is validated when you have 100+ visitors from a single source and see email → book click rate above the target for that source. Do not declare failure or success with fewer than 100 visitors per source.
3. Tagging Architecture
This section defines the tagging standard for all future freebie pages. Establish this before launching more than one page — retroactive retagging is expensive.

3.1 Tag Structure
Use two-field structured attributes, not single concatenated strings.

✅ Correct:
   topic:burnout  +  persona:nurse_or_healthcare

❌ Wrong:
   tag: burnout_nurse_reset

The two-field structure lets you filter by either dimension independently.
Single concatenated tags explode combinatorially at 1,200 books.

3.2 Canonical Topic Tags
Tag Value
Maps to canonical_topics.yaml
Primary Personas
burnout
Yes
healthcare, education, tech_workers, therapists
anxiety
Yes
general, executives, students, new_parents
grief
Yes
general, caregivers, healthcare
trauma
Yes
general, survivors, healthcare
overthinking
Yes
executives, tech_workers, entrepreneurs
sleep
Yes
general, shift_workers
chronic_pain
Yes
general, healthcare
depression
Yes
general, caregivers
purpose
Yes
executives, midlife, spiritual_seekers
relationships
Yes
general, new_parents, caregivers

3.3 Canonical Persona Tags
These are the values for the PERSONA attribute. They match the 10 personas in canonical_personas.yaml.
nurse_or_healthcare
therapist_or_counselor
teacher_or_educator
caregiver
entrepreneur_or_leader
tech_worker
spiritual_seeker
new_parent
grief_holder
general

⚠️  Do not create new persona tags without updating canonical_personas.yaml. Tag fragmentation is the primary cause of recommendation engine failure at scale.
4. Phase 2 — SEO Topic Hubs
Do not build Phase 2 until MVP is validated (100+ visitors, measurable conversion). This section is planning-only until that threshold is met.

4.1 The Thin Content Risk
🚨  Critical Warning for Phoenix Scale
Your system can generate structurally identical pages at scale. Google's Helpful Content System penalizes pages where structure, paragraph patterns, and content are interchangeable — regardless of word count. A 4,000-word page assembled from a config file can still read as thin. Length does not solve this. Genuine editorial differentiation does.

4.2 Hub Page Requirements
Each topic hub must contain at least ONE of the following irreplaceable elements — content that could not be generated from a template:
	•	A practitioner observation from Nihala's monastic or therapeutic work (specific, not generic)
	•	A real anonymized case story: specific profession, specific moment, specific outcome
	•	A primary research citation with a specific finding (not 'studies show...')
	•	A quote from a named expert with direct attribution

⚠️  The irreplaceable element must be written or approved by Nihala before the page is built. It is not a placeholder to fill in later. This element determines whether the page ranks or is suppressed.

4.3 Hub Page Structure
URL: /burnout-recovery  (not /burnout-recovery-for-nurses — that's a sub-section)

Sections:
  H1: Identity headline (e.g., 'For People Who Give Too Much')
  Authority narrative (Nihala's — canonical, not regenerated per page)
  What burnout actually is (plain language, 2–3 paragraphs)
  Irreplaceable element (practitioner insight / story / citation)
  The practice (embedded freebie audio + description)
  Persona sub-sections (300–500 words each, NOT separate URLs):
    - Burnout for Healthcare Workers
    - Burnout for Teachers
    - Burnout for Entrepreneurs
    - Burnout for Therapists
  Recommended books (3–5, linked to /books/{slug})
  Email capture form
  Internal links to 3–5 related hubs

4.4 Hub Build Order
Build in this order — highest search intent + lowest competition first:
Priority
Hub URL
Primary Persona Targets
Build After
1
/burnout-recovery
healthcare, educators, therapists
MVP validated
2
/anxiety-breathing
general, executives, new parents
Hub 1 indexed
3
/overthinking-help
tech workers, executives
Hub 1 indexed
4
/grief-breathing
caregivers, healthcare
Hub 2 indexed
5
/somatic-healing
trauma survivors, general
Hub 3 indexed
6–10
Remaining canonical topics
Per canonical_topics.yaml
After 90 days data

⏱️  SEO Timeline Expectation
Months 0–3: content indexed, minimal traffic. Months 4–8: early keyword rankings appear. Months 9–18: cluster authority builds, traffic compounds. Do not evaluate SEO success before month 9. This is a 12–18 month investment, not a launch-day channel.
5. Phase 2 — Freebie to Book Mapping
Add this file to the repo after MVP is validated. It enables the email sequence to generate book recommendations automatically from catalog metadata rather than manually.

5.1 File: freebie_to_book_map.yaml
burnout_reset:
  primary_book: burnout-recovery-healthcare-workers
  secondary_books:
    - compassion-fatigue-reset
    - boundaries-for-caregivers
  series_id: phoenix_burnout_series

anxiety_anchor:
  primary_book: calming-overthinking
  secondary_books:
    - nervous-system-reset
    - panic-relief-guide
  series_id: phoenix_anxiety_series

compassion_restore:
  primary_book: burnout-recovery-healthcare-workers
  secondary_books:
    - compassion-fatigue-reset
    - boundaries-for-caregivers
  series_id: phoenix_burnout_series

# ... one entry per freebie slug

5.2 Book Recommendation Logic
The recommendation engine at MVP stage is a simple lookup, not a behavioral scoring system. Behavioral scoring (weighted clicks + downloads) is a Phase 3 build after you have real usage data.
def recommend_books(exercise_tag, persona=None):
    mapping = load_yaml('freebie_to_book_map.yaml')
    entry = mapping.get(exercise_tag)
    if not entry: return []
    
    primary = entry['primary_book']
    secondary = entry.get('secondary_books', [])
    
    # Persona filter: if persona known, filter secondary to persona-matched first
    if persona:
        persona_matched = [b for b in secondary if persona in catalog[b]['personas']]
        secondary = persona_matched + [b for b in secondary if b not in persona_matched]
    
    return [primary] + secondary[:2]  # Return max 3

⚠️  Do not build a weighted behavioral scoring system (freebie_download +10, email_click +6, etc.) until you have at least 1,000 subscribers with behavioral data. Premature scoring architecture adds database complexity with no measurable benefit at launch.
6. Phase 2 — Series Upsell
6.1 Trigger Conditions
Trigger
Action
Delay
Book link clicked from Email 4
Add to series_upsell automation
Immediate
No book click after Email 4
Add to re-engagement sequence
+14 days after Email 4
90 days no email open
Add to win-back sequence
Auto

6.2 Series Upsell Email (1 email)
Subject: You started something. Here's where it goes.

Body:
  You downloaded [EXERCISE] and you're working with [BOOK_1].
  I want to show you the full path.

  [SERIES_NAME] is a [N]-book journey:
  Book 1: [TITLE] — Foundation (you are here)
  Book 2: [TITLE] — Integration
  Book 3: [TITLE] — Embodiment

  Each builds on the last.
  When you're ready: [BOOK_2_LINK]

  Keep practicing,
  [AUTHOR_NAME]

UTM: utm_campaign={exercise_tag}&utm_content=series_upsell_email1
7. Traffic Strategy
7.1 Priority Order
📊  Traffic Hierarchy for Phoenix Protocol
SEO (topic hubs) is the primary long-term engine. Social is the accelerant. Do not invert this. A system with strong SEO and weak social outlasts a system with strong social and weak SEO.

Channel
Role
When to Activate
Notes
Personal network
MVP validation traffic
Now
Only source with reliable conversion data for MVP test
LinkedIn
Warm professional traffic
MVP launch
Article: 'Why burnout is nervous system overload, not weakness'
SEO (topic hubs)
Primary long-term engine
Phase 2
12–18 month investment. Authority first, scale second.
Pinterest
Visual traffic accelerant
Phase 2, after SEO
5 pins per freebie. Test. Scale only winning formats.
YouTube/TikTok
Awareness + trust
Phase 2
Short practice demos. Link to freebie page in bio.
Reddit/Quora
Tactical only
Phase 2
Requires weeks of genuine community participation first. Not a launch channel.
Podcast
Catalog promotional tool
Phase 3
Only after freebie audio library proves which exercises convert best.

7.2 Pinterest — Correct Approach
Pinterest rewards consistency and re-pinning of high-performing content, not volume. The correct workflow:
	•	Create 5 pin styles per freebie (not 30)
	•	Post over 2 weeks — one pin every 2–3 days
	•	At day 14: identify top performer by saves and clicks
	•	Create 10 variations of the top-performing style only
	•	Never bulk-upload — algorithm treats it as spam

7.3 SEO — Cluster Ownership Strategy
The opportunity is not individual keyword volume — it is owning a cluster of 40–80 low-competition long-tail terms per topic. Individual terms may have 20–50 searches/month. Owning 60 terms in a cluster = 1,200–3,000 monthly visitors from one hub over time.

Example cluster for /burnout-recovery:
burnout recovery breathing
nervous system burnout
somatic burnout exercises
burnout for nurses
burnout for teachers
burnout for therapists
compassion fatigue breathing
vagal tone burnout
how to recover from burnout naturally
... (50+ related terms)
8. Decisions Required Before Build Starts
The developer cannot start without answers to these questions. They are listed in order of blocking priority.

#
Decision
Options
Blocking?
1
Where does the MVP page live?
Existing PhoenixProtocolBooks.com CMS / New subdomain / Static HTML hosted separately
YES — changes entire build approach
2
What is the primary burnout book to recommend?
Must be a real title from the catalog
YES — needed for Email 4 and page
3
Does Nihala approve Brevo as email platform?
Brevo / MailerLite (backup)
YES — determines automation setup
4
Who writes Email 3 (the story)?
Nihala / editor with Nihala approval
YES — cannot be generated
5
Who writes the authority narrative?
Nihala (dictate or write) + editor
YES — highest SEO and trust impact
6
Formspree → Brevo: code or no-code?
Make.com (no-code) / Direct API (code)
YES — determines implementation path
7
Book link routing?
Via PhoenixProtocolBooks.com/books/{slug} redirect / Direct Amazon
Strongly recommended: via your domain
9. Explicitly Out of Scope for MVP
These items are listed because they appeared in planning discussions and may seem urgent. They are not. Build them after MVP validation only.

Feature
Why Out of Scope Now
When to Build
Weighted behavioral scoring engine
Requires 1,000+ subscribers with behavioral data to calibrate
Phase 3
Recommendation engine (complex)
freebie_to_book_map.yaml simple lookup is sufficient until scale
Phase 3
Multi-locale pipeline
en-US only until funnel proves conversion in English
Phase 3
Podcast distribution
Freebie audio library must prove which content converts first
Phase 3
20 SEO hubs simultaneously
Thin content risk — 10 strong hubs beat 100 weak ones
Phase 2, 1 at a time
Pinterest at scale (30 pins/freebie)
Algorithmic penalty for bulk upload; test 5 first
Phase 2
Series bundle pages
Need conversion data to know which series resonates
Phase 2
Author persona branding (many authors)
Maximum 3–4 consolidated author personas; more fragments authority
Phase 2
10. Implementation Checklist
Week 1: Infrastructure
	•	☐  Answer all 7 decisions in Section 8
	•	☐  Nihala writes authority narrative paragraph
	•	☐  Nihala writes or approves Email 3 story
	•	☐  Create Brevo account + set up 8 contact attribute fields
	•	☐  Create list: burnout_reset in Brevo
	•	☐  Set up Formspree → Brevo connection (Make.com or API)
	•	☐  Set up /books/{slug} redirect page for primary burnout book

Week 2: Build
	•	☐  Build /burnout-reset page with all 6 sections
	•	☐  Implement form with hidden fields + UTM capture JS
	•	☐  Build /free/burnout-reset thank-you page with audio player
	•	☐  Load 4-email sequence into Brevo automation
	•	☐  Install GA4 + configure 4 custom events
	•	☐  Test full flow: page → form → email → sequence triggers

Week 3: Launch & Measure
	•	☐  Share to personal network only — document traffic source in UTM
	•	☐  Post LinkedIn article — separate UTM campaign
	•	☐  Monitor GA4 daily: page views, signups, book clicks
	•	☐  Monitor Brevo: email open rates, click rates
	•	☐  At 100 visitors: evaluate against Section 2.9 benchmarks
	•	☐  Identify what to adjust before scaling



Phoenix Protocol Books · Marketing Funnel Developer Spec v1.0
SpiritualTech Systems · Questions: direct to Nihala before building
