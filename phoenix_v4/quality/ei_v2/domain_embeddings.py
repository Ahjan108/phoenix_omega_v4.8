"""
Domain-tuned embedding adapter for EI V2.

Enhances thesis alignment scoring by incorporating persona and topic
context into the similarity computation. Instead of raw cosine(thesis, text),
this module computes a weighted similarity that accounts for:

  1. Thesis alignment (core meaning match)
  2. Persona affinity (does the text speak to this persona's life context?)
  3. Topic coherence (does the text stay within the topic's semantic field?)

When no external embed_fn is provided, falls back to a heuristic
word-overlap approach using the domain lexicons from cross_encoder_reranker.

The weighting is configurable so you can tune persona vs thesis vs topic
emphasis per use case.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Any, Callable, Dict, List, Optional

from phoenix_v4.quality.ei_v2.cross_encoder_reranker import (
    _SEMANTIC_FIELDS,
    _tokenize,
    _token_overlap,
    _semantic_field_overlap,
)


# Persona context lexicons: words/phrases strongly associated with each persona.
_PERSONA_LEXICONS: Dict[str, set] = {
    "gen_alpha_students": {
        "notification", "phone", "screen", "tiktok", "instagram", "group chat",
        "school", "homework", "test", "grade", "teacher", "parent", "friend",
        "gaming", "streaming", "social media", "cancel", "cringe", "viral",
    },
    "gen_z_professionals": {
        "side hustle", "linkedin", "remote", "hybrid", "startup", "app",
        "content", "brand", "hustle", "grind", "burnout", "adulting",
        "rent", "student loan", "therapy", "boundaries", "toxic",
    },
    "gen_x_sandwich": {
        "parent", "aging", "teenager", "mortgage", "college", "retirement",
        "sandwich generation", "caregiver", "middle age", "career",
        "second shift", "invisible", "forgotten",
    },
    "corporate_managers": {
        "meeting", "quarterly", "kpi", "team", "stakeholder", "deliverable",
        "performance review", "budget", "strategy", "leadership", "board",
        "executive", "decision", "accountability", "politics",
    },
    "healthcare_rns": {
        "shift", "patient", "chart", "hospital", "clinic", "code",
        "icu", "nurse", "doctor", "medication", "compassion fatigue",
        "night shift", "double shift", "scrubs", "bedside",
    },
    "tech_finance_burnout": {
        "sprint", "deploy", "standup", "deadline", "quarter", "bonus",
        "stock", "options", "ping", "slack", "on-call", "production",
        "dashboard", "metrics", "performance",
    },
    "entrepreneurs": {
        "founder", "startup", "pitch", "investor", "runway", "revenue",
        "pivot", "scale", "growth", "funding", "equity", "bootstrap",
        "launch", "customer", "product-market fit",
    },
    "millennial_women_professionals": {
        "work-life", "balance", "career", "motherhood", "imposter",
        "glass ceiling", "lean in", "boundaries", "self-care",
        "comparison", "instagram", "wellness",
    },
    "nyc_executives": {
        "manhattan", "midtown", "wall street", "office", "commute",
        "subway", "penthouse", "boardroom", "corner office", "networking",
        "power lunch", "status", "success",
    },
    "working_parents": {
        "daycare", "school pickup", "bedtime", "morning routine",
        "juggling", "guilt", "childcare", "balance", "exhausted",
        "patience", "tantrum", "homework", "family",
    },
    "first_responders": {
        "dispatch", "call", "scene", "adrenaline", "partner",
        "uniform", "shift", "trauma", "line of duty", "debriefing",
        "hypervigilance", "critical incident",
    },
    "educators": {
        "classroom", "student", "lesson plan", "curriculum", "grade",
        "parent conference", "administration", "burnout", "summer",
        "tenure", "standardized test",
    },
}

# Topic context lexicons: core words for each topic domain.
_TOPIC_LEXICONS: Dict[str, set] = {
    "anxiety": {"anxiety", "worry", "panic", "nervous", "dread", "fear", "alarm", "racing", "spiral", "catastrophize"},
    "burnout": {"burnout", "exhaustion", "depleted", "empty", "overwork", "fatigue", "collapse", "running on empty"},
    "boundaries": {"boundary", "boundaries", "no", "limit", "protect", "space", "enmesh", "codependent", "assert"},
    "grief": {"grief", "loss", "death", "mourning", "gone", "absence", "missing", "memorial", "farewell"},
    "overthinking": {"overthink", "ruminate", "loop", "spiral", "replay", "analyze", "obsess", "intrusive"},
    "imposter_syndrome": {"imposter", "fraud", "fake", "deserve", "belong", "exposed", "credential", "prove"},
    "sleep_anxiety": {"sleep", "insomnia", "3am", "awake", "night", "bed", "rest", "tossing", "racing mind"},
    "financial_stress": {"money", "debt", "bill", "afford", "savings", "rent", "mortgage", "paycheck", "broke"},
    "compassion_fatigue": {"compassion", "empathy", "numb", "caring", "helper", "absorb", "secondary trauma"},
    "self_worth": {"worth", "enough", "deserve", "value", "matter", "invisible", "unworthy", "lovable"},
    "somatic_healing": {"body", "somatic", "nervous system", "regulate", "discharge", "tension", "release"},
    "social_anxiety": {"social", "people", "crowd", "judgment", "seen", "awkward", "avoid", "shy"},
    "courage": {"courage", "brave", "fear", "risk", "leap", "voice", "speak", "stand", "confront"},
    "depression": {"depression", "flat", "empty", "numb", "heavy", "dark", "hopeless", "withdrawn", "apathy"},
}


def _persona_affinity(text_tokens: List[str], persona_id: str) -> float:
    """Score how well text tokens match a persona's life context."""
    lexicon = _PERSONA_LEXICONS.get(persona_id, set())
    if not lexicon or not text_tokens:
        return 0.0
    text_set = set(text_tokens)
    hits = text_set & lexicon
    return min(1.0, len(hits) / max(3, len(lexicon) * 0.15))


def _topic_coherence(text_tokens: List[str], topic_id: str) -> float:
    """Score how well text tokens stay within a topic's semantic field."""
    lexicon = _TOPIC_LEXICONS.get(topic_id, set())
    if not lexicon or not text_tokens:
        return 0.0
    text_set = set(text_tokens)
    hits = text_set & lexicon
    return min(1.0, len(hits) / max(2, len(lexicon) * 0.2))


def _cosine_sim(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def domain_thesis_similarity(
    thesis: str,
    candidate_text: str,
    *,
    persona_id: str = "",
    topic_id: str = "",
    cfg: Optional[Dict[str, Any]] = None,
    embed_fn: Optional[Callable[[str, str], List[float]]] = None,
) -> float:
    """
    Compute domain-aware thesis similarity.

    Returns score in [0, 1] combining:
      - Thesis alignment (embedding or heuristic)
      - Persona affinity
      - Topic coherence

    Weights are configurable via cfg.
    """
    cfg = cfg or {}
    w_thesis = float(cfg.get("thesis_weight", 0.4))
    w_persona = float(cfg.get("persona_weight", 0.3))
    w_topic = float(cfg.get("topic_weight", 0.3))

    c_tokens = _tokenize(candidate_text)
    t_tokens = _tokenize(thesis)

    # Thesis alignment
    if embed_fn is not None:
        model = cfg.get("model", "")
        try:
            vec_t = embed_fn(thesis, model)
            vec_c = embed_fn(candidate_text, model)
            thesis_sim = _cosine_sim(vec_t, vec_c)
        except Exception:
            thesis_sim = _token_overlap(t_tokens, c_tokens)
    else:
        tok_overlap = _token_overlap(t_tokens, c_tokens)
        field_overlap = _semantic_field_overlap(t_tokens, c_tokens)
        thesis_sim = 0.6 * tok_overlap + 0.4 * field_overlap

    # Persona affinity
    persona_score = _persona_affinity(c_tokens, persona_id)

    # Topic coherence
    topic_score = _topic_coherence(c_tokens, topic_id)

    composite = w_thesis * thesis_sim + w_persona * persona_score + w_topic * topic_score
    return round(min(1.0, composite), 4)
