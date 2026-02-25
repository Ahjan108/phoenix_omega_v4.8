#!/usr/bin/env python3
"""
phoenix_v4/quality/marketing_assets_from_lines.py

Takes memorable_line_detector JSON and generates marketing assets:
- quotes.csv
- pin_captions.txt
- landing_page_hooks.txt
- trailer_lines.txt
- email_subject_lines.txt

Usage:
  PYTHONPATH=. python3 phoenix_v4/quality/marketing_assets_from_lines.py \
    --mem-lines artifacts/ops/mem_lines.json \
    --brand phoenix \
    --topic overthinking \
    --persona nurses \
    --out-dir artifacts/marketing/book_002
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List


def sanitize_quote(q: str) -> str:
    q = q.strip()
    q = re.sub(r"\s+", " ", q)
    return q


def load_mem_lines(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pick_top_candidates(data: Dict, n: int = 25) -> List[Dict]:
    cands = data.get("candidates", [])
    return cands[:n]


def make_pin_caption(quote: str, brand: str, topic: str, persona: str) -> str:
    return f"{quote} — {brand} • {topic} for {persona}"


def make_hook(quote: str, topic: str) -> str:
    return f"{quote} (A new way to understand {topic}.)"


def make_trailer_line(quote: str) -> str:
    return f"{quote}"


def make_email_subject(quote: str) -> str:
    s = quote
    if len(s) > 60:
        s = s[:57].rstrip() + "…"
    return s


def write_quotes_csv(out_dir: Path, rows: List[Dict], meta: Dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "quotes.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "book_id",
                "brand",
                "topic",
                "persona",
                "quote",
                "score",
                "tags",
                "chapter_index",
                "sentence_index",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    meta["book_id"],
                    meta["brand"],
                    meta["topic"],
                    meta["persona"],
                    sanitize_quote(r["text"]),
                    r.get("score", ""),
                    " ".join(r.get("tags", [])),
                    r.get("chapter_index", ""),
                    r.get("sentence_index", ""),
                ]
            )


def generate_assets(
    mem_lines_data: Dict,
    brand: str,
    topic: str,
    persona: str,
    top_n: int = 25,
) -> Dict:
    """
    Generate marketing assets from memorable-line data (in-memory). Returns bundle-shaped
    tool result for book_quality_bundle: status, assets (quotes, pin_captions,
    landing_hooks, trailer_lines, email_subjects). Does not write files.
    """
    top = pick_top_candidates(mem_lines_data, n=top_n)
    quotes = [sanitize_quote(r["text"]) for r in top]
    pin_captions = [make_pin_caption(q, brand, topic, persona) for q in quotes]
    landing_hooks = [make_hook(q, topic) for q in quotes[:12]]
    trailer_lines = [make_trailer_line(q) for q in quotes[:15]]
    email_subjects = [make_email_subject(q) for q in quotes[:20]]
    return {
        "status": "pass",
        "assets": {
            "quotes": quotes,
            "pin_captions": pin_captions,
            "landing_hooks": landing_hooks,
            "trailer_lines": trailer_lines,
            "email_subjects": email_subjects,
        },
    }


def write_lines(out_dir: Path, filename: str, lines: List[str]) -> None:
    (out_dir / filename).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mem-lines", required=True, help="memorable_line_detector JSON")
    ap.add_argument("--brand", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--persona", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--top-n", type=int, default=25)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    mem_path = Path(args.mem_lines)
    if not mem_path.exists():
        print(f"Error: mem-lines file not found: {mem_path}", file=sys.stderr)
        return 1

    data = load_mem_lines(mem_path)

    meta = {
        "book_id": data.get("book_id", "unknown_book"),
        "brand": args.brand,
        "topic": args.topic,
        "persona": args.persona,
    }

    top = pick_top_candidates(data, n=args.top_n)

    quotes = [sanitize_quote(r["text"]) for r in top]

    pin_captions = [make_pin_caption(q, args.brand, args.topic, args.persona) for q in quotes]
    hooks = [make_hook(q, args.topic) for q in quotes[:12]]
    trailer_lines = [make_trailer_line(q) for q in quotes[:15]]
    email_subjects = [make_email_subject(q) for q in quotes[:20]]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    write_quotes_csv(out_dir, top, meta)
    write_lines(out_dir, "pin_captions.txt", pin_captions)
    write_lines(out_dir, "landing_page_hooks.txt", hooks)
    write_lines(out_dir, "trailer_lines.txt", trailer_lines)
    write_lines(out_dir, "email_subject_lines.txt", email_subjects)

    manifest = {
        "schema_version": "1.0",
        "book_id": meta["book_id"],
        "inputs": {
            "brand": meta["brand"],
            "topic": meta["topic"],
            "persona": meta["persona"],
            "mem_lines_path": str(mem_path.resolve()),
        },
        "outputs": {
            "quotes_csv": "quotes.csv",
            "pin_captions": "pin_captions.txt",
            "landing_page_hooks": "landing_page_hooks.txt",
            "trailer_lines": "trailer_lines.txt",
            "email_subject_lines": "email_subject_lines.txt",
        },
    }
    (out_dir / "marketing_assets_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Wrote marketing assets to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
