#!/usr/bin/env python3
"""
Phoenix Title Engine v2.0
========================
Generates unique, brand-voiced, persona-specific, topic-appropriate,
locale-aware audiobook titles for the Phoenix catalog.

Architecture:
  Title  = owns a search keyword + names an invisible script
  Subtitle = signals the persona + delivers a benefit promise
  Both carry brand voice through vocabulary, not labels.

Dimensions:
  - 24 brands (each with distinct voice vocabulary)
  - 9 topics (each with topic-specific templates, never universal)
  - 10 personas (each with hook language matching their lived experience)
  - 5 markets (US, China, Taiwan, Hong Kong, Singapore) with locale names
  - Geographic locale appears in title when market != US-universal

Usage:
  python3 phoenix_title_engine.py --max-books 1008 --market us --out catalog.json
  python3 phoenix_title_engine.py --max-books 1008 --market all --out catalog.json
  python3 phoenix_title_engine.py --brand stoic_edge --topic anxiety --persona first_responders --market us
"""

from __future__ import annotations
import argparse
import hashlib
import json
import random
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# =============================================================================
# SECTION 1: BRAND VOICE BANKS
# Each brand has: tone words, power verbs, texture adjectives, and title patterns
# The brand should be AUDIBLE in the title even without the brand name.
# =============================================================================

BRAND_VOICES = {
    "stabilizer": {
        "tone": "grounding, steady, anchoring",
        "power_verbs": ["anchor", "steady", "ground", "settle", "hold", "root", "land"],
        "adjectives": ["solid", "quiet", "steady", "grounded", "still", "centered"],
        "title_frames": [
            "{adjective} Ground: {hook}",
            "The {adjective} Place: {hook}",
            "{verb} Here: {hook}",
            "Still Standing: {hook}",
            "Finding {adjective} Ground {locale_phrase}",
        ],
        "subtitle_frames": [
            "A grounding guide to {outcome} when {situation}",
            "How to find steady footing when {situation}",
            "{outcome} without losing your center",
        ],
    },
    "adhd_forge": {
        "tone": "energetic, direct, builder-mentality",
        "power_verbs": ["forge", "build", "wire", "hack", "sprint", "channel", "redirect"],
        "adjectives": ["wired", "electric", "raw", "unfiltered", "fast", "sharp"],
        "title_frames": [
            "The {adjective} Brain: {hook}",
            "{verb} Your Focus: {hook}",
            "Wired for This: {hook}",
            "The {topic_word} Hack: {hook}",
            "{adjective} and {outcome_word} {locale_phrase}",
        ],
        "subtitle_frames": [
            "A fast-brain guide to {outcome} when {situation}",
            "How to channel the chaos into {outcome}",
            "{outcome} for the mind that won't sit still",
        ],
    },
    "executive_calm": {
        "tone": "composed, strategic, boardroom-quiet",
        "power_verbs": ["command", "navigate", "lead", "decide", "compose", "steer", "govern"],
        "adjectives": ["composed", "strategic", "measured", "precise", "clear-eyed", "poised"],
        "title_frames": [
            "The {adjective} Leader: {hook}",
            "{verb} the Room: {hook}",
            "Quiet Authority: {hook}",
            "Above the Noise: {hook}",
            "The {adjective} Executive {locale_phrase}",
        ],
        "subtitle_frames": [
            "A leadership guide to {outcome} under {situation}",
            "How to lead through {situation} without losing composure",
            "Strategic {outcome} for leaders who carry too much",
        ],
    },
    "trauma_path": {
        "tone": "gentle, honest, unflinching but safe",
        "power_verbs": ["name", "witness", "release", "unlearn", "reclaim", "untangle", "surface"],
        "adjectives": ["honest", "unflinching", "tender", "brave", "bare", "real"],
        "title_frames": [
            "What You Carry: {hook}",
            "The {adjective} Truth: {hook}",
            "{verb} What Was Never Yours: {hook}",
            "Before You Were This: {hook}",
            "What {locale_name} Taught You to Hide",
        ],
        "subtitle_frames": [
            "An honest guide to {outcome} after {situation}",
            "How to {verb} what was never yours to carry",
            "Healing {situation} without pretending it didn't happen",
        ],
    },
    "stoic_edge": {
        "tone": "disciplined, philosophical, iron-quiet",
        "power_verbs": ["endure", "forge", "temper", "sharpen", "discipline", "master", "withstand"],
        "adjectives": ["quiet", "iron", "forged", "tempered", "unflinching", "still", "resolute"],
        "title_frames": [
            "The {adjective} Path: {hook}",
            "{verb} in Silence: {hook}",
            "Iron Quiet: {hook}",
            "The Discipline of {outcome_word}: {hook}",
            "{adjective} Resolve {locale_phrase}",
        ],
        "subtitle_frames": [
            "A stoic guide to {outcome} through {situation}",
            "How to {verb} without breaking",
            "Mastering {situation} through disciplined {outcome}",
        ],
    },
    "gentle_growth": {
        "tone": "nurturing, soft, patient unfolding",
        "power_verbs": ["bloom", "unfold", "soften", "tend", "nurture", "grow", "open"],
        "adjectives": ["soft", "tender", "patient", "warm", "slow", "kind", "gentle"],
        "title_frames": [
            "The {adjective} Unfolding: {hook}",
            "{verb} at Your Own Pace: {hook}",
            "Permission to Be {adjective}: {hook}",
            "Small and {adjective}: {hook}",
            "{adjective} Growth {locale_phrase}",
        ],
        "subtitle_frames": [
            "A gentle guide to {outcome} when {situation}",
            "How to {verb} without forcing it",
            "Finding {outcome} at your own pace",
        ],
    },
    "night_reset": {
        "tone": "quiet, decompressing, end-of-day release",
        "power_verbs": ["release", "shed", "dissolve", "let go", "rest", "unwind", "settle"],
        "adjectives": ["quiet", "dark", "still", "soft", "heavy", "restful", "dim"],
        "title_frames": [
            "What You Carry Home: {hook}",
            "The {adjective} Hour: {hook}",
            "{verb} Before You Sleep: {hook}",
            "After the Day: {hook}",
            "The Night You Deserve {locale_phrase}",
        ],
        "subtitle_frames": [
            "Releasing {situation} before you sleep",
            "How to {verb} the day and find {outcome}",
            "A bedtime guide to {outcome} after {situation}",
        ],
    },
    "career_lift": {
        "tone": "ambitious, pragmatic, upward-moving",
        "power_verbs": ["climb", "leverage", "position", "negotiate", "advance", "pivot", "claim"],
        "adjectives": ["strategic", "bold", "sharp", "clear", "ambitious", "decisive"],
        "title_frames": [
            "The {adjective} Move: {hook}",
            "{verb} Your Position: {hook}",
            "Next Level: {hook}",
            "The Career {topic_word}: {hook}",
            "Your {adjective} Advantage {locale_phrase}",
        ],
        "subtitle_frames": [
            "A career guide to {outcome} when {situation}",
            "How to {verb} past {situation} and get ahead",
            "{outcome} for professionals who refuse to stay stuck",
        ],
    },
    "resilient_parent": {
        "tone": "empathetic, fierce, protective but honest",
        "power_verbs": ["protect", "model", "hold", "repair", "show up", "sustain", "endure"],
        "adjectives": ["fierce", "tender", "honest", "imperfect", "present", "real"],
        "title_frames": [
            "The {adjective} Parent: {hook}",
            "Still Here, Still Parenting: {hook}",
            "{verb} for Them Without Losing You: {hook}",
            "What Your Kids See: {hook}",
            "Parenting Through {topic_word} {locale_phrase}",
        ],
        "subtitle_frames": [
            "A parent's guide to {outcome} while raising {situation}",
            "How to {verb} for your kids without abandoning yourself",
            "{outcome} for the parent who's running on empty",
        ],
    },
    "optimizer": {
        "tone": "data-driven, efficient, systems-thinking",
        "power_verbs": ["optimize", "calibrate", "streamline", "measure", "iterate", "debug", "tune"],
        "adjectives": ["precise", "efficient", "systematic", "calibrated", "lean", "clear"],
        "title_frames": [
            "The {topic_word} Algorithm: {hook}",
            "{verb} Your {outcome_word}: {hook}",
            "Systems for {outcome_word}: {hook}",
            "The {adjective} Fix: {hook}",
            "{adjective} Systems {locale_phrase}",
        ],
        "subtitle_frames": [
            "A systems approach to {outcome} when {situation}",
            "How to {verb} your way out of {situation}",
            "Data-driven {outcome} for analytical minds",
        ],
    },
    "creative_unfold": {
        "tone": "artistic, exploratory, meaning-making",
        "power_verbs": ["create", "explore", "express", "reimagine", "compose", "draw out", "render"],
        "adjectives": ["raw", "vivid", "expressive", "open", "layered", "luminous"],
        "title_frames": [
            "The {adjective} Canvas: {hook}",
            "{verb} Your Way Through: {hook}",
            "Art of {outcome_word}: {hook}",
            "What {topic_word} Creates: {hook}",
            "The {adjective} Path {locale_phrase}",
        ],
        "subtitle_frames": [
            "A creative guide to {outcome} through {situation}",
            "How to {verb} meaning from {situation}",
            "Turning {situation} into {outcome}",
        ],
    },
    "spiritual_ground": {
        "tone": "contemplative, sacred, rooted in practice",
        "power_verbs": ["surrender", "practice", "return", "breathe", "center", "invoke", "sit with"],
        "adjectives": ["sacred", "still", "deep", "rooted", "ancient", "quiet", "whole"],
        "title_frames": [
            "The {adjective} Practice: {hook}",
            "{verb} to Yourself: {hook}",
            "Sacred {outcome_word}: {hook}",
            "The {adjective} Return: {hook}",
            "A {adjective} Path {locale_phrase}",
        ],
        "subtitle_frames": [
            "A contemplative guide to {outcome} through {situation}",
            "How to {verb} your way back to {outcome}",
            "Finding the {adjective} in {situation}",
        ],
    },
    "focus_sprint": {
        "tone": "high-tempo, action-first, momentum",
        "power_verbs": ["sprint", "lock in", "execute", "crush", "attack", "launch", "drive"],
        "adjectives": ["fast", "sharp", "locked", "intense", "focused", "relentless"],
        "title_frames": [
            "Lock In: {hook}",
            "The {adjective} Sprint: {hook}",
            "{verb} First, Feel Later: {hook}",
            "90 Days of {outcome_word}: {hook}",
            "{adjective} Focus {locale_phrase}",
        ],
        "subtitle_frames": [
            "A high-tempo guide to {outcome} through {situation}",
            "How to {verb} past {situation} in record time",
            "{outcome} for people who'd rather act than wait",
        ],
    },
    "hormone_reset": {
        "tone": "body-aware, clinical-warm, biological honesty",
        "power_verbs": ["reset", "regulate", "balance", "restore", "sync", "recalibrate", "heal"],
        "adjectives": ["biological", "hormonal", "cyclical", "embodied", "chemical", "whole-body"],
        "title_frames": [
            "The {adjective} Truth: {hook}",
            "{verb} Your System: {hook}",
            "It's Not Just In Your Head: {hook}",
            "The Body Keeps the {topic_word}: {hook}",
            "Your {adjective} Reset {locale_phrase}",
        ],
        "subtitle_frames": [
            "A body-first guide to {outcome} when {situation}",
            "How to {verb} what your nervous system is telling you",
            "{outcome} by working with your biology, not against it",
        ],
    },
    "longevity_lab": {
        "tone": "scientific, long-view, compounding gains",
        "power_verbs": ["compound", "sustain", "build", "invest", "stack", "protect", "extend"],
        "adjectives": ["sustained", "long-game", "compounding", "durable", "evidence-based", "lasting"],
        "title_frames": [
            "The Long Game: {hook}",
            "{verb} for the Years Ahead: {hook}",
            "{adjective} {outcome_word}: {hook}",
            "The {topic_word} Investment: {hook}",
            "Playing Long {locale_phrase}",
        ],
        "subtitle_frames": [
            "A long-view guide to {outcome} beyond {situation}",
            "How to {verb} resilience that compounds over time",
            "{outcome} that lasts, not just {outcome} that starts",
        ],
    },
    "calm_student": {
        "tone": "relatable, age-appropriate, pressure-aware",
        "power_verbs": ["breathe", "pause", "choose", "unplug", "step back", "ask for", "name"],
        "adjectives": ["real", "okay", "young", "honest", "messy", "growing"],
        "title_frames": [
            "It's Okay to Not Be Okay: {hook}",
            "The {adjective} Guide: {hook}",
            "{verb} Through It: {hook}",
            "You're Not Behind: {hook}",
            "Being {adjective} {locale_phrase}",
        ],
        "subtitle_frames": [
            "A real guide to {outcome} when {situation}",
            "How to {verb} when everything feels like too much",
            "{outcome} for young people who are tired of pretending",
        ],
    },
    "morning_momentum": {
        "tone": "energizing, ritual-based, first-hour power",
        "power_verbs": ["launch", "ignite", "start", "set", "prime", "charge", "activate"],
        "adjectives": ["first-light", "morning", "fresh", "early", "charged", "ready"],
        "title_frames": [
            "Before the World Wakes Up: {hook}",
            "The {adjective} Hour: {hook}",
            "{verb} Your Morning: {hook}",
            "First Light: {hook}",
            "Your {adjective} Start {locale_phrase}",
        ],
        "subtitle_frames": [
            "A morning ritual for {outcome} before {situation} starts",
            "How to {verb} your day before {situation} takes over",
            "{outcome} starts in the first hour",
        ],
    },
    "high_performer": {
        "tone": "elite, under-pressure, peak-state",
        "power_verbs": ["perform", "execute", "sustain", "peak", "deliver", "dominate", "recover"],
        "adjectives": ["elite", "peak", "high-stakes", "pressure-tested", "world-class", "top-tier"],
        "title_frames": [
            "Under Pressure: {hook}",
            "The {adjective} Standard: {hook}",
            "{verb} at the Top: {hook}",
            "Peak State: {hook}",
            "{adjective} Performance {locale_phrase}",
        ],
        "subtitle_frames": [
            "An elite guide to {outcome} under {situation}",
            "How to {verb} at the highest level while {situation}",
            "{outcome} for performers who can't afford to crack",
        ],
    },
    "relationship_clarity": {
        "tone": "honest, boundary-aware, relational intelligence",
        "power_verbs": ["clarify", "speak", "set", "repair", "leave", "choose", "see"],
        "adjectives": ["clear", "honest", "direct", "brave", "true", "seen"],
        "title_frames": [
            "The {adjective} Conversation: {hook}",
            "{verb} What You Need: {hook}",
            "Between Us: {hook}",
            "What You're Not Saying: {hook}",
            "{adjective} Connections {locale_phrase}",
        ],
        "subtitle_frames": [
            "A guide to {outcome} in relationships shaped by {situation}",
            "How to {verb} the truth without burning it down",
            "{outcome} for people who learned love wrong the first time",
        ],
    },
    "confidence_core": {
        "tone": "identity-rebuilding, inner-authority, self-trust",
        "power_verbs": ["reclaim", "trust", "own", "stand", "believe", "declare", "occupy"],
        "adjectives": ["unshakeable", "core", "earned", "real", "rooted", "inner"],
        "title_frames": [
            "The {adjective} You: {hook}",
            "{verb} Your Own Voice: {hook}",
            "Enough: {hook}",
            "The Authority You Already Have: {hook}",
            "{adjective} Confidence {locale_phrase}",
        ],
        "subtitle_frames": [
            "Rebuilding {outcome} after {situation}",
            "How to {verb} self-trust when {situation}",
            "{outcome} that comes from the inside out",
        ],
    },
    "bio_flow": {
        "tone": "somatic, flow-state, body-mind integration",
        "power_verbs": ["flow", "sync", "breathe", "regulate", "embody", "move", "integrate"],
        "adjectives": ["fluid", "somatic", "embodied", "flowing", "integrated", "alive"],
        "title_frames": [
            "In the Body: {hook}",
            "The {adjective} State: {hook}",
            "{verb} Into Flow: {hook}",
            "Your Nervous System Knows: {hook}",
            "{adjective} Flow {locale_phrase}",
        ],
        "subtitle_frames": [
            "A body-based guide to {outcome} through {situation}",
            "How to {verb} your way back into flow",
            "{outcome} by listening to what your body already knows",
        ],
    },
    "healing_ground": {
        "tone": "recovery-focused, soil metaphor, slow rebuilding",
        "power_verbs": ["rebuild", "restore", "plant", "recover", "mend", "tend", "renew"],
        "adjectives": ["slow", "deep", "fertile", "broken-open", "rebuilding", "new"],
        "title_frames": [
            "From the Ground Up: {hook}",
            "The {adjective} Rebuild: {hook}",
            "{verb} What Was Broken: {hook}",
            "Good Soil: {hook}",
            "Rebuilding {locale_phrase}",
        ],
        "subtitle_frames": [
            "A recovery guide to {outcome} after {situation}",
            "How to {verb} something new from what was broken",
            "{outcome} for people starting over",
        ],
    },
    "minimal_mind": {
        "tone": "stripped-back, clarity through subtraction",
        "power_verbs": ["strip", "clear", "simplify", "subtract", "drop", "release", "edit"],
        "adjectives": ["minimal", "clear", "clean", "bare", "simple", "light", "essential"],
        "title_frames": [
            "Less: {hook}",
            "The {adjective} Mind: {hook}",
            "{verb} the Noise: {hook}",
            "What's Left When You Stop: {hook}",
            "{adjective} Living {locale_phrase}",
        ],
        "subtitle_frames": [
            "A minimalist guide to {outcome} by releasing {situation}",
            "How to {verb} everything that isn't helping",
            "{outcome} through subtraction, not addition",
        ],
    },
    "legacy_builder": {
        "tone": "generational, purposeful, long-arc meaning",
        "power_verbs": ["build", "pass on", "model", "establish", "shape", "leave", "invest"],
        "adjectives": ["generational", "lasting", "purposeful", "meaningful", "enduring", "wise"],
        "title_frames": [
            "What You Leave Behind: {hook}",
            "The {adjective} Legacy: {hook}",
            "{verb} for the Next Generation: {hook}",
            "Beyond You: {hook}",
            "Your {adjective} Legacy {locale_phrase}",
        ],
        "subtitle_frames": [
            "A legacy guide to {outcome} that outlasts {situation}",
            "How to {verb} meaning that your children will inherit",
            "{outcome} that echoes beyond your own lifetime",
        ],
    },
}


# =============================================================================
# SECTION 2: TOPIC VOCABULARY
# Each topic gets its own emotional vocabulary, search keywords, and
# situation descriptions. NO universal templates.
# =============================================================================

TOPIC_VOCAB = {
    "anxiety": {
        "search_keywords": ["anxiety", "anxious", "worry", "panic", "nervous system", "overthinking"],
        "invisible_scripts": [
            "the fear that won't name itself",
            "the alarm that never turns off",
            "the quiet panic underneath everything",
            "the loop your mind won't stop running",
            "the thing you can't stop bracing for",
        ],
        "situations": ["the worry won't stop", "your nervous system runs the show",
                       "calm feels dangerous", "you can't stop scanning for threats",
                       "everything feels like an emergency"],
        "outcomes": ["calm", "safety", "stillness", "peace", "steady ground", "quiet"],
        "outcome_words": ["Calm", "Peace", "Stillness", "Safety", "Quiet"],
        "topic_words": ["Anxiety", "Worry", "Panic", "Fear"],
        "forbidden_frames": [],  # anxiety can use most frames
    },
    "boundaries": {
        "search_keywords": ["boundaries", "people pleasing", "saying no", "codependency", "limits"],
        "invisible_scripts": [
            "the no you've never been allowed to say",
            "the version of you that exists only to make others comfortable",
            "the guilt that arrives every time you choose yourself",
            "the belief that your needs are an inconvenience",
            "the pattern of disappearing to keep the peace",
        ],
        "situations": ["saying no feels impossible", "you keep disappearing to keep the peace",
                       "everyone else's needs come first", "your yes has become a cage",
                       "guilt follows every boundary"],
        "outcomes": ["freedom", "self-respect", "clarity", "protected space", "your own voice"],
        "outcome_words": ["Freedom", "Space", "Clarity", "Protection", "Voice"],
        "topic_words": ["Boundaries", "Limits", "The No", "Permission"],
        "forbidden_frames": [],
    },
    "grief": {
        "search_keywords": ["grief", "loss", "bereavement", "mourning", "after loss", "death"],
        "invisible_scripts": [
            "the weight that has no deadline",
            "the absence that reorganized your entire life",
            "the grief nobody asks about anymore",
            "the loss you're still explaining to your body",
            "the before and after that split your life in two",
        ],
        "situations": ["the loss is still fresh", "grief arrives without warning",
                       "nobody asks how you're doing anymore", "you're expected to be over it",
                       "the absence reshapes every day"],
        "outcomes": ["presence", "meaning", "carrying it differently", "continuing", "honoring what was"],
        "outcome_words": ["Presence", "Meaning", "Honoring", "Continuing", "Still Here"],
        "topic_words": ["Grief", "Loss", "Absence", "What Remains"],
        "forbidden_frames": ["confident", "crush", "dominate", "hack", "optimize"],  # grief-inappropriate
    },
    "shame": {
        "search_keywords": ["shame", "not enough", "imposter", "self-worth", "unworthiness", "hiding"],
        "invisible_scripts": [
            "the thing about yourself you've never said out loud",
            "the part you've been hiding since before you can remember",
            "the belief that if they really knew you, they'd leave",
            "the performance of okayness that exhausts you",
            "the secret conviction that you're fundamentally broken",
        ],
        "situations": ["the mask is getting heavier", "you've been performing for so long you forgot what's real",
                       "exposure feels like annihilation", "you hide the parts that need the most light",
                       "the secret costs more than the truth would"],
        "outcomes": ["self-acceptance", "being seen", "wholeness", "truth", "coming out of hiding"],
        "outcome_words": ["Truth", "Wholeness", "Acceptance", "Being Seen", "Freedom"],
        "topic_words": ["Shame", "Hiding", "The Mask", "Enough"],
        "forbidden_frames": ["confident", "crush", "dominate", "peak"],
    },
    "depression": {
        "search_keywords": ["depression", "low mood", "numbness", "emptiness", "can't get up", "flatness"],
        "invisible_scripts": [
            "the weight that makes everything harder than it should be",
            "the numbness that pretends to be peace",
            "the fog that steals your future before you get there",
            "the flatness that scares you more than sadness would",
            "the energy debt you can never seem to repay",
        ],
        "situations": ["getting up takes everything you have", "nothing sounds good anymore",
                       "the flatness won't lift", "you're going through the motions",
                       "you're tired in a way sleep doesn't fix"],
        "outcomes": ["movement", "feeling again", "small sparks", "showing up", "something shifts"],
        "outcome_words": ["Movement", "Light", "Feeling", "Showing Up", "A Shift"],
        "topic_words": ["Depression", "The Fog", "Flatness", "The Weight"],
        "forbidden_frames": ["crush", "dominate", "sprint", "hack", "optimize"],
    },
    "self_worth": {
        "search_keywords": ["self-worth", "confidence", "imposter syndrome", "not enough", "self-esteem"],
        "invisible_scripts": [
            "the voice that says you haven't earned your place",
            "the success that never feels like enough",
            "the compliment you always deflect",
            "the achievement that someone else would have done better",
            "the inner critic that sounds like someone you trusted",
        ],
        "situations": ["success feels fraudulent", "you deflect every compliment",
                       "the inner critic runs the show", "you over-prepare to compensate for who you are",
                       "your worth is tied to your output"],
        "outcomes": ["self-trust", "enoughness", "inner authority", "self-belief", "owning your place"],
        "outcome_words": ["Enough", "Worth", "Self-Trust", "Authority", "Belonging"],
        "topic_words": ["Worth", "Imposter", "Enough", "The Inner Critic"],
        "forbidden_frames": [],
    },
    "courage": {
        "search_keywords": ["courage", "fear", "brave", "taking risks", "stepping up", "speaking up"],
        "invisible_scripts": [
            "the thing you keep almost doing",
            "the conversation you've rehearsed a hundred times",
            "the risk that keeps you up at night",
            "the version of you that's waiting on the other side of fear",
            "the safety that's become a smaller prison each year",
        ],
        "situations": ["the leap feels impossible", "safety has become a cage",
                       "you know what to do but can't start", "fear makes every decision for you",
                       "you keep rehearsing and never performing"],
        "outcomes": ["action", "the leap", "freedom on the other side", "showing up scared", "movement"],
        "outcome_words": ["The Leap", "Action", "Movement", "Voice", "Freedom"],
        "topic_words": ["Courage", "Fear", "The Edge", "The Leap"],
        "forbidden_frames": [],
    },
    "compassion_fatigue": {
        "search_keywords": ["compassion fatigue", "burnout", "caregiver burnout", "emotional exhaustion", "helper fatigue"],
        "invisible_scripts": [
            "the emptiness that comes from giving everything away",
            "the guilt of having nothing left for the people you serve",
            "the resentment you're not allowed to feel",
            "the helper who forgot they need help too",
            "the exhaustion that empathy left behind",
        ],
        "situations": ["you've given until there's nothing left", "caring for others has emptied you",
                       "you feel guilty for being tired", "empathy has become a weight",
                       "you can't feel what you used to feel for the people you serve"],
        "outcomes": ["replenishment", "sustainable caring", "self-preservation", "feeling again", "refilling the well"],
        "outcome_words": ["Refilling", "Restoration", "Sustainable Care", "Self-Preservation", "Return"],
        "topic_words": ["Fatigue", "Burnout", "The Empty Well", "Compassion"],
        "forbidden_frames": ["crush", "dominate", "sprint"],
    },
    "financial_stress": {
        "search_keywords": ["financial stress", "money anxiety", "debt stress", "financial worry", "money mindset"],
        "invisible_scripts": [
            "the number you're afraid to look at",
            "the shame that lives in your bank account",
            "the scarcity mindset your childhood installed",
            "the belief that money problems mean you're failing at life",
            "the financial panic that hijacks every other decision",
        ],
        "situations": ["money panic drives every decision", "the numbers keep you up at night",
                       "financial shame is running the show", "scarcity thinking controls your life",
                       "you avoid your own bank account"],
        "outcomes": ["financial clarity", "money calm", "clear-eyed decisions", "breaking the scarcity loop", "control"],
        "outcome_words": ["Clarity", "Calm", "Control", "Freedom", "Clear Decisions"],
        "topic_words": ["Money", "Financial Stress", "Scarcity", "The Numbers"],
        "forbidden_frames": [],
    },
}


# =============================================================================
# SECTION 3: PERSONA HOOK LANGUAGE
# Each persona gets identity-specific language that shapes emotional framing.
# =============================================================================

PERSONA_HOOKS = {
    "millennial_women_professionals": {
        "identity_words": ["woman", "professional", "career", "millennial"],
        "lived_context": ["the office", "the meeting", "the performance review", "the group chat", "the Sunday scaries"],
        "emotional_frame": "proving and performing while secretly exhausted",
        "subtitle_hooks": [
            "for women who are tired of holding it all together",
            "for the professional woman who never learned to stop performing",
            "for women who built the career and lost themselves inside it",
        ],
    },
    "tech_finance_burnout": {
        "identity_words": ["tech", "finance", "startup", "Wall Street", "Silicon Valley"],
        "lived_context": ["the sprint", "the standup", "the quarterly review", "the cap table", "the on-call rotation"],
        "emotional_frame": "optimized everything except their own nervous system",
        "subtitle_hooks": [
            "for high-performers who optimized everything except themselves",
            "for tech and finance professionals running on fumes",
            "for the person who built the system but forgot to build a life",
        ],
    },
    "entrepreneurs": {
        "identity_words": ["founder", "entrepreneur", "business owner", "solo", "startup"],
        "lived_context": ["the pitch", "the cash flow", "the 3am idea", "the investor call", "the pivot"],
        "emotional_frame": "building something that's quietly consuming them",
        "subtitle_hooks": [
            "for founders whose business became their identity",
            "for entrepreneurs who forgot they exist outside the company",
            "for the builder who can't stop building long enough to breathe",
        ],
    },
    "working_parents": {
        "identity_words": ["parent", "working parent", "mom", "dad", "caregiver"],
        "lived_context": ["the school pickup", "the bedtime routine", "the work call during dinner",
                          "the guilt of choosing", "the impossible schedule"],
        "emotional_frame": "splitting themselves between two worlds and failing at both",
        "subtitle_hooks": [
            "for parents who feel like they're failing at everything",
            "for the working parent who has nothing left at the end of the day",
            "for parents who are present everywhere and rested nowhere",
        ],
    },
    "gen_x_sandwich": {
        "identity_words": ["Gen X", "sandwich generation", "midlife", "caregiver", "aging parents"],
        "lived_context": ["the parent's doctor appointment", "the teenager's crisis", "the retirement account",
                          "the midlife reckoning", "the 'what happened to my life' moment"],
        "emotional_frame": "carrying two generations while their own needs disappear",
        "subtitle_hooks": [
            "for the generation caught between aging parents and growing kids",
            "for the person who takes care of everyone and no one takes care of them",
            "for midlifers who lost themselves in the middle of everyone else's needs",
        ],
    },
    "gen_z_professionals": {
        "identity_words": ["Gen Z", "young professional", "early career", "first job"],
        "lived_context": ["the open floor plan", "the Slack message", "the comparison scroll",
                          "the 'adulting' moment", "the entry-level grind"],
        "emotional_frame": "performing adulthood while secretly terrified they're doing it wrong",
        "subtitle_hooks": [
            "for young professionals who are tired of pretending they have it figured out",
            "for Gen Z workers who feel behind before they've even started",
            "for the new professional who inherited a broken world and is expected to thrive in it",
        ],
    },
    "healthcare_rns": {
        "identity_words": ["nurse", "RN", "healthcare worker", "caregiver", "clinician"],
        "lived_context": ["the shift", "the patient", "the code", "the break room cry",
                          "the drive home in silence"],
        "emotional_frame": "carrying other people's worst days home in their body",
        "subtitle_hooks": [
            "for healthcare workers who carry the ward home in their body",
            "for nurses who learned to care for everyone except themselves",
            "for the clinician whose compassion became a wound",
        ],
    },
    "first_responders": {
        "identity_words": ["first responder", "firefighter", "EMT", "police", "paramedic"],
        "lived_context": ["the call", "the scene", "the debrief that never happens",
                          "the adrenaline crash", "the thing you can't unsee"],
        "emotional_frame": "trained to run toward danger, never trained to process what they saw",
        "subtitle_hooks": [
            "for first responders who were trained to save everyone but themselves",
            "for the person who runs toward danger and never processes the aftermath",
            "for those who serve the call and carry the cost",
        ],
    },
    "corporate_managers": {
        "identity_words": ["manager", "director", "team lead", "executive", "VP"],
        "lived_context": ["the one-on-one", "the restructure", "the all-hands",
                          "the difficult conversation", "the targets"],
        "emotional_frame": "responsible for everyone's performance while their own is cracking",
        "subtitle_hooks": [
            "for leaders who carry the weight of every person on their team",
            "for managers who absorb everyone's stress and call it leadership",
            "for the leader who's holding it together so their team doesn't have to",
        ],
    },
    "gen_alpha_students": {
        "identity_words": ["student", "teen", "young person", "Gen Alpha"],
        "lived_context": ["the classroom", "the group chat", "the feed", "the exam",
                          "the pressure to have your life figured out at 16"],
        "emotional_frame": "growing up in a world that's already overwhelmed and expects them to be fine",
        "subtitle_hooks": [
            "for young people who are tired of being told it gets better without being shown how",
            "for students who feel the weight of a world they didn't build",
            "for the young person who needs real tools, not motivational posters",
        ],
    },
}


# =============================================================================
# SECTION 4: GEOGRAPHIC LOCALE
# Location name integration for market-specific books.
# =============================================================================

US_CITIES = {
    "nyc": {
        "city_name": "New York",
        "short": "NYC",
        "locale_phrases": ["in New York", "in NYC", "in the City That Never Sleeps"],
        "persona_flavor": {
            "tech_finance_burnout": "on Wall Street",
            "corporate_managers": "in Midtown",
            "millennial_women_professionals": "in New York",
            "entrepreneurs": "in NYC",
        },
    },
    "la": {
        "city_name": "Los Angeles",
        "short": "LA",
        "locale_phrases": ["in Los Angeles", "in LA", "in the City of Angels"],
        "persona_flavor": {
            "entrepreneurs": "in LA",
            "creative_unfold": "in Los Angeles",
            "gen_z_professionals": "in LA",
        },
    },
    "sf": {
        "city_name": "San Francisco",
        "short": "SF",
        "locale_phrases": ["in San Francisco", "in the Bay Area", "in Silicon Valley", "in the Bay"],
        "persona_flavor": {
            "tech_finance_burnout": "in Silicon Valley",
            "entrepreneurs": "in the Bay Area",
            "gen_z_professionals": "in San Francisco",
            "corporate_managers": "in the Bay",
        },
    },
    "chicago": {
        "city_name": "Chicago",
        "short": "Chicago",
        "locale_phrases": ["in Chicago", "in the Windy City"],
        "persona_flavor": {
            "first_responders": "in Chicago",
            "working_parents": "in Chicago",
            "corporate_managers": "in Chicago",
        },
    },
    "boston": {
        "city_name": "Boston",
        "short": "Boston",
        "locale_phrases": ["in Boston"],
        "persona_flavor": {
            "healthcare_rns": "in Boston",
            "gen_alpha_students": "in Boston",
            "tech_finance_burnout": "in Boston",
        },
    },
    "dc": {
        "city_name": "Washington DC",
        "short": "DC",
        "locale_phrases": ["in DC", "in Washington", "inside the Beltway"],
        "persona_flavor": {
            "corporate_managers": "in DC",
            "gen_x_sandwich": "in Washington",
            "millennial_women_professionals": "in DC",
        },
    },
}


MARKET_LOCALES = {
    "us": {
        "locale_name": "",  # US-universal books: no locale in title
        "locale_phrases": ["", ""],  # empty — US-generic books don't need geographic markers
        "market_topics": {},  # standard topic set
        "cities": US_CITIES,  # city-specific editions available
    },
    "china": {
        "locale_name": "China",
        "locale_phrases": ["in China", "for China's", "in Chinese Life"],
        "market_topics": {
            "involution_anxiety": {"search_kw": "内卷焦虑", "en": "Involution Anxiety"},
            "mental_energy_drain": {"search_kw": "精神内耗", "en": "Mental Energy Drain"},
            "age_35_crisis": {"search_kw": "35岁危机", "en": "The Age-35 Crisis"},
            "parenting_anxiety": {"search_kw": "育儿焦虑", "en": "Parenting Anxiety"},
            "appearance_anxiety": {"search_kw": "容貌焦虑", "en": "Appearance Anxiety"},
            "social_phobia": {"search_kw": "社恐", "en": "Social Phobia"},
            "exam_anxiety": {"search_kw": "考研焦虑", "en": "Exam Anxiety"},
            "workplace_pua": {"search_kw": "职场PUA", "en": "Workplace Manipulation"},
            "family_origin_trauma": {"search_kw": "原生家庭", "en": "Family-of-Origin Wounds"},
        },
    },
    "taiwan": {
        "locale_name": "Taiwan",
        "locale_phrases": ["in Taiwan", "for Taiwan's", "in Taiwanese Life"],
        "market_topics": {
            "housing_pressure": {"search_kw": "買房焦慮", "en": "Housing Pressure"},
            "low_salary_trap": {"search_kw": "低薪困境", "en": "The Low-Salary Trap"},
            "marriage_pressure": {"search_kw": "婚育壓力", "en": "Marriage & Fertility Pressure"},
            "small_happiness": {"search_kw": "小確幸", "en": "Small Certainties of Happiness"},
        },
    },
    "hong_kong": {
        "locale_name": "Hong Kong",
        "locale_phrases": ["in Hong Kong", "for Hong Kong's", "in Hong Kong Life"],
        "market_topics": {
            "emigration_anxiety": {"search_kw": "移民焦慮", "en": "Emigration Anxiety"},
            "housing_stress": {"search_kw": "housing stress", "en": "Housing Stress"},
            "ot_culture": {"search_kw": "OT culture", "en": "Overtime Culture"},
        },
    },
    "singapore": {
        "locale_name": "Singapore",
        "locale_phrases": ["in Singapore", "for Singapore's", "in Singaporean Life"],
        "market_topics": {
            "kiasu_stress": {"search_kw": "kiasu stress", "en": "Kiasu Culture Stress"},
            "sandwich_caregiving": {"search_kw": "sandwich generation", "en": "Sandwich Generation"},
            "expat_identity": {"search_kw": "expat identity", "en": "Expat Identity"},
            "cost_of_living": {"search_kw": "cost of living", "en": "Cost of Living Anxiety"},
        },
    },
}


# =============================================================================
# SECTION 5: TITLE GENERATION ENGINE
# =============================================================================

@dataclass
class GeneratedTitle:
    """A single generated book title with all metadata."""
    brand_id: str
    topic_id: str
    persona_id: str
    market: str
    title: str
    subtitle: str
    search_keyword: str
    invisible_script: str
    locale_name: str = ""
    city: str = ""
    series_id: str = ""
    book_id: str = ""


class PhoenixTitleEngine:
    """
    Generates unique, brand-voiced, persona-aware, topic-specific,
    locale-present audiobook titles.
    """

    def __init__(self, seed: str = "phoenix_v2"):
        self.seed = seed
        self.generated_titles: set[str] = set()
        self.generated_subtitles: set[str] = set()

    def _seeded_random(self, *parts: str) -> random.Random:
        """Create a deterministic random from seed + parts for reproducibility."""
        combined = ":".join([self.seed] + list(parts))
        h = hashlib.sha256(combined.encode()).hexdigest()
        return random.Random(h)

    def _pick(self, rng: random.Random, items: list[str]) -> str:
        """Pick a random item from a list."""
        return rng.choice(items)

    def _pick_n(self, rng: random.Random, items: list[str], n: int = 2) -> list[str]:
        """Pick n unique items from a list."""
        return rng.sample(items, min(n, len(items)))

    def generate_one(
        self,
        brand_id: str,
        topic_id: str,
        persona_id: str,
        market: str = "us",
        city: str = "",
        attempt: int = 0,
    ) -> GeneratedTitle:
        """Generate a single unique title for the given dimensions.

        For US market: city="" means no location in title (universal US).
                       city="nyc"|"la"|"sf"|"chicago"|"boston"|"dc" puts the city in the title.
        For non-US markets: locale_name always appears in the title.
        """

        brand = BRAND_VOICES.get(brand_id)
        topic = TOPIC_VOCAB.get(topic_id)
        persona = PERSONA_HOOKS.get(persona_id)
        locale = MARKET_LOCALES.get(market, MARKET_LOCALES["us"])

        if not brand or not topic or not persona:
            raise ValueError(f"Unknown dimension: brand={brand_id}, topic={topic_id}, persona={persona_id}")

        rng = self._seeded_random(brand_id, topic_id, persona_id, market, city, str(attempt))

        # --- Build components ---
        verb = self._pick(rng, brand["power_verbs"])
        adjective = self._pick(rng, brand["adjectives"])
        invisible_script = self._pick(rng, topic["invisible_scripts"])
        situation = self._pick(rng, topic["situations"])
        outcome = self._pick(rng, topic["outcomes"])
        outcome_word = self._pick(rng, topic["outcome_words"])
        topic_word = self._pick(rng, topic["topic_words"])
        search_keyword = self._pick(rng, topic["search_keywords"])

        # Locale integration — US city-specific vs. US-universal vs. international
        locale_name = ""
        locale_phrase = ""
        city_data = None

        if market == "us" and city:
            # US city-specific book: city name goes in title
            city_data = US_CITIES.get(city)
            if city_data:
                locale_name = city_data["city_name"]
                # Use persona-specific city flavor if available, otherwise generic
                persona_flavor = city_data.get("persona_flavor", {})
                if persona_id in persona_flavor:
                    locale_phrase = persona_flavor[persona_id]
                else:
                    locale_phrase = self._pick(rng, city_data["locale_phrases"])
        elif market == "us" and not city:
            # US-universal: no location at all
            locale_name = ""
            locale_phrase = ""
        else:
            # International markets: always show locale
            locale_name = locale["locale_name"]
            locale_phrase = self._pick(rng, locale["locale_phrases"]) if locale["locale_phrases"] else ""

        # Filter out forbidden frames for this topic
        forbidden = set(topic.get("forbidden_frames", []))
        valid_title_frames = [
            f for f in brand["title_frames"]
            if not any(fw in f.lower() for fw in forbidden)
        ]
        valid_subtitle_frames = [
            f for f in brand["subtitle_frames"]
            if not any(fw in f.lower() for fw in forbidden)
        ]

        if not valid_title_frames:
            valid_title_frames = brand["title_frames"][:2]
        if not valid_subtitle_frames:
            valid_subtitle_frames = brand["subtitle_frames"][:2]

        # --- Generate title ---
        title_frame = self._pick(rng, valid_title_frames)
        title = title_frame.format(
            adjective=adjective.title(),
            verb=verb.title(),
            hook=invisible_script[0].upper() + invisible_script[1:],
            outcome_word=outcome_word,
            topic_word=topic_word,
            locale_phrase=locale_phrase,
            locale_name=locale_name or "Here",
        ).strip()

        # Clean up empty locale artifacts and dangling punctuation
        title = title.replace("  ", " ").replace(" :", ":").strip()
        if title.endswith(":"):
            title = title[:-1].strip()
        if title.endswith("'s"):
            title = title[:-2].strip()
        # Ensure title starts with uppercase
        if title and title[0].islower():
            title = title[0].upper() + title[1:]
        # Fix double "The The" from template + topic_word collision
        title = title.replace("The The ", "The ").replace("the The ", "The ")

        # ENFORCE: if city or international locale is set, the location MUST be in the title
        if locale_phrase and locale_phrase not in title:
            # Append locale to title if the chosen frame didn't include it
            if ":" in title:
                # Insert before the colon hook
                parts = title.split(":", 1)
                title = f"{parts[0].strip()} {locale_phrase}: {parts[1].strip()}"
            else:
                title = f"{title} {locale_phrase}"
            title = title.replace("  ", " ").strip()

        # --- Generate subtitle ---
        persona_hook = self._pick(rng, persona["subtitle_hooks"])
        subtitle_frame = self._pick(rng, valid_subtitle_frames)
        subtitle_base = subtitle_frame.format(
            outcome=outcome,
            situation=situation,
            verb=verb,
            adjective=adjective.lower(),
        ).strip()

        # Capitalize first letter of subtitle
        if subtitle_base and subtitle_base[0].islower():
            subtitle_base = subtitle_base[0].upper() + subtitle_base[1:]

        # Subtitle = benefit promise + persona signal
        subtitle = f"{subtitle_base.rstrip('.')} — {persona_hook}"
        # Clean any double spaces or awkward phrasing
        subtitle = subtitle.replace("  ", " ")

        # --- Dedup check ---
        title_lower = title.lower().strip()
        if title_lower in self.generated_titles and attempt < 10:
            return self.generate_one(brand_id, topic_id, persona_id, market, city, attempt + 1)

        self.generated_titles.add(title_lower)

        # --- Build book_id ---
        city_suffix = f"_{city}" if city else ""
        book_id = f"bk_{brand_id}_{topic_id}_{persona_id}_{market}{city_suffix}"

        return GeneratedTitle(
            brand_id=brand_id,
            topic_id=topic_id,
            persona_id=persona_id,
            market=market,
            title=title,
            subtitle=subtitle,
            search_keyword=search_keyword,
            invisible_script=invisible_script,
            locale_name=locale_name,
            city=city,
            book_id=book_id,
        )

    def generate_catalog(
        self,
        max_books: int = 1008,
        market: str = "us",
        brands: Optional[list[str]] = None,
        topics: Optional[list[str]] = None,
        personas: Optional[list[str]] = None,
    ) -> list[GeneratedTitle]:
        """Generate a full catalog using round-robin across dimensions."""

        brand_ids = brands or list(BRAND_VOICES.keys())
        topic_ids = topics or list(TOPIC_VOCAB.keys())
        persona_ids = personas or list(PERSONA_HOOKS.keys())

        markets = list(MARKET_LOCALES.keys()) if market == "all" else [market]

        catalog: list[GeneratedTitle] = []
        i = 0

        while len(catalog) < max_books:
            b = brand_ids[i % len(brand_ids)]
            t = topic_ids[i % len(topic_ids)]
            p = persona_ids[i % len(persona_ids)]
            m = markets[i % len(markets)] if len(markets) > 1 else markets[0]

            try:
                entry = self.generate_one(b, t, p, m)
                catalog.append(entry)
            except Exception as e:
                print(f"WARN: Generation failed for {b}/{t}/{p}/{m}: {e}", file=sys.stderr)

            i += 1
            if i > max_books * 3:  # safety valve
                print(f"WARN: Hit safety limit at {len(catalog)} books", file=sys.stderr)
                break

        return catalog


# =============================================================================
# SECTION 6: QUALITY VALIDATION
# =============================================================================

def validate_catalog(catalog: list[GeneratedTitle]) -> dict:
    """Run quality checks on generated catalog."""
    titles = [e.title for e in catalog]
    subtitles = [e.subtitle for e in catalog]

    unique_titles = len(set(t.lower() for t in titles))
    unique_subtitles = len(set(s.lower() for s in subtitles))

    # Check for raw slugs
    slug_titles = [t for t in titles if t.lower() in ("at work", "sudden loss", "imposter at work", "for readers")]
    broken_grammar = [t for t in titles if "How to How" in t or "Shut Downing" in t or "Panicing" in t]
    tautologies = [t for t in titles if "confident with confidence" in t.lower()]

    # Brand voice check — do different brands produce different titles for same topic+persona?
    brand_samples: dict[str, list[str]] = {}
    for e in catalog:
        key = f"{e.topic_id}:{e.persona_id}"
        if key not in brand_samples:
            brand_samples[key] = []
        brand_samples[key].append(f"{e.brand_id}: {e.title}")

    # Locale check
    locale_books = [e for e in catalog if e.locale_name and e.locale_name in e.title]
    locale_needed = [e for e in catalog if e.locale_name]

    report = {
        "total_books": len(catalog),
        "unique_titles": unique_titles,
        "uniqueness_rate": f"{unique_titles / len(catalog) * 100:.1f}%",
        "unique_subtitles": unique_subtitles,
        "subtitle_uniqueness": f"{unique_subtitles / len(catalog) * 100:.1f}%",
        "raw_slug_count": len(slug_titles),
        "broken_grammar_count": len(broken_grammar),
        "tautology_count": len(tautologies),
        "locale_books_needed": len(locale_needed),
        "locale_present_in_title": len(locale_books),
        "quality": "PASS" if (
            unique_titles / len(catalog) > 0.85
            and len(slug_titles) == 0
            and len(broken_grammar) == 0
            and len(tautologies) == 0
        ) else "FAIL",
    }
    return report


# =============================================================================
# SECTION 7: CLI
# =============================================================================

def main() -> int:
    ap = argparse.ArgumentParser(description="Phoenix Title Engine v2.0")
    ap.add_argument("--max-books", type=int, default=1008)
    ap.add_argument("--market", default="us", choices=["us", "china", "taiwan", "hong_kong", "singapore", "all"])
    ap.add_argument("--brand", default=None, help="Single brand to generate for")
    ap.add_argument("--topic", default=None, help="Single topic to generate for")
    ap.add_argument("--persona", default=None, help="Single persona to generate for")
    ap.add_argument("--city", default="", choices=["", "nyc", "la", "sf", "chicago", "boston", "dc"],
                    help="US city for city-specific editions (US market only)")
    ap.add_argument("--seed", default="phoenix_v2")
    ap.add_argument("--out", default="-", help="Output path (- for stdout)")
    ap.add_argument("--validate", action="store_true", help="Run quality validation")
    ap.add_argument("--sample", type=int, default=0, help="Print N sample titles to stderr")
    args = ap.parse_args()

    engine = PhoenixTitleEngine(seed=args.seed)

    # Single title mode
    if args.brand and args.topic and args.persona:
        entry = engine.generate_one(args.brand, args.topic, args.persona, args.market, city=args.city)
        print(f"Title:    {entry.title}")
        print(f"Subtitle: {entry.subtitle}")
        print(f"Keyword:  {entry.search_keyword}")
        print(f"Script:   {entry.invisible_script}")
        if entry.locale_name:
            print(f"Locale:   {entry.locale_name}")
        if entry.city:
            print(f"City:     {entry.city}")
        return 0

    # Catalog mode
    brands = [args.brand] if args.brand else None
    topics = [args.topic] if args.topic else None
    personas = [args.persona] if args.persona else None

    catalog = engine.generate_catalog(
        max_books=args.max_books,
        market=args.market,
        brands=brands,
        topics=topics,
        personas=personas,
    )

    # Sample output
    if args.sample > 0:
        import random as rmod
        samples = rmod.sample(catalog, min(args.sample, len(catalog)))
        print("\n--- SAMPLE TITLES ---", file=sys.stderr)
        for s in samples:
            locale_tag = f" [{s.locale_name}]" if s.locale_name else ""
            print(f"  [{s.brand_id}] [{s.topic_id}] [{s.persona_id}]{locale_tag}", file=sys.stderr)
            print(f"    Title:    {s.title}", file=sys.stderr)
            print(f"    Subtitle: {s.subtitle}", file=sys.stderr)
            print(f"    Keyword:  {s.search_keyword}", file=sys.stderr)
            print(file=sys.stderr)

    # Validation
    if args.validate:
        report = validate_catalog(catalog)
        print("\n--- QUALITY REPORT ---", file=sys.stderr)
        for k, v in report.items():
            print(f"  {k}: {v}", file=sys.stderr)
        print(file=sys.stderr)

    # Output
    rows = [asdict(e) for e in catalog]
    text = json.dumps(rows, indent=2, ensure_ascii=False)

    if args.out == "-":
        print(text)
    else:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {len(rows)} titles to {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
