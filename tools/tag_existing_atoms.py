#!/usr/bin/env python3
"""
Tag existing CANONICAL.txt atoms with narrative metadata. Dev Spec §2.8.
Interactive: prompt for MECHANISM_DEPTH, COST_TYPE, COST_INTENSITY, IDENTITY_STAGE, CALLBACK_ID, CALLBACK_PHASE.
Batch: apply values from CSV (atom_id, mechanism_depth, cost_type, ...).
Usage:
  python tools/tag_existing_atoms.py --atoms-dir atoms/nyc_executives/anxiety --mode interactive
  python tools/tag_existing_atoms.py --atoms-dir atoms/ --csv tags.csv --mode batch
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Narrative field names and valid values (from assembly_compiler / spec)
NARRATIVE_KEYS = [
    "MECHANISM_DEPTH",
    "COST_TYPE",
    "COST_INTENSITY",
    "IDENTITY_STAGE",
    "CALLBACK_ID",
    "CALLBACK_PHASE",
]
COST_TYPES = ("social", "internal", "opportunity", "identity")
IDENTITY_STAGES = ("pre_awareness", "destabilization", "experimentation", "self_claim")
CALLBACK_PHASES = ("setup", "escalation", "return")


def _find_canonical_files(atoms_dir: Path) -> list[Path]:
    """All CANONICAL.txt under atoms_dir (recursive)."""
    if not atoms_dir.exists():
        return []
    return sorted(atoms_dir.rglob("CANONICAL.txt"))


def _parse_blocks_with_prose(text: str) -> list[tuple[str, str, str, str]]:
    """
    Parse file into blocks. Each element: (header_line, metadata, prose, trailing).
    Header is e.g. "## RECOGNITION v01"; metadata between first --- and second ---; prose between second and third ---.
    """
    # Split by --- so we get [preamble?, header+\n, metadata, prose, header2+\n, metadata2, prose2, ...]
    parts = re.split(r"\n---\s*\n", text)
    blocks: list[tuple[str, str, str, str]] = []
    i = 0
    while i < len(parts):
        part = parts[i]
        if re.match(r"^##\s+[A-Z_]+\s+v\d+", part.strip()):
            header = part.strip()
            meta = parts[i + 1] if i + 1 < len(parts) else ""
            prose = parts[i + 2] if i + 2 < len(parts) else ""
            blocks.append((header, meta, prose, ""))
            i += 3
        else:
            i += 1
    return blocks


def _metadata_set_or_append(metadata: str, key: str, value: str | int | None) -> str:
    """Return new metadata string with key: value (replace existing line for key or append)."""
    if value is None or value == "":
        value_str = ""
    else:
        value_str = str(value).strip()
    lines = [ln for ln in metadata.splitlines() if not line_is_narrative_key(ln, key)]
    if value_str:
        lines.append(f"{key}: {value_str}")
    return "\n".join(lines) if lines else ""


def line_is_narrative_key(line: str, key: str) -> bool:
    return line.strip().upper().startswith(key + ":")


def _strip_narrative_from_metadata(metadata: str) -> str:
    """Remove any existing narrative key lines so we can add fresh ones."""
    out = []
    for line in metadata.splitlines():
        skip = False
        for k in NARRATIVE_KEYS:
            if line.strip().upper().startswith(k + ":"):
                skip = True
                break
        if not skip:
            out.append(line)
    return "\n".join(out).strip()


def _apply_narrative_to_metadata(
    metadata: str,
    mechanism_depth: int | None = None,
    cost_type: str | None = None,
    cost_intensity: int | None = None,
    identity_stage: str | None = None,
    callback_id: str | None = None,
    callback_phase: str | None = None,
) -> str:
    """Produce new metadata with narrative lines added/replaced."""
    base = _strip_narrative_from_metadata(metadata)
    if mechanism_depth is not None:
        base = _metadata_set_or_append(base, "MECHANISM_DEPTH", mechanism_depth)
    if cost_type:
        base = _metadata_set_or_append(base, "COST_TYPE", cost_type)
    if cost_intensity is not None:
        base = _metadata_set_or_append(base, "COST_INTENSITY", cost_intensity)
    if identity_stage:
        base = _metadata_set_or_append(base, "IDENTITY_STAGE", identity_stage)
    if callback_id is not None:
        base = _metadata_set_or_append(base, "CALLBACK_ID", callback_id or "")
    if callback_phase:
        base = _metadata_set_or_append(base, "CALLBACK_PHASE", callback_phase)
    return base


def _atom_id_from_block(path: Path, header: str) -> str:
    persona = path.parent.parent.parent.name
    topic = path.parent.parent.name
    engine = path.parent.name
    m = re.match(r"##\s+([A-Z_]+)\s+v(\d+)", header.strip())
    role, ver = m.group(1), m.group(2) if m else ("", "01")
    return f"{persona}_{topic}_{engine}_{role}_v{ver}"


def run_interactive(atoms_dir: Path) -> int:
    canonical_files = _find_canonical_files(atoms_dir)
    if not canonical_files:
        print("No CANONICAL.txt files found under", atoms_dir, file=sys.stderr)
        return 1
    updated = 0
    for path in canonical_files:
        text = path.read_text()
        blocks = _parse_blocks_with_prose(text)
        if not blocks:
            continue
        new_parts: list[str] = []
        for header, metadata, prose, _ in blocks:
            atom_id = _atom_id_from_block(path, header)
            prose_preview = (prose.strip()[:200] + "...") if len(prose.strip()) > 200 else prose.strip()
            print("\n---")
            print("Atom:", atom_id)
            print("Prose preview:", prose_preview or "(empty)")
            try:
                md = int(input("MECHANISM_DEPTH (1-4) [1]: ").strip() or "1")
            except ValueError:
                md = 1
            ct = (input("COST_TYPE (social|internal|opportunity|identity) [social]: ").strip() or "social").lower()
            if ct not in COST_TYPES:
                ct = "social"
            try:
                ci = int(input("COST_INTENSITY (1-5) [2]: ").strip() or "2")
            except ValueError:
                ci = 2
            is_ = (input("IDENTITY_STAGE (pre_awareness|destabilization|experimentation|self_claim) [pre_awareness]: ").strip() or "pre_awareness").lower()
            if is_ not in IDENTITY_STAGES:
                is_ = "pre_awareness"
            cid = input("CALLBACK_ID (or empty) []: ").strip() or None
            cphase = (input("CALLBACK_PHASE (setup|escalation|return or empty) []: ").strip() or "").lower()
            if cphase and cphase not in CALLBACK_PHASES:
                cphase = ""
            new_meta = _apply_narrative_to_metadata(metadata, mechanism_depth=md, cost_type=ct, cost_intensity=ci, identity_stage=is_, callback_id=cid, callback_phase=cphase or None)
            new_parts.append(header)
            new_parts.append(new_meta)
            new_parts.append(prose)
            updated += 1
        new_text = "\n---\n".join(new_parts) + "\n---\n"
        path.write_text(new_text)
        print("Wrote", path)
    print("Updated", updated, "blocks.")
    return 0


def run_batch(atoms_dir: Path, csv_path: Path) -> int:
    """Read CSV with columns atom_id, mechanism_depth, cost_type, cost_intensity, identity_stage, callback_id, callback_phase. Apply to files."""
    if not csv_path.exists():
        print("CSV not found:", csv_path, file=sys.stderr)
        return 1
    rows: list[dict[str, str]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k.strip(): v.strip() for k, v in r.items()})
    # Group by file: atom_id -> persona_topic_engine_role_vNN so path is atoms/persona/topic/engine/CANONICAL.txt
    by_path: dict[Path, list[tuple[dict, str]]] = {}  # path -> [(row, atom_id), ...]
    for r in rows:
        aid = (r.get("atom_id") or "").strip()
        if not aid:
            continue
        parts = aid.split("_")
        if len(parts) < 4:
            continue
        # persona_topic_engine_role_vNN -> persona, topic, engine
        persona, topic, engine = parts[0], parts[1], parts[2]
        path = atoms_dir / persona / topic / engine / "CANONICAL.txt"
        by_path.setdefault(path, []).append((r, aid))
    for path, items in by_path.items():
        if not path.exists():
            print("Skip (missing):", path, file=sys.stderr)
            continue
        text = path.read_text()
        blocks = _parse_blocks_with_prose(text)
        row_by_id = {aid: row for row, aid in items}
        new_parts = []
        for header, metadata, prose, _ in blocks:
            atom_id = _atom_id_from_block(path, header)
            row = row_by_id.get(atom_id)
            if not row:
                new_parts.append(header)
                new_parts.append(metadata)
                new_parts.append(prose)
                continue
            try:
                md = int(row.get("mechanism_depth") or "1")
            except ValueError:
                md = 1
            ct = (row.get("cost_type") or "social").lower()
            if ct not in COST_TYPES:
                ct = "social"
            try:
                ci = int(row.get("cost_intensity") or "2")
            except ValueError:
                ci = 2
            is_ = (row.get("identity_stage") or "pre_awareness").lower()
            if is_ not in IDENTITY_STAGES:
                is_ = "pre_awareness"
            cid = (row.get("callback_id") or "").strip() or None
            cphase = (row.get("callback_phase") or "").lower()
            if cphase not in CALLBACK_PHASES:
                cphase = None
            new_meta = _apply_narrative_to_metadata(metadata, mechanism_depth=md, cost_type=ct, cost_intensity=ci, identity_stage=is_, callback_id=cid, callback_phase=cphase)
            new_parts.append(header)
            new_parts.append(new_meta)
            new_parts.append(prose)
        new_text = "\n---\n".join(new_parts) + "\n---\n"
        path.write_text(new_text)
        print("Wrote", path)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Tag CANONICAL.txt atoms with narrative metadata.")
    ap.add_argument("--atoms-dir", type=Path, default=REPO_ROOT / "atoms", help="Atoms root or persona/topic subdir.")
    ap.add_argument("--csv", type=Path, default=None, help="CSV for batch mode: atom_id, mechanism_depth, cost_type, cost_intensity, identity_stage, callback_id, callback_phase.")
    ap.add_argument("--mode", choices=("interactive", "batch"), default="interactive", help="interactive: prompt per block; batch: apply from CSV.")
    args = ap.parse_args()
    atoms_dir = args.atoms_dir.resolve()
    if args.mode == "batch":
        if not args.csv:
            print("--csv required for batch mode", file=sys.stderr)
            return 1
        return run_batch(atoms_dir, args.csv.resolve())
    return run_interactive(atoms_dir)


if __name__ == "__main__":
    sys.exit(main())
