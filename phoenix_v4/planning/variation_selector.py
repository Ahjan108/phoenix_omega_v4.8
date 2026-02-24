"""
Structural Variation V4: deterministic knob selection with anti-cluster policy.
Selects: book_structure_id, journey_shape_id, motif_id, section_reorder_mode,
reframe_profile_id, chapter_archetypes; computes variation_signature.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_SOT = REPO_ROOT / "config" / "source_of_truth"

# Hard cap: reject combo if its wave count exceeds this share of wave size.
ANTI_CLUSTER_COMBO_MAX_SHARE = 0.15  # 15% of wave
# Soft penalty: reduce effective weight by this factor per extra use.
SOFT_PENALTY_PER_USE = 0.7


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _seed_digest(
    seed: str,
    topic_id: str,
    persona_id: str,
    angle_id: str = "",
    arc_id: str = "",
    installment_number: Optional[int] = None,
) -> bytes:
    """Spec: sha256(seed + topic_id + persona_id + angle_id + arc_id + installment_number)."""
    payload = f"{seed}|{topic_id}|{persona_id}|{angle_id}|{arc_id}|{installment_number or 0}"
    return hashlib.sha256(payload.encode("utf-8")).digest()


def _compatible(
    entry: dict,
    persona_id: str,
    topic_id: str,
    arc_tags: Optional[list[str]] = None,
) -> bool:
    """True if entry has no tags or persona/topic/arc in tags."""
    pt = entry.get("persona_tags") or []
    tt = entry.get("topic_tags") or []
    at = entry.get("arc_tags") or []
    if pt and persona_id and persona_id not in pt:
        return False
    if tt and topic_id and topic_id not in tt:
        return False
    if arc_tags and at:
        if not any(t in at for t in arc_tags):
            return False
    return True


def _weight(entry: dict, key: str = "default") -> float:
    w = entry.get("weights") or {}
    return float(w.get(key, w.get("default", 1.0)))


def _weighted_select(
    candidates: list[tuple[str, float]],
    digest: bytes,
    used_counts: Optional[dict[str, int]] = None,
    soft_penalty: bool = True,
) -> str:
    """
    Deterministic weighted choice. Tie-break: lexical sort then digest-based index.
    used_counts: optional id -> count for soft penalty (reduce weight by SOFT_PENALTY_PER_USE per use).
    """
    if not candidates:
        return ""
    used_counts = used_counts or {}
    # Apply soft penalty: effective_weight = weight * (SOFT_PENALTY_PER_USE ** use_count)
    weighted: list[tuple[str, float]] = []
    for cid, w in candidates:
        u = used_counts.get(cid, 0)
        if soft_penalty and u > 0:
            w = w * (SOFT_PENALTY_PER_USE ** u)
        weighted.append((cid, max(1e-6, w)))
    total = sum(w for _, w in weighted)
    if total <= 0:
        return sorted(c[0] for c in weighted)[0]
    # Deterministic index: first 4 bytes of digest as big-endian int, then scale to [0, total)
    idx_val = int.from_bytes(digest[:4], "big") / (2**32)
    target = idx_val * total
    cum = 0.0
    for cid, w in weighted:
        cum += w
        if cum >= target:
            return cid
    return weighted[-1][0]


def _combo_key(book_structure_id: str, journey_shape_id: str, motif_id: str, reframe_profile_id: str) -> str:
    return f"{book_structure_id}|{journey_shape_id}|{motif_id}|{reframe_profile_id}"


def select_variation_knobs(
    topic_id: str,
    persona_id: str,
    chapter_count: int,
    seed: str = "default_seed",
    angle_id: str = "",
    arc_id: str = "",
    installment_number: Optional[int] = None,
    wave_index: Optional[list[dict[str, Any]]] = None,
    config_root: Optional[Path] = None,
    arc_tags: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Deterministic selection pipeline (spec §4, §7).
    1. Select book_structure_id from compatible archetypes.
    2. Select journey_shape_id constrained by arc and structure.
    3. Select motif_id with anti-cluster least-used tie-break.
    4. Select reframe_profile_id by persona/topic compatibility.
    5. Select section_reorder_mode by size and structure compatibility.
    6. Generate chapter_archetypes from structure blueprint.
    7. Compute variation_signature.
    """
    config_root = config_root or CONFIG_SOT
    digest = _seed_digest(seed, topic_id, persona_id, angle_id, arc_id or "", installment_number)

    structures = _load_yaml(config_root / "book_structure_archetypes.yaml")
    journey = _load_yaml(config_root / "journey_shapes.yaml")
    chapter_arch = _load_yaml(config_root / "chapter_archetypes.yaml")
    reorder = _load_yaml(config_root / "section_reorder_modes.yaml")
    motifs = _load_yaml(config_root / "recurring_motif_bank.yaml")
    reframe = _load_yaml(config_root / "reframe_line_bank.yaml")

    arch_list = list((structures.get("archetypes") or {}).items())
    journey_list = list((journey.get("shapes") or {}).items())
    motif_list = list((motifs.get("motifs") or {}).items())
    reorder_list = list((reorder.get("modes") or {}).items())
    profile_list = list((reframe.get("profiles") or {}).items())

    # Build wave usage for anti-cluster
    wave_rows = [r for r in (wave_index or []) if isinstance(r, dict)]
    combo_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    for row in wave_rows:
        combo = _combo_key(
            row.get("book_structure_id", ""),
            row.get("journey_shape_id", ""),
            row.get("motif_id", ""),
            row.get("reframe_profile_id", ""),
        )
        combo_counts[combo] = combo_counts.get(combo, 0) + 1
        mid = row.get("motif_id", "")
        if mid:
            motif_counts[mid] = motif_counts.get(mid, 0) + 1
    wave_size = max(1, len(wave_rows))
    combo_cap = max(1, int(wave_size * ANTI_CLUSTER_COMBO_MAX_SHARE))

    # 1. book_structure_id
    struct_candidates = [
        (sid, _weight(ent))
        for sid, ent in arch_list
        if _compatible(ent, persona_id, topic_id, arc_tags)
    ]
    if not struct_candidates:
        struct_candidates = [(k, 1.0) for k, _ in arch_list]
    book_structure_id = _weighted_select(struct_candidates, digest, soft_penalty=False)
    if not book_structure_id and arch_list:
        book_structure_id = arch_list[0][0]

    # 2. journey_shape_id (chapter_count in range)
    journey_candidates = []
    for jid, jent in journey_list:
        if not _compatible(jent, persona_id, topic_id, arc_tags):
            continue
        rng = jent.get("chapter_count_range") or [0, 99]
        if rng and len(rng) >= 2 and not (rng[0] <= chapter_count <= rng[1]):
            continue
        journey_candidates.append((jid, _weight(jent)))
    if not journey_candidates:
        journey_candidates = [(jid, _weight(jent)) for jid, jent in journey_list]
    journey_shape_id = _weighted_select(journey_candidates, digest, soft_penalty=False)
    if not journey_shape_id and journey_list:
        journey_shape_id = journey_list[0][0]

    # 3. motif_id with anti-cluster (least-used tie-break via soft penalty)
    motif_candidates = [
        (mid, _weight(ment))
        for mid, ment in motif_list
        if _compatible(ment, persona_id, topic_id, arc_tags)
    ]
    if not motif_candidates:
        motif_candidates = [(mid, _weight(ment)) for mid, ment in motif_list]
    motif_id = _weighted_select(motif_candidates, digest, used_counts=motif_counts, soft_penalty=True)
    if not motif_id and motif_list:
        motif_id = motif_list[0][0]

    # 4. reframe_profile_id
    profile_candidates = [
        (pid, _weight(pent))
        for pid, pent in profile_list
        if _compatible(pent, persona_id, topic_id, arc_tags)
    ]
    if not profile_candidates:
        profile_candidates = [(pid, _weight(pent)) for pid, pent in profile_list]
    reframe_profile_id = _weighted_select(profile_candidates, digest, soft_penalty=False)
    if not reframe_profile_id and profile_list:
        reframe_profile_id = profile_list[0][0]
    default_profile = reframe.get("default_profile_id", "balanced")
    if reframe_profile_id not in (p[0] for p in profile_list):
        reframe_profile_id = default_profile

    # Hard cap: if (structure, journey, motif, reframe) over cap, try next motif then reframe
    combo = _combo_key(book_structure_id, journey_shape_id, motif_id, reframe_profile_id)
    while combo_counts.get(combo, 0) >= combo_cap and (motif_candidates or profile_list):
        # Try different motif first
        motif_candidates = [(mid, w) for mid, w in motif_candidates if mid != motif_id]
        if motif_candidates:
            motif_id = _weighted_select(motif_candidates, digest, used_counts=motif_counts, soft_penalty=True)
            combo = _combo_key(book_structure_id, journey_shape_id, motif_id, reframe_profile_id)
        else:
            profile_candidates = [(pid, w) for pid, w in profile_candidates if pid != reframe_profile_id]
            if profile_candidates:
                reframe_profile_id = _weighted_select(profile_candidates, digest, soft_penalty=False)
                combo = _combo_key(book_structure_id, journey_shape_id, motif_id, reframe_profile_id)
            else:
                break

    # 5. section_reorder_mode (chapter_count and structure compatibility)
    reorder_candidates = []
    for rid, rent in reorder_list:
        min_ch = rent.get("min_chapter_count") or 0
        max_ch = rent.get("max_chapter_count") or 99
        if not (min_ch <= chapter_count <= max_ch):
            continue
        struct_ids = rent.get("structure_ids") or []
        if struct_ids and book_structure_id not in struct_ids:
            continue
        reorder_candidates.append((rid, _weight(rent)))
    if not reorder_candidates:
        reorder_candidates = [(rid, _weight(rent)) for rid, rent in reorder_list]
    section_reorder_mode = _weighted_select(reorder_candidates, digest, soft_penalty=False)
    if not section_reorder_mode and reorder_list:
        section_reorder_mode = "none"

    # 6. chapter_archetypes from structure blueprint
    blueprints = (chapter_arch.get("structure_blueprints") or {}).get(book_structure_id)
    if blueprints:
        seq = blueprints.get("sequence") or ["establish", "expose", "destabilize", "reframe", "stabilize", "integrate"]
        repeat = blueprints.get("repeat_tail", True)
        if repeat and seq:
            chapter_archetypes = [seq[i % len(seq)] for i in range(chapter_count)]
        else:
            chapter_archetypes = (seq * ((chapter_count // len(seq)) + 1))[:chapter_count]
    else:
        base = ["establish", "expose", "destabilize", "reframe", "stabilize", "integrate"]
        chapter_archetypes = [base[i % len(base)] for i in range(chapter_count)]

    # 7. variation_signature
    from phoenix_v4.planning.schema_v4 import compute_variation_signature
    variation_signature = compute_variation_signature(
        book_structure_id=book_structure_id,
        journey_shape_id=journey_shape_id,
        motif_id=motif_id,
        section_reorder_mode=section_reorder_mode,
        reframe_profile_id=reframe_profile_id,
        angle_id=angle_id or "",
        topic_id=topic_id or "",
        persona_id=persona_id or "",
        arc_id=arc_id or "",
        installment_number=installment_number,
        chapter_archetypes=chapter_archetypes,
    )

    return {
        "book_structure_id": book_structure_id,
        "journey_shape_id": journey_shape_id,
        "motif_id": motif_id,
        "section_reorder_mode": section_reorder_mode,
        "reframe_profile_id": reframe_profile_id,
        "chapter_archetypes": chapter_archetypes,
        "variation_signature": variation_signature,
    }
