# PHOENIX CATALOG PLANNING: UNIFIED PERSONAS & TOPICS
## Complete Metadata for 10 Target Personas + 12 Canonical Topics
**Date:** February 2026 | **System:** Phoenix V4 | **Target:** 1,008 books / 24 brands / 12 months

---

## PART 1: PERSONA REGISTRY (10 Canonical Production Personas)

### Revenue Tier Assignment

| Tier | Persona ID | Display Name | Revenue Est. (US Annual) | Atom Status |
|------|-----------|--------------|-------------------------|-------------|
| **1** | `millennial_women_professionals` | Millennial Women Professionals | $130–165M | **NEW — No atoms** |
| **1** | `tech_finance_burnout` | Tech & Finance Burnout Professionals | $80–120M | **PARTIAL — nyc_executives + sf_founders atoms exist** |
| **1** | `entrepreneurs` | Entrepreneurs & Solopreneurs | $60–100M | **PARTIAL — overlaps smb_owners** |
| **2** | `working_parents` | Working Parents of Young Children | $70–100M | **NEW — parents_teens metadata exists, no atoms** |
| **2** | `gen_x_sandwich` | Gen X Sandwich Generation | $165M+ | **NEW — No atoms** |
| **2** | `corporate_managers` | Corporate Middle Managers | $50–80M | **PARTIAL — overlaps nyc_executives** |
| **3** | `gen_z_professionals` | Gen Z Professionals | Included in Tier 1 overlap | **STRONG — most existing atoms** |
| **3** | `healthcare_rns` | Healthcare RNs | Niche ($3.4M workforce) | **GOOD — templates + atoms exist** |
| **3** | `gen_alpha_students` | Gen Alpha Students | Low (no purchasing power) | **PARTIAL — templates exist** |
| **3** | `first_responders` | First Responders | Niche ($2.5M workforce) | **NEW — No atoms** |

---

### PERSONA 1: `millennial_women_professionals`

```yaml
# === SYSTEM METADATA ===
persona_id: millennial_women_professionals
display_name: Millennial Women Professionals
locale: en-US
generation_dialect: millennial
active: true
revenue_tier: 1

# === PRODUCTION PARAMETERS ===
beat_map: phoenix_14
template_packs:
  base: core_self_help_v1
  overrides:
    - emotional_intelligence_pack
    - boundary_strength_pack
language_packs:
  primary: en-US_core_v1
  fallbacks: []

# === VOICE PROFILE ===
voice_tone: warm, direct, evidence-grounded, emotionally intelligent
formality: 0.55
slang_level: 0.25
pace_bpm: 145
pause_default_ms: 300
story_injection_rate: 0.35
breathing_exercise_frequency: 0.30

# === TONE BIAS ===
tone_bias_business: 0.65
tone_bias_scientific: 0.55
tone_bias_spiritual: 0.15
tone_bias_mythic: 0.10
tone_bias_personal: 0.75

# === VOICE DISTINCTION ===
# Voice: emotionally literate but not therapy-speak saturated,
# names feelings precisely, references research casually ("studies show"),
# balances vulnerability with competence, never condescending
# Key differentiator from gen_z: more settled identity, deeper stakes
# (career trajectory, partnership, potential parenthood), less anxious
# about being seen, more anxious about being enough

domain_jargon:
  - boundaries
  - emotional labor
  - capacity
  - bandwidth
  - unpack
  - hold space
  - regulate
  - nervous system

metaphor_style:
  - container/overflow
  - seasons/cycles
  - foundation/structure
  - current/undertow
  - root system

# === PERSONA SCENARIOS ===
persona_scenarios:
  primary_dimension: career_identity
  secondary_dimension: relationships
  integration_dimension: self_relationship
  content_templates:
    primary:
      dimension: your career and professional identity
      scenario_library:
        - the meeting where you stayed silent when you should have spoken
        - the promotion you earned but can't stop second-guessing
        - the Sunday dread that starts before dinner is over
        - the colleague who takes credit and the anger you swallow
        - the performance review that reduced you to a number
    secondary:
      dimension: your relationships
      scenario_library:
        - the partner who doesn't see how much you carry
        - the friend you haven't called because you have nothing left
        - the family dinner where you perform "fine"
        - the dating app that makes loneliness feel like failure
        - the conversation you rehearse but never have
    integration:
      dimension: your relationship with yourself
      scenario_library:
        - the mirror check that became a critique
        - the rest you won't let yourself take
        - the achievement that brought no relief
        - the body scan that revealed tension you didn't know you held
        - the moment you realized you'd been performing wellness

# === TITLE RULES ===
rewrite_config:
  style_notes:
    - Warm but not saccharine. Direct but not cold.
    - Reference evidence casually, never pedantically.
    - Name the emotional truth before offering the tool.
    - Respect intelligence, time, and emotional complexity.
    - Acknowledge systemic pressures without making the book about feminism.
  dialect_rules:
    allow_slang: false
    emoji_ok: false
  forbidden_markers:
    - girlboss
    - lean in
    - manifest
    - queen
    - slay
    - hustle
    - wine o'clock
    - mompreneur
    - tribe
  title_rules:
    min_words: 2
    max_words: 8
    max_chars: 70
    vibe: warm, direct, intelligent; treats her as capable, not broken
    allow_punctuation: [":", "—"]
    banned_punctuation: ["!!!", "??", "..."]
    avoid_words: [bestie, vibes, manifest, girlboss, slay]
    preferred_language: [grounded, clear, precise, honest]
    patterns:
      - "The {Noun} You've Been Carrying"
      - "When {Symptom} Is Actually {Mechanism}"
      - "{Verb} Without {Cost}"
      - "What {Trigger} Is Really About"
    subtitle:
      enabled: true
      max_chars: 90
      style: benefit-forward, mechanism-aware, respects her intelligence

# === EMOTIONAL APPROPRIATENESS ===
emotional_appropriateness:
  identity_assumptions:
    appropriate:
      - Navigating career pressure alongside relationship complexity
      - Managing invisible emotional labor at work and home
      - Carrying high competence alongside quiet self-doubt
      - Balancing evidence-seeking with emotional overwhelm
    inappropriate:
      - Assuming she needs permission to have ambition
      - Treating her stress as "drama" or overreaction
      - Centering romantic relationship as primary identity
  tone_requirements:
    avoid:
      - Patronizing reassurance ("You're doing amazing, sweetie")
      - Toxic positivity or gratitude shaming
      - Reducing her to her relationship status
    prefer:
      - Naming the mechanism before offering the solution
      - Validating the structural pressures, not just the feeling
      - Direct, warm, competent tone

# === LOCAL ENVIRONMENT ===
local_environment:
  morning_routine:
    - the alarm that feels like a starter pistol
    - the 20 minutes between waking and performing
    - the commute where the mask goes on
  workspace:
    - the open-plan office where everyone can hear you breathe
    - the Slack notification that spikes your cortisol
    - the meeting where you over-prepare to feel safe
  mid_day:
    - the lunch you eat at your desk pretending it's productive
    - the 3pm wall where the body finally registers the morning
    - the walk around the block that feels like escape
  evening:
    - the apartment that's supposed to feel like sanctuary
    - the workout that's become another performance metric
    - the scroll through Instagram that compares lives
  relationships:
    - the text from the friend you're too drained to answer
    - the partner's question that lands like a demand
    - the family call that makes you 14 again

# === BOOK GENERATION ===
book_generation:
  pain_template: >
    You know what it's like when {topic} settles in—not dramatically, but
    like weather. How it sits in your chest during meetings, follows you
    into the shower, makes rest feel like another thing to fail at.
  location_cues:
    intro: Maybe it happened after a meeting that went sideways,
    body: in the quiet of a Tuesday evening when the doing finally stopped,
    outro: and something in you recognized this couldn't keep going.
  work_context: office_hybrid

# === MARKET DATA ===
market_data:
  us_population: 37M (millennial women)
  audiobook_consumption: 6.8 titles/year
  self_help_purchase_rate: high (70% of all self-help buyers are women)
  primary_platforms: [Spotify, Instagram, Google Play]
  discovery_channels: [BookTok, Instagram Reels, podcasts, email]
  price_sensitivity: moderate ($9.99–$17.99 sweet spot)
  distribution_strategy: spotify_primary_google_secondary

# === TOPIC RESONANCE (ranked) ===
topic_resonance:
  1: overthinking       # anxiety/psychological freedom
  2: boundaries         # communication/relationships
  3: burnout            # resilience/career
  4: self_worth         # emotional regulation
  5: financial_anxiety  # financial wellness

# === TEMPLATE SHARING ===
template_set: millennial_professional_women
shares_templates_with: [mid_career_women_variant]
# Voice is distinct enough to require own template set.
# Cannot share with gen_z (different identity stakes)
# or gen_x (different cultural references, formality level)
```

---

### PERSONA 2: `tech_finance_burnout`

```yaml
persona_id: tech_finance_burnout
display_name: Tech & Finance Burnout Professionals
locale: en-US
generation_dialect: mixed_millennial_gen_z
active: true
revenue_tier: 1

beat_map: phoenix_14
template_packs:
  base: core_self_help_v1
  overrides:
    - energy_budget_pack
    - cognitive_load_pack
language_packs:
  primary: en-US_core_v1
  fallbacks: []

voice_tone: analytical, dry, no-nonsense, quietly exhausted
formality: 0.65
slang_level: 0.15
pace_bpm: 155
pause_default_ms: 260
story_injection_rate: 0.25
breathing_exercise_frequency: 0.25

tone_bias_business: 0.85
tone_bias_scientific: 0.70
tone_bias_spiritual: 0.05
tone_bias_mythic: 0.05
tone_bias_personal: 0.40

# VOICE DISTINCTION:
# Analytical mind applied to own breakdown. Uses systems thinking
# metaphors. Comfortable with data but uncomfortable with feelings.
# "I can debug a distributed system but I can't figure out why
# I'm crying in the parking garage." Dry humor as defense.
# Merges existing nyc_executives voice with tech worker specificity.

domain_jargon:
  - bandwidth
  - pipeline
  - sprint
  - standup
  - PIP
  - calibration
  - scope creep
  - tech debt
  - burn rate
  - runway
  - leverage
  - delta
  - OKRs

metaphor_style:
  - system/crash/reboot
  - signal/noise
  - technical debt (emotional)
  - optimization/diminishing returns
  - stack overflow (emotional)

persona_scenarios:
  primary_dimension: work_performance
  secondary_dimension: relationships
  integration_dimension: self_relationship
  content_templates:
    primary:
      dimension: your work performance and career
      scenario_library:
        - the on-call rotation that became your entire personality
        - the PIP threat that rewired your nervous system
        - the sprint review where you realized you'd built nothing that mattered
        - the AI announcement that made your skillset feel obsolete
        - the Blind post about your company that you can't stop refreshing
    secondary:
      dimension: your relationships
      scenario_library:
        - the partner who says you're "always working" (they're right)
        - the friend group that became a Slack channel
        - the parents who don't understand what you do or why you're tired
    integration:
      dimension: your relationship with yourself
      scenario_library:
        - the meditation app with 200 days logged and no calm
        - the body you optimized into something you can't feel
        - the identity crisis when the company identity disappears

rewrite_config:
  style_notes:
    - Analytical but human. Dry humor is welcome.
    - Use systems/engineering metaphors for emotional concepts.
    - Respect their intelligence — don't oversimplify.
    - Acknowledge the structural absurdity of tech/finance culture.
    - Never suggest the problem is just "work-life balance."
  forbidden_markers:
    - hustle
    - grind
    - 10x
    - growth hacking
    - disrupt
    - synergy
    - move fast and break things
  title_rules:
    vibe: analytical, slightly sardonic, respects their intelligence
    patterns:
      - "The {System} That Crashed"
      - "When {Optimization} Becomes the Problem"
      - "{Verb} Without the {Tech Metric}"
      - "After the {Tech Event}"
    subtitle:
      enabled: true
      max_chars: 90
      style: mechanism-forward, acknowledges the absurdity

emotional_appropriateness:
  identity_assumptions:
    appropriate:
      - High cognitive capacity paired with emotional avoidance
      - Identity fused with professional competence
      - Always-on culture creating chronic dysregulation
      - Imposter syndrome despite measurable achievement
    inappropriate:
      - Assuming they're emotionally unintelligent
      - Treating tech culture as inherently shallow

local_environment:
  morning_routine:
    - the Slack messages that accumulated overnight
    - the standup where you performed energy you don't have
    - the coffee that's become a coping mechanism
  workspace:
    - the open office / home office that never turns off
    - the code review that felt personal
    - the all-hands where the reorg was announced cheerfully
  evening:
    - the decompression ritual that takes longer every week
    - the gym session that's become compulsive
    - the partner's face when you check your phone during dinner

book_generation:
  pain_template: >
    You know what it's like when {topic} shows up—not as a feeling you
    can name, but as a system running hot. The performance metrics are
    green. The human metrics are red. And you've been ignoring the alerts.
  location_cues:
    intro: Maybe it happened in the middle of a sprint,
    body: or in the quiet after a deploy when everything worked but nothing felt right,
    outro: and the dashboard couldn't show you what was actually breaking.
  work_context: office_remote_hybrid

market_data:
  us_population: 12.1M (tech) + 6.3M (finance)
  audiobook_consumption: 9.4 titles/year (highest)
  primary_platforms: [Spotify, Reddit, LinkedIn]
  price_sensitivity: low ($14.99–$39.99 tolerated)
  distribution_strategy: spotify_primary_google_secondary

topic_resonance:
  1: burnout
  2: overthinking
  3: imposter_syndrome
  4: sleep_anxiety
  5: somatic_healing

# MIGRATION NOTE: Absorbs atoms from nyc_executives and sf_founders.
# nyc_executives atoms → tech_finance_burnout with finance variables
# sf_founders atoms → tech_finance_burnout with tech variables
# New template set required (voice is distinct from both predecessors)
template_set: tech_finance_burnout
shares_templates_with: []
migrates_from: [nyc_executives, sf_founders]
```

---

### PERSONA 3: `entrepreneurs`

```yaml
persona_id: entrepreneurs
display_name: Entrepreneurs & Solopreneurs
locale: en-US
generation_dialect: mixed
active: true
revenue_tier: 1

beat_map: phoenix_14
template_packs:
  base: core_self_help_v1
  overrides:
    - energy_budget_pack
    - resilience_pack
language_packs:
  primary: en-US_core_v1
  fallbacks: []

voice_tone: direct, energetic, pragmatic, fellow-traveler
formality: 0.45
slang_level: 0.20
pace_bpm: 150
pause_default_ms: 270
story_injection_rate: 0.30
breathing_exercise_frequency: 0.20

tone_bias_business: 0.90
tone_bias_scientific: 0.35
tone_bias_spiritual: 0.15
tone_bias_mythic: 0.20
tone_bias_personal: 0.55

# VOICE DISTINCTION:
# Talks to them as a peer who's been in the arena.
# Respects risk-taking without romanticizing it.
# "You didn't fail because you're weak. You failed because
# you treated your nervous system like it had infinite runway."
# Higher energy, more action-oriented than tech/finance persona.

domain_jargon:
  - runway
  - pivot
  - burn rate
  - bootstrapped
  - founder mode
  - cash flow
  - churn
  - traction
  - PMF
  - exit

metaphor_style:
  - building/foundation/scaffolding
  - weather/storms/clearing
  - engine/fuel/maintenance
  - frontier/terrain/navigation

persona_scenarios:
  primary_dimension: business_survival
  secondary_dimension: relationships
  integration_dimension: self_relationship
  content_templates:
    primary:
      dimension: your business and financial survival
      scenario_library:
        - the month you couldn't make payroll and told nobody
        - the pitch that went sideways and the silence after
        - the competitor who launched what you've been building
        - the client who ghosted after 3 months of work
        - the spreadsheet that shows 4 months of runway
    secondary:
      dimension: your relationships
      scenario_library:
        - the partner who married you, not your startup
        - the friend who stopped inviting you because you always cancel
        - the parent who asks when you'll get a "real job"
    integration:
      dimension: your relationship with yourself
      scenario_library:
        - the identity crisis when the business IS you
        - the rest day that felt like betrayal
        - the success that brought panic instead of relief

rewrite_config:
  style_notes:
    - Talk to them like a peer, not a patient.
    - Respect the courage of entrepreneurship.
    - Acknowledge financial stakes are real, not theoretical.
    - Never dismiss their ambition as the problem.
    - Solutions must be time-efficient — they won't do 45-minute meditations.
  forbidden_markers:
    - passive income
    - 4-hour work week
    - digital nomad
    - crush it
    - six figures
    - empire
    - boss babe

market_data:
  us_population: 33M small businesses / 582M globally
  audiobook_consumption: 12+ titles/year (highest per capita)
  primary_platforms: [Google Play, Spotify, podcasts]
  price_sensitivity: variable (volume at $5.99–$9.99, premium at $34.99–$49.99)
  distribution_strategy: google_spotify_equal

topic_resonance:
  1: financial_anxiety
  2: burnout
  3: overthinking
  4: self_worth
  5: boundaries

template_set: entrepreneurs
shares_templates_with: []
migrates_from: [smb_owners]
```

---

### PERSONA 4: `working_parents`

```yaml
persona_id: working_parents
display_name: Working Parents of Young Children
locale: en-US
generation_dialect: millennial
active: true
revenue_tier: 2

beat_map: phoenix_14
template_packs:
  base: core_self_help_v1
  overrides:
    - family_boundary_pack
    - compassion_pack
language_packs:
  primary: en-US_core_v1
  fallbacks: []

voice_tone: warm, knowing, unhurried, permission-giving
formality: 0.40
slang_level: 0.25
pace_bpm: 135
pause_default_ms: 340
story_injection_rate: 0.40
breathing_exercise_frequency: 0.35

tone_bias_business: 0.25
tone_bias_scientific: 0.40
tone_bias_spiritual: 0.20
tone_bias_mythic: 0.15
tone_bias_personal: 0.85

# VOICE DISTINCTION:
# Knows their hands are full and their ears are the only free organ.
# Never adds to the should-pile. Names the exhaustion without wallowing.
# "You lost your temper at bath time. That's not a character flaw.
# That's a nervous system that's been on duty for 14 hours."
# Shorter sentences. Gentler pace. More somatic, less cognitive.

domain_jargon:
  - mental load
  - bedtime
  - screen time
  - meltdown (the kid's and yours)
  - sleep regression
  - co-regulation
  - sensory overload
  - village

metaphor_style:
  - container/overflow
  - oxygen mask (used sparingly, acknowledged as cliché)
  - seasons (of childhood, of marriage)
  - anchor/current
  - noise/silence

persona_scenarios:
  primary_dimension: parenting_demands
  secondary_dimension: partnership
  integration_dimension: self_relationship
  content_templates:
    primary:
      dimension: your parenting and family demands
      scenario_library:
        - the morning where everything went wrong before 7:30am
        - the meltdown at checkout where strangers watched
        - the bedtime that took 90 minutes and all your humanity
        - the school email that arrived during a meeting
        - the guilt of choosing work over the school play
    secondary:
      dimension: your partnership
      scenario_library:
        - the argument about dishes that was about everything else
        - the partner you love but can't reach across the exhaustion
        - the night you both scrolled your phones in silence
    integration:
      dimension: your relationship with yourself
      scenario_library:
        - the person you were before kids and the grief of that
        - the body that doesn't feel like yours anymore
        - the 10 minutes alone in the car that felt like salvation

rewrite_config:
  style_notes:
    - Short chapters. They'll be interrupted.
    - Never add to the guilt. Name it, don't amplify it.
    - Exercises must work in 2-5 minutes. No 20-minute meditations.
    - Acknowledge the body is exhausted. Lead with somatic, not cognitive.
    - Humor is welcome — gentle, self-deprecating, recognizing absurdity.
  forbidden_markers:
    - mommy wine culture
    - supermom
    - blessed
    - cherish every moment
    - it goes so fast
    - mompreneur
    - hot mess

market_data:
  us_population: 63M parents with children under 18
  audiobook_consumption: 6.8+ titles/year (hands-free format = natural fit)
  primary_platforms: [Spotify, Facebook, Instagram]
  price_sensitivity: high ($7.99–$12.99 sweet spot; short-form preferred)
  distribution_strategy: spotify_primary

topic_resonance:
  1: boundaries
  2: overthinking
  3: burnout
  4: self_worth
  5: grief  # intergenerational patterns

template_set: working_parents
shares_templates_with: []
```

---

### PERSONA 5: `gen_x_sandwich`

```yaml
persona_id: gen_x_sandwich
display_name: Gen X Sandwich Generation
locale: en-US
generation_dialect: gen_x
active: true
revenue_tier: 2

beat_map: phoenix_14
template_packs:
  base: core_self_help_v1
  overrides:
    - energy_budget_pack
    - resilience_pack
language_packs:
  primary: en-US_core_v1
  fallbacks: []

voice_tone: pragmatic, wry, no-bullshit, quietly compassionate
formality: 0.65
slang_level: 0.10
pace_bpm: 140
pause_default_ms: 310
story_injection_rate: 0.28
breathing_exercise_frequency: 0.25

tone_bias_business: 0.70
tone_bias_scientific: 0.55
tone_bias_spiritual: 0.10
tone_bias_mythic: 0.10
tone_bias_personal: 0.55

# VOICE DISTINCTION:
# Skeptical of self-help but here anyway. Earned their cynicism.
# "I don't need someone to hold space for me. I need someone to
# explain why I can't sleep when I've done everything right."
# Pragmatic, results-oriented. Give them the mechanism, skip the
# affirmation. Respects their intelligence and their exhaustion.
# Distinct from millennial women: less emotional vocabulary,
# more action-oriented, skeptical of therapy-speak.

domain_jargon:
  - retirement
  - sandwich generation
  - eldercare
  - college fund
  - estate planning
  - mid-career
  - succession
  - downsizing
  - equity
  - second act

metaphor_style:
  - machine/maintenance/wear
  - bridge/load-bearing
  - season/harvest
  - instrument/tuning
  - infrastructure/foundation

persona_scenarios:
  primary_dimension: dual_caregiving
  secondary_dimension: career_legacy
  integration_dimension: self_relationship
  content_templates:
    primary:
      dimension: your caregiving responsibilities
      scenario_library:
        - the parent's doctor appointment during the quarterly review
        - the teenager's crisis that arrived by text during a client dinner
        - the weekend that was supposed to be rest but became logistics
        - the medical bill that rewrote the retirement timeline
        - the conversation about assisted living that nobody wants to have
    secondary:
      dimension: your career and legacy
      scenario_library:
        - the promotion that feels like more weight, not more power
        - the younger colleague who reminds you of who you were
        - the retirement calculator that makes you nauseous
    integration:
      dimension: your relationship with yourself
      scenario_library:
        - the body that's sending signals you've been ignoring
        - the marriage that runs on logistics instead of connection
        - the quiet question: is this all there is?

rewrite_config:
  style_notes:
    - Respect their skepticism. Earn trust through evidence and mechanism.
    - Never use therapy-speak or millennial emotional vocabulary.
    - Pragmatic tone. "Here's what's happening in your body. Here's what to do."
    - Acknowledge the unfairness of the sandwich without making them a victim.
    - Exercises must be brief and feel like maintenance, not self-care luxury.
  forbidden_markers:
    - self-care Sunday
    - you deserve it
    - treat yourself
    - live your truth
    - manifest
    - journey (overused)
    - healing journey
    - inner child

market_data:
  us_population: 65M Gen X (highest household income: $113,445)
  audiobook_consumption: 5-7 titles/year (growing)
  primary_platforms: [Google Play, Audible]
  price_sensitivity: low (will pay premium: $17.99–$24.99)
  distribution_strategy: google_primary

topic_resonance:
  1: burnout
  2: financial_anxiety
  3: boundaries
  4: somatic_healing
  5: grief  # aging parents

template_set: gen_x_sandwich
shares_templates_with: []
```

---

### PERSONA 6: `corporate_managers`

```yaml
persona_id: corporate_managers
display_name: Corporate Middle Managers & Emerging Leaders
locale: en-US
generation_dialect: mixed
active: true
revenue_tier: 2

beat_map: phoenix_14
template_packs:
  base: core_self_help_v1
  overrides:
    - energy_budget_pack
    - leadership_transition_pack
language_packs:
  primary: en-US_core_v1
  fallbacks: []

voice_tone: authoritative, measured, strategic, privately human
formality: 0.75
slang_level: 0.05
pace_bpm: 150
pause_default_ms: 280
story_injection_rate: 0.22
breathing_exercise_frequency: 0.20

tone_bias_business: 1.00
tone_bias_scientific: 0.50
tone_bias_spiritual: 0.05
tone_bias_mythic: 0.10
tone_bias_personal: 0.35

# VOICE DISTINCTION:
# Professional voice that acknowledges private struggle.
# "You ran a flawless all-hands. Then sat in your car for 20 minutes
# because you couldn't face walking through your own front door."
# Most formal of all personas. Uses leadership vocabulary.
# Distinct from tech/finance: less sardonic, more measured.
# Distinct from entrepreneurs: less frontier energy, more institutional.

domain_jargon:
  - stakeholder
  - alignment
  - executive presence
  - skip-level
  - difficult conversation
  - managing up
  - succession
  - restructuring
  - headcount
  - deliverable

metaphor_style:
  - architecture/blueprint
  - bridge/span
  - signal/noise
  - compass/navigation
  - instrument/orchestra

persona_scenarios:
  primary_dimension: leadership_pressure
  secondary_dimension: relationships
  integration_dimension: self_relationship
  content_templates:
    primary:
      dimension: your leadership and organizational pressure
      scenario_library:
        - the skip-level where you learned you're being "managed out"
        - the team member crying in your office about something you can't fix
        - the reorg announcement you have to deliver with enthusiasm
        - the difficult conversation you've postponed for three weeks
        - the promotion to director that made you feel like a fraud
    secondary:
      dimension: your relationships
      scenario_library:
        - the partner who says you've brought work home again
        - the friend who doesn't understand why you can't just quit
    integration:
      dimension: your relationship with yourself
      scenario_library:
        - the imposter syndrome that grows with every promotion
        - the body that holds the tension your face won't show
        - the Sunday planning session that's become Sunday dread

rewrite_config:
  style_notes:
    - Speak to the private human inside the professional role.
    - Never undermine their competence or authority.
    - Frame therapeutic tools as performance tools — not weakness.
    - "Regulation" not "self-care." "Capacity" not "bandwidth."
    - Premium feel — this person expects quality.
  forbidden_markers:
    - synergy
    - circle back
    - touch base
    - empower (corporate-speak version)
    - thought leader
    - guru

market_data:
  us_population: 10.8M management-level positions
  audiobook_consumption: 5-8 titles/year
  primary_platforms: [Google Play, Audible]
  price_sensitivity: very low (premium: $17.99–$49.99)
  distribution_strategy: google_primary
  b2b_potential: high (L&D budgets, corporate subscriptions)

topic_resonance:
  1: imposter_syndrome
  2: burnout
  3: boundaries
  4: overthinking
  5: leadership_development  # NEW TOPIC

template_set: corporate_managers
shares_templates_with: []
migrates_from: [nyc_executives]  # absorbs some existing atoms
```

---

### PERSONA 7: `gen_z_professionals` (EXISTING — Updated)

```yaml
# UNCHANGED from current system. Already has:
# - Strong STORY atom pools across 8 topics
# - Templates for gen_z/ voice
# - Location variables for 23 locations
# - Compression atoms for burnout
#
# UPDATES for catalog planning:
# - Reclassified to Revenue Tier 3 (lower spending power)
# - Serves as "discovery" persona — TikTok drives awareness
# - Books at $9.95–$14.95 price point
# - Drafts behind flagship titles from Tier 1 personas

persona_id: gen_z_professionals
display_name: Gen Z Professionals
revenue_tier: 3
active: true
distribution_strategy: spotify_primary
topic_resonance:
  1: overthinking
  2: social_anxiety
  3: imposter_syndrome
  4: boundaries
  5: financial_anxiety
```

---

### PERSONA 8: `healthcare_rns` (EXISTING — Updated)

```yaml
# UNCHANGED from current system. Already has:
# - Templates for healthcare_rns/ voice
# - STORY atoms across topics
#
# UPDATES:
# - Revenue Tier 3 (small workforce: 3.4M)
# - High-value niche: persona-specific titles with low competition
# - "Compassion fatigue" is a Blue Ocean keyword (85 Audible titles)
# - Wide distribution (Findaway) to capture library revenue
# - Target podcast advertising in nursing podcasts

persona_id: healthcare_rns
display_name: Healthcare RNs
revenue_tier: 3
active: true
distribution_strategy: wide_findaway
topic_resonance:
  1: compassion_fatigue
  2: burnout
  3: boundaries
  4: sleep_anxiety
  5: somatic_healing
```

---

### PERSONA 9: `gen_alpha_students` (EXISTING — Updated)

```yaml
# UNCHANGED from current system.
#
# UPDATES:
# - Revenue Tier 3 (lowest: no purchasing power)
# - Spotify-only distribution (45% listen via Spotify)
# - Short-form only: 1–2 hour titles
# - Priced at $4.99–$7.99 (cash, not credit)
# - Functions as brand awareness / future customer pipeline

persona_id: gen_alpha_students
display_name: Gen Alpha Students
revenue_tier: 3
active: true
distribution_strategy: spotify_only
topic_resonance:
  1: overthinking
  2: social_anxiety
  3: self_worth
  4: sleep_anxiety
  5: boundaries
```

---

### PERSONA 10: `first_responders`

```yaml
persona_id: first_responders
display_name: First Responders
locale: en-US
generation_dialect: default
active: true
revenue_tier: 3

beat_map: phoenix_14
template_packs:
  base: core_self_help_v1
  overrides:
    - resilience_pack
    - somatic_deep_pack
language_packs:
  primary: en-US_core_v1
  fallbacks: []

voice_tone: steady, no-frills, earned-trust, quietly strong
formality: 0.60
slang_level: 0.15
pace_bpm: 140
pause_default_ms: 320
story_injection_rate: 0.30
breathing_exercise_frequency: 0.35

tone_bias_business: 0.20
tone_bias_scientific: 0.45
tone_bias_spiritual: 0.10
tone_bias_mythic: 0.25
tone_bias_personal: 0.50

# VOICE DISTINCTION:
# Talks like someone who's been on the job. No softness for its own sake.
# "You can run into a burning building but you can't sit still for
# five minutes. That's not weakness. That's a nervous system that
# forgot how to stand down." Respects the culture. Doesn't pathologize.

domain_jargon:
  - shift
  - call
  - scene
  - dispatch
  - on-duty / off-duty
  - station
  - mutual aid
  - critical incident
  - debrief
  - turnout

metaphor_style:
  - gear/maintenance/readiness
  - station/home
  - engine/idle
  - weather/storm
  - watch/shift

persona_scenarios:
  primary_dimension: duty_and_trauma
  secondary_dimension: relationships
  integration_dimension: self_relationship
  content_templates:
    primary:
      dimension: your duty and the weight of what you've seen
      scenario_library:
        - the call that followed you home and won't leave
        - the rookie's face that reminded you of yours
        - the debrief that didn't debrief anything
        - the injury that changed what your body can do
    secondary:
      dimension: your relationships
      scenario_library:
        - the partner who can't understand what you won't say
        - the crew that's closer than family but can't go there
    integration:
      dimension: your relationship with yourself
      scenario_library:
        - the drink that became the shift-end ritual
        - the sleep that stopped coming without noise
        - the anger that shows up where the grief should be

market_data:
  us_population: 2.5M (fire, EMS, police)
  audiobook_consumption: 4.2 titles/year
  primary_platforms: [Facebook, YouTube]
  price_sensitivity: moderate
  distribution_strategy: wide_findaway  # library access important

topic_resonance:
  1: somatic_healing  # nervous system regulation is #1 need
  2: sleep_anxiety
  3: burnout
  4: grief
  5: boundaries

template_set: first_responders
shares_templates_with: []
```

---

## PART 2: CANONICAL TOPIC REGISTRY (12 Production Topics)

### Topic Tier Assignment (Market Data-Driven)

| Tier | Topic ID | Search Vol (Book) | Market State | Duration Default | Price Default |
|------|---------|-------------------|--------------|-----------------|--------------|
| **1** | `overthinking` | 85k | Fragmented | 3–4 hr | $14.95 |
| **1** | `burnout` | 50k | Fragmented | 3–4 hr | $14.95 |
| **1** | `boundaries` | 35k | Top-heavy | 3–4 hr | $14.95 |
| **1** | `self_worth` | 30k+ | Top-heavy | 3–4 hr | $14.95 |
| **1** | `social_anxiety` | 55k | Top-heavy | 3–4 hr | $14.95 |
| **2** | `financial_anxiety` | 22k | Blue Ocean | 2.5–3.5 hr | $12.95 |
| **2** | `imposter_syndrome` | 30k | Blue Ocean | 2.5–3.5 hr | $12.95 |
| **2** | `sleep_anxiety` | 65k | Top-heavy | 2.5–3.5 hr | $12.95 |
| **2** | `depression` | 22k (book) | Fragmented | 3–4 hr | $14.95 |
| **3** | `grief` | 7.4k (book) | Fragmented | 2–3 hr | $9.95 |
| **3** | `compassion_fatigue` | <1k (book) | Blue Ocean | 2–3 hr | $9.95 |
| **3** | `somatic_healing` | Growing (TikTok) | Blue Ocean | 2–3 hr | $9.95 |

### NEW TOPICS (Not in Current Canonical List — Recommended Addition)

| Topic ID | Justification | Top Personas | Engine Overlap |
|---------|--------------|-------------|----------------|
| `leadership_development` | #1 L&D spending priority; top topic for 3 of 6 new personas | corporate_managers, gen_x, entrepreneurs | NEW engines needed |
| `productivity_habits` | Gateway topic for tech/finance and entrepreneurs; 9.4 titles/yr consumption | tech_finance, entrepreneurs, corporate_managers | Partial overlap with existing |

---

### TOPIC 1: `overthinking`

```yaml
topic_id: overthinking
display_name: Overthinking & Rumination
market_tier: 1
active: true

# === MARKET DATA ===
market:
  search_volume_book: 85000
  search_volume_mental_health: 250000
  audible_title_count: 1200
  category_state: fragmented  # no single 5x dominant leader
  top_competitor:
    title: "Don't Believe Everything You Think"
    author: Joseph Nguyen
    ratings: 15000
    length: "3h 05m"
    price: 14.95
  top_competitor_2:
    title: "Stop Overthinking"
    author: Nick Trenton
    ratings: 629
    length: "3h 13m"
  opportunity: >
    Massive search volume, fragmented field. Nguyen dominates but
    no persona-specific challenger exists. Gap between #1 (15k ratings)
    and #2 (629 ratings) means positions 2-10 are wide open.

# === CONSUMER LANGUAGE ===
consumer_language:
  primary_terms:
    - stop overthinking
    - brain won't shut off
    - replaying conversations
    - can't stop thinking
    - how to clear my mind
  clinical_terms_to_avoid:
    - rumination (only 18% recognition)
    - cognitive distortion
    - perseverative thinking
  consumer_prevalence: 82%  # use consumer language
  search_intent: problem-solving

# === PRODUCTION CONFIG ===
production:
  duration_class: full
  target_hours: 3-4
  target_words: 28000-37000
  pricing:
    flagship: 14.95
    persona_variant: 9.95
    bundle_3: 24.95
  distribution:
    flagship: acx_exclusive
    persona_variant: wide_findaway

# === THERAPEUTIC ARCHITECTURE ===
engines:
  - engine_id: avoidance
    description: Avoiding situations/thoughts that trigger the spiral
    mechanism: cognitive_defusion
    compatible_arcs: [recognition_spiral, exposure_gradient]
  - engine_id: control_loop
    description: Trying to think your way out of thinking
    mechanism: cognitive_defusion
    compatible_arcs: [recognition_spiral, paradox_dissolution]
  - engine_id: hypervigilance
    description: Scanning for what could go wrong
    mechanism: autonomic_regulation
    compatible_arcs: [somatic_settling, recognition_spiral]
  - engine_id: reassurance_seeking
    description: External validation as anxiety management
    mechanism: self_trust_repair
    compatible_arcs: [trust_gradient, recognition_spiral]

# === PERSONA COMPATIBILITY ===
persona_fit:
  tier_1: [millennial_women_professionals, tech_finance_burnout, entrepreneurs]
  tier_2: [working_parents, gen_x_sandwich, corporate_managers]
  tier_3: [gen_z_professionals, gen_alpha_students]
  exclusions: []  # universal topic

# === SEASONAL PEAKS ===
seasonal:
  peak_months: [1, 9]  # January (new year anxiety), September (back to routine)
  evergreen: true

# === SUBTITLE HOOKS PER PERSONA ===
subtitle_hooks:
  millennial_women_professionals: "When Your Brain Won't Let You Rest"
  tech_finance_burnout: "A Recovery Guide for the Overoptimized Mind"
  entrepreneurs: "How to Make Decisions When Your Mind Won't Stop"
  working_parents: "Quieting the Noise After the House Goes Silent"
  gen_x_sandwich: "When the Mental Load Becomes a Mental Loop"
  corporate_managers: "Strategic Thinking vs. Strategic Spiraling"
  gen_z_professionals: "For the Generation That Knows Too Much and Feels Everything"
  healthcare_rns: "Letting Go of the Shift When the Shift Won't Let Go of You"
  gen_alpha_students: "When Your Brain Won't Let You Sleep Before the Test"
  first_responders: "When the Call Ends but the Replay Doesn't"
```

---

### TOPIC 2: `burnout`

```yaml
topic_id: burnout
display_name: Burnout & Exhaustion Recovery
market_tier: 1
active: true

market:
  search_volume_book: 50000
  search_volume_mental_health: 150000
  audible_title_count: 680
  category_state: fragmented
  top_competitor:
    title: "Burnout"
    author: Emily Nagoski
    ratings: 5586
    length: "7h 01m"
    price: 18.00
  opportunity: >
    Fragmented category with only one strong competitor.
    Nagoski's book is 7 hours — our 3-hour mechanism-focused
    approach directly competes with the "shorter is better" trend.

consumer_language:
  primary_terms:
    - feeling burnt out
    - work exhaustion
    - am I burnt out or lazy
    - burnout recovery
    - how to recover from burnout
  clinical_terms_to_avoid:
    - occupational burnout
    - adjustment disorder
  consumer_prevalence: 55%
  search_intent: life-transition

production:
  duration_class: full
  target_hours: 3-4
  target_words: 28000-37000

engines:
  - engine_id: depletion_cycle
    mechanism: autonomic_regulation
  - engine_id: identity_fusion
    description: When you ARE your work
    mechanism: self_trust_repair
  - engine_id: boundary_collapse
    mechanism: behavioral_disconfirmation
  - engine_id: emotional_numbness
    mechanism: emotional_permission

persona_fit:
  tier_1: [tech_finance_burnout, millennial_women_professionals, entrepreneurs]
  tier_2: [gen_x_sandwich, corporate_managers, working_parents]
  tier_3: [healthcare_rns, gen_z_professionals, first_responders]

seasonal:
  peak_months: [1, 9]  # January rebound, September Q4 pressure
  evergreen: true

subtitle_hooks:
  millennial_women_professionals: "When Doing Everything Right Still Leaves You Empty"
  tech_finance_burnout: "A Recovery Protocol for the Always-On Professional"
  entrepreneurs: "Rebuilding After the Startup Grind"
  working_parents: "When There's Nothing Left After Everyone Else Gets Fed"
  gen_x_sandwich: "The Exhaustion That Earned Respect But Cost Everything Else"
  corporate_managers: "Leading Through Depletion Without Losing Your Team"
  gen_z_professionals: "You Shouldn't Be This Tired at 27"
  healthcare_rns: "When Caring for Everyone Else Left Nothing for You"
  first_responders: "Standing Down When Your Nervous System Won't"
```

---

### TOPIC 3: `boundaries`

```yaml
topic_id: boundaries
display_name: Boundaries & People Pleasing
market_tier: 1
active: true

market:
  search_volume_book: 35000
  search_volume_mental_health: 120000
  audible_title_count: 450
  category_state: top_heavy
  top_competitor:
    title: "Set Boundaries, Find Peace"
    author: Nedra Tawwab
    ratings: 8000
    length: "6h"
    price: 19.95
  opportunity: >
    Top-heavy but consumer language ("people pleasing") has
    massive search volume without a dominant audiobook.
    Persona-specific boundary content is nearly nonexistent.

consumer_language:
  primary_terms:
    - people pleasing
    - how to say no
    - how to say no without guilt
    - setting healthy boundaries
    - codependency
  consumer_prevalence: 72%
  search_intent: behavioral-change

production:
  duration_class: full
  target_hours: 3-4

engines:
  - engine_id: people_pleasing
    mechanism: behavioral_disconfirmation
  - engine_id: enmeshment
    mechanism: self_trust_repair
  - engine_id: guilt_as_signal
    mechanism: cognitive_defusion
  - engine_id: over_responsibility
    mechanism: meaning_realignment

persona_fit:
  tier_1: [millennial_women_professionals, working_parents]
  tier_2: [gen_x_sandwich, healthcare_rns, corporate_managers]
  tier_3: [gen_z_professionals, gen_alpha_students]

seasonal:
  peak_months: [11, 12]  # Holiday family pressure
  evergreen: true

subtitle_hooks:
  millennial_women_professionals: "Saying No When Your Career Depends on Saying Yes"
  tech_finance_burnout: "Disconnecting Without Derailing Your Career"
  working_parents: "Protecting Your Energy When Everyone Needs a Piece"
  gen_x_sandwich: "Setting Limits When Everyone Is Counting on You"
  healthcare_rns: "How to Say No When Your Job Is Saying Yes"
  gen_z_professionals: "Setting Boundaries in Your First Real Job"
  corporate_managers: "The Leadership Skill Nobody Teaches You"
```

---

### TOPIC 4: `self_worth`

```yaml
topic_id: self_worth
display_name: Self-Worth & Self-Esteem
market_tier: 1
active: true

market:
  search_volume_book: 30000
  search_volume_mental_health: 80000
  audible_title_count: 4000
  category_state: top_heavy
  top_competitor:
    title: "The Gifts of Imperfection"
    author: Brené Brown
    ratings: 11000
  opportunity: >
    Massive category but dominated by Brené Brown.
    Mechanism-specific approach (shame vs comparison vs
    achievement-dependency) differentiates from general
    "love yourself" content.

consumer_language:
  primary_terms:
    - how to love yourself
    - low self-esteem
    - not feeling good enough
    - signs of low self-worth
    - why do I hate myself
  search_intent: identity-repair

engines:
  - engine_id: shame
    mechanism: emotional_permission
  - engine_id: comparison
    mechanism: cognitive_defusion
  - engine_id: achievement_dependency
    mechanism: self_trust_repair
  - engine_id: inner_critic
    mechanism: meaning_realignment

persona_fit:
  tier_1: [millennial_women_professionals, gen_z_professionals]
  tier_2: [working_parents, gen_alpha_students]

subtitle_hooks:
  millennial_women_professionals: "When Achievement Doesn't Fix the Feeling"
  tech_finance_burnout: "The Imposter Behind the Performance Review"
  gen_z_professionals: "You're Not Behind. You're Not Broken."
  gen_alpha_students: "Who You Are When Nobody's Watching"
```

---

### TOPIC 5: `social_anxiety`

```yaml
topic_id: social_anxiety
display_name: Social Anxiety
market_tier: 1
active: true

market:
  search_volume_book: 55000
  search_volume_mental_health: 180000
  audible_title_count: 3045
  category_state: top_heavy
  top_competitor:
    title: "How to Be Yourself"
    author: Ellen Hendriksen
    ratings: 1200
  opportunity: >
    Extremely high search volume. Top-heavy but rating gap
    between #1 (1200) and field means quality challenger can rank.
    "Hybrid work social anxiety" is an untapped angle.

consumer_language:
  primary_terms:
    - socially awkward
    - afraid of being judged
    - social anxiety at work
    - shyness
    - how to stop being socially anxious
  search_intent: social-belonging

engines:
  - engine_id: avoidance
    mechanism: behavioral_disconfirmation
  - engine_id: safety_behavior
    mechanism: cognitive_defusion
  - engine_id: anticipation
    mechanism: autonomic_regulation
  - engine_id: post_event_processing
    mechanism: cognitive_defusion

subtitle_hooks:
  millennial_women_professionals: "When Networking Feels Like Performing"
  tech_finance_burnout: "Social Anxiety for Hybrid Work"
  gen_z_professionals: "The Anxiety of Being Seen in a World That's Always Watching"
  gen_alpha_students: "When School Feels Like a Stage You Can't Get Off"
```

---

### TOPIC 6: `financial_anxiety`

```yaml
topic_id: financial_anxiety
display_name: Financial Anxiety & Money Stress
market_tier: 2
active: true

market:
  search_volume_book: 22000
  audible_title_count: 220
  category_state: blue_ocean
  top_competitor:
    title: "The Psychology of Money"
    author: Morgan Housel
    ratings: 45000  # dominates but is general finance, not therapeutic
  opportunity: >
    Blue Ocean for THERAPEUTIC financial anxiety content.
    Psychology of Money is financial advice, not anxiety treatment.
    59% of Americans cite finances as #1 stressor. Only 220
    audiobooks address this as an anxiety mechanism.

consumer_language:
  primary_terms:
    - money stress
    - debt anxiety
    - anxiety about spending
    - financial overwhelm
    - scared about money

engines:
  - engine_id: scarcity_loop
    mechanism: autonomic_regulation
  - engine_id: shame_avoidance
    mechanism: emotional_permission
  - engine_id: catastrophizing
    mechanism: cognitive_defusion

seasonal:
  peak_months: [3, 4]  # Tax season (March-April)
  secondary_peak: [1]  # Post-holiday debt

subtitle_hooks:
  millennial_women_professionals: "When Your Bank Balance Controls Your Nervous System"
  entrepreneurs: "Making Peace with Uncertainty When It's Your Only Income"
  gen_z_professionals: "Adulting, Anxiety, and the Account Balance"
  gen_x_sandwich: "The Sandwich Generation's Hidden Stressor"
```

---

### TOPIC 7: `imposter_syndrome`

```yaml
topic_id: imposter_syndrome
display_name: Imposter Syndrome
market_tier: 2
active: true

market:
  search_volume_book: 30000
  audible_title_count: 310
  category_state: blue_ocean
  opportunity: >
    Rising search interest, low competition. Particularly strong
    with tech workers (65% report it) and corporate managers
    (transition to leadership triggers it).

consumer_language:
  primary_terms:
    - feeling like a fraud
    - imposter syndrome
    - do I have imposter syndrome
    - not qualified enough
  search_intent: identity-validation

engines:
  - engine_id: competence_discounting
    mechanism: cognitive_defusion
  - engine_id: attribution_error
    mechanism: self_trust_repair
  - engine_id: success_anxiety
    mechanism: emotional_permission

subtitle_hooks:
  tech_finance_burnout: "When Every Code Review Feels Like an Exposure"
  corporate_managers: "The Promotion That Made You Feel Like a Fraud"
  millennial_women_professionals: "Qualified on Paper, Terrified in Practice"
  gen_z_professionals: "You Got the Job. Now You're Waiting to Be Found Out."
```

---

### TOPIC 8: `sleep_anxiety`

```yaml
topic_id: sleep_anxiety
display_name: Sleep Anxiety & Insomnia
market_tier: 2
active: true

market:
  search_volume_book: 65000
  search_volume_mental_health: 300000
  audible_title_count: 920
  category_state: top_heavy
  opportunity: >
    Massive search volume. Special production consideration:
    audiobooks in this category are used AS sleep aids.
    Narration style must be atmospheric, soothing.
    "Brain won't shut off at night" = #1 consumer query.

consumer_language:
  primary_terms:
    - can't sleep because of stress
    - night anxiety
    - brain won't shut off at night
    - anxiety insomnia
    - racing thoughts at bedtime

engines:
  - engine_id: hyperarousal
    mechanism: autonomic_regulation
  - engine_id: performance_anxiety_sleep
    description: Anxious about not sleeping
    mechanism: cognitive_defusion
  - engine_id: rumination_loop_nocturnal
    mechanism: cognitive_defusion

# SPECIAL PRODUCTION NOTE:
# Sleep anxiety titles require different narration parameters:
# pace_bpm: 120 (slower)
# pause_default_ms: 500 (longer pauses)
# breathing_exercise_frequency: 0.50 (higher)
# Atmospheric production quality (subtle ambient texture)

subtitle_hooks:
  tech_finance_burnout: "Shutting Down When the System Won't"
  healthcare_rns: "Finding Rest After a 12-Hour Shift"
  working_parents: "Sleep When the Mental Load Won't Quiet"
  millennial_women_professionals: "The 3am Spiral and How to End It"
```

---

### TOPIC 9: `depression`

```yaml
topic_id: depression
display_name: Depression & Feeling Stuck
market_tier: 2
active: true

market:
  search_volume_book: 22000
  search_volume_mental_health: 300000
  audible_title_count: 10000
  category_state: fragmented
  opportunity: >
    Massive general search but very clinical category.
    Phoenix opportunity: "feeling stuck" framing avoids
    clinical territory while addressing functional depression.
    Consumer language is key differentiator.

consumer_language:
  primary_terms:
    - feeling stuck
    - why am I so unmotivated
    - nothing makes me happy anymore
    - emotional numbness
    - how to get out of a rut
  clinical_terms_to_avoid:
    - major depressive disorder
    - clinical depression treatment

engines:
  - engine_id: withdrawal_loop
    mechanism: behavioral_disconfirmation
  - engine_id: anhedonia
    mechanism: emotional_permission
  - engine_id: learned_helplessness
    mechanism: self_trust_repair
  - engine_id: meaning_collapse
    mechanism: meaning_realignment

subtitle_hooks:
  millennial_women_professionals: "When Going Through the Motions Becomes Your Life"
  gen_x_sandwich: "The Flatness That Settled In When Nobody Was Looking"
  gen_z_professionals: "You're Not Lazy. You're Running on Empty."
```

---

### TOPIC 10: `grief`

```yaml
topic_id: grief
display_name: Grief & Loss Recovery
market_tier: 3
active: true

market:
  search_volume_book: 7400
  audible_title_count: 3500
  category_state: fragmented
  opportunity: >
    Moderate search, many titles. Persona-specific grief
    (loss of parent for Gen X, loss of identity for career
    changers, loss of health) is underserved.

consumer_language:
  primary_terms:
    - grief recovery
    - how to deal with loss
    - stages of grief
    - grief and depression
    - how long does grief last

engines:
  - engine_id: avoidance_grief
    mechanism: emotional_permission
  - engine_id: meaning_reconstruction
    mechanism: meaning_realignment
  - engine_id: identity_after_loss
    mechanism: self_trust_repair

subtitle_hooks:
  gen_x_sandwich: "When You Become the Person Who Takes Care of Everything"
  working_parents: "The Losses Nobody Sees"
  first_responders: "The Weight of What You've Witnessed"
```

---

### TOPIC 11: `compassion_fatigue`

```yaml
topic_id: compassion_fatigue
display_name: Compassion Fatigue & Secondary Trauma
market_tier: 3
active: true

market:
  search_volume_book: 1000
  audible_title_count: 85
  category_state: blue_ocean
  opportunity: >
    Tiny search volume but extreme persona specificity.
    Only 85 audiobooks. Healthcare workers (22M), first
    responders (2.5M), educators (3.8M) all need this.
    Blue Ocean = easy ranking. Persona subtitle captures intent.

consumer_language:
  primary_terms:
    - secondary trauma
    - caregiver burnout
    - compassion fatigue
    - emotional exhaustion from helping others

engines:
  - engine_id: empathy_depletion
    mechanism: autonomic_regulation
  - engine_id: vicarious_trauma
    mechanism: emotional_permission
  - engine_id: helper_identity_fusion
    mechanism: self_trust_repair

subtitle_hooks:
  healthcare_rns: "A Recovery Guide for the Nurse Who Gives Everything"
  first_responders: "When the Weight of Others' Pain Becomes Your Own"
```

---

### TOPIC 12: `somatic_healing`

```yaml
topic_id: somatic_healing
display_name: Somatic Healing & Nervous System Regulation
market_tier: 3
active: true

market:
  search_volume_book: growing  # TikTok trending
  audible_title_count: 400
  category_state: blue_ocean
  opportunity: >
    Rising trend: vagus nerve, polyvagal theory, somatic
    exercises on TikTok. Few quality audiobooks exist.
    Phoenix differentiator: secular, science-backed somatic
    content vs. woo-adjacent competitors.

consumer_language:
  primary_terms:
    - vagus nerve exercises
    - nervous system regulation
    - somatic exercises
    - polyvagal theory
    - body keeps the score (related)
    - how to calm nervous system

engines:
  - engine_id: freeze_release
    mechanism: autonomic_regulation
  - engine_id: hyperactivation_settling
    mechanism: autonomic_regulation
  - engine_id: interoception_development
    mechanism: emotional_permission

# SPECIAL PRODUCTION NOTE:
# Somatic titles require higher exercise density.
# breathing_exercise_frequency: 0.50+
# Every chapter should include a guided practice.
# Audio production needs space for silence and breath cues.

subtitle_hooks:
  tech_finance_burnout: "When Your Body Keeps the Score of Every Sprint"
  first_responders: "Resetting the Nervous System That Won't Stand Down"
  healthcare_rns: "Body-Based Recovery for the Caregiver's Nervous System"
  millennial_women_professionals: "The Science of Settling Your Body When Your Mind Won't"
```

---

## PART 3: CATALOG MATH

### Production Grid (10 Personas × 12 Topics)

```
                   overthink  burnout  bound  self_w  soc_anx  fin_anx  imposter  sleep  depress  grief  comp_fat  somatic
mill_women_prof       F         F        F      F       F        V         V        V       V       -       -        V
tech_fin_burn         F         F        V      V       V        -         F        V       -       -       -        F
entrepreneurs         F         F        V      -       -        F         V        -       V       -       -        -
working_parents       F         F        F      V       -        -         -        V       -       V       -        -
gen_x_sandwich        V         F        F      -       -        F         -        -       V       F       -        V
corp_managers         V         F        F      -       -        -         F        -       -       -       -        -
gen_z_prof            F         V        F      V       F        V         F        V       V       -       -        -
healthcare_rns        -         F        F      -       -        -         -        V       -       -       F        F
gen_alpha             V         -        V      V       F        -         -        V       -       -       -        -
first_responders      -         V        V      -       -        -         -        V       -       F       F        F

F = Flagship (human narration, active marketing)
V = Variant (AI narration, drafts behind flagship)
- = Not produced (low persona-topic fit)
```

### Title Count Projection

| Category | Count | Notes |
|---------|-------|-------|
| Flagship titles (F) | 68 | Active marketing, human narration |
| Variant titles (V) | 52 | AI narration, persona subtitle |
| Angle variants per flagship (×3) | 204 | Different engine per book |
| Angle variants per variant (×2) | 104 | Fewer angles for variants |
| Location variants for Gen Z + Gen Alpha | 200+ | Existing location variable files |
| Depth books (Model B) for Tier 1 topics | 50 | Foundations + Advanced |
| Short-form / freebie-adjacent | 100 | 1-hour, $4.99-$7.99 |
| **Subtotal (core catalog)** | **~778** | |
| Seasonal / trending titles | 50 | Tax anxiety, holiday stress, etc. |
| Bundle compilations | 50 | 3-book topic bundles |
| Companion audio exercises | 130 | Lead magnets, post-purchase |
| **Total catalog** | **~1,008** | |

---

## PART 4: TEMPLATE SET REQUIREMENTS

| Template Set ID | Personas Served | New or Existing | Priority |
|----------------|----------------|-----------------|----------|
| `millennial_professional_women` | millennial_women_professionals | **NEW** | P0 |
| `tech_finance_burnout` | tech_finance_burnout | **NEW** (migrates from nyc_exec) | P0 |
| `entrepreneurs` | entrepreneurs | **NEW** | P0 |
| `working_parents` | working_parents | **NEW** | P1 |
| `gen_x_sandwich` | gen_x_sandwich | **NEW** | P1 |
| `corporate_managers` | corporate_managers | **NEW** (migrates from nyc_exec) | P1 |
| `gen_z` | gen_z_professionals + location variants | **EXISTS** | — |
| `gen_alpha` | gen_alpha_students + location variants | **EXISTS** | — |
| `healthcare_rns` | healthcare_rns | **EXISTS** | — |
| `first_responders` | first_responders | **NEW** | P2 |

**6 new template sets required.** Each = 4 role templates (recognition, mechanism_proof, turning_point, embodiment) × topics × engines. Priority order follows revenue tier.

---

## PART 5: CONSUMER LANGUAGE MAP (Config File)

```yaml
# config/catalog_planning/consumer_language_map.yaml
# Use these terms in titles, subtitles, and Audible keywords
# NEVER use the clinical terms in customer-facing content

overthinking:
  use: ["stop overthinking", "brain won't shut off", "replaying conversations", "can't stop thinking"]
  avoid: ["rumination", "perseverative thinking", "cognitive distortion"]

burnout:
  use: ["feeling burnt out", "work exhaustion", "am I burnt out or lazy", "running on empty"]
  avoid: ["occupational burnout", "adjustment disorder"]

boundaries:
  use: ["people pleasing", "how to say no", "saying no without guilt", "setting healthy boundaries"]
  avoid: ["enmeshment", "codependency disorder"]

self_worth:
  use: ["not good enough", "low self-esteem", "how to love yourself", "why do I hate myself"]
  avoid: ["narcissistic injury", "core schema"]

social_anxiety:
  use: ["socially awkward", "afraid of being judged", "shyness", "social anxiety at work"]
  avoid: ["social phobia", "avoidant personality"]

financial_anxiety:
  use: ["money stress", "debt anxiety", "anxiety about spending", "scared about money"]
  avoid: ["financial anxiety disorder"]

imposter_syndrome:
  use: ["feeling like a fraud", "imposter syndrome", "not qualified enough"]
  avoid: ["competence discounting"]

sleep_anxiety:
  use: ["can't sleep because of stress", "night anxiety", "brain won't shut off at night"]
  avoid: ["insomnia disorder", "sleep-onset latency"]

depression:
  use: ["feeling stuck", "nothing makes me happy", "emotional numbness", "how to get out of a rut"]
  avoid: ["major depressive disorder", "anhedonia"]

grief:
  use: ["grief recovery", "dealing with loss", "how long does grief last"]
  avoid: ["complicated grief disorder", "prolonged grief"]

compassion_fatigue:
  use: ["secondary trauma", "caregiver burnout", "compassion fatigue"]
  avoid: ["vicarious traumatization"]

somatic_healing:
  use: ["vagus nerve exercises", "nervous system regulation", "somatic exercises", "calm your body"]
  avoid: ["interoceptive processing", "afferent signaling"]
```

---

## PART 6: PRODUCTION SEQUENCE

### Month 1-2: Template + Atom Foundation
1. Author 3 P0 template sets (millennial_women, tech_finance, entrepreneurs)
2. Micro-stakes research for Tier 1 personas × Tier 1 topics
3. Fill STORY + REFLECTION + EXERCISE + INTEGRATION pools for first 9 lanes
4. Build series wrapper configs and topic lattice YAML

### Month 2-4: First 20 Flagships
5. Compile and publish 20 flagship titles across Tier 1 personas × Tier 1 topics
6. Launch freebie funnel (audio exercises → email → book recommendation)
7. Begin Tier 2 persona template authoring (working_parents, gen_x, corporate)

### Month 4-8: Scale to Variants
8. Publish 50 persona variant titles (AI narration, persona subtitles)
9. Fill Tier 2 topic atom pools
10. Launch location variants for Gen Z and Gen Alpha

### Month 8-12: Full Catalog
11. Complete all template sets including P2 (first_responders)
12. Publish remaining titles to reach 1,008
13. Launch bundle compilations and companion products
14. Seasonal titles for Q4 (holiday stress, relationship anxiety)
