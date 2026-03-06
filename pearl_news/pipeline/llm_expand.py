"""
Pearl News — expand article content toward target word count using an LLM (Qwen / OpenAI-compatible API).
Allowed under llm_safety.yaml (expansion without full-article evaluation).
Environment override: QWEN_BASE_URL, QWEN_API_KEY, QWEN_MODEL (e.g. from GitHub Actions secrets on self-hosted runner).

v2: Injects teacher (name, tradition, atoms), research_excerpt, language, audience, template_id into user message
so the model has real context rather than expanding a generic placeholder.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Research excerpt loader — primary: KB, fallback: embedded snippets
# ---------------------------------------------------------------------------

def _get_research_excerpt_from_kb(topic: str, language: str, repo_root: Path | None = None) -> str:
    """Try to pull research excerpt from the KB. Returns '' if KB unavailable."""
    try:
        from pearl_news.research_kb.retrieval import get_research_excerpt
        return get_research_excerpt(topic, language=language, n=3, max_words=400, repo_root=repo_root)
    except Exception as e:
        logger.debug("KB retrieval failed (%s); using fallback snippets", e)
        return ""


_RESEARCH_SNIPPETS: dict[str, str] = {
    "mental_health": (
        "Gen Z Contradiction Audit — mental health: Gen Z self-report mental health struggles "
        "at higher rates than any prior recorded cohort (52% of US Gen Z ages 18-25 report "
        "anxiety, APA 2023), yet engagement with formal mental health services remains low "
        "(only 37% of those reporting anxiety sought professional help, same survey). "
        "Invisible script: 'I know something is wrong but institutions are not trustworthy.' "
        "Behavior signal: peer-to-peer mental health disclosure on TikTok and Discord has "
        "replaced clinical disclosure for many. For Japanese Gen Z specifically: 2023 Cabinet "
        "Office survey found 47% of ages 18-29 cited global instability as top anxiety source; "
        "hikikomori prevalence estimated at 1.46M (Cabinet Office 2023). "
        "Persona switch — Gen Alpha (ages 10-15): unlike Gen Z who discovered social media "
        "as adolescents, Gen Alpha was born into it; their mental health baseline has never "
        "included a pre-platform reference point."
    ),
    "climate": (
        "Gen Z Climate Contradiction Audit: 75% of Gen Z globally rate climate change as "
        "their top concern (Deloitte 2023 Global Gen Z Survey, n=22,841), yet same cohort "
        "shows highest fast-fashion consumption rate of any living generation (ThredUp 2023). "
        "Invisible script: 'Individual action is insufficient but collective action feels "
        "inaccessible.' Behavior signal: climate grief is real (68% of US Gen Z report "
        "climate anxiety, APA 2021) but primarily expressed online, rarely through sustained "
        "civic participation. Japanese context: 2022 Ministry of Environment survey found "
        "73% of Japanese ages 15-29 'worried' about climate, but only 12% had taken any "
        "action beyond recycling in the prior year. "
        "Persona switch — Gen Alpha: for children ages 10-15 in Pacific Island nations, "
        "climate change is not a future threat but a present reality — school relocation, "
        "coastal flooding, and displacement are current lived experience, not projection."
    ),
    "peace_conflict": (
        "Gen Z Peace/Conflict Research: Gen Z in conflict-adjacent countries shows "
        "'compassion fatigue' patterns — high initial engagement with conflict news followed "
        "by withdrawal and emotional numbing (Reuters Institute Digital News Report 2023). "
        "Contradiction: Gen Z identifies as most 'globally aware' generation, yet social "
        "media algorithm exposure to conflict is often geographically and ideologically "
        "siloed — different Gen Z cohorts are watching entirely different versions of the "
        "same conflict. Japanese Gen Z context: Japan's pacifist constitution and post-war "
        "education have produced strong anti-war sentiment (83% oppose constitutional "
        "revision to allow collective defense, Asahi Shimbun 2022), yet Japan's defense "
        "budget reached ¥6.8 trillion in FY2023, highest since WWII. "
        "Persona switch — youth in conflict zones (Gen Alpha/Z): access to education is "
        "primary casualty; UNESCO estimates 250M children out of school due to conflict-related "
        "disruption globally."
    ),
    "education": (
        "Gen Z Education Contradiction Audit: Gen Z is the most credentialled generation "
        "in history (US: 57% of Gen Z enrolled in or completed college, NCES 2022), yet "
        "reports the highest rates of 'education-to-employment mismatch' — 52% of recent "
        "US graduates employed in roles not requiring their degree (Federal Reserve 2023). "
        "Japanese context: juken (exam preparation) industry revenue ¥945B in 2022; "
        "student average daily study hours outside school: 4.2 (MEXT 2022). Despite high "
        "credential attainment, 35% of Japanese ages 22-29 report being 'unsure their "
        "education prepared them for work' (Recruit Works Institute 2023). "
        "Invisible script: 'The credential was the path; the path has not arrived at the "
        "destination.' Persona switch — Gen Alpha: AI integration into primary education "
        "is producing the first cohort who will have co-created their own educational "
        "content; the long-term effect on deep literacy and sustained attention is unknown."
    ),
    "economy_work": (
        "Gen Z Economy/Work Contradiction Audit: 67% of Gen Z globally list financial "
        "security as top life goal (Deloitte 2023), yet same cohort shows highest 'lying flat' "
        "/ 'quiet quitting' adoption rate — 59% of US Gen Z report being disengaged at work "
        "(Gallup 2023). Chinese tangping (lying flat) movement — originated 2021, explicitly "
        "rejects 996 culture and competitive consumption. Invisible script: 'The system "
        "rewards compliance and punishes ambition — I will reduce my exposure.' "
        "Japan: youth unemployment 4.3% (2023, lower than global average) but non-regular "
        "employment among under-35s at 31% (Ministry of Health, Labour and Welfare 2023), "
        "creating employment without security or career trajectory. "
        "Persona switch — Gen Alpha in developing economies: ILO estimates 160M child "
        "labourers globally ages 5-17; for these young people, 'work' is not a career "
        "question but a survival condition."
    ),
    "inequality": (
        "Gen Z Inequality Research: Gen Z is on track to be the first generation in modern "
        "history to be less wealthy than their parents at equivalent age (Fed Reserve 2023 — "
        "median Gen Z wealth at age 25 is 30% lower in real terms than Boomers at same age). "
        "Contradiction: Gen Z identifies as most equity-conscious generation (73% say reducing "
        "inequality is important, Pew 2022), yet consumption of luxury goods among Gen Z "
        "increased 26% 2020-2023 (Bain & Co). Invisible script: 'I want a more equal world "
        "and I want the things inequality currently provides.' "
        "Japanese context: child poverty rate 13.5% (2021, MHLW) — highest sustained level "
        "since 1985; youth homelessness increasing in major cities despite official data "
        "undercounting. Chinese context: urban-rural income gap ratio 2.45 (2022, NBS); "
        "gaokao performance strongly predicts lifetime income trajectory."
    ),
    "partnerships": (
        "Gen Z Partnership/Institutions Research: Trust in global institutions among Gen Z "
        "is at generational low — only 34% of Gen Z trust international organisations "
        "(Edelman Trust Barometer 2023, ages 18-26). Contradiction: same cohort shows "
        "highest rates of civic participation through informal channels (online petitions, "
        "mutual aid networks, climate strikes) while disengaging from formal institutional "
        "processes. Invisible script: 'Formal institutions failed to address what matters; "
        "informal networks are doing the work.' "
        "Youth-led organisations globally raised $2.3B in civic tech and advocacy funding "
        "2021-2023 (Candid Foundation data), suggesting high capacity alongside high distrust. "
        "UN Youth Envoy data: 4,200 formal youth-governmental partnerships established "
        "2015-2023 under SDG17 framework, but youth-reported influence in those partnerships "
        "averages 2.1/5 (satisfaction score, UN Youth Survey 2023)."
    ),
}


def _get_research_excerpt(topic: str, language: str = "en", repo_root: Path | None = None) -> str:
    """
    Return a research excerpt for this topic.
    Priority: research KB (artifacts/research/kb/) → embedded fallback snippets.
    """
    kb_excerpt = _get_research_excerpt_from_kb(topic, language=language, repo_root=repo_root)
    if kb_excerpt:
        return kb_excerpt
    return _RESEARCH_SNIPPETS.get(topic, "")


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def _load_config(config_root: Path) -> dict[str, Any]:
    path = config_root / "llm_expansion.yaml"
    data: dict[str, Any] = {}
    if path.exists() and yaml:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    # Env override (e.g. GitHub Secrets on self-hosted runner with LM Studio)
    if os.environ.get("QWEN_BASE_URL"):
        data["base_url"] = os.environ.get("QWEN_BASE_URL", "").strip()
    if os.environ.get("QWEN_API_KEY") is not None:
        data["api_key"] = (os.environ.get("QWEN_API_KEY") or "").strip()
    if os.environ.get("QWEN_MODEL"):
        data["model"] = os.environ.get("QWEN_MODEL", "").strip()
    if os.environ.get("QWEN_BASE_URL") and data.get("enabled") is not True:
        data["enabled"] = True
    return data


def _load_system_prompt(prompts_root: Path) -> str:
    path = prompts_root / "expansion_system.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return (
        "You are an editor for Pearl News. Expand the draft article to the target word count. "
        "Keep the same HTML structure and facts. Add detail by elaborating; do not invent. "
        "Output only the expanded HTML body, no preamble."
    )


# ---------------------------------------------------------------------------
# Core expansion call
# ---------------------------------------------------------------------------

def expand_article_with_llm(
    content: str,
    title: str,
    topic: str,
    primary_sdg: str,
    sdg_label: str,
    target_word_count: int,
    config: dict[str, Any],
    teacher: dict[str, Any] | None = None,
    language: str = "en",
    audience: str = "Gen Z",
    region: str = "",
    template_id: str = "hard_news_spiritual_response",
    rss_title: str = "",
    rss_summary: str = "",
    rss_date: str = "",
    rss_source_url: str = "",
    research_excerpt: str = "",
) -> str | None:
    """
    Call OpenAI-compatible API to expand article HTML toward target_word_count.
    v2: Injects teacher, research_excerpt, language, audience into user message.
    Returns expanded content or None on failure.
    """
    base_url = (config.get("base_url") or "").strip()
    model = config.get("model") or "Qwen2.5-14B-Instruct"
    api_key = (config.get("api_key") or "lm-studio").strip()
    timeout = float(config.get("timeout") or 360)
    max_tokens = int(config.get("max_tokens") or 2048)
    temperature = float(config.get("temperature") or 0.5)

    if not base_url:
        logger.warning("LLM expansion: base_url not set; skipping")
        return None

    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("LLM expansion: openai package not installed; pip install openai")
        return None

    root = Path(__file__).resolve().parent.parent
    system_prompt = _load_system_prompt(root / "prompts")

    # --- Build teacher block ---
    if teacher and teacher.get("display_name") and teacher.get("atoms"):
        from pearl_news.pipeline.teacher_resolver import format_teacher_atoms_for_prompt
        teacher_block = format_teacher_atoms_for_prompt(teacher)
    else:
        teacher_block = (
            "Teacher: a teacher from the United Spiritual Leaders Forum\n"
            "Tradition: interfaith\n"
            "Attribution: A teacher from the United Spiritual Leaders Forum teaches that\n\n"
            "Approved teachings:\n"
            "  1. reflection and resilience in the face of uncertainty support youth well-being.\n"
            "  2. ethical traditions speak to young people in times of change.\n"
            "  3. one voice at a time allows readers to engage with a clear perspective."
        )

    # --- Build research block ---
    if not research_excerpt:
        research_excerpt = _get_research_excerpt(topic, language=language)
    research_block = research_excerpt or "(no research excerpt available for this topic)"

    # --- Language / audience labels ---
    lang_labels = {
        "en": ("English", "Gen Z (ages 15–28) and Gen Alpha (ages 10–15)", "English-speaking"),
        "ja": ("Japanese", "Gen Z (ages 15–28) and Gen Alpha (ages 10–15)", "Japan"),
        "zh-cn": ("Simplified Chinese", "Gen Z (ages 15–28) and Gen Alpha (ages 10–15)", "China"),
    }
    lang_label, audience_label, region_label = lang_labels.get(language.lower(), lang_labels["en"])
    if region:
        region_label = region

    # --- Full user message ---
    user_prompt = f"""Expand and improve the following Pearl News draft article to approximately {target_word_count} words.

ARTICLE LANGUAGE: {lang_label}
TARGET AUDIENCE: {audience_label} — {region_label}
TEMPLATE: {template_id}

UN RSS SOURCE:
Title: {rss_title or title}
Source: {rss_source_url}
Summary: {rss_summary or "(see draft below)"}
Date: {rss_date}

SDG: {primary_sdg} — {sdg_label}
TOPIC: {topic}

TEACHER KNOWLEDGE BASE:
{teacher_block}

GEN Z / GEN ALPHA RESEARCH EXCERPT (use to add specific data points and anchors):
{research_block}

DRAFT ARTICLE (expand and improve in place — replace the teacher section with the named teacher above):
{content}

Instructions:
- Expand each section in place using the rules in the system prompt.
- Replace any generic "a teacher from the Forum" placeholder with {teacher.get("display_name", "the named teacher") if teacher else "the named teacher"} using all three approved teachings.
- Keep the Source line at the end unchanged.
- Output only the final HTML body. No preamble."""

    client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    choice = resp.choices[0] if resp.choices else None
    if not choice or not getattr(choice, "message", None):
        return None
    raw = (choice.message.content or "").strip()
    # Drop markdown code fence if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines)
    return raw if raw else None


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def run_expansion(
    items: list[dict[str, Any]],
    config_root: Path | None = None,
    max_retries: int = 1,
) -> list[dict[str, Any]]:
    """
    For each item, if LLM expansion is enabled, expand content toward target_word_count.
    v2: Injects teacher (resolved on item), research excerpt, language, audience.
    On failure: one retry (temperature +0.1), then keeps original.
    """
    root = Path(__file__).resolve().parent.parent
    config_root = config_root or (root / "config")
    config = _load_config(config_root)
    if not config.get("enabled", False):
        logger.info("LLM expansion disabled or config missing; skipping")
        return items

    target = int(config.get("target_word_count") or 1000)

    for item in items:
        content = item.get("content") or ""
        if not content:
            continue

        title = item.get("article_title") or item.get("title") or ""
        topic = item.get("topic") or "partnerships"
        primary_sdg = item.get("primary_sdg") or "17"
        sdg_labels_map = item.get("sdg_labels") or {}
        sdg_label = sdg_labels_map.get(primary_sdg) or "Partnerships for the Goals"
        language = item.get("language") or "en"
        template_id = item.get("template_id") or "hard_news_spiritual_response"

        # Teacher (should already be resolved and attached to item by run_article_pipeline)
        teacher = item.get("_teacher_resolved") or None

        # Research excerpt (from item or embedded KB)
        research_excerpt = item.get("_research_excerpt") or ""

        # RSS fields for user message context
        rss_title = item.get("raw_title") or item.get("title") or title
        rss_summary = item.get("raw_summary") or item.get("summary") or ""
        rss_date = item.get("pub_date") or ""
        rss_source_url = item.get("url") or ""

        attempt = 0
        expanded = None
        while attempt <= max_retries and expanded is None:
            try:
                attempt_config = dict(config)
                if attempt > 0:
                    attempt_config["temperature"] = min(0.9, float(config.get("temperature") or 0.5) + 0.1 * attempt)
                    logger.info("Retry %d for article %s (temp=%.1f)", attempt, item.get("id"), attempt_config["temperature"])
                expanded = expand_article_with_llm(
                    content=content,
                    title=title,
                    topic=topic,
                    primary_sdg=primary_sdg,
                    sdg_label=sdg_label,
                    target_word_count=target,
                    config=attempt_config,
                    teacher=teacher,
                    language=language,
                    template_id=template_id,
                    rss_title=rss_title,
                    rss_summary=rss_summary,
                    rss_date=rss_date,
                    rss_source_url=rss_source_url,
                    research_excerpt=research_excerpt,
                )
            except Exception as e:
                logger.warning("Expansion attempt %d failed for %s: %s", attempt, item.get("id"), e)
            attempt += 1

        if expanded:
            item["content"] = expanded
            item["_expansion_retries"] = attempt - 1
            wc = len(expanded.split())
            logger.info("Expanded article %s to ~%d words (retries=%d)", item.get("id"), wc, attempt - 1)
        else:
            item["_expansion_failed"] = True
            logger.warning("Expansion failed after %d attempts for %s; keeping original", attempt, item.get("id"))

    return items
