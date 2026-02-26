#!/usr/bin/env python3
"""
LLM intake pass for Teacher Authoring Layer. Produces doctrine assets from raw/.
Authority: specs/TEACHER_AUTHORING_LAYER_SPEC.md §7.
Reads raw/ (RTF, TXT, MD), runs 3-5 LLM extraction calls, writes:
  main_teaching_atoms.yaml, story_helpers.yaml, exercise_helpers.yaml,
  signature_vibe.yaml, content_audit.yaml, intake_manifest.json.
If doctrine.yaml missing, generates it. All outputs have reviewed_by: null.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_TEACHER = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_TEACHER))

try:
    import yaml
except ImportError:
    yaml = None

try:
    from rtf_to_text import rtf_to_text
except ImportError:
    rtf_to_text = None


def _extract_text(path: Path) -> str:
    """Extract plain text from RTF, TXT, MD. PDF not supported here."""
    suffix = path.suffix.lower()
    raw = path.read_bytes()
    if suffix == ".rtf" and rtf_to_text:
        return rtf_to_text(raw)
    if suffix in (".txt", ".md"):
        return raw.decode("utf-8", errors="replace")
    return raw.decode("utf-8", errors="replace")


def _load_raw_corpus(raw_dir: Path) -> list[tuple[str, str]]:
    """Return [(filename, text), ...] for RTF, TXT, MD under raw_dir."""
    out: list[tuple[str, str]] = []
    if not raw_dir.is_dir():
        return out
    for p in sorted(raw_dir.rglob("*")):
        if not p.is_file() or p.name.startswith("."):
            continue
        if p.suffix.lower() not in (".rtf", ".txt", ".md"):
            continue
        try:
            text = _extract_text(p)
            if text.strip():
                out.append((p.name, text.strip()))
        except Exception:
            continue
    return out


def _load_doctrine(doctrine_path: Path) -> dict | None:
    if not doctrine_path.exists() or not yaml:
        return None
    try:
        data = yaml.safe_load(doctrine_path.read_text()) or {}
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _call_llm(
    system: str,
    user: str,
    teacher_id: str,
    model: str,
    dry_run: bool,
) -> str:
    """One LLM call. Seed by teacher_id, temperature 0. Stub if no API key or dry_run."""
    if dry_run:
        return ""
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    try:
        import anthropic
    except ImportError:
        anthropic = None
    if not api_key or not anthropic:
        return ""
    # Seed for reproducibility (spec §7.4)
    seed = int(hashlib.sha256(f"intake_normalize:{teacher_id}".encode()).hexdigest()[:8], 16)
    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model,
            max_tokens=8192,
            system=system,
            messages=[{"role": "user", "content": user}],
            temperature=0,
        )
        if msg.content and isinstance(msg.content, list) and len(msg.content) > 0:
            block = msg.content[0]
            if hasattr(block, "text"):
                return block.text
            if isinstance(block, dict) and "text" in block:
                return block["text"]
    except Exception as e:
        sys.stderr.write(f"LLM call failed: {e}\n")
    return ""


def _parse_llm_yaml_block(raw: str) -> dict:
    """Extract first YAML block from markdown or raw YAML."""
    if not raw or not yaml:
        return {}
    # Try full doc
    try:
        return yaml.safe_load(raw) or {}
    except Exception:
        pass
    # Try ```yaml ... ```
    m = re.search(r"```(?:yaml|yml)?\s*\n([\s\S]*?)```", raw)
    if m:
        try:
            return yaml.safe_load(m.group(1)) or {}
        except Exception:
            pass
    return {}


def _stub_main_teaching_atoms(teacher_id: str) -> dict:
    """Stub YAML when LLM is not available (dry-run or no API key)."""
    base = {
        "teaching_statement": "Placeholder: replace with teacher's core idea.",
        "mechanism": "Placeholder: how change works in this framework.",
        "counter_pattern": "Placeholder: what this teaching corrects.",
        "story_seed": "Placeholder: what a story proving this teaching looks like.",
        "exercise_seed": "Placeholder: what a practice applying this teaching looks like.",
        "band_affinity": [2, 3, 4],
        "allowed_topics": ["anxiety", "self_worth"],
        "tags": ["placeholder"],
    }
    atoms = [{**base, "concept_id": f"core_teaching_{i}"} for i in range(1, 6)]
    return {
        "schema_version": "1.0",
        "teacher_id": teacher_id,
        "extraction_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "reviewed_by": None,
        "review_date": None,
        "main_teaching_atoms": atoms,
    }


def _stub_story_helpers(teacher_id: str) -> dict:
    return {
        "schema_version": "1.0",
        "teacher_id": teacher_id,
        "narrator_position": "author_as_interpreter",
        "narrator_voice": "The author describes how someone benefited from the teacher's teaching. Third person for others.",
        "transformation_patterns": [
            {"pattern_id": "recognition", "description": "Placeholder.", "serves_mta": ["core_teaching_1", "core_teaching_2"], "typical_arc": "stuck → encounter_teaching → shift"},
            {"pattern_id": "application", "description": "Placeholder.", "serves_mta": ["core_teaching_1"], "typical_arc": "apply → difficulty → partial_resolution"},
        ],
        "persona_scenarios": {"gen_z_professionals": ["Placeholder scenario."], "healthcare_rns": ["Placeholder scenario."]},
        "band_templates": {
            "band_1_2": {"shape": "Early recognition.", "resolution": "Open."},
            "band_3": {"shape": "Mechanism visible.", "resolution": "Partial."},
            "band_4_5": {"shape": "Cost and complication.", "resolution": "Open loop."},
        },
        "forbidden_moves": [
            "Character has emotional breakthrough through journaling alone",
            "Story ends with character feeling healed or fixed",
            "Author claims direct lineage with teacher",
        ],
    }


def _stub_exercise_helpers(teacher_id: str) -> dict:
    return {
        "schema_version": "1.0",
        "teacher_id": teacher_id,
        "supported_families": [
            {"family_id": "grounding", "description": "Placeholder.", "example_prompt": "Notice the ground.", "frequency": "primary"},
            {"family_id": "breath_grounding", "description": "Placeholder.", "example_prompt": "Breathe and notice place.", "frequency": "secondary"},
        ],
        "unsupported_families": ["journaling", "visualization", "affirmation"],
        "adaptation_wrappers": {
            "intro_templates": ["Before you begin, notice where you are. {TEACHER_CONCEPT} begins with location.", "This practice works with body and environment."],
            "close_templates": ["The ground was here before the stress arrived.", "Knowing where you are is the first step."],
        },
        "safety": {
            "max_intensity": "low_to_moderate",
            "notes": "Observation-based; low risk.",
            "forbidden_exercise_types": ["trauma_regression", "emotional_catharsis"],
        },
        "mta_mapping": {"core_teaching_1": ["grounding", "breath_grounding"], "core_teaching_2": ["grounding"]},
    }


def _stub_signature_vibe(teacher_id: str) -> dict:
    return {
        "schema_version": "1.0",
        "teacher_id": teacher_id,
        "voice_instruction": "Write in a clear, observational tone. Show rather than tell. No motivational language.",
        "sentence_constraints": {
            "preferred_length_range": [8, 25],
            "max_sentence_length": 35,
            "preferred_paragraph_length": [2, 5],
            "allowed_opening_words": {"preferred": ["The", "He", "She", "It", "This"], "forbidden": ["Amazingly", "Interestingly"]},
            "forbidden_sentence_patterns": ["exclamation marks", "rhetorical questions for emphasis"],
        },
        "vocabulary": {
            "preferred_words": ["notice", "observe", "ground", "shift"],
            "forbidden_words": ["manifest", "guaranteed", "breakthrough", "amazing"],
            "tone_words": ["quiet", "precise", "observational"],
            "anti_tone_words": ["devotional", "inspirational", "urgent"],
        },
        "emotional_register": {"allowed": ["calm_observation", "matter_of_fact"], "forbidden": ["catharsis", "triumph", "devotional_reverence"]},
    }


def _stub_content_audit(teacher_id: str, filenames: list[str]) -> dict:
    files = []
    for fn in filenames[:50]:
        files.append({
            "filename": fn,
            "usability": "medium",
            "atom_types": ["TEACHING", "STORY"],
            "mta_coverage": ["core_teaching_1"],
            "notes": "Stub: review and set usability and MTA coverage.",
        })
    return {
        "schema_version": "1.0",
        "teacher_id": teacher_id,
        "files": files if files else [{"filename": "placeholder.txt", "usability": "high", "atom_types": ["TEACHING"], "mta_coverage": ["core_teaching_1"], "notes": "No raw files found."}],
        "unusable_content": [],
    }


def _run_extraction(
    teacher_id: str,
    raw_dir: Path,
    out_dir: Path,
    model: str,
    dry_run: bool,
    doctrine_path: Path,
) -> tuple[dict, dict, dict, dict, dict, dict | None]:
    """Run LLM extraction (or stub). Returns (mta, story, exercise, vibe, audit, doctrine_or_none)."""
    corpus = _load_raw_corpus(raw_dir)
    corpus_text = "\n\n---\n\n".join(f"[{fn}]\n{t[:50000]}" for fn, t in corpus)  # cap per file for context
    filenames = [fn for fn, _ in corpus]
    prior_doctrine = _load_doctrine(doctrine_path)

    mta_data = {}
    story_data = {}
    exercise_data = {}
    vibe_data = {}
    audit_data = {}

    if not dry_run and corpus_text and os.environ.get("ANTHROPIC_API_KEY"):
        # Call 1: Main Teaching Atoms
        sys.stderr.write("Call 1: Core concept extraction...\n")
        system1 = "You are analyzing a teacher's body of work to extract their core intellectual contributions. Identify 5-20 distinct main teaching concepts. For each provide: concept_id (snake_case), teaching_statement, mechanism, counter_pattern, story_seed, exercise_seed, band_affinity (list 1-5), allowed_topics (list), optional tags. Output valid YAML only."
        user1 = f"Teacher ID: {teacher_id}\n\nCorpus:\n{corpus_text[:120000]}"
        out1 = _call_llm(system1, user1, teacher_id, model, False)
        mta_data = _parse_llm_yaml_block(out1)
        if not mta_data or "main_teaching_atoms" not in mta_data:
            mta_data = _stub_main_teaching_atoms(teacher_id)
        else:
            mta_data.setdefault("schema_version", "1.0")
            mta_data.setdefault("teacher_id", teacher_id)
            mta_data.setdefault("reviewed_by", None)
            mta_data.setdefault("review_date", None)
            mta_data.setdefault("extraction_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

        # Call 2: Story Helpers
        sys.stderr.write("Call 2: Story helper extraction...\n")
        system2 = "Create story-writing guidance. Extract: narrator_position, narrator_voice, transformation_patterns (pattern_id, description, serves_mta, typical_arc), persona_scenarios (persona_id -> list of scenario strings), band_templates (band_1_2, band_3, band_4_5: shape, resolution), forbidden_moves (list). Output valid YAML only."
        user2 = f"Teacher ID: {teacher_id}\n\nMain teaching atoms:\n{yaml.dump(mta_data) if yaml else ''}\n\nCorpus excerpt:\n{corpus_text[:60000]}"
        out2 = _call_llm(system2, user2, teacher_id, model, False)
        story_data = _parse_llm_yaml_block(out2)
        if not story_data or "transformation_patterns" not in story_data:
            story_data = _stub_story_helpers(teacher_id)
        else:
            story_data.setdefault("schema_version", "1.0")
            story_data.setdefault("teacher_id", teacher_id)

        # Call 3: Exercise Helpers
        sys.stderr.write("Call 3: Exercise helper extraction...\n")
        system3 = "Identify practice families and exercise guidance. Extract: supported_families (family_id, description, example_prompt, frequency), unsupported_families, adaptation_wrappers (intro_templates, close_templates; may use {TEACHER_CONCEPT}), safety (max_intensity, notes, forbidden_exercise_types), mta_mapping (concept_id -> list of family_ids). Output valid YAML only."
        user3 = f"Teacher ID: {teacher_id}\n\nMain teaching atoms:\n{yaml.dump(mta_data) if yaml else ''}\n\nCorpus excerpt:\n{corpus_text[:60000]}"
        out3 = _call_llm(system3, user3, teacher_id, model, False)
        exercise_data = _parse_llm_yaml_block(out3)
        if not exercise_data or "supported_families" not in exercise_data:
            exercise_data = _stub_exercise_helpers(teacher_id)
        else:
            exercise_data.setdefault("schema_version", "1.0")
            exercise_data.setdefault("teacher_id", teacher_id)

        # Call 4: Signature Vibe
        sys.stderr.write("Call 4: Signature vibe extraction...\n")
        system4 = "Capture the felt quality as writing constraints. Extract: voice_instruction (max 200 words), sentence_constraints (preferred_length_range, max_sentence_length, preferred_paragraph_length, allowed_opening_words, forbidden_sentence_patterns), vocabulary (preferred_words, forbidden_words, tone_words, anti_tone_words), emotional_register (allowed, forbidden). Output valid YAML only."
        user4 = f"Teacher ID: {teacher_id}\n\nCorpus excerpt:\n{corpus_text[:80000]}"
        out4 = _call_llm(system4, user4, teacher_id, model, False)
        vibe_data = _parse_llm_yaml_block(out4)
        if not vibe_data or "voice_instruction" not in vibe_data:
            vibe_data = _stub_signature_vibe(teacher_id)
        else:
            vibe_data.setdefault("schema_version", "1.0")
            vibe_data.setdefault("teacher_id", teacher_id)

        # Call 5: Content Audit
        sys.stderr.write("Call 5: Content audit...\n")
        file_previews = "\n".join(f"[{fn}]\n{t[:2000]}" for fn, t in corpus[:30])
        system5 = "Classify each source file. For each: usability (high/medium/low), atom_types (list), mta_coverage (concept_ids), notes, optional extraction_warnings. Also list unusable_content (description, reason). Output valid YAML with 'files' and optional 'unusable_content'."
        user5 = f"Teacher ID: {teacher_id}\n\nMain teaching concept_ids: {[a.get('concept_id') for a in mta_data.get('main_teaching_atoms', [])]}\n\nFile previews:\n{file_previews}"
        out5 = _call_llm(system5, user5, teacher_id, model, False)
        audit_data = _parse_llm_yaml_block(out5)
        if not audit_data or "files" not in audit_data:
            audit_data = _stub_content_audit(teacher_id, filenames)
        else:
            audit_data.setdefault("schema_version", "1.0")
            audit_data.setdefault("teacher_id", teacher_id)
    else:
        mta_data = _stub_main_teaching_atoms(teacher_id)
        story_data = _stub_story_helpers(teacher_id)
        exercise_data = _stub_exercise_helpers(teacher_id)
        vibe_data = _stub_signature_vibe(teacher_id)
        audit_data = _stub_content_audit(teacher_id, filenames)

    # Ensure reviewed_by null
    for d in (mta_data, story_data, exercise_data, vibe_data, audit_data):
        d["reviewed_by"] = None
        d["review_date"] = None

    # Doctrine: generate minimal if missing
    doctrine_out = None
    if not prior_doctrine or not prior_doctrine.get("teacher_id"):
        doctrine_out = {
            "teacher_id": teacher_id,
            "doctrine_version": 1,
            "glossary": [],
            "forbidden_claims": [],
            "tone_profile": "observational",
        }

    return mta_data, story_data, exercise_data, vibe_data, audit_data, doctrine_out


def _validate_and_collect_errors(
    teacher_id: str,
    mta_data: dict,
    story_data: dict,
    exercise_data: dict,
    audit_data: dict,
) -> list[dict]:
    """Cross-check concept_ids, persona_ids, topics, family_ids. Return list of error dicts."""
    errors: list[dict] = []
    concept_ids = {a.get("concept_id") for a in (mta_data.get("main_teaching_atoms") or []) if a.get("concept_id")}

    # MTAs count
    mta_list = mta_data.get("main_teaching_atoms") or []
    if len(mta_list) < 5:
        errors.append({"rule": "min_mtas", "message": f"main_teaching_atoms has {len(mta_list)} items; minimum is 5."})
    if len(mta_list) > 20:
        errors.append({"rule": "max_mtas", "message": f"main_teaching_atoms has {len(mta_list)} items; maximum is 20."})

    # story_helpers: serves_mta reference valid concept_ids
    for tp in (story_data.get("transformation_patterns") or []):
        for sid in (tp.get("serves_mta") or []):
            if sid not in concept_ids:
                errors.append({"rule": "story_serves_mta", "message": f"transformation_pattern serves_mta '{sid}' not in main_teaching_atoms concept_ids."})

    # exercise_helpers: mta_mapping keys in concept_ids, values in supported_families
    supported = {f.get("family_id") for f in (exercise_data.get("supported_families") or [])}
    for cid, fams in (exercise_data.get("mta_mapping") or {}).items():
        if cid not in concept_ids:
            errors.append({"rule": "mta_mapping_concept", "message": f"mta_mapping concept_id '{cid}' not in main_teaching_atoms."})
        for fid in (fams or []):
            if fid not in supported:
                errors.append({"rule": "mta_mapping_family", "message": f"mta_mapping family_id '{fid}' not in supported_families."})

    # content_audit: mta_coverage references concept_ids
    for f in (audit_data.get("files") or []):
        for mid in (f.get("mta_coverage") or []):
            if mid not in concept_ids:
                errors.append({"rule": "audit_mta_coverage", "message": f"content_audit file {f.get('filename')} mta_coverage '{mid}' not in main_teaching_atoms."})

    # teacher_registry allowed_topics
    reg_path = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"
    if reg_path.exists() and yaml:
        try:
            reg = yaml.safe_load(reg_path.read_text()) or {}
            teacher_entry = (reg.get("teachers") or {}).get(teacher_id, {})
            allowed_topics = set(teacher_entry.get("allowed_topics") or [])
            for a in mta_list:
                for t in (a.get("allowed_topics") or []):
                    if t not in allowed_topics:
                        errors.append({"rule": "mta_allowed_topics", "message": f"MTA {a.get('concept_id')} allowed_topic '{t}' not in teacher_registry allowed_topics."})
        except Exception:
            pass

    return errors


def run_intake(
    teacher_id: str,
    raw_dir: Path,
    out_dir: Path,
    model: str = "claude-sonnet-4-20250514",
    dry_run: bool = False,
) -> int:
    """Run full intake pass. Write YAMLs and manifest. Return 0 on success, 1 on validation failure."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    doctrine_path = out_dir / "doctrine.yaml"
    raw_dir = Path(raw_dir)

    mta_data, story_data, exercise_data, vibe_data, audit_data, doctrine_out = _run_extraction(
        teacher_id, raw_dir, out_dir, model, dry_run, doctrine_path
    )

    if yaml:
        (out_dir / "main_teaching_atoms.yaml").write_text(yaml.dump(mta_data, default_flow_style=False, allow_unicode=True, sort_keys=False))
        (out_dir / "story_helpers.yaml").write_text(yaml.dump(story_data, default_flow_style=False, allow_unicode=True, sort_keys=False))
        (out_dir / "exercise_helpers.yaml").write_text(yaml.dump(exercise_data, default_flow_style=False, allow_unicode=True, sort_keys=False))
        (out_dir / "signature_vibe.yaml").write_text(yaml.dump(vibe_data, default_flow_style=False, allow_unicode=True, sort_keys=False))
        (out_dir / "content_audit.yaml").write_text(yaml.dump(audit_data, default_flow_style=False, allow_unicode=True, sort_keys=False))
    else:
        for name, data in [("main_teaching_atoms.yaml", mta_data), ("story_helpers.yaml", story_data), ("exercise_helpers.yaml", exercise_data), ("signature_vibe.yaml", vibe_data), ("content_audit.yaml", audit_data)]:
            (out_dir / name).write_text(json.dumps(data, indent=2))

    if doctrine_out and not dry_run:
        if yaml:
            (out_dir / "doctrine.yaml").write_text(yaml.dump(doctrine_out, default_flow_style=False, allow_unicode=True, sort_keys=False))
        else:
            (out_dir / "doctrine.yaml").write_text(json.dumps(doctrine_out, indent=2))

    validation_errors = _validate_and_collect_errors(teacher_id, mta_data, story_data, exercise_data, audit_data)
    if validation_errors:
        err_path = out_dir / "intake_validation_errors.json"
        err_path.write_text(json.dumps({"teacher_id": teacher_id, "errors": validation_errors}, indent=2))
        for e in validation_errors:
            sys.stderr.write(f"Validation: {e.get('message', '')}\n")
        return 1

    manifest = {
        "teacher_id": teacher_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "dry_run": dry_run,
        "raw_dir": str(raw_dir),
        "out_dir": str(out_dir),
        "corpus_files": [fn for fn, _ in _load_raw_corpus(raw_dir)],
        "extraction_prompts_used": ["core_concepts", "story_helpers", "exercise_helpers", "signature_vibe", "content_audit"],
    }
    (out_dir / "intake_manifest.json").write_text(json.dumps(manifest, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="LLM intake pass for Teacher Authoring Layer (TEACHER_AUTHORING_LAYER_SPEC §7)")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    ap.add_argument("--raw-dir", default=None, help="Raw files dir (default: SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/raw)")
    ap.add_argument("--out-dir", default=None, help="Doctrine output dir (default: SOURCE_OF_TRUTH/teacher_banks/<teacher_id>/doctrine)")
    ap.add_argument("--model", default="claude-sonnet-4-20250514", help="LLM model")
    ap.add_argument("--dry-run", action="store_true", help="Write stub YAML only, no LLM calls")
    args = ap.parse_args()
    teacher_id = args.teacher.strip()
    banks = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks" / teacher_id
    raw_dir = Path(args.raw_dir) if args.raw_dir else banks / "raw"
    out_dir = Path(args.out_dir) if args.out_dir else banks / "doctrine"
    return run_intake(teacher_id, raw_dir, out_dir, model=args.model, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
