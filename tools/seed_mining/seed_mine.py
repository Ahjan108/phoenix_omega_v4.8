#!/usr/bin/env python3
"""
Minimal seed mining: read source file(s), chunk by paragraph or word count, write candidate CANONICAL-style blocks.
No LLM. Output is staging for review and validation; then tag_existing_atoms and move to atoms/.../CANONICAL.txt.
Usage:
  python -m tools.seed_mining.seed_mine --input draft.txt --persona nyc_executives --topic anxiety --engine overwhelm --out get_these/nyc_anxiety_overwhelm_candidate.txt
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

DEFAULT_ROLE = "RECOGNITION"
DEFAULT_BAND = 3


def _chunk_by_paragraphs(text: str, max_chunk_words: int | None) -> list[str]:
    """Split text into chunks. Each chunk is one or more paragraphs, optionally capped by max_chunk_words."""
    blocks = re.split(r"\n\s*\n", text.strip())
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0
    for blk in blocks:
        blk = blk.strip()
        if not blk:
            continue
        w = len(blk.split())
        if max_chunk_words and current_words + w > max_chunk_words and current:
            chunks.append("\n\n".join(current))
            current = []
            current_words = 0
        current.append(blk)
        current_words += w
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _read_sources(input_path: Path) -> str:
    """Read file or all .txt/.md in directory."""
    if input_path.is_file():
        return input_path.read_text(encoding="utf-8", errors="replace")
    text_parts = []
    for f in sorted(input_path.rglob("*")):
        if f.suffix.lower() in (".txt", ".md") and f.is_file():
            text_parts.append(f.read_text(encoding="utf-8", errors="replace"))
    return "\n\n".join(text_parts)


def mine(
    input_path: Path,
    persona: str,
    topic: str,
    engine: str,
    out_path: Path,
    role: str = DEFAULT_ROLE,
    band: int = DEFAULT_BAND,
    max_chunk_words: int | None = 400,
) -> None:
    """Read source, chunk, write candidate CANONICAL-style file."""
    text = _read_sources(input_path)
    chunks = _chunk_by_paragraphs(text, max_chunk_words)
    lines = []
    path_prefix = f"atoms/{persona}/{topic}/{engine}"
    for i, prose in enumerate(chunks, 1):
        ver = f"v{i:02d}"
        path_line = f"path: {path_prefix}/recognition_{ver}.txt"
        lines.append(f"## {role} {ver}")
        lines.append("---")
        lines.append(path_line)
        lines.append(f"BAND: {band}")
        lines.append("---")
        lines.append(prose.strip())
        lines.append("---")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Seed mine: source → candidate CANONICAL blocks")
    ap.add_argument("--input", "-i", type=Path, required=True, help="Input file or directory")
    ap.add_argument("--persona", required=True, help="Persona slug")
    ap.add_argument("--topic", required=True, help="Topic slug")
    ap.add_argument("--engine", required=True, help="Engine slug")
    ap.add_argument("--out", "-o", type=Path, required=True, help="Output candidate CANONICAL-style file")
    ap.add_argument("--role", default=DEFAULT_ROLE, help="Placeholder role for all blocks")
    ap.add_argument("--band", type=int, default=DEFAULT_BAND, help="Placeholder BAND 1-5")
    ap.add_argument("--max-chunk-words", type=int, default=400, help="Max words per chunk (0 = no limit)")
    args = ap.parse_args()
    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 1
    mine(
        args.input,
        persona=args.persona,
        topic=args.topic,
        engine=args.engine,
        out_path=args.out,
        role=args.role,
        band=args.band,
        max_chunk_words=args.max_chunk_words or None,
    )
    print("Wrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
