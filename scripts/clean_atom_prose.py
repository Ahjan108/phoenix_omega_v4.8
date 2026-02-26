#!/usr/bin/env python3
"""
Clean all atom prose in the system: keep only book text.

- Removes from prose: *, #, ---, cue/placeholder lines (e.g. [Exercise N for ...]),
  headers that are not chapter titles/subtitles.
- Preserves CANONICAL block structure (## ROLE vNN --- metadata --- body ---) so
  pipeline and parsers continue to work.
- Applies to: atoms/**/CANONICAL*.txt and SOURCE_OF_TRUTH/compression_atoms/approved/**/*.yaml
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"
COMPRESSION_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "compression_atoms" / "approved"

# Header pattern for block start
HEADER_RE = re.compile(r"^##\s*(.+)$", re.MULTILINE)
# Metadata-like content (key: value lines)
META_LIKE_RE = re.compile(r"^\s*(path|BAND|MECHANISM|COST_TYPE|IDENTITY_STAGE|mode|family|voice_mode|reframe_type|weight|carry_line|note|semantic_family)\s*:", re.I | re.MULTILINE)

# Cue/placeholder lines to remove (exact or pattern)
CUE_PATTERNS = [
    re.compile(r"^\[Exercise\s+\d+\s+for\s+[^\]]+\]\s*$", re.I),
    re.compile(r"^Step\s+\d+:\s*\[\s*step\s+\d+\s*\]\.?\s*$", re.I),
    re.compile(r"^\[.*(?:step|placeholder|todo).*\]\s*$", re.I),
]


def clean_prose(text: str) -> str:
    """Keep only book text: remove *, #, ---, cue lines; strip formatting."""
    if not text or not text.strip():
        return text
    lines = text.splitlines()
    out = []
    for line in lines:
        raw = line
        # Strip leading/trailing * # --- and whitespace
        line = line.strip()
        line = re.sub(r"^[\*\#\-]+\s*", "", line)
        line = re.sub(r"\s*[\*\#\-]+$", "", line)
        line = line.strip()
        # Skip lines that are only *, #, ---, or blank
        if not line or re.match(r"^[\*\#\-\s]+$", line):
            continue
        # Skip cue/placeholder lines
        if any(p.search(line) for p in CUE_PATTERNS):
            continue
        if re.match(r"^\[Exercise\s+\d+", line, re.I) or re.match(r"^Step\s+\d+:\s*\[", line, re.I):
            continue
        out.append(line)
    # Join with single newline, collapse internal multiple newlines to one
    joined = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", joined).strip()


def _looks_like_metadata(part: str) -> bool:
    """True if this part looks like metadata (key: value lines), not prose."""
    return bool(META_LIKE_RE.search(part)) if part.strip() else False


def clean_canonical_file(path: Path, dry_run: bool = False) -> bool:
    """Parse CANONICAL.txt by splitting on ---; clean each block body; rewrite. Returns True if changed."""
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    # Strip leading file-level # comments and --- before first ##
    lead_match = re.match(r"^([\s\S]*?)(?=^##\s)", text, re.MULTILINE)
    if lead_match:
        prefix = lead_match.group(1)
        if re.search(r"^#", prefix, re.MULTILINE) or re.search(r"^---", prefix, re.MULTILINE):
            text = text[len(prefix) :].lstrip()
    parts = re.split(r"\n---\s*\n", text)
    blocks: list[tuple[str, str, str]] = []  # (header, meta, body)
    i = 0
    while i < len(parts):
        part = parts[i].strip()
        m = re.search(r"##\s*(.+)$", part, re.MULTILINE)
        if m:
            header = m.group(1).strip()
            # Header might be alone (e.g. "## RECOGNITION v01") or with leading # lines in same part
            if "\n" in part:
                header = part[part.rfind("##") :].replace("##", "").strip()
            if not re.search(r"\S+\s+v\d+", header) and not re.search(r"v\d+-v\d+", header):
                i += 1
                continue
            meta = ""
            prose = ""
            if i + 1 < len(parts):
                candidate = parts[i + 1].strip()
                if candidate.startswith("##"):
                    i += 1
                    continue
                if _looks_like_metadata(candidate):
                    meta = candidate
                    if i + 2 < len(parts):
                        prose = parts[i + 2].strip()
                    i += 2
                else:
                    prose = candidate
                    i += 1
            blocks.append((header, meta, prose))
        i += 1
    if not blocks:
        return False
    new_parts = []
    for header, meta, body in blocks:
        body_cleaned = clean_prose(body)
        new_parts.append(f"## {header}\n---\n{meta}\n---\n{body_cleaned}\n---")
    new_text = "\n\n" + "\n\n".join(new_parts) + "\n"
    if new_text != text:
        if not dry_run:
            path.write_text(new_text, encoding="utf-8")
        return True
    return False


def clean_compression_yaml(path: Path, dry_run: bool = False) -> bool:
    """Clean body field in compression atom YAML. Returns True if changed."""
    if not path.exists() or yaml is None:
        return False
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if not data or "body" not in data:
        return False
    body = data.get("body")
    if isinstance(body, str):
        cleaned = clean_prose(body)
        if cleaned != body:
            data["body"] = cleaned
            if not dry_run:
                with open(path, "w", encoding="utf-8") as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            return True
    return False


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Clean atom prose: remove metadata/format/cues, keep only book text")
    ap.add_argument("--dry-run", action="store_true", help="Report only, do not write")
    ap.add_argument("--atoms-only", action="store_true", help="Only atoms/ (skip compression YAMLs)")
    args = ap.parse_args()

    changed = 0
    # All CANONICAL*.txt under atoms/
    for path in sorted(ATOMS_ROOT.rglob("CANONICAL*.txt")):
        if path.is_file():
            if clean_canonical_file(path, dry_run=args.dry_run):
                changed += 1
                print(path.relative_to(REPO_ROOT))

    if not args.atoms_only and COMPRESSION_ROOT.exists():
        for path in sorted(COMPRESSION_ROOT.rglob("*.yaml")):
            if path.is_file():
                if clean_compression_yaml(path, dry_run=args.dry_run):
                    changed += 1
                    print(path.relative_to(REPO_ROOT))

    if args.dry_run:
        print(f"[dry-run] Would clean {changed} files")
    else:
        print(f"Cleaned {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
