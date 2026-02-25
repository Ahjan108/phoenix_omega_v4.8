#!/usr/bin/env python3
"""
Generate a week-by-week release schedule from a wave or candidate list.

Two independent lanes (config/release_velocity/lanes.yaml):
  EN lane: English brands only; cap against Google Play Books only (no Findaway/Ximalaya).
  ZH24 lane: 24 Chinese brands; Findaway + Ximalaya, or sub-locale (zh_cn = local only; zh_tw_hk_sg = Findaway-eligible).
Default (no --lane): global = all platforms, conservative min cap.

Ramp: 1 series → 90 days → 30% growth to 6 months → 60 days toward target. Schedule is CAPPED
by the lane's platform caps; script fails hard if any brand/platform/week exceeds cap_max.

Output: schedule + platform_validation (platform, trust_tier, cap_min, cap_max, scheduled_count, blocked_excess).

Usage:
  # Global (conservative; Ximalaya clamps)
  python scripts/release/generate_weekly_schedule.py --candidates-dir ... --out schedule.json
  # EN lane: English only, Google cap (e.g. 20/wk new imprint)
  python scripts/release/generate_weekly_schedule.py --lane en --candidates-dir ... --out schedule_en.json
  # ZH24 lane: Chinese 24 brands
  python scripts/release/generate_weekly_schedule.py --lane zh24 --candidates-dir ... --out schedule_zh24.json
  # ZH24 sub-locale: zh-CN local only or TW/HK/SG Findaway-eligible
  python scripts/release/generate_weekly_schedule.py --lane zh24 --zh-sublocale zh_cn --out schedule_zh_cn.json
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_RAMP = REPO_ROOT / "config" / "release_velocity" / "velocity_ramp.yaml"
CONFIG_SAFE_VELOCITY = REPO_ROOT / "config" / "release_velocity" / "safe_velocity.yaml"
CONFIG_LANES = REPO_ROOT / "config" / "release_velocity" / "lanes.yaml"


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


def _resolve_lane_platforms(lanes_config: dict, lane: str | None, zh_sublocale: str | None) -> list[str] | None:
    """
    Return platform list for the given lane. None = use safe_velocity default (global).
    lane en -> lanes.en.platforms; lane zh24 -> lanes.zh24.sub_locales[zh_sublocale].platforms or lanes.zh24.platforms.
    """
    if not lane or not lanes_config:
        return None
    lanes = lanes_config.get("lanes") or {}
    lane_cfg = lanes.get(lane)
    if not lane_cfg:
        return None
    if lane == "zh24" and zh_sublocale:
        sub = (lane_cfg.get("sub_locales") or {}).get(zh_sublocale)
        if sub:
            return sub.get("platforms") or lane_cfg.get("platforms")
    return lane_cfg.get("platforms")


def _get_platform_caps(safe_config: dict, platform_list: list[str] | None = None) -> tuple[list[dict], int]:
    """
    Read safe_velocity: default_trust_tier_for_scheduling, trust_tier_platform_key, and
    per-platform cap ranges. If platform_list is given (from lane config), use only those
    platforms; else use platforms_for_schedule_validation (global). Return (caps_list, effective_cap).
    effective_cap = min over platforms of cap_max.
    """
    platforms = platform_list if platform_list is not None else (
        safe_config.get("platforms_for_schedule_validation") or [
            "google_play_books", "findaway_voices", "ximalaya"
        ]
    )
    trust_tier = safe_config.get("default_trust_tier_for_scheduling") or "new_imprint"
    tier_keys = safe_config.get("trust_tier_platform_key") or {}
    platform_keys = (tier_keys.get(trust_tier) or {}).copy()
    # Fallback keys per platform if not in map
    if "google_play_books" not in platform_keys:
        platform_keys["google_play_books"] = "new_imprint"
    if "findaway_voices" not in platform_keys:
        platform_keys["findaway_voices"] = "new_account"
    if "ximalaya" not in platform_keys:
        platform_keys["ximalaya"] = "verified_account"

    caps_list: list[dict] = []
    effective_cap = 999999
    for plat in platforms:
        plat_cfg = safe_config.get(plat) or {}
        key = platform_keys.get(plat)
        if not key:
            continue
        range_cfg = plat_cfg.get(key) or {}
        per_week = range_cfg.get("per_week") or [0, 999999]
        cap_min, cap_max = int(per_week[0]), int(per_week[1])
        caps_list.append({
            "platform": plat,
            "trust_tier": trust_tier,
            "cap_min": cap_min,
            "cap_max": cap_max,
        })
        if cap_max < effective_cap:
            effective_cap = cap_max
    return caps_list, effective_cap if effective_cap != 999999 else 84


def _validate_schedule_against_platforms(
    schedule: list[dict],
    caps_list: list[dict],
) -> list[dict]:
    """
    For each (week, brand) in schedule, check scheduled_count vs each platform cap_max.
    Return list of violations: {week, week_start, brand_id, platform, cap_max, scheduled_count, blocked_excess}.
    """
    violations: list[dict] = []
    for row in schedule:
        week = row.get("week")
        week_start = row.get("week_start", "")
        assignments = row.get("assignments") or {}
        for brand, paths in assignments.items():
            scheduled_count = len(paths) if isinstance(paths, list) else 0
            for c in caps_list:
                cap_max = c["cap_max"]
                if scheduled_count > cap_max:
                    violations.append({
                        "week": week,
                        "week_start": week_start,
                        "brand_id": brand,
                        "platform": c["platform"],
                        "trust_tier": c["trust_tier"],
                        "cap_max": cap_max,
                        "scheduled_count": scheduled_count,
                        "blocked_excess": scheduled_count - cap_max,
                    })
    return violations


def _build_platform_rows(schedule: list[dict], caps_list: list[dict]) -> list[dict]:
    """Build platform-aware rows: one per (week, brand, platform) with scheduled_count, cap_min, cap_max, blocked_excess."""
    rows: list[dict] = []
    for row in schedule:
        week = row.get("week")
        week_start = row.get("week_start", "")
        phase = row.get("phase", "")
        assignments = row.get("assignments") or {}
        for brand, paths in assignments.items():
            scheduled_count = len(paths) if isinstance(paths, list) else 0
            for c in caps_list:
                cap_min, cap_max = c["cap_min"], c["cap_max"]
                blocked = max(0, scheduled_count - cap_max)
                rows.append({
                    "week": week,
                    "week_start": week_start,
                    "phase": phase,
                    "brand_id": brand,
                    "platform": c["platform"],
                    "trust_tier": c["trust_tier"],
                    "cap_min": cap_min,
                    "cap_max": cap_max,
                    "scheduled_count": scheduled_count,
                    "blocked_excess": blocked,
                })
    return rows


def _load_plan_brand(plan_path: Path) -> str | None:
    """Extract brand_id from compiled plan JSON if present."""
    if not plan_path.exists():
        return None
    try:
        data = json.loads(plan_path.read_text())
        return data.get("brand_id") or data.get("brand")
    except Exception:
        return None


def _load_wave_plans(wave_path: Path) -> list[Path]:
    """Return list of plan paths from wave file (one path per line)."""
    if not wave_path.exists():
        return []
    paths = []
    for line in wave_path.read_text().strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = Path(line)
        if not p.is_absolute():
            p = REPO_ROOT / p
        paths.append(p)
    return paths


def _gather_by_brand(plan_paths: list[Path], brand_from_plan: bool) -> dict[str, list[Path]]:
    """Group plan paths by brand_id. If brand_from_plan False, put all under 'default'."""
    by_brand: dict[str, list[Path]] = defaultdict(list)
    for p in plan_paths:
        if brand_from_plan:
            brand = _load_plan_brand(p)
            if not brand:
                brand = "default"
        else:
            brand = "default"
        by_brand[brand].append(p)
    return dict(by_brand)


def _stagger_count(low: int, high: int, seed: int | None = None) -> int:
    if seed is not None:
        random.seed(seed)
    return random.randint(low, high) if high >= low else low


def generate_schedule(
    by_brand: dict[str, list[Path]],
    ramp_config: dict,
    start_date: datetime,
    effective_platform_cap: int | None = None,
) -> list[dict]:
    """
    Produce week-by-week schedule. Each row: week_number, week_start, brand_id, count, plan_paths.
    Ramp: phase 1 (90 d), phase 2 (90 d), phase 3 (60 d) toward target. Phase 3 per-brand count
    is capped at effective_platform_cap (min over platforms from safe_velocity) so we never exceed.
    """
    ramp = ramp_config.get("target_books_per_week_per_brand") or [70, 84]
    target_low, target_high = ramp[0], ramp[1]
    # Cap target by platform-safe max so we don't generate an invalid schedule
    if effective_platform_cap is not None:
        target_high = min(target_high, effective_platform_cap)
        target_low = min(target_low, effective_platform_cap)
        if target_low > target_high:
            target_low = target_high
    phase1_days = 90
    phase2_days = 90
    phase3_days = ramp_config.get("target_ramp_weeks", 60)  # used as days for simplicity; script uses weeks

    total_weeks_phase1 = (phase1_days + 6) // 7
    total_weeks_phase2 = (phase2_days + 6) // 7
    total_weeks_phase3 = max(1, (phase3_days + 6) // 7)

    brands = list(by_brand.keys())
    total_books = sum(len(plans) for plans in by_brand.values())
    if total_books == 0:
        return []

    schedule: list[dict] = []
    week_start = start_date
    week_num = 0

    # Indices per brand for handing out books
    indices: dict[str, int] = {b: 0 for b in brands}
    plans_by_brand = {b: list(plans) for b, plans in by_brand.items()}

    # Phase 1: start with 1 series (approximate as few books in first weeks), build to ~10% of total by week 13
    phase1_weeks = total_weeks_phase1
    phase1_share = 0.10  # 10% of books released in phase 1
    books_phase1 = max(1, int(total_books * phase1_share))
    first_week_books = max(1, min(3, books_phase1 // 4))  # first week: 1–3 books total
    remaining_phase1 = books_phase1 - first_week_books
    per_week_phase1 = remaining_phase1 / max(1, phase1_weeks - 1) if phase1_weeks > 1 else 0

    for w in range(phase1_weeks):
        week_num += 1
        if w == 0:
            count_total = first_week_books
        else:
            count_total = max(0, int(per_week_phase1))
        _assign_books_to_week(schedule, week_num, week_start, brands, plans_by_brand, indices, count_total, "phase1")
        week_start += timedelta(days=7)

    # Phase 2: 30% growth in weekly rate; release ~25% of books
    phase2_weeks = total_weeks_phase2
    books_phase2 = int(total_books * 0.25)
    per_week_phase2 = books_phase2 / max(1, phase2_weeks)
    for w in range(phase2_weeks):
        week_num += 1
        count_total = max(0, int(per_week_phase2))
        _assign_books_to_week(schedule, week_num, week_start, brands, plans_by_brand, indices, count_total, "phase2")
        week_start += timedelta(days=7)

    # Phase 3: ramp toward target per brand per week (staggered), CAPPED by platform
    phase3_weeks = total_weeks_phase3
    remaining_total = total_books - books_phase1 - books_phase2
    if phase3_weeks > 0 and remaining_total > 0:
        for w in range(phase3_weeks):
            week_num += 1
            n_per_brand = _stagger_count(target_low, target_high, seed=week_num * 1000 + w)
            count_total = min(n_per_brand * len(brands), remaining_total)
            if count_total <= 0:
                break
            _assign_books_to_week(schedule, week_num, week_start, brands, plans_by_brand, indices, count_total, "phase3")
            week_start += timedelta(days=7)
            remaining_total -= count_total
            if remaining_total <= 0:
                break

    # Any remaining books: spread over weeks so we never exceed effective_platform_cap per brand per week
    if schedule and effective_platform_cap is not None:
        cap = effective_platform_cap
        while True:
            added = 0
            for b in brands:
                while indices[b] < len(plans_by_brand[b]) and len(schedule[-1]["assignments"].get(b, [])) < cap:
                    path = plans_by_brand[b][indices[b]]
                    indices[b] += 1
                    schedule[-1]["assignments"].setdefault(b, []).append(str(path))
                    added += 1
            if added == 0:
                break
            # If any brand still has books left, add a new week
            if any(indices[b] < len(plans_by_brand[b]) for b in brands):
                week_start += timedelta(days=7)
                week_num += 1
                schedule.append({
                    "week": week_num,
                    "week_start": week_start.strftime("%Y-%m-%d"),
                    "assignments": {},
                    "phase": "phase3",
                })
        return schedule

    # No cap: legacy behavior (dump all remaining into last week)
    if schedule:
        for b in brands:
            while indices[b] < len(plans_by_brand[b]):
                path = plans_by_brand[b][indices[b]]
                indices[b] += 1
                schedule[-1]["assignments"].setdefault(b, []).append(str(path))

    return schedule


def _assign_books_to_week(
    schedule: list[dict],
    week_num: int,
    week_start: datetime,
    brands: list[str],
    plans_by_brand: dict[str, list[Path]],
    indices: dict[str, int],
    count_total: int,
    phase: str,
) -> None:
    """Assign count_total books across brands (round-robin) and append to schedule."""
    assignments: dict[str, list[str]] = {b: [] for b in brands}
    count_per_brand = max(0, count_total // len(brands)) if brands else 0
    extra = count_total % len(brands) if brands else 0
    for i, b in enumerate(brands):
        n = count_per_brand + (1 if i < extra else 0)
        for _ in range(n):
            if indices[b] < len(plans_by_brand[b]):
                path = plans_by_brand[b][indices[b]]
                indices[b] += 1
                assignments[b].append(str(path))
    schedule.append({
        "week": week_num,
        "week_start": week_start.strftime("%Y-%m-%d"),
        "assignments": {b: p for b, p in assignments.items() if p},
        "phase": phase,
    })


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate week-by-week release schedule from wave or candidates. "
        "Use --lane to cap by that lane only (EN = Google only; ZH24 = Findaway + Ximalaya or sub-locale)."
    )
    ap.add_argument("--wave", type=Path, default=None, help="Wave file (one plan path per line)")
    ap.add_argument("--candidates-dir", type=Path, default=None, help="Directory of plan JSONs (instead of --wave)")
    ap.add_argument("--brand-from-plan", action="store_true", help="Read brand_id from each plan JSON (when using --candidates-dir)")
    ap.add_argument("--start-date", default=None, help="First week start (YYYY-MM-DD). Default: next Monday.")
    ap.add_argument("--out", type=Path, default=None, help="Output path (JSON or CSV)")
    ap.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    ap.add_argument(
        "--lane",
        choices=["en", "zh24"],
        default=None,
        help="Schedule lane: en = English brands only (Google cap); zh24 = 24 Chinese brands (Findaway + Ximalaya). Default = global (all platforms, conservative).",
    )
    ap.add_argument(
        "--zh-sublocale",
        choices=["zh_cn", "zh_tw_hk_sg"],
        default=None,
        help="When --lane zh24: zh_cn = local only (Ximalaya); zh_tw_hk_sg = Findaway-eligible. Omit for union caps.",
    )
    args = ap.parse_args()

    if not args.wave and not args.candidates_dir:
        print("Provide --wave or --candidates-dir.", file=sys.stderr)
        return 1

    if args.wave:
        plan_paths = _load_wave_plans(args.wave)
    else:
        candidates_dir = Path(args.candidates_dir)
        if not candidates_dir.is_dir():
            print(f"Not a directory: {candidates_dir}", file=sys.stderr)
            return 1
        plan_paths = []
        for f in sorted(candidates_dir.glob("*.json")):
            if f.suffix == ".json" and "spec" not in f.name.lower():
                plan_paths.append(f)
            elif f.suffix == ".json":
                plan_paths.append(f)

    if not plan_paths:
        print("No plan paths found.", file=sys.stderr)
        return 1

    ramp_config = _load_yaml(CONFIG_RAMP)
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid --start-date; use YYYY-MM-DD.", file=sys.stderr)
            return 1
    else:
        from datetime import date
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start_date = datetime.combine(today + timedelta(days=days_until_monday), datetime.min.time())

    safe_config = _load_yaml(CONFIG_SAFE_VELOCITY)
    lanes_config = _load_yaml(CONFIG_LANES)
    platform_list = _resolve_lane_platforms(lanes_config, args.lane, args.zh_sublocale)
    caps_list, effective_cap = _get_platform_caps(safe_config, platform_list=platform_list)

    by_brand = _gather_by_brand(plan_paths, args.brand_from_plan)
    schedule = generate_schedule(by_brand, ramp_config, start_date, effective_platform_cap=effective_cap)

    # Fail hard if any brand/platform/week exceeds that platform's cap
    violations = _validate_schedule_against_platforms(schedule, caps_list)
    if violations:
        print("ERROR: Schedule exceeds platform-safe caps. Fail.", file=sys.stderr)
        for v in violations:
            print(
                f"  week={v['week']} week_start={v['week_start']} brand={v['brand_id']} "
                f"platform={v['platform']} scheduled_count={v['scheduled_count']} cap_max={v['cap_max']} "
                f"blocked_excess={v['blocked_excess']}",
                file=sys.stderr,
            )
        return 1

    platform_rows = _build_platform_rows(schedule, caps_list)

    out = args.out or (REPO_ROOT / "artifacts" / "release_schedule.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "csv" or (args.out and args.out.suffix.lower() == ".csv"):
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["week", "week_start", "phase", "brand_id", "book_count", "plan_paths"])
            for row in schedule:
                for brand, paths in row.get("assignments", {}).items():
                    w.writerow([
                        row["week"],
                        row["week_start"],
                        row.get("phase", ""),
                        brand,
                        len(paths),
                        "|".join(paths),
                    ])
            w.writerow([])
            w.writerow(["week", "week_start", "phase", "brand_id", "platform", "trust_tier", "cap_min", "cap_max", "scheduled_count", "blocked_excess"])
            for r in platform_rows:
                w.writerow([
                    r["week"],
                    r["week_start"],
                    r["phase"],
                    r["brand_id"],
                    r["platform"],
                    r["trust_tier"],
                    r["cap_min"],
                    r["cap_max"],
                    r["scheduled_count"],
                    r["blocked_excess"],
                ])
    else:
        payload = {
            "lane": args.lane,
            "zh_sublocale": args.zh_sublocale,
            "platforms": [c["platform"] for c in caps_list],
            "effective_platform_cap": effective_cap,
            "schedule": schedule,
            "platform_validation": platform_rows,
        }
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lane_info = f" (lane={args.lane}" + (f", zh_sublocale={args.zh_sublocale}" if args.zh_sublocale else "") + ")" if args.lane else " (global)"
    print(f"Wrote {len(schedule)} weeks to {out}{lane_info} effective_platform_cap={effective_cap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
