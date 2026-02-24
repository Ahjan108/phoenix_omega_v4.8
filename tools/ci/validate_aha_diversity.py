"""CI: warn if AHA blocks in a compile wave are too similar (repetition risk)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPILED_BOOKS_DIR = REPO_ROOT / "artifacts"
SIM_THRESHOLD = 0.85
CLUSTER_WARN_RATIO = 0.25


def _normalize(text: str):
    t = (text or "").lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return [w for w in t.split() if w]


def _char_ngrams(tokens, n=4):
    s = " ".join(tokens)
    if len(s) < n:
        return {s} if s else set()
    return {s[i:i+n] for i in range(len(s) - n + 1)}


def _jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _load_wave_aha_texts():
    out = []
    if not COMPILED_BOOKS_DIR.exists():
        return out
    for p in COMPILED_BOOKS_DIR.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            book_id = data.get("book_id") or p.stem
            blocks = data.get("exercise_aha_blocks", [])
            for i, txt in enumerate(blocks):
                out.append((f"{book_id}#aha{i:02d}", txt))
        except Exception:
            pass
    return out


def main() -> int:
    items = _load_wave_aha_texts()
    if len(items) < 2:
        print("OK: not enough AHA blocks to evaluate diversity")
        return 0
    grams = {k: _char_ngrams(_normalize(txt), 4) for k, txt in items}
    keys = [k for k, _ in items]
    near_dupes = []
    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            sim = _jaccard(grams[a], grams[b])
            if sim >= SIM_THRESHOLD:
                near_dupes.append((a, b, sim))
                union(a, b)

    clusters = defaultdict(list)
    for k in keys:
        clusters[find(k)].append(k)
    biggest = max((len(v) for v in clusters.values()), default=1)
    ratio = biggest / max(1, len(keys))

    if near_dupes or ratio >= CLUSTER_WARN_RATIO:
        print("WARN: AHA diversity guard triggered")
        for a, b, sim in near_dupes[:50]:
            print(f"  near-dup: {a} ~ {b}  sim={sim:.2f}")
        if len(near_dupes) > 50:
            print(f"  ... {len(near_dupes)-50} more")
        print(f"  largest cluster: {biggest}/{len(keys)} ({ratio:.0%})")
        return 0
    print("OK: AHA diversity looks healthy for this wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
