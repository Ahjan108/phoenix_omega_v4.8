"""
Pool index: atoms by slot type for (persona, topic).
Used by capability check and slot resolver. Canonical layout: block-file pattern.
STORY: atoms/<persona>/<topic>/<engine>/CANONICAL.txt (existing).
Other slot types: atoms/<persona>/<topic>/<slot_type>/CANONICAL.txt (or <slot_type>/<engine>/CANONICAL.txt).
"""
from __future__ import annotations

import hashlib
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
COMPRESSION_ATOMS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "compression_atoms"


@dataclass
class AtomEntry:
    """Minimal entry for an atom in a pool. atom_source: teacher_native | teacher_synthetic | practice_fallback (Teacher Mode)."""
    atom_id: str
    metadata: Optional[dict[str, Any]] = None
    atom_source: Optional[str] = None  # teacher_native | teacher_synthetic | practice_fallback


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def _bindings_topic_key(topic_slug: str) -> str:
    # grief_topic was renamed to grief; keep backward compat for any stale refs
    if topic_slug == "grief_topic":
        return "grief"
    return topic_slug


def _load_story_entries(
    atoms_root: Path,
    persona_slug: str,
    topic_slug: str,
    bindings: dict,
) -> list[AtomEntry]:
    """Load STORY atoms from engines allowed for topic (delegate to assembly_compiler)."""
    from phoenix_v4.planning.assembly_compiler import _load_story_atoms_for_persona_topic
    raw = _load_story_atoms_for_persona_topic(atoms_root, persona_slug, topic_slug, bindings)
    out: list[AtomEntry] = []
    narrative_keys = ("mechanism_depth", "cost_type", "cost_intensity", "identity_stage", "callback_id", "callback_phase")
    for a in raw:
        meta: dict[str, Any] = {"band": a.get("band", 3)}
        if a.get("semantic_family"):
            meta["semantic_family"] = str(a["semantic_family"])
        for k in narrative_keys:
            if k in a and a[k] is not None:
                meta[k] = a[k]
        out.append(AtomEntry(atom_id=a["atom_id"], metadata=meta))
    return out


def _parse_block_file_canonical(path: Path, persona: str, topic: str, slot_type: str) -> list[AtomEntry]:
    """Parse a CANONICAL.txt block file (non-STORY). Blocks: ## TYPE vNN --- metadata --- prose ---."""
    if not path.exists():
        return []
    text = path.read_text()
    # Match ## SOMETHING vNN --- ... ---
    block_re = re.compile(
        r"^##\s+(\S+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---",
        re.MULTILINE,
    )
    out: list[AtomEntry] = []
    for m in block_re.finditer(text):
        _label, ver = m.group(1), m.group(2)
        metadata = m.group(3)
        atom_id = f"{persona}_{topic}_{slot_type}_v{ver}"
        # Optional ID line in metadata overrides
        for line in metadata.splitlines():
            if line.strip().lower().startswith("id:"):
                atom_id = line.split(":", 1)[1].strip()
                break
        out.append(AtomEntry(atom_id=atom_id, metadata={}))
    return out


def _load_compression_pool(persona_slug: str, topic_slug: str) -> list[AtomEntry]:
    """Load COMPRESSION atoms from SOURCE_OF_TRUTH/compression_atoms/approved/<persona>/<topic>/. DEV SPEC 2."""
    approved_dir = COMPRESSION_ATOMS_ROOT / "approved" / persona_slug / topic_slug
    if not approved_dir.exists():
        return []
    entries: list[AtomEntry] = []
    for path in sorted(approved_dir.glob("*.yaml")):
        data = _load_yaml(path)
        if not data:
            continue
        atom_id = data.get("atom_id") or path.stem
        wc = data.get("word_count")
        if wc is not None:
            wc = int(wc)
        meta: dict[str, Any] = {}
        if wc is not None:
            meta["word_count"] = wc
        fam = data.get("compression_family")
        if fam:
            meta["compression_family"] = str(fam)
        entries.append(AtomEntry(atom_id=atom_id, metadata=meta if meta else None))
    return entries


def _load_teacher_pool(teacher_atoms_root: Path, slot_type: str) -> list[AtomEntry]:
    """Load teacher approved atoms from teacher_atoms_root/<slot_type>/*.yaml. Teacher Mode V4. Stamp atom_source from YAML source:."""
    slot_dir = teacher_atoms_root / slot_type
    if not slot_dir.exists():
        return []
    entries: list[AtomEntry] = []
    for path in sorted(slot_dir.glob("*.yaml")):
        data = _load_yaml(path)
        if not data:
            continue
        atom_id = data.get("atom_id") or path.stem
        meta: dict[str, Any] = {}
        if slot_type == "STORY":
            band = data.get("band")
            if band is not None:
                meta["band"] = int(band)
            else:
                meta["band"] = 3
        fam = data.get("semantic_family")
        if fam is not None:
            meta["semantic_family"] = str(fam)
        src = data.get("source") or ""
        atom_source = "teacher_synthetic" if src and "synthetic" in str(src).lower() else "teacher_native"
        entries.append(AtomEntry(atom_id=atom_id, metadata=meta if meta else None, atom_source=atom_source))
    return entries


class PoolIndex:
    """Index of approved atoms by (persona, topic, slot_type). Supports Teacher Mode via teacher_atoms_root."""

    def __init__(
        self,
        atoms_root: Optional[Path] = None,
        bindings_path: Optional[Path] = None,
        teacher_atoms_root: Optional[Path] = None,
    ):
        self.atoms_root = atoms_root or ATOMS_ROOT
        self.bindings_path = bindings_path or (CONFIG_ROOT / "topic_engine_bindings.yaml")
        self.teacher_atoms_root = teacher_atoms_root
        self._bindings = _load_yaml(self.bindings_path)

    def get_pool(
        self,
        slot_type: str,
        persona_id: str,
        topic_id: str,
        format_plan: Optional[dict] = None,
        required_count: Optional[int] = None,
        teacher_exercise_fallback: bool = False,
    ) -> list[AtomEntry]:
        """
        Return list of AtomEntry for (persona, topic, slot_type).
        When teacher_atoms_root is set, loads from teacher_banks/<teacher_id>/approved_atoms/<slot_type>/*.yaml first.
        EXERCISE fallback: when teacher_exercise_fallback and 0 < len(teacher_pool) < required_count, merge with practice library (teacher first); sort by (source_priority, stable_hash(atom_id)).
        Otherwise: STORY from engines; others from atoms/<persona>/<topic>/<slot_type>/CANONICAL.txt.
        """
        if self.teacher_atoms_root is not None:
            teacher_pool = _load_teacher_pool(self.teacher_atoms_root, slot_type)
            if slot_type == "EXERCISE" and teacher_exercise_fallback and required_count is not None and 0 < len(teacher_pool) < required_count:
                from phoenix_v4.planning.practice_selector import get_backstop_pool
                backstop = get_backstop_pool()
                merged = list(teacher_pool) + list(backstop)
                _SOURCE_PRIORITY = {"teacher_native": 0, "teacher_synthetic": 1, "practice_fallback": 2}

                def _sort_key(e: AtomEntry) -> tuple:
                    pri = _SOURCE_PRIORITY.get(getattr(e, "atom_source", None) or "teacher_native", 0)
                    h = hashlib.sha256(e.atom_id.encode("utf-8")).hexdigest()
                    return (pri, h)

                merged.sort(key=_sort_key)
                return merged
            if teacher_pool:
                return teacher_pool
            # Empty teacher pool: return empty (compile will fail or placeholder per spec)
            return []
        if slot_type == "STORY":
            return _load_story_entries(
                self.atoms_root,
                persona_id,
                topic_id,
                self._bindings,
            )
        if slot_type == "COMPRESSION":
            return _load_compression_pool(persona_id, topic_id)
        # Non-STORY: single path atoms/<persona>/<topic>/<slot_type>/CANONICAL.txt
        path = self.atoms_root / persona_id / topic_id / slot_type / "CANONICAL.txt"
        pool = _parse_block_file_canonical(path, persona_id, topic_id, slot_type)
        # EXERCISE backstop: when canonical missing/empty, fill from practice library
        if slot_type == "EXERCISE" and not pool:
            from phoenix_v4.planning.practice_selector import get_backstop_pool
            pool = get_backstop_pool()
        return pool

    def get_pool_sizes(
        self,
        persona_id: str,
        topic_id: str,
        slot_definitions: list[list[str]],
    ) -> dict[str, int]:
        """Return pool size per slot type that appears in slot_definitions."""
        slot_types = set()
        for row in slot_definitions:
            slot_types.update(row)
        sizes: dict[str, int] = {}
        for st in slot_types:
            pool = self.get_pool(st, persona_id, topic_id, None)
            sizes[st] = len(pool)
        return sizes
