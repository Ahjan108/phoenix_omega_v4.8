#!/usr/bin/env python3
"""
Book script content validation — all locs, langs, personas, topics, teachers.

Knows where all content is that may be used in a book script. Checks:
- All locations and languages (per locale_registry + content_roots_by_locale)
- Enough stories for all persona × topic × engine (STORY pools + min depth)
- Non-STORY slots (HOOK, SCENE, REFLECTION, EXERCISE, INTEGRATION) for all persona × topic
- 100% teacher readiness (doctrine, approved_atoms min counts per teacher)
- 100% system content that appears IN the book script (mechanism_aliases, arcs, reframe bank, etc.)
- 100% system metadata that does NOT appear in the book script (BookSpec/CompiledBook fields)

Authority: docs/DOCS_INDEX.md, config/catalog_planning, config/localization,
  config/source_of_truth, SOURCE_OF_TRUTH/teacher_banks, specs/OMEGA_LAYER_CONTRACTS.md.

Usage:
  python scripts/book_script_content_validation.py [--locale LOC] [--teacher ID] [--plan PATH] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

NON_STORY_SLOT_TYPES = ("HOOK", "SCENE", "REFLECTION", "EXERCISE", "INTEGRATION")

SYSTEM_CONTENT_IN_SCRIPT = [
    ("mechanism_aliases", "config/source_of_truth/mechanism_aliases/{persona}/{topic}.yaml", "persona×topic"),
    ("master_arcs", "config/source_of_truth/master_arcs/{persona}__{topic}__{engine}__{format}.yaml", "persona×topic×engine×format"),
    ("reframe_line_bank", "config/source_of_truth/reframe_line_bank.yaml", "single"),
    ("journey_shapes", "config/source_of_truth/journey_shapes.yaml", "single"),
    ("book_structure_archetypes", "config/source_of_truth/book_structure_archetypes.yaml", "single"),
    ("recurring_motif_bank", "config/source_of_truth/recurring_motif_bank.yaml", "single"),
    ("intro_ending_variation", "config/source_of_truth/intro_ending_variation.yaml", "single"),
    ("carry_line_styles", "config/source_of_truth/carry_line_styles.yaml", "single"),
    ("chapter_archetypes", "config/source_of_truth/chapter_archetypes.yaml", "single"),
    ("opening_recognition_styles", "config/source_of_truth/opening_recognition_styles.yaml", "single"),
    ("integration_ending_styles", "config/source_of_truth/integration_ending_styles.yaml", "single"),
    ("pre_intro_banks", "config/source_of_truth/pre_intro/banks.yaml", "single"),
    ("mechanism_alias_schema", "config/source_of_truth/mechanism_aliases/_schema.yaml", "single"),
    ("mechanism_alias_naming_template", "config/source_of_truth/mechanism_aliases/_naming_template.md", "single"),
]

SYSTEM_METADATA_NOT_IN_SCRIPT = [
    "plan_hash", "chapter_slot_sequence", "atom_ids", "dominant_band_sequence",
    "arc_id", "emotional_temperature_sequence", "chapter_archetypes",
    "chapter_exercise_modes", "chapter_reflection_weights", "chapter_story_depths",
    "chapter_planner_warnings", "slot_sig", "exercise_chapters",
    "topic_id", "persona_id", "series_id", "installment_number", "teacher_id",
    "brand_id", "angle_id", "domain_id", "seed", "locale", "territory",
    "teacher_mode", "author_id", "author_positioning_profile", "narrator_id",
    "freebie_bundle", "freebie_bundle_with_formats", "cta_template_id", "freebie_slug",
    "positioning_signature_hash", "compression_atom_ids", "compression_sig",
    "compression_pos_sig", "compression_len_vec", "emotional_role_sequence",
    "emotional_role_sig", "format_id", "structural_format", "plan_id", "engine_id",
]


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        return {}
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _get_locales(repo: Path) -> list[str]:
    reg = repo / "config" / "localization" / "locale_registry.yaml"
    data = _load_yaml(reg)
    locales = data.get("locales") or {}
    return sorted(locales.keys())


def _get_content_root_for_locale(repo: Path, locale: str) -> str:
    roots = repo / "config" / "localization" / "content_roots_by_locale.yaml"
    data = _load_yaml(roots)
    locs = (data.get("locales") or {}).get(locale) or {}
    return locs.get("atoms_root") or ("atoms" if locale == "en-US" else f"atoms/{locale}")


def _get_personas(repo: Path) -> list[str]:
    path = repo / "config" / "catalog_planning" / "canonical_personas.yaml"
    data = _load_yaml(path)
    return [str(p) for p in (data.get("personas") or []) if p]


def _get_topics(repo: Path) -> list[str]:
    path = repo / "config" / "catalog_planning" / "canonical_topics.yaml"
    data = _load_yaml(path)
    return [str(t) for t in (data.get("topics") or []) if t]


def _get_topic_engines(repo: Path) -> list[tuple[str, list[str]]]:
    path = repo / "config" / "topic_engine_bindings.yaml"
    data = _load_yaml(path)
    out: list[tuple[str, list[str]]] = []
    for k, v in (data or {}).items():
        if k in ("---", "notes") or not isinstance(v, dict):
            continue
        allowed = v.get("allowed_engines") or v.get("engines")
        if allowed:
            out.append((k, [str(e) for e in allowed]))
    return out


def _required_story_tuples(repo: Path) -> list[tuple[str, str, str]]:
    personas = _get_personas(repo)
    topic_engines = _get_topic_engines(repo)
    out: list[tuple[str, str, str]] = []
    for p in personas:
        for topic, engines in topic_engines:
            for e in engines:
                out.append((p, topic, e))
    return sorted(out)


def _required_persona_topic_pairs(repo: Path) -> list[tuple[str, str]]:
    personas = _get_personas(repo)
    topic_engines = _get_topic_engines(repo)
    topics = [t for t, _ in topic_engines]
    out: list[tuple[str, str]] = []
    for p in personas:
        for t in topics:
            out.append((p, t))
    return sorted(set(out))


def _count_story_blocks_plaintext(path: Path) -> int:
    """Plain-text fallback: count ## STORY v\d blocks in a CANONICAL.txt."""
    try:
        text = path.read_text(encoding="utf-8")
        return len(re.findall(r"^##\s+STORY\s+v\d+", text, re.MULTILINE))
    except Exception:
        return 0


def _has_story_pool(atoms_root: Path, persona: str, topic: str, engine: str) -> tuple[bool, int]:
    path = atoms_root / persona / topic / engine / "CANONICAL.txt"
    if not path.exists():
        return False, 0
    try:
        from phoenix_v4.planning.assembly_compiler import _parse_canonical_txt
        atoms = _parse_canonical_txt(path)
        return len(atoms) > 0, len(atoms)
    except Exception:
        # Fallback: plain-text block count so import failures don't silently
        # mark every existing pool as missing.
        count = _count_story_blocks_plaintext(path)
        return count > 0, count


_NON_STORY_BLOCK_RE = re.compile(
    r"^##\s+(\S+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---",
    re.MULTILINE,
)


def _has_non_story_pool(atoms_root: Path, persona: str, topic: str, slot_type: str) -> tuple[bool, int]:
    path = atoms_root / persona / topic / slot_type / "CANONICAL.txt"
    if not path.exists():
        return False, 0
    try:
        text = path.read_text(encoding="utf-8")
        count = len(_NON_STORY_BLOCK_RE.findall(text))
        return count > 0, count
    except Exception:
        return False, 0


def _min_story_depth(repo: Path) -> int:
    try:
        g = _load_yaml(repo / "config" / "gates.yaml")
        return int((g.get("tuple_viability") or {}).get("min_story_pool_size", 12))
    except Exception:
        return 12


def check_locs_langs(repo: Path) -> dict:
    locales = _get_locales(repo)
    min_depth = _min_story_depth(repo)
    story_tuples = _required_story_tuples(repo)
    pairs = _required_persona_topic_pairs(repo)
    by_locale: dict = {}
    for locale in locales:
        root_rel = _get_content_root_for_locale(repo, locale)
        atoms_root = repo / root_rel
        if not atoms_root.exists():
            by_locale[locale] = {
                "status": "missing_root",
                "atoms_root": root_rel,
                "story_ok": 0,
                "story_total": len(story_tuples),
                "story_missing": list(story_tuples)[:20],
                "story_shallow": [],
                "non_story_missing": {},
            }
            continue
        story_missing: list[tuple[str, str, str]] = []
        story_shallow: list[tuple[str, str, str, int]] = []
        for p, t, e in story_tuples:
            ok, count = _has_story_pool(atoms_root, p, t, e)
            if not ok:
                story_missing.append((p, t, e))
            elif count < min_depth:
                story_shallow.append((p, t, e, count))
        non_story_missing: dict[str, list[tuple[str, str]]] = {st: [] for st in NON_STORY_SLOT_TYPES}
        for p, t in pairs:
            for st in NON_STORY_SLOT_TYPES:
                ok, _ = _has_non_story_pool(atoms_root, p, t, st)
                if not ok:
                    non_story_missing[st].append((p, t))
        total_non_story = sum(len(v) for v in non_story_missing.values())
        by_locale[locale] = {
            "status": "ok" if not story_missing and total_non_story == 0 else "gaps",
            "atoms_root": root_rel,
            "story_ok": len(story_tuples) - len(story_missing),
            "story_total": len(story_tuples),
            "story_missing": story_missing[:30],
            "story_shallow": story_shallow[:20],
            "min_story_depth": min_depth,
            "non_story_missing": {k: v[:15] for k, v in non_story_missing.items() if v},
        }
    return {"locales": locales, "by_locale": by_locale}


def check_teachers(repo: Path) -> dict:
    reg_path = repo / "config" / "teachers" / "teacher_registry.yaml"
    data = _load_yaml(reg_path)
    teachers = list((data.get("teachers") or {}).keys())
    banks = repo / "SOURCE_OF_TRUTH" / "teacher_banks"
    by_teacher: dict = {}
    for tid in teachers:
        bank = banks / tid
        doctrine = bank / "doctrine" / "doctrine.yaml"
        if not doctrine.exists():
            doctrine = bank / "doctrine.yaml"
        approved_root = bank / "approved_atoms"
        counts: dict[str, int] = {}
        if approved_root.exists():
            for slot_dir in approved_root.iterdir():
                if slot_dir.is_dir():
                    n = sum(1 for f in slot_dir.iterdir() if f.suffix in (".yaml", ".yml", ".json"))
                    counts[slot_dir.name] = n
        min_exercise, min_story = 12, 12
        min_hook = min_reflection = min_integration = 0
        errors: list[str] = []
        if counts.get("EXERCISE", 0) < min_exercise:
            errors.append(f"EXERCISE {counts.get('EXERCISE', 0)} < {min_exercise}")
        if counts.get("STORY", 0) < min_story:
            errors.append(f"STORY {counts.get('STORY', 0)} < {min_story}")
        if counts.get("HOOK", 0) < min_hook:
            errors.append(f"HOOK {counts.get('HOOK', 0)} < {min_hook}")
        if counts.get("REFLECTION", 0) < min_reflection:
            errors.append(f"REFLECTION {counts.get('REFLECTION', 0)} < {min_reflection}")
        if counts.get("INTEGRATION", 0) < min_integration:
            errors.append(f"INTEGRATION {counts.get('INTEGRATION', 0)} < {min_integration}")
        by_teacher[tid] = {
            "doctrine_present": doctrine.exists(),
            "approved_atoms": counts,
            "errors": errors,
            "status": "ok" if not errors and doctrine.exists() else "gaps",
        }
    return {"teachers": teachers, "by_teacher": by_teacher}


def check_system_content_in_script(repo: Path) -> dict:
    personas = _get_personas(repo)
    topic_engines = _get_topic_engines(repo)
    topics_canonical = _get_topics(repo)
    format_id = "F006"
    single_files: list[tuple[str, str]] = []
    mechanism_missing: list[tuple[str, str]] = []
    arc_missing: list[tuple[str, str, str, str]] = []
    for name, pattern, kind in SYSTEM_CONTENT_IN_SCRIPT:
        if kind == "single":
            p = repo / pattern
            single_files.append((name, "ok" if p.exists() else "missing"))
        elif kind == "persona×topic":
            for persona in personas:
                for topic in topics_canonical:
                    path = repo / pattern.format(persona=persona, topic=topic)
                    if not path.exists():
                        mechanism_missing.append((persona, topic))
        elif kind == "persona×topic×engine×format":
            for persona in personas:
                for topic, engines in topic_engines:
                    for engine in engines:
                        path = repo / pattern.format(
                            persona=persona, topic=topic, engine=engine, format=format_id
                        )
                        if not path.exists():
                            arc_missing.append((persona, topic, engine, format_id))
    return {
        "single_files": dict(single_files),
        "mechanism_aliases_missing": mechanism_missing[:50],
        "master_arcs_missing": arc_missing[:50],
        "status": "ok"
        if all(s[1] == "ok" for s in single_files) and not mechanism_missing and not arc_missing
        else "gaps",
    }


def system_metadata_not_in_script_report() -> dict:
    return {
        "description": "These fields exist on BookSpec/CompiledBook but are not rendered into book text.",
        "fields": list(SYSTEM_METADATA_NOT_IN_SCRIPT),
    }


def check_plan_metadata(plan_path: Path) -> dict | None:
    if not plan_path.exists():
        return None
    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    present = [f for f in SYSTEM_METADATA_NOT_IN_SCRIPT if f in data and data[f] is not None]
    return {
        "plan_path": str(plan_path),
        "metadata_fields_present": present,
        "metadata_fields_expected": SYSTEM_METADATA_NOT_IN_SCRIPT,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Book script content validation (all locs, langs, teachers, system content)")
    ap.add_argument("--locale", default=None, help="Check only this locale (default: all)")
    ap.add_argument("--teacher", default=None, help="Check only this teacher (default: all)")
    ap.add_argument("--plan", default=None, help="Path to plan JSON: report metadata vs script for this book")
    ap.add_argument("--json", action="store_true", help="Output JSON report")
    ap.add_argument("--repo", default=None, help="Repo root (default: script parent parent)")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else REPO_ROOT

    out: dict = {
        "locs_langs": check_locs_langs(repo),
        "teachers": check_teachers(repo),
        "system_content_in_script": check_system_content_in_script(repo),
        "system_metadata_not_in_script": system_metadata_not_in_script_report(),
    }
    if args.plan:
        out["plan_metadata"] = check_plan_metadata(Path(args.plan))

    if args.json:
        print(json.dumps(out, indent=2))
        failed = False
        for loc, info in out["locs_langs"].get("by_locale", {}).items():
            if args.locale and loc != args.locale:
                continue
            if info.get("status") != "ok":
                failed = True
                break
        for tid, info in out["teachers"].get("by_teacher", {}).items():
            if args.teacher and tid != args.teacher:
                continue
            if info.get("status") != "ok":
                failed = True
                break
        if out["system_content_in_script"].get("status") != "ok":
            failed = True
        return 1 if failed else 0

    lines: list[str] = []
    lines.append("=== Book script content validation ===\n")
    ll = out["locs_langs"]
    lines.append("Locations & languages")
    for loc, info in ll.get("by_locale", {}).items():
        if args.locale and loc != args.locale:
            continue
        s = info.get("status", "?")
        root = info.get("atoms_root", "?")
        so, st = info.get("story_ok", 0), info.get("story_total", 0)
        lines.append(f"  {loc}: {s} (atoms_root={root}, story {so}/{st})")
        if info.get("story_missing"):
            for m in info["story_missing"][:5]:
                lines.append(f"    missing STORY: {m[0]}/{m[1]}/{m[2]}")
        if info.get("non_story_missing"):
            for slot, missing in info["non_story_missing"].items():
                lines.append(f"    missing {slot}: {len(missing)} pairs")
    lines.append("")
    te = out["teachers"]
    lines.append("Teachers (100% readiness)")
    for tid, info in te.get("by_teacher", {}).items():
        if args.teacher and tid != args.teacher:
            continue
        s = info.get("status", "?")
        doctrine = "yes" if info.get("doctrine_present") else "no"
        counts = info.get("approved_atoms", {})
        lines.append(f"  {tid}: {s} (doctrine={doctrine}, atoms={counts})")
        for e in info.get("errors", [])[:5]:
            lines.append(f"    {e}")
    lines.append("")
    sc = out["system_content_in_script"]
    lines.append("System content IN book script (100%)")
    lines.append(f"  status: {sc.get('status', '?')}")
    for name, status in sc.get("single_files", {}).items():
        lines.append(f"  {name}: {status}")
    if sc.get("mechanism_aliases_missing"):
        lines.append(f"  mechanism_aliases missing: {len(sc['mechanism_aliases_missing'])} persona×topic")
    if sc.get("master_arcs_missing"):
        lines.append(f"  master_arcs missing: {len(sc['master_arcs_missing'])} persona×topic×engine×format")
    lines.append("")
    meta = out["system_metadata_not_in_script"]
    lines.append("System metadata NOT in book script (reference)")
    lines.append(f"  {meta.get('description', '')}")
    lines.append(f"  fields: {len(meta.get('fields', []))} (see --json for list)")
    if out.get("plan_metadata"):
        pm = out["plan_metadata"]
        lines.append(f"\nPlan: {pm.get('plan_path', '')}")
        lines.append(f"  metadata present: {len(pm.get('metadata_fields_present', []))} fields")
    print("\n".join(lines))

    failed = False
    for loc, info in ll.get("by_locale", {}).items():
        if args.locale and loc != args.locale:
            continue
        if info.get("status") != "ok":
            failed = True
            break
    for tid, info in te.get("by_teacher", {}).items():
        if args.teacher and tid != args.teacher:
            continue
        if info.get("status") != "ok":
            failed = True
            break
    if sc.get("status") != "ok":
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
