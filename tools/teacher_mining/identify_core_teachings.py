#!/usr/bin/env python3
"""
Identify core teachings from TEACHING atoms and tag atoms.
Structural only: glossary frequency, cross-atom repetition, doc spread. No NLP/embeddings.
Outputs doctrine/core_teachings.yaml and updates TEACHING atom YAMLs with tags.
Authority: Teacher Mode structural design — concept anchoring, TPS, vocabulary stability.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Minimum atoms for a cluster to be candidate core teaching
MIN_CLUSTER_SIZE = 4
# Minimum share of TEACHING atoms — 8% forces conceptual hierarchy (was 5%)
MIN_ATOM_PCT = 0.08
# Glossary term must appear in at least this many atoms to be core
MIN_GLOSSARY_OCCURRENCES = 3
# Concept must appear in at least this many distinct source docs
MIN_DOC_SPREAD = 4
# Cap: 60 "core" = no core; enforce 8–15 typical, 20 absolute max
MAX_CORE_TEACHINGS = 20


def _load_yaml(p: Path) -> tuple[dict, bool]:
    """Load YAML. Returns (data, doctrine_missing). doctrine_missing=True if parse failed."""
    if not p.exists() or yaml is None:
        return {}, not p.exists()
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}, False
    except Exception as e:
        import sys
        print(f"Warning: doctrine YAML parse failed ({p}): {e}", file=sys.stderr)
        return {}, True


def _save_yaml(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _normalize_for_phrase(text: str) -> str:
    """Lowercase, collapse whitespace, keep letters and spaces for phrase extraction."""
    t = re.sub(r"[^\w\s]", " ", text.lower())
    return " ".join(t.split())


def _phrase_to_id(phrase: str) -> str:
    """Canonical snake_case id from phrase."""
    t = re.sub(r"[^a-z0-9\s]", "", phrase.lower())
    return re.sub(r"\s+", "_", t.strip()).strip("_") or "concept"


def _tokenize_words(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{3,}\b", text.lower())


def load_teaching_atoms(teaching_dir: Path) -> list[dict]:
    """Load all TEACHING atom YAMLs; each has atom_id, body, teacher.source_refs."""
    atoms = []
    if not teaching_dir.exists():
        return atoms
    for path in sorted(teaching_dir.glob("*.yaml")):
        data, _ = _load_yaml(path)
        if data and data.get("atom_id") and data.get("body"):
            atoms.append(data)
    return atoms


def load_glossary(doctrine_path: Path) -> tuple[list[str], bool]:
    """Returns (glossary_terms, doctrine_missing). doctrine_missing=True if doctrine failed to parse."""
    doctrine, doctrine_missing = _load_yaml(doctrine_path)
    glossary = doctrine.get("glossary") or []
    terms = []
    for g in glossary:
        if isinstance(g, str):
            term = g.split(" / ")[0].strip().lower()
            if term:
                terms.append(term)
        else:
            terms.append(str(g).lower())
    return terms, doctrine_missing


def get_doc_ids(atom: dict) -> set[str]:
    """Unique doc_ids from teacher.source_refs."""
    refs = (atom.get("teacher") or {}).get("source_refs") or []
    return {r.get("doc_id", "") for r in refs if r.get("doc_id")}


def run_identification(
    teacher_id: str,
    atoms_root: Path,
    doctrine_path: Path,
    *,
    min_cluster: int = MIN_CLUSTER_SIZE,
    min_pct: float = MIN_ATOM_PCT,
    min_glossary: int = MIN_GLOSSARY_OCCURRENCES,
    min_docs: int = MIN_DOC_SPREAD,
) -> tuple[list[dict], dict[str, list[str]], bool]:
    """
    Identify core teachings and which atom_ids belong to each.
    Returns (core_teachings_list, atom_id -> list of core ids, doctrine_missing).
    """
    teaching_dir = atoms_root / "TEACHING"
    atoms = load_teaching_atoms(teaching_dir)
    if not atoms:
        return [], {}, False

    glossary_terms, doctrine_missing = load_glossary(doctrine_path)
    n_atoms = len(atoms)
    min_freq_pct = int(n_atoms * min_pct)  # e.g. 8% of 100 = 8 atoms

    # Term frequency across atoms (glossary terms and significant 2-word phrases)
    term_in_atoms: dict[str, set[str]] = {}  # term -> set of atom_id
    term_docs: dict[str, set[str]] = {}      # term -> set of doc_id
    atom_cores: dict[str, list[str]] = {a["atom_id"]: [] for a in atoms}

    for atom in atoms:
        aid = atom["atom_id"]
        body = (atom.get("body") or "").strip()
        norm = _normalize_for_phrase(body)
        doc_ids = get_doc_ids(atom)

        # Glossary term presence
        for g in glossary_terms:
            if g in norm or g.replace(" ", "_") in norm:
                key = _phrase_to_id(g)
                term_in_atoms.setdefault(key, set()).add(aid)
                term_docs.setdefault(key, set()).update(doc_ids)

        # 2–3 word phrases (skip very common words)
        stop = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "her", "his", "has", "had", "was", "were", "been", "have", "this", "that", "with", "from", "they", "will", "their", "what", "when", "which", "while", "about", "into", "through", "during"}
        words = _tokenize_words(norm)
        for n in (2, 3):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i : i + n])
                if any(w in stop for w in words[i : i + n]):
                    continue
                if len(phrase) < 6:
                    continue
                key = _phrase_to_id(phrase)
                term_in_atoms.setdefault(key, set()).add(aid)
                term_docs.setdefault(key, set()).update(doc_ids)

    # Select core: must satisfy at least TWO of (≥8% freq, glossary term, ≥4 distinct docs). Cap top 20.
    glossary_ids = {_phrase_to_id(g) for g in glossary_terms}
    core_teachings: list[dict] = []
    for term_key, aids in term_in_atoms.items():
        count = len(aids)
        doc_count = len(term_docs.get(term_key, set()))
        is_glossary = term_key in glossary_ids
        meets_freq = count >= min_freq_pct
        meets_glossary = is_glossary and count >= min_glossary
        meets_docs = doc_count >= min_docs
        criteria_met = sum([meets_freq, meets_glossary, meets_docs])
        if criteria_met < 2:
            continue
        canonical = term_key.replace("_", " ")
        core_teachings.append({
            "id": term_key,
            "canonical_phrase": canonical,
            "atom_ids": sorted(aids),
            "frequency": count,
            "glossary_term": is_glossary,
            "_doc_count": doc_count,
        })
        for aid in aids:
            atom_cores[aid].append(term_key)

    # Dedupe by id (keep highest frequency if duplicate ids)
    by_id: dict[str, dict] = {}
    for c in core_teachings:
        k = c["id"]
        if k not in by_id or c["frequency"] > by_id[k]["frequency"]:
            by_id[k] = c
    core_teachings = list(by_id.values())

    # Rank: glossary first, then doc spread, then frequency. Take top MAX_CORE_TEACHINGS.
    for c in core_teachings:
        c["_rank_key"] = (0 if c["glossary_term"] else 1, -c.get("_doc_count", 0), -c["frequency"])
    core_teachings.sort(key=lambda x: x["_rank_key"])
    for c in core_teachings:
        c.pop("_rank_key", None)
        c.pop("_doc_count", None)
    core_teachings = core_teachings[:MAX_CORE_TEACHINGS]
    allowed_core_ids = {c["id"] for c in core_teachings}
    for aid in atom_cores:
        atom_cores[aid] = [x for x in atom_cores[aid] if x in allowed_core_ids]

    return core_teachings, atom_cores, doctrine_missing


def write_core_teachings_yaml(doctrine_dir: Path, core_teachings: list[dict]) -> Path:
    out_path = doctrine_dir / "core_teachings.yaml"
    data = {"core_teachings": core_teachings}
    _save_yaml(out_path, data)
    return out_path


def update_atom_tags(teaching_dir: Path, atom_cores: dict[str, list[str]]) -> int:
    """Update each TEACHING atom YAML with tags: [core: <id>, ...]. Returns count updated."""
    updated = 0
    for path in sorted(teaching_dir.glob("*.yaml")):
        data, _ = _load_yaml(path)
        if not data or not data.get("atom_id"):
            continue
        aid = data["atom_id"]
        cores = atom_cores.get(aid, [])
        if not cores:
            if "tags" in data:
                data["tags"] = [t for t in data.get("tags", []) if not str(t).startswith("core:")]
                if not data["tags"]:
                    del data["tags"]
                _save_yaml(path, data)
                updated += 1
            continue
        tags = list(data.get("tags") or [])
        existing_core = {t for t in tags if isinstance(t, str) and t.startswith("core:")}
        new_core = {f"core:{c}" for c in cores}
        tags = [t for t in tags if t not in existing_core] + sorted(new_core)
        data["tags"] = tags
        _save_yaml(path, data)
        updated += 1
    return updated


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Identify core teachings from TEACHING atoms; tag atoms and write core_teachings.yaml"
    )
    ap.add_argument("--teacher", required=True, help="Teacher id")
    ap.add_argument("--atoms-root", default=None, help="Path to approved_atoms or candidate_atoms (default: teacher_banks/<id>/approved_atoms)")
    ap.add_argument("--doctrine", default=None, help="Path to doctrine.yaml (default: teacher_banks/<id>/doctrine/doctrine.yaml)")
    ap.add_argument("--min-cluster", type=int, default=MIN_CLUSTER_SIZE, help=f"Min atoms per cluster (default {MIN_CLUSTER_SIZE})")
    ap.add_argument("--min-pct", type=float, default=MIN_ATOM_PCT, help=f"Min share of atoms (default {MIN_ATOM_PCT})")
    ap.add_argument("--no-update-atoms", action="store_true", help="Do not write tags to TEACHING atom YAMLs")
    ap.add_argument("--repo", default=None, help="Repo root")
    args = ap.parse_args()
    repo = Path(args.repo) if args.repo else REPO_ROOT
    banks = repo / "SOURCE_OF_TRUTH" / "teacher_banks" / args.teacher.strip().lower()
    atoms_root = Path(args.atoms_root) if args.atoms_root else banks / "approved_atoms"
    doctrine_path = Path(args.doctrine) if args.doctrine else banks / "doctrine" / "doctrine.yaml"

    if not doctrine_path.exists():
        print(f"Doctrine not found: {doctrine_path}", file=sys.stderr)
        return 1
    if not (atoms_root / "TEACHING").exists():
        print(f"TEACHING dir not found: {atoms_root / 'TEACHING'}", file=sys.stderr)
        return 1

    core_teachings, atom_cores, doctrine_missing = run_identification(
        args.teacher.strip().lower(),
        atoms_root,
        doctrine_path,
        min_cluster=args.min_cluster,
        min_pct=args.min_pct,
    )

    if doctrine_missing:
        print("Warning: doctrine YAML failed to parse; glossary was empty (doctrine_missing).", file=sys.stderr)

    doctrine_dir = doctrine_path.parent
    out_path = write_core_teachings_yaml(doctrine_dir, core_teachings)
    print(f"Wrote {out_path} ({len(core_teachings)} core teachings, max {MAX_CORE_TEACHINGS})")

    if not args.no_update_atoms:
        n = update_atom_tags(atoms_root / "TEACHING", atom_cores)
        print(f"Updated tags in {n} TEACHING atoms")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
