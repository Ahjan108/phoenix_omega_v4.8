#!/usr/bin/env python3
"""
Export weekly brand packets: one folder per brand with upload_manifest.csv,
book_files/, cover/, advisory_report.json, release_day.txt; then zip each.

Idempotent: re-running same week overwrites deterministically.
Single week key: YYYY-WW derived once from week_start (normalized to Monday).
Feasibility guard: strict mode (default) fails whole week if any plan or required
rendered file is missing. Required rendered output: artifacts/rendered/<plan_id>/book.txt
(or wave .../rendered/<plan_id>/book.txt). See REQUIRED_RENDERED_FILE.
Validates advisory_report against schema; CSV headers/rows per upload_manifest_csv_v1.

Usage:
  python scripts/release/export_brand_packets.py --week 1
  python scripts/release/export_brand_packets.py --week-start 2026-03-10
  python scripts/release/export_brand_packets.py --week 1 --wave-id my_wave --no-strict
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_CSV = REPO_ROOT / "schemas" / "release" / "upload_manifest_csv_v1.schema.json"
SCHEMA_MANIFEST = REPO_ROOT / "schemas" / "release" / "brand_packet_manifest_v1.schema.json"
# Required rendered output: this file must exist for each plan in strict mode.
# Path: artifacts/rendered/<plan_id>/book.txt or wave .../rendered/<plan_id>/book.txt
REQUIRED_RENDERED_FILE = "book.txt"


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def _load_manifest_columns() -> list[str]:
    """Required CSV headers from upload_manifest_csv_v1.schema.json."""
    if SCHEMA_CSV.exists():
        try:
            data = json.loads(SCHEMA_CSV.read_text())
            return list(data.get("required_headers") or [])
        except (json.JSONDecodeError, OSError):
            pass
    return [
        "plan_id", "title", "subtitle", "description", "keywords", "category",
        "series_id", "installment_number", "price", "brand_id", "topic_id", "persona_id", "locale",
    ]


def _iso_week(week_start: str) -> str:
    """Return YYYY-WW from week_start after normalizing to Monday (avoids timezone drift)."""
    import sys
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from scripts.release.week_utils import iso_week_from_week_start
    return iso_week_from_week_start(week_start)


def _resolve_plan_path(path_str: str, repo_root: Path) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = repo_root / p
    return p


def _plan_to_manifest_row(plan: dict, repo_root: Path) -> dict:
    """Build one CSV row from plan JSON."""
    plan_id = plan.get("plan_id") or plan.get("plan_hash") or ""
    return {
        "plan_id": plan_id,
        "title": plan.get("title") or "",
        "subtitle": plan.get("subtitle") or "",
        "description": plan.get("description") or "",
        "keywords": plan.get("keywords") or "",
        "category": plan.get("category") or "",
        "series_id": plan.get("series_id") or "",
        "installment_number": plan.get("installment_number") or "",
        "price": plan.get("price") or "",
        "brand_id": plan.get("brand_id") or "",
        "topic_id": plan.get("topic_id") or "",
        "persona_id": plan.get("persona_id") or "",
        "locale": plan.get("locale") or "en-US",
    }


def _release_day_for_brand(week_start: str, brand_id: str, scheduler_config: dict) -> str:
    """First weekday in the week that matches brand_days; week_start should be Monday (normalized)."""
    brand_days = (scheduler_config.get("brand_days") or {}).get(brand_id)
    if not brand_days:
        return week_start
    import sys
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from scripts.release.week_utils import normalize_week_start_to_monday
    monday = normalize_week_start_to_monday(week_start)
    dt = datetime.strptime(monday, "%Y-%m-%d")
    day_slugs = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    for i in range(7):
        d = dt + timedelta(days=i)
        slug = day_slugs[d.weekday()]
        if slug in brand_days:
            return d.strftime("%Y-%m-%d")
    return week_start


def _gather_advisory_issues(prepublish_report_path: Path | None, plan_stems: set[str]) -> list[dict]:
    """Extract advisory issues for given plan stems from prepublish report."""
    issues: list[dict] = []
    if not prepublish_report_path or not prepublish_report_path.exists():
        return issues
    try:
        data = json.loads(prepublish_report_path.read_text())
    except (json.JSONDecodeError, OSError):
        return issues
    for step in (data.get("steps") or []):
        if step.get("advisory_issue"):
            issue = step["advisory_issue"]
            if isinstance(issue, dict) and step.get("plan"):
                stem = Path(step["plan"]).stem
                if stem in plan_stems:
                    issues.append(issue)
    return issues


def _validate_advisory_report(report: dict) -> None:
    """Ensure advisory_report has schema_version and issues array."""
    if report.get("schema_version") != "1.0":
        raise ValueError("advisory_report schema_version must be '1.0'")
    if not isinstance(report.get("issues"), list):
        raise ValueError("advisory_report.issues must be an array")


def main() -> int:
    ap = argparse.ArgumentParser(description="Export weekly brand packets (idempotent, single week key).")
    ap.add_argument("--schedule", type=Path, default=REPO_ROOT / "artifacts" / "release_schedule.json")
    ap.add_argument("--week", type=int, default=None, help="1-based week index in schedule")
    ap.add_argument("--week-start", default=None, help="YYYY-MM-DD to select week by start date")
    ap.add_argument("--wave-id", default=None, help="Prefer artifacts/waves/<wave_id>/plans and .../rendered")
    ap.add_argument("--prepublish-report", type=Path, default=None)
    ap.add_argument("--out-dir", type=Path, default=None, help="Override artifacts/brand_packets (default: artifacts/brand_packets/YYYY-WW)")
    ap.add_argument("--strict", action="store_true", default=True, help="Fail whole week if any plan or required rendered file missing (default)")
    ap.add_argument("--no-strict", action="store_false", dest="strict", help="Permissive: skip broken brand and continue")
    args = ap.parse_args()

    if not args.schedule.exists():
        print(f"Schedule not found: {args.schedule}", file=sys.stderr)
        return 1

    payload = json.loads(args.schedule.read_text())
    schedule_list = payload.get("schedule") if isinstance(payload.get("schedule"), list) else payload
    if not isinstance(schedule_list, list):
        schedule_list = [payload]

    # Select one week
    if args.week_start:
        week_start = args.week_start
        row = None
        for r in schedule_list:
            if r.get("week_start") == week_start:
                row = r
                break
        if not row:
            print(f"No schedule row for week_start={week_start}", file=sys.stderr)
            return 1
    elif args.week is not None:
        idx = args.week - 1
        if idx < 0 or idx >= len(schedule_list):
            print(f"Invalid --week {args.week} (schedule has {len(schedule_list)} weeks)", file=sys.stderr)
            return 1
        row = schedule_list[idx]
        week_start = row.get("week_start", "")
        if not week_start:
            print("Schedule row missing week_start", file=sys.stderr)
            return 1
    else:
        if not schedule_list:
            print("Schedule is empty", file=sys.stderr)
            return 1
        row = schedule_list[0]
        week_start = row.get("week_start", "")
        if not week_start:
            print("First schedule row missing week_start", file=sys.stderr)
            return 1

    import sys
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from scripts.release.week_utils import normalize_week_start_to_monday
    week_start = normalize_week_start_to_monday(week_start)
    week_key = _iso_week(week_start)
    base_out = args.out_dir or (REPO_ROOT / "artifacts" / "brand_packets" / week_key)
    base_out.mkdir(parents=True, exist_ok=True)

    assignments = row.get("assignments") or {}
    if not assignments:
        print(f"Week {week_key} has no brand assignments", file=sys.stderr)
        return 1

    # Feasibility guard: plan file + required rendered output (artifacts/rendered/<plan_id>/book.txt or wave .../rendered/<plan_id>/book.txt)
    wave_rendered_dir = REPO_ROOT / "artifacts" / "waves" / args.wave_id / "rendered" if args.wave_id else None
    missing: list[str] = []
    plan_paths_by_brand: dict[str, list[Path]] = {}
    for brand_id, path_list in assignments.items():
        paths: list[Path] = []
        for path_str in path_list or []:
            p = _resolve_plan_path(path_str, REPO_ROOT)
            if not p.exists():
                missing.append(str(p))
                continue
            plan_id = ""
            try:
                plan = json.loads(p.read_text())
                plan_id = plan.get("plan_id") or plan.get("plan_hash") or p.stem
            except (json.JSONDecodeError, OSError):
                plan_id = p.stem
            if wave_rendered_dir and wave_rendered_dir.exists():
                rend_dir = wave_rendered_dir / plan_id
                if not rend_dir.exists():
                    rend_dir = wave_rendered_dir / p.stem
            else:
                rend_dir = REPO_ROOT / "artifacts" / "rendered" / plan_id
                if not rend_dir.exists():
                    rend_dir = REPO_ROOT / "artifacts" / "rendered" / p.stem
            required_file = rend_dir / REQUIRED_RENDERED_FILE
            if not required_file.exists():
                missing.append(str(required_file))
                if args.strict:
                    continue
                # permissive: still add plan so we export partial
            paths.append(p)
        if paths:
            plan_paths_by_brand[brand_id] = paths
    if missing and args.strict:
        print("Feasibility guard (strict): missing plan or required rendered path (e.g. .../book.txt):", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1

    # Idempotent: remove existing content under base_out (brand dirs and zips), keep base_out
    for child in list(base_out.iterdir()):
        if child.is_dir() and not child.name.startswith("."):
            shutil.rmtree(child, ignore_errors=True)
        elif child.suffix == ".zip":
            child.unlink(missing_ok=True)

    run_id = str(uuid.uuid4())
    scheduler_config = _load_yaml(REPO_ROOT / "config" / "release_velocity" / "release_scheduler.yaml")
    report_export: dict = {
        "run_id": run_id,
        "week": week_key,
        "export": {"success": True, "brand_count": 0, "errors": []},
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    for brand_id, plan_paths in plan_paths_by_brand.items():
        brand_dir = base_out / brand_id
        brand_dir.mkdir(parents=True, exist_ok=True)
        (brand_dir / "book_files").mkdir(exist_ok=True)
        (brand_dir / "cover").mkdir(exist_ok=True)

        MANIFEST_COLUMNS = _load_manifest_columns()
        # upload_manifest.csv (headers/rows per upload_manifest_csv_v1)
        rows: list[dict] = []
        plan_stems: set[str] = set()
        for plan_path in plan_paths:
            plan_stems.add(plan_path.stem)
            try:
                plan = json.loads(plan_path.read_text())
            except (json.JSONDecodeError, OSError) as e:
                report_export["export"]["errors"].append(f"{brand_id}: {plan_path}: {e}")
                continue
            row = _plan_to_manifest_row(plan, REPO_ROOT)
            for col in MANIFEST_COLUMNS:
                if col not in row:
                    row[col] = ""
            rows.append(row)

            # Copy plan into book_files
            dest_plan = brand_dir / "book_files" / plan_path.name
            shutil.copy2(plan_path, dest_plan)

            # Rendered: wave or artifacts/rendered/<plan_id>
            plan_id = plan.get("plan_id") or plan.get("plan_hash") or plan_path.stem
            if wave_rendered_dir and wave_rendered_dir.exists():
                src_rendered = wave_rendered_dir / plan_id
                if not src_rendered.exists():
                    src_rendered = wave_rendered_dir / plan_path.stem
            else:
                src_rendered = REPO_ROOT / "artifacts" / "rendered" / plan_id
                if not src_rendered.exists():
                    src_rendered = REPO_ROOT / "artifacts" / "rendered" / plan_path.stem
            if src_rendered.exists():
                dest_rendered = brand_dir / "book_files" / f"{plan_id}_rendered"
                if dest_rendered.exists():
                    shutil.rmtree(dest_rendered)
                shutil.copytree(src_rendered, dest_rendered)

            # Cover: from plan cover_asset if present
            cover_src = plan.get("cover_asset") or plan.get("cover_path")
            if cover_src:
                cp = Path(cover_src) if Path(cover_src).is_absolute() else REPO_ROOT / cover_src
                if cp.exists():
                    shutil.copy2(cp, brand_dir / "cover" / f"{plan_id}_cover{cp.suffix}")

        with open(brand_dir / "upload_manifest.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

        # advisory_report.json
        issues = _gather_advisory_issues(args.prepublish_report, plan_stems)
        advisory_report = {
            "schema_version": "1.0",
            "week": week_key,
            "brand_id": brand_id,
            "issues": issues,
        }
        _validate_advisory_report(advisory_report)
        (brand_dir / "advisory_report.json").write_text(json.dumps(advisory_report, indent=2), encoding="utf-8")

        # release_day.txt
        release_day = _release_day_for_brand(week_start, brand_id, scheduler_config)
        (brand_dir / "release_day.txt").write_text(release_day + "\n", encoding="utf-8")

        # Zip
        zip_path = base_out / f"{week_key}_{brand_id}_packet.zip"
        shutil.make_archive(str(zip_path.with_suffix("")), "zip", base_out, brand_id)

        report_export["export"]["brand_count"] = report_export["export"]["brand_count"] + 1

    report_export["export"]["success"] = len(report_export["export"]["errors"]) == 0
    report_path = base_out / "packet_delivery_report.json"
    existing = {}
    if report_path.exists():
        try:
            existing = json.loads(report_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    existing["run_id"] = run_id
    existing["week"] = week_key
    existing["export"] = report_export["export"]
    existing["timestamp"] = report_export["timestamp"]
    if "upload" not in existing:
        existing["upload"] = {}
    if "notify" not in existing:
        existing["notify"] = {}
    report_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    print(f"Exported {report_export['export']['brand_count']} brand(s) to {base_out}")
    for z in sorted(base_out.glob("*.zip")):
        print(f"  {z.name}")
    return 0 if report_export["export"]["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
