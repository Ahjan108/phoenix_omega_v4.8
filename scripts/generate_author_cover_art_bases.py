#!/usr/bin/env python3
"""
Generate author signature cover art base backgrounds for the first 10 authors of every catalog.
Authority: docs/authoring/AUTHOR_COVER_ART_SYSTEM.md, config/authoring/author_cover_art_registry.yaml
Output: assets/authors/cover_art/{author_id}_base.png
Dimensions: 1080x1920 (mobile/audiobook portrait ratio).
Pure Python (zlib only); no Pillow required.
"""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "assets" / "authors" / "cover_art"

# author_id -> list of hex colors (top to bottom gradient), from registry palette_tokens
AUTHOR_PALETTES = {
    "ahjan": ["#4A5568", "#718096", "#E2E8F0"],
    "master_feung": ["#5D4E37", "#8B7355", "#C4B896"],
    "sai_ma": ["#6B7B8C", "#4A5568", "#A8B5C4"],
    "ra": ["#5C6B73", "#3D4F56", "#B8C5CE"],
    "junko": ["#8B6914", "#C9A227", "#E8D5A3"],
    "miki": ["#4A6B7C", "#2C4A5A", "#B5D4E3"],
    "master_wu": ["#6B5344", "#8B7355", "#D4C4B8"],
    "pamela_fellows": ["#3D5A6C", "#2C4050", "#A8C5D8"],
    "joshin": ["#7B6B8C", "#5A4A6B", "#D4C8E8"],
    "maat": ["#5C4A3A", "#8B7355", "#C9B8A8"],
    "ajahn_x": ["#4A5568", "#718096", "#E2E8F0"],
    "luna_hart": ["#7B6B8C", "#5A4A6B", "#D4C8E8"],
    "kai_nakamura": ["#3D5A6C", "#2C4050", "#A8C5D8"],
    "marcus_cole": ["#5D4E37", "#8B7355", "#C4B896"],
    "diane_reyes": ["#5C4A3A", "#8B7355", "#C9B8A8"],
}


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)


def write_png_rgb(width: int, height: int, row_data: bytes, out_path: Path) -> None:
    """Write a PNG file (RGB, no alpha) from raw row data. Each row: filter byte 0 + width*3 bytes."""
    raw = row_data
    compressed = zlib.compress(raw, 9)
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    chunks = (
        signature
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", compressed)
        + png_chunk(b"IEND", b"")
    )
    out_path.write_bytes(chunks)


def generate_gradient_png(width: int, height: int, colors: list[str], out_path: Path) -> None:
    rgb = [hex_to_rgb(c) for c in colors]
    n = len(rgb) - 1
    step = height / n if n else 0
    rows = []
    for y in range(height):
        idx = min(int(y / step), n - 1) if step else 0
        t = (y / step - idx) if step and idx < n else 0
        t = max(0.0, min(1.0, t))
        r1, g1, b1 = rgb[idx]
        r2, g2, b2 = rgb[min(idx + 1, n)]
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        row = bytes([0]) + bytes([r, g, b] * width)
        rows.append(row)
    write_png_rgb(width, height, b"".join(rows), out_path)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1920

    for author_id, colors in AUTHOR_PALETTES.items():
        out_path = OUT_DIR / f"{author_id}_base.png"
        generate_gradient_png(width, height, colors, out_path)
        print(f"Wrote {out_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
