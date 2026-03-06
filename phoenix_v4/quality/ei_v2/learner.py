"""
EI V2 learner: load/save learned params and feedback log for hybrid override tuning.
Fail-open; used by hybrid_selector for override_margin and composite_weights.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, List

DEFAULT_COMPOSITE_WEIGHTS = {
    "rerank": 0.35,
    "domain": 0.25,
    "safety": 0.2,
    "tts": 0.1,
    "emotion_arc": 0.1,
}


@dataclass
class LearnedParams:
    version: int = 1
    override_margin: float = 0.12
    total_observations: int = 0
    composite_weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_COMPOSITE_WEIGHTS))

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "override_margin": self.override_margin,
            "total_observations": self.total_observations,
            "composite_weights": self.composite_weights,
        }


def load_learned_params(path: Path | None = None) -> LearnedParams:
    """Load learned params from JSON; return defaults if file missing."""
    if path is None or not path.exists():
        return LearnedParams()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        weights = data.get("composite_weights") or {}
        for k, v in DEFAULT_COMPOSITE_WEIGHTS.items():
            if k not in weights:
                weights[k] = v
        return LearnedParams(
            version=int(data.get("version", 1)),
            override_margin=float(data.get("override_margin", 0.12)),
            total_observations=int(data.get("total_observations", 0)),
            composite_weights=weights,
        )
    except (json.JSONDecodeError, OSError):
        return LearnedParams()


def save_learned_params(params: LearnedParams, path: Path) -> None:
    """Write learned params to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(params.to_dict(), indent=2), encoding="utf-8")


@dataclass
class FeedbackRecord:
    timestamp: str
    slot: str
    chapter_index: int
    persona_id: str
    topic_id: str
    v1_chosen_id: str
    v2_chosen_id: str
    hybrid_chosen_id: str
    override_applied: bool


def log_feedback(record: FeedbackRecord, path: Path) -> None:
    """Append one feedback record as JSONL line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(asdict(record), ensure_ascii=False) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def load_feedback(path: Path) -> List[FeedbackRecord]:
    """Load all feedback records from JSONL."""
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if not line:
            continue
        try:
            d = json.loads(line)
            records.append(FeedbackRecord(
                timestamp=d.get("timestamp", ""),
                slot=d.get("slot", ""),
                chapter_index=int(d.get("chapter_index", 0)),
                persona_id=d.get("persona_id", ""),
                topic_id=d.get("topic_id", ""),
                v1_chosen_id=d.get("v1_chosen_id", ""),
                v2_chosen_id=d.get("v2_chosen_id", ""),
                hybrid_chosen_id=d.get("hybrid_chosen_id", ""),
                override_applied=bool(d.get("override_applied", False)),
            ))
        except (json.JSONDecodeError, KeyError):
            continue
    return records
