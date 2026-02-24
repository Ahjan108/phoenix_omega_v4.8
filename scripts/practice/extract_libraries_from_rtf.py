"""
Extract *_library_34.json from specs/34_exercises.rtf.
RTF embeds JSON with control words like \\cf13 "id"\\cf12 : \\cf14 "value".
Strips RTF codes then parses JSON blocks by content_type.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def strip_rtf_for_json(line: str) -> str:
    """Remove RTF control words and keep quotes/braces/colons/commas/numbers."""
    # Remove \word and \word123
    s = re.sub(r"\\[a-zA-Z]+\d*\s?", " ", line)
    s = re.sub(r"[\{\}\\]", lambda m: m.group(0), s)
    return s


def strip_rtf_to_plain(text: str) -> str:
    """Remove RTF control words so JSON-like structure is parseable."""
    # Remove \word and \word123 (control words)
    s = re.sub(r"\\[a-zA-Z]+\d*\s?", " ", text)
    # Remove stray backslashes that break JSON (e.g. [ \ { and \ " from RTF)
    s = re.sub(r"\s+\\\s+", " ", s)
    s = re.sub(r"\[\s*\\\s*\{", "[ {", s)
    s = re.sub(r",\s*\\\s*\{", ", {", s)
    s = re.sub(r"\\\"", '"', s)  # \" -> "
    s = re.sub(r"\\\s*}", "}", s)  # \ } -> }
    s = re.sub(r"\\\s*\]", "]", s)  # \ ] -> ]
    s = re.sub(r"\\\s*\{", " {", s)  # \ { -> {
    # Collapse multiple spaces/newlines to single space
    s = re.sub(r"[\r\n]+", " ", s)
    s = re.sub(r"  +", " ", s)
    return s


def extract_json_from_rtf(rtf_path: Path) -> list[tuple[str, dict]]:
    """Read RTF and return list of (content_type, raw_dict) for each library."""
    text = rtf_path.read_text(encoding="utf-8", errors="replace")
    # Strip RTF: remove \word and \word123 so we get parseable JSON-like text
    cleaned = strip_rtf_to_plain(text)
    # Find library blocks by "exercises" : [ (unique to library JSON)
    out = []
    seen_signatures: set[str] = set()
    for m in re.finditer(r'"exercises"\s*:\s*\[', cleaned):
        # Start of "exercises" : [; find the opening { of the containing object
        exercises_start = m.start()
        brace_start = cleaned.rfind("{", 0, exercises_start)
        if brace_start == -1:
            continue
        depth = 0
        end = -1
        for i in range(brace_start, len(cleaned)):
            if cleaned[i] == "{":
                depth += 1
            elif cleaned[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end == -1:
            continue
        chunk = cleaned[brace_start:end]
        try:
            obj = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if "content_type" not in obj or "exercises" not in obj:
            continue
        ct = obj["content_type"]
        sig = f"{ct}:{len(obj.get('exercises', []))}"
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)
        out.append((ct, obj))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract library JSON from 34_exercises.rtf")
    ap.add_argument("--rtf", type=Path, default=Path("specs/34_exercises.rtf"))
    ap.add_argument("--out-dir", type=Path, default=Path("SOURCE_OF_TRUTH/practice_library/inbox"))
    args = ap.parse_args()
    rtf_path = args.rtf.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not rtf_path.exists():
        print(f"RTF not found: {rtf_path}")
        return
    libraries = extract_json_from_rtf(rtf_path)
    if not libraries:
        # Fallback: read line by line, strip \cfN and rebuild lines for JSON
        text = rtf_path.read_text(encoding="utf-8", errors="replace")
        # Simpler: replace \cf13 " with ", \cf14 " with " so we get clean quoted strings
        cleaned = re.sub(r'\\cf\d+\s*', '', text)
        cleaned = re.sub(r'\\cb\d+\s*', '', cleaned)
        cleaned = re.sub(r'\\[a-z]+\d*\s*', ' ', cleaned)
        # Find content_type blocks
        for ct in ["sensory_grounding", "gratitude_practices", "integration_bridges", "self_inquiry"]:
            idx = cleaned.find(f'"content_type" : "{ct}"')
            if idx == -1:
                idx = cleaned.find(f'"content_type":"{ct}"')
            if idx == -1:
                continue
            start = cleaned.rfind("{", 0, idx)
            if start == -1:
                continue
            depth = 0
            end = -1
            for i in range(start, len(cleaned)):
                if cleaned[i] == "{":
                    depth += 1
                elif cleaned[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            if end == -1:
                continue
            chunk = cleaned[start:end]
            chunk = re.sub(r"\s+", " ", chunk)
            try:
                obj = json.loads(chunk)
            except json.JSONDecodeError:
                continue
            libraries.append((ct, obj))
    for content_type, obj in libraries:
        out_file = out_dir / f"{content_type}_library_34.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
        n = len(obj.get("exercises") or [])
        print(f"Wrote {out_file} ({n} exercises)")
    if not libraries:
        print("No libraries extracted. Inbox may need manual JSON files.")


if __name__ == "__main__":
    main()
