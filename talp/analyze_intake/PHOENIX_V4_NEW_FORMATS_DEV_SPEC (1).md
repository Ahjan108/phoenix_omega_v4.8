# Phoenix V4 — New Format Portfolio Development Specification

**Status:** Proposal  
**Version:** 1.0  
**Date:** 2026-02-14  
**Author:** Ma'at (Nihala)  
**Scope:** 15 new therapeutic audiobook formats for SOURCE_OF_TRUTH expansion  

---

## Executive Summary

This spec defines 15 new book formats compatible with Phoenix V4's atom-based assembly system. Each format includes:

1. **Format policy YAML** (slot structure)
2. **K-table requirements** (minimum atoms per combo)
3. **Catalog planning hierarchy** (domain → series → angle)
4. **Duplication thresholds** (format-specific)
5. **Blueprint rotation variants** (3+ per format)
6. **Persona affinity mapping**
7. **Audio production considerations**

All formats maintain Phoenix's core principles: no resolution language, human governance of meaning, deterministic assembly, and strict quality gates.

---

## Format Portfolio Matrix

| Format ID | Name | Chapter Count | Avg Minutes | Persona Fit | Production Priority |
|-----------|------|---------------|-------------|-------------|---------------------|
| F001 | 90-Day Transformation | 90 | 240-300 | All | HIGH |
| F002 | Daily Practice Rituals | 30-365 | 120-500 | All | HIGH |
| F003 | Challenge Series | 7-21 | 60-180 | Gen Z, Millennials | MEDIUM |
| F004 | Somatic Body Journey | 12-15 | 150-200 | Healthcare, HSPs | HIGH |
| F005 | Scenario Rescue Kit | 10-20 | 40-80 | All | HIGH |
| F006 | Nervous System Ladder | 8-12 | 100-150 | Trauma-informed | HIGH |
| F007 | Shadow Work Series | 8-12 | 120-180 | Millennials, Gen X | MEDIUM |
| F008 | Micro-Habits Stacking | 52 | 90-120 | Busy professionals | MEDIUM |
| F009 | Parts Work (IFS) | 10-15 | 150-200 | Therapy-adjacent | HIGH |
| F010 | Energy Management | 12-16 | 150-200 | Empaths, caregivers | MEDIUM |
| F011 | Relationship Repair | 8-12 | 120-160 | All | HIGH |
| F012 | Permission Slip Collection | 52 | 60-90 | Gen Z, Millennials | LOW |
| F013 | Before/During/After Crisis | 3×8 | 150-200 | Situational | MEDIUM |
| F014 | Archetype Transformation | 10-15 | 150-200 | Spiritual seekers | MEDIUM |
| F015 | Sensory Regulation Library | 5-8 | 80-120 | Neurodivergent, HSPs | MEDIUM |

---

## F001: 90-Day Transformation Format

### Format Policy YAML

```yaml
# phoenix_v4/policy/format_policies/90_day_transformation.yaml

format_id: 90_day_transformation
format_name: "90-Day Transformation Journey"
description: "Time-bound daily practice for sustained behavioral change"

structure:
  chapter_count: 90
  chapters_per_week: 7
  total_weeks: ~13
  
  weekly_arc:
    week_1-2: grounding_and_recognition
    week_3-6: pattern_interruption
    week_7-10: new_behavior_installation
    week_11-13: integration_and_sustainability

slot_definitions:
  slot_01_day_number:
    category: scene
    role: day_marker
    description: "Day X of 90 - brief orientation"
    
  slot_02_micro_teaching:
    category: story
    role: recognition
    description: "One micro-concept per day"
    
  slot_03_practice:
    category: exercise
    role: daily_practice
    description: "2-5 minute daily practice"
    
  slot_04_reflection:
    category: scene
    role: closing
    description: "Brief reflection prompt"

weekly_milestones:
  - day: 7
    slot_05_weekly_review:
      category: story
      role: integration
      description: "Week integration story"
      
  - day: 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84
    slot_05_weekly_review:
      category: story
      role: progress_check
      description: "Progress recognition"
      
  - day: 30, 60, 90
    slot_06_milestone:
      category: story
      role: transformation_marker
      description: "Major milestone recognition"

pacing:
  days_1-30:
    exercise_duration: "2-3 minutes"
    teaching_depth: "foundational"
    
  days_31-60:
    exercise_duration: "3-5 minutes"
    teaching_depth: "intermediate"
    
  days_61-90:
    exercise_duration: "4-6 minutes"
    teaching_depth: "integration"

k_table_requirements:
  story_recognition_daily: 90  # unique recognition atoms
  story_integration_weekly: 13  # unique weekly atoms
  story_milestone_major: 3  # unique milestone atoms
  exercise_daily_practice: 90  # unique practice atoms
  scene_day_marker: 90  # can template-vary
  scene_reflection: 90  # can template-vary

duplication_thresholds:
  paragraph_hash: 0.0  # zero collisions
  sentence_hash: 0.15  # stricter for daily format
  six_gram_overlap: 0.12
  daily_practice_similarity: 0.75  # exercises can have more pattern

governance:
  exercise_cadence_rule: "progressive_intensity"
  weekly_review_mandatory: true
  milestone_approval: "requires_clinical_advisor"
  no_missing_days: true
```

### Catalog Planning Hierarchy

```yaml
# omega/catalog_planning/domains/90_day_transformation.yaml

domain: "90-Day Transformation"
domain_id: D001

capacity_assessment:
  max_books_per_year: 24  # 2 per month sustainable
  atom_velocity_required: "high"
  
search_intent_cluster:
  - "90 day challenge"
  - "3 month transformation"
  - "daily practice guide"
  - "habit change program"

series_templates:
  
  - series_name: "90 Days to [Outcome State]"
    persona_affinity: [all]
    search_keywords:
      - "overcome anxiety 90 days"
      - "build confidence 90 days"
      - "heal trauma 90 days"
    angles:
      - anxiety_freedom
      - confidence_building
      - grief_integration
      - boundary_mastery
      - self_compassion
      - emotional_regulation
      - sleep_restoration
      - stress_resilience
      
  - series_name: "The 90-Day [Practice Type] Journey"
    persona_affinity: [spiritual_seekers, wellness_focused]
    search_keywords:
      - "meditation daily practice"
      - "breathwork program"
      - "somatic healing journey"
    angles:
      - meditation_foundation
      - breathwork_mastery
      - somatic_awareness
      - mindful_movement
      
  - series_name: "Transform Your [Life Domain] in 90 Days"
    persona_affinity: [busy_professionals, parents]
    search_keywords:
      - "work life balance 90 days"
      - "parenting transformation"
    angles:
      - work_relationship
      - parenting_presence
      - relationship_repair
      - creative_expression

capacity_guards:
  safety_margin: 1.2
  heavy_hitter_rate_max: 0.20  # daily format needs variety
  semantic_delta_min: 0.60
```

### Blueprint Rotation (3 variants)

```yaml
# omega/blueprint_rotation/90_day_transformation/

variant_01_linear_progression.yaml:
  name: "Linear Daily Build"
  description: "Steady escalation, predictable rhythm"
  weekly_structure:
    - 5 teaching days + 2 integration days
  milestone_placement: [30, 60, 90]
  
variant_02_wave_pattern.yaml:
  name: "Wave Intensity Pattern"
  description: "Build-release-integrate cycles"
  weekly_structure:
    - weeks 1-3: build
    - week 4: integrate
    - repeat
  milestone_placement: [21, 49, 77, 90]
  
variant_03_scaffold_removal.yaml:
  name: "Progressive Independence"
  description: "Heavy guidance early, self-led later"
  weekly_structure:
    - days 1-30: full teaching + practice
    - days 31-60: lighter teaching + practice
    - days 61-90: minimal teaching + advanced practice
  milestone_placement: [30, 60, 90]
```

---

## F002: Daily Practice Rituals Format

### Format Policy YAML

```yaml
# phoenix_v4/policy/format_policies/daily_practice_rituals.yaml

format_id: daily_practice_rituals
format_name: "Daily Practice Rituals"
description: "Return-to listening format for habitual practice"

structure:
  chapter_count_variants:
    - 30  # monthly cycle
    - 365  # full year
  practice_types:
    - morning_ritual
    - evening_ritual
    - midday_reset
    - commute_practice

slot_definitions:
  slot_01_arrival:
    category: scene
    role: entry
    description: "Gentle arrival sequence"
    
  slot_02_intention:
    category: story
    role: recognition
    description: "Why this practice matters today"
    
  slot_03_core_practice:
    category: exercise
    role: primary_practice
    description: "The main meditation/breathwork/somatic practice"
    duration_target: "5-12 minutes"
    
  slot_04_integration:
    category: story
    role: embodiment
    description: "Bridging practice to daily life"
    
  slot_05_closing:
    category: scene
    role: closing
    description: "Soft landing back to day"

special_days:
  new_moon_full_moon:
    slot_06_lunar_reflection:
      category: story
      role: cyclical_wisdom
      
  season_transitions:
    slot_06_seasonal_shift:
      category: story
      role: nature_alignment

k_table_requirements:
  story_intention_daily: 365  # or 30 for monthly
  exercise_core_practice: 365  # or 30
  story_integration: 365  # or 30
  scene_arrival: 12  # can repeat monthly
  scene_closing: 12  # can repeat monthly
  story_lunar: 24  # for year version
  story_seasonal: 4  # for year version

duplication_thresholds:
  paragraph_hash: 0.0
  sentence_hash: 0.18  # slightly relaxed for ritual language
  six_gram_overlap: 0.15
  practice_instruction_similarity: 0.80  # practices have inherent pattern

audio_production:
  background_music: true
  silence_after_practice: "30 seconds minimum"
  tone: "meditative_steady"
  
governance:
  return_listener_optimized: true
  no_narrative_arc_required: true
  standalone_chapters: true
```

### Catalog Planning Hierarchy

```yaml
# omega/catalog_planning/domains/daily_practice_rituals.yaml

domain: "Daily Practice Rituals"
domain_id: D002

series_templates:

  - series_name: "Morning [Practice Type] - 365 Days"
    persona_affinity: [wellness_focused, spiritual_seekers]
    angles:
      - morning_meditation
      - morning_breathwork
      - morning_yoga_nidra
      - morning_gratitude
      
  - series_name: "Evening [Outcome] - 30 Days"
    persona_affinity: [busy_professionals, insomniacs]
    angles:
      - sleep_preparation
      - day_release
      - nervous_system_downregulation
      
  - series_name: "Midday Reset - [Persona]"
    persona_affinity: [healthcare_workers, parents, caregivers]
    angles:
      - quick_grounding
      - energy_renewal
      - stress_release

capacity_assessment:
  max_books_per_year: 36  # 3 per month - high return value
  atom_velocity_required: "very_high"
```

---

## F003: Challenge Series Format

### Format Policy YAML

```yaml
# phoenix_v4/policy/format_policies/challenge_series.yaml

format_id: challenge_series
format_name: "Therapeutic Challenge Series"
description: "Gamified healing journey with clear wins"

structure:
  chapter_count_variants:
    - 7  # week-long
    - 14  # two-week
    - 21  # three-week
    
  challenge_arc:
    day_1: commitment_and_baseline
    days_2-N-1: progressive_skills
    day_N: integration_and_celebration

slot_definitions:
  slot_01_challenge_intro:
    category: scene
    role: entry
    description: "Today's challenge preview"
    
  slot_02_why_this_matters:
    category: story
    role: recognition
    description: "Stakes and benefits"
    
  slot_03_challenge_exercise:
    category: exercise
    role: challenge_practice
    description: "The actual challenge task"
    difficulty_marker: true
    
  slot_04_common_obstacles:
    category: story
    role: pattern
    description: "What makes this hard + how to navigate"
    
  slot_05_win_recognition:
    category: scene
    role: closing
    description: "Celebrating completion"
    
  slot_06_next_preview:
    category: scene
    role: transition
    description: "Teaser for tomorrow"

daily_progression:
  difficulty_curve: "exponential_early_linear_late"
  skill_stacking: true
  
milestone_days:
  - day: 1
    slot_07_baseline:
      category: story
      role: starting_point
      
  - day: N/2
    slot_07_midpoint:
      category: story
      role: progress_check
      
  - day: N
    slot_07_completion:
      category: story
      role: transformation_marker

k_table_requirements:
  story_recognition: [7, 14, 21]  # per variant
  exercise_challenge: [7, 14, 21]
  story_obstacles: [7, 14, 21]
  scene_win_recognition: [7, 14, 21]
  story_baseline: 1
  story_midpoint: 1
  story_completion: 1

duplication_thresholds:
  paragraph_hash: 0.0
  sentence_hash: 0.12  # strict - Gen Z detects repetition fast
  six_gram_overlap: 0.10

persona_optimization:
  gen_z:
    language_style: "direct_no_fluff"
    challenge_framing: "level_up"
    social_proof: "high"
    
  millennials:
    language_style: "authentic_vulnerable"
    challenge_framing: "personal_growth"
    community_reference: "medium"
```

### Catalog Planning

```yaml
domain: "Challenge Series"
domain_id: D003

series_templates:

  - series_name: "The [N]-Day [Outcome] Challenge"
    persona_affinity: [gen_z, millennials, busy_professionals]
    angles:
      - confidence_challenge
      - anxiety_freedom_challenge
      - self_compassion_challenge
      - boundary_challenge
      - morning_routine_challenge
      - digital_detox_challenge
      
  - series_name: "[N] Days to [Skill]"
    persona_affinity: [action_oriented, wellness_focused]
    angles:
      - meditation_mastery
      - breathwork_basics
      - somatic_awareness
      - emotional_literacy
```

---

## F004: Somatic Body Journey Format

### Format Policy YAML

```yaml
# phoenix_v4/policy/format_policies/somatic_body_journey.yaml

format_id: somatic_body_journey
format_name: "Somatic Body Journey"
description: "Body-region-based trauma release and reconnection"

structure:
  chapter_count: 12-15
  progression_map:
    - feet_and_legs (grounding)
    - pelvis_and_hips (safety, creativity)
    - belly (emotions, digestion of experience)
    - chest (heart, breath, expression)
    - throat (voice, truth)
    - jaw (holding, release)
    - shoulders (burden, responsibility)
    - arms_and_hands (agency, reach)
    - neck (flexibility, protection)
    - head (thinking, sensing)
    - spine (support, uprightness)
    - full_body_integration

slot_definitions:
  slot_01_location_arrival:
    category: scene
    role: entry
    description: "Arriving at this body region"
    
  slot_02_somatic_story:
    category: story
    role: recognition
    description: "What we hold here - culturally informed"
    body_lexemes_required: true
    
  slot_03_sensation_exploration:
    category: exercise
    role: awareness
    description: "Guided sensation mapping"
    
  slot_04_trauma_informed_story:
    category: story
    role: mechanism_proof
    description: "Why tension accumulates here"
    
  slot_05_release_practice:
    category: exercise
    role: somatic_release
    description: "Gentle trauma release technique"
    safety_protocols: required
    
  slot_06_reconnection_story:
    category: story
    role: agency_glimmer
    description: "New relationship with this region"
    
  slot_07_integration_movement:
    category: exercise
    role: integration
    description: "Embodied integration movement"
    
  slot_08_closing:
    category: scene
    role: closing
    description: "Gratitude for body wisdom"
    
  slot_09_transition:
    category: scene
    role: transition
    description: "Bridge to next region"

k_table_requirements:
  story_somatic_recognition: 15  # per body region
  story_mechanism: 15
  story_agency: 15
  exercise_sensation_exploration: 15
  exercise_release: 15
  exercise_integration_movement: 15
  scene_arrival: 15
  scene_closing: 15
  scene_transition: 14

duplication_thresholds:
  paragraph_hash: 0.0
  sentence_hash: 0.16
  six_gram_overlap: 0.13
  body_lexeme_reuse: 0.70  # some anatomical terms repeat

safety_protocols:
  clinical_advisor_review: required
  trauma_informed_language: required
  dissociation_warning: required
  pacing_guidance: required
  
audio_production:
  silence_for_practice: "60-90 seconds per exercise"
  tone: "gentle_steady_grounded"
  pacing: "slower_than_standard"
```

### Catalog Planning

```yaml
domain: "Somatic Body Journey"
domain_id: D004

series_templates:

  - series_name: "Healing [Body Region]: A Somatic Journey"
    persona_affinity: [trauma_survivors, healthcare_workers, HSPs]
    angles:
      - full_body_journey
      - lower_body_grounding
      - upper_body_expression
      - core_emotions
      
  - series_name: "Release [Emotion] from Your Body"
    persona_affinity: [therapy_adjacent, wellness_focused]
    angles:
      - anxiety_release
      - anger_release
      - grief_release
      - shame_release
```

---

## F005: Scenario Rescue Kit Format

### Format Policy YAML

```yaml
# phoenix_v4/policy/format_policies/scenario_rescue_kit.yaml

format_id: scenario_rescue_kit
format_name: "Scenario Rescue Kit"
description: "Acute intervention for specific triggering moments"

structure:
  chapter_count: 10-20
  chapter_duration_target: "3-7 minutes"
  use_case: "immediate_crisis_support"

slot_definitions:
  slot_01_scenario_match:
    category: scene
    role: entry
    description: "You're experiencing [scenario] - you're in the right place"
    persona_specific: true
    
  slot_02_validation:
    category: story
    role: recognition
    description: "This is real and makes sense"
    
  slot_03_immediate_practice:
    category: exercise
    role: grounding
    description: "First 60 seconds - nervous system regulation"
    
  slot_04_what_happening_story:
    category: story
    role: mechanism_proof
    description: "What's happening in your body/mind right now"
    
  slot_05_second_practice:
    category: exercise
    role: stabilization
    description: "Next step - continued regulation"
    
  slot_06_next_steps:
    category: scene
    role: closing
    description: "What to do after this audio"

scenarios_library:
  acute_anxiety:
    - panic_attack
    - social_anxiety_spike
    - generalized_anxiety_surge
    - anticipatory_anxiety
    
  relationship_crisis:
    - just_fought_partner
    - ghosted_or_rejected
    - boundary_violated
    - difficult_conversation_ahead
    
  work_stress:
    - before_presentation
    - after_criticism
    - burnout_moment
    - imposter_syndrome_spike
    
  grief_moments:
    - anniversary_trigger
    - unexpected_reminder
    - wave_of_grief
    - complicated_grief_spike
    
  trauma_activation:
    - flashback
    - trigger_response
    - dissociation_moment
    - hypervigilance_spike

k_table_requirements:
  story_validation: 20  # per scenario
  story_mechanism: 20
  exercise_grounding: 20
  exercise_stabilization: 20
  scene_scenario_match: 20
  scene_next_steps: 20

duplication_thresholds:
  paragraph_hash: 0.0
  sentence_hash: 0.14
  six_gram_overlap: 0.11
  grounding_exercise_similarity: 0.75  # some techniques overlap

audio_production:
  voice_tone: "calm_present_warm"
  pacing: "measured_not_rushed"
  background_music: "minimal_grounding_tones"
  
governance:
  clinical_advisor_approval: required
  safety_disclaimer: required
  crisis_resource_list: required
  no_medical_advice: enforced
```

### Catalog Planning

```yaml
domain: "Scenario Rescue Kits"
domain_id: D005

series_templates:

  - series_name: "SOS: [Emotion] Emergency Kit"
    persona_affinity: [all]
    angles:
      - anxiety_sos
      - panic_sos
      - grief_sos
      - anger_sos
      - overwhelm_sos
      
  - series_name: "Quick Calm for [Persona]"
    persona_affinity: varies
    angles:
      - healthcare_workers
      - parents
      - students
      - caregivers
      
  - series_name: "[Scenario] Rescue Guide"
    persona_affinity: [situational]
    angles:
      - relationship_crisis
      - work_stress
      - social_anxiety
      - trauma_triggers

capacity_assessment:
  max_books_per_year: 48  # high demand, short format
  atom_velocity_required: "medium"
```

---

## F006: Nervous System Ladder Format

### Format Policy YAML

```yaml
# phoenix_v4/policy/format_policies/nervous_system_ladder.yaml

format_id: nervous_system_ladder
format_name: "Nervous System Ladder"
description: "Polyvagal-informed state regulation journey"

structure:
  chapter_count: 8-12
  progression: "shutdown → fight_flight → social_engagement → play_rest"
  
  state_map:
    - dorsal_shutdown (freeze, collapse)
    - sympathetic_activation (fight/flight)
    - ventral_safe_social (connection)
    - ventral_play (joy, creativity)

slot_definitions:
  slot_01_state_entry:
    category: scene
    role: entry
    description: "Recognizing current nervous system state"
    
  slot_02_state_recognition:
    category: story
    role: recognition
    description: "What this state feels like - somatic + behavioral"
    
  slot_03_state_awareness:
    category: exercise
    role: awareness
    description: "Mapping current state in body"
    
  slot_04_state_mechanism:
    category: story
    role: mechanism_proof
    description: "Polyvagal science - why this state exists"
    
  slot_05_regulation_practice:
    category: exercise
    role: regulation
    description: "State-appropriate regulation technique"
    
  slot_06_co_regulation_story:
    category: story
    role: agency_glimmer
    description: "How to seek/offer co-regulation"
    
  slot_07_integration_practice:
    category: exercise
    role: integration
    description: "Practice for sustainable regulation"
    
  slot_08_state_flexibility:
    category: story
    role: embodiment
    description: "Building capacity to move between states"
    
  slot_09_closing:
    category: scene
    role: closing
    description: "Honoring nervous system wisdom"
    
  slot_10_ladder_step:
    category: scene
    role: transition
    description: "Moving to next state on ladder"

progression_principles:
  - start_where_you_are
  - no_forced_positivity
  - respect_shutdown_as_wisdom
  - celebrate_small_shifts
  
k_table_requirements:
  story_state_recognition: 12  # per state variant
  story_mechanism: 12
  story_agency: 12
  story_flexibility: 12
  exercise_awareness: 12
  exercise_regulation: 12
  exercise_integration: 12
  scene_state_entry: 12
  scene_closing: 12
  scene_ladder_step: 11

duplication_thresholds:
  paragraph_hash: 0.0
  sentence_hash: 0.15
  six_gram_overlap: 0.12

safety_protocols:
  trauma_informed_mandatory: true
  no_forcing_ventral: true
  respect_protective_states: true
  
audio_production:
  tone_matches_state: true
  pacing_matches_state: true
  # dorsal: very slow, gentle
  # sympathetic: steady, grounding
  # ventral: warm, connected
```

### Catalog Planning

```yaml
domain: "Nervous System Regulation"
domain_id: D006

series_templates:

  - series_name: "The Nervous System Ladder: [Outcome]"
    persona_affinity: [trauma_survivors, therapy_adjacent, HSPs]
    angles:
      - from_shutdown_to_safety
      - anxiety_to_calm
      - dysregulation_to_balance
      
  - series_name: "Polyvagal Healing for [Persona]"
    persona_affinity: varies
    angles:
      - healthcare_workers
      - parents
      - veterans
      - chronic_illness
```

---

## F007-F015: Abbreviated Specs

### F007: Shadow Work Series

```yaml
format_id: shadow_work_series
chapter_count: 8-12
progression: archetype_per_chapter

slot_structure:
  - archetype_introduction (scene)
  - shadow_recognition (story)
  - projection_awareness (exercise)
  - wound_exploration (story)
  - compassion_practice (exercise)
  - integration_story (story)
  - embodiment_practice (exercise)
  - closing (scene)

archetypes:
  - the_people_pleaser
  - the_perfectionist
  - the_avoider
  - the_controller
  - the_victim
  - the_critic
  - the_performer
  - the_rebel
  - the_martyr
  - the_cynic

persona_affinity: [millennials, gen_x, spiritual_seekers]
```

### F008: Micro-Habits Stacking

```yaml
format_id: micro_habits_stacking
chapter_count: 52
duration_per_chapter: "2-3 minutes"

slot_structure:
  - habit_introduction (scene)
  - why_tiny_matters (story)
  - 60_second_practice (exercise)
  - stacking_strategy (story)
  - closing (scene)

progression:
  weeks_1-13: foundation_habits
  weeks_14-26: emotional_regulation_habits
  weeks_27-39: relationship_habits
  weeks_40-52: integration_habits

persona_affinity: [busy_professionals, parents, adhd_community]
```

### F009: Parts Work (IFS)

```yaml
format_id: parts_work_ifs
chapter_count: 10-15
based_on: internal_family_systems

slot_structure:
  - part_introduction (scene)
  - part_recognition (story)
  - getting_to_know_part (exercise)
  - part_burden_story (story)
  - unburdening_practice (exercise)
  - self_leadership_story (story)
  - integration (exercise)
  - closing (scene)

parts_library:
  - inner_critic
  - protector
  - wounded_child
  - firefighter
  - manager
  - exile
  - wise_self
  - playful_part
  - grieving_part
  - angry_defender

persona_affinity: [therapy_adjacent, trauma_survivors]
clinical_advisor_required: true
```

### F010: Energy Management

```yaml
format_id: energy_management
chapter_count: 12-16
focus: protection_clearing_recharging

slot_structure:
  - energy_leak_identification (story)
  - somatic_awareness (exercise)
  - boundary_story (story)
  - boundary_practice (exercise)
  - clearing_technique (exercise)
  - recharge_story (story)
  - integration (scene)

energy_domains:
  - emotional_boundaries
  - physical_space
  - digital_hygiene
  - relationship_energy
  - work_boundaries
  - empathic_overwhelm
  - energy_vampires
  - seasonal_cycles
  - lunar_cycles
  - shielding_practices
  - grounding_daily
  - recharge_rituals

persona_affinity: [empaths, HSPs, caregivers, healthcare_workers]
```

### F011: Relationship Repair

```yaml
format_id: relationship_repair
chapter_count: 8-12
focus: healing_relational_wounds

slot_structure:
  - wound_recognition (story)
  - grief_practice (exercise)
  - pattern_understanding (story)
  - forgiveness_prep (exercise)
  - reparenting_story (story)
  - reparenting_practice (exercise)
  - boundary_story (story)
  - integration (scene)

relationship_types:
  - father_wounds
  - mother_wounds
  - sibling_wounds
  - romantic_wounds
  - friendship_wounds
  - self_relationship
  - spiritual_betrayal
  - cultural_wounds

persona_affinity: [all, especially 30-50 age range]
```

### F012: Permission Slip Collection

```yaml
format_id: permission_slip_collection
chapter_count: 52
duration_per_chapter: "90 seconds"

slot_structure:
  - permission_statement (scene)
  - brief_story (story)
  - integration (exercise)

permissions:
  - to_rest
  - to_feel
  - to_change_your_mind
  - to_need_help
  - to_say_no
  - to_be_imperfect
  - to_take_up_space
  - to_have_needs
  - to_be_angry
  - to_grieve
  - to_succeed
  - to_fail
  (40 more...)

persona_affinity: [gen_z, millennials, perfectionists]
```

### F013: Before/During/After Crisis

```yaml
format_id: crisis_companion
chapter_count: 3_sections_x_8_chapters
structure: phased_support

phase_1_before:
  chapters: 8
  focus: anticipatory_preparation
  
phase_2_during:
  chapters: 8
  focus: active_coping
  
phase_3_after:
  chapters: 8
  focus: integration_growth

crisis_types:
  - divorce
  - grief_loss
  - job_loss
  - diagnosis
  - burnout
  - relocation
  - betrayal
  - identity_crisis

persona_affinity: [situational, all]
```

### F014: Archetype Transformation

```yaml
format_id: archetype_transformation
chapter_count: 10-15
focus: identity_evolution

slot_structure:
  - current_archetype (story)
  - shadow_aspects (story)
  - embodiment_practice (exercise)
  - transition_story (story)
  - new_archetype_practice (exercise)
  - integration_story (story)
  - closing (scene)

transformation_journeys:
  - wounded_healer_to_wise_guide
  - anxious_achiever_to_peaceful_success
  - people_pleaser_to_authentic_giver
  - perfectionist_to_excellence_pursuer
  - victim_to_survivor_to_thriver

persona_affinity: [spiritual_seekers, midlife_transition]
```

### F015: Sensory Regulation Library

```yaml
format_id: sensory_regulation
chapter_count: 5-8
focus: five_senses_regulation

slot_structure:
  - sense_introduction (scene)
  - dysregulation_story (story)
  - sensory_exploration (exercise)
  - regulation_technique (exercise)
  - integration_story (story)
  - closing (scene)

chapters:
  - visual_anchoring
  - auditory_soothing
  - tactile_grounding
  - olfactory_regulation
  - taste_awareness
  - vestibular_balance
  - proprioceptive_grounding
  - interoceptive_awareness

persona_affinity: [neurodivergent, HSPs, sensory_processing]
```

---

## Implementation Priorities

### Phase 1: High-Impact Launch (Q1 2026)
1. **F001: 90-Day Transformation** - flagship format
2. **F005: Scenario Rescue Kit** - immediate utility
3. **F002: Daily Practice Rituals** - return listening

### Phase 2: Clinical Depth (Q2 2026)
4. **F004: Somatic Body Journey** - differentiation
5. **F006: Nervous System Ladder** - polyvagal authority
6. **F009: Parts Work (IFS)** - therapy integration

### Phase 3: Market Expansion (Q3 2026)
7. **F003: Challenge Series** - Gen Z capture
8. **F007: Shadow Work** - millennial depth
9. **F011: Relationship Repair** - universal need

### Phase 4: Niche Authority (Q4 2026)
10-15. Remaining formats per market testing

---

## K-Table Capacity Planning

### Atom Production Velocity Required

| Format | Story Atoms | Exercise Atoms | Scene Atoms | Total | Velocity |
|--------|-------------|----------------|-------------|-------|----------|
| F001 | 106 | 90 | 180 | 376 | Very High |
| F002 | 365-30 | 365-30 | 24-12 | 389-72 | Extreme |
| F003 | 42-21 | 21-7 | 42-21 | 105-49 | Medium |
| F004 | 45 | 45 | 44 | 134 | Medium |
| F005 | 40 | 40 | 40 | 120 | Medium |
| F006 | 48 | 36 | 33 | 117 | Medium |
| F007-15 | ~40 each | ~40 each | ~30 each | ~110 each | Medium |

**Production Strategy:**
- Prioritize F003, F004, F005, F006 (medium velocity)
- Build atom library for F001, F002 over 6 months
- Use Golden Phoenix Coverage Agent for provisional atoms
- Human approval bottleneck = rate limiter

---

## Duplication Simulation Adjustments

```yaml
# phoenix_v4/policy/duplication_thresholds_by_format.yaml

format_specific_overrides:

  daily_practice_rituals:
    sentence_hash: 0.18  # ritual language repeats
    practice_instruction_similarity: 0.80
    
  scenario_rescue_kit:
    grounding_exercise_similarity: 0.75  # techniques overlap
    
  micro_habits_stacking:
    sentence_hash: 0.20  # micro-teaching format
    
  permission_slip_collection:
    sentence_hash: 0.25  # permission language intentionally similar
    
  all_others:
    # use standard thresholds from §22.4
```

---

## Audio Production Considerations

### Format-Specific Voice Direction

```yaml
# registry/voice_registry_format_guidance.yaml

format_voice_profiles:

  90_day_transformation:
    tone: "supportive_steady_encouraging"
    pacing: "measured"
    energy: "consistent_grounded"
    
  daily_practice_rituals:
    tone: "meditative_gentle_warm"
    pacing: "slow"
    energy: "calm_present"
    background_music: true
    
  challenge_series:
    tone: "energized_direct_motivating"
    pacing: "brisk"
    energy: "uplifting_action"
    
  somatic_body_journey:
    tone: "gentle_trauma_informed_safe"
    pacing: "very_slow"
    energy: "grounding_tender"
    silence_generous: true
    
  scenario_rescue_kit:
    tone: "calm_present_reassuring"
    pacing: "measured_not_rushed"
    energy: "grounded_warm"
    
  nervous_system_ladder:
    tone: "matches_state_being_addressed"
    pacing: "state_appropriate"
    energy: "adaptive"
```

---

## Governance & Safety Protocols

### Clinical Advisor Review Requirements

| Format | Review Type | Frequency |
|--------|-------------|-----------|
| F004 (Somatic) | Full | Every book |
| F006 (Nervous System) | Full | Every book |
| F009 (Parts Work) | Full | Every book |
| F005 (Rescue Kit) | Sample | 20% of books |
| F011 (Relationship) | Sample | 20% of books |
| F013 (Crisis) | Full | Every book |
| Others | Initial | First 3 books per series |

### Safety Language Enforcement

```yaml
# phoenix_v4/policy/safety_language_by_format.yaml

mandatory_disclaimers:

  scenario_rescue_kit:
    - "This is not a substitute for professional help"
    - "If experiencing crisis, contact [resource]"
    - "This audio provides coping tools, not treatment"
    
  crisis_companion:
    - "Consult mental health professional for clinical support"
    - "Crisis resources: [list]"
    
  somatic_body_journey:
    - "If you experience dissociation, stop and seek support"
    - "Go at your own pace"
    - "This is not physical therapy"
```

---

## Omega Orchestration Integration

### Brand Affinity Mapping

```yaml
# omega/brand_registry/format_brand_affinity.yaml

brand_format_strategy:

  zen_daily:
    formats: [F002_daily_practice, F012_permission_slips]
    voice_id: calm_feminine_mid_30s
    
  resilience_path:
    formats: [F001_90_day, F006_nervous_system, F013_crisis]
    voice_id: grounded_gender_neutral_40s
    
  body_wisdom:
    formats: [F004_somatic, F015_sensory]
    voice_id: gentle_feminine_35_trauma_informed
    
  quick_shift:
    formats: [F005_rescue_kit, F008_micro_habits]
    voice_id: warm_energized_30s
    
  depth_work:
    formats: [F007_shadow, F009_parts, F011_relationship, F014_archetype]
    voice_id: wise_grounded_45_depth
    
  gen_z_real:
    formats: [F003_challenge, F012_permission]
    voice_id: authentic_direct_25
```

### Release Wave Strategy

```yaml
# omega/release_waves/format_rollout.yaml

wave_strategy:

  wave_1_foundation:
    month: "March 2026"
    formats: [F005_rescue_kit, F003_challenge_7day]
    books_per_format: 3
    rationale: "Quick wins, market testing"
    
  wave_2_depth:
    month: "April 2026"
    formats: [F004_somatic, F006_nervous_system]
    books_per_format: 2
    rationale: "Clinical differentiation"
    
  wave_3_daily:
    month: "May 2026"
    formats: [F002_daily_30day, F008_micro_habits]
    books_per_format: 4
    rationale: "Return listening capture"
    
  wave_4_transformation:
    month: "June 2026"
    formats: [F001_90day]
    books_per_format: 2
    rationale: "Flagship premium offering"
```

---

## CI Gate Additions

### New Format-Specific Gates

```yaml
# phoenix_v4/ci/format_validation_gates.yaml

additional_gates:

  gate_40_progressive_intensity:
    applies_to: [F001, F003]
    check: "exercise_duration_and_difficulty_increase_over_chapters"
    
  gate_41_state_appropriate_regulation:
    applies_to: [F006]
    check: "regulation_technique_matches_nervous_system_state"
    
  gate_42_standalone_chapter:
    applies_to: [F002, F008, F012]
    check: "each_chapter_complete_without_prior_chapters"
    
  gate_43_body_region_specificity:
    applies_to: [F004]
    check: "anatomical_accuracy_and_somatic_precision"
    
  gate_44_crisis_resource_inclusion:
    applies_to: [F005, F013]
    check: "crisis_hotline_info_present_in_metadata"
    
  gate_45_ifs_fidelity:
    applies_to: [F009]
    check: "internal_family_systems_framework_adherence"
```

---

## Success Metrics

### Format Performance Indicators

```yaml
success_metrics_per_format:

  completion_rate:
    F001_90day: 35%  # industry standard ~25%
    F002_daily: 60%  # return listening
    F003_challenge: 45%
    F004_somatic: 40%
    F005_rescue: 80%  # acute need
    
  repeat_listening:
    F002_daily: 15x average
    F005_rescue: 8x average
    F008_micro_habits: 12x average
    
  catalog_longevity:
    evergreen: [F001, F002, F004, F006]
    seasonal_spike: [F003, F012]
    crisis_dependent: [F005, F013]
```

---

## Next Steps: Implementation Roadmap

### Week 1-2: Format Policy Creation
- [ ] Create all 15 format YAML files
- [ ] Define slot structures
- [ ] Write K-table requirements
- [ ] Set duplication thresholds

### Week 3-4: Catalog Planning
- [ ] Domain decomposition per format
- [ ] Series template creation
- [ ] Angle generation for each series
- [ ] Capacity assessment

### Week 5-6: Blueprint Rotation
- [ ] Design 3+ variants per format
- [ ] Arc progression mapping
- [ ] Milestone placement logic

### Week 7-8: Audio Production Prep
- [ ] Voice profile creation per format
- [ ] SSML formatting rules
- [ ] Silence/pacing guidelines
- [ ] Background music selection

### Week 9-10: Safety & Governance
- [ ] Clinical advisor review protocols
- [ ] Safety language templates
- [ ] Disclaimer creation
- [ ] Crisis resource compilation

### Week 11-12: CI Integration
- [ ] Add new format validation gates
- [ ] Update duplication simulator
- [ ] Omega orchestration rules
- [ ] Release wave generator updates

### Week 13-14: QA Campaign
- [ ] Run `make v4_qa_1000` with new formats
- [ ] Coverage verification
- [ ] Duplication simulation
- [ ] Production readiness gate

### Week 15-16: Launch Wave 1
- [ ] F005 Scenario Rescue Kit (3 books)
- [ ] F003 Challenge Series (3 books)
- [ ] Monitor metrics, iterate

---

## Appendix A: Slot Structure Reference Table

| Format | Slots/Ch | Story | Exercise | Scene | Special |
|--------|----------|-------|----------|-------|---------|
| Standard (existing) | 10 | 5 | 2 | 3 | - |
| F001: 90-Day | 4-6 | 1-2 | 1 | 1-2 | Weekly/milestone |
| F002: Daily Practice | 5-6 | 2 | 1 | 2 | Lunar/seasonal |
| F003: Challenge | 6-7 | 2 | 1 | 3 | Milestone days |
| F004: Somatic | 9 | 3 | 3 | 3 | - |
| F005: Rescue Kit | 6 | 2 | 2 | 2 | - |
| F006: Nervous System | 10 | 4 | 3 | 3 | - |
| F007: Shadow Work | 8 | 3 | 2 | 3 | - |
| F008: Micro-Habits | 5 | 2 | 1 | 2 | - |
| F009: Parts Work | 8 | 3 | 2 | 3 | - |
| F010: Energy Mgmt | 7 | 3 | 3 | 1 | - |
| F011: Relationship | 8 | 4 | 2 | 2 | - |
| F012: Permissions | 3 | 1 | 1 | 1 | - |
| F013: Crisis | 6 | 2 | 2 | 2 | 3 phases |
| F014: Archetype | 7 | 3 | 2 | 2 | - |
| F015: Sensory | 6 | 2 | 2 | 2 | - |

---

## Appendix B: Atom Production Estimate

**Assumptions:**
- 5 personas
- 12 topics per format
- 3 roles per (story type)
- 2 exercise types per slot
- Conservative duplication simulation pass rate: 85%

**6-Month Atom Production Schedule:**

| Month | Focus Formats | Story Atoms | Exercise Atoms | Total |
|-------|---------------|-------------|----------------|-------|
| 1 | F003, F005, F008 | 500 | 300 | 800 |
| 2 | F004, F006, F015 | 600 | 400 | 1000 |
| 3 | F007, F009, F011 | 700 | 350 | 1050 |
| 4 | F010, F012, F013, F014 | 650 | 300 | 950 |
| 5 | F002 (30-day) | 800 | 500 | 1300 |
| 6 | F001 (90-day) | 1200 | 800 | 2000 |
| **Total** | **15 formats** | **4450** | **2650** | **7100** |

**Human Approval Bottleneck:**
- Assuming 50 atoms/day approval capacity
- 7100 atoms / 50 = 142 days (~5 months if sequential)
- Requires parallel review team of 3-4 reviewers

---

## Appendix C: Revenue Projection Model

**Per-Format Revenue Estimates (Year 1):**

| Format | Books | Avg Price | Units/Book | Revenue |
|--------|-------|-----------|------------|---------|
| F001: 90-Day | 12 | $24.99 | 800 | $239,904 |
| F002: Daily (30) | 24 | $19.99 | 600 | $287,856 |
| F003: Challenge | 18 | $14.99 | 1200 | $323,784 |
| F004: Somatic | 8 | $22.99 | 500 | $91,960 |
| F005: Rescue Kit | 30 | $12.99 | 1500 | $584,550 |
| F006: Nervous System | 6 | $24.99 | 400 | $59,976 |
| Others (F007-15) | 54 | $18.99 | 400 | $410,328 |
| **Total** | **152** | - | - | **$1,998,358** |

**Assumptions:**
- Modest market penetration (1-5% of niche)
- Repeat purchases for daily formats
- Bundle discounts not factored
- Excludes subscription revenue model

---

**END OF DEVELOPMENT SPECIFICATION**

This spec is ready for:
1. Engineering team review
2. Clinical advisor approval
3. Atom production planning
4. CI/CD pipeline integration
5. Phased rollout execution

Ma'at — do you want me to expand any specific format into a full production-ready spec, or start generating the actual format YAML files for Phoenix integration?
