"""
Pearl News — deterministic teacher exercise + CTA + freebies resolver.

Selection order (no LLM choice):
  1) exact match: teacher_id + topic
  2) teacher_id + sdg
  3) teacher_id only
  4) topic default

Tie-break:
  stable hash over (article_id, exercise_id), so same inputs always pick same exercise.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

REQUIRED_EXERCISE_FIELDS = (
    "exercise_id",
    "name",
    "duration_minutes",
    "steps",
    "safety_note",
    "delivery_format",
)


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _normalize_locale(language: str) -> str:
    language = (language or "en").lower()
    if language.startswith("zh"):
        return "zh-cn"
    if language.startswith("ja"):
        return "ja"
    return "en"


def _normalize_age_fit(v: str) -> str:
    x = (v or "").lower().strip()
    if x in ("gen_z", "gen-alpha", "gen_alpha", "z"):
        return "gen_z"
    if x in ("alpha", "genalpha"):
        return "gen_alpha"
    return "both"


def _hash_score(article_id: str, exercise_id: str) -> int:
    token = f"{article_id}::{exercise_id}".encode("utf-8")
    return int(hashlib.sha256(token).hexdigest(), 16)


def _duration_ok(v: Any) -> bool:
    try:
        return 3 <= int(v) <= 10
    except Exception:
        return False


def _is_valid_exercise(ex: dict[str, Any]) -> bool:
    if not isinstance(ex, dict):
        return False
    for k in REQUIRED_EXERCISE_FIELDS:
        if not ex.get(k):
            return False
    if not _duration_ok(ex.get("duration_minutes")):
        return False
    steps = ex.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        return False
    return True


def _infer_exercise_type(ex: dict[str, Any]) -> str:
    declared = str(ex.get("exercise_type") or "").strip().lower()
    if declared:
        return declared
    fmt = str(ex.get("delivery_format") or "").lower()
    topic = str(ex.get("topic") or "").lower()
    if "text_reflection" in fmt:
        return "reflective"
    if "short_video" in fmt:
        return "cognitive"
    if "audio" in fmt and topic in {"mental_health", "climate"}:
        return "regulate"
    if topic in {"inequality", "partnerships", "peace_conflict"}:
        return "civic"
    if topic in {"education", "economy_work"}:
        return "planning"
    return "somatic"


def _policy_rank(
    *,
    policy: dict[str, Any],
    article_type: str,
    topic: str,
    age_fit: str,
    exercise_type: str,
) -> int:
    defaults = policy.get("defaults") or {}
    t_map = defaults.get("preferred_types_by_template") or {}
    topic_map = defaults.get("preferred_types_by_topic") or {}
    age_map = defaults.get("preferred_types_by_age_fit") or {}
    ordered: list[str] = []
    ordered.extend(t_map.get(article_type, []))
    ordered.extend(topic_map.get(topic, []))
    ordered.extend(age_map.get(age_fit, age_map.get("both", [])))
    # Deduplicate while preserving order
    seen = set()
    uniq = [x for x in ordered if not (x in seen or seen.add(x))]
    if exercise_type in uniq:
        return uniq.index(exercise_type)
    return len(uniq) + 100


def _matches_article_type(entry: dict[str, Any], article_type: str) -> bool:
    allowed = entry.get("article_types")
    if not allowed:
        return True
    if isinstance(allowed, str):
        return allowed == "all" or allowed == article_type
    if isinstance(allowed, list):
        return "all" in allowed or article_type in allowed
    return True


def _matches_age_fit(entry: dict[str, Any], age_fit: str) -> bool:
    """Match age_fit: exercises are always eligible for articles targeting 'both'.
    gen_z/gen_alpha exercises are specialized but not excluded from 'both' articles.
    """
    entry_fit = _normalize_age_fit(str(entry.get("age_fit") or "both"))
    article_fit = _normalize_age_fit(age_fit)
    # Exercise for 'both' → always matches
    if entry_fit == "both":
        return True
    # Article for 'both' → accepts all exercises (specialized ones included)
    if article_fit == "both":
        return True
    # Otherwise must match exactly
    return entry_fit == article_fit


def _build_exercise_description(ex: dict[str, Any], *, topic: str, mode: str) -> str:
    if ex.get("exercise_description"):
        return str(ex.get("exercise_description"))
    name = str(ex.get("name") or "practice")
    ex_type = _infer_exercise_type(ex)
    return (
        f"{name} is a short {ex_type} exercise for {topic.replace('_', ' ')} stories. "
        f"It is designed to help readers stabilize, understand, and take one concrete {mode} step."
    )


def _non_guided_component(step: str) -> str:
    s = (step or "").strip().lower()
    if any(k in s for k in ("breathe", "breath", "inhale", "exhale")):
        return "A brief breath-regulation interval to settle attention."
    if any(k in s for k in ("name", "write", "document", "notice", "observe")):
        return "A short reflection moment to identify the core stressor clearly."
    if any(k in s for k in ("choose", "action", "send", "request", "contact", "register")):
        return "One concrete next-step action linked directly to this issue."
    return "A short structured reflection component connected to the article topic."


def _locale_match(entry: dict[str, Any], locale: str) -> bool:
    allowed = entry.get("locale") or "all"
    if isinstance(allowed, str):
        if allowed == "all":
            return True
        return allowed == locale
    if isinstance(allowed, list):
        return "all" in allowed or locale in allowed
    return True


def _tier(entry: dict[str, Any], teacher_id: str, topic: str, sdg: str) -> int | None:
    e_teacher = str(entry.get("teacher_id") or "")
    e_topic = str(entry.get("topic") or "")
    e_sdg = str(entry.get("sdg") or "")
    if e_teacher == teacher_id and e_topic == topic:
        return 1
    if e_teacher == teacher_id and e_sdg == sdg:
        return 2
    if e_teacher == teacher_id and not e_topic and not e_sdg:
        return 3
    if e_topic == topic and not e_teacher:
        return 4
    return None


def select_exercise_from_bank(
    *,
    bank: dict[str, Any],
    teacher_id: str,
    topic: str,
    sdg: str,
    language: str,
    article_id: str,
    article_type: str,
    age_fit: str,
    policy: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    entries = bank.get("exercises") or []
    locale = _normalize_locale(language)
    candidates: list[tuple[int, int, int, dict[str, Any]]] = []

    for entry in entries:
        if not _locale_match(entry, locale):
            continue
        if not _matches_article_type(entry, article_type):
            continue
        if not _matches_age_fit(entry, age_fit):
            continue
        t = _tier(entry, teacher_id=teacher_id, topic=topic, sdg=sdg)
        if t is None:
            continue
        if not _is_valid_exercise(entry):
            continue
        ex_type = _infer_exercise_type(entry)
        rank = _policy_rank(
            policy=policy,
            article_type=article_type,
            topic=topic,
            age_fit=age_fit,
            exercise_type=ex_type,
        )
        score = _hash_score(article_id, str(entry.get("exercise_id")))
        e = dict(entry)
        e["exercise_type"] = ex_type
        candidates.append((t, rank, score, e))

    if not candidates:
        return {}, ["exercise_payload"]

    # Lowest tier number strongest; then policy rank; then stable hash.
    candidates.sort(key=lambda x: (x[0], x[1], x[2]))
    chosen = candidates[0][3]
    return chosen, []


def _pick_mode(primary_sdg: str, mapping: dict[str, Any]) -> str:
    sdg_modes = mapping.get("sdg_modes") or {}
    return str(sdg_modes.get(str(primary_sdg), "regulation"))


def _pick_freebies(topic: str, mode: str, mapping: dict[str, Any]) -> list[str]:
    topic_overrides = mapping.get("topic_overrides") or {}
    if topic in topic_overrides and topic_overrides[topic]:
        return list(topic_overrides[topic])
    mode_defaults = mapping.get("mode_defaults") or {}
    return list(mode_defaults.get(mode) or [])


def _build_freebie_payload(
    freebie_ids: list[str],
    mapping: dict[str, Any],
    freebie_registry: dict[str, Any],
) -> list[dict[str, Any]]:
    links = mapping.get("freebie_links") or {}
    landing_base = str(mapping.get("landing_base_url") or "").rstrip("/")
    registry = (freebie_registry.get("freebies") or {})
    out: list[dict[str, Any]] = []
    for fid in freebie_ids:
        meta = registry.get(fid) or {}
        url = links.get(fid) or (f"{landing_base}/{fid}" if landing_base else "")
        out.append({
            "freebie_id": fid,
            "title": (meta.get("type") or fid).replace("_", " ").title(),
            "type": meta.get("type"),
            "url": url,
        })
    return out


def _build_cta_payload(
    mode: str,
    topic: str,
    exercise_name: str,
    exercise_id: str,
    freebies: list[dict[str, Any]],
    mapping: dict[str, Any],
) -> dict[str, Any]:
    ctas = mapping.get("cta_templates") or {}
    t = ctas.get(mode) or ctas.get("regulation") or {}
    primary_label = (t.get("primary_action_label") or "Start Practice").format(exercise_name=exercise_name)
    secondary_label = t.get("secondary_action_label") or "Get Freebies"
    micro_actions = mapping.get("topic_micro_actions") or {}
    return {
        "title": t.get("title") or "Take Action Now",
        "body": t.get("body") or "Use the practice and take one concrete next step.",
        "primary_action_label": primary_label,
        "primary_action_url": f"#exercise-{exercise_id}" if exercise_id else "#exercise",
        "secondary_action_label": secondary_label,
        "secondary_action_url": (freebies[0].get("url") if freebies else ""),
        "micro_action": micro_actions.get(topic, "Choose one traceable action in your local context this week."),
    }


def resolve_news_actions(
    item: dict[str, Any],
    teacher: dict[str, Any],
    *,
    pearl_config_root: Path | None = None,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    pearl_config_root = pearl_config_root or (root / "pearl_news" / "config")
    exercise_bank = _load_yaml(pearl_config_root / "teacher_exercise_bank.yaml")
    mapping = _load_yaml(root / "config" / "freebies" / "news_freebie_mapping.yaml")
    policy = _load_yaml(root / "config" / "freebies" / "news_exercise_selection_policy.yaml")
    freebie_registry = _load_yaml(root / "config" / "freebies" / "freebie_registry.yaml")

    topic = str(item.get("topic") or "")
    primary_sdg = str(item.get("primary_sdg") or "17")
    teacher_id = str(teacher.get("teacher_id") or "")
    article_id = str(item.get("id") or item.get("slug") or item.get("title") or "article")
    language = str(item.get("language") or "en")
    article_type = str(item.get("template_id") or "hard_news_spiritual_response")
    age_fit = _normalize_age_fit(str(item.get("age_fit") or "both"))
    mode = _pick_mode(primary_sdg, mapping)

    exercise, missing_required = select_exercise_from_bank(
        bank=exercise_bank,
        teacher_id=teacher_id,
        topic=topic,
        sdg=primary_sdg,
        language=language,
        article_id=article_id,
        article_type=article_type,
        age_fit=age_fit,
        policy=policy,
    )
    if exercise:
        exercise["exercise_description"] = _build_exercise_description(exercise, topic=topic, mode=mode)
        exercise["age_fit"] = _normalize_age_fit(str(exercise.get("age_fit") or age_fit))
        exercise["article_types"] = exercise.get("article_types") or ["all"]

    freebie_ids = _pick_freebies(topic, mode, mapping)
    freebies_payload = _build_freebie_payload(freebie_ids, mapping, freebie_registry)
    cta_payload = _build_cta_payload(
        mode=mode,
        topic=topic,
        exercise_name=str(exercise.get("name") or "Practice"),
        exercise_id=str(exercise.get("exercise_id") or ""),
        freebies=freebies_payload,
        mapping=mapping,
    )

    if not cta_payload:
        missing_required.append("cta_payload")
    if not freebies_payload:
        missing_required.append("freebies_payload")

    return {
        "exercise_payload": exercise,
        "cta_payload": cta_payload,
        "freebies_payload": freebies_payload,
        "mode": mode,
        "policy_match": bool(exercise),
        "missing_required": sorted(set(missing_required)),
    }


def render_news_action_block(actions: dict[str, Any]) -> str:
    exercise = actions.get("exercise_payload") or {}
    cta = actions.get("cta_payload") or {}
    freebies = actions.get("freebies_payload") or []

    if not exercise or not cta or not freebies:
        return ""

    steps = (exercise.get("steps") or [])[:3]
    components: list[str] = []
    for s in steps:
        c = _non_guided_component(str(s))
        if c not in components:
            components.append(c)
    components_html = "".join(f"<li>{c}</li>" for c in components[:3])
    freebies_html = "".join(
        f"<li><a href=\"{f.get('url', '#')}\">{f.get('title') or f.get('freebie_id')}</a></li>"
        for f in freebies
    )
    duration = exercise.get("duration_minutes")
    duration_label = f"{duration} min" if duration else "short"
    delivery_format = exercise.get("delivery_format") or "brief"
    ex_type = exercise.get("exercise_type") or "exercise"
    description = exercise.get("exercise_description") or ""
    safety_note = exercise.get("safety_note") or ""
    exercise_id = exercise.get("exercise_id") or "exercise"

    return (
        "\n\n<div class=\"pearl-news-action\" data-news-action=\"true\">"
        f"<h2>Take Action Now</h2>"
        f"<p id=\"exercise-{exercise_id}\"><strong>{exercise.get('name', 'Practice')}</strong> ({duration_label}, {delivery_format}, {ex_type}).</p>"
        f"<p>{description}</p>"
        f"<p><strong>Helpful components:</strong></p><ul>{components_html}</ul>"
        f"<p><em>Safety: {safety_note}</em></p>"
        f"<p><strong>{cta.get('title', '')}</strong> {cta.get('body', '')}</p>"
        f"<p><a href=\"{cta.get('primary_action_url', '#')}\">{cta.get('primary_action_label', 'Start')}</a></p>"
        f"<p>{cta.get('micro_action', '')}</p>"
        f"<h3>Companion Freebies</h3><ul>{freebies_html}</ul>"
        "</div>\n"
    )
