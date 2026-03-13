#!/usr/bin/env python3
"""
Pearl News — Claude-powered article writer (replaces Qwen/LM Studio expansion).

Slot-by-slot article generation using the Anthropic API (Claude Sonnet).
Each slot uses the same prompts from pearl_news/prompts/slot_by_slot/ that were
designed for the original pipeline, but now Claude writes the content directly.

API key: read from ANTHROPIC_API_KEY env var or claude_api_key.rtf in repo root.
"""
from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)

from pearl_news.pipeline.deterministic_teacher_topic import (
    build_commentary_deterministic_plan,
    build_explainer_deterministic_plan,
    build_hard_news_deterministic_plan,
    build_interfaith_deterministic_plan,
    build_unsay_deterministic_plan,
    build_youth_feature_deterministic_plan,
)

STANDARD_V52_SLOTS: tuple[str, ...] = (
    "headline_layer_1", "headline_layer_2",
    "hook_personal", "hook_big_picture",
    "news_peg", "teacher_intro",
    "youth_somatic", "teacher_witness", "body_data",
    "turnaround", "bridge",
    "teacher_perspective", "practice_announce",
    "forward_look",
)

# ── Slot definitions per template ──
TEMPLATE_SLOTS: dict[str, tuple[str, ...]] = {
    "hard_news_spiritual_response": (
        "headline", "news_summary", "youth_impact",
        "teacher_perspective", "sdg_un_tie", "forward_look",
    ),
    "commentary": (
        "headline", "thesis", "teaching_interpretation",
        "civic_recommendation", "sdg_reference",
    ),
    "interfaith_dialogue_report": (
        "headline", "event_summary", "leaders_present",
        "themes_discussed", "youth_commitments",
        "sdg_alignment", "next_steps",
    ),
    "explainer_context": (
        "headline", "what_happened", "historical_background",
        "ethical_spiritual_dimension", "youth_implications",
        "sdg_policy_tie", "future_outlook",
    ),
    "youth_feature": (
        "headline", "youth_narrative", "data_research",
        "teacher_reflection", "sdg_framework", "solutions",
    ),
}

# Maps template-specific slots to v5.2 standard 6-slot names
V52_SLOT_MAP: dict[str, dict[str, str]] = {
    "hard_news_spiritual_response": {
        "headline": "headline",
        "news_summary": "news_summary",
        "youth_impact": "youth_impact",
        "teacher_perspective": "teacher_perspective",
        "sdg_un_tie": "sdg_un_tie",
        "forward_look": "forward_look",
    },
    "commentary": {
        "headline": "headline",
        "thesis": "news_summary",
        "teaching_interpretation": "teacher_perspective",
        "civic_recommendation": "forward_look",
        "sdg_reference": "sdg_un_tie",
    },
    "interfaith_dialogue_report": {
        "headline": "headline",
        "event_summary": "news_summary",
        "themes_discussed": "teacher_perspective",
        "youth_commitments": "youth_impact",
        "sdg_alignment": "sdg_un_tie",
        "next_steps": "forward_look",
    },
    "explainer_context": {
        "headline": "headline",
        "what_happened": "news_summary",
        "ethical_spiritual_dimension": "teacher_perspective",
        "youth_implications": "youth_impact",
        "sdg_policy_tie": "sdg_un_tie",
        "future_outlook": "forward_look",
    },
    "youth_feature": {
        "headline": "headline",
        "youth_narrative": "news_summary",
        "data_research": "youth_impact",
        "teacher_reflection": "teacher_perspective",
        "sdg_framework": "sdg_un_tie",
        "solutions": "forward_look",
    },
}

# Interfaith: deterministic from pair-pack except headline and event_summary
INTERFAITH_SLOTS: tuple[str, ...] = (
    "headline_layer_1",
    "event_summary",
    "leaders_present",
    "themes_discussed",
    "youth_commitments",
    "sdg_alignment",
    "convergence",
    "distinction",
    "next_steps",
)

# Explainer uses the standard rendered/gated slots plus explainer-specific extras.
EXPLAINER_V52_SLOTS: tuple[str, ...] = (
    "headline_layer_1",
    "headline_layer_2",
    "hook_personal",
    "news_peg",
    "youth_somatic",
    "body_data",
    "teacher_intro",
    "teacher_witness",
    "turnaround",
    "bridge",
    "teacher_perspective",
    "practice_announce",
    "forward_look",
)

EXPLAINER_OPTIONAL_V52_SLOTS: tuple[str, ...] = (
    "what_happened",
    "historical_background",
    "ethical_spiritual_dimension",
    "youth_implications",
    "future_outlook",
    "sdg_policy_tie",
    "sdg_un_tie",
)

# v5.2 Editorial Spec: 14-prompt architecture
TEMPLATE_SLOTS_V52: dict[str, tuple[str, ...]] = {
    "hard_news_spiritual_response": STANDARD_V52_SLOTS,
    "commentary": STANDARD_V52_SLOTS,
    "interfaith_dialogue_report": INTERFAITH_SLOTS,
    "explainer_context": EXPLAINER_V52_SLOTS,
    "youth_feature": STANDARD_V52_SLOTS,
}

# Maps 14-slot architecture back to legacy 6-slot names for backward compatibility
V52_TO_LEGACY_MAP = {
    "headline_layer_1": "headline",
    "headline_layer_2": "headline_layer_2",  # new field
    "hook_personal": "hook_personal",  # new field
    "hook_big_picture": "hook_big_picture",  # new field
    "news_peg": "news_peg",  # new field
    "teacher_intro": "teacher_intro",  # new field
    "youth_somatic": "youth_somatic",  # new field
    "teacher_witness": "teacher_witness",  # new field
    "body_data": "body_data",  # new field
    "turnaround": "turnaround",  # new field
    "bridge": "bridge",  # new field
    "teacher_perspective": "teacher_perspective",
    "practice_announce": "practice_announce",  # new field
    "forward_look": "forward_look",
}

OPTIONAL_V52_SLOTS: dict[str, tuple[str, ...]] = {
    "hard_news_spiritual_response": ("sdg_un_tie",),
    "commentary": ("sdg_un_tie",),
    "interfaith_dialogue_report": ("sdg_un_tie",),
    "explainer_context": EXPLAINER_OPTIONAL_V52_SLOTS,
    "youth_feature": ("sdg_un_tie",),
}


# ── API key loader ──
def _load_api_key() -> str:
    """Load Anthropic API key from env or claude_api_key.rtf."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key

    repo_root = Path(__file__).resolve().parents[2]
    rtf_path = repo_root / "claude_api_key.rtf"
    if rtf_path.exists():
        raw = rtf_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"sk-ant-[a-zA-Z0-9_-]{20,}", raw)
        if m:
            return m.group(0)

    return ""


# ── Prompt loader ──
def _load_slot_prompt(prompts_root: Path, template_id: str, slot_name: str) -> str:
    path = prompts_root / "slot_by_slot" / template_id / f"{slot_name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _load_system_prompt(prompts_root: Path) -> str:
    docs_path = prompts_root.parent.parent / "docs" / "pearl_news_prompts" / "00_SYSTEM_PROMPT.md"
    if docs_path.exists():
        return docs_path.read_text(encoding="utf-8").strip()
    path = prompts_root / "expansion_system.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return (
        "You are an editor for Pearl News. Write publish-grade journalism for Gen Z readers. "
        "Output only the requested content, no preamble or explanation."
    )


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def _render_prompt(template: str, context: dict[str, Any]) -> str:
    return template.format_map(_SafeDict({k: ("" if v is None else str(v)) for k, v in context.items()}))


_SLOT_FORMAT_PREFIXES: dict[str, tuple[str, ...]] = {
    "hook_personal": ("HEADER:", "HOOK:"),
    "hook_big_picture": ("HEADER:", "BIG_PICTURE:"),
    "news_peg": ("HEADER:", "PEG:"),
    "teacher_perspective": ("HEADER:",),
    "youth_somatic": ("HEADER:",),
    "teacher_witness": ("HEADER:",),
}


def _clean_slot_output(slot: str, text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return ""
    if cleaned.upper() == "READY":
        return ""

    prefixes = _SLOT_FORMAT_PREFIXES.get(slot)
    if not prefixes:
        return cleaned

    kept: list[str] = []
    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(line.upper().startswith(prefix) for prefix in prefixes):
            for prefix in prefixes:
                if line.upper().startswith(prefix):
                    remainder = line[len(prefix):].strip()
                    if prefix != "HEADER:" and remainder:
                        kept.append(remainder)
                    break
            continue
        kept.append(line)
    return "\n\n".join(part for part in kept if part).strip()


def _short_text(value: str | None, *, max_chars: int) -> str:
    text = (value or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].strip().rstrip(" ,.;:") + "..."


def _teacher_quotes_text(teacher: dict[str, Any] | None, *, max_items: int = 2, max_chars: int = 320) -> str:
    atoms = ((teacher or {}).get("atoms") or [])[:max_items]
    if not atoms:
        return "No teacher atom bundle available."
    return "\n".join(f"- {_short_text(str(atom), max_chars=max_chars)}" for atom in atoms)


def _teacher_framework_text(teacher: dict[str, Any] | None) -> str:
    if not teacher:
        return ""
    attribution = (teacher.get("attribution") or "").strip()
    if attribution:
        return attribution
    atoms = teacher.get("atoms") or []
    if atoms:
        return str(atoms[0]).strip()
    tradition = (teacher.get("tradition") or "").strip()
    if tradition:
        return f"{tradition} framework for naming, diagnosing, and responding to youth distress."
    return ""


def _extract_turnaround_stats(text: str) -> tuple[str, str]:
    numbers = re.findall(r"\b\d[\d,%.]*\b", text or "")
    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    if len(numbers) == 1:
        return numbers[0], ""
    return "", ""


def _extract_reader_loop_sentence(text: str) -> str:
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("LOOP_SEQUENCE:"):
            return stripped.split(":", 1)[1].strip().strip('"')
    return _short_text(text, max_chars=180)


def _teacher_prompt_meta(repo_root: Path, teacher: dict[str, Any] | None) -> dict[str, str]:
    teacher = teacher or {}
    teacher_id = str(teacher.get("teacher_id") or "").strip()
    role = "teacher"
    years = ""
    tradition_age = ""

    if not teacher_id or yaml is None:
        return {
            "teacher_role": role,
            "teacher_years": years,
            "tradition_age": tradition_age,
        }

    doctrine_path = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine" / "doctrine.yaml"
    if not doctrine_path.exists():
        return {
            "teacher_role": role,
            "teacher_years": years,
            "tradition_age": tradition_age,
        }

    try:
        doctrine = yaml.safe_load(doctrine_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {
            "teacher_role": role,
            "teacher_years": years,
            "tradition_age": tradition_age,
        }

    role_text = str(doctrine.get("role_definition") or "").strip()
    if role_text:
        role = _short_text(role_text, max_chars=80)

    text_pool = "\n".join(
        [
            role_text,
            "\n".join(str(x) for x in (doctrine.get("verified_ground") or [])),
        ]
    )
    years_match = re.search(r"\b(\d{1,3})\s+years?\b", text_pool, re.IGNORECASE)
    if years_match:
        years = years_match.group(1)
    age_match = re.search(r"\b(\d{1,4}(?:,\d{3})?)\s+years?\b", str(doctrine.get("tradition") or ""), re.IGNORECASE)
    if age_match:
        tradition_age = age_match.group(1)

    return {
        "teacher_role": role,
        "teacher_years": years,
        "tradition_age": tradition_age,
    }


# ── Claude API call ──
def _call_claude(
    *,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.5,
    model: str = "claude-sonnet-4-20250514",
    timeout_seconds: float = 90.0,
) -> str | None:
    """Call Claude via Anthropic SDK. Returns text or None on failure."""
    try:
        from anthropic import Anthropic
    except ImportError:
        logger.error("anthropic package not installed: pip install anthropic")
        return None

    client = Anthropic(api_key=api_key, timeout=timeout_seconds, max_retries=1)
    for attempt in range(2):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=temperature,
                timeout=timeout_seconds,
            )
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            return text.strip() if text.strip() else None
        except Exception as e:
            message = str(e)
            if "rate_limit_error" in message or "429" in message:
                if attempt == 0:
                    logger.warning("Claude API rate-limited; sleeping 65s before retry")
                    time.sleep(65)
                    continue
            logger.warning("Claude API call failed: %s", e)
            return None
    return None


# ── Slot budget ──
def _slot_token_budget(slot: str) -> int:
    budgets = {
        "headline": 80,
        "news_summary": 300,
        "youth_impact": 350,
        "teacher_perspective": 600,
        "sdg_un_tie": 200,
        "forward_look": 250,
        "thesis": 300,
        "teaching_interpretation": 600,
        "civic_recommendation": 300,
        "sdg_reference": 200,
        "event_summary": 300,
        "leaders_present": 250,
        "themes_discussed": 500,
        "youth_commitments": 300,
        "sdg_alignment": 200,
        "next_steps": 250,
        "what_happened": 300,
        "historical_background": 350,
        "ethical_spiritual_dimension": 600,
        "youth_implications": 350,
        "sdg_policy_tie": 250,
        "future_outlook": 300,
        "youth_narrative": 350,
        "data_research": 350,
        "teacher_reflection": 500,
        "sdg_framework": 200,
        "solutions": 350,
        # v5.2 14-prompt architecture slots
        "headline_layer_1": 60,
        "headline_layer_2": 40,
        "hook_personal": 150,
        "hook_big_picture": 150,
        "news_peg": 200,
        "teacher_intro": 150,
        "youth_somatic": 200,
        "teacher_witness": 200,
        "body_data": 250,
        "turnaround": 200,
        "bridge": 150,
        "practice_announce": 200,
        "sdg_un_tie": 220,
    }
    return budgets.get(slot, 400)


def _to_html_paragraph(text: str) -> str:
    t = text.strip()
    if not t:
        return ""
    if t.startswith("<"):
        return t
    return f"<p>{t}</p>"


# ── Simulation mode (for testing without API access) ──
def _simulate_slot(slot: str, ctx: dict[str, Any]) -> str:
    """Generate realistic slot content for E2E testing without API access."""
    topic = ctx.get("topic", "global affairs")
    teacher_name = ctx.get("teacher_name", "Maat")
    teacher_tradition = ctx.get("teacher_tradition", "interfaith")
    sdg_number = ctx.get("sdg_number", "17")
    sdg_name = ctx.get("sdg_name", "Partnerships for the Goals")
    title = ctx.get("news_event", "").split("\n")[0].replace("Title: ", "").strip()

    simulated = {
        "headline": f"Youth Voices Rise as {topic.replace('_', ' ').title()} Reshapes Global Priorities",
        "news_summary": (
            f"A new development in {topic.replace('_', ' ')} is drawing attention from policymakers and educators worldwide. "
            f"The issue, reported across multiple regions, highlights systemic challenges that disproportionately affect young people aged 15-24. "
            f"Community organizations and school districts have begun coordinating response frameworks."
        ),
        "youth_impact": (
            f"In New York City, 67% of surveyed high school students reported that {topic.replace('_', ' ')} directly affects their daily routines, "
            f"according to a 2024 district wellness survey. Students in after-school programs have launched peer support groups, "
            f"with participation doubling in the past semester. A 17-year-old organizer in Brooklyn noted that youth-led workshops "
            f"now draw 40 participants weekly — up from 12 last year."
        ),
        "teacher_perspective": (
            f"{teacher_name} teaches that awareness must precede action — that naming a challenge with precision "
            f"is the first step toward addressing it. This principle, drawn from decades of interfaith educational practice, "
            f"offers students a framework for moving beyond anxiety into structured response.\n\n"
            f"In practice, {teacher_name} recommends a three-step reflection exercise: identify the feeling, "
            f"trace it to a specific cause, and name one concrete action within your capacity. Students who "
            f"have used this method report greater clarity and reduced overwhelm.\n\n"
            f"\"The work is not to fix everything,\" {teacher_name} emphasizes, \"but to see clearly and act where you stand.\""
        ),
        "sdg_un_tie": (
            f"This story relates to SDG {sdg_number}: {sdg_name}. The UN tracks progress through annual indicator reviews, "
            f"with the next reporting cycle expected in Q3 2026. Pearl News is an independent nonprofit and is not affiliated with the United Nations."
        ),
        "forward_look": (
            f"City education offices are expected to release updated program data within the coming quarter, "
            f"including participation rates and outcome metrics. Pearl News will track those scheduled updates "
            f"so readers can compare commitments against measurable follow-through."
        ),
        # Additional template-specific slots
        "thesis": f"The intersection of {topic.replace('_', ' ')} and youth agency demands a framework that honors both systemic analysis and individual capacity for change.",
        "teaching_interpretation": f"{teacher_name} offers a lens for understanding how structural challenges become personal ones — and how personal practice can feed back into collective response.",
        "civic_recommendation": f"Local school boards and community organizations should integrate {topic.replace('_', ' ')} literacy into existing civic engagement curricula, ensuring students have both conceptual tools and practical outlets.",
        "sdg_reference": f"SDG {sdg_number} ({sdg_name}) provides the international framework. The UN's voluntary national reviews track implementation. Pearl News is not affiliated with the United Nations.",
        "event_summary": f"A gathering of interfaith leaders and educators addressed {topic.replace('_', ' ')} with concrete commitments to youth programming and cross-tradition collaboration.",
        "leaders_present": f"Representatives from Buddhist, Christian, Islamic, and Hindu traditions joined educators and youth advocates at the three-day convening.",
        "themes_discussed": f"Participants identified three priority areas: youth mental health support, interfaith literacy in schools, and community-based response networks for {topic.replace('_', ' ')}.",
        "youth_commitments": f"Youth delegates pledged to establish peer mentorship programs in 12 cities by year-end, with quarterly progress reporting to the convening's steering committee.",
        "sdg_alignment": f"The commitments align with SDG {sdg_number}: {sdg_name}. Pearl News is not affiliated with the United Nations.",
        "next_steps": f"The steering committee will reconvene in 90 days to assess implementation progress. Pearl News will report on measurable outcomes.",
        "what_happened": f"A significant development in {topic.replace('_', ' ')} has prompted responses from international organizations, educators, and youth advocates across multiple regions.",
        "historical_background": f"This issue has roots in policy shifts dating to the early 2010s, when international frameworks first began explicitly addressing youth-specific dimensions of {topic.replace('_', ' ')}.",
        "ethical_spiritual_dimension": f"{teacher_name} frames this through the lens of interconnection — recognizing that individual wellbeing and systemic conditions shape each other in ways that demand both personal practice and collective action.",
        "youth_implications": f"For students aged 15-24, the practical effects include changes to school programming, increased demand for counseling services, and new opportunities for civic engagement through community organizations.",
        "sdg_policy_tie": f"SDG {sdg_number} ({sdg_name}) frames the policy dimension. Progress is tracked through the UN's annual sustainable development report. Pearl News is not affiliated with the United Nations.",
        "future_outlook": f"The next 12 months will be critical as new program data becomes available and institutions adjust their approaches based on early results.",
        "youth_narrative": f"Maya, 16, started a peer education group at her high school after noticing classmates struggling with {topic.replace('_', ' ')}. What began with five students now reaches 80 weekly.",
        "data_research": f"Research from the Brookings Institution shows that youth-led initiatives addressing {topic.replace('_', ' ')} have 2.3x higher engagement rates than adult-designed programs in comparable communities.",
        "teacher_reflection": f"{teacher_name} sees in these youth efforts a living example of what contemplative education aims to cultivate: the capacity to see clearly, respond with precision, and sustain effort over time.",
        "sdg_framework": f"SDG {sdg_number}: {sdg_name}. Pearl News is not affiliated with the United Nations.",
        "solutions": f"Three models are showing measurable results: peer mentorship networks, school-community partnership hubs, and youth-led research projects that feed into local policy discussions.",
        "headline_layer_1": f"{topic.replace('_', ' ').title()} Is Reshaping Youth Life",
        "headline_layer_2": f"{teacher_name} reads the same shift through a civic-spiritual lens.",
        "hook_personal": "You read the update. You keep functioning. A quieter part of you knows the cost is rising.",
        "hook_big_picture": "A new global data point confirms what many young people already tracked in their own routines: the system pressure is not imagined, and it is no longer small.",
        "news_peg": f"New reporting on {topic.replace('_', ' ')} is forcing institutions to name what young people have been carrying in daily life. The numbers are now public, the impact is measurable, and the pressure is no longer easy to dismiss.",
        "teacher_intro": f"{teacher_name}, a {teacher_tradition} teacher, has seen in practice spaces what this does to young people. Students are not asking for inspiration first. They are asking how to stay functional inside it.",
        "youth_somatic": "You read the number. Your throat tightened. You closed the tab. Then you opened it again.\nLOOP_SEQUENCE: \"read the number. throat tightened. closed the tab. opened it again.\"",
        "teacher_witness": f"{teacher_name} has seen this exact loop in young people this year — the reading, the tightening, the tab that closes, the return.",
        "body_data": "The scale is public now, but the consequence still lands one person at a time. Daily functioning shifts first: sleep, concentration, attention, and the energy it takes to keep going through a normal day.",
        "turnaround": "Young people are already building responses.\n\n184 initiatives. 23 countries.\n\nStudents, organizers, and local groups are creating practical routes forward even before policy catches up.",
        "bridge": f"184 initiatives. 23 countries. The tracker measures what young people did. It has no column for the capacity to stay functional enough to act again when the system keeps not responding. The person who built the next response needed it. So does the reader who closed the tab and opened it again. {teacher_name}'s tradition has been developing it for generations.",
        "practice_announce": "The practice in the sidebar is designed for this exact pressure. It gives the mind one clear action, restores enough functional capacity to stay present, and makes the next honest step easier to take.",
    }
    return simulated.get(slot, f"[Simulated content for {slot}]")


# ── Main expansion function ──
def expand_with_claude(
    items: list[dict[str, Any]],
    config_root: Path | None = None,
    simulate: bool = False,
) -> list[dict[str, Any]]:
    """
    For each item, generate article content slot-by-slot using Claude.
    Replaces the Qwen-based expansion entirely.
    """
    api_key = _load_api_key()
    if not api_key and not simulate:
        logger.error("No Anthropic API key found (ANTHROPIC_API_KEY or claude_api_key.rtf)")
        for item in items:
            item["_expansion_failed"] = True
            item["_expansion_error"] = "no_anthropic_api_key"
        return items

    if simulate:
        logger.info("Running in SIMULATION mode (no API calls)")
        api_key = api_key or "sim"

    root = Path(__file__).resolve().parent.parent
    config_root = config_root or (root / "config")
    prompts_root = root / "prompts"
    system_prompt = _load_system_prompt(prompts_root)

    # Load config for model preference
    config_path = config_root / "llm_expansion.yaml"
    config: dict[str, Any] = {}
    if config_path.exists() and yaml:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    model = os.environ.get("CLAUDE_MODEL") or config.get("claude_model") or "claude-sonnet-4-20250514"
    temperature = float(config.get("temperature") or 0.5)

    logger.info("Claude expansion: model=%s, %d items", model, len(items))
    repo_root = Path(__file__).resolve().parents[2]

    for item in items:
        article_id = item.get("id", "?")
        template_id = item.get("template_id") or "hard_news_spiritual_response"
        slots_list = TEMPLATE_SLOTS_V52.get(template_id) or TEMPLATE_SLOTS.get(
            template_id,
            TEMPLATE_SLOTS["hard_news_spiritual_response"],
        )
        optional_slots = OPTIONAL_V52_SLOTS.get(template_id, ())
        is_v52_template = template_id in TEMPLATE_SLOTS_V52

        teacher = item.get("_teacher_resolved") or {}
        teacher_name = teacher.get("display_name") or "Forum Participant"
        teacher_tradition = teacher.get("tradition") or "interfaith"
        teacher_meta = _teacher_prompt_meta(repo_root, teacher)
        deterministic_plan = None
        if template_id == "hard_news_spiritual_response":
            deterministic_plan = build_hard_news_deterministic_plan(item, repo_root)
        elif template_id == "commentary":
            deterministic_plan = build_commentary_deterministic_plan(item, repo_root)
        elif template_id == "explainer_context":
            deterministic_plan = build_explainer_deterministic_plan(item, repo_root)
        elif template_id == "interfaith_dialogue_report":
            deterministic_plan = build_interfaith_deterministic_plan(item, repo_root)
        elif template_id == "youth_feature":
            deterministic_plan = build_youth_feature_deterministic_plan(item, repo_root)
        elif template_id == "unsay_dialogue":
            deterministic_plan = build_unsay_deterministic_plan(item, repo_root)
        if deterministic_plan:
            item["_deterministic_teacher_topic_pack"] = deterministic_plan.get("pack_path")
            item["_deterministic_beat_map"] = deterministic_plan.get("beat_map_id")
            item["_deterministic_article_plan"] = deterministic_plan.get("ordered_sections")

        # Build context for prompt rendering
        ctx = {
            "news_event": (
                f"Title: {_short_text(item.get('raw_title') or item.get('title') or '', max_chars=150)}\n"
                f"Summary: {_short_text(item.get('raw_summary') or item.get('summary') or '', max_chars=300)}\n"
                f"URL: {item.get('url')}\nDate: {item.get('pub_date')}"
            ),
            "news_event_topic": item.get("topic") or "global affairs",
            "topic": item.get("topic") or "global affairs",
            "youth_impact_summary": _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=200),
            "youth_impact": _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=250),
            "teacher_name": teacher_name,
            "teacher_tradition": teacher_tradition,
            "teacher_framework": _teacher_framework_text(teacher),
            "teacher_quotes_practices": _teacher_quotes_text(teacher),
            "teacher_role": teacher_meta["teacher_role"],
            "teacher_years": teacher_meta["teacher_years"],
            "tradition_age": teacher_meta["tradition_age"],
            "sdg_number": item.get("primary_sdg") or "17",
            "sdg_name": (item.get("sdg_labels") or {}).get(item.get("primary_sdg", "17"), "Partnerships for the Goals"),
            "sdg_target": "",
            "un_agency_name": item.get("un_body") or "United Nations",
            "locale": item.get("language") or "en",
            "news_topic": item.get("topic") or "global affairs",
            "gen_z_impact": _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=160),
            "reader_loop_sentence": "",
            "turnaround_stat_1": "",
            "turnaround_stat_2": "",
        }

        # Generate each slot
        values: dict[str, str] = {}
        all_ok = True
        t0 = time.monotonic()

        if deterministic_plan:
            for slot, value in (deterministic_plan.get("slots") or {}).items():
                if value:
                    values[slot] = value
                    ctx[slot] = value
                    if slot == "youth_somatic":
                        ctx["reader_loop_sentence"] = _extract_reader_loop_sentence(value)
                    elif slot == "turnaround":
                        stat_1, stat_2 = _extract_turnaround_stats(value)
                        ctx["turnaround_stat_1"] = stat_1
                        ctx["turnaround_stat_2"] = stat_2

        for slot in slots_list:
            if values.get(slot):
                continue
            out = None

            if simulate:
                out = _simulate_slot(slot, ctx)
            else:
                slot_template = _load_slot_prompt(prompts_root, template_id, slot)
                if not slot_template:
                    logger.warning("No prompt template for %s/%s — skipping", template_id, slot)
                    values[slot] = ""
                    continue

                prompt = _render_prompt(slot_template, {**ctx, **values})
                out = _call_claude(
                    api_key=api_key,
                    system_prompt=system_prompt,
                    user_prompt=prompt,
                    max_tokens=_slot_token_budget(slot),
                    temperature=temperature,
                    model=model,
                )

            if out:
                out = _clean_slot_output(slot, out)
            if out:
                values[slot] = out
                # Feed forward: make previous slots available to later prompts
                ctx[slot] = out
                if slot == "youth_somatic":
                    ctx["reader_loop_sentence"] = _extract_reader_loop_sentence(out)
                elif slot == "turnaround":
                    stat_1, stat_2 = _extract_turnaround_stats(out)
                    ctx["turnaround_stat_1"] = stat_1
                    ctx["turnaround_stat_2"] = stat_2
                logger.debug("  slot %s: %d chars", slot, len(out))
            else:
                logger.warning("  slot %s: FAILED for article %s", slot, article_id)
                values[slot] = ""
                all_ok = False

        elapsed = time.monotonic() - t0

        if not all_ok or not values.get(slots_list[0]):
            item["_expansion_failed"] = True
            item["_expansion_error"] = "claude_slot_generation_incomplete"
            logger.warning("Article %s: expansion incomplete (%.1fs)", article_id, elapsed)
            continue

        for slot in optional_slots:
            if simulate:
                out = _simulate_slot(slot, ctx)
            else:
                slot_template = _load_slot_prompt(prompts_root, template_id, slot)
                if not slot_template:
                    continue
                prompt = _render_prompt(slot_template, {**ctx, **values})
                out = _call_claude(
                    api_key=api_key,
                    system_prompt=system_prompt,
                    user_prompt=prompt,
                    max_tokens=_slot_token_budget(slot),
                    temperature=temperature,
                    model=model,
                )
            if out:
                out = _clean_slot_output(slot, out)
            if out:
                values[slot] = out
                ctx[slot] = out

        # Build merged HTML content (for backward compatibility with basic pipeline)
        if is_v52_template:
            headline = " ".join(
                part.strip().rstrip(".")
                for part in [values.get("headline_layer_1", ""), values.get("headline_layer_2", "")]
                if part and part.strip()
            ).strip() or values.get(slots_list[0], "")
        else:
            headline = values.get("headline") or values.get(slots_list[0], "")
        source_url = item.get("url") or ""
        body_parts = [f"<h1>{headline.strip()}</h1>"]
        content_slots = list(slots_list[1:]) + [slot for slot in optional_slots if slot in values]
        for slot in content_slots:
            text = values.get(slot, "")
            if text:
                body_parts.append(_to_html_paragraph(text))
        if source_url:
            body_parts.append(f'<p><em>Source: <a href="{source_url}">{source_url}</a></em></p>')

        item["content"] = "\n\n".join([p for p in body_parts if p.strip()])

        # Store v5.2 slots for the design-system assembler.
        v52_slots = {}
        if is_v52_template:
            for slot in slots_list:
                if values.get(slot):
                    v52_slots[slot] = values[slot]
            for slot in optional_slots:
                if values.get(slot):
                    v52_slots[slot] = values[slot]
        else:
            v52_map = V52_SLOT_MAP.get(template_id, V52_SLOT_MAP["hard_news_spiritual_response"])
            for template_slot, v52_name in v52_map.items():
                if template_slot in values and values[template_slot]:
                    v52_slots[v52_name] = values[template_slot]
        item["_v52_slots"] = v52_slots

        item["_expansion_retries"] = 0
        wc = len(item["content"].split())
        logger.info("Article %s: Claude wrote %d words across %d slots (%.1fs)",
                     article_id, wc, len([v for v in values.values() if v]), elapsed)

    return items
