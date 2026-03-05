
AUDIOBOOK PUBLISHING
OPERATIONS MANUAL

Performance Baselines • Channel Economics • Testing Framework
Metadata Governance • Brand Architecture • Compliance
Localization Policy • Release Cadence

SpiritualTech Systems • Confidential • February 2026

1. Performance Baselines by Persona × Template
The following benchmarks are derived from industry data across Google Play, Spotify, Audible, and independent audiobook publishers operating at scale in the self-help category. These are realistic targets for AI-narrated, persona-targeted titles at the price points and runtimes in your system. Human-narrated titles typically perform 15–25% above these baselines.
1.1 Funnel Metrics by Template
Each template has a distinct conversion profile based on runtime, price point, and buyer psychology. The table below shows expected performance across the purchase funnel.
Template
CTR (Search)
Sample-to-Buy
Completion
Review Rate
Refund Rate
Phoenix Drop (21-day)
3.2–4.5%
12–18%
38–45%
4–6%
5–8%
Morning Weapon (5-min)
4.0–6.0%
18–25%
62–75%
6–9%
3–5%
Somatic Rescue (30-day)
2.5–3.8%
10–15%
30–40%
5–8%
6–9%
Identity Claim (story)
3.5–5.0%
14–20%
45–55%
7–10%
4–7%
Quiet Protocol (90-day)
2.0–3.0%
8–12%
22–30%
6–9%
7–10%
Silent Authority
2.8–4.0%
10–16%
40–50%
5–7%
5–8%
Relationship Repair
3.0–4.5%
12–18%
35–45%
5–8%
6–8%
Money Mirror
3.5–5.5%
15–22%
50–60%
6–8%
4–6%
Micro Reset (utility)
5.0–7.0%
20–30%
N/A (non-linear)
8–12%
2–4%
Night Dissolve
2.8–4.2%
12–18%
55–70%*
5–7%
3–5%
Habit Engine
2.5–3.5%
10–15%
35–45%
4–6%
5–8%

*Night Dissolve completion is inflated because listeners fall asleep and the chapter finishes. This still counts as a completion for algorithmic purposes, which is why it’s strategically valuable.
1.2 Performance Variance by Persona
Not all personas convert equally. The table below shows relative performance multipliers against the template baselines above. A 1.0x means baseline performance; above 1.0x means that persona over-performs on that metric.
Persona
CTR Mult.
Sample-to-Buy
Completion
Review Rate
Refund Risk
P5: Millennial Women
1.2x
1.15x
1.1x
1.3x
0.8x (low)
P6: Gen X Sandwich
0.9x
1.1x
0.9x
0.7x
0.7x (low)
P7: Tech/Finance
1.1x
1.0x
0.85x
0.6x
1.2x (high)
P8: Entrepreneurs
1.0x
1.2x
0.8x
0.9x
1.1x
P9: Working Parents
1.15x
1.1x
0.75x
1.1x
0.9x
P10: Corporate Managers
0.85x
0.95x
0.9x
0.5x
0.8x
Gen Z
1.4x
0.85x
0.7x
1.5x
1.3x (high)
Gen Z Professionals
1.2x
0.9x
0.8x
1.2x
1.1x
Healthcare RNs
1.0x
1.15x
0.95x
1.2x
0.7x (low)
Gen Alpha
1.3x
0.7x
0.6x
0.8x
1.4x (high)

Key Insight: The Revenue Formula
Revenue per title = CTR × Sample-to-Buy × Price × Volume
Your highest revenue per title: P6 Gen X × Quiet Protocol ($24.99, low refund, high price tolerance)
Your highest total revenue: P5 Millennial Women × Phoenix Drop (volume × strong conversion × reviews that compound)
Your best ROI (revenue per production dollar): Morning Weapon × Gen Z (cheapest to produce, highest completion, most reviews)
1.3 Red-Flag Thresholds
Pull a title for review if any metric falls below these floors within the first 90 days:
Metric
Floor
Action if Below
CTR
< 1.5%
Title/cover A/B test immediately
Sample-to-Buy
< 6%
Re-evaluate sample chapter selection or audio quality
Completion
< 20%
Content quality issue — review chapter pacing and narrator
Review Rate
< 2%
Add in-audio review prompt at chapter 3 and final chapter
Refund Rate
> 15%
Possible misleading title/description or quality failure — investigate
Star Rating
< 3.5
Quality emergency — pull from promotion, investigate root cause

2. Channel-Level Economics
2.1 Revenue Share & Unit Economics
Channel
Revenue Share
Pricing Control
Net per $14.99 Title
Discovery Model
Google Play
48% to author/publisher
Full control
~$7.19
Search + algorithmic recommendation
Spotify (streaming)
$0.005–$0.02/min
No per-title control
~$1.50–$6.00 per full listen*
Playlist + recommendation engine
Spotify (premium)
15-hr included in Premium
No control
Pool-based royalty
High discovery, low per-unit
Owned (email/social)
100% after processing
Full control
~$13.50–$14.24
Email list + social funnel
Audible (ACX)
25–40% royalty
Limited
~$3.75–$6.00
Audible search + credits
*Spotify streaming revenue varies dramatically by listen duration. Short titles (Morning Weapon, Micro Reset) earn less per listen but accumulate more total listens. Long titles (Quiet Protocol, Somatic Rescue) earn more per full listen but fewer total listens.
2.2 CAC and LTV by Channel
Channel
Est. CAC
Est. 12-Month LTV
LTV:CAC
Notes
Google Play (organic)
$0
$8–$12
∞
Free discovery — your catalog density IS the acquisition strategy
Google Play (paid ads)
$3–$8
$8–$12
1.5–4x
Google Ads for audiobooks is immature; low competition = low CPC
Spotify (organic)
$0
$3–$8
∞
Algorithmic placement from completion rates and replays
Spotify (playlist)
$0.50–$2
$3–$8
2–16x
Playlist placement deals with curators
Email list (owned)
$0.10–$0.50*
$15–$25
30–250x
Best LTV channel — direct sales at full margin
TikTok/social
$1–$5
$5–$10
1–10x
Volatile; best for Identity Claim titles that are shareable
Audible
$0
$4–$7
∞
Organic only — Audible ads not available for self-pub
*Email CAC assumes you’re building the list via free content, lead magnets (free Micro Reset chapters), and social media funnels through 48 Social. The $0.10–$0.50 reflects amortized content creation cost per subscriber.
2.3 Channel Strategy by Template
Template
Primary Channel
Secondary
Rationale
Phoenix Drop
Google Play
Spotify
Mid-price, mid-length — ideal for ownership purchase
Morning Weapon
Spotify
Google Play
Short, high replay — streaming rewards repeat listens
Somatic Rescue
Google Play
Email list
Premium niche — buyers want to own and return to practices
Identity Claim
Spotify + TikTok
Google Play
Shareable titles drive social discovery
Quiet Protocol
Google Play
Email list
Premium price — ownership model, serious buyers
Silent Authority
Google Play
LinkedIn ads
Leadership buyers purchase on Google Play; LinkedIn targets them
Relationship Repair
Spotify
Google Play
Volume play — relationships is broadest topic
Money Mirror
Google Play
Email list
Financial identity content converts to email subscribers
Micro Reset
Spotify
Email (free lead)
Ultra-short = streaming natural fit; free chapters build email list
Night Dissolve
Spotify
Google Play
Repeat nightly listens = streaming revenue compounding
Habit Engine
Google Play
Spotify
Analytical buyers prefer ownership for reference

The Funnel Architecture
AWARENESS: Spotify streaming (Morning Weapon, Micro Reset, Night Dissolve) — free or low-friction discovery
CONVERSION: Google Play purchase (Phoenix Drop, Somatic Rescue, Identity Claim) — mid-price ownership
RETENTION: Email list (Quiet Protocol, Silent Authority, Money Mirror) — premium, direct, full margin
AMPLIFICATION: TikTok/social (Identity Claim titles) — organic sharing drives awareness loop
Your short titles feed your mid titles feed your premium titles. Never optimize a channel in isolation.

3. A/B Testing Framework
3.1 What to Test (Priority Order)
Not all variables have equal revenue impact. Test in this order:
Priority
Variable
Revenue Impact
Test Method
1
Title
40–60% of CTR
Publish 2–3 title variants as separate listings; measure CTR at 500+ impressions each
2
Cover
20–35% of CTR
A/B within same listing if platform allows; otherwise parallel listings
3
Subtitle
10–20% of CTR
Swap subtitle on existing listing; compare 2-week windows
4
Sample chapter selection
15–25% of sample-to-buy
Change which chapter plays as sample; measure conversion over 2 weeks
5
Description copy
5–15% of sample-to-buy
Rewrite description; compare conversion over 2-week windows
6
Price
Direct revenue impact
Test $9.99 vs $12.99 vs $14.99 on same title over 3-week windows
7
Narrator voice
10–20% of completion
Publish same title with 2 different ElevenLabs voices; compare completion + reviews
3.2 Decision Thresholds
Do not make decisions on small sample sizes. Minimum thresholds before declaring a winner:
Metric
Minimum Sample
Minimum Difference
Decision Window
CTR
500 impressions per variant
> 0.5% absolute difference
7–14 days
Sample-to-Buy
200 sample plays per variant
> 3% absolute difference
14–21 days
Completion Rate
100 purchases per variant
> 8% absolute difference
30–45 days
Review Rate
200 purchases per variant
> 1.5% absolute difference
45–60 days
Refund Rate
150 purchases per variant
> 3% absolute difference
30 days
Price Test
100 purchases per price point
Revenue per impression, not just conversion
21–28 days
3.3 Title Testing Rules
Title Formula Components
	•	Hook: The emotional entry point. Test the biggest emotional word. “Breakdown” vs “Burnout” vs “Collapse.”
	•	Frame: The program container. Test the time frame. “21 Days” vs “30 Days” vs “4 Weeks.”
	•	Identity: The who. Test specificity. “A Woman’s Reset” vs “A Professional’s Reset” vs “An Introvert’s Reset.”
	•	Promise: The destination. Test the outcome. “Reset” vs “Recovery” vs “Rebuild.”
Testing Protocol
	•	Test ONE variable at a time. Never change title + cover simultaneously.
	•	Run each variant for minimum 7 days before evaluating (platform algorithms need time to stabilize).
	•	Always keep a “control” — your best-performing existing title in that template/persona slot.
	•	Document every test in a central spreadsheet: title variant, dates, impressions, CTR, conversions, revenue.
	•	Once a winner is established, roll the winning element into all future titles in that template.
3.4 Cover Testing Rules
	•	Covers must be legible at thumbnail size (120×120 pixels). If title text is unreadable at thumbnail, redesign.
	•	Test color palette first (warm vs cool), typography second (serif vs sans-serif), imagery third.
	•	Avoid faces on covers for AI-generated content — uncanny valley risk increases refund rates.
	•	Use abstract/symbolic imagery, gradient backgrounds, or bold typography-forward designs.
	•	Each template should have a recognizable visual family while being distinct from other templates.

4. Metadata Governance
At 1,000–4,000 titles, metadata uniqueness is the difference between a thriving catalog and a spam flag. These rules are non-negotiable.
4.1 Title Uniqueness Rules
Rule
Requirement
Example
No duplicate titles
Every title must be unique across entire catalog
Cannot have two books called “21 Days After the Breakdown”
3-word minimum difference
Any two titles must differ by at least 3 words
“21 Days After the Breakdown: A Nurse’s Reset” vs “21 Days After the Burnout: A Parent’s Recovery” — OK
No formulaic repetition
Avoid identical structures across > 5 titles
Cannot have 20 titles all formatted as “[X] Days After the [Y]: A [Z]’s [W]”
Subtitle must add unique value
Subtitle cannot repeat title words
“Stop the Spiral” (title) + “A 5-Minute Guide to Stopping Spirals” (subtitle) — BAD
4.2 Description Uniqueness Rules
Rule
Requirement
Word count
150–400 words per description. Under 150 looks thin. Over 400 gets truncated.
Unique opening sentence
First sentence must be unique across all titles. This is what appears in search results.
No boilerplate blocks
Never copy-paste identical paragraphs across descriptions. Platform text-matching will flag this.
Template variation
Create 5–8 description templates per book template. Rotate systematically across persona and topic variations.
Keyword density
Max 3 repetitions of primary keyword per description. More = keyword stuffing flag.
No cross-referencing
Descriptions should not mention other books in your catalog. This signals mass production.
4.3 Keyword & Category Rules
Rule
Details
Keywords per title
7–10 keywords. Mix broad (“anxiety”) with long-tail (“anxiety recovery for nurses”).
No keyword duplication
No two titles should share more than 4 of the same keywords.
Category spread
Distribute titles across minimum 8 categories. Never place more than 15% of catalog in one category.
Category rotation
Rotate category assignments quarterly to avoid clustering signals.
Competitor keyword gap
For each persona, research which keywords top competitors rank for and target gaps they miss.
4.4 Category Distribution Map
Category
Max % of Catalog
Best Templates
Best Personas
Self-Help / Anxiety & Stress
12%
Phoenix Drop, Somatic Rescue, Micro Reset
P5, P7, Gen Z
Self-Help / Personal Growth
12%
Identity Claim, Morning Weapon
P5, P8, Gen Z
Health & Wellness / Mental Health
10%
Phoenix Drop, Night Dissolve
P5, P9, RNs
Business / Leadership
10%
Silent Authority, Quiet Protocol
P6, P10, P8
Business / Productivity
8%
Habit Engine, Morning Weapon
P7, P8, P10
Self-Help / Relationships
10%
Relationship Repair
P5, P9, Gen Z
Health & Wellness / Mindfulness
8%
Somatic Rescue, Night Dissolve
P5, P6, P9
Self-Help / Financial
8%
Money Mirror
P5, P6, P8
Psychology / Behavioral Science
8%
Habit Engine, Identity Claim
P7, P10
Other / Emerging
14%
Overflow and niche titles
All

Spam Detection Signals to Avoid
Same author name on > 50 titles released in < 90 days — use 3–5 distinct pen name brands (see Section 5)
Identical audio fingerprint across multiple titles — vary ElevenLabs voice per template cluster
Description text similarity > 60% between any two titles — use your description template rotation system
Burst publishing > 20 titles/week from same account — stagger releases (see Section 7)
Category concentration > 15% in single category — spread across minimum 8 categories
Keyword stuffing in title/subtitle — max 2 keywords in title, 2 in subtitle

5. Brand Architecture & Positioning System
With thousands of titles, you need a brand structure that prevents the catalog from looking like a content farm while still allowing massive scale. The system below creates perceived intentionality.
5.1 Imprint/Pen Name Architecture
Do not publish all titles under one name. Create 3–5 imprints (pen name brands), each with a distinct positioning and visual identity.
Imprint
Positioning
Templates
Personas
Visual Identity
Imprint A: “Calm” Brand
Gentle, therapeutic, body-based healing
Somatic Rescue, Night Dissolve, Micro Reset
P5, P9, RNs
Soft gradients, muted earth tones, sans-serif
Imprint B: “Edge” Brand
Direct, high-performance, no-nonsense
Morning Weapon, Habit Engine, Silent Authority
P7, P8, P10
Bold typography, dark backgrounds, sharp lines
Imprint C: “Rise” Brand
Aspirational, identity transformation, story-driven
Phoenix Drop, Identity Claim, Money Mirror
P5, P6, Gen Z
Warm colors, sunrise imagery, expressive type
Imprint D: “Root” Brand
Deep work, long-form recovery, clinical credibility
Quiet Protocol, Relationship Repair
P6, P10, P8
Minimal, white space, serif typography
5.2 Visual Consistency Rules
	•	Each imprint has a fixed color palette (3 colors max), typography family (1 header + 1 body font), and cover layout template.
	•	Within an imprint, covers should be recognizable as a family but distinct per title. Think: same spine design, different hero element.
	•	Across imprints, covers should look like they come from different publishers. No shared design elements.
	•	Never use the same cover template across imprints. A buyer who discovers titles from two imprints should not realize they’re from the same publisher unless they investigate.
5.3 Author Persona Guidelines
	•	Each imprint has a consistent author name. This name appears on all titles within that imprint.
	•	Author bios should be distinct per imprint. The “Calm” brand author has a wellness/therapeutic background. The “Edge” brand author has a performance/executive background.
	•	Do not cross-promote between imprints in descriptions, author bios, or metadata. They should appear as independent publishers.
	•	SpiritualTech Systems remains the backend publisher entity but is not consumer-facing on any imprint.
5.4 Series Architecture
Group titles into series within each imprint to create algorithmic clustering that works FOR you rather than against you. When a buyer purchases one title in a series, the platform recommends the rest.
Series Strategy
Structure
Example
Persona series
All titles for one persona within one template
“The Nurse’s Reset Collection” — Phoenix Drop, Morning Weapon, Somatic Rescue for RNs
Template series
All persona variants of one template
“The 21-Day Reset Series” — Phoenix Drop for nurses, parents, executives, Gen Z
Topic series
All titles on one topic across templates
“Anxiety Recovery Library” — Phoenix Drop, Micro Reset, Night Dissolve on anxiety
City series
All localized titles for one city
“New York Reset Collection” — localized Phoenix Drops + Morning Weapons for NYC
Use persona series as your default. These create the tightest recommendation loops because the buyer has already self-identified with that persona.

6. Compliance: Therapeutic & Mental Health Claims
Self-help audiobooks that reference anxiety, depression, trauma, PTSD, somatic healing, and nervous system regulation operate in a regulatory gray zone. The rules below protect you from platform removal, legal risk, and consumer complaints.
6.1 Claim Boundaries
Category
Allowed
NOT Allowed
Emotional support
“Strategies to help manage feelings of anxiety”
“Cures anxiety” / “Treats anxiety disorder”
Behavioral change
“Practices to build healthier habits”
“Clinic-tested treatment protocol”
Somatic practices
“Breathing exercises for stress relief”
“Vagal nerve therapy” / “Nervous system treatment”
Trauma
“Support for processing difficult experiences”
“Trauma therapy” / “PTSD treatment”
Clinical terms
“Inspired by CBT/ACT principles”
“CBT therapy program” / “Clinical ACT protocol”
Outcomes
“Many listeners report feeling calmer”
“Proven to reduce anxiety by 47%”
Professional equivalence
“Complement to your wellness practice”
“As effective as therapy” / “Replacement for medication”
6.2 Required Disclaimers
In-Audio Disclaimer (Required in every title)
Place at the beginning of Chapter 1, before any content. Spoken by the narrator in the same voice:

Standard Disclaimer Script
“This audiobook is designed for educational and self-improvement purposes. It is not a substitute for professional medical or psychological treatment. If you are experiencing a mental health crisis, please contact a qualified healthcare provider or call 988 (Suicide & Crisis Lifeline) for immediate support. The practices in this book are intended to complement, not replace, professional care.”
In-Description Disclaimer (Required in every listing)
Place at the end of every product description:

Standard Description Disclaimer
“This title is for educational and self-improvement purposes only and does not constitute medical or psychological advice. Consult a qualified professional for diagnosis or treatment of any mental health condition.”
6.3 Category-Safe Wording by Topic
Topic
Safe Terms
Flagged Terms to Avoid
Anxiety
worry, overwhelm, racing thoughts, unease, stress
anxiety disorder, GAD, clinical anxiety, diagnosis
Depression
low mood, emotional heaviness, feeling stuck, dark days
clinical depression, MDD, depressive episode, suicidal
Trauma
difficult experiences, past wounds, emotional pain
PTSD, C-PTSD, trauma disorder, traumatic brain injury
Somatic
body-based practices, breathwork, physical awareness
vagal nerve stimulation therapy, somatic therapy, clinical
Addiction
unhealthy patterns, compulsive habits, dependency
addiction treatment, substance abuse therapy, rehab
Eating
relationship with food, nourishment mindset
eating disorder, anorexia, bulimia, ED recovery
6.4 Platform-Specific Rules
	•	Google Play: Audiobooks flagged for medical claims can be removed without warning. Err heavily on the side of caution. Google’s content moderation is automated and does not distinguish nuance.
	•	Spotify: Less strict on claims in descriptions but still subject to Spotify’s content policy. Avoid any language suggesting clinical treatment.
	•	Audible/ACX: Most stringent. Audible has human reviewers and has rejected titles for using “therapy” in descriptions of non-clinical content.

7. Localization Policy
7.1 City Qualification Matrix
Not every city justifies localization. Qualify based on population density of target persona, strength of city identity, and audiobook market penetration.
Tier
Cities
Personas Qualified
Templates to Localize
Annual Titles
Tier 1 (mandatory)
New York, Los Angeles, Chicago
P5, P7, P9, P10, RNs
Phoenix Drop, Morning Weapon
60–80
Tier 2 (strong)
San Francisco, Seattle, Austin, Houston
P7, P8, RNs (Houston)
Phoenix Drop, Morning Weapon
40–60
Tier 3 (selective)
Miami, Boston, Denver, DC, Atlanta
P5, P8, P10
Phoenix Drop only
20–30
Skip
All other US cities
—
—
0
7.2 Local Cue Authenticity Standards
Every localized title requires a city cue sheet of 15–20 vetted sensory details. Cues must pass the “Local Cringe Test”: would a 5-year resident roll their eyes at this detail?
Cue Categories (Required per City)
Category
Examples (NYC)
Examples (Austin)
Vetting Method
Transit/Commute
6 train, L train, BQE traffic, Penn Station crush
I-35 at MoPac, the 183 merge, MetroRail
Reddit r/[city], Google Maps commute forums
Weather/Sensory
August subway platform heat, March wind off the Hudson
Cedar fever season, July heat at 6am
Local weather blogs, seasonal complaint threads
Neighborhoods
Washington Heights bodega, Park Slope stroller traffic
East Austin vs Mueller, South Lamar traffic
Local real estate + community threads
Food/Daily Life
Dollar slice at 11pm, halal cart line
Breakfast tacos at 7am, HEB parking lot
Yelp, local food media
Work Culture
Midtown elevator silence, FiDi lunch rush
Tech campus ping pong tables, remote work coffee shops
Glassdoor, local business media
Emotional Texture
Alone in a crowd of 8 million
Keeping up with the Austin hustle
Literature, essays, local podcasts
Disqualified Cue Types
	•	Tourist landmarks as primary reference: “You’re passing the Statue of Liberty” — no local thinks about this.
	•	Outdated references: Restaurants that closed, transit lines that changed, neighborhoods that gentrified beyond recognition.
	•	Stereotypes: “You grab your cowboy hat” (Austin) or “You’re doing yoga on the beach” (LA) — clichés break trust.
	•	Hyper-specific addresses: “You’re at 347 West 42nd Street” — too precise, feels surveillance-like rather than relatable.
7.3 Localization QA Checklist
Check
Pass Criteria
Fail Action
Cue accuracy
All transit names, neighborhoods, and landmarks verified current
Replace with verified alternative
Local cringe test
3 residents from target city review cue list with no objections
Remove or replace flagged cues
Emotional resonance
Cues trigger recognition (“that’s my life”), not tourism (“I’ve visited there”)
Replace with deeper local texture
Density balance
1–2 local cues per chapter maximum. Not every sentence needs a city reference.
Thin out — local cues should season, not overwhelm
Generalizability
If a non-local accidentally buys this title, local cues do not make content useless
Ensure core practices work without local context

8. Release Cadence & Promotional Calendar
8.1 Launch Wave Structure
Do not release all titles simultaneously. Stagger releases in waves that build catalog density without triggering spam detection and that align with seasonal demand.
Phase
Timeline
Titles
Focus
Goal
Seed Wave
Months 1–2
50–75 titles
Phoenix Drop × all 10 personas × top 2 topics. General only, no city variants.
Establish catalog footprint. Test title/cover formulas. Gather baseline data.
Volume Wave
Months 3–4
100–150 titles
Add Morning Weapon + Micro Reset. Begin city variants for Tier 1 cities.
Build Spotify streaming volume. Create funnel entry points.
Depth Wave
Months 5–6
150–200 titles
Add Somatic Rescue + Identity Claim + Night Dissolve. Expand city variants to Tier 2.
Differentiate catalog. Establish somatic healing moat. Drive premium purchases.
Premium Wave
Months 7–8
100–150 titles
Add Quiet Protocol + Silent Authority + Relationship Repair. Email list launch.
Capture high-LTV buyers. Build direct sales channel.
Scale Wave
Months 9–12
200–300 titles
Habit Engine + Money Mirror. Fill remaining persona/topic/city gaps. Catalog padding with diversity titles.
Complete the catalog. Trigger algorithmic recommendation loops at density threshold.
8.2 Weekly Release Cadence
Rule
Details
Max titles per week per imprint
8–10. More than this risks burst-publishing flags.
Max titles per week total (all imprints)
25–30. Distributed across 3–4 imprints = 7–8 per imprint.
Release days
Tuesday and Thursday — highest audiobook discovery traffic on Google Play.
Avoid
Never release > 5 titles in the same category in the same week.
Stagger imprints
Imprint A releases Tuesday. Imprint B releases Thursday. Imprint C releases following Tuesday. Rotate.
8.3 Seasonal Alignment
Season
Peak Topics
Templates to Push
Personas to Target
Promo Strategy
January (New Year)
Habit formation, productivity, financial wellness
Morning Weapon, Habit Engine, Money Mirror
P7, P8, P5
Bundle “New Year Reset” collections at 20% discount
March–April (Spring)
Relationships, identity, fresh starts
Identity Claim, Relationship Repair
P5, P9, Gen Z
Social media campaign around “Spring Reset”
May (Mental Health Month)
Anxiety, depression, somatic healing
Phoenix Drop, Somatic Rescue, Micro Reset
All personas
Free Micro Reset chapters as lead magnets. Full catalog push.
August–Sept (Back to School/Work)
Productivity, leadership, career
Silent Authority, Habit Engine, Morning Weapon
P10, P7, Gen Z Pro
LinkedIn campaign for leadership titles
October (World Mental Health Day)
Mental health, resilience, burnout
Phoenix Drop, Night Dissolve
P5, P7, RNs
Awareness partnerships + free chapter drops
November–December (Holidays)
Relationships, family stress, identity
Relationship Repair, Identity Claim, Night Dissolve
P9, P5, P6
Gift bundle positioning: “Give the Gift of Calm”
8.4 Backlist Refresh Strategy
Titles are not “publish and forget.” Backlist optimization is where long-term revenue compounds.
Action
Frequency
Trigger
Expected Impact
Title/subtitle refresh
Every 6 months
CTR < 2% or sales decline > 30%
15–25% CTR lift
Description rewrite
Every 6 months
Sample-to-buy < 8%
10–15% conversion lift
Cover refresh
Every 12 months
CTR decline or visual trend shift
10–20% CTR lift
Category reassignment
Every 3 months
Category becomes saturated (> 15% of catalog)
Improved ranking in less competitive category
Price optimization
Every 3 months
Revenue per impression declining
Variable — test before committing
Sample chapter swap
Every 6 months
Sample-to-buy < 8%
15–25% conversion lift
Narrator voice update
As new voices become available
Completion < 25% or quality complaints
10–20% completion lift
8.5 Promotional Calendar Template
Week
Monday
Wednesday
Friday
Week 1
New title releases (8–10)
Email blast: new releases to list
Social post: excerpt from Identity Claim title
Week 2
New title releases (8–10)
Spotify playlist pitch for Morning Weapon titles
TikTok/Instagram: Identity Claim title hook
Week 3
Backlist refresh (update 5–10 underperformers)
Email blast: themed collection (“Anxiety Recovery Week”)
Social proof post: reviews from top-performing titles
Week 4
New title releases (8–10)
Performance review: pull red-flag titles, plan A/B tests
Community engagement: respond to reviews, gather feedback

The Compounding Effect
Month 1–3: You’re building. Revenue is modest. Focus on testing and data collection.
Month 4–6: Algorithmic recommendation starts kicking in. Titles with strong completion rates surface organically.
Month 7–9: Email list reaches critical mass. Direct sales channel provides predictable revenue independent of platform algorithms.
Month 10–12: Catalog density triggers recommendation loops. New titles launch into an existing ecosystem that cross-promotes them automatically.
Year 2+: Backlist revenue exceeds new release revenue. The catalog becomes a compounding asset. Your job shifts from production to optimization.
