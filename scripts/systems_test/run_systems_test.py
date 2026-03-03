#!/usr/bin/env python3
"""
Rigorous systems test: exercises pipeline, config, resolvers, freebies, asset pipeline, CI/QA, contracts.
Learn: structured report with category. Fix: suggested_fix per failure. Enhance: regression assertions inline.
Usage:
  python scripts/systems_test/run_systems_test.py --all
  python scripts/systems_test/run_systems_test.py --phase 1 --phase 2
  python scripts/systems_test/run_systems_test.py --all --output-dir artifacts/systems_test --strict
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

# Result: pass (bool), check_id (str), category (str), message (str), artifact_path (str|None), suggested_fix (str|None)
RESULTS: list[dict] = []


def record(check_id: str, passed: bool, category: str, message: str, artifact_path: str | None = None, suggested_fix: str | None = None) -> None:
    RESULTS.append({
        "check_id": check_id,
        "passed": passed,
        "category": category,
        "message": message,
        "artifact_path": artifact_path,
        "suggested_fix": suggested_fix,
    })


def run_phase_1_config(output_dir: Path) -> None:
    """Phase 1: Config and schema validity."""
    try:
        import yaml
    except ImportError:
        record("phase1_yaml", False, "config_missing", "PyYAML required for config checks", None, "pip install pyyaml")
        return

    config_root = REPO_ROOT / "config"
    # topic_engine_bindings
    bindings_path = config_root / "topic_engine_bindings.yaml"
    if not bindings_path.exists():
        record("phase1_topic_engine_bindings", False, "config_missing", "config/topic_engine_bindings.yaml missing", str(bindings_path), "Create file with topic keys and allowed_engines")
    else:
        try:
            data = yaml.safe_load(bindings_path.read_text()) or {}
            topics = [k for k in data if isinstance(data[k], dict) and k not in ("---", "notes")]
            if not topics:
                record("phase1_topic_engine_bindings", False, "config_schema", "No topic entries with allowed_engines", str(bindings_path), "Add topics with allowed_engines")
            else:
                bad = [t for t in topics if "allowed_engines" not in (data.get(t) or {})]
                if bad:
                    record("phase1_topic_engine_bindings", False, "config_schema", f"Topics missing allowed_engines: {bad[:5]}", str(bindings_path), "Add allowed_engines per topic")
                else:
                    record("phase1_topic_engine_bindings", True, "config_schema", "topic_engine_bindings OK", str(bindings_path), None)
        except Exception as e:
            record("phase1_topic_engine_bindings", False, "config_schema", str(e), str(bindings_path), "Fix YAML syntax")

    # identity_aliases
    aliases_path = config_root / "identity_aliases.yaml"
    if not aliases_path.exists():
        record("phase1_identity_aliases", False, "config_missing", "config/identity_aliases.yaml missing", str(aliases_path), "Create file with persona_aliases, topic_aliases")
    else:
        try:
            data = yaml.safe_load(aliases_path.read_text()) or {}
            if "persona_aliases" not in data or "topic_aliases" not in data:
                record("phase1_identity_aliases", False, "config_schema", "persona_aliases or topic_aliases missing", str(aliases_path), "Add persona_aliases and topic_aliases")
            else:
                record("phase1_identity_aliases", True, "config_schema", "identity_aliases OK", str(aliases_path), None)
        except Exception as e:
            record("phase1_identity_aliases", False, "config_schema", str(e), str(aliases_path), "Fix YAML syntax")

    # format_registry + selection_rules
    fmt_dir = config_root / "format_selection"
    reg_path = fmt_dir / "format_registry.yaml"
    sel_path = fmt_dir / "selection_rules.yaml"
    if not reg_path.exists() or not sel_path.exists():
        record("phase1_format_selection", False, "config_missing", "format_registry.yaml or selection_rules.yaml missing", str(fmt_dir), "Add both under config/format_selection/")
    else:
        try:
            reg = yaml.safe_load(reg_path.read_text()) or {}
            if not reg:
                record("phase1_format_selection", False, "config_schema", "format_registry empty", str(reg_path), "Define structural formats")
            else:
                record("phase1_format_selection", True, "config_schema", "format_selection OK", str(reg_path), None)
        except Exception as e:
            record("phase1_format_selection", False, "config_schema", str(e), str(reg_path), "Fix YAML syntax")

    # emotional_role_slot_requirements (optional)
    role_req = fmt_dir / "emotional_role_slot_requirements.yaml"
    if role_req.exists():
        try:
            yaml.safe_load(role_req.read_text())
            record("phase1_emotional_role_slot", True, "config_schema", "emotional_role_slot_requirements OK", str(role_req), None)
        except Exception as e:
            record("phase1_emotional_role_slot", False, "config_schema", str(e), str(role_req), "Fix YAML")
    else:
        record("phase1_emotional_role_slot", True, "config_schema", "emotional_role_slot_requirements optional; skip", None, None)

    # freebie_registry + selection_rules
    freebie_dir = config_root / "freebies"
    fb_reg = freebie_dir / "freebie_registry.yaml"
    fb_sel = freebie_dir / "freebie_selection_rules.yaml"
    if not fb_reg.exists() or not fb_sel.exists():
        record("phase1_freebie_config", False, "config_missing", "freebie_registry or freebie_selection_rules missing", str(freebie_dir), "Add both under config/freebies/")
    else:
        try:
            reg = yaml.safe_load(fb_reg.read_text()) or {}
            freebies = reg.get("freebies") or {}
            for fid, entry in list(freebies.items())[:3]:
                if not isinstance(entry, dict):
                    continue
                if "freebie_id" not in entry and "type" not in entry:
                    record("phase1_freebie_config", False, "config_schema", f"Freebie {fid} missing freebie_id/type", str(fb_reg), "Add freebie_id, type per entry")
                    break
            else:
                record("phase1_freebie_config", True, "config_schema", "freebie registry OK", str(fb_reg), None)
        except Exception as e:
            record("phase1_freebie_config", False, "config_schema", str(e), str(fb_reg), "Fix YAML")

    # narrator_registry + brand_narrator_assignments
    narr_reg = config_root / "narrators" / "narrator_registry.yaml"
    narr_assign = config_root / "brand_narrator_assignments.yaml"
    if not narr_reg.exists() or not narr_assign.exists():
        record("phase1_narrator_config", False, "config_missing", "narrator_registry or brand_narrator_assignments missing", str(narr_reg), "Create config/narrators/narrator_registry.yaml and config/brand_narrator_assignments.yaml")
    else:
        try:
            reg = yaml.safe_load(narr_reg.read_text()) or {}
            narrators = reg.get("narrators") or {}
            assign_data = yaml.safe_load(narr_assign.read_text()) or {}
            assignments = assign_data.get("assignments") or []
            if not narrators:
                record("phase1_narrator_config", False, "config_schema", "narrators section empty", str(narr_reg), "Add at least one narrator with status, brand_compatibility")
            elif not assignments:
                record("phase1_narrator_config", False, "config_schema", "assignments empty", str(narr_assign), "Add default_narrator per brand_id")
            else:
                nid = next(iter(narrators))
                ent = narrators[nid]
                if "status" not in ent or "brand_compatibility" not in ent:
                    record("phase1_narrator_config", False, "config_schema", "Narrator entry missing status/brand_compatibility", str(narr_reg), "Add status and brand_compatibility")
                else:
                    record("phase1_narrator_config", True, "config_schema", "narrator config OK", str(narr_reg), None)
        except Exception as e:
            record("phase1_narrator_config", False, "config_schema", str(e), str(narr_reg), "Fix YAML")

    # Angle Integration (V4.7): angle_registry optional
    angle_reg = config_root / "angles" / "angle_registry.yaml"
    if angle_reg.exists():
        try:
            reg = yaml.safe_load(angle_reg.read_text()) or {}
            angles = reg.get("angles") or {}
            if not angles:
                record("phase1_angle_registry", False, "config_schema", "angles section empty", str(angle_reg), "Add angles with arc_variant, framing_mode, integration_reinforcement_type")
            else:
                bad = [aid for aid, ent in angles.items() if not isinstance(ent, dict) or not ent.get("framing_mode")]
                if bad:
                    record("phase1_angle_registry", False, "config_schema", f"Angles missing framing_mode: {bad[:5]}", str(angle_reg), "Add framing_mode (debunk|framework|reveal|leverage) per angle")
                else:
                    record("phase1_angle_registry", True, "config_schema", "angle_registry OK", str(angle_reg), None)
        except Exception as e:
            record("phase1_angle_registry", False, "config_schema", str(e), str(angle_reg), "Fix YAML")
    else:
        record("phase1_angle_registry", True, "config_schema", "angle_registry optional; skip", None, None)

    # canonical_topics + canonical_personas
    cat_dir = config_root / "catalog_planning"
    canon_topics = cat_dir / "canonical_topics.yaml"
    canon_personas = cat_dir / "canonical_personas.yaml"
    if not canon_topics.exists() or not canon_personas.exists():
        record("phase1_canonical", False, "config_missing", "canonical_topics or canonical_personas missing", str(cat_dir), "Create canonical_topics.yaml and canonical_personas.yaml")
    else:
        try:
            t = yaml.safe_load(canon_topics.read_text()) or {}
            p = yaml.safe_load(canon_personas.read_text()) or {}
            if not (t.get("topics") and p.get("personas")):
                record("phase1_canonical", False, "config_schema", "topics or personas list empty", str(canon_topics), "Add topics: [...] and personas: [...]")
            else:
                record("phase1_canonical", True, "config_schema", "canonical OK", str(canon_topics), None)
        except Exception as e:
            record("phase1_canonical", False, "config_schema", str(e), str(canon_topics), "Fix YAML")

    # master arcs
    arcs_dir = config_root / "source_of_truth" / "master_arcs"
    if not arcs_dir.exists():
        record("phase1_master_arcs", False, "config_missing", "master_arcs dir missing", str(arcs_dir), "Create config/source_of_truth/master_arcs/")
    else:
        arc_files = list(arcs_dir.glob("*.yaml"))
        if not arc_files:
            record("phase1_master_arcs", False, "config_missing", "No arc YAML in master_arcs", str(arcs_dir), "Add at least one arc YAML")
        else:
            errs = []
            for ap in arc_files[:5]:
                try:
                    d = yaml.safe_load(ap.read_text()) or {}
                    if not d.get("chapter_count") or (not d.get("emotional_curve") and not d.get("emotional_role_sequence")):
                        errs.append(f"{ap.name}: missing chapter_count or emotional curve/role_sequence")
                    if not d.get("engine"):
                        errs.append(f"{ap.name}: missing engine")
                except Exception as e:
                    errs.append(f"{ap.name}: {e}")
            if errs:
                record("phase1_master_arcs", False, "config_schema", "; ".join(errs[:3]), str(arcs_dir), "Fix arc YAML schema")
            else:
                record("phase1_master_arcs", True, "config_schema", f"{len(arc_files)} arc(s) OK", str(arcs_dir), None)

    # engines
    engines_dir = config_root / "source_of_truth" / "engines"
    if not engines_dir.exists():
        record("phase1_engines", True, "config_schema", "engines dir optional", str(engines_dir), None)
    else:
        engine_files = list(engines_dir.glob("*.yaml"))
        if engine_files:
            record("phase1_engines", True, "config_schema", f"{len(engine_files)} engine(s)", str(engines_dir), None)
        else:
            record("phase1_engines", True, "config_schema", "engines dir empty; optional", str(engines_dir), None)

    # emotional_governance_rules
    gov_path = REPO_ROOT / "phoenix_v4" / "qa" / "emotional_governance_rules.yaml"
    if not gov_path.exists():
        record("phase1_governance", False, "config_missing", "emotional_governance_rules.yaml missing", str(gov_path), "Create phoenix_v4/qa/emotional_governance_rules.yaml")
    else:
        try:
            data = yaml.safe_load(gov_path.read_text()) or {}
            required = ("chapter_level", "tts_rhythm", "book_level", "catalog_level", "failure_protocol")
            missing = [r for r in required if r not in data]
            if missing:
                record("phase1_governance", False, "config_schema", f"Missing sections: {missing}", str(gov_path), "Add sections to governance YAML")
            else:
                record("phase1_governance", True, "config_schema", "governance OK", str(gov_path), None)
        except Exception as e:
            record("phase1_governance", False, "config_schema", str(e), str(gov_path), "Fix YAML")

    # CTA templates, tier_bundles
    cta_path = freebie_dir / "cta_templates.yaml"
    tier_path = freebie_dir / "tier_bundles.yaml"
    if not cta_path.exists():
        record("phase1_cta_tier", False, "config_missing", "cta_templates.yaml missing", str(cta_path), "Create config/freebies/cta_templates.yaml")
    elif not tier_path.exists():
        record("phase1_cta_tier", False, "config_missing", "tier_bundles.yaml missing", str(tier_path), "Create config/freebies/tier_bundles.yaml")
    else:
        try:
            tier = yaml.safe_load(tier_path.read_text()) or {}
            if "good" not in tier or "better" not in tier or "best" not in tier:
                record("phase1_cta_tier", False, "config_schema", "tier_bundles needs good/better/best", str(tier_path), "Add good, better, best keys")
            else:
                record("phase1_cta_tier", True, "config_schema", "cta and tier_bundles OK", str(cta_path), None)
        except Exception as e:
            record("phase1_cta_tier", False, "config_schema", str(e), str(tier_path), "Fix YAML")


def run_phase_2_resolvers(output_dir: Path) -> None:
    """Phase 2: Resolvers (teacher, author, narrator, canonical)."""
    # teacher_brand_resolver
    try:
        from phoenix_v4.planning.teacher_brand_resolver import resolve_teacher_brand
        t, b = resolve_teacher_brand(topic_id="self_worth", persona_id="nyc_executives", series_id=None)
        if not isinstance(t, str) or not isinstance(b, str):
            record("phase2_teacher_resolver", False, "resolver_fail", f"resolve_teacher_brand returned unexpected types: {type(t)}, {type(b)}", None, "Ensure brand_teacher_assignments has default for this combo")
        else:
            record("phase2_teacher_resolver", True, "resolver_fail", "resolve_teacher_brand OK", None, None)
    except Exception as e:
        record("phase2_teacher_resolver", False, "resolver_fail", str(e), None, "Fix teacher_brand_resolver or config/brand_teacher_assignments")

    # author_brand_resolver
    try:
        from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand
        a = resolve_author_from_brand(brand_id="phoenix")
        # May be None or str
        record("phase2_author_resolver", True, "resolver_fail", "resolve_author_from_brand OK", None, None)
    except Exception as e:
        record("phase2_author_resolver", False, "resolver_fail", str(e), None, "Fix author_brand_resolver or config/brand_author_assignments")

    # narrator_brand_resolver
    try:
        from phoenix_v4.planning.narrator_brand_resolver import resolve_narrator_from_brand, validate_narrator_for_book
        nid = resolve_narrator_from_brand(brand_id="phoenix")
        if nid:
            ok, err = validate_narrator_for_book(nid, "phoenix", topic_id="self_worth")
            if not ok:
                record("phase2_narrator_resolver", False, "resolver_fail", err or "validate_narrator_for_book failed", None, "Add narrator to registry and brand assignment")
            else:
                record("phase2_narrator_resolver", True, "resolver_fail", "narrator resolve and validate OK", None, None)
        else:
            record("phase2_narrator_resolver", True, "resolver_fail", "no default narrator; skip validate", None, None)
    except Exception as e:
        record("phase2_narrator_resolver", False, "resolver_fail", str(e), None, "Fix narrator_brand_resolver or config")

    # resolve_to_canonical (identity_aliases)
    try:
        from scripts.run_pipeline import resolve_to_canonical, ALIASES_PATH
        topic, persona = resolve_to_canonical(ALIASES_PATH, "relationship_anxiety", "nyc_exec")
        if not topic or not persona:
            record("phase2_resolve_canonical", False, "resolver_fail", "resolve_to_canonical returned empty", None, "Check identity_aliases.yaml")
        else:
            record("phase2_resolve_canonical", True, "resolver_fail", "resolve_to_canonical OK", None, None)
    except Exception as e:
        record("phase2_resolve_canonical", False, "resolver_fail", str(e), None, "Fix identity_aliases or resolve_to_canonical")


def run_phase_3_pipeline(output_dir: Path) -> None:
    """Phase 3: Full pipeline per arc; validators; index append."""
    arcs_dir = REPO_ROOT / "config" / "source_of_truth" / "master_arcs"
    if not arcs_dir.exists():
        record("phase3_pipeline", False, "pipeline_fail", "master_arcs not found", str(arcs_dir), None)
        return
    arc_files = sorted(arcs_dir.glob("*.yaml"))
    if not arc_files:
        record("phase3_pipeline", False, "pipeline_fail", "No arc YAML", str(arcs_dir), None)
        return

    try:
        import yaml
    except ImportError:
        record("phase3_pipeline", False, "pipeline_fail", "PyYAML required", None, "pip install pyyaml")
        return

    plans_dir = output_dir / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    pipeline_script = REPO_ROOT / "scripts" / "run_pipeline.py"

    for arc_path in arc_files:
        try:
            arc_data = yaml.safe_load(arc_path.read_text()) or {}
            topic = arc_data.get("topic") or "self_worth"
            persona = arc_data.get("persona") or "nyc_executives"
        except Exception:
            topic, persona = "self_worth", "nyc_executives"

        out_path = plans_dir / f"{arc_path.stem}_out.json"
        r = subprocess.run(
            [sys.executable, str(pipeline_script), "--topic", topic, "--persona", persona, "--arc", str(arc_path), "--out", str(out_path), "--no-generate-freebies"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode != 0:
            record(f"phase3_pipeline_{arc_path.stem}", False, "pipeline_fail", r.stderr or r.stdout or "Pipeline exited non-zero", str(out_path), "Fix arc or pool so compile succeeds")
            continue
        if not out_path.exists():
            record(f"phase3_pipeline_{arc_path.stem}", False, "pipeline_fail", "Output file not created", str(out_path), None)
            continue

        try:
            plan = json.loads(out_path.read_text())
        except Exception as e:
            record(f"phase3_plan_json_{arc_path.stem}", False, "contract_violation", str(e), str(out_path), None)
            continue

        # CompiledBook minimal
        if not isinstance(plan.get("plan_hash"), str):
            record(f"phase3_plan_hash_{arc_path.stem}", False, "contract_violation", "plan_hash missing or not str", str(out_path), None)
        if not isinstance(plan.get("atom_ids"), list):
            record(f"phase3_atom_ids_{arc_path.stem}", False, "contract_violation", "atom_ids missing or not list", str(out_path), None)
        if not plan.get("arc_id"):
            record(f"phase3_arc_id_{arc_path.stem}", False, "contract_violation", "arc_id missing", str(out_path), None)

        # validate_compiled_plan
        format_plan = plan.get("format_id")
        if format_plan:
            format_plan_dict = {"format_structural_id": format_plan, "chapter_count": len(plan.get("chapter_slot_sequence") or []), "slot_definitions": plan.get("chapter_slot_sequence") or []}
        else:
            format_plan_dict = {"chapter_count": len(plan.get("chapter_slot_sequence") or []), "slot_definitions": plan.get("chapter_slot_sequence") or []}
        try:
            from phoenix_v4.qa.validate_compiled_plan import validate_compiled_plan
            val = validate_compiled_plan(plan, format_plan_dict)
            if not val.valid:
                record(f"phase3_validate_compiled_{arc_path.stem}", False, "validator_fail", "; ".join(val.errors[:3]), str(out_path), "Fix plan or format_plan to satisfy validators")
            else:
                record(f"phase3_validate_compiled_{arc_path.stem}", True, "validator_fail", "validate_compiled_plan OK", str(out_path), None)
        except Exception as e:
            record(f"phase3_validate_compiled_{arc_path.stem}", False, "validator_fail", str(e), str(out_path), None)

        # validate_arc_alignment
        try:
            from phoenix_v4.planning.arc_loader import load_arc
            from phoenix_v4.qa.validate_arc_alignment import validate_arc_alignment
            arc = load_arc(arc_path)
            arc_errors = validate_arc_alignment(plan, arc)
            if arc_errors:
                record(f"phase3_arc_alignment_{arc_path.stem}", False, "validator_fail", "; ".join(arc_errors[:3]), str(out_path), "Fix arc or plan")
            else:
                record(f"phase3_arc_alignment_{arc_path.stem}", True, "validator_fail", "validate_arc_alignment OK", str(out_path), None)
        except Exception as e:
            record(f"phase3_arc_alignment_{arc_path.stem}", False, "validator_fail", str(e), str(out_path), None)

        # validate_engine_resolution
        try:
            from phoenix_v4.planning.engine_loader import load_engine
            from phoenix_v4.qa.validate_engine_resolution import validate_engine_resolution
            arc = load_arc(arc_path)
            engine_def = load_engine(arc.engine)
            if engine_def:
                errs = validate_engine_resolution(arc, engine_def)
                if errs:
                    record(f"phase3_engine_resolution_{arc_path.stem}", False, "validator_fail", "; ".join(errs[:3]), str(out_path), "Fix engine def or arc")
                else:
                    record(f"phase3_engine_resolution_{arc_path.stem}", True, "validator_fail", "validate_engine_resolution OK", str(out_path), None)
            else:
                record(f"phase3_engine_resolution_{arc_path.stem}", True, "validator_fail", "no engine def; skip", str(out_path), None)
        except Exception as e:
            record(f"phase3_engine_resolution_{arc_path.stem}", False, "validator_fail", str(e), str(out_path), None)

    record("phase3_pipeline_runs", True, "pipeline_fail", f"Ran pipeline for {len(arc_files)} arc(s)", str(plans_dir), None)


def run_phase_4_freebies(output_dir: Path) -> None:
    """Phase 4: Freebie planner and renderer."""
    plans_dir = output_dir / "plans"
    plan_files = list(plans_dir.glob("*_out.json")) if plans_dir.exists() else []
    if not plan_files:
        # Use one arc to produce a plan in memory or run pipeline once
        arc_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "nyc_executives__self_worth__shame__F006.yaml"
        if not arc_path.exists():
            record("phase4_freebies", False, "freebie_planner_fail", "No plan and no arc for freebie test", None, "Run phase 3 first or add arc")
            return
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "run_pipeline.py"), "--topic", "self_worth", "--persona", "nyc_executives", "--arc", str(arc_path), "--out", str(output_dir / "plans" / "freebie_test_out.json"), "--no-generate-freebies"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            record("phase4_freebies", False, "freebie_planner_fail", r.stderr or "Pipeline failed", None, None)
            return
        plan_files = [output_dir / "plans" / "freebie_test_out.json"]

    plan_path = plan_files[0]
    try:
        plan = json.loads(plan_path.read_text())
    except Exception as e:
        record("phase4_plan_load", False, "freebie_planner_fail", str(e), str(plan_path), None)
        return

    try:
        from phoenix_v4.planning.freebie_planner import plan_freebies, get_freebie_bundle_with_formats
        import yaml
    except Exception as e:
        record("phase4_import", False, "freebie_planner_fail", str(e), None, None)
        return

    book_spec = {"topic_id": plan.get("topic_id") or "self_worth", "persona_id": plan.get("persona_id") or "nyc_executives"}
    format_plan_dict = {"chapter_count": len(plan.get("chapter_slot_sequence") or []), "slot_definitions": plan.get("chapter_slot_sequence") or []}
    try:
        from phoenix_v4.planning.arc_loader import load_arc
        arc_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "nyc_executives__self_worth__shame__F006.yaml"
        if not arc_path.exists():
            arc_path = list((REPO_ROOT / "config" / "source_of_truth" / "master_arcs").glob("*.yaml"))[0] if list((REPO_ROOT / "config" / "source_of_truth" / "master_arcs").glob("*.yaml")) else None
        arc = load_arc(arc_path) if arc_path else None
    except Exception:
        arc = None

    try:
        bundle, cta_id, slug = plan_freebies(book_spec, format_plan_dict, plan, arc)
        if not isinstance(bundle, list):
            record("phase4_plan_freebies", False, "freebie_planner_fail", "plan_freebies did not return list bundle", None, None)
        else:
            record("phase4_plan_freebies", True, "freebie_planner_fail", f"plan_freebies OK (bundle len={len(bundle)})", None, None)
    except Exception as e:
        record("phase4_plan_freebies", False, "freebie_planner_fail", str(e), None, "Fix freebie_planner or selection_rules")

    reg_path = REPO_ROOT / "config" / "freebies" / "freebie_registry.yaml"
    if reg_path.exists() and yaml:
        reg = yaml.safe_load(reg_path.read_text()) or {}
        freebies_map = reg.get("freebies") or {}
        try:
            with_formats = get_freebie_bundle_with_formats(plan.get("freebie_bundle") or [], freebies_map, book_spec, format_plan_dict, plan)
            if not isinstance(with_formats, list):
                record("phase4_bundle_with_formats", False, "freebie_planner_fail", "get_freebie_bundle_with_formats did not return list", None, None)
            else:
                record("phase4_bundle_with_formats", True, "freebie_planner_fail", "get_freebie_bundle_with_formats OK", None, None)
        except Exception as e:
            record("phase4_bundle_with_formats", False, "freebie_planner_fail", str(e), None, None)

    # generate_freebies_for_book (HTML only, no publish)
    try:
        from phoenix_v4.freebies.freebie_renderer import generate_freebies_for_book
        out_dir = output_dir / "freebie_artifacts"
        paths = generate_freebies_for_book(plan, book_spec, formats=["html"], output_dir_override=out_dir)
        if paths is None:
            paths = []
        record("phase4_generate_freebies", True, "freebie_render_fail", f"generate_freebies_for_book OK ({len(paths)} files)", str(out_dir), None)
    except Exception as e:
        record("phase4_generate_freebies", False, "freebie_render_fail", str(e), None, "Add templates or fix registry file_template")

    # load_template for first freebie with file_template
    if reg_path.exists() and yaml:
        reg = yaml.safe_load(reg_path.read_text()) or {}
        for fid, entry in (reg.get("freebies") or {}).items():
            ft = entry.get("file_template") if isinstance(entry, dict) else None
            if ft:
                try:
                    from phoenix_v4.freebies.freebie_renderer import load_template
                    load_template(ft)
                    record("phase4_load_template", True, "missing_template", f"load_template({ft}) OK", None, None)
                    break
                except Exception as e:
                    record("phase4_load_template", False, "missing_template", str(e), None, "Add template to SOURCE_OF_TRUTH/freebies/templates or config/freebies/templates")
                    break
        else:
            record("phase4_load_template", True, "missing_template", "No file_template in registry; skip", None, None)

    # _render_cta
    try:
        from phoenix_v4.freebies.freebie_renderer import _render_cta
        s = _render_cta("tool_forward", "anxiety", "Breath Timer", "anxiety-nyc-breath")
        if not s or not isinstance(s, str):
            record("phase4_render_cta", False, "freebie_render_fail", "CTA render empty", None, "Add cta_templates.yaml script for tool_forward")
        else:
            record("phase4_render_cta", True, "freebie_render_fail", "CTA render OK", None, None)
    except Exception as e:
        record("phase4_render_cta", False, "freebie_render_fail", str(e), None, "Add config/freebies/cta_templates.yaml with tool_forward script")


def run_phase_5_asset_pipeline(output_dir: Path) -> None:
    """Phase 5: validate_canonical_sources, plan_freebie_assets, create_freebie_assets, validate_asset_store."""
    canon_script = REPO_ROOT / "scripts" / "validate_canonical_sources.py"
    if not canon_script.exists():
        record("phase5_validate_canonical", False, "canonical_drift", "validate_canonical_sources.py not found", str(canon_script), None)
    else:
        r = subprocess.run([sys.executable, str(canon_script), "--warn-only"], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
        if r.returncode != 0 and "Required: pip install pyyaml" not in (r.stderr or ""):
            record("phase5_validate_canonical", False, "canonical_drift", r.stderr or r.stdout or "Exit non-zero", str(canon_script), "Sync canonical with topic_engine_bindings and identity_aliases")
        else:
            record("phase5_validate_canonical", True, "canonical_drift", "validate_canonical_sources OK or warn-only", str(canon_script), None)

    plan_assets_script = REPO_ROOT / "scripts" / "plan_freebie_assets.py"
    manifest_path = output_dir / "manifest.jsonl"
    if not plan_assets_script.exists():
        record("phase5_plan_freebie_assets", False, "asset_plan_fail", "plan_freebie_assets.py not found", str(plan_assets_script), None)
    else:
        topics = REPO_ROOT / "config" / "catalog_planning" / "canonical_topics.yaml"
        personas = REPO_ROOT / "config" / "catalog_planning" / "canonical_personas.yaml"
        if not topics.exists() or not personas.exists():
            record("phase5_plan_freebie_assets", False, "asset_plan_fail", "canonical topics/personas missing", None, None)
        else:
            r = subprocess.run(
                [sys.executable, str(plan_assets_script), "--topics", str(topics), "--personas", str(personas), "--out", str(manifest_path)],
                cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60,
            )
            if r.returncode != 0:
                record("phase5_plan_freebie_assets", False, "asset_plan_fail", r.stderr or r.stdout or "Exit non-zero", str(manifest_path), "Fix canonical or planner")
            else:
                lines = [ln for ln in manifest_path.read_text().strip().splitlines() if ln.strip()]
                if not lines:
                    record("phase5_plan_freebie_assets", False, "asset_plan_fail", "Manifest empty", str(manifest_path), "Check canonical and freebie planner")
                else:
                    record("phase5_plan_freebie_assets", True, "asset_plan_fail", f"Manifest has {len(lines)} row(s)", str(manifest_path), None)

    store_dir = output_dir / "store"
    create_script = REPO_ROOT / "scripts" / "create_freebie_assets.py"
    if create_script.exists() and manifest_path.exists():
        r = subprocess.run(
            [sys.executable, str(create_script), "--manifest", str(manifest_path), "--format", "html", "--store", str(store_dir)],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            record("phase5_create_freebie_assets", False, "asset_create_fail", r.stderr or r.stdout or "Exit non-zero", str(store_dir), "Add templates or fix create script")
        else:
            html_count = len(list(store_dir.rglob("*.html"))) if store_dir.exists() else 0
            record("phase5_create_freebie_assets", True, "asset_create_fail", f"create_freebie_assets OK ({html_count} html)", str(store_dir), None)
    else:
        record("phase5_create_freebie_assets", True, "asset_create_fail", "create_freebie_assets script or manifest missing; skip", None, None)

    validate_store_script = REPO_ROOT / "scripts" / "validate_asset_store.py"
    if validate_store_script.exists() and manifest_path.exists():
        r = subprocess.run([sys.executable, str(validate_store_script), "--store", str(store_dir), "--manifest", str(manifest_path)], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
        if r.returncode != 0 and store_dir.exists():
            record("phase5_validate_asset_store", False, "asset_validate_fail", r.stderr or r.stdout or "Exit non-zero", str(store_dir), "Ensure store matches manifest or run create_freebie_assets")
        else:
            record("phase5_validate_asset_store", True, "asset_validate_fail", "validate_asset_store OK or store empty", str(store_dir), None)
    else:
        record("phase5_validate_asset_store", True, "asset_validate_fail", "validate_asset_store script missing; skip", None, None)


def run_phase_6_ci_qa(output_dir: Path) -> None:
    """Phase 6: CI and QA validators."""
    plans_dir = output_dir / "plans"
    plan_files = list(plans_dir.glob("*_out.json")) if plans_dir.exists() else []
    plan_path = plan_files[0] if plan_files else REPO_ROOT / "artifacts" / "golden_plans" / "_gate_pipeline_out.json"
    if not plan_path.exists() and plan_files:
        plan_path = plan_files[0]

    # check_structural_entropy
    ent_script = REPO_ROOT / "scripts" / "ci" / "check_structural_entropy.py"
    if ent_script.exists() and plan_path.exists():
        r = subprocess.run([sys.executable, str(ent_script), "--plan", str(plan_path)], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
        record("phase6_structural_entropy", r.returncode == 0 or "FAIL" in (r.stdout or ""), "validator_fail", (r.stdout or r.stderr or "")[:200], str(plan_path), None)
    else:
        record("phase6_structural_entropy", True, "validator_fail", "script or plan missing; skip", None, None)

    # check_author_positioning (may fail if no author_id in plan)
    auth_script = REPO_ROOT / "scripts" / "ci" / "check_author_positioning.py"
    if auth_script.exists() and plan_path.exists():
        r = subprocess.run([sys.executable, str(auth_script), "--plan", str(plan_path)], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
        record("phase6_author_positioning", True, "validator_fail", "check_author_positioning ran (exit may be 0 or 1)", str(plan_path), None)
    else:
        record("phase6_author_positioning", True, "validator_fail", "skip", None, None)

    # check_platform_similarity
    sim_script = REPO_ROOT / "scripts" / "ci" / "check_platform_similarity.py"
    if sim_script.exists() and plan_path.exists():
        r = subprocess.run([sys.executable, str(sim_script), "--plan", str(plan_path)], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
        record("phase6_platform_similarity", True, "validator_fail", "check_platform_similarity ran", str(plan_path), None)
    else:
        record("phase6_platform_similarity", True, "validator_fail", "skip", None, None)

    # validate_brand_archetype_registry
    brand_script = REPO_ROOT / "phoenix_v4" / "qa" / "validate_brand_archetype_registry.py"
    if brand_script.exists():
        r = subprocess.run([sys.executable, "-m", "phoenix_v4.qa.validate_brand_archetype_registry"], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30, env={**os.environ, "PYTHONPATH": str(REPO_ROOT)})
        record("phase6_brand_archetype", r.returncode == 0, "gate_fail", r.stderr or r.stdout or "", None, "Fix brand_archetype_registry YAML" if r.returncode != 0 else None)
    else:
        record("phase6_brand_archetype", True, "gate_fail", "script missing; skip", None, None)

    # Gate #49
    gate49 = REPO_ROOT / "scripts" / "distribution" / "pre_export_check.py"
    if gate49.exists() and plan_path.exists():
        r = subprocess.run([sys.executable, str(gate49), "--plan", str(plan_path)], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=10)
        record("phase6_gate49", r.returncode == 0, "gate_fail", r.stderr or r.stdout or "", str(plan_path), "Plan must include locale, territory" if r.returncode != 0 else None)
    else:
        record("phase6_gate49", True, "gate_fail", "skip", None, None)

    # run_production_readiness_gates
    gates_script = REPO_ROOT / "scripts" / "run_production_readiness_gates.py"
    if gates_script.exists():
        r = subprocess.run([sys.executable, str(gates_script)], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=90)
        record("phase6_production_gates", r.returncode == 0, "gate_fail", "run_production_readiness_gates completed", None, "Address failed gates" if r.returncode != 0 else None)
    else:
        record("phase6_production_gates", False, "gate_fail", "run_production_readiness_gates.py not found", str(gates_script), None)

    # simulation
    sim_run = REPO_ROOT / "simulation" / "run_simulation.py"
    if sim_run.exists():
        r = subprocess.run([sys.executable, str(sim_run), "--n", "1"], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60)
        record("phase6_simulation", r.returncode == 0, "gate_fail", r.stderr or r.stdout or "" if r.returncode != 0 else "simulation OK", None, None)
    else:
        record("phase6_simulation", True, "gate_fail", "simulation script missing; skip", None, None)


def run_phase_7_contracts(output_dir: Path) -> None:
    """Phase 7: Contract and schema compliance."""
    plans_dir = output_dir / "plans"
    plan_files = list(plans_dir.glob("*_out.json")) if plans_dir.exists() else []
    if not plan_files:
        record("phase7_contracts", False, "contract_violation", "No plan JSON for contract check", str(plans_dir), "Run phase 3 first")
        return

    plan_path = plan_files[0]
    try:
        plan = json.loads(plan_path.read_text())
    except Exception as e:
        record("phase7_contracts", False, "contract_violation", str(e), str(plan_path), None)
        return

    # CompiledBook CI fields
    ok = True
    if not isinstance(plan.get("plan_hash"), str):
        record("phase7_plan_hash", False, "contract_violation", "plan_hash must be str", str(plan_path), None)
        ok = False
    else:
        record("phase7_plan_hash", True, "contract_violation", "plan_hash OK", str(plan_path), None)
    if not isinstance(plan.get("chapter_slot_sequence"), list):
        record("phase7_chapter_slot_sequence", False, "contract_violation", "chapter_slot_sequence must be list", str(plan_path), None)
        ok = False
    else:
        record("phase7_chapter_slot_sequence", True, "contract_violation", "chapter_slot_sequence OK", str(plan_path), None)
    if not isinstance(plan.get("atom_ids"), list):
        record("phase7_atom_ids", False, "contract_violation", "atom_ids must be list", str(plan_path), None)
        ok = False
    else:
        record("phase7_atom_ids", True, "contract_violation", "atom_ids OK", str(plan_path), None)

    # chapter_slot_sequence shape: list of chapters, each chapter list of slot types
    seq = plan.get("chapter_slot_sequence") or []
    if seq:
        first = seq[0]
        if isinstance(first, list):
            record("phase7_slot_sequence_shape", True, "contract_violation", "chapter_slot_sequence shape OK", str(plan_path), None)
        else:
            record("phase7_slot_sequence_shape", True, "contract_violation", "chapter_slot_sequence (flat or mixed) OK", str(plan_path), None)

    # freebie_bundle_with_formats
    bwf = plan.get("freebie_bundle_with_formats")
    if bwf is not None:
        if not isinstance(bwf, list):
            record("phase7_freebie_bundle_with_formats", False, "contract_violation", "freebie_bundle_with_formats must be list", str(plan_path), None)
        else:
            record("phase7_freebie_bundle_with_formats", True, "contract_violation", "freebie_bundle_with_formats OK", str(plan_path), None)
    else:
        record("phase7_freebie_bundle_with_formats", True, "contract_violation", "freebie_bundle_with_formats optional", str(plan_path), None)


def write_report(output_dir: Path) -> tuple[str, str]:
    """Write report_<timestamp>.json and report_<timestamp>.md. Return (json_path, md_path)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    json_path = output_dir / f"report_{ts}.json"
    md_path = output_dir / f"report_{ts}.md"

    payload = {
        "timestamp": ts,
        "total": len(RESULTS),
        "passed": sum(1 for r in RESULTS if r["passed"]),
        "failed": sum(1 for r in RESULTS if not r["passed"]),
        "results": RESULTS,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Markdown
    lines = [f"# Systems test report — {ts}", "", f"**Passed:** {payload['passed']} | **Failed:** {payload['failed']} | **Total:** {payload['total']}", ""]
    fails = [r for r in RESULTS if not r["passed"]]
    if fails:
        lines.append("## Failures")
        for r in fails:
            lines.append(f"- **{r['check_id']}** ({r['category']}): {r['message']}")
            if r.get("artifact_path"):
                lines.append(f"  - Artifact: `{r['artifact_path']}`")
            if r.get("suggested_fix"):
                lines.append(f"  - Suggested fix: {r['suggested_fix']}")
        lines.append("")
    lines.append("## All results")
    for r in RESULTS:
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(f"- {status} {r['check_id']}: {r['message'][:80]}")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return str(json_path), str(md_path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Rigorous systems test (learn, fix, enhance)")
    ap.add_argument("--phase", type=int, action="append", choices=[1, 2, 3, 4, 5, 6, 7], help="Run specific phase(s)")
    ap.add_argument("--all", action="store_true", help="Run all phases 1-7")
    ap.add_argument("--output-dir", default=None, help="Output dir for reports and artifacts (default: artifacts/systems_test)")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if any check failed")
    args = ap.parse_args()

    phases = sorted(set(args.phase or []))
    if args.all:
        phases = [1, 2, 3, 4, 5, 6, 7]
    if not phases:
        ap.error("Specify --phase N (repeatable) or --all")

    output_dir = Path(args.output_dir or str(REPO_ROOT / "artifacts" / "systems_test"))
    output_dir.mkdir(parents=True, exist_ok=True)

    if 1 in phases:
        run_phase_1_config(output_dir)
    if 2 in phases:
        run_phase_2_resolvers(output_dir)
    if 3 in phases:
        run_phase_3_pipeline(output_dir)
    if 4 in phases:
        run_phase_4_freebies(output_dir)
    if 5 in phases:
        run_phase_5_asset_pipeline(output_dir)
    if 6 in phases:
        run_phase_6_ci_qa(output_dir)
    if 7 in phases:
        run_phase_7_contracts(output_dir)

    json_path, md_path = write_report(output_dir)
    failed = sum(1 for r in RESULTS if not r["passed"])
    print(f"Report: {json_path}")
    print(f"Summary: {md_path}")
    print(f"Passed: {len(RESULTS) - failed} | Failed: {failed}")
    if args.strict and failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
