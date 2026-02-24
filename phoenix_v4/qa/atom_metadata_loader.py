"""
Load atom metadata for narrative gates. Dev Spec §2.7.
Returns dict[atom_id, metadata] with mechanism_depth, cost_type, cost_intensity,
identity_stage, callback_id, callback_phase, band, etc.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from phoenix_v4.planning.assembly_compiler import (
    ATOMS_ROOT,
    NARRATIVE_DEFAULTS,
    _load_story_atoms_for_persona_topic,
)
from phoenix_v4.planning.pool_index import REPO_ROOT

CONFIG_ROOT = REPO_ROOT / "config"


def _load_bindings(bindings_path: Path | None) -> dict:
    try:
        import yaml
    except ImportError:
        return {}
    p = bindings_path or CONFIG_ROOT / "topic_engine_bindings.yaml"
    if not p.exists():
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def _bindings_topic_key(topic_slug: str) -> str:
    if topic_slug == "grief_topic":
        return "grief"
    return topic_slug


def load_atom_metadata(
    atoms_root: Path | None = None,
    persona: str | None = None,
    topic: str | None = None,
    bindings_path: Path | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Load metadata for all STORY atoms for (persona, topic).
    Returns {atom_id: {mechanism_depth, cost_type, cost_intensity, identity_stage,
    callback_id, callback_phase, band, ...}}.
    Defaults from NARRATIVE_DEFAULTS when fields are missing.
    """
    atoms_root = atoms_root or ATOMS_ROOT
    if not persona or not topic:
        return {}
    bindings = _load_bindings(bindings_path)
    bkey = _bindings_topic_key(topic)
    raw_list = _load_story_atoms_for_persona_topic(atoms_root, persona, topic, bindings)
    out: dict[str, dict[str, Any]] = {}
    for a in raw_list:
        atom_id = a.get("atom_id")
        if not atom_id:
            continue
        meta: dict[str, Any] = {
            "band": a.get("band", 3),
            "mechanism_depth": a.get("mechanism_depth", NARRATIVE_DEFAULTS["mechanism_depth"]),
            "cost_type": a.get("cost_type", NARRATIVE_DEFAULTS["cost_type"]),
            "cost_intensity": a.get("cost_intensity", NARRATIVE_DEFAULTS["cost_intensity"]),
            "identity_stage": a.get("identity_stage", NARRATIVE_DEFAULTS["identity_stage"]),
            "callback_id": a.get("callback_id"),
            "callback_phase": a.get("callback_phase"),
        }
        if a.get("semantic_family"):
            meta["semantic_family"] = str(a["semantic_family"])
        out[atom_id] = meta
    return out


def load_atom_metadata_for_plan(
    plan: dict | Any,
    atoms_root: Path | None = None,
    bindings_path: Path | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Load atom metadata for the persona/topic of a compiled plan.
    plan may be dict with persona_id/topic_id at top level, or have .persona_id/.topic_id.
    If missing, derive from first real atom_id (persona_topic_engine_role_vNN).
    """
    plan_d = plan if isinstance(plan, dict) else {}
    if hasattr(plan, "persona_id"):
        persona = getattr(plan, "persona_id", None) or ""
        topic = getattr(plan, "topic_id", None) or ""
    else:
        persona = plan_d.get("persona_id") or plan_d.get("persona") or ""
        topic = plan_d.get("topic_id") or plan_d.get("topic") or ""
    if not persona or not topic:
        atom_ids = plan_d.get("atom_ids") if plan_d else (getattr(plan, "atom_ids", None) or [])
        real = [a for a in atom_ids if "placeholder:" not in a and "silence:" not in a]
        if real:
            parts = real[0].split("_")
            if len(parts) >= 2:
                persona = persona or parts[0]
                topic = topic or parts[1]
    return load_atom_metadata(
        atoms_root=atoms_root,
        persona=persona,
        topic=topic,
        bindings_path=bindings_path,
    )
