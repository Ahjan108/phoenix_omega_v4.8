"""
Unified foundation for phoenix_v4/quality tools.

- Exit code contract: 0 PASS, 1 FAIL, 2 WARN. Automation should treat 1 as blocking.
- Production block parser: CANONICAL.txt → List[AtomBlock]; fail-fast on malformed.
- Helpers: exit_with_status(), QualityResult.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

# Block pattern: ## ROLE vNN --- metadata --- body (body until next ## or end)
BLOCK_PATTERN = re.compile(
    r"##\s*(?P<header>[^\n]+)\n---\s*\n(?P<meta>.*?)\n---\s*\n(?P<body>.*?)(?=\n##\s|\Z)",
    re.DOTALL,
)

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_WARN = 2


@dataclass
class AtomBlock:
    """One parsed atom from CANONICAL.txt."""
    header: str
    atom_id: str
    band: str
    body: str


@dataclass
class QualityResult:
    """Structured result for any quality tool."""
    status: str  # "pass" | "warn" | "fail"
    score: float
    details: Dict[str, Any]


def _parse_meta(meta: str, header: str, path: Path | None) -> tuple[str, str]:
    """Extract atom_id and band from metadata lines (key: value). Returns (atom_id, band)."""
    atom_id = ""
    band = ""
    persona = topic = slot = ""
    if path and path.parts:
        if "atoms" in path.parts:
            idx = path.parts.index("atoms")
            if idx + 4 < len(path.parts):
                persona = path.parts[idx + 1]
                topic = path.parts[idx + 2]
                slot = path.parts[idx + 3] if path.parts[idx + 3] != "CANONICAL.txt" else ""
    header_match = re.match(r"(\S+)\s+v(\d+)", header.strip())
    role_ver = f"{header_match.group(1)}_v{header_match.group(2)}" if header_match else "unknown"

    for line in meta.strip().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip().lower(), val.strip()
        if key == "id" or key == "atom_id":
            atom_id = val
        elif key == "band":
            band = val
        elif key == "path" and not atom_id and role_ver != "unknown":
            pass  # can derive from path below
    if not atom_id and (persona or topic or slot) and header_match:
        atom_id = f"{persona}_{topic}_{slot}_{header_match.group(1)}_v{header_match.group(2)}".strip("_")
    if not atom_id:
        atom_id = role_ver.replace(" ", "_")
    if not band:
        band = "0"
    return atom_id, band


def parse_canonical_blocks(text: str, path: Path | None = None) -> List[AtomBlock]:
    """
    Parse CANONICAL.txt content into structured atom blocks.
    Raises ValueError if no blocks detected or structure malformed.
    """
    blocks: List[AtomBlock] = []
    for m in BLOCK_PATTERN.finditer(text):
        header = m.group("header").strip()
        meta = m.group("meta").strip()
        body = m.group("body").strip()
        if not header or not body:
            continue
        if not re.search(r"\S+\s+v\d+", header):
            raise ValueError(f"Malformed block header (expected ROLE vNN): {header[:80]!r}")
        atom_id, band = _parse_meta(meta, header, path)
        blocks.append(
            AtomBlock(header=header, atom_id=atom_id, band=band, body=body)
        )
    if not blocks:
        raise ValueError("No atom blocks detected. File may be malformed or empty.")
    return blocks


def parse_canonical_blocks_from_path(path: Path) -> List[AtomBlock]:
    """Load file and parse into blocks. Raises ValueError on malformed or missing."""
    if not path.exists():
        raise ValueError(f"File not found: {path}")
    text = path.read_text(encoding="utf-8")
    return parse_canonical_blocks(text, path=path)


def exit_with_status(status: str) -> None:
    """
    Exit with standard code. status: 'pass' | 'warn' | 'fail'.
    """
    s = (status or "").strip().lower()
    if s == "pass":
        raise SystemExit(EXIT_PASS)
    if s == "warn":
        raise SystemExit(EXIT_WARN)
    if s == "fail":
        raise SystemExit(EXIT_FAIL)
    raise ValueError(f"Unknown exit status: {status!r}")


def status_to_exit_code(status: str) -> int:
    """Map pass/warn/fail (case-insensitive) to EXIT_* constant."""
    s = (status or "").strip().lower()
    if s == "pass":
        return EXIT_PASS
    if s == "warn":
        return EXIT_WARN
    if s == "fail":
        return EXIT_FAIL
    return EXIT_FAIL
