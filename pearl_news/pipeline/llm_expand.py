"""
Pearl News — expand article content toward target word count using an LLM (Qwen / OpenAI-compatible API).
Expands bullet-point drafts into prose paragraphs.
Environment override: QWEN_BASE_URL, QWEN_API_KEY, QWEN_MODEL (e.g. from GitHub Actions secrets on self-hosted runner).

v2: Injects teacher (name, tradition, atoms), research_excerpt, language, audience, template_id into user message
so the model has real context rather than expanding a generic placeholder.
"""
from __future__ import annotations

import logging
import os
import re
import json
import time
import urllib.request
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)

_PREWRITE_PROMPT_FILES = {
    "commentary": "01_PREWRITE_COMMENTARY.md",
    "hard_news_spiritual_response": "02_PREWRITE_HARD_NEWS.md",
    "interfaith_dialogue_report": "03_PREWRITE_INTERFAITH.md",
    "explainer_context": "04_PREWRITE_EXPLAINER.md",
    "youth_feature": "05_PREWRITE_YOUTH_FEATURE.md",
}

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
    docs_path = prompts_root.parent.parent / "docs" / "pearl_news_prompts" / "00_SYSTEM_PROMPT.md"
    if docs_path.exists():
        return docs_path.read_text(encoding="utf-8").strip()
    path = prompts_root / "expansion_system.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return (
        "You are an editor for Pearl News. Expand the draft article to the target word count. "
        "Keep the same HTML structure and facts. Add detail by elaborating; do not invent. "
        "Output only the expanded HTML body, no preamble."
    )


def _load_prewrite_prompt(repo_root: Path, template_id: str) -> str:
    runtime_path = repo_root / "pearl_news" / "prompts" / "prewrite_runtime" / f"{template_id}.txt"
    if runtime_path.exists():
        return runtime_path.read_text(encoding="utf-8").strip()
    filename = _PREWRITE_PROMPT_FILES.get(template_id)
    if not filename:
        return ""
    path = repo_root / "docs" / "pearl_news_prompts" / filename
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _load_slot_prompt(prompts_root: Path, template_id: str, slot_name: str) -> str:
    path = prompts_root / "slot_by_slot" / template_id / f"{slot_name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def _render_prompt(template: str, context: dict[str, Any]) -> str:
    return template.format_map(_SafeDict({k: ("" if v is None else str(v)) for k, v in context.items()}))


def _extract_source_line_html(content: str) -> str:
    m = re.search(r"(<p>\s*<em>\s*Source:.*?</p>)", content, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def _sanitize_model_output(raw: str | None) -> str | None:
    if not raw:
        return None
    text = raw.strip()
    text = re.sub(r"^\s*<think>\s*</think>\s*", "", text, flags=re.DOTALL)
    if text.startswith("```"):
        lines = text.split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text or None


def _teacher_framework_text(teacher: dict[str, Any] | None) -> str:
    if not teacher:
        return ""
    attribution = (teacher.get("attribution") or "").strip()
    if attribution:
        return attribution
    atoms = teacher.get("atoms") or []
    if atoms:
        first = str(atoms[0]).strip()
        if first:
            return first
    tradition = (teacher.get("tradition") or "").strip()
    if tradition:
        return f"{tradition} framework for naming, diagnosing, and responding to youth distress."
    return ""


def _short_text(value: str | None, *, max_chars: int) -> str:
    text = (value or "").strip()
    if len(text) <= max_chars:
        return text
    clipped = text[:max_chars].rsplit(" ", 1)[0].strip()
    return (clipped or text[:max_chars]).rstrip(" ,.;:") + "..."


def _teacher_quotes_text(teacher: dict[str, Any] | None, *, max_items: int = 2, max_chars: int = 320) -> str:
    atoms = ((teacher or {}).get("atoms") or [])[:max_items]
    if not atoms:
        return "No teacher atom bundle available."
    lines = [f"- {_short_text(str(atom), max_chars=max_chars)}" for atom in atoms]
    return "\n".join(lines)


def _build_prewrite_messages(
    *,
    repo_root: Path,
    template_id: str,
    context: dict[str, Any],
) -> list[dict[str, str]]:
    prewrite = _load_prewrite_prompt(repo_root, template_id)
    if not prewrite:
        return []
    rendered = _render_prompt(prewrite, context)
    return [
        {"role": "user", "content": rendered},
        {"role": "assistant", "content": "READY"},
    ]


def _chat_once(
    *,
    client: Any,
    model: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    disable_thinking: bool,
    system_prompt: str | None = None,
    base_messages: list[dict[str, str]] | None = None,
) -> str | None:
    # Qwen3 GGUF stability: force explicit no-think directive at prompt level.
    if not user_prompt.lstrip().startswith("/no_think"):
        user_prompt = "/no_think\n" + user_prompt

    raw = None
    extra_body = {"enable_thinking": False} if disable_thinking else {}
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    else:
        messages.append({"role": "system", "content": "Follow the user's instructions exactly and output only requested content."})
    if base_messages:
        messages.extend(base_messages)
    messages.append({"role": "user", "content": user_prompt})
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=0.8,
            presence_penalty=1.5,
            max_tokens=max_tokens,
            **({"extra_body": extra_body} if extra_body else {}),
        )
        choice = resp.choices[0] if resp.choices else None
        if choice and getattr(choice, "message", None):
            raw = (choice.message.content or "").strip()
    except Exception as e:
        logger.warning("OpenAI client chat failed; trying direct HTTP fallback: %s", e)

    if not raw:
        # Fallback path for environments where OpenAI client transport fails but endpoint is reachable.
        try:
            base_url = str(getattr(client, "base_url", "")).rstrip("/")
            if not base_url:
                return None
            url = f"{base_url}/chat/completions"
            payload: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "top_p": 0.8,
                "presence_penalty": 1.5,
                "max_tokens": max_tokens,
            }
            if disable_thinking:
                payload["enable_thinking"] = False
            body = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {getattr(client, 'api_key', 'lm-studio')}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8", errors="ignore"))
            raw = (
                (((data.get("choices") or [{}])[0].get("message") or {}).get("content"))
                or ""
            ).strip()
        except Exception as e:
            logger.warning("Direct HTTP fallback failed: %s", e)
            return None

    return _sanitize_model_output(raw)


def _create_openai_client(config: dict[str, Any]) -> Any | None:
    base_url = (config.get("base_url") or "").strip()
    api_key = (config.get("api_key") or "lm-studio").strip()
    timeout = float(config.get("timeout") or 360)
    if not base_url:
        return None
    from openai import OpenAI
    try:
        from httpx import Timeout as HttpxTimeout
        http_timeout = HttpxTimeout(timeout)
    except Exception:
        http_timeout = timeout
    return OpenAI(base_url=base_url, api_key=api_key, timeout=http_timeout)


def _preflight_chat_health(
    *,
    client: Any,
    model: str,
    disable_thinking: bool,
    config: dict[str, Any],
    system_prompt: str,
) -> tuple[bool, str | None]:
    max_seconds = float(config.get("preflight_max_seconds") or 45)
    started = time.monotonic()
    reply = _chat_once(
        client=client,
        model=model,
        user_prompt="/no_think\nreply only READY",
        temperature=0.1,
        max_tokens=12,
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
    )
    elapsed = time.monotonic() - started
    if not reply:
        return False, "llm_preflight_no_response"
    normalized = reply.strip()
    if normalized != "READY":
        return False, f"llm_preflight_bad_reply:{normalized[:80]}"
    if elapsed > max_seconds:
        return False, f"llm_preflight_too_slow:{elapsed:.1f}s"
    return True, None


def _to_html_paragraph(text: str) -> str:
    t = text.strip()
    if not t:
        return ""
    if t.startswith("<"):
        return t
    return f"<p>{t}</p>"


def _slot_token_budget(slot: str, default_max: int) -> int:
    budgets = {
        "headline": 90,
        "thesis": 220,
        "news_summary": 220,
        "event_summary": 220,
        "leaders_present": 180,
        "historical_background": 260,
        "youth_impact": 260,
        "youth_narrative": 260,
        "teacher_perspective": 420,
        "teacher_reflection": 420,
        "teaching_interpretation": 520,
        "themes_discussed": 420,
        "ethical_spiritual_dimension": 520,
        "youth_commitments": 240,
        "youth_implications": 300,
        "civic_recommendation": 240,
        "sdg_reference": 180,
        "sdg_alignment": 180,
        "sdg_un_tie": 180,
        "sdg_policy_tie": 220,
        "forward_look": 220,
        "future_outlook": 260,
        "next_steps": 220,
        "solutions": 280,
        "data_research": 280,
    }
    return min(default_max, budgets.get(slot, default_max))


def _expand_commentary_slotwise(
    *,
    content: str,
    item: dict[str, Any],
    teacher: dict[str, Any] | None,
    sdg_label: str,
    config: dict[str, Any],
) -> str | None:
    repo_root = Path(__file__).resolve().parents[2]
    pearl_root = repo_root / "pearl_news"
    prompts_root = pearl_root / "prompts"
    slots = ("headline", "thesis", "teaching_interpretation", "civic_recommendation", "sdg_reference")
    slot_templates = {s: _load_slot_prompt(prompts_root, "commentary", s) for s in slots}
    if not all(slot_templates.values()):
        return None
    system_prompt = _load_system_prompt(prompts_root)

    base_url = (config.get("base_url") or "").strip()
    model = config.get("model") or "qwen3-14b"
    api_key = (config.get("api_key") or "lm-studio").strip()
    timeout = float(config.get("timeout") or 360)
    max_tokens = int(config.get("max_tokens") or 2048)
    temperature = float(config.get("temperature") or 0.5)
    disable_thinking = config.get("disable_thinking", True)
    if not base_url:
        return None
    client = _create_openai_client(config)
    if client is None:
        return None

    news_event = (
        f"Title: {_short_text(item.get('raw_title') or item.get('title') or '', max_chars=120)}\n"
        f"Summary: {_short_text(item.get('raw_summary') or item.get('summary') or '', max_chars=220)}\n"
        f"URL: {item.get('url')}\nDate: {item.get('pub_date')}"
    )
    teacher_name = (teacher or {}).get("display_name") or "Forum Teacher"
    teacher_tradition = (teacher or {}).get("tradition") or "interfaith"
    teacher_quotes = _teacher_quotes_text(teacher)
    source_html = _extract_source_line_html(content)

    ctx = {
        "news_event": news_event,
        "teacher_name": teacher_name,
        "teacher_tradition": teacher_tradition,
        "teacher_framework": _teacher_framework_text(teacher),
        "teacher_quotes_practices": teacher_quotes,
        "sdg_number": item.get("primary_sdg") or "17",
        "sdg_name": sdg_label,
        "un_agency_name": item.get("un_body") or "United Nations",
        "locale": item.get("language") or "en",
    }
    prewrite_messages = _build_prewrite_messages(repo_root=repo_root, template_id="commentary", context=ctx)

    headline = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["headline"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("headline", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not headline:
        return None
    ctx["headline"] = headline

    # Use first sentence of summary as crisis anchor context for headline/thesis prompts.
    crisis_anchor = (item.get("summary") or item.get("raw_summary") or "").split(".")[0].strip()
    ctx["gen_z_crisis_anchor"] = crisis_anchor

    thesis = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["thesis"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("thesis", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not thesis:
        return None
    ctx["thesis"] = thesis

    teaching = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["teaching_interpretation"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("teaching_interpretation", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not teaching:
        return None
    ctx["teaching_interpretation"] = teaching

    civic = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["civic_recommendation"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("civic_recommendation", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not civic:
        return None

    sdg_ref = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["sdg_reference"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("sdg_reference", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not sdg_ref:
        return None

    body_parts = [
        f"<p><strong>Commentary</strong></p>",
        f"<h1>{headline.strip()}</h1>",
        _to_html_paragraph(thesis),
        _to_html_paragraph(item.get("summary") or item.get("raw_summary") or ""),
        _to_html_paragraph(teaching),
        _to_html_paragraph(civic),
        _to_html_paragraph(sdg_ref.replace("\n", "<br>")),
    ]
    if source_html:
        body_parts.append(source_html)
    elif item.get("url"):
        body_parts.append(
            f"<p><em>Source: <a href=\"{item['url']}\">{item['url']}</a></em></p>"
        )
    return "\n\n".join([p for p in body_parts if p.strip()])


def _expand_interfaith_slotwise(
    *,
    content: str,
    item: dict[str, Any],
    teacher: dict[str, Any] | None,
    sdg_label: str,
    config: dict[str, Any],
) -> str | None:
    repo_root = Path(__file__).resolve().parents[2]
    pearl_root = repo_root / "pearl_news"
    prompts_root = pearl_root / "prompts"
    slots = (
        "headline",
        "event_summary",
        "leaders_present",
        "themes_discussed",
        "youth_commitments",
        "sdg_alignment",
        "next_steps",
    )
    slot_templates = {s: _load_slot_prompt(prompts_root, "interfaith_dialogue_report", s) for s in slots}
    if not all(slot_templates.values()):
        return None
    system_prompt = _load_system_prompt(prompts_root)

    base_url = (config.get("base_url") or "").strip()
    model = config.get("model") or "qwen3-14b"
    api_key = (config.get("api_key") or "lm-studio").strip()
    timeout = float(config.get("timeout") or 360)
    max_tokens = int(config.get("max_tokens") or 2048)
    temperature = float(config.get("temperature") or 0.5)
    disable_thinking = config.get("disable_thinking", True)
    if not base_url:
        return None
    client = _create_openai_client(config)
    if client is None:
        return None

    teacher_name = (teacher or {}).get("display_name") or "Forum Teacher"
    teacher_tradition = (teacher or {}).get("tradition") or "interfaith"
    teachers_list = f"{teacher_name} ({teacher_tradition})"
    news_topic = item.get("topic") or "global affairs"
    youth_impact = _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=220)
    source_html = _extract_source_line_html(content)
    teacher_quotes = _teacher_quotes_text(teacher)

    ctx = {
        "news_event_topic": news_topic,
        "news_event": (
            f"Title: {_short_text(item.get('raw_title') or item.get('title') or '', max_chars=120)}\n"
            f"Summary: {_short_text(item.get('raw_summary') or item.get('summary') or '', max_chars=220)}\n"
            f"URL: {item.get('url')}"
        ),
        "teacher_1_name": teacher_name,
        "teacher_1_tradition": teacher_tradition,
        "teacher_2_name": "",
        "teacher_2_tradition": "",
        "teacher_3_name": "",
        "teacher_3_tradition": "",
        "teachers_list": teachers_list,
        "teachers_data": teachers_list,
        "teacher_quotes_practices": teacher_quotes,
        "youth_impact": youth_impact,
        "sdg_number": item.get("primary_sdg") or "17",
        "sdg_name": sdg_label,
        "un_agency_name": item.get("un_body") or "United Nations",
    }
    prewrite_messages = _build_prewrite_messages(repo_root=repo_root, template_id="interfaith_dialogue_report", context=ctx)

    headline = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["headline"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("headline", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not headline:
        return None
    ctx["headline"] = headline

    event_summary = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["event_summary"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("event_summary", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not event_summary:
        return None
    ctx["event_summary"] = event_summary

    leaders_present = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["leaders_present"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("leaders_present", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not leaders_present:
        return None
    ctx["leaders_present"] = leaders_present

    themes_discussed = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["themes_discussed"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("themes_discussed", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not themes_discussed:
        return None
    ctx["themes_discussed"] = themes_discussed

    youth_commitments = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["youth_commitments"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("youth_commitments", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not youth_commitments:
        return None
    ctx["youth_commitments"] = youth_commitments

    sdg_alignment = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["sdg_alignment"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("sdg_alignment", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not sdg_alignment:
        return None
    ctx["sdg_alignment"] = sdg_alignment

    next_steps = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["next_steps"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("next_steps", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not next_steps:
        return None

    body_parts = [
        f"<h1>{headline.strip()}</h1>",
        _to_html_paragraph(event_summary),
        _to_html_paragraph(leaders_present),
        _to_html_paragraph(themes_discussed),
        _to_html_paragraph(youth_commitments),
        _to_html_paragraph(sdg_alignment.replace("\n", "<br>")),
        _to_html_paragraph(next_steps),
    ]
    if source_html:
        body_parts.append(source_html)
    elif item.get("url"):
        body_parts.append(f"<p><em>Source: <a href=\"{item['url']}\">{item['url']}</a></em></p>")
    return "\n\n".join([p for p in body_parts if p.strip()])


def _expand_explainer_slotwise(
    *,
    content: str,
    item: dict[str, Any],
    teacher: dict[str, Any] | None,
    sdg_label: str,
    config: dict[str, Any],
) -> str | None:
    repo_root = Path(__file__).resolve().parents[2]
    pearl_root = repo_root / "pearl_news"
    prompts_root = pearl_root / "prompts"
    slots = (
        "headline",
        "what_happened",
        "historical_background",
        "ethical_spiritual_dimension",
        "youth_implications",
        "sdg_policy_tie",
        "future_outlook",
    )
    slot_templates = {s: _load_slot_prompt(prompts_root, "explainer_context", s) for s in slots}
    if not all(slot_templates.values()):
        return None
    system_prompt = _load_system_prompt(prompts_root)

    base_url = (config.get("base_url") or "").strip()
    model = config.get("model") or "qwen3-14b"
    api_key = (config.get("api_key") or "lm-studio").strip()
    timeout = float(config.get("timeout") or 360)
    max_tokens = int(config.get("max_tokens") or 2048)
    temperature = float(config.get("temperature") or 0.5)
    disable_thinking = config.get("disable_thinking", True)
    if not base_url:
        return None
    client = _create_openai_client(config)
    if client is None:
        return None

    teacher_name = (teacher or {}).get("display_name") or "Forum Teacher"
    teacher_tradition = (teacher or {}).get("tradition") or "interfaith"
    youth_impact = _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=220)
    source_html = _extract_source_line_html(content)
    teacher_quotes = _teacher_quotes_text(teacher)

    ctx = {
        "news_event_topic": item.get("topic") or "global affairs",
        "news_event": (
            f"Title: {_short_text(item.get('raw_title') or item.get('title') or '', max_chars=120)}\n"
            f"Summary: {_short_text(item.get('raw_summary') or item.get('summary') or '', max_chars=220)}\n"
            f"URL: {item.get('url')}\nDate: {item.get('pub_date')}"
        ),
        "teacher_name": teacher_name,
        "teacher_tradition": teacher_tradition,
        "teacher_framework": _teacher_framework_text(teacher),
        "teacher_quotes_practices": teacher_quotes,
        "youth_impact": youth_impact,
        "sdg_number": item.get("primary_sdg") or "17",
        "sdg_name": sdg_label,
        "un_agency_name": item.get("un_body") or "United Nations",
    }
    prewrite_messages = _build_prewrite_messages(repo_root=repo_root, template_id="explainer_context", context=ctx)

    headline = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["headline"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("headline", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not headline:
        return None
    ctx["headline"] = headline

    what_happened = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["what_happened"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("what_happened", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not what_happened:
        return None
    ctx["what_happened"] = what_happened

    historical_background = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["historical_background"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("historical_background", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not historical_background:
        return None
    ctx["historical_background"] = historical_background

    ethical_spiritual_dimension = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["ethical_spiritual_dimension"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("ethical_spiritual_dimension", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not ethical_spiritual_dimension:
        return None
    ctx["ethical_spiritual_dimension"] = ethical_spiritual_dimension

    youth_implications = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["youth_implications"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("youth_implications", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not youth_implications:
        return None
    ctx["youth_implications"] = youth_implications

    sdg_policy_tie = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["sdg_policy_tie"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("sdg_policy_tie", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not sdg_policy_tie:
        return None
    ctx["sdg_policy_tie"] = sdg_policy_tie

    future_outlook = _chat_once(
        client=client,
        model=model,
        user_prompt=_render_prompt(slot_templates["future_outlook"], ctx),
        temperature=temperature,
        max_tokens=_slot_token_budget("future_outlook", max_tokens),
        disable_thinking=disable_thinking,
        system_prompt=system_prompt,
        base_messages=prewrite_messages,
    )
    if not future_outlook:
        return None

    body_parts = [
        f"<h1>{headline.strip()}</h1>",
        _to_html_paragraph(what_happened),
        _to_html_paragraph(historical_background),
        _to_html_paragraph(ethical_spiritual_dimension),
        _to_html_paragraph(youth_implications),
        _to_html_paragraph(sdg_policy_tie.replace("\n", "<br>")),
        _to_html_paragraph(future_outlook),
    ]
    if source_html:
        body_parts.append(source_html)
    elif item.get("url"):
        body_parts.append(f"<p><em>Source: <a href=\"{item['url']}\">{item['url']}</a></em></p>")
    return "\n\n".join([p for p in body_parts if p.strip()])


def _expand_hard_news_slotwise(
    *,
    content: str,
    item: dict[str, Any],
    teacher: dict[str, Any] | None,
    sdg_label: str,
    config: dict[str, Any],
) -> str | None:
    repo_root = Path(__file__).resolve().parents[2]
    pearl_root = repo_root / "pearl_news"
    prompts_root = pearl_root / "prompts"
    slots = (
        "headline",
        "news_summary",
        "youth_impact",
        "teacher_perspective",
        "sdg_un_tie",
        "forward_look",
    )
    slot_templates = {s: _load_slot_prompt(prompts_root, "hard_news_spiritual_response", s) for s in slots}
    if not all(slot_templates.values()):
        return None
    system_prompt = _load_system_prompt(prompts_root)

    base_url = (config.get("base_url") or "").strip()
    model = config.get("model") or "qwen3-14b"
    api_key = (config.get("api_key") or "lm-studio").strip()
    timeout = float(config.get("timeout") or 360)
    max_tokens = int(config.get("max_tokens") or 2048)
    temperature = float(config.get("temperature") or 0.5)
    disable_thinking = config.get("disable_thinking", True)
    if not base_url:
        return None
    client = _create_openai_client(config)
    if client is None:
        return None

    teacher_name = (teacher or {}).get("display_name") or "Forum Teacher"
    teacher_tradition = (teacher or {}).get("tradition") or "interfaith"
    teacher_quotes = _teacher_quotes_text(teacher)
    source_html = _extract_source_line_html(content)

    ctx = {
        "news_event": (
            f"Title: {_short_text(item.get('raw_title') or item.get('title') or '', max_chars=120)}\n"
            f"Summary: {_short_text(item.get('raw_summary') or item.get('summary') or '', max_chars=220)}\n"
            f"URL: {item.get('url')}\nDate: {item.get('pub_date')}"
        ),
        "news_event_topic": item.get("topic") or "global affairs",
        "topic": item.get("topic") or "global affairs",
        "youth_impact_summary": _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=180),
        "teacher_name": teacher_name,
        "teacher_tradition": teacher_tradition,
        "teacher_framework": _teacher_framework_text(teacher),
        "teacher_quotes_practices": teacher_quotes,
        "youth_impact": _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=220),
        "sdg_number": item.get("primary_sdg") or "17",
        "sdg_name": sdg_label,
        "un_agency_name": item.get("un_body") or "United Nations",
    }
    prewrite_messages = _build_prewrite_messages(repo_root=repo_root, template_id="hard_news_spiritual_response", context=ctx)

    values: dict[str, str] = {}
    for slot in slots:
        prompt = _render_prompt(slot_templates[slot], {**ctx, **values})
        out = _chat_once(
            client=client,
            model=model,
            user_prompt=prompt,
            temperature=temperature,
            max_tokens=_slot_token_budget(slot, max_tokens),
            disable_thinking=disable_thinking,
            system_prompt=system_prompt,
            base_messages=prewrite_messages,
        )
        if not out:
            return None
        values[slot] = out

    body_parts = [
        f"<h1>{values['headline'].strip()}</h1>",
        _to_html_paragraph(values["news_summary"]),
        _to_html_paragraph(values["youth_impact"]),
        _to_html_paragraph(values["teacher_perspective"]),
        _to_html_paragraph(values["sdg_un_tie"].replace("\n", "<br>")),
        _to_html_paragraph(values["forward_look"]),
    ]
    if source_html:
        body_parts.append(source_html)
    elif item.get("url"):
        body_parts.append(f"<p><em>Source: <a href=\"{item['url']}\">{item['url']}</a></em></p>")
    return "\n\n".join([p for p in body_parts if p.strip()])


def _expand_youth_feature_slotwise(
    *,
    content: str,
    item: dict[str, Any],
    teacher: dict[str, Any] | None,
    sdg_label: str,
    config: dict[str, Any],
) -> str | None:
    repo_root = Path(__file__).resolve().parents[2]
    pearl_root = repo_root / "pearl_news"
    prompts_root = pearl_root / "prompts"
    slots = (
        "headline",
        "youth_narrative",
        "data_research",
        "teacher_reflection",
        "sdg_framework",
        "solutions",
    )
    slot_templates = {s: _load_slot_prompt(prompts_root, "youth_feature", s) for s in slots}
    if not all(slot_templates.values()):
        return None
    system_prompt = _load_system_prompt(prompts_root)

    base_url = (config.get("base_url") or "").strip()
    model = config.get("model") or "qwen3-14b"
    api_key = (config.get("api_key") or "lm-studio").strip()
    timeout = float(config.get("timeout") or 360)
    max_tokens = int(config.get("max_tokens") or 2048)
    temperature = float(config.get("temperature") or 0.5)
    disable_thinking = config.get("disable_thinking", True)
    if not base_url:
        return None
    client = _create_openai_client(config)
    if client is None:
        return None

    teacher_name = (teacher or {}).get("display_name") or "Forum Teacher"
    teacher_tradition = (teacher or {}).get("tradition") or "interfaith"
    teacher_quotes = _teacher_quotes_text(teacher)
    source_html = _extract_source_line_html(content)

    ctx = {
        "news_event": (
            f"Title: {_short_text(item.get('raw_title') or item.get('title') or '', max_chars=120)}\n"
            f"Summary: {_short_text(item.get('raw_summary') or item.get('summary') or '', max_chars=220)}\n"
            f"URL: {item.get('url')}\nDate: {item.get('pub_date')}"
        ),
        "news_event_topic": item.get("topic") or "global affairs",
        "topic": item.get("topic") or "global affairs",
        "youth_impact": _short_text(item.get("summary") or item.get("raw_summary") or "", max_chars=220),
        "teacher_name": teacher_name,
        "teacher_tradition": teacher_tradition,
        "teacher_framework": _teacher_framework_text(teacher),
        "teacher_quotes_practices": teacher_quotes,
        "sdg_number": item.get("primary_sdg") or "17",
        "sdg_name": sdg_label,
        "un_agency_name": item.get("un_body") or "United Nations",
    }
    prewrite_messages = _build_prewrite_messages(repo_root=repo_root, template_id="youth_feature", context=ctx)

    values: dict[str, str] = {}
    for slot in slots:
        prompt = _render_prompt(slot_templates[slot], {**ctx, **values})
        out = _chat_once(
            client=client,
            model=model,
            user_prompt=prompt,
            temperature=temperature,
            max_tokens=_slot_token_budget(slot, max_tokens),
            disable_thinking=disable_thinking,
            system_prompt=system_prompt,
            base_messages=prewrite_messages,
        )
        if not out:
            return None
        values[slot] = out

    body_parts = [
        f"<h1>{values['headline'].strip()}</h1>",
        _to_html_paragraph(values["youth_narrative"]),
        _to_html_paragraph(values["data_research"]),
        _to_html_paragraph(values["teacher_reflection"]),
        _to_html_paragraph(values["sdg_framework"].replace("\n", "<br>")),
        _to_html_paragraph(values["solutions"]),
    ]
    if source_html:
        body_parts.append(source_html)
    elif item.get("url"):
        body_parts.append(f"<p><em>Source: <a href=\"{item['url']}\">{item['url']}</a></em></p>")
    return "\n\n".join([p for p in body_parts if p.strip()])


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
    repair_feedback: str = "",
) -> str | None:
    """
    Call OpenAI-compatible API to expand article HTML toward target_word_count.
    v2: Injects teacher, research_excerpt, language, audience into user message.
    Returns expanded content or None on failure.
    """
    base_url = (config.get("base_url") or "").strip()
    model = config.get("model") or "qwen3-14b"
    api_key = (config.get("api_key") or "lm-studio").strip()
    timeout = float(config.get("timeout") or 360)
    max_tokens = int(config.get("max_tokens") or 2048)
    temperature = float(config.get("temperature") or 0.5)
    # Qwen3 ships with thinking mode ON by default; disable it for article writing.
    # Setting enable_thinking=False via extra_body removes the <think> block and
    # saves ~1200-1800 tokens per call (roughly 3-4 minutes on M4 at Q4_K_M).
    disable_thinking = config.get("disable_thinking", True)

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
    repair_block = ""
    if repair_feedback.strip():
        repair_block = (
            "\nREPAIR FEEDBACK FROM FAILED GATES (must fix all):\n"
            f"{repair_feedback.strip()}\n"
        )

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
{repair_block}

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

    # Use httpx Timeout so connect/read/write all honour the full timeout value,
    # not just the default 5-second httpx socket timeout that was causing
    # "Client disconnected" at ~4 min even though timeout=360 was set.
    try:
        from httpx import Timeout as HttpxTimeout
        http_timeout = HttpxTimeout(timeout)
    except ImportError:
        http_timeout = timeout  # fallback: scalar still better than nothing

    client = OpenAI(base_url=base_url, api_key=api_key, timeout=http_timeout)

    # Build extra_body: disable Qwen3 thinking mode if configured
    extra_body = {}
    if disable_thinking:
        extra_body["enable_thinking"] = False

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        **({"extra_body": extra_body} if extra_body else {}),
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
    model = config.get("model") or "qwen3-14b"
    disable_thinking = config.get("disable_thinking", True)
    prompts_root = root / "prompts"
    system_prompt = _load_system_prompt(prompts_root)

    try:
        client = _create_openai_client(config)
    except Exception as e:
        logger.warning("LLM expansion: client init failed: %s", e)
        client = None

    if client is None:
        for item in items:
            item["_expansion_failed"] = True
            item["_expansion_error"] = "llm_client_init_failed"
        return items

    ok, preflight_error = _preflight_chat_health(
        client=client,
        model=model,
        disable_thinking=disable_thinking,
        config=config,
        system_prompt=system_prompt,
    )
    if not ok:
        logger.warning("LLM expansion preflight failed: %s", preflight_error)
        for item in items:
            item["_expansion_failed"] = True
            item["_expansion_error"] = preflight_error
        return items

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
        repair_feedback = item.get("_repair_feedback") or ""

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
                if template_id == "commentary":
                    expanded = _expand_commentary_slotwise(
                        content=content,
                        item=item,
                        teacher=teacher,
                        sdg_label=sdg_label,
                        config=attempt_config,
                    )
                elif template_id == "interfaith_dialogue_report":
                    expanded = _expand_interfaith_slotwise(
                        content=content,
                        item=item,
                        teacher=teacher,
                        sdg_label=sdg_label,
                        config=attempt_config,
                    )
                elif template_id == "explainer_context":
                    expanded = _expand_explainer_slotwise(
                        content=content,
                        item=item,
                        teacher=teacher,
                        sdg_label=sdg_label,
                        config=attempt_config,
                    )
                elif template_id == "hard_news_spiritual_response":
                    expanded = _expand_hard_news_slotwise(
                        content=content,
                        item=item,
                        teacher=teacher,
                        sdg_label=sdg_label,
                        config=attempt_config,
                    )
                elif template_id == "youth_feature":
                    expanded = _expand_youth_feature_slotwise(
                        content=content,
                        item=item,
                        teacher=teacher,
                        sdg_label=sdg_label,
                        config=attempt_config,
                    )
                else:
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
                        repair_feedback=repair_feedback,
                    )
            except Exception as e:
                logger.warning("Expansion attempt %d failed for %s: %s", attempt, item.get("id"), e)
                item["_expansion_error"] = str(e)
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
