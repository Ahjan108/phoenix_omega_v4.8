#!/usr/bin/env python3
"""
Full pipeline: Stage 1 (catalog) -> Stage 2 (format selector) -> Stage 3 (assembly compiler). Arc-First: --arc required.
Usage:
  python3 scripts/run_pipeline.py --topic self_worth --persona nyc_executives --arc config/source_of_truth/master_arcs/nyc_executives__self_worth__shame__F006.yaml --out artifacts/out.plan.json
  python3 scripts/run_pipeline.py --input example_input.yaml --arc path/to/arc.yaml --out out.plan.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None

ALIASES_PATH = REPO_ROOT / "config" / "identity_aliases.yaml"


def resolve_to_canonical(aliases_path: Path, topic_id: str, persona_id: str) -> tuple[str, str]:
    """Resolve topic_id and persona_id to canonical (atoms dir names). Stage 3 receives only canonical IDs."""
    if not aliases_path.exists() or not yaml:
        return topic_id, persona_id
    data = yaml.safe_load(aliases_path.read_text()) or {}
    persona_aliases = data.get("persona_aliases") or {}
    topic_aliases = data.get("topic_aliases") or {}
    canonical_persona = persona_aliases.get(persona_id, persona_id)
    canonical_topic = topic_aliases.get(topic_id, topic_id)
    return canonical_topic, canonical_persona


def _upsert_plan_index_row(index_path: Path, row: dict) -> None:
    """
    Maintain one plan-row per book_id in artifacts/freebies/index.jsonl.
    Non-plan rows (e.g., artifact logs) are preserved.
    """
    rows: list[dict] = []
    if index_path.exists():
        for ln in index_path.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            try:
                rows.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
    book_id = str(row.get("book_id") or "")
    kept = []
    for r in rows:
        is_plan_row = isinstance(r, dict) and "freebie_bundle" in r
        same_book = str(r.get("book_id") or "") == book_id
        if is_plan_row and same_book:
            continue
        kept.append(r)
    kept.append(row)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="BookSpec -> FormatPlan -> CompiledBook")
    ap.add_argument("--topic", default=None, help="Topic ID (e.g. relationship_anxiety)")
    ap.add_argument("--persona", default=None, help="Persona ID (e.g. nyc_exec)")
    ap.add_argument("--installment", type=int, default=None, help="Installment number")
    ap.add_argument("--series", default=None, help="Series ID")
    ap.add_argument(
        "--angle",
        type=str,
        default=None,
        help=(
            "Angle ID for this book (e.g. 'at_work', 'public_speaking'). "
            "If not supplied, angle is derived from topic + persona via series config. "
            "Required for deterministic naming engine output."
        ),
    )
    ap.add_argument("--seed", default="pipeline_seed_001", help="Determinism seed")
    ap.add_argument("--runtime-format", default=None, help="Force Stage 2 runtime (e.g. standard_book for 12 chapters)")
    ap.add_argument("--structural-format", default=None, help="Force Stage 2 structural format (e.g. F006 for 8-12 chapters)")
    ap.add_argument(
        "--output-format",
        default=None,
        help=(
            "Modular output format id (freeze mode). "
            "Examples: five_min_practice, pocket_guide, ten_things_to_do, symptom_to_action_atlas, "
            "daily_text_audio_companion, crisis_cards, weekly_challenge_pack, faq_audiobook, myth_vs_mechanism, protocol_library"
        ),
    )
    ap.add_argument(
        "--disable-v4-freeze",
        action="store_true",
        help="Disable modular V4 freeze for this run and allow legacy structural/runtime format selection.",
    )
    ap.add_argument("--input", default=None, help="YAML file with topic_id, persona_id, installment_number (Stage 2 input)")
    ap.add_argument("--arc", required=True, help="Path to Master Arc YAML (required; no arc = no compile)")
    ap.add_argument("--teacher", default=None, help="Teacher id for Teacher Mode (validated against teacher_persona_matrix)")
    ap.add_argument("--author", default=None, help="Author id (pen-name; resolved from author_registry, sets author_positioning_profile)")
    ap.add_argument("--narrator", default=None, help="Narrator id (resolved from brand_narrator_assignments when not supplied; Writer Spec §23.5)")
    ap.add_argument("--out", default=None, help="Write CompiledBook JSON here")
    ap.add_argument("--generate-freebies", action="store_true", help="Generate HTML freebie artifacts (public/free/<slug>/)")
    ap.add_argument("--no-generate-freebies", action="store_true", help="Disable freebie HTML generation when writing plan (default: generate when --out)")
    ap.add_argument("--no-update-freebie-index", action="store_true", help="Do not upsert plan row into artifacts/freebies/index.jsonl (use for test runs; DoD freebies governance)")
    ap.add_argument("--formats", default=None, help="Comma-separated freebie formats: html,pdf,epub,mp3 (default: html, or html+pdf if store has assets)")
    ap.add_argument("--skip-audio", action="store_true", help="Do not include mp3 in freebie formats")
    ap.add_argument("--publish-dir", default=None, help="Copy freebies to this dir for public/free (e.g. public/free)")
    ap.add_argument("--asset-store", default=None, help="Asset store root to copy pre-created assets from (e.g. artifacts/freebie_assets/store)")
    ap.add_argument("--render-book", action="store_true", help="Stage 6: render plan to prose (txt) after writing plan")
    ap.add_argument("--render-formats", default="txt", help="Comma-separated book output formats (default: txt)")
    ap.add_argument("--render-dir", default=None, help="Output dir for rendered book (default: artifacts/rendered/<plan_id>)")
    ap.add_argument("--skip-word-count-gate", action="store_true", help="Bypass word count minimum gate (use when content density work is in progress)")
    ap.add_argument(
        "--enforce-book-pass-gate",
        action="store_true",
        help="Run book-pass quality gate (claim progression, non-shuffleability, ending transformation) and fail on errors",
    )
    ap.add_argument(
        "--ei-v2-compare",
        action="store_true",
        help="Run EI V2 AI techniques in parallel with V1 and produce comparison report (artifacts/ei_v2/)",
    )
    ap.add_argument("--atoms-root", default=None, help="Atoms root (e.g. atoms/zh-TW). Default: repo atoms/")
    ap.add_argument(
        "--atoms-model",
        choices=["legacy", "cluster"],
        default=None,
        help="Atoms model: legacy (persona-specific) or cluster (core+overlay). Precedence: CLI > spec > config (legacy_personas).",
    )
    args = ap.parse_args()
    # V4 freeze settings: restrict pipeline outputs to modular formats unless explicitly disabled.
    from pearl_prime.modular_format_freeze import (
        apply_output_format_to_plan,
        load_freeze_settings,
        require_valid_output_format,
    )
    freeze_settings = load_freeze_settings()
    freeze_enabled = bool(freeze_settings.enabled and not args.disable_v4_freeze)

    if freeze_enabled and (args.structural_format or args.runtime_format):
        print(
            "Error: --structural-format/--runtime-format are blocked while V4 freeze is enabled. "
            "Use --output-format with modular formats.",
            file=sys.stderr,
        )
        return 1

    # Resolve input: CLI or YAML
    topic_id = args.topic
    persona_id = args.persona
    installment_number = args.installment
    series_id = args.series
    angle_id = args.angle
    seed = args.seed
    input_atoms_model = None  # from --input YAML when present
    if args.input:
        p = Path(args.input)
        if not p.exists():
            print(f"Error: input file not found: {p}", file=sys.stderr)
            return 1
        data = yaml.safe_load(p.read_text()) if yaml else {}
        topic_id = topic_id or data.get("topic_id", "relationship_anxiety")
        persona_id = persona_id or data.get("persona_id", "nyc_exec")
        installment_number = installment_number if installment_number is not None else data.get("installment_number", 1)
        series_id = series_id if series_id is not None else data.get("series_id")
        if angle_id is None:
            angle_id = data.get("angle_id")
        seed = data.get("seed", seed)
        if data.get("atoms_model") in ("legacy", "cluster"):
            input_atoms_model = data["atoms_model"]

    if not topic_id or not persona_id:
        print("Error: need --topic and --persona (or --input YAML with topic_id, persona_id)", file=sys.stderr)
        return 1

    arc_path = Path(args.arc)
    # Angle Integration (V4.7): resolve arc path from angle when angle_id in registry with arc_path
    if angle_id:
        from phoenix_v4.planning.angle_resolver import resolve_arc_path as angle_resolve_arc_path
        arc_path = angle_resolve_arc_path(angle_id, arc_path, repo_root=REPO_ROOT)
    if not arc_path.exists():
        print(f"Error: arc file not found: {arc_path}", file=sys.stderr)
        return 1

    # Load arc early so we can align format plan to arc chapter_count (Arc-First)
    from phoenix_v4.planning.arc_loader import load_arc
    arc = load_arc(arc_path)

    requested_teacher = (args.teacher or "").strip() or None
    from phoenix_v4.planning.teacher_brand_resolver import resolve_teacher_brand
    _, resolved_brand = resolve_teacher_brand(
        topic_id=topic_id,
        persona_id=persona_id,
        series_id=series_id,
    )
    teacher_id = requested_teacher or "default_teacher"
    brand_id = resolved_brand
    if teacher_id and teacher_id != "default_teacher":
        from phoenix_v4.planning.teacher_matrix import load_teacher_matrix, validate_teacher_assignment
        matrix = load_teacher_matrix()
        if matrix:
            try:
                validate_teacher_assignment(
                    matrix=matrix,
                    teacher_id=teacher_id,
                    persona_id=persona_id,
                    engine_id=getattr(arc, "engine", None),
                    locale_key=None,
                )
            except ValueError as e:
                print(f"Teacher assignment invalid: {e}", file=sys.stderr)
                return 1

    # Resolve author from brand when --author not supplied (brand_author_assignments.yaml)
    author_id = (args.author or "").strip() or None
    if author_id is None:
        from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand
        author_id = resolve_author_from_brand(
            brand_id=brand_id,
            topic_id=topic_id,
            persona_id=persona_id,
            series_id=series_id,
        )

    # Resolve narrator from brand when --narrator not supplied (brand_narrator_assignments.yaml)
    narrator_id = (args.narrator or "").strip() or None
    if narrator_id is None:
        from phoenix_v4.planning.narrator_brand_resolver import resolve_narrator_from_brand
        narrator_id = resolve_narrator_from_brand(brand_id=brand_id)
    if narrator_id:
        from phoenix_v4.planning.narrator_brand_resolver import validate_narrator_for_book
        ok, err = validate_narrator_for_book(narrator_id, brand_id, topic_id=topic_id)
        if not ok:
            print(f"Error: narrator validation failed: {err}", file=sys.stderr)
            return 1

    # Tuple viability preflight (hard entry gate; before Stage 1). No override.
    from phoenix_v4.gates.check_tuple_viability import check_tuple_viability
    teacher_mode = bool(teacher_id and teacher_id != "default_teacher")
    viability = check_tuple_viability(
        persona=arc.persona,
        topic=arc.topic,
        engine=arc.engine,
        format_id=arc.format,
        repo_root=REPO_ROOT,
        teacher_mode=teacher_mode,
        teacher_id=teacher_id if teacher_mode else None,
        arc=arc,
        brand_id=brand_id,
    )
    if viability.status != "PASS":
        for e in viability.errors:
            print(f"Tuple viability: {e}", file=sys.stderr)
        return 1

    # Stage 1: BookSpec (author_id, narrator_id optional)
    from phoenix_v4.planning.catalog_planner import AtomsModel, CatalogPlanner, BookSpec
    planner = CatalogPlanner()
    teacher_mode = bool(teacher_id and teacher_id != "default_teacher")
    spec_atoms_model = AtomsModel(input_atoms_model) if input_atoms_model in ("legacy", "cluster") else None
    book_spec = planner.produce_single(
        topic_id=topic_id,
        persona_id=persona_id,
        teacher_id=teacher_id,
        brand_id=brand_id,
        seed=seed,
        series_id=series_id,
        installment_number=installment_number,
        angle_id=angle_id,
        author_id=author_id,
        narrator_id=narrator_id,
        teacher_mode=teacher_mode,
        atoms_model=spec_atoms_model,
    )

    if book_spec.angle_id.endswith("_general"):
        import warnings
        warnings.warn(
            f"angle_id resolved to fallback '{book_spec.angle_id}' for "
            f"topic='{topic_id}', persona='{persona_id}'. "
            f"Naming engine will produce a less-specific title. "
            f"Pass --series <id> or --angle <id> for a precise angle.",
            UserWarning,
            stacklevel=2,
        )

    # Stage 2: FormatPlan
    from phoenix_v4.planning.format_selector import FormatSelector
    selector = FormatSelector()
    constraints = {}
    if args.runtime_format:
        constraints["force_runtime_format"] = args.runtime_format
    if args.structural_format:
        constraints["force_structural_format"] = args.structural_format
    format_plan = selector.select_format(
        topic_id=topic_id,
        persona_id=persona_id,
        installment_number=installment_number,
        series_id=series_id,
        constraints=constraints or None,
    )

    # Resolve aliases before Stage 3 (Canonical §3.0). Stage 3 only sees canonical IDs.
    canonical_topic, canonical_persona = resolve_to_canonical(ALIASES_PATH, topic_id, persona_id)
    book_spec_for_compiler = {**book_spec.to_dict(), "topic_id": canonical_topic, "persona_id": canonical_persona}

    # atoms_model: precedence 1) CLI --atoms-model 2) book spec 3) derive from config (legacy_personas). Always persist in plan.
    if args.atoms_model is not None:
        effective_atoms_model = args.atoms_model
    elif book_spec.atoms_model is not None:
        effective_atoms_model = book_spec.atoms_model.value
    else:
        from phoenix_v4.planning.atoms_model_loader import atoms_model_for_persona
        effective_atoms_model = atoms_model_for_persona(persona_id).value
        print(f"Warning: atoms_model missing in spec; derived from config (legacy_personas) -> {effective_atoms_model}", file=sys.stderr)
    book_spec_for_compiler["atoms_model"] = effective_atoms_model

    # atoms_root: default None (repo atoms/). Cluster future-guard: when atoms_model=cluster and unset, warn and set default.
    atoms_root = Path(args.atoms_root) if args.atoms_root else None
    if effective_atoms_model == "cluster" and atoms_root is None:
        atoms_root = REPO_ROOT / "atoms"
        print(
            "Warning: atoms_model=cluster but atoms_root not set; using repo atoms/ — cluster layout (core/ + overlay/) required when implemented",
            file=sys.stderr,
        )

    # Author assets (Writer Spec §23.3, §23.9): load when author_id set; fail if any required asset missing.
    author_assets = None
    if book_spec_for_compiler.get("author_id"):
        from phoenix_v4.planning.author_asset_loader import load_author_assets
        author_assets = load_author_assets(book_spec_for_compiler["author_id"], repo_root=REPO_ROOT)
        if author_assets.get("errors"):
            print("Error: author assets missing or invalid (Writer Spec §23.9):", file=sys.stderr)
            for e in author_assets["errors"]:
                print(f"  - {e}", file=sys.stderr)
            return 1
        # Attach for downstream (templates, audiobook pre-intro, etc.); omit internal 'errors' in payload
        book_spec_for_compiler["author_assets"] = {k: v for k, v in author_assets.items() if k != "errors"}

        # Controlled Intro/Conclusion Variation: resolve pre-intro from pattern banks when enabled
        intro_ending_cfg = {}
        try:
            from phoenix_v4.planning.intro_ending_caps import load_intro_ending_config
            intro_ending_cfg = load_intro_ending_config()
        except Exception:
            pass
        if intro_ending_cfg.get("intro_ending_variation_enabled"):
            from phoenix_v4.planning.pre_intro_resolver import (
                resolve_pre_intro_blocks,
                compute_pre_intro_signature,
                PRE_INTRO_BLOCK_ORDER,
            )
            from phoenix_v4.planning.author_asset_loader import render_audiobook_pre_intro
            from phoenix_v4.qa.validate_pre_intro import validate_pre_intro
            from phoenix_v4.planning.intro_ending_caps import (
                get_quarter_for_brand,
                load_signature_index,
                check_intro_cap_and_duplicate,
            )
            config_sot = REPO_ROOT / "config" / "source_of_truth"
            pattern_bank_overrides_yaml = bool(intro_ending_cfg.get("pattern_bank_overrides_yaml"))
            max_retries = int(intro_ending_cfg.get("max_retries", 5))
            cap_share = float(intro_ending_cfg.get("intro_signature_cap_share", 0.15))
            selector_key = f"{canonical_topic}|{canonical_persona}|{seed}"
            series_id = book_spec_for_compiler.get("series_id")
            include_series_line = bool(series_id)
            book_title_runtime = ""  # TODO: from naming engine when available
            series_name_runtime = ""
            signature_index_path = REPO_ROOT / "artifacts" / "pre_intro_signatures.jsonl"
            signature_index = load_signature_index(signature_index_path)
            quarter = get_quarter_for_brand(brand_id)
            last_cap_result = None
            resolved_blocks = None
            pre_intro_sig = None
            for retry in range(max_retries):
                sk = selector_key if retry == 0 else f"{selector_key}:retry{retry}"
                try:
                    resolved_blocks = resolve_pre_intro_blocks(
                        author_assets,
                        brand_id,
                        sk,
                        book_title=book_title_runtime,
                        series_name=series_name_runtime,
                        include_series_line=include_series_line,
                        pattern_bank_overrides_yaml=pattern_bank_overrides_yaml,
                        config_root=config_sot,
                    )
                except ValueError as e:
                    print(f"Pre-intro resolution failed: {e}", file=sys.stderr)
                    return 1
                # Merge stable blocks from original so required blocks present
                yaml_blocks = author_assets.get("audiobook_pre_intro") or {}
                for k in ("author_intro", "author_background"):
                    if yaml_blocks.get(k) and not resolved_blocks.get(k):
                        resolved_blocks[k] = yaml_blocks[k]
                val = validate_pre_intro(resolved_blocks, book_spec_for_compiler.get("author_id"))
                if not val.valid:
                    for err in val.errors:
                        print(f"Pre-intro validation failed: {err}", file=sys.stderr)
                    return 1
                full_text = render_audiobook_pre_intro(
                    author_assets,
                    book_title=book_title_runtime,
                    series_name=series_name_runtime,
                    include_series_line=include_series_line,
                    resolved_blocks=resolved_blocks,
                )
                pre_intro_sig = compute_pre_intro_signature(full_text)
                last_cap_result = check_intro_cap_and_duplicate(
                    brand_id, quarter, pre_intro_sig, signature_index, cap_share=cap_share,
                )
                if last_cap_result.ok:
                    break
            if not last_cap_result.ok:
                print(f"Pre-intro cap/duplicate gate failed after {max_retries} retries: {last_cap_result.error}", file=sys.stderr)
                if last_cap_result.candidate_alternatives:
                    for alt in last_cap_result.candidate_alternatives:
                        print(f"  Alternative: {alt}", file=sys.stderr)
                return 1
            # Replace author_assets audiobook_pre_intro with resolved and attach signature for plan output
            author_assets = {**author_assets, "audiobook_pre_intro": resolved_blocks}
            book_spec_for_compiler["author_assets"] = {k: v for k, v in author_assets.items() if k != "errors"}
            book_spec_for_compiler["_pre_intro_signature"] = pre_intro_sig
            # Opening chapter recognition style (soft bias for chapter 0)
            from phoenix_v4.planning.intro_ending_selector import (
                select_opening_style_id,
                select_integration_ending_style_id,
                select_carry_line_style_id,
            )
            book_spec_for_compiler["opening_style_id"] = select_opening_style_id(
                canonical_topic, canonical_persona, seed, config_root=config_sot,
            )
            book_spec_for_compiler["integration_ending_style_id"] = select_integration_ending_style_id(
                canonical_topic, canonical_persona, seed, config_root=config_sot,
            )
            book_spec_for_compiler["carry_line_style_id"] = select_carry_line_style_id(
                canonical_topic, canonical_persona, seed, config_root=config_sot,
            )
            book_spec_for_compiler["seed"] = seed

    format_plan_dict = format_plan.to_compiler_input()

    # V4 freeze: apply modular output format before variation/compile wiring.
    if freeze_enabled:
        selected_output_format = (args.output_format or freeze_settings.default_output_format or "").strip()
        try:
            require_valid_output_format(selected_output_format, freeze_settings)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        format_plan_dict = apply_output_format_to_plan(
            format_plan_dict,
            output_format_id=selected_output_format,
            chapter_count=arc.chapter_count,
            settings=freeze_settings,
        )

    # Structural Variation V4: select variation knobs (deterministic, anti-cluster) — before Stage 3 so compiler can use them
    variation_knobs = {}
    try:
        from phoenix_v4.planning.variation_selector import select_variation_knobs
        wave_index_for_variation = []
        index_path = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"
        if index_path.exists():
            for ln in index_path.read_text(encoding="utf-8").strip().splitlines():
                if ln.strip():
                    try:
                        wave_index_for_variation.append(json.loads(ln))
                    except json.JSONDecodeError:
                        pass
        variation_knobs = select_variation_knobs(
            topic_id=canonical_topic,
            persona_id=canonical_persona,
            chapter_count=arc.chapter_count,
            seed=seed,
            angle_id=book_spec_for_compiler.get("angle_id") or "",
            arc_id=getattr(arc, "arc_id", "") or "",
            installment_number=installment_number,
            wave_index=wave_index_for_variation or None,
        )
    except Exception as e:
        import warnings
        warnings.warn(f"Variation knobs selection failed, using defaults: {e}", stacklevel=2)
        from phoenix_v4.planning.schema_v4 import VARIATION_DEFAULTS, apply_variation_defaults, get_plan_variation_signature
        base = {"chapter_slot_sequence": []}
        applied = apply_variation_defaults(base, arc.chapter_count)
        variation_knobs = {
            "book_structure_id": applied["book_structure_id"],
            "journey_shape_id": applied["journey_shape_id"],
            "motif_id": applied["motif_id"],
            "section_reorder_mode": applied["section_reorder_mode"],
            "reframe_profile_id": applied["reframe_profile_id"],
            "chapter_archetypes": applied["chapter_archetypes"],
            "variation_signature": get_plan_variation_signature({**applied, "topic_id": canonical_topic, "persona_id": canonical_persona, "angle_id": book_spec_for_compiler.get("angle_id"), "arc_id": getattr(arc, "arc_id", "")}),
        }

    # Pass variation knobs into format_plan for Stage 3 (section reorder, motif/reframe injection)
    format_plan_dict["section_reorder_mode"] = variation_knobs.get("section_reorder_mode", "none")
    format_plan_dict["motif_id"] = variation_knobs.get("motif_id") or ""
    format_plan_dict["reframe_profile_id"] = variation_knobs.get("reframe_profile_id") or "balanced"

    # Arc-First: align format plan chapter_count and slot_definitions to arc
    if format_plan_dict.get("chapter_count") != arc.chapter_count:
        format_plan_dict["chapter_count"] = arc.chapter_count
        slot_defs = format_plan_dict.get("slot_definitions") or []
        if len(slot_defs) == 1:
            template = list(slot_defs[0])
            format_plan_dict["slot_definitions"] = [template[:] for _ in range(arc.chapter_count)]
        elif len(slot_defs) > arc.chapter_count:
            format_plan_dict["slot_definitions"] = slot_defs[: arc.chapter_count]
        else:
            template = list(slot_defs[-1]) if slot_defs else []
            extra = [template[:] for _ in range(arc.chapter_count - len(slot_defs))]
            format_plan_dict["slot_definitions"] = list(slot_defs) + extra
    # Ensure book_size stays coherent after any chapter_count alignment.
    ch_count_for_size = int(format_plan_dict.get("chapter_count") or arc.chapter_count or 0)
    format_plan_dict["book_size"] = "short" if ch_count_for_size <= 6 else ("medium" if ch_count_for_size <= 10 else "long")

    # Part 3.1 capability check (before Stage 3)
    from phoenix_v4.planning.pool_index import PoolIndex
    from phoenix_v4.planning.capability_check import capability_check
    pool_index = PoolIndex()
    cap_result = capability_check(
        book_spec_for_compiler,
        format_plan_dict,
        pool_index,
        mode="relaxed",
    )
    if not cap_result.ok:
        for e in cap_result.errors:
            print(f"Capability check failed: {e}", file=sys.stderr)
        for d in cap_result.diagnostics:
            print(d, file=sys.stderr)
        return 1
    if cap_result.achievable_chapters < (format_plan_dict.get("chapter_count") or 12):
        # Optionally reduce chapter count and re-slice slot_definitions (not done here; just warn)
        print(f"Note: achievable_chapters={cap_result.achievable_chapters}", file=sys.stderr)

    # DEV SPEC 3: Arc/format role-slot compatibility
    from phoenix_v4.planning.arc_loader import validate_arc_format_role_compat
    role_compat_errors = validate_arc_format_role_compat(arc, format_plan_dict)
    if role_compat_errors:
        for e in role_compat_errors:
            print(f"Arc/format role compatibility: {e}", file=sys.stderr)
        return 1

    # Teacher Mode: mandatory pre-compile coverage gate (after arc + format expanded, before compile)
    if book_spec_for_compiler.get("teacher_mode"):
        from phoenix_v4.teacher.coverage_gate import run_coverage_gate, TeacherCoverageError
        from phoenix_v4.teacher.teacher_config import load_teacher_config
        artifacts_dir = REPO_ROOT / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        _tid = (book_spec_for_compiler.get("teacher_id") or "").strip()
        _tcfg = load_teacher_config(_tid) if _tid else {}
        teacher_exercise_fallback = bool(_tcfg.get("teacher_exercise_fallback"))
        passed, gap_report = run_coverage_gate(
            book_spec_for_compiler,
            format_plan_dict,
            arc,
            teacher_exercise_fallback=teacher_exercise_fallback,
            artifacts_dir=artifacts_dir,
        )
        if not passed and gap_report is not None:
            (artifacts_dir / "teacher_coverage_report.json").write_text(
                json.dumps(gap_report, indent=2), encoding="utf-8"
            )
            print("Teacher coverage gate failed. See artifacts/teacher_coverage_report.json", file=sys.stderr)
            raise TeacherCoverageError(
                "Teacher coverage insufficient for required slots. See artifacts/teacher_coverage_report.json"
            )

    # Stage 3: CompiledBook (Arc-First: arc required)
    # Teacher Mode: require_full_resolution=True so no placeholders are allowed (Gate A).
    require_full_resolution = bool(book_spec_for_compiler.get("teacher_mode"))
    from phoenix_v4.planning.assembly_compiler import compile_plan
    compiled = compile_plan(
        book_spec_for_compiler,
        format_plan_dict,
        arc_path=arc_path,
        require_full_resolution=require_full_resolution,
        atoms_root=atoms_root,
        atoms_model=effective_atoms_model,
    )

    # Part 3.1 / 3.3 validate compiled plan (structure)
    from phoenix_v4.qa.validate_compiled_plan import validate_compiled_plan
    from phoenix_v4.planning.angle_resolver import get_angle_context
    angle_ctx = get_angle_context(book_spec_for_compiler.get("angle_id")) if book_spec_for_compiler.get("angle_id") else None
    # Chapter planner may adjust per-chapter slot policies at compile time; validate against actual compiled sequence.
    format_plan_for_validation = dict(format_plan_dict)
    format_plan_for_validation["slot_definitions"] = compiled.chapter_slot_sequence
    format_plan_for_validation["chapter_count"] = len(compiled.chapter_slot_sequence)
    format_plan_for_validation["target_chapter_count"] = len(compiled.chapter_slot_sequence)
    val_result = validate_compiled_plan(
        compiled, format_plan_for_validation,
        angle_context=angle_ctx,
        enforce_integration_reinforcement=False,
    )
    if not val_result.valid:
        for e in val_result.errors:
            print(f"Validation failed: {e}", file=sys.stderr)
        for w in val_result.warnings:
            print(f"Warning: {w}", file=sys.stderr)
        return 1
    for w in val_result.warnings:
        print(f"Warning: {w}", file=sys.stderr)

    # Arc-First: arc alignment and engine resolution
    from phoenix_v4.qa.validate_arc_alignment import validate_arc_alignment
    arc_errors = validate_arc_alignment(compiled, arc)
    if arc_errors:
        for e in arc_errors:
            print(f"Arc alignment failed: {e}", file=sys.stderr)
        return 1

    from phoenix_v4.planning.engine_loader import load_engine
    engine_def = load_engine(arc.engine)
    if engine_def:
        from phoenix_v4.qa.validate_engine_resolution import validate_engine_resolution
        engine_errors = validate_engine_resolution(arc, engine_def)
        if engine_errors:
            for e in engine_errors:
                print(f"Engine resolution failed: {e}", file=sys.stderr)
            return 1

    # Book-pass gate: narrative progression + prose-level claim quality (optional hard gate)
    if args.enforce_book_pass_gate:
        from phoenix_v4.qa.atom_metadata_loader import load_atom_metadata
        from phoenix_v4.qa.book_pass_gate import validate_book_pass
        from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan

        plan_for_gate = {
            "chapter_slot_sequence": compiled.chapter_slot_sequence,
            "atom_ids": compiled.atom_ids,
            "dominant_band_sequence": compiled.dominant_band_sequence or [],
            "exercise_chapters": compiled.exercise_chapters or [],
            "persona_id": canonical_persona,
            "topic_id": canonical_topic,
            "emotional_curve": getattr(arc, "emotional_curve", None) or [],
        }
        atom_meta = load_atom_metadata(
            atoms_root=atoms_root,
            persona=canonical_persona,
            topic=canonical_topic,
        )
        prose = resolve_prose_for_plan(plan_for_gate, atoms_root=atoms_root).prose_map
        book_pass = validate_book_pass(plan_for_gate, atom_meta, prose_map=prose)

        report_dir = REPO_ROOT / "artifacts" / "book_pass"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"{compiled.plan_hash}.json"
        report_path.write_text(
            json.dumps(
                {
                    "plan_hash": compiled.plan_hash,
                    "persona_id": canonical_persona,
                    "topic_id": canonical_topic,
                    "valid": book_pass.valid,
                    "errors": book_pass.errors,
                    "warnings": book_pass.warnings,
                    "metrics": book_pass.metrics,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        if not book_pass.valid:
            print(f"Book-pass gate failed. Report: {report_path}", file=sys.stderr)
            for e in book_pass.errors:
                print(f"  - {e}", file=sys.stderr)
            return 1
        for w in book_pass.warnings:
            print(f"Book-pass warning: {w}", file=sys.stderr)
        print(f"Book-pass gate passed. Report: {report_path}", file=sys.stderr)

    # Teacher matrix: enforce peak_intensity_limit on compiled band sequence
    if teacher_id and teacher_id != "default_teacher":
        from phoenix_v4.planning.teacher_matrix import load_teacher_matrix
        matrix = load_teacher_matrix()
        if matrix:
            teacher_entry = matrix.get("teachers", {}).get(teacher_id, {})
            constraints = teacher_entry.get("constraints") or {}
            peak_limit = constraints.get("peak_intensity_limit")
            if peak_limit is not None:
                bands = [b for b in (compiled.dominant_band_sequence or []) if b is not None]
                if bands:
                    max_band = max(bands)
                    if max_band > peak_limit:
                        print(
                            f"Peak intensity limit exceeded: plan max band={max_band}, "
                            f"teacher {teacher_id} peak_intensity_limit={peak_limit}",
                            file=sys.stderr,
                        )
                        return 1

    # Plan §6.1: teacher exercise share ≥ 60% when fallback used
    if teacher_id and teacher_id != "default_teacher" and getattr(compiled, "atom_sources", None):
        from phoenix_v4.qa.validate_teacher_exercise_share import validate_teacher_exercise_share
        ok, msg = validate_teacher_exercise_share(
            compiled.chapter_slot_sequence,
            compiled.atom_ids,
            list(compiled.atom_sources),
            min_share=0.60,
        )
        if not ok:
            print(f"Teacher exercise share validation failed: {msg}", file=sys.stderr)
            return 1

    out = {
        "plan_hash": compiled.plan_hash,
        "plan_id": compiled.plan_hash,
        "chapter_slot_sequence": compiled.chapter_slot_sequence,
        "atom_ids": compiled.atom_ids,
        "dominant_band_sequence": compiled.dominant_band_sequence,
    }
    if compiled.arc_id:
        out["arc_id"] = compiled.arc_id
    if teacher_id and teacher_id != "default_teacher":
        out["teacher_id"] = teacher_id
        out["teacher_mode"] = True
        # Plan §5.4: emit doctrine_version, doctrine_fingerprint for CI/audit (load from teacher bank if present)
        teacher_banks = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"
        doctrine_path = teacher_banks / teacher_id / "doctrine" / "doctrine.yaml"
        if not doctrine_path.exists():
            doctrine_path = teacher_banks / teacher_id / "doctrine.yaml"
        if doctrine_path.exists():
            try:
                from phoenix_v4.teacher.doctrine_fingerprint import load_doctrine_yaml, fingerprint_doctrine
                doctrine = load_doctrine_yaml(doctrine_path)
                if doctrine:
                    out["teacher_doctrine_version"] = doctrine.get("doctrine_version")
                    out["doctrine_fingerprint"] = fingerprint_doctrine(doctrine)
            except Exception:
                pass
    if getattr(compiled, "atom_sources", None):
        out["atom_sources"] = compiled.atom_sources
    if getattr(compiled, "chapter_thesis", None):
        out["chapter_thesis"] = compiled.chapter_thesis
    # Plan §3.12: when teacher_mode and any synthetic present, doctrine version must be pinned
    if teacher_id and teacher_id != "default_teacher" and getattr(compiled, "atom_sources", None):
        if "teacher_synthetic" in (compiled.atom_sources or []) and not out.get("teacher_doctrine_version"):
            print("Teacher mode with synthetic atoms requires teacher_doctrine_version (doctrine.yaml with doctrine_version).", file=sys.stderr)
            return 1
    # Structural fingerprint (CI / wave density / similarity)
    if compiled.emotional_temperature_sequence:
        out["emotional_temperature_sequence"] = compiled.emotional_temperature_sequence
    elif compiled.dominant_band_sequence:
        out["emotional_temperature_sequence"] = [str(b) if b is not None else "3" for b in compiled.dominant_band_sequence]
    if compiled.exercise_chapters is not None:
        out["exercise_chapters"] = compiled.exercise_chapters
    if compiled.slot_sig:
        out["slot_sig"] = compiled.slot_sig
    out["format_id"] = format_plan_dict.get("format_structural_id") or format_plan_dict.get("format_id") or ""
    out["runtime_format_id"] = args.runtime_format or format_plan_dict.get("runtime_format_id") or ""
    if format_plan_dict.get("output_format_id"):
        out["output_format_id"] = format_plan_dict.get("output_format_id")
        out["output_format_name"] = format_plan_dict.get("output_format_name")
    out["v4_freeze_enabled"] = freeze_enabled
    out["locale"] = book_spec_for_compiler.get("locale", "en-US")
    out["territory"] = book_spec_for_compiler.get("territory", "US")
    out["atoms_model"] = effective_atoms_model
    if getattr(arc, "engine", None):
        out["engine_id"] = arc.engine
    # Angle Integration (V4.7) — structural fingerprint / CTSS / wave density
    if book_spec_for_compiler.get("angle_id"):
        out["angle_id"] = book_spec_for_compiler["angle_id"]
    if compiled.reflection_strategy_sequence:
        out["reflection_strategy_sequence"] = compiled.reflection_strategy_sequence
    if compiled.chapter_archetypes:
        out["chapter_archetypes"] = compiled.chapter_archetypes
    if compiled.chapter_exercise_modes:
        out["chapter_exercise_modes"] = compiled.chapter_exercise_modes
    if compiled.chapter_reflection_weights:
        out["chapter_reflection_weights"] = compiled.chapter_reflection_weights
    if compiled.chapter_story_depths:
        out["chapter_story_depths"] = compiled.chapter_story_depths
    if compiled.chapter_planner_warnings:
        out["chapter_planner_warnings"] = compiled.chapter_planner_warnings
    if getattr(compiled, "chapter_bestseller_structures", None):
        out["chapter_bestseller_structures"] = compiled.chapter_bestseller_structures
    # Author identity and assets (Writer Spec §23)
    if book_spec_for_compiler.get("author_id"):
        out["author_id"] = book_spec_for_compiler["author_id"]
    if book_spec_for_compiler.get("narrator_id"):
        out["narrator_id"] = book_spec_for_compiler["narrator_id"]
    if author_assets is not None:
        out["author_assets"] = {k: v for k, v in author_assets.items() if k != "errors"}
    # Author cover art base (docs/authoring/AUTHOR_COVER_ART_SYSTEM.md): for export/storefront; fallback to default when no author/teacher
    cover_author_id = book_spec_for_compiler.get("author_id") or (teacher_id if (teacher_id and teacher_id != "default_teacher") else None)
    from phoenix_v4.planning.author_cover_art_resolver import resolve_author_cover_art
    cover_art = resolve_author_cover_art(cover_author_id, repo_root=REPO_ROOT)
    out["cover_art_base"] = cover_art.get("cover_art_base", "")
    out["cover_art_style_hint"] = cover_art.get("cover_art_style_hint", "")
    out["cover_art_palette_tokens"] = cover_art.get("cover_art_palette_tokens", [])
    out["cover_variant_id"] = cover_art.get("cover_variant_id", "")
    if book_spec_for_compiler.get("_pre_intro_signature"):
        out["pre_intro_signature"] = book_spec_for_compiler["_pre_intro_signature"]
    if book_spec_for_compiler.get("opening_style_id"):
        out["opening_style_id"] = book_spec_for_compiler["opening_style_id"]
    if book_spec_for_compiler.get("integration_ending_style_id"):
        out["integration_ending_style_id"] = book_spec_for_compiler["integration_ending_style_id"]
    if book_spec_for_compiler.get("carry_line_style_id"):
        out["carry_line_style_id"] = book_spec_for_compiler["carry_line_style_id"]
    if getattr(compiled, "ending_signature", None):
        out["ending_signature"] = compiled.ending_signature
    if getattr(compiled, "carry_line", None):
        out["carry_line"] = compiled.carry_line
    # Author positioning (Writer Spec §24)
    if compiled.author_positioning_profile:
        out["author_positioning_profile"] = compiled.author_positioning_profile
    if compiled.positioning_signature_hash:
        out["positioning_signature_hash"] = compiled.positioning_signature_hash
    # Compression (DEV SPEC 2)
    if compiled.compression_atom_ids:
        out["compression_atom_ids"] = compiled.compression_atom_ids
    if compiled.compression_sig:
        out["compression_sig"] = compiled.compression_sig
    if compiled.compression_pos_sig:
        out["compression_pos_sig"] = compiled.compression_pos_sig
    if compiled.compression_len_vec:
        out["compression_len_vec"] = compiled.compression_len_vec
    # DEV SPEC 3: Emotional Role Taxonomy
    if compiled.emotional_role_sequence:
        out["emotional_role_sequence"] = compiled.emotional_role_sequence
    if compiled.emotional_role_sig:
        out["emotional_role_sig"] = compiled.emotional_role_sig
    # Structural Variation V4: variation knobs and signature
    out["book_structure_id"] = variation_knobs.get("book_structure_id", "linear_transformation")
    out["journey_shape_id"] = variation_knobs.get("journey_shape_id", "recognition_to_agency")
    out["motif_id"] = variation_knobs.get("motif_id", "motif_pattern")
    out["section_reorder_mode"] = variation_knobs.get("section_reorder_mode", "none")
    out["reframe_profile_id"] = variation_knobs.get("reframe_profile_id", "balanced")
    out["variation_chapter_archetypes"] = variation_knobs.get("chapter_archetypes", [])
    if not out.get("chapter_archetypes"):
        out["chapter_archetypes"] = variation_knobs.get("chapter_archetypes", [])
    out["variation_signature"] = variation_knobs.get("variation_signature", "")
    if getattr(compiled, "motif_injections", None):
        out["motif_injections"] = compiled.motif_injections
    if getattr(compiled, "reframe_injections", None):
        out["reframe_injections"] = compiled.reframe_injections
    # Freebie attachment (post-Stage 3; Phase 1+3 — specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md)
    from phoenix_v4.planning.freebie_planner import plan_freebies, get_freebie_bundle_with_formats
    index_path = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"
    wave_index = []
    if index_path.exists():
        try:
            for ln in index_path.read_text(encoding="utf-8").strip().splitlines():
                if ln.strip():
                    wave_index.append(json.loads(ln))
        except (json.JSONDecodeError, OSError):
            pass
    series_context = None
    if book_spec_for_compiler.get("series_id") or book_spec_for_compiler.get("installment_number") is not None:
        series_context = {
            "series_id": book_spec_for_compiler.get("series_id") or "",
            "installment_number": book_spec_for_compiler.get("installment_number"),
            "total_in_series": book_spec_for_compiler.get("total_in_series"),
            "previous_primary_freebies": [r.get("freebie_bundle", [None])[0] for r in wave_index if r.get("freebie_bundle")],
        }
    freebie_bundle, cta_template_id, freebie_slug = plan_freebies(
        book_spec_for_compiler,
        format_plan_dict,
        compiled,
        arc,
        wave_index=wave_index if wave_index else None,
        series_context=series_context,
    )
    out["freebie_bundle"] = freebie_bundle
    out["cta_template_id"] = cta_template_id
    out["freebie_slug"] = freebie_slug
    # Formats per freebie for asset manifest (V4 Immersion Ecosystem)
    if yaml:
        registry_path = REPO_ROOT / "config" / "freebies" / "freebie_registry.yaml"
        if registry_path.exists():
            reg = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
            freebies_map = reg.get("freebies") or {}
            out["freebie_bundle_with_formats"] = get_freebie_bundle_with_formats(
                freebie_bundle, freebies_map, book_spec_for_compiler, format_plan_dict, compiled
            )
        else:
            out["freebie_bundle_with_formats"] = [{"freebie_id": fid, "formats": ["html"]} for fid in freebie_bundle]
    else:
        out["freebie_bundle_with_formats"] = [{"freebie_id": fid, "formats": ["html"]} for fid in freebie_bundle]
    out["topic_id"] = book_spec_for_compiler.get("topic_id") or book_spec_for_compiler.get("topic") or ""
    out["persona_id"] = book_spec_for_compiler.get("persona_id") or book_spec_for_compiler.get("persona") or ""
    # Ending cap/duplicate gate (intro_ending_variation)
    if out.get("ending_signature"):
        try:
            from phoenix_v4.planning.intro_ending_caps import (
                load_intro_ending_config,
                get_quarter_for_brand,
                load_signature_index,
                check_ending_cap_and_duplicate,
            )
            intro_cfg = load_intro_ending_config()
            if intro_cfg.get("intro_ending_variation_enabled"):
                sig_path = REPO_ROOT / "artifacts" / "pre_intro_signatures.jsonl"
                end_index = load_signature_index(sig_path)
                quarter = get_quarter_for_brand(brand_id)
                end_cap = float(intro_cfg.get("ending_signature_cap_share", 0.20))
                end_result = check_ending_cap_and_duplicate(
                    brand_id, quarter, out["ending_signature"], end_index, cap_share=end_cap,
                )
                if not end_result.ok:
                    print(f"Ending cap/duplicate gate failed: {end_result.error}", file=sys.stderr)
                    if end_result.candidate_alternatives:
                        for alt in end_result.candidate_alternatives:
                            print(f"  Alternative: {alt}", file=sys.stderr)
                    return 1
        except Exception as e:
            import warnings
            warnings.warn(f"Ending cap check failed: {e}", stacklevel=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Wrote {args.out}")
        # Record pre-intro signature for cap/duplicate gate (intro_ending_variation)
        if out.get("pre_intro_signature") or out.get("ending_signature"):
            from phoenix_v4.planning.intro_ending_caps import get_quarter_for_brand
            sig_path = REPO_ROOT / "artifacts" / "pre_intro_signatures.jsonl"
            sig_path.parent.mkdir(parents=True, exist_ok=True)
            quarter = get_quarter_for_brand(brand_id)
            row = {"brand_id": brand_id, "quarter": quarter}
            if out.get("pre_intro_signature"):
                row["pre_intro_signature"] = out["pre_intro_signature"]
            if out.get("ending_signature"):
                row["ending_signature"] = out["ending_signature"]
            with open(sig_path, "a", encoding="utf-8") as sf:
                sf.write(json.dumps(row) + "\n")
        # Upsert plan row into freebie plan index (one row per book_id) unless test run
        if not getattr(args, "no_update_freebie_index", False):
            index_path = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"
            index_row = {
                "book_id": out.get("plan_id") or out.get("plan_hash", ""),
                "freebie_bundle": freebie_bundle,
                "cta_template_id": cta_template_id,
                "slug": freebie_slug,
                "freebie_slug": freebie_slug,
            }
            # Structural Variation V4: include variation knobs in index for wave density / collision
            for key in ("book_structure_id", "journey_shape_id", "motif_id", "section_reorder_mode", "reframe_profile_id", "variation_signature", "chapter_archetypes"):
                if out.get(key) is not None:
                    index_row[key] = out[key]
            _upsert_plan_index_row(index_path, index_row)
        # Generate freebies (HTML, optional PDF) when writing plan (default on; use --no-generate-freebies to disable)
        do_generate_freebies = (bool(args.out) and not args.no_generate_freebies) or args.generate_freebies
        if do_generate_freebies and freebie_slug:
            from phoenix_v4.freebies.freebie_renderer import generate_freebies_for_book
            formats_list = None
            if args.formats:
                formats_list = [f.strip().lower() for f in args.formats.split(",") if f.strip()]
            publish_dir = Path(args.publish_dir) if args.publish_dir else None
            asset_store = Path(args.asset_store) if args.asset_store else None
            paths = generate_freebies_for_book(
                out,
                book_spec_for_compiler,
                include_pdf=bool(formats_list and "pdf" in formats_list) if formats_list else False,
                formats=formats_list,
                skip_audio=args.skip_audio,
                publish_dir=publish_dir,
                asset_store_root=asset_store,
            )
            if paths:
                print(f"Generated freebie artifacts: {len(paths)} file(s) under artifacts/freebies/")
        # Stage 6: render plan to book prose (manuscript/QA) when requested
        if args.render_book:
            from phoenix_v4.rendering import render_book
            render_dir = Path(args.render_dir) if args.render_dir else (REPO_ROOT / "artifacts" / "rendered" / (out.get("plan_id") or out.get("plan_hash", "book")))
            formats_list = [f.strip().lower() for f in (args.render_formats or "txt").split(",") if f.strip()]
            try:
                written = render_book(
                    out,
                    render_dir,
                    formats=formats_list,
                    allow_placeholders=False,
                    on_missing="fail",
                    title_page=True,
                    include_slot_labels_qa=False,
                    enforce_word_count=not args.skip_word_count_gate,
                )
                for fmt, path in written.items():
                    print(f"Rendered book ({fmt}): {path}")
            except ValueError as e:
                print(f"Stage 6 render failed: {e}", file=sys.stderr)
                return 1
        # EI V2 parallel comparison (advisory; V1 remains authoritative)
        if args.ei_v2_compare:
            try:
                from phoenix_v4.quality.ei_parallel_adapter import (
                    compare_slot,
                    build_pipeline_comparison,
                    write_comparison_report,
                )
                from phoenix_v4.quality.ei_v2.config import load_ei_v2_config
                from phoenix_v4.rendering.prose_resolver import resolve_prose_for_plan

                v2_cfg = load_ei_v2_config()
                v1_cfg = {}  # V1 loads its own config from ei_registry
                try:
                    v1_cfg_path = REPO_ROOT / "config" / "source_of_truth" / "enlightened_intelligence_registry.yaml"
                    if v1_cfg_path.exists() and yaml:
                        v1_cfg = yaml.safe_load(v1_cfg_path.read_text(encoding="utf-8")) or {}
                except Exception:
                    pass

                prose_result = resolve_prose_for_plan(out, atoms_root=atoms_root)
                prose_map = prose_result.prose_map

                book_thesis = f"{canonical_topic} for {canonical_persona}"
                chapter_thesis_map = out.get("chapter_thesis") or {}
                chapter_bestseller_structures = out.get("chapter_bestseller_structures") or []
                chapter_slot_seq = out.get("chapter_slot_sequence", [])
                atom_ids_list = out.get("atom_ids", [])
                band_seq = out.get("dominant_band_sequence", [])
                emotional_roles = out.get("emotional_role_sequence", [])

                slot_comparisons = []
                atom_idx = 0
                for ch_idx, slots in enumerate(chapter_slot_seq):
                    chapter_prose_parts = []
                    chapter_candidates_by_slot = []

                    for si, slot_type in enumerate(slots):
                        if atom_idx >= len(atom_ids_list):
                            break
                        aid = atom_ids_list[atom_idx]
                        prose = prose_map.get(aid, "")
                        chapter_prose_parts.append(prose)
                        chapter_candidates_by_slot.append((slot_type, si, aid, prose))
                        atom_idx += 1

                    chapter_text = "\n\n".join(chapter_prose_parts)
                    band = band_seq[ch_idx] if ch_idx < len(band_seq) else None
                    role = emotional_roles[ch_idx] if ch_idx < len(emotional_roles) else ""
                    # EI v2: use chapter thesis when present (for learning and thesis alignment)
                    thesis_ch = chapter_thesis_map.get(ch_idx + 1) if isinstance(chapter_thesis_map, dict) else None
                    thesis = (thesis_ch or "").strip() or book_thesis
                    bestseller_structure = chapter_bestseller_structures[ch_idx] if ch_idx < len(chapter_bestseller_structures) else None
                    arc_intent = {
                        "band": band,
                        "emotional_role": role,
                        "chapter_index": ch_idx,
                        "chapter_thesis": thesis_ch,
                        "bestseller_structure": bestseller_structure,
                    }

                    for slot_type, si, aid, prose in chapter_candidates_by_slot:
                        candidates_raw = [{"id": aid, "text": prose, "meta": {}}]
                        try:
                            result = compare_slot(
                                slot=slot_type,
                                chapter_index=ch_idx,
                                slot_index=si,
                                candidates_raw=candidates_raw,
                                persona_id=canonical_persona,
                                topic_id=canonical_topic,
                                thesis=thesis,
                                v1_cfg=v1_cfg,
                                v2_cfg=v2_cfg,
                                selector_key=f"ei:{slot_type}:ch{ch_idx}:{canonical_persona}:{canonical_topic}",
                                teacher_mode=teacher_mode,
                                chapter_text=chapter_text,
                                arc_intent=arc_intent,
                            )
                            slot_comparisons.append(result)
                        except Exception as exc:
                            print(f"EI V2 compare failed at ch{ch_idx} {slot_type}: {exc}", file=sys.stderr)

                comparison = build_pipeline_comparison(
                    slot_comparisons,
                    plan_hash=out.get("plan_hash", ""),
                    persona_id=canonical_persona,
                    topic_id=canonical_topic,
                )
                ei_v2_dir = REPO_ROOT / "artifacts" / "ei_v2"
                report_path = write_comparison_report(comparison, ei_v2_dir)
                print(f"EI V2 comparison: {report_path}")
                print(
                    f"  Slots compared: {comparison.total_slots} | "
                    f"Agreement: {comparison.agreement_rate * 100:.0f}% | "
                    f"Safety flags: {len(comparison.v2_safety_flags)} | "
                    f"TTS issues: {len(comparison.v2_tts_issues)} | "
                    f"Dedup flags: {len(comparison.v2_dedup_flags)} | "
                    f"Arc issues: {len(comparison.v2_arc_issues)}"
                )
            except Exception as exc:
                print(f"EI V2 comparison failed (non-blocking): {exc}", file=sys.stderr)
    else:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
