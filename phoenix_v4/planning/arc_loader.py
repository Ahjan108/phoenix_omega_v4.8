"""
Arc Blueprint loader and schema validator (Arc-First Canonical Spec v1.1).
Structural validation only: required fields and value domains. No prose inspection.

Auto-generation: if a concrete arc file is missing, the loader can generate one
on-the-fly from a parameterized template via arc_generator.generate_arc().
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_ROOT = REPO_ROOT / "config"
DEFAULT_ARCS_ROOT = CONFIG_ROOT / "source_of_truth" / "master_arcs"
TEMPLATES_ROOT = DEFAULT_ARCS_ROOT / "templates"

# Default template selection order. First match wins.
DEFAULT_TEMPLATE_ID = "standard_escalation"

log = logging.getLogger(__name__)

REQUIRED_ARC_KEYS = frozenset({
    "arc_id", "persona", "topic", "engine", "format",
    "chapter_count", "emotional_curve", "emotional_temperature_curve",
    "chapter_intent", "reflection_strategy_sequence", "cost_chapter_index",
    "resolution_type", "motif",
})
ALLOWED_RESOLUTION_TYPES = frozenset({"open_loop", "internal_shift_only", "grounded_reframe", "identity_shift"})
ALLOWED_TEMPERATURES = frozenset({"cool", "warm", "hot"})
ALLOWED_REFLECTION_STRATEGIES = frozenset({"didactic", "socratic", "narrative_embedded"})
# DEV SPEC 3: Emotional Role Taxonomy
ALLOWED_EMOTIONAL_ROLES = frozenset({"recognition", "destabilization", "reframe", "stabilization", "integration"})
ROLE_SIG_MAP = {"recognition": "r", "destabilization": "d", "reframe": "f", "stabilization": "s", "integration": "i"}


@dataclass
class ArcBlueprint:
    """Loaded arc; structural only. DEV SPEC 3: emotional_role_sequence, opening_override. Asymmetry: chapter_weights."""
    arc_id: str
    persona: str
    topic: str
    engine: str
    format: str
    chapter_count: int
    emotional_curve: list[int]
    emotional_temperature_curve: dict[int, str]
    chapter_intent: dict[int, str]
    reflection_strategy_sequence: list[str]
    cost_chapter_index: int
    resolution_type: str
    motif: dict[str, Any]
    raw: dict[str, Any]
    emotional_role_sequence: list[str]
    opening_override: bool = False
    # Asymmetry: optional weight/density per chapter (validators may allow unevenness)
    chapter_weights: Optional[list[float]] = None  # length == chapter_count
    # Chapter thesis: one sentence per chapter (claim the chapter proves). Optional; used for TAKEAWAY slot and atom filtering.
    chapter_thesis: Optional[dict[int, str]] = None  # keys 1..chapter_count


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def validate_arc_schema(arc: dict[str, Any]) -> list[str]:
    """
    Structural validation only. Returns list of errors; empty if valid.
    Does not inspect prose. Checks required fields and value domains.
    """
    errors: list[str] = []
    missing = REQUIRED_ARC_KEYS - set(arc.keys())
    if missing:
        errors.append(f"Missing required keys: {sorted(missing)}")

    chapter_count = arc.get("chapter_count")
    if chapter_count is not None:
        if not isinstance(chapter_count, int) or chapter_count < 1:
            errors.append("chapter_count must be a positive integer")
        nc = chapter_count
        curve = arc.get("emotional_curve")
        if curve is not None:
            if not isinstance(curve, list) or len(curve) != nc:
                errors.append(f"emotional_curve must be list of length chapter_count ({nc})")
            else:
                for i, b in enumerate(curve):
                    if not isinstance(b, int) or not (1 <= b <= 5):
                        errors.append(f"emotional_curve[{i}] must be int 1-5, got {b!r}")
        temp_curve = arc.get("emotional_temperature_curve")
        if temp_curve is not None:
            if not isinstance(temp_curve, dict):
                errors.append("emotional_temperature_curve must be dict (chapter index -> cool|warm|hot)")
            else:
                for k, v in temp_curve.items():
                    if isinstance(k, int) and 1 <= k <= nc and v not in ALLOWED_TEMPERATURES:
                        errors.append(f"emotional_temperature_curve[{k}] must be one of {sorted(ALLOWED_TEMPERATURES)}, got {v!r}")
        ref_seq = arc.get("reflection_strategy_sequence")
        if ref_seq is not None:
            if not isinstance(ref_seq, list) or len(ref_seq) != nc:
                errors.append(f"reflection_strategy_sequence must be list of length chapter_count ({nc})")
            else:
                for i, s in enumerate(ref_seq):
                    if s not in ALLOWED_REFLECTION_STRATEGIES:
                        errors.append(f"reflection_strategy_sequence[{i}] must be one of {sorted(ALLOWED_REFLECTION_STRATEGIES)}, got {s!r}")
        cost_idx = arc.get("cost_chapter_index")
        if cost_idx is not None:
            if not isinstance(cost_idx, int) or not (1 <= cost_idx <= nc):
                errors.append(f"cost_chapter_index must be int 1..chapter_count ({nc}), got {cost_idx!r}")

    res = arc.get("resolution_type")
    if res is not None and res not in ALLOWED_RESOLUTION_TYPES:
        errors.append(f"resolution_type must be one of {sorted(ALLOWED_RESOLUTION_TYPES)}, got {res!r}")

    motif = arc.get("motif")
    if motif is not None and not isinstance(motif, dict):
        errors.append("motif must be a dict (e.g. primary_symbol, tonal_signature)")

    # Asymmetry: optional chapter_weights (length chapter_count, numeric)
    nc_weights = arc.get("chapter_count")
    if nc_weights is not None and isinstance(nc_weights, int) and nc_weights >= 1:
        weights = arc.get("chapter_weights")
        if weights is not None:
            if not isinstance(weights, list) or len(weights) != nc_weights:
                errors.append(f"chapter_weights must be list of length chapter_count ({nc_weights})")
            else:
                for i, w in enumerate(weights):
                    try:
                        float(w)
                    except (TypeError, ValueError):
                        errors.append(f"chapter_weights[{i}] must be numeric, got {w!r}")

    # Optional chapter_thesis: when present, must have one string per chapter (keys 1..chapter_count)
    nc_thesis = arc.get("chapter_count")
    if nc_thesis is not None and isinstance(nc_thesis, int) and nc_thesis >= 1:
        thesis = arc.get("chapter_thesis")
        if thesis is not None:
            if not isinstance(thesis, dict):
                errors.append("chapter_thesis must be a dict (chapter index -> thesis sentence)")
            else:
                for k, v in thesis.items():
                    try:
                        ki = int(k)
                        if ki < 1 or ki > nc_thesis:
                            errors.append(f"chapter_thesis key {k} must be 1..chapter_count ({nc_thesis})")
                    except (TypeError, ValueError):
                        errors.append(f"chapter_thesis key must be int, got {k!r}")
                    if not isinstance(v, str) or not v.strip():
                        errors.append(f"chapter_thesis[{k}] must be non-empty string")

    # DEV SPEC 3: emotional_role_sequence
    nc = arc.get("chapter_count")
    if nc is not None and isinstance(nc, int) and nc >= 1:
        role_seq = arc.get("emotional_role_sequence")
        chapters = arc.get("chapters")
        if chapters and isinstance(chapters, list) and len(chapters) == nc:
            role_seq = []
            for ch in chapters:
                if isinstance(ch, dict) and "emotional_role" in ch:
                    role_seq.append(str(ch["emotional_role"]))
                else:
                    role_seq = None
                    break
        if role_seq is None or not isinstance(role_seq, list):
            errors.append("emotional_role_sequence required (list of length chapter_count) or chapters[].emotional_role")
        elif len(role_seq) != nc:
            errors.append(f"emotional_role_sequence length must be chapter_count ({nc}), got {len(role_seq)}")
        else:
            for i, r in enumerate(role_seq):
                if r not in ALLOWED_EMOTIONAL_ROLES:
                    errors.append(f"emotional_role_sequence[{i}] must be one of {sorted(ALLOWED_EMOTIONAL_ROLES)}, got {r!r}")
            if not errors:
                if role_seq[0] != "recognition" and not arc.get("opening_override"):
                    errors.append("Chapter 0 must have emotional_role recognition (or set opening_override: true)")
                if role_seq[-1] != "integration":
                    errors.append("Last chapter must have emotional_role integration")
                run_len = 1
                for i in range(1, len(role_seq)):
                    if role_seq[i] == role_seq[i - 1]:
                        run_len += 1
                        if run_len > 2:
                            errors.append(f"Max 2 consecutive same emotional_role; chapters {i - 1}-{i} repeat {role_seq[i]}")
                    else:
                        run_len = 1
                unique_roles = len(set(role_seq))
                if nc >= 6 and unique_roles < 4:
                    errors.append(f"chapter_count >= 6 must include at least 4 of 5 roles; got {unique_roles}")
                elif 4 <= nc <= 5 and unique_roles < 3:
                    errors.append(f"chapter_count 4-5 must include at least 3 of 5 roles; got {unique_roles}")

    return errors


def _auto_generate_arc(
    persona: str,
    topic: str,
    engine: str,
    format_id: str,
    chapter_count: int = 10,
    template_id: str = DEFAULT_TEMPLATE_ID,
    cache: bool = True,
    arcs_root: Optional[Path] = None,
) -> dict:
    """
    Generate a concrete arc dict from a parameterized template.
    If cache=True, writes the generated YAML to arcs_root for future loads.
    Imports arc_generator lazily to avoid circular deps.
    """
    import importlib
    gen_mod_path = REPO_ROOT / "tools" / "arc_generator.py"
    if not gen_mod_path.exists():
        raise ValueError(f"arc_generator.py not found at {gen_mod_path}; cannot auto-generate arc")
    spec = importlib.util.spec_from_file_location("arc_generator", gen_mod_path)
    gen_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen_mod)

    template_path = TEMPLATES_ROOT / f"{template_id}.yaml"
    if not template_path.exists():
        raise ValueError(f"Template not found: {template_path}")

    root = arcs_root or DEFAULT_ARCS_ROOT
    out_path = root / f"{persona}__{topic}__{engine}__{format_id}.yaml" if cache else None

    log.info(
        "Auto-generating arc: persona=%s topic=%s engine=%s format=%s chapters=%d template=%s",
        persona, topic, engine, format_id, chapter_count, template_id,
    )
    arc_data = gen_mod.generate_arc(
        template_path=template_path,
        persona=persona,
        topic=topic,
        format_id=format_id,
        chapter_count=chapter_count,
        engine=engine,
        out_path=out_path,
    )
    return arc_data


def load_arc(arc_path: Path, arcs_root: Optional[Path] = None) -> ArcBlueprint:
    """
    Load and validate arc YAML. Raises ValueError if file missing or schema invalid.
    """
    if not arc_path.exists():
        raise ValueError(f"Arc file not found: {arc_path}")
    data = _load_yaml(arc_path)
    if not data:
        raise ValueError(f"Arc file empty or invalid YAML: {arc_path}")
    errs = validate_arc_schema(data)
    if errs:
        raise ValueError(f"Arc schema invalid: {'; '.join(errs)}")

    nc = int(data["chapter_count"])
    # Normalize temperature curve: keys may be int or string "1","2",...
    temp_curve = data.get("emotional_temperature_curve") or {}
    temp_curve = {int(k): str(v) for k, v in temp_curve.items()}
    chapter_intent = data.get("chapter_intent") or {}
    chapter_intent = {int(k): str(v) for k, v in chapter_intent.items()}
    motif = data.get("motif") or {}
    # emotional_role_sequence: from explicit list or from chapters[]
    role_seq = data.get("emotional_role_sequence")
    if not role_seq and isinstance(data.get("chapters"), list) and len(data["chapters"]) == nc:
        role_seq = []
        for ch in data["chapters"]:
            if isinstance(ch, dict) and "emotional_role" in ch:
                role_seq.append(str(ch["emotional_role"]))
        if len(role_seq) != nc:
            role_seq = None
    if not role_seq or len(role_seq) != nc:
        raise ValueError("Arc must define emotional_role_sequence (length chapter_count) or chapters[].emotional_role")
    emotional_role_sequence = list(role_seq)
    opening_override = bool(data.get("opening_override", False))
    chapter_weights = None
    if isinstance(data.get("chapter_weights"), list) and len(data["chapter_weights"]) == nc:
        try:
            chapter_weights = [float(w) for w in data["chapter_weights"]]
        except (TypeError, ValueError):
            chapter_weights = None

    chapter_thesis = None
    raw_thesis = data.get("chapter_thesis")
    if isinstance(raw_thesis, dict) and raw_thesis:
        chapter_thesis = {int(k): str(v).strip() for k, v in raw_thesis.items() if str(v).strip()}

    return ArcBlueprint(
        arc_id=str(data["arc_id"]),
        persona=str(data["persona"]),
        topic=str(data["topic"]),
        engine=str(data["engine"]),
        format=str(data["format"]),
        chapter_count=nc,
        emotional_curve=list(data["emotional_curve"]),
        emotional_temperature_curve=temp_curve,
        chapter_intent=chapter_intent,
        reflection_strategy_sequence=list(data["reflection_strategy_sequence"]),
        cost_chapter_index=int(data["cost_chapter_index"]),
        resolution_type=str(data["resolution_type"]),
        motif=motif,
        raw=data,
        emotional_role_sequence=emotional_role_sequence,
        opening_override=opening_override,
        chapter_weights=chapter_weights,
        chapter_thesis=chapter_thesis,
    )


def validate_arc_format_role_compat(arc: ArcBlueprint, format_plan: dict) -> list[str]:
    """
    DEV SPEC 3: Fail if arc uses roles whose required slots are missing from format.
    Returns list of errors; empty if compatible.
    """
    errors: list[str] = []
    try:
        req_path = REPO_ROOT / "config" / "format_selection" / "emotional_role_slot_requirements.yaml"
        if not req_path.exists() or yaml is None:
            return []
        data = _load_yaml(req_path)
        role_reqs = (data.get("role_requirements") or {})
        slot_definitions = format_plan.get("slot_definitions") or []
        format_slots = set()
        for row in slot_definitions:
            for s in row:
                format_slots.add(str(s).strip())
        for ch_idx, role in enumerate(arc.emotional_role_sequence):
            required = (role_reqs.get(role) or {}).get("must_include_slots") or []
            if not required:
                continue
            if not any(s in format_slots for s in required):
                errors.append(
                    f"Arc chapter {ch_idx} has emotional_role={role} but format lacks required slot "
                    f"(need one of {required})"
                )
    except Exception:
        pass
    return errors


def resolve_arc_path(
    persona: str,
    topic: str,
    engine: str,
    format_id: str,
    arcs_root: Optional[Path] = None,
) -> Path:
    """Canonical arc file path: persona__topic__engine__format.yaml"""
    root = arcs_root or DEFAULT_ARCS_ROOT
    name = f"{persona}__{topic}__{engine}__{format_id}.yaml"
    return root / name


def load_or_generate_arc(
    persona: str,
    topic: str,
    engine: str,
    format_id: str,
    chapter_count: int = 10,
    template_id: str = DEFAULT_TEMPLATE_ID,
    arcs_root: Optional[Path] = None,
    cache: bool = True,
) -> ArcBlueprint:
    """
    Primary entry point. Tries to load a pre-built arc YAML.
    If none exists, auto-generates from template, validates, and returns.
    Generated arc is cached to disk by default for future runs.

    Parameters
    ----------
    persona : str       Persona slug (e.g. "nyc_executives")
    topic : str         Topic slug (e.g. "anxiety")
    engine : str        Engine slug (e.g. "overwhelm")
    format_id : str     Format ID (e.g. "F002")
    chapter_count : int Chapters (used only when generating; ignored if arc exists)
    template_id : str   Template to use for generation (default: standard_escalation)
    arcs_root : Path    Override arc directory
    cache : bool        Write generated arc to disk for reuse
    """
    root = arcs_root or DEFAULT_ARCS_ROOT
    arc_path = resolve_arc_path(persona, topic, engine, format_id, root)

    if arc_path.exists():
        return load_arc(arc_path, root)

    # Auto-generate from template
    log.info("Pre-built arc not found at %s — auto-generating from template '%s'", arc_path, template_id)
    data = _auto_generate_arc(
        persona=persona,
        topic=topic,
        engine=engine,
        format_id=format_id,
        chapter_count=chapter_count,
        template_id=template_id,
        cache=cache,
        arcs_root=root,
    )
    errs = validate_arc_schema(data)
    if errs:
        raise ValueError(f"Auto-generated arc failed validation: {'; '.join(errs)}")

    # Build ArcBlueprint from data (same logic as load_arc)
    nc = int(data["chapter_count"])
    temp_curve = {int(k): str(v) for k, v in (data.get("emotional_temperature_curve") or {}).items()}
    chapter_intent = {int(k): str(v) for k, v in (data.get("chapter_intent") or {}).items()}
    motif = data.get("motif") or {}
    role_seq = data.get("emotional_role_sequence")
    if not role_seq and isinstance(data.get("chapters"), list) and len(data["chapters"]) == nc:
        role_seq = [str(ch["emotional_role"]) for ch in data["chapters"] if isinstance(ch, dict) and "emotional_role" in ch]
        if len(role_seq) != nc:
            role_seq = None
    if not role_seq or len(role_seq) != nc:
        raise ValueError("Auto-generated arc missing emotional_role_sequence")
    opening_override = bool(data.get("opening_override", False))
    chapter_weights = None
    if isinstance(data.get("chapter_weights"), list) and len(data["chapter_weights"]) == nc:
        try:
            chapter_weights = [float(w) for w in data["chapter_weights"]]
        except (TypeError, ValueError):
            chapter_weights = None

    chapter_thesis = None
    raw_thesis = data.get("chapter_thesis")
    if isinstance(raw_thesis, dict) and raw_thesis:
        chapter_thesis = {int(k): str(v).strip() for k, v in raw_thesis.items() if str(v).strip()}

    return ArcBlueprint(
        arc_id=str(data["arc_id"]),
        persona=str(data["persona"]),
        topic=str(data["topic"]),
        engine=str(data["engine"]),
        format=str(data["format"]),
        chapter_count=nc,
        emotional_curve=list(data["emotional_curve"]),
        emotional_temperature_curve=temp_curve,
        chapter_intent=chapter_intent,
        reflection_strategy_sequence=list(data["reflection_strategy_sequence"]),
        cost_chapter_index=int(data["cost_chapter_index"]),
        resolution_type=str(data["resolution_type"]),
        motif=motif,
        raw=data,
        emotional_role_sequence=list(role_seq),
        opening_override=opening_override,
        chapter_weights=chapter_weights,
        chapter_thesis=chapter_thesis,
    )
