#!/usr/bin/env python3
"""
Single pre-publish gate entrypoint.

Canonical order (frozen):
1) Structural entropy (per plan)
2) Platform similarity (per plan, against existing index)
3) Prose duplication (wave rendered vs catalog rendered)
4) Wave density (wave-wide)
5) Update similarity index (last, only when gates 1-4 all pass; sole state mutation)

All non-mutating gates (1-4) are always run for full diagnostics; we do not
short-circuit on first failure. Step 5 runs only when there are no failures.

Exit codes:
- 0: all blocking gates passed
- 1: one or more blocking gates failed
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _run(cmd: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
    )


def _plan_files(plans_dir: Path) -> List[Path]:
    return sorted([p for p in plans_dir.glob("*.json") if p.is_file()])


def _maybe_book_spec(book_spec_dir: Path | None, plan_path: Path) -> Path | None:
    if book_spec_dir is None:
        return None
    cand = book_spec_dir / plan_path.name
    return cand if cand.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Run all blocking pre-publish gates in fixed order")
    ap.add_argument("--plans-dir", required=True, help="Directory of compiled plan .json files")
    ap.add_argument("--index", required=True, help="Catalog similarity index.jsonl path")
    ap.add_argument("--wave-rendered-dir", required=True, help="Rendered .txt directory for this wave")
    ap.add_argument("--catalog-rendered-dir", default="", help="Rendered .txt directory for existing catalog")
    ap.add_argument("--book-spec-dir", default="", help="Optional BookSpec .json directory matching plan filenames")
    ap.add_argument("--block-threshold", type=float, default=0.78, help="CTSS block threshold")
    ap.add_argument("--review-threshold", type=float, default=0.65, help="CTSS review threshold")
    ap.add_argument("--fail-on-similarity-warn", action="store_true", help="Treat CTSS WARN as blocking")
    ap.add_argument("--fail-ngram-jaccard", type=float, default=0.35)
    ap.add_argument("--warn-ngram-jaccard", type=float, default=0.25)
    ap.add_argument("--report", default="", help="Optional JSON report path")
    ap.add_argument("--dry-run-index-update", action="store_true", help="Do not append to similarity index")
    args = ap.parse_args()

    plans_dir = Path(args.plans_dir)
    index_path = Path(args.index)
    wave_rendered_dir = Path(args.wave_rendered_dir)
    catalog_rendered_dir = Path(args.catalog_rendered_dir) if args.catalog_rendered_dir else None
    book_spec_dir = Path(args.book_spec_dir) if args.book_spec_dir else None

    plans = _plan_files(plans_dir)
    if not plans:
        print(f"PREPUBLISH: FAIL (no plan json files in {plans_dir})", file=sys.stderr)
        return 1

    failures: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    steps: List[Dict[str, Any]] = []

    # 1) Structural entropy + 2) Platform similarity (per plan)
    for plan in plans:
        step = {"plan": str(plan), "structural_entropy": None, "platform_similarity": None}

        se_cmd = [sys.executable, str(REPO_ROOT / "scripts" / "ci" / "check_structural_entropy.py"), "--plan", str(plan)]
        bs = _maybe_book_spec(book_spec_dir, plan)
        if bs is not None:
            se_cmd += ["--book-spec", str(bs)]
        r = _run(se_cmd)
        step["structural_entropy"] = {"rc": r.returncode, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
        if r.returncode != 0:
            failures.append({"gate": "check_structural_entropy", "plan": str(plan), "detail": r.stderr.strip() or r.stdout.strip()})

        sim_cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ci" / "check_platform_similarity.py"),
            "--plan",
            str(plan),
            "--index",
            str(index_path),
            "--block",
            str(args.block_threshold),
            "--review",
            str(args.review_threshold),
        ]
        r = _run(sim_cmd)
        out = (r.stdout or "").strip()
        step["platform_similarity"] = {"rc": r.returncode, "stdout": out, "stderr": r.stderr.strip()}
        if r.returncode != 0:
            failures.append({"gate": "check_platform_similarity", "plan": str(plan), "detail": r.stderr.strip() or out})
        elif "PLATFORM SIMILARITY CHECK: WARN" in out:
            w = {"gate": "check_platform_similarity", "plan": str(plan), "detail": out}
            if args.fail_on_similarity_warn:
                failures.append(w)
            else:
                warnings.append(w)

        steps.append(step)

    # 3) Prose duplication (wave-wide)
    prose_cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "ci" / "check_prose_duplication.py"),
        "--wave-rendered-dir",
        str(wave_rendered_dir),
        "--fail-ngram-jaccard",
        str(args.fail_ngram_jaccard),
        "--warn-ngram-jaccard",
        str(args.warn_ngram_jaccard),
    ]
    if catalog_rendered_dir is not None:
        prose_cmd += ["--catalog-rendered-dir", str(catalog_rendered_dir)]
    r = _run(prose_cmd)
    steps.append(
        {
            "prose_duplication": {
                "rc": r.returncode,
                "stdout": (r.stdout or "").strip(),
                "stderr": (r.stderr or "").strip(),
            }
        }
    )
    if r.returncode != 0:
        failures.append({"gate": "check_prose_duplication", "detail": r.stderr.strip() or r.stdout.strip()})

    # 4) Wave density (wave-wide)
    wd_cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "ci" / "check_wave_density.py"),
        "--plans-dir",
        str(plans_dir),
    ]
    r = _run(wd_cmd)
    steps.append(
        {
            "wave_density": {
                "rc": r.returncode,
                "stdout": (r.stdout or "").strip(),
                "stderr": (r.stderr or "").strip(),
            }
        }
    )
    if r.returncode != 0:
        failures.append({"gate": "check_wave_density", "detail": r.stderr.strip() or r.stdout.strip()})

    # 4a) Delivery gate: no placeholders/metadata in book output (§10.6)
    placeholder_cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "ci" / "check_book_output_no_placeholders.py"),
        "--wave-rendered-dir",
        str(wave_rendered_dir),
    ]
    r = _run(placeholder_cmd)
    steps.append(
        {
            "book_output_no_placeholders": {
                "rc": r.returncode,
                "stdout": (r.stdout or "").strip(),
                "stderr": (r.stderr or "").strip(),
            }
        }
    )
    if r.returncode != 0:
        failures.append({"gate": "check_book_output_no_placeholders", "detail": r.stderr.strip() or r.stdout.strip()})

    # 4b) Series diversity (P0: hard fail on adjacent mech+journey or band_curve; soft warn on combo density)
    try:
        from phoenix_v4.qa.validate_series_diversity import validate_series_diversity
        hard_series, soft_series = validate_series_diversity(plans_dir)
        steps.append({"series_diversity": {"hard_violations": len(hard_series), "soft_warnings": len(soft_series)}})
        for v in hard_series:
            failures.append({"gate": "validate_series_diversity", "detail": str(v)})
        for w in soft_series:
            warnings.append({"gate": "validate_series_diversity", "detail": str(w)})
    except Exception as e:
        steps.append({"series_diversity": {"error": str(e)}})
        failures.append({"gate": "validate_series_diversity", "detail": str(e)})

    # 5) Index append only if all prior gates pass
    index_updates: List[Dict[str, Any]] = []
    if not failures and not args.dry_run_index_update:
        for plan in plans:
            upd_cmd = [
                sys.executable,
                str(REPO_ROOT / "scripts" / "ci" / "update_similarity_index.py"),
                "--plan",
                str(plan),
                "--index",
                str(index_path),
            ]
            r = _run(upd_cmd)
            rec = {"plan": str(plan), "rc": r.returncode, "stdout": (r.stdout or "").strip(), "stderr": (r.stderr or "").strip()}
            index_updates.append(rec)
            if r.returncode != 0:
                failures.append({"gate": "update_similarity_index", "plan": str(plan), "detail": r.stderr.strip() or r.stdout.strip()})
    elif args.dry_run_index_update:
        warnings.append({"gate": "update_similarity_index", "detail": "dry-run enabled; index not updated"})

    status = "pass" if not failures else "fail"
    report = {
        "status": status,
        "plans_dir": str(plans_dir),
        "index": str(index_path),
        "wave_rendered_dir": str(wave_rendered_dir),
        "catalog_rendered_dir": str(catalog_rendered_dir) if catalog_rendered_dir else "",
        "plan_count": len(plans),
        "failures": failures,
        "warnings": warnings,
        "steps": steps,
        "index_updates": index_updates,
    }

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wrote {out}")

    if failures:
        print("PREPUBLISH: FAIL")
        for f in failures:
            print(f" - {f['gate']}: {f.get('plan', '')} {f.get('detail', '')}".strip())
        return 1

    print("PREPUBLISH: PASS")
    if warnings:
        print(f" - WARNINGS: {len(warnings)}")
    print(f" - Plans validated: {len(plans)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

