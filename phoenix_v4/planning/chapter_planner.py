"""
Chapter planner (Stage 3 pre-assembly policy layer).

Execution order is intentional and strict:
1) Generate archetype candidates per chapter
2) Filter invalid candidates (quotas, transitions, slot viability)
3) Novelty-score remaining candidates
4) Deterministic select

This prevents high-scoring but invalid chapter plans.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POLICY_PATH = REPO_ROOT / "config" / "source_of_truth" / "chapter_planner_policies.yaml"

ROLE_MAP = {
    "recognition": "introduce",
    "destabilization": "deepen",
    "reframe": "challenge",
    "stabilization": "resolve",
    "integration": "resolve",
}


# 12 Bestseller chapter structures (narrative shapes). Max 3 same in a row per book.
BESTSELLER_STRUCTURES = [
    "promise_engine",
    "gladwell_spiral",
    "van_der_kolk",
    "atomic",
    "brene_brown",
    "myth_killer",
    "case_file",
    "permission_slip",
    "zoom_lens",
    "contrast_engine",
    "ancestor",
    "letter",
]
MAX_BESTSELLER_RUN = 3


def assign_bestseller_structures(chapter_count: int, selector_key_prefix: str) -> list[str]:
    """
    Assign one of the 12 Bestseller structures per chapter. Deterministic.
    Never more than MAX_BESTSELLER_RUN (3) of the same structure in a row.
    """
    result: list[str] = []
    n = len(BESTSELLER_STRUCTURES)
    for ch in range(chapter_count):
        seed = f"{selector_key_prefix}:bestseller:ch{ch}"
        h = hashlib.sha256(seed.encode("utf-8")).digest()
        idx = int.from_bytes(h[:2], "big") % n
        candidate = BESTSELLER_STRUCTURES[idx]
        run_len = 0
        for i in range(len(result) - 1, -1, -1):
            if result[i] == candidate:
                run_len += 1
            else:
                break
        if run_len >= MAX_BESTSELLER_RUN:
            # Pick next distinct structure (deterministic)
            used = {result[i] for i in range(max(0, len(result) - MAX_BESTSELLER_RUN), len(result))}
            for j in range(1, n):
                next_idx = (idx + j) % n
                alt = BESTSELLER_STRUCTURES[next_idx]
                if alt not in used:
                    candidate = alt
                    break
        result.append(candidate)
    return result


@dataclass
class ChapterPlanResult:
    slot_definitions: list[list[str]]
    chapter_archetypes: list[str]
    chapter_exercise_modes: list[str]
    chapter_reflection_weights: list[str]
    chapter_story_depths: list[str]
    warnings: list[str]
    chapter_bestseller_structures: Optional[list[str]] = None  # length == chapter_count


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def infer_book_size(chapter_count: int, policy: dict[str, Any]) -> str:
    ranges = policy.get("book_size_by_chapters") or {}
    for size in ("short", "medium", "long"):
        rr = ranges.get(size)
        if isinstance(rr, list) and len(rr) == 2 and rr[0] <= chapter_count <= rr[1]:
            return size
    if chapter_count <= 6:
        return "short"
    if chapter_count <= 10:
        return "medium"
    return "long"


def _role_distribution_warnings(
    book_size: str,
    emotional_role_sequence: Optional[list[str]],
    policy: dict[str, Any],
) -> list[str]:
    if not emotional_role_sequence:
        return []
    targets = (policy.get("role_distribution_targets") or {}).get(book_size) or {}
    if not targets:
        return []
    counts: dict[str, int] = {"introduce": 0, "deepen": 0, "challenge": 0, "resolve": 0}
    for role in emotional_role_sequence:
        mapped = ROLE_MAP.get(str(role).strip().lower())
        if mapped:
            counts[mapped] += 1
    warns: list[str] = []
    for role_name, bounds in targets.items():
        if not isinstance(bounds, list) or len(bounds) != 2:
            continue
        low, high = int(bounds[0]), int(bounds[1])
        c = counts.get(role_name, 0)
        if c < low or c > high:
            warns.append(
                f"arc_role_distribution[{book_size}] {role_name}={c} outside target [{low},{high}]"
            )
    return warns


def _apply_slot_policy(base_slots: list[str], slot_policy: dict[str, Any]) -> list[str]:
    base = [str(s).strip().upper() for s in base_slots]
    req = [str(s).strip().upper() for s in (slot_policy.get("require") or [])]
    opt = [str(s).strip().upper() for s in (slot_policy.get("optional") or [])]
    forbid = {str(s).strip().upper() for s in (slot_policy.get("forbid") or [])}

    out: list[str] = []
    for s in base:
        if s in forbid:
            continue
        if s in req or s in opt:
            out.append(s)

    # Ensure required slots exist in output in deterministic order, appended if absent.
    for s in req:
        if s not in out:
            out.append(s)

    # Basic viability: chapter should still carry narrative spine.
    if not any(s in out for s in ("HOOK", "SCENE", "STORY", "REFLECTION", "INTEGRATION")):
        return []

    return out


def _chapter_role(emotional_role_sequence: Optional[list[str]], chapter_idx: int) -> str:
    if not emotional_role_sequence or chapter_idx >= len(emotional_role_sequence):
        return "deepen"
    return ROLE_MAP.get(str(emotional_role_sequence[chapter_idx]).strip().lower(), "deepen")


def _score_candidate(
    *,
    chapter_idx: int,
    archetype_id: str,
    archetype_cfg: dict[str, Any],
    chapter_archetypes: list[str],
    signature_counts: dict[str, int],
    selector_key_prefix: str,
) -> float:
    # Base priority
    score = float(archetype_cfg.get("priority") or 1.0)

    # Novelty penalties on sequence rhythm
    if chapter_archetypes and chapter_archetypes[-1] == archetype_id:
        score -= 0.35
    if len(chapter_archetypes) >= 2 and chapter_archetypes[-1] == archetype_id and chapter_archetypes[-2] == archetype_id:
        score -= 0.75

    sig = archetype_id
    score -= 0.12 * float(signature_counts.get(sig, 0))

    # Small deterministic jitter to avoid stable global tie bias.
    h = hashlib.sha256(f"{selector_key_prefix}:novelty:ch{chapter_idx}:{archetype_id}".encode("utf-8")).digest()
    score += (h[0] / 2550.0)

    return score


def plan_chapters(
    *,
    slot_definitions: list[list[str]],
    chapter_count: int,
    selector_key_prefix: str,
    emotional_role_sequence: Optional[list[str]] = None,
    book_size: Optional[str] = None,
    policy_path: Optional[Path] = None,
    enforce_role_distribution: bool = False,
) -> ChapterPlanResult:
    """
    Build chapter-level archetype/weight plan and derive effective slot_definitions.
    """
    policy = _load_yaml(policy_path or POLICY_PATH)
    if not policy:
        return ChapterPlanResult(
            slot_definitions=slot_definitions,
            chapter_archetypes=["legacy_uniform"] * chapter_count,
            chapter_exercise_modes=["none"] * chapter_count,
            chapter_reflection_weights=["standard"] * chapter_count,
            chapter_story_depths=["standard"] * chapter_count,
            warnings=["chapter_planner_policies missing; fallback to uniform slot plan"],
        )

    size = book_size or infer_book_size(chapter_count, policy)
    warnings = _role_distribution_warnings(size, emotional_role_sequence, policy)
    if enforce_role_distribution and warnings:
        raise ValueError("; ".join(warnings))

    chapter_bestseller_structures = assign_bestseller_structures(chapter_count, selector_key_prefix)

    archetypes = (policy.get("archetypes") or {})
    quotas = (policy.get("quotas") or {}).get(size) or {}
    full_exercise_max = int(quotas.get("full_exercise_max") or 0)
    reflection_heavy_max = int(quotas.get("reflection_heavy_max") or 0)

    chapter_archetypes: list[str] = []
    chapter_exercise_modes: list[str] = []
    chapter_reflection_weights: list[str] = []
    chapter_story_depths: list[str] = []
    out_slots: list[list[str]] = []

    signature_counts: dict[str, int] = {}
    full_ex_used = 0
    reflection_heavy_used = 0

    for ch in range(chapter_count):
        base_row = list(slot_definitions[ch]) if ch < len(slot_definitions) else []
        role = _chapter_role(emotional_role_sequence, ch)

        # 1) Candidate generation
        generated: list[tuple[str, dict[str, Any], list[str]]] = []
        for aid, cfg in archetypes.items():
            roles = [str(r).strip().lower() for r in (cfg.get("arc_roles") or [])]
            if role not in roles:
                continue
            slot_policy = cfg.get("slot_policy") or {}
            row = _apply_slot_policy(base_row, slot_policy)
            if row:
                generated.append((aid, cfg, row))

        if not generated:
            generated = [("legacy_uniform", {"slot_policy": {}}, base_row)]

        # 2) Hard filter (quotas + transitions) before scoring
        filtered: list[tuple[str, dict[str, Any], list[str]]] = []
        prev = chapter_archetypes[-1] if chapter_archetypes else None
        for aid, cfg, row in generated:
            sp = cfg.get("slot_policy") or {}
            ex_mode = str(sp.get("exercise_mode") or "none")
            refl_w = str(sp.get("reflection_weight") or "standard")

            # Transition compatibility
            if prev:
                prev_cfg = archetypes.get(prev) or {}
                allowed_next = [str(x) for x in (prev_cfg.get("allowed_next") or [])]
                if allowed_next and aid not in allowed_next:
                    continue

            # Exercise quota
            would_full = (ex_mode == "full")
            if would_full and full_ex_used >= full_exercise_max:
                continue

            # Reflection-heavy quota
            would_heavy = (refl_w == "heavy")
            if would_heavy and reflection_heavy_used >= reflection_heavy_max:
                continue

            filtered.append((aid, cfg, row))

        if not filtered:
            filtered = [("legacy_uniform", {"slot_policy": {}}, base_row)]

        # 3) Novelty scoring
        scored: list[tuple[float, str, dict[str, Any], list[str]]] = []
        for aid, cfg, row in filtered:
            score = _score_candidate(
                chapter_idx=ch,
                archetype_id=aid,
                archetype_cfg=cfg,
                chapter_archetypes=chapter_archetypes,
                signature_counts=signature_counts,
                selector_key_prefix=selector_key_prefix,
            )
            scored.append((score, aid, cfg, row))

        scored.sort(key=lambda x: (-x[0], x[1]))
        best_score = scored[0][0]
        best = [x for x in scored if x[0] == best_score]

        # 4) Deterministic selection among score ties
        h = hashlib.sha256(f"{selector_key_prefix}:choose:ch{ch}".encode("utf-8")).digest()
        pick_idx = h[0] % len(best)
        _, archetype_id, archetype_cfg, chosen_row = best[pick_idx]

        sp = archetype_cfg.get("slot_policy") or {}
        ex_mode = str(sp.get("exercise_mode") or "none")
        refl_w = str(sp.get("reflection_weight") or "standard")
        story_d = str(sp.get("story_depth") or "standard")

        if ex_mode == "none":
            chosen_row = [s for s in chosen_row if s != "EXERCISE"]
        elif ex_mode in ("micro", "full") and "EXERCISE" not in chosen_row and "INTEGRATION" in chosen_row:
            # Deterministic insertion before INTEGRATION for better chapter flow.
            ins = chosen_row.index("INTEGRATION")
            chosen_row = chosen_row[:ins] + ["EXERCISE"] + chosen_row[ins:]

        if ex_mode == "full":
            full_ex_used += 1
        if refl_w == "heavy":
            reflection_heavy_used += 1

        chapter_archetypes.append(archetype_id)
        chapter_exercise_modes.append(ex_mode)
        chapter_reflection_weights.append(refl_w)
        chapter_story_depths.append(story_d)
        out_slots.append(chosen_row)
        signature_counts[archetype_id] = signature_counts.get(archetype_id, 0) + 1

    return ChapterPlanResult(
        slot_definitions=out_slots,
        chapter_archetypes=chapter_archetypes,
        chapter_exercise_modes=chapter_exercise_modes,
        chapter_reflection_weights=chapter_reflection_weights,
        chapter_story_depths=chapter_story_depths,
        warnings=warnings,
        chapter_bestseller_structures=chapter_bestseller_structures,
    )
