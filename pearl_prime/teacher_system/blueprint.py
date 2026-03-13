"""
Pearl Prime Teacher System Blueprint — paths, contracts, quality levels.

Authority: specs/PEARL_PRIME_TEACHER_SYSTEM_BLUEPRINT.md.

Defines:
- Layer paths (source truth, authoring, runtime atoms)
- Active/inactive teacher authority for V4 and Pearl Prime
- Order of operations
- Quality levels: runtime_ready, authoring_complete, source_complete
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# Slot families the compiler uses (blueprint §1.3)
RUNTIME_ATOM_SLOT_FAMILIES = ("HOOK", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION")

# Authoring layer primary assets (blueprint §1.2)
AUTHORING_PRIMARY_ASSETS = (
    "main_teaching_atoms.yaml",
    "story_helpers.yaml",
    "exercise_helpers.yaml",
    "signature_vibe.yaml",
    "content_audit.yaml",
)


class QualityLevel(str, Enum):
    """Pearl Prime teacher quality (blueprint §4)."""

    INCOMPLETE = "incomplete"  # missing doctrine or approved atoms / gates
    RUNTIME_READY = "runtime_ready"
    AUTHORING_COMPLETE = "authoring_complete"
    SOURCE_COMPLETE = "source_complete"


def _dir_has_files(path: Path, glob: str = "*") -> bool:
    """True if directory exists and has at least one file (or matching glob)."""
    if not path.exists() or not path.is_dir():
        return False
    return next(path.glob(glob), None) is not None


@dataclass(frozen=True)
class SourceTruthPaths:
    """Paths for source truth layer (blueprint §1.1)."""

    raw_dir: Path
    kb_dir: Path
    doctrine_file: Path

    def has_doctrine(self) -> bool:
        return self.doctrine_file.exists()

    def has_source_material(self) -> bool:
        """True if raw/ or kb/ has at least one file (provenance recoverable)."""
        return _dir_has_files(self.raw_dir) or _dir_has_files(self.kb_dir)


@dataclass(frozen=True)
class AuthoringLayerPaths:
    """Paths for authoring layer (blueprint §1.2)."""

    doctrine_dir: Path
    main_teaching_atoms: Path
    story_helpers: Path
    exercise_helpers: Path
    signature_vibe: Path
    content_audit: Path

    def primary_assets_exist(self) -> dict[str, bool]:
        return {
            "main_teaching_atoms.yaml": self.main_teaching_atoms.exists(),
            "story_helpers.yaml": self.story_helpers.exists(),
            "exercise_helpers.yaml": self.exercise_helpers.exists(),
            "signature_vibe.yaml": self.signature_vibe.exists(),
            "content_audit.yaml": self.content_audit.exists(),
        }

    def primary_assets_non_empty(self, min_bytes: int = 50) -> dict[str, bool]:
        """True only if file exists and has at least min_bytes (avoids empty stubs)."""
        out = {}
        for name, path in [
            ("main_teaching_atoms.yaml", self.main_teaching_atoms),
            ("story_helpers.yaml", self.story_helpers),
            ("exercise_helpers.yaml", self.exercise_helpers),
            ("signature_vibe.yaml", self.signature_vibe),
            ("content_audit.yaml", self.content_audit),
        ]:
            out[name] = path.exists() and path.stat().st_size >= min_bytes
        return out


@dataclass(frozen=True)
class RuntimeAtomPaths:
    """Paths for runtime atom layer (blueprint §1.3)."""

    approved_atoms_dir: Path
    slot_dirs: dict[str, Path] = field(default_factory=dict)

    def slot_counts(self) -> dict[str, int]:
        counts = {}
        for slot, slot_dir in self.slot_dirs.items():
            if slot_dir.exists():
                counts[slot] = len(list(slot_dir.glob("*.yaml")))
            else:
                counts[slot] = 0
        return counts


@dataclass(frozen=True)
class TeacherBankPaths:
    """All layer paths for one teacher bank."""

    teacher_id: str
    bank_root: Path
    source: SourceTruthPaths
    authoring: AuthoringLayerPaths
    runtime: RuntimeAtomPaths


@dataclass(frozen=True)
class TeacherAuthorityRecord:
    """Canonical teacher authority record for V4 / Pearl Prime runtime and CI."""

    teacher_id: str
    active: bool
    registry_entry: dict[str, Any]
    config_path: Path
    bank: TeacherBankPaths


def get_teacher_bank_paths(
    repo_root: Path,
    teacher_id: str,
) -> TeacherBankPaths:
    """
    Build layer paths for a teacher from SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/.
    """
    bank_root = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id
    raw_dir = bank_root / "raw"
    kb_dir = bank_root / "kb"
    doctrine_in_doctrine = bank_root / "doctrine" / "doctrine.yaml"
    doctrine_root = bank_root / "doctrine.yaml"
    doctrine_file = doctrine_in_doctrine if doctrine_in_doctrine.exists() else doctrine_root

    doctrine_dir = bank_root / "doctrine"
    source = SourceTruthPaths(raw_dir=raw_dir, kb_dir=kb_dir, doctrine_file=doctrine_file)
    authoring = AuthoringLayerPaths(
        doctrine_dir=doctrine_dir,
        main_teaching_atoms=doctrine_dir / "main_teaching_atoms.yaml",
        story_helpers=doctrine_dir / "story_helpers.yaml",
        exercise_helpers=doctrine_dir / "exercise_helpers.yaml",
        signature_vibe=doctrine_dir / "signature_vibe.yaml",
        content_audit=doctrine_dir / "content_audit.yaml",
    )
    approved = bank_root / "approved_atoms"
    slot_dirs = {slot: approved / slot for slot in RUNTIME_ATOM_SLOT_FAMILIES}
    runtime = RuntimeAtomPaths(approved_atoms_dir=approved, slot_dirs=slot_dirs)
    return TeacherBankPaths(teacher_id=teacher_id, bank_root=bank_root, source=source, authoring=authoring, runtime=runtime)


def quality_level(
    paths: TeacherBankPaths,
    *,
    doctrine_exists: bool | None = None,
    min_slots: dict[str, int] | None = None,
) -> QualityLevel:
    """
    Determine quality level for a teacher bank (blueprint §4). Stays honest:
    only teachers with full authoring layer and real content get AUTHORING_COMPLETE;
    only those with actual source material (raw/kb files) get SOURCE_COMPLETE.

    - incomplete: missing doctrine or approved atoms or slot counts below min_slots.
    - runtime_ready: doctrine exists, approved atoms exist, readiness gates pass.
    - authoring_complete: all five primary authoring assets exist and are non-empty (not stubs).
    - source_complete: authoring_complete and raw/ or kb/ has at least one file.

    min_slots: optional per-slot minimum counts for runtime_ready (e.g. EXERCISE 40, HOOK 30).
    """
    min_slots = min_slots or {}
    has_doctrine = doctrine_exists if doctrine_exists is not None else paths.source.has_doctrine()
    if not has_doctrine or not paths.runtime.approved_atoms_dir.exists():
        return QualityLevel.INCOMPLETE
    slot_counts = paths.runtime.slot_counts()
    slots_ok = all(slot_counts.get(slot, 0) >= min_slots.get(slot, 0) for slot in RUNTIME_ATOM_SLOT_FAMILIES)
    if not slots_ok:
        return QualityLevel.INCOMPLETE
    # Authoring-complete: all five primary assets present and non-empty (honest; no stub-only teachers)
    assets_ok = paths.authoring.primary_assets_non_empty()
    if not all(assets_ok.values()):
        return QualityLevel.RUNTIME_READY
    # Source-complete: provenance recoverable (raw or kb has at least one file)
    if not paths.source.has_source_material():
        return QualityLevel.AUTHORING_COMPLETE
    return QualityLevel.SOURCE_COMPLETE


def load_teacher_registry(repo_root: Path) -> dict[str, Any]:
    """Load config/teachers/teacher_registry.yaml; return dict with teachers key."""
    reg_path = repo_root / "config" / "teachers" / "teacher_registry.yaml"
    if not reg_path.exists():
        return {}
    try:
        import yaml
        with open(reg_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def list_active_teacher_ids(repo_root: Path) -> list[str]:
    """Canonical active teacher list for V4 / Pearl Prime runtime and CI."""
    registry = load_teacher_registry(repo_root)
    teachers = registry.get("teachers") or {}
    return [tid for tid, cfg in teachers.items() if (cfg or {}).get("active", True)]


def is_teacher_active(repo_root: Path, teacher_id: str) -> bool:
    """True only when teacher exists in registry and is not explicitly inactive."""
    teachers = (load_teacher_registry(repo_root).get("teachers") or {})
    cfg = teachers.get(teacher_id)
    if cfg is None:
        return False
    return bool(cfg.get("active", True))


def get_teacher_authority(repo_root: Path, teacher_id: str) -> TeacherAuthorityRecord:
    """Return full teacher authority record for runtime, CI, and planning code."""
    registry = load_teacher_registry(repo_root)
    teachers = registry.get("teachers") or {}
    entry = dict(teachers.get(teacher_id) or {})
    return TeacherAuthorityRecord(
        teacher_id=teacher_id,
        active=bool(entry.get("active", True)) if entry else False,
        registry_entry=entry,
        config_path=repo_root / "config" / "teachers" / f"{teacher_id}.yaml",
        bank=get_teacher_bank_paths(repo_root, teacher_id),
    )
