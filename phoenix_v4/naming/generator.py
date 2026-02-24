"""
Deterministic title + subtitle candidate generation. Exactly 12 candidates, seeded shuffle.
Authority: SYSTEMS_DOCUMENTATION §29.2.5.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any

from . import keyword_bank
from ._config import (
    load_persona_flavor,
    load_recognition_lexemes,
    load_subtitle_patterns,
)


def book_id_from_spec(
    series_id: str,
    angle_id: str,
    installment_number: int,
) -> str:
    """Produce stable book_id e.g. bk_social_anx_work_003."""
    def series_abbrev(s: str) -> str:
        parts = (s or "").replace("-", "_").split("_")[:2]
        out = []
        for p in parts:
            if not p:
                continue
            out.append("anx" if p == "anxiety" else (p if len(p) <= 6 else p[:4]))
        return "_".join(out) if out else (s[:6] if s else "bk")
    def angle_abbrev(s: str) -> str:
        parts = (s or "").replace("-", "_").split("_")
        return parts[-1] if parts else (s[:4] if s else "gen")
    ser = series_abbrev(series_id or "bk")
    ang = angle_abbrev(angle_id or "gen")
    inst = max(1, int(installment_number) if installment_number is not None else 1)
    return f"bk_{ser}_{ang}_{inst:03d}"


def _seed_int(book_id: str, persona_id: str, angle_id: str, brand_id: str) -> int:
    seed_str = f"{book_id}{persona_id}{angle_id}{brand_id}"
    seed_bytes = hashlib.sha256(seed_str.encode()).digest()
    return int.from_bytes(seed_bytes[:4], "big")


def _pick_seeded(seq: list[str], rng: random.Random, n: int = 1) -> list[str]:
    if not seq or n <= 0:
        return []
    if n >= len(seq):
        return list(seq)
    indices = rng.sample(range(len(seq)), n)
    return [seq[i] for i in indices]


def generate_candidates(
    topic_id: str,
    persona_id: str,
    series_id: str,
    angle_id: str,
    brand_id: str,
    seed: str,
    installment_number: int = 1,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Returns (book_id, list of 12 candidate dicts).
    Each candidate: title, subtitle, template_used, candidate_id, intent (for scorer).
    """
    bid = book_id_from_spec(series_id, angle_id, installment_number)
    seed_int = _seed_int(bid, persona_id, angle_id, brand_id)
    rng = random.Random(seed_int)

    keywords = keyword_bank.get_keywords(series_id, angle_id, topic_id)
    primary = keywords.get("primary") or angle_id.replace("_", " ")
    secondary = keywords.get("secondary") or []
    scenario_phrase = angle_id.replace("_", " ")

    patterns = load_subtitle_patterns()
    title_tpl = (patterns.get("title_templates") or {}).copy()
    subtitle_tpl = (patterns.get("subtitle_templates") or {}).copy()
    brand_prefs = (patterns.get("brand_template_preferences") or {}).get(brand_id) or {}
    preferred_title = list(brand_prefs.get("title") or ["scenario_direct"])
    preferred_sub = list(brand_prefs.get("subtitle") or ["micro_promise"])
    micro_promises_cfg = patterns.get("micro_promises") or {}
    micro_list = micro_promises_cfg.get(brand_id) or micro_promises_cfg.get("default") or [
        "How to Stop Freezing and Speak Up with Confidence"
    ]

    flavor = load_persona_flavor()
    personas_cfg = flavor.get("personas") or {}
    persona_desc = (personas_cfg.get(persona_id) or personas_cfg.get("default") or {}).get("persona_role") or persona_id.replace("_", " ").title()
    title_tone = (personas_cfg.get(persona_id) or personas_cfg.get("default") or {}).get("title_tone") or "Readers"

    lex = load_recognition_lexemes()
    distress_verbs = list(lex.get("distress_verbs") or ["freeze", "panic", "overthink"])
    outcome_phrases = list(lex.get("outcome_phrases") or ["speak up", "feel confident", "find calm"])
    rng.shuffle(distress_verbs)
    rng.shuffle(outcome_phrases)
    dv = (distress_verbs[0] or "freeze").lower()
    distress_verb = dv.title()
    distress_verb_ing = (dv + "ing") if not dv.endswith("e") else (dv.rstrip("e") + "ing")
    distress_verb_ing = distress_verb_ing.title()
    outcome_verb = (outcome_phrases[0] or "feel confident").title()
    action1 = (outcome_phrases[1 % len(outcome_phrases)] or "speak up").title()
    action2 = (outcome_phrases[2 % len(outcome_phrases)] or "stop worrying").title()
    action3 = (outcome_phrases[3 % len(outcome_phrases)] or "find calm").title()
    promise_clause = rng.choice(micro_list) if micro_list else "How to Find Calm and Show Up"

    # Format placeholders (Phase 1 default)
    n_sessions = 8
    format_unit = "sessions"

    def fill(s: str) -> str:
        return (s or "").replace("{PrimaryKeyword}", primary).replace("{ScenarioPhrase}", scenario_phrase).replace("{PersonaDescription}", persona_desc).replace("{PromiseClause}", promise_clause).replace("{DistressVerb}", distress_verb).replace("{DistressVerbIng}", distress_verb_ing).replace("{OutcomeVerb}", outcome_verb).replace("{Action1}", action1).replace("{Action2}", action2).replace("{Action3}", action3).replace("{N}", str(n_sessions)).replace("{FormatUnit}", format_unit)

    title_names = list(title_tpl.keys())
    subtitle_names = list(subtitle_tpl.keys())
    preferred_title_set = set(preferred_title)
    preferred_sub_set = set(preferred_sub)
    # Prefer 2 each for preferred, 1 for others; build (tn, sn) pairs
    pairs = []
    for tn in title_names:
        count = 2 if tn in preferred_title_set else 1
        for _ in range(count):
            for sn in subtitle_names:
                pairs.append((tn, sn))
    rng.shuffle(pairs)
    seen = set()
    candidates = []
    for i, (tn, sn) in enumerate(pairs):
        if len(candidates) >= 12:
            break
        t_tpl = title_tpl.get(tn, "{PrimaryKeyword}")
        s_tpl = subtitle_tpl.get(sn, "How to {OutcomeVerb} in {ScenarioPhrase}")
        title_text = fill(t_tpl)
        subtitle_text = fill(s_tpl)
        key = (title_text, subtitle_text)
        if key in seen:
            continue
        seen.add(key)
        candidates.append({
            "title": title_text,
            "subtitle": subtitle_text,
            "template_used": tn,
            "template_id": f"T{i+1:03d}",
            "candidate_id": f"cand_{len(candidates)+1:03d}",
            "intent": "scenario_specific",
        })
    while len(candidates) < 12 and pairs:
        tn, sn = rng.choice(pairs)
        t_tpl = title_tpl.get(tn, "{PrimaryKeyword}")
        s_tpl = subtitle_tpl.get(sn, "How to {OutcomeVerb} in {ScenarioPhrase}")
        title_text = fill(t_tpl)
        subtitle_text = fill(s_tpl)
        key = (title_text, subtitle_text)
        if key not in seen:
            seen.add(key)
            candidates.append({
                "title": title_text,
                "subtitle": subtitle_text,
                "template_used": tn,
                "template_id": f"T{len(candidates)+1:03d}",
                "candidate_id": f"cand_{len(candidates)+1:03d}",
                "intent": "scenario_specific",
            })
    return bid, candidates[:12]
