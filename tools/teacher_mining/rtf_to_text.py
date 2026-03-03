"""
Extract plain text from RTF for teacher KB. No runtime dependency.
Used by build_kb.py.
"""
from __future__ import annotations

import re
from pathlib import Path


def rtf_to_text(rtf_bytes: bytes) -> str:
    """Strip RTF control words and return plain text. Tolerates cp1252 and utf-8."""
    try:
        s = rtf_bytes.decode("utf-8")
    except UnicodeDecodeError:
        s = rtf_bytes.decode("cp1252", errors="replace")
    # Remove \controlword and \controlword123 and \{ ... \} groups (nested minimally)
    out: list[str] = []
    i = 0
    while i < len(s):
        if s[i] == "\\":
            i += 1
            if i >= len(s):
                break
            if s[i] in "{}":
                i += 1
                continue
            # Control word: \word or \word123
            m = re.match(r"([a-z]+)(-?\d*)\s?", s[i:])
            if m:
                i += len(m.group(0))
                continue
            if s[i] == "'":
                # hex: \'XX
                if i + 2 < len(s):
                    i += 3
                continue
            i += 1
            continue
        if s[i] == "{":
            i += 1
            continue
        if s[i] == "}":
            i += 1
            continue
        out.append(s[i])
        i += 1
    text = "".join(out)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r" *\n *", "\n", text).strip()
    return text
