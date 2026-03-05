#!/usr/bin/env python3
"""
Build teacher knowledge base from raw files (RTF, txt, md).
Writes kb/index.json and optionally chunked text to kb/chunks/.
Authority: specs/TEACHER_MODE_V4_CANONICAL_SPEC.md §10.
Runtime never reads this; offline only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_TEACHER = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_TEACHER))

from rtf_to_text import rtf_to_text


def _source_of_truth_teacher_banks() -> Path:
    return REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"


def _raw_dir(teacher_id: str) -> Path:
    return _source_of_truth_teacher_banks() / teacher_id / "raw"


def _kb_dir(teacher_id: str) -> Path:
    return _source_of_truth_teacher_banks() / teacher_id / "kb"


def extract_text(path: Path) -> str:
    """Extract plain text from file. RTF -> strip; .txt/.md -> read."""
    suffix = path.suffix.lower()
    raw = path.read_bytes()
    if suffix == ".rtf":
        return rtf_to_text(raw)
    if suffix in (".txt", ".md"):
        return raw.decode("utf-8", errors="replace")
    # Fallback: try decode as text
    return raw.decode("utf-8", errors="replace")


def build_index(teacher_id: str, exclude_doc_ids: list[str] | None = None) -> dict:
    """Build KB index: doc_id -> path, text, byte_start, byte_end, hash."""
    raw = _raw_dir(teacher_id)
    kb = _kb_dir(teacher_id)
    exclude = set(exclude_doc_ids or [])
    index: dict = {"teacher_id": teacher_id, "documents": [], "chunks": []}
    doc_list = []
    for path in sorted(raw.rglob("*")):
        if path.is_dir():
            continue
        if path.name.startswith(".") or path.suffix.lower() not in (".rtf", ".txt", ".md"):
            continue
        rel = path.relative_to(raw)
        doc_id = f"raw/{rel.as_posix()}"
        if rel.as_posix() in exclude or path.name in exclude or doc_id in exclude:
            continue
        text = extract_text(path)
        if not text.strip():
            continue
        entry = {
            "doc_id": doc_id,
            "path": rel.as_posix(),
            "text": text,
            "char_count": len(text),
            "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
        }
        doc_list.append(entry)
        # Simple chunking: by paragraph (double newline) or ~600 chars
        chunk_size = 600
        start = 0
        chunk_idx = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                # Break at sentence or space
                for sep in (". ", "\n", " "):
                    last = text.rfind(sep, start, end + 1)
                    if last > start:
                        end = last + len(sep)
                        break
            chunk_text = text[start:end].strip()
            if chunk_text:
                index["chunks"].append({
                    "doc_id": doc_id,
                    "chunk_index": chunk_idx,
                    "span": [start, end],
                    "text": chunk_text,
                    "quote_hash": hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()[:16],
                })
                chunk_idx += 1
            start = end
    index["documents"] = doc_list
    return index


def main() -> int:
    ap = argparse.ArgumentParser(description="Build teacher KB from raw/ (RTF, txt, md)")
    ap.add_argument("--teacher", required=True, help="Teacher id (e.g. ahjan)")
    ap.add_argument("--out", default=None, help="Override kb output dir (default: SOURCE_OF_TRUTH/teacher_banks/<teacher>/kb)")
    ap.add_argument("--exclude", nargs="*", help="Exclude doc paths from index (e.g. comparison videos AM.rtf)")
    args = ap.parse_args()
    teacher_id = args.teacher.strip().lower()
    raw = _raw_dir(teacher_id)
    if not raw.exists():
        print(f"Error: raw dir not found: {raw}", file=sys.stderr)
        return 1
    kb = Path(args.out) if args.out else _kb_dir(teacher_id)
    kb.mkdir(parents=True, exist_ok=True)
    index = build_index(teacher_id, exclude_doc_ids=args.exclude)
    out_file = kb / "index.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_file} ({len(index['documents'])} docs, {len(index['chunks'])} chunks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
