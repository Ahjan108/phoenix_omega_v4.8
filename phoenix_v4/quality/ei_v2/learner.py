"""
EI V2 Learning System — adaptive threshold and weight tuning.

Collects feedback from hybrid override decisions and quality evaluations,
then adjusts V2 composite weights and dimension thresholds to improve
performance in weak areas.

Architecture:
  1. OBSERVE — log every hybrid decision (override/keep) with full scores
  2. AGGREGATE — compute running statistics per dimension, persona, topic
  3. ADJUST — shift weights toward dimensions where V2 adds value;
     tighten thresholds where V2 underperforms
  4. PERSIST — write learned parameters to feedback store (JSONL)

The learner never changes V1 behavior. It only tunes V2's composite
weights and override thresholds so V2 gets better at picking winners.

Storage: artifacts/ei_v2/learner_feedback.jsonl (append-only)
         artifacts/ei_v2/learned_params.json (latest snapshot)
"""
from __future__ import annotations

import json
import math
import statistics
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from phoenix_v4.quality.ei_v2.config import ei_v2_repo_root
from phoenix_v4.quality.ei_v2.ei_warnings import log_ei_warning

_DEFAULT_STORE = ei_v2_repo_root() / "artifacts" / "ei_v2" / "learner_feedback.jsonl"
_DEFAULT_PARAMS = ei_v2_repo_root() / "artifacts" / "ei_v2" / "learned_params.json"

# Exponential moving average decay: recent observations weight more.
_EMA_ALPHA = 0.15

# Minimum observations before adjusting a parameter.
_MIN_OBSERVATIONS = 10

# Maximum weight shift per learning cycle (prevents runaway drift).
_MAX_WEIGHT_DELTA = 0.05

# Dimension keys tracked by the learner.
TRACKED_DIMENSIONS = [
    "rerank", "safety", "domain_similarity", "tts_readability",
    "uniqueness", "engagement", "somatic_precision",
    "emotional_coherence", "chapter_journey", "cohesion",
    "marketability", "therapeutic_value", "listen_experience",
]


@dataclass
class FeedbackRecord:
    """Single observation from a hybrid decision."""
    timestamp: str
    slot: str
    chapter_index: int
    persona_id: str
    topic_id: str
    v1_chosen_id: str
    v2_chosen_id: Optional[str]
    hybrid_chosen_id: str
    override_applied: bool
    override_reason: str = ""
    v1_composite: float = 0.0
    v2_composite: float = 0.0
    margin: float = 0.0
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    safety_risk: float = 0.0
    dedup_max_sim: float = 0.0
    arc_deviation: float = 0.0
    tts_composite: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LearnedParams:
    """Snapshot of learned V2 parameters."""
    version: int = 0
    updated_at: str = ""
    total_observations: int = 0
    composite_weights: Dict[str, float] = field(default_factory=dict)
    override_margin: float = 0.12
    dimension_thresholds: Dict[str, float] = field(default_factory=dict)
    per_persona_adjustments: Dict[str, Dict[str, float]] = field(default_factory=dict)
    per_topic_adjustments: Dict[str, Dict[str, float]] = field(default_factory=dict)
    dimension_ema: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _default_weights() -> Dict[str, float]:
    return {
        "rerank": 0.35,
        "safety": 0.25,
        "domain_similarity": 0.20,
        "tts_readability": 0.20,
    }


def _default_thresholds() -> Dict[str, float]:
    return {
        "uniqueness": 0.10,
        "engagement": 0.25,
        "somatic_precision": 0.30,
        "emotional_coherence": 0.85,
        "chapter_journey": 0.50,
        "cohesion": 0.35,
        "listen_experience": 0.50,
        "marketability": 0.25,
        "therapeutic_value": 0.60,
        "safety_compliance": 0.95,
    }


def load_learned_params(path: Optional[Path] = None) -> LearnedParams:
    """Load the latest learned parameters, or return defaults."""
    path = path or _DEFAULT_PARAMS
    if path and not path.is_absolute():
        path = ei_v2_repo_root() / path
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            params = LearnedParams(
                version=data.get("version", 0),
                updated_at=data.get("updated_at", ""),
                total_observations=data.get("total_observations", 0),
                composite_weights=data.get("composite_weights", _default_weights()),
                override_margin=data.get("override_margin", 0.12),
                dimension_thresholds=data.get("dimension_thresholds", _default_thresholds()),
                per_persona_adjustments=data.get("per_persona_adjustments", {}),
                per_topic_adjustments=data.get("per_topic_adjustments", {}),
                dimension_ema=data.get("dimension_ema", {}),
            )
            return params
        except (json.JSONDecodeError, KeyError) as e:
            log_ei_warning("learner", f"load_learned_params failed: {e}", {"path": str(path)})

    return LearnedParams(
        composite_weights=_default_weights(),
        dimension_thresholds=_default_thresholds(),
    )


def save_learned_params(params: LearnedParams, path: Optional[Path] = None) -> Path:
    """Persist the learned parameters snapshot."""
    path = path or _DEFAULT_PARAMS
    if path and not path.is_absolute():
        path = ei_v2_repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(params.to_dict(), indent=2, default=str), encoding="utf-8")
    return path


def log_feedback(record: FeedbackRecord, path: Optional[Path] = None) -> None:
    """Append a feedback record to the JSONL store."""
    path = path or _DEFAULT_STORE
    if path and not path.is_absolute():
        path = ei_v2_repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record.to_dict(), default=str) + "\n")


def load_feedback(path: Optional[Path] = None, limit: int = 0) -> List[FeedbackRecord]:
    """Load feedback records. If limit > 0, return only the last N."""
    path = path or _DEFAULT_STORE
    if path and not path.is_absolute():
        path = ei_v2_repo_root() / path
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    if limit > 0:
        lines = lines[-limit:]
    records = []
    for line in lines:
        try:
            data = json.loads(line)
            records.append(FeedbackRecord(**{
                k: v for k, v in data.items()
                if k in FeedbackRecord.__dataclass_fields__
            }))
        except (json.JSONDecodeError, TypeError) as e:
            log_ei_warning("learner", f"load_feedback parse error: {e}", {"line_index": len(records)})
            continue
    return records


def learn(
    feedback_path: Optional[Path] = None,
    params_path: Optional[Path] = None,
    window: int = 200,
) -> LearnedParams:
    """
    Run one learning cycle:
      1. Load recent feedback records
      2. Compute per-dimension EMAs
      3. Identify weak dimensions (below threshold)
      4. Shift composite weights to emphasize weak areas
      5. Adjust override margin based on override success rate
      6. Compute per-persona/topic adjustments
      7. Save updated params

    Returns the updated LearnedParams.
    """
    records = load_feedback(feedback_path, limit=window)
    params = load_learned_params(params_path)

    if len(records) < _MIN_OBSERVATIONS:
        return params

    # --- Compute dimension EMAs ---
    dim_values: Dict[str, List[float]] = {d: [] for d in TRACKED_DIMENSIONS}
    override_outcomes: List[bool] = []
    persona_scores: Dict[str, Dict[str, List[float]]] = {}
    topic_scores: Dict[str, Dict[str, List[float]]] = {}

    for rec in records:
        for dim, val in rec.dimension_scores.items():
            if dim in dim_values:
                dim_values[dim].append(val)

        if rec.override_applied:
            better = rec.v2_composite > rec.v1_composite
            override_outcomes.append(better)

        pid = rec.persona_id
        if pid not in persona_scores:
            persona_scores[pid] = {d: [] for d in TRACKED_DIMENSIONS}
        for dim, val in rec.dimension_scores.items():
            if dim in persona_scores[pid]:
                persona_scores[pid][dim].append(val)

        tid = rec.topic_id
        if tid not in topic_scores:
            topic_scores[tid] = {d: [] for d in TRACKED_DIMENSIONS}
        for dim, val in rec.dimension_scores.items():
            if dim in topic_scores[tid]:
                topic_scores[tid][dim].append(val)

    for dim in TRACKED_DIMENSIONS:
        vals = dim_values[dim]
        if vals:
            new_avg = statistics.mean(vals)
            old_ema = params.dimension_ema.get(dim, new_avg)
            params.dimension_ema[dim] = old_ema * (1 - _EMA_ALPHA) + new_avg * _EMA_ALPHA

    # --- Weight adjustment: boost dimensions that are weak ---
    thresholds = params.dimension_thresholds
    weight_keys = list(params.composite_weights.keys())
    weak_dims = []

    for dim, ema in params.dimension_ema.items():
        threshold = thresholds.get(dim, 0.5)
        if ema < threshold:
            weak_dims.append(dim)

    if weak_dims:
        dim_to_weight = {
            "uniqueness": "safety",
            "engagement": "rerank",
            "somatic_precision": "domain_similarity",
            "tts_readability": "tts_readability",
            "emotional_coherence": "rerank",
            "marketability": "domain_similarity",
            "chapter_journey": "rerank",
            "cohesion": "domain_similarity",
            "therapeutic_value": "safety",
            "listen_experience": "tts_readability",
        }

        boost_targets = set()
        for wd in weak_dims:
            mapped = dim_to_weight.get(wd)
            if mapped and mapped in params.composite_weights:
                boost_targets.add(mapped)

        if boost_targets:
            n_boost = len(boost_targets)
            n_other = len(weight_keys) - n_boost
            delta = min(_MAX_WEIGHT_DELTA, 0.10 / max(1, n_boost))

            for wk in weight_keys:
                if wk in boost_targets:
                    params.composite_weights[wk] = min(0.60,
                        params.composite_weights[wk] + delta)
                elif n_other > 0:
                    params.composite_weights[wk] = max(0.05,
                        params.composite_weights[wk] - delta * n_boost / n_other)

            total = sum(params.composite_weights.values())
            if total > 0:
                for wk in weight_keys:
                    params.composite_weights[wk] = round(
                        params.composite_weights[wk] / total, 4)

    # --- Override margin adjustment ---
    if override_outcomes:
        success_rate = sum(override_outcomes) / len(override_outcomes)
        if success_rate > 0.7:
            params.override_margin = max(0.05, params.override_margin - 0.01)
        elif success_rate < 0.4:
            params.override_margin = min(0.30, params.override_margin + 0.01)

    # --- Per-persona/topic adjustments ---
    for pid, pdims in persona_scores.items():
        adjustments = {}
        for dim, vals in pdims.items():
            if len(vals) >= 5:
                avg = statistics.mean(vals)
                global_ema = params.dimension_ema.get(dim, avg)
                if global_ema > 0:
                    ratio = avg / global_ema
                    if abs(ratio - 1.0) > 0.1:
                        adjustments[dim] = round(ratio, 4)
        if adjustments:
            params.per_persona_adjustments[pid] = adjustments

    for tid, tdims in topic_scores.items():
        adjustments = {}
        for dim, vals in tdims.items():
            if len(vals) >= 5:
                avg = statistics.mean(vals)
                global_ema = params.dimension_ema.get(dim, avg)
                if global_ema > 0:
                    ratio = avg / global_ema
                    if abs(ratio - 1.0) > 0.1:
                        adjustments[dim] = round(ratio, 4)
        if adjustments:
            params.per_topic_adjustments[tid] = adjustments

    params.version += 1
    params.updated_at = datetime.now(timezone.utc).isoformat()
    params.total_observations = len(records)

    save_learned_params(params, params_path)
    return params
