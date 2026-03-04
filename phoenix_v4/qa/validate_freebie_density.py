#!/usr/bin/env python3
"""
Freebie density gate — Phase 3 (scale hardening). Do not run in Phase 1.
Authority: specs/PHOENIX_FREEBIE_SYSTEM_SPEC.md §10.

FAIL if across the wave:
- identical_bundle_ratio >= 0.40
- identical_cta_ratio >= 0.50
- identical_slug_pattern_ratio >= 0.60

Use --plans-dir (compiled plan JSONs with freebie_bundle, cta_template_id, freebie_slug)
or --index (artifacts/freebies/index.jsonl).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FREEBIES = REPO_ROOT / "config" / "freebies"
CTA_ANTI_SPAM = CONFIG_FREEBIES / "cta_anti_spam.yaml"

THRESHOLD_BUNDLE = 0.40
THRESHOLD_CTA = 0.50
THRESHOLD_SLUG = 0.60


def _load_thresholds() -> tuple[float, float, float]:
    """Load thresholds from config/freebies/cta_anti_spam.yaml if present."""
    if not CTA_ANTI_SPAM.exists():
        return THRESHOLD_BUNDLE, THRESHOLD_CTA, THRESHOLD_SLUG
    cfg = _load_yaml(CTA_ANTI_SPAM)
    dt = cfg.get("density_thresholds") or {}
    return (
        float(dt.get("identical_bundle_ratio", THRESHOLD_BUNDLE)),
        float(dt.get("identical_cta_ratio", THRESHOLD_CTA)),
        float(dt.get("identical_slug_pattern_ratio", THRESHOLD_SLUG)),
    )


def _load_yaml(p: Path) -> dict:
    try:
        import yaml
        if p.exists():
            with open(p, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except ImportError:
        pass
    return {}


def _mode_share(values: list[str]) -> tuple[float, str]:
    if not values:
        return 0.0, ""
    c = Counter(values)
    val, count = c.most_common(1)[0]
    return count / len(values), val


def _slug_pattern(slug: str) -> str:
    """Reduce slug to pattern for clustering (e.g. topic-persona only)."""
    if not slug:
        return ""
    parts = (slug or "").split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return slug


def _normalize_plan_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Keep only plan rows and dedupe by book_id (last row wins) so repeated reruns
    of the same plan do not inflate density ratios.
    """
    plan_rows = [r for r in rows if isinstance(r, dict) and "freebie_bundle" in r]
    if not plan_rows:
        return []
    dedup: dict[str, dict[str, Any]] = {}
    ordered_keys: list[str] = []
    for i, row in enumerate(plan_rows):
        key = str(row.get("book_id") or row.get("plan_id") or row.get("plan_hash") or f"row:{i}")
        if key not in dedup:
            ordered_keys.append(key)
        dedup[key] = row
    return [dedup[k] for k in ordered_keys]


def run(
    rows: list[dict[str, Any]],
    threshold_bundle: float = THRESHOLD_BUNDLE,
    threshold_cta: float = THRESHOLD_CTA,
    threshold_slug: float = THRESHOLD_SLUG,
) -> tuple[bool, list[str]]:
    """
    Check freebie density. Returns (passed, list of failure messages).
    Only considers plan rows (freebie_bundle present). Ignores artifact-only rows (file_path).
    """
    plan_rows = _normalize_plan_rows(rows)
    if len(plan_rows) < 2:
        return True, []

    bundles = []
    ctas = []
    slug_patterns = []
    for r in plan_rows:
        bundle = r.get("freebie_bundle")
        if isinstance(bundle, list):
            bundles.append("|".join(sorted(bundle)))
        else:
            bundles.append("")
        ctas.append(str(r.get("cta_template_id") or ""))
        slug_patterns.append(_slug_pattern(str(r.get("freebie_slug") or r.get("slug") or "")))

    failures = []

    bundle_share, _ = _mode_share(bundles)
    if bundle_share >= threshold_bundle:
        failures.append(
            f"identical freebie_bundle ratio {bundle_share:.0%} >= {threshold_bundle:.0%}"
        )

    cta_share, _ = _mode_share(ctas)
    if cta_share >= threshold_cta:
        failures.append(
            f"identical cta_template_id ratio {cta_share:.0%} >= {threshold_cta:.0%}"
        )

    slug_share, _ = _mode_share(slug_patterns)
    if slug_share >= threshold_slug:
        failures.append(
            f"identical slug_pattern ratio {slug_share:.0%} >= {threshold_slug:.0%}"
        )

    return (len(failures) == 0, failures)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Freebie density gate: FAIL if bundle/cta/slug clustering exceeds thresholds"
    )
    ap.add_argument(
        "--plans-dir",
        default=None,
        help="Directory of compiled plan JSON files (with freebie_bundle, cta_template_id, freebie_slug)",
    )
    ap.add_argument(
        "--index",
        default=None,
        help="Path to artifacts/freebies/index.jsonl",
    )
    ap.add_argument(
        "--threshold-bundle",
        type=float,
        default=THRESHOLD_BUNDLE,
        help=f"FAIL if identical bundle ratio >= this (default {THRESHOLD_BUNDLE})",
    )
    ap.add_argument(
        "--threshold-cta",
        type=float,
        default=THRESHOLD_CTA,
        help=f"FAIL if identical CTA ratio >= this (default {THRESHOLD_CTA})",
    )
    ap.add_argument(
        "--threshold-slug",
        type=float,
        default=THRESHOLD_SLUG,
        help=f"FAIL if identical slug pattern ratio >= this (default {THRESHOLD_SLUG})",
    )
    ap.add_argument(
        "--last-n",
        type=int,
        default=None,
        help="When using --index: use only the last N plan rows (after dedupe by book_id). Wave scope.",
    )
    args = ap.parse_args()

    rows: list[dict[str, Any]] = []

    if args.plans_dir:
        pdir = Path(args.plans_dir)
        if not pdir.is_dir():
            print(f"Not a directory: {pdir}", file=sys.stderr)
            return 1
        for f in sorted(pdir.iterdir()):
            if f.suffix != ".json":
                continue
            with open(f, encoding="utf-8") as fp:
                plan = json.load(fp)
            rows.append({
                "book_id": plan.get("plan_id") or plan.get("plan_hash") or f.stem,
                "freebie_bundle": plan.get("freebie_bundle") or [],
                "cta_template_id": plan.get("cta_template_id") or "",
                "slug": plan.get("freebie_slug") or "",
            })

    if args.index:
        idx = Path(args.index)
        if idx.exists():
            with open(idx, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rows.append(json.loads(line))

    if not rows:
        print("FREEBIE DENSITY: PASS (no plans or index)")
        return 0

    # Optional scope: last N plan rows (wave) when using index
    plan_rows = _normalize_plan_rows(rows)
    if getattr(args, "last_n", None) is not None and getattr(args, "last_n", None) > 0:
        plan_rows = plan_rows[-args.last_n:]
    if not plan_rows:
        print("FREEBIE DENSITY: PASS (no plan rows after scope filter)")
        return 0
    rows = plan_rows

    tb, tc, ts = _load_thresholds()
    # Config overrides built-in defaults; CLI args override config
    bundle_th = args.threshold_bundle if args.threshold_bundle != THRESHOLD_BUNDLE else tb
    cta_th = args.threshold_cta if args.threshold_cta != THRESHOLD_CTA else tc
    slug_th = args.threshold_slug if args.threshold_slug != THRESHOLD_SLUG else ts
    passed, failures = run(
        rows,
        threshold_bundle=bundle_th,
        threshold_cta=cta_th,
        threshold_slug=slug_th,
    )
    if not passed:
        print("FREEBIE DENSITY: FAIL", file=sys.stderr)
        for msg in failures:
            print(f" - {msg}", file=sys.stderr)
        return 2
    print("FREEBIE DENSITY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
