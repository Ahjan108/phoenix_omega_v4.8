#!/usr/bin/env python3
"""
Pearl News v5.2 Article Assembler
==================================
Takes slot-based article JSON and renders full v5.2 interactive HTML
with the complete design system: colored blocks, sidebar, exercise,
CTA, poll, co-creation, authority bar, and nav pillars.

Usage:
    python -m pearl_news.pipeline.assemble_v52 article.json -o output.html
    python -m pearl_news.pipeline.assemble_v52 article.json --metadata meta.json -o output.html

The assembler:
1. Reads the 6 pipeline slots (headline, news_summary, youth_impact,
   teacher_perspective, sdg_un_tie, forward_look)
2. Restructures content into v5.2 semantic sections (hook, news peg,
   sage/body blocks, gold/teacher blocks, blue/turnaround blocks,
   italic hints, practice blocks)
3. Wraps in the full v5.2 HTML template with sidebar, exercise, poll, etc.

Requires either:
  - Extended JSON with metadata fields (teacher, pillar, sdg, etc.)
  - Or a separate metadata JSON file
"""
from __future__ import annotations

import html
import json
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

# ── TEACHER DATABASE ─────────────────────────────────────────────────────────
# Maps teacher name → tradition, key terms, practice, exercise steps, etc.
# This is the minimum teacher data needed for v5.2 rendering.

TEACHER_DB: dict[str, dict[str, Any]] = {
    "maat": {
        "tradition": "Ancient Egyptian Ma'at",
        "tradition_short": "the Egyptian wisdom tradition",
        "credential": "keeper of the Ma'at tradition",
        "key_terms": {
            "witnessing": "the experience of being truly seen — not watched, not surveilled, but seen",
            "field collapse": "when the space where real connection lives gets artificially interrupted",
            "right relationship": "alignment with what is true, including the truths you'd rather not share",
            "isfet": "cosmic disorder — the inversion of truth that makes exploitation look like opportunity",
        },
        "practice_name": "Truth-Speaking Practice",
        "practice_duration": "5 min",
        "practice_description": "From Maat's distinction between being watched and being witnessed. Designed for the weight of disconnection.",
        "exercise_steps": [
            {"phase": "Step 1 of 5 · Ground", "duration": 30, "instruction": "Feel your feet on the floor or your body in the chair. You are here. Not in the feed. Not in the group chat. Here."},
            {"phase": "Step 2 of 5 · Record", "duration": 60, "instruction": "Open your phone's voice memo. Record yourself saying one true sentence about what you're actually feeling right now. No editing. No softening. Just what is true."},
            {"phase": "Step 3 of 5 · Listen", "duration": 60, "instruction": "Play it back. Notice where your chest or jaw tightens. That's the place where witnessing hasn't reached yet. Stay with it."},
            {"phase": "Step 4 of 5 · Witness", "duration": 90, "instruction": "Record a second memo. This time, simply name what you noticed — no fixing, no reframe. Just seeing clearly what is there. This is witnessing."},
            {"phase": "Step 5 of 5 · Notice", "duration": 60, "instruction": "Put the phone down. Notice the difference between how your body felt before and how it feels now. You were seen — by yourself. That counts."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. One true sentence, witnessed without editing, changes more in your nervous system than a thousand curated posts. That's the field Maat teaches about.", "final": True},
        ],
        "cta_practice_label": "Start The Truth-Speaking Practice",
        "cta_regulation_text": "Witness First, Then Connect",
        "cta_body": "Your nervous system knows the difference between being watched and being witnessed. Do the truth-speaking practice now, then choose one real connection.",
        "micro_action": "72-hour micro-action: Have one conversation this week where you say something true that you'd normally edit out.",
    },
    "ahjan": {
        "tradition": "Theravada Buddhism",
        "tradition_short": "the Theravada Buddhist tradition",
        "credential": "Theravada Buddhist teacher for 25 years",
        "key_terms": {
            "saṃvega": "the urgency that arises from seeing clearly how serious things are",
            "vicikicchā": "paralysing doubt — the shutdown, the numbness, the scrolling past",
        },
        "practice_name": "Saṃvega Reset",
        "practice_duration": "4 min",
        "practice_description": "From Ahjan's distinction between shutdown and urgency. Designed for the weight of climate news.",
        "exercise_steps": [
            {"phase": "Step 1 of 6 · Locate", "duration": 20, "instruction": "Close your eyes if you can. Where did the news land in your body? Chest, jaw, stomach, behind the eyes. Find the spot. Stay there."},
            {"phase": "Step 2 of 6 · Name", "duration": 20, "instruction": 'Say the location silently to yourself. "My chest." "My jaw." Just the name. No story about it. Just where it lives right now.'},
            {"phase": "Step 3 of 6 · Breathe", "duration": 60, "instruction": "Inhale for 4 counts. Exhale for 8. The long exhale tells your nervous system: you are safe enough to think clearly. Repeat six times.", "breathe": True},
            {"phase": "Step 4 of 6 · Breathe", "duration": 60, "instruction": "Keep going. Inhale 4, exhale 8. Each breath is not about calming down. It's about moving from shutdown to clarity. You're training the gear shift.", "breathe": True},
            {"phase": "Step 5 of 6 · Ask", "duration": 50, "instruction": 'Ask yourself: "Am I shutting down — or gearing up?" There\'s no right answer. Just sit with the question. Let it do its work.'},
            {"phase": "Step 6 of 6 · Notice", "duration": 30, "instruction": "Notice what shifted. Your shoulders, your jaw, the space behind your eyes. You don't need to feel better. You just need to know which gear you're in."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. What you felt reading that number was not weakness. It was your system registering a real threat. Now you know the difference between shutdown and response.", "final": True},
        ],
        "cta_practice_label": "Start The Saṃvega Reset",
        "cta_regulation_text": "Regulate First, Then Act",
        "cta_body": "Your nervous system responds before your analysis does. Do the teacher-guided reset now, then choose one practical action.",
        "micro_action": "72-hour micro-action: Identify one local climate adaptation meeting or school/community project and register this week.",
    },
    "junko": {
        "tradition": "Contemporary Japanese channeling and light-language spirituality",
        "tradition_short": "the Japanese channeling tradition",
        "credential": "channeler and light-language transmitter",
        "key_terms": {
            "light language": "vibrational communication that carries direct messages from higher beings — not words, but frequency that reaches the soul before the mind",
            "transmission": "guidance that arrives through resonance rather than explanation, carrying real information the receiver's soul recognizes",
            "alignment": "the inner energetic posture from which requests, prayers, and intentions actually reach the field",
            "soul remembrance": "the recognition that you already know what you are being shown — the soul remembering, not the mind learning",
        },
        "practice_name": "Receiving Practice",
        "practice_duration": "5 min",
        "practice_description": "From Junko's teaching on receiving direct guidance. Designed for when you have been trying too hard to figure things out on your own.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Arrive", "duration": 30, "instruction": "Sit somewhere quiet. Close your eyes. Let your hands rest open. You are not here to produce an answer. You are here to receive one."},
            {"phase": "Step 2 of 7 · Soften", "duration": 40, "instruction": "Let your attention drop from your head into your chest. Stop trying to think your way forward. The mind analyzes. The chest receives. Let the chest lead for now."},
            {"phase": "Step 3 of 7 · Breathe", "duration": 45, "instruction": "Breathe slowly. Each exhale softens the guard a little more. You are not calming down — you are opening a channel. Guidance travels most clearly through a system that is not clenched.", "breathe": True},
            {"phase": "Step 4 of 7 · Listen", "duration": 60, "instruction": "Stop producing. Start listening. Not with your ears — with your whole system. Notice if anything arrives: a word, a feeling, a sense of direction, a warmth. Do not interpret it yet. Just notice what shows up when you stop generating."},
            {"phase": "Step 5 of 7 · Receive", "duration": 50, "instruction": "Whatever arrived — even if it was faint, strange, or wordless — let it stay. Do not argue with it. Do not test it against logic yet. The meaning may unfold later. Your only job right now is to let it land."},
            {"phase": "Step 6 of 7 · Ground", "duration": 40, "instruction": "Feel your feet on the floor. Feel the weight of your body. You have been in a receptive state — now bring yourself gently back to ordinary awareness. The message does not disappear when you open your eyes."},
            {"phase": "Step 7 of 7 · Record", "duration": 35, "instruction": "Open your eyes. Write down whatever arrived, even if it does not make sense yet. One sentence is enough. Over time, these notes become a map of what your guidance is pointing toward."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. What came through was not your imagination producing content — it was your system receiving a signal it already knew how to recognize. That recognition is the beginning of everything Junko teaches about.", "final": True},
        ],
        "cta_practice_label": "Start The Receiving Practice",
        "cta_regulation_text": "Receive First, Then Understand",
        "cta_body": "Your soul already knows what it is being shown. Stop trying to figure it out and start receiving. Do the guided practice now, then notice what arrived.",
        "micro_action": "72-hour micro-action: Each evening this week, write one sentence capturing any guidance or knowing that arrived during the day without you trying to produce it.",
    },
    "sai_ma": {
        "tradition": "Consciousness, Divine Feminine, and Grace-Mastery teaching",
        "tradition_short": "the consciousness and divine feminine tradition",
        "credential": "spiritual master, consciousness teacher, and humanitarian leader",
        "key_terms": {
            "consciousness": "the awareness that already knows what you are — awakening is not becoming, it is recognizing",
            "shakti": "the divine feminine as creative force, power, and sovereignty — not only tenderness but the fierce refusal to shrink",
            "grace and mastery": "grace allows the old pattern to release; mastery is the practice of choosing differently — together they transform",
        },
        "practice_name": "Consciousness Awakening",
        "practice_duration": "5 min",
        "practice_description": "From Sai Maa's teaching on consciousness, pattern release, and divine feminine power. Designed for when old patterns run the show.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Ground", "duration": 30, "instruction": "Feel your feet on the ground. Place your hand on your heart. You are not trying to become worthy. You already are. Feel the ground beneath you — love is the foundation, not the goal."},
            {"phase": "Step 2 of 7 · Breathe", "duration": 40, "instruction": "Breathe naturally. With each exhale, release one layer of striving. The breath is the bridge between conscious and unconscious. Let it carry you back to what is already here.", "breathe": True},
            {"phase": "Step 3 of 7 · Locate", "duration": 40, "instruction": "Bring awareness to one place in your body where you feel contraction — where an old pattern holds. Do not judge it. Just locate it. The trigger is not a malfunction. It is showing you exactly where the limitation lives."},
            {"phase": "Step 4 of 7 · Meet", "duration": 50, "instruction": "Breathe directly into that contraction. Say silently: I see you. You protected me once. Thank you. Grace is not forcing release. It is meeting what is here with awareness."},
            {"phase": "Step 5 of 7 · Choose", "duration": 40, "instruction": "Now, from that meeting, choose. Not from force — from clarity. Say: I can choose differently now. Feel the sovereignty in that choice. This is mastery — the practice of conscious response."},
            {"phase": "Step 6 of 7 · Activate", "duration": 40, "instruction": "Feel your spine lengthen. Feel your voice in your throat. The divine feminine in you is not asking permission. She is here. She matters. Let that power activate — not as aggression, but as truth."},
            {"phase": "Step 7 of 7 · Integrate", "duration": 30, "instruction": "Return to the ground. Feel yourself held. The consciousness that moved just now was not something you created. It was something you allowed by clearing the obstruction."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. You are not broken. You are awake. Grace and mastery — both are yours.", "final": True},
        ],
        "cta_practice_label": "Start The Consciousness Awakening Practice",
        "cta_regulation_text": "Awaken, Then Choose",
        "cta_body": "Your patterns are not failures — they are the soul's curriculum. Meet them with awareness. Choose from consciousness, not reactivity.",
        "micro_action": "72-hour micro-action: When a trigger fires this week, pause and ask: what is this pattern protecting me from? Thank it. Then choose differently.",
    },
    "master_wu": {
        "tradition": "Taiwanese geomancy and dragon-vein land-energy teaching",
        "tradition_short": "the Taiwanese geomancy tradition",
        "credential": "geomancer and land-energy teacher",
        "key_terms": {
            "dragon vein": "the continuous energetic flow across land — when it flows, life along it thrives; when blocked, the disruption ripples into human life",
            "blockage": "interruption in the flow channel — in land or in body — that produces downstream dysfunction; the primary diagnostic frame",
            "earth energy": "地氣 — the vital force received through physical contact with the ground, severed by sealed environments and digital life",
            "place memory": "the accumulated energy and information a place holds from everyone who lived, walked, and shaped it over time",
        },
        "practice_name": "Ground-Flow Reset",
        "practice_duration": "5 min",
        "practice_description": "From Master Wu's teaching on dragon-vein flow. Designed for when you feel stuck, sealed off, or disconnected from the ground.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Contact", "duration": 30, "instruction": "Feel your feet on the floor. Whatever surface is beneath you, it is covering something older — soil, stone, the original terrain. Feel the weight of your body transferring downward. The ground is holding the building. It can hold you too."},
            {"phase": "Step 2 of 7 · Locate", "duration": 35, "instruction": "Scan your body. Where is the tightness? The compression? The sense that something should be moving but is not? Jaw, shoulders, chest, low back — find the blockage point. Name it. You have just done what a geomancer does with land: located where the flow is interrupted."},
            {"phase": "Step 3 of 7 · Breathe", "duration": 45, "instruction": "Imagine a vertical line from the base of your spine to the top of your head. This is your internal dragon vein. Breathe along the line — inhale up from the base, exhale down from the crown. Do not force it. Follow the channel.", "breathe": True},
            {"phase": "Step 4 of 7 · Clear", "duration": 50, "instruction": "Bring your breath toward the blockage point you found. Not to force it open — to bring warmth and attention. Each exhale softens the obstruction by one percent. You are not adding anything. You are removing what was imposed."},
            {"phase": "Step 5 of 7 · Flow", "duration": 45, "instruction": "Continue breathing along the vertical line. Notice if the channel feels different now — more open, less compressed, slightly warmer. The flow does not need your effort. It needs the obstruction cleared. Whatever shifted, let it continue.", "breathe": True},
            {"phase": "Step 6 of 7 · Ground", "duration": 35, "instruction": "Return your attention to your feet on the floor. Feel the weight transfer down. You have been working with the internal channel. Now reconnect it to the ground beneath you. The internal dragon vein meets the earth here — at the soles of your feet."},
            {"phase": "Step 7 of 7 · Settle", "duration": 30, "instruction": "Open your eyes. Notice the room. Notice the ground. Notice your body in this place. The flow you restored does not require maintenance right now — just the acknowledgment that the channel is more open than it was five minutes ago."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. What shifted was not something you created. It was something you allowed by locating the blockage and letting the channel soften. That is the principle — in land and in body.", "final": True},
        ],
        "cta_practice_label": "Start The Ground-Flow Reset",
        "cta_regulation_text": "Locate First, Then Clear",
        "cta_body": "Your body has a geography — channels, blockages, and flow. The ground beneath you has been waiting for your attention. Do the diagnostic reset now, then notice what shifted.",
        "micro_action": "72-hour micro-action: Three times daily, stop for thirty seconds — feel your feet on the ground, feel your spine as a vertical line, take one slow breath along it.",
    },
    "master_sha": {
        "tradition": "Tao Source, Soulfulness, and sacred wisdom teaching",
        "tradition_short": "the Tao Source and Soulfulness tradition",
        "credential": "spiritual master and Tao Source teacher",
        "key_terms": {
            "Tao Source": "the ultimate spiritual source — a living presence of golden light that sustains all life and to which all practice returns",
            "Soulfulness": "soul guided meditation — the systematic practice of listening to the soul's intelligence rather than the mind's analysis",
            "blockage": "where flow has stopped in the energetic system — created by held emotions, unprocessed experience, and attachment — can be washed with golden light",
        },
        "practice_name": "Tao Source Golden Light",
        "practice_duration": "5 min",
        "practice_description": "From Master Sha's teaching on Tao Source light, blockage clearing, and greatest love-forgiveness-compassion. Designed for when blockages are running the show.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Ground", "duration": 30, "instruction": "Sit with your spine upright. Feel your feet on the ground. Place your hands on your lower abdomen. Feel the connection to Mother Earth beneath you — stable, patient, holding."},
            {"phase": "Step 2 of 7 · Invite", "duration": 35, "instruction": "Imagine a sphere of golden light above your crown. This is Tao Source light — the origin of everything. With each inhale, invite the golden light to enter through the crown of your head."},
            {"phase": "Step 3 of 7 · Wash", "duration": 50, "instruction": "Feel the golden light flowing downward through your body — head, throat, chest, belly, legs, feet. Wherever it encounters a blockage — tightness, heaviness, stagnation — let it pause and wash.", "breathe": True},
            {"phase": "Step 4 of 7 · Forgive", "duration": 40, "instruction": "Bring to mind one thing you are holding — a resentment, a regret, a self-judgment. Say silently: I offer greatest forgiveness. I release this blockage. I return to peace. Feel the golden light washing through the holding."},
            {"phase": "Step 5 of 7 · Love", "duration": 40, "instruction": "Generate the feeling of greatest love in your heart center. Not as performance — as frequency. Feel it expand outward. Love melts what resistance cannot. Let it flow through every remaining blockage."},
            {"phase": "Step 6 of 7 · Listen", "duration": 35, "instruction": "Shift into Soulfulness. Ask silently: Dear soul, what do you need me to know? Then listen — not with the mind, but with the body. The soul speaks in warmth, in knowing, in sudden clarity. Receive whatever comes."},
            {"phase": "Step 7 of 7 · Return", "duration": 30, "instruction": "Feel yourself filled with golden light from Tao Source. Feel the peace that comes when blockages have been washed. You are not separate from this light. You are this light, temporarily traveling."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. The golden light continues to work after you open your eyes. Carry the peace of Tao Source into whatever comes next.", "final": True},
        ],
        "cta_practice_label": "Start The Tao Source Golden Light Practice",
        "cta_regulation_text": "Wash First, Then Flow",
        "cta_body": "Blockages are not character flaws — they are obstructions that can be cleared. Golden light from Tao Source washes what force cannot move. Return to the source now.",
        "micro_action": "72-hour micro-action: Once each day, close your eyes for one minute and imagine golden light washing through your body from crown to feet. Let it carry one blockage away.",
    },
    "master_feung": {
        "tradition": "Taoist cultivation through art and embodied practice",
        "tradition_short": "the Taoist artistic cultivation tradition",
        "credential": "Chinese cultivation master, painter, and Guqin practitioner",
        "key_terms": {
            "naturalness": "the state that remains when striving falls away — not laziness, but the deepest kind of ease, aligned with the Tao",
            "cultivation": "the practice of refining the self through art, movement, breath, and attention — not producing results, but becoming more natural",
            "heart response": "sensing from the heart before the mind categorises — a faster and more honest intelligence that lives below thought",
        },
        "practice_name": "Mountain Stillness & Brush",
        "practice_duration": "5 min",
        "practice_description": "From Master Fan's teaching on naturalness, Tai Chi, and art as cultivation. Designed for when the body is tight and the mind is forcing.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Stand", "duration": 30, "instruction": "Stand with feet shoulder-width apart. Soften the knees. Let the arms hang. Feel the ground through the soles of the feet. This is standing root — the foundation of Tai Chi and all cultivation."},
            {"phase": "Step 2 of 7 · Breathe", "duration": 35, "instruction": "Breathe naturally. Do not change the rhythm. Just notice where the breath goes — chest, belly, throat. The breath tells the truth about what the body is carrying. Let it speak.", "breathe": True},
            {"phase": "Step 3 of 7 · Settle", "duration": 40, "instruction": "Release ten per cent of the tension in your shoulders, jaw, and hands. Not all of it — just ten per cent. Naturalness arrives in increments. The mountain does not try to be stable. Let the body find its own stillness."},
            {"phase": "Step 4 of 7 · Sense", "duration": 35, "instruction": "Place a hand on your chest. Ask: what does the heart sense right now? Not think — sense. Wait three seconds. Heart response is faster and more honest than analysis. Trust what arrives."},
            {"phase": "Step 5 of 7 · Move", "duration": 40, "instruction": "Slowly shift your weight to one foot. Then back. Then to the other. Feel the ground rise to meet you. This is Tai Chi's first lesson: the body moves, the mind observes. Let the body lead."},
            {"phase": "Step 6 of 7 · Draw", "duration": 35, "instruction": "If a pen is near, draw one slow line on paper. If not, trace a line in the air with your finger. Let the movement coordinate with the exhale. The line is a record of your breath. Let it be honest, not perfect."},
            {"phase": "Step 7 of 7 · Return", "duration": 30, "instruction": "Stand still again. Feel what has shifted. The body is slightly more settled. The breath is slightly more natural. This is cultivation — not dramatic, not loud, just one degree closer to naturalness."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. Carry the stillness with you. The mountain does not leave the mountain. You do not have to leave this calm.", "final": True},
        ],
        "cta_practice_label": "Start The Mountain Stillness & Brush Practice",
        "cta_regulation_text": "Settle First, Then Move",
        "cta_body": "The body knows before the mind. Cultivation through art, breath, and stillness returns you to what was always there — naturalness. Begin now.",
        "micro_action": "72-hour micro-action: Once each day, draw one slow line on paper. Let the breath coordinate with the stroke. Notice what the line teaches the hand.",
    },
    "joshin": {
        "tradition": "Mainstream Shingon Buddhism (Mikkyo)",
        "tradition_short": "the Shingon Mikkyo tradition",
        "credential": "Shingon teacher in the mainstream Mikkyo lineage",
        "key_terms": {
            "Sokushin Jobutsu": "Buddhahood realised in this present body — not deferred, not distant, but available through embodied practice now",
            "Sanmitsu": "the three mysteries — body (mudra), speech (mantra), and mind (visualization) aligned simultaneously in practice",
            "Rigu no Jobutsu": "inherent awakened worth — enlightenment is already present, practice reveals rather than creates it",
        },
        "practice_name": "Sanmitsu Alignment",
        "practice_duration": "5 min",
        "practice_description": "From Joshin's Shingon teaching on body-speech-mind integration, mantra, and mudra. Designed for when the mind is scattered and the body needs to lead.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Sit", "duration": 30, "instruction": "Sit upright. Feel the spine as a vertical axis. Let the body settle. In Shingon, the body is the first temple. Before any practice, the body must be present and willing."},
            {"phase": "Step 2 of 7 · Breathe", "duration": 30, "instruction": "Breathe naturally. Do not control the rhythm. Follow the breath to the belly and let it settle on its own. This settling is the ground from which Sanmitsu rises.", "breathe": True},
            {"phase": "Step 3 of 7 · Form", "duration": 35, "instruction": "Bring your palms together at the heart. This is the most basic mudra — the gesture of meeting. Hold it with attention. The hands shape the body's state. Feel what opens in the chest."},
            {"phase": "Step 4 of 7 · Chant", "duration": 40, "instruction": "Silently repeat the syllable A — once per exhale. Feel where the vibration settles: chest, throat, belly. The mantra is not words. It is vibration entering the body and aligning speech with awakened activity."},
            {"phase": "Step 5 of 7 · See", "duration": 40, "instruction": "Visualize a bright full moon at your heart centre. Let it glow with the inherent clarity of your own mind. This is Gachirinkan. The brightness was always there. The practice makes it visible."},
            {"phase": "Step 6 of 7 · Align", "duration": 35, "instruction": "Hold all three together: mudra at the heart, silent mantra on the exhale, moon disc in the mind. Body, speech, mind — aligned. This is Sanmitsu. When all three converge, you are practising as Buddhahood."},
            {"phase": "Step 7 of 7 · Receive", "duration": 30, "instruction": "Release the mudra and the mantra. Let the visualization fade. Sit in the space they created. Kaji — the blessings — enter in the stillness after practice. Receive whatever comes."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. Sokushin Jobutsu: this body just practised realization. Carry that knowing into whatever comes next.", "final": True},
        ],
        "cta_practice_label": "Start The Sanmitsu Alignment Practice",
        "cta_regulation_text": "Align First, Then Act",
        "cta_body": "Body, speech, and mind — when all three converge, realization is not distant. It is here. Shingon gives the method. Your body is the vehicle. Begin now.",
        "micro_action": "72-hour micro-action: Once each day, press your thumbs together for thirty seconds while silently repeating one syllable. Feel what shifts in the chest.",
    },
    "pamela_fellows": {
        "tradition": "Heartfulness and Embodiment",
        "tradition_short": "heartfulness-through-embodiment practice",
        "credential": "teacher of heartfulness and embodied transformation",
        "key_terms": {
            "heartfulness": "living from the heart's intelligence — not sentiment, but a deeper knowing that includes the body and the present moment",
            "embodiment": "returning attention to the body as a source of truth — the body holds what the mind avoids",
            "inner blockage": "the deeper pattern underneath surface problems — met with safety and presence, it can release",
        },
        "practice_name": "Heart and Body Check-In",
        "practice_duration": "5 min",
        "practice_description": "From Pamela's teaching on heartfulness and embodiment. Designed for when you are living from the head and the body needs to be included.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Ground", "duration": 30, "instruction": "Feel your feet on the floor. Feel what is supporting your body right now — the chair, the ground, the surface beneath you. You are here. Let the body know it is safe."},
            {"phase": "Step 2 of 7 · Breathe", "duration": 35, "instruction": "Let the breath be natural. Do not control it. Follow the inhale and exhale for a few rounds. Let the breath be the bridge between doing and being. The body settles when the breath is noticed.", "breathe": True},
            {"phase": "Step 3 of 7 · Scan", "duration": 40, "instruction": "Bring attention slowly through the body — head, shoulders, chest, belly, legs, feet. Do not try to fix anything. Just notice what is there. Tension. Ease. Heaviness. Aliveness. The body has been holding all of this."},
            {"phase": "Step 4 of 7 · Heart", "duration": 40, "instruction": "Place your hand on your heart. Breathe gently. Ask: what does the heart want me to know right now? Do not force an answer. Just listen. The heart speaks in feeling, in warmth, in a quiet pull. Trust what arrives."},
            {"phase": "Step 5 of 7 · Feel", "duration": 35, "instruction": "If something is emotionally present — a worry, a sadness, an unresolved feeling — find where it lives in the body. Do not analyze it. Just feel it there. Let it be held by your awareness, not managed by your mind."},
            {"phase": "Step 6 of 7 · Meet", "duration": 30, "instruction": "Whatever you found — tension, emotion, quietness — meet it with warmth. Say silently: I see you. You can be here. The meeting is the practice. You are not fixing. You are including."},
            {"phase": "Step 7 of 7 · Settle", "duration": 30, "instruction": "Let the hand rest in your lap. Take three easy breaths. Notice what shifted — even slightly. The body may feel a little lighter, a little more present. Let whatever happened settle on its own."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. The heart and body were included. That changes the quality of whatever comes next — not through effort, but through presence.", "final": True},
        ],
        "cta_practice_label": "Start The Heart and Body Check-In",
        "cta_regulation_text": "Feel First, Then Move",
        "cta_body": "The body holds what the mind avoids. The heart knows what the mind has not caught up to. When both are included, you are more present, more grounded, more yourself. Begin now.",
        "micro_action": "72-hour micro-action: Three times each day, place your hand on your heart for ten seconds. Feel what the heart is holding. You do not need to do anything with it. Just notice.",
    },
    "miki": {
        "tradition": "Light Language and Sound Healing",
        "tradition_short": "light-language and sound healing practice",
        "credential": "healer and light-language transmitter",
        "key_terms": {
            "light language": "a transmission that bypasses the analytical mind and speaks directly to the body — it does not require understanding, only receiving",
            "transmission": "healing energy that moves through sound, light, and presence — the body receives it before the mind can interpret",
            "healing as remembering": "the original self is not gone — it is covered — and healing is the process of uncovering what was always there",
        },
        "practice_name": "Sound and Light Receiving",
        "practice_duration": "5 min",
        "practice_description": "From Miki's teaching on sound healing and light-language transmission. Designed for when the body needs to receive what words cannot reach.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Settle", "duration": 30, "instruction": "Sit or lie comfortably. Close your eyes. Let the body land. Feel whatever is supporting you — the chair, the floor, the ground. You do not need to do anything yet. Just arrive."},
            {"phase": "Step 2 of 7 · Breathe", "duration": 30, "instruction": "Breathe naturally. Do not control it. Let each exhale be a little longer, a little softer. The breath is not the practice. It is the preparation. It tells the body: you can receive now.", "breathe": True},
            {"phase": "Step 3 of 7 · Sound", "duration": 40, "instruction": "Hum a single note — whatever note feels right. Feel the vibration in the chest, the throat, the belly. This is your body making its own sound. The vibration reaches places that words cannot touch."},
            {"phase": "Step 4 of 7 · Receive", "duration": 40, "instruction": "Stop humming. Sit in the silence. The silence after sound is full. Let the body receive whatever is present — warmth, settling, a quality of light. You do not need to name it. Just let it in."},
            {"phase": "Step 5 of 7 · Soften", "duration": 35, "instruction": "Find a tight place in the body. Breathe warmth toward it. Do not force. Just offer. The tightness will soften when it is ready. If tears come, let them. They are part of the opening."},
            {"phase": "Step 6 of 7 · Remember", "duration": 30, "instruction": "Ask quietly: who was I before the contraction? Before the covering? Let the answer arrive as feeling, not words. The original self is not gone. It is here. Under everything. Still here."},
            {"phase": "Step 7 of 7 · Rest", "duration": 25, "instruction": "Let everything settle. Do not analyze what happened. The body integrates quietly, in its own time. Rest is part of healing. Let the body do what it knows how to do."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. Sound entered. Something softened. The body received. Let the quiet continue to work.", "final": True},
        ],
        "cta_practice_label": "Start The Sound and Light Receiving Practice",
        "cta_regulation_text": "Receive First, Then Rest",
        "cta_body": "Sound reaches what words cannot. Light language enters through the body, not the mind. What is contracted can soften. What is forgotten can be remembered. The body knows what to do. Let it receive.",
        "micro_action": "72-hour micro-action: Once each day, hum a single note for thirty seconds. Feel the vibration in your chest. Let the body receive its own sound.",
    },
    "yuan_miao": {
        "tradition": "Esoteric Buddhist and Dakini-Lineage Joy Practice",
        "tradition_short": "dakini-lineage esoteric Buddhist joy practice",
        "credential": "lineage-bearing spiritual teacher and dakini",
        "key_terms": {
            "Yoga of Joy": "a unified practice system where joy is both the method and the realization — combining breath, posture, mantra, mudra, and visualization",
            "transmission": "living energy passed through lineage, sound, and practice — not information but vibration and quality that the body receives directly",
            "primordial nature": "the luminous, unconditioned ground of being that practice reveals — not manufactured by effort but remembered through direct experience",
        },
        "practice_name": "Joy and Mantra Practice",
        "practice_duration": "5 min",
        "practice_description": "From Yuan Miao's Yoga of Joy and sacred sound transmission. Designed for when the body needs to enter practice through joy, breath, and mantra.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Settle", "duration": 30, "instruction": "Sit upright, shoulders relaxed, spine tall. Close the eyes. Let the body arrive. Feel the weight settle. You do not need to do anything yet. Just be here."},
            {"phase": "Step 2 of 7 · Breathe", "duration": 30, "instruction": "Begin the breath — slow, steady, through the nose. Let each exhale be a release. Each inhale, a receiving. The breath is the foundation. Let it settle the body.", "breathe": True},
            {"phase": "Step 3 of 7 · Joy", "duration": 30, "instruction": "Now let joy enter the breath. Not forced. Invited. Breathe joy in with the inhale. Let the body hold it. If a smile arises, let it stay. Joy is not a reward. It is the practice."},
            {"phase": "Step 4 of 7 · Mantra", "duration": 40, "instruction": "Add the mantra on the exhale. Chant softly or silently. Feel where the vibration lands — the chest, the throat, the belly. The mantra carries transmission. Let it work."},
            {"phase": "Step 5 of 7 · Mudra", "duration": 30, "instruction": "Form the mudra with both hands. Hold it. Feel what shifts — a subtle settling, a warmth, a change in the body's energy. Mudra is precise configuration. The body receives it."},
            {"phase": "Step 6 of 7 · Visualize", "duration": 35, "instruction": "Hold the Blue Pearl at the heart — a luminous sphere, radiating light. Each exhale extends its glow. This is your primordial nature. Practice did not create it. Practice reveals it."},
            {"phase": "Step 7 of 7 · Rest", "duration": 25, "instruction": "Release the technique. Let everything settle. The mantra continues to work after the chanting stops. The joy remains. Rest in what the practice revealed."},
            {"phase": "Complete", "duration": 0, "instruction": "Joy, compassion, direct experience — these are what the practice reveals. What arose was not manufactured. It was remembered.", "final": True},
        ],
        "cta_practice_label": "Start The Joy and Mantra Practice",
        "cta_regulation_text": "Practice with Joy, Rest in Transmission",
        "cta_body": "Joy is not a reward for practice. It is the practice itself. Sacred sound carries what concepts cannot. The Blue Pearl at the heart radiates your primordial nature. Let the lineage enter through breath, mantra, and joy.",
        "micro_action": "72-hour micro-action: Once each day, chant a mantra for one minute — aloud or silently. Feel the vibration in your body. Then rest in the silence that follows.",
    },
    "omote": {
        "tradition": "Japanese Sacred Way-of-Life and Purification Teaching",
        "tradition_short": "Japanese sacred way-of-life and purification teaching",
        "credential": "Japanese traditional wisdom teacher",
        "key_terms": {
            "purification": "the ongoing practice of cleansing what has accumulated — not magical erasure, but the honest discipline of restoring clarity through water, wind, ritual, and breath",
            "oni": "not only external monsters — the inner afflictions, destructive patterns, and habits that must be faced with honest seeing rather than avoidance",
            "helping others": "service as spiritual practice — helping others is what ultimately saves ourselves, restoring both the one served and the one serving",
        },
        "practice_name": "Purification and Service Practice",
        "practice_duration": "4 min",
        "practice_description": "From Omote's teaching on Japanese purification and the way of life. Designed for when you need to clear what has accumulated and return to right relationship.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 · Settle", "duration": 25, "instruction": "Sit quietly. Let the body arrive. Feel the ground beneath you. The tradition begins with settling — the body first, then the spirit."},
            {"phase": "Step 2 of 7 · Purify", "duration": 30, "instruction": "Breathe as if the breath were water — washing through the body, clearing what has accumulated. Three slow breaths of cleansing. Let each exhale carry something away.", "breathe": True},
            {"phase": "Step 3 of 7 · Face", "duration": 30, "instruction": "Turn inward. Ask: what pattern is running in me right now? Not the surface emotion — the deeper pattern. The oni within. Name it. Not to punish. To see."},
            {"phase": "Step 4 of 7 · Release", "duration": 25, "instruction": "Hold what you named without judgment. Breathe into it. Then let the breath carry it outward. Purification does not require force. It requires honest release."},
            {"phase": "Step 5 of 7 · Serve", "duration": 25, "instruction": "Think of one person who needs help. Hold them in your awareness. Set the intention: today, I will do one thing for them. Helping others is what saves ourselves."},
            {"phase": "Step 6 of 7 · Remember", "duration": 25, "instruction": "Remember those who practiced before you. The ancestors. The tradition carriers. Their practice lives through yours. Let their strength enter."},
            {"phase": "Step 7 of 7 · Return", "duration": 20, "instruction": "Rest in the clarity. What was cleansed does not need to be carried forward. What was intended for service will find its moment. The practice is done. Carry it into the day."},
            {"phase": "Complete", "duration": 0, "instruction": "Purification, service, honest seeing — these are the practice. The tradition lives through what you do next.", "final": True},
        ],
        "cta_practice_label": "Start The Purification and Service Practice",
        "cta_regulation_text": "Cleanse, Face, Serve",
        "cta_body": "Purification clears what has accumulated. The oni within is faced with honesty, not hatred. Helping others saves ourselves. This is the way of life that Japanese tradition teaches.",
        "micro_action": "72-hour micro-action: Each day, wash your hands with intention — let the water carry one thing you no longer need to hold. Then do one small act of service.",
    },
    "ra": {
        "tradition": "Awakening, Integration, and Satsang",
        "tradition_short": "the awakening and integrated satsang tradition",
        "credential": "awakening mentor and satsang teacher",
        "key_terms": {
            "integrated awakening": "awakening that is lived and grounded in daily life — not a peak experience but a sustained shift in how you meet reality",
            "conditioning": "the inherited patterns of thought, emotion, and reaction that run automatically — they can be seen and released",
            "trust": "the willingness to let go of what the mind insists on and rest in what awareness already knows",
        },
        "practice_name": "Integrated Awakening Practice",
        "practice_duration": "5 min",
        "practice_description": "From Ra's teaching on awakening, integration, and the release of conditioning. Designed for when old patterns are running the show and clarity feels distant.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 \u00b7 Ground", "duration": 30, "instruction": "Sit comfortably. Feel your body in the chair. Feel the ground beneath your feet. You are here \u2014 not in the story the mind is telling. Here."},
            {"phase": "Step 2 of 7 \u00b7 Witness", "duration": 40, "instruction": "Notice what is present \u2014 a thought, a feeling, a sensation. Do not judge it. Do not try to change it. Simply observe it with curiosity. The awareness that is watching is never harmed by what it sees."},
            {"phase": "Step 3 of 7 \u00b7 Identify", "duration": 40, "instruction": "Ask: what pattern is running right now? Is it fear? Control? The need to be right? Name the conditioning. Naming it creates distance. You are not the pattern. You are the one who can see it."},
            {"phase": "Step 4 of 7 \u00b7 Release", "duration": 45, "instruction": "Breathe into the pattern. Say silently: I see you. I do not need to follow you. Each exhale is a small letting go. Release is not force. It is trust \u2014 trusting that what you are is larger than the conditioning.", "breathe": True},
            {"phase": "Step 5 of 7 \u00b7 Rest", "duration": 40, "instruction": "Let go of the effort. Rest in the spaciousness that remains when the pattern loosens. This is not emptiness. It is the ground. It does not move. You can rest here."},
            {"phase": "Step 6 of 7 \u00b7 Integrate", "duration": 35, "instruction": "Ask: what does this clarity want me to bring into my day? Not a grand insight \u2014 one practical thing. Integration means the awakening walks with you into ordinary life. Let one clear action emerge."},
            {"phase": "Step 7 of 7 \u00b7 Return", "duration": 30, "instruction": "Open your eyes. Feel the room. Feel your body. The witness did not leave. The clarity did not vanish. They are here, underneath the next thought. You can return any time."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. Awakening is not somewhere else. It is what happens when conditioning loosens and you see clearly. Integration is what happens when you take that seeing into your next conversation, your next choice, your next breath.", "final": True},
        ],
        "cta_practice_label": "Start The Integrated Awakening Practice",
        "cta_regulation_text": "See Clearly, Then Respond",
        "cta_body": "Your patterns are not who you are \u2014 they are what runs when awareness is elsewhere. When you see conditioning clearly, it loses its grip. Awakening is not a destination. It is what is already here when the noise settles.",
        "micro_action": "72-hour micro-action: Three times each day, pause and ask: what pattern is running right now? Name it. Then choose one response that comes from clarity rather than habit.",
    },
    "channeler_junko": {
        "tradition": "Contemporary Japanese channeling and light-language spirituality",
        "tradition_short": "the Japanese channeling tradition",
        "credential": "channeler and light-language transmitter",
        "key_terms": {
            "light language": "vibrational communication that carries direct messages from higher beings \u2014 not words, but frequency that reaches the soul before the mind",
            "transmission": "guidance that arrives through resonance rather than explanation, carrying real information the receiver's soul recognizes",
            "alignment": "the inner energetic posture from which requests, prayers, and intentions actually reach the field",
            "soul remembrance": "the recognition that you already know what you are being shown \u2014 the soul remembering, not the mind learning",
        },
        "practice_name": "Receiving Practice",
        "practice_duration": "5 min",
        "practice_description": "From Junko's teaching on receiving direct guidance. Designed for when you have been trying too hard to figure things out on your own.",
        "exercise_steps": [
            {"phase": "Step 1 of 7 \u00b7 Arrive", "duration": 30, "instruction": "Sit somewhere quiet. Close your eyes. Let your hands rest open. You are not here to produce an answer. You are here to receive one."},
            {"phase": "Step 2 of 7 \u00b7 Soften", "duration": 40, "instruction": "Let your attention drop from your head into your chest. Stop trying to think your way forward. The mind analyzes. The chest receives. Let the chest lead for now."},
            {"phase": "Step 3 of 7 \u00b7 Breathe", "duration": 45, "instruction": "Breathe slowly. Each exhale softens the guard a little more. You are not calming down \u2014 you are opening a channel. Guidance travels most clearly through a system that is not clenched.", "breathe": True},
            {"phase": "Step 4 of 7 \u00b7 Listen", "duration": 60, "instruction": "Stop producing. Start listening. Not with your ears \u2014 with your whole system. Notice if anything arrives: a word, a feeling, a sense of direction, a warmth. Do not interpret it yet. Just notice what shows up when you stop generating."},
            {"phase": "Step 5 of 7 \u00b7 Receive", "duration": 50, "instruction": "Whatever arrived \u2014 even if it was faint, strange, or wordless \u2014 let it stay. Do not argue with it. Do not test it against logic yet. The meaning may unfold later. Your only job right now is to let it land."},
            {"phase": "Step 6 of 7 \u00b7 Ground", "duration": 40, "instruction": "Feel your feet on the floor. Feel the weight of your body. You have been in a receptive state \u2014 now bring yourself gently back to ordinary awareness. The message does not disappear when you open your eyes."},
            {"phase": "Step 7 of 7 \u00b7 Record", "duration": 35, "instruction": "Open your eyes. Write down whatever arrived, even if it does not make sense yet. One sentence is enough. Over time, these notes become a map of what your guidance is pointing toward."},
            {"phase": "Complete", "duration": 0, "instruction": "The practice is done. What came through was not your imagination producing content \u2014 it was your system receiving a signal it already knew how to recognize. That recognition is the beginning of everything Junko teaches about.", "final": True},
        ],
        "cta_practice_label": "Start The Receiving Practice",
        "cta_regulation_text": "Receive First, Then Understand",
        "cta_body": "Your soul already knows what it is being shown. Stop trying to figure it out and start receiving. Do the guided practice now, then notice what arrived.",
        "micro_action": "72-hour micro-action: Each evening this week, write one sentence capturing any guidance or knowing that arrived during the day without you trying to produce it.",
    },
}

# ── PILLAR MAPPING ────────────────────────────────────────────────────────────
TOPIC_TO_PILLAR = {
    "climate": "Planet",
    "environment": "Planet",
    "mental_health": "Mind",
    "loneliness": "Mind",
    "social_media": "Mind",
    "education": "Work & Future",
    "labor": "Work & Future",
    "inequality": "Work & Future",
    "economic": "Work & Future",
    "peace": "Peace & Conflict",
    "conflict": "Peace & Conflict",
    "interfaith": "Peace & Conflict",
    "spirituality": "Meaning",
    "meaning": "Meaning",
}

# ── SDG DATABASE ──────────────────────────────────────────────────────────────
SDG_DB = {
    "3": {"name": "Good Health & Well-Being", "target": "3.4", "color": "#4C9F38"},
    "4": {"name": "Quality Education", "target": "4.7", "color": "#C5192D"},
    "10": {"name": "Reduced Inequalities", "target": "10.3", "color": "#DD1367"},
    "13": {"name": "Climate Action", "target": "13.3", "color": "#3F7E44"},
    "16": {"name": "Peace, Justice & Strong Institutions", "target": "16.7", "color": "#00689D"},
}

# ── ARTICLE TYPE MAPPING ─────────────────────────────────────────────────────
TEMPLATE_TO_TYPE = {
    "hard_news_spiritual_response": "Hard News + Insight + Action",
    "explainer": "Explainer + Context",
    "commentary": "Commentary",
    "interfaith": "Interfaith Dialogue",
    "youth_feature": "Youth Feature",
}

# ── HERO IMAGE CATEGORY MAP ───────────────────────────────────────────────────
# Maps topic/template keywords → custom-made Pearl News hero PNG filename.
# Files live in pearl_news/del_intake_pics/ relative to repo root.
# The assembler will embed a base64 data-URI for standalone HTML,
# and the WP posting script will upload as featured image.
HERO_IMAGE_MAP = {
    # By topic keyword
    "climate": "climate_watch.png",
    "environment": "climate_watch.png",
    "mental_health": "youth_impact.png",
    "loneliness": "youth_impact.png",
    "social_media": "youth_impact.png",
    "education": "education_and_identity.png",
    "identity": "education_and_identity.png",
    "labor": "cultural_insight.png",
    "inequality": "cultural_insight.png",
    "economic": "cultural_insight.png",
    "peace": "peace_and_governance.png",
    "conflict": "peace_and_governance.png",
    "governance": "peace_and_governance.png",
    "interfaith": "interfath_dialogue.png",
    "dialogue": "interfath_dialogue.png",
    "sdg": "sdg_brief.png",
    "global": "global_update.png",
}


def _resolve_hero_image(topic: str, template: str, repo_root: Path | None = None) -> Path | None:
    """
    Resolve custom hero PNG path from topic or template keywords.
    Returns Path to the image file, or None if not found.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    pics_dir = repo_root / "pearl_news" / "del_intake_pics"
    if not pics_dir.is_dir():
        return None

    topic_lower = topic.lower().replace(" ", "_")
    # Check topic keywords first
    for key, filename in HERO_IMAGE_MAP.items():
        if key in topic_lower:
            img = pics_dir / filename
            if img.exists():
                return img

    # Check template keywords
    template_lower = template.lower()
    for key, filename in HERO_IMAGE_MAP.items():
        if key in template_lower:
            img = pics_dir / filename
            if img.exists():
                return img

    # Fallback to global_update
    fallback = pics_dir / "global_update.png"
    return fallback if fallback.exists() else None


def _image_to_data_uri(img_path: Path) -> str:
    """Convert local image to base64 data URI for standalone HTML."""
    import base64
    data = img_path.read_bytes()
    suffix = img_path.suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(
        suffix.lstrip("."), "image/png"
    )
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _esc(text: str) -> str:
    """HTML-escape text."""
    return html.escape(text)


def _paragraphs_to_html(text: str, css_class: str = "") -> str:
    """Split text on double newlines into <p> tags."""
    cls = f' class="{css_class}"' if css_class else ""
    paras = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    return "\n".join(f"    <p{cls}>{_esc(p)}</p>" for p in paras)


def _split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraph strings."""
    return [p.strip() for p in text.strip().split("\n\n") if p.strip()]


def _infer_pillar(topic: str) -> str:
    """Map topic to nav pillar."""
    topic_lower = topic.lower().replace(" ", "_")
    for key, pillar in TOPIC_TO_PILLAR.items():
        if key in topic_lower:
            return pillar
    return "Mind"  # default


def _build_exercise_steps_js(steps: list[dict]) -> str:
    """Generate JavaScript steps array."""
    lines = []
    for s in steps:
        parts = [f'phase: "{_esc(s["phase"])}"', f'duration: {s["duration"]}']
        # Escape instruction for JS string
        instr = s["instruction"].replace("\\", "\\\\").replace('"', '\\"')
        parts.append(f'instruction: "{instr}"')
        if s.get("breathe"):
            parts.append("breathe: true")
        if s.get("final"):
            parts.append("final: true")
        lines.append("  { " + ", ".join(parts) + " }")
    return "[\n" + ",\n".join(lines) + "\n]"


def _hero_img_tag(url: str, alt: str) -> str:
    if not url:
        return ""
    return (
        '<img class="hero-image" id="heroImg" src="' + _esc(url)
        + '" alt="' + _esc(alt)
        + '" onerror="document.getElementById(\'heroFallback\').style.display=\'flex\'; this.style.display=\'none\';">'
    )


def _hero_fallback_style(url: str) -> str:
    if url:
        return 'style="display:none;"'
    return ""


def extract_loop_sequence(youth_somatic_text: str) -> str:
    """
    Extract the LOOP_SEQUENCE label from youth_somatic output.
    Returns the loop string (e.g. "the read. the tighten. the scroll. the return.")
    and strips the label line from the source text.
    """
    for line in youth_somatic_text.split("\n"):
        stripped = line.strip()
        if stripped.upper().startswith("LOOP_SEQUENCE:"):
            return stripped.split(":", 1)[1].strip().strip('"').strip("'")
    # Fallback: derive from the somatic text itself (last sentence fragments)
    return ""


def _strip_loop_sequence_label(text: str) -> str:
    """Remove the LOOP_SEQUENCE: label line from rendered output."""
    lines = text.split("\n")
    cleaned = [l for l in lines if not l.strip().upper().startswith("LOOP_SEQUENCE:")]
    return "\n".join(cleaned).strip()


def _is_14_slot_format(slots: dict) -> bool:
    """Detect if slots use the new 14-prompt architecture."""
    return "headline_layer_1" in slots


def _parse_14_slot_format(slots: dict) -> dict:
    """
    Parse the 14-slot architecture into the template variables used by the assembler.
    This pre-split approach avoids the guessing that led to empty turnaround blocks.

    Returns dict with keys: h1, h2, hook_para, news_peg_paras, body_paras,
    turnaround_paras, teacher_teaching, teacher_practice, forward_paras, etc.
    """
    h1 = (slots.get("headline_layer_1") or "").strip().rstrip(".")
    h2 = (slots.get("headline_layer_2") or "").strip()
    if h2 and not h2.endswith("."):
        h2 += "."

    # Hook combines personal and big picture
    hook_personal = (slots.get("hook_personal") or "").strip()
    hook_big_picture = (slots.get("hook_big_picture") or "").strip()
    hook_para = hook_personal or hook_big_picture or ""

    # News peg section
    news_peg = (slots.get("news_peg") or "").strip()
    teacher_intro = (slots.get("teacher_intro") or "").strip()
    news_peg_paras = [p for p in [news_peg, teacher_intro] if p]

    # Body experience sections — extract loop_sequence for mirror rule
    youth_somatic_raw = (slots.get("youth_somatic") or "").strip()
    loop_sequence = extract_loop_sequence(youth_somatic_raw)
    youth_somatic = _strip_loop_sequence_label(youth_somatic_raw)
    # Pass loop_sequence forward so teacher_witness can use it
    slots["loop_sequence"] = loop_sequence
    teacher_witness = (slots.get("teacher_witness") or "").strip()
    body_data = (slots.get("body_data") or "").strip()
    body_paras = [p for p in [youth_somatic, teacher_witness, body_data] if p]

    # Turnaround + bridge (kept separate for header placement)
    turnaround = (slots.get("turnaround") or "").strip()
    bridge = (slots.get("bridge") or "").strip()
    turnaround_paras = _split_into_paragraphs(turnaround) if turnaround else []
    bridge_paras = [bridge] if bridge else []

    # Teacher perspective (split into teaching + practice)
    teacher_perspective = (slots.get("teacher_perspective") or "").strip()
    teacher_perspective_paras = _split_into_paragraphs(teacher_perspective)
    teacher_teaching = teacher_perspective_paras[:max(1, len(teacher_perspective_paras) - 1)]

    # Practice announcement
    practice_announce = (slots.get("practice_announce") or "").strip()
    teacher_practice = [practice_announce] if practice_announce else []

    # Forward look
    forward_look = (slots.get("forward_look") or "").strip()
    forward_paras = _split_into_paragraphs(forward_look)

    return {
        "h1": h1,
        "h2": h2,
        "hook_para": hook_para,
        "news_peg_paras": news_peg_paras,
        "body_paras": body_paras,
        "turnaround_paras": turnaround_paras,
        "bridge_paras": bridge_paras,
        "teacher_teaching": teacher_teaching,
        "teacher_practice": teacher_practice,
        "forward_paras": forward_paras,
    }


_HARD_NEWS_FRAGMENT_BY_SLOT = {
    "hook_personal": "hook",
    "hook_big_picture": "hook",
    "news_peg": "news",
    "teacher_intro": "intro",
    "youth_somatic": "youth",
    "teacher_witness": "witness",
    "body_data": "evidence",
    "turnaround": "turnaround",
    "bridge": "bridge",
    "teacher_perspective": "perspective",
    "practice_announce": "practice",
    "forward_look": "forward",
    "sdg_un_tie": "forward",
}

_DEFAULT_HARD_NEWS_FRAGMENT_ORDER = [
    "hook",
    "youth",
    "news",
    "intro",
    "witness",
    "evidence",
    "turnaround",
    "bridge",
    "perspective",
    "practice",
    "forward",
]


def _resolve_hard_news_fragment_order(meta: dict) -> list[str]:
    ordered_sections = meta.get("_deterministic_article_plan") or []
    fragment_order: list[str] = []
    seen: set[str] = set()
    for entry in ordered_sections:
        if not isinstance(entry, dict):
            continue
        slot = str(entry.get("slot") or "").strip()
        fragment = _HARD_NEWS_FRAGMENT_BY_SLOT.get(slot)
        if fragment and fragment not in seen:
            seen.add(fragment)
            fragment_order.append(fragment)
    for fragment in _DEFAULT_HARD_NEWS_FRAGMENT_ORDER:
        if fragment not in seen:
            fragment_order.append(fragment)
    return fragment_order


def assemble_v52(article_json: dict, metadata: dict | None = None, *, standalone: bool = True) -> str:
    """
    Assemble a full v5.2 HTML article from slot JSON + metadata.

    Parameters
    ----------
    article_json : dict
        Must contain 'slots' dict with keys: headline, news_summary,
        youth_impact, teacher_perspective, sdg_un_tie, forward_look
    metadata : dict, optional
        Override/supplement fields: teacher, topic, sdg, pillar,
        template, news_event, sources, hero_image_url, hero_fallback_text

    Returns
    -------
    str : Complete v5.2 HTML document
    """
    meta = {**article_json, **(metadata or {})}
    slots = article_json.get("slots", article_json.get("article", {}))

    # ── Extract metadata ──
    # Support both flat "teacher" key and nested "teacher_used.teacher_id"
    _raw_teacher = meta.get("teacher") or (meta.get("teacher_used") or {}).get("teacher_id") or "maat"
    teacher_id = _raw_teacher.lower().replace(" ", "_")
    teacher = TEACHER_DB.get(teacher_id, TEACHER_DB["maat"])
    teacher_name = teacher_id.replace("_", " ").title()  # always prettify

    topic = meta.get("topic", "general")
    pillar = meta.get("pillar") or _infer_pillar(topic)
    sdg_num = str(meta.get("sdg", "3"))
    sdg = SDG_DB.get(sdg_num, SDG_DB["3"])
    template = meta.get("template", "hard_news_spiritual_response")
    article_type = TEMPLATE_TO_TYPE.get(template, "Hard News + Insight + Action")
    news_event = meta.get("news_event", "")
    date_str = meta.get("date", "March 10, 2026")
    layout = meta.get("layout", "default")  # "default" | "scroll_story" | "dock"

    # ── Parse slots ──
    # Detect 14-slot architecture vs 6-slot legacy format
    if _is_14_slot_format(slots):
        # New 14-prompt architecture: pre-split slots
        parsed = _parse_14_slot_format(slots)
        h1 = parsed["h1"]
        h2 = parsed["h2"]
        hook_para = parsed["hook_para"]
        news_peg_paras = parsed["news_peg_paras"]
        body_paras = parsed["body_paras"]
        turnaround_paras = parsed["turnaround_paras"]
        bridge_paras = parsed["bridge_paras"]
        teacher_teaching = parsed["teacher_teaching"]
        teacher_practice = parsed["teacher_practice"]
        forward_paras = parsed["forward_paras"]
        sdg_content = slots.get("sdg_un_tie", "")
        # Reconstruct headline_raw for alt text
        headline_raw = f"{h1}. {h2}".strip()
    else:
        # Legacy 6-slot format: assembler guesses split points
        headline_raw = slots.get("headline", "Untitled")
        news_summary = slots.get("news_summary", "")
        youth_impact = slots.get("youth_impact", "")
        teacher_perspective = slots.get("teacher_perspective", "")
        sdg_un_tie = slots.get("sdg_un_tie", "")
        forward_look = slots.get("forward_look", "")

        # ── Split headline into two layers ──
        # Try to split on semantic punctuation, then fall back to clause boundary
        if " — " in headline_raw:
            h1, h2 = headline_raw.split(" — ", 1)
        elif " – " in headline_raw:
            h1, h2 = headline_raw.split(" – ", 1)
        elif " - " in headline_raw:
            h1, h2 = headline_raw.split(" - ", 1)
        elif ": " in headline_raw:
            h1, h2 = headline_raw.split(": ", 1)
        elif ", " in headline_raw:
            # Split at last comma to keep layer 1 as complete thought
            idx = headline_raw.rfind(", ")
            h1, h2 = headline_raw[:idx], headline_raw[idx + 2:]
        else:
            # Split at roughly halfway on a word boundary
            words = headline_raw.split()
            mid = len(words) // 2
            h1 = " ".join(words[:mid])
            h2 = " ".join(words[mid:])
        h1 = h1.strip().rstrip(".")
        h2 = h2.strip()
        if not h2.endswith("."):
            h2 += "."

        # ── Parse news_summary into hook + news peg ──
        news_paras = _split_into_paragraphs(news_summary)
        hook_para = news_paras[0] if news_paras else ""
        news_peg_paras = news_paras[1:] if len(news_paras) > 1 else []

        # ── Parse youth_impact into body sections ──
        youth_paras = _split_into_paragraphs(youth_impact)
        # First para(s) = body experience, last = turnaround (if starts with action words)
        body_paras = youth_paras[:max(1, len(youth_paras) - 1)]
        turnaround_paras = youth_paras[-1:] if len(youth_paras) > 1 else []
        bridge_paras = []  # legacy format has no separate bridge

        # ── Parse teacher_perspective into gold block + practice ──
        teacher_paras = _split_into_paragraphs(teacher_perspective)
        # Split: first 2 paras = teacher teaching, last para = practice instruction
        teacher_teaching = teacher_paras[:max(1, len(teacher_paras) - 1)]
        teacher_practice = teacher_paras[-1:] if len(teacher_paras) > 1 else []

        # ── Parse sdg_un_tie ──
        sdg_paras = _split_into_paragraphs(sdg_un_tie)
        sdg_content = sdg_paras[0] if sdg_paras else ""

        # ── Parse forward_look ──
        forward_paras = _split_into_paragraphs(forward_look)

    # ── Extract sources from news_event, slots, or metadata ──
    sources = meta.get("sources", [])
    if not sources:
        import re as _re
        # Scan all available text for recognisable org names (word-boundary match)
        # Build scan text based on available slots (14-slot or 6-slot format)
        scan_parts = [news_event, str(sdg_content)]
        if _is_14_slot_format(slots):
            # 14-slot format
            for key in ["hook_personal", "hook_big_picture", "news_peg", "teacher_intro",
                       "youth_somatic", "teacher_witness", "body_data", "turnaround",
                       "bridge", "teacher_perspective", "practice_announce", "forward_look"]:
                if key in slots:
                    scan_parts.append(str(slots[key]))
        else:
            # 6-slot format
            scan_parts.extend([news_summary, youth_impact, teacher_perspective, forward_look])
        scan_text = " ".join(scan_parts)
        for org in ["World Health Organization", "World Meteorological Organization",
                     "The Lancet", "UNICEF", "UNESCO", "Sapien Labs",
                     "Surgeon General", "Economic Policy Institute", "UN Women",
                     "UNFCCC", "YOUNGO", "GlobeScan", "Fridays for Future",
                     "UN Human Rights", "UNDP", "UNHCR"]:
            if _re.search(r'\b' + _re.escape(org) + r'\b', scan_text, _re.IGNORECASE):
                sources.append(org)

    # ── Hero image (3-tier: external URL → custom PNG → gradient fallback) ──
    hero_url = meta.get("hero_image_url", "")
    hero_local_path: Path | None = None
    if not hero_url:
        # Tier 2: resolve custom Pearl News hero PNG by topic/template
        hero_local_path = _resolve_hero_image(topic, template)
        if hero_local_path:
            # Standalone preview HTML may embed the local hero. Compact render paths should not.
            if standalone:
                hero_url = _image_to_data_uri(hero_local_path)
            else:
                hero_url = ""
    hero_alt = meta.get("hero_alt", f"Illustration for: {headline_raw}")
    hero_caption = meta.get("hero_caption", "Image: Pearl News" if hero_local_path else "Image: Source")
    hero_fallback_num = meta.get("hero_fallback_text", sdg_num if sdg_num != "3" else "")
    hero_fallback_label = meta.get("hero_fallback_label", topic.replace("_", " ").title())

    # ── Poll question ──
    poll_question = meta.get("poll_question", f'When you read this news, what was your first response?')
    poll_options = meta.get("poll_options", [
        "My chest tightened",
        "I scrolled past",
        "I felt nothing",
        "I texted someone",
    ])

    # ── Co-creation prompt ──
    cocreation = meta.get("cocreation_prompt",
        f"What does this news do to your daily life? Name one specific moment. "
        f"Your input shapes our reporting and the questions we raise at UNA-USA meetings.")

    # ── Section headers ──
    # 14-slot articles may include custom section_headers
    sec_h = meta.get("section_headers", {})
    hook_header = sec_h.get("hook", meta.get("hook_header", "The Weight of It"))
    news_peg_header = sec_h.get("news_peg", meta.get("news_peg_header", "The Number"))
    body_header = sec_h.get("youth_somatic", meta.get("body_header", "What It Looks Like"))
    turnaround_header = meta.get("turnaround_header", "Already Moving")
    teacher_header = sec_h.get("bridge", meta.get("teacher_header", "What the Data Skips"))
    gold_block_header = sec_h.get("teacher_perspective_block",
        meta.get("gold_block_header", f"What {teacher_name} Sees"))
    sage_body_header = sec_h.get("body_data", meta.get("sage_body_header", "How Others Experience It"))
    practice_header = "The Practice"
    forward_header = meta.get("forward_header", "There's a Door")
    data_chain_header = "Your Voice Has Power"

    # ── Build exercise step dots ──
    total_steps = len(teacher["exercise_steps"])
    step_dots = "\n".join(f'        <div class="step-dot" data-step="{i}"></div>'
                          for i in range(total_steps))

    # ── Pillar nav ──
    pillars = ["Planet", "Mind", "Work & Future", "Peace & Conflict", "Meaning"]
    nav_parts = []
    for p in pillars:
        cls = ' class="active"' if p == pillar else ""
        nav_parts.append(f'  <a href="#{cls}">{p}</a>')
    nav_links = "\n".join(nav_parts)

    # ── Authority sources ──
    authority_sources = "<br>\n        ".join(_esc(s) for s in sources) if sources else "Multiple sources"

    # ── Reporting attribution ──
    attribution_sources = "\n".join(
        f'      <span class="attr-source">{_esc(s)}</span>'
        for s in sources
    ) if sources else '      <span class="attr-source">Multiple sources</span>'

    # ── Build body paragraphs ──
    def _paras(texts: list[str], cls: str = "") -> str:
        c = f' class="{cls}"' if cls else ""
        return "\n".join(f"      <p{c}>{_esc(t)}</p>" for t in texts)

    def _block_paras(texts: list[str]) -> str:
        return "\n".join(f"      <p>{_esc(t)}</p>" for t in texts)

    # ── Italic hints ──
    hint_after_turnaround = meta.get("hint_after_turnaround",
        f"The data and the feeling are happening in the same body, at the same time.")
    # For 14-slot: practice_announce may contain the shift sentence as last paragraph
    if _is_14_slot_format(slots):
        pa = (slots.get("practice_announce") or "").strip()
        pa_paras = [p.strip() for p in pa.split("\n\n") if p.strip()]
        if len(pa_paras) >= 2:
            # Last paragraph is the shift hint
            hint_after_practice = pa_paras[-1]
            # Update teacher_practice to exclude the hint
            teacher_practice = pa_paras[:-1]
        else:
            hint_after_practice = meta.get("hint_after_practice",
                f"{teacher_name} has seen this shift in practice rooms. It may help you as well.")
    else:
        hint_after_practice = meta.get("hint_after_practice",
            f"{teacher_name} has seen this shift in practice rooms. It may help you as well.")

    # ── PRE-COMPUTE CONDITIONAL BLOCKS ──
    # Sage block (body data): show only if there's content beyond what hook-2 already rendered
    _sage_body_content = body_paras[2:] if _is_14_slot_format(slots) and len(body_paras) > 2 else body_paras[1:]
    _sage_body_html = ''
    if _sage_body_content:
        _sage_body_html = (
            f'<div class="block-sage">\n'
            f'      <div class="block-header">{_esc(sage_body_header)}</div>\n'
            f'      {_block_paras(_sage_body_content)}\n'
            f'    </div>'
        )

    # Gold block (teacher perspective): show only if there's content beyond the first paragraph
    _gold_block_html = ''
    if len(teacher_teaching) > 1:
        _gold_block_html = (
            f'<div class="block-gold">\n'
            f'      <div class="block-header">{_esc(gold_block_header)}</div>\n'
            f'      {_block_paras(teacher_teaching[1:])}\n'
            f'    </div>'
        )

    # ── Layout CSS selection ──
    _layout_css = ""
    if layout == "scroll_story":
        _layout_css = CSS_SCROLL_STORY
    elif layout == "dock":
        _layout_css = CSS_DOCK

    # ── Build inline interstitial HTML for scroll_story layout ──
    _inline_exercise_html = ""
    _inline_cta_html = ""
    _inline_poll_html = ""
    _inline_cocreation_html = ""
    _inline_sdg_html = ""
    if layout == "scroll_story":
        _inline_exercise_html = f'''
    <div class="interstitial interstitial-exercise" id="exerciseCard">
      <h3>Practice · {_esc(teacher["practice_name"])} · {_esc(teacher["practice_duration"])}</h3>
      <p style="color: rgba(255,255,255,0.65); font-size: 13px;">{_esc(teacher["practice_description"])}</p>
      <div class="exercise-display" id="exerciseDisplay">
        <div class="exercise-phase" id="exercisePhase">Ready when you are</div>
        <div class="exercise-timer-num" id="exerciseTimer">{teacher["practice_duration"].replace(" min", ":00")}</div>
        <div class="exercise-instruction" id="exerciseInstruction">Tap begin to start a guided {_esc(teacher["practice_duration"])} practice.</div>
      </div>
      <button class="exercise-btn" id="exerciseBtn" onclick="toggleExercise()">Begin</button>
      <div class="exercise-progress" id="exerciseProgress">{step_dots}</div>
    </div>'''
        _inline_cta_html = f'''
    <div class="interstitial interstitial-cta">
      <h3>Free Tools</h3>
      <div class="cta-title">{_esc(teacher["cta_regulation_text"])}</div>
      <div class="cta-body">{_esc(teacher["cta_body"])}</div>
      <a href="https://phoenixprotocolbooks.com/free/regulation-tool-breath-v1" class="cta-primary">{_esc(teacher["cta_practice_label"])}</a>
      <a href="https://phoenixprotocolbooks.com/free/companion-core-v2" class="cta-secondary">Get The Companion Freebie Pack</a>
      <div class="cta-micro-action">{_esc(teacher["micro_action"])}</div>
    </div>'''
        _inline_poll_html = f'''
    <div class="interstitial interstitial-poll">
      <h3>Hot Take Poll</h3>
      <p style="margin-bottom: 12px; font-family: var(--font-sans); font-size: 14px; color: var(--text-secondary);">{_esc(poll_question)}</p>
      {"".join(f'<div class="poll-option"><span>{_esc(opt)}</span></div>' + chr(10) + "      " for opt in poll_options)}
      <p style="font-size: 12px; color: var(--text-muted); margin-top: 8px; font-family: var(--font-sans);">Results after you vote. Responses feed into Pearl News reporting.</p>
    </div>'''
        _inline_sdg_html = f'''
    <div class="interstitial interstitial-sdg">
      <h3>SDG Connection</h3>
      <p><span class="sdg-badge">SDG {_esc(sdg_num)} · {_esc(sdg["name"])} · Target {_esc(sdg["target"])}</span></p>
      <p style="margin-top: 10px; font-size: 14px;">{_esc(sdg_content)}</p>
      <p class="disclaimer">Pearl News is an independent nonprofit. We are not affiliated with the United Nations.</p>
    </div>'''

    # ── Build dock sidebar HTML ──
    _dock_sidebar_html = ""
    if layout == "dock":
        _section_nav_items = []
        _nav_sections = [
            ("sec-hook", hook_header or "The Hook"),
            ("sec-news", news_peg_header or "The Story"),
            ("sec-body", sage_body_header or "The Evidence"),
            ("sec-turnaround", turnaround_header or "What's Changing"),
            ("sec-bridge", teacher_header or "The Connection"),
            ("sec-perspective", gold_block_header or "Perspective"),
            ("sec-practice", practice_header or "The Practice"),
            ("sec-forward", forward_header or "What's Next"),
        ]
        for sec_id, sec_label in _nav_sections:
            _section_nav_items.append(f'        <a class="dock-nav-item" href="#{sec_id}">{_esc(sec_label)}</a>')
        _dock_nav = "\n".join(_section_nav_items)

        _dock_sidebar_html = f'''
  <div class="sidebar-dock">
    <div class="dock-nav">
{_dock_nav}
    </div>
    <div class="dock-exercise" id="exerciseCard">
      <h3>Practice · {_esc(teacher["practice_duration"])}</h3>
      <div class="exercise-display" id="exerciseDisplay">
        <div class="exercise-phase" id="exercisePhase">Ready</div>
        <div class="exercise-timer-num" id="exerciseTimer">{teacher["practice_duration"].replace(" min", ":00")}</div>
        <div class="exercise-instruction" id="exerciseInstruction">Tap begin to start</div>
      </div>
      <button class="exercise-btn" id="exerciseBtn" onclick="toggleExercise()">Begin</button>
      <div class="exercise-progress" id="exerciseProgress">{step_dots}</div>
    </div>
    <div class="dock-cta">
      <h3>Free Tools</h3>
      <a href="https://phoenixprotocolbooks.com/free/regulation-tool-breath-v1" class="cta-primary">{_esc(teacher["cta_practice_label"])}</a>
      <a href="https://phoenixprotocolbooks.com/free/companion-core-v2" class="cta-secondary">Companion Freebie Pack</a>
    </div>
    <div class="dock-sdg">
      <h3>SDG {_esc(sdg_num)}</h3>
      <p><span class="sdg-badge">SDG {_esc(sdg_num)} · {_esc(sdg["name"])}</span></p>
      <p class="disclaimer">Pearl News is not affiliated with the United Nations.</p>
    </div>
  </div>'''

    _hard_news_fragment_order = _DEFAULT_HARD_NEWS_FRAGMENT_ORDER
    if template == "hard_news_spiritual_response" and _is_14_slot_format(slots):
        _hard_news_fragment_order = _resolve_hard_news_fragment_order(meta)

    _hard_news_fragment_html = {
        "hook": (
            f'    <!-- HOOK -->\n'
            f'    <div id="sec-hook" class="section-header">{_esc(hook_header)}</div>\n'
            f'    <p class="hook-1">{_esc(hook_para)}</p>\n'
        ) if hook_para else "",
        "news": (
            f'    <!-- NEWS PEG -->\n'
            f'    <div id="sec-news" class="section-header">{_esc(news_peg_header)}</div>\n'
            f'{_paras(news_peg_paras[:1])}\n'
        ) if news_peg_paras[:1] else "",
        "intro": (
            f'    <!-- TEACHER INTRO -->\n'
            f'{_paras(news_peg_paras[1:])}\n'
        ) if news_peg_paras[1:] else "",
        "youth": (
            f'    <!-- YOUTH EXPERIENCE -->\n'
            f'    <div id="sec-body" class="section-header">{_esc(body_header)}</div>\n'
            f'{_paras(body_paras[:1], "hook-2")}\n'
        ) if body_paras[:1] else "",
        "witness": (
            f'    <!-- TEACHER WITNESS -->\n'
            f'    <p class="hook-2"><span class="teacher-read">{_esc(body_paras[1])}</span></p>\n'
        ) if _is_14_slot_format(slots) and len(body_paras) > 1 else "",
        "evidence": (
            f'    <!-- BODY DATA -->\n'
            f'{_sage_body_html}\n'
        ) if _sage_body_html else "",
        "turnaround": (
            f'    <!-- TURNAROUND -->\n'
            f'    <div id="sec-turnaround" class="block-blue">\n'
            f'      <div class="block-header">{_esc(turnaround_header)}</div>\n'
            f'      {_block_paras(turnaround_paras)}\n'
            f'    </div>\n'
            f'{_inline_exercise_html}\n'
        ) if turnaround_paras else "",
        "bridge": (
            f'    <!-- BRIDGE -->\n'
            f'    <div id="sec-bridge" class="section-header">{_esc(teacher_header)}</div>\n'
            f'{_paras(bridge_paras)}\n'
        ) if bridge_paras else "",
        "perspective": (
            f'    <!-- TEACHER PERSPECTIVE -->\n'
            f'{_paras(teacher_teaching[:1])}\n'
            f'    <div id="sec-perspective">{_gold_block_html}</div>\n'
        ) if teacher_teaching or _gold_block_html else "",
        "practice": (
            f'    <!-- PRACTICE -->\n'
            f'    <div id="sec-practice" class="block-sage">\n'
            f'      <div class="block-header">{_esc(practice_header)}</div>\n'
            f'      {_block_paras(teacher_practice)}\n'
            f'    </div>\n'
            f'    <p class="hint-italic">{_esc(hint_after_practice)}</p>\n'
            f'{_inline_cta_html}\n'
            f'{_inline_sdg_html}\n'
        ) if teacher_practice else "",
        "forward": (
            f'    <!-- FORWARD LOOK -->\n'
            f'    <div id="sec-forward" class="section-header">{_esc(forward_header)}</div>\n'
            f'{_paras(forward_paras[:1])}\n'
            f'    <div class="section-header">Take Action Now!</div>\n'
            f'{_paras(forward_paras[1:])}\n'
            f'{_inline_poll_html}\n'
        ) if forward_paras else "",
    }

    _article_sections_html = "".join(
        _hard_news_fragment_html[fragment]
        for fragment in _hard_news_fragment_order
        if _hard_news_fragment_html.get(fragment)
    )

    # ── ASSEMBLE HTML ──
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pearl News — {_esc(h1)}</title>
{CSS_BLOCK}
{_layout_css}
</head>
<body>
<!-- ═══════ PILLAR NAVIGATION ═══════ -->
<nav class="nav-pillars">
{nav_links}
</nav>
<!-- ═══════ AUTHORITY BLOCK ═══════ -->
<div class="authority-block">
  <div class="authority-inner">
    <div class="authority-left">
      <div class="authority-pillar">{_esc(pillar.upper())} <span class="article-type">· {_esc(article_type)}</span></div>
      <div class="authority-sources">
        <span class="label">Based on reporting from</span>
        {authority_sources}
      </div>
    </div>
    <div class="authority-right">
      Reported by Pearl News<br>
      For the United Spiritual Leaders Forum<br>
      {_esc(date_str)}
    </div>
  </div>
</div>
<!-- ═══════ ARTICLE + SIDEBAR ═══════ -->
<div class="article-container">
{_dock_sidebar_html}
  <div class="article-body">
    <!-- HEADLINE -->
    <div class="headline-layer-1">{_esc(h1)}.</div>
    <h1 class="headline-layer-2">{_esc(h2)}</h1>
    <!-- HERO IMAGE -->
    <div class="hero-image-wrapper">
      {_hero_img_tag(hero_url, hero_alt)}
      <div class="hero-fallback" id="heroFallback" {_hero_fallback_style(hero_url)}>
        <span>{_esc(hero_fallback_num or "·")}</span>
        <small>{_esc(hero_fallback_label)}</small>
      </div>
    </div>
    <div class="hero-image-caption">{_esc(hero_caption)}</div>
{_article_sections_html}
    <!-- READER DATA CHAIN — blue block: collective action, shared impact -->
    <div class="block-blue">
      <div class="block-header">{_esc(data_chain_header)}</div>
      <p>The poll on this page connects to that chain. Pearl News brings aggregated reader data to UNA-USA convenings and UN press briefings.</p>
      <p>Your response is not a comment. It is a data point in a set that gets presented to people deciding which questions get asked.</p>
      <p>Vote in the sidebar. Submit your take. Be part of the solution.</p>
    </div>
    <!-- REPORTING ATTRIBUTION -->
    <div class="reporting-attribution">
      <span class="attr-label">Reporting based on</span>
{attribution_sources}
    </div>
    <div class="ai-disclosure">
      Pearl Prime Enlightened Intelligence and AI was used in sourcing and summarizing news in this article.
    </div>
  </div>
  <!-- ─── SIDEBAR ─── -->
  <div class="sidebar">
    <!-- GUIDED EXERCISE -->
    <div class="sidebar-card exercise-card" id="exerciseCard">
      <h3>Practice · {_esc(teacher["practice_name"])} · {_esc(teacher["practice_duration"])}</h3>
      <p style="color: rgba(255,255,255,0.65); font-size: 13px;">{_esc(teacher["practice_description"])}</p>
      <div class="exercise-display" id="exerciseDisplay">
        <div class="exercise-phase" id="exercisePhase">Ready when you are</div>
        <div class="exercise-timer-num" id="exerciseTimer">{teacher["practice_duration"].replace(" min", ":00")}</div>
        <div class="exercise-instruction" id="exerciseInstruction">Tap begin to start a guided {_esc(teacher["practice_duration"])} practice. Each step will advance automatically.</div>
      </div>
      <button class="exercise-btn" id="exerciseBtn" onclick="toggleExercise()">Begin</button>
      <div class="exercise-progress" id="exerciseProgress">
{step_dots}
      </div>
    </div>
    <!-- CTA -->
    <div class="sidebar-card cta-card">
      <h3>Free Tools</h3>
      <div class="cta-title">{_esc(teacher["cta_regulation_text"])}</div>
      <div class="cta-body">{_esc(teacher["cta_body"])}</div>
      <a href="https://phoenixprotocolbooks.com/free/regulation-tool-breath-v1" class="cta-primary">{_esc(teacher["cta_practice_label"])}</a>
      <a href="https://phoenixprotocolbooks.com/free/companion-core-v2" class="cta-secondary">Get The Companion Freebie Pack</a>
      <div class="cta-micro-action">{_esc(teacher["micro_action"])}</div>
    </div>
    <!-- SDG DETAIL -->
    <div class="sidebar-card">
      <h3>SDG Connection</h3>
      <p><span class="sdg-badge">SDG {_esc(sdg_num)} · {_esc(sdg["name"])} · Target {_esc(sdg["target"])}</span></p>
      <p style="margin-top: 10px;">{_esc(sdg_content)}</p>
      <p class="disclaimer">Pearl News is an independent nonprofit. We are not affiliated with the United Nations.</p>
    </div>
    <!-- POLL -->
    <div class="sidebar-card">
      <h3>Hot Take Poll</h3>
      <p style="margin-bottom: 12px; font-family: var(--font-sans); font-size: 13px; color: var(--text-secondary);">{_esc(poll_question)}</p>
      {"".join(f'<div class="poll-option"><span>{_esc(opt)}</span></div>' + chr(10) + "      " for opt in poll_options)}
      <p style="font-size: 11px; color: var(--text-muted); margin-top: 8px; font-family: var(--font-sans);">Results after you vote. Responses feed into Pearl News reporting and UNA-USA policy briefs.</p>
    </div>
    <!-- CO-CREATION -->
    <div class="sidebar-card">
      <h3>Your Take → Editorial Input</h3>
      <p style="margin-bottom: 12px; font-size: 13px;">{_esc(cocreation)}</p>
      <textarea class="cocreation-input" placeholder="Type here..."></textarea>
      <p style="font-size: 11px; color: var(--text-muted); margin-top: 8px; font-family: var(--font-sans);">Your take is editorial input — not a comment. It becomes source material.</p>
    </div>
  </div>
</div>
<script>
const steps = {_build_exercise_steps_js(teacher["exercise_steps"])};
let currentStep = -1, timer = null, secondsLeft = {sum(s["duration"] for s in teacher["exercise_steps"])};
let breathInterval = null, stepTimeout = null, paused = false;
let stepTimeRemaining = 0, started = false;
function updateTimerDisplay() {{
  const m = Math.floor(secondsLeft / 60), s = secondsLeft % 60;
  document.getElementById('exerciseTimer').textContent = m + ':' + (s < 10 ? '0' : '') + s;
}}
function updateProgress(stepIndex) {{
  document.querySelectorAll('.step-dot').forEach((dot, i) => {{
    dot.classList.remove('active', 'done');
    if (i < stepIndex) dot.classList.add('done');
    if (i === stepIndex) dot.classList.add('active');
  }});
}}
function showBreathGuide(container) {{
  if (breathInterval) clearInterval(breathInterval);
  const guide = document.createElement('div');
  guide.id = 'breathGuide';
  guide.style.cssText = 'font-family:var(--font-sans);font-size:24px;font-weight:300;color:rgba(255,255,255,0.9);margin-top:12px;transition:opacity 0.5s;';
  container.appendChild(guide);
  let inhaling = true, count = 0;
  guide.textContent = 'Inhale...';
  breathInterval = setInterval(() => {{
    if (paused) return;
    count++;
    if (inhaling && count >= 4) {{ inhaling = false; count = 0; guide.textContent = 'Exhale slowly...'; guide.style.opacity = '0.6'; }}
    else if (!inhaling && count >= 8) {{ inhaling = true; count = 0; guide.textContent = 'Inhale...'; guide.style.opacity = '1'; }}
  }}, 1000);
}}
function advanceStep() {{
  currentStep++;
  if (breathInterval) {{ clearInterval(breathInterval); breathInterval = null; }}
  if (stepTimeout) {{ clearTimeout(stepTimeout); stepTimeout = null; }}
  const step = steps[currentStep];
  if (!step) return;
  document.getElementById('exercisePhase').textContent = step.phase;
  document.getElementById('exerciseInstruction').textContent = step.instruction;
  updateProgress(currentStep);
  const oldGuide = document.getElementById('breathGuide');
  if (oldGuide) oldGuide.remove();
  if (step.final) {{
    document.getElementById('exerciseTimer').textContent = '✓';
    document.getElementById('exerciseBtn').textContent = 'Done';
    document.getElementById('exerciseBtn').disabled = true;
    updateProgress(steps.length);
    if (timer) clearInterval(timer);
    started = false; return;
  }}
  if (step.breathe) showBreathGuide(document.getElementById('exerciseDisplay'));
  stepTimeRemaining = step.duration * 1000;
  stepTimeout = setTimeout(() => {{ if (currentStep < steps.length - 1) advanceStep(); }}, stepTimeRemaining);
}}
function pauseExercise() {{
  paused = true;
  if (timer) {{ clearInterval(timer); timer = null; }}
  if (stepTimeout) {{ clearTimeout(stepTimeout); stepTimeout = null; }}
  document.getElementById('exerciseBtn').textContent = 'Resume';
  document.getElementById('exercisePhase').textContent += ' (paused)';
}}
function resumeExercise() {{
  paused = false;
  timer = setInterval(() => {{ if (paused) return; secondsLeft--; if (secondsLeft <= 0) {{ clearInterval(timer); secondsLeft = 0; }} updateTimerDisplay(); }}, 1000);
  if (stepTimeRemaining > 0) stepTimeout = setTimeout(() => {{ if (currentStep < steps.length - 1) advanceStep(); }}, stepTimeRemaining);
  document.getElementById('exerciseBtn').textContent = 'Pause';
  const phase = document.getElementById('exercisePhase');
  phase.textContent = phase.textContent.replace(' (paused)', '');
}}
function toggleExercise() {{
  const btn = document.getElementById('exerciseBtn');
  if (!started) {{
    started = true; paused = false; btn.textContent = 'Pause';
    secondsLeft = {sum(s["duration"] for s in teacher["exercise_steps"])}; updateTimerDisplay();
    timer = setInterval(() => {{ if (paused) return; secondsLeft--; if (secondsLeft <= 0) {{ clearInterval(timer); secondsLeft = 0; }} updateTimerDisplay(); }}, 1000);
    advanceStep();
  }} else if (paused) {{ resumeExercise(); }} else {{ pauseExercise(); }}
}}
</script>
</body>
</html>'''


# ── CSS BLOCK (extracted from v5.2 gold standard — identical across all articles) ──
CSS_BLOCK = '''<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&display=swap');
  :root {
    --un-blue: #009EDB;
    --un-blue-dark: #00629B;
    --un-blue-deep: #003F6B;
    --un-blue-light: #E8F4FD;
    --un-blue-ghost: #F4F9FD;
    --bg-primary: #FFFFFF;
    --bg-sidebar: #F7FAFC;
    --bg-authority: #00629B;
    --text-primary: #1A1A2E;
    --text-secondary: #4A5568;
    --text-muted: #8896A6;
    --accent-gold: #C59A2B;
    --accent-gold-light: #FFF8E7;
    --accent-sage: #2D6A4F;
    --accent-sage-light: #EAF5EE;
    --border-light: #E2E8F0;
    --border-blue: rgba(0,158,219,0.2);
    --font-sans: 'Inter', -apple-system, sans-serif;
    --font-serif: 'Merriweather', Georgia, serif;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: var(--bg-primary); color: var(--text-primary); font-family: var(--font-serif); line-height: 1.7; }
  .nav-pillars { display: flex; gap: 0; border-bottom: 2px solid var(--border-light); font-family: var(--font-sans); font-size: 12px; letter-spacing: 1.5px; text-transform: uppercase; max-width: 1100px; margin: 0 auto; padding: 0 24px; background: var(--bg-primary); }
  .nav-pillars a { padding: 14px 20px; color: var(--text-muted); text-decoration: none; border-bottom: 3px solid transparent; margin-bottom: -2px; transition: all 0.2s; font-weight: 500; }
  .nav-pillars a:hover { color: var(--un-blue); }
  .nav-pillars a.active { color: var(--un-blue); border-bottom-color: var(--un-blue); font-weight: 600; }
  .authority-block { background: var(--bg-authority); color: white; padding: 24px 0; }
  .authority-inner { max-width: 1100px; margin: 0 auto; padding: 0 24px; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px; }
  .authority-pillar { font-family: var(--font-sans); font-size: 13px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: white; margin-bottom: 10px; }
  .authority-pillar .article-type { font-weight: 400; opacity: 0.7; }
  .authority-sources { font-family: var(--font-sans); font-size: 12px; opacity: 0.85; line-height: 1.7; }
  .authority-sources .label { opacity: 0.65; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; display: block; margin-bottom: 2px; }
  .authority-right { font-family: var(--font-sans); font-size: 11px; text-align: right; opacity: 0.75; line-height: 1.7; }
  .article-container { display: grid; grid-template-columns: 1fr 360px; gap: 48px; max-width: 1100px; margin: 0 auto; padding: 0 24px 60px; }
  @media (max-width: 768px) { .article-container { grid-template-columns: 1fr; gap: 32px; } .sidebar { order: 2; } .nav-pillars { overflow-x: auto; flex-wrap: nowrap; } }
  .article-body { max-width: 640px; padding-top: 40px; }
  .headline-layer-1 { font-family: var(--font-serif); font-size: 32px; font-weight: 700; color: var(--text-primary); letter-spacing: 0.2px; margin-bottom: 8px; line-height: 1.25; }
  .headline-layer-2 { font-family: var(--font-sans); font-size: 20px; line-height: 1.4; font-weight: 500; color: var(--un-blue-dark); margin-bottom: 32px; }
  .hero-image-wrapper { margin-bottom: 8px; }
  .hero-image { width: 100%; border-radius: 8px; aspect-ratio: 16/9; object-fit: cover; background: var(--un-blue-light); }
  .hero-fallback { width: 100%; aspect-ratio: 16/9; border-radius: 8px; background: linear-gradient(135deg, var(--un-blue-deep) 0%, #B91C1C 50%, var(--accent-gold) 100%); display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; }
  .hero-fallback span { font-family: var(--font-serif); font-size: 64px; font-weight: 700; letter-spacing: -1px; }
  .hero-fallback small { font-family: var(--font-sans); font-size: 14px; opacity: 0.7; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }
  .hero-image-caption { font-family: var(--font-sans); font-size: 11px; color: var(--text-muted); margin-bottom: 28px; line-height: 1.5; }
  .article-body p { font-size: 17px; margin-bottom: 18px; color: var(--text-secondary); }
  .hook-1 { color: var(--text-primary); font-size: 19px; font-weight: 400; line-height: 1.6; }
  .hook-2 { color: var(--text-secondary); }
  .teacher-read { color: var(--un-blue-dark); font-weight: 500; }
  .hint-italic { color: var(--text-muted); font-style: italic; font-size: 15px; line-height: 1.6; margin-bottom: 18px; }
  .teacher-voice { border-left: 3px solid var(--un-blue); padding-left: 20px; margin: 24px 0; color: var(--text-secondary); font-style: italic; }
  .block-blue { background: var(--un-blue-light); border-left: 4px solid var(--un-blue); border-radius: 0 8px 8px 0; padding: 24px 28px; margin: 28px 0; }
  .block-blue .block-header { font-family: var(--font-sans); font-size: 13px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--un-blue-dark); margin-bottom: 12px; }
  .block-blue p { font-size: 16px !important; color: var(--text-primary) !important; margin-bottom: 10px !important; line-height: 1.6; }
  .block-blue p:last-child { margin-bottom: 0 !important; }
  .block-gold { background: var(--accent-gold-light); border-left: 4px solid var(--accent-gold); border-radius: 0 8px 8px 0; padding: 24px 28px; margin: 28px 0; }
  .block-gold .block-header { font-family: var(--font-sans); font-size: 13px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #8B6914; margin-bottom: 12px; }
  .block-gold p { font-size: 16px !important; color: #3D2E04 !important; margin-bottom: 10px !important; line-height: 1.65; }
  .block-gold p:last-child { margin-bottom: 0 !important; }
  .block-gold em { color: #6B4F12; }
  .block-sage { background: var(--accent-sage-light); border-left: 4px solid var(--accent-sage); border-radius: 0 8px 8px 0; padding: 24px 28px; margin: 28px 0; }
  .block-sage .block-header { font-family: var(--font-sans); font-size: 13px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--accent-sage); margin-bottom: 12px; }
  .block-sage p { font-size: 16px !important; color: #1B4332 !important; margin-bottom: 10px !important; line-height: 1.65; }
  .block-sage p:last-child { margin-bottom: 0 !important; }
  .section-header { font-family: var(--font-sans); font-size: 13px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--un-blue-dark); margin-top: 36px; margin-bottom: 14px; padding-bottom: 6px; border-bottom: 2px solid var(--border-blue); }
  .reporting-attribution { font-family: var(--font-sans); font-size: 12px; color: var(--text-muted); margin-top: 40px; padding-top: 24px; border-top: 2px solid var(--border-light); line-height: 1.8; }
  .reporting-attribution .attr-label { color: var(--text-secondary); font-weight: 600; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; display: block; margin-bottom: 6px; }
  .reporting-attribution .attr-source { display: block; color: var(--text-secondary); }
  .ai-disclosure { font-family: var(--font-sans); font-size: 11px; color: var(--text-muted); margin-top: 16px; }
  .sidebar { display: flex; flex-direction: column; gap: 20px; padding-top: 40px; }
  .sidebar-card { background: var(--bg-sidebar); border: 1px solid var(--border-light); border-radius: 12px; padding: 24px; }
  .sidebar-card h3 { font-family: var(--font-sans); font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: var(--un-blue-dark); margin-bottom: 14px; font-weight: 700; }
  .sidebar-card p { font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 8px; }
  .exercise-card { background: var(--un-blue-deep); color: white; border: none; }
  .exercise-card h3 { color: rgba(255,255,255,0.7); }
  .exercise-card p { color: rgba(255,255,255,0.8); }
  .exercise-display { text-align: center; padding: 32px 16px; background: rgba(255,255,255,0.08); border-radius: 12px; margin: 16px 0; min-height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: all 0.5s ease; }
  .exercise-timer-num { font-size: 48px; font-weight: 300; font-family: var(--font-sans); color: white; margin-bottom: 4px; }
  .exercise-phase { font-size: 13px; font-family: var(--font-sans); letter-spacing: 1px; text-transform: uppercase; color: rgba(255,255,255,0.6); margin-bottom: 12px; }
  .exercise-instruction { font-size: 16px; font-family: var(--font-serif); color: rgba(255,255,255,0.95); max-width: 280px; line-height: 1.5; font-style: italic; }
  .exercise-btn { display: block; width: 100%; padding: 14px; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); border-radius: 8px; color: white; font-family: var(--font-sans); font-size: 14px; font-weight: 500; letter-spacing: 0.5px; cursor: pointer; transition: all 0.2s; margin-top: 12px; }
  .exercise-btn:hover { background: rgba(255,255,255,0.25); }
  .exercise-btn:disabled { opacity: 0.4; cursor: default; }
  .exercise-progress { display: flex; gap: 4px; margin-top: 16px; }
  .exercise-progress .step-dot { flex: 1; height: 3px; background: rgba(255,255,255,0.15); border-radius: 2px; transition: background 0.3s; }
  .exercise-progress .step-dot.active { background: rgba(255,255,255,0.5); }
  .exercise-progress .step-dot.done { background: var(--un-blue); }
  .sdg-badge { display: inline-block; background: var(--un-blue); color: white; font-size: 11px; padding: 5px 12px; border-radius: 4px; font-family: var(--font-sans); font-weight: 600; letter-spacing: 0.5px; }
  .disclaimer { font-size: 11px; color: var(--text-muted); margin-top: 10px; font-style: italic; }
  .poll-option { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: white; border: 1px solid var(--border-light); border-radius: 8px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s; font-family: var(--font-sans); font-size: 13px; color: var(--text-secondary); }
  .poll-option:hover { border-color: var(--un-blue); color: var(--un-blue); }
  .cocreation-input { background: white; border: 1px solid var(--border-light); border-radius: 8px; padding: 14px; min-height: 70px; color: var(--text-muted); font-size: 14px; font-family: var(--font-sans); width: 100%; resize: vertical; outline: none; transition: border-color 0.2s; }
  .cocreation-input:focus { border-color: var(--un-blue); }
  .cta-card { background: linear-gradient(135deg, var(--un-blue-deep) 0%, var(--un-blue-dark) 100%); color: white; border: none; }
  .cta-card h3 { color: rgba(255,255,255,0.65); }
  .cta-card .cta-title { font-family: var(--font-serif); font-size: 18px; font-weight: 700; color: white; margin-bottom: 8px; line-height: 1.3; }
  .cta-card .cta-body { font-size: 13px; color: rgba(255,255,255,0.8); line-height: 1.5; margin-bottom: 16px; }
  .cta-primary { display: block; width: 100%; padding: 14px; background: white; border: none; border-radius: 8px; color: var(--un-blue-deep); font-family: var(--font-sans); font-size: 14px; font-weight: 600; letter-spacing: 0.3px; cursor: pointer; text-align: center; text-decoration: none; transition: all 0.2s; margin-bottom: 8px; }
  .cta-primary:hover { background: var(--un-blue-light); }
  .cta-secondary { display: block; width: 100%; padding: 12px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: white; font-family: var(--font-sans); font-size: 13px; font-weight: 500; cursor: pointer; text-align: center; text-decoration: none; transition: all 0.2s; }
  .cta-secondary:hover { background: rgba(255,255,255,0.22); }
  .cta-micro-action { font-family: var(--font-sans); font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 12px; line-height: 1.5; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px; }
</style>'''


# ── LAYOUT: SCROLL STORY (full-width immersive, sidebar cards become inline interstitials) ──
CSS_SCROLL_STORY = '''<style>
  /* Override: single column, no sidebar grid */
  .article-container { display: block; max-width: 720px; margin: 0 auto; padding: 0 24px 60px; }
  .article-body { max-width: 720px; padding-top: 40px; }
  .sidebar { display: none; }  /* hidden — cards rendered inline instead */

  /* Inline interstitial cards (exercise, CTA, poll, co-creation) */
  .interstitial { margin: 48px -24px; padding: 40px 32px; border-radius: 0; position: relative; }
  @media (min-width: 769px) { .interstitial { margin: 48px -60px; padding: 48px 60px; border-radius: 16px; } }
  .interstitial-exercise { background: var(--un-blue-deep); color: white; }
  .interstitial-exercise h3 { color: rgba(255,255,255,0.7); font-family: var(--font-sans); font-size: 11px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 14px; font-weight: 700; }
  .interstitial-exercise p { color: rgba(255,255,255,0.8); font-size: 14px; line-height: 1.6; margin-bottom: 8px; }
  .interstitial-cta { background: linear-gradient(135deg, var(--un-blue-deep) 0%, var(--un-blue-dark) 100%); color: white; }
  .interstitial-cta h3 { color: rgba(255,255,255,0.65); font-family: var(--font-sans); font-size: 11px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 14px; font-weight: 700; }
  .interstitial-cta .cta-title { font-family: var(--font-serif); font-size: 20px; font-weight: 700; color: white; margin-bottom: 10px; line-height: 1.3; }
  .interstitial-cta .cta-body { font-size: 14px; color: rgba(255,255,255,0.8); line-height: 1.5; margin-bottom: 16px; }
  .interstitial-poll { background: var(--un-blue-ghost); border: 1px solid var(--border-blue); }
  .interstitial-poll h3 { color: var(--un-blue-dark); font-family: var(--font-sans); font-size: 11px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 14px; font-weight: 700; }
  .interstitial-cocreation { background: var(--bg-sidebar); border: 1px solid var(--border-light); }
  .interstitial-cocreation h3 { color: var(--un-blue-dark); font-family: var(--font-sans); font-size: 11px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 14px; font-weight: 700; }
  .interstitial-sdg { background: var(--un-blue-ghost); border-left: 4px solid var(--un-blue); }

  /* Full-bleed teacher perspective */
  .block-gold-full { background: var(--accent-gold-light); margin: 48px -24px; padding: 40px 32px; }
  @media (min-width: 769px) { .block-gold-full { margin: 48px -60px; padding: 48px 60px; border-radius: 16px; } }
  .block-gold-full .block-header { font-family: var(--font-sans); font-size: 13px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #8B6914; margin-bottom: 12px; }
  .block-gold-full p { font-size: 17px !important; color: #3D2E04 !important; margin-bottom: 14px !important; line-height: 1.7; }
  .block-gold-full em { color: #6B4F12; }

  /* Section breathing room */
  .scroll-section { margin-bottom: 40px; }
  .scroll-section .section-header { margin-top: 48px; }

  /* Headline goes bigger */
  .headline-layer-1 { font-size: 38px; line-height: 1.2; }
  .headline-layer-2 { font-size: 22px; }
</style>'''


# ── LAYOUT: DOCK (left sticky sidebar with section nav + exercise dock) ──
CSS_DOCK = '''<style>
  /* Override: flip grid — sidebar left, content right */
  .article-container { display: grid; grid-template-columns: 280px 1fr; gap: 40px; max-width: 1100px; margin: 0 auto; padding: 0 24px 60px; }
  @media (max-width: 768px) { .article-container { grid-template-columns: 1fr; gap: 32px; } .sidebar-dock { display: none; } .sidebar-mobile-fallback { display: block; } }
  .article-body { max-width: 660px; padding-top: 40px; order: 2; }
  .sidebar { display: none; }  /* original sidebar hidden */

  /* Dock sidebar: left, sticky */
  .sidebar-dock { order: 1; position: sticky; top: 24px; align-self: start; height: calc(100vh - 48px); overflow-y: auto; padding-top: 40px; display: flex; flex-direction: column; gap: 16px; }
  .sidebar-dock::-webkit-scrollbar { width: 3px; }
  .sidebar-dock::-webkit-scrollbar-thumb { background: var(--border-light); border-radius: 2px; }

  /* Section nav */
  .dock-nav { display: flex; flex-direction: column; gap: 2px; margin-bottom: 16px; }
  .dock-nav-item { font-family: var(--font-sans); font-size: 12px; color: var(--text-muted); padding: 8px 12px; border-left: 3px solid transparent; border-radius: 0 6px 6px 0; cursor: pointer; transition: all 0.2s; text-decoration: none; display: block; line-height: 1.4; letter-spacing: 0.3px; }
  .dock-nav-item:hover { color: var(--un-blue); background: var(--un-blue-ghost); }
  .dock-nav-item.active { color: var(--un-blue); border-left-color: var(--un-blue); background: var(--un-blue-ghost); font-weight: 600; }

  /* Dock exercise card (compact) */
  .dock-exercise { background: var(--un-blue-deep); color: white; border-radius: 12px; padding: 20px; }
  .dock-exercise h3 { color: rgba(255,255,255,0.7); font-family: var(--font-sans); font-size: 10px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; font-weight: 700; }
  .dock-exercise .exercise-display { text-align: center; padding: 20px 12px; background: rgba(255,255,255,0.08); border-radius: 10px; margin: 10px 0; min-height: 120px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
  .dock-exercise .exercise-timer-num { font-size: 36px; font-weight: 300; font-family: var(--font-sans); color: white; margin-bottom: 4px; }
  .dock-exercise .exercise-phase { font-size: 11px; font-family: var(--font-sans); letter-spacing: 1px; text-transform: uppercase; color: rgba(255,255,255,0.6); margin-bottom: 8px; }
  .dock-exercise .exercise-instruction { font-size: 13px; font-family: var(--font-serif); color: rgba(255,255,255,0.9); max-width: 240px; line-height: 1.4; font-style: italic; }
  .dock-exercise .exercise-btn { display: block; width: 100%; padding: 10px; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); border-radius: 8px; color: white; font-family: var(--font-sans); font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s; margin-top: 10px; }
  .dock-exercise .exercise-btn:hover { background: rgba(255,255,255,0.25); }

  /* Dock CTA (compact) */
  .dock-cta { background: linear-gradient(135deg, var(--un-blue-deep), var(--un-blue-dark)); border-radius: 12px; padding: 20px; color: white; }
  .dock-cta h3 { color: rgba(255,255,255,0.65); font-family: var(--font-sans); font-size: 10px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; font-weight: 700; }
  .dock-cta .cta-primary { display: block; width: 100%; padding: 10px; background: white; border: none; border-radius: 6px; color: var(--un-blue-deep); font-family: var(--font-sans); font-size: 12px; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; margin-bottom: 6px; }
  .dock-cta .cta-secondary { display: block; width: 100%; padding: 8px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; color: white; font-family: var(--font-sans); font-size: 11px; font-weight: 500; cursor: pointer; text-align: center; text-decoration: none; }

  /* SDG badge in dock */
  .dock-sdg { background: var(--un-blue-ghost); border: 1px solid var(--border-light); border-radius: 12px; padding: 16px; }
  .dock-sdg h3 { font-family: var(--font-sans); font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: var(--un-blue-dark); margin-bottom: 8px; font-weight: 700; }
  .dock-sdg p { font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 6px; }

  /* Mobile fallback: show sidebar cards below article */
  .sidebar-mobile-fallback { display: none; margin-top: 40px; }
  .sidebar-mobile-fallback .sidebar-card { margin-bottom: 16px; }
</style>
<script>
// Dock: Intersection Observer for section nav highlighting
document.addEventListener('DOMContentLoaded', () => {
  const navItems = document.querySelectorAll('.dock-nav-item');
  const sections = [];
  navItems.forEach(item => {
    const target = document.querySelector(item.getAttribute('href'));
    if (target) sections.push({ el: target, nav: item });
  });
  if (!sections.length) return;
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navItems.forEach(n => n.classList.remove('active'));
        const match = sections.find(s => s.el === entry.target);
        if (match) match.nav.classList.add('active');
      }
    });
  }, { rootMargin: '-20% 0px -60% 0px' });
  sections.forEach(s => observer.observe(s.el));
});
</script>'''


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Assemble Pearl News v5.2 HTML from slot JSON")
    parser.add_argument("article", help="Path to article JSON file")
    parser.add_argument("-o", "--output", help="Output HTML file path")
    parser.add_argument("-m", "--metadata", help="Optional metadata JSON file")
    args = parser.parse_args()

    article = json.loads(Path(args.article).read_text())
    metadata = json.loads(Path(args.metadata).read_text()) if args.metadata else None

    html_output = assemble_v52(article, metadata)

    if args.output:
        out = Path(args.output)
        out.write_text(html_output, encoding="utf-8")
        print(f"✓ Assembled v5.2 HTML → {out} ({len(html_output):,} bytes)")
    else:
        sys.stdout.write(html_output)


if __name__ == "__main__":
    main()
