"""
Release-wave similarity & burst controls (Phase 6).

Validates a batch of compiled plans (wave) for:
- Weekly caps (topic, persona, arc, band_sig, slot_sig, etc.)
- Exact fingerprint clusters (structural clones)
- Anti-homogeneity diversity score
- Optional: sliding-window share caps, near-cluster detection

Consumes Stage 3 plan JSON. Exit: 0 PASS, 1 FAIL, 2 WARN-only (if configured).

CLI:
  PYTHONPATH=. python3 phoenix_v4/ops/check_release_wave.py \\
    --plans-dir artifacts/plans/wave_2026_02_25 \\
    --calendar-week 2026-W09 \\
    --history-index artifacts/catalog_similarity/index.jsonl \\
    --out-dir artifacts/ops/release_wave_checks \\
    --config config/release_wave_controls.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Plan extraction (aligned with Stage 3 output and CTSS index)
# ---------------------------------------------------------------------------


def _safe_list(x: Any) -> list:
    return x if isinstance(x, list) else []


def _band_sig_from_plan(plan: dict[str, Any]) -> str:
    for key in ("dominant_band_sequence", "emotional_temperature_sequence"):
        v = plan.get(key)
        if isinstance(v, list) and v:
            return "-".join(str(x) if x is not None else "3" for x in v)
    return ""


def _slot_sig_from_plan(plan: dict[str, Any]) -> str:
    explicit = plan.get("slot_sig")
    if isinstance(explicit, str) and explicit:
        return explicit
    fmt = plan.get("format_id") or plan.get("format_structural_id") or ""
    seq = plan.get("chapter_slot_sequence") or plan.get("slot_definitions") or []
    payload = json.dumps(seq, sort_keys=True, ensure_ascii=False)
    return f"{fmt}:{_sha256_str(payload)}"


def _exercise_chapters_sig(plan: dict[str, Any]) -> str:
    explicit = plan.get("exercise_chapters")
    if isinstance(explicit, list):
        if not explicit:
            return "E:none"
        return "E:" + ",".join(str(int(x)) for x in explicit)
    seq = _safe_list(plan.get("chapter_slot_sequence"))
    ex: list[int] = []
    for ci, ch in enumerate(seq):
        slots = ch if isinstance(ch, list) else (ch.get("slots") or ch.get("chapter_slots") or []) if isinstance(ch, dict) else []
        for s in _safe_list(slots):
            t = (s.get("slot_type") or s.get("type") or s) if isinstance(s, dict) else s
            if str(t).upper() == "EXERCISE":
                ex.append(ci)
                break
    return "E:" + ",".join(str(x) for x in ex) if ex else "E:none"


def _role_sig_from_plan(plan: dict[str, Any]) -> str:
    explicit = plan.get("emotional_role_sig")
    if isinstance(explicit, str):
        return explicit
    seq = plan.get("emotional_role_sequence")
    if isinstance(seq, list) and seq:
        return "|".join(str(x) for x in seq)
    return ""


def _slug_pattern(slug: str) -> str:
    """Reduce slug to pattern for CTA/slug diversity (e.g. topic-persona). Aligned with validate_freebie_density."""
    if not slug:
        return ""
    parts = (slug or "").split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return slug


@dataclass
class WavePlanRow:
    book_id: str
    topic_id: str
    persona_id: str
    brand_id: str
    arc_id: str
    engine_id: str
    slot_sig: str
    band_sig: str
    variation_signature: str
    teacher_id: str
    teacher_mode: bool
    exercise_chapters_sig: str
    role_sig: str
    chapter_count: int
    cta_template_id: str = ""
    slug_pattern: str = ""
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


def extract_wave_row(plan: dict[str, Any], plan_path: str = "") -> Optional[WavePlanRow]:
    """Extract wave fingerprint row from plan. Returns None if too legacy (missing critical fields)."""
    book_id = (
        plan.get("plan_id")
        or plan.get("book_id")
        or plan.get("plan_hash")
        or (Path(plan_path).stem if plan_path else "")
    )
    topic_id = str(plan.get("topic_id") or plan.get("topic") or "")
    persona_id = str(plan.get("persona_id") or plan.get("persona") or "")
    brand_id = str(plan.get("brand_id") or "phoenix")
    arc_id = str(plan.get("arc_id") or plan.get("arc") or "")
    engine_id = str(plan.get("engine_id") or plan.get("engine") or "")
    slot_sig = _slot_sig_from_plan(plan)
    band_sig = _band_sig_from_plan(plan)
    variation_signature = str(plan.get("variation_signature") or "")
    teacher_id = str(plan.get("teacher_id") or "")
    teacher_mode = bool(plan.get("teacher_mode") or False)
    exercise_chapters_sig = _exercise_chapters_sig(plan)
    role_sig = _role_sig_from_plan(plan)
    ch_seq = _safe_list(plan.get("chapter_slot_sequence"))
    chapter_count = len(ch_seq) if ch_seq else int(plan.get("chapter_count") or 0)
    cta_template_id = str(plan.get("cta_template_id") or "")
    slug_pattern = _slug_pattern(str(plan.get("freebie_slug") or plan.get("slug") or ""))

    # Minimal required for wave checks: need arc_id or meaningful structure (chapter_slot_sequence)
    if not book_id and not plan_path:
        return None
    if not arc_id and not _safe_list(plan.get("chapter_slot_sequence")):
        return None

    return WavePlanRow(
        book_id=book_id,
        topic_id=topic_id,
        persona_id=persona_id,
        brand_id=brand_id,
        arc_id=arc_id,
        engine_id=engine_id,
        slot_sig=slot_sig,
        band_sig=band_sig,
        variation_signature=variation_signature,
        teacher_id=teacher_id,
        teacher_mode=teacher_mode,
        exercise_chapters_sig=exercise_chapters_sig,
        role_sig=role_sig,
        chapter_count=chapter_count,
        cta_template_id=cta_template_id,
        slug_pattern=slug_pattern,
        raw=plan,
    )


def wave_fingerprint(row: WavePlanRow) -> str:
    """Exact bucket key for structural clones."""
    return "|".join([
        row.arc_id or "none",
        row.slot_sig or "none",
        row.band_sig or "none",
        row.variation_signature or "none",
    ])


def token_set_for_near(row: WavePlanRow) -> set[str]:
    """Token set for Jaccard near-cluster similarity."""
    tokens: set[str] = set()
    if row.arc_id:
        tokens.add(f"arc:{row.arc_id}")
    if row.slot_sig:
        tokens.add(f"slot:{row.slot_sig}")
    if row.band_sig:
        tokens.add(f"band:{row.band_sig}")
    if row.variation_signature:
        tokens.add(f"var:{row.variation_signature}")
    if row.exercise_chapters_sig:
        tokens.add(f"ex:{row.exercise_chapters_sig}")
    if row.role_sig:
        tokens.add(f"role:{row.role_sig}")
    return tokens


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ---------------------------------------------------------------------------
# Normalized entropy (diversity)
# ---------------------------------------------------------------------------


def normalized_entropy(counts: dict[str, int], total: int) -> float:
    """H_norm = H / log(k). 0 = single category, 1 = uniform."""
    if total <= 0 or not counts:
        return 0.0
    k = len(counts)
    if k <= 1:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log(p)
    return h / math.log(k)


# ---------------------------------------------------------------------------
# Check logic
# ---------------------------------------------------------------------------


@dataclass
class Violation:
    code: str
    metric: str
    actual: Any
    cap: Any
    detail: str = ""


@dataclass
class ClusterInfo:
    fingerprint: str
    size: int
    book_ids: list[str]
    example_topic_persona: list[tuple[str, str]]


@dataclass
class WaveCheckResult:
    status: str  # PASS | FAIL | WARN
    total_plans: int
    valid_plans: int
    violations: list[Violation]
    exact_clusters: list[ClusterInfo]
    near_clusters: list[ClusterInfo]
    anti_homogeneity_score: float
    sliding_window_violations: list[Violation]
    remediation_hints: list[str]
    warnings: list[str]


def run_weekly_caps(
    rows: list[WavePlanRow],
    caps: dict[str, int],
) -> list[Violation]:
    out: list[Violation] = []
    topic_count: dict[str, int] = defaultdict(int)
    persona_count: dict[str, int] = defaultdict(int)
    topic_persona_count: dict[str, int] = defaultdict(int)
    arc_count: dict[str, int] = defaultdict(int)
    engine_count: dict[str, int] = defaultdict(int)
    brand_count: dict[str, int] = defaultdict(int)
    band_sig_count: dict[str, int] = defaultdict(int)
    slot_sig_count: dict[str, int] = defaultdict(int)
    variation_count: dict[str, int] = defaultdict(int)
    wave_fp_count: dict[str, int] = defaultdict(int)
    teacher_count: dict[str, int] = defaultdict(int)
    teacher_mode_count = 0
    cta_style_count: dict[str, int] = defaultdict(int)
    slug_pattern_count: dict[str, int] = defaultdict(int)

    for r in rows:
        topic_count[r.topic_id] += 1
        persona_count[r.persona_id] += 1
        topic_persona_count[f"{r.topic_id}|{r.persona_id}"] += 1
        arc_count[r.arc_id] += 1
        engine_count[r.engine_id] += 1
        brand_count[r.brand_id] += 1
        if r.band_sig:
            band_sig_count[r.band_sig] += 1
        if r.slot_sig:
            slot_sig_count[r.slot_sig] += 1
        if r.variation_signature:
            variation_count[r.variation_signature] += 1
        wf = wave_fingerprint(r)
        wave_fp_count[wf] += 1
        if r.teacher_mode:
            teacher_mode_count += 1
        if r.teacher_id:
            teacher_count[r.teacher_id] += 1
        if r.cta_template_id:
            cta_style_count[r.cta_template_id] += 1
        if r.slug_pattern:
            slug_pattern_count[r.slug_pattern] += 1

    cap_map = {
        "topic_id": (topic_count, caps.get("max_same_topic"), "WEEKLY_CAP_TOPIC_EXCEEDED"),
        "persona_id": (persona_count, caps.get("max_same_persona"), "WEEKLY_CAP_PERSONA_EXCEEDED"),
        "topic_persona": (topic_persona_count, caps.get("max_same_topic_persona_pair"), "WEEKLY_CAP_TOPIC_PERSONA_EXCEEDED"),
        "arc_id": (arc_count, caps.get("max_same_arc_id"), "WEEKLY_CAP_ARC_EXCEEDED"),
        "engine_id": (engine_count, caps.get("max_same_engine_id"), "WEEKLY_CAP_ENGINE_EXCEEDED"),
        "brand_id": (brand_count, caps.get("max_same_brand_id"), "WEEKLY_CAP_BRAND_EXCEEDED"),
        "band_sig": (band_sig_count, caps.get("max_same_band_signature"), "WEEKLY_CAP_BAND_SIG_EXCEEDED"),
        "slot_sig": (slot_sig_count, caps.get("max_same_slot_sig"), "WEEKLY_CAP_SLOT_SIG_EXCEEDED"),
        "variation_signature": (variation_count, caps.get("max_same_variation_signature"), "WEEKLY_CAP_VARIATION_SIG_EXCEEDED"),
        "wave_fingerprint": (wave_fp_count, caps.get("max_same_wave_fingerprint"), "WAVE_CLUSTER_EXACT_TOO_LARGE"),
        "teacher_id": (teacher_count, caps.get("max_same_teacher_id"), "WEEKLY_CAP_TEACHER_EXCEEDED"),
        "cta_template_id": (cta_style_count, caps.get("max_same_cta_style"), "WEEKLY_CAP_CTA_STYLE_EXCEEDED"),
        "slug_pattern": (slug_pattern_count, caps.get("max_same_slug_pattern"), "WEEKLY_CAP_SLUG_PATTERN_EXCEEDED"),
    }
    for key, (counts, cap, code) in cap_map.items():
        if cap is None:
            continue
        for val, cnt in counts.items():
            if cnt > cap:
                out.append(Violation(code=code, metric=key, actual=cnt, cap=cap, detail=f"{key}={val}"))

    if caps.get("max_teacher_mode_books") is not None and teacher_mode_count > caps["max_teacher_mode_books"]:
        out.append(Violation(
            code="WEEKLY_CAP_TEACHER_MODE_EXCEEDED",
            metric="teacher_mode_books",
            actual=teacher_mode_count,
            cap=caps["max_teacher_mode_books"],
        ))
    return out


def run_exact_clusters(
    rows: list[WavePlanRow],
    min_cluster_size: int,
) -> list[ClusterInfo]:
    by_fp: dict[str, list[WavePlanRow]] = defaultdict(list)
    for r in rows:
        by_fp[wave_fingerprint(r)].append(r)
    out: list[ClusterInfo] = []
    for fp, group in by_fp.items():
        if len(group) >= min_cluster_size:
            book_ids = sorted(r.book_id for r in group)[:10]
            example_topic_persona = [(r.topic_id, r.persona_id) for r in group[:5]]
            out.append(ClusterInfo(fingerprint=fp, size=len(group), book_ids=book_ids, example_topic_persona=example_topic_persona))
    return sorted(out, key=lambda c: -c.size)


def run_near_clusters(
    rows: list[WavePlanRow],
    jaccard_threshold: float,
    min_cluster_size: int,
) -> list[ClusterInfo]:
    if not rows or min_cluster_size < 2:
        return []
    tokens_per_row = [token_set_for_near(r) for r in rows]
    n = len(rows)
    # Union-find
    parent = list(range(n))

    def find(i: int) -> int:
        if parent[i] != i:
            parent[i] = find(parent[i])
        return parent[i]

    def union(i: int, j: int) -> None:
        pi, pj = find(i), find(j)
        if pi != pj:
            parent[pi] = pj

    pairs: list[tuple[float, int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            sim = jaccard(tokens_per_row[i], tokens_per_row[j])
            if sim >= jaccard_threshold:
                pairs.append((sim, i, j))
    pairs.sort(key=lambda x: (-x[0], x[1], x[2]))
    for _, i, j in pairs:
        union(i, j)

    comp: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        comp[find(i)].append(i)
    out: list[ClusterInfo] = []
    for indices in comp.values():
        if len(indices) >= min_cluster_size:
            group = [rows[i] for i in indices]
            book_ids = sorted(r.book_id for r in group)[:10]
            example_topic_persona = [(r.topic_id, r.persona_id) for r in group[:5]]
            common = set(tokens_per_row[indices[0]])
            for idx in indices[1:]:
                common &= tokens_per_row[idx]
            fp = "near:" + ",".join(sorted(common)[:5])
            out.append(ClusterInfo(fingerprint=fp, size=len(group), book_ids=book_ids, example_topic_persona=example_topic_persona))
    return sorted(out, key=lambda c: -c.size)


def run_anti_homogeneity(
    rows: list[WavePlanRow],
    weights: dict[str, float],
) -> float:
    if not rows:
        return 0.0
    total = len(rows)
    topic_count: dict[str, int] = defaultdict(int)
    persona_count: dict[str, int] = defaultdict(int)
    arc_count: dict[str, int] = defaultdict(int)
    band_count: dict[str, int] = defaultdict(int)
    slot_count: dict[str, int] = defaultdict(int)
    var_count: dict[str, int] = defaultdict(int)
    cta_count: dict[str, int] = defaultdict(int)
    slug_count: dict[str, int] = defaultdict(int)
    for r in rows:
        topic_count[r.topic_id] += 1
        persona_count[r.persona_id] += 1
        arc_count[r.arc_id] += 1
        if r.band_sig:
            band_count[r.band_sig] += 1
        if r.slot_sig:
            slot_count[r.slot_sig] += 1
        if r.variation_signature:
            var_count[r.variation_signature] += 1
        if r.cta_template_id:
            cta_count[r.cta_template_id] += 1
        if r.slug_pattern:
            slug_count[r.slug_pattern] += 1

    w = weights
    score = (
        w.get("topic_diversity", 0) * normalized_entropy(topic_count, total)
        + w.get("persona_diversity", 0) * normalized_entropy(persona_count, total)
        + w.get("arc_diversity", 0) * normalized_entropy(arc_count, total)
        + w.get("band_shape_diversity", 0) * normalized_entropy(band_count, total)
        + w.get("slot_diversity", 0) * normalized_entropy(slot_count, total)
        + w.get("variation_diversity", 0) * normalized_entropy(var_count, total)
        + w.get("cta_diversity", 0) * normalized_entropy(cta_count, total)
        + w.get("slug_diversity", 0) * normalized_entropy(slug_count, total)
    )
    total_w = sum(w.get(k, 0) for k in ("topic_diversity", "persona_diversity", "arc_diversity", "band_shape_diversity", "slot_diversity", "variation_diversity", "cta_diversity", "slug_diversity"))
    if total_w > 0:
        score /= total_w
    return round(score, 4)


def run_sliding_window(
    rows: list[WavePlanRow],
    history_index_path: Optional[Path],
    calendar_week: str,
    window_weeks: int,
    share_caps: dict[str, float],
) -> list[Violation]:
    """Load history index (JSONL with release_week or similar), compute shares over window. If no index or no release_week, return []."""
    out: list[Violation] = []
    if not history_index_path or not history_index_path.exists() or not share_caps:
        return out
    history_rows: list[dict[str, Any]] = []
    with open(history_index_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    history_rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    if not history_rows or not any("release_week" in r or "publish_date" in r for r in history_rows):
        return out
    # Simplified: treat current wave + last (window_weeks-1) from index as window (no real week parsing here)
    window_topic: dict[str, int] = defaultdict(int)
    window_persona: dict[str, int] = defaultdict(int)
    window_arc: dict[str, int] = defaultdict(int)
    window_band: dict[str, int] = defaultdict(int)
    for r in rows:
        window_topic[r.topic_id] += 1
        window_persona[r.persona_id] += 1
        window_arc[r.arc_id] += 1
        if r.band_sig:
            window_band[r.band_sig] += 1
    for h in history_rows:
        window_topic[str(h.get("topic_id", ""))] += 1
        window_persona[str(h.get("persona_id", ""))] += 1
        window_arc[str(h.get("arc_id", ""))] += 1
        band_raw = h.get("band_seq") or h.get("band_sig")
        if isinstance(band_raw, list):
            bs = "-".join(str(x) for x in band_raw)
        else:
            bs = str(band_raw or "")
        if bs:
            window_band[bs] += 1
    total_in_window = len(rows) + len(history_rows)
    if total_in_window <= 0:
        return out
    for key, cap in share_caps.items():
        if key == "max_topic_share":
            for t, c in window_topic.items():
                if c / total_in_window > cap:
                    out.append(Violation("WINDOW_TOPIC_SHARE_EXCEEDED", "topic_share", round(c / total_in_window, 3), cap, detail=t))
        elif key == "max_persona_share":
            for p, c in window_persona.items():
                if c / total_in_window > cap:
                    out.append(Violation("WINDOW_PERSONA_SHARE_EXCEEDED", "persona_share", round(c / total_in_window, 3), cap, detail=p))
        elif key == "max_arc_share":
            for a, c in window_arc.items():
                if c / total_in_window > cap:
                    out.append(Violation("WINDOW_ARC_SHARE_EXCEEDED", "arc_share", round(c / total_in_window, 3), cap, detail=a))
        elif key == "max_band_sig_share":
            for b, c in window_band.items():
                if c / total_in_window > cap:
                    out.append(Violation("WINDOW_BAND_SIG_SHARE_EXCEEDED", "band_sig_share", round(c / total_in_window, 3), cap, detail=b))
    return out


def build_remediation_hints(violations: list[Violation], exact_clusters: list[ClusterInfo]) -> list[str]:
    hints: list[str] = []
    for v in violations:
        if "TOPIC_EXCEEDED" in v.code:
            hints.append(f"Reduce topic count by {v.actual - v.cap} books (smallest set removal by book_id)")
        elif "PERSONA_EXCEEDED" in v.code:
            hints.append(f"Reduce persona count by {v.actual - v.cap} books")
        elif "ARC_EXCEEDED" in v.code:
            hints.append("Swap some arc_id to alternatives or move books to next week")
        elif "WAVE_CLUSTER_EXACT" in v.code:
            hints.append("Move or reselect books to break exact structural clone cluster")
    for c in exact_clusters[:3]:
        hints.append(f"Exact cluster size {c.size} (e.g. {c.book_ids[:3]}); diversify arc/slot/band/variation")
    return hints


def check_release_wave(
    plans_dir: Path,
    config_path: Path,
    calendar_week: str = "",
    history_index_path: Optional[Path] = None,
) -> WaveCheckResult:
    cfg = _load_yaml(config_path)
    rwc = cfg.get("release_wave_controls") or {}
    allow_legacy = rwc.get("allow_legacy_plans", True)
    weekly_caps_cfg = rwc.get("weekly_caps") or {}
    clustering_cfg = rwc.get("clustering") or {}
    sliding_cfg = rwc.get("sliding_window") or {}
    anti_cfg = rwc.get("anti_homogeneity") or {}
    reporting_cfg = rwc.get("reporting") or {}

    plans: list[dict[str, Any]] = []
    if plans_dir.is_dir():
        for p in plans_dir.glob("*.json"):
            try:
                plans.append(json.loads(p.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                pass

    rows: list[WavePlanRow] = []
    warnings: list[str] = []
    for i, plan in enumerate(plans):
        row = extract_wave_row(plan, str(plans_dir / f"plan_{i}.json"))
        if row is None:
            if allow_legacy:
                warnings.append(f"Plan {i} missing required fields; skipped")
            else:
                violations.append(Violation(
                    code="WAVE_INPUT_INVALID",
                    metric="plan",
                    actual=i,
                    cap="required fields",
                    detail="missing required fields (book_id/topic_id/persona_id/arc_id/slot_sig/band_sig or equivalent)",
                ))
            continue
        rows.append(row)

    violations: list[Violation] = []
    exact_clusters: list[ClusterInfo] = []
    near_clusters: list[ClusterInfo] = []
    sliding_violations: list[Violation] = []
    remediation_hints: list[str] = []

    if clustering_cfg.get("enabled"):
        min_exact = int(clustering_cfg.get("exact_bucket_min_cluster_size", 3))
        exact_clusters = run_exact_clusters(rows, min_exact)
        cap_fp = weekly_caps_cfg.get("max_same_wave_fingerprint")
        if cap_fp is not None:
            for c in exact_clusters:
                if c.size > cap_fp:
                    violations.append(Violation(
                        code="WAVE_CLUSTER_EXACT_TOO_LARGE",
                        metric="wave_fingerprint",
                        actual=c.size,
                        cap=cap_fp,
                        detail=c.fingerprint[:80],
                    ))

    violations.extend(run_weekly_caps(rows, weekly_caps_cfg))

    if clustering_cfg.get("enabled") and (clustering_cfg.get("near_bucket") or {}).get("enabled"):
        nb = clustering_cfg["near_bucket"]
        near_clusters = run_near_clusters(
            rows,
            float(nb.get("jaccard_threshold", 0.85)),
            int(nb.get("min_cluster_size", 4)),
        )
        for c in near_clusters:
            violations.append(Violation(
                code="WAVE_CLUSTER_NEAR_TOO_LARGE",
                metric="near_cluster",
                actual=c.size,
                cap=nb.get("min_cluster_size", 4),
                detail=c.fingerprint[:80],
            ))

    anti_score = 0.0
    if anti_cfg.get("enabled") and rows:
        weights = anti_cfg.get("weights") or {}
        anti_score = run_anti_homogeneity(rows, weights)
        min_score = float(anti_cfg.get("min_score", 0.62))
        if anti_score < min_score:
            violations.append(Violation(
                code="ANTI_HOMOGENEITY_SCORE_TOO_LOW",
                metric="anti_homogeneity_score",
                actual=anti_score,
                cap=min_score,
            ))

    if sliding_cfg.get("enabled") and history_index_path:
        sliding_violations = run_sliding_window(
            rows,
            history_index_path,
            calendar_week,
            int(sliding_cfg.get("weeks", 4)),
            (sliding_cfg.get("caps") or {}),
        )
        violations.extend(sliding_violations)

    remediation_hints = build_remediation_hints(violations, exact_clusters)

    has_fail = bool(violations)
    status = "FAIL" if has_fail else "PASS"
    return WaveCheckResult(
        status=status,
        total_plans=len(plans),
        valid_plans=len(rows),
        violations=violations,
        exact_clusters=exact_clusters,
        near_clusters=near_clusters,
        anti_homogeneity_score=anti_score,
        sliding_window_violations=sliding_violations,
        remediation_hints=remediation_hints,
        warnings=warnings,
    )


def write_report(result: WaveCheckResult, out_dir: Path, week: str, config: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"release_wave_check_{week.replace('-', '_')}"
    json_path = out_dir / f"{base}.json"
    md_path = out_dir / f"{base}.md"

    payload = {
        "calendar_week": week,
        "status": result.status,
        "total_plans": result.total_plans,
        "valid_plans": result.valid_plans,
        "anti_homogeneity_score": result.anti_homogeneity_score,
        "violations": [
            {"code": v.code, "metric": v.metric, "actual": v.actual, "cap": v.cap, "detail": v.detail}
            for v in result.violations
        ],
        "exact_clusters": [
            {"fingerprint": c.fingerprint[:120], "size": c.size, "book_ids": c.book_ids, "example_topic_persona": c.example_topic_persona}
            for c in result.exact_clusters
        ],
        "near_clusters": [
            {"fingerprint": c.fingerprint, "size": c.size, "book_ids": c.book_ids}
            for c in result.near_clusters
        ],
        "remediation_hints": result.remediation_hints,
        "warnings": result.warnings,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    lines = [
        f"# Release Wave Check — {week}",
        "",
        "## Summary",
        f"- **Status:** {result.status}",
        f"- **Total plans:** {result.total_plans}",
        f"- **Valid plans:** {result.valid_plans}",
        f"- **Anti-homogeneity score:** {result.anti_homogeneity_score}",
        "",
    ]
    if result.violations:
        lines.append("## Violations")
        lines.append("")
        for v in result.violations:
            lines.append(f"- **{v.code}** — {v.metric}: actual={v.actual}, cap={v.cap}" + (f" ({v.detail})" if v.detail else ""))
        lines.append("")
    if result.exact_clusters:
        lines.append("## Top exact clusters")
        lines.append("")
        for c in result.exact_clusters[: (config.get("reporting") or {}).get("include_top_clusters", 10)]:
            lines.append(f"- Size {c.size}: {c.book_ids[:5]} ...")
        lines.append("")
    if result.near_clusters:
        lines.append("## Top near clusters")
        lines.append("")
        for c in result.near_clusters[: (config.get("reporting") or {}).get("include_top_clusters", 10)]:
            lines.append(f"- Size {c.size}: {c.book_ids[:5]} ...")
        lines.append("")
    if result.remediation_hints:
        lines.append("## Remediation hints")
        lines.append("")
        for h in result.remediation_hints:
            lines.append(f"- {h}")
        lines.append("")
    if result.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in result.warnings:
            lines.append(f"- {w}")
        lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description="Release-wave similarity & burst controls (Phase 6)")
    ap.add_argument("--plans-dir", type=Path, required=True, help="Directory of compiled plan JSON files")
    ap.add_argument("--calendar-week", default="", help="Calendar week id (e.g. 2026-W09)")
    ap.add_argument("--history-index", type=Path, default=None, help="JSONL index for sliding window")
    ap.add_argument("--out-dir", type=Path, default=None, help="Output directory for report (default: artifacts/ops/release_wave_checks)")
    ap.add_argument("--config", type=Path, default=None, help="Config YAML (default: config/release_wave_controls.yaml)")
    ap.add_argument("--warn-only", action="store_true", help="On violation exit 2 (WARN) instead of 1 (FAIL)")
    args = ap.parse_args()

    repo = REPO_ROOT
    config_path = args.config or repo / "config" / "release_wave_controls.yaml"
    out_dir = args.out_dir or repo / "artifacts" / "ops" / "release_wave_checks"
    week = args.calendar_week or "unknown"

    if not args.plans_dir.exists():
        print(f"Error: plans-dir not found: {args.plans_dir}", file=sys.stderr)
        return 1
    if not config_path.exists():
        print(f"Error: config not found: {config_path}", file=sys.stderr)
        return 1

    result = check_release_wave(
        plans_dir=args.plans_dir,
        config_path=config_path,
        calendar_week=week,
        history_index_path=args.history_index,
    )
    cfg = _load_yaml(config_path)
    write_report(result, out_dir, week, cfg.get("release_wave_controls") or {})

    print(f"Release wave check: {result.status}")
    print(f"  Plans: {result.valid_plans}/{result.total_plans}  Anti-homogeneity score: {result.anti_homogeneity_score}")
    if result.violations:
        for v in result.violations[:10]:
            print(f"  - {v.code}: {v.metric}={v.actual} (cap={v.cap})")

    if result.status == "PASS":
        return 0
    if args.warn_only:
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
