#!/usr/bin/env python3
"""
Mine teacher KB (index.json) into STORY, EXERCISE, QUOTE, and TEACHING atom banks.
Writes to candidate_atoms/ by default; use --approve to write to approved_atoms/.
Authority: specs/TEACHER_MODE_V4_CANONICAL_SPEC.md (gap-fill / mining).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Classification patterns (Ahjan / Buddha Dojo blog style)
# ---------------------------------------------------------------------------

STORY_MARKERS = re.compile(
    r"\b(Consider the story of|Consider the Story of|In the ancient|One day,? |"
    r"The story of|tale of the Buddha|Angulimala|finger necklace|"
    r"Prince Siddhartha|Bodhi tree|two brothers at the river|"
    r"young man approached the Buddha|Buddha replied|Buddha said,? \"|"
    r"starving tigress|feed a starving tigress|"
    r"He set out to find|fell to his knees|Siddhartha renounced|"
    r"Buddha approached Angulimala|I have already stopped, Angulimala|"
    r"Once,? a young man|handful of salt|cup of water|river water|"
    r"Lahiri Mahasaya|Ralph Honda|Zen master turned samurai)\b",
    re.I,
)

EXERCISE_MARKERS = re.compile(
    r"\b(meditation|sit (and|in)|focus (on|your)|practice (of|this)|"
    r"breathe|close your eyes|mindfulness (practice|and)|"
    r"step (one|1)|first, (sit|close|focus)|focus your attention|"
    r"let go of (your|negative)|observe your (breath|thoughts)|"
    r"channeling your focus|approach (it|work) as (a )?form of meditation|"
    r"yoga|breathing exercises|qigong)\b",
    re.I,
)

QUOTE_MARKERS = re.compile(
    r"\b(Dhammapada|as the Buddha said|Buddha said|the Buddha (said|replied)|"
    r"This statement from|The words of the Buddha|"
    r"quote aligns|resonates.*:?\s*[\"']|"
    r"only three things matter|Hatred does not cease by hatred)\b",
    re.I,
)

# Short quoted sentence(s) — extract for QUOTE
QUOTED_PHRASE = re.compile(r'"([^"]{20,300})"')

# Section header / core teaching
TEACHING_MARKERS = re.compile(
    r"\b(Buddhism teaches|central to (this|the)|key to (achieving|understanding)|"
    r"the path involves|essential for|One of the key aspects|"
    r"The concept of|In Buddhism,|enlightenment is (a|not)|"
    r"The essence of|True (happiness|spiritual)|"
    r"Personal power is|Love (is|as) the (greatest|universal)|"
    r"Spiritual (purity|tenacity)|inner light|Dharmakaya|"
    r"right livelihood|karma yoga|self-effort)\b",
    re.I,
)

# ---------------------------------------------------------------------------
# STORY Band Heuristic (deterministic; no sentiment scoring)
# Authority: Teacher Mode structural design — Arc band alignment
# ---------------------------------------------------------------------------

ESCALATION_KEYWORDS = {
    "again", "repeatedly", "struggled", "avoided", "conflicted",
    "anxious", "ashamed", "afraid", "worried", "overwhelmed",
    "restless", "resisted", "tense",
}

COST_KEYWORDS = {
    "lost", "rejected", "humiliated", "failed", "collapse",
    "isolated", "alone", "exposed", "broke", "exhausted",
    "abandoned", "betrayed",
}

CRISIS_KEYWORDS = {
    "death", "killed", "murdered", "terminal", "destroyed",
    "suicide", "violence", "exile", "execution", "irreversible",
}

MILD_INDICATORS = {
    "once", "one day", "at one time", "a student asked",
    "a monk said", "consider the story",
}


def _assign_story_band(body: str) -> int:
    """
    Deterministic band assignment from structural tension markers.
    No sentiment scoring. No AI. Transparent rules. Arc-First compatible.
    """
    text = body.lower()
    escalation_hits = sum(1 for k in ESCALATION_KEYWORDS if k in text)
    cost_hits = sum(1 for k in COST_KEYWORDS if k in text)
    crisis_hits = sum(1 for k in CRISIS_KEYWORDS if k in text)
    mild_hits = sum(1 for k in MILD_INDICATORS if k in text)

    band_score = (
        escalation_hits * 1
        + cost_hits * 2
        + crisis_hits * 3
    )

    if crisis_hits > 0:
        return 5
    if band_score >= 6:
        return 5
    if band_score >= 4:
        return 4
    if band_score >= 2:
        return 3
    if escalation_hits > 0:
        return 2
    if len(body.split()) < 150 and mild_hits > 0:
        return 1
    return 2


def _source_of_truth_teacher_banks() -> Path:
    return REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"


def load_kb(teacher_id: str) -> dict:
    kb_dir = _source_of_truth_teacher_banks() / teacher_id / "kb"
    index_path = kb_dir / "index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"KB not found: {index_path}. Run build_kb.py --teacher {teacher_id} first.")
    with open(index_path, encoding="utf-8") as f:
        return json.load(f)


def classify_chunk(text: str) -> str | None:
    """Return slot_type (STORY, EXERCISE, QUOTE, TEACHING) or None if skip."""
    t = text.strip()
    if len(t) < 50:
        return None
    # Prefer QUOTE for short, quote-like content
    if QUOTE_MARKERS.search(t) or (len(t) <= 280 and QUOTED_PHRASE.search(t)):
        return "QUOTE"
    if STORY_MARKERS.search(t):
        return "STORY"
    if EXERCISE_MARKERS.search(t):
        return "EXERCISE"
    if TEACHING_MARKERS.search(t):
        return "TEACHING"
    # Default doctrinal/expository to TEACHING if substantial
    if len(t) >= 200 and (
        "Buddh" in t or "enlightenment" in t or "meditation" in t or "love" in t or "path" in t
    ):
        return "TEACHING"
    return None


def extract_quotes_from_doc(text: str, doc_id: str) -> list[tuple[str, int, int]]:
    """Extract (quote_text, start, end) for notable quoted phrases from full doc text."""
    out = []
    for m in QUOTED_PHRASE.finditer(text):
        quote = m.group(1).strip()
        if 25 <= len(quote) <= 320 and "Buddha" in text[max(0, m.start() - 200) : m.end() + 100]:
            out.append((quote, m.start(), m.end()))
    # Known canonical quotes we want as atoms even if not in quotes in text
    known = [
        "Hatred does not cease by hatred, but only by love; this is the eternal rule.",
        "In the end, only three things matter: how much you loved, how gently you lived, and how gracefully you let go of things not meant for you.",
        "I have already stopped, Angulimala. It is you who must stop.",
    ]
    for q in known:
        if q in text and not any(q == x[0] for x in out):
            idx = text.find(q)
            out.append((q, idx, idx + len(q)))
    return out


def build_atom_id(teacher_id: str, slot_type: str, index: int, slug: str = "") -> str:
    safe = re.sub(r"[^a-z0-9_]", "_", (slug or str(index))[:32].lower())
    return f"{teacher_id}_{slot_type}_{index:03d}_{safe}".rstrip("_")


def _clean_body(text: str) -> str:
    """Remove common RTF/import artifacts from extracted text."""
    t = text.strip()
    for prefix in ("Helvetica; ;; ;; ", "Helvetica; ;; ;;"):
        if t.startswith(prefix):
            t = t[len(prefix) :].strip()
            break
    return t


def chunk_to_source_ref(chunk: dict) -> dict:
    return {
        "doc_id": chunk["doc_id"],
        "span": chunk["span"],
        "quote_hash": chunk.get("quote_hash", ""),
    }


def write_atom_yaml(
    out_dir: Path,
    atom_id: str,
    slot_type: str,
    body: str,
    teacher_id: str,
    source_refs: list[dict],
    band: int | None = None,
) -> Path:
    data = {
        "atom_id": atom_id,
        "body": _clean_body(body),
        "teacher": {
            "teacher_id": teacher_id,
            "source_refs": source_refs,
            "synthesis_method": "kb_mine_v1",
        },
    }
    if slot_type == "STORY" and band is not None:
        data["band"] = band
    path = out_dir / slot_type / f"{atom_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return path


def mine(
    teacher_id: str,
    out_root: Path,
    *,
    approve: bool = False,
    default_story_band: int = 3,
    force_band: int | None = None,
) -> dict[str, int]:
    """Mine KB into atoms. out_root = candidate_atoms or approved_atoms. Returns counts per slot."""
    kb = load_kb(teacher_id)
    documents = {d["doc_id"]: d for d in kb["documents"]}
    chunks = kb.get("chunks", [])
    if not chunks:
        # Fallback: treat each doc as one chunk for TEACHING
        chunks = []
        for doc in kb["documents"]:
            text = doc.get("text", "")
            if len(text) > 100:
                chunks.append({
                    "doc_id": doc["doc_id"],
                    "chunk_index": 0,
                    "span": [0, min(800, len(text))],
                    "text": text[:800].strip(),
                    "quote_hash": hashlib.sha256(text[:800].encode("utf-8")).hexdigest()[:16],
                })

    counts: dict[str, int] = {"STORY": 0, "EXERCISE": 0, "QUOTE": 0, "TEACHING": 0}
    used_quote_bodies: set[str] = set()
    story_chunks: list[dict] = []
    story_doc_id: str | None = None

    def flush_story():
        nonlocal story_chunks, story_doc_id
        if not story_chunks:
            return
        body = _clean_body("\n\n".join(c["text"] for c in story_chunks))
        if len(body) < 100:
            story_chunks = []
            return
        band = force_band if force_band is not None else _assign_story_band(body)
        idx = counts["STORY"]
        aid = build_atom_id(teacher_id, "STORY", idx, "mined")
        refs = [chunk_to_source_ref(c) for c in story_chunks]
        write_atom_yaml(
            out_root, aid, "STORY", body, teacher_id, refs, band=band
        )
        counts["STORY"] += 1
        story_chunks = []
        story_doc_id = None

    for chunk in chunks:
        slot = classify_chunk(chunk["text"])
        if slot is None:
            if story_chunks and story_doc_id != chunk["doc_id"]:
                flush_story()
            continue
        if slot == "STORY":
            if story_chunks and chunk["doc_id"] != story_doc_id:
                flush_story()
            story_doc_id = chunk["doc_id"]
            story_chunks.append(chunk)
            continue
        flush_story()
        if slot == "QUOTE":
            # Prefer extracting clean quote from chunk (short, quoted phrase only)
            qm = QUOTED_PHRASE.search(chunk["text"])
            if qm:
                body = _clean_body(qm.group(1))
            else:
                # If chunk is short and quote-like, use it; else skip (we'll get it from extract_quotes_from_doc)
                body = _clean_body(chunk["text"])
            if len(body) > 400:
                body = body[:397] + "..."
            if body in used_quote_bodies:
                continue
            used_quote_bodies.add(body)
        else:
            body = _clean_body(chunk["text"])
            if len(body) > 2000:
                body = body[:1997] + "..."
        idx = counts[slot]
        aid = build_atom_id(teacher_id, slot, idx, "mined")
        write_atom_yaml(
            out_root, aid, slot, body, teacher_id, [chunk_to_source_ref(chunk)],
            band=default_story_band if slot == "STORY" else None,
        )
        counts[slot] += 1
    flush_story()

    # Add standalone quotes from full documents
    for doc_id, doc in documents.items():
        text = doc.get("text", "")
        for quote_text, start, end in extract_quotes_from_doc(text, doc_id):
            if quote_text in used_quote_bodies:
                continue
            used_quote_bodies.add(quote_text)
            idx = counts["QUOTE"]
            aid = build_atom_id(teacher_id, "QUOTE", idx, "mined")
            refs = [{"doc_id": doc_id, "span": [start, end], "quote_hash": hashlib.sha256(quote_text.encode("utf-8")).hexdigest()[:16]}]
            write_atom_yaml(out_root, aid, "QUOTE", _clean_body(quote_text), teacher_id, refs)
            counts["QUOTE"] += 1

    return counts


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Mine teacher KB into STORY, EXERCISE, QUOTE, TEACHING banks"
    )
    ap.add_argument("--teacher", required=True, help="Teacher id (e.g. ahjan)")
    ap.add_argument(
        "--out",
        default=None,
        help="Output root (default: teacher_banks/<teacher>/candidate_atoms or approved_atoms)",
    )
    ap.add_argument(
        "--approve",
        action="store_true",
        help="Write to approved_atoms/ instead of candidate_atoms/",
    )
    ap.add_argument("--band", type=int, default=3, help="Default STORY band when --force-band not set (fallback)")
    ap.add_argument("--force-band", type=int, default=None, metavar="N", help="Override band for all STORY atoms (1-5)")
    args = ap.parse_args()
    teacher_id = args.teacher.strip().lower()
    banks = _source_of_truth_teacher_banks() / teacher_id
    if args.out:
        out_root = Path(args.out)
    else:
        out_root = banks / ("approved_atoms" if args.approve else "candidate_atoms")
    out_root = out_root.resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    for slot in ("STORY", "EXERCISE", "QUOTE", "TEACHING"):
        (out_root / slot).mkdir(parents=True, exist_ok=True)
    counts = mine(
        teacher_id,
        out_root,
        approve=args.approve,
        default_story_band=args.band,
        force_band=args.force_band,
    )
    print(f"Wrote {out_root}")
    for slot, n in sorted(counts.items()):
        print(f"  {slot}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
