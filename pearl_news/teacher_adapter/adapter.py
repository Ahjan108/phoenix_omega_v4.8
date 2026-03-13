"""
Pearl News Teacher Adapter — build article-ready payload from Pearl Prime.

Authority: specs/PEARL_NEWS_TEACHER_ADAPTER_SPEC.md §2.3, §4.

Prefers explicit structured fields when they exist; warns or fails when inferring weak fields.
Source order: doctrine -> authoring layer -> approved atoms.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class NewsTeacherPayload:
    """
    Compact teacher payload for Pearl News article generation (adapter spec §4).

    Required: teacher_id, teacher_name, tradition, topic_fit, teacher_framework_term,
    teacher_diagnostic_claim, teacher_named_practice, teacher_quotes,
    teacher_safety_boundary, teacher_behavior_bridge, teacher_civic_bridge.
    """

    teacher_id: str
    teacher_name: str
    tradition: str
    topic_fit: str  # validated against roster news_topics when possible
    teacher_framework_term: str
    teacher_diagnostic_claim: str
    teacher_named_practice: str
    teacher_quotes: list[str]
    teacher_safety_boundary: str
    teacher_behavior_bridge: str
    teacher_civic_bridge: str
    # Optional (spec §4.2)
    teacher_preferred_phrases: list[str] = field(default_factory=list)
    teacher_forbidden_moves: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = {
            "teacher_id": self.teacher_id,
            "teacher_name": self.teacher_name,
            "tradition": self.tradition,
            "topic_fit": self.topic_fit,
            "teacher_framework_term": self.teacher_framework_term,
            "teacher_diagnostic_claim": self.teacher_diagnostic_claim,
            "teacher_named_practice": self.teacher_named_practice,
            "teacher_quotes": list(self.teacher_quotes),
            "teacher_safety_boundary": self.teacher_safety_boundary,
            "teacher_behavior_bridge": self.teacher_behavior_bridge,
            "teacher_civic_bridge": self.teacher_civic_bridge,
        }
        if self.teacher_preferred_phrases:
            d["teacher_preferred_phrases"] = list(self.teacher_preferred_phrases)
        if self.teacher_forbidden_moves:
            d["teacher_forbidden_moves"] = list(self.teacher_forbidden_moves)
        return d


@dataclass
class BuildResult:
    """Result of build_news_payload: payload (or None), warnings, and which fields were inferred."""

    payload: NewsTeacherPayload | None
    warnings: list[str] = field(default_factory=list)
    inferred_fields: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.payload is not None and len(self.warnings) == 0


def get_teacher_news_topics(repo_root: Path, teacher_id: str, roster: dict[str, Any] | None = None) -> list[str]:
    """
    Return allowed news_topics for this teacher from Pearl News roster (canonical source).
    Normalized to lowercase. Empty if roster missing or teacher not in roster.
    """
    if roster is None:
        roster_path = repo_root / "pearl_news" / "config" / "teacher_news_roster.yaml"
        roster = _load_yaml(roster_path) if roster_path.exists() else {}
    teachers = roster.get("teachers") or {}
    entry = teachers.get(teacher_id) or {}
    topics = entry.get("news_topics") or []
    return [str(t).lower().strip() for t in topics if t]


def _is_teacher_active(repo_root: Path, teacher_id: str, roster: dict[str, Any] | None = None) -> bool:
    """Only active teachers may be used by live Pearl News pipelines."""
    if roster is None:
        roster_path = repo_root / "pearl_news" / "config" / "teacher_news_roster.yaml"
        roster = _load_yaml(roster_path) if roster_path.exists() else {}
    roster_entry = ((roster or {}).get("teachers") or {}).get(teacher_id) or {}
    if roster_entry and not roster_entry.get("active", True):
        return False
    reg_path = repo_root / "config" / "teachers" / "teacher_registry.yaml"
    reg = _load_yaml(reg_path) if reg_path.exists() else {}
    reg_entry = (reg.get("teachers") or {}).get(teacher_id) or {}
    if reg_entry and not reg_entry.get("active", True):
        return False
    return True


def validate_topic_fit(
    topic_fit: str,
    allowed_topics: list[str],
) -> tuple[bool, str | None]:
    """
    Validate topic_fit against allowed news_topics. Returns (valid, error_message).
    """
    topic_fit = (topic_fit or "").strip().lower()
    if not topic_fit:
        return False, "topic_fit is empty"
    if not allowed_topics:
        return True, None  # no roster data: cannot validate
    if topic_fit in allowed_topics:
        return True, None
    # Allow partial match (e.g. topic "mental_health" vs "mental_health")
    for t in allowed_topics:
        if t in topic_fit or topic_fit in t:
            return True, None
    return False, f"topic_fit '{topic_fit}' not in teacher news_topics {allowed_topics}"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return dict(data) if data else {}
    except Exception:
        return {}


def _load_doctrine(repo_root: Path, teacher_id: str) -> dict[str, Any]:
    doctrine_path = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine" / "doctrine.yaml"
    if not doctrine_path.exists():
        doctrine_path = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "doctrine.yaml"
    return _load_yaml(doctrine_path)


def _glossary_terms(doctrine: dict[str, Any]) -> set[str]:
    """Extract preferred terms from doctrine glossary (left side of 'term / definition')."""
    out: set[str] = set()
    for g in doctrine.get("glossary") or []:
        if isinstance(g, str) and " / " in g:
            out.add(g.split(" / ")[0].strip().lower())
    return out


def _quotes_from_atoms(
    repo_root: Path,
    teacher_id: str,
    doctrine: dict[str, Any],
    max_quotes: int = 5,
) -> list[str]:
    """
    Extract quote-like lines from HOOK and REFLECTION. Prefer atoms whose body or tags
    align with doctrine glossary/signature terms (concept-aligned), then fill with others.
    """
    bank = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id / "approved_atoms"
    preferred_terms = _glossary_terms(doctrine)
    primary_methods = doctrine.get("primary_methods") or ""
    if isinstance(primary_methods, str):
        for w in primary_methods.lower().split():
            if len(w) > 4:
                preferred_terms.add(w)
    elif isinstance(primary_methods, list):
        for x in primary_methods[:5]:
            if isinstance(x, str) and len(x) > 3:
                preferred_terms.add(x.lower().strip())

    candidates: list[tuple[int, str]] = []  # (score: more preferred terms = higher), body_line
    for slot in ("HOOK", "REFLECTION"):
        slot_dir = bank / slot
        if not slot_dir.exists():
            continue
        for p in sorted(slot_dir.glob("*.yaml"))[:15]:
            data = _load_yaml(p)
            body = (data.get("body") or "").strip()
            if not body or len(body) > 400:
                continue
            line = body.split("\n")[0].strip() if "\n" in body else body
            if not line:
                continue
            line_lower = line.lower()
            tags = (data.get("tags") or [])
            tag_str = " ".join(str(t) for t in tags).lower()
            score = sum(1 for t in preferred_terms if t in line_lower or t in tag_str)
            candidates.append((score, line))

    # Sort by score desc, then dedupe by text
    candidates.sort(key=lambda x: (-x[0], x[1]))
    seen: set[str] = set()
    quotes: list[str] = []
    for _score, line in candidates:
        if line not in seen and len(quotes) < max_quotes:
            seen.add(line)
            quotes.append(line)
    return quotes[:max_quotes]


def _first_line(text: str | list | None) -> str:
    if isinstance(text, list) and text:
        return str(text[0]).strip()
    if isinstance(text, str) and text.strip():
        return text.strip().split("\n")[0].strip()
    return ""


def build_news_payload(
    teacher_id: str,
    repo_root: Path,
    topic_fit: str,
    *,
    roster: dict[str, Any] | None = None,
    doctrine_override: dict[str, Any] | None = None,
    require_topic_in_roster: bool = True,
) -> BuildResult:
    """
    Build Pearl News adapter payload from Pearl Prime teacher truth (spec §2.3, §4).

    - Prefers explicit structured fields when they exist; records inferred fields and warns when weak.
    - topic_fit is validated against teacher news_topics in roster when require_topic_in_roster=True.
    - Returns BuildResult with payload (or None on hard failure), warnings, and inferred_fields.
    """
    warnings: list[str] = []
    inferred: list[str] = []
    doctrine = doctrine_override or _load_doctrine(repo_root, teacher_id)
    if not doctrine:
        return BuildResult(payload=None, warnings=["Doctrine missing; cannot build payload."])
    if not _is_teacher_active(repo_root, teacher_id, roster):
        return BuildResult(payload=None, warnings=[f"teacher '{teacher_id}' is inactive for Pearl News runtime"])

    # Topic contract: validate against roster news_topics
    allowed_topics = get_teacher_news_topics(repo_root, teacher_id, roster)
    valid_topic, topic_err = validate_topic_fit(topic_fit, allowed_topics)
    if not valid_topic and topic_err:
        if require_topic_in_roster and allowed_topics:
            return BuildResult(
                payload=None,
                warnings=[f"topic_fit contract: {topic_err}"],
            )
        warnings.append(f"topic_fit contract: {topic_err}")

    # Load roster/registry for display name and tradition
    if roster is None:
        roster_path = repo_root / "pearl_news" / "config" / "teacher_news_roster.yaml"
        roster = _load_yaml(roster_path) if roster_path.exists() else {}
    teachers_config = (roster.get("teachers") or {}).get(teacher_id) or {}
    reg_path = repo_root / "config" / "teachers" / "teacher_registry.yaml"
    reg = _load_yaml(reg_path) if reg_path.exists() else {}
    reg_teacher = (reg.get("teachers") or {}).get(teacher_id) or {}

    teacher_name = (
        doctrine.get("display_name")
        or teachers_config.get("display_name")
        or reg_teacher.get("display_name")
        or teacher_id
    )
    if isinstance(teacher_name, list):
        teacher_name = teacher_name[0] if teacher_name else teacher_id
    tradition = (
        doctrine.get("tradition")
        or teachers_config.get("tradition")
        or reg_teacher.get("tradition")
        or "interfaith"
    )
    if isinstance(tradition, list):
        tradition = tradition[0] if tradition else "interfaith"

    # Framework term: explicit from doctrine first
    framework_term = _first_line(doctrine.get("core_principles")) or _first_line(doctrine.get("primary_methods"))
    if not framework_term or len(framework_term.strip()) < 8:
        framework_term = tradition if tradition and tradition != "interfaith" else ""
    if not framework_term:
        inferred.append("teacher_framework_term")
        framework_term = "(no explicit framework; add to doctrine)"
        warnings.append("teacher_framework_term is inferred; doctrine has no core_principles/primary_methods.")

    # Diagnostic claim: from doctrine core_principles first; else one reflection-style atom
    diagnostic_claim = _first_line(doctrine.get("core_principles")) or ""
    if not diagnostic_claim or len(diagnostic_claim.strip()) < 15:
        ref_quotes = _quotes_from_atoms(repo_root, teacher_id, doctrine, max_quotes=1)
        if ref_quotes:
            diagnostic_claim = ref_quotes[0]
            inferred.append("teacher_diagnostic_claim")
        else:
            diagnostic_claim = ""
        if not diagnostic_claim:
            warnings.append("teacher_diagnostic_claim missing; no doctrine core_principles and no suitable atoms.")

    # Named practice: explicit from doctrine
    named_practice = _first_line(doctrine.get("signature_practices")) or _first_line(doctrine.get("primary_methods"))
    if not named_practice or len(named_practice.strip()) < 2:
        inferred.append("teacher_named_practice")
        named_practice = "reflection and grounding"
        warnings.append("teacher_named_practice inferred; doctrine has no signature_practices/primary_methods.")

    # Quotes: concept-aligned from atoms (glossary/primary_methods preferred)
    teacher_quotes = _quotes_from_atoms(repo_root, teacher_id, doctrine, max_quotes=5)
    if not teacher_quotes:
        warnings.append("teacher_quotes empty; no HOOK/REFLECTION atoms or bank missing.")

    # Safety boundary: always from doctrine (forbidden_claims + tone_boundaries)
    forbidden = doctrine.get("forbidden_claims") or doctrine.get("avoid_claims") or []
    tone = doctrine.get("tone_boundaries") or []
    parts = []
    if isinstance(forbidden, list) and forbidden:
        parts.append("Do not: " + "; ".join(str(x) for x in forbidden[:3]))
    if isinstance(tone, list) and tone:
        parts.append("Tone: " + "; ".join(str(x) for x in tone[:2]))
    teacher_safety_boundary = " ".join(parts) if parts else "No therapeutic overclaim; no false certainty; no devotional pressure."

    # Bridges: explicit from doctrine if present
    behavior_bridge = _first_line(doctrine.get("behavior_bridge"))
    if not behavior_bridge or len(behavior_bridge.strip()) < 10:
        inferred.append("teacher_behavior_bridge")
        behavior_bridge = "Offer one concrete practice or reflection step readers can try."
    civic_bridge = _first_line(doctrine.get("civic_bridge"))
    if not civic_bridge or len(civic_bridge.strip()) < 8:
        inferred.append("teacher_civic_bridge")
        civic_bridge = "Connect to shared responsibility or community without demanding activism."

    # Optional: preferred phrases from glossary, forbidden from doctrine
    preferred: list[str] = []
    if isinstance(doctrine.get("glossary"), list):
        for g in doctrine["glossary"][:5]:
            if isinstance(g, str) and " / " in g:
                preferred.append(g.split(" / ")[0].strip())
    forbidden_moves: list[str] = []
    if isinstance(doctrine.get("forbidden_claims"), list):
        forbidden_moves = [str(x) for x in doctrine["forbidden_claims"][:5]]

    payload = NewsTeacherPayload(
        teacher_id=teacher_id,
        teacher_name=str(teacher_name),
        tradition=str(tradition),
        topic_fit=topic_fit.strip().lower(),
        teacher_framework_term=framework_term,
        teacher_diagnostic_claim=diagnostic_claim,
        teacher_named_practice=named_practice,
        teacher_quotes=teacher_quotes,
        teacher_safety_boundary=teacher_safety_boundary,
        teacher_behavior_bridge=behavior_bridge,
        teacher_civic_bridge=civic_bridge,
        teacher_preferred_phrases=preferred,
        teacher_forbidden_moves=forbidden_moves,
    )
    return BuildResult(payload=payload, warnings=warnings, inferred_fields=inferred)
