#!/usr/bin/env python3
"""
Opener/Closer Collision Gate (P1).

Exact-match only: opening collision (first two sentences), final integration line collision.
Blocking in prepublish.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _first_two_sentences(text: str) -> str:
    """Return first two sentences (by . ! ?) normalized for comparison."""
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()
    # Split on sentence boundaries
    parts = re.split(r'(?<=[.!?])\s+', text)
    parts = [p.strip() for p in parts if p.strip()]
    two = " ".join(parts[:2]) if len(parts) >= 2 else (parts[0] if parts else "")
    return " ".join(two.split())


def _final_integration_line_from_plan(plan_path: Path) -> Optional[str]:
    """Extract final INTEGRATION prose from rendered book or from plan slot sequence.
    If no rendered file, we cannot check final line; return None (caller may skip or fail).
    """
    # Prefer rendered book: last INTEGRATION block text
    rendered_dir = plan_path.parent.parent / "rendered" if "plans" in str(plan_path) else plan_path.parent / "rendered"
    plan_id = plan_path.stem
    book_txt = rendered_dir / plan_id / "book.txt"
    if not book_txt.exists():
        return None
    text = book_txt.read_text(encoding="utf-8", errors="replace")
    # Find last block that looks like an integration (e.g. ## INTEGRATION or slot marker)
    # Simple heuristic: last paragraph before end or last 500 chars
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for p in reversed(paragraphs):
        if len(p) > 20 and not p.startswith("#"):
            return " ".join(p.split())[:500]
    return None


def _first_two_sentences_from_rendered(plan_path: Path) -> str:
    """Read rendered book and return first two sentences."""
    rendered_dir = plan_path.parent.parent / "rendered" if "plans" in str(plan_path) else plan_path.parent / "rendered"
    plan_id = plan_path.stem
    book_txt = rendered_dir / plan_id / "book.txt"
    if not book_txt.exists():
        return ""
    text = book_txt.read_text(encoding="utf-8", errors="replace")
    return _first_two_sentences(text)


def check_series_open_close_collision(
    plans_dir: Path,
    wave_rendered_dir: Optional[Path] = None,
) -> list[dict]:
    """
    For each series: exact opener (first two sentences) collision and final integration line collision.
    wave_rendered_dir: if set, look for book.txt under wave_rendered_dir / <plan_stem> / book.txt.
    """
    import json
    plan_files = sorted([p for p in plans_dir.glob("*.json") if p.is_file() and "spec" not in p.name.lower()])
    by_series: dict[str, list[Path]] = {}
    for p in plan_files:
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        if not data.get("series_id"):
            continue
        by_series.setdefault(data["series_id"], []).append(p)

    # Resolve rendered root: wave_rendered_dir or infer from plans_dir
    rendered_root = wave_rendered_dir or (plans_dir.parent / "rendered" if plans_dir.name == "plans" else plans_dir / "rendered")

    violations: list[dict] = []
    for series_id, paths in by_series.items():
        # Sort by installment
        with_inst: list[tuple[int, Path]] = []
        for path in paths:
            try:
                data = json.loads(path.read_text())
                inst = data.get("installment_number") or 0
                with_inst.append((inst, path))
            except Exception:
                continue
        with_inst.sort(key=lambda x: x[0])
        paths_ordered = [p for _, p in with_inst]

        openers: dict[str, list[str]] = {}
        closers: dict[str, list[str]] = {}
        for path in paths_ordered:
            stem = path.stem
            book_txt = rendered_root / stem / "book.txt"
            if book_txt.exists():
                text = book_txt.read_text(encoding="utf-8", errors="replace")
                op = _first_two_sentences(text)
                if op:
                    openers.setdefault(op, []).append(str(path))
                # Last paragraph as closer proxy
                paras = [p.strip() for p in text.split("\n\n") if p.strip() and not p.startswith("#")]
                if paras:
                    last = " ".join(paras[-1].split())[:500]
                    if last:
                        closers.setdefault(last, []).append(str(path))

        for op, path_list in openers.items():
            if len(path_list) > 1:
                violations.append({"rule": "opening_collision", "series_id": series_id, "plan_paths": path_list})
        for cl, path_list in closers.items():
            if len(path_list) > 1:
                violations.append({"rule": "final_integration_line_collision", "series_id": series_id, "plan_paths": path_list})
    return violations


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Series opener/closer collision (P1): exact first-two-sentences and final integration line")
    ap.add_argument("--plans-dir", type=Path, required=True, help="Directory of compiled plan JSONs")
    ap.add_argument("--wave-rendered-dir", type=Path, default=None, help="Rendered book.txt root (e.g. artifacts/waves/<id>/rendered)")
    args = ap.parse_args()

    violations = check_series_open_close_collision(args.plans_dir, args.wave_rendered_dir)
    if violations:
        print("CHECK_SERIES_OPEN_CLOSE_COLLISION: FAIL")
        for v in violations:
            print(f"  {v}")
        return 1
    print("CHECK_SERIES_OPEN_CLOSE_COLLISION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
