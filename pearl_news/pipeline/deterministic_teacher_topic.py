from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - runtime dependency in repo
    yaml = None


PACKS_ROOT = Path("pearl_news") / "teacher_topic_packs"
PAIRS_INTERFAITH_ROOT = PACKS_ROOT / "pairs" / "interfaith_dialogue_report"
UNSAY_PAIRS_ROOT = PACKS_ROOT / "pairs" / "unsay_dialogue"
BEAT_MAPS_ROOT = Path("pearl_news") / "beat_maps"
PROMPTED_HARD_NEWS_SLOTS = {"news_peg", "body_data"}
PROMPTED_INTERFAITH_SLOTS = {"headline_layer_1", "event_summary"}
PROMPTED_COMMENTARY_SLOTS = {"headline_layer_1", "news_peg", "body_data"}
PROMPTED_EXPLAINER_SLOTS = {
    "headline_layer_1",
    "news_peg",
    "body_data",
}
PROMPTED_YOUTH_FEATURE_SLOTS = {
    "headline_layer_1",
    "news_peg",
    "body_data",
}
_FORBIDDEN_HARD_NEWS_BEAT_MAP_RULES = {
    "bridge_before_turnaround": ("bridge", "turnaround"),
    "practice_before_teacher_perspective": ("practice_announce", "teacher_perspective"),
    "sdg_before_practice": ("sdg_un_tie", "practice_announce"),
}
_FORBIDDEN_COMMENTARY_BEAT_MAP_RULES = {
    "bridge_before_thesis": ("bridge", "hook_personal"),
    "teaching_before_bridge": ("teacher_perspective", "bridge"),
    "civic_before_teaching": ("forward_look", "teacher_perspective"),
    "sdg_before_civic": ("sdg_un_tie", "forward_look"),
}
_FORBIDDEN_EXPLAINER_BEAT_MAP_RULES = {
    "ethical_spiritual_dimension_before_youth_implications": ("ethical_spiritual_dimension", "youth_implications"),
    "teacher_perspective_before_ethical_spiritual_dimension": ("teacher_perspective", "ethical_spiritual_dimension"),
    "sdg_policy_tie_before_future_outlook": ("sdg_policy_tie", "future_outlook"),
}
_FORBIDDEN_YOUTH_FEATURE_BEAT_MAP_RULES = {
    "solutions_before_teacher_reflection": ("solutions", "teacher_reflection"),
    "sdg_before_solutions": ("sdg_framework", "solutions"),
    "data_before_narrative": ("data_research", "youth_narrative"),
    "data_before_reflection": ("data_research", "teacher_reflection"),
    "solutions_before_data": ("solutions", "data_research"),
    "teacher_reflection_before_data": ("teacher_reflection", "data_research"),
}


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _stable_index(key: str, n: int) -> int:
    if n <= 0:
        return 0
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest, 16) % n


def _normalize_topic(topic: str) -> str:
    return (topic or "").strip().lower().replace(" ", "_")


def load_teacher_topic_pack(
    repo_root: Path,
    teacher_id: str,
    topic: str,
    template_id: str | None = None,
) -> dict[str, Any] | None:
    topic = _normalize_topic(topic)
    base_path = repo_root / PACKS_ROOT / "teachers" / teacher_id / f"{topic}.yaml"
    base = _load_yaml(base_path)
    if not base:
        return None

    if template_id:
        overlay_path = repo_root / PACKS_ROOT / "overlays" / template_id / f"{teacher_id}__{topic}.yaml"
        overlay = _load_yaml(overlay_path)
        if overlay:
            base = _deep_merge(base, overlay)
    return base


def load_interfaith_pair_pack(
    repo_root: Path,
    teacher_a_id: str,
    teacher_b_id: str,
    topic: str,
) -> dict[str, Any] | None:
    """Load interfaith pair-pack from pairs/interfaith_dialogue_report/.

    File naming: {teacher_a_id}__{teacher_b_id}__{topic}.yaml.
    If not found, tries {teacher_b_id}__{teacher_a_id}__{topic}.yaml.
    """
    topic = _normalize_topic(topic)
    a, b = (teacher_a_id or "").strip(), (teacher_b_id or "").strip()
    if not a or not b or a == b or not topic:
        return None
    for path in (
        repo_root / PAIRS_INTERFAITH_ROOT / f"{a}__{b}__{topic}.yaml",
        repo_root / PAIRS_INTERFAITH_ROOT / f"{b}__{a}__{topic}.yaml",
    ):
        data = _load_yaml(path)
        if data and data.get("active", True):
            return data
    return None


def load_unsay_pair_pack(
    repo_root: Path,
    teacher_a_id: str,
    teacher_b_id: str,
    topic: str,
) -> dict[str, Any] | None:
    """Load UNSAY pair-pack from pairs/unsay_dialogue/.

    File naming: {teacher_a_id}__{teacher_b_id}__{topic}.yaml.
    If not found, tries {teacher_b_id}__{teacher_a_id}__{topic}.yaml.
    Returns None if file missing, active is false, or pack's teacher_a_id/teacher_b_id/topic don't match.
    """
    topic = _normalize_topic(topic)
    a, b = (teacher_a_id or "").strip().lower(), (teacher_b_id or "").strip().lower()
    if not a or not b or a == b or not topic:
        return None
    for path in (
        repo_root / UNSAY_PAIRS_ROOT / f"{a}__{b}__{topic}.yaml",
        repo_root / UNSAY_PAIRS_ROOT / f"{b}__{a}__{topic}.yaml",
    ):
        data = _load_yaml(path)
        if not data or not data.get("active", True):
            continue
        pack_a = (data.get("teacher_a_id") or "").strip().lower()
        pack_b = (data.get("teacher_b_id") or "").strip().lower()
        pack_topic = _normalize_topic(data.get("topic") or "")
        if {pack_a, pack_b} != {a, b} or pack_topic != topic:
            continue
        return data
    return None


def load_beat_map_config(repo_root: Path, template_id: str) -> dict[str, Any]:
    return _load_yaml(repo_root / BEAT_MAPS_ROOT / f"{template_id}.yaml")


def select_beat_map(
    beat_map_config: dict[str, Any],
    *,
    article_id: str,
    topic: str,
    forced_map_id: str | None = None,
) -> dict[str, Any] | None:
    maps = beat_map_config.get("maps") or []
    if not maps:
        return None

    topic = _normalize_topic(topic)
    candidates = [
        item for item in maps
        if not item.get("allowed_for_topics") or topic in [str(t).strip().lower() for t in item.get("allowed_for_topics", [])]
    ]
    candidates = candidates or maps

    if forced_map_id:
        for item in candidates:
            if item.get("id") == forced_map_id:
                return item

    idx = _stable_index(f"{article_id}|beat_map|{topic}", len(candidates))
    return candidates[idx]


def _metadata_for(option: dict[str, Any]) -> dict[str, Any]:
    meta = option.get("metadata") or {}
    if isinstance(meta, dict):
        return meta
    simple = {}
    for key in (
        "semantic_family",
        "tone",
        "intensity",
        "article_types",
        "topic_subcases",
        "persona_id",
        "age_register",
        "body_register",
        "digital_behavior",
        "loop_type",
        "avoid_with",
        "angle",
        "reframe_style",
        "motive",
        "metaphor_family",
        "trust_anchor_style",
        "youth_world",
    ):
        if key in option:
            simple[key] = option[key]
    return simple


def _option_allowed(
    option: dict[str, Any],
    *,
    template_id: str,
    topic_subcase: str | None,
    used_families: set[str],
) -> bool:
    meta = _metadata_for(option)
    article_types = meta.get("article_types") or []
    if article_types and template_id not in article_types:
        return False
    topic_subcases = meta.get("topic_subcases") or []
    if topic_subcase and topic_subcases and topic_subcase not in topic_subcases:
        return False
    avoid_with = set(meta.get("avoid_with") or [])
    if avoid_with & used_families:
        return False
    return True


def _select_option(
    section: dict[str, Any],
    *,
    article_id: str,
    slot_name: str,
    teacher_id: str,
    topic: str,
    template_id: str,
    topic_subcase: str | None,
    used_families: set[str],
) -> dict[str, Any] | None:
    options = section.get("options") or []
    if not options:
        return None

    candidates = [
        option for option in options
        if _option_allowed(
            option,
            template_id=template_id,
            topic_subcase=topic_subcase,
            used_families=used_families,
        )
    ]
    if not candidates:
        default_id = section.get("default_id")
        if default_id:
            for option in options:
                if option.get("id") == default_id:
                    candidates = [option]
                    break
        if not candidates:
            candidates = [options[0]]

    idx = _stable_index(f"{article_id}|{slot_name}|{teacher_id}|{topic}", len(candidates))
    chosen = candidates[idx]
    meta = _metadata_for(chosen)
    family = meta.get("semantic_family")
    if family:
        used_families.add(str(family))
    return chosen


def _render_teacher_perspective(option: dict[str, Any]) -> str:
    paragraphs = option.get("paragraphs") or []
    if paragraphs:
        return "\n\n".join(str(p).strip() for p in paragraphs if str(p).strip())
    return str(option.get("line") or "").strip()


def _build_forward_look(pack: dict[str, Any], cta_option: dict[str, Any] | None) -> str:
    parts: list[str] = []
    primary = ((pack.get("sdg") or {}).get("primary") or {}).get("line")
    if primary:
        parts.append(str(primary).strip())
    if cta_option and cta_option.get("line"):
        parts.append(str(cta_option["line"]).strip())
    fallback = ((pack.get("cta") or {}).get("fallback") or {}).get("line")
    if fallback:
        parts.append(str(fallback).strip())
    return "\n\n".join(part for part in parts if part)


def _title_line(
    section: dict[str, Any],
    *,
    article_id: str,
    slot_name: str,
    teacher_id: str,
    topic: str,
    template_id: str = "hard_news_spiritual_response",
) -> str:
    option = _select_option(
        section,
        article_id=article_id,
        slot_name=slot_name,
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=None,
        used_families=set(),
    )
    return str((option or {}).get("line") or "").strip()


def _validate_beat_map(beat_map: dict[str, Any], *, forbidden_rules: dict[str, tuple[str, str]]) -> None:
    sequence = [str(slot).strip() for slot in beat_map.get("sequence") or [] if str(slot).strip()]
    constraints = beat_map.get("constraints") or {}
    required = [str(slot).strip() for slot in constraints.get("requires") or [] if str(slot).strip()]
    missing = [slot for slot in required if slot not in sequence]
    if missing:
        raise ValueError(f"Beat map {beat_map.get('id')} missing required slots: {missing}")

    positions = {slot: idx for idx, slot in enumerate(sequence)}
    for forbid in constraints.get("forbids") or []:
        pair = forbidden_rules.get(str(forbid).strip())
        if not pair:
            continue
        left, right = pair
        if left in positions and right in positions and positions[left] < positions[right]:
            raise ValueError(
                f"Beat map {beat_map.get('id')} violates {forbid}: {left} appears before {right}"
            )


def _apply_transition_prefix(slot_text: str, transition_line: str) -> str:
    transition_line = (transition_line or "").strip()
    slot_text = (slot_text or "").strip()
    if not transition_line:
        return slot_text
    if not slot_text:
        return transition_line
    return f"{transition_line}\n\n{slot_text}"


def _render_option_text(option: dict[str, Any] | None) -> str:
    option = option or {}
    paragraphs = option.get("paragraphs") or []
    if paragraphs:
        return "\n\n".join(str(p).strip() for p in paragraphs if str(p).strip())
    line = str(option.get("line") or "").strip()
    return line


def _render_structured_option(option: dict[str, Any] | None) -> str:
    option = option or {}
    parts: list[str] = []
    header = str(option.get("header") or "").strip()
    if header:
        parts.append(header)
    paragraphs = option.get("paragraphs") or []
    for paragraph in paragraphs:
        text = str(paragraph).strip()
        if text:
            parts.append(text)
    items = option.get("items") or []
    if items:
        bullet_block = "\n".join(f"- {str(item).strip()}" for item in items if str(item).strip())
        if bullet_block:
            parts.append(bullet_block)
    closing_line = str(option.get("closing_line") or "").strip()
    if closing_line:
        parts.append(closing_line)
    if parts:
        return "\n\n".join(parts)
    return _render_option_text(option)


def build_hard_news_deterministic_plan(
    item: dict[str, Any],
    repo_root: Path,
    *,
    forced_map_id: str | None = None,
) -> dict[str, Any] | None:
    teacher = item.get("_teacher_resolved") or {}
    teacher_id = teacher.get("teacher_id")
    topic = _normalize_topic(item.get("topic") or "")
    if not teacher_id or not topic:
        return None

    pack = load_teacher_topic_pack(repo_root, teacher_id, topic, "hard_news_spiritual_response")
    if not pack or not pack.get("active", True):
        return None

    beat_map_config = load_beat_map_config(repo_root, "hard_news_spiritual_response")
    beat_map = select_beat_map(
        beat_map_config,
        article_id=item.get("id") or item.get("title") or "default",
        topic=topic,
        forced_map_id=forced_map_id,
    )
    if not beat_map:
        return None
    _validate_beat_map(beat_map, forbidden_rules=_FORBIDDEN_HARD_NEWS_BEAT_MAP_RULES)

    article_id = item.get("id") or item.get("title") or "default"
    template_id = "hard_news_spiritual_response"
    topic_subcase = item.get("topic_subcase")
    used_families: set[str] = set()

    intro = _select_option(
        pack.get("teacher_intro") or {},
        article_id=article_id,
        slot_name="teacher_intro",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    hook_personal = _select_option(
        pack.get("hook_personal") or {},
        article_id=article_id,
        slot_name="hook_personal",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    youth_somatic = _select_option(
        pack.get("youth_somatic") or {},
        article_id=article_id,
        slot_name="youth_somatic",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    witness = _select_option(
        pack.get("teacher_witness") or {},
        article_id=article_id,
        slot_name="teacher_witness",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    turnaround = _select_option(
        pack.get("turnaround") or {},
        article_id=article_id,
        slot_name="turnaround",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    bridge = _select_option(
        pack.get("bridge") or {},
        article_id=article_id,
        slot_name="bridge",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    perspective = _select_option(
        pack.get("teacher_perspective") or {},
        article_id=article_id,
        slot_name="teacher_perspective",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    practice = _select_option(
        pack.get("practice") or {},
        article_id=article_id,
        slot_name="practice_announce",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    hook_personal = _select_option(
        pack.get("hook_personal") or {},
        article_id=article_id,
        slot_name="hook_personal",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    hook_big_picture = _select_option(
        pack.get("hook_big_picture") or {},
        article_id=article_id,
        slot_name="hook_big_picture",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    cta = _select_option(
        pack.get("cta") or {},
        article_id=article_id,
        slot_name="cta",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )

    slots = {
        "headline_layer_1": _title_line(pack.get("title_system", {}).get("headline_layer_1", {}), article_id=article_id, slot_name="headline_layer_1", teacher_id=teacher_id, topic=topic),
        "headline_layer_2": _title_line(pack.get("title_system", {}).get("headline_layer_2", {}), article_id=article_id, slot_name="headline_layer_2", teacher_id=teacher_id, topic=topic),
        "hook_personal": str((hook_personal or {}).get("line") or "").strip(),
        "hook_big_picture": str((hook_big_picture or {}).get("line") or "").strip(),
        "teacher_intro": str((intro or {}).get("line") or "").strip(),
        "youth_somatic": str((youth_somatic or {}).get("line") or "").strip(),
        "teacher_witness": str((witness or {}).get("line") or "").strip(),
        "turnaround": "\n\n".join(
            part for part in [
                str((turnaround or {}).get("stat_line_1") or "").strip(),
                str((turnaround or {}).get("stat_line_2") or "").strip(),
            ] if part
        ),
        "bridge": str((bridge or {}).get("line") or "").strip(),
        "teacher_perspective": _render_teacher_perspective(perspective or {}),
        "practice_announce": str((practice or {}).get("announcement_line") or "").strip(),
        "sdg_un_tie": str((((pack.get("sdg") or {}).get("fallback_un_tie") or {}).get("line")) or "").strip(),
        "forward_look": _build_forward_look(pack, cta),
    }

    selected_transitions: dict[str, dict[str, str]] = {}
    for boundary_key, family_id in (beat_map.get("transitions") or {}).items():
        target_slot = str(boundary_key).replace("before_", "", 1).strip()
        transition_section = (pack.get("transitions") or {}).get(str(family_id).strip()) or {}
        transition_option = _select_option(
            transition_section,
            article_id=article_id,
            slot_name=f"transition:{boundary_key}",
            teacher_id=teacher_id,
            topic=topic,
            template_id=template_id,
            topic_subcase=topic_subcase,
            used_families=used_families,
        )
        transition_line = str((transition_option or {}).get("line") or "").strip()
        if not transition_line or not target_slot:
            continue
        slots[target_slot] = _apply_transition_prefix(slots.get(target_slot, ""), transition_line)
        selected_transitions[boundary_key] = {
            "family_id": str(family_id).strip(),
            "target_slot": target_slot,
            "line": transition_line,
        }
    slots = {key: value for key, value in slots.items() if value}

    ordered_sections: list[dict[str, Any]] = []
    for slot in beat_map.get("sequence") or []:
        source = "prompted" if slot in PROMPTED_HARD_NEWS_SLOTS else "deterministic"
        content = slots.get(slot, "")
        ordered_sections.append({
            "slot": slot,
            "source": source,
            "content": content,
        })

    return {
        "slots": slots,
        "beat_map_id": beat_map.get("id"),
        "beat_map_sequence": beat_map.get("sequence") or [],
        "ordered_sections": ordered_sections,
        "selected_transitions": selected_transitions,
        "pack_path": str(PACKS_ROOT / "teachers" / teacher_id / f"{topic}.yaml"),
        "teacher_id": teacher_id,
        "topic": topic,
    }


def build_commentary_deterministic_plan(
    item: dict[str, Any],
    repo_root: Path,
    *,
    forced_map_id: str | None = None,
) -> dict[str, Any] | None:
    teacher = item.get("_teacher_resolved") or {}
    teacher_id = teacher.get("teacher_id")
    topic = _normalize_topic(item.get("topic") or "")
    if not teacher_id or not topic:
        return None

    pack = load_teacher_topic_pack(repo_root, teacher_id, topic, "commentary")
    if not pack or not pack.get("active", True):
        return None

    beat_map_config = load_beat_map_config(repo_root, "commentary")
    beat_map = select_beat_map(
        beat_map_config,
        article_id=item.get("id") or item.get("title") or "default",
        topic=topic,
        forced_map_id=forced_map_id,
    )
    if not beat_map:
        return None
    _validate_beat_map(beat_map, forbidden_rules=_FORBIDDEN_COMMENTARY_BEAT_MAP_RULES)

    article_id = item.get("id") or item.get("title") or "default"
    template_id = "commentary"
    topic_subcase = item.get("topic_subcase")
    used_families: set[str] = set()

    intro = _select_option(
        pack.get("teacher_intro") or {},
        article_id=article_id,
        slot_name="teacher_intro",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    youth_somatic = _select_option(
        pack.get("youth_somatic") or {},
        article_id=article_id,
        slot_name="youth_somatic",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    witness = _select_option(
        pack.get("teacher_witness") or {},
        article_id=article_id,
        slot_name="teacher_witness",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    turnaround = _select_option(
        pack.get("turnaround") or {},
        article_id=article_id,
        slot_name="turnaround",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    bridge = _select_option(
        pack.get("bridge") or {},
        article_id=article_id,
        slot_name="bridge",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    perspective = _select_option(
        pack.get("teaching_interpretation") or pack.get("teacher_perspective") or {},
        article_id=article_id,
        slot_name="teacher_perspective",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    practice = _select_option(
        pack.get("practice") or {},
        article_id=article_id,
        slot_name="practice_announce",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    thesis = _select_option(
        pack.get("thesis") or {},
        article_id=article_id,
        slot_name="thesis",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    civic = _select_option(
        pack.get("civic_recommendation") or {},
        article_id=article_id,
        slot_name="civic_recommendation",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )

    sdg_primary = (((pack.get("sdg") or {}).get("primary") or {}).get("line") or "").strip()
    sdg_fallback = (((pack.get("sdg") or {}).get("fallback_un_tie") or {}).get("line") or "").strip()
    sdg_text = "\n\n".join(part for part in [sdg_primary, sdg_fallback] if part)

    slots = {
        "headline_layer_1": "",
        "headline_layer_2": _title_line(
            pack.get("headline_layer_2") or pack.get("title_system", {}).get("headline_layer_2", {}),
            article_id=article_id,
            slot_name="headline_layer_2",
            teacher_id=teacher_id,
            topic=topic,
        ),
        "hook_personal": _render_option_text(thesis),
        "hook_big_picture": "",
        "news_peg": "",
        "teacher_intro": _render_option_text(intro),
        "youth_somatic": _render_option_text(youth_somatic),
        "teacher_witness": _render_option_text(witness),
        "body_data": "",
        "turnaround": _render_option_text(turnaround),
        "bridge": _render_option_text(bridge),
        "teacher_perspective": _render_teacher_perspective(perspective or {}),
        "practice_announce": str((practice or {}).get("announcement_line") or "").strip(),
        "sdg_un_tie": sdg_text,
        "forward_look": _render_option_text(civic),
    }
    slots = {key: value for key, value in slots.items() if value or key in PROMPTED_COMMENTARY_SLOTS}

    ordered_sections: list[dict[str, Any]] = []
    for slot in beat_map.get("sequence") or []:
        mapped_slot = {
            "thesis": "hook_personal",
            "event_reference": "news_peg",
            "teaching_interpretation": "teacher_perspective",
            "civic_recommendation": "forward_look",
            "sdg_reference": "sdg_un_tie",
        }.get(slot, slot)
        source = "prompted" if mapped_slot in PROMPTED_COMMENTARY_SLOTS else "deterministic"
        ordered_sections.append(
            {"slot": mapped_slot, "source": source, "content": slots.get(mapped_slot, "")}
        )

    return {
        "slots": slots,
        "beat_map_id": beat_map.get("id"),
        "beat_map_sequence": beat_map.get("sequence") or [],
        "ordered_sections": ordered_sections,
        "pack_path": str(PACKS_ROOT / "teachers" / teacher_id / f"{topic}.yaml"),
        "teacher_id": teacher_id,
        "topic": topic,
    }


PROMPTED_UNSAY_SLOTS = {"headline_layer_1", "event_summary", "news_peg", "body_data"}


def build_unsay_deterministic_plan(item: dict[str, Any], repo_root: Path) -> dict[str, Any] | None:
    """Build deterministic plan from UNSAY pair-pack. No prompt fallback for teacher meaning."""
    resolved = item.get("_teacher_resolved") or item.get("_unsay_pair") or {}
    teacher_a_id = (resolved.get("teacher_a_id") or "").strip()
    teacher_b_id = (resolved.get("teacher_b_id") or "").strip()
    topic = _normalize_topic(item.get("topic") or "")
    if not teacher_a_id or not teacher_b_id or teacher_a_id == teacher_b_id or not topic:
        return None

    pack = load_unsay_pair_pack(repo_root, teacher_a_id, teacher_b_id, topic)
    if not pack:
        return None

    article_id = item.get("id") or item.get("title") or "default"
    pair_id = f"{teacher_a_id}_{teacher_b_id}"
    template_id = "unsay_dialogue"
    used_families: set[str] = set()

    def _pick(section_key: str) -> dict[str, Any] | None:
        section = pack.get(section_key) or {}
        return _select_option(
            section,
            article_id=article_id,
            slot_name=section_key,
            teacher_id=pair_id,
            topic=topic,
            template_id=template_id,
            topic_subcase=None,
            used_families=used_families,
        )

    opt_a_diag = _pick("teacher_a_diagnosis")
    opt_b_diag = _pick("teacher_b_diagnosis")
    opt_conv = _pick("convergence_bridge")
    opt_agree = _pick("shared_agreement")
    opt_practice = _pick("practice_announce")
    opt_why_a = _pick("practice_why_a")
    opt_why_b = _pick("practice_why_b")
    opt_boundary = _pick("disagreement_boundary")

    practice_announce_text = ""
    if opt_practice:
        practice_announce_text = str(
            opt_practice.get("announcement_line")
            or opt_practice.get("line")
            or ""
        ).strip()

    slots = {
        "teacher_a_perspective": str((opt_a_diag or {}).get("line") or "").strip(),
        "teacher_b_perspective": str((opt_b_diag or {}).get("line") or "").strip(),
        "convergence_bridge": str((opt_conv or {}).get("line") or "").strip(),
        "shared_agreement": str((opt_agree or {}).get("line") or "").strip(),
        "practice_announce": practice_announce_text,
        "practice_why_a": str((opt_why_a or {}).get("line") or "").strip(),
        "practice_why_b": str((opt_why_b or {}).get("line") or "").strip(),
        "disagreement_boundary": str((opt_boundary or {}).get("line") or "").strip(),
    }

    sequence = [
        "headline_layer_1",
        "headline_layer_2",
        "hook_personal",
        "news_peg",
        "youth_somatic",
        "body_data",
        "teacher_a_intro",
        "teacher_a_perspective",
        "teacher_b_intro",
        "teacher_b_perspective",
        "convergence_bridge",
        "shared_agreement",
        "practice_announce",
        "practice_why_a",
        "practice_why_b",
        "disagreement_boundary",
        "forward_look",
    ]
    ordered_sections = []
    for slot in sequence:
        source = "prompted" if slot in PROMPTED_UNSAY_SLOTS else "deterministic"
        ordered_sections.append({
            "slot": slot,
            "source": source,
            "content": slots.get(slot, ""),
        })

    pack_path = str(UNSAY_PAIRS_ROOT / f"{teacher_a_id}__{teacher_b_id}__{topic}.yaml")
    return {
        "slots": slots,
        "beat_map_id": None,
        "beat_map_sequence": sequence,
        "ordered_sections": ordered_sections,
        "pack_path": pack_path,
        "teacher_id": pair_id,
        "teacher_a_id": teacher_a_id,
        "teacher_b_id": teacher_b_id,
        "topic": topic,
    }


def build_explainer_deterministic_plan(
    item: dict[str, Any],
    repo_root: Path,
    *,
    forced_map_id: str | None = None,
) -> dict[str, Any] | None:
    """Build deterministic plan for explainer_context from base pack + overlay.

    Uses existing overlays only. Prompted slots: headline_layer_1, what_happened,
    historical_background, body_data, future_outlook. All teacher meaning is deterministic.
    """
    teacher = item.get("_teacher_resolved") or {}
    teacher_id = teacher.get("teacher_id")
    topic = _normalize_topic(item.get("topic") or "")
    if not teacher_id or not topic:
        return None

    pack = load_teacher_topic_pack(repo_root, teacher_id, topic, "explainer_context")
    if not pack or not pack.get("active", True):
        return None

    beat_map_config = load_beat_map_config(repo_root, "explainer_context")
    beat_map = select_beat_map(
        beat_map_config,
        article_id=item.get("id") or item.get("title") or "default",
        topic=topic,
        forced_map_id=forced_map_id,
    )
    if not beat_map:
        return None
    _validate_beat_map(beat_map, forbidden_rules=_FORBIDDEN_EXPLAINER_BEAT_MAP_RULES)

    article_id = item.get("id") or item.get("title") or "default"
    template_id = "explainer_context"
    topic_subcase = item.get("topic_subcase")
    used_families: set[str] = set()

    headline_layer_2_section = pack.get("title_system") or {}
    headline_layer_2_section = headline_layer_2_section.get("headline_layer_2") or pack.get("headline_layer_2") or {}
    headline_layer_2 = _title_line(
        headline_layer_2_section,
        article_id=article_id,
        slot_name="headline_layer_2",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
    )

    intro = _select_option(
        pack.get("teacher_intro") or {},
        article_id=article_id,
        slot_name="teacher_intro",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    hook_personal = _select_option(
        pack.get("hook_personal") or {},
        article_id=article_id,
        slot_name="hook_personal",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    youth_somatic = _select_option(
        pack.get("youth_somatic") or {},
        article_id=article_id,
        slot_name="youth_somatic",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    witness = _select_option(
        pack.get("teacher_witness") or {},
        article_id=article_id,
        slot_name="teacher_witness",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    turnaround = _select_option(
        pack.get("turnaround") or {},
        article_id=article_id,
        slot_name="turnaround",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    bridge = _select_option(
        pack.get("bridge") or {},
        article_id=article_id,
        slot_name="bridge",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    perspective = _select_option(
        pack.get("teacher_perspective") or {},
        article_id=article_id,
        slot_name="teacher_perspective",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    cta = _select_option(
        pack.get("cta") or {},
        article_id=article_id,
        slot_name="cta",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    ethical = _select_option(
        pack.get("ethical_spiritual_dimension") or {},
        article_id=article_id,
        slot_name="ethical_spiritual_dimension",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    practice = _select_option(
        pack.get("practice") or {},
        article_id=article_id,
        slot_name="practice_announce",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    youth_impl_section = pack.get("youth_implications") or {}
    youth_impl_options = youth_impl_section.get("options") or []
    youth_implications = ""
    if youth_impl_options:
        youth_impl_opt = _select_option(
            youth_impl_section,
            article_id=article_id,
            slot_name="youth_implications",
            teacher_id=teacher_id,
            topic=topic,
            template_id=template_id,
            topic_subcase=topic_subcase,
            used_families=used_families,
        )
        youth_implications = str((youth_impl_opt or {}).get("line") or "").strip()

    sdg_policy_section = pack.get("sdg_policy_tie") or {}
    sdg_policy_options = sdg_policy_section.get("options") or []
    if sdg_policy_options:
        sdg_policy_opt = _select_option(
            sdg_policy_section,
            article_id=article_id,
            slot_name="sdg_policy_tie",
            teacher_id=teacher_id,
            topic=topic,
            template_id=template_id,
            topic_subcase=topic_subcase,
            used_families=used_families,
        )
        sdg_policy_tie = str((sdg_policy_opt or {}).get("line") or "").strip()
    else:
        sdg_policy_tie = str((((pack.get("sdg") or {}).get("primary") or {}).get("line")) or "").strip()
    sdg_un_tie = str((((pack.get("sdg") or {}).get("fallback_un_tie") or {}).get("line")) or "").strip()

    turnaround_text = "\n\n".join(
        part for part in [
            str((turnaround or {}).get("stat_line_1") or "").strip(),
            str((turnaround or {}).get("stat_line_2") or "").strip(),
        ] if part
    )

    slots = {
        "hook_personal": _render_option_text(hook_personal),
        "headline_layer_2": headline_layer_2,
        "teacher_intro": str((intro or {}).get("line") or "").strip(),
        "youth_somatic": _render_option_text(youth_somatic),
        "teacher_witness": str((witness or {}).get("line") or "").strip(),
        "turnaround": turnaround_text,
        "bridge": str((bridge or {}).get("line") or "").strip(),
        "teacher_perspective": _render_teacher_perspective(perspective or {}),
        "ethical_spiritual_dimension": _render_teacher_perspective(ethical or {}),
        "practice_announce": str((practice or {}).get("announcement_line") or "").strip(),
        "sdg_policy_tie": sdg_policy_tie,
        "sdg_un_tie": sdg_un_tie,
        "forward_look": _build_forward_look(pack, cta),
    }
    if youth_implications:
        slots["youth_implications"] = youth_implications
    slots = {k: v for k, v in slots.items() if v}

    ordered_sections = []
    for slot in beat_map.get("sequence") or []:
        source = "prompted" if slot in PROMPTED_EXPLAINER_SLOTS else "deterministic"
        ordered_sections.append({
            "slot": slot,
            "source": source,
            "content": slots.get(slot, ""),
        })

    overlay_path = repo_root / PACKS_ROOT / "overlays" / "explainer_context" / f"{teacher_id}__{topic}.yaml"
    pack_path = str(overlay_path) if overlay_path.exists() else str(PACKS_ROOT / "teachers" / teacher_id / f"{topic}.yaml")

    return {
        "slots": slots,
        "beat_map_id": beat_map.get("id"),
        "beat_map_sequence": beat_map.get("sequence") or [],
        "ordered_sections": ordered_sections,
        "pack_path": pack_path,
        "teacher_id": teacher_id,
        "topic": topic,
    }


def build_youth_feature_deterministic_plan(
    item: dict[str, Any],
    repo_root: Path,
    *,
    forced_map_id: str | None = None,
) -> dict[str, Any] | None:
    """Build deterministic plan for youth_feature from base pack + overlay.

    Prompted slots stay limited to factual compression / youth scene framing.
    Teacher meaning, bridge, reflection, practice, solutions, and SDG framing
    come from deterministic packs and overlays.
    """
    teacher = item.get("_teacher_resolved") or {}
    teacher_id = teacher.get("teacher_id")
    topic = _normalize_topic(item.get("topic") or "")
    if not teacher_id or not topic:
        return None

    pack = load_teacher_topic_pack(repo_root, teacher_id, topic, "youth_feature")
    if not pack or not pack.get("active", True):
        return None

    beat_map_config = load_beat_map_config(repo_root, "youth_feature")
    beat_map = select_beat_map(
        beat_map_config,
        article_id=item.get("id") or item.get("title") or "default",
        topic=topic,
        forced_map_id=forced_map_id,
    )
    if not beat_map:
        return None
    _validate_beat_map(beat_map, forbidden_rules=_FORBIDDEN_YOUTH_FEATURE_BEAT_MAP_RULES)

    article_id = item.get("id") or item.get("title") or "default"
    template_id = "youth_feature"
    topic_subcase = item.get("topic_subcase")
    used_families: set[str] = set()

    headline_layer_2_section = pack.get("title_system") or {}
    headline_layer_2_section = headline_layer_2_section.get("headline_layer_2") or pack.get("headline_layer_2") or {}
    headline_layer_2 = _title_line(
        headline_layer_2_section,
        article_id=article_id,
        slot_name="headline_layer_2",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
    )

    intro = _select_option(
        pack.get("teacher_intro") or {},
        article_id=article_id,
        slot_name="teacher_intro",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    hook_personal = _select_option(
        pack.get("hook_personal") or {},
        article_id=article_id,
        slot_name="hook_personal",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    hook_big_picture = _select_option(
        pack.get("hook_big_picture") or {},
        article_id=article_id,
        slot_name="hook_big_picture",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    youth_somatic = _select_option(
        pack.get("youth_somatic") or {},
        article_id=article_id,
        slot_name="youth_somatic",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    witness = _select_option(
        pack.get("teacher_witness") or {},
        article_id=article_id,
        slot_name="teacher_witness",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    turnaround = _select_option(
        pack.get("turnaround") or {},
        article_id=article_id,
        slot_name="turnaround",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    bridge = _select_option(
        pack.get("bridge") or {},
        article_id=article_id,
        slot_name="bridge",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    reflection = _select_option(
        pack.get("teacher_reflection") or {},
        article_id=article_id,
        slot_name="teacher_reflection",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    practice = _select_option(
        pack.get("practice") or {},
        article_id=article_id,
        slot_name="practice_announce",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )
    solutions = _select_option(
        pack.get("solutions") or {},
        article_id=article_id,
        slot_name="solutions",
        teacher_id=teacher_id,
        topic=topic,
        template_id=template_id,
        topic_subcase=topic_subcase,
        used_families=used_families,
    )

    sdg_framework = str((((pack.get("sdg") or {}).get("primary") or {}).get("line")) or "").strip()
    sdg_un_tie = str((((pack.get("sdg") or {}).get("fallback_un_tie") or {}).get("line")) or "").strip()
    sdg_text = "\n\n".join(part for part in [sdg_framework, sdg_un_tie] if part)
    turnaround_text = "\n\n".join(
        part for part in [
            str((turnaround or {}).get("stat_line_1") or "").strip(),
            str((turnaround or {}).get("stat_line_2") or "").strip(),
        ] if part
    )

    slots = {
        "headline_layer_1": "",
        "headline_layer_2": headline_layer_2,
        "hook_personal": _render_option_text(hook_personal),
        "hook_big_picture": _render_option_text(hook_big_picture),
        "news_peg": "",
        "teacher_intro": str((intro or {}).get("line") or "").strip(),
        "youth_somatic": _render_option_text(youth_somatic),
        "teacher_witness": _render_option_text(witness),
        "body_data": "",
        "turnaround": turnaround_text,
        "bridge": _render_option_text(bridge),
        "teacher_perspective": _render_structured_option(reflection),
        "practice_announce": str((practice or {}).get("announcement_line") or "").strip(),
        "sdg_un_tie": sdg_text,
        "forward_look": _render_structured_option(solutions),
    }
    slots = {k: v for k, v in slots.items() if v or k in PROMPTED_YOUTH_FEATURE_SLOTS}

    ordered_sections = []
    for slot in beat_map.get("sequence") or []:
        mapped_slot = {
            "youth_narrative": "hook_personal",
            "data_research": "body_data",
            "teacher_reflection": "teacher_perspective",
            "practice_bridge": "bridge",
            "solutions": "forward_look",
            "sdg_framework": "sdg_un_tie",
        }.get(slot, slot)
        source = "prompted" if mapped_slot in PROMPTED_YOUTH_FEATURE_SLOTS else "deterministic"
        ordered_sections.append({
            "slot": mapped_slot,
            "source": source,
            "content": slots.get(mapped_slot, ""),
        })

    overlay_path = repo_root / PACKS_ROOT / "overlays" / "youth_feature" / f"{teacher_id}__{topic}.yaml"
    pack_path = str(overlay_path) if overlay_path.exists() else str(PACKS_ROOT / "teachers" / teacher_id / f"{topic}.yaml")

    return {
        "slots": slots,
        "beat_map_id": beat_map.get("id"),
        "beat_map_sequence": beat_map.get("sequence") or [],
        "ordered_sections": ordered_sections,
        "pack_path": pack_path,
        "teacher_id": teacher_id,
        "topic": topic,
    }


def build_interfaith_deterministic_plan(item: dict[str, Any], repo_root: Path) -> dict[str, Any] | None:
    """Build deterministic plan for interfaith_dialogue_report from a pair-pack.

    Item must have _interfaith_pair_resolved: { teacher_a_id, teacher_b_id } and topic.
    Deterministic slots: leaders_present, themes_discussed, youth_commitments,
    sdg_alignment, convergence, distinction, next_steps.
    No fallback to single-teacher or prompt for teacher meaning.
    """
    pair = item.get("_interfaith_pair_resolved") or {}
    teacher_a_id = (pair.get("teacher_a_id") or "").strip()
    teacher_b_id = (pair.get("teacher_b_id") or "").strip()
    topic = _normalize_topic(item.get("topic") or "")
    if not teacher_a_id or not teacher_b_id or teacher_a_id == teacher_b_id or not topic:
        return None

    pack = load_interfaith_pair_pack(repo_root, teacher_a_id, teacher_b_id, topic)
    if not pack:
        return None

    article_id = item.get("id") or item.get("title") or "default"
    template_id = "interfaith_dialogue_report"
    pair_key = f"{teacher_a_id}_{teacher_b_id}"
    used_families: set[str] = set()

    def _pick(section_key: str) -> str:
        section = pack.get(section_key) or {}
        options = section.get("options") or []
        if not options:
            return ""
        candidates = [
            opt for opt in options
            if _option_allowed(
                opt,
                template_id=template_id,
                topic_subcase=None,
                used_families=used_families,
            )
        ]
        if not candidates:
            default_id = section.get("default_id")
            if default_id:
                for opt in options:
                    if opt.get("id") == default_id:
                        candidates = [opt]
                        break
            if not candidates:
                candidates = [options[0]]
        idx = _stable_index(f"{article_id}|{section_key}|{pair_key}|{topic}", len(candidates))
        chosen = candidates[idx]
        meta = _metadata_for(chosen)
        family = meta.get("semantic_family")
        if family:
            used_families.add(str(family))
        return str((chosen.get("line") or "").strip())

    leaders_present = _pick("leaders_present")
    themes_discussed = _pick("themes_discussed")
    youth_commitments = _pick("youth_commitments")
    sdg_alignment = _pick("sdg_alignment")
    convergence = _pick("convergence")
    distinction = _pick("distinction")
    next_steps = _pick("next_steps")

    slots = {
        "leaders_present": leaders_present,
        "themes_discussed": themes_discussed,
        "youth_commitments": youth_commitments,
        "sdg_alignment": sdg_alignment,
        "convergence": convergence,
        "distinction": distinction,
        "next_steps": next_steps,
    }
    slots = {k: v for k, v in slots.items() if v}

    interfaith_sequence = [
        "leaders_present",
        "themes_discussed",
        "youth_commitments",
        "sdg_alignment",
        "convergence",
        "distinction",
        "next_steps",
    ]
    ordered_sections = []
    for slot in interfaith_sequence:
        content = slots.get(slot, "")
        source = "prompted" if slot in PROMPTED_INTERFAITH_SLOTS else "deterministic"
        ordered_sections.append({"slot": slot, "source": source, "content": content})

    pack_filename = f"{teacher_a_id}__{teacher_b_id}__{topic}.yaml"
    pack_path = str(PAIRS_INTERFAITH_ROOT / pack_filename)
    if not (repo_root / PAIRS_INTERFAITH_ROOT / pack_filename).exists():
        pack_path = str(PAIRS_INTERFAITH_ROOT / f"{teacher_b_id}__{teacher_a_id}__{topic}.yaml")

    return {
        "slots": slots,
        "beat_map_id": None,
        "beat_map_sequence": [],
        "ordered_sections": ordered_sections,
        "pack_path": pack_path,
        "teacher_id": pair_key,
        "teacher_a_id": teacher_a_id,
        "teacher_b_id": teacher_b_id,
        "topic": topic,
    }
