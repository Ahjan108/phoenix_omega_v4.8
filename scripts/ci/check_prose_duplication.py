#!/usr/bin/env python3
"""
Prose duplication gate for pre-publish wave checks.

Deterministic, no embeddings/LLM:
- paragraph exact-match collisions (SHA-256)
- opening 12-word collision
- closing sentence collision
- 6-gram Jaccard overlap

Exit codes:
- 0: pass (may include warnings)
- 1: fail
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


WORD_RE = re.compile(r"\b[\w']+\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    text = re.sub(r"[ \t]+", " ", text)
    return text


def words(text: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def opening_12(text: str) -> str:
    ws = words(text)
    return " ".join(ws[:12]) if ws else ""


def closing_sentence(text: str) -> str:
    parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p.strip()]
    return parts[-1].lower() if parts else ""


def split_paragraphs(text: str) -> List[str]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    return blocks


def hash_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def ngrams(ws: Sequence[str], n: int = 6) -> set[str]:
    if len(ws) < n:
        return set()
    return {" ".join(ws[i : i + n]) for i in range(len(ws) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


@dataclass
class DocFeatures:
    book_id: str
    path: str
    opening12: str
    closing_sentence: str
    paragraph_hashes: set[str]
    ngram6: set[str]


def load_doc(path: Path) -> DocFeatures:
    text = normalize_text(path.read_text(encoding="utf-8", errors="replace"))
    paras = [normalize_text(p).lower() for p in split_paragraphs(text)]
    para_hashes = {hash_str(p) for p in paras if p}
    ws = words(text)
    return DocFeatures(
        book_id=path.stem,
        path=str(path),
        opening12=opening_12(text),
        closing_sentence=closing_sentence(text),
        paragraph_hashes=para_hashes,
        ngram6=ngrams(ws, n=6),
    )


def collect_txt_files(dir_path: Path) -> List[Path]:
    if not dir_path.exists():
        return []
    return sorted([p for p in dir_path.rglob("*.txt") if p.is_file()])


def compare_docs(
    wave_docs: List[DocFeatures],
    corpus_docs: List[DocFeatures],
    fail_ngram_jaccard: float,
    warn_ngram_jaccard: float,
) -> Tuple[List[Dict], List[Dict]]:
    failures: List[Dict] = []
    warnings: List[Dict] = []

    # Wave-vs-wave
    for i in range(len(wave_docs)):
        for j in range(i + 1, len(wave_docs)):
            a, b = wave_docs[i], wave_docs[j]
            _compare_pair(a, b, "wave", fail_ngram_jaccard, warn_ngram_jaccard, failures, warnings)

    # Wave-vs-corpus
    for a in wave_docs:
        for b in corpus_docs:
            if a.book_id == b.book_id:
                continue
            _compare_pair(a, b, "catalog", fail_ngram_jaccard, warn_ngram_jaccard, failures, warnings)

    return failures, warnings


def _compare_pair(
    a: DocFeatures,
    b: DocFeatures,
    scope: str,
    fail_ngram_jaccard: float,
    warn_ngram_jaccard: float,
    failures: List[Dict],
    warnings: List[Dict],
) -> None:
    if a.opening12 and a.opening12 == b.opening12:
        failures.append(
            {
                "type": "OPENING_12_COLLISION",
                "scope": scope,
                "left_book_id": a.book_id,
                "right_book_id": b.book_id,
            }
        )

    if a.closing_sentence and a.closing_sentence == b.closing_sentence:
        failures.append(
            {
                "type": "CLOSING_SENTENCE_COLLISION",
                "scope": scope,
                "left_book_id": a.book_id,
                "right_book_id": b.book_id,
            }
        )

    shared_para = len(a.paragraph_hashes & b.paragraph_hashes)
    if shared_para > 0:
        failures.append(
            {
                "type": "PARAGRAPH_EXACT_MATCH",
                "scope": scope,
                "left_book_id": a.book_id,
                "right_book_id": b.book_id,
                "shared_paragraph_count": shared_para,
            }
        )

    sim = jaccard(a.ngram6, b.ngram6)
    if sim >= fail_ngram_jaccard:
        failures.append(
            {
                "type": "NGRAM6_JACCARD_FAIL",
                "scope": scope,
                "left_book_id": a.book_id,
                "right_book_id": b.book_id,
                "score": round(sim, 4),
                "threshold": fail_ngram_jaccard,
            }
        )
    elif sim >= warn_ngram_jaccard:
        warnings.append(
            {
                "type": "NGRAM6_JACCARD_WARN",
                "scope": scope,
                "left_book_id": a.book_id,
                "right_book_id": b.book_id,
                "score": round(sim, 4),
                "threshold": warn_ngram_jaccard,
            }
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Prose duplication pre-publish gate")
    ap.add_argument("--wave-rendered-dir", required=True, help="Rendered .txt files for current release wave")
    ap.add_argument("--catalog-rendered-dir", default="", help="Rendered .txt files for existing catalog (optional)")
    ap.add_argument("--fail-ngram-jaccard", type=float, default=0.35)
    ap.add_argument("--warn-ngram-jaccard", type=float, default=0.25)
    ap.add_argument("--report", default="", help="Optional JSON report path")
    args = ap.parse_args()

    wave_dir = Path(args.wave_rendered_dir)
    catalog_dir = Path(args.catalog_rendered_dir) if args.catalog_rendered_dir else None

    wave_files = collect_txt_files(wave_dir)
    if not wave_files:
        print(f"PROSE DUPLICATION: FAIL (no .txt files in wave dir: {wave_dir})")
        return 1

    wave_docs = [load_doc(p) for p in wave_files]
    catalog_docs = [load_doc(p) for p in collect_txt_files(catalog_dir)] if catalog_dir else []

    failures, warnings = compare_docs(
        wave_docs=wave_docs,
        corpus_docs=catalog_docs,
        fail_ngram_jaccard=args.fail_ngram_jaccard,
        warn_ngram_jaccard=args.warn_ngram_jaccard,
    )

    report = {
        "wave_rendered_dir": str(wave_dir),
        "catalog_rendered_dir": str(catalog_dir) if catalog_dir else "",
        "wave_books": len(wave_docs),
        "catalog_books": len(catalog_docs),
        "failures": failures,
        "warnings": warnings,
        "pass": len(failures) == 0,
    }

    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wrote {out}")

    if failures:
        print("PROSE DUPLICATION: FAIL")
        for f in failures[:20]:
            print(" -", json.dumps(f, ensure_ascii=False))
        return 1

    print("PROSE DUPLICATION: PASS")
    if warnings:
        print(f" - WARNINGS: {len(warnings)} (non-blocking)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

