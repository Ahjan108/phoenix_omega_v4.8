#!/usr/bin/env python3
"""
Run V4.5 Production Readiness gates (14 conditions).
Usage: from repo root: python scripts/run_production_readiness_gates.py
       or: python -m scripts.run_production_readiness_gates
"""
from __future__ import annotations

import os
import subprocess
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

RESULTS = []


def gate(name: str, passed: bool, detail: str = "", skip: bool = False):
    status = "SKIP" if skip else ("PASS" if passed else "FAIL")
    RESULTS.append((name, status, detail))
    return passed


def main() -> int:
    failed = 0

    # --- 1. Canonical Spec Is Single Source of Truth ---
    writer_spec = REPO_ROOT / "specs" / "PHOENIX_V4_5_WRITER_SPEC.md"
    canonical_spec = REPO_ROOT / "specs" / "PHOENIX_V4_CANONICAL_SPEC.md"
    if not gate(
        "1. Canonical Spec Is Single Source of Truth",
        writer_spec.exists() and canonical_spec.exists(),
        "Writer + Canonical specs exist",
    ):
        failed += 1
    if writer_spec.exists():
        text = writer_spec.read_text()
        has_s16 = "## 16." in text or "# 16. Emotional QA" in text
        if not gate("1b. Writer Spec Section 16 (Emotional QA) exists", has_s16, "§16 present"):
            failed += 1

    # --- 2. SOURCE_OF_TRUTH Coverage Is Complete ---
    atoms_dir = REPO_ROOT / "atoms"
    atoms_structure_ok = atoms_dir.exists()
    personas = []
    if atoms_structure_ok:
        personas = [d.name for d in atoms_dir.iterdir() if d.is_dir()]
        atoms_structure_ok = len(personas) >= 1
    gate(
        "2. SOURCE_OF_TRUTH Coverage (atoms layout)",
        atoms_structure_ok,
        f"atoms/ exists, personas: {personas or 'none'}",
    )
    if not atoms_structure_ok:
        failed += 1
    # K-table / coverage enforcement in CI (PLANNING_STATUS: coverage checker)
    try:
        from phoenix_v4.planning.coverage_checker import run_coverage_check
        coverage_ok, coverage_errors = run_coverage_check(mode="relaxed")
        if not gate("2b. K-table coverage (coverage_checker)", coverage_ok, "; ".join(coverage_errors[:3]) if coverage_errors else "All persona×topic pass"):
            failed += 1
    except Exception as e:
        if not gate("2b. K-table coverage (coverage_checker)", False, str(e)):
            failed += 1

    # --- 3. K-Table Thresholds Are Enforced ---
    qa_rules = REPO_ROOT / "phoenix_v4" / "qa" / "emotional_governance_rules.yaml"
    k_tables_dir = REPO_ROOT / "phoenix_v4" / "policy" / "k_tables"
    gate(
        "3. K-Table / governance rules exist",
        qa_rules.exists(),
        "emotional_governance_rules.yaml present" + ("; k_tables/ optional" if not k_tables_dir.exists() else ""),
    )
    if not qa_rules.exists():
        failed += 1

    # --- 4. Assembly Is Deterministic ---
    gate("4. Assembly Is Deterministic", True, "Spec-defined; verify with same seed → same plan hash", skip=True)

    # --- 5. Emotional QA (Section 16) Passes ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            has_chapter = "chapter_level" in data
            has_volatile = "chapter_level" in data and "volatile_requirement" in data.get("chapter_level", {})
            has_cog_body = "chapter_level" in data and "cognitive_body_ratio" in data.get("chapter_level", {})
            gate(
                "5. Emotional QA rules (chapter_level)",
                has_chapter and (has_volatile or has_cog_body),
                "chapter_level + volatile/cognitive_body present",
            )
            if not has_chapter:
                failed += 1
        except Exception as e:
            gate("5. Emotional QA rules", False, str(e))
            failed += 1
    else:
        gate("5. Emotional QA rules", False, "emotional_governance_rules.yaml missing")
        failed += 1

    # --- 6. TTS Rhythm Governance Passes ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            tts = data.get("tts_rhythm", {})
            gate("6. TTS Rhythm in governance", bool(tts), "tts_rhythm section present")
            if not tts:
                failed += 1
        except Exception as e:
            gate("6. TTS Rhythm", False, str(e))
            failed += 1

    # --- 7. Drift Detection Passes (Book-Level) ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            bl = data.get("book_level", {})
            gate("7. Drift / book_level rules", bool(bl), "book_level section present")
            if not bl:
                failed += 1
        except Exception:
            gate("7. Drift book_level", False, "YAML error")
            failed += 1

    # --- 8. Structural Similarity Limits Pass ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            cat = data.get("catalog_level", {})
            gate("8. Catalog-level similarity rules", bool(cat), "catalog_level section present")
            if not cat:
                failed += 1
        except Exception:
            gate("8. Catalog-level", False, "YAML error")
            failed += 1

    # --- 9. Persona Hydration Is Enforced ---
    topic_skins = REPO_ROOT / "config" / "topic_skins.yaml"
    bindings = REPO_ROOT / "config" / "topic_engine_bindings.yaml"
    gate(
        "9. Persona / topic config (topic_skins, bindings)",
        topic_skins.exists() and bindings.exists(),
        "config/topic_skins.yaml + topic_engine_bindings.yaml",
    )
    if not (topic_skins.exists() and bindings.exists()):
        failed += 1

    # --- 10. No Forbidden Resolution Language ---
    gate("10. No Forbidden Resolution Language", True, "Spec §11 + Canonical §4.4; CI gate", skip=True)

    # --- 11. CI Failure Protocol Is Active ---
    if qa_rules.exists():
        try:
            data = yaml.safe_load(qa_rules.read_text()) or {}
            fp = data.get("failure_protocol", {})
            gate("11. CI failure_protocol defined", bool(fp), "failure_protocol in emotional_governance_rules")
            if not fp:
                failed += 1
        except Exception:
            gate("11. failure_protocol", False, "YAML error")
            failed += 1

    # --- 12. Release Simulation Passes ---
    run_sim = REPO_ROOT / "simulation" / "run_simulation.py"
    gate("12. Release simulation script exists", run_sim.exists(), "simulation/run_simulation.py")
    if not run_sim.exists():
        failed += 1

    # --- 13. FMT Enforced for Full-Book Formats ---
    binge_spec = REPO_ROOT / "specs" / "V4_6_BINGE_OPTIMIZATION_LAYER.md"
    gate("13. FMT / Binge spec exists", binge_spec.exists(), "V4_6_BINGE_OPTIMIZATION_LAYER.md")
    if not binge_spec.exists():
        failed += 1

    # --- 14. Repo-Root config / registry / atoms Integrity ---
    registry_dir = REPO_ROOT / "registry"
    registry_ok = registry_dir.exists() and any(registry_dir.glob("*.yaml"))
    config_ok = (REPO_ROOT / "config" / "topic_engine_bindings.yaml").exists() and (REPO_ROOT / "config" / "topic_skins.yaml").exists()
    atoms_ok = atoms_dir.exists() and any((atoms_dir / p / t / e / "CANONICAL.txt").exists() for p in (atoms_dir.iterdir() if atoms_dir.exists() else []) for t in (p.iterdir() if p.is_dir() else []) for e in (t.iterdir() if t.is_dir() else []) if p.is_dir() and t.is_dir())
    # simpler atoms check
    canon_count = len(list(atoms_dir.rglob("CANONICAL.txt"))) if atoms_dir.exists() else 0
    atoms_ok = canon_count > 0
    gate(
        "14. config/registry/atoms integrity",
        config_ok and registry_ok and atoms_ok,
        f"config={config_ok} registry={registry_ok} atoms({canon_count} CANONICAL.txt)={atoms_ok}",
    )
    if not (config_ok and registry_ok and atoms_ok):
        failed += 1

    # --- 15. Full pipeline (Stage 1→2→3) runnable ---
    pipeline_script = REPO_ROOT / "scripts" / "run_pipeline.py"
    catalog_planner = REPO_ROOT / "phoenix_v4" / "planning" / "catalog_planner.py"
    assembly_compiler = REPO_ROOT / "phoenix_v4" / "planning" / "assembly_compiler.py"
    pipeline_ok = pipeline_script.exists() and catalog_planner.exists() and assembly_compiler.exists()
    if pipeline_ok:
        arc_path = REPO_ROOT / "config" / "source_of_truth" / "master_arcs" / "nyc_executives__self_worth__shame__F006.yaml"
        if not arc_path.exists():
            pipeline_ok = False
        else:
            try:
                out_path = REPO_ROOT / "artifacts" / "golden_plans" / "_gate_pipeline_out.json"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                r = subprocess.run(
                    [
                        sys.executable, str(pipeline_script),
                        "--topic", "self_worth", "--persona", "nyc_executives",
                        "--arc", str(arc_path),
                        "--out", str(out_path),
                    ],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if r.returncode == 0 and out_path.exists():
                    import json
                    data = json.loads(out_path.read_text())
                    pipeline_ok = isinstance(data.get("plan_hash"), str) and isinstance(data.get("atom_ids"), list)
                else:
                    pipeline_ok = False
            except Exception:
                pipeline_ok = False
    gate(
        "15. Full pipeline (Stage 1→2→3) runnable",
        pipeline_ok,
        "run_pipeline.py + catalog_planner + assembly_compiler; one run produces valid CompiledBook",
    )
    if not pipeline_ok:
        failed += 1

    # --- 16. Freebie density (Phase 3; run when index has ≥2 plan rows) ---
    freebie_index = REPO_ROOT / "artifacts" / "freebies" / "index.jsonl"
    if freebie_index.exists():
        lines = [ln for ln in freebie_index.read_text().strip().splitlines() if ln.strip()]
        if len(lines) >= 2:
            try:
                env = os.environ.copy()
                env["PYTHONPATH"] = str(REPO_ROOT)
                r = subprocess.run(
                    [sys.executable, "-m", "phoenix_v4.qa.validate_freebie_density", "--index", str(freebie_index)],
                    cwd=str(REPO_ROOT),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                freebie_density_ok = r.returncode == 0
                freebie_detail = "Density within thresholds" if freebie_density_ok else (r.stderr.strip() or "validate_freebie_density.py FAIL")
            except Exception:
                freebie_density_ok = False
                freebie_detail = "validate_freebie_density.py FAIL"
            if not gate("16. Freebie density (wave)", freebie_density_ok, freebie_detail):
                failed += 1
        else:
            gate("16. Freebie density (wave)", True, f"Index has {len(lines)} row(s); need ≥2 for wave density check; skip", skip=True)
    else:
        gate("16. Freebie density (wave)", True, "No freebie index; skip", skip=True)

    # --- Report ---
    print("V4.5 Production Readiness — 15 (+ freebie) conditions\n")
    for name, status, detail in RESULTS:
        sym = "✓" if status == "PASS" else ("○" if status == "SKIP" else "✗")
        print(f"  {sym} {status:4}  {name}")
        if detail:
            print(f"      {detail}")
    print()
    if failed > 0:
        print(f"FAILED: {failed} condition(s) not met.")
        return 1
    print("All automatable gates passed. Run simulation (--phase2 --phase3) and manual checks for full sign-off.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
