"""
Stage 3 Assembly Compiler.
Consumes BookSpec + FormatPlan; reads atoms from atoms/<persona>/<topic>/<engine>/CANONICAL.txt;
outputs CompiledBook (plan_hash, chapter_slot_sequence, atom_ids, dominant_band_sequence).
Contract: Canonical Spec §3.0, OMEGA_LAYER_CONTRACTS.md.
Stage 3 MUST NOT infer persona/topic mappings or slot types. Caller must pass canonical IDs and format_plan.slot_definitions.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"
CONFIG_ROOT = REPO_ROOT / "config"
TEACHER_BANKS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"

# Frozen story roles (Canonical §5.3). Parser accepts only these.
FROZEN_STORY_ROLES = frozenset({"RECOGNITION", "MECHANISM_PROOF", "TURNING_POINT", "EMBODIMENT"})
LEGACY_VER_TO_ROLE = {
    1: "RECOGNITION",
    2: "MECHANISM_PROOF",
    3: "TURNING_POINT",
    4: "EMBODIMENT",
}
LEGACY_STAGE_TO_ROLE = {
    "pre_awareness": "RECOGNITION",
    "destabilization": "MECHANISM_PROOF",
    "experimentation": "TURNING_POINT",
    "self_claim": "EMBODIMENT",
}


def _compute_exercise_chapters(chapter_slot_sequence: list[list[str]]) -> list[int]:
    """Chapter indices (0-based) that contain an EXERCISE slot. Deterministic; no fallback."""
    return [
        i for i, ch in enumerate(chapter_slot_sequence)
        if any(str(s).upper() == "EXERCISE" for s in ch)
    ]


def _compute_slot_signature(format_id: str, chapter_slot_sequence: list[list[str]]) -> str:
    """Stable hash of slot layout for similarity/density CI. Deterministic."""
    payload = json.dumps(chapter_slot_sequence, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{format_id}:{h}"


@dataclass
class CompiledBook:
    """Stage 3 output. Contract: plan_hash, chapter_slot_sequence, atom_ids, dominant_band_sequence.
    dominant_band_sequence: one entry per chapter = max(bands of STORY atoms in that chapter), or None if no STORY slots.
    Arc-First: when arc supplied, arc_id, emotional_temperature_sequence, reflection_strategy_sequence from arc.
    Structural fingerprint (CI): exercise_chapters, slot_sig from derived fields.
    Freebie fields: set after Stage 3 by freebie_planner (specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md).
    Author positioning (Writer Spec §24): author_positioning_profile, positioning_signature_hash."""
    plan_hash: str
    chapter_slot_sequence: list[list[str]]
    atom_ids: list[str]
    dominant_band_sequence: Optional[list[Optional[int]]] = None
    arc_id: Optional[str] = None
    emotional_temperature_sequence: Optional[list[str]] = None
    reflection_strategy_sequence: Optional[list[str]] = None
    exercise_chapters: Optional[list[int]] = None
    slot_sig: Optional[str] = None
    freebie_bundle: Optional[list[str]] = None
    cta_template_id: Optional[str] = None
    freebie_slug: Optional[str] = None
    author_positioning_profile: Optional[str] = None
    positioning_signature_hash: Optional[str] = None
    # Compression slot (DEV SPEC 2): one atom per chapter when format has COMPRESSION
    compression_atom_ids: Optional[list[str]] = None  # length == chapter_count; "" where no slot
    compression_sig: Optional[str] = None
    compression_pos_sig: Optional[str] = None  # e.g. "0,1,2" for chapters with compression
    compression_len_vec: Optional[list[str]] = None   # S/M/L per chapter; "" where none
    # DEV SPEC 3: Emotional Role Taxonomy
    emotional_role_sequence: Optional[list[str]] = None  # length == chapter_count
    emotional_role_sig: Optional[str] = None  # compact e.g. r-d-f-s-i
    # Teacher Mode: atom_source per slot (teacher_native | teacher_synthetic | practice_fallback); same length as atom_ids
    atom_sources: Optional[list[Optional[str]]] = None
    # Optional slots / silence: slots allowed to be empty under budget
    silence_budget_used: Optional[int] = None
    # Asymmetry: optional weight/density per chapter (from arc)
    chapter_weights: Optional[list[float]] = None  # length == chapter_count
    # Structural Variation V4: motif/reframe injection points for downstream renderer
    motif_injections: Optional[list[dict[str, Any]]] = None  # [{chapter_index, slot_index, phrase}]
    reframe_injections: Optional[list[dict[str, Any]]] = None  # [{chapter_index, slot_index, line_type, text}]
    # Chapter planner outputs (anti-template cadence controls)
    chapter_archetypes: Optional[list[str]] = None
    chapter_exercise_modes: Optional[list[str]] = None
    chapter_reflection_weights: Optional[list[str]] = None
    chapter_story_depths: Optional[list[str]] = None
    chapter_planner_warnings: Optional[list[str]] = None
    # Bestseller structure assignment (max 3 in a row); one of 12 narrative shapes per chapter
    chapter_bestseller_structures: Optional[list[str]] = None  # length == chapter_count
    # Intro/ending variation (Controlled Intro/Conclusion): final chapter INTEGRATION + carry line
    ending_signature: Optional[str] = None  # SHA256(final INTEGRATION atom_id + carry_line)[:16]
    carry_line: Optional[str] = None  # chosen carry line for final chapter (for TTS)
    # Chapter thesis from arc (keys 1..chapter_count); used to resolve TAKEAWAY slots (atom_id arc_thesis:chN)
    chapter_thesis: Optional[dict[int, str]] = None


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def validate_canonical_atom_file(path: Path) -> list[str]:
    """Validate CANONICAL.txt schema. Returns list of errors; empty if valid. Canonical §5.3."""
    errors: list[str] = []
    if not path.exists():
        return [f"File not found: {path}"]
    text = path.read_text()
    block = re.compile(
        r"^##\s+([A-Z_]+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---",
        re.MULTILINE,
    )
    for m in block.finditer(text):
        role, ver, meta = m.group(1), m.group(2), m.group(3)
        mapped_role = _resolve_story_role(role, ver, meta)
        if mapped_role is None:
            errors.append(f"Unknown role: {role} (frozen set: {sorted(FROZEN_STORY_ROLES)})")
        if not ver.isdigit():
            errors.append(f"Malformed version: {ver}")
        if "path:" not in meta:
            errors.append(f"Block {mapped_role or role} v{ver}: missing path line in metadata")
    return errors


def _parse_band_from_metadata(metadata: str, path: Path, role: str, ver: str) -> int:
    """Parse optional BAND: N from metadata. Default 3 only when key missing; malformed fails fast. Canonical §5.3."""
    band_line = re.search(r"^BAND:\s*(.+)$", metadata, re.MULTILINE)
    if band_line is None:
        return 3
    raw = band_line.group(1).strip()
    try:
        band = int(raw)
    except ValueError:
        raise ValueError(f"Invalid CANONICAL.txt {path}: block {role} v{ver} BAND must be integer, got {raw!r}")
    if not 1 <= band <= 5:
        raise ValueError(f"Invalid CANONICAL.txt {path}: block {role} v{ver} BAND must be 1-5, got {band}")
    return band


# Narrative Intelligence (V4 Dev Spec): optional metadata with safe defaults for existing atoms.
NARRATIVE_DEFAULTS = {
    "mechanism_depth": 1,
    "cost_type": "social",
    "cost_intensity": 2,
    "identity_stage": "pre_awareness",
    "callback_id": None,
    "callback_phase": None,
}
VALID_COST_TYPES = frozenset({"social", "internal", "opportunity", "identity"})
VALID_IDENTITY_STAGES = frozenset({"pre_awareness", "destabilization", "experimentation", "self_claim"})
VALID_CALLBACK_PHASES = frozenset({"setup", "escalation", "return"})


def _parse_narrative_metadata(metadata: str, path: Path, role: str, ver: str) -> dict[str, Any]:
    """Parse optional narrative fields from CANONICAL block. Returns dict with defaults for missing/invalid. Dev Spec §2.1."""
    out: dict[str, Any] = dict(NARRATIVE_DEFAULTS)
    lines = [ln.strip() for ln in metadata.splitlines()]
    for line in lines:
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip().upper(), val.strip()
        if key == "MECHANISM_DEPTH":
            try:
                v = int(val)
                if 1 <= v <= 4:
                    out["mechanism_depth"] = v
            except ValueError:
                pass
        elif key == "COST_TYPE" and val.lower() in VALID_COST_TYPES:
            out["cost_type"] = val.lower()
        elif key == "COST_INTENSITY":
            try:
                v = int(val)
                if 1 <= v <= 5:
                    out["cost_intensity"] = v
            except ValueError:
                pass
        elif key == "IDENTITY_STAGE" and val.lower() in VALID_IDENTITY_STAGES:
            out["identity_stage"] = val.lower()
        elif key == "CALLBACK_ID":
            out["callback_id"] = val if val else None
        elif key == "CALLBACK_PHASE" and val.lower() in VALID_CALLBACK_PHASES:
            out["callback_phase"] = val.lower()
    return out


def _resolve_story_role(raw_role: str, ver: str, metadata: str) -> Optional[str]:
    """
    Resolve role from canonical/legacy headers.
    Canonical: role is explicit (RECOGNITION/MECHANISM_PROOF/TURNING_POINT/EMBODIMENT).
    Legacy compatibility: character-name headers (e.g. DAVID v01) map by IDENTITY_STAGE,
    then by version index (v01..v04).
    """
    role = (raw_role or "").strip().upper()
    if role in FROZEN_STORY_ROLES:
        return role

    id_stage = None
    for line in metadata.splitlines():
        if line.strip().upper().startswith("IDENTITY_STAGE:"):
            id_stage = line.split(":", 1)[1].strip().lower()
            break
    if id_stage in LEGACY_STAGE_TO_ROLE:
        return LEGACY_STAGE_TO_ROLE[id_stage]

    try:
        vnum = int(ver)
    except ValueError:
        return None
    return LEGACY_VER_TO_ROLE.get(vnum)


def _parse_canonical_txt(path: Path) -> list[dict[str, Any]]:
    """Parse CANONICAL.txt into list of {role, atom_id, path_line, band}. Canonical §5.3. BAND default 3 only when key missing."""
    if not path.exists():
        return []
    errs = validate_canonical_atom_file(path)
    if errs:
        raise ValueError(f"Invalid CANONICAL.txt {path}: " + "; ".join(errs))
    text = path.read_text()
    atoms: list[dict[str, Any]] = []
    block = re.compile(
        r"^##\s+([A-Z_]+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---",
        re.MULTILINE,
    )
    persona_dir = path.parent.parent.parent.name
    topic_dir = path.parent.parent.name
    engine = path.parent.name
    for m in block.finditer(text):
        raw_role, ver, metadata = m.group(1), m.group(2), m.group(3)
        role = _resolve_story_role(raw_role, ver, metadata)
        if role is None:
            raise ValueError(f"Invalid CANONICAL.txt {path}: unknown role {raw_role!r} in v{ver}")
        path_line = ""
        semantic_family = None
        for line in metadata.splitlines():
            if line.strip().startswith("path:"):
                path_line = line.split("path:", 1)[1].strip()
            elif line.strip().upper().startswith("SEMANTIC_FAMILY:"):
                semantic_family = line.split(":", 1)[1].strip()
        band = _parse_band_from_metadata(metadata, path, role, ver)
        if raw_role == role:
            atom_id = f"{persona_dir}_{topic_dir}_{engine}_{role}_v{ver}"
        else:
            raw_slug = re.sub(r"[^A-Za-z0-9]+", "_", raw_role).strip("_").upper() or "LEGACY"
            atom_id = f"{persona_dir}_{topic_dir}_{engine}_{role}_{raw_slug}_v{ver}"
        a = {"role": role, "atom_id": atom_id, "path_line": path_line, "band": band}
        if semantic_family:
            a["semantic_family"] = semantic_family
        narrative = _parse_narrative_metadata(metadata, path, role, ver)
        a.update(narrative)
        atoms.append(a)
    return atoms


def _bindings_topic_key(topic_slug: str) -> str:
    """Atoms dir name -> topic_engine_bindings key."""
    if topic_slug == "grief_topic":
        return "grief"
    return topic_slug


def _load_story_atoms_for_persona_topic(
    atoms_root: Path,
    persona_slug: str,
    topic_slug: str,
    bindings: dict,
) -> list[dict[str, Any]]:
    """Load all STORY atoms for (persona, topic) across allowed engines. persona_slug/topic_slug must be canonical."""
    bkey = _bindings_topic_key(topic_slug)
    allowed = (bindings.get(bkey) or {}).get("allowed_engines") or []
    if not allowed:
        allowed = ["false_alarm", "overwhelm", "shame", "spiral", "watcher", "grief", "comparison"]
    out: list[dict[str, Any]] = []
    for engine in allowed:
        path = atoms_root / persona_slug / topic_slug / engine / "CANONICAL.txt"
        try:
            for a in _parse_canonical_txt(path):
                a["engine"] = engine
                out.append(a)
        except ValueError:
            continue
    return out


def _compute_motif_reframe_injections(
    chapter_slot_sequence: list[list[str]],
    motif_id: Optional[str],
    reframe_profile_id: Optional[str],
    selector_key_prefix: str,
    config_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Structural Variation V4: compute motif and reframe injection points.
    Motif: max 2 per chapter, max 12 per book, min slot distance ~2 (proxy for 250 words).
    Reframe: reflection/integration slots only; one line type per slot.
    """
    motif_injections: list[dict[str, Any]] = []
    reframe_injections: list[dict[str, Any]] = []
    config_sot = config_root / "source_of_truth"
    if motif_id:
        motif_cfg = _load_yaml(config_sot / "recurring_motif_bank.yaml")
        motifs = (motif_cfg.get("motifs") or {}).get(motif_id)
        if motifs:
            variants = motifs.get("variants") or []
            max_per_chapter = int(motifs.get("max_per_chapter") or 2)
            max_per_book = int(motifs.get("max_per_book") or 12)
            slot_distance_min = 2
            last_slot_idx = -99
            book_count = 0
            for ch, ch_slots in enumerate(chapter_slot_sequence):
                ch_count = 0
                for si, st in enumerate(ch_slots):
                    if st not in ("REFLECTION", "INTEGRATION", "STORY"):
                        continue
                    if book_count >= max_per_book or ch_count >= max_per_chapter:
                        break
                    global_slot = sum(len(c) for c in chapter_slot_sequence[:ch]) + si
                    if global_slot - last_slot_idx < slot_distance_min and last_slot_idx >= 0:
                        continue
                    idx = (hashlib.sha256(f"{selector_key_prefix}:motif:ch{ch}:s{si}".encode()).digest()[0]) % max(1, len(variants))
                    phrase = variants[idx] if variants else ""
                    motif_injections.append({"chapter_index": ch, "slot_index": si, "phrase": phrase})
                    last_slot_idx = global_slot
                    ch_count += 1
                    book_count += 1
    if reframe_profile_id:
        reframe_cfg = _load_yaml(config_sot / "reframe_line_bank.yaml")
        profiles = reframe_cfg.get("profiles") or {}
        profile = profiles.get(reframe_profile_id) or profiles.get("balanced", {})
        line_types = ["constraint_lines", "worldview_lines", "micro_reframe_lines"]
        for ch, ch_slots in enumerate(chapter_slot_sequence):
            for si, st in enumerate(ch_slots):
                if st not in ("REFLECTION", "INTEGRATION"):
                    continue
                lt = line_types[ch % len(line_types)]
                lines = profile.get(lt) or []
                if not lines:
                    continue
                idx = (hashlib.sha256(f"{selector_key_prefix}:reframe:{lt}:ch{ch}:s{si}".encode()).digest()[0]) % len(lines)
                text = lines[idx]
                reframe_injections.append({
                    "chapter_index": ch, "slot_index": si, "line_type": lt.replace("_lines", ""), "text": text,
                })
                break
    return motif_injections, reframe_injections


def _apply_section_reorder(
    slot_definitions: list[list[str]],
    section_reorder_mode: str,
    config_root: Optional[Path] = None,
) -> list[list[str]]:
    """
    Structural Variation V4: apply role-safe reorder per chapter.
    Only allowed_swaps from section_reorder_modes.yaml; never move STORY/EXERCISE.
    """
    if not section_reorder_mode or section_reorder_mode == "none":
        return slot_definitions
    config_root = config_root or CONFIG_ROOT
    reorder_cfg = _load_yaml(config_root / "source_of_truth" / "section_reorder_modes.yaml")
    modes = reorder_cfg.get("modes") or {}
    mode_cfg = modes.get(section_reorder_mode)
    if not mode_cfg:
        return slot_definitions
    allowed = mode_cfg.get("allowed_swaps") or []
    blocked = frozenset(
        tuple(sorted(pair)) for pair in (mode_cfg.get("blocked_swaps") or [])
    )
    result = []
    for ch_slots in slot_definitions:
        row = list(ch_slots)
        for pair in allowed:
            if len(pair) != 2:
                continue
            a, b = pair[0], pair[1]
            for i in range(len(row) - 1):
                if (row[i], row[i + 1]) == (a, b):
                    row[i], row[i + 1] = b, a
                    break
                if (row[i], row[i + 1]) == (b, a) and (a, b) not in blocked:
                    row[i], row[i + 1] = a, b
                    break
        result.append(row)
    return result


def _deterministic_select(
    atoms: list[dict],
    slot_type: str,
    chapter_index: int,
    slot_index: int,
    seed: str,
    used_ids: set[str],
    count: int = 1,
) -> list[str]:
    """Select up to count atom IDs deterministically; exclude used_ids."""
    if slot_type != "STORY":
        return []
    available = [a for a in atoms if a["atom_id"] not in used_ids]
    if not available:
        return []
    available.sort(key=lambda x: x["atom_id"])
    h = hashlib.sha256(f"{seed}:ch{chapter_index}:slot{slot_index}".encode()).digest()
    start = int.from_bytes(h[:4], "big") % max(1, len(available))
    selected: list[str] = []
    for i in range(count):
        idx = (start + i) % len(available)
        aid = available[idx]["atom_id"]
        selected.append(aid)
        used_ids.add(aid)
    return selected


def compile_plan(
    book_spec: dict[str, Any],
    format_plan: dict[str, Any],
    arc_path: Optional[Path] = None,
    arc: Optional[Any] = None,
    atoms_root: Optional[Path] = None,
    bindings_path: Optional[Path] = None,
    validate_atom_schema: bool = True,
    require_full_resolution: bool = False,
    atoms_model: Optional[str] = None,
) -> CompiledBook:
    """
    Stage 3: BookSpec + FormatPlan + Arc -> CompiledBook (Arc-First: arc required).
    book_spec must contain canonical topic_id and persona_id. format_plan must contain slot_definitions.
    arc_path or arc (loaded ArcBlueprint or dict) is required; no arc = no compile.
    Same (book_spec, format_plan, arc) -> same plan_hash and atom_ids.
    atoms_model: optional "legacy" | "cluster". When "cluster", a future implementation will switch to
    core+overlay resolution and require atoms_root to contain core/ and overlay/. Currently no resolution change.
    """
    atoms_root = atoms_root or ATOMS_ROOT
    bindings_path = bindings_path or (CONFIG_ROOT / "topic_engine_bindings.yaml")
    bindings = _load_yaml(bindings_path)

    # Arc-First: require arc
    if arc is None and arc_path is None:
        raise ValueError("Arc required: provide arc_path or arc. No arc = no compile.")
    if arc is None and arc_path is not None:
        from phoenix_v4.planning.arc_loader import load_arc
        arc = load_arc(arc_path, arcs_root=None)
    arc_raw = arc.raw if hasattr(arc, "raw") else arc
    arc_id = str(arc_raw.get("arc_id", "")) if isinstance(arc_raw, dict) else getattr(arc, "arc_id", "")
    emotional_curve = arc_raw.get("emotional_curve") if isinstance(arc_raw, dict) else getattr(arc, "emotional_curve", [])
    emotional_temperature_curve = arc_raw.get("emotional_temperature_curve") if isinstance(arc_raw, dict) else getattr(arc, "emotional_temperature_curve", {})
    reflection_strategy_sequence = arc_raw.get("reflection_strategy_sequence") if isinstance(arc_raw, dict) else getattr(arc, "reflection_strategy_sequence", [])
    emotional_role_sequence = arc_raw.get("emotional_role_sequence") if isinstance(arc_raw, dict) else getattr(arc, "emotional_role_sequence", None)
    if emotional_role_sequence is None and hasattr(arc, "raw"):
        emotional_role_sequence = getattr(arc, "emotional_role_sequence", None) or (arc.raw.get("emotional_role_sequence") if isinstance(arc.raw, dict) else None)
    chapter_weights_from_arc = getattr(arc, "chapter_weights", None) if hasattr(arc, "chapter_weights") else (arc_raw.get("chapter_weights") if isinstance(arc_raw, dict) else None)
    chapter_thesis_from_arc: Optional[dict[int, str]] = getattr(arc, "chapter_thesis", None) if hasattr(arc, "chapter_thesis") else (arc_raw.get("chapter_thesis") if isinstance(arc_raw, dict) else None)
    if chapter_thesis_from_arc and isinstance(chapter_thesis_from_arc, dict):
        chapter_thesis_from_arc = {int(k): str(v).strip() for k, v in chapter_thesis_from_arc.items() if str(v).strip()}
    else:
        chapter_thesis_from_arc = None
    if isinstance(emotional_temperature_curve, dict):
        emotional_temperature_sequence = [emotional_temperature_curve.get(i + 1) or "warm" for i in range(len(emotional_curve))]
    else:
        emotional_temperature_sequence = []

    topic_id = book_spec.get("topic_id") or book_spec.get("topic")
    persona_id = book_spec.get("persona_id") or book_spec.get("persona")
    if not topic_id or not persona_id:
        raise ValueError("Stage 3 requires book_spec.topic_id and book_spec.persona_id (canonical atoms dir names)")

    slot_definitions = format_plan.get("slot_definitions")
    if not slot_definitions or not isinstance(slot_definitions, list):
        raise ValueError("Stage 3 requires format_plan.slot_definitions (List[List[string]]). No inference allowed.")
    chapter_count = int(format_plan.get("chapter_count") or format_plan.get("target_chapter_count", 12))
    if len(slot_definitions) != chapter_count:
        if len(slot_definitions) == 1 and isinstance(slot_definitions[0], list):
            template = list(slot_definitions[0])
            slot_definitions = [template[:] for _ in range(chapter_count)]
        else:
            raise ValueError(f"format_plan.slot_definitions length ({len(slot_definitions)}) must match chapter_count ({chapter_count}) or be [template]")

    # Structural Variation V4: role-safe section reorder (optional)
    section_reorder_mode = format_plan.get("section_reorder_mode") or "none"
    if section_reorder_mode and section_reorder_mode != "none":
        slot_definitions = _apply_section_reorder(slot_definitions, section_reorder_mode, CONFIG_ROOT)

    if len(emotional_curve) != chapter_count:
        raise ValueError(f"Arc emotional_curve length ({len(emotional_curve)}) must match chapter_count ({chapter_count})")

    # Stable selector key prefix including arc (determinism)
    selector_key_prefix = hashlib.sha256(
        json.dumps({"book_spec": book_spec, "format_plan": format_plan, "arc": arc_raw}, sort_keys=True).encode()
    ).hexdigest()[:24]

    # Chapter planner: archetype/weight planning (non-uniform slot application).
    chapter_archetypes_out: Optional[list[str]] = None
    chapter_exercise_modes_out: Optional[list[str]] = None
    chapter_reflection_weights_out: Optional[list[str]] = None
    chapter_story_depths_out: Optional[list[str]] = None
    chapter_planner_warnings_out: Optional[list[str]] = None
    chapter_bestseller_structures_out: Optional[list[str]] = None
    try:
        from phoenix_v4.planning.chapter_planner import plan_chapters
        chapter_plan = plan_chapters(
            slot_definitions=slot_definitions,
            chapter_count=chapter_count,
            selector_key_prefix=selector_key_prefix,
            emotional_role_sequence=emotional_role_sequence if isinstance(emotional_role_sequence, list) else None,
            book_size=(format_plan.get("book_size") or book_spec.get("book_size")),
            enforce_role_distribution=bool(format_plan.get("enforce_arc_role_distribution") or False),
        )
        slot_definitions = chapter_plan.slot_definitions
        chapter_archetypes_out = chapter_plan.chapter_archetypes
        chapter_exercise_modes_out = chapter_plan.chapter_exercise_modes
        chapter_reflection_weights_out = chapter_plan.chapter_reflection_weights
        chapter_story_depths_out = chapter_plan.chapter_story_depths
        chapter_planner_warnings_out = chapter_plan.warnings
        chapter_bestseller_structures_out = chapter_plan.chapter_bestseller_structures
    except Exception as e:
        # Do not hard-fail legacy flows on chapter-planner issues; preserve existing Stage 3 behavior.
        chapter_planner_warnings_out = [f"chapter planner fallback: {e}"]

    required_band_by_chapter = {i: emotional_curve[i] for i in range(chapter_count)} if emotional_curve else None

    from phoenix_v4.planning.pool_index import PoolIndex
    from phoenix_v4.planning.slot_resolver import ResolverContext, resolve_slot

    teacher_mode = book_spec.get("teacher_mode") is True
    teacher_id = (book_spec.get("teacher_id") or "").strip()
    teacher_atoms_root: Optional[Path] = None
    teacher_exercise_fallback = False
    required_slots_by_type: Optional[dict[str, int]] = None
    if teacher_mode and teacher_id and TEACHER_BANKS_ROOT.exists():
        teacher_root = TEACHER_BANKS_ROOT / teacher_id / "approved_atoms"
        if teacher_root.exists():
            teacher_atoms_root = teacher_root
        from phoenix_v4.teacher.teacher_config import load_teacher_config
        tcfg = load_teacher_config(teacher_id)
        teacher_exercise_fallback = bool(tcfg.get("teacher_exercise_fallback"))
        required_slots_by_type = {}
        for row in slot_definitions:
            for st in row:
                slot_type = str(st).strip().upper()
                if slot_type:
                    required_slots_by_type[slot_type] = required_slots_by_type.get(slot_type, 0) + 1

    pool_index = PoolIndex(
        atoms_root=atoms_root,
        bindings_path=bindings_path,
        teacher_atoms_root=teacher_atoms_root,
    )
    story_pool = pool_index.get_pool("STORY", persona_id, topic_id, format_plan)
    band_by_id: dict[str, int] = {
        e.atom_id: (e.metadata or {}).get("band", 3) for e in story_pool
    }
    used: set[str] = set()
    optional_slot_types = frozenset(
        (format_plan.get("optional_slot_types") or book_spec.get("optional_slot_types") or [])
    )
    silence_budget = int(format_plan.get("silence_budget") or book_spec.get("silence_budget") or 0)
    used_semantic_families: set[str] = set()
    # Angle Integration (V4.7): chapter 1 framing bias; intro/ending variation: opening_style_id soft bias
    angle_context = None
    _angle_id = book_spec.get("angle_id") if isinstance(book_spec, dict) else getattr(book_spec, "angle_id", None)
    if _angle_id:
        from phoenix_v4.planning.angle_resolver import get_angle_context
        angle_context = get_angle_context(_angle_id)
    _opening_style_id = book_spec.get("opening_style_id") if isinstance(book_spec, dict) else getattr(book_spec, "opening_style_id", None)
    if _opening_style_id:
        angle_context = dict(angle_context) if angle_context else {}
        angle_context["opening_style_id"] = _opening_style_id
    # Intro/ending variation: final chapter INTEGRATION ranking and carry line
    ending_context = None
    _integration_ending_style_id = book_spec.get("integration_ending_style_id") if isinstance(book_spec, dict) else getattr(book_spec, "integration_ending_style_id", None)
    if _integration_ending_style_id is not None:
        ending_context = {
            "final_chapter_index": chapter_count - 1,
            "integration_ending_style_id": _integration_ending_style_id,
        }
    context = ResolverContext(
        persona_id=persona_id,
        topic_id=topic_id,
        slot_definitions=slot_definitions,
        used_atom_ids=used,
        pool_index=pool_index,
        selector_key_prefix=selector_key_prefix,
        required_band_by_chapter=required_band_by_chapter,
        used_semantic_families=used_semantic_families,
        angle_context=angle_context,
        ending_context=ending_context,
        teacher_mode=teacher_mode,
        required_slots_by_type=required_slots_by_type,
        teacher_exercise_fallback=teacher_exercise_fallback,
    )

    chapter_slot_sequence: list[list[str]] = []
    atom_ids: list[str] = []
    atom_sources_out: Optional[list[Optional[str]]] = [] if teacher_mode else None
    dominant_band_sequence: list[Optional[int]] = []
    placeholder_slot_types: set[str] = set()
    compression_atom_ids: list[str] = [""] * chapter_count
    compression_word_counts: list[int] = [0] * chapter_count
    silence_budget_used = 0

    for ch in range(chapter_count):
        ch_slots = list(slot_definitions[ch]) if ch < len(slot_definitions) else []
        chapter_story_bands: list[int] = []
        for si, slot_type in enumerate(ch_slots):
            # TAKEAWAY: resolve from arc chapter_thesis when present; no pool lookup
            if str(slot_type).strip().upper() == "TAKEAWAY" and chapter_thesis_from_arc:
                thesis_text = chapter_thesis_from_arc.get(ch + 1)
                if thesis_text:
                    atom_ids.append(f"arc_thesis:ch{ch}")
                    if atom_sources_out is not None:
                        atom_sources_out.append(None)
                    continue
            result = resolve_slot(slot_type, ch, si, context)
            if result is not None:
                aid, atom_source = result
                atom_ids.append(aid)
                if atom_sources_out is not None:
                    atom_sources_out.append(atom_source)
                used.add(aid)
                if slot_type == "STORY":
                    chapter_story_bands.append(band_by_id.get(aid, 3))
                if slot_type == "COMPRESSION":
                    compression_atom_ids[ch] = aid
                    comp_pool = pool_index.get_pool("COMPRESSION", persona_id, topic_id, None)
                    comp_entry = next((e for e in comp_pool if e.atom_id == aid), None)
                    compression_word_counts[ch] = (comp_entry.metadata or {}).get("word_count", 0) if comp_entry else 0
            else:
                # Optional/silence: allow empty slot if type is optional and within silence budget
                if (
                    slot_type in optional_slot_types
                    and silence_budget_used < silence_budget
                ):
                    atom_ids.append(f"silence:{slot_type}:ch{ch}:slot{si}")
                    if atom_sources_out is not None:
                        atom_sources_out.append(None)
                    silence_budget_used += 1
                elif arc is not None and slot_type == "STORY":
                    raise ValueError(
                        f"Arc required BAND {required_band_by_chapter.get(ch)} for chapter {ch + 1} but no STORY atom available. "
                        "Add atoms for this BAND or adjust arc emotional_curve."
                    )
                else:
                    atom_ids.append(f"placeholder:{slot_type}:ch{ch}:slot{si}")
                    if atom_sources_out is not None:
                        atom_sources_out.append(None)
                    placeholder_slot_types.add(slot_type)
        chapter_slot_sequence.append(ch_slots)
        dominant_band_sequence.append(max(chapter_story_bands) if chapter_story_bands else None)

    # Intro/ending variation: compute ending_signature from final INTEGRATION atom + carry line
    ending_signature_out: Optional[str] = None
    carry_line_out: Optional[str] = None
    _carry_line_style_id = book_spec.get("carry_line_style_id") if isinstance(book_spec, dict) else getattr(book_spec, "carry_line_style_id", None)
    if _carry_line_style_id and chapter_count > 0:
        final_ch = chapter_count - 1
        final_slots = slot_definitions[final_ch] if final_ch < len(slot_definitions) else []
        final_int_si = next((i for i, st in enumerate(final_slots) if str(st).strip().upper() == "INTEGRATION"), None)
        if final_int_si is not None:
            global_idx = sum(len(slot_definitions[i]) for i in range(final_ch)) + final_int_si
            if global_idx < len(atom_ids):
                final_integration_atom_id = atom_ids[global_idx]
                from phoenix_v4.planning.intro_ending_selector import select_carry_line
                _seed = book_spec.get("seed", "default_seed") if isinstance(book_spec, dict) else getattr(book_spec, "seed", "default_seed")
                carry_line_out = select_carry_line(
                    _carry_line_style_id, topic_id, persona_id, _seed, config_root=CONFIG_ROOT / "source_of_truth",
                )
                payload = f"{final_integration_atom_id}\n{carry_line_out}"
                ending_signature_out = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    if require_full_resolution and placeholder_slot_types:
        raise ValueError(
            "require_full_resolution=True but plan has placeholders. Missing pools for slot types: "
            + ", ".join(sorted(placeholder_slot_types))
        )

    digest_input = {
        "book_spec_digest": hashlib.sha256(json.dumps(book_spec, sort_keys=True).encode()).hexdigest()[:24],
        "format_plan_digest": hashlib.sha256(json.dumps(format_plan, sort_keys=True).encode()).hexdigest()[:24],
        "atom_ids": atom_ids,
    }
    plan_hash = hashlib.sha256(json.dumps(digest_input, sort_keys=True).encode()).hexdigest()[:32]

    format_id = str(format_plan.get("format_structural_id") or format_plan.get("format_id") or "")
    exercise_chapters = _compute_exercise_chapters(chapter_slot_sequence)
    slot_sig = _compute_slot_signature(format_id, chapter_slot_sequence)

    # Layer 2: Author positioning (Writer Spec §24). Signature = sha256(profile + plan_hash) for determinism.
    author_positioning_profile = book_spec.get("author_positioning_profile")
    positioning_signature_hash = None
    if author_positioning_profile:
        payload = f"{author_positioning_profile}:{plan_hash}"
        positioning_signature_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]

    # Compression (DEV SPEC 2): pos_sig, len_vec (S/M/L bins), compression_sig
    def _compression_bin(w: int) -> str:
        if 40 <= w <= 59:
            return "S"
        if 60 <= w <= 99:
            return "M"
        if 100 <= w <= 120:
            return "L"
        return ""

    compression_pos_sig = ",".join(str(i) for i in range(chapter_count) if compression_atom_ids[i])
    compression_len_vec = [
        _compression_bin(compression_word_counts[i]) if compression_atom_ids[i] else ""
        for i in range(chapter_count)
    ]
    compression_sig = None
    if compression_pos_sig or any(compression_len_vec):
        compression_sig = hashlib.sha256(
            json.dumps({"pos": compression_pos_sig, "bins": compression_len_vec}, sort_keys=True).encode()
        ).hexdigest()[:16]

    # DEV SPEC 3: emotional_role_sequence from arc; compact sig (r,d,f,s,i)
    from phoenix_v4.planning.arc_loader import ROLE_SIG_MAP
    role_seq_out: Optional[list[str]] = None
    role_sig_out: Optional[str] = None
    if emotional_role_sequence and len(emotional_role_sequence) == chapter_count:
        role_seq_out = list(emotional_role_sequence)
        role_sig_out = "-".join(ROLE_SIG_MAP.get(r, r[0] if r else "") for r in role_seq_out)

    # Structural Variation V4: motif and reframe injection points (metadata for downstream)
    motif_injections_out: Optional[list[dict[str, Any]]] = None
    reframe_injections_out: Optional[list[dict[str, Any]]] = None
    if format_plan.get("motif_id") or format_plan.get("reframe_profile_id"):
        motif_injections_out, reframe_injections_out = _compute_motif_reframe_injections(
            chapter_slot_sequence=chapter_slot_sequence,
            motif_id=format_plan.get("motif_id"),
            reframe_profile_id=format_plan.get("reframe_profile_id"),
            selector_key_prefix=selector_key_prefix,
            config_root=CONFIG_ROOT,
        )

    return CompiledBook(
        plan_hash=plan_hash,
        chapter_slot_sequence=chapter_slot_sequence,
        atom_ids=atom_ids,
        dominant_band_sequence=dominant_band_sequence,
        arc_id=arc_id or None,
        emotional_temperature_sequence=emotional_temperature_sequence or None,
        reflection_strategy_sequence=list(reflection_strategy_sequence) if reflection_strategy_sequence else None,
        exercise_chapters=exercise_chapters,
        slot_sig=slot_sig,
        author_positioning_profile=author_positioning_profile or None,
        positioning_signature_hash=positioning_signature_hash,
        compression_atom_ids=compression_atom_ids if any(compression_atom_ids) else None,
        compression_sig=compression_sig,
        compression_pos_sig=compression_pos_sig if compression_pos_sig else None,
        compression_len_vec=compression_len_vec if any(compression_len_vec) else None,
        emotional_role_sequence=role_seq_out,
        emotional_role_sig=role_sig_out,
        atom_sources=atom_sources_out,
        silence_budget_used=silence_budget_used if silence_budget > 0 else None,
        chapter_weights=chapter_weights_from_arc if chapter_weights_from_arc and len(chapter_weights_from_arc) == chapter_count else None,
        motif_injections=motif_injections_out,
        reframe_injections=reframe_injections_out,
        chapter_archetypes=chapter_archetypes_out,
        chapter_exercise_modes=chapter_exercise_modes_out,
        chapter_reflection_weights=chapter_reflection_weights_out,
        chapter_story_depths=chapter_story_depths_out,
        chapter_planner_warnings=chapter_planner_warnings_out,
        chapter_bestseller_structures=chapter_bestseller_structures_out,
        ending_signature=ending_signature_out,
        carry_line=carry_line_out,
        chapter_thesis=chapter_thesis_from_arc,
    )
