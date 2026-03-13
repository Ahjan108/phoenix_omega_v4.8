"""
Pearl Prime Teacher System — blueprint implementation.

Authority: specs/PEARL_PRIME_TEACHER_SYSTEM_BLUEPRINT.md.

Flow: source truth -> authoring layer -> approved atoms -> books.
"""
from pearl_prime.teacher_system.blueprint import (
    AUTHORING_PRIMARY_ASSETS,
    RUNTIME_ATOM_SLOT_FAMILIES,
    AuthoringLayerPaths,
    QualityLevel,
    RuntimeAtomPaths,
    SourceTruthPaths,
    TeacherAuthorityRecord,
    TeacherBankPaths,
    get_teacher_authority,
    get_teacher_bank_paths,
    is_teacher_active,
    list_active_teacher_ids,
    load_teacher_registry,
    quality_level,
)

__all__ = [
    "AUTHORING_PRIMARY_ASSETS",
    "RUNTIME_ATOM_SLOT_FAMILIES",
    "AuthoringLayerPaths",
    "QualityLevel",
    "RuntimeAtomPaths",
    "SourceTruthPaths",
    "TeacherAuthorityRecord",
    "TeacherBankPaths",
    "get_teacher_authority",
    "get_teacher_bank_paths",
    "is_teacher_active",
    "list_active_teacher_ids",
    "load_teacher_registry",
    "quality_level",
]
