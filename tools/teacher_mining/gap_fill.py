#!/usr/bin/env python3
"""
Teacher Gap-Fill Pipeline: generate candidate atoms from gap report (offline).
Authority: specs/TEACHER_MODE_V4_CANONICAL_SPEC.md §10.
Loads gaps JSON; writes candidate atoms to teacher_banks/<teacher_id>/candidate_atoms/ and run report to artifacts.
With --kb-dir: loads teacher KB (index.json or text files) and fills candidate body from KB snippets (KB-driven).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_OF_TRUTH = REPO_ROOT / "SOURCE_OF_TRUTH"
TEACHER_BANKS = SOURCE_OF_TRUTH / "teacher_banks"
ARTIFACTS = REPO_ROOT / "artifacts"

# Default max words for a KB-derived body snippet (Writer Spec STORY min 120)
KB_SNIPPET_MAX_WORDS = 150


def _candidate_dir(teacher_id: str) -> Path:
    return TEACHER_BANKS / teacher_id / "candidate_atoms"


def _run_report_path(out_artifacts: Path | None) -> Path:
    out = out_artifacts or ARTIFACTS
    out.mkdir(parents=True, exist_ok=True)
    return out / "gap_fill_run_report.json"


def _load_kb_texts(kb_dir: Path) -> list[str]:
    """Load all document texts from teacher KB. Prefer index.json; else glob *.txt."""
    texts: list[str] = []
    index_path = kb_dir / "index.json"
    if index_path.exists():
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
            for doc in data.get("documents") or []:
                t = doc.get("text") or ""
                if isinstance(t, str) and t.strip():
                    texts.append(t.strip())
        except Exception:
            pass
    if not texts:
        for p in sorted(kb_dir.rglob("*.txt")):
            try:
                texts.append(p.read_text(encoding="utf-8").strip())
            except Exception:
                pass
    return texts


def _first_n_words(text: str, n: int = KB_SNIPPET_MAX_WORDS) -> str:
    """Return first n words of text, cleaned for prose."""
    if not text or n <= 0:
        return ""
    # Strip leading font/format cruft (e.g. "Helvetica; ;; ;; ")
    text = re.sub(r"^[\w\s;.]+\s{2,}", "", text, count=1).strip()
    words = text.split()
    return " ".join(words[:n]) if words else ""


def run_gap_fill(
    teacher_id: str,
    gaps_path: Path,
    out_candidate_dir: Path | None = None,
    out_report_path: Path | None = None,
    kb_dir: Path | None = None,
) -> tuple[int, dict]:
    """
    Load gaps.json; for each gap write a candidate atom stub (or KB-driven body when kb_dir set); write run report.
    Returns (number of candidates written, report dict).
    """
    if not gaps_path.exists():
        return 0, {"error": f"Gaps file not found: {gaps_path}"}

    data = json.loads(gaps_path.read_text())
    teacher_id_from_file = data.get("teacher_id") or teacher_id
    gaps = data.get("gaps") or {}
    topic = data.get("topic", "")
    persona = data.get("persona", "")
    format_id = data.get("format_id", "")

    kb_texts: list[str] = []
    if kb_dir and kb_dir.is_dir():
        kb_texts = _load_kb_texts(kb_dir)
    kb_index = 0

    def _next_kb_snippet() -> str:
        nonlocal kb_index
        if not kb_texts:
            return ""
        snippet = _first_n_words(kb_texts[kb_index % len(kb_texts)], KB_SNIPPET_MAX_WORDS)
        kb_index += 1
        return snippet

    candidate_root = out_candidate_dir or _candidate_dir(teacher_id_from_file)
    candidate_root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    source_label = "gap_fill_kb" if kb_texts else "gap_fill_stub"
    stub_content = {
        "teacher_id": teacher_id_from_file,
        "topic": topic,
        "persona": persona,
        "source": source_label,
        "source_refs": [],
    }

    for role, role_gaps in gaps.items():
        if not isinstance(role_gaps, dict):
            continue
        slot_dir = candidate_root / role
        slot_dir.mkdir(parents=True, exist_ok=True)
        for key, count in role_gaps.items():
            if not isinstance(count, int) or count <= 0:
                continue
            for i in range(min(count, 10)):
                atom_id = f"{teacher_id_from_file}_{role}_{key}_{i}_gap"
                path = slot_dir / f"{atom_id}.yaml"
                stub = {**stub_content, "atom_id": atom_id, "role": role, "band_or_type": key}
                if kb_texts:
                    snippet = _next_kb_snippet()
                    if snippet:
                        stub["body"] = f"[KB draft — review and edit before approval]\n\n{snippet}"
                try:
                    import yaml
                    path.write_text(yaml.dump(stub, default_flow_style=False, allow_unicode=True))
                    written.append(atom_id)
                except Exception:
                    path.write_text(json.dumps(stub, indent=2))

    report = {
        "teacher_id": teacher_id_from_file,
        "topic": topic,
        "persona": persona,
        "format_id": format_id,
        "gaps_loaded": list(gaps.keys()),
        "candidates_written": len(written),
        "candidate_ids": written[:50],
        "run_at": datetime.utcnow().isoformat() + "Z",
        "kb_driven": bool(kb_texts),
        "kb_docs_used": len(kb_texts) if kb_texts else 0,
    }
    report_path = out_report_path or _run_report_path(ARTIFACTS)
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    return len(written), report


def main() -> int:
    ap = argparse.ArgumentParser(description="Gap-fill: generate candidate atoms from gap report (TEACHER_MODE §10)")
    ap.add_argument("--teacher", required=True, help="Teacher ID")
    ap.add_argument("--gaps", required=True, help="Path to gaps JSON (from report_teacher_gaps.py)")
    ap.add_argument("--out", default=None, help="Candidate output dir (default: SOURCE_OF_TRUTH/teacher_banks/<teacher>/candidate_atoms)")
    ap.add_argument("--report", default=None, help="Run report path (default: artifacts/gap_fill_run_report.json)")
    ap.add_argument("--kb-dir", default=None, help="Teacher KB dir (e.g. SOURCE_OF_TRUTH/teacher_banks/<teacher>/kb); when set, candidate body filled from KB snippets")
    args = ap.parse_args()
    out_dir = Path(args.out) if args.out else None
    report_path = Path(args.report) if args.report else None
    kb_dir = Path(args.kb_dir) if args.kb_dir else None
    n, report = run_gap_fill(
        args.teacher,
        Path(args.gaps),
        out_candidate_dir=out_dir,
        out_report_path=report_path,
        kb_dir=kb_dir,
    )
    if report.get("error"):
        print(report["error"], file=sys.stderr)
        return 1
    print(f"Wrote {n} candidate(s) to {out_dir or _candidate_dir(args.teacher)}")
    print(f"Report: {report_path or _run_report_path(None)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
