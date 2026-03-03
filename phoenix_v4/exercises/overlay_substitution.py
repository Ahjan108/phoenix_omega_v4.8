# Persona overlay for exercise sections. Token or phrase substitution.
# Overlay constraints: preserve grammatical role; no future language; no emotional intensity
# increase; do not modify callout sentence (validated post-overlay via must_start_with_one_of).
from __future__ import annotations
import re
from typing import Dict, List

CALL_OUT_PREFIXES_AHA = (
    "Now, I want you", "Now, I want to", "Now, pause", "Now, take a moment",
    "Now, take a second", "Now, let's", "Now, stop", "Now, reflect",
    "Now, observe", "Now, notice", "Now, consider", "Now, check",
)
CALL_OUT_PREFIXES_INTEGRATION = (
    "Now, before you move on,", "Now, as you return,",
    "Now, for the next few minutes,", "Now, as you go back to your day,",
    "Now, keep it simple,",
)
BODY_REFERENCE_WORDS = ("breath", "chest", "shoulders", "jaw", "neck", "rhythm", "tension", "weight", "pressure", "warmth", "movement", "exhale", "inhale", "body", "system", "nervous system")
BANNED_OUTCOME_PHRASES = ("you will", "this will", "guarantee", "cure", "heal", "fix", "transform", "forever", "completely")
TOKEN_PATTERN = re.compile(r"\{([A-Z0-9_]+)\}")

def _safe_token_substitute(text: str, token_map: Dict[str, str]) -> str:
    return TOKEN_PATTERN.sub(lambda m: token_map.get(m.group(1), m.group(0)), text)

def _ordered_phrase_substitute(text: str, phrase_map: Dict[str, str]) -> str:
    out = text
    for src, dst in sorted(phrase_map.items(), key=lambda kv: -len(kv[0])):
        out = re.sub(rf"(?<!\w){re.escape(src)}(?!\w)", dst, out)
    return out

def apply_persona_overlay(base_sections: Dict[str, str], persona: str, apply_to_sections: List[str], token_overlays: Dict = None, phrase_overlays: Dict = None) -> Dict[str, str]:
    out = dict(base_sections)
    tok = (token_overlays or {}).get(persona, {})
    phr = (phrase_overlays or {}).get(persona, {})
    for sec in apply_to_sections:
        if sec not in out: continue
        t = out[sec]
        if tok: t = _safe_token_substitute(t, tok)
        if phr: t = _ordered_phrase_substitute(t, phr)
        out[sec] = t
    return out

def validate_callout_prefix(section_name: str, text: str) -> List[str]:
    t = (text or "").strip()
    if section_name == "aha_noticing" and not t.startswith(CALL_OUT_PREFIXES_AHA): return ["aha_noticing missing required callout prefix"]
    if section_name == "integration" and not t.startswith(CALL_OUT_PREFIXES_INTEGRATION): return ["integration missing required callout prefix"]
    return []

def validate_required_terms_for_aha(text: str) -> List[str]:
    lower = (text or "").lower()
    errs = []
    if "notice" not in lower and "might notice" not in lower: errs.append("aha_noticing must contain notice or might notice")
    if not any(w in lower for w in BODY_REFERENCE_WORDS): errs.append("aha_noticing missing body reference word")
    return errs

def validate_banned_outcomes(text: str) -> List[str]:
    return [f"contains banned outcome phrase: {p}" for p in BANNED_OUTCOME_PHRASES if p in (text or "").lower()]
