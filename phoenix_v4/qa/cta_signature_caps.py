"""
CTA signature index + caps (per brand/quarter).

Authority: specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md §10, §10.5.
Config: config/freebies/cta_anti_spam.yaml (max_same_cta_signature_per_brand_per_quarter).

Reads plan rows (from artifacts/freebies/index.jsonl or --index), groups by (brand_id, quarter),
counts by cta_signature (cta_template_id + freebie_slug). Fails when any (brand, quarter)
exceeds the cap. Optionally writes artifacts/freebies/cta_signature_index.jsonl.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FREEBIES = REPO_ROOT / "config" / "freebies"
ARTIFACTS_FREEBIES = REPO_ROOT / "artifacts" / "freebies"


def _load_yaml(p: Path) -> dict:
    try:
        import yaml
        if p.exists():
            with open(p, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except ImportError:
        pass
    return {}


def _cta_signature(row: dict[str, Any]) -> str:
    """Normalized CTA wording key: template + slug."""
    cta = str(row.get("cta_template_id") or "").strip()
    slug = str(row.get("freebie_slug") or row.get("slug") or "").strip()
    return f"{cta}|{slug}" if cta or slug else ""


def _quarter_from_row(row: dict[str, Any]) -> str:
    """Derive quarter for grouping: release_week (e.g. 2026-W09 -> 2026-Q1) or 'unknown'."""
    rw = row.get("release_week") or row.get("release_week_id") or row.get("publish_week") or ""
    if isinstance(rw, str) and rw:
        # "2026-W09" -> "2026-Q1"; simple: first 4 chars + "-Q" + quarter from week
        try:
            year = rw[:4]
            if len(rw) >= 8 and rw[5:6] == "W":
                w = int(rw[6:8])
                q = (w - 1) // 13 + 1
                return f"{year}-Q{min(4, max(1, q))}"
        except (ValueError, TypeError):
            pass
        return rw[:7] if len(rw) >= 7 else rw or "unknown"
    return "unknown"


def _normalize_plan_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dedupe by book_id (last wins)."""
    plan_rows = [r for r in rows if isinstance(r, dict) and (r.get("freebie_bundle") is not None or r.get("cta_template_id") is not None)]
    if not plan_rows:
        return []
    dedup: dict[str, dict[str, Any]] = {}
    ordered: list[str] = []
    for i, row in enumerate(plan_rows):
        key = str(row.get("book_id") or row.get("plan_id") or row.get("plan_hash") or f"row:{i}")
        if key not in dedup:
            ordered.append(key)
        dedup[key] = row
    return [dedup[k] for k in ordered]


def run(
    rows: list[dict[str, Any]],
    max_same_per_brand_per_quarter: int = 5,
) -> tuple[bool, list[str]]:
    """
    Check CTA signature caps per (brand_id, quarter). Returns (passed, list of failure messages).
    """
    plan_rows = _normalize_plan_rows(rows)
    if not plan_rows:
        return True, []

    # (brand_id, quarter) -> { cta_signature -> count }
    by_brand_quarter: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    index_rows: list[dict[str, Any]] = []

    for r in plan_rows:
        brand = str(r.get("brand_id") or "phoenix")
        quarter = _quarter_from_row(r)
        sig = _cta_signature(r)
        if not sig:
            continue
        by_brand_quarter[(brand, quarter)][sig] += 1
        index_rows.append({
            "book_id": r.get("book_id") or r.get("plan_id") or r.get("plan_hash"),
            "brand_id": brand,
            "quarter": quarter,
            "cta_signature": sig,
        })

    failures: list[str] = []
    for (brand, quarter), counts in by_brand_quarter.items():
        for sig, cnt in counts.items():
            if cnt > max_same_per_brand_per_quarter:
                failures.append(
                    f"CTA signature cap exceeded: brand={brand} quarter={quarter} "
                    f"cta_signature={sig[:60]}... count={cnt} cap={max_same_per_brand_per_quarter}"
                )

    return (len(failures) == 0, failures)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="CTA signature caps per brand/quarter (PHOENIX_FREEBIE_SYSTEM_SPEC §10.5)"
    )
    ap.add_argument("--index", default=None, help="Path to artifacts/freebies/index.jsonl (or plan rows JSONL)")
    ap.add_argument("--plans-dir", default=None, help="Directory of compiled plan JSON files (same scope as validate_freebie_density)")
    ap.add_argument("--last-n", type=int, default=None, help="When using --index: use only last N plan rows after dedupe. Wave scope.")
    ap.add_argument("--config", default=None, help="Path to config/freebies/cta_anti_spam.yaml")
    ap.add_argument("--write-index", action="store_true", help="Write cta_signature_index.jsonl to artifacts/freebies")
    args = ap.parse_args()

    index_path = Path(args.index) if args.index else (ARTIFACTS_FREEBIES / "index.jsonl")
    config_path = Path(args.config) if args.config else (CONFIG_FREEBIES / "cta_anti_spam.yaml")

    rows: list[dict[str, Any]] = []
    if args.plans_dir:
        pdir = Path(args.plans_dir)
        if pdir.is_dir():
            for f in sorted(pdir.iterdir()):
                if f.suffix != ".json":
                    continue
                try:
                    with open(f, encoding="utf-8") as fp:
                        plan = json.load(fp)
                    rows.append({
                        "book_id": plan.get("plan_id") or plan.get("plan_hash") or f.stem,
                        "freebie_bundle": plan.get("freebie_bundle") or [],
                        "cta_template_id": plan.get("cta_template_id") or "",
                        "freebie_slug": plan.get("freebie_slug") or "",
                        "slug": plan.get("freebie_slug") or "",
                        "brand_id": plan.get("brand_id"),
                        "release_week": plan.get("release_week"),
                    })
                except (json.JSONDecodeError, OSError):
                    pass
    if not rows and index_path.exists():
        with open(index_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    # Same scope as density: optional last-n (wave)
    plan_rows = _normalize_plan_rows(rows)
    if getattr(args, "last_n", None) is not None and getattr(args, "last_n", None) > 0:
        plan_rows = plan_rows[-args.last_n:]
    rows = plan_rows

    cfg = _load_yaml(config_path)
    caps = (cfg.get("cta_signature_caps") or {})
    max_same = int(caps.get("max_same_cta_signature_per_brand_per_quarter", 5))

    passed, failures = run(rows, max_same_per_brand_per_quarter=max_same)

    if args.write_index and rows:
        out_path = ARTIFACTS_FREEBIES / "cta_signature_index.jsonl"
        plan_rows = _normalize_plan_rows(rows)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for r in plan_rows:
                sig = _cta_signature(r)
                if sig:
                    f.write(json.dumps({
                        "book_id": r.get("book_id") or r.get("plan_id") or r.get("plan_hash"),
                        "brand_id": str(r.get("brand_id") or "phoenix"),
                        "quarter": _quarter_from_row(r),
                        "cta_signature": sig,
                    }, ensure_ascii=False) + "\n")

    if not passed:
        print("CTA SIGNATURE CAPS: FAIL", file=sys.stderr)
        for msg in failures:
            print(f" - {msg}", file=sys.stderr)
        return 2
    print("CTA SIGNATURE CAPS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
