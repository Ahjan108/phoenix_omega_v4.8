#!/usr/bin/env python3
"""
Phoenix Title Generation Engine v3
Production-grade title generation for 1,008+ unique audiobook titles across 24 brands.

Generates psychologically-informed, market-tested titles that:
- Own a searchable keyword from brand + topic vocabularies
- Name the invisible script (hidden belief) running the reader's life
- Carry brand voice through vocabulary and power verbs
- Signal persona without saying "for {persona}"
- Validate for uniqueness, grammar, topic appropriateness
- Support series angles and multi-market localization
"""

import json
import argparse
import sys
import random
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
import hashlib
from dataclasses import dataclass, asdict
from itertools import cycle


@dataclass
class Title:
    """Represents a generated title with all metadata."""
    book_id: str
    brand_id: str
    topic_id: str
    persona_id: str
    series_id: str
    angle_id: str
    title: str
    subtitle: str
    search_keyword: str
    invisible_script: str
    market: str
    locale_name: str
    city: str


# ============================================================================
# BRAND VOICE BANKS
# ============================================================================

BRAND_REGISTRY = {
    "stabilizer": {
        "name": "stabilizer",
        "archetype": "burned_out_professional",
        "context": "evening_wind_down",
        "promise": "calm nervous system",
        "keywords": ["nervous system regulation", "burnout recovery"],
        "tokens": ["calm", "grounded", "regulation", "safety"],
        "power_verbs": ["settle", "regulate", "anchor", "ground", "restore", "pause", "reset"],
        "adjectives": ["nervous", "braced", "frayed", "scattered", "wound-up", "restless", "racing"],
    },
    "optimizer": {
        "name": "optimizer",
        "archetype": "high_efficiency_achiever",
        "context": "morning_commute",
        "promise": "feel ahead of the day",
        "keywords": ["dopamine management", "focus system"],
        "tokens": ["focus", "clarity", "momentum", "discipline"],
        "power_verbs": ["sharpen", "streamline", "calibrate", "unlock", "activate", "prime"],
        "adjectives": ["scattered", "derailed", "unfocused", "reactive", "overwhelmed"],
    },
    "night_reset": {
        "name": "night_reset",
        "archetype": "insomniac_creative",
        "context": "late_night_spiral",
        "promise": "stop dreading the night",
        "keywords": ["insomnia", "racing thoughts", "sleep anxiety"],
        "tokens": ["calm", "rest", "release", "safety"],
        "power_verbs": ["quiet", "slow", "settle", "release", "surrender", "drift"],
        "adjectives": ["racing", "looping", "wired", "restless", "spiraling", "haunted"],
    },
    "career_lift": {
        "name": "career_lift",
        "archetype": "mid_career_stalled",
        "context": "sunday_planning",
        "promise": "feel unstuck",
        "keywords": ["career transition", "mid career"],
        "tokens": ["clarity", "momentum", "grounded", "choice"],
        "power_verbs": ["unstick", "reclaim", "reframe", "pivot", "choose", "build"],
        "adjectives": ["stuck", "derailed", "overlooked", "trapped", "aimless"],
    },
    "adhd_forge": {
        "name": "adhd_forge",
        "archetype": "neurodivergent_young_adult",
        "context": "afternoon_focus_crash",
        "promise": "stop feeling broken",
        "keywords": ["ADHD focus", "neurodivergent"],
        "tokens": ["focus", "clarity", "regulation", "acceptance"],
        "power_verbs": ["harness", "channel", "organize", "anchor", "activate", "work with"],
        "adjectives": ["scattered", "restless", "impulsive", "scattered-brain", "overstimulated"],
    },
    "longevity_lab": {
        "name": "longevity_lab",
        "archetype": "longevity_seeker",
        "context": "morning_health_routine",
        "promise": "feel in control of aging",
        "keywords": ["longevity", "healthspan"],
        "tokens": ["clarity", "calm", "regulation", "vitality"],
        "power_verbs": ["optimize", "sustain", "build", "preserve", "strengthen", "cultivate"],
        "adjectives": ["aging", "declining", "fragile", "deteriorating", "out-of-control"],
    },
    "creative_unfold": {
        "name": "creative_unfold",
        "archetype": "artistic_student",
        "context": "reflective_walk",
        "promise": "creative confidence",
        "keywords": ["creative block", "artist"],
        "tokens": ["flow", "grounded", "release", "curiosity"],
        "power_verbs": ["unfold", "explore", "emerge", "create", "trust", "surrender"],
        "adjectives": ["blocked", "frozen", "stifled", "self-doubting", "silenced"],
    },
    "resilient_parent": {
        "name": "resilient_parent",
        "archetype": "overwhelmed_parent",
        "context": "post_kids_bedtime",
        "promise": "feel like a person again",
        "keywords": ["parent burnout", "overwhelmed parent"],
        "tokens": ["calm", "grounded", "safety", "rest"],
        "power_verbs": ["reclaim", "pause", "protect", "restore", "soften", "rest"],
        "adjectives": ["depleted", "overwhelmed", "fragmented", "invisible", "burnt-out"],
    },
    "executive_calm": {
        "name": "executive_calm",
        "archetype": "corporate_leader",
        "context": "pre_board_meeting",
        "promise": "steady under pressure",
        "keywords": ["executive stress", "board meeting"],
        "tokens": ["clarity", "calm", "grounded", "presence"],
        "power_verbs": ["steady", "center", "anchor", "command", "ground", "compose"],
        "adjectives": ["pressured", "scattered", "reactive", "ungrounded", "overwhelmed"],
    },
    "trauma_path": {
        "name": "trauma_path",
        "archetype": "trauma_recovery_adult",
        "context": "therapy_integration",
        "promise": "feel safe in body",
        "keywords": ["trauma recovery", "somatic"],
        "tokens": ["safety", "grounded", "regulation", "witness"],
        "power_verbs": ["restore", "reclaim", "ground", "witness", "heal", "integrate"],
        "adjectives": ["unsafe", "fragmented", "disconnected", "hypervigilant", "numb"],
    },
    "spiritual_ground": {
        "name": "spiritual_ground",
        "archetype": "spiritually_curious_professional",
        "context": "morning_meditation",
        "promise": "connection to something larger",
        "keywords": ["meditation", "spiritual"],
        "tokens": ["presence", "grounded", "calm", "clarity"],
        "power_verbs": ["connect", "ground", "witness", "attune", "arrive", "open"],
        "adjectives": ["disconnected", "lost", "searching", "scattered", "empty"],
    },
    "focus_sprint": {
        "name": "focus_sprint",
        "archetype": "startup_founder",
        "context": "late_night_work",
        "promise": "sustain without burning out",
        "keywords": ["founder burnout", "startup focus"],
        "tokens": ["focus", "clarity", "momentum", "regulation"],
        "power_verbs": ["sustain", "sprint", "protect", "build", "navigate", "drive"],
        "adjectives": ["scattered", "burnt-out", "unfocused", "reactive", "exhausted"],
    },
    "hormone_reset": {
        "name": "hormone_reset",
        "archetype": "women_35_plus",
        "context": "health_research_evening",
        "promise": "feel in control of body",
        "keywords": ["hormone health", "women 35+"],
        "tokens": ["calm", "grounded", "regulation", "vitality"],
        "power_verbs": ["regulate", "balance", "reclaim", "restore", "align", "attune"],
        "adjectives": ["out-of-control", "moody", "depleted", "disconnected", "frustrated"],
    },
    "stoic_edge": {
        "name": "stoic_edge",
        "archetype": "young_male_growth",
        "context": "gym_drive",
        "promise": "mental toughness",
        "keywords": ["stoic", "mental toughness"],
        "tokens": ["clarity", "discipline", "grounded", "focus"],
        "power_verbs": ["sharpen", "strengthen", "forge", "command", "build", "master"],
        "adjectives": ["weak", "distracted", "soft", "undisciplined", "unmotivated"],
    },
    "calm_student": {
        "name": "calm_student",
        "archetype": "gen_z_student",
        "context": "pre_exam_evening",
        "promise": "stop spiraling",
        "keywords": ["exam anxiety", "student stress"],
        "tokens": ["calm", "grounded", "focus", "safety"],
        "power_verbs": ["calm", "anchor", "focus", "settle", "quiet", "ground"],
        "adjectives": ["spiraling", "panicked", "frozen", "scattered", "overwhelmed"],
    },
    "healing_ground": {
        "name": "healing_ground",
        "archetype": "chronic_stress_worker",
        "context": "lunch_break",
        "promise": "reset in the middle of the day",
        "keywords": ["lunch break calm", "chronic stress"],
        "tokens": ["calm", "grounded", "regulation", "reset"],
        "power_verbs": ["reset", "pause", "ground", "restore", "breathe", "return"],
        "adjectives": ["stressed", "wound-up", "frazzled", "scattered", "exhausted"],
    },
    "bio_flow": {
        "name": "bio_flow",
        "archetype": "biohacker",
        "context": "quantified_self_review",
        "promise": "optimize and feel good",
        "keywords": ["biohacking", "quantified self"],
        "tokens": ["clarity", "optimization", "regulation", "focus"],
        "power_verbs": ["optimize", "track", "calibrate", "unlock", "activate", "design"],
        "adjectives": ["suboptimal", "inefficient", "untracked", "reactive", "scattered"],
    },
    "confidence_core": {
        "name": "confidence_core",
        "archetype": "socially_anxious_adult",
        "context": "pre_social_event",
        "promise": "feel okay showing up",
        "keywords": ["social anxiety", "pre-event calm"],
        "tokens": ["safety", "grounded", "calm", "confidence"],
        "power_verbs": ["ground", "steady", "anchor", "arrive", "show up", "calm"],
        "adjectives": ["anxious", "self-conscious", "judged", "exposed", "fragile"],
    },
    "relationship_clarity": {
        "name": "relationship_clarity",
        "archetype": "couples_repair",
        "context": "post_argument",
        "promise": "repair and reconnect",
        "keywords": ["couples", "relationship repair"],
        "tokens": ["calm", "grounded", "connection", "safety"],
        "power_verbs": ["repair", "reconnect", "soften", "understand", "bridge", "restore"],
        "adjectives": ["broken", "disconnected", "defensive", "wounded", "estranged"],
    },
    "morning_momentum": {
        "name": "morning_momentum",
        "archetype": "early_riser_professional",
        "context": "sunrise_drive",
        "promise": "feel set for the day",
        "keywords": ["morning routine", "early riser"],
        "tokens": ["clarity", "momentum", "focus", "calm"],
        "power_verbs": ["prime", "set", "activate", "launch", "build", "anchor"],
        "adjectives": ["rushed", "scattered", "unfocused", "reactive", "unprepared"],
    },
    "minimal_mind": {
        "name": "minimal_mind",
        "archetype": "digital_overwhelm_adult",
        "context": "doomscroll_fatigue",
        "promise": "feel less scattered",
        "keywords": ["digital detox", "doomscroll"],
        "tokens": ["calm", "clarity", "grounded", "reset"],
        "power_verbs": ["detox", "simplify", "pause", "disconnect", "clear", "reset"],
        "adjectives": ["scattered", "addicted", "overwhelmed", "numb", "drained"],
    },
    "high_performer": {
        "name": "high_performer",
        "archetype": "competitive_sales",
        "context": "pre_call_prep",
        "promise": "confident under pressure",
        "keywords": ["sales confidence", "pre-call"],
        "tokens": ["focus", "confidence", "clarity", "grounded"],
        "power_verbs": ["prime", "sharpen", "activate", "command", "execute", "close"],
        "adjectives": ["scattered", "anxious", "unprepared", "reactive", "unfocused"],
    },
    "gentle_growth": {
        "name": "gentle_growth",
        "archetype": "therapy_newcomer",
        "context": "journaling_time",
        "promise": "feel safe exploring",
        "keywords": ["therapy beginner", "journaling"],
        "tokens": ["safety", "curiosity", "grounded", "gentle"],
        "power_verbs": ["explore", "discover", "gently", "unfold", "trust", "arrive"],
        "adjectives": ["scared", "hesitant", "fragile", "self-critical", "overwhelmed"],
    },
    "legacy_builder": {
        "name": "legacy_builder",
        "archetype": "45_plus_reinventor",
        "context": "life_transition",
        "promise": "meaning in next chapter",
        "keywords": ["midlife", "reinvention", "life transition"],
        "tokens": ["clarity", "grounded", "meaning", "presence"],
        "power_verbs": ["build", "reclaim", "step into", "author", "create", "discover"],
        "adjectives": ["lost", "adrift", "aimless", "invisible", "unmoored"],
    },
}


# ============================================================================
# TOPIC VOCABULARIES
# ============================================================================

TOPIC_VOCABULARY = {
    "anxiety": {
        "search_keywords": ["anxiety management", "nervous system calm", "worry reduction"],
        "invisible_scripts": [
            "something bad is always about to happen",
            "my body can't be trusted",
            "I need to stay vigilant to stay safe",
            "if I worry enough, I can prevent disaster",
            "calm means I'm not paying attention",
            "anxiety is a sign I'm doing it wrong",
        ],
        "power_verbs": ["quiet", "calm", "settle", "ground", "anchor", "release"],
        "nouns": ["alarm", "spiral", "dread", "anticipation", "vigilance", "bracing"],
        "forbidden_tokens": [],
    },
    "boundaries": {
        "search_keywords": ["boundary setting", "saying no", "assertiveness"],
        "invisible_scripts": [
            "my needs are selfish",
            "I can earn love by giving",
            "saying no ruins relationships",
            "good people don't have limits",
            "boundaries mean I don't care",
        ],
        "power_verbs": ["reclaim", "set", "speak", "honor", "protect", "claim"],
        "nouns": ["edge", "limit", "line", "claim", "permission", "sovereignty"],
        "forbidden_tokens": [],
    },
    "burnout": {
        "search_keywords": ["burnout recovery", "work-life balance", "sustainable pace"],
        "invisible_scripts": [
            "my worth is my output",
            "rest is laziness",
            "I have to do it all",
            "stopping means failing",
            "rest is irresponsible",
        ],
        "power_verbs": ["restore", "pace", "protect", "reclaim", "rebuild", "reset"],
        "nouns": ["fire", "emptiness", "collapse", "depletion", "extraction"],
        "forbidden_tokens": [],
    },
    "compassion_fatigue": {
        "search_keywords": ["caregiver burnout", "compassion fatigue", "helper depletion"],
        "invisible_scripts": [
            "my wellbeing is secondary",
            "I should be able to help without cost",
            "I can't stop even if I'm dying",
            "self-care is abandonment",
        ],
        "power_verbs": ["restore", "reclaim", "protect", "refill", "replenish", "return"],
        "nouns": ["emptiness", "depletion", "sacrifice", "cost", "extraction"],
        "forbidden_tokens": [],
    },
    "courage": {
        "search_keywords": ["courage building", "fear facing", "brave choices"],
        "invisible_scripts": [
            "I'm too afraid to try",
            "courage means fearlessness",
            "I'm the only one scared",
            "being brave means being alone",
        ],
        "power_verbs": ["step into", "face", "choose", "build", "forge", "claim"],
        "nouns": ["fear", "doubt", "calling", "possibility", "threshold"],
        "forbidden_tokens": [],
    },
    "depression": {
        "search_keywords": ["depression management", "low mood recovery", "emotional pain"],
        "invisible_scripts": [
            "I'm broken",
            "nothing will ever change",
            "my pain is too big to survive",
            "I don't deserve to feel better",
            "if I feel good, I'll drop my guard",
        ],
        "power_verbs": ["emerge", "return", "lift", "rise", "reclaim", "unfold"],
        "nouns": ["weight", "fog", "numbness", "void", "heaviness", "darkness"],
        "forbidden_tokens": ["sprint", "hack", "crush", "optimize", "disrupt"],
    },
    "financial_anxiety": {
        "search_keywords": ["financial anxiety", "money worry", "financial security"],
        "invisible_scripts": [
            "I'm always one crisis away from disaster",
            "money is dangerous",
            "I don't deserve to have money",
            "financial security is for other people",
        ],
        "power_verbs": ["steady", "build", "secure", "clarify", "reclaim", "anchor"],
        "nouns": ["instability", "threat", "fear", "chaos", "scarcity"],
        "forbidden_tokens": [],
    },
    "financial_stress": {
        "search_keywords": ["financial pressure", "money stress", "earning clarity"],
        "invisible_scripts": [
            "I have to do it all to survive",
            "earning means suffering",
            "money is too complicated",
            "my financial situation is permanent",
        ],
        "power_verbs": ["build", "grow", "clarify", "navigate", "steady", "secure"],
        "nouns": ["pressure", "weight", "complexity", "overwhelm", "instability"],
        "forbidden_tokens": [],
    },
    "grief": {
        "search_keywords": ["grief support", "loss processing", "bereavement"],
        "invisible_scripts": [
            "my grief is too big to survive",
            "if I stop crying, I'm abandoning them",
            "good people don't recover from loss",
            "grief never ends, it just changes",
        ],
        "power_verbs": ["honor", "carry", "move through", "integrate", "transform", "witness"],
        "nouns": ["loss", "absence", "void", "weight", "sorrow", "remembrance"],
        "forbidden_tokens": ["confident", "crush", "optimize", "disrupt"],
    },
    "imposter_syndrome": {
        "search_keywords": ["imposter syndrome", "self-doubt", "confidence at work"],
        "invisible_scripts": [
            "I don't belong here",
            "everyone will eventually find out I'm a fraud",
            "I didn't earn this",
            "I'm not smart enough",
            "success is happening to me, not because of me",
        ],
        "power_verbs": ["claim", "earn", "arrive", "reclaim", "own", "step into"],
        "nouns": ["doubt", "fraud", "threshold", "proof", "belonging"],
        "forbidden_tokens": [],
    },
    "overthinking": {
        "search_keywords": ["overthinking", "rumination", "racing thoughts"],
        "invisible_scripts": [
            "if I think about it enough, I can solve it",
            "my thoughts are reality",
            "stopping thinking means I'm lazy",
            "I can think my way to safety",
        ],
        "power_verbs": ["quiet", "settle", "pause", "interrupt", "anchor", "return"],
        "nouns": ["spiral", "loop", "loop", "noise", "clutter", "weight"],
        "forbidden_tokens": [],
    },
    "self_worth": {
        "search_keywords": ["self-worth", "self-esteem", "inherent value"],
        "invisible_scripts": [
            "I'm only worthy if I'm productive",
            "I have to earn the right to exist",
            "my value depends on others' approval",
            "being wrong means being bad",
            "I'm fundamentally less than",
        ],
        "power_verbs": ["reclaim", "anchor", "return", "own", "trust", "arrive"],
        "nouns": ["core", "essence", "value", "truth", "worth", "foundation"],
        "forbidden_tokens": [],
    },
    "sleep_anxiety": {
        "search_keywords": ["sleep anxiety", "insomnia", "nighttime worry"],
        "invisible_scripts": [
            "I can't sleep without fear",
            "the night is dangerous",
            "if I sleep, I'll miss disaster",
            "my mind won't let me rest",
        ],
        "power_verbs": ["settle", "drift", "surrender", "quiet", "release", "rest"],
        "nouns": ["dread", "spiral", "anticipation", "restlessness", "racing"],
        "forbidden_tokens": [],
    },
    "social_anxiety": {
        "search_keywords": ["social anxiety", "social confidence", "social courage"],
        "invisible_scripts": [
            "people are judging me",
            "I'll do something embarrassing",
            "I don't belong with these people",
            "I can't trust anyone",
            "being seen means being rejected",
        ],
        "power_verbs": ["ground", "arrive", "show up", "calm", "steady", "anchor"],
        "nouns": ["judgment", "exposure", "shame", "scrutiny", "belonging"],
        "forbidden_tokens": [],
    },
    "somatic_healing": {
        "search_keywords": ["somatic healing", "body healing", "embodiment"],
        "invisible_scripts": [
            "my body is my enemy",
            "I'm not safe in my body",
            "I have to escape my body to be safe",
            "healing happens in my head, not my body",
        ],
        "power_verbs": ["return", "inhabit", "ground", "restore", "integrate", "arrive"],
        "nouns": ["body", "ground", "safety", "home", "embodiment", "presence"],
        "forbidden_tokens": [],
    },
}


# ============================================================================
# PERSONA HOOK LIBRARIES
# ============================================================================

PERSONA_LIBRARY = {
    "millennial_women_professionals": {
        "tier": 1,
        "vibe": "warm, direct, intelligent; treats her as capable, not broken",
        "forbidden": ["girlboss", "lean in", "manifest", "queen", "slay", "hustle", "wine o'clock", "mompreneur", "tribe"],
        "patterns": [
            "The {Noun} You've Been Carrying",
            "When {Symptom} Is Actually {Mechanism}",
            "{Verb} Without {Cost}",
            "What {Trigger} Is Really About",
            "{Noun}: Why {Belief} Is Keeping You {State}",
            "The {Invisible Script} Keeping You {State}",
            "What No One Told You About {Noun}",
            "The {Noun} Behind the {Cost}",
            "After the {Noun}: Finding {Verb}",
            "The Quiet {Noun}",
            "Before You {Verb} Again",
            "{Noun} and the Lie of {Cost}",
        ],
        "subtitle_hooks": [
            "for women who've built everything but don't know how to rest",
            "for women managing impossible expectations",
            "for women who thought success would feel better than this",
            "for women who are done performing",
            "a clear-eyed guide for women who know better",
            "for women who carry everything and ask for nothing",
            "for professional women rethinking what strength means",
        ],
    },
    "tech_finance_burnout": {
        "tier": 1,
        "vibe": "analytical, slightly sardonic, respects their intelligence",
        "forbidden": ["hustle", "grind", "10x", "growth hacking", "disrupt", "synergy"],
        "patterns": [
            "The {System} That Crashed",
            "When {Optimization} Becomes the Problem",
            "{Verb} Without the {Tech Metric}",
            "After the {Tech Event}",
            "Why {Belief} Is Keeping You {State}",
            "The {Invisible Script} in Your {System}",
            "Debug Your {Noun}",
            "The {Noun} Your Dashboard Can't Show",
            "{Noun}: A System Failure",
            "Running Hot: The {Noun}",
            "The Human Metric: {Noun}",
            "When {Symptom} Is a Feature, Not a Bug",
        ],
        "subtitle_hooks": [
            "for people who optimized themselves into a corner",
            "for people who built the systems but can't live in them",
            "for ambitious people learning unsustainability is a feature, not a bug",
            "for people who built everything but forgot to build themselves",
            "for high-performers whose metrics are green but they're running red",
            "for people who debug systems but can't debug themselves",
        ],
    },
    "entrepreneurs": {
        "tier": 1,
        "vibe": "pragmatic, direct, respects the grind",
        "forbidden": ["passive income", "4-hour work week", "digital nomad", "crush it", "six figures", "empire", "boss babe"],
        "patterns": [
            "The {Noun} Building You (While You Build)",
            "{Verb} Without the {Cost}",
            "When {Belief} Becomes {Cost}",
            "The {Invisible Script} in Your Business",
            "What {Noun} Is Costing Your Business",
            "The Founder's {Noun}",
            "After the {Noun}: A Founder's Guide",
            "Beyond the {Noun}",
            "{Noun} with Finite Runway",
            "Your Business Is Not Your {Noun}",
            "What the Spreadsheet Can't Show: {Noun}",
            "Build Without {Cost}",
        ],
        "subtitle_hooks": [
            "for founders learning to build sustainable lives, not just sustainable businesses",
            "for people who built the thing but lost themselves",
            "for ambitious people learning what actually sustains",
            "for founders whose identity fused with their company",
            "for entrepreneurs who treated their nervous system like it had infinite runway",
        ],
    },
    "working_parents": {
        "tier": 2,
        "vibe": "warm, knowing, unhurried, validates the difficulty",
        "forbidden": ["mommy wine culture", "supermom", "blessed", "cherish every moment", "it goes so fast", "mompreneur", "hot mess"],
        "patterns": [
            "When {Belief} Meets {Cost}",
            "{Verb} Without {Cost}",
            "The {Invisible Script} Stealing Your {Noun}",
            "{Noun}: Why {Belief} Is Hurting You",
            "Still Here, Still {Verb}ing",
            "After Bedtime: The {Noun}",
            "The {Noun} Nobody Sees",
            "What Happens After the {Noun}",
            "Parent First, {Noun} Second",
            "The {Noun} Between Bath Time and Bedtime",
            "{Verb} in the Margins",
            "The 10 Minutes That Matter: {Noun}",
        ],
        "subtitle_hooks": [
            "for parents who love their kids and are barely surviving",
            "for people managing impossible expectations from all sides",
            "for parents learning that collapse isn't commitment",
            "for the parent who has nothing left at the end of the day",
            "for parents who are present everywhere and rested nowhere",
        ],
    },
    "gen_x_sandwich": {
        "tier": 2,
        "vibe": "pragmatic, wry, no-bullshit, skeptical of self-help",
        "forbidden": ["found yourself", "authentic journey", "lean into", "manifest"],
        "patterns": [
            "The {Noun} You're Actually Carrying",
            "When {Noun} Is Not Yours",
            "{Verb} Without {Cost}",
            "What {Belief} Is Costing You",
            "Nobody's Coming: The {Noun}",
            "The {Noun} in the Middle",
            "Carrying Two Generations: {Noun}",
            "Is This All There Is: {Noun}",
            "What {Noun} Looks Like at {Symptom}",
            "The {Noun} You Never Asked For",
            "After {Noun}: Now What",
            "The Load-Bearing {Noun}",
        ],
        "subtitle_hooks": [
            "for people who are taking care of everyone but themselves",
            "for pragmatic people learning boundaries matter",
            "for people in the middle of everything",
            "for the generation that was told to figure it out alone",
            "for people who earned their cynicism about self-help",
        ],
    },
    "corporate_managers": {
        "tier": 2,
        "vibe": "professional, direct, results-oriented",
        "forbidden": ["servant leader", "authentic self", "vulnerable", "cultural fit"],
        "patterns": [
            "How {Belief} Is Limiting Your {Noun}",
            "When {Noun} Meets {Cost}",
            "{Verb} Without {Cost}",
            "The {Noun} Your Team Needs You to Name",
            "Leading Through {Noun}",
            "The {Noun} Above the Org Chart",
            "Managing {Noun}: A Leader's Guide",
            "Before the All-Hands: {Noun}",
            "The {Noun} Behind Closed Doors",
            "Your Team Sees Your {Noun}",
            "{Verb} and Still Lead",
            "The {Noun} Between Strategy and Survival",
        ],
        "subtitle_hooks": [
            "for leaders learning to lead themselves first",
            "for managers who give everything and have nothing left",
            "for leaders who absorb everyone's stress and call it leadership",
            "for the manager who's holding it together so their team doesn't have to",
        ],
    },
    "gen_z_professionals": {
        "tier": 3,
        "vibe": "authenticity-driven, direct, no corporate speak",
        "forbidden": ["growth mindset", "lean in", "authentic self", "unlocking"],
        "patterns": [
            "The {Noun} You're Expected to Carry",
            "When {Belief} Meets {Cost}",
            "{Verb} Without {Cost}",
            "The {Noun} They Said Was Normal",
            "You're Not Behind: {Noun}",
            "What They Call {Noun}",
            "The {Noun} Your Feed Won't Show",
            "Stop Performing {Noun}",
            "The Real {Noun}",
            "{Noun} Is Not Your Personality",
            "After the {Noun}: What's Actually True",
            "The {Noun} Underneath the Performance",
        ],
        "subtitle_hooks": [
            "for young professionals learning the rules don't actually apply",
            "for people learning to opt out of unsustainable paths",
            "for the generation that inherited a broken world and is expected to thrive in it",
            "for new professionals tired of pretending they have it figured out",
        ],
    },
    "healthcare_rns": {
        "tier": 3,
        "vibe": "caregiver-identity, direct, understands duty",
        "forbidden": ["self-care is the answer", "mindfulness fixes systems", "you need more rest"],
        "patterns": [
            "When {Belief} Meets Your {Cost}",
            "The {Noun} You're Carrying from the Ward",
            "{Verb} Without {Cost}",
            "After the Shift: {Noun}",
            "The Drive Home: {Noun}",
            "What You Carry Home: {Noun}",
            "The {Noun} Between Patients",
            "Before the Next Shift: {Noun}",
            "Your {Noun} Is Not a Weakness",
            "Healing the Healer: {Noun}",
            "The {Noun} the Training Never Covered",
            "Code {Noun}: What Happens After",
        ],
        "subtitle_hooks": [
            "for nurses who save lives but can't save themselves",
            "for healthcare workers learning they can't pour from empty cups",
            "for clinicians whose compassion became a wound",
            "for nurses who carry the ward home in their body",
        ],
    },
    "gen_alpha_students": {
        "tier": 3,
        "vibe": "age-appropriate, pressure-aware, validating",
        "forbidden": ["just focus more", "study harder", "you'll regret this"],
        "patterns": [
            "When {Belief} Becomes Your {Cost}",
            "The {Noun} School Never Names",
            "{Verb} Without {Cost}",
            "It's Okay to Not {Verb}",
            "The {Noun} Nobody Talks About",
            "You're Not the Only One: {Noun}",
            "What {Noun} Actually Feels Like",
            "Before the Exam: {Noun}",
            "The {Noun} Behind the Grade",
            "Your {Noun} Is Real",
            "{Noun} Is Not Your Fault",
            "What Adults Don't Say About {Noun}",
        ],
        "subtitle_hooks": [
            "for students learning the system's pressure doesn't define their worth",
            "for young people learning their future isn't decided at 16",
            "for the young person who needs real tools, not motivational posters",
            "for students who feel the weight of a world they didn't build",
        ],
    },
    "first_responders": {
        "tier": 3,
        "vibe": "duty/service language, respect for sacrifice",
        "forbidden": ["just let it go", "think positive", "you're overreacting"],
        "patterns": [
            "When {Noun} Meets {Cost}",
            "The {Noun} You're Carrying from the Job",
            "{Verb} Without {Cost}",
            "After the Call: {Noun}",
            "The {Noun} Nobody Debriefs",
            "What the Badge Doesn't Cover: {Noun}",
            "Between Calls: {Noun}",
            "The {Noun} That Follows You Home",
            "Off Duty: {Noun}",
            "The Thing You Can't Unsee: {Noun}",
            "Serving and {Verb}ing",
            "The {Noun} Behind the Uniform",
        ],
        "subtitle_hooks": [
            "for people who serve and are barely surviving",
            "for heroes learning their sacrifice has limits",
            "for first responders trained to save everyone but themselves",
            "for those who run toward danger and never process the aftermath",
        ],
    },
}


# ============================================================================
# SERIES & ANGLES
# ============================================================================

SERIES_REGISTRY = {
    "social_anxiety_arc": {
        "cluster": "anxiety_cluster",
        "angles": ["at_work", "on_dates", "public_speaking", "at_parties", "online", "with_authority_figures", "in_new_groups", "after_conflict"],
    },
    "panic_response_arc": {
        "cluster": "anxiety_cluster",
        "angles": ["at_night", "while_driving", "in_public", "at_work", "physical_symptoms", "anticipatory"],
    },
    "acute_loss_arc": {
        "cluster": "grief_cluster",
        "angles": ["sudden_loss", "long_illness_loss", "loss_of_parent", "loss_of_partner", "loss_of_child", "grieving_alone"],
    },
    "ambiguous_loss_arc": {
        "cluster": "grief_cluster",
        "angles": ["estranged_family", "dementia_loss", "relationship_ending", "pregnancy_loss", "identity_loss"],
    },
    "social_shame_arc": {
        "cluster": "shame_cluster",
        "angles": ["imposter_at_work", "after_public_mistake", "fear_of_promotion", "hiding_struggle", "comparison_trap", "first_generation_shame"],
    },
    "body_shame_arc": {
        "cluster": "shame_cluster",
        "angles": ["in_professional_settings", "in_intimate_relationships", "in_health_contexts", "on_social_media", "after_body_change"],
    },
}

# Mapping topics to series
SERIES_TOPIC_MAP = {
    "anxiety": ["social_anxiety_arc", "panic_response_arc"],
    "grief": ["acute_loss_arc", "ambiguous_loss_arc"],
    "imposter_syndrome": ["social_shame_arc"],
    "self_worth": ["body_shame_arc", "social_shame_arc"],
}


# ============================================================================
# CITY CUSTOMIZATION
# ============================================================================

CITY_PERSONAS = {
    "nyc": ["millennial_women_professionals", "tech_finance_burnout"],
    "la": ["entrepreneurs", "millennial_women_professionals"],
    "sf": ["tech_finance_burnout", "bio_flow"],
    "chicago": ["working_parents", "corporate_managers"],
    "boston": ["tech_finance_burnout", "gen_z_professionals"],
    "dc": ["corporate_managers", "high_performer"],
}


# ============================================================================
# TITLE GENERATION ENGINE
# ============================================================================

class TitleGenerator:
    """Generates psychologically-informed titles for audiobook catalog."""

    def __init__(self):
        self.generated_titles = set()
        self.title_details = {}
        self.validation_errors = []

    def generate_invisible_script(self, brand_id: str, topic_id: str, persona_id: str) -> str:
        """Generate a persona-specific invisible script."""
        topic_vocab = TOPIC_VOCABULARY[topic_id]
        persona = PERSONA_LIBRARY[persona_id]

        scripts = topic_vocab["invisible_scripts"]
        # Weight by persona tier (Tier 1 gets more sophisticated scripts)
        if persona["tier"] == 1:
            # Tier 1: more complex, layered invisible scripts
            if len(scripts) > 2:
                return scripts[len(persona_id) % len(scripts)]
        elif persona["tier"] == 2:
            # Tier 2: moderately sophisticated
            if len(scripts) > 1:
                return scripts[(len(persona_id) + len(topic_id)) % len(scripts)]
        else:
            # Tier 3: simpler, more direct
            return scripts[0]

        return scripts[0]

    def generate_title(self, brand_id: str, topic_id: str, persona_id: str,
                      series_id: str = "", angle_id: str = "", variation: int = 0) -> Tuple[str, str]:
        """
        Generate a unique title and subtitle using seeded random selection.
        variation: 0-based index for different title variants from same brand-topic-persona combo
        Returns: (title, subtitle)
        """
        import re

        brand = BRAND_REGISTRY[brand_id]
        topic_vocab = TOPIC_VOCABULARY[topic_id]
        persona = PERSONA_LIBRARY[persona_id]

        # Create deterministic seed for this specific combination
        seed_string = f"{brand_id}:{topic_id}:{persona_id}:{series_id}:{angle_id}:{variation}"
        rng = random.Random(seed_string)

        # Use seeded random to select title pattern
        title_pattern = rng.choice(persona["patterns"])

        # Get vocabulary components
        power_verbs = topic_vocab["power_verbs"]
        nouns = topic_vocab["nouns"]
        brand_adjectives = brand["adjectives"]

        # Use seeded random to select core components
        verb = rng.choice(power_verbs)
        noun = rng.choice(nouns)
        symptom = rng.choice(brand_adjectives)

        # Dynamic variable pools — selected via seeded random
        mechanism_pool = ["system protection", "nervous system defense", "survival wiring",
                          "pattern recognition", "threat detection", "adaptation", "self-preservation",
                          "coping architecture", "protective shutdown", "emotional armor"]
        cost_pool = ["unsustainability", "burnout", "disconnection", "numbness", "exhaustion",
                     "self-abandonment", "isolation", "silence", "collapse", "emptiness"]
        belief_pool = [symptom, noun, "the myth", "the story", "the rule", "the standard",
                       "the expectation", "the script", "the assumption", "the pattern"]
        state_pool = ["stuck", "frozen", "spinning", "sinking", "hiding", "performing",
                      "bracing", "numbing", "avoiding", "shrinking"]
        system_pool = ["system", "algorithm", "operating system", "pattern", "loop",
                       "circuit", "program", "architecture", "protocol", "routine"]
        tech_event_pool = ["the crash", "the reorg", "the burnout", "the layoff",
                           "the all-hands", "the pivot", "the quiet quit", "the PIP"]
        tech_metric_pool = ["optimization", "efficiency", "throughput", "velocity",
                            "the KPI", "the OKR", "the sprint", "uptime"]
        business_belief_pool = ["the grind", "the hustle myth", "founder mode", "the runway panic",
                                "the pivot pressure", "the growth imperative", "bootstrapping identity"]
        parenting_belief_pool = ["the myth", "the should-pile", "the guilt cycle", "the perfect parent lie",
                                 "the comparison trap", "the invisible labor", "the bedtime battle"]
        responsibility_pool = ["the weight", "the load", "the invisible cost", "the carrying",
                               "the holding", "the absorbing", "the managing", "the protecting"]
        impossible_pool = ["it all", "perfection", "the standard", "the impossible", "enough",
                           "the expectation", "the performance", "the role"]
        duty_pool = ["duty", "the oath", "the call", "the shift", "the scene",
                     "the uniform", "the weight of service", "the cost of showing up"]

        # Pick a second noun that differs from the first for patterns with repeated slots
        alt_nouns = [n for n in nouns if n != noun]
        alt_noun = rng.choice(alt_nouns) if alt_nouns else noun

        template_vars = {
            "Verb": verb.capitalize(),
            "Noun": noun.capitalize(),
            "Symptom": symptom.capitalize(),
            "Trigger": alt_noun.capitalize(),
            "Mechanism": rng.choice(mechanism_pool),
            "Cost": rng.choice(cost_pool),
            "Belief": rng.choice(belief_pool),
            "Invisible Script": f"{alt_noun}",
            "State": rng.choice(state_pool),
            "Tech Event": rng.choice(tech_event_pool),
            "Tech Metric": rng.choice(tech_metric_pool),
            "Optimization": rng.choice(tech_metric_pool),
            "System": rng.choice(system_pool),
            "Business": "business",
            "Business Belief": rng.choice(business_belief_pool),
            "Parenting Belief": rng.choice(parenting_belief_pool),
            "Reality": rng.choice(cost_pool),
            "Responsibility": rng.choice(responsibility_pool),
            "Impossible Task": rng.choice(impossible_pool),
            "Impossible Standard": rng.choice(impossible_pool),
            "Impossible Expectation": rng.choice(impossible_pool),
            "Management Belief": rng.choice(belief_pool),
            "Team Need": rng.choice(responsibility_pool),
            "Your Limit": rng.choice(cost_pool),
            "Your What": "yourself",
            "Burnout Path": rng.choice(cost_pool),
            "Healthcare Belief": rng.choice(belief_pool),
            "School Belief": rng.choice(belief_pool),
            "Duty": rng.choice(duty_pool),
        }

        # Apply template substitution
        title = title_pattern
        for key, value in template_vars.items():
            title = title.replace(f"{{{key}}}", value)

        # Clean up any remaining unmatched templates
        title = re.sub(r"\{[^}]+\}", noun.capitalize(), title)

        # Fix verb+ing conjugation: drop silent-e before -ing (e.g., Restoreing → Restoring)
        title = re.sub(r'(\w)eing\b', r'\1ing', title)
        # Fix CVC doubling for short verbs (e.g., Reseting → Resetting, Seting → Setting)
        ing_fixes = {"Reseting": "Resetting", "Seting": "Setting", "Geting": "Getting",
                     "Runing": "Running", "Stoping": "Stopping", "Droping": "Dropping",
                     "Planing": "Planning", "Siting": "Sitting", "Hiting": "Hitting",
                     "Cuting": "Cutting", "Puting": "Putting", "Shuting": "Shutting",
                     "Spining": "Spinning", "Begining": "Beginning", "Fliping": "Flipping"}
        for bad, good in ing_fixes.items():
            if bad in title:
                title = title.replace(bad, good)
            if bad.lower() in title:
                title = title.replace(bad.lower(), good.lower())

        # Capitalize after colon (e.g., "After Bedtime: the Collapse" → "After Bedtime: The Collapse")
        title = re.sub(r':\s+([a-z])', lambda m: ': ' + m.group(1).upper(), title)

        # Title-case: capitalize important words (skip articles/prepositions unless first word or after colon)
        skip_words = {"the", "a", "an", "in", "of", "at", "to", "for", "and", "but", "or", "not", "with", "its", "my", "from", "by", "on"}
        words_raw = title.split()
        cased = []
        after_colon = False
        for idx_w, w in enumerate(words_raw):
            if idx_w == 0 or after_colon or w.lower() not in skip_words:
                cased.append(w.capitalize() if w[0:1].islower() else w)
            else:
                cased.append(w.lower())
            after_colon = w.endswith(":")
        title = " ".join(cased)

        # Capitalize after comma in titles (e.g., "Feature, not a Bug" → "Feature, Not a Bug")
        title = re.sub(r',\s+([a-z])', lambda m: ', ' + m.group(1).upper(), title)

        # Fix double words and common issues
        title = re.sub(r"\b(\w+)\s+\1\b", r"\1", title)  # Remove duplicate words
        title = " ".join(title.split())  # Normalize whitespace

        # Ensure title is 2-8 words and under 70 chars
        words = title.split()
        if len(words) < 2:
            title = f"The {noun.capitalize()}"
        elif len(words) > 8:
            title = " ".join(words[:8])

        if len(title) > 70:
            title = title[:67].rsplit(" ", 1)[0]  # Break at word boundary

        # Generate subtitle with seeded random
        subtitle_hook = rng.choice(persona["subtitle_hooks"])

        keyword = topic_vocab["search_keywords"][0]
        subtitle = f"{subtitle_hook} • {keyword}"

        if len(subtitle) > 90:
            subtitle = subtitle[:87].rsplit(" ", 1)[0] + "..."

        return title.strip(), subtitle.strip()

    def validate_title(self, title: str, subtitle: str, brand_id: str, topic_id: str) -> bool:
        """Validate title against all rules."""
        errors = []

        # Check length
        if len(title) < 4 or len(title) > 70:
            errors.append(f"Title length invalid: '{title}' ({len(title)} chars)")

        if len(subtitle) > 90:
            errors.append(f"Subtitle too long: {len(subtitle)} chars")

        # Check for forbidden global tokens
        forbidden_global = ["guaranteed", "instant", "cure"]
        for token in forbidden_global:
            if token.lower() in title.lower():
                errors.append(f"Forbidden global token '{token}' in title")

        # Check topic-specific forbidden tokens
        topic_forbidden = TOPIC_VOCABULARY[topic_id].get("forbidden_tokens", [])
        for token in topic_forbidden:
            if token.lower() in title.lower():
                errors.append(f"Forbidden topic token '{token}' for {topic_id}")

        # Check for raw slugs (no_underscore style in titles)
        if "_" in title and not ":" in title:
            errors.append(f"Raw slug detected: '{title}'")

        # Check for grammar issues
        if title.startswith("How to How to"):
            errors.append("Broken grammar: double 'How to'")

        # Check for tautologies
        if title.count("confident") > 1 and "confidence" in title:
            errors.append("Tautology detected")

        # Topic-specific restrictions
        if topic_id in ["grief", "somatic_healing"]:
            forbidden_grief = ["confident", "crush", "optimize", "disrupt"]
            for token in forbidden_grief:
                if token in title.lower():
                    errors.append(f"Grief topic cannot use '{token}'")

        if topic_id == "depression":
            forbidden_depression = ["sprint", "hack", "crush", "optimize", "disrupt"]
            for token in forbidden_depression:
                if token in title.lower():
                    errors.append(f"Depression topic cannot use '{token}'")

        if errors:
            self.validation_errors.append({
                "title": title,
                "subtitle": subtitle,
                "errors": errors
            })
            return False

        return True

    def generate_catalog(self, max_books: int = 1008, market: str = "us",
                        city: str = "", validate: bool = True) -> List[Dict]:
        """
        Generate complete catalog of unique titles using deterministic combo shuffling.
        """
        catalog = []
        brands = list(BRAND_REGISTRY.keys())
        topics = list(TOPIC_VOCABULARY.keys())
        personas = list(PERSONA_LIBRARY.keys())

        # Pre-compute all possible brand-topic-persona combinations (3600 total)
        all_combos = []
        for b in brands:
            for t in topics:
                for p in personas:
                    all_combos.append((b, t, p))

        # Shuffle deterministically then take first max_books
        rng = random.Random("phoenix_catalog_v3_seed")
        rng.shuffle(all_combos)

        # Process combos with variation cycling for second+ passes
        book_counter = 0
        variation = 0
        combo_idx = 0
        max_attempts = max_books * 10  # safety valve
        attempts = 0

        while book_counter < max_books and attempts < max_attempts:
            brand_id, topic_id, persona_id = all_combos[combo_idx % len(all_combos)]

            # Track when we've cycled through all combos
            if combo_idx > 0 and combo_idx % len(all_combos) == 0:
                variation += 1

            # Determine series/angle (~33% of books)
            series_id = ""
            angle_id = ""
            series_candidates = SERIES_TOPIC_MAP.get(topic_id, [])
            if series_candidates and (combo_idx % 3 == 0):
                series_idx = combo_idx % len(series_candidates)
                series_id = series_candidates[series_idx]
                angles = SERIES_REGISTRY[series_id]["angles"]
                angle_id = angles[combo_idx % len(angles)]

            # Generate title
            title, subtitle = self.generate_title(brand_id, topic_id, persona_id, series_id, angle_id, variation)
            combo_idx += 1
            attempts += 1

            # Basic validation
            if validate:
                if not (4 <= len(title) <= 70):
                    continue
                if len(subtitle) > 90:
                    continue
                if any(t in title.lower() for t in ["guaranteed", "instant", "cure"]):
                    continue

            # Check uniqueness
            title_hash = hashlib.md5(title.encode()).hexdigest()
            if title_hash in self.generated_titles:
                # Try with incremented variation instead of skipping
                variation += 1
                title2, subtitle2 = self.generate_title(brand_id, topic_id, persona_id, series_id, angle_id, variation)
                title_hash2 = hashlib.md5(title2.encode()).hexdigest()
                if title_hash2 not in self.generated_titles:
                    title, subtitle, title_hash = title2, subtitle2, title_hash2
                else:
                    continue

            self.generated_titles.add(title_hash)

            # Get search keyword
            search_keyword = TOPIC_VOCABULARY[topic_id]["search_keywords"][0]

            # Get invisible script
            invisible_script = self.generate_invisible_script(brand_id, topic_id, persona_id)

            # Get locale name
            locale_name = ""
            if city:
                locale_name = city.upper()

            # Build book record
            book = {
                "book_id": f"bk_{brand_id}_{topic_id}_{persona_id}_{book_counter:04d}",
                "brand_id": brand_id,
                "topic_id": topic_id,
                "persona_id": persona_id,
                "series_id": series_id,
                "angle_id": angle_id,
                "title": title,
                "subtitle": subtitle,
                "search_keyword": search_keyword,
                "invisible_script": invisible_script,
                "market": market,
                "locale_name": locale_name,
                "city": city if city else "",
            }

            catalog.append(book)
            self.title_details[title_hash] = book
            book_counter += 1

        return catalog

    def validate_catalog(self, catalog: List[Dict]) -> Dict:
        """Validate entire catalog for quality."""
        stats = {
            "total_books": len(catalog),
            "unique_titles": len(set(b["title"] for b in catalog)),
            "unique_by_brand": defaultdict(int),
            "topics_per_brand": defaultdict(set),
            "personas_per_brand": defaultdict(set),
            "validation_errors": len(self.validation_errors),
            "error_details": self.validation_errors[:10],  # First 10 errors
        }

        for book in catalog:
            brand = book["brand_id"]
            stats["unique_by_brand"][brand] += 1
            stats["topics_per_brand"][brand].add(book["topic_id"])
            stats["personas_per_brand"][brand].add(book["persona_id"])

        # Convert sets to counts
        stats["topics_per_brand"] = {k: len(v) for k, v in stats["topics_per_brand"].items()}
        stats["personas_per_brand"] = {k: len(v) for k, v in stats["personas_per_brand"].items()}

        return stats


# ============================================================================
# CLI
# ============================================================================

def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Phoenix Title Generation Engine v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 phoenix_title_engine_v3.py --max-books 1008 --market us --validate --out catalog.json
  python3 phoenix_title_engine_v3.py --brand stoic_edge --topic anxiety --persona first_responders
  python3 phoenix_title_engine_v3.py --max-books 1008 --market us --city nyc --validate --out nyc_catalog.json
        """
    )

    parser.add_argument("--max-books", type=int, default=1008, help="Max books to generate (default: 1008)")
    parser.add_argument("--market", default="us", help="Market/region (default: us)")
    parser.add_argument("--brand", help="Specific brand to generate for")
    parser.add_argument("--topic", help="Specific topic to generate for")
    parser.add_argument("--persona", help="Specific persona to generate for")
    parser.add_argument("--city", help="US city for localized generation (nyc, la, sf, chicago, boston, dc)")
    parser.add_argument("--validate", action="store_true", help="Validate all titles")
    parser.add_argument("--sample", type=int, default=0, help="Show N random samples (0=none)")
    parser.add_argument("--out", help="Output JSON file")
    parser.add_argument("--stats", action="store_true", help="Show validation stats")

    args = parser.parse_args()

    # Initialize generator
    gen = TitleGenerator()

    # Generate catalog
    if args.brand or args.topic or args.persona:
        # Single book generation
        brand_id = args.brand or "stabilizer"
        topic_id = args.topic or "anxiety"
        persona_id = args.persona or "millennial_women_professionals"

        title, subtitle = gen.generate_title(brand_id, topic_id, persona_id)

        print(f"\n📖 Generated Title")
        print(f"{'=' * 70}")
        print(f"Brand: {brand_id}")
        print(f"Topic: {topic_id}")
        print(f"Persona: {persona_id}")
        print(f"\nTitle: {title}")
        print(f"Subtitle: {subtitle}")
        print()
    else:
        # Full catalog generation
        print(f"Generating {args.max_books} titles...")
        catalog = gen.generate_catalog(
            max_books=args.max_books,
            market=args.market,
            city=args.city,
            validate=args.validate
        )

        print(f"Generated {len(catalog)} titles")

        # Validation stats
        if args.validate or args.stats:
            stats = gen.validate_catalog(catalog)
            print(f"\n✓ Validation Results")
            print(f"{'=' * 70}")
            print(f"Total books: {stats['total_books']}")
            print(f"Unique titles: {stats['unique_titles']}")
            print(f"Uniqueness: {100 * stats['unique_titles'] / stats['total_books']:.1f}%")
            print(f"Validation errors: {stats['validation_errors']}")

            if stats['validation_errors'] > 0 and stats['error_details']:
                print(f"\nFirst errors:")
                for error in stats['error_details'][:3]:
                    print(f"  - {error['title']}: {', '.join(error['errors'][:2])}")

            print(f"\nBooks per brand: {min(stats['unique_by_brand'].values())}-{max(stats['unique_by_brand'].values())}")
            print(f"Topics covered per brand: {stats['topics_per_brand'].get(list(stats['topics_per_brand'].keys())[0], 0)}")

        # Sample output
        if args.sample > 0:
            import random
            samples = random.sample(catalog, min(args.sample, len(catalog)))
            print(f"\n🎯 Sample Titles (showing {len(samples)})")
            print(f"{'=' * 70}")
            for i, book in enumerate(samples, 1):
                print(f"\n{i}. {book['title']}")
                print(f"   {book['subtitle']}")
                print(f"   Brand: {book['brand_id']} | Topic: {book['topic_id']} | Persona: {book['persona_id']}")
                if book['series_id']:
                    print(f"   Series: {book['series_id']} > {book['angle_id']}")

        # Write output
        if args.out:
            with open(args.out, 'w') as f:
                json.dump(catalog, f, indent=2)
            print(f"\n✓ Wrote {len(catalog)} titles to {args.out}")


if __name__ == "__main__":
    main()
